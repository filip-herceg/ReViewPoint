import asyncio
import logging
import os
from collections.abc import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from loguru import logger as loguru_logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.models.base import Base

# Use a file-based SQLite DB for all tests
TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.db"))
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["REVIEWPOINT_DB_URL"] = TEST_DB_URL
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"

DATABASE_URL = TEST_DB_URL


@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVIEWPOINT_DB_URL", TEST_DB_URL)
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_URL, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session_local = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session


@pytest.fixture(autouse=True, scope="session")
def loguru_to_standard_logging() -> Iterator[None]:
    class PropagateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)
    loguru_logger.remove()
    loguru_logger.add(PropagateHandler(), format="{message}")
    yield
    loguru_logger.remove()


@pytest.fixture
def loguru_list_sink() -> Iterator[list[str]]:
    """Fixture to capture loguru logs in a list for assertions."""
    logs: list[str] = []
    sink_id = loguru_logger.add(logs.append, format="{message}")
    yield logs
    loguru_logger.remove(sink_id)


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


@pytest.fixture(scope="session", autouse=True)
def create_test_db_tables() -> None:

    # Use a synchronous engine to create tables
    sync_engine = create_engine(f"sqlite:///{TEST_DB_PATH}")
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()
    # Optionally, check tables in DB (can be removed if not needed)
    # import aiosqlite
    # async def log_tables():
    #     try:
    #         async with aiosqlite.connect(TEST_DB_PATH) as db:
    #             cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #             tables = await cursor.fetchall()
    #     except Exception:
    #         pass
    # asyncio.get_event_loop().run_until_complete(log_tables())
