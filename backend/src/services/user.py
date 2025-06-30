"""
User service: registration, authentication, logout, and authentication check.
"""

import os
import secrets
import sys
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from fastapi import UploadFile
from jose import JWTError, jwt
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
from src.models.used_password_reset_token import UsedPasswordResetToken
from src.models.user import User
from src.repositories import user as user_repo
from src.repositories.blacklisted_token import is_token_blacklisted
from src.repositories.user import (
    change_user_password,
    get_user_by_id,
    partial_update_user,
    update_last_login,
    user_action_limiter,
)
from src.schemas.user import (
    UserAvatarResponse,
    UserPreferences,
    UserProfile,
    UserProfileUpdate,
)
from src.utils.errors import (
    InvalidDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from src.utils.hashing import hash_password, verify_password
from src.utils.validation import get_password_validation_error, validate_email

# Expose exceptions for API usage
InvalidDataError = InvalidDataError
UserAlreadyExistsError = UserAlreadyExistsError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


# In-memory mock role store (user_id -> set of roles)
# In production, this would be persisted in the database
_mock_user_roles: dict[int, set[str]] = {}


async def register_user(session: AsyncSession, data: dict[str, Any]) -> User:
    """
    Register a new user. Hashes the password and stores the user in the database.
    Raises ValidationError or UserAlreadyExistsError on error.
    """
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise ValidationError("Email and password are required.")
    logger.info("User registration attempt", email=email)
    # Use repo helper for validation and creation
    user = await user_repo.create_user_with_validation(session, email, password)
    logger.info("User registered successfully", user_id=user.id, email=user.email)
    return user


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> tuple[str, str]:
    """
    Authenticate user credentials and return a tuple of (access_token, refresh_token).
    Raises ValidationError or UserNotFoundError on error.
    If authentication is disabled, return default tokens for dev user.
    """
    logger.info("User login attempt", email=email)
    if not settings.auth_enabled:
        logger.warning(
            "Authentication is DISABLED! Returning dev token for any credentials.",
            email=email,
        )
        access_token = create_access_token(
            {
                "sub": "dev-user",
                "user_id": "dev-user",
                "email": email,
                "role": "admin",
                "is_authenticated": True,
            }
        )
        jti = str(uuid.uuid4())
        exp = int((datetime.now(UTC) + timedelta(days=7)).timestamp())
        refresh_token = create_refresh_token(
            {
                "sub": "dev-user",
                "user_id": "dev-user",
                "email": email,
                "role": "admin",
                "is_authenticated": True,
                "jti": jti,
                "exp": exp,
            }
        )
        logger.debug(
            f"Refresh token payload at creation: {{'sub': 'dev-user', 'user_id': 'dev-user', 'email': '{email}', 'role': 'admin', 'is_authenticated': True, 'jti': '{jti}', 'exp': {exp}}}"
        )
        return access_token, refresh_token
    # Fetch user by email
    result = await session.execute(user_repo.select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_deleted:
        logger.warning("Login failed: user not found or inactive", email=email)
        raise UserNotFoundError("User not found or inactive.")
    if not verify_password(password, user.hashed_password):
        logger.warning("Login failed: incorrect password", user_id=user.id, email=email)
        raise ValidationError("Incorrect password.")
    # Update last login
    await user_repo.update_last_login(session, user.id)
    logger.info("User authenticated successfully", user_id=user.id, email=user.email)
    # Create JWT tokens
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "role": "admin" if getattr(user, "is_admin", False) else "user",
        }
    )
    jti = str(uuid.uuid4())
    exp = int((datetime.now(UTC) + timedelta(days=7)).timestamp())
    refresh_token = create_refresh_token(
        {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "role": "admin" if getattr(user, "is_admin", False) else "user",
            "jti": jti,
            "exp": exp,
        }
    )
    logger.debug(
        f"Refresh token payload at creation: {{'sub': str(user.id), 'user_id': str(user.id), 'email': user.email, 'jti': '{jti}', 'exp': {exp}}}"
    )
    return access_token, refresh_token


