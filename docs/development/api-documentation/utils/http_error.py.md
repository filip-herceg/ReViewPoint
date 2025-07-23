# HTTP Error Utilities Documentation

## Purpose

The `http_error.py` module provides standardized HTTP error handling with integrated logging for the ReViewPoint application. This module combines FastAPI's HTTPException with structured logging to ensure consistent error responses and comprehensive error tracking throughout the application. It enables centralized error handling with rich contextual information for debugging and monitoring.

## Architecture

The HTTP error system follows a unified error handling design:

- **Standardized Responses**: Consistent HTTP error format across all endpoints
- **Integrated Logging**: Automatic logging of errors with contextual information
- **Type Safety**: Comprehensive type annotations for error data structures
- **Flexible Logging**: Configurable logging functions for different error types
- **Exception Chaining**: Proper exception chaining for error traceability
- **Rich Context**: Structured extra information for error analysis

## Type System

### Extra Logging Information

**ExtraLogInfo TypedDict:**

```python
from typing_extensions import TypedDict
from typing import Literal

class ExtraLogInfo(TypedDict, total=False):
    user_id: int                                                   # User identifier
    request_id: str                                               # Request tracking ID
    action: Literal["login", "logout", "create", "update", "delete"]  # Action type
    error_code: int                                               # Internal error code
    # Add more known keys and restrict values with Literal or stricter types as needed
```

**Design Features:**
- **Structured Context**: Predefined fields for common error context
- **Type Safety**: Literal types for action values prevent typos
- **Extensible**: Easy to add new fields while maintaining type safety
- **Optional Fields**: `total=False` allows partial error information
- **Rich Debugging**: Comprehensive context for error analysis

### Logging Function Type

**Logger Function Protocol:**

```python
from collections.abc import Callable

DEFAULT_LOGGER_FUNC: Final[Callable[[str], None]] = logger.error
```

**Integration Features:**
- **Flexible Logging**: Compatible with different logging frameworks
- **Default Behavior**: Uses loguru error logging by default
- **Customizable**: Can be overridden for specific error types
- **Type Safety**: Ensures proper function signature compatibility

## Core Function

### HTTP Error with Logging

**http_error Function:**

```python
def http_error(
    status_code: int,
    detail: str,
    logger_func: Callable[[str], None] = DEFAULT_LOGGER_FUNC,
    extra: ExtraLogInfo | None = None,
    exc: BaseException | None = None,
) -> None:
    """
    Raises an HTTPException with logging.
    
    Args:
        status_code (int): HTTP status code to raise.
        detail (str): Error detail message.
        logger_func (Callable[[str], None]): Logging function to use.
        extra (Optional[Mapping[str, object]]): Additional log info.
        exc (Optional[Exception]): Exception to chain.
    
    Raises:
        HTTPException: Always raised with the given status and detail.
        TypeError: If logger_func signature is incompatible with extra.
    """
```

**Implementation Details:**

1. **Structured Logging with Extra Context:**
   ```python
   if extra is not None:
       try:
           logger_func(detail, extra=extra)  # loguru's logger accepts extra
       except TypeError:
           logger_func(f"{detail} | {extra}")
   ```

2. **Simple Logging:**
   ```python
   else:
       logger_func(detail)
   ```

3. **Exception Raising:**
   ```python
   raise HTTPException(status_code=status_code, detail=detail) from exc
   ```

**Key Features:**
- **Automatic Logging**: Every HTTP error is automatically logged
- **Fallback Logging**: Handles loggers that don't support extra parameters
- **Exception Chaining**: Preserves original exception context
- **Consistent Interface**: Single function for all HTTP error scenarios

## Usage Patterns

### API Endpoint Error Handling

**Standardized API Error Responses:**

