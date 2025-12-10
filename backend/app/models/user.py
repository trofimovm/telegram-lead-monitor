from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    """
    User model with email verification support.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="member", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Email verification fields
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    # Notification preferences
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    in_app_notifications_enabled = Column(Boolean, default=True, nullable=False)
    notify_on_new_lead = Column(Boolean, default=True, nullable=False)
    notify_on_lead_status_change = Column(Boolean, default=False, nullable=False)
    notify_on_lead_assignment = Column(Boolean, default=True, nullable=False)

    # Telegram Bot preferences
    telegram_chat_id = Column(String(50), nullable=True)
    telegram_bot_enabled = Column(Boolean, default=False, nullable=False)
    telegram_verification_code = Column(String(10), nullable=True)
    telegram_verification_expires = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    assigned_leads = relationship("Lead", back_populates="assignee", foreign_keys="Lead.assignee_id")
    notifications = relationship("Notification", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
