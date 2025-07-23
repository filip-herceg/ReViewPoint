# Database Module

**File:** `backend/src/core/database.py`  
**Purpose:** Async database connection management and session handling for ReViewPoint backend  
**Lines of Code:** 417  
**Type:** Core Infrastructure Module

## Overview

The database module provides robust async database connection management with comprehensive debugging, monitoring, and connection pooling for the ReViewPoint backend. It implements sophisticated session lifecycle management, connection pool optimization, and extensive logging for troubleshooting database-related issues in development, testing, and production environments.

## Architecture

### Core Design Principles

1. **Lazy Initialization**: Engine and session creation deferred until first use
2. **Comprehensive Debugging**: Extensive logging for connection lifecycle and pool state
3. **Environment-Specific Configuration**: Different pool settings for dev/test/prod
4. **Thread Safety**: Proper synchronization for concurrent access
5. **Error Resilience**: Graceful error handling with detailed diagnostic information
6. **Test Isolation**: Special handling for parallel pytest execution

### Key Components

#### Global State Management

```python
# Global state tracking for debugging
_engine_creation_count: int = 0
_session_creation_count: int = 0
_connection_failures: int = 0
_creation_lock: Final[threading.Lock] = threading.Lock()
```

Thread-safe global counters for tracking database operation statistics and debugging concurrent access patterns.

#### Lazy Engine Initialization

```python
# Delay engine/session creation to runtime to avoid top-level config loading
engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None
```

Engine and sessionmaker are initialized on first use to ensure configuration is loaded before database setup.

## Core Functions

### 🔧 **Engine and Session Management**

#### `get_engine_and_sessionmaker()`

```python
def get_engine_and_sessionmaker() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create and return a new AsyncEngine and async_sessionmaker."""
```

**Purpose:** Creates and configures a new database engine with environment-specific settings

**Configuration Logic:**

- **PostgreSQL Production**: Pool size 10, max overflow 20
- **PostgreSQL Development**: Pool size 5, max overflow 10
- **PostgreSQL Testing**: Pool size 1, max overflow 1 (parallel test isolation)
- **SQLite**: `check_same_thread=False` for async compatibility

**Connection Pool Settings:**

| Environment    | Database   | Pool Size | Max Overflow | Special Settings              |
| -------------- | ---------- | --------- | ------------ | ----------------------------- |
| Production     | PostgreSQL | 10        | 20           | Standard production settings  |
| Development    | PostgreSQL | 5         | 10           | Reduced resource usage        |
| Parallel Tests | PostgreSQL | 1         | 1            | `pool_reset_on_return=commit` |
| Any            | SQLite     | N/A       | N/A          | `check_same_thread=False`     |

#### `ensure_engine_initialized()`

```python
def ensure_engine_initialized() -> None:
    """Ensure the global engine and sessionmaker are initialized."""
```

**Purpose:** Lazy initialization guard for global database components

**Behavior:**

- Creates engine and sessionmaker only when first needed
- Thread-safe initialization with proper locking
- Prevents multiple initialization attempts

#### `get_async_session()`

```python
@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes/services."""
```

**Purpose:** Primary session factory for dependency injection in FastAPI endpoints

**Session Lifecycle:**

1. **Creation**: Creates new session with connection testing
2. **Connection Test**: Executes `SELECT 1` to verify connectivity
3. **Yield**: Provides session to application code
4. **Cleanup**: Automatic rollback on error, proper session closure
5. **Monitoring**: Comprehensive timing and error logging

**Error Handling:**

- SQLAlchemy errors: Automatic rollback with detailed logging
- Connection failures: Retry logic with failure counting
- Session cleanup: Guaranteed resource cleanup in finally block

### 🏥 **Health Monitoring**

#### `db_healthcheck()`

```python
async def db_healthcheck() -> bool:
    """Check if the database connection is healthy."""
```

**Purpose:** Database connectivity verification for health endpoints and monitoring

**Health Check Process:**

