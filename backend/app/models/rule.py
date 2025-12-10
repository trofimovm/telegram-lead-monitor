from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Rule(Base):
    """
    Monitoring rule with LLM prompt and threshold.
    """
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)  # LLM system prompt with criteria
    threshold = Column(Numeric(3, 2), default=0.70, nullable=False)  # 0.00 to 1.00
    schedule = Column(JSON, default={"always": True})  # For future scheduling features
    channel_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # NULL = all channels (subscriptions)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="rules")
    leads = relationship("Lead", back_populates="rule", cascade="all, delete-orphan")
    analysis_progress = relationship("RuleAnalysisProgress", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rule {self.name} (threshold={self.threshold})>"
