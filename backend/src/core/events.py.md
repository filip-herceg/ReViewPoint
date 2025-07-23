# Application Events Module

**File:** `backend/src/core/events.py`  
**Purpose:** FastAPI application lifecycle management and startup/shutdown event handling  
**Lines of Code:** 149  
**Type:** Core Infrastructure Module

## Overview

The events module provides comprehensive application lifecycle management for the ReViewPoint backend. It handles FastAPI startup and shutdown events with thorough validation, health checking, and resource management. The module ensures proper application initialization sequence, validates critical configuration, performs database health checks, and manages graceful shutdown procedures. This is essential for production deployment reliability and proper resource cleanup.

## Architecture

### Core Design Principles

1. **Fail-Fast Startup**: Comprehensive validation during application startup
2. **Health Monitoring**: Database connectivity verification before serving requests
3. **Graceful Shutdown**: Proper resource cleanup during application termination
4. **Error Resilience**: Detailed error handling and logging throughout lifecycle
5. **Resource Management**: Database connection pool initialization and disposal
6. **Configuration Validation**: Runtime verification of required environment variables

### Key Components

#### Startup Validation Sequence

```python
async def on_startup() -> None:
    """FastAPI startup event handler."""
    logger.info("Starting up application...")
    await validate_config()           # 1. Validate configuration
    await db_healthcheck()           # 2. Check database health
    log_startup_complete()           # 3. Log startup completion
```

**Startup Process:**

- Environment variable validation
- Database connectivity verification
- Connection pool initialization monitoring
- Comprehensive error handling and logging

#### Shutdown Cleanup Sequence

```python
async def on_shutdown() -> None:
    """FastAPI shutdown event handler."""
    logger.info("Shutting down application...")
    # Complete pending tasks
    await engine.dispose()           # Close database connections
    logger.info("Shutdown complete.")
```

**Shutdown Process:**

- Pending task completion (placeholder for custom logic)
- Database connection pool disposal
- Resource cleanup verification
- Final status logging

## Core Functions

### 🔧 **Configuration Validation**

#### `validate_config()`

```python
async def validate_config() -> None:
    """Validate required environment variables and config logic."""
```

**Purpose:** Comprehensive runtime validation of critical configuration

**Validation Process:**

1. **Database URL Check**: Validates REVIEWPOINT_DB_URL is configured
2. **Environment Check**: Ensures REVIEWPOINT_ENVIRONMENT is set
3. **JWT Secret Validation**: Verifies JWT secret is configured (if JWT auth enabled)
4. **Error Collection**: Accumulates all missing variables for comprehensive reporting
5. **Early Failure**: Raises RuntimeError with all missing variables at once

**Configuration Requirements:**

```python
# Required environment variables
REVIEWPOINT_DB_URL          # Database connection string
REVIEWPOINT_ENVIRONMENT     # Application environment (dev/prod/test)
REVIEWPOINT_JWT_SECRET      # JWT signing secret (if using JWT auth)
```

**Error Handling:**

```python
if missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(missing)}"
    )
```

### 🏥 **Database Health Checking**

#### `db_healthcheck()`

```python
async def db_healthcheck() -> None:
    """Run a simple DB health check query."""
```

**Purpose:** Verify database connectivity before serving requests

**Health Check Process:**

1. **Engine Initialization**: Ensures database engine is properly initialized
2. **Connection Test**: Establishes connection to database
3. **Query Execution**: Executes simple SELECT 1 query to verify functionality
4. **Error Reporting**: Comprehensive error handling with specific error types

**Connection Verification:**

```python
async with engine.connect() as conn:
    connection: AsyncConnection = conn
    await connection.execute(text("SELECT 1"))
```

**Error Handling:**

- **SQLAlchemyError**: Database-specific errors with detailed logging
- **RuntimeError**: Engine initialization failures
- **General Exception**: Unexpected errors during health check

### 📊 **Startup Monitoring**

#### `log_startup_complete()`

```python
def log_startup_complete() -> None:
    """Log startup completion information."""
```

**Purpose:** Comprehensive logging of startup state and configuration

**Monitoring Information:**

1. **Environment Configuration**: Current environment (dev/prod/test)
2. **Database Type**: Database engine type from connection URL
3. **Connection Pool Status**: Pool size information (when available)
4. **Startup Confirmation**: Success confirmation with key metrics

**Pool Size Detection:**

```python
pool = getattr(db_module.engine, "pool", None)
if pool is not None and hasattr(pool, "size") and callable(pool.size):
    pool_size = str(pool.size())
else:
    pool_size = "n/a"  # Graceful fallback
```

### 🚀 **Startup Event Handler**

#### `on_startup()`

```python
async def on_startup() -> None:
    """FastAPI startup event handler."""
```

**Purpose:** Main FastAPI startup event coordinating all initialization

