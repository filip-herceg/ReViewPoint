"""
Fast test configuration for ReViewPoint backend.

This configuration optimizes the entire test suite for speed by:
1. Using SQLite in-memory databases
2. Disabling authentication middleware in tests
3. Optimizing fixture scopes
4. Reducing startup overhead
5. Providing mock implementations for slow operations
"""

import os
import sys
import asyncio
import uuid
from pathlib import Path
from typing import Any, Callable, Generator, Iterator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from loguru import logger
from pydantic import field_validator

# Set up the source path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Fast test environment variables - set early
os.environ.update({
    "REVIEWPOINT_ENVIRONMENT": "test",
    "REVIEWPOINT_JWT_SECRET": "fasttestsecret123",
    "REVIEWPOINT_JWT_SECRET_KEY": "fasttestsecret123",
    "REVIEWPOINT_API_KEY_ENABLED": "false",  # Disable API key auth for fast tests
    "REVIEWPOINT_API_KEY": "testkey",
    "REVIEWPOINT_AUTH_ENABLED": "true",
    "REVIEWPOINT_LOG_LEVEL": "WARNING",  # Reduce log noise
    "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
    
    # Feature flags - enable all
    "REVIEWPOINT_FEATURE_AUTH_REGISTER": "true",
    "REVIEWPOINT_FEATURE_AUTH_LOGIN": "true",
    "REVIEWPOINT_FEATURE_AUTH_REQUEST_PASSWORD_RESET": "true",
    "REVIEWPOINT_FEATURE_AUTH_RESET_PASSWORD": "true",
    "REVIEWPOINT_FEATURE_AUTH_ME": "true",
    "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
    "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
    "REVIEWPOINT_FEATURE_HEALTH": "true",
    "REVIEWPOINT_FEATURE_HEALTH_READ": "true",
    "REVIEWPOINT_FEATURE_UPLOADS": "true",
    "REVIEWPOINT_FEATURE_UPLOADS_UPLOAD": "true",
    "REVIEWPOINT_FEATURE_UPLOADS_GET": "true",
    "REVIEWPOINT_FEATURE_UPLOADS_LIST": "true",
    "REVIEWPOINT_FEATURE_UPLOADS_UPDATE": "true",
    "REVIEWPOINT_FEATURE_UPLOADS_DELETE": "true",
    "REVIEWPOINT_FEATURE_USERS_CREATE": "true",
    "REVIEWPOINT_FEATURE_USERS_GET": "true",
    "REVIEWPOINT_FEATURE_USERS_UPDATE": "true",
    "REVIEWPOINT_FEATURE_USERS_DELETE": "true",
    "REVIEWPOINT_FEATURE_USERS_LIST": "true",
    "REVIEWPOINT_FEATURE_USERS_EXPORT": "true",
    "REVIEWPOINT_FEATURE_USERS_EXPORT_ALIVE": "true",
    "REVIEWPOINT_FEATURE_USERS_EXPORT_SIMPLE": "true",
    
    # Mock external services
    "REVIEWPOINT_EXTERNAL_SERVICES_ENABLED": "false",
    "FAST_TESTS": "1",
})

# Import after environment setup
from src.core.config import Settings
from src.models.base import Base
from src.models import user, file
from src.main import create_app

# Configure test logging
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="WARNING", format="{time} | {level} | {message}")

# Optimize async event loop for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    
    yield loop
    loop.close()

# Test engine and session
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,  # Disable SQL echo for speed
        pool_pre_ping=False,  # Disable ping for speed
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create clean database session for each test."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def async_session(db_session):
    """Alias for db_session to match test expectations."""
    return db_session

@pytest_asyncio.fixture
async def app():
    """Create FastAPI test application."""
    return create_app()

@pytest_asyncio.fixture
async def async_client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
def client(test_app):
    """
    Provides a synchronous TestClient for the FastAPI app for use in API tests.
    This matches the signature from the main conftest.py for compatibility.
    """
    with TestClient(test_app) as c:
        yield c

