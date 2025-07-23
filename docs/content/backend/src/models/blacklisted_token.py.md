# BlacklistedToken Model - JWT Security and Logout Management

## Purpose

The blacklisted token model provides secure JWT token revocation functionality for the ReViewPoint platform, enabling proper logout operations and token invalidation. This model stores JWT token identifiers (JTI) with expiration tracking to prevent replay attacks and ensure secure session termination. It serves as a critical security component for authentication workflows and token lifecycle management.

## Key Components

### BlacklistedToken Entity

**`BlacklistedToken`** class inheriting from `BaseModel`:
- JWT token identifier (JTI) storage with unique constraints
- Token expiration tracking for cleanup operations
- Database indexing for efficient token verification
- Integration with JWT authentication workflows

### Core Attributes

#### Token Security Fields
- `jti` - JWT token identifier with unique constraint and index
- `expires_at` - Token expiration timestamp for cleanup

#### Inherited Attributes
- `id` - Primary key from BaseModel
- `created_at` - Blacklisting timestamp
- `updated_at` - Last modification timestamp

## Database Schema Design

### Table Configuration

```python
__tablename__ = "blacklisted_tokens"
```

### Column Definitions

#### JWT Token Tracking
```python
jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
expires_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=False
)
```

**Security Features:**
- **Unique Constraint**: Prevents duplicate JTI entries
- **Database Index**: Fast token lookup during verification
- **Non-nullable Fields**: Ensures complete token information
- **Timezone-aware Expiration**: Consistent expiration handling

## JWT Integration Patterns

### Token Revocation Workflow

The model supports secure token invalidation:

1. **Logout Operation**: User logout triggers token blacklisting
2. **JTI Extraction**: JWT token identifier extracted from token
3. **Expiration Capture**: Token expiration time stored for cleanup
4. **Database Storage**: Blacklisted token persisted with metadata

### Token Verification

Authentication middleware uses the model for security checks:

1. **JTI Lookup**: Token JTI checked against blacklisted tokens
2. **Index Performance**: Database index enables fast verification
3. **Expiration Validation**: Expired tokens automatically invalid
4. **Access Denial**: Blacklisted tokens reject authentication

## Security Architecture

### Logout Security

Comprehensive logout protection:
- **Immediate Revocation**: Tokens blacklisted instantly on logout
- **Replay Prevention**: Blacklisted tokens cannot be reused
- **Session Termination**: Complete session invalidation
- **Audit Trail**: Blacklisting timestamp for security analysis

### Token Lifecycle Management

Complete token security lifecycle:
- **Active Tokens**: Normal authentication and authorization
- **Logout Trigger**: User-initiated or administrative logout
- **Blacklist Storage**: Secure token identifier storage
- **Cleanup Process**: Automatic removal of expired entries

## Performance Optimization

### Database Performance

Efficient blacklist operations through design optimization:
- **Unique Index**: O(log n) lookup performance for JTI verification
- **Minimal Storage**: Only essential data stored (JTI + expiration)
- **Cleanup Strategy**: Expired tokens removed automatically
- **Query Optimization**: Index-based verification prevents table scans

### Memory Efficiency

Lightweight model design for high-frequency operations:
- **Minimal Attributes**: Only security-critical data stored
- **String Efficiency**: JTI as string for UUID compatibility
- **Timestamp Precision**: Timezone-aware datetime for accuracy
- **No Relationships**: Standalone model prevents join overhead

## Cleanup and Maintenance

### Automatic Cleanup Strategy

The model supports automated maintenance:
- **Expiration Tracking**: Expires_at enables cleanup queries
- **Background Jobs**: Scheduled cleanup of expired tokens
- **Storage Optimization**: Regular cleanup prevents table bloat
- **Performance Maintenance**: Index efficiency through cleanup

### Cleanup Implementation Pattern

