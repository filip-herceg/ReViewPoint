# utils/hashing.py - Password Hashing and Verification Utilities

## Purpose

The `utils/hashing.py` module provides secure password hashing and verification utilities using the industry-standard bcrypt algorithm. It implements configurable bcrypt settings with proper security practices and type safety for the ReViewPoint platform.

## Key Components

### Core Imports and Dependencies

#### Essential Cryptographic Libraries

```python
from typing import Final, Literal, Protocol

from loguru import logger
from passlib.context import CryptContext

from src.core.config import get_settings
```

### Type Safety and Configuration

#### Settings Protocol for Type Safety

```python
class SettingsProtocol(Protocol):
    BCRYPT_ROUNDS: int
    BCRYPT_IDENT: str
```

**Features:**

- Protocol-based typing for configuration settings
- Ensures required bcrypt configuration attributes
- Compile-time type checking for settings access
- Runtime validation of configuration conformance

#### Bcrypt Configuration Constants

```python
SCHEME_BCRYPT: Final = "bcrypt"
SCHEMES: Final[tuple[Literal["bcrypt"], ...]] = (SCHEME_BCRYPT,)
DEPRECATED_POLICY: Final = "auto"
```

**Configuration Parameters:**

- **SCHEME_BCRYPT**: Primary hashing scheme identifier
- **SCHEMES**: Tuple of supported hashing schemes
- **DEPRECATED_POLICY**: Automatic deprecation handling policy

### Password Context Management

#### Dynamic Context Configuration

```python
def _get_pwd_context() -> CryptContext:
    """
    Get password context with current settings.

    Returns:
        CryptContext: The password hashing context.

    Raises:
        AttributeError: If settings do not have required attributes.
    """
    settings: SettingsProtocol = get_settings()  # type: ignore[assignment]
    schemes: tuple[Literal["bcrypt"], ...] = SCHEMES
    deprecated: Literal["auto"] = DEPRECATED_POLICY
    bcrypt_rounds: int = getattr(settings, "BCRYPT_ROUNDS", 12)
    bcrypt_ident: str = getattr(settings, "BCRYPT_IDENT", "2b")
    return CryptContext(
        schemes=schemes,
        deprecated=deprecated,
        bcrypt__rounds=bcrypt_rounds,  # Configurable rounds
        bcrypt__ident=bcrypt_ident,  # Configurable identifier
    )
```

**Key Features:**

- Dynamic configuration from application settings
- Configurable bcrypt rounds for security vs. performance tuning
- Configurable bcrypt identifier (2a, 2b, 2x, 2y variants)
- Default fallback values (12 rounds, 2b identifier)
- Type-safe configuration access with runtime validation

**Security Considerations:**

- Bcrypt rounds default to 12 (industry recommended minimum)
- 2b identifier for maximum compatibility and security
- Automatic deprecation handling for future algorithm updates
- Settings-driven configuration for environment-specific tuning

### Password Hashing

#### Secure Password Hash Generation

```python
def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        password (str): The plain password to hash.

    Returns:
        str: The bcrypt hash of the password.

    Raises:
        ValueError: If password is not hashable.
    """
    # Never log or expose the plain password
    logger.debug("Hashing password (input not logged)")
    pwd_context: CryptContext = _get_pwd_context()
    hash_result: str = pwd_context.hash(password)
    return hash_result
```

**Security Features:**

- Industry-standard bcrypt hashing algorithm
- Configurable work factor (rounds) for future-proofing
- Automatic salt generation for each password
- Secure logging practices (no plaintext password exposure)
- Type-safe string input/output handling

**Usage Examples:**

```python
# Basic password hashing
plain_password = "user_password_123"
hashed = hash_password(plain_password)
# Returns: "$2b$12$randomsaltandhashedpassword..."

# Hash is different each time due to unique salts
hash1 = hash_password("password")
hash2 = hash_password("password")
assert hash1 != hash2  # Different salts, different hashes

# Configuration-driven rounds
# Settings: BCRYPT_ROUNDS=14 for high-security applications
# Settings: BCRYPT_ROUNDS=10 for performance-critical applications
```

### Password Verification

#### Secure Password Verification

