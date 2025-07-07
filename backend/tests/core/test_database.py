"""Advanced database tests using DatabaseTestTemplate and real models."""

from __future__ import annotations

import asyncio
import datetime
import os
import uuid
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Final, Literal, cast

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

# Import config-dependent modules inside test class to ensure env vars are set by fixtures first
from tests.test_data_generators import get_unique_email, get_test_user
from tests.test_templates import DatabaseTestTemplate

USER_EMAIL: Final[str] = get_unique_email()
USER_DATA: Final[dict[str, str]] = {"email": USER_EMAIL, "hashed_password": "pw"}


class TestDatabase(DatabaseTestTemplate):
    # These attributes are set by the _setup_db_env_function fixture in conftest.py
    User: type[Any]  # SQLAlchemy model class
    File: type[Any]  # SQLAlchemy model class
    AsyncSessionLocal: Callable[[], AsyncSession]
    get_async_session: Callable[[], AsyncSession]
    db_healthcheck: Callable[[], Awaitable[None]]
    engine: Any  # SQLAlchemy async engine

    # Typed wrapper methods for base class methods
    async def _run_concurrent_operations_typed(
        self, operations: list[Callable[[AsyncSession], Awaitable[Any]]]
    ) -> list[Any]:
        """Typed wrapper for run_concurrent_operations."""
        return cast(list[Any], await cast(Any, super().run_concurrent_operations)(operations))

    async def _assert_healthcheck_ok_typed(
        self, healthcheck_func: Callable[[], Awaitable[None]]
    ) -> None:
        """Typed wrapper for assert_healthcheck_ok."""
        await cast(Any, super().assert_healthcheck_ok)(healthcheck_func)

    async def _assert_session_context_ok_typed(
        self, get_session_func: Callable[[], AsyncSession], session_type: type[AsyncSession]
    ) -> None:
        """Typed wrapper for assert_session_context_ok."""
        await cast(Any, super().assert_session_context_ok)(get_session_func, session_type)

    async def _assert_session_rollback_typed(
        self, session_factory: Callable[[], AsyncSession]
    ) -> None:
        """Typed wrapper for assert_session_rollback."""
        await cast(Any, super().assert_session_rollback)(session_factory)

    async def _assert_table_exists_typed(
        self, session_factory: Callable[[], AsyncSession], table_name: str
    ) -> None:
        """Typed wrapper for assert_table_exists."""
        await cast(Any, super().assert_table_exists)(session_factory, table_name)

    async def _assert_can_insert_and_query_typed(
        self,
        session_factory: Callable[[], AsyncSession],
        table: type[Any],
        insert_dict: dict[str, str],
        query_filter: dict[str, str],
    ) -> None:
        """Typed wrapper for assert_can_insert_and_query."""
        await cast(Any, super().assert_can_insert_and_query)(
            session_factory, table, insert_dict, query_filter
        )

    async def _assert_transaction_isolation_typed(
        self, session_factory: Callable[[], AsyncSession], table: type[Any], insert_dict: dict[str, str]
    ) -> None:
        """Typed wrapper for assert_transaction_isolation."""
        await cast(Any, super().assert_transaction_isolation)(session_factory, table, insert_dict)

    async def _bulk_insert_typed(
        self, session_factory: Callable[[], AsyncSession], table: type[Any], rows: list[dict[str, str]]
    ) -> None:
        """Typed wrapper for bulk_insert."""
        await cast(Any, super().bulk_insert)(session_factory, table, rows)

    async def _assert_db_integrity_error_typed(
        self, session_factory: Callable[[], AsyncSession], table: type[Any], insert_dict: dict[str, str]
    ) -> None:
        """Typed wrapper for assert_db_integrity_error."""
        await cast(Any, super().assert_db_integrity_error)(session_factory, table, insert_dict)

    async def _assert_bulk_query_typed(
        self,
        session_factory: Callable[[], AsyncSession],
        table: type[Any],
        filter_dict: dict[str, bool],
        expected_count: int,
    ) -> None:
        """Typed wrapper for assert_bulk_query."""
        await cast(Any, super().assert_bulk_query)(session_factory, table, filter_dict, expected_count)

    async def _seed_database_typed(
        self, session_factory: Callable[[], AsyncSession], table: type[Any], rows: list[dict[str, str]]
    ) -> None:
        """Typed wrapper for seed_database."""
        await cast(Any, super().seed_database)(session_factory, table, rows)

    async def _truncate_tables_typed(
        self, session_factory: Callable[[], AsyncSession], tables: list[str]
    ) -> None:
        """Typed wrapper for truncate_tables."""
        await cast(Any, super().truncate_tables)(session_factory, tables)

    def _assert_migration_applied_typed(
        self, session_factory: Callable[[], AsyncSession], table_name: str
    ) -> None:
        """Typed wrapper for assert_migration_applied."""
        cast(Any, super().assert_migration_applied)(session_factory, table_name)

    def _run_migration_typed(self, command: str) -> None:
        """Typed wrapper for run_migration."""
        cast(Any, super().run_migration)(command)

    def _simulate_db_disconnect_typed(self, session_factory: Callable[[], AsyncSession]) -> None:
        """Typed wrapper for simulate_db_disconnect."""
        cast(Any, super().simulate_db_disconnect)(session_factory)

    def _simulate_db_latency_typed(
        self, session_factory: Callable[[], AsyncSession], delay: float
    ) -> None:
        """Typed wrapper for simulate_db_latency."""
        cast(Any, super().simulate_db_latency)(session_factory, delay)

    def _assert_connection_pool_size_typed(self, engine: Any, expected_size: int) -> None:
        """Typed wrapper for assert_connection_pool_size."""
        cast(Any, super().assert_connection_pool_size)(engine, expected_size)

    @pytest.mark.asyncio
    async def test_true_concurrent_inserts(self) -> None:
        """Test true concurrent inserts using run_concurrent_operations helper.
        
        Raises:
            AssertionError: If the concurrent inserts fail or results are not unique.
        """
        User: type[Any] = self.User

        async def insert_user(session: AsyncSession) -> str:
            email: str = f"concurrent_{uuid.uuid4().hex[:8]}@ex.com"
            user: Any = User(email=email, hashed_password="pw")
            session.add(user)
            await session.commit()
            return email

        # Run 5 concurrent inserts, each with its own session
        operations: list[Callable[[AsyncSession], Awaitable[str]]] = [insert_user] * 5
        results: list[str] = await self._run_concurrent_operations_typed(operations)
        # Check that all emails are unique and present
        assert len(set(results)) == 5

    @pytest.mark.asyncio
    async def test_db_healthcheck(self) -> None:
        """Test that db_healthcheck succeeds on a valid connection.
        
        Raises:
            AssertionError: If the healthcheck fails unexpectedly.
        """
        await self._assert_healthcheck_ok_typed(self.db_healthcheck)

    @pytest.mark.asyncio
    async def test_db_session_context(self) -> None:
        """Test that session context manager works properly.
        
        Raises:
            AssertionError: If the session context doesn't work as expected.
        """
        await self._assert_session_context_ok_typed(self.get_async_session, AsyncSession)

    @pytest.mark.asyncio
    async def test_session_rollback(self) -> None:
        """Test session rollback on error.
        
        Raises:
            AssertionError: If session rollback doesn't work properly.
        """
        await self._assert_session_rollback_typed(self.AsyncSessionLocal)

    @pytest.mark.asyncio
    async def test_users_table_exists(self) -> None:
        """Test that the users table exists.
        
        Raises:
            AssertionError: If the users table doesn't exist.
        """
        await self._assert_table_exists_typed(self.AsyncSessionLocal, "users")

    @pytest.mark.asyncio
    async def test_can_insert_and_query_user(self) -> None:
        """Test inserting and querying a user.
        
        Raises:
            AssertionError: If inserting and querying fails.
        """
        await self._assert_can_insert_and_query_typed(
            self.AsyncSessionLocal, self.User, USER_DATA, {"email": USER_EMAIL}
        )

    @pytest.mark.asyncio
    async def test_transaction_isolation(self) -> None:
        """Test transaction isolation for concurrent sessions.
        
        Raises:
            AssertionError: If transaction isolation doesn't work properly.
        """
        await self._assert_transaction_isolation_typed(
            self.AsyncSessionLocal, self.User, USER_DATA
        )

    @pytest.mark.asyncio
    async def test_integrity_error_on_duplicate_email(self) -> None:
        """Test that inserting a user with a duplicate email raises an integrity error.
        
        Raises:
            AssertionError: If integrity error is not raised for duplicate email.
        """
        await self._bulk_insert_typed(self.AsyncSessionLocal, self.User, [USER_DATA])
        await self._assert_db_integrity_error_typed(
            self.AsyncSessionLocal, self.User, USER_DATA
        )

    @pytest.mark.asyncio
    async def test_bulk_insert_and_query(self) -> None:
        """Test bulk inserting and querying users.
        
        Raises:
            AssertionError: If bulk operations fail.
        """
        emails: list[str] = [f"user{i}@ex.com" for i in range(5)]
        rows: list[dict[str, str]] = [dict(email=e, hashed_password="pw") for e in emails]
        await self._bulk_insert_typed(self.AsyncSessionLocal, self.User, rows)
        await self._assert_bulk_query_typed(
            self.AsyncSessionLocal, self.User, {"is_active": True}, 5
        )

    @pytest.mark.asyncio
    async def test_seed_and_truncate(self) -> None:
        """Test seeding and truncating the users table.
        
        Raises:
            AssertionError: If seeding and truncating operations fail.
        """
        await self._seed_database_typed(self.AsyncSessionLocal, self.User, [USER_DATA])
        await self._truncate_tables_typed(self.AsyncSessionLocal, ["users"])
        await self._assert_bulk_query_typed(
            self.AsyncSessionLocal, self.User, {"is_active": True}, 0
        )

    def test_migration_applied(self) -> None:
        """Test that the migration has been applied.
        
        Raises:
            AssertionError: If migration is not applied.
        """
        self._assert_migration_applied_typed(self.AsyncSessionLocal, "users")

    @pytest.mark.skip_if_fast_tests(
        "Migration test not applicable in fast (SQLite in-memory) mode"
    )
    def test_run_migration(self) -> None:
        """Test running the migration.
        
        Raises:
            AssertionError: If migration fails.
        """
        self._run_migration_typed("upgrade head")

    def test_simulate_db_disconnect(self) -> None:
        """Test simulating a database disconnect.
        
        Raises:
            pytest.skip: If running in fast tests mode.
            AssertionError: If disconnect simulation doesn't work.
        """
        if os.environ.get("FAST_TESTS") == "1":
            pytest.skip(
                "Simulate DB disconnect is not supported in fast (SQLite in-memory) mode."
            )
        self._simulate_db_disconnect_typed(self.AsyncSessionLocal)
        
        # Use asyncio.run with a proper coroutine
        async def test_healthcheck() -> None:
            await self.db_healthcheck()
            
        with pytest.raises(Exception):
            asyncio.run(test_healthcheck())

    def test_simulate_db_latency(self) -> None:
        """Test simulating database latency.
        
        Raises:
            AssertionError: If latency simulation fails.
        """
        self._simulate_db_latency_typed(self.AsyncSessionLocal, 0.1)
        # No assertion: just ensures patching works and doesn't error

    def test_connection_pool_size(self) -> None:
        """Test the connection pool size.
        
        Raises:
            AssertionError: If connection pool size doesn't match expected.
        """
        self._assert_connection_pool_size_typed(self.engine, 5)

    @pytest.mark.asyncio
    async def test_file_fk_constraint(self) -> None:
        """Test foreign key constraint enforcement.
        
        Raises:
            pytest.skip: If running in fast tests mode.
            AssertionError: If foreign key constraint is not enforced.
        """
        if os.environ.get("FAST_TESTS") == "1":
            pytest.skip(
                "SQLite in-memory does not reliably enforce foreign key constraints for this test."
            )
        # Should fail: user_id does not exist
        bad_file_data: dict[str, str | int] = dict(filename="bad.txt", content_type="text/plain", user_id=999999)
        async with self.AsyncSessionLocal() as session:
            file_obj: Any = self.File(**bad_file_data)
            session.add(file_obj)
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

    @pytest.mark.asyncio
    async def test_cascade_delete_user_files(self) -> None:
        """Test cascade delete functionality for user files.
        
        Raises:
            pytest.skip: If running SQLite backend or fast tests mode.
            AssertionError: If cascade delete doesn't work properly.
        """
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
        user: Any = self.User(email=get_unique_email(), hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            file_obj: Any = self.File(
                filename="f.txt", content_type="text/plain", user_id=user.id
            )
            session.add(file_obj)
            await session.commit()
            await session.delete(user)
            await session.commit()
            result: Any = await session.execute(
                self.File.__table__.select().filter_by(user_id=user.id)
            )
            files: list[Any] = result.scalars().all()
            # If cascade is not enabled, files may remain; adjust assertion as needed
            assert (
                not files or files == []
            ), "Files should be deleted with user if cascade is enabled"

    @pytest.mark.asyncio
    async def test_unique_constraint_on_email(self) -> None:
        """Test unique constraint on email field.
        
        Raises:
            AssertionError: If unique constraint is not enforced.
        """
        await self._bulk_insert_typed(self.AsyncSessionLocal, self.User, [USER_DATA])
        await self._assert_db_integrity_error_typed(
            self.AsyncSessionLocal, self.User, USER_DATA
        )

    def test_indexes_exist(self) -> None:
        """Test that expected indexes exist on tables.
        
        Raises:
            RuntimeError: If inspector is None.
            AssertionError: If expected indexes don't exist.
        """
        # Check if using SQLite backend or FAST_TESTS mode - both require async engine handling
        if os.environ.get("FAST_TESTS") == "1" or (
            hasattr(self, "engine") and "sqlite" in str(self.engine.url)
        ):
            from sqlalchemy import inspect

            async def check_indexes() -> None:
                async with self.engine.begin() as conn:

                    def get_indexes(sync_conn: Any) -> tuple[list[str], list[str]]:
                        insp: Any = inspect(sync_conn)
                        if insp is None:
                            raise RuntimeError(
                                f"Inspector is None for sync_conn: {sync_conn}, type: {type(sync_conn)}"
                            )
                        user_indexes: list[str] = [ix["name"] for ix in insp.get_indexes("users")]
                        file_indexes: list[str] = [ix["name"] for ix in insp.get_indexes("files")]
                        return user_indexes, file_indexes

                    user_indexes, file_indexes = await conn.run_sync(get_indexes)
                    assert any("ix_users_email" in ix for ix in user_indexes)
                    assert any("ix_files_user_id" in ix for ix in file_indexes)

            asyncio.run(check_indexes())
        else:
            from sqlalchemy import inspect

            insp: Any = inspect(self.engine)
            user_indexes: list[str] = [ix["name"] for ix in insp.get_indexes("users")]
            file_indexes: list[str] = [ix["name"] for ix in insp.get_indexes("files")]
            assert any("ix_users_email" in ix for ix in user_indexes)
            assert any("ix_files_user_id" in ix for ix in file_indexes)

    @pytest.mark.asyncio
    async def test_user_defaults(self) -> None:
        """Test that user model has correct default values.
        
        Raises:
            AssertionError: If default values are not set correctly.
        """
        email = get_unique_email()
        user: Any = self.User(email=email, hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result: Any = await session.execute(
                select(self.User).filter_by(email=email)
            )
            row: Any = result.scalar_one()
            assert row.is_active is True
            assert row.is_deleted is False
            assert row.is_admin is False

    @pytest.mark.asyncio
    async def test_update_and_query(self) -> None:
        """Test updating user data and querying the changes.
        
        Raises:
            AssertionError: If update operation doesn't work correctly.
        """
        email = get_unique_email()
        user: Any = self.User(email=email, hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            user.is_active = False
            await session.commit()
            result: Any = await session.execute(
                select(self.User).filter_by(email=email)
            )
            row: Any = result.scalar_one()
            assert row.is_active is False

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self) -> None:
        """Test that session rollback works correctly on exceptions.
        
        Raises:
            AssertionError: If rollback doesn't work properly.
        """
        user: Any = self.User(email=get_unique_email(), hashed_password="pw")
        try:
            async with self.AsyncSessionLocal() as session:
                session.add(user)
                raise Exception("fail before commit")
        except Exception:
            pass
        # User should not be committed
        async with self.AsyncSessionLocal() as session:
            result: Any = await session.execute(
                select(self.User).filter_by(email=get_unique_email())
            )
            row: Any | None = result.scalar_one_or_none()
            assert row is None

    @pytest.mark.asyncio
    async def test_user_repr(self) -> None:
        """Test string representation of user objects.
        
        Raises:
            AssertionError: If __repr__ doesn't return expected format.
        """
        user_email = get_unique_email()
        user: Any = self.User(email=user_email, hashed_password="pw")
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result: Any = await session.execute(
                select(self.User).filter_by(email=user_email)
            )
            row: Any = result.scalar_one()
            assert f"<User id={row.id} email={user_email}>" == repr(row)

    @pytest.mark.asyncio
    async def test_user_preferences_json(self) -> None:
        """Test JSON field handling for user preferences.
        
        Raises:
            AssertionError: If JSON field doesn't store/retrieve correctly.
        """
        prefs: dict[str, str] = {"theme": "dark", "lang": "en"}
        email = get_unique_email()
        user: Any = self.User(
            email=email, hashed_password="pw", preferences=prefs
        )
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result: Any = await session.execute(
                select(self.User).filter_by(email=email)
            )
            row: Any = result.scalar_one()
            assert row.preferences == prefs

    @pytest.mark.asyncio
    async def test_user_last_login_datetime(self) -> None:
        """Test datetime field handling for last login timestamp.
        
        Raises:
            AssertionError: If datetime field doesn't store/retrieve correctly.
        """
        now: datetime.datetime = datetime.datetime.now(datetime.UTC)
        email = get_unique_email()
        user: Any = self.User(
            email=email, hashed_password="pw", last_login_at=now
        )
        async with self.AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            result: Any = await session.execute(
                select(self.User).filter_by(email=email)
            )
            row: Any = result.scalar_one()
            assert row.last_login_at.replace(microsecond=0) == now.replace(
                microsecond=0
            )