```python
# Cleanup expired blacklisted tokens
async def cleanup_expired_tokens():
    current_time = datetime.now(UTC)
    expired_tokens = await session.execute(
        select(BlacklistedToken).where(
            BlacklistedToken.expires_at < current_time
        )
    )
    # Delete expired tokens
```

## Integration with Authentication

### Middleware Integration

Authentication middleware leverages the model:
- **Request Interception**: Every authenticated request checked
- **JTI Extraction**: Token JTI extracted from Authorization header
- **Blacklist Verification**: Database lookup for JTI presence
- **Access Control**: Request denied if token blacklisted

### Repository Layer Support

Blacklisted token repository provides:
- **Create Operations**: New blacklist entries during logout
- **Lookup Operations**: Fast JTI verification during authentication
- **Cleanup Operations**: Expired token removal
- **Batch Operations**: Bulk token revocation for security incidents

## Error Handling and Edge Cases

### Database Constraints

Model validation through SQLAlchemy constraints:
- **Unique Violation**: Duplicate JTI attempts handled gracefully
- **Non-null Validation**: Ensures complete blacklist entries
- **Type Validation**: Proper string and datetime types
- **Foreign Key Integrity**: No foreign keys for independence

### Security Edge Cases

Comprehensive security coverage:
- **Token Expiration**: Expired tokens automatically invalid
- **Malformed JTI**: Database constraints prevent invalid entries
- **Concurrent Logout**: Unique constraints handle race conditions
- **System Clock Issues**: Timezone-aware handling prevents issues

## Testing Support

### Test-Friendly Design

The model supports comprehensive security testing:
- **Minimal Dependencies**: No foreign keys simplify testing
- **Predictable Behavior**: Deterministic blacklist operations
- **Cleanup Testing**: Expiration-based test scenarios
- **Performance Testing**: Index performance validation

### Common Test Patterns

```python
# Test token blacklisting
blacklisted = BlacklistedToken(
    jti="unique-token-id",
    expires_at=datetime.now(UTC) + timedelta(hours=1)
)

# Test verification
is_blacklisted = await repository.is_token_blacklisted("token-id")
assert is_blacklisted is True

# Test cleanup
await repository.cleanup_expired_tokens()
```

## Security Best Practices

### JTI Management

Secure JTI handling patterns:
- **UUID Standards**: Use UUID4 for JTI generation
- **Uniqueness Guarantee**: Database constraints ensure uniqueness
- **No PII**: JTI contains no personally identifiable information
- **Cryptographic Security**: Random JTI generation prevents prediction

### Expiration Handling

Proper expiration management:
- **Timezone Awareness**: UTC storage prevents timezone issues
- **Clock Synchronization**: Server time consistency critical
- **Buffer Management**: Slight expiration buffer for clock skew
- **Cleanup Scheduling**: Regular cleanup prevents storage issues

## Monitoring and Analytics

### Security Monitoring

The model supports security analytics:
- **Logout Patterns**: Created_at timestamps for user behavior analysis
- **Token Abuse**: Frequent blacklisting detection
- **Cleanup Metrics**: Expired token volume monitoring
- **Performance Tracking**: Lookup performance measurement

### Audit Trail

Complete audit support:
- **Blacklist Timestamp**: When token was revoked
- **Token Expiration**: Original token validity period
- **Automatic Cleanup**: Expired token removal tracking
- **Performance Metrics**: Query performance monitoring

## Related Files

- [`base.py`](base.py.md) - BaseModel inheritance with timestamp functionality
- [`../schemas/blacklisted_token.py`](../schemas/blacklisted_token.py.md) - Blacklisted token schemas
- [`../repositories/blacklisted_token.py`](../repositories/blacklisted_token.py.md) - Blacklist repository operations
- [`../core/security.py`](../core/security.py.md) - JWT security integration
- [`../api/v1/auth.py`](../api/v1/auth.py.md) - Authentication endpoints using blacklist
- [`../middlewares/`](../middlewares/__init__.py.md) - Authentication middleware integration
