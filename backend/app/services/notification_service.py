"""
Notification Service для создания и отправки уведомлений.
Используется Rule Processor'ом и другими частями системы.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.lead import Lead
from app.models.rule import Rule
from app.models.global_message import GlobalMessage
from app.models.global_channel import GlobalChannel
from app.services.email_service import email_service
from app.services.telegram_bot_service import telegram_bot_service
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Сервис для создания уведомлений.

    Поддерживает:
    - Создание in-app уведомлений
    - Отправку email уведомлений (если включено в настройках пользователя)
    - Различные типы уведомлений (новый лид, изменение статуса, назначение)
    """

    async def create_new_lead_notification(
        self,
        db: Session,
        lead: Lead,
        user: User,
    ) -> Optional[Notification]:
        """
        Создать уведомление о новом лиде.

        Args:
            db: Database session
            lead: Lead объект (должен иметь загруженные relationships: global_message, rule, global_message.channel)
            user: User объект, который получит уведомление

        Returns:
            Notification объект или None если уведомления отключены
        """
        # Проверить настройки пользователя
        if not user.notify_on_new_lead:
            return None

        # Получить связанные данные
        rule = lead.rule
        global_message = lead.global_message
        channel = global_message.channel if global_message else None

        # Создать заголовок и текст
        title = f"New Lead Found: {rule.name}"
        message_text = f"A new lead matching rule '{rule.name}' has been found in {channel.title if channel else 'unknown channel'} with {int(lead.score * 100)}% confidence."

        # Создать in-app уведомление если включено
        notification = None
        if user.in_app_notifications_enabled:
            notification = Notification(
                tenant_id=user.id,
                type=NotificationType.LEAD_CREATED,
                title=title,
                message=message_text,
                related_lead_id=lead.id,
                is_read=False,
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            logger.info(f"Created in-app notification for user {user.id}: {title}")

        # Отправить email если включено
        if user.email_notifications_enabled:
            try:
                await email_service.send_new_lead_notification(
                    to_email=user.email,
                    user_name=user.full_name,
                    lead_id=str(lead.id),
                    lead_score=float(lead.score),
                    lead_reasoning=lead.reasoning or "No reasoning provided",
                    rule_name=rule.name,
                    source_title=channel.title if channel else "Unknown channel",
                    message_preview=global_message.text[:500] if global_message and global_message.text else "No message text",
                )
                logger.info(f"Sent email notification to {user.email}: {title}")
            except Exception as e:
                logger.error(f"Failed to send email notification to {user.email}: {str(e)}")

        # Отправить Telegram уведомление если включено
        if user.telegram_bot_enabled and user.telegram_chat_id:
            try:
                lead_url = f"{settings.FRONTEND_URL}/dashboard/leads?lead_id={lead.id}"

                # Получить ссылку на оригинальное сообщение
                message_link = global_message.get_telegram_link() if global_message else ""

                # HTTP POST к backend endpoint (worker не имеет прямого доступа к telegram_bot_service)
                import httpx
                backend_url = getattr(settings, 'BACKEND_URL', 'http://backend:8000')

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{backend_url}/api/internal/telegram/send-notification",
                        json={
                            "chat_id": user.telegram_chat_id,
                            "lead_id": str(lead.id),
                            "rule_name": rule.name,
                            "source_title": channel.title if channel else "Unknown channel",
                            "message_preview": global_message.text if global_message and global_message.text else "No message text",
                            "lead_url": lead_url,
                            "score": float(lead.score),
                            "message_link": message_link
                        },
                        timeout=10.0
                    )
                    response.raise_for_status()

                logger.info(f"Sent Telegram notification request to backend for user {user.id}")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification to user {user.id}: {str(e)}", exc_info=True)

        return notification

    async def create_lead_status_change_notification(
        self,
        db: Session,
        lead: Lead,
        user: User,
        old_status: str,
        new_status: str,
    ) -> Optional[Notification]:
        """
        Создать уведомление об изменении статуса лида.

        Args:
            db: Database session
            lead: Lead объект
            user: User объект, который получит уведомление
            old_status: Старый статус
            new_status: Новый статус

        Returns:
            Notification объект или None если уведомления отключены
        """
        # Проверить настройки пользователя
        if not user.notify_on_lead_status_change:
            return None

        # Создать заголовок и текст
        title = f"Lead Status Changed: {old_status} → {new_status}"
        message_text = f"The status of lead '{lead.rule.name}' has been changed from {old_status} to {new_status}."

        # Создать in-app уведомление если включено
        notification = None
        if user.in_app_notifications_enabled:
            notification = Notification(
                tenant_id=user.id,
                type=NotificationType.LEAD_STATUS_CHANGED,
                title=title,
                message=message_text,
                related_lead_id=lead.id,
                is_read=False,
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            logger.info(f"Created in-app notification for user {user.id}: {title}")

        # Отправить email если включено
        if user.email_notifications_enabled:
            try:
                await email_service.send_lead_status_change_notification(
                    to_email=user.email,
                    user_name=user.full_name,
                    lead_id=str(lead.id),
                    old_status=old_status,
                    new_status=new_status,
                    rule_name=lead.rule.name,
                )
                logger.info(f"Sent email notification to {user.email}: {title}")
            except Exception as e:
                logger.error(f"Failed to send email notification to {user.email}: {str(e)}")

        return notification

    async def create_lead_assignment_notification(
        self,
        db: Session,
        lead: Lead,
        assignee: User,
    ) -> Optional[Notification]:
        """
        Создать уведомление о назначении лида на пользователя.

        Args:
            db: Database session
            lead: Lead объект
            assignee: User объект, на которого назначен лид

        Returns:
            Notification объект или None если уведомления отключены
        """
        # Проверить настройки пользователя
        if not assignee.notify_on_lead_assignment:
            return None

        # Получить связанные данные
        rule = lead.rule
        global_message = lead.global_message
        channel = global_message.channel if global_message else None

        # Создать заголовок и текст
        title = f"Lead Assigned to You: {rule.name}"
        message_text = f"A lead from {channel.title if channel else 'unknown channel'} has been assigned to you."

        # Создать in-app уведомление если включено
        notification = None
        if assignee.in_app_notifications_enabled:
            notification = Notification(
                tenant_id=assignee.id,
                type=NotificationType.LEAD_ASSIGNED,
                title=title,
                message=message_text,
                related_lead_id=lead.id,
                is_read=False,
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            logger.info(f"Created in-app notification for user {assignee.id}: {title}")

        # Отправить email если включено
        if assignee.email_notifications_enabled:
            try:
                await email_service.send_lead_assignment_notification(
                    to_email=assignee.email,
                    user_name=assignee.full_name,
                    lead_id=str(lead.id),
                    rule_name=rule.name,
                    source_title=channel.title if channel else "Unknown channel",
                )
                logger.info(f"Sent email notification to {assignee.email}: {title}")
            except Exception as e:
                logger.error(f"Failed to send email notification to {assignee.email}: {str(e)}")

        return notification


# Singleton instance
notification_service = NotificationService()
