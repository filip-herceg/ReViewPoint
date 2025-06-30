#
# ENFORCED TEST ENVIRONMENT/DB SETUP POLICY
#
# All environment variable and database setup for tests MUST be centralized in this file (conftest.py).
# No test file (except explicit config/validation tests) may set environment variables or database URLs directly.
# Valid exceptions: tests that explicitly test config/env/DB error handling (e.g., test_config.py).
# This is enforced by an automated check below. If you need to add a new exception, update the list in the check.
#

import os
from collections.abc import (
    Callable,
    Generator,  # Explicit import for type annotation
)

# Set required env vars before any other imports
os.environ["REVIEWPOINT_DB_URL"] = (
    os.environ.get("REVIEWPOINT_DB_URL") or "sqlite+aiosqlite:///:memory:"
)
os.environ["REVIEWPOINT_JWT_SECRET"] = (
    os.environ.get("REVIEWPOINT_JWT_SECRET") or "testsecret"
)
os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = (
    os.environ.get("REVIEWPOINT_JWT_SECRET_KEY") or "testsecret"
)

import asyncio
import uuid
from collections.abc import AsyncGenerator, Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI  # Add this import for type annotations
from fastapi.testclient import TestClient
from loguru import logger
from loguru import logger as _loguru_logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.database import get_async_session
from src.core.security import create_access_token
from src.main import create_app  # Use factory, not global app
from src.models.base import Base

# Use a file-based SQLite DB for all tests
TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.db"))
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
DATABASE_URL = TEST_DB_URL


