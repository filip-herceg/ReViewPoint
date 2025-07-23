# Error Utilities Documentation

## Purpose

The `errors.py` module defines a comprehensive hierarchy of custom exception classes for the ReViewPoint application. This module standardizes error handling across the user repository and related components, providing specific exception types for different error conditions with consistent messaging and HTTP status code mapping. The error hierarchy enables precise error handling, logging, and API response generation throughout the application.

## Architecture

The error system follows a hierarchical exception design:

- **Base Exception**: Single root exception for all user repository errors
- **Specific Exceptions**: Dedicated exception types for distinct error conditions
- **HTTP Mapping**: Direct correlation between exceptions and HTTP status codes
- **Message Standardization**: Consistent default messages with customization support
- **Type Safety**: Full type annotations for reliable exception handling
- **Extensibility**: Easy to extend for new error types and use cases

## Exception Hierarchy

### Base Exception

**UserRepositoryError:**

```python
class UserRepositoryError(Exception):
    """Base exception for user repository errors."""
```

**Design Purpose:**

- **Single Root**: All user-related exceptions inherit from this base
- **Catch-All**: Enables catching all user repository errors with single except clause
- **Consistency**: Ensures all user errors follow same exception interface
- **Future-Proof**: Easy to add common functionality to all user exceptions

**Usage Pattern:**

```python
try:
    user = await user_repository.get_user_by_id(user_id)
except UserRepositoryError as e:
    # Handles all user repository errors
    logger.error(f"User repository error: {e}")
    return {"error": "User operation failed"}
```

### Specific Exception Classes

**User Not Found Error:**

```python
class UserNotFoundError(UserRepositoryError):
    """Raised when a user is not found in the repository."""

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)
```

**User Already Exists Error:**

```python
class UserAlreadyExistsError(UserRepositoryError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)
```

**Validation Error:**

```python
class ValidationError(UserRepositoryError):
    """Raised when user input fails validation checks."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)
```

**Rate Limit Exceeded Error:**

```python
class RateLimitExceededError(UserRepositoryError):
    """Raised when a user exceeds the allowed rate limit."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)
```

**Invalid Data Error:**

```python
class InvalidDataError(UserRepositoryError):
    """Raised when user input data is invalid but not a validation error."""

    def __init__(self, message: str = "Invalid data") -> None:
        super().__init__(message)
```

## HTTP Status Code Mapping

### Error Code Constants

**HTTP Status Code Mapping:**

```python
USER_NOT_FOUND_CODE: Final[int] = 404          # Not Found
USER_ALREADY_EXISTS_CODE: Final[int] = 409     # Conflict
VALIDATION_ERROR_CODE: Final[int] = 422        # Unprocessable Entity
RATE_LIMIT_EXCEEDED_CODE: Final[int] = 429     # Too Many Requests
INVALID_DATA_ERROR_CODE: Final[int] = 400      # Bad Request
```

**Error to HTTP Status Mapping:**

| Exception                | HTTP Code | Description             |
| ------------------------ | --------- | ----------------------- |
| `UserNotFoundError`      | 404       | Resource not found      |
| `UserAlreadyExistsError` | 409       | Resource conflict       |
| `ValidationError`        | 422       | Input validation failed |
| `RateLimitExceededError` | 429       | Rate limit exceeded     |
| `InvalidDataError`       | 400       | Malformed request data  |

## Usage Patterns

### Repository Layer Error Handling

**User Repository Implementation:**