```python
from src.utils.http_error import http_error, ExtraLogInfo
from fastapi import Depends
from loguru import logger

@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get user endpoint with standardized error handling."""
    
    try:
        # Validate user ID format
        if not user_id or not isinstance(user_id, str):
            http_error(
                status_code=400,
                detail="Invalid user ID format",
                extra=ExtraLogInfo(
                    user_id=current_user.id,
                    action="get",
                    error_code=4001
                )
            )
        
        # Get user from repository
        user = await user_repository.get_user_by_id(user_id)
        
        if not user:
            http_error(
                status_code=404,
                detail=f"User {user_id} not found",
                extra=ExtraLogInfo(
                    user_id=current_user.id,
                    action="get",
                    error_code=4041
                )
            )
        
        # Check access permissions
        if not await can_access_user(current_user.id, user_id):
            http_error(
                status_code=403,
                detail="Access denied to user profile",
                extra=ExtraLogInfo(
                    user_id=current_user.id,
                    action="get",
                    error_code=4031
                )
            )
        
        return UserResponse.from_user(user)
        
    except HTTPException:
        # Re-raise HTTP exceptions from http_error
        raise
    except Exception as e:
        # Handle unexpected errors
        http_error(
            status_code=500,
            detail="Internal server error",
            extra=ExtraLogInfo(
                user_id=current_user.id,
                action="get",
                error_code=5001
            ),
            exc=e
        )

@app.post("/users")
async def create_user(
    user_request: CreateUserRequest,
    current_user: User = Depends(get_current_admin)
) -> UserResponse:
    """Create user endpoint with comprehensive error handling."""
    
    try:
        # Validate request data
        if not user_request.email:
            http_error(
                status_code=400,
                detail="Email is required",
                extra=ExtraLogInfo(
                    user_id=current_user.id,
                    action="create",
                    error_code=4002
                )
            )
        
        # Check if user already exists
        existing_user = await user_repository.get_user_by_email(user_request.email)
        if existing_user:
            http_error(
                status_code=409,
                detail=f"User with email {user_request.email} already exists",
                extra=ExtraLogInfo(
                    user_id=current_user.id,
                    action="create",
                    error_code=4091
                )
            )
        
        # Create user
        user_data = user_request.dict()
        user = await user_repository.create_user(user_data)
        
        logger.info(f"User created successfully: {user.email}", extra={
            "user_id": current_user.id,
            "action": "create",
            "created_user_id": user.id
        })
        
        return UserResponse.from_user(user)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        http_error(
            status_code=500,
            detail="User creation failed",
            extra=ExtraLogInfo(
                user_id=current_user.id,
                action="create",
                error_code=5002
            ),
            exc=e
        )
```

### Service Layer Error Handling

**Service-Level Error Processing:**

```python
from src.utils.http_error import http_error, ExtraLogInfo

class UserService:
    """User service with standardized error handling."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def update_user_profile(
        self,
        user_id: str,
        update_data: dict,
        requester_id: str
    ) -> User:
        """Update user profile with comprehensive error handling."""
        
        try:
            # Validate user exists
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                http_error(
                    status_code=404,
                    detail=f"User {user_id} not found",
                    extra=ExtraLogInfo(
                        user_id=requester_id,
                        action="update",
                        error_code=4042
                    )
                )
            
            # Check permissions
            if not await self.can_update_user(requester_id, user_id):
                http_error(
                    status_code=403,
                    detail="Insufficient permissions to update user",
                    extra=ExtraLogInfo(
                        user_id=requester_id,
                        action="update",
                        error_code=4032
                    )
                )
            
            # Validate update data
            validation_errors = await self.validate_user_update(update_data)
            if validation_errors:
                http_error(
                    status_code=422,
                    detail=f"Validation failed: {validation_errors}",
                    extra=ExtraLogInfo(
                        user_id=requester_id,
                        action="update",
                        error_code=4221
                    )
                )
            
            # Update user
            updated_user = await self.user_repository.update_user(user_id, update_data)
            
            logger.info(f"User profile updated: {user_id}", extra={
                "user_id": requester_id,
                "action": "update",
                "updated_user_id": user_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_user
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            http_error(
                status_code=500,
                detail="User profile update failed",
                extra=ExtraLogInfo(
                    user_id=requester_id,
                    action="update",
                    error_code=5003
                ),
                exc=e
            )
    
    async def delete_user(self, user_id: str, requester_id: str) -> bool:
        """Delete user with audit logging."""
        
        try:
            # Validate user exists
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                http_error(
                    status_code=404,
                    detail=f"User {user_id} not found",
                    extra=ExtraLogInfo(
                        user_id=requester_id,
                        action="delete",
                        error_code=4043
                    )
                )
            
            # Check if user can be deleted
            if user.is_admin and not await self.is_super_admin(requester_id):
                http_error(
                    status_code=403,
                    detail="Cannot delete admin user",
                    extra=ExtraLogInfo(
                        user_id=requester_id,
                        action="delete",
                        error_code=4033
                    )
                )
            
            # Check for dependencies
            user_dependencies = await self.check_user_dependencies(user_id)
            if user_dependencies:
                http_error(
                    status_code=409,
                    detail=f"Cannot delete user with dependencies: {user_dependencies}",
                    extra=ExtraLogInfo(
                        user_id=requester_id,
                        action="delete",
                        error_code=4092
                    )
                )
            
            # Perform deletion
            await self.user_repository.delete_user(user_id)
            
            logger.warning(f"User deleted: {user.email}", extra={
                "user_id": requester_id,
                "action": "delete",
                "deleted_user_id": user_id,
                "deleted_user_email": user.email
            })
            
            return True
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            http_error(
                status_code=500,
                detail="User deletion failed",
                extra=ExtraLogInfo(
                    user_id=requester_id,
                    action="delete",
                    error_code=5004
                ),
                exc=e
            )
```

