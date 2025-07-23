# Security Module

**File:** `backend/src/core/security.py`  
**Purpose:** JWT authentication and token management for ReViewPoint backend  
**Lines of Code:** 239  
**Type:** Core Security Infrastructure Module

## Overview

The security module provides comprehensive JWT (JSON Web Token) authentication services for the ReViewPoint backend. It implements secure token creation, validation, and management with configurable expiration times, robust error handling, and optional authentication bypass for development environments. The module supports both access tokens (short-lived) and refresh tokens (long-lived) with unique token identifiers for blacklisting capabilities.

## Architecture

### Core Design Principles

1. **Configuration-Driven Security**: All JWT settings sourced from configuration
2. **Dual Token System**: Access tokens (30 min) and refresh tokens (7 days)
3. **Unique Token Identification**: JTI (JSON Token Identifier) for token blacklisting
4. **Development Flexibility**: Optional authentication bypass for development
5. **Comprehensive Error Handling**: Detailed error logging with security in mind
6. **Type Safety**: Full type annotations with TypedDict payload structure

### Key Components

#### JWT Payload Structure

```python
class JWTPayload(TypedDict, total=False):
    sub: str              # Subject (user identifier)
    role: str             # User role (admin, user, etc.)
    is_authenticated: bool # Authentication status
    exp: int              # Expiration timestamp
    iat: int              # Issued at timestamp
    jti: str              # JWT ID (unique identifier)
```

**Standard JWT Claims:**

- `sub` (Subject): User identifier or username
- `exp` (Expiration): Unix timestamp when token expires
- `iat` (Issued At): Unix timestamp when token was created
- `jti` (JWT ID): Unique identifier for token blacklisting

**Custom Claims:**

- `role`: User authorization level
- `is_authenticated`: Authentication status flag

## Core Functions

### 🔐 **Access Token Management**

#### `create_access_token()`

```python
def create_access_token(data: Mapping[str, str | int | bool]) -> str:
    """Create a JWT access token with the given data payload."""
```

**Purpose:** Creates short-lived access tokens for API authentication

**Token Creation Process:**

1. **Payload Preparation**: Merge user data with standard JWT claims
2. **Expiration Setting**: Use configured expiration time (default: 30 minutes)
3. **Timestamp Addition**: Add `iat` (issued at) and `exp` (expiration) claims
4. **Unique ID**: Generate `jti` using UUID4 for token blacklisting
5. **Encoding**: Sign token with configured secret and algorithm
6. **Logging**: Log creation with sanitized claims (no sensitive data)

**Configuration Integration:**

```python
settings = get_settings()
expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
```

**Security Features:**

- Configurable expiration time
- Unique token identification (JTI)
- Secure logging (excludes sensitive claims)
- Comprehensive error handling

#### `verify_access_token()` & `decode_access_token()`

```python
def verify_access_token(token: str) -> JWTPayload:
    """Validate a JWT access token and return the decoded payload."""

def decode_access_token(token: str) -> JWTPayload:
    """Alias for verify_access_token for backward compatibility."""
```

**Purpose:** Validates and decodes access tokens for request authentication

**Validation Process:**

1. **Authentication Check**: Bypass validation if auth is disabled (development mode)
2. **Format Validation**: Verify token has 3 parts separated by dots
3. **Secret Verification**: Ensure JWT secret is configured
4. **Token Decoding**: Decode using configured secret and algorithm
5. **Type Validation**: Ensure payload is a dictionary
6. **Payload Return**: Return typed payload for application use

**Development Mode Behavior:**

```python
if not settings.auth_enabled:
    return JWTPayload(
        sub="dev-user",
        role="admin",
        is_authenticated=True,
        exp=int((now + timedelta(hours=24)).timestamp()),
    )
```

**Security Validation:**

- Token format validation (3-part JWT structure)
- Secret key presence verification
- Algorithm verification
- Payload type checking
- Comprehensive error logging

### 🔄 **Refresh Token Management**

#### `create_refresh_token()`

```python
def create_refresh_token(data: Mapping[str, str | int | bool]) -> str:
    """Create a JWT refresh token with the given data payload."""
```

**Purpose:** Creates long-lived refresh tokens for session management

**Token Characteristics:**

- **Expiration**: 7 days (extended lifetime)
- **Purpose**: Renew access tokens without re-authentication
- **Security**: Same secret and algorithm as access tokens
- **Identification**: Unique JTI for blacklisting

