# Blacklisted Token Schema Module

## Overview

The `blacklisted_token.py` schema module provides a comprehensive Pydantic model definition for JWT token blacklisting operations in the ReViewPoint application. This module implements token revocation data validation, serialization, and API contract definitions for logout, token invalidation, and security operations with proper type safety and ORM integration.

**Key Features:**

- Complete blacklisted token metadata schema
- ORM model integration with `from_attributes=True`
- JWT ID (JTI) tracking for token identification
- Timestamp management for expiration handling
- Type-safe token revocation operations

## Module Structure

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict
```

### Core Dependencies

#### External Dependencies

- `datetime` - Standard library datetime support for timestamp fields
- `pydantic` - Core validation and serialization framework
- `pydantic.BaseModel` - Base class for schema definitions
- `pydantic.ConfigDict` - Model configuration

## Blacklisted Token Schema

### BlacklistedTokenSchema Class

```python
class BlacklistedTokenSchema(BaseModel):
    """
    Schema for a blacklisted JWT token.

    Attributes:
        jti (str): The JWT ID (unique identifier for the token).
        expires_at (datetime): The expiration datetime of the token.
        created_at (Optional[datetime]): The creation datetime of the token, if available.
    """

    jti: str
    expires_at: datetime
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
```

**Purpose:** Primary schema for representing blacklisted JWT tokens in API responses and database operations.

**Key Features:**

- **JWT Identification:** JTI (JWT ID) for unique token tracking
- **Expiration Management:** Tracks when tokens naturally expire
- **Creation Tracking:** Optional timestamp for blacklist entry creation
- **ORM Integration:** `from_attributes=True` enables direct ORM model conversion
- **Type Safety:** Strict typing with optional creation timestamp

## Field Definitions and Validation

### Token Identifier Field

#### JTI Field

```python
jti: str
```

**Purpose:** JWT ID (JTI) claim for unique token identification and revocation.

**Key Features:**

- **Unique Identifier:** Each JWT token has a unique JTI value
- **Required Field:** All blacklisted tokens must have JTI
- **Revocation Tracking:** Enables specific token invalidation
- **Security Critical:** Primary key for blacklist operations

**JWT Integration:**

```python
# JWT token with JTI claim
payload = {
    "sub": "user_id",
    "jti": "unique-token-id-123",
    "exp": 1234567890
}
token = jwt.encode(payload, secret_key)

# Blacklist the token
blacklisted = BlacklistedTokenSchema(
    jti="unique-token-id-123",
    expires_at=datetime.fromtimestamp(1234567890)
)
```

### Timestamp Fields

#### Expires At Field

```python
expires_at: datetime
```

**Purpose:** Records when the blacklisted token naturally expires.

**Key Features:**

- **Expiration Tracking:** Knows when token becomes invalid naturally
- **Cleanup Operations:** Enables automatic blacklist cleanup
- **Required Field:** All tokens have expiration times
- **UTC Timestamps:** Consistent timezone handling

**Usage Patterns:**

- Automatic cleanup of expired blacklisted tokens
- Optimization to avoid checking expired tokens
- Audit trail for token lifecycle management
- Database indexing for efficient queries

#### Created At Field

```python
created_at: datetime | None = None
```

**Purpose:** Optional timestamp recording when the token was blacklisted.

**Key Features:**

- **Optional Field:** May not be available in all contexts
- **Audit Trail:** Tracks when revocation occurred
- **Investigation Support:** Helps with security incident analysis
- **Flexible Usage:** Can be None for backwards compatibility

**Audit Use Cases:**

- Security incident investigation
- User logout tracking
- Token revocation pattern analysis
- Compliance and logging requirements

## Model Configuration

### ORM Integration Configuration

```python
model_config = ConfigDict(from_attributes=True)
```

**Purpose:** Enables seamless conversion from ORM models to Pydantic schemas.

**Key Benefits:**

- **Direct Conversion:** `BlacklistedTokenSchema.model_validate(token_orm)` works automatically
- **Attribute Mapping:** ORM model attributes map to schema fields
- **Performance:** Efficient conversion without manual field mapping
- **Type Safety:** Maintains type validation during conversion

**Usage Example:**

```python
# Convert ORM model to schema
blacklisted_orm = await session.get(BlacklistedToken, jti)
schema = BlacklistedTokenSchema.model_validate(blacklisted_orm)

# Use in API response
return schema
```

## Security and Token Revocation

### Token Blacklisting Flow

```python
async def blacklist_token(jti: str, expires_at: datetime) -> BlacklistedTokenSchema:
    """Blacklist a JWT token for security purposes."""
    
    # Create blacklist entry
    blacklist_data = {
        "jti": jti,
        "expires_at": expires_at,
        "created_at": datetime.utcnow()
    }
    
    # Validate with schema
    blacklisted_schema = BlacklistedTokenSchema(**blacklist_data)
    
    # Save to database
    await blacklist_repository.create(blacklisted_schema)
    
    return blacklisted_schema
