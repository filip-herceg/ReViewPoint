"""Simple tests to improve coverage for database.py."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from backend.core.database import get_async_session, db_healthcheck, AsyncSessionLocal


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
async def test_db_healthcheck_success():
    """Test that db_healthcheck succeeds on a valid connection."""
    result = await db_healthcheck()
    assert result is True


@pytest.mark.asyncio
async def test_session_rollback():
    """Test session rollback on error."""
    # Create a direct session without the context manager
    session = AsyncSessionLocal()
    from sqlalchemy import text

    try:
        # Do something that would need a rollback
        await session.execute(
            text("SELECT invalid_column_name")
        )  # This will cause an error
        await session.commit()
        assert False, "Should not reach here"
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
    try:
        async with get_async_session() as session:
            raise SQLAlchemyError("Test error")
        # Should not reach here
        assert False, "Should have raised an exception"
    except SQLAlchemyError:
        # This is expected
        pass
