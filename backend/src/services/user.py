"""
User service: registration, authentication, logout, and authentication check.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories import user as user_repo
from src.models.user import User
from src.utils.hashing import verify_password
from src.utils.errors import ValidationError, UserNotFoundError
# Patch for test/discovery import issues in src/services/user.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.core.security import create_access_token

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
