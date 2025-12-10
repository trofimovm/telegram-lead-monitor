"""
Скрипт миграции данных из старой архитектуры в новую глобальную архитектуру.

Миграция выполняет:
1. sources → global_channels + channel_subscriptions
2. messages → global_messages
3. leads.message_id → leads.global_message_id

ВАЖНО: Запускать только один раз после применения миграции БД!
"""
import logging
import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime

# Добавляем путь к app в PYTHONPATH
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.source import Source
from app.models.message import Message
from app.models.lead import Lead
from app.models.global_channel import GlobalChannel
from app.models.global_message import GlobalMessage
from app.models.channel_subscription import ChannelSubscription

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_sources_to_global_channels(db: Session) -> dict:
    """
    Мигрирует sources → global_channels + channel_subscriptions.

    Returns:
        {
            "channels_created": int,
            "subscriptions_created": int,
            "channel_mapping": dict  # source.tg_id → global_channel.id
        }
    """
    logger.info("="*80)
    logger.info("STAGE 1: Migrating sources to global_channels + channel_subscriptions")
    logger.info("="*80)

    stats = {
        "channels_created": 0,
        "subscriptions_created": 0,
        "channel_mapping": {}  # tg_id → global_channel.id
    }

    # Получить все sources
    sources = db.query(Source).all()
    logger.info(f"Found {len(sources)} sources to migrate")

    for source in sources:
        try:
            # Найти или создать global_channel
            global_channel = db.query(GlobalChannel).filter(
                GlobalChannel.tg_id == source.tg_id
            ).first()

            if not global_channel:
                # Создать новый global_channel
                global_channel = GlobalChannel(
                    tg_id=source.tg_id,
                    username=source.username,
                    title=source.title,
                    channel_type=source.type,
                    is_active=True,  # Активируем если хоть один source активен
                    created_at=source.created_at
                )
                db.add(global_channel)
                db.flush()  # Получить ID

                stats["channels_created"] += 1
                logger.info(f"Created global_channel: {global_channel.username or global_channel.tg_id}")

            # Сохранить mapping для миграции messages
            stats["channel_mapping"][source.tg_id] = global_channel.id

            # Создать channel_subscription для этого source
            existing_subscription = db.query(ChannelSubscription).filter(
                ChannelSubscription.tenant_id == source.tenant_id,
                ChannelSubscription.channel_id == global_channel.id
            ).first()

            if not existing_subscription:
                subscription = ChannelSubscription(
                    tenant_id=source.tenant_id,
                    channel_id=global_channel.id,
                    telegram_account_id=source.telegram_account_id,
                    is_active=source.is_active,
                    tags=source.tags if hasattr(source, 'tags') else [],
                    created_at=source.created_at,
                    updated_at=source.updated_at if hasattr(source, 'updated_at') else datetime.utcnow()
                )
                db.add(subscription)
                stats["subscriptions_created"] += 1
                logger.debug(f"Created subscription: tenant={source.tenant_id} → channel={global_channel.id}")

            db.commit()

        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Integrity error for source {source.id}: {str(e)}")
            continue
        except Exception as e:
            db.rollback()
            logger.error(f"Error migrating source {source.id}: {str(e)}", exc_info=True)
            continue

    logger.info(f"Sources migration complete: {stats['channels_created']} channels, {stats['subscriptions_created']} subscriptions created")
    return stats


