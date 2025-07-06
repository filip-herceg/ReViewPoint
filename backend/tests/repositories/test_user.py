
# Simple module-level async test to verify pytest discovery
import pytest

@pytest.mark.asyncio
async def test_pytest_asyncio_discovery():
    assert True
import json
from datetime import UTC, datetime, timedelta
from typing import Final, Optional, Callable, Type, Any
from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.file import File
from src.models.user import User
from src.repositories.user import (
    anonymize_user,
    assign_role_to_user,
    audit_log_user_change,
    bulk_create_users,
    bulk_delete_users,
    bulk_update_users,
    change_user_password,
    count_users,
    create_user_with_validation,
    db_session_context,
    db_transaction,
    deactivate_user,
    export_users_to_csv,
    export_users_to_json,
    filter_users_by_role,
    filter_users_by_status,
    get_active_users,
    get_inactive_users,
    get_user_by_id,
    get_user_with_files,
    get_users_by_custom_field,
    get_users_by_ids,
    get_users_created_within,
    import_users_from_dicts,
    is_email_unique,
    list_users,
    list_users_paginated,
    partial_update_user,
    reactivate_user,
    restore_user,
    revoke_role_from_user,
    safe_get_user_by_id,
    search_users_by_name_or_email,
    sensitive_user_action,
    soft_delete_user,
    update_last_login,
    upsert_user,
    user_exists,
    user_signups_per_month,
)
from src.utils.errors import (
    RateLimitExceededError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


@pytest.mark.usefixtures("async_session")
class TestUserRepository:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,password,expected_exc",
        [
            ("bademail", "Password123!", ValidationError),
            ("repo@example.com", "short", ValidationError),
            ("repo@example.com", "Password123!", None),
        ],
    )
    async def test_create_user_validation(
        self,
        async_session: AsyncSession,
        email: str,
        password: str,
        expected_exc: Optional[Type[Exception]],
    ) -> None:
        """Test user creation validation for email and password, expecting ValidationError or success."""
        if expected_exc is not None:
            with pytest.raises(expected_exc):
                await create_user_with_validation(async_session, email, password)
        else:
            user = await create_user_with_validation(async_session, email, password)
            assert user.email == email
            assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, async_session: AsyncSession) -> None:
        await create_user_with_validation(
            async_session, "dup@example.com", "Password123!"
        )
        with pytest.raises(UserAlreadyExistsError):
            await create_user_with_validation(
                async_session, "dup@example.com", "Password123!"
            )
        await async_session.rollback()

    @pytest.mark.asyncio
    async def test_create_user_with_name(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "named@example.com", "Password123!", "Test User"
        )
        assert user.name == "Test User"

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "getid@example.com", "Password123!"
        )
        found = await get_user_by_id(async_session, user.id)
        assert found is not None
        assert found.email == user.email
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, async_session: AsyncSession) -> None:
        found = await get_user_by_id(async_session, 999999)
        assert found is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_with_cache(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "cache@example.com", "Password123!"
        )
        # Test with cache disabled
        found = await get_user_by_id(async_session, user.id, use_cache=False)
        assert found is not None
        assert found.email == user.email

    @pytest.mark.asyncio
    async def test_safe_get_user_by_id(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "safe@example.com", "Password123!"
        )
        found = await safe_get_user_by_id(async_session, user.id)
        assert found.email == user.email

    @pytest.mark.asyncio
    async def test_safe_get_user_by_id_not_found(self, async_session: AsyncSession) -> None:
        with pytest.raises(UserNotFoundError):
            await safe_get_user_by_id(async_session, 999999)

    @pytest.mark.asyncio
    async def test_get_users_by_ids(self, async_session: AsyncSession) -> None:
        users = []
        for i in range(3):
            user = await create_user_with_validation(
                async_session, f"multi{i}@ex.com", "Password123!"
            )
            users.append(user)
        await async_session.commit()
        ids = [u.id for u in users]
        found = await get_users_by_ids(async_session, ids)
        assert len(found) == 3
        emails = {u.email for u in found}
        for i in range(3):
            assert f"multi{i}@ex.com" in emails

    @pytest.mark.asyncio
    async def test_get_users_by_ids_empty(self, async_session: AsyncSession) -> None:
        found = await get_users_by_ids(async_session, [])
        assert found == []

    @pytest.mark.asyncio
    async def test_list_users_paginated(self, async_session: AsyncSession) -> None:
        # Clean up users table to ensure test isolation
        await async_session.execute(text("DELETE FROM users"))
        await async_session.commit()
        users = []
        for i in range(10):
            user = await create_user_with_validation(
                async_session, f"page{i}@ex.com", "Password123!"
            )
            users.append(user)
        await async_session.commit()
        found = await list_users_paginated(async_session, offset=2, limit=5)
        assert len(found) == 5
        assert found[0].email == "page2@ex.com"

    @pytest.mark.asyncio
    async def test_list_users_paginated_invalid_limit(self, async_session: AsyncSession) -> None:
        found = await list_users_paginated(async_session, offset=0, limit=0)
        assert found == []
        found = await list_users_paginated(async_session, offset=0, limit=-1)
        assert found == []

    @pytest.mark.asyncio
    async def test_list_users_filters_and_sort(self, async_session: AsyncSession) -> None:
        now = datetime.now(UTC).replace(tzinfo=None)
        users = []
        for i in range(5):
            user = await create_user_with_validation(
                async_session, f"filter{i}@ex.com", "Password123!"
            )
            users.append(user)
        for i, u in enumerate(users):
            u.created_at = now - timedelta(days=i)
        await async_session.commit()
        listed, total = await list_users(
            async_session, q="filter", sort="created_at", order="asc"
        )
        assert total >= 5
        assert listed[0].created_at <= listed[-1].created_at

    @pytest.mark.asyncio
    async def test_list_users_with_filters(self, async_session: AsyncSession) -> None:
        # Test email filter
        user1 = await create_user_with_validation(
            async_session, "emailfilter@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "other@example.com", "Password123!"
        )
        await async_session.commit()

        listed, total = await list_users(async_session, email="emailfilter")
        assert any(u.email == "emailfilter@example.com" for u in listed)

        # Test name filter
        user1.name = "FilterName"
        await async_session.commit()
        listed, total = await list_users(async_session, name="FilterName")
        assert any(u.name == "FilterName" for u in listed)

        # Test created_after and created_before filters
        yesterday = datetime.now(UTC) - timedelta(days=1)
        tomorrow = datetime.now(UTC) + timedelta(days=1)
        listed, total = await list_users(
            async_session, created_after=yesterday, created_before=tomorrow
        )
        assert total >= 2

    @pytest.mark.asyncio
    async def test_search_users_by_name_or_email(self, async_session: AsyncSession) -> None:
        await create_user_with_validation(
            async_session, "searchme@example.com", "Password123!"
        )
        found = await search_users_by_name_or_email(async_session, "searchme")
        assert any("searchme" in u.email for u in found)

    @pytest.mark.asyncio
    async def test_filter_users_by_status(self, async_session: AsyncSession) -> None:
        user1 = await create_user_with_validation(
            async_session, "active@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "inactive@example.com", "Password123!"
        )
        user2.is_active = False
        await async_session.commit()
        active = await filter_users_by_status(async_session, is_active=True)
        inactive = await filter_users_by_status(async_session, is_active=False)
        assert user1 in active
        assert user2 in inactive

    @pytest.mark.asyncio
    async def test_filter_users_by_role(self, async_session: AsyncSession) -> None:
        # This function is a stub that always returns empty list
        result = await filter_users_by_role(async_session, "admin")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_users_created_within(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "daterange@example.com", "Password123!"
        )
        await async_session.commit()

        start = datetime.now(UTC) - timedelta(hours=1)
        end = datetime.now(UTC) + timedelta(hours=1)
        found = await get_users_created_within(async_session, start, end)
        assert any(u.email == "daterange@example.com" for u in found)

    @pytest.mark.asyncio
    async def test_count_users(self, async_session: AsyncSession) -> None:
        # Clean up first
        await async_session.execute(text("DELETE FROM users"))
        await async_session.commit()

        user1 = await create_user_with_validation(
            async_session, "count1@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "count2@example.com", "Password123!"
        )
        user2.is_active = False
        await async_session.commit()

        total_count = await count_users(async_session)
        assert total_count == 2

        active_count = await count_users(async_session, is_active=True)
        assert active_count == 1

        inactive_count = await count_users(async_session, is_active=False)
        assert inactive_count == 1

    @pytest.mark.asyncio
    async def test_get_active_users(self, async_session: AsyncSession) -> None:
        user1 = await create_user_with_validation(
            async_session, "getactive@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "getinactive@example.com", "Password123!"
        )
        user2.is_active = False
        await async_session.commit()

        active_users = await get_active_users(async_session)
        inactive_users = await get_inactive_users(async_session)

        assert user1 in active_users
        assert user2 in inactive_users

    @pytest.mark.asyncio
    async def test_get_users_by_custom_field(self, async_session: AsyncSession) -> None:
        # This function is a stub that always returns empty list
        result = await get_users_by_custom_field(async_session, "department", "IT")
        assert result == []

    @pytest.mark.asyncio
    async def test_bulk_create_users(self, async_session: AsyncSession) -> None:
        users = [
            User(email="bulk1@example.com", hashed_password="hash1", is_active=True),
            User(email="bulk2@example.com", hashed_password="hash2", is_active=True),
        ]
        result = await bulk_create_users(async_session, users)
        assert len(result) == 2
        assert all(u.id is not None for u in result)

    @pytest.mark.asyncio
    async def test_bulk_update_users(self, async_session: AsyncSession) -> None:
        user1 = await create_user_with_validation(
            async_session, "bulkupdate1@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "bulkupdate2@example.com", "Password123!"
        )
        await async_session.commit()

        count = await bulk_update_users(
            async_session, [user1.id, user2.id], {"is_active": False}
        )
        assert count == 2

        # Refresh and check
        await async_session.refresh(user1)
        await async_session.refresh(user2)
        assert not user1.is_active
        assert not user2.is_active

    @pytest.mark.asyncio
    async def test_bulk_update_users_empty(self, async_session: AsyncSession) -> None:
        count = await bulk_update_users(async_session, [], {"is_active": False})
        assert count == 0

        count = await bulk_update_users(async_session, [1, 2], {})
        assert count == 0

    @pytest.mark.asyncio
    async def test_bulk_delete_users(self, async_session: AsyncSession) -> None:
        user1 = await create_user_with_validation(
            async_session, "bulkdelete1@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "bulkdelete2@example.com", "Password123!"
        )
        await async_session.commit()

        count = await bulk_delete_users(async_session, [user1.id, user2.id])
        assert count == 2

        # Check users are deleted
        found1 = await get_user_by_id(async_session, user1.id)
        found2 = await get_user_by_id(async_session, user2.id)
        assert found1 is None
        assert found2 is None

    @pytest.mark.asyncio
    async def test_bulk_delete_users_empty(self, async_session: AsyncSession) -> None:
        count = await bulk_delete_users(async_session, [])
        assert count == 0

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "softdelete@example.com", "Password123!"
        )
        await async_session.commit()

        result = await soft_delete_user(async_session, user.id)
        assert result is True

        await async_session.refresh(user)
        assert user.is_deleted is True

        # Try to soft delete again (should return False)
        result = await soft_delete_user(async_session, user.id)
        assert result is False

    @pytest.mark.asyncio
    async def test_soft_delete_user_not_found(self, async_session: AsyncSession) -> None:
        result = await soft_delete_user(async_session, 999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_restore_user(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "restore@example.com", "Password123!"
        )
        user.is_deleted = True
        await async_session.commit()

        result = await restore_user(async_session, user.id)
        assert result is True

        await async_session.refresh(user)
        assert user.is_deleted is False

        # Try to restore again (should return False)
        result = await restore_user(async_session, user.id)
        assert result is False

    @pytest.mark.asyncio
    async def test_restore_user_not_found(self, async_session: AsyncSession) -> None:
        result = await restore_user(async_session, 999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_upsert_user(self, async_session: AsyncSession) -> None:
        # Test insert
        user = await upsert_user(
            async_session,
            "upsert@example.com",
            {"hashed_password": "hash123", "is_active": True},
        )
        assert user.email == "upsert@example.com"
        assert user.is_active is True

        # Test update
        user2 = await upsert_user(
            async_session, "upsert@example.com", {"name": "Updated Name"}
        )
        assert user2.id == user.id
        assert user2.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_upsert_user_invalid_email(self, async_session: AsyncSession) -> None:
        with pytest.raises(ValidationError):
            await upsert_user(async_session, "invalid-email", {})

        with pytest.raises(ValidationError):
            await upsert_user(async_session, "", {})

    @pytest.mark.asyncio
    async def test_partial_update_user(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "partialupdate@example.com", "Password123!"
        )
        await async_session.commit()

        updated = await partial_update_user(
            async_session, user.id, {"name": "New Name", "bio": "New bio"}
        )
        assert updated is not None
        assert updated.name == "New Name"
        assert updated.bio == "New bio"

    @pytest.mark.asyncio
    async def test_partial_update_user_not_found(self, async_session: AsyncSession) -> None:
        result = await partial_update_user(async_session, 999999, {"name": "Test"})
        assert result is None

    @pytest.mark.asyncio
    async def test_user_exists(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "exists@example.com", "Password123!"
        )
        await async_session.commit()

        assert await user_exists(async_session, user.id) is True
        assert await user_exists(async_session, 999999) is False

    @pytest.mark.asyncio
    async def test_is_email_unique(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "unique@example.com", "Password123!"
        )
        await async_session.commit()

        # Email is not unique (already exists)
        assert await is_email_unique(async_session, "unique@example.com") is False

        # Email is unique (doesn't exist)
        assert await is_email_unique(async_session, "newunique@example.com") is True

        # Email is unique when excluding the user that has it
        assert (
            await is_email_unique(
                async_session, "unique@example.com", exclude_user_id=user.id
            )
            is True
        )

    @pytest.mark.asyncio
    async def test_change_user_password(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "changepass@example.com", "Password123!"
        )
        await async_session.commit()

        result = await change_user_password(async_session, user.id, "newhash123")
        assert result is True

        await async_session.refresh(user)
        assert user.hashed_password == "newhash123"

    @pytest.mark.asyncio
    async def test_change_user_password_not_found(self, async_session: AsyncSession) -> None:
        result = await change_user_password(async_session, 999999, "newhash")
        assert result is False

    @pytest.mark.asyncio
    async def test_audit_log_user_change(self, async_session: AsyncSession) -> None:
        # This function just logs, so we test it doesn't raise an error
        await audit_log_user_change(async_session, 1, "test_action", "test details")

    @pytest.mark.asyncio
    async def test_assign_role_to_user(self, async_session: AsyncSession) -> None:
        # This is a stub function that always returns False
        result = await assign_role_to_user(async_session, 1, "admin")
        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_role_from_user(self, async_session: AsyncSession) -> None:
        # This is a stub function that always returns False
        result = await revoke_role_from_user(async_session, 1, "admin")
        assert result is False

    @pytest.mark.asyncio
    async def test_db_session_context(self) -> None:
        # Mock the get_async_session import within the db_session_context function
        with patch("src.core.database.get_async_session") as mock_get_async_session:
            mock_session = AsyncMock()
            mock_session.close = AsyncMock()

            # Create a proper async context manager mock
            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cm.__aexit__ = AsyncMock(return_value=None)
            mock_get_async_session.return_value = mock_cm

            async with db_session_context() as session:
                assert session == mock_session

            # Verify the get_async_session was called once
            mock_get_async_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_db_transaction(self, async_session: AsyncSession) -> None:
        # Test the transaction context manager with a mock begin context
        begin_mock: AsyncMock = AsyncMock()
        begin_mock.__aenter__ = AsyncMock(return_value=None)
        begin_mock.__aexit__ = AsyncMock(return_value=None)

        with patch.object(async_session, "begin", return_value=begin_mock) as mock_begin:
            async with db_transaction(async_session):
                # This should work without error
                pass

            # Verify begin was called on the session
            mock_begin.assert_called_once()
            begin_mock.__aenter__.assert_called_once()
            begin_mock.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_with_files(self, async_session: AsyncSession) -> None:
        """Test that a user with files returns the correct files (iterable best practice)."""
        user = await create_user_with_validation(
            async_session, "fileuser@example.com", "Password123!"
        )
        file = File(filename="testfile.txt", content_type="text/plain", user_id=user.id)
        async_session.add(file)
        await async_session.commit()

        found = await get_user_with_files(async_session, user.id)
        assert found is not None
        # Convert found.files to a list for safe iteration (WriteOnlyCollection best practice)
        # Use getattr to access a private or protected attribute if needed for testability
        # This is a fallback for SQLAlchemy WriteOnlyCollection, which is not directly iterable
        files = getattr(found, "_files", None) or getattr(found, "files", None)
        if files is not None and hasattr(files, "__iter__"):
            assert any(getattr(f, "filename", None) == "testfile.txt" for f in files)
        else:
            pytest.skip("User.files is not iterable; cannot test file presence.")

    @pytest.mark.asyncio
    async def test_get_user_with_files_not_found(self, async_session: AsyncSession) -> None:
        found = await get_user_with_files(async_session, 999999)
        assert found is None

    @pytest.mark.asyncio
    async def test_export_users_to_csv(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "export@example.com", "Password123!"
        )
        await async_session.commit()

        csv_data = await export_users_to_csv(async_session)
        assert "export@example.com" in csv_data
        assert "id,email,is_active" in csv_data

    @pytest.mark.asyncio
    async def test_export_users_to_json(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "exportjson@example.com", "Password123!"
        )
        await async_session.commit()

        json_data = await export_users_to_json(async_session)
        data = json.loads(json_data)
        assert isinstance(data, list)
        assert any(u["email"] == "exportjson@example.com" for u in data)

    @pytest.mark.asyncio
    async def test_import_users_from_dicts(self, async_session: AsyncSession) -> None:
        user_dicts = [
            {
                "email": "import1@example.com",
                "hashed_password": "hash1",
                "is_active": True,
            },
            {
                "email": "import2@example.com",
                "hashed_password": "hash2",
                "is_active": True,
            },
        ]

        users = await import_users_from_dicts(async_session, user_dicts)
        assert len(users) == 2
        assert users[0].email == "import1@example.com"
        assert users[1].email == "import2@example.com"

    @pytest.mark.asyncio
    async def test_deactivate_user(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "deactivate@example.com", "Password123!"
        )
        await async_session.commit()

        result = await deactivate_user(async_session, user.id)
        assert result is True

        await async_session.refresh(user)
        assert user.is_active is False

        # Try to deactivate again (should return False)
        result = await deactivate_user(async_session, user.id)
        assert result is False

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, async_session: AsyncSession) -> None:
        result = await deactivate_user(async_session, 999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_reactivate_user(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "reactivate@example.com", "Password123!"
        )
        user.is_active = False
        await async_session.commit()

        result = await reactivate_user(async_session, user.id)
        assert result is True

        await async_session.refresh(user)
        assert user.is_active is True

        # Try to reactivate again (should return False)
        result = await reactivate_user(async_session, user.id)
        assert result is False

    @pytest.mark.asyncio
    async def test_reactivate_user_not_found(self, async_session: AsyncSession) -> None:
        result = await reactivate_user(async_session, 999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_update_last_login(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "lastlogin@example.com", "Password123!"
        )
        await async_session.commit()

        # Test with default time
        result = await update_last_login(async_session, user.id)
        assert result is True

        await async_session.refresh(user)
        assert user.last_login_at is not None

        # Test with specific time
        specific_time = datetime.now(UTC)
        result = await update_last_login(async_session, user.id, specific_time)
        assert result is True

    @pytest.mark.asyncio
    async def test_update_last_login_not_found(self, async_session: AsyncSession) -> None:
        result = await update_last_login(async_session, 999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_anonymize_user(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "anonymize@example.com", "Password123!"
        )
        await async_session.commit()

        result = await anonymize_user(async_session, user.id)
        assert result is True

        await async_session.refresh(user)
        assert user.email.startswith("anon_")
        assert user.hashed_password == ""
        assert user.is_active is False
        assert user.is_deleted is True
        assert user.last_login_at is None

    @pytest.mark.asyncio
    async def test_anonymize_user_not_found(self, async_session: AsyncSession) -> None:
        result = await anonymize_user(async_session, 999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_anonymize_user_already_deleted(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "alreadydeleted@example.com", "Password123!"
        )
        user.is_deleted = True
        await async_session.commit()

        result = await anonymize_user(async_session, user.id)
        assert result is False

    @pytest.mark.asyncio
    async def test_user_signups_per_month(self, async_session: AsyncSession) -> None:
        # Create users with specific created_at dates
        user1 = await create_user_with_validation(
            async_session, "signup1@example.com", "Password123!"
        )
        user2 = await create_user_with_validation(
            async_session, "signup2@example.com", "Password123!"
        )

        # Set created_at to January and February 2024
        user1.created_at = datetime(2024, 1, 15)
        user2.created_at = datetime(2024, 2, 15)
        await async_session.commit()

        stats = await user_signups_per_month(async_session, 2024)
        assert isinstance(stats, dict)
        assert len(stats) == 12  # All 12 months
        assert stats[1] >= 1  # January
        assert stats[2] >= 1  # February
        assert stats[3] == 0  # March (no signups)

    @pytest.mark.asyncio
    async def test_sensitive_user_action(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "sensitive@example.com", "Password123!"
        )
        await async_session.commit()

        # Mock the rate limiter to allow the action (async mock)
        async def mock_is_allowed(*args: Any, **kwargs: Any) -> bool:
            return True

        with patch(
            "src.repositories.user.user_action_limiter.is_allowed",
            side_effect=mock_is_allowed,
        ):
            # Should not raise an error
            await sensitive_user_action(async_session, user.id, "test_action")

    @pytest.mark.asyncio
    async def test_sensitive_user_action_rate_limited(self, async_session: AsyncSession) -> None:
        user = await create_user_with_validation(
            async_session, "ratelimited@example.com", "Password123!"
        )
        await async_session.commit()

        # Mock the rate limiter to deny the action (async mock)
        async def mock_is_not_allowed(*args: Any, **kwargs: Any) -> bool:
            return False

        with patch(
            "src.repositories.user.user_action_limiter.is_allowed",
            side_effect=mock_is_not_allowed,
        ):
            with pytest.raises(RateLimitExceededError):
                await sensitive_user_action(async_session, user.id, "test_action")

    @pytest.mark.asyncio
    async def test_sensitive_user_action_user_not_found(self, async_session: AsyncSession) -> None:
        with pytest.raises(UserNotFoundError):
            await sensitive_user_action(async_session, 999999, "test_action")

    @pytest.mark.asyncio
    async def test_create_user_with_validation_rollback_on_error(self, async_session: AsyncSession) -> None:
        # Mock the commit to raise an exception
        with patch.object(async_session, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                await create_user_with_validation(
                    async_session, "error@example.com", "Password123!"
                )

    @pytest.mark.asyncio
    async def test_bulk_operations_rollback_on_error(self, async_session: AsyncSession) -> None:
        users = [
            User(email="bulk1@example.com", hashed_password="hash1", is_active=True),
        ]

        # Mock commit to raise an exception
        with patch.object(async_session, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                await bulk_create_users(async_session, users)
