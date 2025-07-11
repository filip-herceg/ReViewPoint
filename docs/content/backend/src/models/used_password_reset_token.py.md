# UsedPasswordResetToken Model

The `UsedPasswordResetToken` model tracks password reset tokens that have been used to prevent token reuse and enhance security in the ReViewPoint application.

## Overview

This model implements a security measure to prevent password reset token reuse attacks. When a password reset token is successfully used, it's recorded in this table to ensure it cannot be used again, even if the token hasn't expired yet.

## Model Definition

```python
class UsedPasswordResetToken(BaseModel):
    __tablename__ = "used_password_reset_tokens"
    
    email: Mapped[str]
    nonce: Mapped[str] 
    used_at: Mapped[datetime]
```

## Fields

### email
- **Type**: `String(255)`
- **Nullable**: `False`
- **Indexed**: `True`
- **Description**: The email address associated with the password reset request
- **Validation**: Must be a non-empty string

### nonce
- **Type**: `String(64)`
- **Nullable**: `False` 
- **Indexed**: `True`
- **Description**: A unique identifier (nonce) for the password reset token
- **Validation**: Must be a non-empty string

### used_at
- **Type**: `DateTime(timezone=True)`
- **Nullable**: `False`
- **Default**: Current UTC timestamp
- **Description**: When the password reset token was used
- **Validation**: Must be timezone-aware datetime

## Key Features

### Timezone Handling
The model includes robust timezone handling to ensure consistent datetime storage:

```python
@validates("used_at")
def _validate_used_at(self, key: str, value: datetime | None) -> datetime:
    if value is None:
        raise ValueError("used_at cannot be None")
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
```

### Property for Timezone-Aware Access
```python
@property
def used_at_aware(self) -> datetime:
    """Always return used_at as a timezone-aware datetime (UTC)."""
    value = self.used_at
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
```

### Field Validation
The model validates that email and nonce fields are non-empty:

```python
@validates("email", "nonce")
def validate_not_empty(self, key: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value
```

## Constructor Behavior

The constructor automatically handles timezone conversion for naive datetime objects:

```python
def __init__(self, *args: object, **kwargs: object) -> None:
    used_at = kwargs.get("used_at")
    if isinstance(used_at, datetime) and used_at.tzinfo is None:
        kwargs["used_at"] = used_at.replace(tzinfo=UTC)
    super().__init__(*args, **kwargs)
```

## Security Purpose

### Token Reuse Prevention
This model serves several security purposes:

1. **Prevents Token Replay Attacks**: Once a token is used, it's recorded and cannot be used again
2. **Audit Trail**: Provides a log of when password reset tokens were consumed
3. **Forensic Analysis**: Helps identify suspicious password reset patterns

### Usage Flow
1. User requests password reset
2. System generates and sends reset token
3. User uses token to reset password
4. System creates `UsedPasswordResetToken` record
5. Subsequent attempts with same token are rejected

## Database Indexes

The model includes indexes on both `email` and `nonce` fields for efficient lookups:

- **email index**: Allows quick filtering by user email
- **nonce index**: Enables fast token existence checks

## Example Usage

### Recording a Used Token
```python
used_token = UsedPasswordResetToken(
    email="user@example.com",
    nonce="abc123def456",
    used_at=datetime.now(UTC)
)
session.add(used_token)
await session.commit()
```

### Checking if Token was Already Used
```python
existing = await session.scalar(
    select(UsedPasswordResetToken)
    .where(
        UsedPasswordResetToken.email == email,
        UsedPasswordResetToken.nonce == nonce
    )
)
if existing:
    raise ValueError("Token has already been used")
```

## String Representation

The model provides a clear string representation for debugging:

```python
def __repr__(self) -> str:
    return f"<UsedPasswordResetToken email={self.email} nonce={self.nonce} used_at={self.used_at}>"
```

## Inheritance

Like all models in the application, `UsedPasswordResetToken` inherits from `BaseModel`, which provides:

- `id`: Primary key (auto-incrementing integer)
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- Standard SQLAlchemy ORM functionality

## Related Components

### Password Reset Service
The model is used by the password reset service to:
- Check if tokens have been used before processing
- Record successful token usage
- Maintain security audit logs

### Database Migration
The model was added in migration `20250605_add_used_password_reset_tokens.py` which creates the corresponding database table.

## Best Practices

1. **Always check for existing tokens** before processing password resets
2. **Use timezone-aware datetimes** for consistent time handling
3. **Index email and nonce fields** for performance
4. **Clean up old records** periodically to prevent table bloat
5. **Log token usage** for security monitoring

## Error Handling

The model includes comprehensive validation that raises appropriate errors:

- `ValueError` for None values in required fields
- `ValueError` for empty strings in email/nonce fields
- Automatic timezone conversion for naive datetime objects

## Performance Considerations

- **Composite Index**: Consider adding a composite index on `(email, nonce)` for common queries
- **Cleanup Strategy**: Implement periodic cleanup of old records (e.g., tokens older than 30 days)
- **Partitioning**: For high-volume applications, consider partitioning by date

This model provides a robust foundation for secure password reset token management in the ReViewPoint application.