**Usage Pattern:**

```python
refresh_token = create_refresh_token({
    "sub": user.username,
    "role": user.role,
    "is_authenticated": True
})
```

#### `verify_refresh_token()`

```python
def verify_refresh_token(token: str) -> JWTPayload:
    """Validate a JWT refresh token and return the decoded payload."""
```

**Purpose:** Validates refresh tokens for access token renewal

**Enhanced Validation:**

1. **Standard JWT Validation**: Signature and expiration verification
2. **Required Claims Check**: Ensures `sub`, `jti`, and `exp` are present
3. **Expiration Verification**: Explicitly checks if token is expired
4. **Type Safety**: Returns typed payload structure

**Required Claims Validation:**

```python
if not ("sub" in payload and "jti" in payload and "exp" in payload):
    raise ValueError("Refresh token missing required claims (sub, jti, exp)")

if exp_val < int(datetime.now(UTC).timestamp()):
    raise ValueError("Refresh token is expired")
```

## Configuration Integration

### JWT Settings from Config Module

```python
from src.core.config import get_settings

settings = get_settings()
# JWT configuration values:
# - settings.jwt_secret_key: Secret for signing tokens
# - settings.jwt_algorithm: Signing algorithm (default: HS256)
# - settings.jwt_expire_minutes: Access token lifetime (default: 30)
# - settings.auth_enabled: Enable/disable authentication
```

**Configuration Dependencies:**

- `jwt_secret_key`: Required in production, validated at runtime
- `jwt_algorithm`: Cryptographic algorithm (HS256, HS512, RS256, etc.)
- `jwt_expire_minutes`: Access token expiration time
- `auth_enabled`: Development authentication bypass flag

### Environment Variables

| Variable                         | Purpose               | Default | Required   |
| -------------------------------- | --------------------- | ------- | ---------- |
| `REVIEWPOINT_JWT_SECRET_KEY`     | Token signing secret  | None    | Yes (prod) |
| `REVIEWPOINT_JWT_ALGORITHM`      | Signing algorithm     | HS256   | No         |
| `REVIEWPOINT_JWT_EXPIRE_MINUTES` | Access token lifetime | 30      | No         |
| `REVIEWPOINT_AUTH_ENABLED`       | Enable authentication | true    | No         |

## Usage Patterns

### FastAPI Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from src.core.security import verify_access_token, JWTPayload

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> JWTPayload:
    """FastAPI dependency for extracting authenticated user from JWT."""
    try:
        payload = verify_access_token(token.credentials)
        return payload
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

@app.get("/protected")
async def protected_endpoint(
    current_user: JWTPayload = Depends(get_current_user)
):
    return {"user": current_user["sub"], "role": current_user["role"]}
```

### Login and Token Creation

```python
from src.core.security import create_access_token, create_refresh_token

async def login_user(username: str, password: str):
    # Authenticate user (password verification, etc.)
    user = await authenticate_user(username, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    token_data = {
        "sub": user.username,
        "role": user.role,
        "is_authenticated": True
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutes in seconds
    }
```

### Token Refresh Pattern

```python
from src.core.security import verify_refresh_token, create_access_token

async def refresh_access_token(refresh_token: str):
    try:
        # Validate refresh token
        payload = verify_refresh_token(refresh_token)

        # Create new access token with same claims
        new_token_data = {
            "sub": payload["sub"],
            "role": payload["role"],
            "is_authenticated": payload["is_authenticated"]
        }

        new_access_token = create_access_token(new_token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60
        }

    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) from e
```

### Role-Based Authorization

```python
from functools import wraps
from src.core.security import JWTPayload

def require_role(required_role: str):
    """Decorator for role-based authorization."""
    def decorator(func):
        @wraps(func)
        async def wrapper(current_user: JWTPayload = Depends(get_current_user), *args, **kwargs):
            if current_user.get("role") != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role: {required_role}"
                )
            return await func(current_user, *args, **kwargs)
        return wrapper
    return decorator

@app.delete("/admin/users/{user_id}")
@require_role("admin")
async def delete_user(user_id: int, current_user: JWTPayload):
    # Only admin users can access this endpoint
    return await user_service.delete_user(user_id)
```

### Development Authentication Bypass

```python
# In development with REVIEWPOINT_AUTH_ENABLED=false
settings = get_settings()

