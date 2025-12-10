"""
Global Message Collector Service - собирает сообщения из глобальных каналов.
Один канал = один fetch запрос, независимо от количества tenants.
"""
import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.global_channel import GlobalChannel
from app.models.global_message import GlobalMessage
from app.models.telegram_account import TelegramAccount
from app.services.telegram_service import telegram_service

logger = logging.getLogger(__name__)


class GlobalMessageCollector:
    """
    Сервис для сбора сообщений из глобальных каналов.
    Собирает сообщения ОДИН раз для всей системы, независимо от tenants.
    """

    async def collect_global_messages(self, db: Session) -> Dict[str, Any]:
        """
        Собирает сообщения из всех активных глобальных каналов.

        Returns:
            Dict с статистикой:
            {
                "channels_processed": int,
                "messages_collected": int,
                "errors": []
            }
        """
        # Получить все активные глобальные каналы
        channels = db.query(GlobalChannel).filter(
            GlobalChannel.is_active == True
        ).all()

        logger.info(f"Found {len(channels)} active global channels to process")

        stats = {
            "channels_processed": 0,
            "messages_collected": 0,
            "errors": []
        }

        for channel in channels:
            try:
                logger.info(f"Processing channel: {channel.username or channel.tg_id}")

                # Получить последний message_id для offset
                last_message = db.query(GlobalMessage).filter(
                    GlobalMessage.channel_id == channel.id
                ).order_by(GlobalMessage.tg_message_id.desc()).first()

                offset_id = last_message.tg_message_id if last_message else 0

                # Получить любой активный Telegram аккаунт для fetch
                # (не важно какой, главное что активный)
                telegram_account = db.query(TelegramAccount).filter(
                    TelegramAccount.status == "active"
                ).first()

                if not telegram_account:
                    logger.error("No active Telegram accounts available")
                    stats["errors"].append({
                        "channel_id": str(channel.id),
                        "error": "No active Telegram accounts"
                    })
                    continue

                # Fetch сообщений из Telegram (ОДИН раз для всех tenants!)
                channel_identifier = f"@{channel.username}" if channel.username else channel.tg_id

                try:
                    telegram_messages = await telegram_service.get_channel_messages(
                        telegram_account.session_encrypted,
                        channel_identifier,
                        limit=100,
                        offset_id=offset_id
                    )
                except Exception as e:
                    logger.error(f"Failed to fetch messages from Telegram: {str(e)}")
                    stats["errors"].append({
                        "channel_id": str(channel.id),
                        "channel_identifier": str(channel_identifier),
                        "error": str(e)
                    })
                    continue

                # Сохранить сообщения в global_messages
                new_messages_count = 0
                for tg_msg in telegram_messages:
                    try:
                        # Извлечь author info
                        author_tg_id = None
                        author_username = None
                        if tg_msg.get("author"):
                            author_tg_id = tg_msg["author"].get("id")
                            author_username = tg_msg["author"].get("username")

                        # Создать global message
                        message = GlobalMessage(
                            channel_id=channel.id,
                            tg_message_id=tg_msg["id"],
                            text=tg_msg.get("text"),
                            author_tg_id=author_tg_id,
                            author_username=author_username,
                            media_type=None,  # TODO: parse media type
                            sent_at=datetime.fromisoformat(tg_msg["date"]),
                        )

                        db.add(message)
                        db.flush()  # Проверить UNIQUE constraint
                        new_messages_count += 1

                    except IntegrityError:
                        # Дубликат - это нормально, просто пропускаем
                        db.rollback()
                        logger.debug(f"Message {tg_msg['id']} already exists in channel {channel.id}")
                        continue
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Failed to save message {tg_msg.get('id')}: {str(e)}")
                        continue

                # Commit всех новых сообщений
                if new_messages_count > 0:
                    try:
                        db.commit()
                        logger.info(f"Saved {new_messages_count} new messages from channel {channel.username or channel.tg_id}")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Failed to commit messages: {str(e)}")
                        stats["errors"].append({
                            "channel_id": str(channel.id),
                            "error": f"Commit failed: {str(e)}"
                        })
                        continue

                # Обновить last_collected_at
                channel.last_collected_at = datetime.utcnow()
                if new_messages_count > 0:
                    channel.last_message_id = telegram_messages[0]["id"]  # Первое сообщение = самое новое

                db.commit()

                stats["channels_processed"] += 1
                stats["messages_collected"] += new_messages_count

            except Exception as e:
                logger.error(f"Error processing channel {channel.id}: {str(e)}", exc_info=True)
                stats["errors"].append({
                    "channel_id": str(channel.id),
                    "error": str(e)
                })

        logger.info(
            f"Global message collection completed: "
            f"processed {stats['channels_processed']} channels, "
            f"collected {stats['messages_collected']} messages"
        )

        return stats


# Глобальный экземпляр сервиса
global_message_collector = GlobalMessageCollector()
