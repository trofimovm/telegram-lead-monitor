"""
RuleAnalysisProgress model - отслеживание прогресса анализа сообщений правилами.
Хранит pointer на последнее проанализированное сообщение вместо всех проверок.
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class RuleAnalysisProgress(Base):
    """
    Прогресс анализа сообщений правилом для конкретного канала.
    Хранит только pointer на последнее обработанное сообщение.
    """
    __tablename__ = "rule_analysis_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Связи
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("global_channels.id", ondelete="CASCADE"), nullable=False)

    # Progress tracking
    last_analyzed_message_id = Column(UUID(as_uuid=True), ForeignKey("global_messages.id", ondelete="SET NULL"), nullable=True)
    last_analyzed_at = Column(DateTime, nullable=True)

    # Статистика
    messages_analyzed = Column(Integer, default=0, nullable=False)
    leads_created = Column(Integer, default=0, nullable=False)

    # Relationships
    rule = relationship("Rule", back_populates="analysis_progress")
    channel = relationship("GlobalChannel")
    last_analyzed_message = relationship("GlobalMessage", foreign_keys=[last_analyzed_message_id])

    # Constraints - один прогресс для пары (rule, channel)
    __table_args__ = (
        UniqueConstraint('rule_id', 'channel_id', name='uq_rule_channel'),
    )

    def __repr__(self):
        return f"<RuleAnalysisProgress rule={self.rule_id} channel={self.channel_id}>"
