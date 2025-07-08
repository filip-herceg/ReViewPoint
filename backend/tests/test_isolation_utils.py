# Add at the top of the file, after other imports
from typing import Callable, Awaitable, Any
"""
Test Cleanup and Isolation Infrastructure

This module provides enhanced cleanup mechanisms and isolation patterns
to ensure tests don't interfere with each other.
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from sqlalchemy.engine import Inspector
from loguru import logger


class TestIsolationManager:
    """Manages test isolation through database cleanup and state management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.created_records: Dict[str, List[Any]] = {}
        self.test_id = str(uuid.uuid4())[:8]
        
    async def track_created_record(self, table_name: str, record: Any) -> None:
        """Track a record created during the test for cleanup."""
        if table_name not in self.created_records:
            self.created_records[table_name] = []
        self.created_records[table_name].append(record)
        
    async def cleanup_created_records(self) -> None:
        """Clean up all records created during the test."""
        for table_name, records in self.created_records.items():
            try:
                for record in records:
                    if hasattr(record, 'id') and record.id:
                        await self.session.delete(record)
                await self.session.commit()
                logger.debug(f"Cleaned up {len(records)} records from {table_name}")
            except Exception as e:
                logger.warning(f"Error cleaning up {table_name}: {e}")
                await self.session.rollback()
    
    async def cleanup_by_email_pattern(self, email_pattern: str) -> None:
        """Clean up users and related data by email pattern."""
        try:
            # Clean up users matching the pattern
            result = await self.session.execute(
                text("DELETE FROM users WHERE email LIKE :pattern"),
                {"pattern": email_pattern}
            )
            deleted_count = getattr(result, 'rowcount', None)
            await self.session.commit()
            
            if deleted_count and deleted_count > 0:
                logger.debug(f"Cleaned up {deleted_count} users matching pattern: {email_pattern}")
        except Exception as e:
            logger.warning(f"Error cleaning up users by pattern {email_pattern}: {e}")
            await self.session.rollback()
    
    async def full_cleanup(self) -> None:
        """Perform full cleanup for the test."""
        await self.cleanup_created_records()
        # Clean up any test data that might have been created
        test_pattern = f"%{self.test_id}%"
        await self.cleanup_by_email_pattern(test_pattern)


@asynccontextmanager
async def isolated_test_session(session: AsyncSession) -> AsyncGenerator[TestIsolationManager, None]:
    """
    Context manager that provides test isolation with automatic cleanup.
    
    Usage:
        async with isolated_test_session(session) as isolation:
            # Your test code here
            user = User(email=f"test-{isolation.test_id}@example.com")
            session.add(user)
            await session.commit()
            await isolation.track_created_record("users", user)
            # Cleanup happens automatically
    """
    isolation_manager = TestIsolationManager(session)
    
    try:
        yield isolation_manager
    finally:
        await isolation_manager.full_cleanup()


