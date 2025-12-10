"""
Pydantic schemas для Notifications (системные уведомления).
Соответствуют модели app/models/notification.py
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Типы уведомлений"""
    LEAD_CREATED = "lead_created"
    LEAD_STATUS_CHANGED = "lead_status_changed"
    LEAD_ASSIGNED = "lead_assigned"
    RULE_TRIGGERED = "rule_triggered"
    SYSTEM = "system"


# ========== Base Schemas ==========

class NotificationBase(BaseModel):
    """Базовая схема для уведомления"""
    type: NotificationType = Field(..., description="Тип уведомления")
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок")
    message: str = Field(..., min_length=1, description="Текст уведомления")
    related_lead_id: Optional[UUID] = Field(None, description="ID связанного лида")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


# ========== Create Schemas ==========

class NotificationCreate(NotificationBase):
    """Схема для создания уведомления (внутреннее использование)"""
    tenant_id: UUID = Field(..., description="ID получателя")


# ========== Response Schemas ==========

class NotificationResponse(NotificationBase):
    """Полная схема уведомления для API ответов"""
    id: UUID
    tenant_id: UUID
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Список уведомлений с пагинацией и статистикой"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


# ========== Update Schemas ==========

class NotificationMarkAsRead(BaseModel):
    """Схема для пометки уведомления как прочитанного"""
    is_read: bool = True


class NotificationMarkAllAsRead(BaseModel):
    """Схема для пометки всех уведомлений как прочитанных"""
    marked_count: int = Field(..., description="Количество помеченных уведомлений")


# ========== User Preferences Schemas ==========

class NotificationPreferencesBase(BaseModel):
    """Базовая схема настроек уведомлений"""
    email_notifications_enabled: bool = Field(True, description="Email уведомления включены")
    in_app_notifications_enabled: bool = Field(True, description="In-app уведомления включены")
    telegram_bot_enabled: bool = Field(False, description="Telegram уведомления включены")
    notify_on_new_lead: bool = Field(True, description="Уведомлять о новых лидах")
    notify_on_lead_status_change: bool = Field(False, description="Уведомлять об изменении статуса")
    notify_on_lead_assignment: bool = Field(True, description="Уведомлять о назначении лида")


class NotificationPreferencesUpdate(NotificationPreferencesBase):
    """Схема для обновления настроек уведомлений"""
    pass


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Схема ответа с настройками уведомлений (из User модели)"""
    pass


# ========== Statistics Schemas ==========

class NotificationStats(BaseModel):
    """Статистика по уведомлениям"""
    total: int = Field(..., description="Всего уведомлений")
    unread: int = Field(..., description="Непрочитанных")
    by_type: Dict[NotificationType, int] = Field(..., description="Распределение по типам")
    recent_count: int = Field(..., description="За последние 24 часа")


# ========== Telegram Bot Schemas ==========

class TelegramBotInfo(BaseModel):
    """Информация о подключении Telegram бота"""
    bot_username: str = Field(..., description="Username бота")
    is_connected: bool = Field(..., description="Бот подключен к аккаунту")
    chat_id: Optional[str] = Field(None, description="Chat ID пользователя в Telegram")


class TelegramVerificationCodeResponse(BaseModel):
    """Ответ с кодом верификации для Telegram"""
    verification_code: str = Field(..., description="6-значный код верификации")
    expires_at: datetime = Field(..., description="Дата истечения кода")
    bot_username: str = Field(..., description="Username бота")
    instructions: str = Field(..., description="Инструкции по подключению")


class TelegramVerifyRequest(BaseModel):
    """Запрос на верификацию Telegram"""
    verification_code: str = Field(..., min_length=6, max_length=6, description="Код верификации")
    chat_id: str = Field(..., description="Chat ID из Telegram")


class TelegramVerifyResponse(BaseModel):
    """Ответ после верификации Telegram"""
    success: bool = Field(..., description="Успешная верификация")
    message: str = Field(..., description="Сообщение о результате")


class TelegramDisconnectResponse(BaseModel):
    """Ответ после отключения Telegram бота"""
    success: bool = Field(..., description="Успешное отключение")
    message: str = Field(..., description="Сообщение о результате")
