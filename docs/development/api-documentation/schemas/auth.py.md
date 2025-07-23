# Authentication Schema Documentation

## Purpose

The `auth.py` schema module defines comprehensive Pydantic data validation models for all authentication-related operations in the ReViewPoint application. This module provides robust input validation, serialization, and type safety for user registration, login, password reset workflows, and authentication responses, ensuring data integrity and security throughout the authentication system.

## Architecture

The schema module follows a validation-first design pattern with multiple layers of security:

- **Input Validation Layer**: Pydantic field validators for email and password security
- **Data Serialization Layer**: TypedDict and BaseModel patterns for API responses
- **Type Safety Layer**: Strong typing with Literal types and ClassVar annotations
- **Security Layer**: Password strength validation and email format verification
- **Constants Layer**: Centralized token type definitions

## Core Schema Classes

### User Registration Schemas

#### `UserRegisterRequest`

Comprehensive user registration validation with security-focused field validation.

```python
# Example usage
registration_data = {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
}

# Pydantic validation
try:
    user_request = UserRegisterRequest(**registration_data)
    # All validation passed
except ValueError as e:
    # Handle validation errors
    print(f"Registration validation failed: {e}")
```

**Field Specifications:**

- `email: EmailStr` - Valid email address with format validation
- `password: str` - 8-128 characters with strength requirements
- `name: str | None` - Optional display name, max 128 characters

**Validation Features:**

**Email Validation:**

```python
@field_validator("email")
@classmethod
def validate_email_field(cls, v: str) -> str:
    if not validate_email(v):
        raise ValueError("Invalid email format.")
    return v
```

**Password Validation:**

```python
@field_validator("password")
@classmethod
def validate_password_field(cls, v: str) -> str:
    err = get_password_validation_error(v)
    if err:
        raise ValueError(err)
    return v
```

**Security Features:**

- Email format validation using custom `validate_email()` utility
- Password strength validation with `get_password_validation_error()`
- Length constraints to prevent buffer overflow attacks
- Type safety with ClassVar annotations for validator signatures

#### `UserLoginRequest`

Streamlined login credential validation for authentication endpoints.

```python
# Example usage
login_data = {
    "email": "user@example.com",
    "password": "userpassword"
}

login_request = UserLoginRequest(**login_data)
```

**Field Specifications:**

- `email: EmailStr` - Validated email address
- `password: str` - Plain text password (hashed server-side)

**Design Features:**

- Minimal validation for performance
- EmailStr type ensures format validation
- No password strength checking (existing users)

### Password Reset Schemas

#### `PasswordResetRequest`

Initiates secure password reset workflow with email validation.

```python
# Example usage
reset_request = PasswordResetRequest(email="user@example.com")

# Validates email format before processing
```

**Field Specifications:**

- `email: EmailStr` - Target email for password reset

**Validation Features:**

- Custom email validation with `validate_email()` utility
- Consistent validation pattern across auth schemas
- Type-safe validator signatures with ClassVar

#### `PasswordResetConfirmRequest`

Completes password reset with token validation and new password requirements.

```python
# Example usage
confirm_data = {
    "token": "secure-reset-token-12345",
    "new_password": "NewSecurePassword123!"
}

confirm_request = PasswordResetConfirmRequest(**confirm_data)
```

**Field Specifications:**

- `token: str` - Password reset token from email
- `new_password: str` - New password with 8-128 character requirement

**Security Features:**

- Full password strength validation for new passwords
- Token format validation (server-side verification)
- Same security standards as registration

### Authentication Response Schemas

#### `AuthResponse` and `AuthResponseDict`

Standardized authentication response format with type safety.

```python
# Example usage
auth_response = AuthResponse(
    access_token="jwt-access-token",
    refresh_token="jwt-refresh-token",
    token_type="bearer"  # Default value
)

# TypedDict for type hints
response_dict: AuthResponseDict = {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "token_type": "bearer"
}
```

**Field Specifications:**

- `access_token: str` - JWT access token for API authentication
- `refresh_token: str` - JWT refresh token for session management
- `token_type: Literal["bearer"]` - OAuth 2.0 bearer token type