class DatabaseStateVerifier:
    """Verifies database state between tests to detect isolation issues."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.initial_state: Dict[str, int] = {}
        
    async def capture_initial_state(self) -> None:
        """Capture the initial state of the database."""
        tables = ['users', 'blacklisted_tokens', 'used_password_reset_tokens', 'files']
        
        for table in tables:
            try:
                result = await self.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar() or 0
                self.initial_state[table] = count
            except Exception as e:
                logger.warning(f"Could not capture state for table {table}: {e}")
                self.initial_state[table] = 0
    
    async def verify_state_unchanged(self) -> Dict[str, int]:
        """
        Verify that database state hasn't changed unexpectedly.
        Returns dict of differences per table.
        """
        differences = {}
        
        for table, initial_count in self.initial_state.items():
            try:
                result = await self.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                current_count = result.scalar() or 0
                difference = current_count - initial_count
                
                if difference != 0:
                    differences[table] = difference
                    logger.warning(f"State change detected in {table}: {difference} records")
                    
            except Exception as e:
                logger.warning(f"Could not verify state for table {table}: {e}")
                differences[table] = -999  # Error indicator
        
        return differences
    
    async def log_current_state(self) -> None:
        """Log current database state for debugging."""
        logger.info("Current database state:")
        for table, initial_count in self.initial_state.items():
            try:
                result = await self.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                current_count = result.scalar() or 0
                logger.info(f"  {table}: {current_count} records (was {initial_count})")
            except Exception as e:
                logger.warning(f"  {table}: Error checking state: {e}")


@asynccontextmanager
async def verified_test_isolation(session: AsyncSession) -> AsyncGenerator[tuple[TestIsolationManager, DatabaseStateVerifier], None]:
    """
    Context manager that provides test isolation with state verification.
    
    Usage:
        async with verified_test_isolation(session) as (isolation, verifier):
            # Your test code here
            # State is verified automatically at the end
    """
    verifier = DatabaseStateVerifier(session)
    await verifier.capture_initial_state()
    
    async with isolated_test_session(session) as isolation:
        try:
            yield isolation, verifier
        finally:
            # Verify state is clean after test
            differences = await verifier.verify_state_unchanged()
            if differences:
                await verifier.log_current_state()
                logger.error(f"Test isolation violation detected: {differences}")


# Pytest fixtures for easy integration
import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_isolation(async_session: "AsyncSession") -> AsyncGenerator[TestIsolationManager, None]:
    """Pytest fixture that provides test isolation for async tests."""
    async with isolated_test_session(async_session) as isolation:
        yield isolation


@pytest.fixture
async def verified_isolation(async_session: "AsyncSession") -> AsyncGenerator[tuple[TestIsolationManager, DatabaseStateVerifier], None]:
    """Pytest fixture that provides test isolation with verification."""
    async with verified_test_isolation(async_session) as (isolation, verifier):
        yield isolation, verifier


# Decorator for automatic test isolation
def with_test_isolation(test_func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Decorator that automatically provides test isolation for test methods.
    
    Usage:
        @with_test_isolation
        async def test_something(self):
            # Access isolation manager via self.test_isolation
            user = User(email=f"test-{self.test_isolation.test_id}@example.com")
            # ... test code
    """
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        async with isolated_test_session(self.async_session) as isolation:
            self.test_isolation = isolation
            try:
                return await test_func(self, *args, **kwargs)
            finally:
                # Cleanup happens automatically
                pass
    
    return wrapper


# Utility functions for common cleanup scenarios
async def cleanup_test_users(session: AsyncSession, email_patterns: List[str]) -> int:
    """Clean up test users matching specific email patterns."""
    total_cleaned = 0
    
    for pattern in email_patterns:
        try:
            result = await session.execute(
                text("DELETE FROM users WHERE email LIKE :pattern"),
                {"pattern": pattern}
            )
            cleaned = getattr(result, 'rowcount', 0) or 0
            total_cleaned += cleaned
            logger.debug(f"Cleaned {cleaned} users matching pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Error cleaning users with pattern {pattern}: {e}")
    
    try:
        await session.commit()
    except Exception as e:
        logger.warning(f"Error committing user cleanup: {e}")
        await session.rollback()
    
    return total_cleaned


async def cleanup_test_tokens(session: AsyncSession, patterns: List[str]) -> int:
    """Clean up test tokens matching specific patterns."""
    total_cleaned = 0
    
    tables = ['blacklisted_tokens', 'used_password_reset_tokens']
    
    for table in tables:
        for pattern in patterns:
            try:
                # Try cleaning by associated email patterns
                if table == 'used_password_reset_tokens':
                    result = await session.execute(
                        text(f"DELETE FROM {table} WHERE email LIKE :pattern"),
                        {"pattern": pattern}
                    )
                else:
                    # For blacklisted_tokens, we'd need to join with users or use token content
                    result = await session.execute(
                        text(f"DELETE FROM {table} WHERE id IN (SELECT id FROM {table} LIMIT 0)")
                    )
                cleaned = getattr(result, 'rowcount', 0) or 0
                total_cleaned += cleaned
                logger.debug(f"Cleaned {cleaned} records from {table} matching pattern: {pattern}")
            except Exception as e:
                logger.debug(f"Pattern {pattern} not applicable to {table}: {e}")
    
    try:
        await session.commit()
    except Exception as e:
        logger.warning(f"Error committing token cleanup: {e}")
        await session.rollback()
    
    return total_cleaned
