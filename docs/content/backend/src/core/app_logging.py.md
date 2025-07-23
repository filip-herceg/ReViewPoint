# app_logging.py - Centralized Logging Configuration System

## Purpose

Provides centralized, repeat-safe logging configuration for the ReViewPoint backend using Loguru as the primary logging framework. This module handles initialization of logging infrastructure with support for console output, file logging, JSON formatting, and seamless integration with standard Python logging while maintaining compatibility with testing frameworks.

## Key Components

### Core Functionality

#### **init_logging() Function**

- **Purpose**: Main entry point for configuring the application's logging system
- **Design**: Repeat-safe initialization that can be called multiple times without side effects
- **Features**: Console/file output, JSON formatting, color support, test environment detection
- **Integration**: Replaces Python's standard logging with Loguru while maintaining compatibility

#### **Environment Detection**

- **Purpose**: Automatically detects testing environments to prevent file logging conflicts
- **Implementation**: Multi-method detection using environment variables, sys.modules, and command-line arguments
- **Benefits**: Prevents file handle conflicts during parallel test execution

#### **Color Management**

- **Purpose**: Provides ANSI color codes for different log levels
- **Implementation**: Immutable mapping with predefined color schemes
- **Usage**: Enhances console readability with color-coded log levels

### Technical Architecture

#### **Loguru Integration**

```python
# Centralized logging configuration
from core.app_logging import init_logging

# Initialize with development settings
init_logging(level="DEBUG", color=True, json_format=False, logfile="app.log")

# Use in modules
from loguru import logger
logger.info("Application started")
```

#### **Handler Management**

```python
class InterceptHandler(logging.Handler):
    """Intercepts standard logging calls and routes them to Loguru"""
    def emit(self, record: logging.LogRecord) -> None:
        # Convert standard logging to Loguru format
        # Maintains proper stack depth for accurate source location
        # Preserves exception information
```

#### **Test Environment Handling**

```python
def _is_testing() -> bool:
    """Multi-method test environment detection"""
    return (
        "PYTEST_CURRENT_TEST" in os.environ or  # Pytest environment variable
        "pytest" in sys.modules or             # Pytest module loaded
        any("test" in arg.lower() for arg in sys.argv)  # Command line detection
    )
```

## Dependencies

### External Libraries

- **loguru**: Primary logging framework providing structured, colored logging
- **pathlib**: Modern path handling for log file creation
- **logging**: Standard library integration for third-party compatibility

### Internal Dependencies

- **No internal dependencies**: Standalone module to prevent circular imports
- **Core module**: Foundation for all other backend logging needs

### Configuration Integration

- **Environment detection**: Automatic test environment handling
- **File management**: Safe log file creation with directory structure handling

## Integration Patterns

### Application Startup

```python
# In main.py or application initialization
from core.app_logging import init_logging

def create_app():
    # Initialize logging first, before other components
    init_logging(
        level=settings.LOG_LEVEL,
        color=not settings.JSON_LOGS,
        json_format=settings.JSON_LOGS,
        logfile=settings.LOG_FILE
    )
    # Continue with app setup...
```

### Module Usage Pattern

```python
# In any backend module
from loguru import logger

def some_function():
    logger.info("Function called")
    try:
        # Business logic
        logger.debug("Processing data")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise
```

### Testing Integration

```python
# Automatic test environment detection prevents file logging
# Pytest handlers remain intact for test capturing
# Colors and formatting maintained for test readability

def test_with_logging():
    logger.info("Test message")  # Captured by pytest
    assert some_condition()
```

## Configuration Options

### Logging Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General information messages (default)
- **WARNING**: Warning messages for unusual conditions
- **ERROR**: Error conditions that don't stop execution
- **CRITICAL**: Critical errors that may stop execution

### Output Formats

- **Human-readable**: Colored, formatted output for development
- **JSON**: Structured output for production log aggregation
- **Console**: Standard output with optional colors
- **File**: Persistent logging with UTF-8 encoding

### Environment Adaptations

- **Development**: Color output, debug level, file logging
- **Production**: JSON format, structured output, centralized logging
- **Testing**: Console only, pytest integration, no file conflicts

## Error Handling

### Initialization Safety

```python
# Remove all existing loguru handlers safely
try:
    loguru_logger.remove()
except (ValueError, OSError):
    # Ignore errors during cleanup
    pass
```