async def logout_user(session: AsyncSession, user_id: int) -> None:
    """
    Invalidate the user's session or refresh token (stub: deactivate user for now).
    """
    logger.info("User logout attempt", user_id=user_id)
    await user_repo.deactivate_user(session, user_id)
    logger.info("User logged out (deactivated)", user_id=user_id)


# Make is_authenticated a synchronous function (not async)
def is_authenticated(user: User) -> bool:
    """
    Check if a user is currently authenticated.
    If authentication is disabled, always return True.
    """
    if not settings.auth_enabled:
        logger.warning(
            "Authentication is DISABLED! All users considered authenticated."
        )
        return True
    return user.is_active and not user.is_deleted


def refresh_access_token(user_id: int | str, refresh_token: str) -> str:
    """
    Validate the refresh token and issue a new access token.
    Stub: No persistent token storage yet.
    """
    try:
        payload = verify_refresh_token(refresh_token)
        # Enforce type consistency: always compare as strings
        if str(payload.get("sub")) != str(user_id):
            raise ValidationError("Refresh token subject mismatch.")
        # Optionally check audience, issuer, exp, etc.
        # Issue new access token
        return create_access_token(
            {
                "sub": str(user_id),
                "user_id": str(user_id),
                "email": payload.get("email"),
            }
        )
    except Exception as e:
        raise ValidationError(f"Invalid refresh token: {e}") from e


def revoke_refresh_token(user_id: int, token: str) -> None:
    """
    Blacklist or invalidate the refresh token (stub).
    """
    # Placeholder: In production, store revoked tokens in a DB or cache
    pass


def verify_email_token(token: str) -> dict[str, Any]:
    """
    Decode and verify an email confirmation token.
    """
    try:
        payload = verify_access_token(token)
        # Optionally check for specific claims (purpose, exp, etc.)
        return payload
    except Exception as e:
        raise ValidationError(f"Invalid email verification token: {e}") from e


def get_password_reset_token(email: str) -> str:
    """
    Generate a secure token and simulate sending a reset link via logging.
    """
    token = create_access_token(
        {"sub": email, "purpose": "reset", "nonce": secrets.token_urlsafe(8)}
    )
    # Use correct environment check (dev/test/prod)
    if settings.environment in ("dev", "test"):
        logger.debug("Password reset token for development", email=email, token=token)
    else:
        logger.info("Password reset link sent to user", email=email)
    return token


