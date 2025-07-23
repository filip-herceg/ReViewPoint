# Application Logging Module

**File:** `backend/src/core/app_logging.py`  
**Purpose:** Centralized logging configuration and setup for ReViewPoint backend  
**Lines of Code:** 140  
**Type:** Core Infrastructure Module  

## Overview

The application logging module provides centralized logging configuration using Loguru as the primary logging framework for the ReViewPoint backend. It offers flexible output formats (human-readable and JSON), color-coded console output, optional file logging, and seamless integration with Python's standard logging framework. The module is designed to be repeat-safe and testing-friendly with automatic test environment detection.

## Architecture

### Core Design Principles

1. **Loguru Foundation**: Uses Loguru for superior logging capabilities
2. **Repeat-Safe Initialization**: Can be called multiple times without issues
3. **Test Environment Awareness**: Automatic test detection with appropriate handling
4. **Flexible Output Formats**: Support for human-readable and JSON formats
5. **Standard Library Integration**: Intercepts standard logging for unified output
6. **Color-Coded Output**: Enhanced readability with configurable colors

### Key Components

#### Color Configuration
```python
COLOR_MAP: Final[Mapping[LevelName, str]] = {
    "DEBUG": "\x1b[36m",     # cyan
    "INFO": "\x1b[32m",      # green  
    "WARNING": "\x1b[33m",   # yellow
    "ERROR": "\x1b[31m",     # red
    "CRITICAL": "\x1b[41m",  # red background
}
```

ANSI color codes for different log levels to improve visual parsing of log output.

#### Test Environment Detection
```python
def _is_testing() -> bool:
    """Check if we're currently running in a test environment."""
```

Automatically detects testing environments to adjust logging behavior (disable file logging, etc.).

## Core Functions

### 🔧 **Primary Configuration Function**

#### `init_logging()`
```python
def init_logging(
    *,
    level: str = "INFO",
    color: bool = True,
    json_format: bool = False,
    json: bool = False,
    logfile: str | None = None,
) -> None:
    """Configure loguru as the main logger for the backend."""
```

**Purpose:** Primary entry point for configuring the entire logging system

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `color` | `bool` | `True` | Enable ANSI colors for console output |
| `json_format` | `bool` | `False` | Emit JSON lines instead of human format |
| `json` | `bool` | `False` | Alternative parameter for JSON format |
| `logfile` | `str \| None` | `None` | Optional file path for log output |

**Configuration Process:**
1. **Handler Cleanup**: Safely removes all existing Loguru handlers
2. **Console Sink Setup**: Configures stdout with specified format and colors
3. **File Sink Setup**: Optionally configures file output (disabled during tests)
4. **Standard Library Integration**: Sets up interception of standard logging
5. **Framework Integration**: Configures third-party logging (uvicorn, etc.)

### 📝 **Console Output Configuration**

#### Human-Readable Format
```python
# Default console format with colors and structured layout
format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>"
```

**Format Components:**
- **Timestamp**: Green-colored ISO format (`2024-01-15 14:30:45`)
- **Level**: Color-coded level name with padding (`INFO    `, `ERROR   `)
- **Logger Name**: Cyan-colored module/logger name
- **Message**: Level-colored log message content

**Example Output:**
```
2024-01-15 14:30:45 | INFO     | src.api.auth | User authentication successful
2024-01-15 14:30:46 | ERROR    | src.core.database | Database connection failed
2024-01-15 14:30:47 | DEBUG    | src.services.user | Loading user profile for ID: 123
```

#### JSON Format
```python
# Structured JSON output for log aggregation systems
loguru_logger.add(sys.stdout, level=level, serialize=True, colorize=False)
```

**JSON Structure:**
```json
{
  "text": "User authentication successful",
  "record": {
    "elapsed": {"repr": "0:00:00.123456", "total": 0.123456},
    "exception": null,
    "extra": {},
    "file": {"name": "auth.py", "path": "/path/to/auth.py"},
    "function": "authenticate_user",
    "level": {"icon": "ℹ️", "name": "INFO", "no": 20},
    "line": 42,
    "message": "User authentication successful",
    "module": "auth",
    "name": "src.api.auth",
    "process": {"id": 1234, "name": "MainProcess"},
    "thread": {"id": 5678, "name": "MainThread"},
    "time": {"repr": "2024-01-15T14:30:45.123456+00:00", "timestamp": 1705330245.123456}
  }
}
```

### 📁 **File Logging Configuration**

#### File Output Setup
```python
if logfile is not None and not _is_testing():
    fp: Path = Path(logfile)
    fp.parent.mkdir(parents=True, exist_ok=True)
    loguru_logger.add(
        str(fp), 
        level=level, 
        serialize=(json or json_format), 
        encoding="utf-8"
    )
```

**File Logging Features:**
- **Automatic Directory Creation**: Creates parent directories if they don't exist
- **Test Environment Protection**: Disabled during testing to prevent file handle conflicts
- **Format Consistency**: Uses same format as console (human or JSON)
- **UTF-8 Encoding**: Ensures proper character handling for international content

**Usage Examples:**
```python
# Basic file logging
init_logging(logfile="logs/app.log")

# JSON file logging for log aggregation
init_logging(logfile="logs/app.jsonl", json_format=True)

# Development logging with debug level
init_logging(level="DEBUG", logfile="logs/debug.log")
```

### 🔌 **Standard Library Integration**

#### InterceptHandler Class
```python
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Converts standard logging records to Loguru format
```

**Purpose:** Intercepts Python standard library logging calls and routes them through Loguru

**Integration Process:**
1. **Handler Replacement**: Replaces all root logging handlers with InterceptHandler
2. **Level Mapping**: Maps standard logging levels to Loguru levels
3. **Frame Detection**: Maintains proper stack trace depth for accurate source location
4. **Exception Propagation**: Preserves exception information in log records

**Benefits:**
- **Unified Output**: All logging appears in consistent Loguru format
- **Third-Party Integration**: FastAPI, SQLAlchemy, etc. logs appear unified
- **Source Tracking**: Maintains accurate file/line information
- **Exception Handling**: Preserves full exception context

### 🧪 **Test Environment Handling**

#### Test Detection Logic
```python
def _is_testing() -> bool:
    """Check if we're currently running in a test environment."""
    import os
    import sys
    
    return (
        "PYTEST_CURRENT_TEST" in os.environ
        or "pytest" in sys.modules
        or any("test" in arg.lower() for arg in sys.argv)
    )
```

**Detection Methods:**
- **Environment Variable**: Checks for `PYTEST_CURRENT_TEST`
- **Module Detection**: Looks for pytest in loaded modules
- **Command Line**: Scans argv for test-related arguments

**Test-Specific Behavior:**
- **File Logging Disabled**: Prevents file handle conflicts in parallel tests
- **Handler Preservation**: Maintains pytest-caplog and other test handlers
- **Format Consistency**: Applies unified formatting to captured test logs

## Configuration Integration

### Configuration from Settings

```python
from src.core.config import get_settings
from src.core.app_logging import init_logging

# Initialize logging based on configuration
settings = get_settings()
init_logging(
    level=settings.log_level,           # INFO, DEBUG, ERROR, etc.
    color=True,                         # Enable colors for development
    json_format=settings.environment == "prod",  # JSON in production
    logfile=f"logs/{settings.app_name}.log"
)
```

### Environment-Specific Configuration

#### Development Environment
```python
# Enhanced debugging with colors and file output
init_logging(
    level="DEBUG",
    color=True,
    json_format=False,
    logfile="logs/development.log"
)
```

#### Production Environment
```python
# Structured logging for log aggregation systems
init_logging(
    level="INFO",
    color=False,           # No colors in production
    json_format=True,      # JSON for log aggregation
    logfile="logs/production.jsonl"
)
```

#### Testing Environment
```python
# Minimal logging during tests
init_logging(
    level="WARNING",       # Reduce noise during tests
    color=False,           # No colors in CI/CD
    json_format=False,     # Human readable for debugging
    logfile=None           # No file logging (automatic)
)
```

