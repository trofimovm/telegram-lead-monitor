from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_session_local
from app.models.user import User
from app.models.tenant import Tenant
from app.utils.security import decode_token
from app.schemas.auth import TokenData


security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database session.

    Yields:
        Database session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency for getting current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_token(token)

        # Verify token type
        if payload.get("type") != "access":
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=UUID(user_id),
            email=payload.get("email"),
            tenant_id=UUID(payload.get("tenant_id")) if payload.get("tenant_id") else None,
        )
    except (JWTError, ValueError):
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency for getting current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    return current_user


async def get_current_tenant(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Tenant:
    """
    Dependency for getting current user's tenant.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Current tenant

    Raises:
        HTTPException: If tenant not found
    """
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return tenant


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency for optionally getting current user.
    Useful for endpoints that work both authenticated and unauthenticated.

    Args:
        credentials: Optional HTTP Bearer token
        db: Database session

    Returns:
        Current user if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = decode_token(token)

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == UUID(user_id)).first()
        return user
    except (JWTError, ValueError):
        return None


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.

    Args:
        required_role: Required user role (e.g., "owner", "admin", "member")

    Returns:
        Dependency function
    """

    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if user has required role.

        Args:
            current_user: Current authenticated user

        Returns:
            Current user if role matches

        Raises:
            HTTPException: If user doesn't have required role
        """
        role_hierarchy = {"owner": 3, "admin": 2, "member": 1}

        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role, 999)

        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker
