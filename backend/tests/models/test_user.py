import pytest
from backend.tests.test_templates import AsyncModelTestTemplate, ModelUnitTestTemplate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.user import User


class TestUserUnit(ModelUnitTestTemplate):
    def test_user_creation_and_repr(self):
        user = User(email="unit@example.com", hashed_password="pw", is_active=True)
        self.assert_model_attrs(
            user,
            {"email": "unit@example.com", "hashed_password": "pw", "is_active": True},
        )
        assert "unit@example.com" in repr(user)

    def test_role_property_and_setter(self):
        user = User(
            email="role@example.com",
            hashed_password="pw",
            is_active=True,
            is_admin=False,
        )
        assert user.role == "user"
        user.role = "admin"
        assert user.is_admin is True
        assert user.role == "admin"
        user.role = "user"
        assert user.is_admin is False
        assert user.role == "user"

    def test_long_email(self):
        long_email = "a" * 255 + "@example.com"
        user = User(email=long_email, hashed_password="pw", is_active=True)
        assert user.email.startswith("a")

    def test_non_ascii_and_special_chars(self):
        user = User(email="юзер+!@#@пример.рф", hashed_password="pw", is_active=True)
        assert "юзер" in user.email
        assert "+!@#" in user.email

    def test_repr(self):
        user = User(email="repr@example.com", hashed_password="pw", is_active=True)
        self.assert_repr(user, "User")

    def test_to_dict_if_present(self):
        user = User(email="dict@example.com", hashed_password="pw", is_active=True)
        if hasattr(user, "to_dict"):
            d = user.to_dict()
            assert d["email"] == user.email
            assert "hashed_password" in d

    def test_profile_fields(self):
        user = User(
            email="profile@example.com",
            hashed_password="pw",
            is_active=True,
            name="Test User",
            bio="Bio text",
            avatar_url="http://avatar.url",
            preferences={"theme": "dark", "lang": "en"},
        )
        assert user.name == "Test User"
        assert user.bio == "Bio text"
        assert user.avatar_url == "http://avatar.url"
        assert user.preferences["theme"] == "dark"
        assert user.preferences["lang"] == "en"


class TestUserDB(AsyncModelTestTemplate):
    @pytest.mark.asyncio
    async def test_user_crud(self):
        user = User(email="test@example.com", hashed_password="hashed", is_active=True)
        self.async_session.add(user)
        await self.async_session.commit()
        await self.async_session.refresh(user)
        assert user.id is not None
        # Read
        stmt = select(User).where(User.email == "test@example.com")
        result = await self.async_session.execute(stmt)
        user_db = result.scalar_one()
        assert user_db.email == "test@example.com"
        # Update
        user_db.is_active = False
        await self.async_session.commit()
        await self.async_session.refresh(user_db)
        assert user_db.is_active is False
        # Delete
        await self.async_session.delete(user_db)
        await self.async_session.commit()
        result = await self.async_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        assert result.scalar() is None

    @pytest.mark.asyncio
    async def test_unique_email_constraint(self):
        user1 = User(email="unique@example.com", hashed_password="pw", is_active=True)
        user2 = User(email="unique@example.com", hashed_password="pw2", is_active=False)
        await self.seed_db([user1])
        await self.assert_integrity_error(user2)

    @pytest.mark.asyncio
    async def test_null_email(self):
        user = User(email=None, hashed_password="pw", is_active=True)  # type: ignore
        self.async_session.add(user)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_null_password(self):
        user = User(email="nullpw@example.com", hashed_password=None, is_active=True)  # type: ignore
        self.async_session.add(user)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_bulk_insert_and_truncate(self):
        users = [
            User(email=f"bulk{i}@ex.com", hashed_password="pw", is_active=True)
            for i in range(5)
        ]
        await self.seed_db(users)
        for u in users:
            assert u.id is not None
        await self.truncate_table("users")
        result = await self.async_session.execute("SELECT COUNT(*) FROM users")
        count = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_transactional_rollback(self):
        user = User(email="rollback@example.com", hashed_password="pw", is_active=True)

        async def op():
            self.async_session.add(user)

        await self.run_in_transaction(op)
        result = await self.async_session.execute(
            "SELECT COUNT(*) FROM users WHERE email = 'rollback@example.com'"
        )
        count = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_non_ascii_and_special_chars_db(self):
        user = User(email="юзер+!@#@пример.рф", hashed_password="pw", is_active=True)
        await self.seed_db([user])
        db_user = await self.async_session.get(User, user.id)
        assert "юзер" in db_user.email
        assert "+!@#" in db_user.email

    @pytest.mark.asyncio
    async def test_user_files_relationship(self):
        from src.models.file import File

        user = User(email="filesrel@example.com", hashed_password="pw", is_active=True)
        await self.seed_db([user])
        files = [
            File(filename=f"file{i}.txt", content_type="text/plain", user_id=user.id)
            for i in range(3)
        ]
        await self.seed_db(files)
        db_user = await self.async_session.get(User, user.id)
        # Relationship is lazy by default; refresh if needed
        await self.async_session.refresh(db_user)
        # Query files for user
        result = await self.async_session.execute(
            select(File).where(File.user_id == user.id)
        )
        user_files = result.scalars().all()
        assert len(user_files) == 3
        for f in user_files:
            assert f.user_id == user.id

    @pytest.mark.asyncio
    async def test_profile_fields_and_preferences_db(self):
        prefs = {"theme": "light", "lang": "fr"}
        user = User(
            email="profiledb@example.com",
            hashed_password="pw",
            is_active=True,
            name="DB User",
            bio="DB Bio",
            avatar_url="http://db.avatar",
            preferences=prefs,
        )
        await self.seed_db([user])
        db_user = await self.async_session.get(User, user.id)
        assert db_user.name == "DB User"
        assert db_user.bio == "DB Bio"
        assert db_user.avatar_url == "http://db.avatar"
        assert db_user.preferences["theme"] == "light"
        assert db_user.preferences["lang"] == "fr"
