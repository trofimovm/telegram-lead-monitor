from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Tenant(Base):
    """
    Tenant model for multi-tenancy support.
    Each tenant represents an organization/workspace.
    """
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free", nullable=False)
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    telegram_accounts = relationship("TelegramAccount", back_populates="tenant", cascade="all, delete-orphan")
    rules = relationship("Rule", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")
    channel_subscriptions = relationship("ChannelSubscription", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant {self.name} ({self.plan})>"
