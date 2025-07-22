# utils/validation.py - Input Validation Utilities

## Purpose

The `utils/validation.py` module provides comprehensive input validation utilities for the ReViewPoint platform. It implements secure validation functions for email addresses, passwords, and other user input data with detailed error reporting and security considerations.

## Key Components

### Core Imports and Dependencies

#### Essential Validation Libraries

```python
import re
from typing import Literal

from email_validator import EmailNotValidError
from email_validator import validate_email as _validate_email
from typing_extensions import TypedDict
```

### Email Validation

#### RFC-Compliant Email Validation

```python
def validate_email(email: str) -> bool:
    """
    Validate email address using the email_validator library.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    try:
        # Limit input length to 320 characters (max email length per RFC)
        if len(email) > 320:
            return False
        _validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False
```

**Key Features:**
- RFC-compliant email validation using the `email_validator` library
- Maximum length enforcement (320 characters per RFC 5321)
- Deliverability checking disabled for performance and privacy
- Graceful error handling with boolean return

**Usage Examples:**
```python
# Valid email addresses
assert validate_email("user@example.com") == True
assert validate_email("test.email+tag@domain.co.uk") == True

# Invalid email addresses
assert validate_email("invalid.email") == False
assert validate_email("@domain.com") == False
assert validate_email("user@") == False

# Edge cases
assert validate_email("") == False
assert validate_email("a" * 321) == False  # Too long
```

### Password Validation

#### Comprehensive Password Security Validation

```python
def validate_password(password: str, min_length: int = 8) -> bool:
    """
    Basic password validation: min length, at least one digit, one letter.

    Args:
        password (str): The password to validate.
        min_length (int, optional): Minimum length. Defaults to 8.

    Returns:
        bool: True if valid, False otherwise.
    """
    is_long_enough: bool = len(password) >= min_length
    has_letter: bool = bool(re.search(r"[A-Za-z]", password))
    has_digit: bool = bool(re.search(r"\d", password))
    result: bool = is_long_enough and has_letter and has_digit
    return result
```

**Password Requirements:**
- Minimum length (default: 8 characters)
- At least one letter (A-Z or a-z)
- At least one digit (0-9)
- Configurable minimum length parameter

**Usage Examples:**
```python
# Valid passwords
assert validate_password("password123") == True
assert validate_password("MySecret1") == True
assert validate_password("abc123def") == True

# Invalid passwords
assert validate_password("password") == False  # No digits
assert validate_password("12345678") == False  # No letters
assert validate_password("pass1") == False     # Too short

# Custom minimum length
assert validate_password("short1", min_length=10) == False
assert validate_password("longenough1", min_length=10) == True
```

### Advanced Password Validation

#### Detailed Password Error Reporting

```python
class PasswordValidationError(TypedDict, total=False):
    error: Literal[
        "Password must be at least {min_length} characters.",
        "Password must contain at least one letter.",
        "Password must contain at least one digit.",
    ]
    min_length: int

def get_password_validation_error(password: str, min_length: int = 8) -> str | None:
    """
    Get the error message for password validation.

    Args:
        password (str): The password to validate.
        min_length (int, optional): Minimum length. Defaults to 8.

    Returns:
        Optional[str]: Error message if invalid, None if valid.

    Raises:
        ValueError: If min_length is less than 1.
    """
    if min_length < 1:
        raise ValueError("min_length must be at least 1")
    if len(password) < min_length:
        return f"Password must be at least {min_length} characters."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    return None
```

**Features:**
- Specific error message for each validation failure
- Type-safe error message literals
- Parameter validation with appropriate exceptions
- Clear, user-friendly error messages

**Usage Examples:**
```python
# Valid password returns None
assert get_password_validation_error("validpass1") is None

# Specific error messages
assert get_password_validation_error("short") == "Password must be at least 8 characters."
assert get_password_validation_error("nodigits") == "Password must contain at least one digit."
assert get_password_validation_error("12345678") == "Password must contain at least one letter."

# Custom minimum length
error = get_password_validation_error("pass1", min_length=10)
assert error == "Password must be at least 10 characters."

# Parameter validation
try:
    get_password_validation_error("test", min_length=0)
    assert False, "Should raise ValueError"
except ValueError as e:
    assert str(e) == "min_length must be at least 1"
```

## Integration Patterns

### Service Layer Integration

#### User Registration Validation

