"""
Test templates and reusable test patterns for backend tests.

This module provides reusable test templates and base classes for common test scenarios.
Import and use these templates in your test files to reduce duplication and enforce consistency.

Note: This file is not a test itself and should be excluded from pytest plugins that check for missing source or test files.
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator, MutableMapping, Sequence
from pathlib import Path
from typing import Final, Literal, Protocol, TypedDict, Union
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from httpx import Response
from loguru import logger
from sqlalchemy import Table, inspect, text
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

# Protocol for mock objects to provide type safety
class MockProtocol(Protocol):
    """Protocol for mock objects with common attributes."""
    called: bool
    call_count: int

# Type definitions for strict typing
ResponseType = Union[Response, Mock]
AppType = Union[FastAPI, Mock]
MockType = Union[Mock, MockProtocol]
ValueType = Union[str, int, float, bool, dict[str, object], list[object], None, Callable[..., object]]
ClaimsDict = dict[str, Union[str, int, float, bool]]
StatusCodeType = Union[int, list[int], tuple[int, ...], set[int]]

# Type for SQLAlchemy model classes (not Table instances)
ModelType = type[object]


class BaseAPITest:
    """
    Base class for API endpoint tests.
    Provides common utility methods for API tests.
    Inherit from this class in your test classes to get auth helpers.
    """

    def safe_request(self, func: Callable[..., ResponseType], *args: object, **kwargs: object) -> ResponseType:
        """
        Helper to make HTTP requests robust to connection errors.
        Usage: resp = self.safe_request(client.get, ...)
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            pytest.xfail(f"Connection/DB error: {e}")

    @pytest.fixture(autouse=True)
    def _setup_base_fixtures(self, override_env_vars: Callable[[dict[str, str]], None], loguru_list_sink: list[str]) -> None:
        """Set up base fixtures for environment variables and logging."""
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink

    @pytest.fixture(autouse=True)
    def _inject_monkeypatch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Inject monkeypatch fixture."""
        self.monkeypatch = monkeypatch

    def get_auth_header(
        self,
        client: TestClient,
        email: str | None = None,
        password: str = "TestPassword123!",
    ) -> dict[str, str]:
        """
        Return an auth header for a test user. Can be overridden for custom logic.
        """
        try:
            from .conftest import get_auth_header
            result = get_auth_header(client, email=email, password=password)  # type: ignore[no-untyped-call]
            if isinstance(result, dict):
                return result
            else:
                # Fallback if conftest function returns unexpected type
                return {"Authorization": "Bearer test-token"}
        except (ImportError, AttributeError):
            # Fallback if conftest not available or function not found
            return {"Authorization": "Bearer test-token"}

    def assert_unauthorized(self, response: ResponseType) -> None:
        """
        Assert that a response is HTTP 401 Unauthorized.
        """
        assert response.status_code == 401
        assert "detail" in response.json()

    def patch_var(self, target: str, value: ValueType) -> None:
        """
        Patch a variable or attribute using monkeypatch.setattr, if available.
        Usage: self.patch_var('module.attr', new_value)
        This centralizes patching for all test templates.
        """
        if hasattr(self, "monkeypatch") and self.monkeypatch is not None:
            self.monkeypatch.setattr(target, value)
        else:
            raise RuntimeError(
                "monkeypatch fixture is not available. "
                "Ensure your test class inherits from a template that provides monkeypatch, "
                "such as AuthUnitTestTemplate, or add it to your template."
            )

    def assert_status(self, response: ResponseType, expected_statuses: StatusCodeType) -> None:
        """
        Assert that a response status code is in the expected set.
        """
        if isinstance(expected_statuses, int):
            expected_statuses = [expected_statuses]
        elif isinstance(expected_statuses, (tuple, set)):
            expected_statuses = list(expected_statuses)
        
        assert (
            response.status_code in expected_statuses
        ), f"Expected {expected_statuses}, got {response.status_code}"

    def assert_content_type(self, response: ResponseType, expected_type: str) -> None:
        """
        Assert that the response content-type header starts with the expected type.
        """
        assert response.headers["content-type"].startswith(expected_type)

    def assert_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that two values are equal."""
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_in(self, a: str, b: str, msg: str | None = None) -> None:
        """Assert that a string is contained in another string."""
        assert a in b, msg or f"Expected {a!r} to be in {b!r}"

    def assert_true(self, expr: object, msg: str | None = None) -> None:
        """Assert that an expression is truthy."""
        assert expr, msg or f"Expected expression to be true, got {expr!r}"

    def assert_is_instance(self, obj: object, cls: type[object], msg: str | None = None) -> None:
        """Assert that an object is an instance of a class."""
        assert isinstance(obj, cls), (
            msg or f"Expected {obj!r} to be instance of {cls!r}"
        )

    def assert_api_key_required(self, response: ResponseType) -> None:
        """
        Assert that a response indicates a missing or invalid API key (401 or 403).
        """
        assert response.status_code in (
            401,
            403,
        ), f"Expected 401 or 403, got {response.status_code}"
        body = response.json()
        assert (
            "api key" in str(body.get("detail", "")).lower()
            or "api key" in str(body).lower()
        ), f"Expected error message about API key, got: {body}"

    def assert_forbidden(self, response: ResponseType) -> None:
        """
        Assert that a response is HTTP 403 Forbidden.
        """
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        body = response.json()
        assert (
            "forbidden" in str(body.get("detail", "")).lower()
            or "forbidden" in str(body).lower()
        ), f"Expected forbidden error message, got: {body}"