### Authentication Error Handling

**Authentication-Specific Error Handling:**

```python
from src.utils.http_error import http_error, ExtraLogInfo

async def authenticate_user(email: str, password: str, request_id: str) -> dict:
    """Authenticate user with detailed error tracking."""
    
    try:
        # Get user by email
        user = await user_repository.get_user_by_email(email)
        
        if not user:
            http_error(
                status_code=401,
                detail="Invalid email or password",
                extra=ExtraLogInfo(
                    action="login",
                    request_id=request_id,
                    error_code=4011
                )
            )
        
        # Check if account is active
        if not user.is_active:
            http_error(
                status_code=401,
                detail="Account is deactivated",
                extra=ExtraLogInfo(
                    user_id=user.id,
                    action="login",
                    request_id=request_id,
                    error_code=4012
                )
            )
        
        # Check account lockout
        if await is_account_locked(user.id):
            http_error(
                status_code=429,
                detail="Account temporarily locked due to failed login attempts",
                extra=ExtraLogInfo(
                    user_id=user.id,
                    action="login",
                    request_id=request_id,
                    error_code=4291
                )
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            # Increment failed attempts
            await increment_failed_login_attempts(user.id)
            
            http_error(
                status_code=401,
                detail="Invalid email or password",
                extra=ExtraLogInfo(
                    user_id=user.id,
                    action="login",
                    request_id=request_id,
                    error_code=4013
                )
            )
        
        # Reset failed attempts on successful login
        await reset_failed_login_attempts(user.id)
        
        # Create session
        access_token = create_access_token(data={"sub": user.id})
        
        logger.info(f"User authenticated successfully: {email}", extra={
            "user_id": user.id,
            "action": "login",
            "request_id": request_id
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected authentication errors
        http_error(
            status_code=500,
            detail="Authentication service unavailable",
            extra=ExtraLogInfo(
                action="login",
                request_id=request_id,
                error_code=5005
            ),
            exc=e
        )

@app.post("/auth/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    request_id: str = Depends(get_request_id)
):
    """Logout endpoint with error handling."""
    
    try:
        # Blacklist current token
        token = await get_current_token()
        await token_repository.blacklist_token(token)
        
        logger.info(f"User logged out: {current_user.email}", extra={
            "user_id": current_user.id,
            "action": "logout",
            "request_id": request_id
        })
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        # Handle logout errors
        http_error(
            status_code=500,
            detail="Logout failed",
            extra=ExtraLogInfo(
                user_id=current_user.id,
                action="logout",
                request_id=request_id,
                error_code=5006
            ),
            exc=e
        )
```

### Custom Logging Functions

**Specialized Error Logging:**

