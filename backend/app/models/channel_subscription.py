"""
ChannelSubscription model - подписки tenants на глобальные каналы.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ChannelSubscription(Base):
    """
    Подписка tenant'а на глобальный канал.
    Связывает tenant → global_channel.
    """
    __tablename__ = "channel_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Связи
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("global_channels.id", ondelete="CASCADE"), nullable=False)
    telegram_account_id = Column(UUID(as_uuid=True), ForeignKey("telegram_accounts.id", ondelete="CASCADE"), nullable=False)

    # Настройки подписки
    is_active = Column(Boolean, default=True, nullable=False)
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="channel_subscriptions")
    channel = relationship("GlobalChannel", back_populates="subscriptions")
    telegram_account = relationship("TelegramAccount", back_populates="channel_subscriptions")

    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'channel_id', name='uq_subscription_tenant_channel'),
        Index('idx_subscriptions_tenant', 'tenant_id'),
        Index('idx_subscriptions_channel', 'channel_id'),
    )

    def __repr__(self):
        return f"<ChannelSubscription tenant={self.tenant_id} channel={self.channel_id}>"
