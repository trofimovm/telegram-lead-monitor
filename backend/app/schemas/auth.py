from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    email_verified: bool
    tenant_id: UUID
    created_at: datetime


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    tenant_id: Optional[UUID] = None


class EmailVerificationRequest(BaseModel):
    """Schema for email verification"""
    token: str


class ResendVerificationRequest(BaseModel):
    """Schema for resending verification email"""
    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str
