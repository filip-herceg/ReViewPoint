# utils/environment.py - Environment Detection Utilities

## Purpose

The `utils/environment.py` module provides reliable environment detection utilities for the ReViewPoint platform. It implements comprehensive test mode detection across multiple environment variables and testing frameworks with type-safe constants and clear boolean logic.

## Key Components

### Core Imports and Constants

#### Essential Environment Detection

```python
import os
from typing import Final

# Module-level constants for environment variable names
ENVIRONMENT_VAR: Final[str] = "ENVIRONMENT"
PYTEST_CURRENT_TEST_VAR: Final[str] = "PYTEST_CURRENT_TEST"
REVIEWPOINT_TEST_MODE_VAR: Final[str] = "REVIEWPOINT_TEST_MODE"
TEST_ENV_LITERAL: Final[str] = "test"
TEST_MODE_LITERAL: Final[str] = "1"
```

**Configuration Constants:**

- **ENVIRONMENT_VAR**: Standard environment variable for application environment
- **PYTEST_CURRENT_TEST_VAR**: PyTest automatic test detection variable
- **REVIEWPOINT_TEST_MODE_VAR**: Application-specific test mode override
- **TEST_ENV_LITERAL**: Expected value for test environment
- **TEST_MODE_LITERAL**: Boolean flag value for test mode activation

### Environment Detection

#### Comprehensive Test Mode Detection

```python
def is_test_mode() -> bool:
    """
    Returns True if the current environment is test mode.
    Checks the following environment variables:
    - ENVIRONMENT == 'test'
    - PYTEST_CURRENT_TEST is set (not None or empty)
    - REVIEWPOINT_TEST_MODE == '1'

    :return: True if in test mode, False otherwise.
    """
    env: str | None = os.environ.get(ENVIRONMENT_VAR)
    pytest_current_test: str | None = os.environ.get(PYTEST_CURRENT_TEST_VAR)
    reviewpoint_test_mode: str | None = os.environ.get(REVIEWPOINT_TEST_MODE_VAR)
    return (
        env == TEST_ENV_LITERAL
        or bool(pytest_current_test)
        or reviewpoint_test_mode == TEST_MODE_LITERAL
    )
```

**Multi-Layer Detection Strategy:**

1. **Standard Environment Check**: `ENVIRONMENT == 'test'`
2. **PyTest Automatic Detection**: `PYTEST_CURRENT_TEST` presence
3. **Application Override**: `REVIEWPOINT_TEST_MODE == '1'`

**Benefits:**
- Automatic test detection without manual configuration
- Framework-agnostic test mode identification
- Application-specific override capability
- Type-safe environment variable handling

**Usage Examples:**
```python
# Basic test mode detection
if is_test_mode():
    print("Running in test environment")
    # Disable external services, use mock data, etc.
else:
    print("Running in production/development environment")

# Conditional behavior based on environment
def get_database_url() -> str:
    if is_test_mode():
        return "sqlite:///:memory:"  # In-memory test database
    else:
        return os.environ.get("DATABASE_URL", "postgresql://...")

# Service configuration
class EmailService:
    def __init__(self):
        if is_test_mode():
            self.backend = MockEmailBackend()
        else:
            self.backend = SMTPEmailBackend()
```

## Integration Patterns

### Application Configuration

#### Environment-Aware Settings

```python
from src.utils.environment import is_test_mode
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment-aware defaults."""
    
    # Database configuration
    database_url: str = "postgresql://localhost/reviewpoint"
    database_echo: bool = False
    
    # Email configuration
    smtp_host: str = "localhost"
    smtp_port: int = 587
    email_enabled: bool = True
    
    # Security settings
    secret_key: str = "your-secret-key"
    access_token_expire_minutes: int = 30
    
    # File upload settings
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Apply test mode overrides
        if is_test_mode():
            self.database_url = "sqlite:///:memory:"
            self.database_echo = True
            self.email_enabled = False
            self.upload_dir = "./test_uploads"
            self.max_file_size = 1024 * 1024  # 1MB for tests
            self.access_token_expire_minutes = 5  # Shorter for tests

    class Config:
        env_file = ".env"
        case_sensitive = False

# Usage
settings = Settings()
print(f"Database URL: {settings.database_url}")
print(f"Test mode: {is_test_mode()}")
```

### Service Layer Integration

#### Test-Aware Service Initialization

```python
from src.utils.environment import is_test_mode

class ExternalServiceManager:
    """Manages external service connections with test mode support."""
    
    def __init__(self):
        self.email_service = self._create_email_service()
        self.payment_service = self._create_payment_service()
        self.analytics_service = self._create_analytics_service()
        self.cache_service = self._create_cache_service()
    
    def _create_email_service(self):
        if is_test_mode():
            return MockEmailService()
        else:
            return SMTPEmailService(
                host=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password
            )
    
    def _create_payment_service(self):
        if is_test_mode():
            return MockPaymentService()
        else:
            return StripePaymentService(
                api_key=settings.stripe_api_key,
                webhook_secret=settings.stripe_webhook_secret
            )
    
    def _create_analytics_service(self):
        if is_test_mode():
            return MockAnalyticsService()
        else:
            return GoogleAnalyticsService(
                tracking_id=settings.ga_tracking_id
            )
    
    def _create_cache_service(self):
        if is_test_mode():
            return InMemoryCacheService()
        else:
            return RedisCacheService(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password
            )

# Global service manager
services = ExternalServiceManager()
```

