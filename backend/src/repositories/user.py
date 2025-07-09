import csv
import io
import json
import logging
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime

# Example: rate limiter for user actions (5 per minute per user)
from typing import (
    Any,
    Final,
    Literal,
    TypedDict,
)

from sqlalchemy import (
    extract,
    func,
    or_,
    select,
)
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

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

user_action_limiter: Final[AsyncRateLimiter[Any]] = AsyncRateLimiter(
    max_calls=5, period=60.0
)


async def get_user_by_id(
    session: AsyncSession, user_id: int, use_cache: bool = True
) -> User | None:
    """Fetch a user by their ID, optionally using async cache (cache only user id, not ORM instance).
    Raises:
        None
    """
    cache_key: Final[str] = f"user_id:{user_id}"
    if use_cache:
        cached_id_obj = await user_cache.get(cache_key)
        cached_id: int | None = (
            cached_id_obj if isinstance(cached_id_obj, int) else None
        )
        if cached_id is not None:
            result = await session.execute(select(User).where(User.id == cached_id))
            return result.scalar_one_or_none()
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is not None and use_cache:
        # user.id is always int, but mypy may not know user is User here
        await user_cache.set(cache_key, user.id, ttl=60)
    return user


async def create_user_with_validation(
    session: AsyncSession, email: str, password: str, name: str | None = None
) -> User:
    """Create a user with validation and error handling.
    Raises:
        ValidationError: If email or password is invalid.
        UserAlreadyExistsError: If email already exists.
        Exception: On DB commit failure.
    """
    import traceback

    logging.debug(f"create_user_with_validation called with email={email}, name={name}")
    if not validate_email(email):
        logging.warning(f"Invalid email format: {email}")
        raise ValidationError("Invalid email format.")
    err: str | None = get_password_validation_error(password)
    if err is not None:
        logging.warning(f"Password validation error for {email}: {err}")
        raise ValidationError(err)
    is_unique: bool = await is_email_unique(session, email)
    if not is_unique:
        logging.warning(f"Email already exists: {email}")
        raise UserAlreadyExistsError("Email already exists.")
    from src.utils.hashing import hash_password

    hashed: str = hash_password(password)
    user = User(email=email, hashed_password=hashed, is_active=True)
    if name is not None:
        user.name = name
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        logging.info(f"User created successfully: {user.email}, id={user.id}")
    except Exception as e:
        tb: str = traceback.format_exc()
        logging.error(
            f"Exception during user creation for {email}: {e}\nTraceback: {tb}"
        )
        await session.rollback()
        raise
    return user


async def sensitive_user_action(
    session: AsyncSession, user_id: int, action: str
) -> None:
    """Example of a rate-limited sensitive action.
    Raises:
        UserNotFoundError: If user not found.
        RateLimitExceededError: If rate limit exceeded.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found.")
    limiter_key: Final[str] = f"user:{user_id}:{action}"
    allowed: bool = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        raise RateLimitExceededError(
            f"Too many {action} attempts. Please try again later."
        )
    # ... perform the action ...


async def safe_get_user_by_id(session: AsyncSession, user_id: int) -> User:
    """Get user by ID or raise UserNotFoundError.
    Raises:
        UserNotFoundError: If user not found.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found.")
    return user


async def get_users_by_ids(
    session: AsyncSession, user_ids: Sequence[int]
) -> Sequence[User]:
    """Fetch multiple users by a list of IDs."""
    if not user_ids:
        return []
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    users: Sequence[User] = result.scalars().all()
    return users


async def list_users_paginated(
    session: AsyncSession, offset: int = 0, limit: int = 20
) -> Sequence[User]:
    """List users with pagination support."""
    if limit is None or limit <= 0:
        return []
    result = await session.execute(select(User).offset(offset).limit(limit))
    users: Sequence[User] = result.scalars().all()
    return users


