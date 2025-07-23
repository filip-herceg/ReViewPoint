# BlacklistedToken Model Documentation

## Purpose

The `blacklisted_token.py` module defines the SQLAlchemy ORM model for JWT token blacklist management in the ReViewPoint application. This model provides secure token revocation functionality by maintaining a database record of invalidated tokens, ensuring that compromised or logged-out tokens cannot be reused for authentication, serving as a critical security component in the JWT authentication system.

## Architecture

The model follows a security-focused token management pattern:

- **Security Layer**: Token invalidation and blacklist enforcement
- **Audit Layer**: Token expiration tracking and cleanup management
- **Performance Layer**: Efficient token lookup and validation
- **Storage Layer**: Persistent token blacklist with database optimization
- **Cleanup Layer**: Automatic removal of expired blacklisted tokens
- **Integration Layer**: Seamless integration with authentication middleware

## Core Model Class

### `BlacklistedToken`

Secure token blacklist model for JWT token revocation management.

```python
# Example usage - Token blacklisting
blacklisted_token = BlacklistedToken(
    jti="unique-jwt-identifier-12345",
    expires_at=datetime(2024, 7, 24, 14, 30, 0, tzinfo=UTC)
)

# Save to database
session.add(blacklisted_token)
await session.commit()
```

**Table Configuration:**

- `__tablename__ = "blacklisted_tokens"` - Database table name
- Inherits from `BaseModel` (id, created_at, updated_at)
- Optimized for fast token lookup and validation

## Field Specifications

### Token Identification

**JWT ID (JTI) Storage:**

```python
jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
```

- **Unique Constraint**: Ensures each token can only be blacklisted once
- **Indexed**: Optimized for fast token lookup during authentication
- **Required Field**: All blacklisted tokens must have JTI
- **String Type**: Flexible to accommodate various JTI formats

**JTI (JWT ID) Explanation:**

- Standard JWT claim identifying unique tokens
- Prevents token replay attacks when combined with blacklisting
- Generated during token creation for tracking purposes
- Used for efficient token validation and revocation

### Expiration Management

**Token Expiration Tracking:**

```python
expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

- **Timezone Aware**: Proper timezone handling for global applications
- **Required Field**: All blacklisted tokens must have expiration
- **Cleanup Support**: Enables automatic removal of expired entries
- **Performance**: Allows efficient cleanup queries

**Expiration Benefits:**

- Automatic cleanup of irrelevant blacklist entries
- Storage optimization for long-running applications
- Performance improvement through reduced blacklist size
- Compliance with token lifecycle management

## Usage Patterns

### Token Blacklisting on Logout

```python
async def blacklist_token_on_logout(jti: str, expires_at: datetime) -> BlacklistedToken:
    """Blacklist a token when user logs out."""

    # Check if token is already blacklisted
    existing = await session.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Token already blacklisted")

    # Create blacklist entry
    blacklisted_token = BlacklistedToken(
        jti=jti,
        expires_at=expires_at
    )

    session.add(blacklisted_token)
    await session.commit()

    logger.info(f"Token blacklisted: {jti}")
    return blacklisted_token
