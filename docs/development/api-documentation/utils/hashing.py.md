# Password Hashing Utilities Documentation

## Purpose

The `hashing.py` module provides secure password hashing and verification utilities for the ReViewPoint application. This module implements industry-standard bcrypt hashing with configurable parameters, ensuring strong password security throughout the authentication system. It emphasizes type safety, security best practices, and comprehensive protection against password-related vulnerabilities.

## Architecture

The password hashing system follows a security-first design:

- **Industry Standard**: Uses bcrypt algorithm for proven password security
- **Configurable Security**: Adjustable rounds and identifiers for future-proofing
- **Type Safety**: Comprehensive type annotations and protocol-based configuration
- **Zero Exposure**: Never logs or exposes plain passwords in any context
- **Performance Optimized**: Efficient hashing with configurable cost parameters
- **Future-Proof**: Designed for easy migration to new hashing standards

## Security Foundation

### Cryptographic Standards

**bcrypt Algorithm Benefits:**

- **Adaptive Hashing**: Computational cost increases with hardware improvements
- **Salt Integration**: Built-in salt generation prevents rainbow table attacks
- **Time-Tested**: Extensively vetted cryptographic algorithm
- **Industry Standard**: Widely adopted in security-critical applications

**Configuration Security:**

- **Adjustable Rounds**: Configurable work factor for performance vs. security balance
- **Version Control**: Configurable bcrypt identifier for algorithm versioning
- **Future Migration**: Easy upgrade path to stronger algorithms

### Type System

**Settings Protocol Definition:**

```python
from typing import Protocol

class SettingsProtocol(Protocol):
    BCRYPT_ROUNDS: int                         # Hashing rounds (work factor)
    BCRYPT_IDENT: str                         # bcrypt identifier version
```

**Design Purpose:**

- **Type Safety**: Ensures configuration contains required password settings
- **Interface Contract**: Clear specification of required configuration
- **Runtime Validation**: Type checking prevents configuration errors
- **Flexibility**: Allows different configuration implementations

### Security Constants

**Algorithm Configuration:**

```python
from typing import Final, Literal

SCHEME_BCRYPT: Final = "bcrypt"                           # Primary hashing scheme
SCHEMES: Final[tuple[Literal["bcrypt"], ...]] = (SCHEME_BCRYPT,)  # Supported schemes
DEPRECATED_POLICY: Final = "auto"                         # Automatic deprecation handling
```

**Security Features:**

- **Algorithm Lock**: Fixed to bcrypt for consistency
- **Future Extension**: Easy to add new algorithms while maintaining compatibility
- **Deprecation Management**: Automatic handling of deprecated hash formats
- **Type Safety**: Literal types prevent algorithm misconfigurations

## Core Functions

### Password Context Creation

**\_get_pwd_context Function:**

```python
from passlib.context import CryptContext

def _get_pwd_context() -> CryptContext:
    """Get password context with current settings.

    Returns:
        CryptContext: The password hashing context.

    Raises:
        AttributeError: If settings do not have required attributes.
    """
```

**Implementation Details:**

1. **Settings Retrieval:**

   ```python
   settings: SettingsProtocol = get_settings()  # type: ignore[assignment]
   ```

2. **Configuration Extraction:**

   ```python
   bcrypt_rounds: int = getattr(settings, "BCRYPT_ROUNDS", 12)
   bcrypt_ident: str = getattr(settings, "BCRYPT_IDENT", "2b")
   ```

3. **Context Creation:**

   ```python
   return CryptContext(
       schemes=schemes,
       deprecated=deprecated,
       bcrypt__rounds=bcrypt_rounds,      # Configurable work factor
       bcrypt__ident=bcrypt_ident,        # Algorithm version
   )
   ```

**Security Configuration:**

- **Rounds (Work Factor)**: Default 12 provides strong security with reasonable performance
- **Identifier**: "2b" uses latest bcrypt version with full UTF-8 support
- **Schemes**: Single bcrypt scheme prevents algorithm confusion attacks
- **Deprecation**: Automatic handling of legacy hash formats

### Password Hashing

**hash_password Function:**

```python
def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt.

    Args:
        password (str): The plain password to hash.

    Returns:
        str: The bcrypt hash of the password.

    Raises:
        ValueError: If password is not hashable.
    """
```

