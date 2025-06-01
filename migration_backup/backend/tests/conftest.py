# type: ignore

import os
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from loguru import logger as loguru_logger

# type: ignore[attr-defined]
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.models.base import Base

# Use a real test database file instead of in-memory
TEST_DB_URL = "sqlite+aiosqlite:///test.db"  # Or use your test Postgres URL

os.environ["REVIEWPOINT_DB_URL"] = TEST_DB_URL
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"

DATABASE_URL = TEST_DB_URL


@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch):
    monkeypatch.setenv("REVIEWPOINT_DB_URL", TEST_DB_URL)
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_local = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session


# Cleanup fixture: truncate all tables after each test for isolation
@pytest_asyncio.fixture(autouse=True, scope="function")
async def cleanup_db(async_engine):
    yield
    async with async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(autouse=True, scope="session")
def loguru_to_standard_logging():
    import logging

    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    loguru_logger.remove()
    loguru_logger.add(PropagateHandler(), format="{message}")
    yield
    loguru_logger.remove()


@pytest.fixture
def loguru_list_sink():
    """Fixture to capture loguru logs in a list for assertions."""
    logs = []
    sink_id = loguru_logger.add(logs.append, format="{message}")
    yield logs
    loguru_logger.remove(sink_id)
