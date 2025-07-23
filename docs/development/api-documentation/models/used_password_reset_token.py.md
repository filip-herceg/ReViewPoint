# UsedPasswordResetToken Model Documentation

## Purpose

The `used_password_reset_token.py` module defines the SQLAlchemy ORM model for tracking used password reset tokens in the ReViewPoint application. This model provides security enforcement for password reset functionality by maintaining a record of consumed reset tokens, preventing token reuse attacks and ensuring that each password reset token can only be used once, serving as a critical security component in the user authentication system.

## Architecture

The model follows a security-focused token tracking pattern:

- **Security Layer**: Password reset token consumption tracking
- **Validation Layer**: Timezone-aware timestamp validation and enforcement
- **Audit Layer**: Complete audit trail of password reset token usage
- **Prevention Layer**: Token reuse attack prevention mechanism
- **Cleanup Layer**: Token lifecycle management and maintenance
- **Integration Layer**: Seamless integration with password reset workflows

## Core Model Class

### `UsedPasswordResetToken`

Secure password reset token tracking model with timezone validation.

```python
# Example usage - Mark token as used
used_token = UsedPasswordResetToken(
    email="user@example.com",
    nonce="secure-random-nonce-12345",
    used_at=datetime.now(UTC)
)

# Save to database
session.add(used_token)
await session.commit()
```

**Table Configuration:**
- `__tablename__ = "used_password_reset_tokens"` - Database table name
- Inherits from `BaseModel` (id, created_at, updated_at)
- Custom timezone validation and handling

## Field Specifications

### User Identification

**Email Tracking:**
```python
email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
```

- **Required Field**: All used tokens must track associated email
- **Indexed**: Optimized for email-based queries and lookups
- **Length Support**: 255 characters for comprehensive email support
- **Security**: Enables user-specific token validation and cleanup

### Token Identification

**Nonce Storage:**
```python
nonce: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
```

- **Required Field**: All used tokens must have nonce identifier
- **Indexed**: Optimized for fast token validation queries
- **Length Limit**: 64 characters supports cryptographically secure nonces
- **Security**: Unique identifier preventing token replay attacks

**Nonce (Number Used Once) Explanation:**
- Cryptographically secure random string unique to each token
- Prevents prediction and brute force attacks
- Combined with email for complete token identification
- Generated during password reset initiation

### Timestamp Management

**Usage Timestamp:**
```python
used_at_default: ClassVar[ABCCallable[[], datetime]] = lambda: datetime.now(UTC)
used_at: Mapped[datetime] = mapped_column(
    "used_at", DateTime(timezone=True), default=used_at_default, nullable=False
)
```

- **Timezone Aware**: Enforces UTC timezone for consistency
- **Required Field**: All used tokens must track usage time
- **Default Value**: Automatically set to current UTC time
- **Audit Trail**: Complete timing information for security analysis

## Advanced Validation Features

### Timezone Validation

**Automatic Timezone Enforcement:**
```python
@validates("used_at")
def _validate_used_at(self, key: str, value: datetime | None) -> datetime:
    # Always ensure used_at is timezone-aware (UTC)
    if value is None:
        raise ValueError("used_at cannot be None")
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
```

**Key Features:**
- Automatic conversion of naive datetime to UTC
- Validation prevents null timestamps
- Ensures consistent timezone handling across deployments
- Maintains data integrity for global applications

### Property-Based Access

**Timezone-Aware Property:**
```python
@property
def used_at_aware(self) -> datetime:
    """Always return used_at as a timezone-aware datetime (UTC)."""
    value = self.used_at
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
```

**Benefits:**
- Guaranteed timezone-aware datetime access
- Backwards compatibility with naive datetime storage
- Consistent API for timezone-sensitive operations
- Safety for global deployment scenarios

### Constructor Validation

**Initialization with Timezone Handling:**
```python
def __init__(self, *args: object, **kwargs: object) -> None:
    used_at = kwargs.get("used_at")
    if isinstance(used_at, datetime):
        if used_at.tzinfo is None:
            # Convert naive datetime to UTC
            kwargs["used_at"] = used_at.replace(tzinfo=UTC)
```

**Security Features:**
- Automatic timezone conversion during object creation
- Prevents timezone-related security vulnerabilities
- Ensures consistent timestamp handling
- Compatible with various datetime input formats

## Usage Patterns

### Password Reset Token Consumption

```python
async def mark_token_as_used(email: str, nonce: str) -> UsedPasswordResetToken:
    """Mark a password reset token as used."""
    
    # Check if token is already used
    existing = await session.execute(
        select(UsedPasswordResetToken).where(
            UsedPasswordResetToken.email == email,
            UsedPasswordResetToken.nonce == nonce
        )
    )
    
    if existing.scalar_one_or_none():
        raise ValueError("Password reset token already used")
    
    # Mark token as used
    used_token = UsedPasswordResetToken(
        email=email,
        nonce=nonce,
        used_at=datetime.now(UTC)
    )
    
    session.add(used_token)
    await session.commit()
    
    logger.info(f"Password reset token used for {email}")
    return used_token
```

