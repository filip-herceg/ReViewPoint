import logging
import uuid
from datetime import UTC, datetime, timedelta
from io import StringIO

import pytest
import pytest_asyncio
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File
from src.models.user import User
from src.repositories import user as user_repo
from src.utils.errors import (
    RateLimitExceededError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from src.utils.validation import (
    get_password_validation_error,
    validate_email,
    validate_password,
)

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(autouse=True)
async def cleanup_users(async_session: AsyncSession) -> None:
    await async_session.rollback()  # Ensure session is clean before deleting
    await async_session.execute(delete(User))
    await async_session.commit()


@pytest_asyncio.fixture()
async def user_instance(
    async_session: AsyncSession, request: pytest.FixtureRequest
) -> User:
    unique_email = f"test_{uuid.uuid4().hex[:8]}_{request.node.name}@example.com"
    user = User(
        email=unique_email,
        hashed_password="fakehashedpassword",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def file_instance(async_session: AsyncSession, user_instance: User) -> File:
    file = File(
        filename="file.txt",
        content_type="text/plain",
        user_id=user_instance.id,
    )
    async_session.add(file)
    await async_session.commit()
    await async_session.refresh(file)
    return file


@pytest.mark.parametrize(
    "email, password, expected_email_error, expected_password_error",
    [
        ("test@example.com", "password1", None, None),
        ("invalid_email", "password1", "Invalid email address.", None),
        ("test@example.com", "short", None, "Password must be at least 8 characters."),
        (
            "test@example.com",
            "NoDigitsHere",
            None,
            "Password must contain at least one digit.",
        ),
        (
            "test@example.com",
            "12345678",
            None,
            "Password must contain at least one letter.",
        ),
    ],
)
async def test_user_validation(
    email: str,
    password: str,
    expected_email_error: str | None,
    expected_password_error: str | None,
) -> None:
    """Test user email and password validation separately."""
    from src.utils.validation import validate_email

    # Email validation
    if expected_email_error:
        assert not validate_email(email)
    else:
        assert validate_email(email)
    # Password validation
    error = get_password_validation_error(password)
    if expected_password_error:
        assert error == expected_password_error
    else:
        assert error is None


async def test_create_user(async_session: AsyncSession) -> None:
    """Test creating a new user."""
    user = User(
        email="newuser@example.com",
        hashed_password="fakehashedpassword",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    retrieved_user = await user_repo.get_user_by_id(async_session, user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == user.email


async def test_create_user_already_exists(
    async_session: AsyncSession, user_instance: User
) -> None:
    """Test creating a user that already exists."""
    from src.repositories.user import create_user_with_validation

    with pytest.raises(UserAlreadyExistsError):
        await create_user_with_validation(
            async_session, user_instance.email, "fakehashedpassword1"
        )
    await async_session.rollback()
    # Do not access user_instance after rollback


async def test_get_user(async_session: AsyncSession, user_instance: User) -> None:
    """Test retrieving an existing user."""
    user = await user_repo.get_user_by_id(async_session, user_instance.id)
    assert user is not None
    assert user.email == user_instance.email


async def test_get_user_not_found(async_session: AsyncSession) -> None:
    """Test retrieving a user that does not exist."""
    user = await user_repo.get_user_by_id(async_session, 999)
    assert user is None


async def test_update_user(async_session: AsyncSession, user_instance: User) -> None:
    """Test updating an existing user."""
    user_instance.is_active = False
    async_session.add(user_instance)
    await async_session.commit()
    updated_user = await user_repo.get_user_by_id(async_session, user_instance.id)
    assert updated_user is not None
    assert updated_user.is_active is False


async def test_delete_user(async_session: AsyncSession, user_instance: User) -> None:
    """Test deleting an existing user."""
    # Delete all files for this user first to avoid FK constraint error
    await async_session.execute(delete(File).where(File.user_id == user_instance.id))
    await async_session.commit()
    await async_session.delete(user_instance)
    await async_session.commit()
    user = await user_repo.get_user_by_id(async_session, user_instance.id)
    assert user is None


async def test_create_file_for_user(
    async_session: AsyncSession, user_instance: User
) -> None:
    file = File(
        filename="newfile.txt",
        content_type="text/plain",
        user_id=user_instance.id,
    )
    async_session.add(file)
    await async_session.commit()
    await async_session.refresh(file)
    result = await async_session.execute(select(File).where(File.id == file.id))
    retrieved_file = result.scalar_one_or_none()
    assert retrieved_file is not None
    assert retrieved_file.filename == file.filename
    assert retrieved_file.user_id == file.user_id


async def test_get_user_files(
    async_session: AsyncSession, user_instance: User, file_instance: File
) -> None:
    """Test retrieving files for a user."""
    result = await async_session.execute(
        select(File).where(File.user_id == user_instance.id)
    )
    files = result.scalars().all()
    assert len(files) >= 1
    assert any(f.id == file_instance.id for f in files)


# Rate limiting tests removed due to missing user_repo_no_cache fixture


async def test_email_validation() -> None:
    """Test email validation."""
    valid_email = "test@example.com"
    invalid_email = "invalid_email"
    assert validate_email(valid_email) is True
    with pytest.raises(ValidationError):
        if not validate_email(invalid_email):
            raise ValidationError()
    # No DB session to rollback here


async def test_password_validation() -> None:
    """Test password validation."""
    valid_password = "StrongPassw0rd!"
    short_password = "short"
    assert validate_password(valid_password) is True
    with pytest.raises(ValidationError):
        if not validate_password(short_password):
            raise ValidationError()
    # No DB session to rollback here


@pytest.mark.asyncio
async def test_get_user_by_id(async_session: AsyncSession) -> None:
    user = User(email="a@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    found = await user_repo.get_user_by_id(async_session, user.id)
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
    # Delete any files related to these users to avoid FK constraint errors
    await async_session.execute(delete(File).where(File.user_id.in_(ids)))
    await async_session.commit()
    deleted_count = await user_repo.bulk_delete_users(async_session, ids)
    assert deleted_count == 2
    result = await async_session.execute(select(User).where(User.id.in_(ids)))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_soft_delete_and_restore_user(async_session: AsyncSession) -> None:
    user = User(email="soft@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    deleted = await user_repo.soft_delete_user(async_session, user.id)
    assert deleted
    user_db = await user_repo.get_user_by_id(async_session, user.id)
    assert user_db is not None and user_db.is_deleted
    restored = await user_repo.restore_user(async_session, user.id)
    assert restored
    user_db = await user_repo.get_user_by_id(async_session, user.id)
    assert user_db is not None and not user_db.is_deleted


@pytest.mark.asyncio
async def test_upsert_user(async_session: AsyncSession) -> None:
    user = await user_repo.upsert_user(
        async_session, "upsert@b.com", {"hashed_password": "pw", "is_active": True}
    )
    assert user.id is not None
    assert user.email == "upsert@b.com"
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
    await async_session.refresh(user)
    updated = await user_repo.partial_update_user(
        async_session, user.id, {"is_active": False}
    )
    assert updated is not None
    assert not updated.is_active
    updated2 = await user_repo.partial_update_user(
        async_session, user.id, {"nonexistent": 123}
    )
    assert updated2 is not None
    assert not hasattr(updated2, "nonexistent")


@pytest.mark.asyncio
async def test_user_exists(async_session: AsyncSession) -> None:
    user = User(email="exists@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    exists = await user_repo.user_exists(async_session, user.id)
    not_exists = await user_repo.user_exists(async_session, 99999)
    assert exists is True
    assert not_exists is False


@pytest.mark.asyncio
async def test_is_email_unique(async_session: AsyncSession) -> None:
    user = User(email="unique@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    unique = await user_repo.is_email_unique(async_session, "unique@b.com")
    assert unique is False
    unique2 = await user_repo.is_email_unique(async_session, "other@b.com")
    assert unique2 is True
    unique3 = await user_repo.is_email_unique(
        async_session, "unique@b.com", exclude_user_id=user.id
    )
    assert unique3 is True


@pytest.mark.asyncio
async def test_change_user_password(async_session: AsyncSession) -> None:
    user = User(email="pw@b.com", hashed_password="old", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    changed = await user_repo.change_user_password(async_session, user.id, "newhash")
    assert changed
    user_db = await user_repo.get_user_by_id(async_session, user.id)
    assert user_db is not None and user_db.hashed_password == "newhash"


@pytest.mark.asyncio
async def test_audit_log_user_change(async_session: AsyncSession) -> None:
    logger = logging.getLogger("user_audit")
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
    # Clean up all files before test
    await async_session.execute(delete(File))
    await async_session.commit()
    user = User(email="files@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    files = [
        File(filename=f"f{i}.txt", content_type="text/plain", user_id=user.id)
        for i in range(2)
    ]
    async_session.add_all(files)
    await async_session.commit()
    user_with_files = await user_repo.get_user_with_files(async_session, user.id)
    # Only count files created in this test
    test_filenames = {"f0.txt", "f1.txt"}
    user_files = [
        f for f in getattr(user_with_files, "files", []) if f.filename in test_filenames
    ]
    assert len(user_files) == 2


@pytest.mark.asyncio
async def test_db_session_context_and_transaction() -> None:
    from src.repositories.user import db_session_context, db_transaction

    async with db_session_context() as session:
        user = User(email="tx@b.com", hashed_password="pw", is_active=True)
        async with db_transaction(session):
            session.add(user)
        await session.commit()
        found = await session.execute(select(User).where(User.email == "tx@b.com"))
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
    assert csv_data.count("\n") == 4
    assert "email" in csv_data and "exp0@b.com" in csv_data
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
    found = await user_repo.get_users_by_ids(async_session, [u.id for u in imported])
    assert len(found) == 2


@pytest.mark.asyncio
async def test_deactivate_and_reactivate_user(async_session: AsyncSession) -> None:
    user = User(email="active@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    deactivated = await user_repo.deactivate_user(async_session, user.id)
    assert deactivated
    user_db = await user_repo.get_user_by_id(async_session, user.id)
    assert user_db is not None and not user_db.is_active
    reactivated = await user_repo.reactivate_user(async_session, user.id)
    assert reactivated
    user_db = await user_repo.get_user_by_id(async_session, user.id)
    assert user_db is not None and user_db.is_active


@pytest.mark.asyncio
async def test_update_last_login(async_session: AsyncSession) -> None:
    from datetime import datetime

    user = User(email="login@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    now = datetime.now(UTC)
    updated = await user_repo.update_last_login(async_session, user.id, login_time=now)
    assert updated
    user_db = await user_repo.get_user_by_id(async_session, user.id)
    assert user_db is not None and user_db.last_login_at is not None
    assert abs((user_db.last_login_at - now).total_seconds()) < 2


@pytest.mark.asyncio
async def test_anonymize_user(async_session: AsyncSession) -> None:
    from src.repositories.user import anonymize_user, get_user_by_id

    user = User(email="gdpr@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    user_id = user.id
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


@pytest.mark.asyncio
async def test_error_handling_utilities(async_session: AsyncSession) -> None:
    create_user_with_validation = user_repo.create_user_with_validation
    sensitive_user_action = user_repo.sensitive_user_action
    safe_get_user_by_id = user_repo.safe_get_user_by_id
    from src.repositories.user import user_action_limiter
    from src.utils.errors import (
        ValidationError,
    )

    # ValidationError
    with pytest.raises(ValidationError):
        await create_user_with_validation(async_session, "bademail", "pw")
    await async_session.rollback()
    user = await create_user_with_validation(async_session, "exists@b.com", "Abc12345")
    assert user is not None
    user_id = user.id  # Store user id before rollback
    with pytest.raises(UserAlreadyExistsError):
        await create_user_with_validation(async_session, "exists@b.com", "Abc12345")
    await async_session.rollback()
    # Reset rate limiter for this user before testing rate limit
    user_action_limiter.reset(f"user:{user_id}:test")
    for _ in range(5):
        await sensitive_user_action(async_session, user_id, "test")
    with pytest.raises(RateLimitExceededError):
        await sensitive_user_action(async_session, user_id, "test")
    await async_session.rollback()
    with pytest.raises(UserNotFoundError):
        await safe_get_user_by_id(async_session, 999999)
    await async_session.rollback()


@pytest.mark.asyncio
async def test_bulk_create_users_empty(async_session: AsyncSession) -> None:
    created = await user_repo.bulk_create_users(async_session, [])
    assert created == []


@pytest.mark.asyncio
async def test_bulk_update_users_empty(async_session: AsyncSession) -> None:
    updated_count = await user_repo.bulk_update_users(
        async_session, [], {"is_active": False}
    )
    assert updated_count == 0


@pytest.mark.asyncio
async def test_bulk_delete_users_empty(async_session: AsyncSession) -> None:
    deleted_count = await user_repo.bulk_delete_users(async_session, [])
    assert deleted_count == 0


@pytest.mark.asyncio
async def test_partial_update_user_invalid_id(async_session: AsyncSession) -> None:
    updated = await user_repo.partial_update_user(
        async_session, 999999, {"is_active": False}
    )
    assert updated is None


@pytest.mark.asyncio
async def test_upsert_user_invalid_email(async_session: AsyncSession) -> None:
    with pytest.raises(ValidationError):
        await user_repo.upsert_user(async_session, "", {"hashed_password": "pw"})
    await async_session.rollback()


@pytest.mark.asyncio
async def test_get_user_by_id_invalid(async_session: AsyncSession) -> None:
    user = await user_repo.get_user_by_id(async_session, 999999)
    assert user is None


@pytest.mark.asyncio
async def test_get_users_by_ids_empty(async_session: AsyncSession) -> None:
    found = await user_repo.get_users_by_ids(async_session, [])
    assert found == []


@pytest.mark.asyncio
async def test_filter_users_by_status_no_users(async_session: AsyncSession) -> None:
    active = await user_repo.filter_users_by_status(async_session, True)
    inactive = await user_repo.filter_users_by_status(async_session, False)
    assert active == []
    assert inactive == []


@pytest.mark.asyncio
async def test_restore_user_not_deleted(async_session: AsyncSession) -> None:
    user = User(email="restore@b.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    restored = await user_repo.restore_user(async_session, user.id)
    assert restored is False


@pytest.mark.asyncio
async def test_soft_delete_user_invalid_id(async_session: AsyncSession) -> None:
    deleted = await user_repo.soft_delete_user(async_session, 999999)
    assert deleted is False


@pytest.mark.asyncio
async def test_deactivate_user_invalid_id(async_session: AsyncSession) -> None:
    deactivated = await user_repo.deactivate_user(async_session, 999999)
    assert deactivated is False


@pytest.mark.asyncio
async def test_reactivate_user_invalid_id(async_session: AsyncSession) -> None:
    reactivated = await user_repo.reactivate_user(async_session, 999999)
    assert reactivated is False


@pytest.mark.asyncio
async def test_update_last_login_invalid_id(async_session: AsyncSession) -> None:
    updated = await user_repo.update_last_login(async_session, 999999)
    assert updated is False


@pytest.mark.asyncio
async def test_anonymize_user_invalid_id(async_session: AsyncSession) -> None:
    from src.repositories.user import anonymize_user

    result = await anonymize_user(async_session, 999999)
    assert result is False


@pytest.mark.asyncio
async def test_import_users_from_dicts_empty(async_session: AsyncSession) -> None:
    imported = await user_repo.import_users_from_dicts(async_session, [])
    assert imported == []


@pytest.mark.asyncio
async def test_export_users_to_csv_and_json_no_users(
    async_session: AsyncSession,
) -> None:
    csv_data = await user_repo.export_users_to_csv(async_session)
    json_data = await user_repo.export_users_to_json(async_session)
    assert "email" in csv_data
    import json as _json

    data = _json.loads(json_data)
    assert isinstance(data, list) and len(data) == 0


@pytest.mark.asyncio
async def test_user_signups_per_month_no_users(async_session: AsyncSession) -> None:
    from datetime import datetime

    from src.repositories.user import user_signups_per_month

    now = datetime.now(UTC)
    stats = await user_signups_per_month(async_session, now.year)
    assert all(v == 0 for v in stats.values())


@pytest.mark.asyncio
async def test_get_user_with_files_invalid_id(async_session: AsyncSession) -> None:
    user_with_files = await user_repo.get_user_with_files(async_session, 999999)
    assert user_with_files is None


@pytest.mark.asyncio
async def test_safe_get_user_by_id_invalid(async_session: AsyncSession) -> None:
    with pytest.raises(user_repo.UserNotFoundError):
        await user_repo.safe_get_user_by_id(async_session, 999999)
    await async_session.rollback()


@pytest.mark.asyncio
async def test_sensitive_user_action_invalid_user(async_session: AsyncSession) -> None:
    with pytest.raises(user_repo.UserNotFoundError):
        await user_repo.sensitive_user_action(async_session, 999999, "test")
    await async_session.rollback()