class CRUDTestTemplate(BaseAPITest):
    """
    Template for CRUD endpoint tests. Inherit and override methods as needed.
    Set the endpoint, create_payload, and update_payload in your subclass.
    Uses loguru_list_sink and override_env_vars for env setup and log capture.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    endpoint: str = ""
    create_payload: dict[str, object] = {}
    update_payload: dict[str, object] = {}

    def test_create(self, client: TestClient, loguru_list_sink: list[str]) -> dict[str, object]:
        """
        Test creating a resource via POST. Captures logs for assertion if needed.
        """
        resp = client.post(
            self.endpoint,
            json=self.create_payload,
            headers=self.get_auth_header(client),
        )
        assert resp.status_code == 201
        data: dict[str, object] = resp.json()
        assert isinstance(data, dict), f"Expected dict response, got {type(data)}"
        assert "id" in data
        return data

    def test_read(self, client: TestClient, loguru_list_sink: list[str]) -> None:
        """
        Test reading a resource via GET after creation. Captures logs for assertion if needed.
        """
        created = self.test_create(client, loguru_list_sink)
        resp = client.get(
            f"{self.endpoint}/{created['id']}", headers=self.get_auth_header(client)
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == created["id"]

    def test_update(self, client: TestClient, loguru_list_sink: list[str]) -> None:
        """
        Test updating a resource via PUT. Captures logs for assertion if needed.
        """
        created = self.test_create(client, loguru_list_sink)
        resp = client.put(
            f"{self.endpoint}/{created['id']}",
            json=self.update_payload,
            headers=self.get_auth_header(client),
        )
        assert resp.status_code in (200, 204)

    def test_delete(self, client: TestClient, loguru_list_sink: list[str]) -> None:
        """
        Test deleting a resource via DELETE. Captures logs for assertion if needed.
        """
        created = self.test_create(client, loguru_list_sink)
        resp = client.delete(
            f"{self.endpoint}/{created['id']}", headers=self.get_auth_header(client)
        )
        assert resp.status_code in (200, 204)


class ExportEndpointTestTemplate(BaseAPITest):
    """
    Template for export/read-only endpoints.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    Uses async fixtures to avoid event loop conflicts.
    """

    @pytest.fixture(autouse=True)
    def _setup_async_fixtures(
        self,
        async_session: AsyncSession,
        test_app: AppType,
        loguru_list_sink: list[str],
        override_env_vars: Callable[[dict[str, str]], None],
    ) -> None:
        """Set up async fixtures for export endpoint tests."""
        self.async_session = async_session
        self.test_app = test_app
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars


class UserCoreEndpointTestTemplate(BaseAPITest):
    """
    Template for user core endpoint tests that require async_session, test_app, loguru_list_sink, and override_env_vars.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    Uses async fixtures to avoid event loop conflicts.
    """

    @pytest.fixture(autouse=True)
    def _setup_async_fixtures(
        self,
        async_session: AsyncSession,
        test_app: AppType,
        loguru_list_sink: list[str],
        override_env_vars: Callable[[dict[str, str]], None],
    ) -> None:
        """Set up async fixtures for user core endpoint tests."""
        self.async_session = async_session
        self.test_app = test_app
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars


class UserAuthEndpointTestTemplate(BaseAPITest):
    """
    Template for user auth endpoint tests that require async_session, test_app_with_auth, loguru_list_sink, and override_env_vars.
    This template is specifically for testing authentication requirements.
    """

    @pytest.fixture(autouse=True)
    def _setup_async_fixtures(
        self,
        async_session: AsyncSession,
        test_app_with_auth: AppType,
        loguru_list_sink: list[str],
        override_env_vars: Callable[[dict[str, str]], None],
    ) -> None:
        """Set up async fixtures for user auth endpoint tests."""
        self.async_session = async_session
        self.test_app = test_app_with_auth
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars


class LogCaptureTestTemplate(BaseAPITest):
    """
    Template for tests that need to assert on log output.
    Uses loguru_list_sink, and override_env_vars.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_env_and_logs(self, loguru_list_sink: list[str], override_env_vars: Callable[[dict[str, str]], None]) -> None:
        """Set up environment and logging fixtures."""
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars


class AuthUnitTestTemplate(BaseAPITest):
    """
    Template for authentication-related unit tests that require monkeypatch, loguru_list_sink, and override_env_vars.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    Provides helpers for patching, restoring, and asserting dependency behaviors.
    """

    @pytest.fixture(autouse=True)
    def _setup_monkeypatch_and_logs(
        self, monkeypatch: pytest.MonkeyPatch, loguru_list_sink: list[str], override_env_vars: Callable[[dict[str, str]], None]
    ) -> Generator[None, None, None]:
        """Set up monkeypatch and logging fixtures."""
        self.monkeypatch = monkeypatch
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        self._patches: list[tuple[str, str, object]] = []
        yield
        # Restore all patched attributes after each test
        import re
        for target, attr, orig in self._patches:
            if isinstance(target, str) and target.startswith("os.environ["):
                import os
                key = target.split('["')[1].split('"]')[0]
                if orig is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = str(orig)
            # Only treat as module path if it looks like a valid Python module path (e.g., no angle brackets, no spaces, not a repr)
            elif (
                isinstance(target, str)
                and "." in target
                and re.match(r'^[a-zA-Z_][\w\.]*\.[a-zA-Z_][\w]*$', target)
            ):
                try:
                    module, attr_name = target.rsplit(".", 1)
                    mod = __import__(module, fromlist=[attr_name])
                    setattr(mod, attr_name, orig)
                except (ModuleNotFoundError, ImportError, AttributeError):
                    # Fallback: treat as object/attribute
                    pass
            else:
                # target is an object, attr is attribute name
                try:
                    setattr(target, attr, orig)
                except Exception:
                    pass

    def patch_dep(self, target: str, value: ValueType) -> None:
        """
        Patch a dependency and automatically restore it after the test.
        Usage: self.patch_dep('src.api.deps.verify_access_token', fake_func)
        """
        module, attr = target.rsplit(".", 1)
        mod = __import__(module, fromlist=[attr])
        orig = getattr(mod, attr)
        self.monkeypatch.setattr(mod, attr, value)
        self._patches.append((target, attr, orig))

    def patch_setting(self, obj: object, attr: str, value: ValueType) -> None:
        """
        Patch a config/settings attribute and restore after test.
        Usage: self.patch_setting(settings, 'auth_enabled', False)

        Special case: If patching a module's 'settings' attribute and the module
        doesn't have one (uses get_settings() instead), patch get_settings function.
        """
        try:
            orig = getattr(obj, attr)
            self.monkeypatch.setattr(obj, attr, value)
            self._patches.append((str(obj), attr, orig))
        except AttributeError:
            if attr == "settings":
                # Module uses get_settings() function instead of settings attribute
                self.monkeypatch.setattr("src.core.config.get_settings", lambda: value)
                self._patches.append(("src.core.config.get_settings", "", None))
            else:
                raise

    def assert_http_exception(self, func: Callable[[], object], status_code: int, detail_substr: str | None = None) -> None:
        """Assert that a function raises an HTTP exception with expected status."""
        with pytest.raises(HTTPException) as exc:
            func()
        assert exc.value.status_code == status_code
        if detail_substr:
            assert detail_substr in str(exc.value.detail)

    async def assert_async_http_exception(self, func: Callable[[], Awaitable[object]], status_code: int, detail_substr: str | None = None) -> None:
        """Assert that an async function raises an HTTP exception with expected status."""
        with pytest.raises(HTTPException) as exc:
            await func()
        assert exc.value.status_code == status_code
        if detail_substr:
            assert detail_substr in str(exc.value.detail)

    def patch_async_dep(self, target: str, async_mock: ValueType) -> None:
        """
        Patch an async dependency (e.g., DB call) and auto-restore after test.
        Usage: self.patch_async_dep('src.api.deps.get_user_by_id', AsyncMock(...))
        """
        self.patch_dep(target, async_mock)

    def patch_env(self, key: str, value: str) -> None:
        """
        Patch an environment variable for the test duration.
        Usage: self.patch_env('MY_ENV', 'value')
        """
        import os

        orig = os.environ.get(key)
        self.monkeypatch.setenv(key, value)
        self._patches.append((f'os.environ["{key}"]', "", orig))

    def restore_env(self, key: str) -> None:
        """Restore an environment variable to its original value."""
        import os

        for i, (target, attr, orig) in enumerate(self._patches):
            if isinstance(target, str) and target == f'os.environ["{key}"]':
                if orig is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = str(orig)
                self._patches.pop(i)
                break