### Token Validation

```python
async def is_token_already_used(email: str, nonce: str) -> bool:
    """Check if a password reset token has already been used."""
    
    try:
        result = await session.execute(
            select(UsedPasswordResetToken).where(
                UsedPasswordResetToken.email == email,
                UsedPasswordResetToken.nonce == nonce
            )
        )
        
        used_token = result.scalar_one_or_none()
        
        if used_token:
            logger.warning(
                f"Attempted reuse of password reset token for {email} "
                f"(originally used at {used_token.used_at_aware})"
            )
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking token usage: {e}")
        # Fail secure - treat as already used on error
        return True
```

### Password Reset Workflow Integration

```python
async def complete_password_reset(
    email: str, 
    nonce: str, 
    new_password: str,
    reset_token_expiry: datetime
) -> bool:
    """Complete password reset with token validation."""
    
    try:
        # Check token expiration
        if datetime.now(UTC) > reset_token_expiry:
            raise ValueError("Password reset token expired")
        
        # Check if token already used
        if await is_token_already_used(email, nonce):
            raise ValueError("Password reset token already used")
        
        # Get user
        user = await get_user_by_email(email)
        if not user:
            raise ValueError("User not found")
        
        # Update password
        user.hashed_password = hash_password(new_password)
        
        # Mark token as used
        await mark_token_as_used(email, nonce)
        
        await session.commit()
        
        logger.info(f"Password reset completed for {email}")
        return True
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Password reset failed for {email}: {e}")
        return False
```

### Token Cleanup Operations

```python
async def cleanup_old_used_tokens(retention_days: int = 30) -> int:
    """Remove old used password reset tokens for storage optimization."""
    
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
    
    # Find old used tokens
    old_tokens = await session.execute(
        select(UsedPasswordResetToken).where(
            UsedPasswordResetToken.used_at < cutoff_date
        )
    )
    
    old_token_list = list(old_tokens.scalars())
    cleanup_count = len(old_token_list)
    
    # Remove old tokens
    for token in old_token_list:
        await session.delete(token)
    
    if cleanup_count > 0:
        await session.commit()
        logger.info(f"Cleaned up {cleanup_count} old used password reset tokens")
    
    return cleanup_count
```

### Security Audit Functions

```python
async def get_password_reset_statistics(days: int = 30) -> dict:
    """Get password reset usage statistics for security monitoring."""
    
    start_date = datetime.now(UTC) - timedelta(days=days)
    
    # Total password resets in period
    total_resets = await session.scalar(
        select(func.count(UsedPasswordResetToken.id))
        .where(UsedPasswordResetToken.used_at >= start_date)
    )
    
    # Unique users who reset passwords
    unique_users = await session.scalar(
        select(func.count(func.distinct(UsedPasswordResetToken.email)))
        .where(UsedPasswordResetToken.used_at >= start_date)
    )
    
    # Daily reset counts
    daily_resets = await session.execute(
        select(
            func.date(UsedPasswordResetToken.used_at).label("date"),
            func.count(UsedPasswordResetToken.id).label("count")
        )
        .where(UsedPasswordResetToken.used_at >= start_date)
        .group_by(func.date(UsedPasswordResetToken.used_at))
        .order_by(func.date(UsedPasswordResetToken.used_at))
    )
    
    # Users with multiple resets (potential security concern)
    frequent_resetters = await session.execute(
        select(
            UsedPasswordResetToken.email,
            func.count(UsedPasswordResetToken.id).label("reset_count")
        )
        .where(UsedPasswordResetToken.used_at >= start_date)
        .group_by(UsedPasswordResetToken.email)
        .having(func.count(UsedPasswordResetToken.id) > 3)
        .order_by(func.count(UsedPasswordResetToken.id).desc())
    )
    
    return {
        "period_days": days,
        "total_resets": total_resets,
        "unique_users": unique_users,
        "daily_resets": {str(row.date): row.count for row in daily_resets},
        "frequent_resetters": {row.email: row.reset_count for row in frequent_resetters},
        "average_resets_per_day": total_resets / days if days > 0 else 0
    }
```

## Security Considerations

### Token Reuse Prevention

**Comprehensive Validation:**
- Email + nonce combination ensures unique token identification
- Database constraint prevents duplicate entries
- Immediate validation during password reset attempts
- Fail-secure approach for validation errors

