import csv
import io
import json
import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User
from src.utils.cache import user_cache
from src.utils.errors import (
    RateLimitExceededError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from src.utils.rate_limit import AsyncRateLimiter
from src.utils.validation import (
    get_password_validation_error,
    validate_email,
)

# Example: rate limiter for user actions (5 per minute per user)
user_action_limiter = AsyncRateLimiter(max_calls=5, period=60.0)


async def get_user_by_id(
    session: AsyncSession, user_id: int, use_cache: bool = True
) -> User | None:
    """Fetch a user by their ID, optionally using async cache (cache only user id, not ORM instance)."""
    cache_key = f"user_id:{user_id}"
    if use_cache:
        cached_id = await user_cache.get(cache_key)
        if cached_id:
            result = await session.execute(select(User).where(User.id == cached_id))
            return result.scalar_one_or_none()
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and use_cache:
        await user_cache.set(cache_key, user.id, ttl=60)
    return user


async def create_user_with_validation(
    session: AsyncSession, email: str, password: str
) -> User:
    """Create a user with validation and error handling."""
    if not validate_email(email):
        raise ValidationError("Invalid email format.")
    err = get_password_validation_error(password)
    if err:
        raise ValidationError(err)
    if not await is_email_unique(session, email):
        raise UserAlreadyExistsError("Email already exists.")
    from src.utils.hashing import hash_password

    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed, is_active=True)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception:
        await session.rollback()
        raise
    return user


async def sensitive_user_action(
    session: AsyncSession, user_id: int, action: str
) -> None:
    """Example of a rate-limited sensitive action."""
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found.")
    limiter_key = f"user:{user_id}:{action}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        raise RateLimitExceededError(
            f"Too many {action} attempts. Please try again later."
        )
    # ... perform the action ...


async def safe_get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found.")
    return user


async def get_users_by_ids(
    session: AsyncSession, user_ids: Sequence[int]
) -> Sequence[User]:
    """Fetch multiple users by a list of IDs."""
    if not user_ids:
        return []
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    return result.scalars().all()


async def list_users_paginated(
    session: AsyncSession, offset: int = 0, limit: int = 20
) -> Sequence[User]:
    """List users with pagination support."""
    result = await session.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()


async def search_users_by_name_or_email(
    session: AsyncSession, query: str, offset: int = 0, limit: int = 20
) -> Sequence[User]:
    """Search users by partial match on email (and name if available)."""
    # If name field is added in the future, include it in the or_ below
    stmt = (
        select(User).where(User.email.ilike(f"%{query}%")).offset(offset).limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def filter_users_by_status(
    session: AsyncSession, is_active: bool
) -> Sequence[User]:
    """Fetch users filtered by their active status."""
    result = await session.execute(select(User).where(User.is_active == is_active))
    return result.scalars().all()


async def filter_users_by_role(session: AsyncSession, role: str) -> Sequence[User]:
    """Stub: Fetch users filtered by role. Not implemented (no role field)."""
    # Role field not present in User model
    return []


async def get_users_created_within(
    session: AsyncSession, start: datetime, end: datetime
) -> Sequence[User]:
    """Fetch users created within a date range (inclusive)."""
    result = await session.execute(
        select(User).where(User.created_at >= start, User.created_at <= end)
    )
    return result.scalars().all()


async def count_users(session: AsyncSession, is_active: bool | None = None) -> int:
    """Count users, optionally filtered by active status."""
    stmt = select(func.count()).select_from(User)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_active_users(session: AsyncSession) -> Sequence[User]:
    """Fetch all active users."""
    return await filter_users_by_status(session, True)


async def get_inactive_users(session: AsyncSession) -> Sequence[User]:
    """Fetch all inactive users."""
    return await filter_users_by_status(session, False)


async def get_users_by_custom_field(
    session: AsyncSession, field: str, value: Any
) -> Sequence[User]:
    """Stub: Fetch users by a custom field (e.g., organization). Not implemented (no such field)."""
    # No custom field in User model
    return []


async def bulk_create_users(
    session: AsyncSession, users: Sequence[User]
) -> Sequence[User]:
    """Bulk create users and return them with IDs."""
    session.add_all(users)
    try:
        await session.commit()
        for user in users:
            await session.refresh(user)
    except Exception:
        await session.rollback()
        raise
    return users


async def bulk_update_users(
    session: AsyncSession, user_ids: Sequence[int], update_data: dict[str, Any]
) -> int:
    """Bulk update users by IDs with the given update_data dict. Returns number of updated rows."""
    if not user_ids or not update_data:
        return 0
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()
    for user in users:
        for key, value in update_data.items():
            setattr(user, key, value)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return len(users)


async def bulk_delete_users(session: AsyncSession, user_ids: Sequence[int]) -> int:
    """Bulk delete users by IDs. Returns number of deleted rows."""
    if not user_ids:
        return 0
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()
    for user in users:
        await session.delete(user)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return len(users)


async def soft_delete_user(session: AsyncSession, user_id: int) -> bool:
    """Mark a user as deleted (soft delete)."""
    user = await get_user_by_id(session, user_id)
    if user is None or user.is_deleted:
        return False
    user.is_deleted = True
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return True


async def restore_user(session: AsyncSession, user_id: int) -> bool:
    """Restore a soft-deleted user."""
    user = await get_user_by_id(session, user_id)
    if user is None or not user.is_deleted:
        return False
    user.is_deleted = False
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return True


async def upsert_user(
    session: AsyncSession, email: str, defaults: dict[str, Any]
) -> User:
    """Insert or update a user by email. Returns the user."""
    if not email or not validate_email(email):
        raise ValidationError("Invalid email format.")
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        for key, value in defaults.items():
            if hasattr(user, key):
                setattr(user, key, value)
    else:
        user = User(email=email, **defaults)
        session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception:
        await session.rollback()
        raise
    return user


async def partial_update_user(
    session: AsyncSession, user_id: int, update_data: dict[str, Any]
) -> User | None:
    """Update only provided fields for a user."""
    user = await get_user_by_id(session, user_id)
    if user is None:
        return None
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception:
        await session.rollback()
        raise
    return user


async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Check if a user exists by ID."""
    result = await session.execute(select(User.id).where(User.id == user_id))
    return result.scalar_one_or_none() is not None


async def is_email_unique(
    session: AsyncSession, email: str, exclude_user_id: int | None = None
) -> bool:
    """Check if an email is unique (optionally excluding a user by ID)."""
    stmt = select(User).where(User.email == email)
    if exclude_user_id is not None:
        stmt = stmt.where(User.id != exclude_user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is None


async def change_user_password(
    session: AsyncSession, user_id: int, new_hashed_password: str
) -> bool:
    """Change a user's password (hashed)."""
    user = await get_user_by_id(session, user_id)
    if user is None:
        return False
    user.hashed_password = new_hashed_password
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return True


logger: logging.Logger = logging.getLogger("user_audit")


async def audit_log_user_change(
    session: AsyncSession, user_id: int, action: str, details: str = ""
) -> None:
    """Log an audit event for a user change."""
    logger.info(f"User {user_id}: {action}. {details}")
    # Optionally, persist audit logs to DB here


async def assign_role_to_user(session: AsyncSession, user_id: int, role: str) -> bool:
    """Stub: Assign a role to a user. Not implemented (no role field)."""
    return False


async def revoke_role_from_user(session: AsyncSession, user_id: int, role: str) -> bool:
    """Stub: Revoke a role from a user. Not implemented (no role field)."""
    return False


@asynccontextmanager
async def db_session_context() -> AsyncIterator[Any]:
    """Async context manager for DB session."""
    from src.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def db_transaction(session: AsyncSession) -> AsyncIterator[Any]:
    """Async context manager for DB transaction (atomic operations)."""
    async with session.begin():
        yield


async def get_user_with_files(session: AsyncSession, user_id: int) -> User | None:
    """Fetch a user and eagerly load their files."""
    result = await session.execute(
        select(User).options(selectinload(User.files)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def export_users_to_csv(session: AsyncSession) -> str:
    """Export all users to CSV string."""
    result = await session.execute(select(User))
    users = result.scalars().all()
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "email",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
            "last_login_at",
        ],
    )
    writer.writeheader()
    for user in users:
        writer.writerow(
            {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_deleted": user.is_deleted,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login_at": user.last_login_at,
            }
        )
    return output.getvalue()


async def export_users_to_json(session: AsyncSession) -> str:
    """Export all users to JSON string."""
    result = await session.execute(select(User))
    users = result.scalars().all()
    data = [
        {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": (
                user.last_login_at.isoformat() if user.last_login_at else None
            ),
        }
        for user in users
    ]
    return json.dumps(data)


