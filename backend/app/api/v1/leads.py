"""
API endpoints для Leads (найденные лиды).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import io

from app.api.deps import get_db, get_current_active_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.models.lead import Lead
from app.models.global_message import GlobalMessage
from app.models.global_channel import GlobalChannel
from app.models.channel_subscription import ChannelSubscription
from app.models.rule import Rule
from app.schemas.lead import (
    LeadResponse,
    LeadUpdate,
    LeadWithDetails,
    LeadStatus,
    LeadStats,
)
from app.services.notification_service import notification_service

router = APIRouter()


@router.get("", response_model=List[LeadResponse])
async def list_leads(
    # Фильтры
    status_filter: Optional[LeadStatus] = Query(None, alias="status"),
    rule_id: Optional[UUID] = None,
    channel_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    min_score: Optional[Decimal] = Query(None, ge=Decimal("0.00"), le=Decimal("1.00")),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    # Пагинация
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    # Dependencies
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить список лидов с фильтрацией и пагинацией.

    **Фильтры:**
    - **status**: Статус лида (new, in_progress, processed, archived)
    - **rule_id**: UUID правила
    - **channel_id**: UUID глобального канала
    - **assignee_id**: UUID назначенного пользователя
    - **min_score**: Минимальный score (0.00-1.00)
    - **date_from**: Начало периода
    - **date_to**: Конец периода

    **Пагинация:**
    - **skip**: Количество пропускаемых записей (default: 0)
    - **limit**: Максимальное количество записей (default: 50, max: 100)
    """
    query = db.query(Lead).filter(Lead.tenant_id == current_tenant.id)

    # Применяем фильтры
    if status_filter:
        query = query.filter(Lead.status == status_filter.value)

    if rule_id:
        query = query.filter(Lead.rule_id == rule_id)

    if assignee_id:
        query = query.filter(Lead.assignee_id == assignee_id)

    if min_score:
        query = query.filter(Lead.score >= min_score)

    if date_from:
        query = query.filter(Lead.created_at >= date_from)

    if date_to:
        query = query.filter(Lead.created_at <= date_to)

    # Фильтр по channel_id
    if channel_id:
        query = query.join(GlobalMessage).filter(
            GlobalMessage.channel_id == channel_id
        )

    # Сортировка и пагинация
    leads = query.order_by(desc(Lead.created_at)).offset(skip).limit(limit).all()

    return [LeadResponse.model_validate(lead) for lead in leads]