if not settings.auth_enabled:
    # All token verification returns admin user
    payload = verify_access_token("any-token")
    # Returns: {"sub": "dev-user", "role": "admin", "is_authenticated": True}
```

## Error Handling and Security

### 🛡️ **Error Categories**

#### Configuration Errors

```python
# Missing JWT secret
if not settings.jwt_secret_key:
    raise ValueError("JWT secret key is not configured.")
```

#### Token Format Errors

```python
# Malformed token structure
if not token or token.count(".") != 2:
    raise JWTError("Invalid token format")
```

#### Validation Errors

```python
# Invalid signature or expired token
try:
    payload = jwt.decode(token, secret, algorithms=[algorithm])
except JWTError as e:
    logger.warning("JWT validation failed: {}", str(e))
    raise
```

#### Payload Errors

```python
# Invalid payload structure
if not isinstance(payload, dict):
    raise TypeError("Decoded JWT payload is not a dictionary")

# Missing required claims
if not ("sub" in payload and "jti" in payload):
    raise ValueError("Token missing required claims")
```

### 🔒 **Security Features**

#### Token Uniqueness (JTI)

```python
# Every token gets a unique identifier
to_encode["jti"] = str(uuid.uuid4())

# Enables token blacklisting:
# 1. Store revoked JTIs in database/cache
# 2. Check JTI against blacklist during validation
# 3. Reject tokens with blacklisted JTIs
```

#### Secure Logging

```python
# Log creation without exposing sensitive data
logger.debug(
    "JWT token created (claims: {})",
    {k: v for k, v in to_encode.items() if k != "exp"}  # Exclude expiration
)

# Never log actual tokens or secrets
# Log validation failures for security monitoring
```

#### Algorithm Protection

```python
# Specify exact algorithm to prevent algorithm confusion attacks
payload = jwt.decode(
    token,
    settings.jwt_secret_key,
    algorithms=[settings.jwt_algorithm]  # Explicit algorithm
)
```

#### Time-Based Security

```python
# Access tokens: Short-lived (30 minutes)
expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)

# Refresh tokens: Longer-lived but manageable (7 days)
expire = datetime.now(UTC) + timedelta(days=7)

# Explicit expiration checking
if exp_val < int(datetime.now(UTC).timestamp()):
    raise ValueError("Token is expired")
```

## Testing and Development

### Development Mode Features

```python
# Authentication bypass for development
if not settings.auth_enabled:
    logger.warning("Authentication is DISABLED! Bypassing token verification")
    return JWTPayload(
        sub="dev-user",
        role="admin",
        is_authenticated=True,
        exp=int((now + timedelta(hours=24)).timestamp()),
    )
```

**Development Benefits:**

- No need for valid JWT secrets during development
- Automatic admin permissions for testing
- Extended token lifetime (24 hours)
- Clear warning logs when auth is bypassed

### Test Utilities

```python
# Test token creation
def create_test_token(user_data: dict) -> str:
    """Create test token with custom data."""
    return create_access_token({
        "sub": user_data.get("username", "test-user"),
        "role": user_data.get("role", "user"),
        "is_authenticated": True
    })

# Test token validation
def test_token_validation():
    token = create_test_token({"username": "alice", "role": "admin"})
    payload = verify_access_token(token)

    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"
    assert payload["is_authenticated"] is True
    assert "jti" in payload
```

### Mock Authentication

```python
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_auth_disabled():
    """Mock authentication disabled for testing."""
    with patch("src.core.config.get_settings") as mock_settings:
        mock_settings.return_value.auth_enabled = False
        yield mock_settings

def test_auth_bypass(mock_auth_disabled):
    """Test authentication bypass in development mode."""
    payload = verify_access_token("invalid-token")
    assert payload["sub"] == "dev-user"
    assert payload["role"] == "admin"
```

## Performance Considerations

### ⚡ **Token Efficiency**

```python
# Lightweight payload structure
token_data = {
    "sub": user.id,        # Minimal user identifier
    "role": user.role,     # Essential authorization info
    "is_authenticated": True  # Simple boolean flag
}

# Avoid large payloads:
# ❌ Don't include: user profiles, permissions lists, session data
# ✅ Do include: user ID, role, essential flags
```

### 🔄 **Token Lifecycle Management**

```python
# Access tokens: Frequent creation, short lifetime
# - Created on every login/refresh
# - 30-minute expiration reduces security window
# - Minimal performance impact due to short lifetime

