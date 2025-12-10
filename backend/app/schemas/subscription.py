"""
Pydantic schemas для Channel Subscriptions (подписки на каналы).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SubscriptionCreate(BaseModel):
    """Схема для создания подписки на канал."""
    telegram_account_id: UUID = Field(..., description="UUID Telegram аккаунта для мониторинга")
    tg_id: int = Field(..., description="Telegram ID канала/чата")
    username: Optional[str] = Field(None, description="Username канала (без @)")
    title: Optional[str] = Field(None, description="Название канала/чата")
    channel_type: str = Field(default="channel", description="Тип: channel, group, chat")
    tags: List[str] = Field(default_factory=list, description="Теги для организации")


class SubscriptionUpdate(BaseModel):
    """Схема для обновления подписки."""
    is_active: Optional[bool] = Field(None, description="Активна ли подписка")
    tags: Optional[List[str]] = Field(None, description="Обновить теги")


class SubscriptionResponse(BaseModel):
    """Схема для ответа с подпиской."""
    id: UUID
    tenant_id: UUID
    channel_id: UUID
    telegram_account_id: UUID
    is_active: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    # Данные канала (joined)
    channel_tg_id: int
    channel_username: Optional[str]
    channel_title: Optional[str]
    channel_type: str

    model_config = {"from_attributes": True}


class ChannelInfo(BaseModel):
    """Информация о глобальном канале."""
    id: UUID
    tg_id: int
    username: Optional[str]
    title: Optional[str]
    channel_type: str
    is_active: bool
    created_at: datetime


class SubscriptionWithChannel(SubscriptionResponse):
    """Подписка с полной информацией о канале."""
    channel: ChannelInfo
