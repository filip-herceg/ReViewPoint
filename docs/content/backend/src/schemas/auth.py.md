# Authentication Schema Module

## Overview

The `auth.py` schema module provides comprehensive Pydantic model definitions for authentication-related operations in the ReViewPoint application. This module implements strict validation schemas for user registration, login, password reset flows, and authentication responses with integrated security validation and proper error handling.

**Key Features:**

- Complete authentication request/response schemas
- Integrated email and password validation
- Password reset workflow support
- Type-safe authentication responses
- Custom field validators with security rules
- TypedDict compatibility for flexible usage

## Module Structure

```python
from collections.abc import Callable
from typing import ClassVar, Final, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing_extensions import TypedDict
from src.utils.validation import get_password_validation_error, validate_email
```

### Core Dependencies

#### Internal Validation Systems

- `src.utils.validation.validate_email` - Email format validation
- `src.utils.validation.get_password_validation_error` - Password strength validation

#### External Dependencies

- `pydantic` - Core validation and serialization framework
- `pydantic.EmailStr` - Email validation type
- `typing_extensions.TypedDict` - Type dictionary support

## Authentication Request Schemas

### 1. User Registration Schema

#### UserRegisterRequest Class

```python
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str | None = Field(None, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError("Invalid email format.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        err = get_password_validation_error(v)
        if err:
            raise ValueError(err)
        return v
```

**Purpose:** Validates user registration requests with comprehensive security validation.

**Key Features:**

- **Email Validation:** Dual validation with EmailStr type and custom validator
- **Password Security:** Length constraints (8-128 chars) with strength validation
- **Optional Name Field:** User-friendly name with length limits
- **Custom Validators:** Integration with utility validation functions
- **Type Safety:** ClassVar annotations for validator method signatures

**Validation Rules:**

1. **Email Requirements:**
   - Must be valid EmailStr format (Pydantic built-in)
   - Must pass custom email validation function
   - Raises ValueError for invalid formats

2. **Password Requirements:**
   - Minimum 8 characters, maximum 128 characters
   - Must pass password strength validation
   - Custom error messages from validation utility

3. **Name Requirements:**
   - Optional field (can be None)
   - Maximum 128 characters when provided
   - No special validation requirements

**Security Considerations:**

- Password validation integrates with centralized security rules
- Email validation prevents malformed addresses
- Field length limits prevent buffer overflow attacks
- Custom validators provide detailed error messages

### 2. User Login Schema

#### UserLoginRequest Class

```python
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
```

**Purpose:** Simple login credential validation without complex rules.

**Key Features:**

- **EmailStr Validation:** Built-in email format validation
- **Plain Password Field:** No length restrictions for login (authentication handles security)
- **Minimal Validation:** Focus on format rather than strength during login
- **Type Safety:** Strict type definitions for credential fields

**Design Rationale:**

- Login should accept any previously valid credentials
- Password strength validation occurs during registration, not login
- Email format validation prevents obvious input errors
- Simple schema reduces login friction

### 3. Password Reset Schemas

#### PasswordResetRequest Class

```python
class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError("Invalid email format.")
        return v
```

**Purpose:** Validates password reset initiation requests.

**Key Features:**

- **Email-Only Request:** Only requires email for password reset initiation
- **Dual Email Validation:** EmailStr type plus custom validator
- **Security Focus:** Validates email format to prevent abuse
- **Error Prevention:** Clear error messages for invalid emails

#### PasswordResetConfirmRequest Class

```python
class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        err = get_password_validation_error(v)
        if err:
            raise ValueError(err)
        return v
```

**Purpose:** Validates password reset confirmation with new password.

**Key Features:**

- **Token Validation:** Accepts reset token as string (validation happens in service layer)
- **New Password Security:** Same validation rules as registration
- **Length Constraints:** 8-128 character requirements
- **Strength Validation:** Integration with password validation utility

**Security Flow:**

1. Token received from password reset email
2. New password must meet all strength requirements
3. Service layer validates token authenticity and expiration
4. Schema ensures new password meets security standards

## Authentication Response Schemas

### 1. Authentication Response