**Security Implementation:**

1. **Security Logging:**

   ```python
   logger.debug("Hashing password (input not logged)")
   ```

2. **Context Retrieval:**

   ```python
   pwd_context: CryptContext = _get_pwd_context()
   ```

3. **Hash Generation:**

   ```python
   hash_result: str = pwd_context.hash(password)
   return hash_result
   ```

**Security Features:**

- **Zero Exposure**: Plain password never logged or exposed
- **Fresh Context**: Uses current configuration for each operation
- **Type Safety**: Strict typing prevents parameter errors
- **Error Handling**: Comprehensive error handling with meaningful messages

### Password Verification

**verify_password Function:**

```python
def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a given bcrypt hash.

    Args:
        plain (str): The plain password to verify.
        hashed (str): The bcrypt hash to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.

    Raises:
        ValueError: If verification fails due to invalid hash or input.
    """
```

**Security Implementation:**

1. **Security Logging:**

   ```python
   logger.debug("Verifying password (input not logged)")
   ```

2. **Context Retrieval:**

   ```python
   pwd_context: CryptContext = _get_pwd_context()
   ```

3. **Verification:**

   ```python
   result: bool = pwd_context.verify(plain, hashed)
   return result
   ```

**Security Features:**

- **Timing Attack Protection**: bcrypt provides constant-time comparison
- **Zero Exposure**: Neither plain password nor hash details logged
- **Format Validation**: Validates hash format before verification
- **Error Isolation**: Specific error handling prevents information leakage

## Usage Patterns

### User Registration

**Secure User Registration with Password Hashing:**

```python
from src.utils.hashing import hash_password
from src.models.user import User
from fastapi import HTTPException

async def register_user(user_data: dict) -> User:
    """Register new user with secure password hashing."""

    # Validate password strength
    password = user_data.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )

    # Check password complexity
    if not has_required_complexity(password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain uppercase, lowercase, digit, and special character"
        )

    # Check if email already exists
    existing_user = await user_repository.get_user_by_email(user_data["email"])
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        # Hash password securely
        hashed_password = hash_password(password)

        # Create user with hashed password
        user_data["password_hash"] = hashed_password
        del user_data["password"]  # Remove plain password

        # Save user
        user = await user_repository.create_user(user_data)

        logger.info(f"User registered successfully: {user.email}")

        return user

    except ValueError as e:
        logger.error(f"Password hashing failed during registration: {e}")
        raise HTTPException(
            status_code=500,
            detail="User registration failed"
        )
    except Exception as e:
        logger.error(f"User registration error: {e}")
        raise HTTPException(
            status_code=500,
            detail="User registration failed"
        )

def has_required_complexity(password: str) -> bool:
    """Check if password meets complexity requirements."""

    import re

    # At least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # At least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # At least one digit
    if not re.search(r'\d', password):
        return False

    # At least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True

# API endpoint for user registration
@app.post("/auth/register")
async def register_endpoint(user_request: UserRegistrationRequest):
    """User registration endpoint with secure password handling."""

    user_data = {
        "email": user_request.email.lower().strip(),
        "username": user_request.username.strip(),
        "password": user_request.password,
        "first_name": user_request.first_name.strip(),
        "last_name": user_request.last_name.strip()
    }

    user = await register_user(user_data)

    # Return user data without password information
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.isoformat()
    }
```

### User Authentication

**Secure Login with Password Verification:**

```python
from src.utils.hashing import verify_password
from src.core.security import create_access_token

async def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user with email and password."""

    try:
        # Get user by email
        user = await user_repository.get_user_by_email(email)

        if not user:
            logger.warning(f"Login attempt for non-existent email: {email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            raise HTTPException(
                status_code=401,
                detail="Account is deactivated"
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Invalid password attempt for user: {email}")

            # Increment failed login attempts
            await user_repository.increment_failed_login_attempts(user.id)

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Reset failed login attempts on successful login
        await user_repository.reset_failed_login_attempts(user.id)

        # Update last login timestamp
        await user_repository.update_last_login(user.id)

        # Create access token
        access_token = create_access_token(data={"sub": user.id})

        logger.info(f"User authenticated successfully: {email}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication error for {email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )

# API endpoint for user login
@app.post("/auth/login")
async def login_endpoint(login_request: LoginRequest):
    """User login endpoint with secure authentication."""

    # Validate input
    email = login_request.email.lower().strip()
    password = login_request.password

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    # Rate limiting check
    await check_login_rate_limit(email)

    # Authenticate user
    auth_result = await authenticate_user(email, password)

    return auth_result
```

