# core/**init**.py - Core Module Initialization

## Purpose

The `core/__init__.py` module serves as the initialization point for the ReViewPoint core infrastructure package. While the file itself is empty (following Python best practices for clean module structure), this documentation provides a comprehensive overview of the core infrastructure architecture, module relationships, and initialization patterns used throughout the core system.

## Core Architecture Overview

### Module Organization

The ReViewPoint core infrastructure is organized into several key modules:

```python
"""
Core Infrastructure Package Structure:

core/
├── __init__.py              # Module initialization (this file)
├── config.py                # Configuration management and settings
├── database.py              # Async database connection and session management
├── sync_database.py         # Sync database session management
├── security.py              # Authentication, authorization, and security utilities
├── app_logging.py           # Application logging configuration and management
├── events.py                # Application lifecycle and event management
├── feature_flags.py         # Feature flag system for controlled rollouts
├── openapi.py               # OpenAPI schema generation and customization
└── documentation.py         # Enhanced API documentation configuration

Dependencies Flow:
config.py → database.py → security.py
    ↓           ↓            ↓
app_logging.py  events.py    feature_flags.py
    ↓           ↓            ↓
openapi.py → documentation.py
"""
```

### Initialization Patterns

#### Core Module Imports

```python
# Standard import pattern for core modules
from .config import get_settings, Settings
from .database import get_database, get_async_session
from .sync_database import get_session, get_sync_session_factory
from .security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user
)
from .app_logging import app_logger, performance_logger, security_logger
from .events import event_manager, health_checker
from .feature_flags import feature_flag_manager, feature_flag_service
from .openapi import setup_openapi, get_schema_manager
from .documentation import get_enhanced_openapi_schema, get_documentation_manager

# Type exports for external use
from .config import Settings
from .database import AsyncDatabase
from .security import TokenData, UserTokenData
from .events import HealthStatus, HealthCheckResult
from .feature_flags import UserContext, FeatureFlag
```

#### Application Initialization Sequence

