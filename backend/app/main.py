from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.workers import message_collector_worker
from app.services.telegram_bot_service import telegram_bot_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    Запускает и останавливает фоновые задачи.
    """
    # Startup
    logger.info("Starting application...")

    # Запускаем worker V2 для сбора и анализа сообщений
    # Интервал берем из переменной окружения (по умолчанию 1 минута)
    import os
    interval = int(os.getenv('WORKER_INTERVAL_MINUTES', '1'))
    logger.info(f"Starting Message Collector Worker V2 (interval: {interval} minute(s))")
    message_collector_worker.start(interval_minutes=interval)

    # Запускаем Telegram бота для уведомлений
    await telegram_bot_service.start_bot()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    message_collector_worker.stop()
    await telegram_bot_service.stop_bot()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok"
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


@app.post("/api/admin/collect-messages")
async def trigger_message_collection():
    """
    Manually trigger message collection from all sources.
    Useful for testing and debugging.
    """
    result = await message_collector_worker.run_once()
    return result


# Include API routes
from app.api.v1 import auth, telegram, subscriptions, rules, leads, notifications, users, analytics, telegram_webhook
from app.api.internal import telegram as internal_telegram

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["telegram"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
app.include_router(rules.router, prefix="/api/v1/rules", tags=["rules"])
app.include_router(leads.router, prefix="/api/v1/leads", tags=["leads"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(telegram_webhook.router, prefix="/api/v1", tags=["telegram"])

# Internal API (for inter-service communication)
app.include_router(internal_telegram.router, prefix="/api/internal/telegram", tags=["internal"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
# Force rebuild for webhook support