```python
from src.utils.validation import validate_email, get_password_validation_error
from src.utils.errors import ValidationError

async def register_user(email: str, password: str, name: str | None = None) -> User:
    """Register a new user with comprehensive validation."""
    
    # Email validation
    if not validate_email(email):
        raise ValidationError("Invalid email format")
    
    # Password validation with detailed error
    password_error = get_password_validation_error(password)
    if password_error:
        raise ValidationError(password_error)
    
    # Additional business logic validation
    if await user_exists(email):
        raise ValidationError("Email already registered")
    
    return await create_user(email, password, name)
```

### API Layer Integration

#### FastAPI Request Validation

```python
from fastapi import HTTPException
from pydantic import BaseModel, validator

class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    name: str | None = None
    
    @validator('email')
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password_field(cls, v):
        error = get_password_validation_error(v)
        if error:
            raise ValueError(error)
        return v

@app.post("/register")
async def register_user_endpoint(request: UserRegistrationRequest):
    try:
        user = await user_service.register_user(
            request.email, 
            request.password, 
            request.name
        )
        return {"message": "User registered successfully", "user_id": user.id}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### Frontend Integration

#### JavaScript/TypeScript Validation

```typescript
// TypeScript client-side validation helpers
export interface PasswordValidationResult {
  isValid: boolean;
  errors: string[];
}

export function validatePassword(
  password: string, 
  minLength: number = 8
): PasswordValidationResult {
  const errors: string[] = [];
  
  if (password.length < minLength) {
    errors.push(`Password must be at least ${minLength} characters.`);
  }
  
  if (!/[A-Za-z]/.test(password)) {
    errors.push("Password must contain at least one letter.");
  }
  
  if (!/\d/.test(password)) {
    errors.push("Password must contain at least one digit.");
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function validateEmail(email: string): boolean {
  // Basic client-side validation (server-side validation is authoritative)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return email.length <= 320 && emailRegex.test(email);
}
```

## Security Considerations

### Input Sanitization

```python
import html
import re

def sanitize_user_input(input_str: str, max_length: int = 1000) -> str:
    """Sanitize user input for security."""
    # Trim whitespace
    sanitized = input_str.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # HTML escape for XSS prevention
    sanitized = html.escape(sanitized)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\'\&]', '', sanitized)
    
    return sanitized
```

### Rate Limiting Integration

```python
from src.utils.rate_limit import AsyncRateLimiter

# Rate limiter for validation attempts
validation_limiter = AsyncRateLimiter(max_calls=10, period=60.0)

async def rate_limited_validation(user_id: str, validator_func, *args):
    """Apply rate limiting to validation functions."""
    key = f"validation:{user_id}"
    
    if not await validation_limiter.is_allowed(key):
        raise ValidationError("Too many validation attempts. Please try again later.")
    
    return validator_func(*args)
```

## Best Practices

### Validation Strategy

- **Client-side validation**: Immediate user feedback, UX improvement
- **Server-side validation**: Security enforcement, authoritative validation
- **Database constraints**: Final data integrity protection
- **Multiple layers**: Defense in depth approach

### Error Messaging

- Provide specific, actionable error messages
- Use consistent language and terminology
- Avoid exposing internal system details
- Support internationalization when needed

### Performance Considerations

- Cache validation results when appropriate
- Use efficient regex patterns
- Validate incrementally for complex forms
- Implement rate limiting for expensive validations

### Testing Validation Functions

```python
import pytest

class TestValidation:
    """Comprehensive validation testing."""
    
    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("invalid.email", False),
        ("test+tag@domain.co.uk", True),
        ("", False),
        ("a" * 321, False),  # Too long
    ])
    def test_email_validation(self, email, expected):
        assert validate_email(email) == expected
    
    @pytest.mark.parametrize("password,min_length,expected", [
        ("validpass1", 8, True),
        ("short1", 8, False),
        ("nodigits", 8, False),
        ("12345678", 8, False),
        ("longenough1", 10, True),
    ])
    def test_password_validation(self, password, min_length, expected):
        assert validate_password(password, min_length) == expected
    
    def test_password_error_messages(self):
        assert get_password_validation_error("short") == "Password must be at least 8 characters."
        assert get_password_validation_error("nodigits") == "Password must contain at least one digit."
        assert get_password_validation_error("12345678") == "Password must contain at least one letter."
        assert get_password_validation_error("validpass1") is None
```

This validation system provides robust, secure, and user-friendly input validation capabilities that integrate seamlessly with the application's architecture while maintaining security and performance standards.
