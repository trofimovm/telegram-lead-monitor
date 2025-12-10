"""
Internal API для отправки Telegram уведомлений.
Используется worker'ом для делегирования отправки уведомлений backend процессу.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

from app.services.telegram_bot_service import telegram_bot_service

router = APIRouter()


class TelegramNotificationRequest(BaseModel):
    """Запрос на отправку Telegram уведомления о новом лиде"""
    chat_id: int
    lead_id: str
    rule_name: str
    source_title: str
    message_preview: str
    lead_url: str
    score: float
    message_link: str = ""  # Ссылка на оригинальное сообщение в Telegram


@router.post("/send-notification")
async def send_telegram_notification(req: TelegramNotificationRequest):
    """
    Internal endpoint: Worker → Backend для отправки Telegram уведомления.

    Этот endpoint вызывается из worker процесса, который не имеет доступа
    к telegram_bot_service (бот запускается только в backend процессе).
    """
    try:
        # Создать минимальный Lead object для совместимости с telegram_bot_service
        class FakeLead:
            def __init__(self, lead_id: str, score: float):
                self.id = UUID(lead_id)
                self.score = Decimal(str(score))

        lead = FakeLead(req.lead_id, req.score)

        # Вызвать telegram_bot_service напрямую
        await telegram_bot_service.send_new_lead_notification(
            chat_id=req.chat_id,
            lead=lead,
            rule_name=req.rule_name,
            source_title=req.source_title,
            message_preview=req.message_preview,
            lead_url=req.lead_url,
            message_link=req.message_link
        )

        return {"status": "sent", "chat_id": req.chat_id, "lead_id": req.lead_id}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send Telegram notification: {str(e)}"
        )
