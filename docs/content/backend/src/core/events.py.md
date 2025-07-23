# events.py - Application Lifecycle Event Management

## Purpose

Manages FastAPI application lifecycle events including startup validation, database health checks, and graceful shutdown procedures. This module provides comprehensive startup and shutdown event handlers that ensure proper initialization of application components, configuration validation, and safe resource cleanup.

## Key Components

### Core Event Handlers

#### **on_startup() Function**

- **Purpose**: FastAPI startup event handler with comprehensive initialization sequence
- **Design**: Sequential validation and initialization with detailed error reporting
- **Features**: Configuration validation, database health checks, component initialization logging
- **Error Handling**: Comprehensive error catching with context-aware error messages

#### **on_shutdown() Function**

- **Purpose**: FastAPI shutdown event handler for graceful resource cleanup
- **Design**: Safe resource disposal with error isolation and logging
- **Features**: Database connection cleanup, pending task completion, comprehensive shutdown logging
- **Safety**: Finally block ensures shutdown completion even with errors

### Validation Components

#### **validate_config() Function**

- **Purpose**: Runtime validation of required environment variables and configuration
- **Design**: Dynamic configuration access with detailed error reporting
- **Validation**: Database URL, environment settings, JWT secrets
- **Error Reporting**: Specific missing variable identification for debugging

#### **db_healthcheck() Function**

- **Purpose**: Database connectivity and health validation during startup
- **Design**: Connection-based health check with engine initialization verification
- **Features**: SQL query execution, connection pool verification, detailed error logging
- **Integration**: Works with database module for engine management

### Monitoring Components

#### **log_startup_complete() Function**

- **Purpose**: Comprehensive startup completion logging with system information
- **Design**: Safe information gathering with fallback handling
- **Features**: Environment logging, database type identification, connection pool status
- **Robustness**: Safe attribute access with exception handling

## Dependencies

### External Libraries

- **loguru**: Structured logging for event tracking and error reporting
- **sqlalchemy**: Database engine management and health check queries
- **sqlalchemy.ext.asyncio**: Async database operations for non-blocking startup/shutdown

### Internal Dependencies

- **[config.py](config.py.md)**: Configuration settings access and validation
- **[database.py](database.py.md)**: Database engine management and initialization
- **FastAPI framework**: Event lifecycle integration

### Runtime Imports

- **Delayed imports**: Avoids circular dependencies and top-level configuration loading
- **Conditional access**: Safe attribute access with proper error handling

## Integration Patterns

### FastAPI Application Integration

```python
# In main.py or app factory
from fastapi import FastAPI
from core.events import on_startup, on_shutdown

app = FastAPI()

# Register event handlers
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)
```

### Configuration Validation Flow

```python
async def validate_config() -> None:
    """Runtime configuration validation"""
    missing: list[str] = []
    settings = get_settings()

    # Dynamic attribute checking with type safety
    if not getattr(settings, "db_url", None):
        missing.append("REVIEWPOINT_DB_URL")

    if missing:
        raise RuntimeError(f"Missing: {', '.join(missing)}")
```

### Database Health Check Integration

```python
async def db_healthcheck() -> None:
    """Database connectivity verification"""
    # Ensure engine initialization
    if db_module.engine is None:
        ensure_engine_initialized()

    # Execute health check query
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
```

## Error Handling Strategy

### Startup Error Management

```python
async def on_startup() -> None:
    try:
        logger.info("Starting up application...")
        await validate_config()          # Configuration errors
        await db_healthcheck()          # Database errors
        log_startup_complete()          # System information gathering
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise RuntimeError(f"Startup failed: {e}") from e
```

### Shutdown Error Isolation

```python
async def on_shutdown() -> None:
    try:
        logger.info("Shutting down application...")
        # Resource cleanup with error handling
        if engine is not None:
            await engine.dispose()
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        raise RuntimeError(f"Shutdown failed: {e}") from e
    finally:
        logger.info("Shutdown complete.")  # Always logs completion
```

### Health Check Error Handling

```python
async def db_healthcheck() -> None:
    try:
        # Database operations
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        raise RuntimeError(f"Database health check failed: {e}") from e
    except Exception as exc:
        logger.error(f"Unexpected error during DB health check: {exc}")
        raise
```

## Configuration Validation

### Required Environment Variables

- **REVIEWPOINT_DB_URL**: Database connection string
- **REVIEWPOINT_ENVIRONMENT**: Application environment (development/production/testing)
- **REVIEWPOINT_JWT_SECRET**: JWT token signing secret (when JWT is enabled)

### Validation Logic

```python
def validate_config():
    """Comprehensive configuration validation"""
    missing: list[str] = []
    settings = get_settings()

    # Database URL validation
    db_url = cast(str | None, getattr(settings, "db_url", None))
    if not db_url:
        missing.append("REVIEWPOINT_DB_URL")

    # Environment validation
    environment = cast(str | None, getattr(settings, "environment", None))
    if not environment:
        missing.append("REVIEWPOINT_ENVIRONMENT")

    # Conditional JWT secret validation
    if hasattr(settings, "jwt_secret"):
        jwt_secret = cast(str | None, getattr(settings, "jwt_secret", None))
        if not jwt_secret:
            missing.append("REVIEWPOINT_JWT_SECRET")

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
```

## Database Integration

### Health Check Implementation

```python
async def db_healthcheck() -> None:
    """Database connectivity and health verification"""
    import src.core.database as db_module
    from src.core.database import ensure_engine_initialized

    try:
        # Ensure engine initialization
        if db_module.engine is None:
            ensure_engine_initialized()

        engine = db_module.engine
        if engine is None:
            raise RuntimeError("Database engine is not initialized.")

        # Execute simple health check query
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        raise RuntimeError(f"Database health check failed: {e}") from e
```

