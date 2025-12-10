from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    EmailVerificationRequest,
    ResendVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    RefreshTokenRequest,
)
from app.services.auth_service import auth_service
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    - **email**: User email address
    - **password**: User password (min 8 characters)
    - **full_name**: User full name

    Returns the created user data and sends a verification email.
    """
    return await auth_service.register_user(user_data, db)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login with email and password.

    - **email**: User email address
    - **password**: User password

    Returns JWT access and refresh tokens.
    """
    return await auth_service.login_user(login_data, db)


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    """
    Verify user email with verification token.

    - **token**: Verification token from email

    Returns success message if verification successful.
    """
    success = await auth_service.verify_email(verification_data.token, db)
    if success:
        return {"message": "Email verified successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email verification failed",
    )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    resend_data: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    """
    Resend verification email.

    - **email**: User email address

    Returns success message if email sent.
    """
    success = await auth_service.resend_verification_email(resend_data.email, db)
    if success:
        return {"message": "Verification email sent"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Failed to send verification email",
    )


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """
    Request password reset.

    - **email**: User email address

    Sends password reset email if user exists.
    Always returns success to prevent user enumeration.
    """
    await auth_service.request_password_reset(reset_request.email, db)
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Reset password with reset token.

    - **token**: Password reset token from email
    - **new_password**: New password (min 8 characters)

    Returns success message if password reset successful.
    """
    success = await auth_service.reset_password(reset_data.token, reset_data.new_password, db)
    if success:
        return {"message": "Password reset successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password reset failed",
    )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token.

    - **refresh_token**: Refresh token from previous login

    Returns new access and refresh tokens.
    """
    return await auth_service.refresh_access_token(refresh_data.refresh_token, db)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user information.

    Requires authentication via Bearer token.

    Returns current user data.
    """
    return UserResponse.model_validate(current_user)