### Database Integration

#### Test Database Management

```python
from src.utils.environment import is_test_mode
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    """Database connection manager with test mode support."""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = create_async_engine(
            self.database_url,
            echo=is_test_mode(),  # Enable SQL logging in test mode
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    def _get_database_url(self) -> str:
        """Get appropriate database URL for current environment."""
        if is_test_mode():
            # Use in-memory SQLite for tests
            return "sqlite+aiosqlite:///:memory:"
        else:
            # Use configured database for production/development
            return os.environ.get(
                "DATABASE_URL",
                "postgresql+asyncpg://localhost/reviewpoint"
            )
    
    async def create_tables(self):
        """Create database tables."""
        from src.models.base import Base
        
        if is_test_mode():
            # Always recreate tables in test mode
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        else:
            # Use migrations in production
            pass  # Alembic handles this
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

# Global database manager
db_manager = DatabaseManager()
```

### Testing Framework Integration

#### PyTest Configuration

```python
import pytest
from src.utils.environment import is_test_mode

# Automatic test mode detection
assert is_test_mode() == True  # This will pass when running under pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Automatically configure test environment."""
    
    # Verify we're in test mode
    assert is_test_mode(), "Tests must run in test mode"
    
    # Set additional test environment variables
    os.environ["REVIEWPOINT_TEST_MODE"] = "1"
    os.environ["ENVIRONMENT"] = "test"
    
    # Configure test-specific settings
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Test database
    os.environ["EMAIL_BACKEND"] = "mock"
    
    yield
    
    # Cleanup after tests
    test_vars = [
        "REVIEWPOINT_TEST_MODE",
        "ENVIRONMENT",
        "DATABASE_URL",
        "REDIS_URL",
        "EMAIL_BACKEND"
    ]
    for var in test_vars:
        os.environ.pop(var, None)

@pytest.fixture
def test_client():
    """Create test client with proper environment detection."""
    from fastapi.testclient import TestClient
    from src.main import app
    
    # Verify test mode
    assert is_test_mode()
    
    with TestClient(app) as client:
        yield client

# Example test with environment detection
def test_service_initialization():
    """Test that services are properly initialized in test mode."""
    assert is_test_mode()
    
    # Services should use mock implementations
    from src.services import email_service, payment_service
    
    assert isinstance(email_service, MockEmailService)
    assert isinstance(payment_service, MockPaymentService)
```

### FastAPI Integration

#### Environment-Aware Application Factory

```python
from fastapi import FastAPI
from src.utils.environment import is_test_mode

def create_app() -> FastAPI:
    """Create FastAPI application with environment-aware configuration."""
    
    app = FastAPI(
        title="ReViewPoint API",
        version="1.0.0",
        debug=is_test_mode(),  # Enable debug mode in tests
        docs_url="/docs" if not is_test_mode() else None,  # Disable docs in production
        redoc_url="/redoc" if not is_test_mode() else None
    )
    
    # Environment-specific middleware
    if is_test_mode():
        # Add test-specific middleware
        from src.middleware.test import TestMiddleware
        app.add_middleware(TestMiddleware)
    else:
        # Add production middleware
        from src.middleware.security import SecurityMiddleware
        from src.middleware.logging import LoggingMiddleware
        app.add_middleware(SecurityMiddleware)
        app.add_middleware(LoggingMiddleware)
    
    # Environment-specific startup events
    @app.on_event("startup")
    async def startup_event():
        if is_test_mode():
            print("Starting application in TEST mode")
            await setup_test_database()
        else:
            print("Starting application in PRODUCTION mode")
            await setup_production_services()
    
    return app

app = create_app()
```

### Cache Integration

#### Environment-Aware Cache Configuration

```python
from src.utils.environment import is_test_mode
import asyncio
from typing import Any, Optional

class CacheService:
    """Cache service with test mode support."""
    
    def __init__(self):
        if is_test_mode():
            self.backend = InMemoryCache()
        else:
            self.backend = RedisCache()
    
    async def get(self, key: str) -> Optional[Any]:
        return await self.backend.get(key)
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        # Shorter TTL in test mode
        if is_test_mode():
            expire = min(expire, 60)  # Max 1 minute in tests
        
        await self.backend.set(key, value, expire)
    
    async def delete(self, key: str) -> None:
        await self.backend.delete(key)
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        if is_test_mode():
            # Allow cache clearing in test mode
            await self.backend.clear()
        else:
            # Prevent accidental cache clearing in production
            raise RuntimeError("Cache clearing not allowed in production")

class InMemoryCache:
    """In-memory cache for testing."""
    
    def __init__(self):
        self.store = {}
        self.expiration = {}
    
    async def get(self, key: str) -> Optional[Any]:
        if key in self.expiration and asyncio.get_event_loop().time() > self.expiration[key]:
            del self.store[key]
            del self.expiration[key]
            return None
        return self.store.get(key)
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        self.store[key] = value
        self.expiration[key] = asyncio.get_event_loop().time() + expire
    
    async def delete(self, key: str) -> None:
        self.store.pop(key, None)
        self.expiration.pop(key, None)
    
    async def clear(self) -> None:
        self.store.clear()
        self.expiration.clear()
```

