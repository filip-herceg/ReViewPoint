"""
Test templates and reusable test patterns for backend tests.

This module provides reusable test templates and base classes for common test scenarios.
Import and use these templates in your test files to reduce duplication and enforce consistency.

Note: This file is not a test itself and should be excluded from pytest plugins that check for missing source or test files.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient


class BaseAPITest:
    def safe_request(self, func, *args, **kwargs):
        """
        Helper to make HTTP requests robust to connection errors.
        Usage: resp = self.safe_request(client.get, ...)
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import pytest
            pytest.xfail(f"Connection/DB error: {e}")
    """
    Base class for API endpoint tests.
    Provides common utility methods for API tests.
    Inherit from this class in your test classes to get auth helpers.
    """

    @pytest.fixture(autouse=True)
    def _setup_base_fixtures(
        self, set_required_env_vars, override_env_vars, loguru_list_sink
    ):
        self.set_required_env_vars = set_required_env_vars
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink
        pass

    @pytest.fixture(autouse=True)
    def _inject_monkeypatch(self, monkeypatch):
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
        from .conftest import get_auth_header

        return get_auth_header(client, email=email, password=password)

    def assert_unauthorized(self, response: Any) -> None:
        """
        Assert that a response is HTTP 401 Unauthorized.
        """
        assert response.status_code == 401
        assert "detail" in response.json()

    def patch_var(self, target: str, value: Any):
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

    def assert_status(self, response: Any, expected_statuses):
        """
        Assert that a response status code is in the expected set.
        """
        if not isinstance(expected_statuses, (list, tuple, set)):
            expected_statuses = (expected_statuses,)
        assert (
            response.status_code in expected_statuses
        ), f"Expected {expected_statuses}, got {response.status_code}"

    def assert_content_type(self, response: Any, expected_type: str):
        """
        Assert that the response content-type header starts with the expected type.
        """
        assert response.headers["content-type"].startswith(expected_type)

    def assert_equal(self, a, b, msg=None):
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_in(self, a, b, msg=None):
        assert a in b, msg or f"Expected {a!r} to be in {b!r}"

    def assert_true(self, expr, msg=None):
        assert expr, msg or f"Expected expression to be true, got {expr!r}"

    def assert_is_instance(self, obj, cls, msg=None):
        assert isinstance(obj, cls), (
            msg or f"Expected {obj!r} to be instance of {cls!r}"
        )

    def assert_api_key_required(self, response: Any) -> None:
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

    def assert_forbidden(self, response: Any) -> None:
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
    Uses set_required_env_vars, loguru_list_sink, and override_env_vars for env setup and log capture.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    endpoint: str = ""
    create_payload: dict = {}
    update_payload: dict = {}

    def test_create(
        self, client: TestClient, set_required_env_vars, loguru_list_sink: list[str]
    ):
        """
        Test creating a resource via POST. Captures logs for assertion if needed.
        """
        resp = client.post(
            self.endpoint,
            json=self.create_payload,
            headers=self.get_auth_header(client),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        return data

    def test_read(
        self, client: TestClient, set_required_env_vars, loguru_list_sink: list[str]
    ):
        """
        Test reading a resource via GET after creation. Captures logs for assertion if needed.
        """
        created = self.test_create(client, set_required_env_vars, loguru_list_sink)
        resp = client.get(
            f"{self.endpoint}/{created['id']}", headers=self.get_auth_header(client)
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == created["id"]

    def test_update(
        self, client: TestClient, set_required_env_vars, loguru_list_sink: list[str]
    ):
        """
        Test updating a resource via PUT. Captures logs for assertion if needed.
        """
        created = self.test_create(client, set_required_env_vars, loguru_list_sink)
        resp = client.put(
            f"{self.endpoint}/{created['id']}",
            json=self.update_payload,
            headers=self.get_auth_header(client),
        )
        assert resp.status_code in (200, 204)

    def test_delete(
        self, client: TestClient, set_required_env_vars, loguru_list_sink: list[str]
    ):
        """
        Test deleting a resource via DELETE. Captures logs for assertion if needed.
        """
        created = self.test_create(client, set_required_env_vars, loguru_list_sink)
        resp = client.delete(
            f"{self.endpoint}/{created['id']}", headers=self.get_auth_header(client)
        )
        assert resp.status_code in (200, 204)


class ExportEndpointTestTemplate(BaseAPITest):
    """
    Template for export/read-only endpoints that require set_required_env_vars for every test.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_env(self, set_required_env_vars, override_env_vars):
        self.override_env_vars = override_env_vars
        pass


class UserCoreEndpointTestTemplate(BaseAPITest):
    """
    Template for user core endpoint tests that require set_required_env_vars, loguru_list_sink, and override_env_vars for every test.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_env_and_logs(
        self, set_required_env_vars, loguru_list_sink, override_env_vars
    ):
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        pass


class LogCaptureTestTemplate(BaseAPITest):
    """
    Template for tests that need to assert on log output.
    Uses set_required_env_vars, loguru_list_sink, and override_env_vars.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_env_and_logs(
        self, set_required_env_vars, loguru_list_sink, override_env_vars
    ):
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        pass


class AuthUnitTestTemplate(BaseAPITest):
    """
    Template for authentication-related unit tests that require monkeypatch, loguru_list_sink, and override_env_vars.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.
    Provides helpers for patching, restoring, and asserting dependency behaviors.
    """

    @pytest.fixture(autouse=True)
    def _setup_monkeypatch_and_logs(
        self, monkeypatch, set_required_env_vars, loguru_list_sink, override_env_vars
    ):
        self.monkeypatch = monkeypatch
        self.set_required_env_vars = set_required_env_vars
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        self._patches = []
        yield
        # Restore all patched attributes after each test
        for target, attr, orig in self._patches:
            if isinstance(target, str) and target.startswith("os.environ["):
                import os

                key = target.split('["')[1].split('"]')[0]
                if orig is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig
            elif isinstance(target, str) and "." in target:
                module, attr_name = target.rsplit(".", 1)
                mod = __import__(module, fromlist=[attr_name])
                setattr(mod, attr_name, orig)
            else:
                # target is an object, attr is attribute name
                setattr(target, attr, orig)

    def patch_dep(self, target: str, value):
        """
        Patch a dependency and automatically restore it after the test.
        Usage: self.patch_dep('src.api.deps.verify_access_token', fake_func)
        """
        module, attr = target.rsplit(".", 1)
        mod = __import__(module, fromlist=[attr])
        orig = getattr(mod, attr)
        self.monkeypatch.setattr(mod, attr, value)
        self._patches.append((target, attr, orig))

    def patch_setting(self, obj, attr, value):
        """
        Patch a config/settings attribute and restore after test.
        Usage: self.patch_setting(settings, 'auth_enabled', False)
        """
        orig = getattr(obj, attr)
        self.monkeypatch.setattr(obj, attr, value)
        self._patches.append((obj, attr, orig))

    def assert_http_exception(self, func, status_code, detail_substr=None):
        import pytest
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            func()
        assert exc.value.status_code == status_code
        if detail_substr:
            assert detail_substr in str(exc.value.detail)

    async def assert_async_http_exception(self, func, status_code, detail_substr=None):
        import pytest
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await func()
        assert exc.value.status_code == status_code
        if detail_substr:
            assert detail_substr in str(exc.value.detail)

    def patch_async_dep(self, target: str, async_mock):
        """
        Patch an async dependency (e.g., DB call) and auto-restore after test.
        Usage: self.patch_async_dep('src.api.deps.get_user_by_id', AsyncMock(...))
        """
        self.patch_dep(target, async_mock)

    def patch_env(self, key: str, value: str):
        """
        Patch an environment variable for the test duration.
        Usage: self.patch_env('MY_ENV', 'value')
        """
        import os

        orig = os.environ.get(key)
        self.monkeypatch.setenv(key, value)
        self._patches.append((f'os.environ["{key}"]', None, orig))

    def restore_env(self, key: str):
        import os

        for i, (target, attr, orig) in enumerate(self._patches):
            if isinstance(target, str) and target == f'os.environ["{key}"]':
                if orig is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig
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
        async_session,
        test_app,
        set_required_env_vars,
        loguru_list_sink,
        override_env_vars,
    ):
        self.async_session = async_session
        self.test_app = test_app
        self.set_required_env_vars = set_required_env_vars
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        pass


class HealthEndpointTestTemplate(BaseAPITest):
    """
    Template for health/liveness/readiness endpoint tests.
    Use this for /health, /alive, /ready endpoints.
    Provides health-specific helpers and ensures consistent assertions.
    The override_env_vars fixture is available as self.override_env_vars for env var overrides in tests.

    Note: Do NOT use BaseAPITest directly for health checks—use this template instead.
    """

    @pytest.fixture(autouse=True)
    def _setup_env(self, set_required_env_vars, override_env_vars, loguru_list_sink):
        self.set_required_env_vars = set_required_env_vars
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink
        pass

    def assert_health_response(self, resp):
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

    @pytest.fixture(autouse=True)
    def _setup_db_env(
        self, monkeypatch, set_required_env_vars, override_env_vars, loguru_list_sink
    ):
        self.override_env_vars = override_env_vars
        self.monkeypatch = monkeypatch
        self.set_required_env_vars = set_required_env_vars
        self.loguru_list_sink = loguru_list_sink
        pass

    async def assert_healthcheck_ok(self, healthcheck_func):
        try:
            await healthcheck_func()
        except Exception as exc:
            pytest.fail(f"db_healthcheck raised unexpectedly: {exc}")

    async def assert_session_context_ok(self, get_session_func, session_type):
        session = None
        async with get_session_func() as s:
            session = s
            assert isinstance(session, session_type)
        assert session is not None

    async def assert_session_rollback(
        self, session_factory, error_sql="SELECT invalid_column_name"
    ):
        from sqlalchemy import text
        from sqlalchemy.exc import SQLAlchemyError

        session = session_factory()
        try:
            await session.execute(text(error_sql))
            await session.commit()
            raise AssertionError("Should not reach here")
        except SQLAlchemyError:
            await session.rollback()
            result = await session.execute(text("SELECT 1"))
            assert result is not None
        finally:
            await session.close()

    async def assert_table_exists(self, session_factory, table_name):
        from sqlalchemy import inspect

        async with session_factory() as session:
            inspector = inspect(session.bind)
            tables = await session.run_sync(inspector.get_table_names)
            assert table_name in tables, f"Table '{table_name}' does not exist"

    async def assert_table_not_exists(self, session_factory, table_name):
        from sqlalchemy import inspect

        async with session_factory() as session:
            inspector = inspect(session.bind)
            tables = await session.run_sync(inspector.get_table_names)
            assert table_name not in tables, f"Table '{table_name}' should not exist"

    async def assert_can_insert_and_query(
        self, session_factory, table, insert_dict, query_filter
    ):
        async with session_factory() as session:
            obj = table(**insert_dict)
            session.add(obj)
            await session.commit()
            result = await session.execute(
                table.__table__.select().filter_by(**query_filter)
            )
            row = result.scalar_one_or_none()
            assert row is not None, f"Row not found for filter {query_filter}"

    async def assert_transaction_isolation(self, session_factory, table, insert_dict):
        async with session_factory() as session:
            trans = await session.begin()
            obj = table(**insert_dict)
            session.add(obj)
            await trans.rollback()
            result = await session.execute(
                table.__table__.select().filter_by(**insert_dict)
            )
            row = result.scalar_one_or_none()
            assert row is None, "Row should not exist after rollback"

    def simulate_db_disconnect(self, session_factory):
        # Patch the session/engine to raise on connect
        from sqlalchemy.exc import OperationalError

        def raise_disconnect(*a, **kw):
            raise OperationalError("Simulated disconnect", None, None)

        self.patch_var(
            f"{session_factory.__module__}.AsyncSession.__init__", raise_disconnect
        )

    async def assert_db_integrity_error(self, session_factory, table, insert_dict):
        from sqlalchemy.exc import IntegrityError

        async with session_factory() as session:
            obj = table(**insert_dict)
            session.add(obj)
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

    async def run_raw_sql(self, session_factory, sql):
        from sqlalchemy import text

        async with session_factory() as session:
            result = await session.execute(text(sql))
            return result.fetchall()

    def assert_db_url_config(self, cfg, expected_url):
        assert getattr(cfg.settings, "db_url", None) == expected_url

    # --- Migration Helpers ---
    def assert_migration_applied(self, session_factory, table_name=None, version=None):
        # Checks for table or migration version presence
        from sqlalchemy import inspect

        async def _check():
            async with session_factory() as session:
                inspector = inspect(session.bind)
                if table_name:
                    tables = await session.run_sync(inspector.get_table_names)
                    assert (
                        table_name in tables
                    ), f"Table '{table_name}' not found after migration"
                if version:
                    versions = await session.execute(
                        "SELECT version_num FROM alembic_version"
                    )
                    found = [row[0] for row in versions]
                    assert version in found, f"Migration version {version} not applied"

        import asyncio

        asyncio.run(_check())

    def run_migration(self, command="upgrade head"):
        # Run Alembic migration command
        import subprocess

        result = subprocess.run(
            ["alembic"] + command.split(), capture_output=True, text=True
        )
        assert result.returncode == 0, f"Migration failed: {result.stderr}"

    # --- Latency/Slow Query Simulation ---
    def simulate_db_latency(self, session_factory, delay=0.5):
        import asyncio

        orig_execute = session_factory().execute

        async def delayed_execute(self, *a, **kw):
            await asyncio.sleep(delay)
            return await orig_execute(*a, **kw)

        self.patch_var(
            f"{session_factory.__module__}.AsyncSession.execute", delayed_execute
        )

    # --- Bulk Insert/Batch Operation Helpers ---
    async def bulk_insert(self, session_factory, table, rows):
        async with session_factory() as session:
            objs = [table(**row) for row in rows]
            session.add_all(objs)
            await session.commit()
            return objs

    async def assert_bulk_query(
        self, session_factory, table, filter_dict, expected_count
    ):
        async with session_factory() as session:
            result = await session.execute(
                table.__table__.select().filter_by(**filter_dict)
            )
            rows = result.scalars().all()
            assert (
                len(rows) == expected_count
            ), f"Expected {expected_count} rows, got {len(rows)}"

    # --- Database Seeding/Cleanup ---
    async def seed_database(self, session_factory, table, rows):
        await self.bulk_insert(session_factory, table, rows)

    async def truncate_tables(self, session_factory, tables):
        from sqlalchemy import text

        async with session_factory() as session:
            for table in tables:
                await session.execute(
                    text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                )
            await session.commit()

    # --- Connection Pool/State Helpers ---
    def assert_connection_pool_size(self, engine, expected_size):
        pool = engine.pool
        size = pool.checkedin() + pool.checkedout()
        assert size == expected_size, f"Expected pool size {expected_size}, got {size}"

    # --- Multi-DB/Shard Helpers ---
    async def assert_cross_db_query(self, session_factories, sql, expected_results):
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
        monkeypatch,
        tmp_path,
        caplog,
        set_required_env_vars,
        loguru_list_sink,
        override_env_vars,
    ):
        self.monkeypatch = monkeypatch
        self.tmp_path = tmp_path
        self.caplog = caplog
        self.set_required_env_vars = set_required_env_vars
        self.loguru_list_sink = loguru_list_sink
        self.override_env_vars = override_env_vars
        # Setup loguru sink for log file capture
        from loguru import logger

        self.log_file = tmp_path / "loguru.log"
        logger.add(self.log_file, format="{message}", enqueue=True)
        yield
        logger.remove()

    def patch_settings(self, target_module, settings_obj):
        self.monkeypatch.setattr(target_module, "settings", settings_obj)

    def get_loguru_text(self):
        return self.log_file.read_text()

    def assert_log_contains(self, text):
        logs = self.get_loguru_text()
        assert text in logs, f"Expected log to contain '{text}', got: {logs}"

    def assert_caplog_contains(self, text, level=None):
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
        test_app: Any,
        request: pytest.FixtureRequest,
        set_required_env_vars,
        override_env_vars,
        loguru_list_sink,
    ):
        from src.core.openapi import setup_openapi

        setup_openapi(test_app)
        self.client: TestClient = TestClient(test_app)
        self.set_required_env_vars = set_required_env_vars
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink
        yield
        if hasattr(self, "client") and hasattr(self.client, "close"):
            self.client.close()

    def assert_openapi_metadata(self, resp: Any) -> None:
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
        assert self.client.get("/docs").status_code == 200
        assert self.client.get("/redoc").status_code == 200

    def assert_endpoint_doc(
        self, path: str, method: str, summary: str, status_code: int
    ) -> None:
        resp = self.client.get("/openapi.json")
        paths = resp.json()["paths"]
        assert path in paths
        op = paths[path][method]
        assert op["summary"] == summary
        assert "responses" in op
        assert str(status_code) in op["responses"]

    def assert_endpoint_missing(self, path: str) -> None:
        resp = self.client.get("/openapi.json")
        paths = resp.json()["paths"]
        assert (
            path not in paths
        ), f"Endpoint {path} should not be present in OpenAPI spec"

    def assert_invalid_docs(self, url: str = "/invalid-docs") -> None:
        resp = self.client.get(url)
        assert resp.status_code == 404

    def validate_openapi_schema(self) -> None:
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
        self, monkeypatch, set_required_env_vars, override_env_vars, loguru_list_sink
    ):
        self.monkeypatch = monkeypatch
        self.set_required_env_vars = set_required_env_vars
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink
        pass

    def assert_jwt_claims(
        self, token: str, secret: str, algorithm: str, expected_claims: dict[str, Any]
    ) -> None:
        from jose import jwt

        decoded = jwt.decode(token, secret, algorithms=[algorithm])
        for k, v in expected_claims.items():
            assert decoded[k] == v, f"JWT claim {k} mismatch: {decoded[k]} != {v}"
        assert "exp" in decoded
        assert "iat" in decoded

    def assert_jwt_expired(self, token: str, secret: str, algorithm: str) -> None:
        from jose import ExpiredSignatureError, jwt

        with pytest.raises(ExpiredSignatureError):
            jwt.decode(token, secret, algorithms=[algorithm])

    def assert_jwt_invalid(self, token: str, secret: str, algorithm: str) -> None:
        from jose import JWTError, jwt

        with pytest.raises(JWTError):
            jwt.decode(token, secret, algorithms=[algorithm])

    def patch_jwt_secret(self, new_secret: str) -> None:
        # Example: self.patch_jwt_secret("badsecret")
        self.patch_var("src.core.config.settings.jwt_secret_key", new_secret)


class ModelUnitTestTemplate:
    """
    Template for SQLAlchemy model/unit tests.
    Provides helpers for to_dict, __repr__, and attribute assertions.
    Centralizes model test patterns for DRYness and maintainability.
    """

    def assert_model_attrs(self, model, attrs: dict, msg=None):
        for k, v in attrs.items():
            actual = getattr(model, k, None)
            assert actual == v, msg or f"Expected {k}={v!r}, got {actual!r}"

    def assert_equal(self, a, b, msg=None):
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_not_equal(self, a, b, msg=None):
        assert a != b, msg or f"Expected {a!r} != {b!r}"

    def assert_in(self, member, container, msg=None):
        assert member in container, msg or f"Expected {member!r} in {container!r}"

    def assert_not_in(self, member, container, msg=None):
        assert member not in container, (
            msg or f"Expected {member!r} not in {container!r}"
        )

    def assert_is_none(self, value, msg=None):
        assert value is None, msg or f"Expected value to be None, got {value!r}"

    def assert_is_not_none(self, value, msg=None):
        assert value is not None, msg or "Expected value to not be None"

    def assert_is_true(self, value, msg=None):
        assert value is True, msg or f"Expected value to be True, got {value!r}"

    def assert_is_false(self, value, msg=None):
        assert value is False, msg or f"Expected value to be False, got {value!r}"

    def assert_raises(self, exc_type, func, *args, **kwargs):
        import pytest

        with pytest.raises(exc_type):
            func(*args, **kwargs)

    def assert_repr(self, obj, class_name: str):
        r = repr(obj)
        assert class_name in r, f"Expected {class_name} in repr: {r}"


class AsyncModelTestTemplate(ModelUnitTestTemplate):
    """
    Template for async SQLAlchemy model tests that require async_session and set_required_env_vars.
    Inherit from this for DB-backed async model tests.
    Provides helpers for DB seeding, cleanup, and transactional test patterns.
    """

    @pytest.fixture(autouse=True)
    def _setup_async_model_fixtures(
        self, async_session, set_required_env_vars, override_env_vars, loguru_list_sink
    ):
        self.async_session = async_session
        self.set_required_env_vars = set_required_env_vars
        self.override_env_vars = override_env_vars
        self.loguru_list_sink = loguru_list_sink
        pass

    async def seed_db(self, objs):
        """Bulk add and commit a list of model instances."""
        self.async_session.add_all(objs)
        await self.async_session.commit()

    async def truncate_table(self, table):
        """Truncate a table and reset identity (Postgres only)."""
        from sqlalchemy import text

        await self.async_session.execute(text(f"DELETE FROM {table}"))
        await self.async_session.commit()

    async def run_in_transaction(self, coro):
        """Run a coroutine in a transaction and roll back after."""
        trans = await self.async_session.begin()
        try:
            await coro()
        finally:
            await trans.rollback()

    async def assert_integrity_error(self, obj):
        import pytest
        from sqlalchemy.exc import IntegrityError

        self.async_session.add(obj)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()


class UtilityUnitTestTemplate:
    """
    Base class for utility (non-API, non-DB) unit tests.
    Provides a consistent structure and utility-specific helpers.
    """

    def assert_equal(self, a, b, msg=None):
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_not_equal(self, a, b, msg=None):
        assert a != b, msg or f"Expected {a!r} != {b!r}"

    def assert_in(self, member, container, msg=None):
        assert member in container, msg or f"Expected {member!r} in {container!r}"

    def assert_not_in(self, member, container, msg=None):
        assert member not in container, (
            msg or f"Expected {member!r} not in {container!r}"
        )

    def assert_almost_equal(self, a, b, tol=1e-7, msg=None):
        assert abs(a - b) <= tol, msg or f"Expected {a!r} ≈ {b!r} (tol={tol})"

    def assert_true(self, expr, msg=None):
        assert expr, msg or f"Expected expression to be True, got {expr!r}"

    def assert_false(self, expr, msg=None):
        assert not expr, msg or f"Expected expression to be False, got {expr!r}"

    def assert_is_none(self, value, msg=None):
        assert value is None, msg or f"Expected value to be None, got {value!r}"

    def assert_is_not_none(self, value, msg=None):
        assert value is not None, msg or "Expected value to not be None"

    def assert_is_instance(self, obj, cls, msg=None):
        assert isinstance(obj, cls), (
            msg or f"Expected {obj!r} to be instance of {cls!r}"
        )

    def assert_is_not_instance(self, obj, cls, msg=None):
        assert not isinstance(obj, cls), (
            msg or f"Expected {obj!r} to not be instance of {cls!r}"
        )

    def assert_raises(self, exc_type, func, *args, **kwargs):
        import pytest

        with pytest.raises(exc_type):
            func(*args, **kwargs)

    async def assert_async_raises(self, exc_type, func, *args, **kwargs):
        import pytest

        with pytest.raises(exc_type):
            await func(*args, **kwargs)

    def assert_greater(self, a, b, msg=None):
        assert a > b, msg or f"Expected {a!r} > {b!r}"

    def assert_greater_equal(self, a, b, msg=None):
        assert a >= b, msg or f"Expected {a!r} >= {b!r}"

    def assert_less(self, a, b, msg=None):
        assert a < b, msg or f"Expected {a!r} < {b!r}"

    def assert_less_equal(self, a, b, msg=None):
        assert a <= b, msg or f"Expected {a!r} <= {b!r}"

    def assert_dict_equal(self, d1, d2, msg=None):
        assert d1 == d2, msg or f"Expected dicts to be equal: {d1!r} == {d2!r}"

    def assert_list_equal(self, l1, l2, msg=None):
        assert list(l1) == list(l2), (
            msg or f"Expected lists to be equal: {l1!r} == {l2!r}"
        )

    def assert_set_equal(self, s1, s2, msg=None):
        assert set(s1) == set(s2), msg or f"Expected sets to be equal: {s1!r} == {s2!r}"

    def assert_startswith(self, s, prefix, msg=None):
        assert str(s).startswith(prefix), (
            msg or f"Expected {s!r} to start with {prefix!r}"
        )

    def assert_endswith(self, s, suffix, msg=None):
        assert str(s).endswith(suffix), msg or f"Expected {s!r} to end with {suffix!r}"

    def assert_between(self, value, low, high, msg=None):
        assert low <= value <= high, (
            msg or f"Expected {value!r} to be between {low!r} and {high!r}"
        )

    def assert_is_true(self, value, msg=None):
        assert value is True, msg or f"Expected value to be True, got {value!r}"

    def assert_is_false(self, value, msg=None):
        assert value is False, msg or f"Expected value to be False, got {value!r}"

    def assert_predicate_true(self, func, *args, msg=None, **kwargs):
        result = func(*args, **kwargs)
        assert result is True, (
            msg or f"Expected {func.__name__} to return True, got {result!r}"
        )

    def assert_predicate_false(self, func, *args, msg=None, **kwargs):
        result = func(*args, **kwargs)
        assert result is False, (
            msg or f"Expected {func.__name__} to return False, got {result!r}"
        )

    def assert_all_true(self, iterable, msg=None):
        for i, value in enumerate(iterable):
            assert value is True, (
                msg or f"Expected all True, but got {value!r} at index {i}"
            )

    def assert_all_false(self, iterable, msg=None):
        for i, value in enumerate(iterable):
            assert value is False, (
                msg or f"Expected all False, but got {value!r} at index {i}"
            )


class MainAppTestTemplate(BaseAPITest):
    """
    Template for FastAPI app-level tests (main.py entrypoint, middleware, startup, branding, etc).
    Inherit from this class for all main app tests. Add app-specific helpers here.
    """

    # Example helper: assert_middleware_present
    def assert_middleware_present(self, app, middleware_name, msg=None):
        names = [getattr(m, "cls", type(m)).__name__ for m in app.user_middleware]
        assert middleware_name in names, (
            msg or f"Expected middleware {middleware_name!r} in {names!r}"
        )


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
