"""
API endpoints для Rules (правила мониторинга).
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_active_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.models.rule import Rule
from app.models.channel_subscription import ChannelSubscription
from app.models.lead import Lead
from app.models.rule_analysis_progress import RuleAnalysisProgress
from app.schemas.rule import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
    RuleTestRequest,
    RuleTestResponse,
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Создать новое правило мониторинга.

    - **name**: Название правила
    - **description**: Описание правила (опционально)
    - **prompt**: LLM промпт с критериями поиска
    - **threshold**: Порог уверенности (0.00-1.00)
    - **channel_ids**: UUID каналов для мониторинга
        - NULL или [] = все подписанные каналы
        - [uuid1, uuid2] = только указанные каналы
        - При добавлении нового канала анализируется история (последние 5 дней, макс. 100 сообщений)
    - **is_active**: Активно ли правило
    - **schedule**: Расписание проверки (для будущих фич)

    **Поведение:**
    - Для новых каналов анализируется история: последние 5 дней, но не более 100 сообщений
    - После первого анализа обрабатываются только новые сообщения (инкрементально)
    """
    # Валидация: если указаны channel_ids, проверяем что tenant подписан на эти каналы
    if rule_data.channel_ids:
        subscriptions_count = db.query(func.count(ChannelSubscription.id)).filter(
            ChannelSubscription.channel_id.in_(rule_data.channel_ids),
            ChannelSubscription.tenant_id == current_tenant.id
        ).scalar()

        if subscriptions_count != len(rule_data.channel_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more channel IDs are not in your subscriptions"
            )

    # Создаем правило
    rule = Rule(
        tenant_id=current_tenant.id,
        name=rule_data.name,
        description=rule_data.description,
        prompt=rule_data.prompt,
        threshold=rule_data.threshold,
        channel_ids=rule_data.channel_ids,
        is_active=rule_data.is_active,
        schedule=rule_data.schedule or {"always": True},
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    # Добавляем leads_count
    response = RuleResponse.model_validate(rule)
    response.leads_count = 0

    return response


@router.get("", response_model=List[RuleResponse])
async def list_rules(
    is_active: Optional[bool] = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить список правил мониторинга.

    - **is_active**: Фильтр по активности (опционально)
    """
    query = db.query(Rule).filter(Rule.tenant_id == current_tenant.id)

    if is_active is not None:
        query = query.filter(Rule.is_active == is_active)

    rules = query.order_by(Rule.created_at.desc()).all()

    # Добавляем leads_count для каждого правила
    results = []
    for rule in rules:
        leads_count = db.query(func.count(Lead.id)).filter(Lead.rule_id == rule.id).scalar()
        rule_response = RuleResponse.model_validate(rule)
        rule_response.leads_count = leads_count
        results.append(rule_response)

    return results


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить детали правила по ID.
    """
    rule = db.query(Rule).filter(
        Rule.id == rule_id,
        Rule.tenant_id == current_tenant.id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    # Добавляем leads_count
    leads_count = db.query(func.count(Lead.id)).filter(Lead.rule_id == rule.id).scalar()
    response = RuleResponse.model_validate(rule)
    response.leads_count = leads_count

    return response


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_update: RuleUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Обновить правило.

    Все поля опциональны. Обновляются только переданные поля.

    **ВАЖНО:** При изменении критических полей прогресс анализа сбрасывается:
    - При изменении `prompt` или `threshold`: прогресс сбрасывается для ВСЕХ каналов
    - При изменении `channel_ids`:
        * Для существующих каналов (которые были и остались): прогресс сохраняется
        * Для новых каналов: анализируется история (последние 5 дней, макс. 100 сообщений)
    """
    rule = db.query(Rule).filter(
        Rule.id == rule_id,
        Rule.tenant_id == current_tenant.id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    # Валидация channel_ids если они переданы
    if rule_update.channel_ids is not None:
        subscriptions_count = db.query(func.count(ChannelSubscription.id)).filter(
            ChannelSubscription.channel_id.in_(rule_update.channel_ids),
            ChannelSubscription.tenant_id == current_tenant.id
        ).scalar()

        if subscriptions_count != len(rule_update.channel_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more channel IDs are not in your subscriptions"
            )

    # Проверяем, изменились ли критические поля (prompt или threshold)
    # При изменении prompt/threshold сбрасываем progress для переанализа ВСЕХ каналов
    # При изменении channel_ids progress НЕ сбрасывается:
    #   - Существующие каналы сохраняют progress
    #   - Удаленные каналы worker пропустит
    #   - Новые каналы worker создаст progress и проанализирует историю (5 дней)
    should_reset_progress = False
    update_data = rule_update.model_dump(exclude_unset=True)

    if "prompt" in update_data and update_data["prompt"] != rule.prompt:
        should_reset_progress = True
        logger.info(f"Rule {rule.id}: prompt changed, resetting progress for all channels")
    if "threshold" in update_data and update_data["threshold"] != rule.threshold:
        should_reset_progress = True
        logger.info(f"Rule {rule.id}: threshold changed, resetting progress for all channels")

    # Логируем изменение channel_ids, но НЕ сбрасываем progress
    if "channel_ids" in update_data and update_data["channel_ids"] != rule.channel_ids:
        logger.info(f"Rule {rule.id}: channel_ids changed, existing channels keep progress, new channels will analyze history")

    # Обновляем поля правила ПЕРЕД сбросом progress
    for field, value in update_data.items():
        setattr(rule, field, value)

    # Если изменился prompt, threshold или channel_ids - сбрасываем progress
    # Worker переанализирует сообщения с новыми параметрами
    if should_reset_progress:
        deleted_count = db.query(RuleAnalysisProgress).filter(
            RuleAnalysisProgress.rule_id == rule_id
        ).delete()
        logger.info(f"Deleted {deleted_count} progress records for rule {rule_id}")

    # Один commit для всех изменений (исправлен race condition)
    db.commit()
    db.refresh(rule)

    # Добавляем leads_count
    leads_count = db.query(func.count(Lead.id)).filter(Lead.rule_id == rule.id).scalar()
    response = RuleResponse.model_validate(rule)
    response.leads_count = leads_count

    return response


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Удалить правило.

    ВНИМАНИЕ: Все связанные лиды также будут удалены (cascade).
    """
    rule = db.query(Rule).filter(
        Rule.id == rule_id,
        Rule.tenant_id == current_tenant.id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    db.delete(rule)
    db.commit()

    return None


@router.post("/{rule_id}/test", response_model=RuleTestResponse)
async def test_rule(
    rule_id: UUID,
    test_request: RuleTestRequest,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Протестировать правило на примере сообщения.

    Возвращает результат анализа LLM без сохранения в БД.
    Полезно для проверки правила перед активацией.
    """
    rule = db.query(Rule).filter(
        Rule.id == rule_id,
        Rule.tenant_id == current_tenant.id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    try:
        # Анализируем сообщение
        analysis = await llm_service.analyze_message(
            message_text=test_request.message_text,
            rule_description=rule.prompt
        )

        # Извлекаем сущности если сообщение подходит
        extracted_entities = None
        if analysis["is_match"]:
            extracted_entities = await llm_service.extract_entities(
                message_text=test_request.message_text
            )

        # Проверяем, будет ли создан лид
        would_create_lead = (
            analysis["is_match"] and
            analysis["confidence"] >= float(rule.threshold)
        )

        return RuleTestResponse(
            is_match=analysis["is_match"],
            confidence=analysis["confidence"],
            reasoning=analysis["reasoning"],
            would_create_lead=would_create_lead,
            extracted_entities=extracted_entities
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM analysis failed: {str(e)}"
        )