async def import_users_from_dicts(
    session: AsyncSession, user_dicts: Sequence[dict[str, Any]]
) -> Sequence[User]:
    """Bulk import users from a list of dicts."""
    users = [User(**d) for d in user_dicts]
    session.add_all(users)
    try:
        await session.commit()
        for user in users:
            await session.refresh(user)
    except Exception:
        await session.rollback()
        raise
    return users


async def deactivate_user(session: AsyncSession, user_id: int) -> bool:
    """Deactivate a user (set is_active=False)."""
    user = await get_user_by_id(session, user_id)
    if user is None or not user.is_active:
        return False
    user.is_active = False
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return True


async def reactivate_user(session: AsyncSession, user_id: int) -> bool:
    """Reactivate a user (set is_active=True)."""
    user = await get_user_by_id(session, user_id)
    if user is None or user.is_active:
        return False
    user.is_active = True
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return True


async def update_last_login(
    session: AsyncSession, user_id: int, login_time: datetime | None = None
) -> bool:
    """Update the last_login_at timestamp for a user."""
    user = await get_user_by_id(session, user_id)
    if user is None:
        return False
    user.last_login_at = login_time or datetime.now(UTC)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return True


async def anonymize_user(session: AsyncSession, user_id: int) -> bool:
    """Anonymize user data for privacy/GDPR (irreversibly removes PII, disables account)."""
    user = await get_user_by_id(session, user_id, use_cache=False)
    if not user:
        return False
    user.email = f"anon_{user.id}_{int(datetime.now(UTC).timestamp())}@anon.invalid"
    user.hashed_password = ""
    user.is_active = False
    user.is_deleted = True
    user.last_login_at = None
    await session.commit()
    return True


async def user_signups_per_month(session: AsyncSession, year: int) -> dict[int, int]:
    """Return a dict of {month: signup_count} for the given year (1-12)."""
    stmt = (
        select(extract("month", User.created_at).label("month"), func.count(User.id))
        .where(extract("year", User.created_at) == year)
        .group_by("month")
        .order_by("month")
    )
    result = await session.execute(stmt)
    rows = result.all()
    # Fill all months 1-12 with 0 if missing
    stats = dict.fromkeys(range(1, 13), 0)
    for month, count in rows:
        stats[int(month)] = count
    return stats


__all__ = [
    "safe_get_user_by_id",
    "create_user_with_validation",
    "sensitive_user_action",
    "anonymize_user",
    "user_signups_per_month",
]
