"""
Telegram Bot Webhook endpoint.
Receives updates from Telegram via POST requests.
"""

import logging
import hmac
from fastapi import APIRouter, Request, HTTPException, Header
from telegram import Update

from app.config import settings
from app.services.telegram_bot_service import telegram_bot_service

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_telegram_signature(token: str, signature: str) -> bool:
    """
    Verify request came from Telegram using secret token.

    Telegram sends X-Telegram-Bot-Api-Secret-Token header.
    """
    if not signature:
        return False
    return hmac.compare_digest(token, signature)


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    """
    Webhook endpoint for Telegram updates.

    Security:
    - Validates secret token in header
    - Returns 403 for invalid signatures

    Flow:
    1. Verify signature
    2. Parse Update object
    3. Process with telegram_bot_service
    4. Return 200 OK
    """

    # Verify signature
    if settings.TELEGRAM_WEBHOOK_SECRET and not verify_telegram_signature(
        settings.TELEGRAM_WEBHOOK_SECRET,
        x_telegram_bot_api_secret_token
    ):
        logger.warning("Invalid Telegram webhook signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse and process update
    try:
        update_data = await request.json()
        update = Update.de_json(update_data, telegram_bot_service.bot)

        await telegram_bot_service.process_update(update)

        return {"ok": True}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        # Return 200 to prevent Telegram retries
        return {"ok": False, "error": str(e)}
