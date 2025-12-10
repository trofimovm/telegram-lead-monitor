"""
Модель для системных уведомлений.
Используется для in-app уведомлений о новых лидах, изменениях статусов и системных событиях.
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class NotificationType(str, Enum):
    """Типы уведомлений"""
    LEAD_CREATED = "lead_created"  # Новый лид найден
    LEAD_STATUS_CHANGED = "lead_status_changed"  # Статус лида изменён
    LEAD_ASSIGNED = "lead_assigned"  # Лид назначен на пользователя
    RULE_TRIGGERED = "rule_triggered"  # Правило сработало
    SYSTEM = "system"  # Системное уведомление


class Notification(Base):
    """
    Модель уведомления.

    Уведомления создаются автоматически при:
    - Создании нового лида
    - Изменении статуса лида
    - Назначении лида на пользователя
    - Срабатывании правил с высоким score
    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Получатель уведомления"
    )

    # Метаданные уведомления
    type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
        comment="Тип уведомления"
    )
    title = Column(String(255), nullable=False, comment="Заголовок уведомления")
    message = Column(Text, nullable=False, comment="Текст уведомления")

    # Связь с лидом (опционально)
    related_lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID связанного лида (если применимо)"
    )

    # Дополнительные данные (JSON) - для будущего расширения
    extra_data = Column(Text, nullable=True, comment="Дополнительные данные в JSON")

    # Статус прочтения
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True, comment="Когда уведомление было прочитано")

    # Временные метки
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("User", back_populates="notifications")
    lead = relationship("Lead", back_populates="notifications", foreign_keys=[related_lead_id])

    def __repr__(self):
        return f"<Notification {self.id} ({self.type}) for {self.tenant_id}>"

    def mark_as_read(self):
        """Пометить уведомление как прочитанное"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