```python
from src.utils.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    ValidationError,
    InvalidDataError
)

class UserRepository:
    """User repository with standardized error handling."""

    async def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID with specific error handling."""

        if not user_id or not isinstance(user_id, str):
            raise InvalidDataError(f"Invalid user ID format: {user_id}")

        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            return user

        except SQLAlchemyError as e:
            logger.error(f"Database error getting user {user_id}: {e}")
            raise UserRepositoryError(f"Failed to retrieve user: {e}")

    async def create_user(self, user_data: dict) -> User:
        """Create user with conflict detection."""

        # Validate required fields
        if not user_data.get("email"):
            raise ValidationError("Email is required for user creation")

        # Check for existing user
        existing_user = await self.get_user_by_email(user_data["email"])
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with email {user_data['email']} already exists"
            )

        try:
            user = User(**user_data)
            self.session.add(user)
            await self.session.commit()
            return user

        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower():
                raise UserAlreadyExistsError(
                    f"User with email {user_data['email']} already exists"
                )
            raise UserRepositoryError(f"Failed to create user: {e}")

    async def update_user(self, user_id: str, update_data: dict) -> User:
        """Update user with validation."""

        # Get existing user (raises UserNotFoundError if not found)
        user = await self.get_user_by_id(user_id)

        # Validate update data
        if "email" in update_data:
            if not isinstance(update_data["email"], str):
                raise ValidationError("Email must be a string")

            if not "@" in update_data["email"]:
                raise ValidationError("Invalid email format")

        try:
            # Apply updates
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    raise InvalidDataError(f"Invalid field: {key}")

            await self.session.commit()
            return user

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UserRepositoryError(f"Failed to update user: {e}")
```

### API Layer Error Handling

**FastAPI Error Handler Integration:**

```python
from fastapi import HTTPException
from src.utils.errors import (
    UserRepositoryError,
    UserNotFoundError,
    UserAlreadyExistsError,
    ValidationError,
    RateLimitExceededError,
    InvalidDataError,
    USER_NOT_FOUND_CODE,
    USER_ALREADY_EXISTS_CODE,
    VALIDATION_ERROR_CODE,
    RATE_LIMIT_EXCEEDED_CODE,
    INVALID_DATA_ERROR_CODE
)

def map_exception_to_http_error(exception: UserRepositoryError) -> HTTPException:
    """Map custom exceptions to HTTP exceptions."""

    error_mapping = {
        UserNotFoundError: USER_NOT_FOUND_CODE,
        UserAlreadyExistsError: USER_ALREADY_EXISTS_CODE,
        ValidationError: VALIDATION_ERROR_CODE,
        RateLimitExceededError: RATE_LIMIT_EXCEEDED_CODE,
        InvalidDataError: INVALID_DATA_ERROR_CODE,
    }

    status_code = error_mapping.get(type(exception), 500)

    return HTTPException(
        status_code=status_code,
        detail=str(exception)
    )

# FastAPI endpoint with error handling
@app.get("/users/{user_id}")
async def get_user(user_id: str) -> UserResponse:
    """Get user endpoint with standardized error handling."""

    try:
        user = await user_repository.get_user_by_id(user_id)
        return UserResponse.from_orm(user)

    except UserRepositoryError as e:
        raise map_exception_to_http_error(e)

# Global exception handler
@app.exception_handler(UserRepositoryError)
async def user_repository_exception_handler(request, exc: UserRepositoryError):
    """Global handler for user repository errors."""

    http_exc = map_exception_to_http_error(exc)

    # Log error for monitoring
    logger.error(f"User repository error: {exc}", extra={
        "user_id": getattr(request.state, "user_id", None),
        "endpoint": request.url.path,
        "method": request.method
    })

    return JSONResponse(
        status_code=http_exc.status_code,
        content={"error": http_exc.detail}
    )
```

### Service Layer Error Handling

**User Service with Error Translation:**