# Refresh tokens: Infrequent creation, long lifetime
# - Created only on login
# - 7-day expiration reduces refresh frequency
# - Enables long-term sessions without constant re-authentication
```

### 🎯 **Caching Considerations**

```python
# JWT verification is stateless (no database lookups required)
# Consider caching for high-frequency validation:

from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_token_validation(token_hash: str) -> JWTPayload:
    """Cache recent token validations."""
    # Note: Be careful with caching tokens directly
    # Consider caching validation results with short TTL
    pass
```

## Best Practices

### ✅ **Do's**

- **Use Strong Secrets**: Generate cryptographically secure JWT secrets (256+ bits)
- **Validate Configuration**: Ensure JWT secret is configured in production
- **Handle Errors Gracefully**: Catch and log JWT errors appropriately
- **Use Short Access Tokens**: Keep access token lifetime minimal (15-60 minutes)
- **Implement Token Refresh**: Use refresh tokens for long-term sessions
- **Log Security Events**: Log authentication failures and suspicious activity
- **Validate Token Format**: Check basic JWT structure before decoding

### ❌ **Don'ts**

- **Log Sensitive Data**: Never log actual tokens, secrets, or sensitive claims
- **Use Weak Secrets**: Don't use predictable or short JWT secrets
- **Skip Validation**: Don't bypass token validation in production
- **Store Secrets in Code**: Don't hardcode JWT secrets in source code
- **Use Long Access Tokens**: Don't create access tokens with long lifetimes
- **Ignore Expiration**: Don't accept expired tokens
- **Trust Client Data**: Don't trust JWT payloads without proper validation

## Security Recommendations

### 🔐 **Production Security**

```python
# Strong JWT secret (256-bit minimum)
REVIEWPOINT_JWT_SECRET_KEY="your-cryptographically-secure-secret-here"

# Secure algorithm (avoid 'none' algorithm)
REVIEWPOINT_JWT_ALGORITHM="HS256"  # or RS256 for asymmetric

# Reasonable token lifetime
REVIEWPOINT_JWT_EXPIRE_MINUTES=30

# Enable authentication in production
REVIEWPOINT_AUTH_ENABLED=true
```

### 🛡️ **Token Security**

```python
# Implement token blacklisting
revoked_tokens = set()  # In production: use Redis/database

def is_token_revoked(jti: str) -> bool:
    return jti in revoked_tokens

def revoke_token(jti: str):
    revoked_tokens.add(jti)
    # In production: persist to database/cache

# Validate against blacklist
payload = verify_access_token(token)
if is_token_revoked(payload["jti"]):
    raise JWTError("Token has been revoked")
```

### 🔄 **Rotation Strategy**

```python
# Regular secret rotation
# 1. Generate new secret
# 2. Update configuration
# 3. Invalidate old tokens (force re-login)
# 4. Monitor for issues

# Graceful token migration
# 1. Support multiple secrets temporarily
# 2. Issue tokens with new secret
# 3. Accept tokens with old secret (limited time)
# 4. Retire old secret after migration period
```

## Error Reference

### Common Error Scenarios

#### `ValueError: JWT secret key is not configured`

- **Cause**: Missing `REVIEWPOINT_JWT_SECRET_KEY` environment variable
- **Solution**: Set proper JWT secret in environment configuration

#### `JWTError: Invalid token format`

- **Cause**: Malformed JWT token (not 3 parts separated by dots)
- **Solution**: Verify token source and transmission

#### `JWTError: Signature verification failed`

- **Cause**: Token signed with different secret or tampered with
- **Solution**: Verify JWT secret consistency and token integrity

#### `ValueError: Token missing required claims`

- **Cause**: JWT payload missing essential claims (sub, jti, exp)
- **Solution**: Ensure token creation includes all required claims

## Related Files

- **`config.py`** - JWT configuration settings and environment variables
- **`api/auth.py`** - Authentication endpoints using these JWT functions
- **`api/deps.py`** - FastAPI dependencies for JWT validation
- **`models/user.py`** - User models that tokens represent
- **`middleware/`** - Request middleware for JWT authentication

## Dependencies

- **`jose`** - Python JWT library for token operations
- **`loguru`** - Logging system for security monitoring
- **`uuid`** - Unique identifier generation for JTI claims
- **`datetime`** - Timestamp handling for token expiration

---

_This module provides the core security infrastructure for JWT-based authentication in the ReViewPoint backend, offering robust token management with comprehensive error handling and configurable security features._