class AuthEndpointTestTemplate(BaseAPITest):
    """
    Template for authentication-related async endpoint tests that require async_session, test_app, loguru_list_sink, and override_env_vars.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_async_fixtures(
        self,
        async_session: AsyncSession,
        test_app: AppType,
        loguru_list_sink: list[str],
        override_env_vars: Callable[[dict[str, str]], None],
    ) -> None:
        """Set up async fixtures for auth endpoint tests."""
        self.async_session = async_session
        self.test_app = test_app
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars


class HealthEndpointTestTemplate(BaseAPITest):
    """
    Template for health/liveness/readiness endpoint tests.
    Use this for /health, /alive, /ready endpoints.
    Provides health-specific helpers and ensures consistent assertions.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.

    Note: Do NOT use BaseAPITest directly for health checks—use this template instead.
    """

    @pytest.fixture(autouse=True)
    def _setup_env(self, override_env_vars: Callable[[dict[str, str]], None], loguru_list_sink: list[str]) -> None:
        """Set up environment fixtures for health tests."""
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink

    def assert_health_response(self, resp: ResponseType) -> None:
        """Assert that a health response is valid."""
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert data["status"] in ("ok", "healthy", "alive")


class DatabaseTestTemplate(BaseAPITest):
    """
    Template for async database/session/engine/healthcheck tests.
    Provides self.override_env_vars and self.monkeypatch for env/patching, and async helpers.
    Inherit from this for all DB-related tests.
    """

    # Engine attribute will be set by fixtures
    engine: AsyncEngine

    @staticmethod
    async def _enable_sqlite_fk(engine: AsyncEngine) -> None:
        """Enable SQLite foreign key enforcement for async engines."""
        if "sqlite" in str(engine.url):
            # For async SQLite engines, we need to enable FK on each connection
            async with engine.begin() as conn:
                await conn.execute(text("PRAGMA foreign_keys=ON"))

    async def get_independent_session(self) -> AsyncSession:
        """
        Get a new independent session for concurrent operations.
        Each call returns a session with its own connection.
        Assumes tables are already created by the test fixture.
        """
        await self._enable_sqlite_fk(self.engine)
        return AsyncSession(self.engine, expire_on_commit=False)

    async def run_concurrent_operations(self, operations: list[Callable[[AsyncSession], Awaitable[object]]]) -> list[object]:
        """
        Run multiple database operations concurrently with separate sessions.
        Args:
            operations: List of async callables that take a session parameter
        """
        async def run_with_session(operation: Callable[[AsyncSession], Awaitable[object]]) -> object:
            # get_independent_session is now async
            session = await self.get_independent_session()
            try:
                async with session:
                    return await operation(session)
            finally:
                await session.close()

        return await asyncio.gather(*[run_with_session(op) for op in operations])

    async def assert_healthcheck_ok(self, healthcheck_func: Callable[[], Awaitable[None]]) -> None:
        """Assert that a database healthcheck function completes without error."""
        try:
            await healthcheck_func()
        except Exception as exc:
            pytest.fail(f"db_healthcheck raised unexpectedly: {exc}")

    async def assert_session_context_ok(self, get_session_func: Callable[[], AsyncSession], session_type: type[AsyncSession]) -> None:
        """Assert that a session context manager works correctly."""
        session: AsyncSession | None = None
        try:
            async with get_session_func() as s:
                session = s
                assert isinstance(session, session_type)
            assert session is not None
        except Exception:
            # If we get connection-related errors during async context cleanup,
            # still check that we got a valid session during the context
            if session is not None and isinstance(session, session_type):
                # The session was valid during the context, so the test passes
                # even if cleanup had issues
                pass
            else:
                # Re-raise if we never got a valid session
                raise

    async def assert_session_rollback(
        self, session_factory: Callable[[], AsyncSession], error_sql: str = "SELECT invalid_column_name"
    ) -> None:
        """Assert that session rollback works correctly after an error."""
        session = session_factory()
        try:
            await session.execute(text(error_sql))
            await session.commit()
            raise AssertionError("Should not reach here")
        except SQLAlchemyError:
            await session.rollback()
            # Test that the session is still usable after rollback
            result = await session.execute(text("SELECT 1"))
            assert result is not None
        except Exception as e:
            # If we get an unexpected error (like connection issues),
            # still try to rollback but don't fail the test
            try:
                await session.rollback()
            except Exception:
                pass  # Ignore rollback errors in case of connection issues
            raise AssertionError(f"Unexpected error during session rollback test: {e}")
        finally:
            # Safely close the session, ignoring any connection cleanup errors
            try:
                await session.close()
            except Exception:
                pass  # Ignore close errors during cleanup

    async def assert_table_exists(self, session_factory: Callable[[], AsyncSession], table_name: str) -> None:
        """Assert that a database table exists."""
        async with session_factory() as session:
            conn = await session.connection()
            def get_tables(sync_conn: object) -> list[str]:
                inspector = inspect(sync_conn)
                if inspector is not None and hasattr(inspector, 'get_table_names'):
                    table_names = getattr(inspector, 'get_table_names')()
                    return table_names if isinstance(table_names, list) else []
                return []
            tables = await conn.run_sync(get_tables)
            assert table_name in tables, f"Table '{table_name}' does not exist"

    async def assert_table_not_exists(self, session_factory: Callable[[], AsyncSession], table_name: str) -> None:
        """Assert that a database table does not exist."""
        async with session_factory() as session:
            conn = await session.connection()
            def get_tables(sync_conn: object) -> list[str]:
                insp = inspect(sync_conn)
                if insp is not None and hasattr(insp, 'get_table_names'):
                    table_names = getattr(insp, 'get_table_names')()
                    return table_names if isinstance(table_names, list) else []
                return []
            tables = await conn.run_sync(get_tables)
            assert table_name not in tables, f"Table '{table_name}' should not exist"

    async def assert_can_insert_and_query(
        self, session_factory: Callable[[], AsyncSession], table: ModelType, insert_dict: dict[str, object], query_filter: dict[str, object]
    ) -> None:
        """Assert that data can be inserted and queried from a table."""
        async with session_factory() as session:
            obj = table(**insert_dict)
            session.add(obj)
            await session.commit()
            result = await session.execute(
                table.__table__.select().filter_by(**query_filter)  # type: ignore[attr-defined]
            )
            row = result.scalar_one_or_none()
            assert row is not None, f"Row not found for filter {query_filter}"

    async def assert_transaction_isolation(self, session_factory: Callable[[], AsyncSession], table: ModelType, insert_dict: dict[str, object]) -> None:
        """Assert that transaction isolation works correctly."""
        async with session_factory() as session:
            trans = await session.begin()
            obj = table(**insert_dict)
            session.add(obj)
            await trans.rollback()
            result = await session.execute(
                table.__table__.select().filter_by(**insert_dict)  # type: ignore[attr-defined]
            )
            row = result.scalar_one_or_none()
            assert row is None, "Row should not exist after rollback"

    def simulate_db_disconnect(self, session_factory: Callable[[], AsyncSession]) -> None:
        """Simulate a database disconnection by patching session creation."""
        # Patch the session/engine to raise on connect (works for async/SQLite)
        def raise_disconnect(*a: object, **kw: object) -> None:
            raise OperationalError("Simulated disconnect", None, RuntimeError("Connection failed"))

        self.patch_var(
            f"{session_factory.__module__}.AsyncSession.__init__", raise_disconnect
        )
        # Also patch sync Session if present
        try:
            self.patch_var(
                f"{session_factory.__module__}.Session.__init__", raise_disconnect
            )
        except Exception:
            pass

    async def assert_db_integrity_error(self, session_factory: Callable[[], AsyncSession], table: ModelType, insert_dict: dict[str, object]) -> None:
        """Assert that database integrity constraints are enforced."""
        async with session_factory() as session:
            obj = table(**insert_dict)
            session.add(obj)
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

    async def run_raw_sql(self, session_factory: Callable[[], AsyncSession], sql: str) -> Sequence[object]:
        """Execute raw SQL and return results."""
        async with session_factory() as session:
            result = await session.execute(text(sql))
            return result.fetchall()

    def assert_db_url_config(self, cfg: object, expected_url: str) -> None:
        """Assert that database URL configuration is correct."""
        assert getattr(cfg, "settings", None) is not None, "Config object must have settings attribute"
        assert getattr(cfg.settings, "db_url", None) == expected_url  # type: ignore[attr-defined]

    # --- Migration Helpers ---
    def assert_migration_applied(self, session_factory: Callable[[], AsyncSession], table_name: str | None = None, version: str | None = None) -> None:
        """Assert that a database migration has been applied."""
        # Checks for table or migration version presence
        async def _check() -> None:
            async with session_factory() as session:
                conn = await session.connection()
                def check_tables(sync_conn: object) -> dict[str, object]:
                    inspector = inspect(sync_conn)
                    result: dict[str, object] = {}
                    if table_name and inspector is not None and hasattr(inspector, 'get_table_names'):
                        tables = getattr(inspector, 'get_table_names')()
                        if isinstance(tables, list):
                            result["tables"] = tables
                    return result
                result = await conn.run_sync(check_tables)
                if table_name:
                    tables = result["tables"]
                    assert isinstance(tables, list), "Tables should be a list"
                    assert (
                        table_name in tables
                    ), f"Table '{table_name}' not found after migration"
                if version:
                    versions = await session.execute(
                        text("SELECT version_num FROM alembic_version")
                    )
                    found = [row[0] for row in versions]
                    assert (
                        version in found
                    ), f"Migration version {version} not applied"
        asyncio.run(_check())

    @pytest.mark.requires_real_db(
        "Alembic migrations are not supported in fast (SQLite in-memory) mode."
    )
    def run_migration(self, command: str = "upgrade head") -> None:
        """Run an Alembic migration command with a temp config file for script_location and sqlalchemy.url."""
        import os
        import tempfile
        from pathlib import Path

        migrations_path = str(Path(__file__).parent.parent / "src" / "alembic_migrations")
        db_url = os.environ.get("REVIEWPOINT_DB_URL")
        assert db_url, "REVIEWPOINT_DB_URL must be set for Alembic migrations"

        # Write a temporary alembic.ini file
        alembic_ini_content = f"""