```python
from src.utils.errors import (
    UserNotFoundError,
    ValidationError,
    RateLimitExceededError
)

class UserService:
    """User service with business logic error handling."""

    def __init__(self, user_repository: UserRepository, rate_limiter: RateLimiter):
        self.user_repository = user_repository
        self.rate_limiter = rate_limiter

    async def get_user_profile(self, user_id: str, requester_id: str) -> UserProfile:
        """Get user profile with rate limiting and access control."""

        # Check rate limit
        if not await self.rate_limiter.check_limit(requester_id, "profile_access"):
            raise RateLimitExceededError(
                "Too many profile access requests. Please try again later."
            )

        # Get user (may raise UserNotFoundError)
        user = await self.user_repository.get_user_by_id(user_id)

        # Check access permissions
        if not await self.can_access_profile(requester_id, user_id):
            raise UserNotFoundError("User not found")  # Hide existence for security

        return UserProfile.from_user(user)

    async def update_user_email(self, user_id: str, new_email: str) -> User:
        """Update user email with validation."""

        # Validate email format
        if not self.is_valid_email(new_email):
            raise ValidationError(f"Invalid email format: {new_email}")

        # Check if email is already in use
        try:
            existing_user = await self.user_repository.get_user_by_email(new_email)
            if existing_user and existing_user.id != user_id:
                raise ValidationError("Email address is already in use")
        except UserNotFoundError:
            # Email not in use - good to proceed
            pass

        # Update user
        return await self.user_repository.update_user(
            user_id,
            {"email": new_email}
        )
```

### Background Task Error Handling

**Async Task Error Management:**

```python
import asyncio
from src.utils.errors import UserRepositoryError

async def background_user_cleanup():
    """Background task with comprehensive error handling."""

    try:
        # Get inactive users
        inactive_users = await user_repository.get_inactive_users(days=365)

        for user in inactive_users:
            try:
                await user_repository.deactivate_user(user.id)
                logger.info(f"Deactivated inactive user: {user.id}")

            except UserNotFoundError:
                # User already deleted - skip
                logger.warning(f"User {user.id} not found during cleanup")
                continue

            except UserRepositoryError as e:
                # Log specific user error but continue with others
                logger.error(f"Failed to deactivate user {user.id}: {e}")
                continue

    except UserRepositoryError as e:
        # Log general error
        logger.error(f"User cleanup task failed: {e}")

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in user cleanup: {e}")

# Schedule background task
async def start_background_tasks():
    """Start background tasks with error handling."""

    while True:
        try:
            await background_user_cleanup()
            await asyncio.sleep(3600)  # Run every hour

        except Exception as e:
            logger.error(f"Background task scheduler error: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes
```

## Error Context Enhancement

### Rich Error Information

**Enhanced Exception Classes:**

```python
from typing import Dict, Any, Optional
from datetime import datetime

class EnhancedUserNotFoundError(UserNotFoundError):
    """Enhanced user not found error with context."""

    def __init__(
        self,
        message: str = "User not found",
        user_id: Optional[str] = None,
        search_criteria: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        super().__init__(message)
        self.user_id = user_id
        self.search_criteria = search_criteria or {}
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_type": "UserNotFoundError",
            "message": str(self),
            "user_id": self.user_id,
            "search_criteria": self.search_criteria,
            "timestamp": self.timestamp.isoformat()
        }

class EnhancedValidationError(ValidationError):
    """Enhanced validation error with field-specific details."""

    def __init__(
        self,
        message: str = "Validation error",
        field_errors: Optional[Dict[str, str]] = None,
        invalid_value: Any = None
    ):
        super().__init__(message)
        self.field_errors = field_errors or {}
        self.invalid_value = invalid_value

    def add_field_error(self, field: str, error: str):
        """Add field-specific error."""
        self.field_errors[field] = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-friendly format."""
        return {
            "error_type": "ValidationError",
            "message": str(self),
            "field_errors": self.field_errors,
            "invalid_value": str(self.invalid_value) if self.invalid_value else None
        }

# Usage with enhanced errors
async def validate_user_data(user_data: dict) -> None:
    """Validate user data with detailed error reporting."""

    validation_error = EnhancedValidationError("User data validation failed")

    # Validate email
    if "email" not in user_data:
        validation_error.add_field_error("email", "Email is required")
    elif not isinstance(user_data["email"], str):
        validation_error.add_field_error("email", "Email must be a string")
    elif "@" not in user_data["email"]:
        validation_error.add_field_error("email", "Invalid email format")

    # Validate name
    if "name" in user_data and not isinstance(user_data["name"], str):
        validation_error.add_field_error("name", "Name must be a string")

    # Raise if any errors found
    if validation_error.field_errors:
        validation_error.invalid_value = user_data
        raise validation_error
```

