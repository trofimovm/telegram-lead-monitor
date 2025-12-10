from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    EmailVerificationRequest,
    ResendVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    RefreshTokenRequest,
)

from app.schemas.telegram import (
    TelegramAccountStartAuth,
    TelegramAccountVerifyCode,
    TelegramAccountResponse,
    TelegramAccountDetail,
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    DialogInfo,
    MessageResponse,
    TelegramMessageInfo,
)

__all__ = [
    # Auth
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "EmailVerificationRequest",
    "ResendVerificationRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "RefreshTokenRequest",
    # Telegram
    "TelegramAccountStartAuth",
    "TelegramAccountVerifyCode",
    "TelegramAccountResponse",
    "TelegramAccountDetail",
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    "DialogInfo",
    "MessageResponse",
    "TelegramMessageInfo",
]