**Design Features:**

- Default token type value with `TOKEN_TYPE_BEARER` constant
- Literal type for token_type ensures correct OAuth 2.0 format
- Dual pattern: BaseModel for validation, TypedDict for type hints

#### `MessageResponse` and `MessageResponseDict`

Generic message response format for operation confirmations.

```python
# Example usage
success_response = MessageResponse(message="Password reset email sent")
error_response = MessageResponse(message="Email address not found")
```

**Field Specifications:**

- `message: str` - Human-readable operation result message

**Use Cases:**

- Password reset confirmation messages
- Registration success notifications
- Authentication error descriptions
- General API operation feedback

## Validation Patterns

### Custom Validator Integration

**Email Validation:**

```python
# Utilizes src.utils.validation.validate_email()
def validate_email_field(cls, v: str) -> str:
    if not validate_email(v):
        raise ValueError("Invalid email format.")
    return v
```

**Password Validation:**

```python
# Utilizes src.utils.validation.get_password_validation_error()
def validate_password_field(cls, v: str) -> str:
    err = get_password_validation_error(v)
    if err:
        raise ValueError(err)
    return v
```

### Type Safety Patterns

**ClassVar Validator Signatures:**

```python
class UserRegisterRequest(BaseModel):
    _email_validator: ClassVar[Callable[[type["UserRegisterRequest"], str], str]]
    _password_validator: ClassVar[Callable[[type["UserRegisterRequest"], str], str]]
```

**Literal Type Constraints:**

```python
token_type: Literal["bearer"] = TOKEN_TYPE_BEARER
```

## Security Considerations

### Input Validation Security

**Email Security:**

- Format validation prevents injection attacks
- EmailStr type ensures RFC compliance
- Custom validation adds application-specific rules

**Password Security:**

- Minimum length requirements (8 characters)
- Maximum length limits (128 characters) prevent DoS
- Strength validation enforces complexity rules
- No password storage in schema (server-side hashing)

**Token Security:**

- Literal types prevent token type confusion
- Consistent token format across responses
- Type safety prevents accidental exposure

### Validation Error Handling

**Secure Error Messages:**

```python
# Good: Generic error message
raise ValueError("Invalid email format.")

# Avoid: Specific error details
# raise ValueError("Email domain not in whitelist")
```

**Input Sanitization:**

- All fields validated before processing
- Length limits prevent buffer overflow
- Type constraints prevent injection

## Usage Patterns

### Registration Workflow

```python
async def register_user(request: UserRegisterRequest):
    # Schema validation happens automatically
    try:
        # request.email, request.password, request.name are validated
        user = await create_user(
            email=request.email,
            password=request.password,
            name=request.name
        )
        return AuthResponse(
            access_token=generate_access_token(user),
            refresh_token=generate_refresh_token(user)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Login Workflow

```python
async def login_user(request: UserLoginRequest):
    # Email format automatically validated
    user = await authenticate_user(request.email, request.password)
    if user:
        return AuthResponse(
            access_token=generate_access_token(user),
            refresh_token=generate_refresh_token(user)
        )
    else:
        return MessageResponse(message="Invalid credentials")
```

### Password Reset Workflow

```python
async def initiate_password_reset(request: PasswordResetRequest):
    # Email validation ensures format correctness
    await send_reset_email(request.email)
    return MessageResponse(message="Password reset email sent")

async def confirm_password_reset(request: PasswordResetConfirmRequest):
    # Token and password validation happens automatically
    await reset_user_password(request.token, request.new_password)
    return MessageResponse(message="Password successfully reset")
```

## Error Handling

### Validation Error Patterns

```python
# Common validation error handling
try:
    user_request = UserRegisterRequest(**user_data)
except ValidationError as e:
    # Pydantic validation errors
    error_details = []
    for error in e.errors():
        error_details.append({
            "field": error["loc"][-1],
            "message": error["msg"],
            "type": error["type"]
        })
    raise HTTPException(status_code=422, detail=error_details)
