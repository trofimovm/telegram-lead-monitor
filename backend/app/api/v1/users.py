"""
API endpoints для управления пользователями и их настройками.
Включает: профиль пользователя, настройки уведомлений.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    TelegramBotInfo,
    TelegramVerificationCodeResponse,
    TelegramVerifyRequest,
    TelegramVerifyResponse,
    TelegramDisconnectResponse,
)
from app.schemas.auth import UserResponse
from app.api.deps import get_current_active_user as get_current_user
from app.services.telegram_bot_service import telegram_bot_service
from app.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Получить профиль текущего пользователя.
    """
    return current_user


@router.get("/me/notification-preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
):
    """
    Получить настройки уведомлений текущего пользователя.
    """
    return NotificationPreferencesResponse(
        email_notifications_enabled=current_user.email_notifications_enabled,
        in_app_notifications_enabled=current_user.in_app_notifications_enabled,
        telegram_bot_enabled=current_user.telegram_bot_enabled,
        notify_on_new_lead=current_user.notify_on_new_lead,
        notify_on_lead_status_change=current_user.notify_on_lead_status_change,
        notify_on_lead_assignment=current_user.notify_on_lead_assignment,
    )


@router.patch("/me/notification-preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    data: NotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить настройки уведомлений текущего пользователя.
    """
    # Обновить поля
    current_user.email_notifications_enabled = data.email_notifications_enabled
    current_user.in_app_notifications_enabled = data.in_app_notifications_enabled
    current_user.telegram_bot_enabled = data.telegram_bot_enabled
    current_user.notify_on_new_lead = data.notify_on_new_lead
    current_user.notify_on_lead_status_change = data.notify_on_lead_status_change
    current_user.notify_on_lead_assignment = data.notify_on_lead_assignment

    db.commit()
    db.refresh(current_user)

    return NotificationPreferencesResponse(
        email_notifications_enabled=current_user.email_notifications_enabled,
        in_app_notifications_enabled=current_user.in_app_notifications_enabled,
        telegram_bot_enabled=current_user.telegram_bot_enabled,
        notify_on_new_lead=current_user.notify_on_new_lead,
        notify_on_lead_status_change=current_user.notify_on_lead_status_change,
        notify_on_lead_assignment=current_user.notify_on_lead_assignment,
    )


# ========== Telegram Bot Endpoints ==========

@router.get("/me/telegram-bot", response_model=TelegramBotInfo)
async def get_telegram_bot_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о подключении Telegram бота.
    """
    return TelegramBotInfo(
        bot_username=settings.TELEGRAM_BOT_USERNAME,
        is_connected=bool(current_user.telegram_chat_id),
        chat_id=current_user.telegram_chat_id
    )


@router.post("/me/telegram-bot/generate-code", response_model=TelegramVerificationCodeResponse)
async def generate_telegram_verification_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Сгенерировать код верификации для подключения Telegram.
    """
    code = telegram_bot_service.create_verification_code(current_user, db)

    return TelegramVerificationCodeResponse(
        verification_code=code,
        expires_at=current_user.telegram_verification_expires,
        bot_username=settings.TELEGRAM_BOT_USERNAME,
        instructions=(
            f"1. Open Telegram and find bot {settings.TELEGRAM_BOT_USERNAME}\n"
            "2. Send /start to get your Chat ID\n"
            "3. Copy Chat ID and verification code\n"
            "4. Return here and click 'Verify & Connect'"
        )
    )


@router.post("/me/telegram-bot/verify", response_model=TelegramVerifyResponse)
async def verify_telegram_code(
    verify_data: TelegramVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Верифицировать код и подключить Telegram.
    """
    success = telegram_bot_service.verify_code(
        user=current_user,
        code=verify_data.verification_code,
        chat_id=verify_data.chat_id,
        db=db
    )

    if success:
        return TelegramVerifyResponse(
            success=True,
            message="Successfully connected! You can now enable Telegram notifications."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )


@router.post("/me/telegram-bot/disconnect", response_model=TelegramDisconnectResponse)
async def disconnect_telegram_bot(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отключить Telegram бота.
    """
    current_user.telegram_chat_id = None
    current_user.telegram_bot_enabled = False
    db.commit()

    return TelegramDisconnectResponse(
        success=True,
        message="Telegram bot disconnected successfully"
    )
