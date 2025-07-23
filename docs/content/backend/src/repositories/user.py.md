# User Repository Module

## Overview

The `user.py` repository module provides comprehensive data access layer functionality for user management in the ReViewPoint application. This module implements a full spectrum of user operations including CRUD operations, advanced querying, bulk operations, data export/import, user lifecycle management, and analytics capabilities with proper error handling and caching integration.

**Key Features:**

- Complete CRUD operations with validation and error handling
- Advanced querying with filtering, pagination, and search capabilities
- Bulk operations for efficient batch processing
- Data export/import functionality (CSV/JSON)
- User lifecycle management (activation, deactivation, soft deletion, anonymization)
- Rate limiting for sensitive operations
- Caching integration for performance optimization
- Analytics and reporting capabilities
- Audit logging and compliance features

## Module Structure

```python
import csv, io, json, logging
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, Final, Literal
from sqlalchemy import extract, func, or_, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict
```

### Core Dependencies

#### Internal Models

- `src.models.user.User` - User ORM model
- `src.models.file.File` - File ORM model for relationships

#### Utility Systems

- `src.utils.cache.user_cache` - Redis-based user caching
- `src.utils.rate_limit.AsyncRateLimiter` - Rate limiting functionality
- `src.utils.errors` - Custom exception classes
- `src.utils.validation` - Email and password validation
- `src.utils.hashing` - Password hashing utilities

#### External Dependencies

- SQLAlchemy for database operations
- AsyncSession for async database access
- Loguru for structured logging

## Core Operations

### 1. Basic CRUD Operations

#### get_user_by_id Function

```python
async def get_user_by_id(
    session: AsyncSession, user_id: int, use_cache: bool = True
) -> User | None:
    """Fetch a user by their ID, optionally using async cache."""
    cache_key: Final[str] = f"user_id:{user_id}"
    if use_cache:
        cached_id_obj = await user_cache.get(cache_key)
        cached_id: int | None = (
            cached_id_obj if isinstance(cached_id_obj, int) else None
        )
        if cached_id is not None:
            result = await session.execute(select(User).where(User.id == cached_id))
            return result.scalar_one_or_none()
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is not None and use_cache:
        await user_cache.set(cache_key, user.id, ttl=60)
    return user
```

**Purpose:** Retrieves a user by ID with optional Redis caching for performance optimization.

**Key Features:**

- **Caching Integration:** Redis-based caching with 60-second TTL
- **Cache Key Strategy:** Structured keys using `user_id:{id}` pattern
- **Type Safety:** Validates cached data types before use
- **Fallback Logic:** Database fallback when cache misses
- **Performance Optimization:** Reduces database load for frequent lookups

**Caching Strategy:**

```python
# Cache hit path
cached_id = await user_cache.get(f"user_id:{user_id}")
if cached_id and isinstance(cached_id, int):
    return await session.execute(select(User).where(User.id == cached_id))

# Cache miss path - fetch from DB and populate cache
user = await session.execute(select(User).where(User.id == user_id))
if user:
    await user_cache.set(f"user_id:{user_id}", user.id, ttl=60)
```

#### create_user_with_validation Function

```python
async def create_user_with_validation(
    session: AsyncSession, email: str, password: str, name: str | None = None
) -> User:
    """Create a user with validation and error handling."""
    if not validate_email(email):
        logging.warning(f"Invalid email format: {email}")
        raise ValidationError("Invalid email format.")

    err: str | None = get_password_validation_error(password)
    if err is not None:
        logging.warning(f"Password validation failed for {email}")
        raise ValidationError(err)

    is_unique: bool = await is_email_unique(session, email)
    if not is_unique:
        logging.warning(f"Email already exists: {email}")
        raise UserAlreadyExistsError("Email already exists.")

    from src.utils.hashing import hash_password
    hashed: str = hash_password(password)
    user = User(email=email, hashed_password=hashed, is_active=True)
    if name is not None:
        user.name = name

    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        logging.info(f"User created successfully: {user.email}, id={user.id}")
    except Exception as e:
        tb: str = traceback.format_exc()
        logging.error(f"Exception during user creation for {email}: {e}\nTraceback: {tb}")
        await session.rollback()
        raise
    return user
```

