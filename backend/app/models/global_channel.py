"""
GlobalChannel model - глобальное хранилище каналов для всех tenants.
Один канал = одна запись, независимо от количества пользователей.
"""
from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class GlobalChannel(Base):
    """
    Глобальный канал/группа Telegram.
    Хранится один раз для всей системы, независимо от tenants.
    """
    __tablename__ = "global_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Telegram идентификаторы
    tg_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=True, unique=True, index=True)

    # Метаданные канала
    title = Column(String(500), nullable=True)
    channel_type = Column(String(50), nullable=True)  # 'channel', 'group', 'chat'

    # Технические поля для сбора сообщений
    last_message_id = Column(BigInteger, nullable=True)  # Для offset_id
    last_collected_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship("GlobalMessage", back_populates="channel", cascade="all, delete-orphan")
    subscriptions = relationship("ChannelSubscription", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GlobalChannel {self.username or self.tg_id}>"


# Дополнительные индексы создаются в миграции