**Startup Sequence:**

1. **Configuration Validation**: Verify all required environment variables
2. **Database Health Check**: Confirm database connectivity
3. **Resource Initialization**: Setup connection pools and resources
4. **Completion Logging**: Record successful startup with system information

**Error Handling:**

```python
except Exception as e:
    error_msg: str = str(e)
    logger.error(f"Startup failed: {error_msg}")
    raise RuntimeError(f"Startup failed: {error_msg}") from e
```

**Integration with FastAPI:**

```python
from fastapi import FastAPI
from src.core.events import on_startup

app = FastAPI()
app.add_event_handler("startup", on_startup)
```

### 🛑 **Shutdown Event Handler**

#### `on_shutdown()`

```python
async def on_shutdown() -> None:
    """FastAPI shutdown event handler."""
```

**Purpose:** Graceful application shutdown with proper resource cleanup

**Shutdown Sequence:**

1. **Shutdown Initiation**: Log shutdown start
2. **Task Completion**: Allow pending operations to complete (placeholder for custom logic)
3. **Database Cleanup**: Dispose of database connection pool
4. **Resource Verification**: Confirm all resources are properly cleaned up
5. **Completion Logging**: Record successful shutdown

**Database Connection Cleanup:**

```python
from src.core.database import engine

if engine is not None:
    await engine.dispose()
    logger.info("Database connections closed.")
```

**Error Handling:**

```python
except Exception as e:
    logger.error(f"Shutdown error: {error_msg}")
    raise RuntimeError(f"Shutdown failed: {error_msg}") from e
finally:
    logger.info("Shutdown complete.")  # Always log completion
```

## Usage Patterns

### 🔧 **FastAPI Integration**

```python
from fastapi import FastAPI
from src.core.events import on_startup, on_shutdown

def create_app() -> FastAPI:
    """Create FastAPI application with lifecycle management."""
    app = FastAPI(
        title="ReViewPoint API",
        description="Scientific paper review platform",
        version="1.0.0"
    )

    # Register lifecycle events
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)

    return app

# Application will now:
# 1. Validate configuration on startup
# 2. Check database health before serving
# 3. Clean up resources on shutdown
```

### 🏥 **Standalone Health Checking**

```python
from src.core.events import db_healthcheck, validate_config

async def manual_health_check():
    """Perform manual health verification."""
    try:
        # Validate configuration
        await validate_config()
        print("✓ Configuration valid")

        # Check database health
        await db_healthcheck()
        print("✓ Database healthy")

    except RuntimeError as e:
        print(f"✗ Health check failed: {e}")
```

### 📊 **Development Debugging**

```python
from src.core.events import log_startup_complete
from src.core.config import get_settings

def debug_startup_state():
    """Debug startup state and configuration."""
    settings = get_settings()

    print("Current Configuration:")
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.db_url}")

    # Log complete startup information
    log_startup_complete()
```

### 🧪 **Testing Integration**

```python
import pytest
from src.core.events import validate_config, db_healthcheck

@pytest.mark.asyncio
async def test_startup_sequence():
    """Test complete startup sequence."""
    # Should validate config without error
    await validate_config()

    # Should connect to test database
    await db_healthcheck()

@pytest.mark.asyncio
async def test_config_validation_failure():
    """Test configuration validation with missing variables."""
    # Mock missing environment variables
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError) as exc_info:
            await validate_config()

        assert "Missing required environment variables" in str(exc_info.value)
```

## Error Handling and Recovery

### 🛠️ **Startup Error Scenarios**

#### Configuration Validation Failures

```python
# Missing environment variables
RuntimeError: Missing required environment variables:
REVIEWPOINT_DB_URL, REVIEWPOINT_ENVIRONMENT
```

**Recovery Approach:**

- Fix environment configuration
- Restart application
- Verify all required variables are set

#### Database Health Check Failures

```python
# Database connectivity issues
SQLAlchemyError: Database health check failed: connection refused
RuntimeError: Database health check failed: connection refused
```

**Recovery Approach:**

- Verify database service is running
- Check network connectivity
- Validate database credentials
- Confirm database exists and is accessible

#### Engine Initialization Failures

```python
# Database engine not initialized
RuntimeError: Database engine is not initialized.
```

**Recovery Approach:**

- Check database URL format
- Verify database drivers are installed
- Validate connection string syntax

### 🔄 **Shutdown Error Scenarios**

#### Database Disposal Errors

```python
# Connection cleanup issues during shutdown
RuntimeError: Shutdown failed: Error disposing database connections
```

**Recovery Approach:**

- Force terminate application if cleanup fails
- Check for connection leaks
- Review database session management

#### Resource Cleanup Failures

```python
# General resource cleanup errors
RuntimeError: Shutdown failed: Resource cleanup error
```