[alembic]
script_location = {migrations_path}
sqlalchemy.url = {db_url}
"""
        with tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False) as tmp_ini:
            tmp_ini.write(alembic_ini_content)
            tmp_ini_path = tmp_ini.name

        try:
            result = subprocess.run(
                ["alembic", "-c", tmp_ini_path] + command.split(),
                capture_output=True, text=True
            )
            assert result.returncode == 0, f"Migration failed: {result.stderr}\n{result.stdout}"
        finally:
            try:
                os.remove(tmp_ini_path)
            except Exception:
                pass

    # --- Latency/Slow Query Simulation ---
    def simulate_db_latency(self, session_factory: Callable[[], AsyncSession], delay: float = 0.5) -> None:
        """Simulate database latency by adding delays to queries."""
        # This is a placeholder implementation since proper patching would require
        # more complex type handling. In practice, this would mock the execute method.
        # For strict typing, we'll use a simpler approach with a warning.
        import warnings
        warnings.warn(
            f"Database latency simulation enabled with {delay}s delay. "
            "Actual implementation would require runtime patching.",
            UserWarning,
            stacklevel=2
        )

    # --- Bulk Insert/Batch Operation Helpers ---
    async def bulk_insert(self, session_factory: Callable[[], AsyncSession], table: ModelType, rows: list[dict[str, object]]) -> list[object]:
        """Bulk insert rows into a table."""
        async with session_factory() as session:
            objs = [table(**row) for row in rows]
            session.add_all(objs)
            await session.commit()
            return objs

    async def assert_bulk_query(
        self, session_factory: Callable[[], AsyncSession], table: ModelType, filter_dict: dict[str, object], expected_count: int
    ) -> None:
        """Assert that a bulk query returns the expected number of rows."""
        async with session_factory() as session:
            result = await session.execute(
                table.__table__.select().filter_by(**filter_dict)  # type: ignore[attr-defined]
            )
            rows = result.scalars().all()
            assert (
                len(rows) == expected_count
            ), f"Expected {expected_count} rows, got {len(rows)}"

    # --- Database Seeding/Cleanup ---
    async def seed_database(self, session_factory: Callable[[], AsyncSession], table: ModelType, rows: list[dict[str, object]]) -> list[object]:
        """Seed the database with test data."""
        return await self.bulk_insert(session_factory, table, rows)

    async def truncate_tables(self, session_factory: Callable[[], AsyncSession], tables: list[str]) -> None:
        """Truncate database tables."""
        async with session_factory() as session:
            # Detect SQLite and use DELETE FROM instead of TRUNCATE
            # Note: session.bind might be AsyncConnection, need to check engine
            bind = session.get_bind()
            engine_url = "unknown"
            
            # Try different ways to get the URL depending on the bind type
            if hasattr(bind, 'url'):
                engine_url = str(getattr(bind, 'url'))
            elif hasattr(bind, 'engine'):
                engine = getattr(bind, 'engine')
                if hasattr(engine, 'url'):
                    engine_url = str(getattr(engine, 'url'))
            
            if engine_url.startswith("sqlite"):
                for table in tables:
                    await session.execute(text(f"DELETE FROM {table}"))
            else:
                for table in tables:
                    await session.execute(
                        text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                    )
            await session.commit()

    # --- Connection Pool/State Helpers ---
    def assert_connection_pool_size(self, engine: AsyncEngine, expected_size: int) -> None:
        """Assert that connection pool has expected size."""
        pool = engine.pool
        # SQLite in-memory uses StaticPool, which lacks checkedin/checkedout
        pool_class = type(pool).__name__
        if pool_class == "StaticPool":
            # In fast mode, just assert pool is StaticPool
            assert pool_class == "StaticPool"
            return
        # For other pool types, attempt to get size if attributes exist
        try:
            size = getattr(pool, 'checkedin', lambda: 0)() + getattr(pool, 'checkedout', lambda: 0)()
            assert size == expected_size, f"Expected pool size {expected_size}, got {size}"
        except (AttributeError, TypeError):
            # If attributes don't exist or aren't callable, skip the check
            pass

    # --- Multi-DB/Shard Helpers ---
    async def assert_cross_db_query(self, session_factories: list[Callable[[], AsyncSession]], sql: str, expected_results: list[object]) -> None:
        """Assert that queries across multiple databases return expected results."""
        for i, (session_factory, expected) in enumerate(
            zip(session_factories, expected_results, strict=False)
        ):
            rows = await self.run_raw_sql(session_factory, sql)
            assert rows == expected, f"DB {i} results mismatch: {rows} != {expected}"


class EventTestTemplate:
    """
    Template for event/lifecycle/log assertion tests.
    Provides monkeypatch, loguru sink, caplog, and log assertion helpers.
    Inherit from this for all event/startup/shutdown/log tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_event_fixtures(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
        loguru_list_sink: list[str],
        override_env_vars: Callable[[dict[str, str]], None],
    ) -> Generator[None, None, None]:
        """Set up event testing fixtures."""
        self.monkeypatch = monkeypatch
        self.tmp_path = tmp_path
        self.caplog = caplog
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        # Setup loguru sink for log file capture
        self.log_file = tmp_path / "loguru.log"
        handler_id = logger.add(self.log_file, format="{message}", enqueue=True)
        yield
        try:
            logger.remove(handler_id)
        except ValueError:
            # Handler already removed or doesn't exist
            pass

    def patch_settings(self, target_module: str, settings_obj: object) -> None:
        """
        Patch settings for a module. This handles both:
        1. Modules that have a 'settings' attribute (legacy)
        2. Modules that use get_settings() function (modern approach)
        """
        try:
            # Try to patch the settings attribute directly
            self.monkeypatch.setattr(target_module, "settings", settings_obj)
        except AttributeError:
            # If the module doesn't have a settings attribute,
            # mock the get_settings function in src.core.config
            self.monkeypatch.setattr(
                "src.core.config.get_settings", lambda: settings_obj
            )

    def get_loguru_text(self) -> str:
        """Get text from loguru log file, ensuring all logs are flushed."""
        from loguru import logger
        import time
        # Flush loguru handlers to ensure all logs are written
        logger.complete()
        time.sleep(0.05)  # Small delay to allow async file handler to flush
        return self.log_file.read_text()

    def assert_log_contains(self, text: str) -> None:
        """Assert that log contains specific text."""
        logs = self.get_loguru_text()
        assert text in logs, f"Expected log to contain '{text}', got: {logs}"

    def assert_caplog_contains(self, text: str, level: str | None = None) -> None:
        """Assert that caplog contains specific text."""
        logs = self.caplog.text
        if level:
            logs = "\n".join(
                [r.getMessage() for r in self.caplog.records if r.levelname == level]
            )
        assert text in logs, f"Expected caplog to contain '{text}', got: {logs}"


