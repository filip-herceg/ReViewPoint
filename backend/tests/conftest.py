# type: ignore

import os
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

# type: ignore[attr-defined]
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.models.base import Base

os.environ["REVIEWPOINT_DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True, scope="function")
def set_required_env_vars(monkeypatch):
    monkeypatch.setenv("REVIEWPOINT_DB_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_engine_function():
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
async def async_session(async_engine_function) -> AsyncGenerator[AsyncSession, None]:
    async_session_local = async_sessionmaker(
        bind=async_engine_function, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session
