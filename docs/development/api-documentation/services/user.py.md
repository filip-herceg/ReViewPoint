# User Service Documentation

## Purpose

The `user.py` service module implements comprehensive user management business logic for the ReViewPoint application. This service provides a complete abstraction layer for user operations including registration, authentication, password management, profile operations, role-based access control, and audit logging. It serves as the primary business logic coordinator between the API layer and the data access layer.

## Architecture

The service follows a layered architecture pattern with clear separation of concerns:

- **Service Layer**: High-level business logic and workflow orchestration
- **Repository Layer**: Data access abstraction through repository pattern
- **Schema Layer**: Data validation and serialization
- **Security Layer**: Password hashing, token management, and access control
- **Audit Layer**: Comprehensive logging for compliance and monitoring

## Core Functions

### User Registration and Authentication

#### `register_user(session, user_data)`

Handles complete user registration workflow with validation and security measures.

```python
# Example usage
new_user = await register_user(session, {
    "email": "user@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
})
```

**Key Features:**

- Email validation and uniqueness checking
- Password strength validation and secure hashing
- Automatic role assignment (default: USER)
- Audit logging for registration events
- Error handling for duplicate users

#### `authenticate_user(session, email, password)`

Authenticates users with comprehensive security checks and JWT token generation.

```python
# Example usage
auth_result = await authenticate_user(session, "user@example.com", "password")
access_token = auth_result["access_token"]
refresh_token = auth_result["refresh_token"]
```

**Key Features:**

- Secure password verification using bcrypt
- JWT token generation with configurable expiration
- Refresh token creation for session management
- Rate limiting protection against brute force attacks
- Comprehensive audit logging

### Password Management

#### `reset_password(session, email)`

Initiates secure password reset process with token generation.

```python
# Example usage
reset_token = await reset_password(session, "user@example.com")
# Token sent via email (handled by email service)
```

#### `confirm_password_reset(session, token, new_password)`

Completes password reset with token validation and password update.

```python
# Example usage
success = await confirm_password_reset(session, reset_token, "new_password")
```

**Security Features:**

- Time-limited reset tokens
- Single-use token validation
- Password strength requirements
- Secure token storage and verification

### Profile Management

#### `get_user_profile(session, user_id)`

Retrieves comprehensive user profile information with privacy controls.

```python
# Example usage
profile = await get_user_profile(session, user_id)
print(f"User: {profile.first_name} {profile.last_name}")
```

#### `update_user_profile(session, user_id, profile_data)`

Updates user profile with validation and audit logging.

```python
# Example usage
updated_profile = await update_user_profile(session, user_id, {
    "first_name": "Jane",
    "last_name": "Smith",
    "bio": "Software developer"
})
```

#### `update_user_preferences(session, user_id, preferences)`

Manages user preferences and application settings.

```python
# Example usage
await update_user_preferences(session, user_id, {
    "email_notifications": True,
    "theme": "dark",
    "language": "en"
})
```

### Token Management

#### `refresh_user_token(session, refresh_token)`

Handles secure token refresh with rate limiting and blacklist checking.

```python
# Example usage
new_tokens = await refresh_user_token(session, refresh_token)
access_token = new_tokens["access_token"]
```

**Security Features:**

- Token blacklist validation
- Rate limiting per user
- Automatic token rotation
- Session tracking and management

#### `logout_user(session, refresh_token)`

Securely logs out users by blacklisting tokens.

```python
# Example usage
await logout_user(session, refresh_token)
```

### Role-Based Access Control

#### `assign_user_role(session, user_id, role)`

Manages user role assignments with proper authorization checks.

```python
# Example usage
await assign_user_role(session, user_id, UserRole.ADMIN)
```

**Available Roles:**

- `USER`: Standard user permissions
- `ADMIN`: Administrative privileges
- `SUPER_ADMIN`: Full system access

### Administrative Functions

#### `list_users_paginated(session, page, page_size, search_query)`

Provides paginated user listings with search capabilities.

```python
# Example usage
users_page = await list_users_paginated(session, page=1, page_size=20, search_query="john")
```

#### `delete_user_account(session, user_id)`

Handles complete user account deletion with data cleanup.

```python
# Example usage
await delete_user_account(session, user_id)
```

## UserService Class

### Dependency Injection Pattern

The `UserService` class implements dependency injection for FastAPI integration:

```python
class UserService:
    """Dependency injection service for user operations."""

    def __init__(self):
        """Initialize service with configuration."""
        self.settings = get_settings()

    # Service methods delegate to module functions
    async def register_user(self, session: AsyncSession, user_data: dict):
        return await register_user(session, user_data)
```

### Usage in FastAPI Endpoints