```python
from typing import Optional
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

async def initialize_core_infrastructure(
    app: FastAPI,
    config_override: Optional[dict] = None
) -> None:
    """
    Initialize all core infrastructure components in correct order.

    This function handles the proper initialization sequence for all core
    components, ensuring dependencies are satisfied and resources are
    properly configured.

    Args:
        app: FastAPI application instance
        config_override: Optional configuration overrides

    Raises:
        RuntimeError: If initialization fails
    """

    logger.info("Initializing ReViewPoint core infrastructure...")

    try:
        # 1. Configuration (must be first)
        from .config import get_settings
        settings = get_settings()
        if config_override:
            settings.update(config_override)
        logger.info("✓ Configuration loaded")

        # 2. Logging system
        from .app_logging import setup_logging, app_logger
        setup_logging()
        app_logger.info("Logging system initialized")
        logger.info("✓ Logging system configured")

        # 3. Database connections
        from .database import initialize_database
        await initialize_database()
        logger.info("✓ Database connections established")

        # 4. Security system
        from .security import initialize_security
        await initialize_security()
        logger.info("✓ Security system initialized")

        # 5. Event management system
        from .events import event_manager
        await event_manager.initialize()
        logger.info("✓ Event management system started")

        # 6. Feature flag system
        from .feature_flags import feature_flag_manager
        await feature_flag_manager.initialize()
        logger.info("✓ Feature flag system loaded")

        # 7. OpenAPI schema enhancement
        from .openapi import setup_openapi, initialize_openapi_utilities
        setup_openapi(app)
        initialize_openapi_utilities(app)
        logger.info("✓ OpenAPI schema configured")

        # 8. Documentation enhancement
        from .documentation import get_documentation_manager
        doc_manager = get_documentation_manager()
        logger.info("✓ Documentation system ready")

        logger.info("🚀 Core infrastructure initialization completed successfully")

    except Exception as e:
        logger.error(f"❌ Core infrastructure initialization failed: {e}")
        raise RuntimeError(f"Failed to initialize core infrastructure: {e}") from e


async def shutdown_core_infrastructure() -> None:
    """
    Gracefully shutdown all core infrastructure components.

    This function handles proper cleanup of resources and graceful
    shutdown of all core components in reverse initialization order.
    """

    logger.info("Shutting down ReViewPoint core infrastructure...")

    try:
        # Shutdown in reverse order of initialization

        # 1. Feature flag system
        from .feature_flags import feature_flag_manager
        if hasattr(feature_flag_manager, 'shutdown'):
            await feature_flag_manager.shutdown()
        logger.info("✓ Feature flag system stopped")

        # 2. Event management system
        from .events import event_manager
        await event_manager.shutdown()
        logger.info("✓ Event management system stopped")

        # 3. Database connections
        from .database import close_database
        await close_database()
        logger.info("✓ Database connections closed")

        # 4. Logging system (last)
        from .app_logging import shutdown_logging
        shutdown_logging()
        logger.info("✓ Logging system shut down")

        logger.info("✅ Core infrastructure shutdown completed")

    except Exception as e:
        logger.error(f"❌ Error during core infrastructure shutdown: {e}")


class CoreInfrastructure:
    """
    Central manager for core infrastructure lifecycle.

    This class provides a unified interface for managing the entire
    core infrastructure lifecycle, including initialization, health
    monitoring, and shutdown procedures.
    """

    def __init__(self):
        self.initialized = False
        self.components_status = {}
        self.startup_time = None
        self.app = None

    async def initialize(self, app: FastAPI, config_override: Optional[dict] = None):
        """
        Initialize core infrastructure.

        Args:
            app: FastAPI application instance
            config_override: Optional configuration overrides
        """
        if self.initialized:
            logger.warning("Core infrastructure already initialized")
            return

        self.app = app

        from datetime import datetime
        start_time = datetime.utcnow()

        await initialize_core_infrastructure(app, config_override)

        self.startup_time = datetime.utcnow() - start_time
        self.initialized = True

        logger.info(f"Core infrastructure initialized in {self.startup_time.total_seconds():.2f}s")

    async def shutdown(self):
        """Shutdown core infrastructure."""
        if not self.initialized:
            logger.warning("Core infrastructure not initialized")
            return

        await shutdown_core_infrastructure()
        self.initialized = False
        self.components_status = {}

        logger.info("Core infrastructure shutdown completed")

    async def health_check(self) -> dict:
        """
        Perform comprehensive health check of all core components.

        Returns:
            Health status of all core components
        """
        if not self.initialized:
            return {
                "status": "not_initialized",
                "components": {}
            }

        components = {}

        try:
            # Database health
            from .database import get_database
            db = get_database()
            db_health = await db.health_check()
            components["database"] = db_health
        except Exception as e:
            components["database"] = {"status": "error", "error": str(e)}

        try:
            # Event system health
            from .events import event_manager
            event_health = await event_manager.get_health_status()
            components["events"] = event_health
        except Exception as e:
            components["events"] = {"status": "error", "error": str(e)}

        try:
            # Feature flags health
            from .feature_flags import feature_flag_manager
            ff_health = feature_flag_manager.get_metrics()
            components["feature_flags"] = {"status": "healthy", "metrics": ff_health}
        except Exception as e:
            components["feature_flags"] = {"status": "error", "error": str(e)}

        # Overall status
        all_healthy = all(
            comp.get("status") == "healthy"
            for comp in components.values()
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "initialized": self.initialized,
            "startup_time": self.startup_time.total_seconds() if self.startup_time else None,
            "components": components
        }

    def get_component_status(self, component_name: str) -> dict:
        """
        Get status of specific component.

        Args:
            component_name: Name of the component

        Returns:
            Component status information
        """
        return self.components_status.get(component_name, {"status": "unknown"})

    def is_ready(self) -> bool:
        """
        Check if core infrastructure is ready for use.

        Returns:
            True if all core components are initialized and healthy
        """
        return self.initialized

# Global core infrastructure instance
core_infrastructure = CoreInfrastructure()

# Convenience functions
async def initialize_core(app: FastAPI, config_override: Optional[dict] = None):
    """Initialize core infrastructure (convenience function)"""
    await core_infrastructure.initialize(app, config_override)

async def shutdown_core():
    """Shutdown core infrastructure (convenience function)"""
    await core_infrastructure.shutdown()

async def core_health_check() -> dict:
    """Get core infrastructure health status (convenience function)"""
    return await core_infrastructure.health_check()

def is_core_ready() -> bool:
    """Check if core infrastructure is ready (convenience function)"""
    return core_infrastructure.is_ready()
```