**Recovery Approach:**

- Implement force shutdown procedures
- Log resource states for debugging
- Review custom cleanup logic

## Environment-Specific Behavior

### 🏗️ **Development Environment**

**Features:**

- Detailed startup logging for debugging
- SQLite database health checking
- Fast startup for development iteration

**Configuration:**

```bash
REVIEWPOINT_ENVIRONMENT=dev
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db
```

### 🚀 **Production Environment**

**Features:**

- Comprehensive health monitoring
- PostgreSQL connection pool management
- Robust error handling and recovery

**Configuration:**

```bash
REVIEWPOINT_ENVIRONMENT=prod
REVIEWPOINT_DB_URL=postgresql+asyncpg://user:pass@host:5432/db
REVIEWPOINT_JWT_SECRET=production-secret
```

### 🧪 **Test Environment**

**Features:**

- Isolated database health checking
- Fast startup/shutdown for test execution
- Memory or temporary database support

**Configuration:**

```bash
REVIEWPOINT_ENVIRONMENT=test
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///:memory:
```

## Performance Considerations

### ⚡ **Startup Performance**

#### Connection Pool Initialization

```python
# Database health check initializes connection pool
await connection.execute(text("SELECT 1"))
```

**Performance Benefits:**

- Early connection pool warmup
- Connection validation before request serving
- Reduced first-request latency

#### Configuration Caching

```python
from src.core.config import get_settings
settings = get_settings()  # Cached after first call
```

**Performance Features:**

- Cached configuration after initial load
- No repeated environment variable parsing
- Fast configuration access during startup

### 🔄 **Shutdown Performance**

#### Graceful Connection Cleanup

```python
await engine.dispose()  # Proper connection pool disposal
```

**Performance Benefits:**

- Clean database connection termination
- No connection leaks or hanging processes
- Fast application shutdown

## Best Practices

### ✅ **Do's**

- **Register Early**: Add event handlers during FastAPI app creation
- **Validate Configuration**: Always validate critical settings on startup
- **Check Database Health**: Verify connectivity before serving requests
- **Log Comprehensively**: Include environment and configuration details
- **Handle Errors Gracefully**: Provide clear error messages for debugging
- **Clean Up Resources**: Properly dispose of connections and resources

### ❌ **Don'ts**

- **Don't Skip Validation**: Never assume configuration is correct
- **Don't Ignore Health Checks**: Database connectivity is critical
- **Don't Block Startup**: Keep validation efficient and fast
- **Don't Suppress Errors**: Always propagate critical startup failures
- **Don't Forget Cleanup**: Resource leaks cause production issues
- **Don't Hardcode Values**: Use configuration for all environment-specific values

## Testing Strategies

### 🧪 **Startup Testing**

```python
@pytest.mark.asyncio
async def test_complete_startup_sequence():
    """Test entire startup sequence."""
    # Should complete without errors
    await on_startup()

    # Verify database is healthy
    from src.core.database import engine
    assert engine is not None

@pytest.mark.asyncio
async def test_startup_failure_handling():
    """Test startup failure scenarios."""
    # Mock database connection failure
    with patch('src.core.events.db_healthcheck') as mock_health:
        mock_health.side_effect = SQLAlchemyError("Connection failed")

        with pytest.raises(RuntimeError):
            await on_startup()
```

### 🛑 **Shutdown Testing**

```python
@pytest.mark.asyncio
async def test_graceful_shutdown():
    """Test graceful shutdown process."""
    # Setup application state
    await on_startup()

    # Should shutdown cleanly
    await on_shutdown()

    # Verify resources cleaned up
    from src.core.database import engine
    # Engine should be disposed but may still exist
```

### 📊 **Health Check Testing**

```python
@pytest.mark.asyncio
async def test_database_health_check_success():
    """Test successful database health check."""
    await db_healthcheck()  # Should not raise

@pytest.mark.asyncio
async def test_database_health_check_failure():
    """Test database health check failure handling."""
    with patch('src.core.database.engine', None):
        with pytest.raises(RuntimeError):
            await db_healthcheck()
```

## Related Files

- **`main.py`** - FastAPI application setup using event handlers
- **`config.py`** - Configuration management used in validation
- **`database.py`** - Database engine management and health checking
- **`app_logging.py`** - Logging configuration for event reporting
- **Deployment scripts** - Production deployment using lifecycle events

## Dependencies

- **`fastapi`** - Application framework providing startup/shutdown events
- **`sqlalchemy`** - Database operations and health checking
- **`loguru`** - Comprehensive logging for lifecycle events
- **`typing`** - Type safety for event handler functions

---

_This module provides robust application lifecycle management for the ReViewPoint backend, ensuring reliable startup validation, database health monitoring, and graceful shutdown procedures essential for production deployment._
