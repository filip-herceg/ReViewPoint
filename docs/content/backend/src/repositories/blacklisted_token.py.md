# Blacklisted Token Repository Module

## Overview

The `blacklisted_token.py` repository module provides data access layer functionality for JWT token blacklisting in the ReViewPoint application. This module implements essential security operations for token invalidation, including blacklisting tokens during logout and checking token validity to prevent reuse of revoked authentication tokens.

**Key Features:**

- JWT token blacklisting for security and logout functionality
- Automatic expiration handling for storage efficiency
- Timezone-aware datetime operations for global compatibility
- Transaction-safe operations with caller-controlled commits
- Performance-optimized token validation checks

## Module Structure

```python
from datetime import UTC, datetime
from typing import Final
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.blacklisted_token import BlacklistedToken
```

### Core Dependencies

#### Internal Models

- `src.models.blacklisted_token.BlacklistedToken` - Blacklisted token ORM model

#### External Dependencies

- SQLAlchemy for async database operations
- Python datetime with UTC timezone support
- Final typing for immutable constants

## Core Operations

### 1. Token Blacklisting Operations

#### blacklist_token Function

```python
async def blacklist_token(
    session: AsyncSession, jti: str, expires_at: datetime
) -> None:
    """
    Blacklist a token by storing its JTI and expiration.

    Args:
        session (AsyncSession): The SQLAlchemy async session.
        jti (str): The JWT ID to blacklist.
        expires_at (datetime): The expiration datetime of the token.
    """
    token: Final[BlacklistedToken] = BlacklistedToken(jti=jti, expires_at=expires_at)
    session.add(token)
    # Do not commit here; let the caller control the transaction boundary.
```

**Purpose:** Adds JWT tokens to the blacklist to prevent their reuse after logout or revocation.

**Key Features:**

- **Token Identification:** Uses JWT ID (JTI) for unique token identification
- **Expiration Tracking:** Stores token expiration for automatic cleanup
- **Transaction Control:** Defers commit to caller for flexible transaction management
- **Immutable Creation:** Uses Final typing for created token objects
- **Security Integration:** Enables logout and token revocation functionality

**Usage Patterns:**

```python
# During user logout
async def logout_user(session: AsyncSession, jwt_token: str):
    jti = extract_jti_from_token(jwt_token)
    expires_at = extract_expiration_from_token(jwt_token)

    await blacklist_token(session, jti, expires_at)
    await session.commit()  # Caller controls transaction

    return {"message": "Logged out successfully"}

# During token revocation
async def revoke_token(session: AsyncSession, token_data: dict):
    await blacklist_token(
        session,
        token_data["jti"],
        datetime.fromtimestamp(token_data["exp"], UTC)
    )
    await session.commit()
```

**Security Model:**

```python
# JWT structure includes JTI for tracking
{
    "sub": "user_id",
    "jti": "unique_token_identifier",  # Used for blacklisting
    "exp": 1640995200,                # Used for expiration
    "iat": 1640908800
}
```

### 2. Token Validation Operations

#### is_token_blacklisted Function

```python
async def is_token_blacklisted(session: AsyncSession, jti: str) -> bool:
    """
    Check if a token is blacklisted and not yet expired.

    Args:
        session (AsyncSession): The SQLAlchemy async session.
        jti (str): The JWT ID to check.

    Returns:
        bool: True if the token is blacklisted and not expired, False otherwise.
    """
    result: Final = await session.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    token: BlacklistedToken | None = result.scalar_one_or_none()
    now: Final[datetime] = datetime.now(UTC)

    if token is not None:
        expires_at: datetime = token.expires_at
        # If naive, treat as UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at > now:
            return True
    return False
```

**Purpose:** Validates whether a JWT token is blacklisted and still within its expiration period.

**Key Features:**

- **Existence Check:** Queries database for blacklisted token by JTI
- **Expiration Validation:** Only considers non-expired tokens as blacklisted
- **Timezone Handling:** Properly handles both naive and timezone-aware datetimes
- **UTC Normalization:** Treats naive datetimes as UTC for consistency
- **Performance Optimization:** Single database query for validation

**Validation Logic:**

