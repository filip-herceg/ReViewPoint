from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text

from src.models.file import File
from src.repositories.user import (
    create_user_with_validation,
    filter_users_by_status,
    get_user_by_id,
    get_user_with_files,
    get_users_by_ids,
    list_users,
    list_users_paginated,
    search_users_by_name_or_email,
)
from src.utils.errors import UserAlreadyExistsError, ValidationError


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
        self, async_session, email, password, expected_exc
    ):
        if expected_exc:
            with pytest.raises(expected_exc):
                await create_user_with_validation(async_session, email, password)
        else:
            user = await create_user_with_validation(async_session, email, password)
            assert user.email == email
            assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, async_session):
        await create_user_with_validation(
            async_session, "dup@example.com", "Password123!"
        )
        with pytest.raises(UserAlreadyExistsError):
            await create_user_with_validation(
                async_session, "dup@example.com", "Password123!"
            )
        await async_session.rollback()

    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self, async_session):
        with pytest.raises(TypeError):
            await create_user_with_validation(async_session, None, "Password123!")
        with pytest.raises(TypeError):
            await create_user_with_validation(
                async_session, "missing@example.com", None
            )

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_session):
        user = await create_user_with_validation(
            async_session, "getid@example.com", "Password123!"
        )
        found = await get_user_by_id(async_session, user.id)
        assert found.email == user.email
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, async_session):
        found = await get_user_by_id(async_session, 999999)
        assert found is None

    @pytest.mark.asyncio
    async def test_get_users_by_ids(self, async_session):
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
    async def test_list_users_paginated(self, async_session):
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
    async def test_list_users_filters_and_sort(self, async_session):
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
    async def test_search_users_by_name_or_email(self, async_session):
        await create_user_with_validation(
            async_session, "searchme@example.com", "Password123!"
        )
        found = await search_users_by_name_or_email(async_session, "searchme")
        assert any("searchme" in u.email for u in found)

    @pytest.mark.asyncio
    async def test_filter_users_by_status(self, async_session):
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
    async def test_update_user(self, async_session):
        user = await create_user_with_validation(
            async_session, "update@example.com", "Password123!"
        )
        user.email = "updated@example.com"
        await async_session.commit()
        found = await get_user_by_id(async_session, user.id)
        assert found.email == "updated@example.com"

    @pytest.mark.asyncio
    async def test_update_user_invalid(self, async_session):
        user = await create_user_with_validation(
            async_session, "updateinv@example.com", "Password123!"
        )
        user.email = None  # type: ignore
        with pytest.raises(Exception):
            await async_session.commit()
        await async_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_user(self, async_session):
        user = await create_user_with_validation(
            async_session, "delme@example.com", "Password123!"
        )
        await async_session.delete(user)
        await async_session.commit()
        found = await get_user_by_id(async_session, user.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_user_profile_fields_and_preferences(self, async_session):
        user = await create_user_with_validation(
            async_session, "profile@example.com", "Password123!"
        )
        user.profile_fields = {"bio": "Hello", "location": "World"}
        user.preferences = {"theme": "dark"}
        await async_session.commit()
        found = await get_user_by_id(async_session, user.id)
        assert found.profile_fields["bio"] == "Hello"
        assert found.preferences["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_user_file_relationship(self, async_session):
        user = await create_user_with_validation(
            async_session, "fileuser@example.com", "Password123!"
        )
        file = File(filename="relfile.txt", content_type="text/plain", user_id=user.id)
        async_session.add(file)
        await async_session.commit()
        found = await get_user_with_files(async_session, user.id)
        assert any(f.filename == "relfile.txt" for f in found.files)

    @pytest.mark.asyncio
    async def test_bulk_create_and_delete_users(self, async_session):
        users = []
        for i in range(5):
            user = await create_user_with_validation(
                async_session, f"bulkuser{i}@ex.com", "Password123!"
            )
            users.append(user)
        await async_session.commit()
        for u in users:
            await async_session.delete(u)
        await async_session.commit()
        found = await list_users(async_session)
        emails = {u.email for u in found[0]}
        for i in range(5):
            assert f"bulkuser{i}@ex.com" not in emails

    @pytest.mark.asyncio
    async def test_edge_cases(self, async_session):
        # Long, non-ASCII, special char email should raise ValidationError
        with pytest.raises(ValidationError):
            await create_user_with_validation(
                async_session, "юзер+!@#@пример.рф", "Password123!"
            )
        # Pagination offset beyond total
        users = []
        for i in range(2):
            u = await create_user_with_validation(
                async_session, f"edge{i}@ex.com", "Password123!"
            )
            users.append(u)
        await async_session.commit()
        found = await list_users_paginated(async_session, offset=100, limit=10)
        assert found == []
        # Zero/negative limit
        found = await list_users_paginated(async_session, offset=0, limit=0)
        assert found == []
        found = await list_users_paginated(async_session, offset=0, limit=-1)
        assert found == []
        # is_admin, is_deleted
        users[0].is_admin = True
        users[0].is_deleted = True
        await async_session.commit()
        found = await get_user_by_id(async_session, users[0].id)
        assert found.is_admin is True
        assert found.is_deleted is True