```

### Token Validation Check

```python
async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted."""

    try:
        # Query blacklist for token
        result = await session.execute(
            select(BlacklistedToken).where(BlacklistedToken.jti == jti)
        )
        blacklisted_token = result.scalar_one_or_none()

        if blacklisted_token:
            # Check if blacklist entry is still valid
            if blacklisted_token.expires_at > datetime.now(UTC):
                logger.warning(f"Blocked blacklisted token: {jti}")
                return True
            else:
                # Token has expired, can be cleaned up
                await session.delete(blacklisted_token)
                await session.commit()
                return False

        return False

    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}")
        # Fail secure - treat as blacklisted on error
        return True
```

### Bulk Token Blacklisting

```python
async def blacklist_user_tokens(user_id: int, token_jti_list: list[str]) -> int:
    """Blacklist multiple tokens for a user (e.g., during account suspension)."""

    blacklisted_count = 0

    for jti in token_jti_list:
        try:
            # Calculate expiration (assuming 24-hour tokens)
            expires_at = datetime.now(UTC) + timedelta(hours=24)

            # Create blacklist entry
            blacklisted_token = BlacklistedToken(
                jti=jti,
                expires_at=expires_at
            )

            session.add(blacklisted_token)
            blacklisted_count += 1

        except Exception as e:
            logger.error(f"Failed to blacklist token {jti}: {e}")

    if blacklisted_count > 0:
        await session.commit()
        logger.info(f"Blacklisted {blacklisted_count} tokens for user {user_id}")

    return blacklisted_count
```

### Automatic Cleanup Process

```python
async def cleanup_expired_blacklisted_tokens() -> int:
    """Remove expired tokens from blacklist."""

    current_time = datetime.now(UTC)

    # Find expired blacklisted tokens
    expired_tokens = await session.execute(
        select(BlacklistedToken).where(BlacklistedToken.expires_at <= current_time)
    )

    expired_list = list(expired_tokens.scalars())
    cleanup_count = len(expired_list)

    # Remove expired tokens
    for token in expired_list:
        await session.delete(token)

    if cleanup_count > 0:
        await session.commit()
        logger.info(f"Cleaned up {cleanup_count} expired blacklisted tokens")

    return cleanup_count
```

### Security Audit Functions

```python
async def get_blacklist_statistics() -> dict:
    """Get comprehensive blacklist statistics for security monitoring."""

    current_time = datetime.now(UTC)

    # Total blacklisted tokens
    total_blacklisted = await session.scalar(
        select(func.count(BlacklistedToken.id))
    )

    # Active (not expired) blacklisted tokens
    active_blacklisted = await session.scalar(
        select(func.count(BlacklistedToken.id))
        .where(BlacklistedToken.expires_at > current_time)
    )

    # Expired tokens (ready for cleanup)
    expired_blacklisted = await session.scalar(
        select(func.count(BlacklistedToken.id))
        .where(BlacklistedToken.expires_at <= current_time)
    )

    # Recent blacklisting activity (last 24 hours)
    recent_date = current_time - timedelta(hours=24)
    recent_blacklisted = await session.scalar(
        select(func.count(BlacklistedToken.id))
        .where(BlacklistedToken.created_at >= recent_date)
    )

    return {
        "total_blacklisted": total_blacklisted,
        "active_blacklisted": active_blacklisted,
        "expired_blacklisted": expired_blacklisted,
        "recent_blacklisted": recent_blacklisted,
        "cleanup_recommended": expired_blacklisted > 0
    }
```

## Security Considerations

### Token Security

**Unique Token Tracking:**

- JTI field ensures each token can only be blacklisted once
- Prevents duplicate blacklist entries
- Enables efficient token lookup and validation
- Supports comprehensive token lifecycle management

**Fail-Secure Design:**

```python
async def validate_token_securely(jti: str) -> bool:
    """Validate token with fail-secure approach."""
    try:
        is_blacklisted = await is_token_blacklisted(jti)
        return not is_blacklisted
    except DatabaseError:
        # Fail secure on database errors
        logger.error("Database error during token validation - failing secure")
        return False
    except Exception as e:
        # Fail secure on any unexpected error
        logger.error(f"Unexpected error during token validation: {e}")
        return False
```

### Performance Security

**Efficient Blacklist Checking:**

```python
# Index-optimized blacklist validation
async def fast_blacklist_check(jti: str) -> bool:
    """Optimized blacklist check with caching."""

    # Check cache first (if implemented)
    cached_result = await get_from_cache(f"blacklist:{jti}")
    if cached_result is not None:
        return cached_result

    # Database lookup with index
    result = await session.execute(
        select(BlacklistedToken.id)
        .where(BlacklistedToken.jti == jti)
        .limit(1)
    )

    is_blacklisted = result.scalar_one_or_none() is not None

    # Cache result for performance
    await cache_result(f"blacklist:{jti}", is_blacklisted, ttl=300)

    return is_blacklisted
```

### Cleanup Security

**Secure Cleanup Process:**

- Only removes truly expired tokens
- Maintains audit trail through BaseModel timestamps
- Logs cleanup operations for security monitoring
- Prevents accidental removal of valid blacklist entries

## Performance Considerations

### Database Optimization

**Indexing Strategy:**

```python
# Recommended additional indexes for large deployments
__table_args__ = (
    Index("ix_blacklisted_tokens_jti", "jti"),  # Already defined
    Index("ix_blacklisted_tokens_expires_at", "expires_at"),
    Index("ix_blacklisted_tokens_created_at", "created_at"),
)
```

**Query Optimization:**

```python
# Efficient cleanup query
async def optimized_cleanup():
    """Optimized cleanup using bulk operations."""
    current_time = datetime.now(UTC)

    # Use bulk delete for better performance
    result = await session.execute(
        delete(BlacklistedToken)
        .where(BlacklistedToken.expires_at <= current_time)
    )

    deleted_count = result.rowcount
    await session.commit()

    return deleted_count
```

### Memory Management

**Efficient Token Processing:**

```python
# Process tokens in batches to avoid memory issues
async def process_blacklist_batch(batch_size: int = 1000):
    """Process blacklist validation in batches."""
    offset = 0

    while True:
        tokens = await session.execute(
            select(BlacklistedToken)
            .offset(offset)
            .limit(batch_size)
        )

        token_batch = list(tokens.scalars())
        if not token_batch:
            break

        # Process batch
        for token in token_batch:
            if token.expires_at <= datetime.now(UTC):
                await session.delete(token)

        await session.commit()
        offset += batch_size
```

## Error Handling

### Blacklisting Errors

```python
async def safe_token_blacklisting(jti: str, expires_at: datetime) -> bool:
    """Safely blacklist token with comprehensive error handling."""
    try:
        blacklisted_token = BlacklistedToken(jti=jti, expires_at=expires_at)
        session.add(blacklisted_token)
        await session.commit()
        return True

    except IntegrityError as e:
        await session.rollback()
        if "unique constraint" in str(e).lower():
            # Token already blacklisted - this is acceptable
            logger.info(f"Token {jti} already blacklisted")
            return True
        raise

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to blacklist token {jti}: {e}")
        return False
```

### Validation Errors

```python
def validate_blacklist_data(jti: str, expires_at: datetime) -> None:
    """Validate blacklist data before database operations."""

    if not jti or not isinstance(jti, str):
        raise ValueError("JTI must be a non-empty string")

    if not expires_at or not isinstance(expires_at, datetime):
        raise ValueError("Expires_at must be a datetime object")

    if expires_at.tzinfo is None:
        raise ValueError("Expires_at must be timezone-aware")

    # Check that expiration is in the future (within reason)
    current_time = datetime.now(UTC)
    max_future = current_time + timedelta(days=365)  # 1 year max

    if expires_at <= current_time:
        raise ValueError("Expiration time must be in the future")

    if expires_at > max_future:
        raise ValueError("Expiration time too far in the future")
```

## Best Practices

### Model Design

- **Security Focus**: Designed specifically for secure token revocation
- **Performance**: Optimized for frequent token validation queries
- **Minimal Data**: Only stores essential information for blacklisting
- **Cleanup Ready**: Automatic expiration support for maintenance
- **Audit Support**: Timestamps for security monitoring

### Token Management

- **Immediate Blacklisting**: Blacklist tokens immediately upon logout
- **Bulk Operations**: Support for bulk token revocation
- **Cleanup Automation**: Regular cleanup of expired entries
- **Error Handling**: Fail-secure approach for security operations
- **Monitoring**: Comprehensive logging and statistics

### Security Implementation

- **Unique Constraints**: Prevent duplicate blacklist entries
- **Index Optimization**: Fast token lookup for security validation
- **Timezone Awareness**: Proper handling of expiration times
- **Fail-Secure**: Security-first error handling approach
- **Audit Trails**: Complete logging of blacklist operations

## Testing Strategies

### Unit Testing

```python
def test_blacklisted_token_creation():
    """Test basic blacklisted token creation."""
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    token = BlacklistedToken(
        jti="test-jti-123",
        expires_at=expires_at
    )

    assert token.jti == "test-jti-123"
    assert token.expires_at == expires_at

def test_blacklisted_token_validation():
    """Test blacklisted token validation."""
    # Test with timezone-naive datetime (should raise error)
    with pytest.raises(ValueError):
        validate_blacklist_data("test-jti", datetime.now())

    # Test with valid data
    expires_at = datetime.now(UTC) + timedelta(hours=1)
    validate_blacklist_data("test-jti", expires_at)  # Should not raise
```

### Integration Testing

```python
async def test_token_blacklist_workflow():
    """Test complete token blacklist workflow."""

    jti = "integration-test-jti"
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    # Test blacklisting
    blacklisted_token = await blacklist_token_on_logout(jti, expires_at)
    assert blacklisted_token.jti == jti

    # Test validation
    is_blacklisted = await is_token_blacklisted(jti)
    assert is_blacklisted is True

    # Test duplicate blacklisting
    with pytest.raises(ValueError):
        await blacklist_token_on_logout(jti, expires_at)

    # Test cleanup after expiration
    # (Would require time manipulation or test data setup)
```

### Security Testing

```python
async def test_blacklist_security():
    """Test blacklist security features."""

    # Test fail-secure behavior
    with patch('session.execute', side_effect=DatabaseError("Connection lost")):
        result = await validate_token_securely("test-jti")
        assert result is False  # Should fail secure

    # Test unique constraint enforcement
    jti = "duplicate-test-jti"
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    # First blacklisting should succeed
    await blacklist_token_on_logout(jti, expires_at)

    # Second blacklisting should fail
    with pytest.raises(ValueError):
        await blacklist_token_on_logout(jti, expires_at)
```

## Related Files

### Dependencies

- `datetime` - Timestamp handling for expires_at field and timezone management
- `sqlalchemy` - ORM framework with Mapped, mapped_column for model definition
- `src.models.base` - BaseModel inheritance providing id, created_at, updated_at

### Security Integration

- `src.core.security` - JWT token utilities and JTI generation
- `src.api.deps` - Authentication middleware with blacklist checking
- `src.services.auth` - Authentication service with token management
- `src.repositories.blacklisted_token` - Blacklist data access layer

### Service Integration

- `src.api.v1.auth` - Authentication endpoints with logout functionality
- `src.utils.cache` - Caching utilities for blacklist performance optimization
- Background tasks for automatic cleanup processes

## Configuration

### Blacklist Settings

```python
# Blacklist configuration
BLACKLIST_CONFIG = {
    "cleanup_interval_hours": 6,
    "max_token_lifetime_days": 30,
    "enable_cleanup_logging": True,
    "batch_size": 1000
}
```

### Performance Settings

```python
# Performance optimization
PERFORMANCE_CONFIG = {
    "enable_blacklist_caching": True,
    "cache_ttl_seconds": 300,
    "index_optimization": True,
    "bulk_operation_size": 5000
}
```

### Security Settings

```python
# Security configuration
SECURITY_CONFIG = {
    "fail_secure_on_errors": True,
    "log_blacklist_operations": True,
    "require_timezone_aware": True,
    "max_future_expiration_days": 365
}
```

This blacklisted token model provides essential security functionality for JWT token revocation in the ReViewPoint application, ensuring that compromised or logged-out tokens cannot be reused while maintaining optimal performance and comprehensive audit capabilities.
