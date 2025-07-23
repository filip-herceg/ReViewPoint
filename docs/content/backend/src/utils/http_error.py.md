# HTTP Error Utilities - Centralized Error Handling with Logging

## Purpose

The http_error module provides a centralized utility for handling HTTP errors with integrated logging throughout the ReViewPoint backend. This module ensures consistent error reporting and logging patterns across all API endpoints, making debugging and monitoring more effective while maintaining clean separation between error handling and business logic.

## Key Components

### Core Function

**`http_error()`** - Centralized HTTP error handler with logging

- Raises HTTPException with automatic logging integration
- Supports custom logging functions and extra metadata
- Provides exception chaining for better error traceability
- Handles both structured and fallback logging formats

### Type Definitions

**`ExtraLogInfo`** - TypedDict for structured logging metadata

- Supports user_id, request_id, action, error_code fields
- Extensible design for additional context information
- Uses Literal types for action enumeration (login, logout, create, update, delete)
- Total=False allows partial information in log entries

**`DEFAULT_LOGGER_FUNC`** - Standard logging function reference

- Uses loguru.logger.error as the default logging mechanism
- Provides consistent logging behavior across the application
- Can be overridden for specific use cases or testing

## Function Signature

```python
def http_error(
    status_code: int,
    detail: str,
    logger_func: Callable[[str], None] = DEFAULT_LOGGER_FUNC,
    extra: ExtraLogInfo | None = None,
    exc: BaseException | None = None,
) -> None
```

## Usage Patterns

### Basic Error Handling

```python
# Simple HTTP error with automatic logging
http_error(404, "User not found")

# HTTP error with status code and custom message
http_error(403, "Insufficient permissions")
```

### Enhanced Error Context

```python
# Error with structured logging metadata
http_error(
    status_code=400,
    detail="Invalid user data",
    extra={
        "user_id": 123,
        "action": "update",
        "error_code": 1001
    }
)
```

### Exception Chaining

```python
# Chain original exception for debugging
try:
    dangerous_operation()
except ValueError as e:
    http_error(
        status_code=422,
        detail="Data validation failed",
        exc=e
    )
```

## Error Handling Strategy

### Logging Behavior

- **Structured Logging**: Attempts loguru-style extra parameter logging first
- **Fallback Logging**: Falls back to string concatenation if structured logging fails
- **Flexible Integration**: Accepts custom logger functions for testing or special cases
- **Context Preservation**: Maintains original exception context through chaining

### Exception Flow

1. Log error details with provided or default logger function
2. Include structured metadata when available
3. Raise HTTPException with specified status code and detail message
4. Chain original exception if provided for debugging purposes

## Integration Points

### API Layer Integration

- Used by all API endpoints for consistent error responses
- Integrates with FastAPI's exception handling system
- Provides automatic HTTP status code mapping
- Maintains request context through structured logging

### Middleware Integration

- Referenced by logging middleware for error tracking
- Supports request ID correlation for distributed tracing
- Enables user action tracking for security monitoring
- Provides standardized error format for monitoring systems

## Security Considerations

### Information Disclosure

- Error details are sanitized for external consumption
- Internal error context is preserved in logs only
- User-specific information is tracked but not exposed in responses
- Exception chaining maintains debugging context internally

### Audit Trail

- All HTTP errors are automatically logged with context
- User actions are tracked for security monitoring
- Request correlation enables attack pattern detection
- Structured logging supports automated security analysis

## Performance Characteristics

### Logging Efficiency

- Lazy evaluation of extra information to minimize overhead
- Efficient fallback mechanism for unsupported logging formats
- Minimal string formatting for performance-critical paths
- Optimized for high-frequency error scenarios

### Memory Management

- No persistent state maintained between calls
- Automatic cleanup of logging context
- Efficient TypedDict usage for metadata structures
- Minimal allocation overhead for error handling

## Testing Considerations

### Mock Integration

- Supports custom logger functions for testing isolation
- Predictable exception raising behavior for test assertions
- Structured metadata enables test verification of log content
- Exception chaining allows verification of error causes

### Error Simulation

- Consistent error format enables automated testing
- Supports both positive and negative test cases
- Enables integration testing of error handling workflows
- Facilitates load testing of error scenarios

## Related Files

- [`../core/app_logging.py`](../core/app_logging.py.md) - Core logging configuration and setup
- [`../middlewares/logging.py`](../middlewares/logging.py.md) - Request logging middleware integration
- [`../../api/v1/auth.py`](../api/v1/auth.py.md) - Authentication error handling examples
- [`../../api/v1/users/core.py`](../api/v1/users/core.py.md) - User management error scenarios
- [`../errors.py`](errors.py.md) - Custom exception definitions and error types

## Future Enhancements

### Advanced Features

- Automatic error categorization and classification
- Integration with external monitoring and alerting systems
- Rate limiting for error logging to prevent log flooding
- Custom error templates for different error types

### Monitoring Integration

- Metrics collection for error frequency and patterns
- Health check integration for error rate monitoring
- Dashboard integration for real-time error analysis
- Automated incident creation for critical error patterns
