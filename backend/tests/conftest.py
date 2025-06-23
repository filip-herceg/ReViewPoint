import os

# Set environment variables at the very top to avoid Pydantic config errors
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Set required env vars before any other imports
os.environ["REVIEWPOINT_DB_URL"] = (
    os.environ.get("REVIEWPOINT_DB_URL") or "sqlite+aiosqlite:///:memory:"
)
os.environ["REVIEWPOINT_JWT_SECRET"] = (
    os.environ.get("REVIEWPOINT_JWT_SECRET") or "testsecret"
)

import asyncio
from collections.abc import AsyncGenerator, Generator, Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from loguru import logger
from loguru import logger as _loguru_logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.database import get_async_session
from src.main import app
from src.models.base import Base

# Remove all handlers at module level to start clean
# logger.remove()

# Use a file-based SQLite DB for all tests
TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.db"))
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["REVIEWPOINT_DB_URL"] = TEST_DB_URL
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "false"

DATABASE_URL = TEST_DB_URL


@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVIEWPOINT_DB_URL", TEST_DB_URL)
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")
    monkeypatch.setenv("REVIEWPOINT_API_KEY_ENABLED", "false")


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_URL, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async_session_local = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session


@pytest.fixture
def loguru_list_sink() -> Iterator[list[str]]:
    """Fixture to capture loguru logs in a list for assertions."""
    logs: list[str] = []
    sink_id = logger.add(logs.append, format="{message}")
    yield logs
    try:
        logger.remove(sink_id)
    except ValueError:
        pass


@pytest.fixture
def loguru_sink(tmp_path: Path) -> Iterator[Path]:
    """Create a log file for capturing loguru logs during tests."""
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


# Clean up the test DB file before and after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db_file(request: pytest.FixtureRequest) -> None:
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


# Ensure the test DB schema is created after DB file cleanup and before
# any test runs
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db_tables(
    cleanup_test_db_file: None, async_engine: AsyncEngine
) -> None:
    # Import all models to register them with Base metadata

    # Create tables using the async engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def override_get_async_session(
    async_session: AsyncSession,
) -> Generator[None, None, None]:
    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.pop(get_async_session, None)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a new event loop for each test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def patch_loguru_remove(monkeypatch: Any) -> Generator[None, None, None]:
    """Patch loguru's logger.remove to suppress ValueError during pytest-loguru teardown."""
    original_remove = _loguru_logger.remove

    def safe_remove(*args: Any, **kwargs: Any) -> None:
        try:
            original_remove(*args, **kwargs)
        except ValueError:
            pass

    monkeypatch.setattr(_loguru_logger, "remove", safe_remove)
    yield
    monkeypatch.setattr(_loguru_logger, "remove", original_remove)