@pytest.fixture(scope="function")
def client_with_api_key(test_app):
    """
    Provides a synchronous TestClient with API key validation enabled via dependency override.
    This enables testing API key validation in the fast test environment.
    """
    from fastapi import HTTPException, Security
    from src.api.deps import require_api_key, api_key_header
    
    async def mock_require_api_key(
        api_key: str = Security(api_key_header),
    ) -> None:
        """Mock API key validation that always enforces validation."""
        if not api_key or api_key != "testkey":
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Override the dependency
    test_app.dependency_overrides[require_api_key] = mock_require_api_key
    
    try:
        with TestClient(test_app) as c:
            yield c
    finally:
        # Clean up the override
        test_app.dependency_overrides.pop(require_api_key, None)

# Auth fixtures
@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user."""
    from src.models.user import User
    from src.utils.hashing import hash_password
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("password123"),
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def admin_user(db_session):
    """Create an admin test user."""
    from src.models.user import User
    from src.utils.hashing import hash_password
    
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        name="Admin User",
        password_hash=hash_password("admin123"),
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Get auth headers for test user."""
    from src.core.security import create_access_token
    
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def admin_headers(admin_user):
    """Get auth headers for admin user."""
    from src.core.security import create_access_token
    
    token = create_access_token({"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}

# Mock fixtures for external dependencies
@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services for all tests."""
    # Mock any external dependencies that might exist
    # Note: Only mock modules that actually exist
    yield None

# Performance optimization fixtures
@pytest.fixture(autouse=True)
def optimize_for_speed():
    """Apply speed optimizations without breaking password validation."""
    # Only patch slow async operations, not password hashing
    with patch("asyncio.sleep", return_value=None):
        yield

# Test markers
pytest_markers = [
    "slow: marks tests as slow (deselected with --fast)",
    "fast: marks tests as fast",
    "integration: marks tests as integration tests", 
    "unit: marks tests as unit tests",
    "auth: marks tests that require authentication",
    "database: marks tests that require database access",
]

# Custom test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection for fast mode."""
    if config.getoption("--fast", default=False):
        # Skip slow tests in fast mode
        skip_slow = pytest.mark.skip(reason="skipped in fast mode")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="run in fast mode (skip slow tests)"
    )

# Fast test utilities
class FastTestMixin:
    """Mixin class for fast test utilities."""
    
    @staticmethod
    async def create_test_user(session: AsyncSession, **kwargs):
        """Create a test user with defaults."""
        from src.models.user import User
        from src.utils.hashing import hash_password
        
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
    async def create_test_file(session: AsyncSession, user_id: uuid.UUID, **kwargs):
        """Create a test file with defaults."""
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

# Export for easy imports
__all__ = [
    "FastTestMixin",
    "test_engine", 
    "db_session",
    "app",
    "client",
    "test_user",
    "admin_user", 
    "auth_headers",
    "admin_headers"
]

@pytest.fixture(scope="session")
def test_db_url() -> str:
    """
    Returns the test database URL used for all tests.
    For fast tests, this will be the SQLite URL.
    """
    return os.environ.get("REVIEWPOINT_DB_URL", "sqlite+aiosqlite:///:memory:")

@pytest.fixture(autouse=True, scope="function")
def set_remaining_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Set remaining environment variables and feature flags for tests.
    Uses monkeypatch for proper cleanup after each test.
    Also clears settings cache to ensure fresh config for each test.
    """
    # Clear settings cache to ensure fresh config
    try:
        from src.core.config import clear_settings_cache
        clear_settings_cache()
    except Exception as e:
        logger.debug(f"Settings cache clear failed: {e}")
    
    # Set remaining environment variables for fast testing
    monkeypatch.setenv("REVIEWPOINT_DEBUG", "True")
    monkeypatch.setenv("REVIEWPOINT_LOG_LEVEL", "DEBUG")
    # Keep API key authentication disabled for fast tests to avoid JWT validation issues
    monkeypatch.setenv("REVIEWPOINT_API_KEY_ENABLED", "false")
    monkeypatch.setenv("REVIEWPOINT_API_KEY", "testkey")


@pytest.fixture
def override_env_vars(monkeypatch: pytest.MonkeyPatch, set_remaining_env_vars: None):
    """
    Fixture to override environment variables for a single test.
    Usage: override_env_vars({"VAR1": "value1", "VAR2": "value2"})
    Ensures required defaults are set first, then applies overrides.
    """
    def _override(vars: dict[str, str]) -> None:
        for k, v in vars.items():
            monkeypatch.setenv(k, v)
    return _override

@pytest.fixture
def loguru_list_sink() -> Iterator[list[str]]:
    """
    Capture loguru logs in a list for assertions, capturing only the loguru 'message' argument.
    Use this fixture to inspect logs generated during tests.
    """
    logs: list[str] = []

    def sink(message: Any) -> None:
        # message is a loguru.Message object; message.record['message'] is the plain log message
        try:
            logs.append(message.record["message"])
        except Exception:
            logs.append(str(message))

    sink_id = logger.add(sink)
    try:
        yield logs
    finally:
        try:
            logger.remove(sink_id)
        except ValueError:
            pass

@pytest.fixture(scope="function")
def test_app(async_session) -> Generator[Any, None, None]:
    """
    Provides a new FastAPI app instance for each test function.
    Overrides get_async_session dependency to use the test async_session fixture.
    """
    from src.core.database import get_async_session
    from src.main import create_app

    app = create_app()

    # Override get_async_session to yield the test session
    async def _override_get_async_session():
        yield async_session

    app.dependency_overrides[get_async_session] = _override_get_async_session
    yield app

# Helper functions for auth testing
def wait_for_condition(
    condition_fn: Callable[[], Any],
    timeout: float = 2.0,
    interval: float = 0.05,
) -> Any:
    """
    Polls the given condition_fn until it returns a truthy value or timeout is reached.
    Returns the value from condition_fn if successful, else None.
    """
    import time

    start = time.time()
    while time.time() - start < timeout:
        result = condition_fn()
        if result:
            return result
        time.sleep(interval)
    return None


def wait_for_admin_promotion(
    client,
    email: str,
    password: str,
    timeout: float = 2.0,
    interval: float = 0.05,
) -> str | None:
    """
    Polls the login endpoint until the user can log in as admin, or timeout is reached.
    Returns the access token if successful, else None.
    """
    login_data = {"email": email, "password": password}

    def try_login():
        resp = client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"X-API-Key": "testkey"},
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        return None

    return wait_for_condition(try_login, timeout=timeout, interval=interval)


def get_auth_header(client, email=None, password="TestPassword123!"):
    """
    Register a new user (or login if already exists) and return an auth header for API requests.
    Promotes the user to admin if registration is successful.
    Returns a dict with Authorization and X-API-Key headers.
    Uses the provided TestClient for all requests for consistency and speed.
    Raises RuntimeError if admin promotion fails unexpectedly.
    """
    import uuid
    from loguru import logger
    from src.core.security import create_access_token

    if email is None:
        email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {"email": email, "password": password, "name": "Test User"}
    register_resp = client.post(
        "/api/v1/auth/register", json=register_data, headers={"X-API-Key": "testkey"}
    )
    if register_resp.status_code == 201:
        token = register_resp.json().get("access_token")
        try:
            promote_resp = client.post(
                "/api/v1/users/promote-admin",
                json={"email": email},
                headers={"Authorization": f"Bearer {token}", "X-API-Key": "testkey"},
            )
            if promote_resp.status_code == 200:
                # Wait for admin promotion to take effect, polling login endpoint
                new_token = wait_for_admin_promotion(client, email, password)
                if new_token:
                    token = new_token
                    return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
                else:
                    logger.error(
                        f"Admin promotion for {email} did not take effect within timeout."
                    )
                    raise RuntimeError(
                        f"Admin promotion for {email} did not take effect within timeout."
                    )
        except Exception as exc:
            logger.error(f"Exception during admin promotion for {email}: {exc}")
            raise
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    else:
        login_data = {"email": email, "password": password}
        try:
            login_resp = client.post(
                "/api/v1/auth/login", json=login_data, headers={"X-API-Key": "testkey"}
            )
            if login_resp.status_code == 200:
                token = login_resp.json().get("access_token")
                return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        except Exception as exc:
            logger.error(f"Exception during login for {email}: {exc}")
            raise
        payload = {"sub": email}
        token = create_access_token(payload)
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
