from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Telegram Account schemas
class TelegramAccountStartAuth(BaseModel):
    """Schema for starting Telegram authentication"""
    phone: str = Field(..., min_length=10, max_length=20)


class TelegramAccountVerifyCode(BaseModel):
    """Schema for verifying authentication code"""
    phone: str = Field(..., min_length=10, max_length=20)
    code: str = Field(..., min_length=5, max_length=6)
    phone_code_hash: str


class TelegramAccountResponse(BaseModel):
    """Schema for Telegram account in responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    phone: str
    status: str
    last_active_at: Optional[datetime] = None
    created_at: datetime


class TelegramAccountDetail(BaseModel):
    """Schema for detailed Telegram account info"""
    account: TelegramAccountResponse
    telegram_user: Optional[dict] = None  # Info from Telegram API


# Source (Channel/Chat) schemas
class SourceCreate(BaseModel):
    """Schema for creating a new source"""
    telegram_account_id: UUID
    tg_id: int
    username: Optional[str] = None
    title: Optional[str] = None
    type: str  # channel, chat, group
    tags: List[str] = []


class SourceUpdate(BaseModel):
    """Schema for updating a source"""
    title: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class SourceResponse(BaseModel):
    """Schema for source in responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    telegram_account_id: UUID
    tg_id: int
    type: str
    username: Optional[str] = None
    title: Optional[str] = None
    subscribers_count: Optional[int] = None
    is_active: bool
    tags: List[str]
    created_at: datetime


# Dialog (for fetching available channels)
class DialogInfo(BaseModel):
    """Schema for Telegram dialog information"""
    id: int
    title: str
    username: Optional[str] = None
    type: str
    participants_count: Optional[int] = None
    is_channel: bool
    is_group: bool


# Message schemas
class MessageResponse(BaseModel):
    """Schema for message in responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    tg_message_id: int
    text: Optional[str] = None
    author_tg_id: Optional[int] = None
    author_username: Optional[str] = None
    media_type: Optional[str] = None
    sent_at: datetime
    created_at: datetime


class TelegramMessageInfo(BaseModel):
    """Schema for Telegram message information from API"""
    id: int
    text: str
    date: str
    views: Optional[int] = None
    forwards: Optional[int] = None
    author: Optional[dict] = None