## Error Monitoring and Analytics

### Error Tracking Integration

**Error Metrics Collection:**

```python
from typing import Counter
from datetime import datetime, timedelta

class ErrorMetrics:
    """Collect and analyze error patterns."""

    def __init__(self):
        self.error_counts = Counter()
        self.error_timestamps = []

    def record_error(self, error: UserRepositoryError, context: dict = None):
        """Record error occurrence for analysis."""

        error_type = type(error).__name__
        self.error_counts[error_type] += 1

        error_record = {
            "type": error_type,
            "message": str(error),
            "timestamp": datetime.utcnow(),
            "context": context or {}
        }

        self.error_timestamps.append(error_record)

        # Log for external monitoring
        logger.error(f"Error recorded: {error_type}", extra={
            "error_type": error_type,
            "error_message": str(error),
            "context": context
        })

    def get_error_summary(self, hours: int = 24) -> dict:
        """Get error summary for specified time period."""

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.error_timestamps
            if error["timestamp"] > cutoff_time
        ]

        recent_counts = Counter(error["type"] for error in recent_errors)

        return {
            "period_hours": hours,
            "total_errors": len(recent_errors),
            "error_types": dict(recent_counts),
            "error_rate_per_hour": len(recent_errors) / hours if hours > 0 else 0
        }

# Global error metrics instance
error_metrics = ErrorMetrics()

# Middleware for automatic error tracking
async def error_tracking_middleware(request, call_next):
    """Middleware to track errors automatically."""

    try:
        response = await call_next(request)
        return response

    except UserRepositoryError as e:
        # Record error with request context
        context = {
            "endpoint": request.url.path,
            "method": request.method,
            "user_id": getattr(request.state, "user_id", None)
        }

        error_metrics.record_error(e, context)
        raise
```

## Testing Strategies

### Exception Testing

**Comprehensive Error Testing:**

```python
import pytest
from src.utils.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    ValidationError,
    RateLimitExceededError,
    InvalidDataError,
    UserRepositoryError
)

class TestUserRepositoryErrors:
    """Test suite for user repository errors."""

    def test_user_not_found_error(self):
        """Test UserNotFoundError functionality."""

        # Test default message
        error = UserNotFoundError()
        assert str(error) == "User not found"

        # Test custom message
        custom_error = UserNotFoundError("User with ID 123 not found")
        assert str(custom_error) == "User with ID 123 not found"

        # Test inheritance
        assert isinstance(error, UserRepositoryError)
        assert isinstance(error, Exception)

    def test_user_already_exists_error(self):
        """Test UserAlreadyExistsError functionality."""

        error = UserAlreadyExistsError("Email already registered")
        assert str(error) == "Email already registered"
        assert isinstance(error, UserRepositoryError)

    def test_validation_error(self):
        """Test ValidationError functionality."""

        error = ValidationError("Invalid email format")
        assert str(error) == "Invalid email format"
        assert isinstance(error, UserRepositoryError)

    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError functionality."""

        error = RateLimitExceededError("Too many requests")
        assert str(error) == "Too many requests"
        assert isinstance(error, UserRepositoryError)

    def test_invalid_data_error(self):
        """Test InvalidDataError functionality."""

        error = InvalidDataError("Invalid user ID format")
        assert str(error) == "Invalid user ID format"
        assert isinstance(error, UserRepositoryError)

    def test_error_hierarchy(self):
        """Test error inheritance hierarchy."""

        errors = [
            UserNotFoundError(),
            UserAlreadyExistsError(),
            ValidationError(),
            RateLimitExceededError(),
            InvalidDataError()
        ]

        for error in errors:
            assert isinstance(error, UserRepositoryError)
            assert isinstance(error, Exception)

    def test_exception_catching(self):
        """Test exception catching patterns."""

        def raise_user_not_found():
            raise UserNotFoundError("Test user not found")

        def raise_validation_error():
            raise ValidationError("Test validation error")

        # Test specific exception catching
        with pytest.raises(UserNotFoundError):
            raise_user_not_found()

        # Test base exception catching
        with pytest.raises(UserRepositoryError):
            raise_user_not_found()

        with pytest.raises(UserRepositoryError):
            raise_validation_error()
```