```python
from loguru import logger
from typing import Callable

def create_security_logger() -> Callable[[str], None]:
    """Create specialized logger for security-related errors."""
    
    def security_log(message: str, **kwargs) -> None:
        """Log security errors with special handling."""
        
        # Add security context
        extra = kwargs.get('extra', {})
        extra['security_event'] = True
        extra['severity'] = 'high'
        
        logger.warning(f"SECURITY: {message}", extra=extra)
    
    return security_log

def create_audit_logger() -> Callable[[str], None]:
    """Create specialized logger for audit events."""
    
    def audit_log(message: str, **kwargs) -> None:
        """Log audit events for compliance."""
        
        extra = kwargs.get('extra', {})
        extra['audit_event'] = True
        extra['timestamp'] = datetime.utcnow().isoformat()
        
        logger.info(f"AUDIT: {message}", extra=extra)
    
    return audit_log

# Usage with custom loggers
security_logger = create_security_logger()
audit_logger = create_audit_logger()

async def handle_security_violation(user_id: str, violation_type: str):
    """Handle security violations with specialized logging."""
    
    http_error(
        status_code=403,
        detail=f"Security violation detected: {violation_type}",
        logger_func=security_logger,
        extra=ExtraLogInfo(
            user_id=user_id,
            action="security_violation",
            error_code=4034
        )
    )

async def handle_audit_required_action(user_id: str, action: str):
    """Handle actions requiring audit logging."""
    
    try:
        # Perform action
        result = await perform_sensitive_action(user_id, action)
        
        audit_logger(f"Sensitive action completed: {action}", extra={
            "user_id": user_id,
            "action": action,
            "result": "success"
        })
        
        return result
        
    except Exception as e:
        http_error(
            status_code=500,
            detail=f"Sensitive action failed: {action}",
            logger_func=audit_logger,
            extra=ExtraLogInfo(
                user_id=user_id,
                action=action,
                error_code=5007
            ),
            exc=e
        )
```

### Error Code Management

**Systematic Error Code Organization:**

```python
from enum import IntEnum

class ErrorCodes(IntEnum):
    """Standardized error codes for tracking and analysis."""
    
    # 4xxx - Client errors
    INVALID_USER_ID_FORMAT = 4001
    EMAIL_REQUIRED = 4002
    
    # Authentication errors (401x)
    INVALID_CREDENTIALS = 4011
    ACCOUNT_DEACTIVATED = 4012
    INVALID_PASSWORD = 4013
    
    # Authorization errors (403x)
    ACCESS_DENIED_PROFILE = 4031
    INSUFFICIENT_UPDATE_PERMISSIONS = 4032
    CANNOT_DELETE_ADMIN = 4033
    SECURITY_VIOLATION = 4034
    
    # Not found errors (404x)
    USER_NOT_FOUND_GET = 4041
    USER_NOT_FOUND_UPDATE = 4042
    USER_NOT_FOUND_DELETE = 4043
    
    # Conflict errors (409x)
    USER_ALREADY_EXISTS = 4091
    USER_HAS_DEPENDENCIES = 4092
    
    # Validation errors (422x)
    VALIDATION_FAILED = 4221
    
    # Rate limiting errors (429x)
    ACCOUNT_LOCKED = 4291
    
    # 5xxx - Server errors
    INTERNAL_SERVER_ERROR = 5001
    USER_CREATION_FAILED = 5002
    USER_UPDATE_FAILED = 5003
    USER_DELETION_FAILED = 5004
    AUTHENTICATION_SERVICE_ERROR = 5005
    LOGOUT_FAILED = 5006
    SENSITIVE_ACTION_FAILED = 5007

def get_error_category(error_code: int) -> str:
    """Get error category from error code."""
    
    if 4000 <= error_code < 4100:
        return "client_error"
    elif 4100 <= error_code < 4200:
        return "authentication_error"
    elif 4200 <= error_code < 4300:
        return "authorization_error"
    elif 4300 <= error_code < 4400:
        return "not_found_error"
    elif 4400 <= error_code < 4500:
        return "conflict_error"
    elif 4500 <= error_code < 4600:
        return "validation_error"
    elif 4600 <= error_code < 4700:
        return "rate_limit_error"
    elif 5000 <= error_code < 6000:
        return "server_error"
    else:
        return "unknown_error"

# Enhanced error function with error code validation
def validated_http_error(
    status_code: int,
    detail: str,
    error_code: ErrorCodes,
    user_id: int = None,
    action: str = None,
    request_id: str = None,
    exc: BaseException = None
) -> None:
    """HTTP error with validated error codes and automatic context."""
    
    extra = ExtraLogInfo(
        error_code=error_code.value,
        user_id=user_id,
        action=action,
        request_id=request_id
    )
    
    # Add error category for analytics
    extra['error_category'] = get_error_category(error_code.value)
    
    http_error(
        status_code=status_code,
        detail=detail,
        extra=extra,
        exc=exc
    )

# Usage with validated error codes
async def example_with_error_codes(user_id: str, requester_id: int):
    """Example using validated error codes."""
    
    user = await user_repository.get_user_by_id(user_id)
    
    if not user:
        validated_http_error(
            status_code=404,
            detail=f"User {user_id} not found",
            error_code=ErrorCodes.USER_NOT_FOUND_GET,
            user_id=requester_id,
            action="get"
        )
    
    return user
```