## Advanced Features

### Environment-Specific Logging

```python
import logging
from src.utils.environment import is_test_mode

def configure_logging() -> None:
    """Configure logging based on environment."""
    
    if is_test_mode():
        # Minimal logging for tests
        logging.basicConfig(
            level=logging.WARNING,
            format="%(levelname)s: %(message)s"
        )
        
        # Disable noisy loggers in test mode
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        
    else:
        # Comprehensive logging for production
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )

# Configure logging at module import
configure_logging()
```

### Performance Optimization

```python
from src.utils.environment import is_test_mode
from functools import lru_cache

class PerformanceManager:
    """Performance optimizations with test mode awareness."""
    
    @staticmethod
    @lru_cache(maxsize=128 if not is_test_mode() else 16)
    def expensive_calculation(input_data: str) -> str:
        """Expensive calculation with environment-aware caching."""
        # Smaller cache in test mode to avoid memory issues
        return f"processed_{input_data}"
    
    @staticmethod
    def get_connection_pool_size() -> int:
        """Get appropriate connection pool size."""
        return 5 if is_test_mode() else 20
    
    @staticmethod
    def get_worker_count() -> int:
        """Get appropriate worker count."""
        return 1 if is_test_mode() else 4
    
    @staticmethod
    def should_enable_feature(feature_name: str) -> bool:
        """Feature flag with test mode consideration."""
        if is_test_mode():
            # Enable all features in test mode for coverage
            return True
        
        # Production feature flags
        return os.environ.get(f"ENABLE_{feature_name.upper()}", "false").lower() == "true"
```

## Best Practices

### Environment Configuration

```python
# Environment variable naming conventions
ENVIRONMENT_VARIABLES = {
    "test": {
        "ENVIRONMENT": "test",
        "REVIEWPOINT_TEST_MODE": "1",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/1",
        "EMAIL_BACKEND": "mock",
        "LOG_LEVEL": "WARNING"
    },
    "development": {
        "ENVIRONMENT": "development",
        "DATABASE_URL": "postgresql+asyncpg://localhost/reviewpoint_dev",
        "REDIS_URL": "redis://localhost:6379/0",
        "EMAIL_BACKEND": "console",
        "LOG_LEVEL": "DEBUG"
    },
    "production": {
        "ENVIRONMENT": "production",
        "DATABASE_URL": "${DATABASE_URL}",  # From deployment
        "REDIS_URL": "${REDIS_URL}",
        "EMAIL_BACKEND": "smtp",
        "LOG_LEVEL": "INFO"
    }
}
```

### Testing Strategies

```python
import pytest
from src.utils.environment import is_test_mode

class TestEnvironmentDetection:
    """Test environment detection functionality."""
    
    def test_pytest_detection(self):
        """Test automatic PyTest detection."""
        # This test automatically runs in test mode due to PYTEST_CURRENT_TEST
        assert is_test_mode() == True
    
    def test_manual_test_mode(self, monkeypatch):
        """Test manual test mode activation."""
        # Clear all test environment variables
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.delenv("REVIEWPOINT_TEST_MODE", raising=False)
        
        # Should not be in test mode
        assert is_test_mode() == False
        
        # Set manual test mode
        monkeypatch.setenv("REVIEWPOINT_TEST_MODE", "1")
        assert is_test_mode() == True
    
    def test_environment_variable(self, monkeypatch):
        """Test ENVIRONMENT variable detection."""
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.delenv("REVIEWPOINT_TEST_MODE", raising=False)
        
        # Set environment to test
        monkeypatch.setenv("ENVIRONMENT", "test")
        assert is_test_mode() == True
        
        # Set environment to production
        monkeypatch.setenv("ENVIRONMENT", "production")
        assert is_test_mode() == False
    
    def test_multiple_indicators(self, monkeypatch):
        """Test behavior with multiple test indicators."""
        # Set multiple test indicators
        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("REVIEWPOINT_TEST_MODE", "1")
        
        assert is_test_mode() == True
        
        # Remove one indicator
        monkeypatch.delenv("ENVIRONMENT")
        assert is_test_mode() == True  # Still true due to REVIEWPOINT_TEST_MODE
```

This environment detection system provides reliable, framework-agnostic test mode detection with comprehensive integration patterns for the ReViewPoint platform.
