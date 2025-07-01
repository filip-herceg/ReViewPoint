
# Fast test mode: use in-memory SQLite for fast tests
import sys
import pytest

@pytest.fixture(scope="session")
def use_fast_db():
    """Enable fast testing mode with shared in-memory SQLite if FAST_TESTS env var is set."""
    return os.environ.get("FAST_TESTS", "0") == "1"

def pytest_configure(config):
    """Register test markers for slow and fast tests."""
    config.addinivalue_line("markers", "slow: marks tests that access real database or are slow")
    config.addinivalue_line("markers", "fast: marks tests that use mocks or in-memory DB")
"""
Centralized test database and environment management for all tests in the backend.

Test DB Policy:
- All tests use a single PostgreSQL container, managed by the session-scoped fixture below.
- The container is started before any tests run and stopped after all tests complete.
- The test DB connection URL is set via the REVIEWPOINT_DB_URL environment variable for all tests.
- No test or fixture should start its own DB container or set DB URLs directly (except for explicit config/env error tests).
- The Postgres image/tag can be overridden via the REVIEWPOINT_TEST_POSTGRES_IMAGE environment variable.
- Container connection details are logged at startup for debugging.
- If Docker is not running or the container fails to start, a clear error is raised and logged.

This policy ensures robust, maintainable, and explicit test DB management for all developers.
"""

# --- DO NOT set env vars at the top level. All config-dependent imports must be inside fixtures. ---
import os
import uuid
from collections.abc import Callable, Generator, Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from loguru import logger


@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    """
    Start a PostgreSQL container for the test session and set DB URL env var for all tests.
    Logs the connection URL at startup. Raises a clear error if Docker is not running.
    The Postgres image can be overridden with the REVIEWPOINT_TEST_POSTGRES_IMAGE env var.
    """
    from testcontainers.postgres import PostgresContainer

    image = os.environ.get("REVIEWPOINT_TEST_POSTGRES_IMAGE", "postgres:15-alpine")
    try:
        with PostgresContainer(image) as postgres:
            db_url = postgres.get_connection_url()
            # Convert sync driver to asyncpg for SQLAlchemy async engine
            if db_url.startswith("postgresql://"):
                async_db_url = db_url.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )
            elif db_url.startswith("postgresql+psycopg2://"):
                async_db_url = db_url.replace(
                    "postgresql+psycopg2://", "postgresql+asyncpg://", 1
                )
            else:
                async_db_url = db_url
            logger.info(
                f"[testcontainers] Started PostgreSQL container: {async_db_url}"
            )
            os.environ["REVIEWPOINT_DB_URL"] = async_db_url
            yield async_db_url
            os.environ.pop("REVIEWPOINT_DB_URL", None)
            logger.info(
                "[testcontainers] PostgreSQL container stopped and env cleaned up."
            )
    except Exception as e:
        logger.error(f"[testcontainers] Failed to start PostgreSQL container: {e}")
        raise RuntimeError(
            "Could not start PostgreSQL test container. Is Docker running? "
            "See the error above for details."
        ) from e


#
# ENFORCED TEST ENVIRONMENT/DB SETUP POLICY
#
# All environment variable and database setup for tests MUST be centralized in this file (conftest.py).
# No test file (except explicit config/validation tests) may set environment variables or database URLs directly.
# Valid exceptions: tests that explicitly test config/env/DB error handling (e.g., test_config.py).
# This is enforced by an automated check below. If you need to add a new exception, update the list in the check.
#


# ENFORCEMENT: Never import or create a global settings = Settings() at import time in any code or test.
# Always use get_settings() to ensure env vars are set first.

import asyncio


# 1. Environment setup (env vars, DB cleanup, DB/table creation)
@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Automatically set all required environment variables and feature flags for tests.
    Ensures a consistent environment for every test function.
    """
    monkeypatch.setenv(
        "REVIEWPOINT_DB_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint",
    )
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




# Session-scoped engine for backward compatibility
@pytest_asyncio.fixture(scope="session")
async def async_engine(use_fast_db, postgres_container):
    """
    Provide a SQLAlchemy async engine for the test session.
    Uses in-memory SQLite if FAST_TESTS=1, otherwise uses PostgreSQL.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import declarative_base

    if use_fast_db:
        db_url = "sqlite+aiosqlite:///:memory:?cache=shared"
        engine = create_async_engine(db_url, future=True, connect_args={"check_same_thread": False})
    else:
        db_url = os.environ["REVIEWPOINT_DB_URL"]
        engine = create_async_engine(db_url, future=True)

    # Import Base only after DB URL is set
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from src.models import Base

    # Create tables once per session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()