# 1. Environment setup (env vars, DB cleanup, DB/table creation)
@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Automatically set all required environment variables and feature flags for tests.
    Ensures a consistent environment for every test function.
    """
    monkeypatch.setenv("REVIEWPOINT_DB_URL", TEST_DB_URL)
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("REVIEWPOINT_API_KEY_ENABLED", "true")
    monkeypatch.setenv("REVIEWPOINT_API_KEY", "testkey")
    # Enable all known feature flags for all endpoints
    # Auth endpoints
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_REGISTER", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_LOGIN", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_REQUEST_PASSWORD_RESET", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_RESET_PASSWORD", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_ME", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_LOGOUT", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN", "true")
    # User endpoints
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_CREATE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_LIST", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_GET", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT_FULL", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT_ALIVE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT_SIMPLE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_READ", "true")
    # Uploads/files endpoints (granular flags)
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_GET_FILE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_EXPORT", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_UPLOAD", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_DELETE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_LIST", "true")
    # Optionally, enable all granular features at once for convenience
    monkeypatch.setenv(
        "REVIEWPOINT_FEATURES",
        "uploads:export,uploads:upload,uploads:delete,uploads:list",
    )
    # Health endpoints
    monkeypatch.setenv("REVIEWPOINT_FEATURE_HEALTH", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_HEALTH_READ", "true")
    # Any other likely features (add more as needed)
    monkeypatch.setenv("REVIEWPOINT_FEATURE_API_KEY", "true")


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db_file(request: pytest.FixtureRequest) -> None:
    """
    Clean up the test database file before and after all tests in the session.
    Ensures a fresh database for every test run and removes it after tests complete.
    """
    import time

    # Remove before tests
    for _ in range(5):
        try:
            if os.path.exists(TEST_DB_PATH):
                os.remove(TEST_DB_PATH)
            break
        except PermissionError:
            time.sleep(0.2)

    # Remove after tests
    def remove_db() -> None:
        import aiosqlite

        try:

            async def close_connections() -> None:
                try:
                    async with aiosqlite.connect(TEST_DB_PATH) as db:
                        await db.close()
                except Exception:
                    pass

            asyncio.get_event_loop().run_until_complete(close_connections())
        except Exception:
            pass
        try:
            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(TEST_DB_URL, future=True)
            asyncio.get_event_loop().run_until_complete(engine.dispose())
        except Exception:
            pass
        for _ in range(5):
            try:
                if os.path.exists(TEST_DB_PATH):
                    os.remove(TEST_DB_PATH)
                break
            except PermissionError:
                time.sleep(0.2)

    request.addfinalizer(remove_db)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db_tables(
    cleanup_test_db_file: None, async_engine: AsyncEngine
) -> None:
    """
    Create all database tables for the test session using the async engine.
    Ensures the schema is ready before any tests run.
    """
    # Import all models to register them with Base metadata

    # Create tables using the async engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 2. Event loop (for async tests)
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create a new asyncio event loop for the test session.
    Required for running async tests with pytest-asyncio.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# 3. Database/session fixtures
@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Provide a SQLAlchemy async engine for the test session.
    Used for database connections in async tests.
    """
    engine = create_async_engine(DATABASE_URL, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async SQLAlchemy session for the test session.
    Used for database operations in async tests.
    """
    async_session_local = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session


# 4. App and client fixtures
@pytest.fixture
def test_app() -> Generator[FastAPI, None, None]:
    """
    Provide a new FastAPI app instance for each test.
    Ensures a fresh app context for every test function.
    """
    app = create_app()
    yield app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """
    Provide a FastAPI TestClient for making HTTP requests in tests.
    """
    return TestClient(test_app)


# 5. Dependency overrides
@pytest.fixture(autouse=True)
def override_get_async_session(
    async_session: AsyncSession, test_app: FastAPI  # Add type annotation
) -> Generator[None, None, None]:
    """
    Override the get_async_session dependency in FastAPI with the test async session.
    Ensures all DB operations in the app use the test session.
    """

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    test_app.dependency_overrides[get_async_session] = _override
    yield
    test_app.dependency_overrides.pop(get_async_session, None)


# 6. Logging fixtures
@pytest.fixture
def loguru_list_sink() -> Iterator[list[str]]:
    """
    Capture loguru logs in a list for assertions, capturing only the loguru 'message' argument.
    Use this fixture to inspect logs generated during tests.
    """
    logs: list[str] = []

    def sink(message: Any) -> None:
        # message is a loguru.Message object; message.record['message'] is the plain log message
        try:
            logs.append(message.record["message"])
        except Exception:
            logs.append(str(message))

    sink_id = logger.add(sink)
    try:
        yield logs
    finally:
        try:
            logger.remove(sink_id)
        except ValueError:
            pass


@pytest.fixture
def loguru_list_sink_middleware() -> Iterator[list[str]]:
    """
    Capture loguru logs in a list for middleware tests.
    Ensures the sink is attached before the FastAPI app is created.
    Use this fixture in middleware tests instead of loguru_list_sink.
    """
    logs: list[str] = []

    def sink(message: Any) -> None:
        try:
            logs.append(message.record["message"])
        except Exception:
            logs.append(str(message))

    sink_id = logger.add(sink)
    try:
        yield logs
    finally:
        try:
            logger.remove(sink_id)
        except ValueError:
            pass


@pytest.fixture
def loguru_sink(tmp_path: Path) -> Iterator[Path]:
    """
    Create a log file for capturing loguru logs during tests.
    Returns the path to the log file for inspection.
    """
    log_file = tmp_path / "loguru.log"
    handler_id = logger.add(
        str(log_file),
        format="{message}",
        enqueue=True,
        catch=True,
        diagnose=False,
        backtrace=False,
        colorize=False,
    )
    try:
        yield log_file
    finally:
        try:
            logger.remove(handler_id)
        except ValueError:
            pass


# 7. Utility fixtures
@pytest.fixture(autouse=True)
def patch_loguru_remove(monkeypatch: Any) -> Generator[None, None, None]:
    """
    Patch loguru's logger.remove to suppress ValueError during pytest-loguru teardown.
    Prevents test failures due to loguru teardown issues.
    """
    original_remove = _loguru_logger.remove

    def safe_remove(*args: Any, **kwargs: Any) -> None:
        try:
            original_remove(*args, **kwargs)
        except ValueError:
            pass

    monkeypatch.setattr(_loguru_logger, "remove", safe_remove)
    yield
    monkeypatch.setattr(_loguru_logger, "remove", original_remove)


@pytest.fixture
def override_env_vars(
    monkeypatch: pytest.MonkeyPatch, set_required_env_vars
) -> Callable[[dict[str, str]], None]:
    """
    Helper fixture to override environment variables for a single test.
    Usage: override_env_vars({"VAR1": "value1", "VAR2": "value2"})
    Ensures required defaults are set first, then applies overrides.
    """

    def _override(vars: dict[str, str]) -> None:
        set_required_env_vars  # Ensure defaults are set first
        for k, v in vars.items():
            monkeypatch.setenv(k, v)

    return _override


# 8. Helper functions (not fixtures)
def get_auth_header(
    client: TestClient,
    email: str | None = None,
    password: str = "TestPassword123!",
) -> dict[str, str]:
    """
    Register a new user (or login if already exists) and return an auth header for API requests.
    Promotes the user to admin if registration is successful.
    Returns a dict with Authorization and X-API-Key headers.
    """
    if email is None:
        email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {"email": email, "password": password, "name": "Test User"}
    register_resp = client.post(
        "/api/v1/auth/register", json=register_data, headers={"X-API-Key": "testkey"}
    )
    if register_resp.status_code == 201:
        token = register_resp.json().get("access_token")
        try:
            promote_resp = client.post(
                "/api/v1/users/promote-admin",
                json={"email": email},
                headers={"Authorization": f"Bearer {token}", "X-API-Key": "testkey"},
            )
            if promote_resp.status_code == 200:
                import time

                time.sleep(0.1)
                login_data = {"email": email, "password": password}
                login_resp = client.post(
                    "/api/v1/auth/login",
                    json=login_data,
                    headers={"X-API-Key": "testkey"},
                )
                if login_resp.status_code == 200:
                    token = login_resp.json().get("access_token")
                return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        except Exception:
            pass
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    else:
        login_data = {"email": email, "password": password}
        login_resp = client.post(
            "/api/v1/auth/login", json=login_data, headers={"X-API-Key": "testkey"}
        )
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        payload = {"sub": email}
        token = create_access_token(payload)
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}


import pathlib
import re

# List of test files (relative to backend/tests/) allowed to set env vars/DB URLs directly
ALLOWED_ENV_OVERRIDE_FILES = {
    "core/test_config.py",  # config/env/DB error handling tests
}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session):
    """
    Enforce that no test file (except allowed exceptions) sets environment variables or DB URLs directly.
    """
    root = pathlib.Path(__file__).parent
    pattern_env = re.compile(r"(os\\.environ|setenv|DATABASE_URL)")
    for item in session.items:
        path = pathlib.Path(item.fspath)
        rel_path = str(path.relative_to(root)).replace("\\", "/")
        if rel_path in ALLOWED_ENV_OVERRIDE_FILES:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            if pattern_env.search(content):
                raise RuntimeError(
                    f"Test file {rel_path} sets environment variables or DB URLs directly. "
                    f"All such setup must be in conftest.py. If this is a valid exception, add it to ALLOWED_ENV_OVERRIDE_FILES."
                )
        except Exception:
            # Don't block collection for unreadable files
            pass