## Usage Patterns

### Basic Application Startup

```python
# Application entry point
from src.core.app_logging import init_logging
from src.core.config import get_settings

def create_app():
    """Create FastAPI application with proper logging."""
    settings = get_settings()
    
    # Initialize logging first
    init_logging(
        level=settings.log_level,
        json_format=settings.environment == "prod",
        logfile=f"logs/{settings.app_name}.log"
    )
    
    # Now safe to use logger
    from loguru import logger
    logger.info("Starting ReViewPoint backend")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Create FastAPI app...
    return app
```

### Module-Level Logging

```python
# In any module throughout the application
from loguru import logger

class UserService:
    async def create_user(self, user_data: dict):
        logger.info("Creating new user: {}", user_data.get("username"))
        
        try:
            # Database operations
            user = await self.db.create_user(user_data)
            logger.info("User created successfully: {}", user.id)
            return user
            
        except Exception as e:
            logger.error("Failed to create user: {}", str(e))
            logger.exception("Full exception details:")
            raise
```

### Structured Logging with Context

```python
from loguru import logger

# Add contextual information to logs
logger = logger.bind(
    request_id="req-123-456",
    user_id="user-789",
    operation="user_update"
)

logger.info("Processing user update request")
logger.debug("Validating user data: {}", user_data)
logger.warning("User attempted to update restricted field")
```

### Performance Monitoring

```python
import time
from loguru import logger

def timed_operation(operation_name: str):
    """Decorator for timing operations."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"Starting {operation_name}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {operation_name} in {duration:.3f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {operation_name} after {duration:.3f}s: {e}")
                raise
                
        return wrapper
    return decorator

@timed_operation("database_query")
async def fetch_user_data(user_id: int):
    # Database operation
    pass
```

## Security and Privacy

### 🔒 **Sensitive Data Handling**

```python
from loguru import logger

# Safe logging practices
def log_user_activity(user_id: int, action: str, details: dict):
    # ✅ Log user ID (not PII)
    logger.info("User activity - ID: {}, Action: {}", user_id, action)
    
    # ✅ Log non-sensitive details
    safe_details = {k: v for k, v in details.items() 
                   if k not in ["password", "email", "ssn", "credit_card"]}
    logger.debug("Activity details: {}", safe_details)
    
    # ❌ Never log sensitive information
    # logger.info("User login: {}", {"password": "secret123"})  # DON'T DO THIS
```

### 🛡️ **Error Logging Security**

```python
from loguru import logger

def secure_error_logging():
    try:
        # Operations that might fail
        pass
    except Exception as e:
        # ✅ Log error type and general message
        logger.error("Database operation failed: {}", type(e).__name__)
        
        # ✅ Log stack trace for debugging (be careful in production)
        logger.exception("Full error details:")
        
        # ❌ Don't log sensitive error details in production
        if settings.environment != "prod":
            logger.debug("Detailed error: {}", str(e))
```

## Performance Considerations

### ⚡ **Logging Efficiency**

```python
from loguru import logger

# Efficient logging patterns
def efficient_logging():
    # ✅ Use appropriate log levels
    logger.debug("Detailed debugging info")      # Only in debug mode
    logger.info("Important application events")  # Always visible
    logger.error("Error conditions")             # Always visible
    
    # ✅ Use lazy evaluation for expensive operations
    logger.debug("Complex data: {}", lambda: expensive_serialization())
    
    # ✅ Use structured logging for searchability
    logger.info("User action", extra={
        "user_id": user.id,
        "action": "login",
        "ip_address": request.client.host
    })
```

### 🔄 **Log Rotation and Management**

```python
# For production deployments, consider external log rotation
init_logging(
    level="INFO",
    json_format=True,
    logfile="logs/app.jsonl"  # Use external rotation (logrotate, etc.)
)

# Or use Loguru's built-in rotation
from loguru import logger

logger.add(
    "logs/app.log",
    rotation="100 MB",     # Rotate when file reaches 100MB
    retention="30 days",   # Keep logs for 30 days
    compression="zip",     # Compress old logs
    level="INFO"
)
```