**Attack Prevention:**
```python
async def validate_reset_attempt(email: str, nonce: str) -> tuple[bool, str]:
    """Comprehensive validation for password reset attempts."""
    
    # Check if token already used (prevent replay attacks)
    if await is_token_already_used(email, nonce):
        return False, "Password reset token has already been used"
    
    # Additional security checks could include:
    # - Rate limiting for email addresses
    # - Temporal validation (token age)
    # - IP address tracking
    # - Suspicious pattern detection
    
    return True, "Token validation passed"
```

### Timezone Security

**Consistent Timing:**
- All timestamps stored in UTC for global consistency
- Automatic timezone conversion prevents timing attacks
- Validation ensures no null or naive datetime values
- Property-based access guarantees timezone awareness

**Audit Trail Integrity:**
```python
def audit_token_usage(used_token: UsedPasswordResetToken) -> dict:
    """Generate audit information for password reset token usage."""
    
    return {
        "email": used_token.email,
        "nonce_hash": hashlib.sha256(used_token.nonce.encode()).hexdigest()[:8],
        "used_at_utc": used_token.used_at_aware.isoformat(),
        "created_at_utc": used_token.created_at.isoformat(),
        "usage_delay_seconds": (
            used_token.used_at_aware - used_token.created_at
        ).total_seconds()
    }
```

### Data Privacy

**Personal Information Protection:**
- Email addresses stored for necessary functionality only
- Nonce values provide security without exposing sensitive data
- Cleanup procedures remove old data automatically
- Audit trails maintain security without privacy violations

## Performance Considerations

### Database Optimization

**Indexing Strategy:**
```python
# Recommended indexes for large deployments
__table_args__ = (
    Index("ix_used_tokens_email", "email"),
    Index("ix_used_tokens_nonce", "nonce"),
    Index("ix_used_tokens_email_nonce", "email", "nonce"),  # Composite index
    Index("ix_used_tokens_used_at", "used_at"),
)
```

**Query Optimization:**
```python
# Efficient token validation query
async def fast_token_check(email: str, nonce: str) -> bool:
    """Optimized token validation with minimal data transfer."""
    
    result = await session.execute(
        select(UsedPasswordResetToken.id)
        .where(
            UsedPasswordResetToken.email == email,
            UsedPasswordResetToken.nonce == nonce
        )
        .limit(1)
    )
    
    return result.scalar_one_or_none() is not None
```

### Memory Management

**Efficient Processing:**
```python
# Batch cleanup for memory efficiency
async def batch_cleanup_old_tokens(
    retention_days: int = 30, 
    batch_size: int = 1000
) -> int:
    """Memory-efficient cleanup of old tokens."""
    
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
    total_deleted = 0
    
    while True:
        # Process in batches
        result = await session.execute(
            delete(UsedPasswordResetToken)
            .where(UsedPasswordResetToken.used_at < cutoff_date)
            .limit(batch_size)
        )
        
        deleted_count = result.rowcount
        if deleted_count == 0:
            break
        
        total_deleted += deleted_count
        await session.commit()
        
        # Log progress for large cleanups
        if total_deleted % 10000 == 0:
            logger.info(f"Cleanup progress: {total_deleted} tokens removed")
    
    return total_deleted
```

## Error Handling

### Validation Errors

```python
async def safe_token_marking(email: str, nonce: str) -> tuple[bool, str]:
    """Safely mark token as used with comprehensive error handling."""
    
    try:
        # Validate inputs
        if not email or not isinstance(email, str):
            return False, "Invalid email format"
        
        if not nonce or not isinstance(nonce, str):
            return False, "Invalid nonce format"
        
        # Check for existing usage
        if await is_token_already_used(email, nonce):
            return False, "Token already used"
        
        # Mark as used
        await mark_token_as_used(email, nonce)
        return True, "Token marked as used successfully"
        
    except IntegrityError as e:
        await session.rollback()
        if "unique constraint" in str(e).lower():
            return False, "Token already used (race condition)"
        return False, "Database integrity error"
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error marking token as used: {e}")
        return False, "Internal error processing token"
```

### Timezone Handling Errors

```python
def safe_timezone_conversion(dt: datetime) -> datetime:
    """Safely convert datetime to UTC with error handling."""
    
    try:
        if dt is None:
            raise ValueError("Datetime cannot be None")
        
        if dt.tzinfo is None:
            # Assume naive datetime is in UTC
            return dt.replace(tzinfo=UTC)
        
        # Convert to UTC if not already
        return dt.astimezone(UTC)
        
    except Exception as e:
        logger.error(f"Timezone conversion error: {e}")
        # Return current UTC time as fallback
        return datetime.now(UTC)
```

## Best Practices

### Model Design

- **Security Focus**: Designed specifically for password reset security
- **Timezone Safety**: Comprehensive timezone handling and validation
- **Audit Ready**: Complete tracking of token usage
- **Performance**: Optimized for frequent validation queries
- **Cleanup Support**: Automatic maintenance and storage optimization