```python
# Token validation workflow
1. Query blacklisted_tokens table for JTI
2. If not found → return False (token not blacklisted)
3. If found → check expiration
4. If expired → return False (token expired, effectively not blacklisted)
5. If not expired → return True (token actively blacklisted)
```

**Timezone Handling:**

```python
# Handle both naive and timezone-aware datetimes
expires_at = token.expires_at
if expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=UTC)  # Assume UTC

# Compare with current UTC time
now = datetime.now(UTC)
is_still_valid = expires_at > now
```

**Usage in Authentication Middleware:**

```python
async def validate_jwt_token(session: AsyncSession, token: str) -> bool:
    try:
        # Decode token to get JTI
        payload = decode_jwt_token(token)
        jti = payload.get("jti")

        if not jti:
            return False  # No JTI means invalid token

        # Check if token is blacklisted
        if await is_token_blacklisted(session, jti):
            return False  # Token is blacklisted

        # Check other validations (expiration, signature, etc.)
        return validate_token_claims(payload)

    except JWTError:
        return False
```

## Advanced Features

### Automatic Expiration Handling

```python
# Expired tokens are automatically considered not blacklisted
if token is not None:
    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    # Only return True if token exists AND is not expired
    if expires_at > now:
        return True
return False
```

**Purpose:** Provides automatic cleanup logic by ignoring expired blacklisted tokens.

**Benefits:**

- **Storage Efficiency:** Expired entries don't affect validation
- **Performance:** Reduces effective blacklist size over time
- **Maintenance:** No need for explicit cleanup of expired entries
- **Accuracy:** Aligns with JWT token expiration semantics

### Timezone Compatibility

```python
# Robust timezone handling
now: Final[datetime] = datetime.now(UTC)

# Normalize stored datetime to UTC
if expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=UTC)
```

**Purpose:** Ensures consistent datetime comparisons across different timezone configurations.

**Features:**

- **UTC Standardization:** All comparisons done in UTC
- **Naive DateTime Handling:** Assumes naive datetimes are UTC
- **Global Compatibility:** Works with different server timezone configurations
- **Consistent Behavior:** Predictable expiration checking regardless of environment

## Security Considerations

### Token Identification

```python
# JTI provides unique token identification
token = BlacklistedToken(jti=jti, expires_at=expires_at)
```

### Secure Validation

```python
# Comprehensive validation includes expiration
if token is not None and expires_at > now:
    return True  # Only consider valid, non-expired blacklisted tokens
```

**Purpose:** Implements secure token management preventing replay attacks and unauthorized access.

**Security Features:**

- **Unique Identification:** JTI ensures specific token targeting
- **Expiration Respect:** Honors JWT expiration semantics
- **Replay Prevention:** Prevents reuse of blacklisted tokens
- **Granular Control:** Individual token revocation capability

## Performance Optimization

### Efficient Queries

```python
# Single query for token lookup
result = await session.execute(
    select(BlacklistedToken).where(BlacklistedToken.jti == jti)
)
token = result.scalar_one_or_none()
```

### Minimal Data Storage

```python
# Only store essential data
BlacklistedToken(jti=jti, expires_at=expires_at)  # Minimal fields
```

**Purpose:** Optimizes performance through efficient database operations and minimal storage.

**Optimization Strategies:**

- **Single Query Validation:** One database operation per check
- **Minimal Schema:** Only necessary fields stored
- **Index Optimization:** JTI field should be indexed for fast lookups
- **Automatic Expiration:** Self-cleaning through expiration logic

## Error Handling Patterns

### Database Operations

```python
# Let caller handle transaction boundaries
session.add(token)
# No commit here - caller controls transaction
```

### Validation Errors

```python
# Safe handling of missing or invalid tokens
token = result.scalar_one_or_none()
if token is not None:
    # Process valid token
    return check_expiration(token)
return False  # Safe default for missing tokens
```

**Purpose:** Provides robust error handling with safe defaults and proper transaction management.

**Error Handling Features:**

- **Safe Defaults:** Returns False for missing or invalid tokens
- **Transaction Safety:** Caller controls commit/rollback
- **Null Safety:** Proper handling of None results
- **Exception Prevention:** Avoids errors from missing data

## Testing Patterns

### Unit Testing Example