#### AuthResponse Class

```python
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = TOKEN_TYPE_BEARER
```

**Purpose:** Standardized authentication response for successful login/registration.

**Key Features:**

- **JWT Tokens:** Both access and refresh tokens included
- **Type Safety:** Literal type for token_type ensures consistency
- **Constant Integration:** Uses module-level constant for token type
- **Standard Compliance:** Follows OAuth2 bearer token standard

#### AuthResponseDict TypedDict

```python
class AuthResponseDict(TypedDict):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"]
```

**Purpose:** TypedDict version for compatibility with non-Pydantic code.

**Use Cases:**

- Function return types that don't need Pydantic features
- Integration with legacy code expecting plain dictionaries
- Performance-critical paths where Pydantic overhead matters

### 2. Message Response

#### MessageResponse Class

```python
class MessageResponse(BaseModel):
    message: str
```

**Purpose:** Generic message response for operations that return status messages.

**Common Usage:**

- Password reset initiation confirmation
- Logout success messages
- General operation status responses
- Error message standardization

#### MessageResponseDict TypedDict

```python
class MessageResponseDict(TypedDict):
    message: str
```

**Purpose:** TypedDict version for flexible message responses.

## Constants and Type Definitions

### Token Type Constant

```python
TOKEN_TYPE_BEARER: Final[Literal["bearer"]] = "bearer"
```

**Purpose:** Centralized constant for OAuth2 bearer token type.

**Benefits:**

- Type safety with Literal type
- Single source of truth for token type
- Prevents typos and inconsistencies
- Easy to change if standards evolve

### Validator Type Annotations

```python
_email_validator: ClassVar[Callable[[type["UserRegisterRequest"], str], str]]
_password_validator: ClassVar[Callable[[type["UserRegisterRequest"], str], str]]
```

**Purpose:** Type hints for field validator methods.

**Technical Details:**

- ClassVar indicates class-level attributes
- Callable types document validator signatures
- Generic type parameters for different model classes
- Helps with IDE support and static analysis

## Field Validation Patterns

### Email Validation Strategy

```python
@field_validator("email")
@classmethod
def validate_email_field(cls, v: str) -> str:
    if not validate_email(v):
        raise ValueError("Invalid email format.")
    return v
```

**Validation Layers:**

1. **Pydantic EmailStr:** Basic format validation
2. **Custom Validator:** Additional business rules
3. **Utility Integration:** Centralized validation logic

### Password Validation Strategy

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

- Integration with centralized password policy
- Detailed error messages for user feedback
- Consistent validation across all password fields
- Easy policy updates through utility functions

## Error Handling and Validation

### Validation Error Patterns

```python
# Email validation failure
ValueError("Invalid email format.")

# Password validation failure
ValueError("Password must contain at least one uppercase letter")
```

**Error Handling Strategy:**

- Clear, user-friendly error messages
- Specific validation failures rather than generic errors
- Integration with API error response formatting
- Consistent error format across all validators

### Pydantic Integration

```python
try:
    user_request = UserRegisterRequest(**request_data)
except ValidationError as e:
    # e.errors() contains detailed field-level errors
    for error in e.errors():
        field = error['loc'][0]
        message = error['msg']
        # Handle specific field errors
```

**Error Information Available:**

- Field location (`loc`)
- Error message (`msg`)
- Error type (`type`)
- Input value (`input`)

## Usage Examples

### Registration Workflow

```python
# Valid registration request
registration_data = {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
}

try:
    request = UserRegisterRequest(**registration_data)
    # Process registration with validated data
    user = await user_service.register(request)

    # Return authentication response
    response = AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )
    return response

except ValidationError as e:
    # Handle validation errors
    raise HTTPException(status_code=422, detail=e.errors())
```

### Login Workflow

```python
# Simple login validation
login_data = {"email": "user@example.com", "password": "password123"}

try:
    request = UserLoginRequest(**login_data)
    # Authenticate user
    tokens = await auth_service.authenticate(request.email, request.password)

    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )

except ValidationError:
    raise HTTPException(status_code=422, detail="Invalid credentials format")
```

