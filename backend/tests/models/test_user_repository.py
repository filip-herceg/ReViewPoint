# All repository tests have been migrated to tests/repositories/test_user.py and verified passing as of 2025-06-05.
# This file is now legacy and can be safely removed if no shared fixtures
# or model tests remain.

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File
from src.models.user import User
from src.repositories import user as user_repo
from src.utils.cache import AsyncInMemoryCache
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
    validate_password,
)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_users(async_session: AsyncSession) -> None:
    await async_session.execute(delete(User))
    await async_session.commit()


@pytest.mark.asyncio
async def test_get_user_by_id(async_session: AsyncSession) -> None:
    user = User(email="a@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    found = await user_repo.get_user_by_id(async_session, user_id)
    assert found is not None
    assert found.email == "a@b.com"


@pytest.mark.asyncio
async def test_get_users_by_ids(async_session: AsyncSession) -> None:
    users = [
        User(email=f"u{i}@b.com", hashed_password="pw", is_active=True)
        for i in range(3)
    ]
    async_session.add_all(users)
    await async_session.commit()
    ids = [u.id for u in users]
    found = await user_repo.get_users_by_ids(async_session, ids)
    assert len(found) == 3
    emails = {u.email for u in found}
    for i in range(3):
        assert f"u{i}@b.com" in emails


@pytest.mark.asyncio
async def test_list_users_paginated(async_session: AsyncSession) -> None:
    users = [
        User(email=f"p{i}@b.com", hashed_password="pw", is_active=True)
        for i in range(10)
    ]
    async_session.add_all(users)
    await async_session.commit()
    found = await user_repo.list_users_paginated(async_session, offset=2, limit=5)
    assert len(found) == 5
    assert found[0].email == "p2@b.com"


@pytest.mark.asyncio
async def test_search_users_by_name_or_email(async_session: AsyncSession) -> None:
    users = [
        User(email=f"search{i}@b.com", hashed_password="pw", is_active=True)
        for i in range(5)
    ]
    async_session.add_all(users)
    await async_session.commit()
    found = await user_repo.search_users_by_name_or_email(async_session, "search")
    assert len(found) == 5
    found_none = await user_repo.search_users_by_name_or_email(
        async_session, "notfound"
    )
    assert found_none == []


@pytest.mark.asyncio
async def test_filter_users_by_status(async_session: AsyncSession) -> None:
    users = [
        User(email="active1@b.com", hashed_password="pw", is_active=True),
        User(email="inactive1@b.com", hashed_password="pw", is_active=False),
        User(email="active2@b.com", hashed_password="pw", is_active=True),
    ]
    async_session.add_all(users)
    await async_session.commit()
    active = await user_repo.filter_users_by_status(async_session, True)
    inactive = await user_repo.filter_users_by_status(async_session, False)
    assert len(active) == 2
    assert all(u.is_active for u in active)
    assert len(inactive) == 1
    assert not inactive[0].is_active


@pytest.mark.asyncio
async def test_get_users_created_within(async_session: AsyncSession) -> None:
    now = datetime.now(UTC)
    users = [
        User(
            email="old@b.com",
            hashed_password="pw",
            is_active=True,
            created_at=now - timedelta(days=10),
        ),
        User(
            email="mid@b.com",
            hashed_password="pw",
            is_active=True,
            created_at=now - timedelta(days=5),
        ),
        User(email="new@b.com", hashed_password="pw", is_active=True, created_at=now),
    ]
    async_session.add_all(users)
    await async_session.commit()
    found = await user_repo.get_users_created_within(
        async_session, now - timedelta(days=6), now + timedelta(days=1)
    )
    emails = {u.email for u in found}
    assert "mid@b.com" in emails
    assert "new@b.com" in emails
    assert "old@b.com" not in emails


@pytest.mark.asyncio
async def test_count_users(async_session: AsyncSession) -> None:
    users = [
        User(email=f"c{i}@b.com", hashed_password="pw", is_active=(i % 2 == 0))
        for i in range(6)
    ]
    async_session.add_all(users)
    await async_session.commit()
    total = await user_repo.count_users(async_session)
    active = await user_repo.count_users(async_session, is_active=True)
    inactive = await user_repo.count_users(async_session, is_active=False)
    assert total == 6
    assert active == 3
    assert inactive == 3


@pytest.mark.asyncio
async def test_get_active_inactive_users(async_session: AsyncSession) -> None:
    users = [
        User(email="a@b.com", hashed_password="pw", is_active=True),
        User(email="b@b.com", hashed_password="pw", is_active=False),
    ]
    async_session.add_all(users)
    await async_session.commit()
    active = await user_repo.get_active_users(async_session)
    inactive = await user_repo.get_inactive_users(async_session)
    assert len(active) == 1 and active[0].is_active
    assert len(inactive) == 1 and not inactive[0].is_active


@pytest.mark.asyncio
async def test_filter_users_by_role_stub(async_session: AsyncSession) -> None:
    users = [User(email="r@b.com", hashed_password="pw", is_active=True)]
    async_session.add_all(users)
    await async_session.commit()
    found = await user_repo.filter_users_by_role(async_session, "admin")
    assert found == []


@pytest.mark.asyncio
async def test_get_users_by_custom_field_stub(async_session: AsyncSession) -> None:
    users = [User(email="cf@b.com", hashed_password="pw", is_active=True)]
    async_session.add_all(users)
    await async_session.commit()
    found = await user_repo.get_users_by_custom_field(
        async_session, "organization", "Acme"
    )
    assert found == []


@pytest.mark.asyncio
async def test_bulk_create_users(async_session: AsyncSession) -> None:
    users = [
        User(email=f"bulk{i}@b.com", hashed_password="pw", is_active=True)
        for i in range(3)
    ]
    created = await user_repo.bulk_create_users(async_session, users)
    assert all(u.id is not None for u in created)
    emails = {u.email for u in created}
    for i in range(3):
        assert f"bulk{i}@b.com" in emails


@pytest.mark.asyncio
async def test_bulk_update_users(async_session: AsyncSession) -> None:
    users = [
        User(email=f"upd{i}@b.com", hashed_password="pw", is_active=True)
        for i in range(2)
    ]
    async_session.add_all(users)
    await async_session.commit()
    ids = [u.id for u in users]
    updated_count = await user_repo.bulk_update_users(
        async_session, ids, {"is_active": False}
    )
    assert updated_count == 2
    result = await async_session.execute(select(User).where(User.id.in_(ids)))
    updated = result.scalars().all()
    assert all(not u.is_active for u in updated)


@pytest.mark.asyncio
async def test_bulk_delete_users(async_session: AsyncSession) -> None:
    users = [
        User(email=f"del{i}@b.com", hashed_password="pw", is_active=True)
        for i in range(2)
    ]
    async_session.add_all(users)
    await async_session.commit()
    ids = [u.id for u in users]
    deleted_count = await user_repo.bulk_delete_users(async_session, ids)
    assert deleted_count == 2
    result = await async_session.execute(select(User).where(User.id.in_(ids)))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_soft_delete_and_restore_user(async_session: AsyncSession) -> None:
    user = User(email="soft@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    # Soft delete
    deleted = await user_repo.soft_delete_user(async_session, user_id)
    assert deleted
    user_db = await user_repo.get_user_by_id(async_session, user_id)
    assert user_db is not None and user_db.is_deleted
    # Restore
    restored = await user_repo.restore_user(async_session, user_id)
    assert restored
    user_db = await user_repo.get_user_by_id(async_session, user_id)
    assert user_db is not None and not user_db.is_deleted


@pytest.mark.asyncio
async def test_upsert_user(async_session: AsyncSession) -> None:
    # Insert
    user = await user_repo.upsert_user(
        async_session, "upsert@b.com", {"hashed_password": "pw", "is_active": True}
    )
    assert user.id is not None
    assert user.email == "upsert@b.com"
    # Update
    user2 = await user_repo.upsert_user(
        async_session, "upsert@b.com", {"hashed_password": "pw2", "is_active": False}
    )
    assert user2.id == user.id
    assert user2.hashed_password == "pw2"
    assert not user2.is_active


@pytest.mark.asyncio
async def test_partial_update_user(async_session: AsyncSession) -> None:
    user = User(email="patch@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    updated = await user_repo.partial_update_user(
        async_session, user_id, {"is_active": False}
    )
    assert updated is not None
    assert not updated.is_active
    # Patch non-existent field is ignored
    updated2 = await user_repo.partial_update_user(
        async_session, user_id, {"nonexistent": 123}
    )
    assert updated2 is not None
    assert not hasattr(updated2, "nonexistent")


@pytest.mark.asyncio
async def test_user_exists(async_session: AsyncSession) -> None:
    user = User(email="exists@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    exists = await user_repo.user_exists(async_session, user_id)
    not_exists = await user_repo.user_exists(async_session, 99999)
    assert exists is True
    assert not_exists is False


@pytest.mark.asyncio
async def test_is_email_unique(async_session: AsyncSession) -> None:
    user = User(email="unique@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    # Should not be unique
    unique = await user_repo.is_email_unique(async_session, "unique@b.com")
    assert unique is False
    # Should be unique
    unique2 = await user_repo.is_email_unique(async_session, "other@b.com")
    assert unique2 is True
    # Should be unique if excluding self
    unique3 = await user_repo.is_email_unique(
        async_session, "unique@b.com", exclude_user_id=user_id
    )
    assert unique3 is True


@pytest.mark.asyncio
async def test_change_user_password(async_session: AsyncSession) -> None:
    user = User(email="pw@b.com", hashed_password="old", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    changed = await user_repo.change_user_password(async_session, user_id, "newhash")
    assert changed
    user_db = await user_repo.get_user_by_id(async_session, user_id)
    assert user_db is not None and user_db.hashed_password == "newhash"


@pytest.mark.asyncio
async def test_audit_log_user_change(async_session: AsyncSession) -> None:
    import logging

    logger = logging.getLogger("user_audit")
    from io import StringIO

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    await user_repo.audit_log_user_change(async_session, 1, "update", "Changed email")
    handler.flush()
    logger.removeHandler(handler)
    log_output = stream.getvalue()
    assert "User 1: update. Changed email" in log_output


@pytest.mark.asyncio
async def test_get_user_with_files(async_session: AsyncSession) -> None:
    user = User(email="files@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    files = [
        File(filename=f"f{i}.txt", content_type="text/plain", user_id=user_id)
        for i in range(2)
    ]
    async_session.add_all(files)
    await async_session.commit()
    user_with_files = await user_repo.get_user_with_files(async_session, user_id)
    assert user_with_files is not None
    assert hasattr(user_with_files, "files")
    # Bypass type checker for runtime attribute
    assert len(getattr(user_with_files, "files", [])) == 2


@pytest.mark.asyncio
async def test_db_session_context_and_transaction(async_session: AsyncSession) -> None:
    from src.repositories.user import db_transaction

    # Use the provided async_session fixture instead of db_session_context()
    user = User(email="tx@b.com", hashed_password="pw", is_active=True)
    async with db_transaction(async_session):
        async_session.add(user)
    await async_session.commit()
    found = await async_session.execute(select(User).where(User.email == "tx@b.com"))
    assert found.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_export_users_to_csv_and_json(async_session: AsyncSession) -> None:
    users = [
        User(email=f"exp{i}@b.com", hashed_password="pw", is_active=(i % 2 == 0))
        for i in range(3)
    ]
    async_session.add_all(users)
    await async_session.commit()
    csv_data = await user_repo.export_users_to_csv(async_session)
    json_data = await user_repo.export_users_to_json(async_session)
    # CSV: header and 3 rows
    assert csv_data.count("\n") == 4
    assert "email" in csv_data and "exp0@b.com" in csv_data
    # JSON: list of 3 dicts
    import json as _json

    data = _json.loads(json_data)
    assert isinstance(data, list) and len(data) == 3
    assert any(u["email"] == "exp1@b.com" for u in data)


@pytest.mark.asyncio
async def test_import_users_from_dicts(async_session: AsyncSession) -> None:
    user_dicts = [
        {"email": "imp1@b.com", "hashed_password": "pw", "is_active": True},
        {"email": "imp2@b.com", "hashed_password": "pw", "is_active": False},
    ]
    imported = await user_repo.import_users_from_dicts(async_session, user_dicts)
    assert len(imported) == 2
    emails = {u.email for u in imported}
    assert "imp1@b.com" in emails and "imp2@b.com" in emails
    # Check DB
    found = await user_repo.get_users_by_ids(async_session, [u.id for u in imported])
    assert len(found) == 2


@pytest.mark.asyncio
async def test_deactivate_and_reactivate_user(async_session: AsyncSession) -> None:
    user = User(email="active@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    # Deactivate
    deactivated = await user_repo.deactivate_user(async_session, user_id)
    assert deactivated
    user_db = await user_repo.get_user_by_id(async_session, user_id)
    assert user_db is not None and not user_db.is_active
    # Reactivate
    reactivated = await user_repo.reactivate_user(async_session, user_id)
    assert reactivated
    user_db = await user_repo.get_user_by_id(async_session, user_id)
    assert user_db is not None and user_db.is_active


@pytest.mark.asyncio
async def test_update_last_login(async_session: AsyncSession) -> None:
    from datetime import datetime

    user = User(email="login@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    now = datetime.now(UTC)
    updated = await user_repo.update_last_login(async_session, user_id, login_time=now)
    assert updated
    user_db = await user_repo.get_user_by_id(async_session, user_id)
    assert user_db is not None and user_db.last_login_at is not None
    # Should be close to now
    assert abs((user_db.last_login_at - now).total_seconds()) < 2


@pytest.mark.asyncio
async def test_validate_email_and_password() -> None:
    assert validate_email("test@example.com")
    assert not validate_email("bademail")
    assert validate_password("Abc12345")
    assert not validate_password("short")
    assert not validate_password("nodigits")  # fixed: no digit at all
    assert not validate_password("12345678")
    assert (
        get_password_validation_error("short")
        == "Password must be at least 8 characters."
    )
    assert (
        get_password_validation_error("abcdefgh")
        == "Password must contain at least one digit."
    )
    assert (
        get_password_validation_error("12345678")
        == "Password must contain at least one letter."
    )
    assert get_password_validation_error("Abc12345") is None


@pytest.mark.asyncio
async def test_async_in_memory_cache() -> None:
    cache = AsyncInMemoryCache()
    await cache.set("foo", 123, ttl=0.1)
    assert await cache.get("foo") == 123
    await asyncio.sleep(0.2)
    assert await cache.get("foo") is None
    await cache.set("bar", 456)
    await cache.clear()
    assert await cache.get("bar") is None


@pytest.mark.asyncio
async def test_async_rate_limiter() -> None:
    limiter = AsyncRateLimiter(max_calls=2, period=0.5)
    key = "user:1:test"
    assert await limiter.is_allowed(key)
    assert await limiter.is_allowed(key)
    assert not await limiter.is_allowed(key)
    await asyncio.sleep(0.6)
    assert await limiter.is_allowed(key)


@pytest.mark.asyncio
async def test_error_handling_utilities(async_session: AsyncSession) -> None:
    create_user_with_validation = user_repo.create_user_with_validation
    sensitive_user_action = user_repo.sensitive_user_action
    safe_get_user_by_id = user_repo.safe_get_user_by_id
    # ValidationError
    with pytest.raises(ValidationError):
        await create_user_with_validation(async_session, "bademail", "pw")
    # UserAlreadyExistsError
    user = await create_user_with_validation(async_session, "exists@b.com", "Abc12345")
    user_id = user.id
    with pytest.raises(UserAlreadyExistsError):
        await create_user_with_validation(async_session, "exists@b.com", "Abc12345")
    # UserNotFoundError
    with pytest.raises(UserNotFoundError):
        await safe_get_user_by_id(async_session, 999999)
    # RateLimitExceededError
    for _ in range(5):
        await sensitive_user_action(async_session, user_id, "test")
    with pytest.raises(RateLimitExceededError):
        await sensitive_user_action(async_session, user_id, "test")


@pytest.mark.asyncio
async def test_anonymize_user(async_session: AsyncSession) -> None:
    from src.repositories.user import anonymize_user, get_user_by_id

    user = User(email="gdpr@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    user_id = user.id
    await async_session.refresh(user)
    # Anonymize
    result = await anonymize_user(async_session, user_id)
    assert result
    anon_user = await get_user_by_id(async_session, user_id, use_cache=False)
    assert anon_user is not None
    assert anon_user.is_active is False
    assert anon_user.is_deleted is True
    assert anon_user.hashed_password == ""
    assert anon_user.last_login_at is None
    assert anon_user.email.startswith(f"anon_{user_id}_") and anon_user.email.endswith(
        "@anon.invalid"
    )


@pytest.mark.asyncio
async def test_user_signups_per_month(async_session: AsyncSession) -> None:
    from datetime import datetime

    from src.repositories.user import user_signups_per_month

    # Create users in different months
    now = datetime.now(UTC)
    users = [
        User(
            email="m1@b.com",
            hashed_password="pw",
            is_active=True,
            created_at=now.replace(month=1),
        ),
        User(
            email="m2@b.com",
            hashed_password="pw",
            is_active=True,
            created_at=now.replace(month=2),
        ),
        User(
            email="m2b@b.com",
            hashed_password="pw",
            is_active=True,
            created_at=now.replace(month=2),
        ),
    ]
    async_session.add_all(users)
    await async_session.commit()
    stats = await user_signups_per_month(async_session, now.year)
    assert stats[1] == 1
    assert stats[2] == 2
    for m in range(3, 13):
        assert stats[m] == 0
