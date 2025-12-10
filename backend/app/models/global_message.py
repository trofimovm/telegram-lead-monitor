"""
GlobalMessage model - глобальное хранилище сообщений для всех tenants.
Одно сообщение = одна запись, независимо от количества пользователей.
"""
from sqlalchemy import Column, String, BigInteger, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class GlobalMessage(Base):
    """
    Глобальное сообщение из Telegram канала.
    Хранится один раз для всей системы, независимо от tenants.
    """
    __tablename__ = "global_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Связь с каналом
    channel_id = Column(UUID(as_uuid=True), ForeignKey("global_channels.id", ondelete="CASCADE"), nullable=False)

    # Telegram ID сообщения
    tg_message_id = Column(BigInteger, nullable=False)

    # Контент сообщения
    text = Column(Text, nullable=True)
    author_tg_id = Column(BigInteger, nullable=True)
    author_username = Column(String(255), nullable=True)
    media_type = Column(String(50), nullable=True)

    # Временные метки
    sent_at = Column(DateTime, nullable=False)  # Когда отправлено в Telegram
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Когда собрано в нашу БД

    # Relationships
    channel = relationship("GlobalChannel", back_populates="messages")
    leads = relationship("Lead", back_populates="global_message")

    # UNIQUE constraint - одна комбинация (channel_id, tg_message_id)
    __table_args__ = (
        UniqueConstraint('channel_id', 'tg_message_id', name='uq_global_messages_channel_tg_id'),
        Index('idx_global_messages_channel', 'channel_id'),
        Index('idx_global_messages_sent_at', 'sent_at'),
    )

    def __repr__(self):
        return f"<GlobalMessage {self.tg_message_id} from channel {self.channel_id}>"

    def get_telegram_link(self) -> str:
        """
        Генерирует ссылку на оригинальное сообщение в Telegram.

        Returns:
            URL в формате:
            - https://t.me/channel_username/message_id (для публичных)
            - https://t.me/c/channel_id/message_id (для приватных)
        """
        if not self.channel:
            return ""

        # Публичный канал (есть username)
        if self.channel.username:
            return f"https://t.me/{self.channel.username}/{self.tg_message_id}"

        # Приватный канал (только tg_id)
        # Убираем префикс -100 из channel_id для формата t.me/c/
        channel_id = str(abs(self.channel.tg_id))
        if self.channel.tg_id < 0 and channel_id.startswith('100'):
            channel_id = channel_id[3:]

        return f"https://t.me/c/{channel_id}/{self.tg_message_id}"