```

### Token Validation Integration

```python
async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted."""
    
    # Query blacklist
    blacklisted = await blacklist_repository.get_by_jti(jti)
    
    if blacklisted is None:
        return False
    
    # Convert to schema for type safety
    schema = BlacklistedTokenSchema.model_validate(blacklisted)
    
    # Check if still relevant (not naturally expired)
    if schema.expires_at < datetime.utcnow():
        # Token naturally expired, no longer need to track
        await blacklist_repository.delete_by_jti(jti)
        return False
    
    return True
```

## API Integration Patterns

### Logout Endpoint

```python
@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user),
    token_data: TokenData = Depends(get_token_data)
):
    if token_data.jti and token_data.exp:
        # Blacklist the current token
        blacklisted = BlacklistedTokenSchema(
            jti=token_data.jti,
            expires_at=token_data.exp,
            created_at=datetime.utcnow()
        )
        
        await blacklist_service.blacklist_token(blacklisted)
    
    return {"message": "Successfully logged out"}
```

### Token Revocation Endpoint

```python
@router.post("/revoke", response_model=BlacklistedTokenSchema)
async def revoke_token(
    jti: str,
    current_user: User = Depends(get_admin_user)
):
    # Admin can revoke any token by JTI
    token_info = await jwt_service.get_token_info(jti)
    
    blacklisted = BlacklistedTokenSchema(
        jti=jti,
        expires_at=token_info.expires_at,
        created_at=datetime.utcnow()
    )
    
    await blacklist_service.blacklist_token(blacklisted)
    return blacklisted
```

### Blacklist Listing Endpoint

```python
@router.get("/blacklist", response_model=list[BlacklistedTokenSchema])
async def list_blacklisted_tokens(
    current_user: User = Depends(get_admin_user)
):
    blacklisted_tokens = await blacklist_repository.list_active()
    return [
        BlacklistedTokenSchema.model_validate(token) 
        for token in blacklisted_tokens
    ]
```

## Database Integration

### ORM Model Mapping

```python
# BlacklistedToken ORM model
class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    
    jti: str = Column(String, primary_key=True)
    expires_at: datetime = Column(DateTime, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

# Schema automatically maps to these fields
schema = BlacklistedTokenSchema.model_validate(blacklisted_orm)
```

### Repository Integration

```python
async def create_blacklisted_token(
    session: AsyncSession,
    jti: str,
    expires_at: datetime
) -> BlacklistedTokenSchema:
    blacklisted_orm = BlacklistedToken(
        jti=jti,
        expires_at=expires_at
    )
    session.add(blacklisted_orm)
    await session.commit()
    await session.refresh(blacklisted_orm)
    
    return BlacklistedTokenSchema.model_validate(blacklisted_orm)
```

## Cleanup and Maintenance

### Automatic Cleanup

```python
async def cleanup_expired_blacklisted_tokens() -> int:
    """Remove blacklisted tokens that have naturally expired."""
    
    current_time = datetime.utcnow()
    
    # Find expired blacklisted tokens
    expired_tokens = await blacklist_repository.get_expired(current_time)
    
    # Validate with schema and count
    count = 0
    for token_orm in expired_tokens:
        schema = BlacklistedTokenSchema.model_validate(token_orm)
        if schema.expires_at < current_time:
            await blacklist_repository.delete_by_jti(schema.jti)
            count += 1
    
    return count
```

### Background Cleanup Task

```python
@periodic_task(hours=1)
async def scheduled_blacklist_cleanup():
    """Scheduled task to clean up expired blacklisted tokens."""
    
    try:
        cleaned_count = await cleanup_expired_blacklisted_tokens()
        logger.info(f"Cleaned up {cleaned_count} expired blacklisted tokens")
    except Exception as e:
        logger.error(f"Blacklist cleanup failed: {e}")
```

## Error Handling

### Validation Errors

```python
try:
    blacklisted_schema = BlacklistedTokenSchema(**token_data)
except ValidationError as e:
    for error in e.errors():
        field = error['loc'][0]
        
        if field == 'jti':
            raise HTTPException(
                status_code=422,
                detail="Invalid JWT ID format"
            )
        elif field == 'expires_at':
            raise HTTPException(
                status_code=422,
                detail="Invalid expiration timestamp"
            )
```

### Common Error Scenarios

- **Missing JTI:** Required field not provided
- **Invalid expiration:** Non-datetime or past timestamp
- **Duplicate blacklisting:** Token already blacklisted
- **Invalid datetime format:** Malformed timestamp data

## Testing Strategies

### Schema Validation Testing

```python
def test_blacklisted_token_schema_valid():
    data = {
        "jti": "unique-token-id-123",
        "expires_at": datetime(2023, 12, 31, 23, 59, 59),
        "created_at": datetime(2023, 1, 1, 12, 0, 0)
    }
    schema = BlacklistedTokenSchema(**data)
    assert schema.jti == "unique-token-id-123"
    assert schema.expires_at.year == 2023
    assert schema.created_at is not None

def test_blacklisted_token_schema_minimal():
    data = {
        "jti": "minimal-token-id",
        "expires_at": datetime(2023, 12, 31, 23, 59, 59)
        # created_at is optional
    }
    schema = BlacklistedTokenSchema(**data)
    assert schema.jti == "minimal-token-id"
    assert schema.created_at is None

def test_blacklisted_token_schema_missing_required():
    data = {
        "jti": "test-token"
        # Missing required expires_at
    }
    with pytest.raises(ValidationError) as exc_info:
        BlacklistedTokenSchema(**data)
    
    errors = exc_info.value.errors()
    assert any(error['loc'] == ('expires_at',) for error in errors)
```

### ORM Integration Testing

```python
def test_blacklisted_token_from_orm(db_session):
    # Create ORM instance
    blacklisted_orm = BlacklistedToken(
        jti="test-jti-123",
        expires_at=datetime(2023, 12, 31, 23, 59, 59)
    )
    db_session.add(blacklisted_orm)
    db_session.commit()
    
    # Convert to schema
    schema = BlacklistedTokenSchema.model_validate(blacklisted_orm)
    
    assert schema.jti == "test-jti-123"
    assert schema.expires_at.year == 2023
    assert schema.created_at is not None  # Set by ORM default
```

### Mock Data Factories

```python
def create_blacklisted_token_data():
    return {
        "jti": "test-token-id-123",
        "expires_at": datetime(2023, 12, 31, 23, 59, 59),
        "created_at": datetime(2023, 1, 1, 12, 0, 0)
    }

def create_minimal_blacklisted_token_data():
    return {
        "jti": "minimal-token-id",
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }
```

## Performance Considerations

### Efficient Operations

- **Simple Schema:** Minimal fields for fast validation
- **Database Indexes:** JTI field should be indexed for fast lookups
- **Cleanup Operations:** Regular cleanup prevents table bloat
- **Timestamp Handling:** UTC timestamps for consistency

### Optimization Strategies

- **Batch Cleanup:** Process multiple expired tokens together
- **Index Usage:** Leverage database indexes for expires_at queries
- **Memory Efficiency:** Lightweight schema with minimal overhead
- **Cache Integration:** Cache frequently checked JTIs if needed

## Security Considerations

### Token Security

- **JTI Uniqueness:** Prevents token reuse attacks
- **Expiration Tracking:** Automatic cleanup for security
- **Audit Trail:** Creation timestamps for investigation
- **Database Security:** Secure storage of blacklist data

### Attack Prevention

- **Token Replay:** Blacklisted tokens cannot be reused
- **Logout Security:** Immediate token invalidation
- **Cleanup Security:** Expired tokens removed automatically
- **Admin Controls:** Administrative token revocation capabilities

## Related Modules

### **Core Dependencies**

- **`src.models.blacklisted_token`** - BlacklistedToken ORM model
- **`src.repositories.blacklisted_token`** - Blacklist repository operations

### **Integration Points**

- **`src.core.security`** - JWT token validation and blacklist checking
- **`src.api.v1.auth`** - Authentication endpoints using blacklist
- **`src.services.auth`** - Authentication service with blacklist integration

### **External Dependencies**

- **`datetime`** - Standard library datetime support
- **`pydantic`** - Core validation and serialization framework

## Configuration Dependencies

- Database configuration for BlacklistedToken model
- JWT configuration for JTI claim handling
- Cleanup task scheduling configuration
- Logging configuration for blacklist operations

## Summary

The `blacklisted_token.py` schema module provides a comprehensive, security-focused schema for JWT token blacklisting operations in the ReViewPoint application. Through a well-structured Pydantic model with proper validation, timestamp management, and ORM integration, it ensures secure token revocation and provides excellent developer experience for authentication security operations.

Key strengths include comprehensive token blacklisting with JTI tracking, proper expiration and cleanup handling, seamless ORM integration with `from_attributes=True`, security-focused design for token revocation, and efficient database operations with cleanup automation. The module serves as the foundation for secure token management and revocation across the entire application.