```python
def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against a given bcrypt hash.

    Args:
        plain (str): The plain password to verify.
        hashed (str): The bcrypt hash to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.

    Raises:
        ValueError: If verification fails due to invalid hash or input.
    """
    # Never log or expose the plain password
    logger.debug("Verifying password (input not logged)")
    pwd_context: CryptContext = _get_pwd_context()
    result: bool = pwd_context.verify(plain, hashed)
    return result
```

**Security Features:**

- Constant-time verification to prevent timing attacks
- Secure handling of verification failures
- No plaintext password logging or exposure
- Automatic handling of different bcrypt variants
- Type-safe boolean return for clear success/failure indication

**Usage Examples:**

```python
# User login verification
stored_hash = "$2b$12$stored_hash_from_database..."
user_input = "user_entered_password"

if verify_password(user_input, stored_hash):
    print("Login successful")
else:
    print("Invalid credentials")

# Password change verification
old_password = "current_password"
stored_hash = user.password_hash

if verify_password(old_password, stored_hash):
    new_hash = hash_password("new_password")
    user.password_hash = new_hash
else:
    raise ValueError("Current password incorrect")
```

## Integration Patterns

### User Registration Flow

#### Secure User Creation

```python
from src.utils.hashing import hash_password
from src.utils.validation import validate_password, get_password_validation_error

async def create_user(email: str, password: str, name: str | None = None) -> User:
    """Create a new user with secure password hashing."""

    # Validate password strength
    password_error = get_password_validation_error(password)
    if password_error:
        raise ValidationError(password_error)

    # Hash the password securely
    password_hash = hash_password(password)

    # Create user with hashed password
    user = User(
        email=email,
        password_hash=password_hash,
        name=name,
        created_at=datetime.utcnow()
    )

    db.add(user)
    await db.commit()
    return user
```

### Authentication Service Integration

#### Login Verification

```python
from src.utils.hashing import verify_password
from src.utils.errors import AuthenticationError

async def authenticate_user(email: str, password: str) -> User:
    """Authenticate user with email and password."""

    # Find user by email
    user = await user_repository.get_by_email(email)
    if not user:
        raise AuthenticationError("Invalid credentials")

    # Verify password
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid credentials")

    # Update last login time
    user.last_login = datetime.utcnow()
    await user_repository.update(user)

    return user
```

### Password Change Service

#### Secure Password Updates

```python
from src.utils.hashing import hash_password, verify_password

async def change_password(
    user_id: int,
    current_password: str,
    new_password: str
) -> None:
    """Change user password with current password verification."""

    # Get user
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise UserNotFoundError("User not found")

    # Verify current password
    if not verify_password(current_password, user.password_hash):
        raise AuthenticationError("Current password incorrect")

    # Validate new password
    password_error = get_password_validation_error(new_password)
    if password_error:
        raise ValidationError(password_error)

    # Hash new password
    new_password_hash = hash_password(new_password)

    # Update user
    user.password_hash = new_password_hash
    user.password_changed_at = datetime.utcnow()
    await user_repository.update(user)
```

### API Endpoint Integration

#### FastAPI Authentication Endpoints

```python
from fastapi import APIRouter, HTTPException, Depends
from src.utils.hashing import verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login")
async def login(credentials: LoginRequest) -> TokenResponse:
    """User login endpoint."""
    try:
        user = await authenticate_user(
            credentials.email,
            credentials.password
        )

        # Generate access token
        access_token = create_access_token(user.id)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id
        )

    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

@router.post("/change-password")
async def change_password_endpoint(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Change user password endpoint."""
    try:
        await change_password(
            current_user.id,
            request.current_password,
            request.new_password
        )

        return {"message": "Password changed successfully"}

    except (AuthenticationError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e))
```

## Security Considerations

### Bcrypt Configuration

#### Work Factor (Rounds) Selection

```python
# Configuration recommendations by environment
DEVELOPMENT_ROUNDS = 10    # Fast iteration, lower security
STAGING_ROUNDS = 12        # Balanced for testing
PRODUCTION_ROUNDS = 14     # High security, acceptable performance
HIGH_SECURITY_ROUNDS = 16  # Maximum security applications
```

**Work Factor Guidelines:**

- **Rounds 10**: Development environments, ~100ms
- **Rounds 12**: Production standard, ~300ms
- **Rounds 14**: High-security applications, ~1.2s
- **Rounds 16**: Maximum security, ~5s

### Salt Management

#### Automatic Salt Generation