async def list_users(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 20,
    email: str | None = None,
    name: str | None = None,
    q: str | None = None,
    sort: Literal["created_at", "name", "email"] = "created_at",
    order: Literal["desc", "asc"] = "desc",
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> tuple[list[User], int]:
    """List users with filtering and pagination.
    Returns:
        (users, total_count)
    """
    stmt = select(User)
    if email:
        stmt = stmt.where(User.email.ilike(f"%{email}%"))
    if name:
        stmt = stmt.where(User.name.ilike(f"%{name}%"))
    if q:
        stmt = stmt.where(or_(User.email.ilike(f"%{q}%"), User.name.ilike(f"%{q}%")))
    if created_after:
        stmt = stmt.where(User.created_at >= created_after)
    if created_before:
        stmt = stmt.where(User.created_at <= created_before)
    if sort in {"created_at", "name", "email"}:
        col = getattr(User, sort)
        # mypy: col is InstrumentedAttribute[Any, Any], so .desc()/.asc() is fine
        if order == "desc":
            col = col.desc()
        else:
            col = col.asc()
        stmt = stmt.order_by(col)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()
    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    users = list(result.scalars().all())
    return users, total


async def search_users_by_name_or_email(
    session: AsyncSession, query: str, offset: int = 0, limit: int = 20
) -> Sequence[User]:
    """Search users by partial match on email (and name if available)."""
    stmt = (
        select(User).where(User.email.ilike(f"%{query}%")).offset(offset).limit(limit)
    )
    result = await session.execute(stmt)
    users: Sequence[User] = result.scalars().all()
    return users


async def filter_users_by_status(
    session: AsyncSession, is_active: bool
) -> Sequence[User]:
    """Fetch users filtered by their active status."""
    result = await session.execute(select(User).where(User.is_active == is_active))
    users: Sequence[User] = result.scalars().all()
    return users


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
    users: Sequence[User] = result.scalars().all()
    return users


async def count_users(session: AsyncSession, is_active: bool | None = None) -> int:
    """Count users, optionally filtered by active status."""
    stmt = select(func.count()).select_from(User)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    result = await session.execute(stmt)
    count: int = result.scalar_one()
    return count


async def get_active_users(session: AsyncSession) -> Sequence[User]:
    """Fetch all active users."""
    return await filter_users_by_status(session, True)


async def get_inactive_users(session: AsyncSession) -> Sequence[User]:
    """Fetch all inactive users."""
    return await filter_users_by_status(session, False)


async def get_users_by_custom_field(
    session: AsyncSession, field: str, value: object
) -> Sequence[User]:
    """Stub: Fetch users by a custom field (e.g., organization). Not implemented (no such field)."""
    # No custom field in User model
    return []


async def bulk_create_users(
    session: AsyncSession, users: Sequence[User]
) -> Sequence[User]:
    """Bulk create users and return them with IDs.
    Raises:
        Exception: On DB commit failure.
    """
    session.add_all(users)
    try:
        await session.commit()
        for user in users:
            await session.refresh(user)
    except Exception as exc:
        await session.rollback()
        raise exc
    return users


class UserUpdateData(TypedDict, total=False):
    # Add all updatable fields here for strict typing
    email: str
    name: str
    is_active: bool
    is_deleted: bool
    hashed_password: str
    last_login_at: datetime | None
    updated_at: datetime | None


async def bulk_update_users(
    session: AsyncSession, user_ids: Sequence[int], update_data: Mapping[str, object]
) -> int:
    """Bulk update users by IDs with the given update_data dict. Returns number of updated rows.
    Raises:
        Exception: On DB commit failure.
    """
    if not user_ids or not update_data:
        return 0
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    users: Sequence[User] = result.scalars().all()
    for user in users:
        for key, value in update_data.items():
            setattr(user, key, value)
    try:
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise exc
    return len(users)


async def bulk_delete_users(session: AsyncSession, user_ids: Sequence[int]) -> int:
    """Bulk delete users by IDs. Returns number of deleted rows.
    Raises:
        Exception: On DB commit failure.
    """
    if not user_ids:
        return 0
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    users: Sequence[User] = result.scalars().all()
    for user in users:
        await session.delete(user)
    try:
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise exc
    return len(users)


async def soft_delete_user(session: AsyncSession, user_id: int) -> bool:
    """Mark a user as deleted (soft delete).
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None or getattr(user, "is_deleted", False):
        return False
    user.is_deleted = True
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit soft delete for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True


async def restore_user(session: AsyncSession, user_id: int) -> bool:
    """Restore a soft-deleted user.
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None or not getattr(user, "is_deleted", False):
        return False
    user.is_deleted = False
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit restore for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True


async def upsert_user(
    session: AsyncSession, email: str, defaults: Mapping[str, object]
) -> User:
    """Insert or update a user by email. Returns the user.
    Raises:
        ValidationError: If email is invalid.
        Exception: On DB commit failure.
    """
    if not email or not validate_email(email):
        raise ValidationError("Invalid email format.")
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        for key, value in defaults.items():
            if hasattr(user, key):
                setattr(user, key, value)
    else:
        user = User(email=email, **defaults)
        session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception as exc:
        logging.error(f"Failed to commit upsert for user {email}: {exc}")
        await session.rollback()
        raise exc
    return user


async def partial_update_user(
    session: AsyncSession, user_id: int, update_data: Mapping[str, object]
) -> User | None:
    """Update only provided fields for a user.
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None:
        return None
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception as exc:
        logging.error(f"Failed to commit partial update for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return user


async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Check if a user exists by ID."""
    result = await session.execute(select(User.id).where(User.id == user_id))
    exists: bool = result.scalar_one_or_none() is not None
    return exists


async def is_email_unique(
    session: AsyncSession, email: str, exclude_user_id: int | None = None
) -> bool:
    """Check if an email is unique (optionally excluding a user by ID)."""
    stmt = select(User).where(User.email == email)
    if exclude_user_id is not None:
        stmt = stmt.where(User.id != exclude_user_id)
    result = await session.execute(stmt)
    unique: bool = result.scalar_one_or_none() is None
    return unique


async def change_user_password(
    session: AsyncSession, user_id: int, new_hashed_password: str
) -> bool:
    """Change a user's password (hashed).
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None:
        return False
    user.hashed_password = new_hashed_password
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit password change for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True


logger: Final[logging.Logger] = logging.getLogger("user_audit")


async def audit_log_user_change(
    session: AsyncSession, user_id: int, action: str, details: str = ""
) -> None:
    """Log an audit event for a user change. In production, consider integrating with Azure Monitor or Application Insights.
    Raises:
        None
    """
    logger.info(f"User {user_id}: {action}. {details}")
    # Optionally, persist audit logs to DB or send to Azure Monitor here


async def assign_role_to_user(session: AsyncSession, user_id: int, role: str) -> bool:
    """Stub: Assign a role to a user. Not implemented (no role field)."""
    return False


async def revoke_role_from_user(session: AsyncSession, user_id: int, role: str) -> bool:
    """Stub: Revoke a role from a user. Not implemented (no role field)."""
    return False


@asynccontextmanager
async def db_session_context() -> AsyncIterator[AsyncSession]:
    """Async context manager for DB session.
    Yields:
        AsyncSession
    """
    # Adjust the import below to match your actual async session maker location and symbol.
    # For example, if your sessionmaker is named "get_async_session" in "src.core.database", import it as shown:
    # from src.core.database import get_async_session
    # async with get_async_session() as session:

    # If you use SQLAlchemy's async sessionmaker, it might look like this:
    from src.core.database import get_async_session

    async with get_async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def db_transaction(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """Async context manager for DB transaction (atomic operations).
    Yields:
        AsyncSession
    """
    async with session.begin():
        yield session


async def get_user_with_files(session: AsyncSession, user_id: int) -> User | None:
    """Fetch a user and their files separately (WriteOnlyMapped doesn't support eager loading)."""
    from src.models.file import File

    # Get the user first
    result = await session.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        return None

    # Get files separately and attach them as a list
    files_result = await session.execute(select(File).where(File.user_id == user_id))
    files_list = files_result.scalars().all()

    # Store files in a way the test can access
    # For test access only; not a real model field
    user._files = files_list  # type: ignore[attr-defined]

    return user


class UserCSVRow(TypedDict):
    id: int
    email: str
    is_active: bool
    is_deleted: bool
    created_at: object
    updated_at: object
    last_login_at: object


async def export_users_to_csv(session: AsyncSession) -> str:
    """Export all users to CSV string."""
    result = await session.execute(select(User))
    users: Sequence[User] = result.scalars().all()
    output: io.StringIO = io.StringIO()
    writer: csv.DictWriter[str] = csv.DictWriter(
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
        row: UserCSVRow = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at,
        }
        writer.writerow(row)
    return output.getvalue()


class UserJSONRow(TypedDict):
    id: int
    email: str
    is_active: bool
    is_deleted: bool
    created_at: str | None
    updated_at: str | None
    last_login_at: str | None


async def export_users_to_json(session: AsyncSession) -> str:
    """Export all users to JSON string."""
    result = await session.execute(select(User))
    users: Sequence[User] = result.scalars().all()
    data: list[UserJSONRow] = [
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
    session: AsyncSession, user_dicts: Sequence[Mapping[str, object]]
) -> Sequence[User]:
    """Bulk import users from a list of dicts.
    Raises:
        Exception: On DB commit failure.
    """
    users: list[User] = [User(**d) for d in user_dicts]
    session.add_all(users)
    try:
        await session.commit()
        for user in users:
            await session.refresh(user)
    except Exception as exc:
        await session.rollback()
        raise exc
    return users


async def deactivate_user(session: AsyncSession, user_id: int) -> bool:
    """Deactivate a user (set is_active=False).
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None or not getattr(user, "is_active", False):
        return False
    user.is_active = False
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit deactivate for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True


async def reactivate_user(session: AsyncSession, user_id: int) -> bool:
    """Reactivate a user (set is_active=True).
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None or getattr(user, "is_active", False):
        return False
    user.is_active = True
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit reactivate for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True


async def update_last_login(
    session: AsyncSession, user_id: int, login_time: datetime | None = None
) -> bool:
    """Update the last_login_at timestamp for a user.
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id)
    if user is None:
        return False
    dt: datetime = login_time or datetime.now(UTC)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    user.last_login_at = dt
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit last login update for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True


async def anonymize_user(session: AsyncSession, user_id: int) -> bool:
    """Anonymize user data for privacy/GDPR (irreversibly removes PII, disables account).
    Raises:
        Exception: On DB commit failure.
    """
    user: User | None = await get_user_by_id(session, user_id, use_cache=False)
    if user is None or getattr(user, "is_deleted", False):
        return False
    user.email = f"anon_{user.id}_{int(datetime.now(UTC).timestamp())}@anon.invalid"
    user.hashed_password = ""
    user.is_active = False
    user.is_deleted = True
    user.last_login_at = None
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit anonymize for user {user_id}: {exc}")
        await session.rollback()
        raise exc
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
    # result.all() returns Sequence[Row[Any]], so extract values explicitly
    rows: Sequence[Row[Any]] = result.all()
    stats: dict[int, int] = dict.fromkeys(range(1, 13), 0)
    for row in rows:
        month: int = int(row[0])
        count: int = int(row[1])
        stats[month] = count
    return stats


__all__: Final[list[str]] = [
    "safe_get_user_by_id",
    "create_user_with_validation",
    "sensitive_user_action",
    "anonymize_user",
    "user_signups_per_month",
    "UserNotFoundError",
    "select",
]
