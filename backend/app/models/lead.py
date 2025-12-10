from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Lead(Base):
    """
    Lead - a message that matched a rule with sufficient score.
    """
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    global_message_id = Column(UUID(as_uuid=True), ForeignKey("global_messages.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    score = Column(Numeric(3, 2), nullable=False)  # 0.00 to 1.00
    reasoning = Column(Text, nullable=True)  # LLM explanation
    extracted_entities = Column(JSON, nullable=True)  # Structured data from LLM
    status = Column(String(50), default="new", nullable=False)  # new, in_progress, processed, archived
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint('tenant_id', 'global_message_id', 'rule_id',
                        name='uq_lead_tenant_message_rule'),
        Index('ix_leads_tenant_status', 'tenant_id', 'status'),
        Index('ix_leads_score', 'score'),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="leads")
    global_message = relationship("GlobalMessage", back_populates="leads", foreign_keys=[global_message_id])
    rule = relationship("Rule", back_populates="leads")
    assignee = relationship("User", back_populates="assigned_leads", foreign_keys=[assignee_id])
    notifications = relationship("Notification", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead {self.id} score={self.score} status={self.status}>"