1. **Engine Verification**: Ensures engine is initialized
2. **Connection Test**: Establishes direct database connection
3. **Query Execution**: Runs simple `SELECT 1` query
4. **Performance Metrics**: Logs connection and query timing
5. **Pool State**: Reports connection pool status

**Return Values:**

- `True`: Database is healthy and responsive
- `False`: Database is unreachable or unresponsive

### 🐛 **Debugging and Diagnostics**

#### `_log_worker_info()`

```python
def _log_worker_info() -> tuple[str, int, int]:
    """Log information about the current worker process for parallel test debugging."""
```

**Purpose:** Tracks process/thread context for debugging concurrent database access

**Information Logged:**

- Worker ID (for pytest-xdist parallel testing)
- Process ID (PID)
- Thread ID
- Environment context (main worker vs. test worker)

#### `_log_engine_pool_state()`

```python
def _log_engine_pool_state(engine: AsyncEngine, context: str) -> None:
    """Log current connection pool state for debugging connection issues."""
```

**Purpose:** Detailed connection pool monitoring and diagnostics

**Pool Metrics Logged:**

- Pool size (total connections)
- Checked out connections (in use)
- Checked in connections (available)
- Overflow connections (beyond pool size)
- Invalidated connections (requiring reset)
- Sanitized database URL

#### `get_connection_debug_info()`

```python
def get_connection_debug_info() -> ConnectionDebugInfo:
    """Get current connection state for debugging."""
```

**Purpose:** Programmatic access to database connection state for debugging and monitoring

**Debug Information Returned:**

```python
class ConnectionDebugInfo(TypedDict, total=False):
    worker_id: str
    process_id: int
    thread_id: int
    engine_creation_count: int
    session_creation_count: int
    connection_failures: int
    engine_initialized: bool
    sessionmaker_initialized: bool
    pool_size: int | None
    pool_checked_out: int | None
    pool_checked_in: int | None
    pool_overflow: int | None
    pool_invalidated: int | None
    pool_error: str
```

## Configuration Integration

### Database URL Handling

The module integrates with `config.py` to retrieve database configuration:

```python
from src.core.config import get_settings

settings = get_settings()
url_obj: URL = make_url(settings.async_db_url)
```

**Supported Database URLs:**

- **PostgreSQL**: `postgresql+asyncpg://user:pass@host:port/database`
- **SQLite**: `sqlite+aiosqlite:///path/to/file.db`
- **In-Memory SQLite**: `sqlite+aiosqlite:///:memory:` (testing)

### Environment-Specific Configuration

#### Production Environment

```python
if settings.environment == "prod":
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
```

**Production Settings:**

- Large connection pool for high concurrency
- Robust error handling and monitoring
- Performance optimization for production workloads

#### Development Environment

```python
engine_kwargs["pool_size"] = 5
engine_kwargs["max_overflow"] = 10
```

**Development Settings:**

- Smaller pool size for resource efficiency
- Enhanced debugging and logging
- SQLite support for simple setup

#### Testing Environment (Parallel)

```python
if os.environ.get("PYTEST_XDIST_WORKER"):
    engine_kwargs["pool_size"] = 1
    engine_kwargs["max_overflow"] = 1
    engine_kwargs["pool_reset_on_return"] = "commit"
    engine_kwargs["connect_args"] = {
        "server_settings": {
            "application_name": f"reviewpoint_test_{worker_id}_{process_id}",
        }
    }
```

**Parallel Test Settings:**

- Minimal pool size to prevent connection conflicts
- Unique application names for test isolation
- Connection reset after each test for clean state
- Worker-specific identification for debugging

## Usage Patterns

### FastAPI Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_async_session

@app.get("/users/")
async def get_users(
    db: AsyncSession = Depends(get_async_session)
):
    # Database operations with automatic session management
    result = await db.execute(select(User))
    return result.scalars().all()
```

**Benefits:**

- Automatic session creation and cleanup
- Exception handling with rollback
- Connection pool management
- Performance monitoring

### Manual Session Management

```python
from src.core.database import get_async_session

