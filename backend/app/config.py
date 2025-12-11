from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Application
    APP_NAME: str = "Telegram Lead Monitor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://telegram_monitor:dev_password@localhost:5432/telegram_monitor"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Telegram API
    TELEGRAM_API_ID: int = 0  # Get from https://my.telegram.org
    TELEGRAM_API_HASH: str = ""  # Get from https://my.telegram.org

    # Encryption (Fernet key for Telegram sessions)
    ENCRYPTION_KEY: str = ""  # Generate using: Fernet.generate_key().decode()

    # LLM Integration
    LLM_API_URL: str = "https://llm.codenrock.com"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT: int = 30

    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Telegram Lead Monitor"

    # Frontend URL (for email verification links)
    FRONTEND_URL: str = "http://localhost:3002"

    # Backend URL (for internal API calls from worker)
    BACKEND_URL: str = "http://backend:8000"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3002"]

    # Verification Token
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # Telegram Bot settings
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""

    # Telegram Bot Webhook configuration
    BACKEND_PUBLIC_URL: str = "https://tgcatch.ru"
    TELEGRAM_WEBHOOK_SECRET: str = ""


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


settings = get_settings()