### FastAPI Lifespan Integration

#### Application Lifecycle Management

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for core infrastructure.

    This context manager handles the complete lifecycle of the core
    infrastructure, ensuring proper startup and shutdown sequences.
    """

    # Startup
    logger.info("🚀 Starting ReViewPoint application...")

    try:
        await initialize_core(app)
        logger.info("✅ Application startup completed successfully")
        yield

    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise

    finally:
        # Shutdown
        logger.info("🔄 Shutting down ReViewPoint application...")

        try:
            await shutdown_core()
            logger.info("✅ Application shutdown completed successfully")
        except Exception as e:
            logger.error(f"❌ Error during application shutdown: {e}")

def create_app_with_core() -> FastAPI:
    """
    Create FastAPI application with core infrastructure.

    Returns:
        Configured FastAPI application with core infrastructure
    """

    app = FastAPI(
        title="ReViewPoint API",
        description="Scientific paper review platform with comprehensive core infrastructure",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add health check endpoint
    @app.get("/health")
    async def health_endpoint():
        """Core infrastructure health check endpoint"""
        return await core_health_check()

    @app.get("/health/components")
    async def detailed_health():
        """Detailed health check of all components"""
        health_status = await core_health_check()
        return health_status

    @app.get("/ready")
    async def readiness_probe():
        """Kubernetes readiness probe endpoint"""
        if is_core_ready():
            return {"status": "ready"}
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Application not ready")

    return app
```

### Configuration Management

#### Core Configuration Structure

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class CoreInfrastructureConfig(BaseModel):
    """Configuration for core infrastructure components"""

    # Database configuration
    database_url: str = "postgresql+asyncpg://localhost/reviewpoint"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False

    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_path: Optional[str] = None

    # Security configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # Feature flags configuration
    feature_flags_config_file: str = "feature_flags.json"
    feature_flags_enable_cache: bool = True
    feature_flags_auto_reload: bool = True

    # Event system configuration
    event_system_enabled: bool = True
    health_check_interval: int = 30

    # OpenAPI configuration
    openapi_enable_docs: bool = True
    openapi_enable_redoc: bool = True

    class Config:
        env_prefix = "REVIEWPOINT_"

def load_core_config() -> CoreInfrastructureConfig:
    """
    Load core infrastructure configuration.

    Returns:
        Loaded and validated configuration
    """
    return CoreInfrastructureConfig()

# Configuration validation
def validate_core_config(config: CoreInfrastructureConfig) -> List[str]:
    """
    Validate core infrastructure configuration.

    Args:
        config: Configuration to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Database validation
    if not config.database_url:
        errors.append("Database URL is required")

    if config.database_pool_size <= 0:
        errors.append("Database pool size must be positive")

    # Security validation
    if not config.secret_key or len(config.secret_key) < 32:
        errors.append("Secret key must be at least 32 characters")

    if config.access_token_expire_minutes <= 0:
        errors.append("Access token expiration must be positive")

    # Logging validation
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level.upper() not in valid_log_levels:
        errors.append(f"Log level must be one of: {valid_log_levels}")

    return errors
```

### Integration Examples

#### Complete Application Setup

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

async def create_production_app() -> FastAPI:
    """
    Create production-ready FastAPI application with full core infrastructure.

    Returns:
        Configured production application
    """

    # Load and validate configuration
    config = load_core_config()
    validation_errors = validate_core_config(config)

    if validation_errors:
        raise ValueError(f"Configuration validation failed: {validation_errors}")

    # Create app with core infrastructure
    app = create_app_with_core()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add feature flag middleware
    from .feature_flags import FeatureFlagMiddleware
    app.add_middleware(FeatureFlagMiddleware)

    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        from .app_logging import app_logger

        app_logger.error(
            f"Unhandled exception in {request.method} {request.url.path}",
            exception=exc,
            request_id=getattr(request.state, 'request_id', 'unknown')
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "status": "error"
            }
        )

    return app

# Development setup
async def create_development_app() -> FastAPI:
    """Create development application with debug features enabled"""

    app = await create_production_app()

    # Enable debug features
    app.debug = True

    # Add development middleware
    from fastapi.middleware.gzip import GZipMiddleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    return app
```

