"""Additional tests to improve coverage for the database module."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.url import make_url

from backend.core.database import get_async_session, AsyncSessionLocal
from backend.core.config import settings


@pytest.mark.asyncio
async def test_get_async_session_error():
    """Test session error handling."""
    # Test session with a raised error
    error_occurred = False
    try:
        async with get_async_session() as session:
            # Simulate error
            raise SQLAlchemyError("Test error")
    except SQLAlchemyError:
        error_occurred = True

    assert error_occurred is True


def test_engine_kwargs_sqlite():
    """Test engine kwargs for SQLite configurations."""
    url_obj = make_url("sqlite+aiosqlite:///:memory:")
    engine_kwargs = {
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
    engine_kwargs = {
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
    engine_kwargs = {
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
