from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_active_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.models.telegram_account import TelegramAccount
from app.schemas.telegram import (
    TelegramAccountStartAuth,
    TelegramAccountVerifyCode,
    TelegramAccountResponse,
    TelegramAccountDetail,
    DialogInfo,
)
from app.services.telegram_service import telegram_service
from app.utils.encryption import encrypt_session

router = APIRouter()


@router.post("/accounts/start-auth", status_code=status.HTTP_200_OK)
async def start_telegram_auth(
    auth_data: TelegramAccountStartAuth,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Start Telegram authentication process.

    - **phone**: Phone number with country code (e.g., +1234567890)

    Returns phone_code_hash for verification step.
    """
    # Check if account already exists
    existing = db.query(TelegramAccount).filter(
        TelegramAccount.tenant_id == current_user.tenant_id,
        TelegramAccount.phone == auth_data.phone
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This phone number is already connected"
        )

    try:
        result = await telegram_service.start_auth(auth_data.phone)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start authentication: {str(e)}"
        )


@router.post("/accounts/verify-code", response_model=TelegramAccountResponse, status_code=status.HTTP_201_CREATED)
async def verify_telegram_code(
    verify_data: TelegramAccountVerifyCode,
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Verify authentication code and complete Telegram account connection.

    - **phone**: Phone number
    - **code**: Verification code from SMS/Telegram
    - **phone_code_hash**: Hash from start-auth step

    Returns created Telegram account.
    """
    try:
        # Verify code and get session string
        session_string = await telegram_service.verify_code(
            verify_data.phone,
            verify_data.code,
            verify_data.phone_code_hash
        )

        # Encrypt session for storage
        session_encrypted = encrypt_session(session_string)

        # Create Telegram account record
        telegram_account = TelegramAccount(
            tenant_id=current_tenant.id,
            phone=verify_data.phone,
            session_encrypted=session_encrypted,
            status="active",
            last_active_at=datetime.utcnow()
        )

        db.add(telegram_account)
        db.commit()
        db.refresh(telegram_account)

        return TelegramAccountResponse.model_validate(telegram_account)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify code: {str(e)}"
        )


@router.get("/accounts", response_model=List[TelegramAccountResponse])
async def list_telegram_accounts(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Get list of connected Telegram accounts for current tenant.
    """
    accounts = db.query(TelegramAccount).filter(
        TelegramAccount.tenant_id == current_tenant.id
    ).all()

    return [TelegramAccountResponse.model_validate(acc) for acc in accounts]


@router.get("/accounts/{account_id}", response_model=TelegramAccountDetail)
async def get_telegram_account(
    account_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a Telegram account.
    """
    account = db.query(TelegramAccount).filter(
        TelegramAccount.id == account_id,
        TelegramAccount.tenant_id == current_tenant.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found"
        )

    # Get Telegram user info
    try:
        telegram_user = await telegram_service.get_me(account.session_encrypted)

        return TelegramAccountDetail(
            account=TelegramAccountResponse.model_validate(account),
            telegram_user=telegram_user
        )
    except Exception as e:
        return TelegramAccountDetail(
            account=TelegramAccountResponse.model_validate(account),
            telegram_user=None
        )


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_telegram_account(
    account_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Delete a Telegram account connection.

    This will also delete all associated sources and their messages.
    """
    account = db.query(TelegramAccount).filter(
        TelegramAccount.id == account_id,
        TelegramAccount.tenant_id == current_tenant.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found"
        )

    db.delete(account)
    db.commit()

    return None


@router.get("/accounts/{account_id}/dialogs", response_model=List[DialogInfo])
async def get_telegram_dialogs(
    account_id: UUID,
    limit: int = 100,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Get list of available dialogs (channels, chats, groups) for a Telegram account.

    - **limit**: Maximum number of dialogs to fetch (default: 100)

    This is used to select which channels/chats to monitor.
    """
    account = db.query(TelegramAccount).filter(
        TelegramAccount.id == account_id,
        TelegramAccount.tenant_id == current_tenant.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found"
        )

    try:
        dialogs = await telegram_service.get_dialogs(account.session_encrypted, limit=limit)
        return [DialogInfo(**dialog) for dialog in dialogs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch dialogs: {str(e)}"
        )
