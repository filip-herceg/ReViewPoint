# UsedPasswordResetToken Model - Password Reset Security

## Purpose

The used password reset token model provides comprehensive security for password reset operations in the ReViewPoint platform, preventing token replay attacks and ensuring single-use password reset functionality. This model tracks used password reset tokens by email and nonce combination, with automatic timezone handling and strict validation to maintain password reset security integrity.

## Key Components

### UsedPasswordResetToken Entity

**`UsedPasswordResetToken`** class inheriting from `BaseModel`:

- Email and nonce tracking for password reset operations
- Timezone-aware timestamp management with UTC enforcement
- Comprehensive validation for email and nonce fields
- Security-focused design preventing token reuse attacks

### Core Attributes

#### Password Reset Tracking

- `email` - User email address with database index
- `nonce` - Unique password reset token nonce with index
- `used_at` - Timezone-aware timestamp of token usage

#### Inherited Attributes

- `id` - Primary key from BaseModel
- `created_at` - Record creation timestamp
- `updated_at` - Last modification timestamp

## Database Schema Design

### Table Configuration

```python
__tablename__ = "used_password_reset_tokens"
```

### Column Definitions

#### Token Tracking Fields

```python
email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
nonce: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
used_at: Mapped[datetime] = mapped_column(
    "used_at", DateTime(timezone=True), default=used_at_default, nullable=False
)
```

**Performance Features:**

- **Email Index**: Fast lookup by user email for token validation
- **Nonce Index**: Efficient nonce verification during reset operations
- **Timezone Storage**: UTC-based datetime storage for consistency
- **Default Handling**: Automatic used_at timestamp with timezone awareness

## Timezone Management System

### UTC Enforcement

Comprehensive timezone handling with automatic UTC conversion:

```python
used_at_default: ClassVar[ABCCallable[[], datetime]] = lambda: datetime.now(UTC)
```

### Timezone Validation

Automatic timezone conversion and validation:

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

**Security Features:**

- **Non-null Enforcement**: used_at cannot be None for security audit
- **Timezone Conversion**: Naive datetimes automatically converted to UTC
- **Consistency Guarantee**: All timestamps stored in UTC timezone
- **Validation Integration**: SQLAlchemy validator ensures data integrity

### Timezone-Aware Property

Safe timezone access through property interface:

```python
@property
def used_at_aware(self) -> datetime:
    """Always return used_at as a timezone-aware datetime (UTC)."""
    value = self.used_at
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
```

## Validation System

### Field Validation

Comprehensive validation for email and nonce fields:

```python
@validates("email", "nonce")
def validate_not_empty(self, key: str, value: str) -> str:
    """Validate that the given value is a non-empty string."""
    if not isinstance(key, str):
        raise ValueError("key must be a string")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value
```

**Validation Features:**

- **Type Checking**: Ensures string types for key and value
- **Empty String Prevention**: Rejects empty or whitespace-only values
- **Field-Specific Errors**: Clear error messages identifying the field
- **Strip Validation**: Whitespace-only strings considered invalid

### Constructor Validation

Timezone handling during object initialization:

```python
def __init__(self, *args: object, **kwargs: object) -> None:
    used_at = kwargs.get("used_at")
    if isinstance(used_at, datetime):
        if used_at.tzinfo is None:
            # Convert naive datetime to UTC
            kwargs["used_at"] = used_at.replace(tzinfo=UTC)
    super().__init__(*args, **kwargs)
```

**Initialization Features:**

- **Timezone Conversion**: Naive datetimes converted during creation
- **Kwargs Processing**: Safe handling of used_at parameter
- **Parent Initialization**: Proper BaseModel initialization chain
- **Type Safety**: isinstance check before datetime processing

## Password Reset Security

### Token Replay Prevention

The model prevents password reset token replay attacks:

1. **Token Usage Tracking**: Each successful password reset recorded
2. **Email-Nonce Combination**: Unique tracking per reset attempt
3. **Usage Timestamp**: Precise timing for security analysis
4. **Database Persistence**: Permanent record for audit trails

### Security Workflow Integration

Password reset security workflow:

1. **Token Generation**: Unique nonce generated for password reset
2. **Email Delivery**: Reset link sent with nonce parameter
3. **Token Validation**: Nonce checked against used tokens
4. **Usage Recording**: Successful reset creates UsedPasswordResetToken record
5. **Replay Prevention**: Subsequent attempts with same nonce rejected

