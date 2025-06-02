from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User  # type: ignore[attr-defined]


class UserRepository:
    """Async repository for User model."""

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        """Fetch a user by email."""
        stmt = select(User).where(User.email == email, ~User.is_deleted)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession, email: str, hashed_password: str, is_active: bool = True
    ) -> User:
        """Create and persist a new user."""
        user = User(email=email, hashed_password=hashed_password, is_active=is_active)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update_user(session: AsyncSession, user: User, **kwargs: Any) -> User:
        """Update user fields and persist changes."""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, user: User) -> None:
        """Delete a user from the database."""
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def soft_delete_user(session: AsyncSession, user: User) -> User:
        """Soft delete a user (set is_deleted=True)."""
        user.is_deleted = True
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
        """Fetch a user by ID (excluding soft-deleted)."""
        stmt = select(User).where(User.id == user_id, ~User.is_deleted)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_users(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Fetch all users with optional pagination (excluding soft-deleted)."""
        stmt = select(User).where(~User.is_deleted).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_active_users(session: AsyncSession) -> list[User]:
        """Fetch all active users (excluding soft-deleted)."""
        stmt = select(User).where(User.is_active, ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def count_users(session: AsyncSession) -> int:
        """Count total number of users (excluding soft-deleted)."""
        stmt = select(func.count()).select_from(User).where(~User.is_deleted)
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def bulk_create_users(
        session: AsyncSession, users_data: list[dict[str, Any]]
    ) -> list[User]:
        """Bulk create users from a list of dicts."""
        users = [User(**data) for data in users_data]
        session.add_all(users)
        await session.commit()
        for user in users:
            await session.refresh(user)
        return users

    @staticmethod
    async def bulk_update_users(
        session: AsyncSession, user_ids: list[int], update_data: dict[str, Any]
    ) -> int:
        """Bulk update users by IDs with provided fields. Returns number of updated users."""
        stmt = select(User).where(User.id.in_(user_ids), ~User.is_deleted)
        result = await session.execute(stmt)
        users = result.scalars().all()
        for user in users:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
        await session.commit()
        return len(users)

    @staticmethod
    async def bulk_soft_delete_users(session: AsyncSession, user_ids: list[int]) -> int:
        """Bulk soft delete users by IDs. Returns number of users soft deleted."""
        stmt = select(User).where(User.id.in_(user_ids), ~User.is_deleted)
        result = await session.execute(stmt)
        users = result.scalars().all()
        for user in users:
            user.is_deleted = True
        await session.commit()
        return len(users)

    @staticmethod
    async def search_users_by_email(
        session: AsyncSession, email_substring: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Search users by partial email (excluding soft-deleted)."""
        stmt = (
            select(User)
            .where(User.email.ilike(f"%{email_substring}%"), ~User.is_deleted)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def filter_users_by_registration_date(
        session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> list[User]:
        """Filter users by registration (created_at) date range (excluding soft-deleted)."""
        stmt = select(User).where(
            User.created_at >= start_date,
            User.created_at <= end_date,
            ~User.is_deleted,
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_by_role(session: AsyncSession, role: str) -> list[User]:
        """Fetch users with a specific role (requires 'role' field on User)."""
        if not hasattr(User, "role"):
            raise NotImplementedError("User model has no 'role' field.")
        stmt = select(User).where(User.role == role, ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_by_status(session: AsyncSession, is_active: bool) -> list[User]:
        """Fetch users by active status (excluding soft-deleted)."""
        stmt = select(User).where(User.is_active == is_active, ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_created_between(
        session: AsyncSession, start: datetime, end: datetime
    ) -> list[User]:
        """Fetch users created between two dates (excluding soft-deleted)."""
        stmt = select(User).where(
            User.created_at >= start, User.created_at <= end, ~User.is_deleted
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_by_ids(
        session: AsyncSession, user_ids: list[int]
    ) -> list[User]:
        """Fetch users by a list of IDs (excluding soft-deleted)."""
        stmt = select(User).where(User.id.in_(user_ids), ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_with_pagination(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Fetch users with pagination (excluding soft-deleted)."""
        stmt = select(User).where(~User.is_deleted).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_with_profile_info(session: AsyncSession) -> list[Any]:
        """Stub: Join with related profile tables to fetch extended user info."""
        # Requires profile model and relationship
        raise NotImplementedError("Profile info join not implemented.")

    @staticmethod
    async def get_recently_updated_users(
        session: AsyncSession, since: datetime
    ) -> list[User]:
        """Fetch users updated after a certain timestamp (excluding soft-deleted)."""
        stmt = select(User).where(User.updated_at >= since, ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_by_email_domain(
        session: AsyncSession, domain: str
    ) -> list[User]:
        """Fetch users whose email ends with a specific domain (excluding soft-deleted)."""
        stmt = select(User).where(User.email.ilike(f"%@{domain}"), ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_deleted_users(session: AsyncSession) -> list[User]:
        """Fetch users that have been soft-deleted."""
        stmt = select(User).where(User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_users_with_no_login_since(
        session: AsyncSession, date: datetime
    ) -> list[User]:
        """Stub: Fetch users who haven’t logged in since a given date (requires last_login field)."""
        if not hasattr(User, "last_login"):
            raise NotImplementedError("User model has no 'last_login' field.")
        stmt = select(User).where(User.last_login < date, ~User.is_deleted)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def restore_soft_deleted_user(session: AsyncSession, user: User) -> User:
        """Restore a soft-deleted user."""
        user.is_deleted = False
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def permanent_delete_user(session: AsyncSession, user: User) -> None:
        """Permanently delete a user from the database."""
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def bulk_restore_users(session: AsyncSession, user_ids: list[int]) -> int:
        """Restore multiple soft-deleted users by IDs."""
        stmt = select(User).where(User.id.in_(user_ids), User.is_deleted)
        result = await session.execute(stmt)
        users = result.scalars().all()
        for user in users:
            user.is_deleted = False
        await session.commit()
        return len(users)

    @staticmethod
    async def bulk_permanent_delete_users(
        session: AsyncSession, user_ids: list[int]
    ) -> int:
        """Permanently delete multiple users by IDs."""
        stmt = select(User).where(User.id.in_(user_ids))
        result = await session.execute(stmt)
        users = result.scalars().all()
        for user in users:
            await session.delete(user)
        await session.commit()
        return len(users)

    @staticmethod
    async def log_user_audit_event(
        session: AsyncSession, user: User, event: str
    ) -> None:
        """Stub: Log changes to user records for auditing purposes."""
        # Requires audit log model/table
        pass

    @staticmethod
    async def update_user_field(
        session: AsyncSession, user: User, field: str, value: Any
    ) -> User:
        """Update a specific field for a user."""
        if hasattr(user, field):
            setattr(user, field, value)
            await session.commit()
            await session.refresh(user)
        return user

    @staticmethod
    async def deactivate_user(session: AsyncSession, user: User) -> User:
        """Deactivate a user (set is_active=False)."""
        user.is_active = False
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def activate_user(session: AsyncSession, user: User) -> User:
        """Activate a user (set is_active=True)."""
        user.is_active = True
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def anonymize_user(session: AsyncSession, user: User) -> User:
        """Stub: Anonymize user data for GDPR compliance."""
        # Overwrite PII fields, e.g., email, name
        raise NotImplementedError("Anonymization logic not implemented.")

    @staticmethod
    async def export_users(session: AsyncSession, format: str = "csv") -> Any:
        """Stub: Export user data to CSV or JSON."""
        raise NotImplementedError("Export logic not implemented.")

    @staticmethod
    async def advanced_search(
        session: AsyncSession, filters: dict[str, Any]
    ) -> list[User]:
        """Stub: Support for complex queries (multiple filters, full-text search)."""
        raise NotImplementedError("Advanced search not implemented.")

    @staticmethod
    async def get_user_by_id_cached(session: AsyncSession, user_id: int) -> User | None:
        """Stub: Use caching for get_user_by_id (requires cache infra)."""
        # Would use a cache like Redis in production
        return await UserRepository.get_user_by_id(session, user_id)
