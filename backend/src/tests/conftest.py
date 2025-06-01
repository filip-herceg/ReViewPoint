import os
import uuid
from collections.abc import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from loguru import logger as loguru_logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.models.base import Base

os.environ["REVIEWPOINT_DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVIEWPOINT_DB_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[object, None]:
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_engine_function() -> AsyncGenerator[AsyncEngine, None]:
    # Use a unique in-memory database for each test function
    db_url = f"sqlite+aiosqlite:///:memory:?cache=shared_{uuid.uuid4()}"
    engine = create_async_engine(db_url, future=True)
    # Drop all tables and indexes before each test function to ensure a clean
    # state
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.reflect)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(
    async_engine_function: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async_session_local: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=async_engine_function, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session


@pytest.fixture(autouse=True, scope="session")
def loguru_to_standard_logging() -> Iterator[None]:
    import logging

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


# Add missing type annotation for the fixture
@pytest.fixture
def some_fixture() -> None:
    # ...fixture implementation...
    pass