**Purpose:** Creates new users with comprehensive validation, security, and error handling.

**Key Features:**

- **Email Validation:** Format validation using utility functions
- **Password Security:** Strength validation and secure hashing
- **Uniqueness Checking:** Prevents duplicate email registrations
- **Comprehensive Logging:** Debug, warning, info, and error logging
- **Transaction Safety:** Rollback on errors with exception propagation
- **Audit Trail:** Creation logging for security monitoring

**Validation Pipeline:**

1. Email format validation
2. Password strength requirements
3. Email uniqueness verification
4. Secure password hashing
5. Database transaction with rollback protection

### 2. Advanced Querying Operations

#### list_users Function

```python
async def list_users(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 20,
    email: str | None = None,
    name: str | None = None,
    q: str | None = None,
    sort: Literal["created_at", "name", "email"] = "created_at",
    order: Literal["desc", "asc"] = "desc",
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> tuple[list[User], int]:
    """List users with filtering and pagination."""
    stmt = select(User)

    # Apply filters
    if email:
        stmt = stmt.where(User.email.ilike(f"%{email}%"))
    if name:
        stmt = stmt.where(User.name.ilike(f"%{name}%"))
    if q:
        stmt = stmt.where(or_(User.email.ilike(f"%{q}%"), User.name.ilike(f"%{q}%")))
    if created_after:
        stmt = stmt.where(User.created_at >= created_after)
    if created_before:
        stmt = stmt.where(User.created_at <= created_before)

    # Apply sorting
    if sort in {"created_at", "name", "email"}:
        col = getattr(User, sort)
        if order == "desc":
            col = col.desc()
        else:
            col = col.asc()
        stmt = stmt.order_by(col)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    # Apply pagination
    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    users = list(result.scalars().all())

    return users, total
```

**Purpose:** Provides comprehensive user listing with filtering, searching, sorting, and pagination capabilities.

**Key Features:**

- **Multiple Filter Types:** Email, name, general search, date ranges
- **Flexible Sorting:** Multiple sort fields with ascending/descending order
- **Pagination Support:** Offset/limit with total count calculation
- **Search Functionality:** Case-insensitive partial matching
- **Performance Optimization:** Subquery-based counting for efficiency

**Filter Categories:**

- **Exact Filters:** Direct field matching
- **Partial Filters:** ILIKE pattern matching for fuzzy search
- **Combined Search:** OR-based search across multiple fields
- **Date Range Filters:** Created date boundary filtering

### 3. Bulk Operations

#### bulk_create_users Function

```python
async def bulk_create_users(
    session: AsyncSession, users: Sequence[User]
) -> Sequence[User]:
    """Bulk create users and return them with IDs."""
    session.add_all(users)
    try:
        await session.commit()
        for user in users:
            await session.refresh(user)
    except Exception as exc:
        await session.rollback()
        raise exc
    return users
```

**Purpose:** Efficiently creates multiple users in a single transaction with proper error handling.

**Key Features:**

- **Batch Processing:** Single transaction for multiple users
- **ID Population:** Refreshes objects to get generated IDs
- **Transaction Safety:** Rollback on any failure
- **Performance Optimization:** Reduces database round trips

#### bulk_update_users Function

```python
async def bulk_update_users(
    session: AsyncSession, user_ids: Sequence[int], update_data: Mapping[str, object]
) -> int:
    """Bulk update users by IDs with the given update_data dict."""
    if not user_ids or not update_data:
        return 0

    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    users: Sequence[User] = result.scalars().all()

    for user in users:
        for key, value in update_data.items():
            setattr(user, key, value)

    try:
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise exc

    return len(users)
```

**Purpose:** Updates multiple users with common field changes in a single transaction.

**Key Features:**

- **Flexible Updates:** Dynamic field updates using setattr
- **Batch Processing:** Multiple user updates in single transaction
- **Return Count:** Returns number of successfully updated users
- **Validation:** Early return for empty inputs

### 4. Rate Limiting and Security

#### Rate Limiter Configuration

```python
user_action_limiter: Final[AsyncRateLimiter[Any]] = AsyncRateLimiter(
    max_calls=5, period=60.0
)
```

#### sensitive_user_action Function