### Token Management

- **Immediate Tracking**: Mark tokens as used immediately after validation
- **Unique Identification**: Email + nonce combination prevents conflicts
- **Cleanup Automation**: Regular removal of old used tokens
- **Error Handling**: Fail-secure approach for all operations
- **Audit Logging**: Comprehensive logging of security events

### Security Implementation

- **Reuse Prevention**: Robust token reuse attack prevention
- **Timing Consistency**: Timezone-aware timestamps for global deployments
- **Validation Strict**: Comprehensive input validation and error handling
- **Privacy Protection**: Minimal data storage with automatic cleanup
- **Monitoring Support**: Statistics and audit functions for security teams

## Testing Strategies

### Unit Testing

```python
def test_used_password_reset_token_creation():
    """Test basic used token creation."""
    email = "test@example.com"
    nonce = "test-nonce-123"
    used_at = datetime.now(UTC)
    
    token = UsedPasswordResetToken(
        email=email,
        nonce=nonce,
        used_at=used_at
    )
    
    assert token.email == email
    assert token.nonce == nonce
    assert token.used_at == used_at
    assert token.used_at_aware.tzinfo == UTC

def test_timezone_validation():
    """Test timezone validation functionality."""
    email = "test@example.com"
    nonce = "test-nonce"
    
    # Test with naive datetime (should be converted to UTC)
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    token = UsedPasswordResetToken(email=email, nonce=nonce, used_at=naive_dt)
    
    assert token.used_at.tzinfo == UTC
    assert token.used_at_aware.tzinfo == UTC
```

### Integration Testing

```python
async def test_password_reset_token_workflow():
    """Test complete password reset token workflow."""
    
    email = "integration@example.com"
    nonce = "integration-test-nonce"
    
    # Test initial state - token not used
    is_used = await is_token_already_used(email, nonce)
    assert is_used is False
    
    # Test marking token as used
    used_token = await mark_token_as_used(email, nonce)
    assert used_token.email == email
    assert used_token.nonce == nonce
    
    # Test token now shows as used
    is_used = await is_token_already_used(email, nonce)
    assert is_used is True
    
    # Test duplicate usage prevention
    with pytest.raises(ValueError):
        await mark_token_as_used(email, nonce)
```

### Security Testing

```python
async def test_token_security_features():
    """Test security features of used token system."""
    
    email = "security@example.com"
    nonce = "security-test-nonce"
    
    # Test fail-secure behavior on database errors
    with patch('session.execute', side_effect=DatabaseError("Connection lost")):
        is_used = await is_token_already_used(email, nonce)
        assert is_used is True  # Should fail secure
    
    # Test timezone consistency
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    utc_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    
    token1 = UsedPasswordResetToken(email=email, nonce="nonce1", used_at=naive_dt)
    token2 = UsedPasswordResetToken(email=email, nonce="nonce2", used_at=utc_dt)
    
    # Both should have UTC timezone
    assert token1.used_at.tzinfo == UTC
    assert token2.used_at.tzinfo == UTC
```

## Related Files

### Dependencies

- `datetime` - Timezone-aware timestamp handling with UTC enforcement
- `sqlalchemy` - ORM framework with validation, Mapped, mapped_column
- `typing` - Type annotations including ClassVar and ABCCallable
- `src.models.base` - BaseModel inheritance providing standard model functionality

### Security Integration

- `src.core.security` - Password hashing and token generation utilities
- `src.services.auth` - Authentication service with password reset workflows
- `src.api.v1.auth` - Password reset endpoints and token validation
- `src.utils.email` - Email sending for password reset tokens

### Validation Integration

- `src.schemas.auth` - Password reset request validation schemas
- `src.utils.validation` - Input validation utilities for security
- Background tasks for token cleanup and maintenance

## Configuration

### Token Settings

```python
# Used token configuration
USED_TOKEN_CONFIG = {
    "email_max_length": 255,
    "nonce_max_length": 64,
    "cleanup_retention_days": 30,
    "cleanup_batch_size": 1000
}
```

### Security Settings

```python
# Security configuration
SECURITY_CONFIG = {
    "enforce_timezone_aware": True,
    "require_utc_storage": True,
    "fail_secure_on_errors": True,
    "log_token_usage": True
}
```

### Performance Settings

```python
# Performance optimization
PERFORMANCE_CONFIG = {
    "enable_composite_indexes": True,
    "batch_cleanup_enabled": True,
    "query_timeout_seconds": 10,
    "max_cleanup_batch_size": 5000
}
```

This used password reset token model provides essential security functionality for password reset workflows in the ReViewPoint application, ensuring that each reset token can only be used once while maintaining comprehensive audit trails and timezone-aware timestamp management.
