"""
Dependency injection utilities for FastAPI API endpoints.

This module provides robust, reusable dependencies for:
- Database session management (get_db)
- User authentication and active user checks (get_current_user, get_current_active_user, optional_get_current_user)
- Pagination parameter validation (pagination_params)
- Repository service locator for testability (get_user_repository)
- Request ID propagation for tracing (get_request_id, get_current_request_id)

All dependencies use loguru for error and event logging, follow security best practices, and are designed for easy testing and mocking.
"""

import contextvars
import os
import uuid
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Any

from fastapi import Depends, HTTPException, Query, Request, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_async_session
from src.core.security import verify_access_token
from src.models.user import User
from src.repositories import user as user_repository
from src.repositories.user import get_user_by_id

REQUEST_ID_HEADER = "X-Request-ID"

# Context variable to store request ID per request
request_id_ctx_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

MAX_LIMIT = 100


class PaginationParams:
    """
    Standardized pagination parameters for API endpoints.

    Args:
        offset (int): Number of items to skip (default 0, must be >= 0).
        limit (int): Number of items to return (default 20, 1 <= limit <= MAX_LIMIT).

    Usage:
        params = Depends(pagination_params)
        items = repo.list(offset=params.offset, limit=params.limit)
    """

    def __init__(self, offset: int = 0, limit: int = 20):
        self.offset = offset
        self.limit = limit


# --- Enhanced logging for all dependencies ---