```

### Field-Specific Error Handling

```python
# Handle specific validation failures
try:
    user_request = UserRegisterRequest(**user_data)
except ValueError as e:
    if "email format" in str(e):
        raise HTTPException(status_code=400, detail="Invalid email address")
    elif "password" in str(e):
        raise HTTPException(status_code=400, detail="Password does not meet requirements")
    else:
        raise HTTPException(status_code=400, detail="Invalid input data")
```

## Best Practices

### Schema Design

- **Single Responsibility**: Each schema validates one specific operation
- **Type Safety**: Use Literal types for constrained values
- **Validation Logic**: Delegate complex validation to utility functions
- **Error Messages**: Provide clear, actionable error messages
- **Documentation**: Include docstrings for all schemas

### Security Practices

- **Input Validation**: Validate all input fields
- **Length Limits**: Enforce reasonable field length constraints
- **Format Validation**: Use appropriate field types (EmailStr, etc.)
- **Error Handling**: Don't expose sensitive information in error messages
- **Type Safety**: Use strong typing to prevent runtime errors

### Performance Optimization

- **Minimal Validation**: Only validate what's necessary for each operation
- **Efficient Validators**: Use fast validation functions
- **Caching**: Cache compiled validation patterns
- **Field Ordering**: Order fields by validation complexity

## Testing Strategies

### Unit Testing

```python
def test_user_register_request_valid():
    # Test valid registration data
    data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    request = UserRegisterRequest(**data)
    assert request.email == "test@example.com"
    assert request.name == "Test User"

def test_user_register_request_invalid_email():
    # Test invalid email format
    data = {
        "email": "invalid-email",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    with pytest.raises(ValidationError):
        UserRegisterRequest(**data)
```

### Security Testing

```python
def test_password_validation():
    # Test password strength requirements
    weak_passwords = ["123", "password", "12345678"]
    for weak_password in weak_passwords:
        data = {
            "email": "test@example.com",
            "password": weak_password,
            "name": "Test User"
        }
        with pytest.raises(ValidationError):
            UserRegisterRequest(**data)

def test_email_injection_prevention():
    # Test email injection attempts
    malicious_emails = [
        "test@example.com<script>alert('xss')</script>",
        "test@example.com'; DROP TABLE users; --",
        "test@example.com\r\nBcc: attacker@evil.com"
    ]
    for malicious_email in malicious_emails:
        with pytest.raises(ValidationError):
            UserRegisterRequest(
                email=malicious_email,
                password="SecurePass123!",
                name="Test User"
            )
```

### Integration Testing

```python
async def test_registration_flow():
    # Test complete registration flow
    registration_data = {
        "email": "integration@example.com",
        "password": "IntegrationTest123!",
        "name": "Integration User"
    }

    # Schema validation
    request = UserRegisterRequest(**registration_data)

    # Service integration
    response = await register_user_service(request)

    # Response validation
    auth_response = AuthResponse(**response)
    assert auth_response.token_type == "bearer"
    assert len(auth_response.access_token) > 0
```

## Related Files

### Dependencies

- `src.utils.validation` - Email and password validation utilities
- `pydantic` - Schema validation framework
- `typing_extensions` - TypedDict and advanced typing support

### API Integration

- `src.api.v1.auth` - Authentication endpoints using these schemas
- `src.services.user` - User service business logic
- `src.repositories.user` - User data access layer

### Security Integration

- `src.core.security` - Password hashing and token generation
- `src.utils.errors` - Custom exception handling
- `src.utils.validation` - Validation utility functions

## Configuration

### Validation Settings

```python
# Validation configuration constants
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MAX_NAME_LENGTH = 128
TOKEN_TYPE_BEARER = "bearer"
```

### Pydantic Configuration

```python
# Global Pydantic settings
class AuthSchemaConfig:
    validate_assignment = True
    str_strip_whitespace = True
    json_schema_extra = {
        "examples": [...]
    }
```

This authentication schema module provides a comprehensive, secure foundation for all authentication operations in the ReViewPoint application, ensuring data integrity, type safety, and security through well-designed Pydantic validation patterns.