def migrate_messages_to_global_messages(db: Session, channel_mapping: dict) -> dict:
    """
    Мигрирует messages → global_messages.

    Args:
        channel_mapping: Dict[tg_id → global_channel.id]

    Returns:
        {
            "messages_migrated": int,
            "message_mapping": dict  # old_message.id → global_message.id
        }
    """
    logger.info("="*80)
    logger.info("STAGE 2: Migrating messages to global_messages")
    logger.info("="*80)

    stats = {
        "messages_migrated": 0,
        "message_mapping": {},  # old_message_id → global_message_id
        "duplicates_skipped": 0
    }

    # Получить все messages
    messages = db.query(Message).all()
    logger.info(f"Found {len(messages)} messages to migrate")

    batch_size = 1000
    batch_count = 0

    for i, message in enumerate(messages, 1):
        try:
            # Получить source для этого сообщения
            source = db.query(Source).filter(Source.id == message.source_id).first()
            if not source:
                logger.warning(f"Source not found for message {message.id}, skipping")
                continue

            # Найти соответствующий global_channel
            global_channel_id = channel_mapping.get(source.tg_id)
            if not global_channel_id:
                logger.warning(f"Global channel not found for tg_id={source.tg_id}, skipping message {message.id}")
                continue

            # Проверить существование global_message
            existing_global_msg = db.query(GlobalMessage).filter(
                GlobalMessage.channel_id == global_channel_id,
                GlobalMessage.tg_message_id == message.tg_message_id
            ).first()

            if existing_global_msg:
                # Сообщение уже существует (дубликат от другого source)
                stats["duplicates_skipped"] += 1
                # Сохраняем mapping для миграции leads
                stats["message_mapping"][message.id] = existing_global_msg.id
                continue

            # Создать global_message
            global_message = GlobalMessage(
                channel_id=global_channel_id,
                tg_message_id=message.tg_message_id,
                text=message.text,
                author_tg_id=message.author_tg_id if hasattr(message, 'author_tg_id') else None,
                author_username=message.author_username if hasattr(message, 'author_username') else None,
                media_type=message.media_type if hasattr(message, 'media_type') else None,
                sent_at=message.sent_at,
                created_at=message.created_at
            )

            db.add(global_message)
            db.flush()  # Получить ID

            # Сохранить mapping
            stats["message_mapping"][message.id] = global_message.id
            stats["messages_migrated"] += 1

            # Commit батчами для производительности
            batch_count += 1
            if batch_count >= batch_size:
                db.commit()
                batch_count = 0
                logger.info(f"Progress: {i}/{len(messages)} messages processed ({stats['messages_migrated']} migrated, {stats['duplicates_skipped']} duplicates)")

        except IntegrityError:
            db.rollback()
            batch_count = 0
            stats["duplicates_skipped"] += 1
            logger.debug(f"Duplicate message skipped: {message.id}")
            continue
        except Exception as e:
            db.rollback()
            batch_count = 0
            logger.error(f"Error migrating message {message.id}: {str(e)}", exc_info=True)
            continue

    # Final commit
    if batch_count > 0:
        db.commit()

    logger.info(
        f"Messages migration complete: {stats['messages_migrated']} migrated, "
        f"{stats['duplicates_skipped']} duplicates skipped"
    )
    return stats


def migrate_leads_to_global_messages(db: Session, message_mapping: dict) -> dict:
    """
    Обновляет leads: message_id → global_message_id.

    Args:
        message_mapping: Dict[old_message_id → global_message_id]

    Returns:
        {
            "leads_updated": int
        }
    """
    logger.info("="*80)
    logger.info("STAGE 3: Updating leads with global_message_id")
    logger.info("="*80)

    stats = {
        "leads_updated": 0,
        "leads_skipped": 0
    }

    # Получить все leads
    leads = db.query(Lead).all()
    logger.info(f"Found {len(leads)} leads to update")

    batch_size = 1000
    batch_count = 0

    for i, lead in enumerate(leads, 1):
        try:
            if not lead.message_id:
                stats["leads_skipped"] += 1
                continue

            # Найти соответствующий global_message
            global_message_id = message_mapping.get(lead.message_id)
            if not global_message_id:
                logger.warning(f"Global message not found for lead {lead.id} (message_id={lead.message_id})")
                stats["leads_skipped"] += 1
                continue

            # Обновить lead
            lead.global_message_id = global_message_id
            stats["leads_updated"] += 1

            # Commit батчами
            batch_count += 1
            if batch_count >= batch_size:
                db.commit()
                batch_count = 0
                logger.info(f"Progress: {i}/{len(leads)} leads processed ({stats['leads_updated']} updated)")

        except Exception as e:
            db.rollback()
            batch_count = 0
            logger.error(f"Error updating lead {lead.id}: {str(e)}", exc_info=True)
            continue

    # Final commit
    if batch_count > 0:
        db.commit()

    logger.info(f"Leads migration complete: {stats['leads_updated']} updated, {stats['leads_skipped']} skipped")
    return stats


def main():
    """Главная функция миграции."""
    logger.info("="*80)
    logger.info("STARTING DATA MIGRATION TO GLOBAL ARCHITECTURE")
    logger.info("="*80)

    # Создать database session
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Stage 1: Sources → GlobalChannels + ChannelSubscriptions
        sources_stats = migrate_sources_to_global_channels(db)

        # Stage 2: Messages → GlobalMessages
        messages_stats = migrate_messages_to_global_messages(db, sources_stats["channel_mapping"])

        # Stage 3: Update Leads with global_message_id
        leads_stats = migrate_leads_to_global_messages(db, messages_stats["message_mapping"])

        # Final summary
        logger.info("="*80)
        logger.info("MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        logger.info(f"Global Channels Created: {sources_stats['channels_created']}")
        logger.info(f"Channel Subscriptions Created: {sources_stats['subscriptions_created']}")
        logger.info(f"Global Messages Migrated: {messages_stats['messages_migrated']}")
        logger.info(f"Duplicates Skipped: {messages_stats['duplicates_skipped']}")
        logger.info(f"Leads Updated: {leads_stats['leads_updated']}")
        logger.info("="*80)

        logger.info("\nNext steps:")
        logger.info("1. Verify data integrity in global tables")
        logger.info("2. Test the new MessageCollectorWorkerV2")
        logger.info("3. Once confirmed working, you can archive old tables (messages, sources)")

    except Exception as e:
        logger.error(f"CRITICAL ERROR during migration: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