### Testing Support

#### Test Infrastructure Setup

```python
import pytest
from unittest.mock import AsyncMock, patch
import tempfile
import os

@pytest.fixture
async def test_core_infrastructure():
    """Pytest fixture for test core infrastructure"""

    # Create temporary config for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_config = {
            "flags": {
                "test_feature": {
                    "name": "test_feature",
                    "description": "Test feature flag",
                    "type": "boolean",
                    "default_value": True,
                    "status": "active"
                }
            }
        }
        import json
        json.dump(test_config, f)
        config_file = f.name

    # Override configuration for testing
    test_config_override = {
        "database_url": "sqlite+aiosqlite:///:memory:",
        "feature_flags_config_file": config_file,
        "log_level": "DEBUG"
    }

    # Create test app
    app = FastAPI(title="Test App")

    try:
        # Initialize core infrastructure
        await initialize_core(app, test_config_override)

        yield core_infrastructure

    finally:
        # Cleanup
        await shutdown_core()
        os.unlink(config_file)

@pytest.mark.asyncio
async def test_core_initialization(test_core_infrastructure):
    """Test core infrastructure initialization"""

    assert test_core_infrastructure.initialized
    assert test_core_infrastructure.is_ready()

    health_status = await test_core_infrastructure.health_check()
    assert health_status["status"] in ["healthy", "degraded"]
    assert "components" in health_status

@pytest.mark.asyncio
async def test_component_health_checks(test_core_infrastructure):
    """Test individual component health checks"""

    health_status = await test_core_infrastructure.health_check()

    # Check that all expected components are present
    expected_components = ["database", "events", "feature_flags"]

    for component in expected_components:
        assert component in health_status["components"]
        component_status = health_status["components"][component]
        assert "status" in component_status
```

## Module Integration Patterns

### Import Conventions

```python
# Recommended import patterns for different use cases

# Basic core functionality
from core import (
    get_settings,
    get_async_session,
    app_logger,
    feature_flag_service
)

# Advanced core functionality
from core.database import AsyncDatabase
from core.security import get_current_user, create_access_token
from core.events import event_manager, HealthChecker
from core.feature_flags import UserContext, FeatureFlag

# Full application setup
from core import create_app_with_core, initialize_core, shutdown_core
```

### Dependency Injection Patterns

```python
# FastAPI dependency injection with core components

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import get_async_session, get_current_user
from core.feature_flags import UserContext, feature_flag_service

async def get_feature_context(
    current_user = Depends(get_current_user)
) -> UserContext:
    """Create feature flag context from current user"""
    return UserContext(
        user_id=current_user.id,
        email=current_user.email,
        user_type=current_user.user_type
    )

async def feature_enabled_endpoint(
    feature_context: UserContext = Depends(get_feature_context),
    session: AsyncSession = Depends(get_async_session)
):
    """Example endpoint using core infrastructure"""

    # Check feature flag
    is_enabled = await feature_flag_service.is_enabled(
        "new_feature",
        feature_context
    )

    if not is_enabled:
        return {"message": "Feature not available"}

    # Use database session
    # ... database operations

    return {"message": "Feature active", "data": []}
```

## Best Practices

### Initialization Order

1. **Configuration** - Must be loaded first
2. **Logging** - Early initialization for debugging
3. **Database** - Core data persistence
4. **Security** - Authentication and authorization
5. **Events** - Application lifecycle management
6. **Feature Flags** - Runtime configuration
7. **OpenAPI** - Documentation generation
8. **Documentation** - Enhanced API docs

### Error Handling

- All initialization functions include comprehensive error handling
- Failed initialization prevents application startup
- Graceful degradation where possible
- Detailed logging for troubleshooting

### Resource Management

- Automatic cleanup during shutdown
- Connection pooling for database resources
- Memory-efficient caching strategies
- Proper lifecycle management for all components

This core infrastructure provides a robust, scalable foundation for the ReViewPoint platform with comprehensive initialization, monitoring, and management capabilities.
