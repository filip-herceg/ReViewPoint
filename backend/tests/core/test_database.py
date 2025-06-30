"""Advanced database tests using DatabaseTestTemplate and real models."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import (
    AsyncSessionLocal,
    db_healthcheck,
    engine,
    get_async_session,
)
from src.models import File, User
from tests.test_templates import DatabaseTestTemplate

USER_EMAIL = "test@example.com"
USER_DATA = {"email": USER_EMAIL, "hashed_password": "pw"}


class TestDatabase(DatabaseTestTemplate):
    @pytest.mark.asyncio
    async def test_db_healthcheck(self) -> None:
        """Test that db_healthcheck succeeds on a valid connection."""
        await self.assert_healthcheck_ok(db_healthcheck)

    @pytest.mark.asyncio
    async def test_db_session_context(self) -> None:
        """Test that session context manager works properly."""
        await self.assert_session_context_ok(get_async_session, AsyncSession)

    @pytest.mark.asyncio
    async def test_session_rollback(self) -> None:
        """Test session rollback on error."""
        await self.assert_session_rollback(AsyncSessionLocal)

    @pytest.mark.asyncio
    async def test_users_table_exists(self) -> None:
        """Test that the users table exists."""
        await self.assert_table_exists(AsyncSessionLocal, "users")

    @pytest.mark.asyncio
    async def test_can_insert_and_query_user(self) -> None:
        """Test inserting and querying a user."""
        await self.assert_can_insert_and_query(
            AsyncSessionLocal, User, USER_DATA, {"email": USER_EMAIL}
        )

    @pytest.mark.asyncio
    async def test_transaction_isolation(self) -> None:
        """Test transaction isolation for concurrent sessions."""
        await self.assert_transaction_isolation(AsyncSessionLocal, User, USER_DATA)

    @pytest.mark.asyncio
    async def test_integrity_error_on_duplicate_email(self) -> None:
        """Test that inserting a user with a duplicate email raises an integrity error."""
        await self.bulk_insert(AsyncSessionLocal, User, [USER_DATA])
        await self.assert_db_integrity_error(AsyncSessionLocal, User, USER_DATA)

    @pytest.mark.asyncio
    async def test_bulk_insert_and_query(self) -> None:
        """Test bulk inserting and querying users."""
        emails = [f"user{i}@ex.com" for i in range(5)]
        rows = [dict(email=e, hashed_password="pw") for e in emails]
        await self.bulk_insert(AsyncSessionLocal, User, rows)
        await self.assert_bulk_query(
            AsyncSessionLocal, User, {"is_active": True}, expected_count=5
        )

    @pytest.mark.asyncio
    async def test_seed_and_truncate(self) -> None:
        """Test seeding and truncating the users table."""
        await self.seed_database(AsyncSessionLocal, User, [USER_DATA])
        await self.truncate_tables(AsyncSessionLocal, ["users"])
        await self.assert_bulk_query(
            AsyncSessionLocal, User, {"is_active": True}, expected_count=0
        )

    def test_migration_applied(self) -> None:
        """Test that the migration has been applied."""
        self.assert_migration_applied(AsyncSessionLocal, table_name="users")

    def test_run_migration(self) -> None:
        """Test running the migration."""
        self.run_migration("upgrade head")

    def test_simulate_db_disconnect(self) -> None:
        """Test simulating a database disconnect."""
        self.simulate_db_disconnect(AsyncSessionLocal)
        with pytest.raises(Exception):
            import asyncio

            asyncio.run(self.assert_healthcheck_ok(db_healthcheck))

    def test_simulate_db_latency(self) -> None:
        """Test simulating database latency."""
        self.simulate_db_latency(AsyncSessionLocal, delay=0.1)
        # No assertion: just ensures patching works and doesn't error

    def test_connection_pool_size(self) -> None:
        """Test the connection pool size."""
        self.assert_connection_pool_size(engine, expected_size=5)

    @pytest.mark.asyncio
    async def test_file_fk_constraint(self):
        # Should fail: user_id does not exist
        from sqlalchemy.exc import IntegrityError

        bad_file = dict(filename="bad.txt", content_type="text/plain", user_id=999999)
        from src.models import File

        async with AsyncSessionLocal() as session:
            file = File(**bad_file)
            session.add(file)
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

    @pytest.mark.asyncio
    async def test_cascade_delete_user_files(self):
        # Insert user and file, delete user, file should be deleted if cascade is enabled
        user = User(email="cascade@example.com", hashed_password="pw")
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            file = File(filename="f.txt", content_type="text/plain", user_id=user.id)
            session.add(file)
            await session.commit()
            await session.delete(user)
            await session.commit()
            result = await session.execute(
                File.__table__.select().filter_by(user_id=user.id)
            )
            files = result.scalars().all()
            # If cascade is not enabled, files may remain; adjust assertion as needed
            assert (
                not files or files == []
            ), "Files should be deleted with user if cascade is enabled"

    @pytest.mark.asyncio
    async def test_unique_constraint_on_email(self):
        await self.bulk_insert(AsyncSessionLocal, User, [USER_DATA])
        await self.assert_db_integrity_error(AsyncSessionLocal, User, USER_DATA)

    def test_indexes_exist(self):
        from sqlalchemy import inspect

        insp = inspect(engine)
        user_indexes = [ix["name"] for ix in insp.get_indexes("users")]
        file_indexes = [ix["name"] for ix in insp.get_indexes("files")]
        assert any("ix_users_email" in ix for ix in user_indexes)
        assert any("ix_files_user_id" in ix for ix in file_indexes)

    @pytest.mark.asyncio
    async def test_user_defaults(self):
        user = User(email="defaults@example.com", hashed_password="pw")
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                User.__table__.select().filter_by(email="defaults@example.com")
            )
            row = result.scalar_one()
            assert row.is_active is True
            assert row.is_deleted is False
            assert row.is_admin is False

    @pytest.mark.asyncio
    async def test_update_and_query(self):
        user = User(email="update@example.com", hashed_password="pw")
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            user.is_active = False
            await session.commit()
            result = await session.execute(
                User.__table__.select().filter_by(email="update@example.com")
            )
            row = result.scalar_one()
            assert row.is_active is False

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        user = User(email="rollback@example.com", hashed_password="pw")
        try:
            async with AsyncSessionLocal() as session:
                session.add(user)
                raise Exception("fail before commit")
        except Exception:
            pass
        # User should not be committed
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                User.__table__.select().filter_by(email="rollback@example.com")
            )
            row = result.scalar_one_or_none()
            assert row is None

    @pytest.mark.asyncio
    async def test_user_repr(self):
        user = User(email="repr@example.com", hashed_password="pw")
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                User.__table__.select().filter_by(email="repr@example.com")
            )
            row = result.scalar_one()
            assert f"<User id={row.id} email=repr@example.com>" == repr(row)

    @pytest.mark.asyncio
    async def test_user_preferences_json(self):
        prefs = {"theme": "dark", "lang": "en"}
        user = User(email="prefs@example.com", hashed_password="pw", preferences=prefs)
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                User.__table__.select().filter_by(email="prefs@example.com")
            )
            row = result.scalar_one()
            assert row.preferences == prefs

    @pytest.mark.asyncio
    async def test_user_last_login_datetime(self):
        import datetime

        now = datetime.datetime.utcnow()
        user = User(email="dt@example.com", hashed_password="pw", last_login_at=now)
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                User.__table__.select().filter_by(email="dt@example.com")
            )
            row = result.scalar_one()
            assert row.last_login_at.replace(microsecond=0) == now.replace(
                microsecond=0
            )
