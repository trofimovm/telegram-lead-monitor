"""
API endpoints для Channel Subscriptions (подписки на каналы).
Замена старого /api/v1/sources.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_active_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.models.channel_subscription import ChannelSubscription
from app.models.global_channel import GlobalChannel
from app.models.telegram_account import TelegramAccount
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
)

router = APIRouter()


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Создать подписку на канал/чат.

    - **telegram_account_id**: Telegram аккаунт для мониторинга
    - **tg_id**: Telegram ID канала/чата
    - **username**: Username канала (опционально)
    - **title**: Название канала (опционально)
    - **channel_type**: Тип (channel, chat, group)
    - **tags**: Теги для организации
    """
    # Проверяем что Telegram аккаунт принадлежит tenant
    telegram_account = db.query(TelegramAccount).filter(
        TelegramAccount.id == subscription_data.telegram_account_id,
        TelegramAccount.tenant_id == current_tenant.id
    ).first()

    if not telegram_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found"
        )

    # Найти или создать глобальный канал
    global_channel = db.query(GlobalChannel).filter(
        GlobalChannel.tg_id == subscription_data.tg_id
    ).first()

    if not global_channel:
        # Создать новый глобальный канал
        global_channel = GlobalChannel(
            tg_id=subscription_data.tg_id,
            username=subscription_data.username,
            title=subscription_data.title,
            channel_type=subscription_data.channel_type,
            is_active=True,
        )
        db.add(global_channel)
        db.flush()  # Получить ID

    # Проверить что подписка не существует
    existing = db.query(ChannelSubscription).filter(
        ChannelSubscription.tenant_id == current_tenant.id,
        ChannelSubscription.channel_id == global_channel.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription already exists"
        )

    # Создать подписку
    subscription = ChannelSubscription(
        tenant_id=current_tenant.id,
        channel_id=global_channel.id,
        telegram_account_id=subscription_data.telegram_account_id,
        is_active=True,
        tags=subscription_data.tags,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    # Загрузить канал для ответа
    subscription = db.query(ChannelSubscription).options(
        joinedload(ChannelSubscription.channel)
    ).filter(ChannelSubscription.id == subscription.id).first()

    # Формируем ответ с данными канала
    response_data = {
        "id": subscription.id,
        "tenant_id": subscription.tenant_id,
        "channel_id": subscription.channel_id,
        "telegram_account_id": subscription.telegram_account_id,
        "is_active": subscription.is_active,
        "tags": subscription.tags or [],
        "created_at": subscription.created_at,
        "updated_at": subscription.updated_at,
        "channel_tg_id": subscription.channel.tg_id,
        "channel_username": subscription.channel.username,
        "channel_title": subscription.channel.title,
        "channel_type": subscription.channel.channel_type,
    }

    return SubscriptionResponse(**response_data)


@router.get("", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить список подписок текущего tenant.
    """
    subscriptions = db.query(ChannelSubscription).options(
        joinedload(ChannelSubscription.channel)
    ).filter(
        ChannelSubscription.tenant_id == current_tenant.id
    ).all()

    results = []
    for sub in subscriptions:
        response_data = {
            "id": sub.id,
            "tenant_id": sub.tenant_id,
            "channel_id": sub.channel_id,
            "telegram_account_id": sub.telegram_account_id,
            "is_active": sub.is_active,
            "tags": sub.tags or [],
            "created_at": sub.created_at,
            "updated_at": sub.updated_at,
            "channel_tg_id": sub.channel.tg_id,
            "channel_username": sub.channel.username,
            "channel_title": sub.channel.title,
            "channel_type": sub.channel.channel_type,
        }
        results.append(SubscriptionResponse(**response_data))

    return results


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить детали конкретной подписки.
    """
    subscription = db.query(ChannelSubscription).options(
        joinedload(ChannelSubscription.channel)
    ).filter(
        ChannelSubscription.id == subscription_id,
        ChannelSubscription.tenant_id == current_tenant.id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    response_data = {
        "id": subscription.id,
        "tenant_id": subscription.tenant_id,
        "channel_id": subscription.channel_id,
        "telegram_account_id": subscription.telegram_account_id,
        "is_active": subscription.is_active,
        "tags": subscription.tags or [],
        "created_at": subscription.created_at,
        "updated_at": subscription.updated_at,
        "channel_tg_id": subscription.channel.tg_id,
        "channel_username": subscription.channel.username,
        "channel_title": subscription.channel.title,
        "channel_type": subscription.channel.channel_type,
    }

    return SubscriptionResponse(**response_data)


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: UUID,
    subscription_update: SubscriptionUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Обновить подписку (активность, теги).
    """
    subscription = db.query(ChannelSubscription).filter(
        ChannelSubscription.id == subscription_id,
        ChannelSubscription.tenant_id == current_tenant.id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Обновляем поля
    update_data = subscription_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)

    db.commit()
    db.refresh(subscription)

    # Загрузить канал для ответа
    subscription = db.query(ChannelSubscription).options(
        joinedload(ChannelSubscription.channel)
    ).filter(ChannelSubscription.id == subscription.id).first()

    response_data = {
        "id": subscription.id,
        "tenant_id": subscription.tenant_id,
        "channel_id": subscription.channel_id,
        "telegram_account_id": subscription.telegram_account_id,
        "is_active": subscription.is_active,
        "tags": subscription.tags or [],
        "created_at": subscription.created_at,
        "updated_at": subscription.updated_at,
        "channel_tg_id": subscription.channel.tg_id,
        "channel_username": subscription.channel.username,
        "channel_title": subscription.channel.title,
        "channel_type": subscription.channel.channel_type,
    }

    return SubscriptionResponse(**response_data)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Удалить подписку.

    ВНИМАНИЕ: Глобальный канал останется в БД, удалится только подписка.
    """
    subscription = db.query(ChannelSubscription).filter(
        ChannelSubscription.id == subscription_id,
        ChannelSubscription.tenant_id == current_tenant.id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    db.delete(subscription)
    db.commit()

    return None
