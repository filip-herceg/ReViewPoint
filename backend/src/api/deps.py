from src.core.config import settings
from src.models.user import User
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import verify_access_token
from src.repositories.user import get_user_by_id
from src.core.database import get_db_session
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session)
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
    payload = verify_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_user_by_id(session, int(user_id))
    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user