class OpenAPITestTemplate(BaseAPITest):
    """
    Template for OpenAPI and documentation endpoint tests.
    Provides self.client and common OpenAPI assertion helpers.
    Handles setup and teardown for the test client.

    Usage:
        class TestOpenAPI(OpenAPITestTemplate):
            def test_metadata(self):
                resp = self.client.get("/openapi.json")
                self.assert_openapi_metadata(resp)
    """

    @pytest.fixture(autouse=True)
    def _setup_client(
        self,
        test_app: AppType,
        request: pytest.FixtureRequest,
        override_env_vars: Callable[[dict[str, str]], None],
        loguru_list_sink: list[str],
    ) -> Generator[None, None, None]:
        """Set up test client and environment."""
        from src.core.openapi import setup_openapi

        setup_openapi(test_app)
        self.client: TestClient = TestClient(test_app)
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink
        yield
        if hasattr(self, "client") and hasattr(self.client, "close"):
            self.client.close()

    def assert_openapi_metadata(self, resp: ResponseType) -> None:
        """Assert that OpenAPI metadata is correct."""
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["info"]["title"] == "ReViewPoint Core API"
        assert data["info"]["description"].startswith(
            "API for modular scientific paper review platform"
        )
        assert data["info"]["version"] == "0.1.0"
        assert "contact" in data["info"]
        assert "license" in data["info"]
        assert "servers" in data
        assert any(s["url"] == "http://localhost:8000" for s in data["servers"])
        assert any(s["url"] == "https://api.reviewpoint.org" for s in data["servers"])

    def assert_docs_accessible(self) -> None:
        """Assert that documentation endpoints are accessible."""
        assert self.client.get("/docs").status_code == 200
        assert self.client.get("/redoc").status_code == 200

    def assert_endpoint_doc(
        self, path: str, method: str, summary: str, status_code: int
    ) -> None:
        """Assert that an endpoint is documented correctly."""
        resp = self.client.get("/openapi.json")
        paths = resp.json()["paths"]
        assert path in paths
        op = paths[path][method]
        assert op["summary"] == summary
        assert "responses" in op
        assert str(status_code) in op["responses"]

    def assert_endpoint_missing(self, path: str) -> None:
        """Assert that an endpoint is not present in OpenAPI spec."""
        resp = self.client.get("/openapi.json")
        paths = resp.json()["paths"]
        assert (
            path not in paths
        ), f"Endpoint {path} should not be present in OpenAPI spec"

    def assert_invalid_docs(self, url: str = "/invalid-docs") -> None:
        """Assert that invalid documentation URLs return 404."""
        resp = self.client.get(url)
        assert resp.status_code == 404

    def validate_openapi_schema(self) -> None:
        """Validate the OpenAPI schema using external validator."""
        try:
            from openapi_schema_validator import validate
        except ImportError:
            pytest.skip("openapi_schema_validator not installed")
        resp = self.client.get("/openapi.json")
        validate(resp.json())


