"""
Fast test templates for ReViewPoint backend.

This module provides base classes and utilities for writing fast, reliable tests.
It addresses common issues found in the test suite and provides optimized patterns.
"""

import asyncio
import uuid
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


class FastTestBase:
    """
    Base class for fast tests with common utilities and patterns.
    Provides solutions for common test issues and optimized fixtures.
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up each test method with common mocks and configurations."""
        # Clear any cached state
        self._cleanup_state()
    
    def _cleanup_state(self):
        """Clean up any cached state between tests."""
        # Override in subclasses if needed
        pass
    
    @staticmethod
    async def create_user(session: AsyncSession, **kwargs) -> "User":
        """Create a test user with sensible defaults."""
        from src.models.user import User
        from src.core.security import hash_password
        
        defaults = {
            "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
            "name": "Test User",
            "password_hash": hash_password("password123"),
            "is_active": True,
            "is_admin": False
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def create_file(session: AsyncSession, user_id: int, **kwargs) -> "File":
        """Create a test file with sensible defaults."""
        from src.models.file import File
        
        defaults = {
            "filename": f"test_{uuid.uuid4().hex[:8]}.txt",
            "original_filename": "test.txt",
            "content_type": "text/plain", 
            "size": 1024,
            "user_id": user_id
        }
        defaults.update(kwargs)
        
        file = File(**defaults)
        session.add(file)
        await session.commit()
        await session.refresh(file)
        return file
    
    @staticmethod
    async def assert_user_in_db(session: AsyncSession, user_id: int):
        """Assert that a user exists in the database."""
        from src.models.user import User
        
        result = await session.execute(
            text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        assert result.scalar() is not None, f"User {user_id} not found in database"
    
    @staticmethod
    async def assert_file_in_db(session: AsyncSession, file_id: int):
        """Assert that a file exists in the database."""
        from src.models.file import File
        
        result = await session.execute(
            text("SELECT id FROM files WHERE id = :file_id"),
            {"file_id": file_id}
        )
        assert result.scalar() is not None, f"File {file_id} not found in database"
    
    @staticmethod
    async def count_table_rows(session: AsyncSession, table_name: str) -> int:
        """Count rows in a table."""
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()
    
    def assert_http_error(self, status_code: int, response_data: Dict[str, Any], expected_detail: Optional[str] = None):
        """Assert HTTP error response format."""
        assert "detail" in response_data, f"Response missing 'detail' field: {response_data}"
        if expected_detail:
            assert expected_detail in response_data["detail"], \
                f"Expected '{expected_detail}' in detail, got: {response_data['detail']}"
    
    def assert_success_response(self, response_data: Dict[str, Any], expected_keys: Optional[list] = None):
        """Assert successful response format."""
        if expected_keys:
            for key in expected_keys:
                assert key in response_data, f"Response missing expected key '{key}': {response_data}"


class FastAPITestCase(FastTestBase):
    """Base class for FastAPI endpoint tests with optimized patterns."""
    
    @pytest_asyncio.fixture
    async def auth_headers(self, async_session: AsyncSession) -> Dict[str, str]:
        """Create authentication headers with a test user."""
        from src.core.security import create_access_token
        
        user = await self.create_user(async_session)
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def admin_headers(self, async_session: AsyncSession) -> Dict[str, str]:
        """Create authentication headers with an admin user."""
        from src.core.security import create_access_token
        
        user = await self.create_user(async_session, is_admin=True)
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    
    async def assert_requires_auth(self, client: AsyncClient, method: str, url: str, **kwargs):
        """Assert that an endpoint requires authentication."""
        response = await client.request(method, url, **kwargs)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    async def assert_success(self, client: AsyncClient, method: str, url: str, 
                           expected_status: int = 200, **kwargs):
        """Assert that a request succeeds with expected status."""
        response = await client.request(method, url, **kwargs)
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        return response
    
    async def assert_error(self, client: AsyncClient, method: str, url: str,
                          expected_status: int, expected_detail: Optional[str] = None, **kwargs):
        """Assert that a request fails with expected status and detail."""
        response = await client.request(method, url, **kwargs)
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        
        if expected_detail:
            data = response.json()
            self.assert_http_error(expected_status, data, expected_detail)
        
        return response


class DatabaseTestCase(FastTestBase):
    """Base class for database tests with transaction management."""
    
    @pytest_asyncio.fixture
    async def transactional_session(self, async_session: AsyncSession):
        """Provide a session that can test transaction rollbacks."""
        # Start a nested transaction
        async with async_session.begin():
            yield async_session
            # Transaction will be rolled back automatically
    
    async def assert_integrity_error(self, session: AsyncSession, operation):
        """Assert that an operation raises an IntegrityError."""
        with pytest.raises(IntegrityError):
            await operation()
            await session.commit()
    
    async def assert_no_error(self, session: AsyncSession, operation):
        """Assert that an operation completes without error."""
        try:
            await operation()
            await session.commit()
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")


class UploadTestCase(FastAPITestCase):
    """Base class for upload endpoint tests with file mocking."""
    
    @pytest.fixture
    def mock_file_upload(self):
        """Mock file upload operations."""
        from unittest.mock import patch
        
        with patch("src.utils.file.save_file") as mock_save, \
             patch("src.utils.file.delete_file") as mock_delete, \
             patch("src.utils.file.get_file_size") as mock_size:
            
            mock_save.return_value = True
            mock_delete.return_value = True
            mock_size.return_value = 1024
            
            yield {
                "save_file": mock_save,
                "delete_file": mock_delete,
                "get_file_size": mock_size
            }
    
    def create_test_file_upload(self, filename: str = "test.txt", content: str = "test content"):
        """Create a test file upload object."""
        from io import BytesIO
        
        return {
            "file": (BytesIO(content.encode()), filename, "text/plain")
        }


# Common fixtures for all test cases
@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import MagicMock
    
    settings = MagicMock()
    settings.auth_enabled = True
    settings.api_key_enabled = False
    settings.environment = "test"
    settings.log_level = "WARNING"
    settings.upload_max_size = 10 * 1024 * 1024  # 10MB
    settings.upload_dir = "/tmp/test_uploads"
    
    return settings


@pytest.fixture
def mock_email_service():
    """Mock email service for faster tests."""
    with pytest.mock.patch("src.services.email.send_email") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def disable_rate_limits():
    """Disable rate limiting for tests."""
    with pytest.mock.patch("src.utils.rate_limit.check_rate_limit") as mock:
        mock.return_value = True
        yield mock


# Performance helpers
def skip_if_slow(reason="Slow test skipped in fast mode"):
    """Skip test if running in fast mode."""
    return pytest.mark.skipif(
        pytest.importorskip("os").environ.get("FAST_TESTS") == "1",
        reason=reason
    )


def mark_slow(test_func):
    """Mark test as slow."""
    return pytest.mark.slow(test_func)


# Database utilities
async def truncate_all_tables(session: AsyncSession):
    """Truncate all tables in the database."""
    from src.models import Base
    
    # Disable foreign key constraints temporarily
    await session.execute(text("PRAGMA foreign_keys = OFF"))
    
    try:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"DELETE FROM {table.name}"))
        await session.commit()
    finally:
        # Re-enable foreign key constraints
        await session.execute(text("PRAGMA foreign_keys = ON"))


async def seed_test_data(session: AsyncSession):
    """Seed the database with common test data."""
    from src.models.user import User
    from src.core.security import hash_password
    
    # Create test admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        password_hash=hash_password("admin123"),
        is_active=True,
        is_admin=True
    )
    session.add(admin)
    
    # Create test regular user
    user = User(
        email="user@example.com", 
        name="Test User",
        password_hash=hash_password("user123"),
        is_active=True,
        is_admin=False
    )
    session.add(user)
    
    await session.commit()
    return {"admin": admin, "user": user}
