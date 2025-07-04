"""Advanced database tests using DatabaseTestTemplate and real models."""

from __future__ import annotations

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import config-dependent modules inside test class to ensure env vars are set by fixtures first
from tests.test_templates import DatabaseTestTemplate

USER_EMAIL = "test@example.com"
USER_DATA = {"email": USER_EMAIL, "hashed_password": "pw"}


class TestDatabase(DatabaseTestTemplate):
    @pytest.mark.asyncio
    async def test_true_concurrent_inserts(self):
        """Test true concurrent inserts using run_concurrent_operations helper."""
        import uuid

        User = self.User

        async def insert_user(session):
            email = f"concurrent_{uuid.uuid4().hex[:8]}@ex.com"
            user = User(email=email, hashed_password="pw")
            session.add(user)
            await session.commit()
            return email

        # Run 5 concurrent inserts, each with its own session
        results = await self.run_concurrent_operations([insert_user] * 5)
        # Check that all emails are unique and present
        assert len(set(results)) == 5

    @pytest.mark.asyncio
    async def test_db_healthcheck(self) -> None:
        """Test that db_healthcheck succeeds on a valid connection."""
        await self.assert_healthcheck_ok(self.db_healthcheck)

    @pytest.mark.asyncio
    async def test_db_session_context(self) -> None:
        """Test that session context manager works properly."""

        await self.assert_session_context_ok(self.get_async_session, AsyncSession)

    @pytest.mark.asyncio
    async def test_session_rollback(self) -> None:
        """Test session rollback on error."""
        await self.assert_session_rollback(self.AsyncSessionLocal)

    @pytest.mark.asyncio
    async def test_users_table_exists(self) -> None:
        """Test that the users table exists."""
        await self.assert_table_exists(self.AsyncSessionLocal, "users")

    @pytest.mark.asyncio
    async def test_can_insert_and_query_user(self) -> None:
        """Test inserting and querying a user."""
        await self.assert_can_insert_and_query(
            self.AsyncSessionLocal, self.User, USER_DATA, {"email": USER_EMAIL}
        )

    @pytest.mark.asyncio
    async def test_transaction_isolation(self) -> None:
        """Test transaction isolation for concurrent sessions."""
        await self.assert_transaction_isolation(
            self.AsyncSessionLocal, self.User, USER_DATA
        )

    @pytest.mark.asyncio
    async def test_integrity_error_on_duplicate_email(self) -> None:
        """Test that inserting a user with a duplicate email raises an integrity error."""
        await self.bulk_insert(self.AsyncSessionLocal, self.User, [USER_DATA])
        await self.assert_db_integrity_error(
            self.AsyncSessionLocal, self.User, USER_DATA
        )

    @pytest.mark.asyncio
    async def test_bulk_insert_and_query(self) -> None:
        """Test bulk inserting and querying users."""
        emails = [f"user{i}@ex.com" for i in range(5)]
        rows = [dict(email=e, hashed_password="pw") for e in emails]
        await self.bulk_insert(self.AsyncSessionLocal, self.User, rows)
        await self.assert_bulk_query(
            self.AsyncSessionLocal, self.User, {"is_active": True}, expected_count=5
        )

    @pytest.mark.asyncio
    async def test_seed_and_truncate(self) -> None:
        """Test seeding and truncating the users table."""
        await self.seed_database(self.AsyncSessionLocal, self.User, [USER_DATA])
        await self.truncate_tables(self.AsyncSessionLocal, ["users"])
        await self.assert_bulk_query(
            self.AsyncSessionLocal, self.User, {"is_active": True}, expected_count=0
        )

    def test_migration_applied(self) -> None:
        """Test that the migration has been applied."""
        self.assert_migration_applied(self.AsyncSessionLocal, table_name="users")

    @pytest.mark.skip_if_fast_tests(
        "Migration test not applicable in fast (SQLite in-memory) mode"
    )
    def test_run_migration(self) -> None:
        """Test running the migration."""
        self.run_migration("upgrade head")

    def test_simulate_db_disconnect(self) -> None:
        """Test simulating a database disconnect."""
        import asyncio

        import pytest

        if os.environ.get("FAST_TESTS") == "1":
            pytest.skip(
                "Simulate DB disconnect is not supported in fast (SQLite in-memory) mode."
            )
        self.simulate_db_disconnect(self.AsyncSessionLocal)
        with pytest.raises(Exception):
            asyncio.run(self.db_healthcheck())

    def test_simulate_db_latency(self) -> None:
        """Test simulating database latency."""
        self.simulate_db_latency(self.AsyncSessionLocal, delay=0.1)
        # No assertion: just ensures patching works and doesn't error

    def test_connection_pool_size(self) -> None:
        """Test the connection pool size."""
        self.assert_connection_pool_size(self.engine, expected_size=5)

    @pytest.mark.asyncio
    async def test_file_fk_constraint(self):
        import pytest

        if os.environ.get("FAST_TESTS") == "1":
            pytest.skip(
                "SQLite in-memory does not reliably enforce foreign key constraints for this test."
            )
        # Should fail: user_id does not exist
        from sqlalchemy.exc import IntegrityError

        bad_file = dict(filename="bad.txt", content_type="text/plain", user_id=999999)
        async with self.AsyncSessionLocal() as session:
            file = self.File(**bad_file)
            session.add(file)
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

    @pytest.mark.asyncio
    async def test_cascade_delete_user_files(self):
        import pytest

        # Check if using SQLite backend
        if hasattr(self, "engine") and "sqlite" in str(self.engine.url):
            pytest.skip(
                "SQLite in-memory does not reliably support ON DELETE CASCADE for this test."
            )
        if os.environ.get("FAST_TESTS") == "1":
            pytest.skip(
                "SQLite in-memory does not reliably support ON DELETE CASCADE for this test."
            )
        # Insert user and file, delete user, file should be deleted if cascade is enabled
        user = self.User(email="cascade@example.com", hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            file = self.File(
                filename="f.txt", content_type="text/plain", user_id=user.id
            )
            session.add(file)
            await session.commit()
            await session.delete(user)
            await session.commit()
            result = await session.execute(
                self.File.__table__.select().filter_by(user_id=user.id)
            )
            files = result.scalars().all()
            # If cascade is not enabled, files may remain; adjust assertion as needed
            assert (
                not files or files == []
            ), "Files should be deleted with user if cascade is enabled"

    @pytest.mark.asyncio
    async def test_unique_constraint_on_email(self):
        await self.bulk_insert(self.AsyncSessionLocal, self.User, [USER_DATA])
        await self.assert_db_integrity_error(
            self.AsyncSessionLocal, self.User, USER_DATA
        )

    def test_indexes_exist(self):
        # Check if using SQLite backend or FAST_TESTS mode - both require async engine handling
        if os.environ.get("FAST_TESTS") == "1" or (
            hasattr(self, "engine") and "sqlite" in str(self.engine.url)
        ):
            import asyncio

            from sqlalchemy import inspect

            async def check_indexes():
                async with self.engine.begin() as conn:

                    def get_indexes(sync_conn):
                        insp = inspect(sync_conn)
                        if insp is None:
                            raise RuntimeError(
                                f"Inspector is None for sync_conn: {sync_conn}, type: {type(sync_conn)}"
                            )
                        user_indexes = [ix["name"] for ix in insp.get_indexes("users")]
                        file_indexes = [ix["name"] for ix in insp.get_indexes("files")]
                        return user_indexes, file_indexes

                    user_indexes, file_indexes = await conn.run_sync(get_indexes)
                    assert any("ix_users_email" in ix for ix in user_indexes)
                    assert any("ix_files_user_id" in ix for ix in file_indexes)

            asyncio.run(check_indexes())
        else:
            from sqlalchemy import inspect

            insp = inspect(self.engine)
            user_indexes = [ix["name"] for ix in insp.get_indexes("users")]
            file_indexes = [ix["name"] for ix in insp.get_indexes("files")]
            assert any("ix_users_email" in ix for ix in user_indexes)
            assert any("ix_files_user_id" in ix for ix in file_indexes)

    @pytest.mark.asyncio
    async def test_user_defaults(self):
        from sqlalchemy import select

        user = self.User(email="defaults@example.com", hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                select(self.User).filter_by(email="defaults@example.com")
            )
            row = result.scalar_one()
            assert row.is_active is True
            assert row.is_deleted is False
            assert row.is_admin is False

    @pytest.mark.asyncio
    async def test_update_and_query(self):
        from sqlalchemy import select

        user = self.User(email="update@example.com", hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            user.is_active = False
            await session.commit()
            result = await session.execute(
                select(self.User).filter_by(email="update@example.com")
            )
            row = result.scalar_one()
            assert row.is_active is False

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        from sqlalchemy import select

        user = self.User(email="rollback@example.com", hashed_password="pw")
        try:
            async with self.AsyncSessionLocal() as session:
                session.add(user)
                raise Exception("fail before commit")
        except Exception:
            pass
        # User should not be committed
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                select(self.User).filter_by(email="rollback@example.com")
            )
            row = result.scalar_one_or_none()
            assert row is None

    @pytest.mark.asyncio
    async def test_user_repr(self):
        from sqlalchemy import select

        user = self.User(email="repr@example.com", hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                select(self.User).filter_by(email="repr@example.com")
            )
            row = result.scalar_one()
            assert f"<User id={row.id} email=repr@example.com>" == repr(row)

    @pytest.mark.asyncio
    async def test_user_preferences_json(self):
        from sqlalchemy import select

        prefs = {"theme": "dark", "lang": "en"}
        user = self.User(
            email="prefs@example.com", hashed_password="pw", preferences=prefs
        )
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                select(self.User).filter_by(email="prefs@example.com")
            )
            row = result.scalar_one()
            assert row.preferences == prefs

    @pytest.mark.asyncio
    async def test_user_last_login_datetime(self):
        import datetime

        from sqlalchemy import select

        now = datetime.datetime.utcnow()
        user = self.User(
            email="dt@example.com", hashed_password="pw", last_login_at=now
        )
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result = await session.execute(
                select(self.User).filter_by(email="dt@example.com")
            )
            row = result.scalar_one()
            assert row.last_login_at.replace(microsecond=0) == now.replace(
                microsecond=0
            )