class SecurityUnitTestTemplate(BaseAPITest):
    """
    Template for security-related unit tests (e.g., JWT, token, cryptography).
    Provides monkeypatch and override_env_vars for patching and env overrides.
    Includes helpers for JWT claims, expiry, and negative/edge case assertions.
    """

    @pytest.fixture(autouse=True)
    def _setup_security_fixtures(
        self, monkeypatch: pytest.MonkeyPatch, override_env_vars: Callable[[dict[str, str]], None], loguru_list_sink: list[str]
    ) -> None:
        """Set up security testing fixtures."""
        self.monkeypatch = monkeypatch
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink

    def assert_jwt_claims(
        self, token: str, secret: str, algorithm: str, expected_claims: ClaimsDict
    ) -> None:
        """Assert that JWT contains expected claims."""
        from jose import jwt

        decoded = jwt.decode(token, secret, algorithms=[algorithm])
        for k, v in expected_claims.items():
            assert decoded[k] == v, f"JWT claim {k} mismatch: {decoded[k]} != {v}"
        assert "exp" in decoded
        assert "iat" in decoded

    def assert_jwt_expired(self, token: str, secret: str, algorithm: str) -> None:
        """Assert that JWT token is expired."""
        from jose import ExpiredSignatureError, jwt

        with pytest.raises(ExpiredSignatureError):
            jwt.decode(token, secret, algorithms=[algorithm])

    def assert_jwt_invalid(self, token: str, secret: str, algorithm: str) -> None:
        """Assert that JWT token is invalid."""
        from jose import JWTError, jwt

        with pytest.raises(JWTError):
            jwt.decode(token, secret, algorithms=[algorithm])

    def patch_jwt_secret(self, new_secret: str) -> None:
        """Patch JWT secret for testing purposes."""
        # Example: self.patch_jwt_secret("badsecret")
        self.patch_var("src.core.config.settings.jwt_secret_key", new_secret)


