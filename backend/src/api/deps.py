from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_async_session
from src.core.security import verify_access_token
from src.models.user import User
from src.repositories.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Get the current user based on JWT token.
    If auth_enabled is False, returns a dev user with admin privileges.
    """
    if not settings.auth_enabled:
        logger.warning("Authentication is DISABLED! Returning development admin user.")
        return User(
            id=0,
            email="dev@example.com",
            hashed_password="",
            is_active=True,
            is_deleted=False,
            name="Dev Admin",
            bio="Development admin user (auth disabled)",
            avatar_url=None,
            preferences=None,
            last_login_at=None,
            created_at=None,
            updated_at=None,
        )
    try:
        payload = verify_access_token(token)
    except (JWTError, ValueError, TypeError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from err
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user = await get_user_by_id(session, int(user_id))
    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


async def optional_get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """
    Like get_current_user, but returns None instead of raising if token is invalid/missing.
    """
    if not settings.auth_enabled:
        return User(
            id=0,
            email="dev@example.com",
            hashed_password="",
            is_active=True,
            is_deleted=False,
            name="Dev Admin",
            bio="Development admin user (auth disabled)",
            avatar_url=None,
            preferences=None,
            last_login_at=None,
            created_at=None,
            updated_at=None,
        )
    try:
        payload = verify_access_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
        user_id = int(payload.get("sub"))
        user = await get_user_by_id(session, user_id)
        if not user or not user.is_active or user.is_deleted:
            return None
        return user
    except Exception:
        return None