```python
from fastapi import Depends
from src.services.user import UserService

@router.post("/register")
async def register_endpoint(
    user_data: UserRegistrationSchema,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends()
):
    return await user_service.register_user(session, user_data.dict())
```

## Security Considerations

### Password Security

- **Hashing**: Uses bcrypt with configurable rounds
- **Validation**: Enforces password complexity requirements
- **Storage**: Never stores plaintext passwords
- **Reset**: Secure token-based password reset flow

### Token Security

- **JWT**: Signed tokens with configurable expiration
- **Refresh Tokens**: Separate tokens for session management
- **Blacklisting**: Comprehensive token invalidation
- **Rate Limiting**: Protection against token abuse

### Access Control

- **Role-Based**: Hierarchical permission system
- **Authorization**: Consistent permission checking
- **Audit Logging**: Complete action tracking
- **Data Privacy**: Profile visibility controls

## Error Handling

### Custom Exceptions

```python
class UserNotFoundError(Exception):
    """Raised when user cannot be found."""
    pass

class UserAlreadyExistsError(Exception):
    """Raised when attempting to create duplicate user."""
    pass

class ValidationError(Exception):
    """Raised when user data validation fails."""
    pass
```

### Error Response Patterns

```python
try:
    user = await register_user(session, user_data)
except UserAlreadyExistsError:
    raise HTTPException(status_code=409, detail="User already exists")
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Usage Patterns

### Registration Flow

```python
# 1. Validate user data
# 2. Check for existing user
# 3. Hash password securely
# 4. Create user record
# 5. Assign default role
# 6. Log registration event
# 7. Return user profile
```

### Authentication Flow

```python
# 1. Validate credentials
# 2. Check rate limiting
# 3. Verify password
# 4. Generate JWT tokens
# 5. Log authentication event
# 6. Return token response
```

### Profile Update Flow

```python
# 1. Validate permissions
# 2. Sanitize input data
# 3. Update user record
# 4. Log profile changes
# 5. Return updated profile
```

## Best Practices

### Service Design

- **Single Responsibility**: Each function has a clear purpose
- **Dependency Injection**: Proper IoC container integration
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed audit trails
- **Validation**: Input sanitization and validation

### Security Practices

- **Password Hashing**: Use bcrypt with sufficient rounds
- **Token Management**: Implement proper JWT lifecycle
- **Rate Limiting**: Protect against abuse
- **Audit Logging**: Track all sensitive operations
- **Access Control**: Enforce role-based permissions

### Performance Optimization

- **Database Queries**: Efficient repository usage
- **Caching**: Strategic caching for frequently accessed data
- **Pagination**: Proper handling of large datasets
- **Async Operations**: Non-blocking I/O operations

## Testing Strategies

### Unit Testing

```python
async def test_register_user():
    # Test user registration with valid data
    user_data = {
        "email": "test@example.com",
        "password": "secure_password",
        "first_name": "Test",
        "last_name": "User"
    }
    user = await register_user(session, user_data)
    assert user.email == "test@example.com"
```

### Integration Testing

```python
async def test_authentication_flow():
    # Test complete auth flow
    user = await register_user(session, user_data)
    auth_result = await authenticate_user(session, user.email, "password")
    assert "access_token" in auth_result
```

### Security Testing

```python
async def test_password_reset_security():
    # Test token expiration and single-use
    token = await reset_password(session, user.email)
    # First use should succeed
    await confirm_password_reset(session, token, "new_password")
    # Second use should fail
    with pytest.raises(ValidationError):
        await confirm_password_reset(session, token, "another_password")
```

## Related Files

### Dependencies

- `src/repositories/user.py` - User data access layer
- `src/schemas/user.py` - User data validation schemas
- `src/models/user.py` - User database models
- `src/core/security.py` - Password hashing and token utilities
- `src/core/config.py` - Application configuration

### API Integration

- `src/api/v1/users/core.py` - User CRUD endpoints
- `src/api/v1/auth.py` - Authentication endpoints
- `src/api/deps.py` - Dependency injection setup

### Utilities

- `src/utils/email.py` - Email notification service
- `src/utils/audit.py` - Audit logging utilities
- `src/utils/rate_limit.py` - Rate limiting implementation

## Module Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Configuration
BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW=300
```

### Service Configuration

```python
# Service settings
settings = get_settings()
password_hasher = PasswordHasher(rounds=settings.bcrypt_rounds)
token_manager = TokenManager(secret=settings.jwt_secret_key)
```

This user service provides a comprehensive foundation for all user-related operations in the ReViewPoint application, ensuring security, scalability, and maintainability through well-designed business logic patterns and proper separation of concerns.