## Error Analytics and Monitoring

### Error Metrics Collection

**Error Analytics Integration:**

```python
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class ErrorAnalytics:
    """Collect and analyze error patterns."""
    
    def __init__(self):
        self.error_counts = Counter()
        self.error_timeline = defaultdict(list)
        self.user_error_patterns = defaultdict(Counter)
    
    def record_error(self, extra: ExtraLogInfo, status_code: int, detail: str):
        """Record error for analytics."""
        
        error_key = f"{status_code}_{extra.get('error_code', 'unknown')}"
        timestamp = datetime.utcnow()
        
        # Count errors
        self.error_counts[error_key] += 1
        
        # Timeline tracking
        self.error_timeline[timestamp.date()].append({
            'error_key': error_key,
            'timestamp': timestamp,
            'user_id': extra.get('user_id'),
            'action': extra.get('action'),
            'detail': detail
        })
        
        # User pattern tracking
        if extra.get('user_id'):
            self.user_error_patterns[extra['user_id']][error_key] += 1
    
    def get_error_summary(self, days: int = 7) -> dict:
        """Get error summary for specified days."""
        
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        
        recent_errors = []
        for date, errors in self.error_timeline.items():
            if date >= cutoff_date:
                recent_errors.extend(errors)
        
        return {
            'total_errors': len(recent_errors),
            'error_types': dict(Counter(e['error_key'] for e in recent_errors)),
            'error_by_day': {
                str(date): len(errors) 
                for date, errors in self.error_timeline.items() 
                if date >= cutoff_date
            },
            'top_error_users': dict(
                Counter(e['user_id'] for e in recent_errors if e['user_id']).most_common(10)
            )
        }

# Global analytics instance
error_analytics = ErrorAnalytics()

# Enhanced http_error with analytics
def analytics_http_error(
    status_code: int,
    detail: str,
    extra: ExtraLogInfo = None,
    logger_func: Callable[[str], None] = DEFAULT_LOGGER_FUNC,
    exc: BaseException = None
) -> None:
    """HTTP error with analytics recording."""
    
    # Record for analytics
    if extra:
        error_analytics.record_error(extra, status_code, detail)
    
    # Standard error handling
    http_error(status_code, detail, logger_func, extra, exc)
```

## Testing Strategies

### HTTP Error Testing

**Comprehensive Error Testing:**