### File Logging Protection

```python
# Optional file sink with test environment protection
if logfile is not None and not _is_testing():
    fp: Path = Path(logfile)
    fp.parent.mkdir(parents=True, exist_ok=True)  # Safe directory creation
    loguru_logger.add(str(fp), level=level, serialize=json_format, encoding="utf-8")
```

### Handler Integration Robustness

```python
# Safe level conversion with fallback
try:
    log_level = loguru_logger.level(record.levelname).name
except ValueError:
    log_level = str(record.levelno)  # Numeric fallback
```

## Performance Considerations

### Lazy Initialization

- **Repeat-safe**: Multiple calls don't create duplicate handlers
- **Cleanup**: Proper handler removal prevents memory leaks
- **Efficiency**: Minimal overhead for logging operations

### Test Performance

- **File avoidance**: No file I/O during tests for faster execution
- **Handler preservation**: Pytest handlers remain for test capturing
- **Memory management**: Clean handler lifecycle

### Production Optimization

- **JSON serialization**: Efficient structured logging for log aggregation
- **Level filtering**: Early filtering reduces processing overhead
- **Buffer management**: Proper file buffering for high-throughput logging

## Security Considerations

### File System Safety

- **Directory creation**: Safe creation of log directories with proper permissions
- **Path validation**: Uses pathlib for safe file path handling
- **Encoding**: UTF-8 encoding prevents character set issues

### Information Disclosure

- **Level control**: Appropriate log levels prevent sensitive information leakage
- **Test isolation**: No file logging during tests prevents data exposure
- **Handler isolation**: Clean separation between application and test logging

## Usage Examples

### Basic Initialization

```python
from core.app_logging import init_logging

# Development setup
init_logging(level="DEBUG", color=True, logfile="debug.log")

# Production setup
init_logging(level="INFO", json_format=True, color=False)

# Testing setup (automatic detection)
init_logging(level="DEBUG")  # File logging automatically disabled
```

### Advanced Configuration

```python
# Environment-aware initialization
import os
from core.app_logging import init_logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
JSON_LOGS = os.getenv("JSON_LOGS", "false").lower() == "true"
LOG_FILE = os.getenv("LOG_FILE", "app.log")

init_logging(
    level=LOG_LEVEL,
    json_format=JSON_LOGS,
    color=not JSON_LOGS,
    logfile=LOG_FILE if not JSON_LOGS else None
)
```

### Module Integration

```python
from loguru import logger

class UserService:
    def create_user(self, user_data):
        logger.info(f"Creating user: {user_data.email}")
        try:
            # User creation logic
            logger.debug("User validation passed")
            user = self.repository.create(user_data)
            logger.info(f"User created successfully: {user.id}")
            return user
        except ValueError as e:
            logger.warning(f"User creation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            raise
```

## Testing Integration

### Pytest Compatibility

```python
# Automatic test detection maintains pytest log capturing
def test_logging_integration():
    from loguru import logger
    logger.info("Test message")  # Captured by pytest
    # Test assertions...
```

### Log Testing

```python
from loguru import logger
import pytest
from _pytest.logging import LogCaptureFixture

def test_service_logging(caplog: LogCaptureFixture):
    with caplog.at_level("INFO"):
        service.perform_operation()
        assert "Operation completed" in caplog.text
```

## Related Files

- **[main.py](../main.py.md)**: Application startup and logging initialization
- **[config.py](config.py.md)**: Configuration settings for logging parameters
- **[database.py](database.py.md)**: Database operations with integrated logging
- **[security.py](security.py.md)**: Authentication operations with security logging
- **[../middlewares/logging.py](../middlewares/logging.py.md)**: HTTP request/response logging middleware

## Migration Notes

### From Standard Logging

```python
# Old pattern
import logging
logger = logging.getLogger(__name__)
logger.info("Message")

# New pattern
from loguru import logger
logger.info("Message")
```

### Configuration Migration

```python
# Old logging.yaml configuration
# Replace with init_logging() calls in application startup
# Centralized configuration instead of external files
```

The app_logging.py module provides the foundation for all logging operations in the ReViewPoint backend, ensuring consistent, efficient, and test-friendly logging across the entire application while maintaining compatibility with existing Python logging ecosystem components.
