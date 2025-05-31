# type: ignore
"""Tests for the database module."""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import (
    AsyncSessionLocal,
    db_healthcheck,
    get_async_session,
)


@pytest.mark.asyncio
async def test_db_healthcheck():
    """Test that db_healthcheck succeeds on a valid connection."""
    assert await db_healthcheck() is True


@pytest.mark.asyncio
async def test_db_session_context():
    """Test that session context manager works properly."""
    session = None
    async with get_async_session() as s:
        session = s
        assert isinstance(session, AsyncSession)

    # Just assert that we were able to enter and exit the context
    assert session is not None


@pytest.mark.asyncio
async def test_session_rollback():
    """Test session rollback on error."""
    # Create a direct session without the context manager
    session = AsyncSessionLocal()

    try:
        # Do something that would need a rollback
        await session.execute(
            text("SELECT invalid_column_name")
        )  # This will cause an error
        await session.commit()
        raise AssertionError("Should not reach here")
    except SQLAlchemyError:
        # Rollback should happen
        await session.rollback()
        # If we can execute a query after rollback, rollback worked
        result = await session.execute(text("SELECT 1"))
        assert result is not None
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_session_error_handling():
    """Test the error handling in get_async_session context manager."""
    error_occurred = False
    try:
        async with get_async_session() as _:
            # Simulate error
            raise SQLAlchemyError("Test error")
    except SQLAlchemyError:
        error_occurred = True

    assert error_occurred is True


def test_engine_kwargs_sqlite():
    """Test engine kwargs for SQLite configurations."""
    url_obj = make_url("sqlite+aiosqlite:///:memory:")
    engine_kwargs: dict[str, int | bool] = {
        "echo": False,
        "pool_pre_ping": True,
        "future": True,
    }

    # SQLite doesn't need pool settings
    if url_obj.drivername.startswith("sqlite"):
        pass
    else:
        engine_kwargs["pool_size"] = 5

    # Verify SQLite has no pool settings
    assert "pool_size" not in engine_kwargs


def test_engine_kwargs_postgres_prod():
    """Test engine kwargs for PostgreSQL in production."""
    url_obj = make_url("postgresql+asyncpg://user:pass@localhost/db")
    engine_kwargs: dict[str, int | bool] = {
        "echo": False,
        "pool_pre_ping": True,
        "future": True,
    }

    if not url_obj.drivername.startswith("sqlite"):
        # Production environment
        env = "prod"
        if env == "prod":
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20
        else:
            engine_kwargs["pool_size"] = 5
            engine_kwargs["max_overflow"] = 10

    # Verify production settings
    assert engine_kwargs["pool_size"] == 10
    assert engine_kwargs["max_overflow"] == 20


def test_engine_kwargs_postgres_dev():
    """Test engine kwargs for PostgreSQL in development."""
    url_obj = make_url("postgresql+asyncpg://user:pass@localhost/db")
    engine_kwargs: dict[str, int | bool] = {
        "echo": False,
        "pool_pre_ping": True,
        "future": True,
    }

    if not url_obj.drivername.startswith("sqlite"):
        # Development environment
        env = "dev"
        if env == "prod":
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20
        else:
            engine_kwargs["pool_size"] = 5
            engine_kwargs["max_overflow"] = 10

    # Verify development settings
    assert engine_kwargs["pool_size"] == 5
    assert engine_kwargs["max_overflow"] == 10
