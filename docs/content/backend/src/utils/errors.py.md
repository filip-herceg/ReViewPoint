# utils/errors.py - Custom Exception Classes

## Purpose

The `utils/errors.py` module defines a comprehensive hierarchy of custom exception classes for the ReViewPoint platform. It provides structured error handling with specific exception types for different error scenarios, enabling precise error handling and appropriate HTTP status code mapping.

## Key Components

### Base Exception Class

#### User Repository Error Hierarchy

```python
from typing import Final

class UserRepositoryError(Exception):
    """Base exception for user repository errors."""
```

### User-Specific Exceptions

#### User Not Found Exception

```python
class UserNotFoundError(UserRepositoryError):
    """Raised when a user is not found in the repository."""

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)
```

**Usage Example:**
```python
# In repository layer
async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    return user

# In API layer
try:
    user = await user_repo.get_user_by_id(session, user_id)
except UserNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

#### User Already Exists Exception

```python
class UserAlreadyExistsError(UserRepositoryError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)
```

**Usage Example:**
```python
# In service layer
async def register_user(session: AsyncSession, email: str, password: str) -> User:
    existing_user = await user_repo.get_user_by_email(session, email)
    if existing_user:
        raise UserAlreadyExistsError(f"User with email {email} already exists")
    
    return await user_repo.create_user(session, email, password)

# In API layer
try:
    user = await user_service.register_user(session, email, password)
except UserAlreadyExistsError as e:
    raise HTTPException(status_code=409, detail=str(e))
```

### Validation Exceptions

#### General Validation Exception

```python
class ValidationError(UserRepositoryError):
    """Raised when user input fails validation checks."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)
```

**Usage Example:**
```python
# In validation utilities
def validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise ValidationError("Invalid email format")

# In service layer
try:
    validate_email(user_email)
    validate_password(user_password)
except ValidationError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

#### Invalid Data Exception

```python
class InvalidDataError(UserRepositoryError):
    """Raised when user input data is invalid but not a validation error."""

    def __init__(self, message: str = "Invalid data") -> None:
        super().__init__(message)
```

**Usage Example:**
```python
# For malformed or structurally invalid data
async def process_user_data(data: dict) -> None:
    if not isinstance(data, dict):
        raise InvalidDataError("Expected dictionary data structure")
    
    required_fields = ["email", "name"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise InvalidDataError(f"Missing required fields: {missing_fields}")
```

### Rate Limiting Exception

#### Rate Limit Exceeded Exception

```python
class RateLimitExceededError(UserRepositoryError):
    """Raised when a user exceeds the allowed rate limit."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)
```

**Usage Example:**
```python
# In rate limiting middleware or service
async def check_rate_limit(user_id: int, action: str) -> None:
    if not await rate_limiter.is_allowed(f"user:{user_id}:{action}"):
        raise RateLimitExceededError(
            f"Too many {action} attempts. Please try again later."
        )

# In API layer
try:
    await check_rate_limit(current_user.id, "login")
    await authenticate_user(credentials)
except RateLimitExceededError as e:
    raise HTTPException(status_code=429, detail=str(e))
```

### Error Code Constants

#### HTTP Status Code Mapping

```python
# Error code constants for consistent HTTP status mapping
USER_NOT_FOUND_CODE: Final[int] = 404
USER_ALREADY_EXISTS_CODE: Final[int] = 409
VALIDATION_ERROR_CODE: Final[int] = 422
RATE_LIMIT_EXCEEDED_CODE: Final[int] = 429
INVALID_DATA_ERROR_CODE: Final[int] = 400
```

**Usage Example:**
```python
# In error handler middleware
def get_http_status_for_exception(exc: Exception) -> int:
    error_mapping = {
        UserNotFoundError: USER_NOT_FOUND_CODE,
        UserAlreadyExistsError: USER_ALREADY_EXISTS_CODE,
        ValidationError: VALIDATION_ERROR_CODE,
        RateLimitExceededError: RATE_LIMIT_EXCEEDED_CODE,
        InvalidDataError: INVALID_DATA_ERROR_CODE,
    }
    
    return error_mapping.get(type(exc), 500)  # Default to 500 for unknown errors
```

## Best Practices

### Exception Hierarchy Design

- Use inheritance to create logical exception hierarchies
- Provide meaningful default messages while allowing customization
- Include relevant context information in exception messages
- Use specific exception types for different error conditions

### Error Handling Patterns

**Service Layer Pattern:**
```python
# Service layer catches repository exceptions and re-raises as appropriate
async def update_user_profile(user_id: int, updates: dict) -> User:
    try:
        return await user_repo.update_user(user_id, updates)
    except UserNotFoundError:
        # Re-raise as-is for API layer to handle
        raise
    except ValidationError as e:
        # Add service-specific context
        raise ValidationError(f"Profile update failed: {e}")
```

**API Layer Pattern:**
```python
# API layer converts exceptions to HTTP responses
@app.put("/users/{user_id}")
async def update_user(user_id: int, updates: UserUpdate):
    try:
        user = await user_service.update_user_profile(user_id, updates.dict())
        return UserResponse.from_orm(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Error Message Guidelines

- Provide clear, actionable error messages
- Include relevant context without exposing sensitive information
- Use consistent language and tone across all error messages
- Avoid technical jargon in user-facing messages

### Logging and Monitoring

**Structured Error Logging:**
```python
import structlog

logger = structlog.get_logger()

try:
    await risky_operation()
except UserRepositoryError as e:
    logger.error(
        "User operation failed",
        error_type=type(e).__name__,
        error_message=str(e),
        user_id=user_id,
        operation="update_profile"
    )
    raise
```

### Testing Exception Handling

**Exception Testing Pattern:**
```python
import pytest

async def test_user_not_found_raises_exception():
    with pytest.raises(UserNotFoundError, match="User with ID 999 not found"):
        await user_repo.get_user_by_id(session, 999)

async def test_api_returns_correct_status_for_user_not_found():
    response = await client.get("/users/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
```

### Integration with FastAPI

**Custom Exception Handler:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(UserRepositoryError)
async def user_repository_exception_handler(
    request: Request, exc: UserRepositoryError
) -> JSONResponse:
    status_code = get_http_status_for_exception(exc)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(exc).__name__,
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )
```

This error handling system provides a robust foundation for consistent error management across the application, enabling proper error propagation, logging, and user feedback while maintaining security and debugging capabilities.
