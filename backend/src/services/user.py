"""
User service: registration, authentication, logout, and authentication check.
"""
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories import user as user_repo
from src.models.user import User
from src.utils.hashing import hash_password, verify_password
from src.utils.validation import get_password_validation_error
from src.repositories.user import get_user_by_id, change_user_password
from src.core.security import create_access_token, verify_access_token
from src.utils.errors import ValidationError, UserNotFoundError
from sqlalchemy import select
from src.models.used_password_reset_token import UsedPasswordResetToken
import logging
import secrets

# Patch for test/discovery import issues in src/services/user.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

async def register_user(session: AsyncSession, data: dict[str, Any]) -> User:
    """
    Register a new user. Hashes the password and stores the user in the database.
    Raises ValidationError or UserAlreadyExistsError on error.
    """
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise ValidationError("Email and password are required.")
    # Use repo helper for validation and creation
    user = await user_repo.create_user_with_validation(session, email, password)
    return user

async def authenticate_user(session: AsyncSession, email: str, password: str) -> str:
    """
    Authenticate user credentials and return a JWT access token.
    Raises ValidationError or UserNotFoundError on error.
    """
    # Fetch user by email
    result = await session.execute(user_repo.select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_deleted:
        raise UserNotFoundError("User not found or inactive.")
    if not verify_password(password, user.hashed_password):
        raise ValidationError("Incorrect password.")
    # Update last login
    await user_repo.update_last_login(session, user.id)
    # Create JWT token
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return token

async def logout_user(session: AsyncSession, user_id: int) -> None:
    """
    Invalidate the user's session or refresh token (stub: deactivate user for now).
    """
    # For demo: deactivate user (real implementation would revoke refresh token/session)
    await user_repo.deactivate_user(session, user_id)

# Make is_authenticated a synchronous function (not async)
def is_authenticated(user: User) -> bool:
    """
    Check if a user is currently authenticated.
    """
    return user.is_active and not user.is_deleted

def refresh_access_token(user_id: int, refresh_token: str) -> str:
    """
    Validate the refresh token and issue a new access token.
    Stub: No persistent token storage yet.
    """
    try:
        payload = verify_access_token(refresh_token)
        if str(payload.get("sub")) != str(user_id):
            raise ValidationError("Refresh token subject mismatch.")
        # Optionally check audience, issuer, exp, etc.
        # Issue new access token
        return create_access_token({"sub": str(user_id), "email": payload.get("email")})
    except Exception as e:
        raise ValidationError(f"Invalid refresh token: {e}")

def revoke_refresh_token(user_id: int, token: str) -> None:
    """
    Blacklist or invalidate the refresh token (stub).
    """
    # Placeholder: In production, store revoked tokens in a DB or cache
    pass

def verify_email_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify an email confirmation token.
    """
    try:
        payload = verify_access_token(token)
        # Optionally check for specific claims (purpose, exp, etc.)
        return payload
    except Exception as e:
        raise ValidationError(f"Invalid email verification token: {e}")

def get_password_reset_token(email: str) -> str:
    """
    Generate a secure token and simulate sending a reset link via logging.
    """
    token = create_access_token({"sub": email, "purpose": "reset", "nonce": secrets.token_urlsafe(8)})
    logging.info(f"Password reset link sent to {email}: /reset?token={token}")
    return token

async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
    """
    Validate the reset token and update the user's password. Enforces one-time-use tokens.
    """
    try:
        payload = verify_access_token(token)
        if payload.get("purpose") != "reset":
            raise ValidationError("Invalid reset token purpose.")
        email = payload.get("sub")
        nonce = payload.get("nonce")
        if not email:
            raise ValidationError("Invalid reset token: missing subject.")
        if not nonce:
            raise ValidationError("Invalid reset token: missing nonce.")
        # Check if this nonce has already been used for this email
        used = await session.execute(
            select(UsedPasswordResetToken).where(
                UsedPasswordResetToken.email == email,
                UsedPasswordResetToken.nonce == nonce
            )
        )
        if used.scalar_one_or_none():
            raise ValidationError("This password reset link has already been used.")
        err = get_password_validation_error(new_password)
        if err:
            raise ValidationError(err)
        result = await session.execute(user_repo.select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not user.is_active or user.is_deleted:
            raise UserNotFoundError("User not found.")
        hashed = hash_password(new_password)
        await change_user_password(session, user.id, hashed)
        # Mark this nonce as used
        session.add(UsedPasswordResetToken(email=email, nonce=nonce))
        await session.commit()
        logging.info(f"Password reset for user {email}")
    except UserNotFoundError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid or expired reset token: {e}")

async def change_password(session: AsyncSession, user_id: int, old_pw: str, new_pw: str) -> None:
    """
    Check old password and update if correct.
    """
    user = await get_user_by_id(session, user_id)
    if not user or not user.is_active or user.is_deleted:
        raise UserNotFoundError("User not found.")
    if not verify_password(old_pw, user.hashed_password):
        raise ValidationError("Old password is incorrect.")
    if old_pw == new_pw or verify_password(new_pw, user.hashed_password):
        raise ValidationError("New password must be different from the old password.")
    err = get_password_validation_error(new_pw)
    if err:
        raise ValidationError(err)
    hashed = hash_password(new_pw)
    await change_user_password(session, user_id, hashed)
    logging.info(f"Password changed for user {user.email}")

def validate_password_strength(password: str) -> None:
    """
    Ensure the password is strong (length, characters, etc). Raise if not.
    Rejects passwords with whitespace or non-ASCII characters.
    """
    if any(c.isspace() for c in password):
        raise ValidationError("Password must not contain whitespace characters.")
    try:
        password.encode('ascii')
    except UnicodeEncodeError:
        raise ValidationError("Password must only contain ASCII characters.")
    err = get_password_validation_error(password)
    if err:
        raise ValidationError(err)