```python
async def sensitive_user_action(
    session: AsyncSession, user_id: int, action: str
) -> None:
    """Example of a rate-limited sensitive action."""
    user: User | None = await get_user_by_id(session, user_id)
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found.")

    limiter_key: Final[str] = f"user:{user_id}:{action}"
    allowed: bool = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        raise RateLimitExceededError(
            f"Too many {action} attempts. Please try again later."
        )
    # ... perform the action ...
```

**Purpose:** Implements rate limiting for sensitive user operations to prevent abuse.

**Key Features:**

- **User-Specific Limiting:** Individual rate limits per user
- **Action-Specific Keys:** Different limits for different actions
- **Security Protection:** Prevents brute force and abuse
- **Clear Error Messages:** Informative rate limit exceeded messages

**Rate Limiting Strategy:**

- 5 calls per 60-second window per user per action
- Key format: `user:{user_id}:{action}`
- Async rate limiter for non-blocking operations

### 5. User Lifecycle Management

#### User Status Management

```python
async def deactivate_user(session: AsyncSession, user_id: int) -> bool:
    """Deactivate a user (set is_active=False)."""
    user: User | None = await get_user_by_id(session, user_id)
    if user is None or not getattr(user, "is_active", False):
        return False

    user.is_active = False
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit deactivate for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True
```

#### Soft Deletion

```python
async def soft_delete_user(session: AsyncSession, user_id: int) -> bool:
    """Mark a user as deleted (soft delete)."""
    user: User | None = await get_user_by_id(session, user_id)
    if user is None or getattr(user, "is_deleted", False):
        return False

    user.is_deleted = True
    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit soft delete for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True
```

#### GDPR Compliance - User Anonymization

```python
async def anonymize_user(session: AsyncSession, user_id: int) -> bool:
    """Anonymize user data for privacy/GDPR compliance."""
    user: User | None = await get_user_by_id(session, user_id, use_cache=False)
    if user is None or getattr(user, "is_deleted", False):
        return False

    user.email = f"anon_{user.id}_{int(datetime.now(UTC).timestamp())}@anon.invalid"
    user.hashed_password = ""
    user.is_active = False
    user.is_deleted = True
    user.last_login_at = None

    try:
        await session.commit()
    except Exception as exc:
        logging.error(f"Failed to commit anonymize for user {user_id}: {exc}")
        await session.rollback()
        raise exc
    return True
```

**Purpose:** Implements GDPR-compliant user data anonymization for privacy protection.

**Key Features:**

- **Irreversible Anonymization:** Replaces PII with non-recoverable data
- **Timestamp-Based Anonymization:** Unique anonymous identifiers
- **Complete Deactivation:** Disables account and clears sensitive data
- **Cache Bypass:** Ensures fresh data during anonymization
- **Compliance Ready:** Meets GDPR right to be forgotten requirements

### 6. Data Export and Import

#### CSV Export

```python
async def export_users_to_csv(session: AsyncSession) -> str:
    """Export all users to CSV string."""
    result = await session.execute(select(User))
    users: Sequence[User] = result.scalars().all()

    output: io.StringIO = io.StringIO()
    writer: csv.DictWriter[str] = csv.DictWriter(
        output,
        fieldnames=["id", "email", "is_active", "is_deleted", "created_at", "updated_at", "last_login_at"]
    )
    writer.writeheader()

    for user in users:
        row: UserCSVRow = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at,
        }
        writer.writerow(row)

    return output.getvalue()
```

#### JSON Export

```python
async def export_users_to_json(session: AsyncSession) -> str:
    """Export all users to JSON string."""
    result = await session.execute(select(User))
    users: Sequence[User] = result.scalars().all()

    data: list[UserJSONRow] = [
        {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        for user in users
    ]

    return json.dumps(data)
```

**Purpose:** Provides data export functionality for backup, migration, and compliance purposes.

**Key Features:**

- **Multiple Formats:** Both CSV and JSON export support
- **Complete Data Export:** All relevant user fields included
- **Date Handling:** Proper ISO format for JSON dates
- **Type Safety:** TypedDict definitions for export formats
- **Memory Efficient:** String-based output suitable for large datasets

### 7. Analytics and Reporting