async def manual_database_operation():
    async with get_async_session() as session:
        # Manual session control
        try:
            result = await session.execute(text("SELECT * FROM users"))
            await session.commit()
            return result.fetchall()
        except Exception:
            await session.rollback()
            raise
```

### Health Check Integration

```python
from fastapi import FastAPI
from src.core.database import db_healthcheck

app = FastAPI()

@app.get("/health/database")
async def database_health():
    is_healthy = await db_healthcheck()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "service": "database"
    }
```

### Debug Information Access

```python
from src.core.database import get_connection_debug_info

async def debug_database_state():
    debug_info = get_connection_debug_info()
    return {
        "worker_id": debug_info["worker_id"],
        "process_id": debug_info["process_id"],
        "engine_created": debug_info["engine_initialized"],
        "sessions_created": debug_info["session_creation_count"],
        "connection_failures": debug_info["connection_failures"],
        "pool_state": {
            "size": debug_info.get("pool_size"),
            "checked_out": debug_info.get("pool_checked_out"),
            "checked_in": debug_info.get("pool_checked_in"),
        }
    }
```

## Error Handling and Resilience

### Connection Failure Management

```python
try:
    async with get_async_session() as session:
        # Database operations
        pass
except SQLAlchemyError as exc:
    # SQLAlchemy-specific error handling
    logger.error(f"Database error: {exc}")
    # Automatic rollback and cleanup
    raise
except Exception as exc:
    # General error handling
    logger.error(f"Unexpected error: {exc}")
    raise
```

**Error Recovery Features:**

- Automatic session rollback on errors
- Connection pool state monitoring
- Failure counting and tracking
- Detailed error logging with context

### Connection Pool Recovery

```python
# Pool state monitoring after errors
_log_engine_pool_state(engine, "After failed operation")

# Automatic pool recovery on next operation
# Connection pool automatically recovers failed connections
```

**Recovery Mechanisms:**

- `pool_pre_ping=True`: Tests connections before use
- Automatic invalidation of failed connections
- Pool overflow handling for traffic spikes
- Connection recycling for long-running processes

### Testing Error Scenarios

```python
import pytest
from src.core.database import get_connection_debug_info

@pytest.fixture
async def db_session():
    """Provide isolated database session for testing."""
    async with get_async_session() as session:
        # Test-specific setup
        yield session
        # Automatic cleanup

def test_connection_failure_handling():
    """Test database connection failure scenarios."""
    debug_info = get_connection_debug_info()
    assert debug_info["engine_initialized"] is True

    # Simulate connection failure
    # Test error handling and recovery
```

## Performance Monitoring

### Timing Metrics

The module provides comprehensive timing metrics for performance analysis:

```python
# Engine creation timing
creation_time: float = time.time() - start_time
logger.info(f"Engine created successfully in {creation_time:.3f}s")

# Session lifecycle timing
session_creation_time = time.time() - session_creation_start
logger.debug(f"Session created in {session_creation_time:.3f}s")

# Connection test timing
connection_test_time = time.time() - connection_test_start
logger.debug(f"Connection test passed in {connection_test_time:.3f}s")

# Total session time
total_session_time = time.time() - session_start_time
logger.debug(f"Session completed in {total_session_time:.3f}s")
```

### Pool Monitoring

```python
# Connection pool state logging
logger.info(f"Pool size: {pool.size()}")
logger.info(f"Checked out: {pool.checkedout()}")
logger.info(f"Checked in: {pool.checkedin()}")
logger.info(f"Overflow: {pool.overflow()}")
logger.info(f"Invalid: {pool.invalidated()}")
```

**Performance Insights:**

- Engine creation latency
- Session establishment time
- Connection test performance
- Pool utilization metrics
- Error frequency tracking

## Testing Integration

### Parallel Test Support

```python
# Automatic parallel test detection
worker_id: str = os.environ.get("PYTEST_XDIST_WORKER", "main")

