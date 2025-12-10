"""
Pydantic schemas для Leads (найденные лиды).
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum


class LeadStatus(str, Enum):
    """Статусы лида."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PROCESSED = "processed"
    ARCHIVED = "archived"


class LeadBase(BaseModel):
    """Базовая схема для Lead."""
    status: LeadStatus = Field(default=LeadStatus.NEW, description="Статус обработки лида")
    assignee_id: Optional[UUID] = Field(None, description="UUID пользователя, назначенного на лид")


class LeadUpdate(BaseModel):
    """Схема для обновления лида. Все поля опциональны."""
    status: Optional[LeadStatus] = None
    assignee_id: Optional[UUID] = None


class LeadResponse(BaseModel):
    """Схема для ответа с лидом."""
    id: UUID
    tenant_id: UUID
    message_id: Union[UUID, None] = Field(default=None, description="UUID старого сообщения (deprecated)")
    global_message_id: Union[UUID, None] = Field(default=None, description="UUID глобального сообщения")
    rule_id: UUID
    score: Decimal = Field(..., description="Уверенность LLM (0.00-1.00)")
    reasoning: Optional[str] = Field(None, description="Объяснение от LLM")
    extracted_entities: Optional[Dict[str, Any]] = Field(
        None,
        description="Извлеченные сущности (контакты, ключевые слова, бюджет и т.д.)"
    )
    status: LeadStatus
    assignee_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadWithDetails(LeadResponse):
    """Схема для лида с полными данными сообщения и правила."""
    # Message data
    message_text: Optional[str] = Field(None, description="Текст сообщения")
    message_date: Optional[datetime] = Field(None, description="Дата сообщения")
    message_sender_id: Optional[int] = Field(None, description="ID отправителя в Telegram")
    message_views_count: Optional[int] = Field(None, description="Количество просмотров")
    message_links: Optional[list[str]] = Field(default_factory=list, description="Ссылки в сообщении")

    # Channel data
    channel_id: Optional[UUID] = Field(None, description="UUID глобального канала")
    channel_title: Optional[str] = Field(None, description="Название канала")
    channel_username: Optional[str] = Field(None, description="Username канала")
    channel_type: Optional[str] = Field(None, description="Тип канала (channel/group/chat)")
    telegram_message_link: Optional[str] = Field(None, description="Ссылка на оригинальное сообщение в Telegram")

    # Rule data
    rule_name: Optional[str] = Field(None, description="Название правила")
    rule_prompt: Optional[str] = Field(None, description="Промпт правила")

    # Assignee data (если есть)
    assignee_email: Optional[str] = Field(None, description="Email назначенного пользователя")
    assignee_name: Optional[str] = Field(None, description="Имя назначенного пользователя")


class LeadListFilters(BaseModel):
    """Фильтры для списка лидов."""
    status: Optional[LeadStatus] = Field(None, description="Фильтр по статусу")
    rule_id: Optional[UUID] = Field(None, description="Фильтр по правилу")
    channel_id: Optional[UUID] = Field(None, description="Фильтр по каналу")
    assignee_id: Optional[UUID] = Field(None, description="Фильтр по назначенному пользователю")
    date_from: Optional[datetime] = Field(None, description="Дата начала периода")
    date_to: Optional[datetime] = Field(None, description="Дата окончания периода")
    min_score: Optional[Decimal] = Field(None, ge=Decimal("0.00"), le=Decimal("1.00"), description="Минимальный score")
    search: Optional[str] = Field(None, description="Поиск по тексту сообщения")


class LeadStats(BaseModel):
    """Статистика по лидам."""
    total: int = Field(..., description="Всего лидов")
    by_status: Dict[LeadStatus, int] = Field(..., description="Количество по статусам")
    by_rule: Dict[str, int] = Field(..., description="Количество по правилам (rule_id: count)")
    by_channel: Dict[str, int] = Field(..., description="Количество по каналам (channel_id: count)")
    avg_score: Optional[Decimal] = Field(None, description="Средний score")
    recent_count: int = Field(..., description="Количество за последние 24 часа")
