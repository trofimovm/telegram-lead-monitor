"""
Pydantic schemas для Rules (правила мониторинга).
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class RuleBase(BaseModel):
    """Базовая схема для Rule."""
    name: str = Field(..., min_length=1, max_length=255, description="Название правила")
    description: Optional[str] = Field(None, description="Описание правила")
    prompt: str = Field(..., min_length=10, description="LLM промпт с критериями поиска")
    threshold: Decimal = Field(
        default=Decimal("0.70"),
        ge=Decimal("0.00"),
        le=Decimal("1.00"),
        description="Порог уверенности для создания лида (0.00-1.00)"
    )
    channel_ids: Optional[List[UUID]] = Field(
        default=None,
        description="UUID каналов для мониторинга. NULL = все каналы (subscriptions) тенанта"
    )
    is_active: bool = Field(default=True, description="Активно ли правило")
    schedule: Optional[Dict[str, Any]] = Field(
        default={"always": True},
        description="Расписание проверки (для будущих фич)"
    )

    @field_validator('threshold')
    @classmethod
    def validate_threshold(cls, v: Decimal) -> Decimal:
        """Валидация threshold: должно быть между 0 и 1."""
        if v < Decimal("0.00") or v > Decimal("1.00"):
            raise ValueError("Threshold must be between 0.00 and 1.00")
        return v


class RuleCreate(RuleBase):
    """Схема для создания правила."""
    pass


class RuleUpdate(BaseModel):
    """Схема для обновления правила. Все поля опциональны."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    prompt: Optional[str] = Field(None, min_length=10)
    threshold: Optional[Decimal] = Field(None, ge=Decimal("0.00"), le=Decimal("1.00"))
    channel_ids: Optional[List[UUID]] = None
    is_active: Optional[bool] = None
    schedule: Optional[Dict[str, Any]] = None

    @field_validator('threshold')
    @classmethod
    def validate_threshold(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Валидация threshold если передан."""
        if v is not None and (v < Decimal("0.00") or v > Decimal("1.00")):
            raise ValueError("Threshold must be between 0.00 and 1.00")
        return v


class RuleResponse(RuleBase):
    """Схема для ответа с правилом."""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    # Дополнительная статистика (может быть добавлена позже)
    leads_count: Optional[int] = Field(default=0, description="Количество найденных лидов")

    model_config = {"from_attributes": True}


class RuleTestRequest(BaseModel):
    """Схема для тестирования правила на примере сообщения."""
    message_text: str = Field(..., min_length=1, description="Текст сообщения для тестирования")


class RuleTestResponse(BaseModel):
    """Схема для результата тестирования правила."""
    is_match: bool = Field(..., description="Соответствует ли сообщение правилу")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность LLM (0.0-1.0)")
    reasoning: str = Field(..., description="Объяснение от LLM")
    would_create_lead: bool = Field(..., description="Будет ли создан лид (confidence >= threshold)")
    extracted_entities: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Извлеченные сущности (контакты, ключевые слова и т.д.)"
    )