# PaginationParams and pagination_params already log errors for invalid input (no sensitive data).
# Add info log for successful pagination param usage.
def pagination_params(
    offset: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        20,
        ge=1,
        le=MAX_LIMIT,
        description=f"Max number of items to return (max {MAX_LIMIT})",
    ),
) -> PaginationParams:
    """
    Dependency to standardize and validate pagination query parameters.

    Parameters:
        offset (int): Number of items to skip (>=0, default 0)
        limit (int): Number of items to return (1 to MAX_LIMIT, default 20)
    Returns:
        PaginationParams: Validated pagination parameters.
    Raises:
        HTTPException(400): If offset or limit is out of bounds.
    Usage:
        params = Depends(pagination_params)
        items = repo.list(offset=params.offset, limit=params.limit)
    """
    if offset < 0:
        logger.error(f"Invalid offset: {offset}")
        raise HTTPException(status_code=400, detail="Offset must be >= 0")
    if limit < 1 or limit > MAX_LIMIT:
        logger.error(f"Invalid limit: {limit}")
        raise HTTPException(
            status_code=400, detail=f"Limit must be between 1 and {MAX_LIMIT}"
        )
    logger.info(f"Pagination params accepted: offset={offset}, limit={limit}")
    return PaginationParams(offset=offset, limit=limit)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Dependency to extract and validate a JWT token from the request and fetch the current user from the database.

    Parameters:
        token (str): JWT access token from the Authorization header.
        session (AsyncSession): SQLAlchemy async session.
    Returns:
        User: The authenticated and active user instance.
    Raises:
        HTTPException(401): If token is invalid/expired, or user is not found/inactive/deleted.
    Usage:
        user = Depends(get_current_user)
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
        )  # Validate token and extract user_id
    try:
        payload = verify_access_token(token)
        if not payload:
            logger.error("Token verification returned empty payload")
            raise ValueError("Empty payload")

        user_id = payload.get("sub")
        if not user_id:
            logger.error("Token payload missing 'sub' (user id)")
            raise ValueError("Missing user id")

    except (JWTError, ValueError, TypeError) as err:
        logger.error(f"Token validation failed: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from err
    user = await get_user_by_id(session, int(user_id))
    if not user or not user.is_active or user.is_deleted:
        logger.error(f"User not found or inactive/deleted: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    logger.info(f"User authenticated: user_id={user_id}")
    return user


async def optional_get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """
    Like get_current_user, but returns None instead of raising if token is invalid/missing.

    Parameters:
        token (str): JWT access token from the Authorization header.
        session (AsyncSession): SQLAlchemy async session.
    Returns:
        User | None: The authenticated user, or None if not authenticated.
    Usage:
        user = Depends(optional_get_current_user)
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
        payload = verify_access_token(
            token
        )  # Only pass token, matches function signature
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            return None
        user_id = int(user_id_raw)
        user = await get_user_by_id(session, user_id)
        if not user or not user.is_active or user.is_deleted:
            return None
        return user
    except Exception:
        return None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a SQLAlchemy AsyncSession for database operations.

    Yields:
        AsyncSession: SQLAlchemy async session for DB operations.
    Raises:
        HTTPException(500): If database session cannot be established or used.
    Usage:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    from src.core.database import AsyncSessionLocal

    session = AsyncSessionLocal()
    logger.info("Database session created.")
    try:
        yield session
    except Exception as exc:
        logger.error(f"Database session error: {exc}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error. Please try again later.",
        ) from exc
    finally:
        await session.close()
        logger.info("Database session closed.")


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the current user is active.

    Parameters:
        user (User): The user instance from get_current_user.
    Returns:
        User: The active user instance.
    Raises:
        HTTPException(403): If the user is inactive or deleted.
    Usage:
        user = Depends(get_current_active_user)
    """
    if not user.is_active or user.is_deleted:
        logger.error(f"Inactive or deleted user tried to access: user_id={user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive or deleted user."
        )
    logger.info(f"Active user check passed: user_id={user.id}")
    return user


def get_request_id(request: Request) -> str:
    """
    Dependency to extract or generate a request ID for tracing.

    Parameters:
        request (Request): FastAPI request object.
    Returns:
        str: The request ID (from header or generated UUID).
    Usage:
        request_id = Depends(get_request_id)
    """
    req_id = request.headers.get(REQUEST_ID_HEADER)
    # Basic validation: must be a valid UUID or a string of reasonable length
    try:
        if req_id:
            uuid.UUID(str(req_id))
        else:
            raise ValueError
    except (ValueError, TypeError):
        req_id = str(uuid.uuid4())
    request_id_ctx_var.set(req_id)
    logger.debug(f"Request ID set: {req_id}")
    return req_id


def get_current_request_id() -> str | None:
    """
    Helper to get the current request ID from contextvar.

    Returns:
        str | None: The current request ID, or None if not set.
    Usage:
        req_id = get_current_request_id()
    """
    return request_id_ctx_var.get()


def get_user_repository() -> Any:
    """
    Service locator for the user repository dependency.

    Returns:
        Any: The user repository module/class (type: Any, since module is not a valid type).
    Usage in endpoint or service:
        repo = Depends(get_user_repository)
    In tests:
        app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()
    """
    return user_repository


# API key security scheme
async def validate_api_key(
    api_key: str = Security(api_key_header),
) -> bool:
    """
    Validate the API key from the X-API-Key header.

    Parameters:
        api_key (str): API key from the X-API-Key header.
    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    if not settings.api_key_enabled:
        # API key validation is disabled, always return True
        return True

    # Get the configured API key
    configured_api_key = os.environ.get("REVIEWPOINT_API_KEY")
    if not configured_api_key:
        logger.warning("API key validation is enabled but no API key is configured")
        return False

    # Check if the provided API key matches the configured one
    return api_key == configured_api_key


async def require_api_key(
    api_key: str = Security(api_key_header),
) -> None:
    """
    Dependency to require a valid API key.

    Parameters:
        api_key (str): API key from the X-API-Key header.
    Raises:
        HTTPException(401): If the API key is missing or invalid.
    Usage:
        _ = Depends(require_api_key)
    """
    if not await validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


# Updated get_current_user that requires API key
async def get_current_user_with_api_key(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_api_key),
) -> User:
    """
    Like get_current_user, but also requires a valid API key.
    This function should be used for endpoints that require both
    JWT authentication and API key validation.
    """
    return await get_current_user(token, session)


get_user_repository = lru_cache()(get_user_repository)