# Worker-specific application names
"application_name": f"reviewpoint_test_{worker_id}_{process_id}"

# Minimal pool configuration for test isolation
engine_kwargs["pool_size"] = 1
engine_kwargs["max_overflow"] = 1
```

**Parallel Testing Features:**

- Worker isolation with unique connection settings
- Minimal connection pools to prevent conflicts
- Worker-specific application names for debugging
- Connection reset between tests for clean state

### Test Fixtures

```python
# Example test fixture using the database module
@pytest.fixture
async def db_session():
    """Provide database session for testing."""
    async with get_async_session() as session:
        # Test setup
        yield session
        # Automatic cleanup

@pytest.fixture
def db_debug_info():
    """Provide database debug information for testing."""
    return get_connection_debug_info()
```

### Test Utilities

```python
# Health check for test setup verification
async def verify_test_database():
    health_status = await db_healthcheck()
    assert health_status, "Test database is not healthy"

# Debug information for test diagnostics
def log_test_database_state():
    debug_info = get_connection_debug_info()
    logger.info(f"Test DB state: {debug_info}")
```

## Security Considerations

### 🔒 **Connection Security**

```python
# Sanitized URL logging (credentials removed)
sanitized_url: str = db_url.split("@")[1] if "@" in db_url else db_url
logger.info(f"DB URL: ...@{sanitized_url}")
```

**Security Features:**

- Database credentials excluded from logs
- Sanitized connection strings in debug output
- Secure handling of database URLs in error messages

### 🛡️ **Connection Isolation**

```python
# Test-specific application names for isolation
"application_name": f"reviewpoint_test_{worker_id}_{process_id}"

# Connection reset between operations
"pool_reset_on_return": "commit"
```

**Isolation Mechanisms:**

- Unique application names prevent connection mixing
- Connection pool isolation between environments
- Automatic connection reset for security

## Best Practices

### ✅ **Do's**

- **Use Dependency Injection**: Always use `Depends(get_async_session)` in FastAPI endpoints
- **Monitor Health**: Implement health checks using `db_healthcheck()`
- **Handle Errors**: Catch `SQLAlchemyError` for database-specific error handling
- **Debug with Info**: Use `get_connection_debug_info()` for troubleshooting
- **Test Isolation**: Let the module handle parallel test configuration automatically

### ❌ **Don'ts**

- **Direct Engine Access**: Don't create engines manually; use the module's functions
- **Session Leaks**: Don't forget to close sessions; use context manager pattern
- **Blocking Operations**: Don't use synchronous database operations in async code
- **Pool Exhaustion**: Don't create excessive concurrent sessions
- **Credentials in Logs**: Don't log raw database URLs with credentials

## Error Reference

### Common Error Scenarios

#### Connection Pool Exhaustion

```python
# Symptom: TimeoutError or pool checkout timeout
# Solution: Reduce concurrent operations or increase pool size
```

#### Database Unavailable

```python
# Symptom: Connection refused or timeout
# Solution: Check database service status and connectivity
```

#### Session Lifecycle Issues

```python
# Symptom: Session already closed errors
# Solution: Use proper context manager pattern
```

## Related Files

- **`config.py`** - Database URL and environment configuration
- **`models/`** - SQLAlchemy model definitions using these sessions
- **`api/deps.py`** - FastAPI dependencies using database sessions
- **`alembic/`** - Database migration using engine configuration
- **`tests/`** - Test fixtures and database test utilities

## Dependencies

- **`sqlalchemy`** - Core async database toolkit
- **`asyncpg`** - PostgreSQL async driver
- **`aiosqlite`** - SQLite async driver
- **`loguru`** - Comprehensive logging system
- **`typing_extensions`** - Enhanced type annotations

---

_This module provides the foundational database infrastructure for the entire ReViewPoint backend, offering robust connection management, comprehensive monitoring, and environment-specific optimization for development, testing, and production deployments._