## Performance Optimization

### Database Indexing

Strategic indexing for password reset operations:

- **Email Index**: Fast lookup by user email during reset
- **Nonce Index**: Efficient nonce verification to prevent reuse
- **Composite Queries**: Efficient email + nonce combination queries
- **Range Queries**: Cleanup operations by timestamp ranges

### Query Patterns

Common password reset query optimizations:

- **Token Existence Check**: Index-based nonce verification
- **User Reset History**: Email-based reset history queries
- **Cleanup Operations**: Timestamp-based expired token removal
- **Security Analysis**: Pattern detection through indexed queries

## Error Handling

### Validation Errors

Comprehensive error handling for security validation:

- **Empty Field Errors**: Clear messages for missing email/nonce
- **Type Errors**: Type validation for all input parameters
- **Timezone Errors**: Used_at cannot be None validation
- **Constructor Errors**: Safe initialization with error propagation

### Database Constraints

Model-level constraint handling:

- **Index Violations**: Efficient handling of duplicate attempts
- **Non-null Constraints**: Required field validation
- **Type Constraints**: String length and type enforcement
- **Foreign Key Independence**: No foreign keys for security isolation

## Security Analytics

### Audit Trail Support

The model provides comprehensive audit capabilities:

- **Usage Tracking**: When each password reset token was used
- **Email Patterns**: Reset attempt patterns by email address
- **Nonce Analysis**: Token generation and usage correlation
- **Timestamp Precision**: Microsecond-level usage tracking

### Attack Detection

Security monitoring through model data:

- **Replay Attempts**: Detection of token reuse attempts
- **Frequency Analysis**: Unusual reset pattern identification
- **Time-based Attacks**: Timing attack detection through timestamps
- **Volume Monitoring**: High-frequency reset attempt detection

## Testing Support

### Test-Friendly Design

The model supports comprehensive security testing:

- **Timezone Testing**: Multiple timezone scenario validation
- **Validation Testing**: Comprehensive field validation coverage
- **Edge Case Testing**: Empty string and None value handling
- **Security Testing**: Token replay attack simulation

### Common Test Patterns

```python
# Test token creation
used_token = UsedPasswordResetToken(
    email="user@example.com",
    nonce="unique-reset-nonce"
)

# Test timezone handling
naive_datetime = datetime(2024, 1, 1, 12, 0, 0)
used_token = UsedPasswordResetToken(
    email="user@example.com",
    nonce="nonce",
    used_at=naive_datetime
)
assert used_token.used_at_aware.tzinfo == UTC

# Test validation
with pytest.raises(ValueError):
    UsedPasswordResetToken(email="", nonce="valid-nonce")
```

## Integration Points

### Repository Layer

Used password reset token repository provides:

- **Creation Operations**: Recording used tokens after successful reset
- **Lookup Operations**: Checking if nonce already used
- **Cleanup Operations**: Removing old used tokens
- **Analytics Queries**: Security pattern analysis

### Security Service Integration

Password reset services leverage the model:

- **Token Validation**: Checking nonce usage before reset
- **Usage Recording**: Creating records after successful reset
- **Security Monitoring**: Analyzing reset patterns
- **Attack Prevention**: Blocking replay attacks

## String Representation

### Debug Support

Clear string representation for security debugging:

```python
def __repr__(self: "UsedPasswordResetToken") -> str:
    """Return a string representation of the UsedPasswordResetToken instance."""
    return f"<UsedPasswordResetToken email={self.email} nonce={self.nonce} used_at={self.used_at}>"
```

**Features:**

- **Email Display**: User identification for debugging
- **Nonce Display**: Token identification for analysis
- **Timestamp Display**: Usage time for security investigation
- **Consistent Format**: Standard representation across application

## Related Files

- [`base.py`](base.py.md) - BaseModel inheritance with timestamp functionality
- [`../schemas/auth.py`](../schemas/auth.py.md) - Password reset schemas
- [`../services/user.py`](../services/user.py.md) - User service with password reset logic
- [`../core/security.py`](../core/security.py.md) - Security utilities for password reset
- [`../api/v1/auth.py`](../api/v1/auth.py.md) - Authentication endpoints
- [`../utils/validation.py`](../utils/validation.py.md) - Additional validation utilities