## Integration Examples

### FastAPI Application Integration

```python
from fastapi import FastAPI, Request
from loguru import logger
from src.core.app_logging import init_logging

# Initialize logging before creating app
init_logging(level="INFO", json_format=False)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()
    
    logger.info(
        "Request started: {} {}",
        request.method,
        request.url.path
    )
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        "Request completed: {} {} - {} in {:.3f}s",
        request.method,
        request.url.path,
        response.status_code,
        duration
    )
    
    return response
```

### Database Integration

```python
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

async def database_operation_with_logging(session: AsyncSession):
    """Example of database operations with proper logging."""
    logger.debug("Starting database transaction")
    
    try:
        # Database operations
        result = await session.execute(query)
        await session.commit()
        
        logger.info("Database transaction completed successfully")
        return result
        
    except Exception as e:
        await session.rollback()
        logger.error("Database transaction failed: {}", str(e))
        logger.exception("Full exception details:")
        raise
    finally:
        logger.debug("Database session cleanup completed")
```

## Testing Integration

### Test-Friendly Logging

```python
import pytest
from loguru import logger
from src.core.app_logging import init_logging

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Configure logging for test environment."""
    init_logging(
        level="WARNING",  # Reduce noise during tests
        color=False,      # No colors in CI/CD
        json_format=False,
        logfile=None      # No file logging during tests
    )

def test_logging_capture(caplog):
    """Test that logging works correctly."""
    logger.info("Test log message")
    
    # Verify log was captured
    assert "Test log message" in caplog.text
    assert caplog.records[0].levelname == "INFO"
```

### Debug Logging in Tests

```python
def test_with_debug_logging():
    """Enable debug logging for specific test."""
    with logger.contextualize(test_case="user_creation"):
        logger.debug("Starting user creation test")
        
        # Test operations
        result = create_user({"username": "test_user"})
        
        logger.debug("User creation test completed: {}", result.id)
```

## Best Practices

### ✅ **Do's**

- **Initialize Early**: Call `init_logging()` before any other logging operations
- **Use Structured Logging**: Include contextual information in log messages
- **Appropriate Levels**: Use DEBUG for development, INFO for events, ERROR for problems
- **Lazy Evaluation**: Use lambda functions for expensive log message generation
- **Exception Context**: Use `logger.exception()` to capture full stack traces
- **Security Conscious**: Never log sensitive information (passwords, tokens, PII)

### ❌ **Don'ts**

- **Don't Log Secrets**: Never log passwords, API keys, or sensitive data
- **Don't Over-Log**: Avoid excessive debug logging in production
- **Don't Block**: Avoid synchronous operations in log message generation
- **Don't Hardcode Levels**: Use configuration for log levels
- **Don't Ignore Errors**: Don't catch and silently log critical errors
- **Don't Mix Formats**: Use consistent format (human vs JSON) within environment

## Error Handling

### Common Issues and Solutions

#### File Permission Errors
```python
try:
    init_logging(logfile="/var/log/app.log")
except OSError as e:
    # Fallback to user directory or disable file logging
    logger.warning("Cannot write to log file: {}", e)
    init_logging(logfile=None)
```

#### Handler Conflicts
```python
# The module handles this automatically, but be aware:
# Multiple init_logging() calls are safe
init_logging(level="INFO")    # First call
init_logging(level="DEBUG")   # Second call - safely reconfigures
```

## Related Files

- **`config.py`** - Provides log level and environment configuration
- **`main.py`** - Application startup using logging initialization
- **`api/`** - API endpoints using logger for request/response logging
- **`services/`** - Business logic using logger for operation tracking
- **`models/`** - Database models using logger for data operations

## Dependencies

- **`loguru`** - Primary logging framework with advanced features
- **`pathlib`** - Path handling for log file creation
- **Standard `logging`** - Integration with Python's logging framework

---

*This module provides the foundational logging infrastructure for the entire ReViewPoint backend, offering flexible, efficient, and secure logging capabilities with seamless integration across all application components.*