@router.get("/stats", response_model=LeadStats)
async def get_lead_stats(
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить статистику по лидам.
    """
    # Всего лидов
    total = db.query(func.count(Lead.id)).filter(
        Lead.tenant_id == current_tenant.id
    ).scalar()

    # По статусам
    status_counts = db.query(Lead.status, func.count(Lead.id)).filter(
        Lead.tenant_id == current_tenant.id
    ).group_by(Lead.status).all()

    by_status = {LeadStatus(status): count for status, count in status_counts}
    # Заполняем нулями отсутствующие статусы
    for status in LeadStatus:
        if status not in by_status:
            by_status[status] = 0

    # По правилам
    rule_counts = db.query(Lead.rule_id, func.count(Lead.id)).filter(
        Lead.tenant_id == current_tenant.id
    ).group_by(Lead.rule_id).all()

    by_rule = {str(rule_id): count for rule_id, count in rule_counts}

    # По каналам (через global_messages)
    channel_counts = db.query(
        GlobalMessage.channel_id, func.count(Lead.id)
    ).join(
        Lead, Lead.global_message_id == GlobalMessage.id
    ).filter(
        Lead.tenant_id == current_tenant.id
    ).group_by(GlobalMessage.channel_id).all()

    by_channel = {str(channel_id): count for channel_id, count in channel_counts}

    # Средний score
    avg_score = db.query(func.avg(Lead.score)).filter(
        Lead.tenant_id == current_tenant.id
    ).scalar() or Decimal("0.00")

    # За последние 24 часа
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_count = db.query(func.count(Lead.id)).filter(
        Lead.tenant_id == current_tenant.id,
        Lead.created_at >= yesterday
    ).scalar()

    return LeadStats(
        total=total,
        by_status=by_status,
        by_rule=by_rule,
        by_channel=by_channel,
        avg_score=avg_score,
        recent_count=recent_count
    )


@router.get("/{lead_id}", response_model=LeadWithDetails)
async def get_lead(
    lead_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить детальную информацию о лиде.

    Включает полные данные сообщения, источника, правила и назначенного пользователя.
    """
    lead = db.query(Lead).options(
        joinedload(Lead.global_message).joinedload(GlobalMessage.channel),
        joinedload(Lead.rule),
        joinedload(Lead.assignee)
    ).filter(
        Lead.id == lead_id,
        Lead.tenant_id == current_tenant.id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Формируем ответ с детальными данными
    response_data = LeadResponse.model_validate(lead).model_dump()

    # Добавляем данные сообщения
    if lead.global_message:
        response_data.update({
            "message_text": lead.global_message.text,
            "message_date": lead.global_message.sent_at,
            "message_sender_id": lead.global_message.author_tg_id,
            "message_views_count": None,  # Поле не существует в GlobalMessage
            "message_links": [],  # Поле не существует в GlobalMessage
        })

        # Добавляем данные канала
        if lead.global_message.channel:
            response_data.update({
                "channel_id": lead.global_message.channel.id,
                "channel_title": lead.global_message.channel.title,
                "channel_username": lead.global_message.channel.username,
                "channel_type": lead.global_message.channel.channel_type,
                "telegram_message_link": lead.global_message.get_telegram_link(),
            })

    # Добавляем данные правила
    if lead.rule:
        response_data.update({
            "rule_name": lead.rule.name,
            "rule_prompt": lead.rule.prompt,
        })

    # Добавляем данные назначенного пользователя
    if lead.assignee:
        response_data.update({
            "assignee_email": lead.assignee.email,
            "assignee_name": lead.assignee.full_name,
        })

    return LeadWithDetails(**response_data)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_update: LeadUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Обновить лид (статус, assignee).
    """
    # Загружаем lead с relationships для уведомлений
    lead = db.query(Lead).options(
        joinedload(Lead.rule),
        joinedload(Lead.global_message).joinedload(GlobalMessage.channel)
    ).filter(
        Lead.id == lead_id,
        Lead.tenant_id == current_tenant.id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Сохраняем старые значения для уведомлений
    old_status = lead.status
    old_assignee_id = lead.assignee_id

    # Валидация assignee_id если передан
    assignee = None
    if lead_update.assignee_id is not None:
        assignee = db.query(User).filter(
            User.id == lead_update.assignee_id,
            User.tenant_id == current_tenant.id
        ).first()

        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee user not found or does not belong to your account"
            )

    # Обновляем поля
    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    # Создаем уведомления если были изменения
    # 1. Уведомление об изменении статуса (владельцу tenant)
    if lead_update.status and lead_update.status.value != old_status:
        tenant_user = db.query(User).filter(User.id == current_tenant.id).first()
        if tenant_user:
            try:
                await notification_service.create_lead_status_change_notification(
                    db=db,
                    lead=lead,
                    user=tenant_user,
                    old_status=old_status,
                    new_status=lead_update.status.value,
                )
            except Exception as e:
                # Не прерываем выполнение если уведомление не отправилось
                import logging
                logging.error(f"Failed to create status change notification: {str(e)}")

    # 2. Уведомление о назначении (новому assignee)
    if lead_update.assignee_id and lead_update.assignee_id != old_assignee_id and assignee:
        try:
            await notification_service.create_lead_assignment_notification(
                db=db,
                lead=lead,
                assignee=assignee,
            )
        except Exception as e:
            import logging
            logging.error(f"Failed to create assignment notification: {str(e)}")

    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Удалить лид.

    ВНИМАНИЕ: Сообщение останется в БД, удалится только запись о лиде.
    """
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.tenant_id == current_tenant.id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    db.delete(lead)
    db.commit()

    return None


@router.get("/export/csv")
async def export_leads_to_csv(
    # Фильтры (те же что и в list_leads)
    status_filter: Optional[LeadStatus] = Query(None, alias="status"),
    rule_id: Optional[UUID] = None,
    channel_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    min_score: Optional[Decimal] = Query(None, ge=Decimal("0.00"), le=Decimal("1.00")),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    # Dependencies
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Экспортировать лиды в CSV файл.

    Применяются те же фильтры что и в list_leads, но без пагинации.
    """
    # Базовый query с join'ами для получения всех данных
    query = db.query(Lead).options(
        joinedload(Lead.global_message).joinedload(GlobalMessage.channel),
        joinedload(Lead.rule),
        joinedload(Lead.assignee)
    ).filter(Lead.tenant_id == current_tenant.id)

    # Применяем фильтры
    if status_filter:
        query = query.filter(Lead.status == status_filter.value)

    if rule_id:
        query = query.filter(Lead.rule_id == rule_id)

    if assignee_id:
        query = query.filter(Lead.assignee_id == assignee_id)

    if min_score:
        query = query.filter(Lead.score >= min_score)

    if date_from:
        query = query.filter(Lead.created_at >= date_from)

    if date_to:
        query = query.filter(Lead.created_at <= date_to)

    # Фильтр по channel_id
    if channel_id:
        query = query.join(GlobalMessage).filter(
            GlobalMessage.channel_id == channel_id
        )

    # Получаем все лиды (без пагинации)
    leads = query.order_by(desc(Lead.created_at)).all()

    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output)

    # Заголовки CSV
    writer.writerow([
        'Lead ID',
        'Created At',
        'Status',
        'Score',
        'Rule Name',
        'Source Title',
        'Source Username',
        'Message Text',
        'Message Date',
        'Reasoning',
        'Contacts',
        'Keywords',
        'Budget',
        'Deadline',
        'Summary',
        'Assignee Email',
        'Assignee Name'
    ])

    # Данные
    for lead in leads:
        # Извлекаем данные из extracted_entities
        entities = lead.extracted_entities or {}
        contacts = ', '.join(entities.get('contacts', [])) if entities.get('contacts') else ''
        keywords = ', '.join(entities.get('keywords', [])) if entities.get('keywords') else ''
        budget = entities.get('budget', '')
        deadline = entities.get('deadline', '')
        summary = entities.get('summary', '')

        writer.writerow([
            str(lead.id),
            lead.created_at.strftime('%Y-%m-%d %H:%M:%S') if lead.created_at else '',
            lead.status,
            float(lead.score),
            lead.rule.name if lead.rule else '',
            lead.global_message.channel.title if (lead.global_message and lead.global_message.channel) else '',
            lead.global_message.channel.username if (lead.global_message and lead.global_message.channel) else '',
            (lead.global_message.text[:200] + '...') if (lead.global_message and lead.global_message.text and len(lead.global_message.text) > 200) else (lead.global_message.text if lead.global_message else ''),
            lead.global_message.sent_at.strftime('%Y-%m-%d %H:%M:%S') if (lead.global_message and lead.global_message.sent_at) else '',
            lead.reasoning or '',
            contacts,
            keywords,
            budget,
            deadline,
            summary,
            lead.assignee.email if lead.assignee else '',
            lead.assignee.full_name if lead.assignee else ''
        ])

    # Готовим ответ
    output.seek(0)
    filename = f"leads_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