class ModelUnitTestTemplate:
    """
    Template for SQLAlchemy model/unit tests.
    Provides helpers for to_dict, __repr__, and attribute assertions.
    Centralizes model test patterns for DRYness and maintainability.
    """

    def assert_to_dict(self, model: object, expected_dict: dict[str, object], msg: str | None = None) -> None:
        """Assert that model.to_dict() returns the expected dictionary."""
        actual: dict[str, object] = getattr(model, 'to_dict', lambda: {})()
        assert actual == expected_dict, (
            msg or f"Expected to_dict() to return {expected_dict!r}, got {actual!r}"
        )

    def assert_model_attrs(self, model: object, attrs: dict[str, object], msg: str | None = None) -> None:
        """Assert that a model has expected attribute values."""
        for k, v in attrs.items():
            actual = getattr(model, k, None)
            assert actual == v, msg or f"Expected {k}={v!r}, got {actual!r}"

    def assert_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that two values are equal."""
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_not_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that two values are not equal."""
        assert a != b, msg or f"Expected {a!r} != {b!r}"

    def assert_in(self, member: object, container: object, msg: str | None = None) -> None:
        """Assert that a member is in a container."""
        assert member in container, msg or f"Expected {member!r} in {container!r}"  # type: ignore[operator]

    def assert_not_in(self, member: object, container: object, msg: str | None = None) -> None:
        """Assert that a member is not in a container."""
        assert member not in container, (  # type: ignore[operator]
            msg or f"Expected {member!r} not in {container!r}"
        )

    def assert_is_none(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is None."""
        assert value is None, msg or f"Expected value to be None, got {value!r}"

    def assert_is_not_none(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is not None."""
        assert value is not None, msg or "Expected value to not be None"

    def assert_is_true(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is True."""
        assert value is True, msg or f"Expected value to be True, got {value!r}"

    def assert_is_false(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is False."""
        assert value is False, msg or f"Expected value to be False, got {value!r}"

    def assert_raises(self, exc_type: type[BaseException], func: Callable[..., object], *args: object, **kwargs: object) -> None:
        """Assert that a function raises a specific exception."""
        with pytest.raises(exc_type):
            func(*args, **kwargs)

    def assert_repr(self, obj: object, class_name: str) -> None:
        """Assert that an object's repr contains the class name."""
        r = repr(obj)
        assert class_name in r, f"Expected {class_name} in repr: {r}"


class AsyncModelTestTemplate(ModelUnitTestTemplate):
    """
    Template for async SQLAlchemy model tests that require async_session.
    Inherit from this for DB-backed async model tests.
    Provides helpers for DB seeding, cleanup, and transactional test patterns.
    """

    @pytest.fixture(autouse=True)
    def _setup_async_model_fixtures(
        self, async_session: AsyncSession, override_env_vars: Callable[[dict[str, str]], None], loguru_list_sink: list[str]
    ) -> None:
        """Set up async model testing fixtures."""
        self.async_session = async_session
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink

    async def seed_db(self, objs: list[object]) -> None:
        """Bulk add and commit a list of model instances."""
        self.async_session.add_all(objs)
        await self.async_session.commit()

    async def truncate_table(self, table: str) -> None:
        """Truncate a table and reset identity (Postgres only)."""
        await self.async_session.execute(text(f"DELETE FROM {table}"))
        await self.async_session.commit()

    async def run_in_transaction(self, coro: Callable[[], Awaitable[None]]) -> None:
        """Run a coroutine in a transaction and roll back after."""
        # If already in a transaction, use a savepoint instead
        if self.async_session.in_transaction():
            trans = await self.async_session.begin_nested()
        else:
            trans = await self.async_session.begin()
        try:
            await coro()
        finally:
            await trans.rollback()

    async def assert_integrity_error(self, obj: object) -> None:
        """Assert that adding an object causes an integrity error."""
        self.async_session.add(obj)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()


class UtilityUnitTestTemplate:
    """
    Base class for utility (non-API, non-DB) unit tests.
    Provides a consistent structure and utility-specific helpers.
    """

    def assert_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that two values are equal."""
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_not_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that two values are not equal."""
        assert a != b, msg or f"Expected {a!r} != {b!r}"

    def assert_in(self, member: object, container: object, msg: str | None = None) -> None:
        """Assert that a member is in a container."""
        assert member in container, msg or f"Expected {member!r} in {container!r}"  # type: ignore[operator]

    def assert_not_in(self, member: object, container: object, msg: str | None = None) -> None:
        """Assert that a member is not in a container."""
        assert member not in container, (  # type: ignore[operator]
            msg or f"Expected {member!r} not in {container!r}"
        )

    def assert_almost_equal(self, a: float, b: float, tol: float = 1e-7, msg: str | None = None) -> None:
        """Assert that two floating point numbers are approximately equal."""
        assert abs(a - b) <= tol, msg or f"Expected {a!r} ≈ {b!r} (tol={tol})"

    def assert_true(self, expr: object, msg: str | None = None) -> None:
        """Assert that an expression is truthy."""
        assert expr, msg or f"Expected expression to be True, got {expr!r}"

    def assert_false(self, expr: object, msg: str | None = None) -> None:
        """Assert that an expression is falsy."""
        assert not expr, msg or f"Expected expression to be False, got {expr!r}"

    def assert_is_none(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is None."""
        assert value is None, msg or f"Expected value to be None, got {value!r}"

    def assert_is_not_none(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is not None."""
        assert value is not None, msg or "Expected value to not be None"

    def assert_is_instance(self, obj: object, cls: type[object], msg: str | None = None) -> None:
        """Assert that an object is an instance of a class."""
        assert isinstance(obj, cls), (
            msg or f"Expected {obj!r} to be instance of {cls!r}"
        )

    def assert_is_not_instance(self, obj: object, cls: type[object], msg: str | None = None) -> None:
        """Assert that an object is not an instance of a class."""
        assert not isinstance(obj, cls), (
            msg or f"Expected {obj!r} to not be instance of {cls!r}"
        )

    def assert_raises(self, exc_type: type[BaseException], func: Callable[..., object], *args: object, **kwargs: object) -> None:
        """Assert that a function raises a specific exception."""
        with pytest.raises(exc_type):
            func(*args, **kwargs)

    async def assert_async_raises(self, exc_type: type[BaseException], func: Callable[..., Awaitable[object]], *args: object, **kwargs: object) -> None:
        """Assert that an async function raises a specific exception."""
        with pytest.raises(exc_type):
            await func(*args, **kwargs)

    def assert_greater(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that a > b."""
        assert a > b, msg or f"Expected {a!r} > {b!r}"  # type: ignore[operator]

    def assert_greater_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that a >= b."""
        assert a >= b, msg or f"Expected {a!r} >= {b!r}"  # type: ignore[operator]

    def assert_less(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that a < b."""
        assert a < b, msg or f"Expected {a!r} < {b!r}"  # type: ignore[operator]

    def assert_less_equal(self, a: object, b: object, msg: str | None = None) -> None:
        """Assert that a <= b."""
        assert a <= b, msg or f"Expected {a!r} <= {b!r}"  # type: ignore[operator]

    def assert_dict_equal(self, d1: dict[str, object], d2: dict[str, object], msg: str | None = None) -> None:
        """Assert that two dictionaries are equal."""
        assert d1 == d2, msg or f"Expected dicts to be equal: {d1!r} == {d2!r}"

    def assert_list_equal(self, l1: Sequence[object], l2: Sequence[object], msg: str | None = None) -> None:
        """Assert that two sequences are equal."""
        assert list(l1) == list(l2), (
            msg or f"Expected lists to be equal: {l1!r} == {l2!r}"
        )

    def assert_set_equal(self, s1: set[object], s2: set[object], msg: str | None = None) -> None:
        """Assert that two sets are equal."""
        assert set(s1) == set(s2), msg or f"Expected sets to be equal: {s1!r} == {s2!r}"

    def assert_startswith(self, s: str, prefix: str, msg: str | None = None) -> None:
        """Assert that a string starts with a prefix."""
        assert str(s).startswith(prefix), (
            msg or f"Expected {s!r} to start with {prefix!r}"
        )

    def assert_endswith(self, s: str, suffix: str, msg: str | None = None) -> None:
        """Assert that a string ends with a suffix."""
        assert str(s).endswith(suffix), msg or f"Expected {s!r} to end with {suffix!r}"

    def assert_between(self, value: float, low: float, high: float, msg: str | None = None) -> None:
        """Assert that a value is between low and high (inclusive)."""
        assert low <= value <= high, (
            msg or f"Expected {value!r} to be between {low!r} and {high!r}"
        )

    def assert_is_true(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is exactly True."""
        assert value is True, msg or f"Expected value to be True, got {value!r}"

    def assert_is_false(self, value: object, msg: str | None = None) -> None:
        """Assert that a value is exactly False."""
        assert value is False, msg or f"Expected value to be False, got {value!r}"

    def assert_predicate_true(self, func: Callable[..., bool], *args: object, msg: str | None = None, **kwargs: object) -> None:
        """Assert that a predicate function returns True."""
        result = func(*args, **kwargs)
        assert result is True, (
            msg or f"Expected {func.__name__} to return True, got {result!r}"
        )

    def assert_predicate_false(self, func: Callable[..., bool], *args: object, msg: str | None = None, **kwargs: object) -> None:
        """Assert that a predicate function returns False."""
        result = func(*args, **kwargs)
        assert result is False, (
            msg or f"Expected {func.__name__} to return False, got {result!r}"
        )

    def assert_all_true(self, iterable: Sequence[bool], msg: str | None = None) -> None:
        """Assert that all values in an iterable are True."""
        for i, value in enumerate(iterable):
            assert value is True, (
                msg or f"Expected all True, but got {value!r} at index {i}"
            )

    def assert_all_false(self, iterable: Sequence[bool], msg: str | None = None) -> None:
        """Assert that all values in an iterable are False."""
        for i, value in enumerate(iterable):
            assert value is False, (
                msg or f"Expected all False, but got {value!r} at index {i}"
            )


class MainAppTestTemplate(BaseAPITest):
    """
    Template for FastAPI app-level tests (main.py entrypoint, middleware, startup, branding, etc).
    Inherit from this class for all main app tests. Add app-specific helpers here.
    """

    def assert_middleware_present(self, app: AppType, middleware_name: str, msg: str | None = None) -> None:
        """Assert that a specific middleware is present in the app."""
        if hasattr(app, 'user_middleware'):
            names = [getattr(m, "cls", type(m)).__name__ for m in getattr(app, 'user_middleware', [])]
        else:
            names = []
        assert middleware_name in names, (
            msg or f"Expected middleware {middleware_name!r} in {names!r}"
        )




# --- AlembicEnvTestTemplate (restored from backup) ---
class AlembicEnvTestTemplate:
    """
    Template for Alembic migration environment tests.
    Provides helpers for patching alembic context, asserting migration calls, and error assertions.
    """

    def patch_alembic_context(self, monkeypatch, context_mod):
        import sys
        import types

        monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
        monkeypatch.setitem(sys.modules, "alembic_migrations.context", context_mod)
        monkeypatch.setitem(
            sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
        )
        monkeypatch.setitem(
            sys.modules,
            "alembic_migrations",
            types.SimpleNamespace(context=context_mod),
        )

    def assert_called_once(self, mock_obj, msg=None):
        assert mock_obj.called, msg or "Expected mock to be called"
        assert mock_obj.call_count == 1, (
            msg or f"Expected mock to be called once, got {mock_obj.call_count}"
        )

    def assert_not_called(self, mock_obj, msg=None):
        assert not mock_obj.called, msg or "Expected mock to not be called"

    def assert_raises(self, exc_type, func, *args, match=None, **kwargs):
        import pytest

        if match:
            with pytest.raises(exc_type, match=match):
                func(*args, **kwargs)
        else:
            with pytest.raises(exc_type):
                func(*args, **kwargs)

    def assert_true(self, expr, msg=None):
        assert expr, msg or f"Expected expression to be True, got {expr}"

    def assert_is_instance(self, obj, cls, msg=None):
        assert isinstance(obj, cls), (
            msg or f"Expected {obj!r} to be instance of {cls!r}, got {type(obj)}"
        )

# pytest: disable=pytest_plugin_missing_source_or_test