```python
import pytest
from unittest.mock import Mock, patch
from src.utils.http_error import http_error, ExtraLogInfo
from fastapi import HTTPException

class TestHTTPError:
    """Test suite for HTTP error utilities."""
    
    def test_basic_http_error(self):
        """Test basic HTTP error functionality."""
        
        with pytest.raises(HTTPException) as exc_info:
            http_error(
                status_code=404,
                detail="Resource not found"
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Resource not found"
    
    def test_http_error_with_extra_info(self):
        """Test HTTP error with extra logging information."""
        
        extra = ExtraLogInfo(
            user_id=123,
            action="get",
            error_code=4041
        )
        
        with pytest.raises(HTTPException) as exc_info:
            http_error(
                status_code=404,
                detail="User not found",
                extra=extra
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"
    
    def test_http_error_with_exception_chaining(self):
        """Test HTTP error with exception chaining."""
        
        original_exception = ValueError("Database connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            http_error(
                status_code=500,
                detail="Internal server error",
                exc=original_exception
            )
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.__cause__ == original_exception
    
    @patch('src.utils.http_error.logger')
    def test_logging_integration(self, mock_logger):
        """Test that errors are properly logged."""
        
        extra = ExtraLogInfo(
            user_id=123,
            action="update",
            error_code=4221
        )
        
        with pytest.raises(HTTPException):
            http_error(
                status_code=422,
                detail="Validation failed",
                extra=extra
            )
        
        # Verify logging was called
        mock_logger.error.assert_called_once()
    
    def test_custom_logger_function(self):
        """Test HTTP error with custom logger function."""
        
        mock_logger = Mock()
        
        with pytest.raises(HTTPException):
            http_error(
                status_code=400,
                detail="Bad request",
                logger_func=mock_logger
            )
        
        # Verify custom logger was used
        mock_logger.assert_called_once_with("Bad request")
    
    def test_logger_fallback(self):
        """Test fallback behavior when logger doesn't support extra."""
        
        def simple_logger(message: str):
            # Logger that doesn't accept extra parameter
            pass
        
        mock_simple_logger = Mock(side_effect=simple_logger)
        
        extra = ExtraLogInfo(user_id=123)
        
        with pytest.raises(HTTPException):
            http_error(
                status_code=500,
                detail="Server error",
                logger_func=mock_simple_logger,
                extra=extra
            )
        
        # Should handle the TypeError and fall back
        mock_simple_logger.assert_called()
```

## Best Practices

### Error Handling Guidelines

- **Consistent Usage**: Use http_error for all HTTP exceptions in the application
- **Rich Context**: Always provide ExtraLogInfo with relevant context
- **Appropriate Status Codes**: Use correct HTTP status codes for different error types
- **Exception Chaining**: Chain original exceptions to preserve error context
- **Security Awareness**: Don't expose sensitive information in error messages

### Logging Guidelines

- **Structured Logging**: Use ExtraLogInfo for consistent log structure
- **Error Codes**: Implement systematic error codes for tracking and analysis
- **Security Events**: Use specialized loggers for security-related errors
- **Audit Trail**: Maintain audit logs for compliance requirements
- **Performance**: Consider logging performance impact in high-traffic scenarios

### API Design Guidelines

- **User-Friendly Messages**: Provide clear, actionable error messages
- **Consistent Format**: Maintain consistent error response format
- **Documentation**: Document all possible error responses for each endpoint
- **Rate Limiting**: Implement proper rate limiting with appropriate error responses

## Related Files

### Dependencies

- `collections.abc.Callable` - Function type annotations
- `fastapi.HTTPException` - FastAPI exception class
- `loguru.logger` - Advanced logging framework
- `typing_extensions.TypedDict` - Structured type definitions

### Integration Points

- `src.api.v1.*` - All API endpoints using standardized error handling
- `src.services.*` - Service layer error handling
- `src.core.logging` - Central logging configuration
- `src.core.monitoring` - Error monitoring and analytics

### Related Utilities

- Authentication middleware for error context
- Rate limiting utilities for error responses
- Monitoring utilities for error tracking

## Configuration

### HTTP Error Settings

```python
# HTTP error configuration
HTTP_ERROR_CONFIG = {
    "log_all_errors": True,               # Log all HTTP errors
    "include_stack_traces": False,        # Include stack traces (dev only)
    "error_code_validation": True,        # Validate error codes
    "analytics_enabled": True,            # Enable error analytics
    "audit_security_errors": True,       # Special handling for security errors
}

# Error code ranges
ERROR_CODE_RANGES = {
    "client_errors": (4000, 4999),
    "server_errors": (5000, 5999),
    "security_errors": (4030, 4039),
    "authentication_errors": (4010, 4019)
}
```

This HTTP error utilities module provides comprehensive error handling for the ReViewPoint application, ensuring consistent error responses, rich logging context, and effective error monitoring throughout the system.