### Password Change Operations

**Secure Password Change with Verification:**

```python
from src.utils.hashing import hash_password, verify_password

async def change_user_password(
    user_id: str,
    current_password: str,
    new_password: str
) -> bool:
    """Change user password with current password verification."""

    try:
        # Get user
        user = await user_repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            logger.warning(f"Invalid current password for password change: {user.email}")
            raise HTTPException(
                status_code=401,
                detail="Current password is incorrect"
            )

        # Validate new password strength
        if len(new_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="New password must be at least 8 characters long"
            )

        if not has_required_complexity(new_password):
            raise HTTPException(
                status_code=400,
                detail="New password must meet complexity requirements"
            )

        # Check if new password is different from current
        if verify_password(new_password, user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="New password must be different from current password"
            )

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update password in database
        await user_repository.update_password_hash(user_id, new_password_hash)

        # Invalidate all existing sessions
        await token_repository.blacklist_user_tokens(user_id)

        logger.info(f"Password changed successfully for user: {user.email}")

        return True

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Password change error for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password change failed"
        )

# API endpoint for password change
@app.post("/auth/change-password")
async def change_password_endpoint(
    password_change: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """Change password endpoint with security validation."""

    success = await change_user_password(
        user_id=current_user.id,
        current_password=password_change.current_password,
        new_password=password_change.new_password
    )

    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Password change failed"
        )
```

### Password Reset Operations

**Secure Password Reset with Token Verification:**

```python
from src.utils.hashing import hash_password

async def reset_user_password(reset_token: str, new_password: str) -> bool:
    """Reset user password using verified reset token."""

    try:
        # Verify reset token
        token_data = await token_repository.verify_password_reset_token(reset_token)

        if not token_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token"
            )

        user_id = token_data["user_id"]

        # Get user
        user = await user_repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )

        if not has_required_complexity(new_password):
            raise HTTPException(
                status_code=400,
                detail="Password must meet complexity requirements"
            )

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update password
        await user_repository.update_password_hash(user_id, new_password_hash)

        # Mark reset token as used
        await token_repository.mark_reset_token_used(reset_token)

        # Invalidate all existing sessions
        await token_repository.blacklist_user_tokens(user_id)

        logger.info(f"Password reset successfully for user: {user.email}")

        return True

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password reset failed"
        )

# API endpoint for password reset
@app.post("/auth/reset-password")
async def reset_password_endpoint(reset_request: PasswordResetRequest):
    """Password reset endpoint with token verification."""

    success = await reset_user_password(
        reset_token=reset_request.token,
        new_password=reset_request.new_password
    )

    if success:
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Password reset failed"
        )
```

### Administrative Password Operations

**Admin Password Management:**

```python
async def admin_reset_user_password(
    admin_user_id: str,
    target_user_id: str,
    temporary_password: str
) -> dict:
    """Admin function to reset user password (requires admin privileges)."""

    try:
        # Verify admin privileges
        admin_user = await user_repository.get_user_by_id(admin_user_id)

        if not admin_user or not admin_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required"
            )

        # Get target user
        target_user = await user_repository.get_user_by_id(target_user_id)

        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate secure temporary password if not provided
        if not temporary_password:
            import secrets
            import string

            # Generate random password with required complexity
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            temporary_password = ''.join(secrets.choice(chars) for _ in range(12))

        # Validate temporary password
        if not has_required_complexity(temporary_password):
            raise HTTPException(
                status_code=400,
                detail="Temporary password does not meet complexity requirements"
            )

        # Hash temporary password
        temp_password_hash = hash_password(temporary_password)

        # Update user password
        await user_repository.update_password_hash(target_user_id, temp_password_hash)

        # Set password change required flag
        await user_repository.set_password_change_required(target_user_id, True)

        # Invalidate all existing sessions for target user
        await token_repository.blacklist_user_tokens(target_user_id)

        # Log admin action
        logger.info(f"Admin password reset performed", extra={
            "admin_user_id": admin_user_id,
            "target_user_id": target_user_id,
            "target_user_email": target_user.email
        })

        return {
            "message": "Password reset successfully",
            "temporary_password": temporary_password,
            "password_change_required": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Admin password reset error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Admin password reset failed"
        )
```

