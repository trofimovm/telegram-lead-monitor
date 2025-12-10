from sqlalchemy import Column, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class TelegramAccount(Base):
    """
    Telegram account model for MTProto connections.
    Session data is encrypted using Fernet.
    """
    __tablename__ = "telegram_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(20), nullable=False)
    session_encrypted = Column(LargeBinary, nullable=False)  # Fernet encrypted session string
    status = Column(String(50), default="active", nullable=False)  # active, requires_reauth, banned
    last_active_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="telegram_accounts")
    channel_subscriptions = relationship("ChannelSubscription", back_populates="telegram_account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TelegramAccount {self.phone} ({self.status})>"
