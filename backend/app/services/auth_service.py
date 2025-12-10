from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    create_token_payload,
)
from app.services.email_service import email_service
from app.config import settings


class AuthService:
    """
    Service for handling authentication operations.
    """

    async def register_user(self, user_data: UserRegister, db: Session) -> UserResponse:
        """
        Register a new user with email verification.

        Args:
            user_data: User registration data
            db: Database session

        Returns:
            Created user data

        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create tenant for the user (each user gets their own tenant in multi-tenant SaaS)
        tenant = Tenant(
            name=f"{user_data.full_name}'s Workspace",
            plan="free",
        )
        db.add(tenant)
        db.flush()  # Get tenant ID

        # Generate verification token
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(
            hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
        )

        # Create user
        user = User(
            tenant_id=tenant.id,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role="owner",  # First user in tenant is owner
            email_verified=False,
            verification_token=verification_token,
            verification_token_expires=verification_expires,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Send verification email
        await email_service.send_verification_email(user.email, verification_token)

        return UserResponse.model_validate(user)

    async def login_user(self, login_data: UserLogin, db: Session) -> Token:
        """
        Authenticate user and return JWT tokens.

        Args:
            login_data: User login credentials
            db: Database session

        Returns:
            Access and refresh tokens

        Raises:
            HTTPException: If credentials are invalid or email not verified
        """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if email is verified
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your inbox.",
            )

        # Create tokens
        token_payload = create_token_payload(user.id, user.email, user.tenant_id)
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def verify_email(self, token: str, db: Session) -> bool:
        """
        Verify user email with verification token.

        Args:
            token: Verification token
            db: Database session

        Returns:
            True if verification successful

        Raises:
            HTTPException: If token is invalid or expired
        """
        user = db.query(User).filter(User.verification_token == token).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        if user.verification_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired",
            )

        # Mark email as verified
        user.email_verified = True
        user.verification_token = None
        user.verification_token_expires = None

        db.commit()
        return True

    async def resend_verification_email(self, email: str, db: Session) -> bool:
        """
        Resend verification email to user.

        Args:
            email: User email
            db: Database session

        Returns:
            True if email sent successfully

        Raises:
            HTTPException: If user not found or already verified
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified",
            )

        # Generate new verification token
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(
            hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
        )

        user.verification_token = verification_token
        user.verification_token_expires = verification_expires

        db.commit()

        # Send verification email
        await email_service.send_verification_email(user.email, verification_token)
        return True

    async def request_password_reset(self, email: str, db: Session) -> bool:
        """
        Send password reset email.

        Args:
            email: User email
            db: Database session

        Returns:
            True if email sent successfully
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if user exists or not
            return True

        # Generate reset token
        reset_token = generate_verification_token()
        reset_expires = datetime.utcnow() + timedelta(
            hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
        )

        user.verification_token = reset_token
        user.verification_token_expires = reset_expires

        db.commit()

        # Send password reset email
        await email_service.send_password_reset_email(user.email, reset_token)
        return True

    async def reset_password(self, token: str, new_password: str, db: Session) -> bool:
        """
        Reset user password with reset token.

        Args:
            token: Password reset token
            new_password: New password
            db: Database session

        Returns:
            True if password reset successful

        Raises:
            HTTPException: If token is invalid or expired
        """
        user = db.query(User).filter(User.verification_token == token).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )

        if user.verification_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        # Update password
        user.password_hash = get_password_hash(new_password)
        user.verification_token = None
        user.verification_token_expires = None

        db.commit()
        return True

    async def refresh_access_token(self, refresh_token: str, db: Session) -> Token:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Refresh token
            db: Database session

        Returns:
            New access and refresh tokens

        Raises:
            HTTPException: If refresh token is invalid
        """
        try:
            payload = decode_token(refresh_token)

            # Verify token type
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            # Get user
            user_id = payload.get("sub")
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            # Create new tokens
            token_payload = create_token_payload(user.id, user.email, user.tenant_id)
            new_access_token = create_access_token(token_payload)
            new_refresh_token = create_refresh_token(token_payload)

            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )


# Global instance
auth_service = AuthService()