```python
import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from src.repositories.blacklisted_token import blacklist_token, is_token_blacklisted

@pytest.mark.asyncio
async def test_blacklist_token():
    mock_session = AsyncMock()

    jti = "test_token_123"
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    await blacklist_token(mock_session, jti, expires_at)

    # Verify token was added to session
    mock_session.add.assert_called_once()
    added_token = mock_session.add.call_args[0][0]
    assert added_token.jti == jti
    assert added_token.expires_at == expires_at

@pytest.mark.asyncio
async def test_is_token_blacklisted_expired():
    mock_session = AsyncMock()

    # Mock expired token
    expired_token = BlacklistedToken(
        jti="expired_token",
        expires_at=datetime.now(UTC) - timedelta(hours=1)  # Expired
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = expired_token

    result = await is_token_blacklisted(mock_session, "expired_token")
    assert result is False  # Expired tokens not considered blacklisted

@pytest.mark.asyncio
async def test_is_token_blacklisted_valid():
    mock_session = AsyncMock()

    # Mock valid blacklisted token
    valid_token = BlacklistedToken(
        jti="valid_token",
        expires_at=datetime.now(UTC) + timedelta(hours=1)  # Not expired
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = valid_token

    result = await is_token_blacklisted(mock_session, "valid_token")
    assert result is True  # Valid blacklisted token
```

### Integration Testing Example

```python
@pytest.mark.asyncio
async def test_token_blacklist_lifecycle():
    async with test_session() as session:
        jti = "integration_test_token"
        expires_at = datetime.now(UTC) + timedelta(hours=1)

        # Initially not blacklisted
        is_blacklisted = await is_token_blacklisted(session, jti)
        assert is_blacklisted is False

        # Blacklist the token
        await blacklist_token(session, jti, expires_at)
        await session.commit()

        # Now should be blacklisted
        is_blacklisted = await is_token_blacklisted(session, jti)
        assert is_blacklisted is True

        # Test with expired token
        expired_jti = "expired_test_token"
        expired_time = datetime.now(UTC) - timedelta(hours=1)

        await blacklist_token(session, expired_jti, expired_time)
        await session.commit()

        # Expired token should not be considered blacklisted
        is_blacklisted = await is_token_blacklisted(session, expired_jti)
        assert is_blacklisted is False
```

## Migration and Upgrade Paths

### From Synchronous Operations

```python
# Old synchronous pattern
def old_blacklist_token(session, jti, expires_at):
    token = BlacklistedToken(jti=jti, expires_at=expires_at)
    session.add(token)
    # session.commit()  # Immediate commit

# New async pattern
async def new_blacklist_token(session: AsyncSession, jti: str, expires_at: datetime):
    token = BlacklistedToken(jti=jti, expires_at=expires_at)
    session.add(token)
    # Let caller handle commit
```

### Enhanced Cleanup Integration

```python
# Add periodic cleanup for expired tokens
async def cleanup_expired_tokens(session: AsyncSession) -> int:
    now = datetime.now(UTC)
    result = await session.execute(
        select(BlacklistedToken).where(BlacklistedToken.expires_at <= now)
    )
    expired_tokens = result.scalars().all()

    for token in expired_tokens:
        await session.delete(token)

    await session.commit()
    return len(expired_tokens)
```

## Related Modules

- **`src.models.blacklisted_token.BlacklistedToken`** - Blacklisted token ORM model
- **`src.core.security`** - JWT token generation and validation
- **`src.api.auth`** - Authentication endpoints using blacklist functionality
- **`src.core.database`** - Database session management

## Configuration Dependencies

- Database connection settings for async operations
- JWT configuration for token structure and expiration
- Timezone configuration for consistent datetime handling

## Summary

The `blacklisted_token.py` repository module provides essential security functionality for JWT token management, implementing token blacklisting for logout and revocation scenarios. The module emphasizes security through proper token validation, performance through efficient database operations, and reliability through robust timezone handling and expiration logic.

Key strengths include secure token invalidation for authentication security, automatic expiration handling for storage efficiency, timezone-aware operations for global compatibility, and transaction-safe operations for flexible integration. The module serves as a critical security component in the ReViewPoint application's authentication system.