```python
# Bcrypt automatically generates unique salts
password1 = hash_password("password")
password2 = hash_password("password")

# Each hash contains a unique salt
assert password1 != password2
assert password1.startswith("$2b$12$")
assert password2.startswith("$2b$12$")

# Salt is embedded in the hash
salt1 = password1[7:29]  # Extract salt portion
salt2 = password2[7:29]  # Extract salt portion
assert salt1 != salt2
```

### Timing Attack Prevention

#### Constant-Time Operations

```python
import asyncio
from src.utils.hashing import verify_password

async def secure_login_attempt(email: str, password: str) -> User | None:
    """Login with timing attack protection."""

    # Always retrieve user (even if email doesn't exist)
    user = await user_repository.get_by_email(email)

    if user:
        # Verify actual password hash
        is_valid = verify_password(password, user.password_hash)
    else:
        # Perform dummy verification to maintain constant timing
        dummy_hash = "$2b$12$dummy.hash.to.maintain.constant.timing"
        verify_password(password, dummy_hash)
        is_valid = False

    return user if is_valid else None
```

### Password Policy Enforcement

#### Integration with Validation

```python
from src.utils.validation import validate_password, get_password_validation_error
from src.utils.hashing import hash_password

class PasswordPolicy:
    """Centralized password policy enforcement."""

    def __init__(self, min_length: int = 12, require_special: bool = True):
        self.min_length = min_length
        self.require_special = require_special

    def validate(self, password: str) -> str | None:
        """Validate password against policy."""
        # Basic validation
        error = get_password_validation_error(password, self.min_length)
        if error:
            return error

        # Additional policy checks
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return "Password must contain at least one special character."

        return None

    def hash_if_valid(self, password: str) -> str:
        """Validate and hash password."""
        error = self.validate(password)
        if error:
            raise ValidationError(error)

        return hash_password(password)

# Usage
policy = PasswordPolicy(min_length=12, require_special=True)
hashed = policy.hash_if_valid("MySecureP@ssw0rd123")
```

## Best Practices

### Configuration Management

```python
# Environment-specific configuration
class SecuritySettings:
    # Development
    DEV_BCRYPT_ROUNDS = 10
    DEV_BCRYPT_IDENT = "2b"

    # Production
    PROD_BCRYPT_ROUNDS = 14
    PROD_BCRYPT_IDENT = "2b"

    # High-security applications
    HIGH_SEC_BCRYPT_ROUNDS = 16
    HIGH_SEC_BCRYPT_IDENT = "2b"
```

### Error Handling

```python
from src.utils.hashing import hash_password, verify_password
import logging

def safe_hash_password(password: str) -> str:
    """Hash password with comprehensive error handling."""
    try:
        if not password or len(password.strip()) == 0:
            raise ValueError("Password cannot be empty")

        return hash_password(password)

    except Exception as e:
        logging.error(f"Password hashing failed: {type(e).__name__}")
        raise ValueError("Password hashing failed") from e

def safe_verify_password(plain: str, hashed: str) -> bool:
    """Verify password with comprehensive error handling."""
    try:
        if not plain or not hashed:
            return False

        return verify_password(plain, hashed)

    except Exception as e:
        logging.error(f"Password verification failed: {type(e).__name__}")
        return False
```

### Testing Utilities

```python
import pytest
from src.utils.hashing import hash_password, verify_password

class TestPasswordHashing:
    """Comprehensive password hashing tests."""

    def test_password_hashing_basic(self):
        """Test basic password hashing functionality."""
        password = "test_password_123"
        hashed = hash_password(password)

        # Verify hash format
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60  # Standard bcrypt hash length

        # Verify password verification
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_unique_salts(self):
        """Test that each hash generates unique salts."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different due to unique salts
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_empty_password_handling(self):
        """Test handling of edge cases."""
        with pytest.raises(ValueError):
            hash_password("")

        assert verify_password("", "any_hash") is False
        assert verify_password("password", "") is False

    @pytest.mark.parametrize("password", [
        "simple",
        "Complex123!",
        "very_long_password_with_many_characters_123",
        "密码123",  # Unicode characters
    ])
    def test_password_variety(self, password):
        """Test hashing various password types."""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password(password + "wrong", hashed) is False
```

This hashing system provides industry-standard password security with configurable performance tuning, comprehensive error handling, and secure integration patterns for the ReViewPoint platform.