## Performance Considerations

### Hashing Performance

**bcrypt Configuration Balance:**

```python
# Performance vs Security Configuration
BCRYPT_PERFORMANCE_CONFIGS = {
    "development": {
        "rounds": 10,        # Faster for development
        "ident": "2b"
    },
    "testing": {
        "rounds": 4,         # Minimal for tests
        "ident": "2b"
    },
    "production": {
        "rounds": 12,        # Strong security for production
        "ident": "2b"
    },
    "high_security": {
        "rounds": 15,        # Maximum security for sensitive systems
        "ident": "2b"
    }
}

def get_bcrypt_config(environment: str) -> dict:
    """Get bcrypt configuration for environment."""

    return BCRYPT_PERFORMANCE_CONFIGS.get(
        environment,
        BCRYPT_PERFORMANCE_CONFIGS["production"]
    )
```

### Async Password Operations

**Async Wrapper for CPU-Intensive Operations:**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Thread pool for CPU-intensive password operations
_password_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="password")

async def hash_password_async(password: str) -> str:
    """Async wrapper for password hashing to prevent blocking."""

    loop = asyncio.get_event_loop()

    # Run password hashing in thread pool
    hash_result = await loop.run_in_executor(
        _password_executor,
        hash_password,
        password
    )

    return hash_result

async def verify_password_async(plain: str, hashed: str) -> bool:
    """Async wrapper for password verification to prevent blocking."""

    loop = asyncio.get_event_loop()

    # Run password verification in thread pool
    verify_result = await loop.run_in_executor(
        _password_executor,
        partial(verify_password, plain, hashed)
    )

    return verify_result

# Usage in async contexts
async def async_authenticate_user(email: str, password: str) -> dict:
    """Async authentication with non-blocking password verification."""

    # Get user (async database operation)
    user = await user_repository.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password asynchronously
    is_valid = await verify_password_async(password, user.password_hash)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Continue with authentication...
    return await create_user_session(user)
```

## Security Best Practices

### Password Security Guidelines

**Implementation Security:**

```python
# Secure password handling checklist
SECURITY_CHECKLIST = {
    "never_log_passwords": True,           # Never log plain passwords
    "secure_memory_handling": True,        # Clear password variables
    "timing_attack_protection": True,      # Use constant-time comparison
    "salt_integration": True,              # bcrypt handles salts automatically
    "configurable_work_factor": True,      # Adjustable bcrypt rounds
    "password_complexity": True,           # Enforce strong passwords
    "rate_limiting": True,                 # Prevent brute force attacks
    "account_lockout": True,               # Lock accounts after failed attempts
    "secure_transmission": True,           # HTTPS for password transmission
    "session_invalidation": True,          # Invalidate sessions on password change
}

def validate_password_security(password: str, user_data: dict = None) -> list:
    """Comprehensive password security validation."""

    errors = []

    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if len(password) > 128:
        errors.append("Password is too long (maximum 128 characters)")

    # Complexity checks
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    # Common password checks
    if password.lower() in COMMON_PASSWORDS:
        errors.append("Password is too common")

    # Personal information checks
    if user_data:
        user_info = [
            user_data.get("email", "").split("@")[0].lower(),
            user_data.get("username", "").lower(),
            user_data.get("first_name", "").lower(),
            user_data.get("last_name", "").lower()
        ]

        for info in user_info:
            if info and info in password.lower():
                errors.append("Password should not contain personal information")
                break

    return errors

# Common passwords list (subset)
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123",
    "password123", "admin", "letmein", "welcome", "monkey"
}
```

### Error Handling Security

**Secure Error Handling:**

```python
class PasswordSecurityError(Exception):
    """Base exception for password security errors."""
    pass

class WeakPasswordError(PasswordSecurityError):
    """Raised when password does not meet security requirements."""
    pass

class PasswordHashingError(PasswordSecurityError):
    """Raised when password hashing fails."""
    pass