#### User Signup Analytics

```python
async def user_signups_per_month(session: AsyncSession, year: int) -> dict[int, int]:
    """Return a dict of {month: signup_count} for the given year (1-12)."""
    stmt = (
        select(extract("month", User.created_at).label("month"), func.count(User.id))
        .where(extract("year", User.created_at) == year)
        .group_by("month")
        .order_by("month")
    )

    result = await session.execute(stmt)
    rows: Sequence[Row[Any]] = result.all()

    stats: dict[int, int] = dict.fromkeys(range(1, 13), 0)
    for row in rows:
        month: int = int(row[0])
        count: int = int(row[1])
        stats[month] = count

    return stats
```

**Purpose:** Provides monthly user signup analytics for business intelligence and growth tracking.

**Key Features:**

- **Monthly Aggregation:** Groups signups by month for specific year
- **Complete Coverage:** Returns all 12 months with zero-filling
- **SQL Optimization:** Uses database-level aggregation for performance
- **Type Safety:** Proper type conversion for extracted values

### 8. Context Managers and Session Management

#### Database Session Context

```python
@asynccontextmanager
async def db_session_context() -> AsyncIterator[AsyncSession]:
    """Async context manager for DB session."""
    from src.core.database import get_async_session

    async with get_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### Transaction Context

```python
@asynccontextmanager
async def db_transaction(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """Async context manager for DB transaction (atomic operations)."""
    async with session.begin():
        yield session
```

**Purpose:** Provides context managers for proper session and transaction management.

**Key Features:**

- **Resource Management:** Automatic session cleanup
- **Transaction Safety:** Atomic operations with automatic rollback
- **Async Context Managers:** Proper async/await patterns
- **Exception Safety:** Guaranteed cleanup even on exceptions

## Type Safety and Data Structures

### TypedDict Definitions

```python
class UserUpdateData(TypedDict, total=False):
    email: str
    name: str
    is_active: bool
    is_deleted: bool
    hashed_password: str
    last_login_at: datetime | None
    updated_at: datetime | None

class UserCSVRow(TypedDict):
    id: int
    email: str
    is_active: bool
    is_deleted: bool
    created_at: object
    updated_at: object
    last_login_at: object

class UserJSONRow(TypedDict):
    id: int
    email: str
    is_active: bool
    is_deleted: bool
    created_at: str | None
    updated_at: str | None
    last_login_at: str | None
```

**Purpose:** Provides type safety for data structures used in user operations.

**Key Features:**

- **Type Safety:** Compile-time type checking for data structures
- **Partial Updates:** `total=False` for optional update fields
- **Export Formats:** Specific types for CSV and JSON export
- **Documentation:** Self-documenting field types and requirements

## Error Handling Patterns

### Custom Exception Usage

```python
# Validation errors
if not validate_email(email):
    raise ValidationError("Invalid email format.")

# Resource not found
if user is None:
    raise UserNotFoundError(f"User with id {user_id} not found.")

# Conflict detection
if not is_unique:
    raise UserAlreadyExistsError("Email already exists.")

# Rate limiting
if not allowed:
    raise RateLimitExceededError("Too many attempts. Please try again later.")
```

### Transaction Error Handling

```python
try:
    await session.commit()
    await session.refresh(user)
except Exception as exc:
    logging.error(f"Database operation failed: {exc}")
    await session.rollback()
    raise exc
```

**Purpose:** Implements comprehensive error handling with specific exception types and recovery strategies.

**Key Features:**

- **Specific Exceptions:** Custom exception types for different error conditions
- **Transaction Safety:** Automatic rollback on database errors
- **Comprehensive Logging:** Error details with context information
- **Exception Propagation:** Proper re-raising after cleanup

## Performance Optimization Strategies

### Caching Integration

```python
# Cache-first strategy
cache_key = f"user_id:{user_id}"
cached_data = await user_cache.get(cache_key)
if cached_data:
    return await session.execute(select(User).where(User.id == cached_data))

# Cache population
if user and use_cache:
    await user_cache.set(cache_key, user.id, ttl=60)
```

### Bulk Operations

```python
# Efficient bulk operations
session.add_all(users)  # Single transaction for multiple objects
await session.commit()  # Single commit for all changes

# Batch querying
stmt = select(User).where(User.id.in_(user_ids))  # IN clause for multiple IDs
```

### Query Optimization

```python
# Subquery for counting
count_stmt = select(func.count()).select_from(stmt.subquery())

# Efficient sorting with database-level operations
col = getattr(User, sort)
if order == "desc":
    col = col.desc()
stmt = stmt.order_by(col)
```

**Purpose:** Implements various performance optimization techniques for high-throughput user operations.

**Key Features:**

- **Redis Caching:** Reduces database load for frequent operations
- **Bulk Processing:** Minimizes database round trips
- **Query Optimization:** Efficient SQL generation and execution
- **Connection Management:** Proper session and connection handling

## Security Considerations

### Rate Limiting

```python
user_action_limiter = AsyncRateLimiter(max_calls=5, period=60.0)
```

### Password Security

```python
from src.utils.hashing import hash_password
hashed = hash_password(password)  # Secure hashing
```

### Data Privacy

```python
# GDPR-compliant anonymization
user.email = f"anon_{user.id}_{timestamp}@anon.invalid"
user.hashed_password = ""
user.is_active = False
```

### Audit Logging

```python
async def audit_log_user_change(
    session: AsyncSession, user_id: int, action: str, details: str = ""
) -> None:
    """Log an audit event for user changes."""
    logger.info(f"User {user_id}: {action}. {details}")
```

**Purpose:** Implements comprehensive security measures for user data protection and compliance.

**Key Features:**

- **Rate Limiting:** Prevents abuse and brute force attacks
- **Secure Password Handling:** Proper hashing and storage
- **Data Privacy:** GDPR-compliant anonymization capabilities
- **Audit Trail:** Comprehensive logging for security monitoring

## Testing Patterns

### Unit Testing Example

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_user_by_id_cached():
    # Mock cache hit
    mock_cache = AsyncMock()
    mock_cache.get.return_value = 123

    with patch('src.repositories.user.user_cache', mock_cache):
        result = await get_user_by_id(mock_session, 123)

    mock_cache.get.assert_called_once_with("user_id:123")
    assert result is not None
```

### Integration Testing Example

```python
@pytest.mark.asyncio
async def test_create_user_workflow():
    async with db_session_context() as session:
        user = await create_user_with_validation(
            session,
            "test@example.com",
            "SecurePassword123!",
            "Test User"
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True

        # Verify user can be retrieved
        retrieved = await get_user_by_id(session, user.id)
        assert retrieved.email == user.email
```

## Migration and Upgrade Paths

### From Synchronous Operations

```python
# Old synchronous pattern
def old_get_user(session, user_id):
    return session.query(User).filter(User.id == user_id).first()

# New async pattern
async def new_get_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### Cache Integration Migration

```python
# Add caching to existing functions
async def enhanced_get_user(session: AsyncSession, user_id: int, use_cache: bool = True):
    if use_cache:
        cached = await user_cache.get(f"user_id:{user_id}")
        if cached:
            return await get_user_from_cache(session, cached)

    return await get_user_from_database(session, user_id)
```

## Related Modules

- **`src.models.user.User`** - User ORM model definition
- **`src.utils.cache`** - Redis caching utilities
- **`src.utils.errors`** - Custom exception definitions
- **`src.utils.validation`** - Email and password validation
- **`src.utils.hashing`** - Password hashing utilities
- **`src.core.database`** - Database session management
- **`src.api.users`** - User API endpoints using repository functions

## Configuration Dependencies

- Redis cache configuration for user caching
- Database connection settings for async operations
- Rate limiting configuration for security
- Logging configuration for audit trails

## Summary

The `user.py` repository module provides a comprehensive, production-ready data access layer for user management with extensive functionality covering all aspects of user lifecycle management, from creation and validation through analytics and compliance. The module emphasizes security, performance, and maintainability through proper error handling, caching strategies, rate limiting, and comprehensive logging.

Key strengths include robust validation and error handling, performance optimization through caching and bulk operations, comprehensive security measures including rate limiting and GDPR compliance, flexible querying and filtering capabilities, and extensive analytics and reporting functions. The module serves as a model for repository pattern implementation in modern async Python applications.