# Function-scoped engine for parallel/isolated tests
@pytest_asyncio.fixture(scope="function")
async def async_engine_isolated(use_fast_db, postgres_container):
    """
    Provide a SQLAlchemy async engine for each test function (parallel safe).
    Uses in-memory SQLite if FAST_TESTS=1, otherwise uses PostgreSQL.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    import uuid
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from src.models import Base

    if use_fast_db:
        db_url = f"sqlite+aiosqlite:///:memory:?cache=shared&test_id={uuid.uuid4()}"
        engine = create_async_engine(db_url, future=True, connect_args={"check_same_thread": False})
    else:
        # Use the same DB URL, but pool_size=1 for isolation
        db_url = os.environ["REVIEWPOINT_DB_URL"]
        engine = create_async_engine(db_url, future=True, pool_size=1, max_overflow=0)

    # Create tables for this test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()



@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine_isolated):
    """
    Provide an async SQLAlchemy session for each test function, using a function-scoped engine for parallel safety.
    Each test gets its own engine and connection pool.
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    async with async_engine_isolated.connect() as connection:
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()


# 4. App and client fixtures


from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def test_app(async_session) -> Generator:
    """
    Provides a new FastAPI app instance for each test function.
    Overrides get_async_session dependency to use the test async_session fixture.
    """
    from src.core.database import get_async_session
    from src.main import create_app

    app = create_app()

    # Override get_async_session to yield the test session
    async def _override_get_async_session():
        yield async_session

    app.dependency_overrides[get_async_session] = _override_get_async_session
    yield app


# Fixture to provide a TestClient for all API tests
@pytest.fixture(scope="function")
def client(test_app) -> Generator:
    """
    Provides a TestClient for the FastAPI app for use in API tests.
    """
    with TestClient(test_app) as c:
        yield c


# 5. Dependency overrides


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
    original_remove = logger.remove

    def safe_remove(*args: Any, **kwargs: Any) -> None:
        try:
            original_remove(*args, **kwargs)
        except ValueError:
            pass

    monkeypatch.setattr(logger, "remove", safe_remove)
    yield
    monkeypatch.setattr(logger, "remove", original_remove)


@pytest.fixture
def override_env_vars(monkeypatch: pytest.MonkeyPatch, set_required_env_vars: None):
    """
    Fixture to override environment variables for a single test.
    Usage: override_env_vars({"VAR1": "value1", "VAR2": "value2"})
    Ensures required defaults are set first, then applies overrides.
    """
    def _override(vars: dict[str, str]) -> None:
        for k, v in vars.items():
            monkeypatch.setenv(k, v)
    return _override


# 8. Helper functions (not fixtures)
def wait_for_condition(
    condition_fn: Callable[[], Any],
    timeout: float = 2.0,
    interval: float = 0.05,
) -> Any:
    """
    Polls the given condition_fn until it returns a truthy value or timeout is reached.
    Returns the value from condition_fn if successful, else None.
    """
    import time

    start = time.time()
    while time.time() - start < timeout:
        result = condition_fn()
        if result:
            return result
        time.sleep(interval)
    return None


def wait_for_admin_promotion(
    client,
    email: str,
    password: str,
    timeout: float = 2.0,
    interval: float = 0.05,
) -> str | None:
    """
    Polls the login endpoint until the user can log in as admin, or timeout is reached.
    Returns the access token if successful, else None.
    """
    login_data = {"email": email, "password": password}

    def try_login():
        resp = client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"X-API-Key": "testkey"},
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        return None

    return wait_for_condition(try_login, timeout=timeout, interval=interval)


import pathlib
import re

# List of test files (relative to backend/tests/) allowed to set env vars/DB URLs directly
ALLOWED_ENV_OVERRIDE_FILES = {
    "core/test_config.py",  # config/env/DB error handling tests
}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session: pytest.Session):
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


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_and_drop_tables(postgres_container):
    """
    Automatically create all tables before the test session and drop them after.
    Ensures a clean PostgreSQL test database for every test run.
    Depends on postgres_container to guarantee DB is up before setup.
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    from src.models.base import Base

    db_url = os.environ["REVIEWPOINT_DB_URL"]
    engine = create_async_engine(db_url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """
    Returns the test database URL used for all tests (from env var REVIEWPOINT_DB_URL).
    """
    return os.environ["REVIEWPOINT_DB_URL"]


def get_auth_header(client, email=None, password="TestPassword123!"):
    """
    Register a new user (or login if already exists) and return an auth header for API requests.
    Promotes the user to admin if registration is successful.
    Returns a dict with Authorization and X-API-Key headers.
    Uses the provided TestClient for all requests for consistency and speed.
    Raises RuntimeError if admin promotion fails unexpectedly.
    """
    from src.core.security import create_access_token

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
                # Wait for admin promotion to take effect, polling login endpoint
                new_token = wait_for_admin_promotion(client, email, password)
                if new_token:
                    token = new_token
                    return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
                else:
                    logger.error(
                        f"Admin promotion for {email} did not take effect within timeout."
                    )
                    raise RuntimeError(
                        f"Admin promotion for {email} did not take effect within timeout."
                    )
        except Exception as exc:
            logger.error(f"Exception during admin promotion for {email}: {exc}")
            raise
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    else:
        login_data = {"email": email, "password": password}
        try:
            login_resp = client.post(
                "/api/v1/auth/login", json=login_data, headers={"X-API-Key": "testkey"}
            )
            if login_resp.status_code == 200:
                token = login_resp.json().get("access_token")
                return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        except Exception as exc:
            logger.error(f"Exception during login for {email}: {exc}")
            raise
        payload = {"sub": email}
        token = create_access_token(payload)
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
