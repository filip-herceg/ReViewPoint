from datetime import UTC, datetime, timedelta

import pytest
from tests.test_templates import AsyncModelTestTemplate
from sqlalchemy.exc import IntegrityError

from src.models.file import File
from src.models.user import User
from src.repositories.user import (
    create_user_with_validation,
    filter_users_by_status,
    get_user_by_id,
    get_users_by_ids,
    list_users,
    list_users_paginated,
    search_users_by_name_or_email,
)
from src.utils.errors import UserAlreadyExistsError, ValidationError


class TestUserRepository(AsyncModelTestTemplate):
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,password,expected_exc",
        [
            ("bademail", "Password123!", ValidationError),
            ("repo@example.com", "short", ValidationError),
            ("repo@example.com", "Password123!", None),
        ],
    )
    async def test_create_user_validation(self, email, password, expected_exc):
        if expected_exc:
            with pytest.raises(expected_exc):
                await create_user_with_validation(self.async_session, email, password)
        else:
            user = await create_user_with_validation(
                self.async_session, email, password
            )
            assert user.email == email
            assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self):
        await create_user_with_validation(
            self.async_session, "dup@example.com", "Password123!"
        )
        with pytest.raises(UserAlreadyExistsError):
            await create_user_with_validation(
                self.async_session, "dup@example.com", "Password123!"
            )
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self):
        with pytest.raises(TypeError):
            await create_user_with_validation(self.async_session, None, "Password123!")
        with pytest.raises(TypeError):
            await create_user_with_validation(
                self.async_session, "missing@example.com", None
            )

    @pytest.mark.asyncio
    async def test_get_user_by_id(self):
        user = await create_user_with_validation(
            self.async_session, "getid@example.com", "Password123!"
        )
        found = await get_user_by_id(self.async_session, user.id)
        assert found.email == user.email
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        found = await get_user_by_id(self.async_session, 999999)
        assert found is None

    @pytest.mark.asyncio
    async def test_get_users_by_ids(self):
        users = [
            await create_user_with_validation(
                self.async_session, f"multi{i}@ex.com", "Password123!"
            )
            for i in range(3)
        ]
        ids = [u.id for u in users]
        found = await get_users_by_ids(self.async_session, ids)
        assert len(found) == 3
        emails = {u.email for u in found}
        for i in range(3):
            assert f"multi{i}@ex.com" in emails

    @pytest.mark.asyncio
    async def test_list_users_paginated(self):
        users = [
            await create_user_with_validation(
                self.async_session, f"page{i}@ex.com", "Password123!"
            )
            for i in range(10)
        ]
        found = await list_users_paginated(self.async_session, offset=2, limit=5)
        assert len(found) == 5
        assert found[0].email == "page2@ex.com"

    @pytest.mark.asyncio
    async def test_list_users_filters_and_sort(self):
        now = datetime.now(UTC)
        users = [
            await create_user_with_validation(
                self.async_session, f"filter{i}@ex.com", "Password123!"
            )
            for i in range(5)
        ]
        for i, u in enumerate(users):
            u.created_at = now - timedelta(days=i)
        await self.async_session.commit()
        listed, total = await list_users(
            self.async_session, q="filter", sort="created_at", order="asc"
        )
        assert total >= 5
        assert listed[0].created_at <= listed[-1].created_at

    @pytest.mark.asyncio
    async def test_search_users_by_name_or_email(self):
        users = [
            await create_user_with_validation(
                self.async_session, f"search{i}@ex.com", "Password123!"
            )
            for i in range(3)
        ]
        found = await search_users_by_name_or_email(self.async_session, "search")
        assert len(found) >= 3
        found_none = await search_users_by_name_or_email(self.async_session, "notfound")
        assert found_none == []

    @pytest.mark.asyncio
    async def test_filter_users_by_status(self):
        u1 = await create_user_with_validation(
            self.async_session, "active@ex.com", "Password123!"
        )
        u2 = await create_user_with_validation(
            self.async_session, "inactive@ex.com", "Password123!"
        )
        u2.is_active = False
        await self.async_session.commit()
        found = await filter_users_by_status(self.async_session, True)
        assert any(u.email == "active@ex.com" for u in found)
        found = await filter_users_by_status(self.async_session, False)
        assert any(u.email == "inactive@ex.com" for u in found)

    @pytest.mark.asyncio
    async def test_update_user(self):
        user = await create_user_with_validation(
            self.async_session, "update@ex.com", "Password123!"
        )
        user.is_active = False
        user.name = "Updated Name"
        await self.async_session.commit()
        found = await get_user_by_id(self.async_session, user.id)
        assert found.is_active is False
        assert found.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_user_invalid(self):
        user = await create_user_with_validation(
            self.async_session, "updateinv@ex.com", "Password123!"
        )
        user.email = None
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_user(self):
        user = await create_user_with_validation(
            self.async_session, "delete@ex.com", "Password123!"
        )
        await self.async_session.delete(user)
        await self.async_session.commit()
        found = await get_user_by_id(self.async_session, user.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self):
        user = User(email="ghost@ex.com", hashed_password="pw", is_active=True)
        # Not added to session
        with pytest.raises(Exception):
            await self.async_session.delete(user)
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_user_profile_fields_and_preferences(self):
        user = await create_user_with_validation(
            self.async_session, "profile@ex.com", "Password123!"
        )
        user.name = "Profile Name"
        user.bio = "Profile Bio"
        user.avatar_url = "http://avatar.url"
        user.preferences = {"theme": "dark", "lang": "en"}
        await self.async_session.commit()
        found = await get_user_by_id(self.async_session, user.id)
        assert found.name == "Profile Name"
        assert found.bio == "Profile Bio"
        assert found.avatar_url == "http://avatar.url"
        assert found.preferences["theme"] == "dark"
        assert found.preferences["lang"] == "en"

    @pytest.mark.asyncio
    async def test_user_file_relationship(self):
        user = await create_user_with_validation(
            self.async_session, "fileuser@ex.com", "Password123!"
        )
        file = File(filename="userfile.txt", content_type="text/plain", user_id=user.id)
        self.async_session.add(file)
        await self.async_session.commit()
        found = await get_user_by_id(self.async_session, user.id)
        result = await self.async_session.execute(
            f"SELECT * FROM files WHERE user_id = {user.id} AND filename = 'userfile.txt'"
        )
        row = result.first()
        assert row is not None

    @pytest.mark.asyncio
    async def test_bulk_create_and_delete_users(self):
        users = [
            await create_user_with_validation(
                self.async_session, f"bulkdel{i}@ex.com", "Password123!"
            )
            for i in range(5)
        ]
        for u in users:
            await self.async_session.delete(u)
        await self.async_session.commit()
        found = await get_users_by_ids(self.async_session, [u.id for u in users])
        assert found == []

    @pytest.mark.asyncio
    async def test_transactional_rollback_create_user(self):
        async def op():
            await create_user_with_validation(
                self.async_session, "rollback@ex.com", "Password123!"
            )

        await self.run_in_transaction(op)
        found = await search_users_by_name_or_email(
            self.async_session, "rollback@ex.com"
        )
        assert found == []

    @pytest.mark.asyncio
    async def test_edge_cases(self):
        # Long, non-ASCII, special char email
        user = await create_user_with_validation(
            self.async_session, "юзер+!@#@пример.рф", "Password123!"
        )
        assert "юзер" in user.email
        # Pagination offset beyond total
        users = [
            await create_user_with_validation(
                self.async_session, f"edge{i}@ex.com", "Password123!"
            )
            for i in range(2)
        ]
        found = await list_users_paginated(self.async_session, offset=100, limit=10)
        assert found == []
        # Zero/negative limit
        found = await list_users_paginated(self.async_session, offset=0, limit=0)
        assert found == []
        found = await list_users_paginated(self.async_session, offset=0, limit=-1)
        assert found == []
        # is_admin, is_deleted
        user.is_admin = True
        user.is_deleted = True
        await self.async_session.commit()
        found = await get_user_by_id(self.async_session, user.id)
        assert found.is_admin is True
        assert found.is_deleted is True
