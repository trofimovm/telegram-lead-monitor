"""
Telegram Bot Service для отправки уведомлений о новых лидах.
Использует python-telegram-bot для работы с Bot API.
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.database import get_session_local

logger = logging.getLogger(__name__)


class TelegramBotService:
    """
    Сервис для работы с Telegram ботом.

    Функции:
    - Запуск/остановка бота вместе с backend
    - Обработка команд /start и /verify
    - Генерация и проверка кодов верификации
    - Отправка уведомлений о новых лидах
    """

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None

    # === Lifecycle ===

    async def start_bot(self):
        """
        Initialize bot and register webhook.
        NON-BLOCKING, IDEMPOTENT operation.
        """
        print("=== Initializing Telegram bot (webhook mode) ===", flush=True)
        logger.info("Initializing Telegram bot (webhook mode)")

        if not settings.TELEGRAM_BOT_TOKEN:
            print("TELEGRAM_BOT_TOKEN not set, bot will not start", flush=True)
            logger.warning("TELEGRAM_BOT_TOKEN not set")
            return

        try:
            # Build application (NO UPDATER!)
            self.application = (
                Application.builder()
                .token(settings.TELEGRAM_BOT_TOKEN)
                .build()
            )

            # Add command handlers
            from telegram.ext import CommandHandler
            print("Adding command handlers...", flush=True)
            self.application.add_handler(CommandHandler("start", self._cmd_start))
            self.application.add_handler(CommandHandler("verify", self._cmd_verify))

            # Initialize (creates bot, handlers, etc.)
            print("Initializing application...", flush=True)
            await self.application.initialize()

            # Use the initialized bot from application
            self.bot = self.application.bot

            # Register webhook (non-critical - may already be set by another replica)
            webhook_url = f"{settings.BACKEND_PUBLIC_URL}/api/v1/telegram/webhook"

            try:
                print(f"Registering webhook: {webhook_url}", flush=True)

                success = await self.bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True,  # Clear old updates
                    secret_token=settings.TELEGRAM_WEBHOOK_SECRET
                )

                if success:
                    print("✅ Telegram webhook registered!", flush=True)
                    logger.info("Webhook registered successfully")

                    # Verify
                    webhook_info = await self.bot.get_webhook_info()
                    print(f"Webhook URL: {webhook_info.url}", flush=True)
                    logger.info(f"Webhook info: {webhook_info}")
                else:
                    print("⚠️ Webhook registration returned false (may already be set)", flush=True)
                    logger.warning("Webhook registration returned false")

            except Exception as webhook_error:
                # Don't crash on webhook errors - it may already be registered by another replica
                print(f"⚠️ Webhook registration failed (non-critical): {webhook_error}", flush=True)
                logger.warning(f"Webhook registration failed (non-critical): {webhook_error}")

                # Try to get current webhook info to verify it's set
                try:
                    webhook_info = await self.bot.get_webhook_info()
                    if webhook_info.url:
                        print(f"✅ Webhook already registered: {webhook_info.url}", flush=True)
                        logger.info(f"Webhook already registered: {webhook_info.url}")
                    else:
                        print(f"⚠️ No webhook currently registered", flush=True)
                        logger.warning("No webhook currently registered")
                except Exception as info_error:
                    logger.warning(f"Could not retrieve webhook info: {info_error}")

        except Exception as e:
            print(f"❌ Bot init failed: {str(e)}", flush=True)
            logger.error(f"Bot init failed: {e}", exc_info=True)

    async def stop_bot(self):
        """
        Cleanup bot resources WITHOUT deleting webhook.

        IMPORTANT: Do NOT delete webhook on shutdown!
        In multi-replica deployment, deleting webhook on one pod shutdown
        breaks the webhook for all other pods.

        Webhook persists until explicitly deleted or replaced.
        """
        print("=== Stopping Telegram bot (keeping webhook) ===", flush=True)
        logger.info("Stopping Telegram bot (keeping webhook)")

        # NOTE: We intentionally do NOT delete the webhook here.
        # In K8s with multiple replicas, deleting webhook on one pod's shutdown
        # would break the bot for all other pods.

        if self.application:
            try:
                await self.application.shutdown()
                print("✅ Application shutdown complete", flush=True)
                logger.info("Application shutdown complete")
            except Exception as e:
                logger.error(f"Shutdown error: {e}", exc_info=True)

    async def process_update(self, update: Update):
        """
        Process incoming update from webhook.
        Called by webhook endpoint for each Telegram update.
        """
        try:
            await self.application.process_update(update)
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)

    # === Verification ===

    def generate_verification_code(self) -> str:
        """Генерирует 6-значный буквенно-цифровой код."""
        return secrets.token_urlsafe(4)[:6].upper()

    def create_verification_code(self, user: User, db: Session) -> str:
        """
        Создает и сохраняет код верификации для пользователя.

        Args:
            user: Пользователь
            db: Database session

        Returns:
            Сгенерированный код
        """
        code = self.generate_verification_code()
        user.telegram_verification_code = code
        user.telegram_verification_expires = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
        logger.info(f"Created verification code for user {user.id}")
        return code

    def verify_code(self, user: User, code: str, chat_id: str, db: Session) -> bool:
        """
        Проверяет код верификации и привязывает chat_id к пользователю.

        Args:
            user: Пользователь
            code: Код верификации
            chat_id: Telegram Chat ID
            db: Database session

        Returns:
            True если верификация успешна, False иначе
        """
        # Проверяем наличие кода
        if not user.telegram_verification_code:
            logger.warning(f"User {user.id} has no verification code")
            return False

        # Проверяем срок действия
        if user.telegram_verification_expires < datetime.utcnow():
            logger.warning(f"Verification code expired for user {user.id}")
            return False

        # Проверяем совпадение
        if user.telegram_verification_code != code.upper():
            logger.warning(f"Invalid verification code for user {user.id}")
            return False

        # Успешная верификация - привязываем chat_id
        user.telegram_chat_id = chat_id
        user.telegram_verification_code = None
        user.telegram_verification_expires = None
        db.commit()

        logger.info(f"Successfully verified Telegram for user {user.id}, chat_id: {chat_id}")
        return True

    # === Bot Commands ===

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start."""
        chat_id = update.effective_chat.id

        message = (
            "👋 Welcome to Telegram Lead Monitor!\n\n"
            f"Your Chat ID: {chat_id}\n\n"
            "To connect your account:\n"
            "1. Copy your Chat ID above\n"
            "2. Go to Settings in web app\n"
            "3. Click 'Connect Telegram Bot' to generate verification code\n"
            "4. Paste your Chat ID and click 'Verify & Connect'\n"
            "5. Enable Telegram notifications\n\n"
            "Or use command: /verify YOUR_CODE"
        )

        await update.message.reply_text(message)
        logger.info(f"User started bot, chat_id: {chat_id}")

    async def _cmd_verify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /verify CODE."""
        if not context.args:
            await update.message.reply_text("Usage: /verify YOUR_CODE")
            return

        code = context.args[0].upper()
        chat_id = str(update.effective_chat.id)

        # Найти пользователя по коду в БД
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                User.telegram_verification_code == code,
                User.telegram_verification_expires > datetime.utcnow()
            ).first()

            if not user:
                await update.message.reply_text(
                    "❌ Invalid or expired code. Generate a new one in Settings."
                )
                return

            # Привязать chat_id
            user.telegram_chat_id = chat_id
            user.telegram_verification_code = None
            user.telegram_verification_expires = None
            db.commit()

            await update.message.reply_text(
                "✅ Successfully connected!\n\n"
                "Go to Settings to enable Telegram notifications."
            )
            logger.info(f"User {user.id} verified via /verify command, chat_id: {chat_id}")

        except Exception as e:
            logger.error(f"Error in /verify command: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred. Please try again or contact support."
            )
        finally:
            db.close()

    # === Send Notifications ===

    async def send_new_lead_notification(
        self,
        chat_id: str,
        lead,
        rule_name: str,
        source_title: str,
        message_preview: str,
        lead_url: str,
        message_link: str = ""
    ):
        """
        Отправляет уведомление о новом лиде в Telegram.

        Args:
            chat_id: Telegram Chat ID пользователя
            lead: Lead object
            rule_name: Название сработавшего правила
            source_title: Название источника
            message_preview: Превью сообщения
            lead_url: Ссылка на лид в дашборде
            message_link: Ссылка на оригинальное сообщение в Telegram
        """
        if not self.bot:
            self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            # Форматирование
            score_percent = int(float(lead.score) * 100)
            preview = message_preview[:300] + "..." if len(message_preview) > 300 else message_preview

            text = (
                f"🎯 *New Lead Found!*\n\n"
                f"*Rule:* {rule_name}\n"
                f"*Source:* {source_title}\n"
                f"*Score:* {score_percent}%\n\n"
                f"*Message Preview:*\n"
                f"{preview}"
            )

            # Создать inline кнопки
            keyboard = [[InlineKeyboardButton("📊 View Lead in Dashboard", url=lead_url)]]

            # Добавить кнопку для оригинального сообщения если ссылка есть
            if message_link:
                keyboard.append([InlineKeyboardButton("📨 View Original Message", url=message_link)])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

            logger.info(f"Sent Telegram notification to chat_id {chat_id} for lead {lead.id}")

        except Exception as e:
            logger.error(
                f"Failed to send Telegram notification to chat_id {chat_id}: {str(e)}",
                exc_info=True
            )


# Глобальный экземпляр
telegram_bot_service = TelegramBotService()