### Integration Error Testing

**Repository Error Integration Testing:**

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.repositories.user import UserRepository
from src.utils.errors import UserNotFoundError, UserAlreadyExistsError

class TestRepositoryErrorIntegration:
    """Test error handling in repository integration."""

    @pytest.fixture
    async def user_repository(self):
        """Create user repository for testing."""
        mock_session = AsyncMock()
        return UserRepository(session=mock_session)

    async def test_user_not_found_integration(self, user_repository):
        """Test UserNotFoundError in repository context."""

        # Mock database returning None
        user_repository.session.execute.return_value.scalar_one_or_none.return_value = None

        with pytest.raises(UserNotFoundError) as exc_info:
            await user_repository.get_user_by_id("nonexistent_id")

        assert "nonexistent_id" in str(exc_info.value)

    async def test_user_already_exists_integration(self, user_repository):
        """Test UserAlreadyExistsError in repository context."""

        # Mock existing user
        existing_user = AsyncMock()
        user_repository.get_user_by_email = AsyncMock(return_value=existing_user)

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await user_repository.create_user({"email": "existing@example.com"})

        assert "existing@example.com" in str(exc_info.value)
```

## Best Practices

### Exception Design

- **Specific Types**: Create specific exception types for distinct error conditions
- **Clear Messages**: Provide descriptive default messages with customization options
- **Consistent Hierarchy**: Use single base exception for related error types
- **HTTP Mapping**: Maintain clear mapping between exceptions and HTTP status codes

### Error Handling Strategy

- **Fail Fast**: Raise exceptions immediately when errors are detected
- **Context Preservation**: Include relevant context in error messages
- **Logging Integration**: Log errors appropriately for monitoring and debugging
- **Recovery Paths**: Design exception handling to enable graceful error recovery

### API Integration

- **Status Code Consistency**: Use consistent HTTP status codes for exception types
- **Client-Friendly Messages**: Provide clear, actionable error messages for API clients
- **Security Considerations**: Avoid exposing sensitive information in error messages
- **Documentation**: Document all possible exceptions for each API endpoint

## Related Files

### Dependencies

- `typing.Final` - Immutable constant annotations for error codes

### Integration Points

- `src.repositories.user` - Primary user of these exception classes
- `src.services.user` - Service layer error handling and translation
- `src.api.v1.users` - API endpoint error handling and HTTP mapping
- `src.core.logging` - Error logging and monitoring integration

### Related Error Handling

- FastAPI exception handlers for HTTP error conversion
- Middleware for automatic error logging and metrics
- Background task error handling and recovery

## Configuration

### Error Handling Settings

```python
# Error handling configuration
ERROR_CONFIG = {
    "log_errors": True,              # Enable error logging
    "include_stack_trace": False,    # Include stack traces in API responses (dev only)
    "error_rate_limit": 100,         # Max errors per hour before alerting
    "enable_error_metrics": True,    # Enable error metrics collection
}

# HTTP status code mapping
HTTP_ERROR_MAPPING = {
    UserNotFoundError: 404,
    UserAlreadyExistsError: 409,
    ValidationError: 422,
    RateLimitExceededError: 429,
    InvalidDataError: 400,
}
```

This error utilities module provides a robust foundation for standardized error handling throughout the ReViewPoint application, enabling consistent error responses, clear debugging information, and reliable exception management across all layers of the application.