def secure_hash_password(password: str, user_data: dict = None) -> str:
    """Hash password with comprehensive security validation."""

    try:
        # Validate password security
        validation_errors = validate_password_security(password, user_data)

        if validation_errors:
            raise WeakPasswordError(f"Password security validation failed: {validation_errors}")

        # Hash password
        hashed = hash_password(password)

        # Verify hash was created properly
        if not hashed or len(hashed) < 50:  # bcrypt hashes are typically 60 characters
            raise PasswordHashingError("Password hashing produced invalid result")

        # Verify hash works
        if not verify_password(password, hashed):
            raise PasswordHashingError("Password hash verification failed")

        return hashed

    except (WeakPasswordError, PasswordHashingError):
        # Re-raise known security errors
        raise
    except Exception as e:
        # Log unexpected errors without exposing details
        logger.error(f"Unexpected password hashing error: {type(e).__name__}")
        raise PasswordHashingError("Password hashing failed")
    finally:
        # Clear password from memory (Python limitation: this is best effort)
        password = None
```

## Testing Strategies

### Password Hashing Tests

**Comprehensive Password Testing:**

```python
import pytest
from src.utils.hashing import hash_password, verify_password

class TestPasswordHashing:
    """Test suite for password hashing utilities."""

    def test_password_hashing_basic(self):
        """Test basic password hashing functionality."""

        password = "TestPassword123!"

        # Hash password
        hashed = hash_password(password)

        # Verify hash properties
        assert hashed != password  # Hash should be different from plain
        assert len(hashed) >= 50   # bcrypt hashes are long
        assert hashed.startswith("$2b$")  # bcrypt format

        # Verify password works
        assert verify_password(password, hashed) is True

        # Verify wrong password fails
        assert verify_password("WrongPassword", hashed) is False

    def test_password_hashing_uniqueness(self):
        """Test that same password generates different hashes (salt)."""

        password = "TestPassword123!"

        # Hash same password multiple times
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        hash3 = hash_password(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3

        # But all should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
        assert verify_password(password, hash3) is True

    def test_password_verification_edge_cases(self):
        """Test password verification with edge cases."""

        password = "TestPassword123!"
        hashed = hash_password(password)

        # Test exact match
        assert verify_password(password, hashed) is True

        # Test case sensitivity
        assert verify_password(password.upper(), hashed) is False
        assert verify_password(password.lower(), hashed) is False

        # Test with extra characters
        assert verify_password(password + " ", hashed) is False
        assert verify_password(" " + password, hashed) is False

        # Test with empty/None
        with pytest.raises(Exception):
            verify_password("", hashed)

        with pytest.raises(Exception):
            verify_password(password, "")

    def test_password_special_characters(self):
        """Test hashing passwords with special characters."""

        special_passwords = [
            "Pāssw0rd!",                    # Unicode
            "Test@#$%^&*()_+{}|<>?",       # Special chars
            "🔐🔑Password123",              # Emoji
            "Pass\nword\tTest123!",         # Whitespace chars
            'Pass"word\'Test123!',          # Quotes
        ]

        for password in special_passwords:
            hashed = hash_password(password)
            assert verify_password(password, hashed) is True
            assert verify_password(password + "x", hashed) is False

    def test_password_length_limits(self):
        """Test password hashing with various lengths."""

        # Test minimum length
        short_password = "Aa1!"
        hashed_short = hash_password(short_password)
        assert verify_password(short_password, hashed_short) is True

        # Test long password
        long_password = "A" * 100 + "a1!"
        hashed_long = hash_password(long_password)
        assert verify_password(long_password, hashed_long) is True

        # Test very long password (bcrypt has 72 byte limit)
        very_long_password = "A" * 200 + "a1!"
        hashed_very_long = hash_password(very_long_password)
        assert verify_password(very_long_password, hashed_very_long) is True
```

### Security Testing

**Password Security Test Suite:**

```python
class TestPasswordSecurity:
    """Test suite for password security features."""

    def test_timing_attack_resistance(self):
        """Test that verification time is consistent."""

        import time

        password = "TestPassword123!"
        hashed = hash_password(password)

        # Test multiple verification attempts
        times = []

        for _ in range(10):
            start = time.time()
            verify_password(password, hashed)
            end = time.time()
            times.append(end - start)

        # Test wrong password times
        wrong_times = []

        for _ in range(10):
            start = time.time()
            verify_password("WrongPassword", hashed)
            end = time.time()
            wrong_times.append(end - start)

        # Times should be similar (bcrypt provides timing attack protection)
        avg_correct = sum(times) / len(times)
        avg_wrong = sum(wrong_times) / len(wrong_times)

        # Allow some variance but should be similar
        assert abs(avg_correct - avg_wrong) < avg_correct * 0.5

    def test_hash_format_validation(self):
        """Test that generated hashes have correct format."""

        password = "TestPassword123!"
        hashed = hash_password(password)

        # bcrypt hash format: $2b$rounds$salt+hash
        parts = hashed.split('$')

        assert len(parts) == 4
        assert parts[0] == ""      # Empty string before first $
        assert parts[1] == "2b"    # bcrypt identifier
        assert parts[2].isdigit()  # rounds should be numeric
        assert len(parts[3]) == 53 # salt + hash should be 53 chars

    def test_configuration_security(self):
        """Test that configuration provides adequate security."""

        from src.utils.hashing import _get_pwd_context

        context = _get_pwd_context()

        # Verify bcrypt configuration
        bcrypt_config = context.handler("bcrypt")

        # Should use adequate rounds for security
        assert bcrypt_config.rounds >= 10

        # Should use modern bcrypt version
        assert bcrypt_config.ident == "2b"

    def test_password_never_logged(self, caplog):
        """Test that passwords are never logged."""

        import logging

        password = "SecretPassword123!"

        # Set logging level to capture debug messages
        caplog.set_level(logging.DEBUG)

        # Hash and verify password
        hashed = hash_password(password)
        verify_password(password, hashed)

        # Check that password never appears in logs
        for record in caplog.records:
            assert password not in record.getMessage()
            assert password not in str(record.args)
```

## Best Practices

### Implementation Guidelines

- **Never Log Passwords**: Plain passwords should never be logged or exposed
- **Use Async Wrappers**: Wrap CPU-intensive operations in async functions
- **Validate Before Hashing**: Always validate password strength before hashing
- **Configure Appropriately**: Use appropriate bcrypt rounds for your environment
- **Handle Errors Securely**: Don't expose sensitive information in error messages

### Security Guidelines

- **Enforce Complexity**: Require strong passwords with multiple character types
- **Rate Limiting**: Implement rate limiting for authentication attempts
- **Account Lockout**: Lock accounts after repeated failed attempts
- **Session Management**: Invalidate sessions on password changes
- **Secure Transmission**: Always use HTTPS for password transmission

### Performance Guidelines

- **Environment-Specific Configuration**: Use different bcrypt rounds for different environments
- **Thread Pool Usage**: Use thread pools for password operations in async contexts
- **Batch Operations**: Process multiple password operations efficiently
- **Monitoring**: Monitor password operation performance and adjust configuration

## Related Files

### Dependencies

- `typing.Protocol` - Protocol-based configuration interface
- `passlib.context.CryptContext` - Password hashing context management
- `loguru.logger` - Secure logging without password exposure
- `src.core.config` - Application configuration settings

### Integration Points

- `src.models.user` - User model with password_hash field
- `src.api.v1.auth` - Authentication endpoints using password utilities
- `src.services.auth` - Authentication service layer
- `src.core.security` - Security configuration and token management

### Related Security Modules

- Token management for session security
- Rate limiting for brute force protection
- Input validation for security compliance

## Configuration

### Password Security Settings

```python
# Password hashing configuration
PASSWORD_CONFIG = {
    "bcrypt_rounds": 12,                   # Work factor (production)
    "bcrypt_ident": "2b",                 # Algorithm version
    "min_password_length": 8,             # Minimum length
    "max_password_length": 128,           # Maximum length
    "require_complexity": True,           # Complexity requirements
    "check_common_passwords": True,       # Block common passwords
    "check_personal_info": True,          # Block personal information
}

# Environment-specific settings
ENVIRONMENT_CONFIGS = {
    "development": {"bcrypt_rounds": 10},
    "testing": {"bcrypt_rounds": 4},
    "production": {"bcrypt_rounds": 12},
    "high_security": {"bcrypt_rounds": 15}
}
```

This password hashing utilities module provides industry-standard security for the ReViewPoint application, ensuring robust protection against password-related attacks while maintaining performance and usability.