### Password Reset Workflow

```python
# Password reset initiation
reset_request_data = {"email": "user@example.com"}
reset_request = PasswordResetRequest(**reset_request_data)

# Send reset email and return confirmation
await auth_service.send_password_reset_email(reset_request.email)
return MessageResponse(message="Password reset email sent")

# Password reset confirmation
reset_confirm_data = {
    "token": "reset_token_from_email",
    "new_password": "NewSecurePassword123!"
}
confirm_request = PasswordResetConfirmRequest(**reset_confirm_data)

# Reset password with validated data
await auth_service.confirm_password_reset(
    confirm_request.token,
    confirm_request.new_password
)
return MessageResponse(message="Password reset successful")
```

## API Integration

### FastAPI Endpoint Usage

```python
@router.post("/register", response_model=AuthResponse)
async def register(request: UserRegisterRequest) -> AuthResponse:
    # request is automatically validated by FastAPI
    user = await user_service.create_user(request)
    tokens = await auth_service.generate_tokens(user)

    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: UserLoginRequest) -> AuthResponse:
    tokens = await auth_service.authenticate(request.email, request.password)
    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )
```

### OpenAPI Documentation

The schemas automatically generate comprehensive OpenAPI documentation with:

- Field descriptions and constraints
- Example values for testing
- Validation error responses
- Type information for client generation

## Testing Considerations

### Schema Validation Testing

```python
def test_user_register_request_valid():
    data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    request = UserRegisterRequest(**data)
    assert request.email == "test@example.com"
    assert request.name == "Test User"

def test_user_register_request_invalid_email():
    data = {
        "email": "invalid-email",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(**data)

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('email',) for error in errors)

def test_user_register_request_weak_password():
    data = {
        "email": "test@example.com",
        "password": "weak",
        "name": "Test User"
    }
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(**data)
```

### Mock Data Generation

```python
# Test data factories
def create_valid_registration_data():
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "name": "Test User"
    }

def create_valid_login_data():
    return {
        "email": "test@example.com",
        "password": "password123"
    }
```

## Performance Considerations

### Validation Efficiency

- **Field Validators:** Cached by Pydantic for repeated use
- **EmailStr Type:** Efficient email format validation
- **Custom Validators:** Only run when fields are present
- **Error Short-Circuiting:** Validation stops on first error per field

### Memory Optimization

- **Literal Types:** Use interned strings for constants
- **Optional Fields:** Efficient handling of None values
- **TypedDict Alternatives:** Available for performance-critical paths
- **Model Caching:** Pydantic caches model metadata

## Security Best Practices

### Input Validation

- All user inputs validated before processing
- Length limits prevent buffer overflow attacks
- Email format validation prevents injection
- Password strength requirements enforced

### Error Information

- Validation errors don't expose internal system details
- Error messages are user-friendly but not revealing
- Sensitive information never included in error responses
- Consistent error format prevents information leakage

## Related Modules

### **Core Dependencies**

- **`src.utils.validation`** - Email and password validation functions
- **`src.utils.errors`** - Custom exception classes for validation errors

### **Integration Points**

- **`src.api.v1.auth`** - Authentication endpoints using these schemas
- **`src.services.user`** - User service receiving validated schema objects
- **`src.core.security`** - JWT token generation and validation

### **External Dependencies**

- **`pydantic[email]`** - EmailStr validation support
- **`typing_extensions`** - Enhanced typing for older Python versions

## Configuration Dependencies

- Email validation configuration in utils module
- Password complexity requirements in validation utilities
- JWT configuration for token generation
- API error response formatting configuration

## Summary

The `auth.py` schema module provides comprehensive, secure validation for all authentication-related operations in the ReViewPoint application. Through strict Pydantic models with custom validators, integrated security validation, and clear request/response separation, it ensures authentication data integrity and security throughout the system.

Key strengths include comprehensive security validation with password and email rules, clear authentication workflow support, type safety with Literal types and ClassVar annotations, flexible usage with both Pydantic models and TypedDict alternatives, and integration with centralized validation utilities. The module serves as the foundation for secure authentication across the entire application.