### Connection Pool Monitoring

```python
def log_startup_complete() -> None:
    """System information logging with safe attribute access"""
    try:
        # Safe pool size extraction
        pool = getattr(db_module.engine, "pool", None)
        if pool is not None and hasattr(pool, "size") and callable(pool.size):
            pool_size = str(pool.size())
        else:
            pool_size = "n/a"
    except Exception:
        pool_size = "n/a"

    logger.info(f"DB pool size: {pool_size}")
```

## Lifecycle Management

### Startup Sequence

1. **Configuration Validation**: Verify all required environment variables
2. **Database Health Check**: Ensure database connectivity and basic functionality
3. **Component Initialization**: Initialize additional components (cache, etc.)
4. **Completion Logging**: Log successful startup with system information

### Shutdown Sequence

1. **Pending Task Completion**: Allow ongoing operations to complete
2. **Resource Cleanup**: Close database connections and external resources
3. **Cache Cleanup**: Close cache connections if applicable
4. **Completion Logging**: Log successful shutdown in finally block

### Error Recovery

```python
# Startup failure handling
try:
    await on_startup()
except RuntimeError as e:
    logger.critical(f"Application startup failed: {e}")
    # Application will not start - FastAPI handles this appropriately
    raise

# Shutdown error handling
try:
    await on_shutdown()
except RuntimeError as e:
    logger.error(f"Shutdown errors occurred: {e}")
    # Application still shuts down - errors are logged but not propagated
```

## Performance Considerations

### Non-blocking Operations

- **Async health checks**: Database operations don't block startup
- **Parallel initialization**: Components can be initialized concurrently
- **Connection pooling**: Database connections are properly managed

### Resource Management

- **Engine disposal**: Proper cleanup of database connection pools
- **Memory cleanup**: Safe resource disposal prevents memory leaks
- **Connection limits**: Health checks use connection pooling efficiently

### Startup Optimization

```python
# Efficient startup sequence
async def on_startup() -> None:
    # Quick configuration validation first
    await validate_config()  # Fast, no I/O

    # Database health check with connection reuse
    await db_healthcheck()  # Uses connection pool

    # Optional: Concurrent initialization
    # await asyncio.gather(
    #     cache.init(),
    #     other_service.init()
    # )
```

## Security Considerations

### Configuration Security

- **Sensitive data validation**: JWT secrets are validated but not logged
- **Environment isolation**: Configuration access is environment-aware
- **Error message safety**: No sensitive information in error messages

### Database Security

- **Connection security**: Health checks use secure connection methods
- **Query safety**: Simple SELECT 1 query minimizes attack surface
- **Connection disposal**: Proper cleanup prevents connection leaks

### Logging Security

```python
# Safe logging without sensitive data
logger.info(f"Environment: {environment}, DB: {db_type}")
# Note: DB URL is not logged to prevent credential exposure
```

## Usage Examples

### Basic FastAPI Integration

```python
from fastapi import FastAPI
from core.events import on_startup, on_shutdown

app = FastAPI()

# Register lifecycle events
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

# Application will now properly initialize and cleanup
```

### Custom Event Extensions

```python
async def extended_startup():
    """Extended startup with additional components"""
    await on_startup()  # Core startup

    # Additional initialization
    await redis_client.connect()
    await message_queue.initialize()
    logger.info("Extended startup complete")

app.add_event_handler("startup", extended_startup)
```

### Health Check Integration

```python
from fastapi import HTTPException
from core.events import db_healthcheck

@app.get("/health")
async def health_endpoint():
    """Health check endpoint using core health check"""
    try:
        await db_healthcheck()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {e}")
```

## Testing Integration

### Startup Testing

```python
import pytest
from core.events import on_startup, validate_config

@pytest.mark.asyncio
async def test_startup_success():
    """Test successful startup sequence"""
    # This should complete without exceptions
    await on_startup()

@pytest.mark.asyncio
async def test_config_validation():
    """Test configuration validation"""
    # Test with missing environment variables
    with pytest.raises(RuntimeError, match="Missing required"):
        await validate_config()
```

### Health Check Testing

```python
@pytest.mark.asyncio
async def test_db_healthcheck():
    """Test database health check"""
    from core.events import db_healthcheck

    # Should complete successfully with test database
    await db_healthcheck()
```

## Related Files

- **[main.py](../main.py.md)**: FastAPI application factory and event handler registration
- **[config.py](config.py.md)**: Configuration settings accessed during validation
- **[database.py](database.py.md)**: Database engine management and initialization
- **[app_logging.py](app_logging.py.md)**: Logging configuration used throughout events
- **[../api/v1/health.py](../api/v1/health.py.md)**: Health check endpoints using event functions

## Future Enhancements

### Planned Features

- **Cache initialization**: Redis/memory cache startup integration
- **Message queue setup**: Async message processing initialization
- **Metrics collection**: Application metrics gathering during startup
- **Service discovery**: Registration with service discovery systems

### Extension Points

```python
# Future extension pattern
async def on_startup() -> None:
    await validate_config()
    await db_healthcheck()

    # Extension points for additional initialization
    await init_cache()
    await init_message_queue()
    await register_with_service_discovery()

    log_startup_complete()
```

The events.py module provides robust, comprehensive application lifecycle management ensuring proper initialization, health validation, and graceful shutdown for the ReViewPoint backend application.