async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
    """
    Validate the reset token and update the user's password. Enforces one-time-use tokens.
    """
    try:
        payload = verify_access_token(token)
        if payload.get("purpose") != "reset":
            logger.warning("Password reset failed: invalid token purpose")
            raise ValidationError("Invalid reset token purpose.")
        email = payload.get("sub")
        nonce = payload.get("nonce")
        if not email:
            logger.warning("Password reset failed: missing subject in token")
            raise ValidationError("Invalid reset token: missing subject.")
        if not nonce:
            logger.warning("Password reset failed: missing nonce in token", email=email)
            raise ValidationError("Invalid reset token: missing nonce.")
        # Check if this nonce has already been used for this email
        used = await session.execute(
            select(UsedPasswordResetToken).where(
                UsedPasswordResetToken.email == email,
                UsedPasswordResetToken.nonce == nonce,
            )
        )
        if used.scalar_one_or_none():
            logger.warning("Password reset failed: token already used", email=email)
            raise ValidationError("This password reset link has already been used.")
        err = get_password_validation_error(new_password)
        if err:
            logger.warning(
                "Password reset failed: password validation error", email=email
            )
            raise ValidationError(err)
        result = await session.execute(
            user_repo.select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user or not user.is_active or user.is_deleted:
            logger.warning(
                "Password reset failed: user not found or inactive", email=email
            )
            raise UserNotFoundError("User not found.")
        hashed = hash_password(new_password)
        await change_user_password(session, user.id, hashed)
        # Mark this nonce as used
        session.add(UsedPasswordResetToken(email=email, nonce=nonce))
        await session.commit()
        logger.info("Password reset successful", user_id=user.id, email=email)
    except UserNotFoundError:
        raise
    except Exception as e:
        logger.error("Password reset failed: {}", str(e))
        raise ValidationError(f"Invalid or expired reset token: {e}") from e


async def change_password(
    session: AsyncSession, user_id: int, old_pw: str, new_pw: str
) -> None:
    """
    Check old password and update if correct.
    """
    user = await get_user_by_id(session, user_id)
    if not user or not user.is_active or user.is_deleted:
        logger.warning(
            "Password change failed: user not found or inactive", user_id=user_id
        )
        raise UserNotFoundError("User not found.")
    if not verify_password(old_pw, user.hashed_password):
        logger.warning(
            "Password change failed: incorrect old password", user_id=user_id
        )
        raise ValidationError("Old password is incorrect.")
    if old_pw == new_pw or verify_password(new_pw, user.hashed_password):
        logger.warning(
            "Password change failed: new password same as old", user_id=user_id
        )
        raise ValidationError("New password must be different from the old password.")
    err = get_password_validation_error(new_pw)
    if err:
        logger.warning(
            "Password change failed: password validation error", user_id=user_id
        )
        raise ValidationError(err)
    hashed = hash_password(new_pw)
    await change_user_password(session, user_id, hashed)
    logger.info("Password changed for user", user_id=user_id)


def validate_password_strength(password: str) -> None:
    """
    Ensure the password is strong (length, characters, etc). Raise if not.
    Rejects passwords with whitespace or non-ASCII characters.
    """
    if any(c.isspace() for c in password):
        raise ValidationError("Password must not contain whitespace characters.")
    try:
        password.encode("ascii")
    except UnicodeEncodeError as e:
        raise ValidationError("Password must only contain ASCII characters.") from e
    err = get_password_validation_error(password)
    if err:
        raise ValidationError(err)


async def get_user_profile(session: AsyncSession, user_id: int) -> UserProfile:
    user = await get_user_by_id(session, user_id)
    if not user or user.is_deleted:
        raise UserNotFoundError("User not found.")
    return UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        bio=user.bio,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


async def update_user_profile(
    session: AsyncSession, user_id: int, data: dict[str, Any]
) -> UserProfile:
    update_data = UserProfileUpdate(**data).model_dump(exclude_unset=True)
    user = await partial_update_user(session, user_id, update_data)
    if not user:
        raise UserNotFoundError("User not found.")
    return await get_user_profile(session, user_id)


async def set_user_preferences(
    session: AsyncSession, user_id: int, preferences: dict[str, Any]
) -> UserPreferences:
    user = await get_user_by_id(session, user_id)
    if not user or user.is_deleted:
        raise UserNotFoundError("User not found.")
    user.preferences = preferences
    await session.commit()
    # Defensive: Only pass known fields to UserPreferences
    theme = preferences.get("theme")
    locale = preferences.get("locale")
    return UserPreferences(theme=theme, locale=locale)


async def upload_avatar(
    session: AsyncSession, user_id: int, file: UploadFile
) -> UserAvatarResponse:
    user = await get_user_by_id(session, user_id)
    if not user or user.is_deleted:
        raise UserNotFoundError("User not found.")
    upload_dir = os.path.join("uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{user_id}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    user.avatar_url = f"/uploads/avatars/{filename}"
    await session.commit()
    return UserAvatarResponse(avatar_url=user.avatar_url or "")


async def delete_user_account(
    session: AsyncSession, user_id: int, *, anonymize: bool = False
) -> bool:
    """
    Delete or anonymize a user account depending on policy.
    If anonymize=True, irreversibly remove PII and disable account (GDPR).
    Otherwise, perform a soft delete (set is_deleted flag).
    Always logs the action for audit purposes.
    Returns True if operation succeeded, False otherwise.
    """
    if anonymize:
        result = await user_repo.anonymize_user(session, user_id)
        action = "anonymize"
        details = "User data anonymized (GDPR/CCPA)."
    else:
        result = await user_repo.soft_delete_user(session, user_id)
        action = "soft_delete"
        details = "User soft-deleted (is_deleted=True)."
    await user_repo.audit_log_user_change(session, user_id, action, details)
    return result


async def deactivate_user(session: AsyncSession, user_id: int) -> bool:
    """
    Mark the user as inactive (is_active=False). Logs the change for audit.
    Returns True if operation succeeded, False otherwise.
    """
    result = await user_repo.deactivate_user(session, user_id)
    await user_repo.audit_log_user_change(
        session, user_id, "deactivate", "User deactivated (is_active=False)."
    )
    return result


async def reactivate_user(session: AsyncSession, user_id: int) -> bool:
    """
    Reactivate a previously deactivated user (is_active=True). Logs the change for audit.
    Returns True if operation succeeded, False otherwise.
    """
    result = await user_repo.reactivate_user(session, user_id)
    await user_repo.audit_log_user_change(
        session, user_id, "reactivate", "User reactivated (is_active=True)."
    )
    return result


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """
    Look up a user by username (email). Returns user if found, else None. Validates input.
    """
    if not username:
        raise ValidationError("Username (email) is required.")
    if not validate_email(username):
        raise ValidationError("Invalid email format.")
    result = await session.execute(user_repo.select(User).where(User.email == username))
    user = result.scalar_one_or_none()
    return user


async def get_users_paginated(
    session: AsyncSession,
    page: int = 1,
    limit: int = 20,
    email: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """
    Return paginated users and total count. Validates input and returns structured response.
    """
    if page < 1 or limit < 1 or limit > 100:
        raise ValidationError("Invalid pagination parameters.")
    offset = (page - 1) * limit
    users, total = await user_repo.list_users(
        session, offset=offset, limit=limit, email=email, name=name
    )
    return {"users": users, "total": total, "page": page, "limit": limit}


async def user_exists(session: AsyncSession, email: str) -> bool:
    """
    Return whether the email is already registered. Validates input.
    """
    if not email:
        raise ValidationError("Email is required.")
    if not validate_email(email):
        raise ValidationError("Invalid email format.")
    # is_email_unique returns True if not found, so invert
    exists = not await user_repo.is_email_unique(session, email)
    return exists


async def assign_role(user_id: int, role: str) -> bool:
    """
    Assign a role to a user. Allowed roles: admin, user, moderator.
    This is a stub; in production, store in DB.
    """
    if role not in UserRole.__members__.values() and role not in [
        r.value for r in UserRole
    ]:
        raise ValidationError(f"Invalid role: {role}")
    roles = _mock_user_roles.setdefault(user_id, set())
    roles.add(role)
    return True


async def check_user_role(user_id: int, required_role: str) -> bool:
    """
    Check if user has the required role. Stub: checks in-memory store.
    """
    roles = _mock_user_roles.get(user_id, set())
    return required_role in roles


async def async_refresh_access_token(
    session: AsyncSession,
    token: str,
    jwt_secret: str,
    jwt_algorithm: str,
    max_attempts: int = 15,
    window_seconds: int = 3600,
) -> str:
    """
    Validate the refresh token, apply rate limiting, check blacklist, and issue a new access token.
    Maximized robustness: strict type checks, user existence check, clear error messages, and no debug logs in production.
    Raises custom exceptions for all error/edge branches.
    """

    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        user_id = payload.get("user_id")
        if not user_id:
            raise RefreshTokenError("Invalid token format: missing user_id.")
        # Ensure user exists and is active
        user = await get_user_by_id(session, int(user_id))
        if not user or not user.is_active or user.is_deleted:
            raise RefreshTokenError("User not found or inactive.")
        # Rate limiting
        limiter_key = f"refresh:{user_id}"
        if callable(user_action_limiter):
            is_allowed = await user_action_limiter(
                limiter_key, max_attempts=max_attempts, window_seconds=window_seconds
            )
            if not is_allowed:
                raise RefreshTokenRateLimitError("Too many token refresh attempts.")
        # Blacklist check
        jti = payload.get("jti") or token
        if await is_token_blacklisted(session, jti):
            raise RefreshTokenBlacklistedError("Refresh token is blacklisted.")
        # Issue new access token
        new_token = refresh_access_token(user_id, token)
        return new_token
    except JWTError as e:
        raise RefreshTokenError(f"JWT decode failed: {e}") from e
    except Exception as e:
        # Only raise as RefreshTokenError if not a known custom error
        if isinstance(
            e,
            RefreshTokenRateLimitError
            | RefreshTokenBlacklistedError
            | RefreshTokenError,
        ):
            raise
        raise RefreshTokenError(f"Unexpected error: {e}") from e


class RefreshTokenError(Exception):
    pass


class RefreshTokenRateLimitError(Exception):
    pass


class RefreshTokenBlacklistedError(Exception):
    pass


class UserService:
    """
    Service class for user registration, authentication, profile, and password management.
    Wraps the module-level functions for better type safety and DI.
    """

    async def register_user(self, session: AsyncSession, data: dict[str, Any]) -> User:
        return await register_user(session, data)

    async def authenticate_user(
        self, session: AsyncSession, email: str, password: str
    ) -> tuple[str, str]:
        return await authenticate_user(session, email, password)

    async def logout_user(self, session: AsyncSession, user_id: int) -> None:
        return await logout_user(session, user_id)

    async def reset_password(
        self, session: AsyncSession, token: str, new_password: str
    ) -> None:
        return await reset_password(session, token, new_password)

    def get_password_reset_token(self, email: str) -> str:
        return get_password_reset_token(email)

    async def get_users_paginated(
        self, session: AsyncSession, page: int = 1, limit: int = 20
    ) -> dict[str, Any]:
        return await get_users_paginated(session, page, limit)

    async def get_user_profile(
        self, session: AsyncSession, user_id: int
    ) -> UserProfile:
        return await get_user_profile(session, user_id)

    async def update_user(
        self, session: AsyncSession, user_id: int, data: dict[str, Any]
    ) -> User:
        # Implement update logic or call the appropriate repository/service function
        from src.repositories.user import is_email_unique

        user = await get_user_by_id(session, user_id)
        if not user:
            raise UserNotFoundError("User not found.")
        if "email" in data:
            # Check for unique email, excluding current user
            is_unique = await is_email_unique(session, data["email"], exclude_user_id=user_id)
            if not is_unique:
                raise UserAlreadyExistsError("Email already exists.")
            user.email = data["email"]
        if "name" in data:
            user.name = data["name"]
        if "password" in data:
            from src.utils.hashing import hash_password

            user.hashed_password = hash_password(data["password"])
        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(self, session: AsyncSession, user_id: int) -> None:
        user = await get_user_by_id(session, user_id)
        if not user:
            raise UserNotFoundError("User not found.")
        await session.delete(user)
        await session.commit()

    async def list_users(self, session, offset=0, limit=20, email=None, name=None):
        from src.repositories.user import list_users

        return await list_users(
            session, offset=offset, limit=limit, email=email, name=name
        )

    async def get_user_by_id(self, session, user_id):
        from src.repositories.user import get_user_by_id

        return await get_user_by_id(session, user_id)


# Dependency provider for FastAPI
user_service_instance = UserService()


def get_user_service() -> UserService:
    return user_service_instance


# For future: integrate with route-based access control (RBAC)
# Example usage in FastAPI route:
#   if not await check_user_role(current_user.id, UserRole.ADMIN):
#       raise HTTPException(status_code=403, detail="Admin access required")

__all__ = [
    "InvalidDataError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "ValidationError",
    "create_access_token",
    "user_repo",
    "update_last_login",
    "RefreshTokenError",
    "RefreshTokenRateLimitError",
    "RefreshTokenBlacklistedError",
    # Add other public symbols here as needed
]
