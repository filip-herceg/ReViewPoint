# User Repository Documentation

## Purpose

The `user.py` repository module provides comprehensive data access layer functionality for user management operations in the ReViewPoint application. This repository implements the Repository pattern to abstract database operations, providing a clean interface between the service layer and the data persistence layer with advanced features including caching, rate limiting, bulk operations, and audit logging.

## Architecture

The repository follows a layered data access pattern with multiple concerns:

- **Data Access Layer**: SQLAlchemy async ORM operations
- **Caching Layer**: Async caching with TTL for performance optimization
- **Rate Limiting Layer**: Protection against abuse with async rate limiters
- **Validation Layer**: Input validation and error handling
- **Audit Layer**: Comprehensive logging for compliance and monitoring
- **Transaction Management**: Context managers for atomic operations

## Core Functions

### User Retrieval Operations

#### `get_user_by_id(session, user_id, use_cache=True)`

Retrieves a user by ID with optional async caching for performance optimization.

```python
# Example usage
user = await get_user_by_id(session, user_id=123, use_cache=True)
if user:
    print(f"Found user: {user.email}")
```

**Caching Features:**

- Async cache with configurable TTL (60 seconds default)
- Cache key pattern: `user_id:{user_id}`
- Cache only stores user ID, not ORM instances
- Automatic cache invalidation and refresh

#### `safe_get_user_by_id(session, user_id)`

Retrieves a user by ID or raises `UserNotFoundError` for guaranteed non-null returns.

```python
# Example usage
try:
    user = await safe_get_user_by_id(session, user_id=123)
    # user is guaranteed to exist
except UserNotFoundError:
    # Handle user not found
    pass
```

#### `get_users_by_ids(session, user_ids)`

Efficiently retrieves multiple users by a list of IDs with batch processing.

```python
# Example usage
user_ids = [1, 2, 3, 4, 5]
users = await get_users_by_ids(session, user_ids)
print(f"Found {len(users)} users")
```

### User Creation and Validation

#### `create_user_with_validation(session, email, password, name=None)`

Creates a user with comprehensive validation and error handling.

```python
# Example usage
try:
    new_user = await create_user_with_validation(
        session=session,
        email="user@example.com",
        password="secure_password",
        name="John Doe"
    )
    print(f"User created with ID: {new_user.id}")
except ValidationError as e:
    print(f"Validation failed: {e}")
except UserAlreadyExistsError:
    print("User already exists")
```

**Validation Features:**

- Email format validation using `validate_email()`
- Password strength validation with `get_password_validation_error()`
- Email uniqueness checking with `is_email_unique()`
- Secure password hashing with bcrypt
- Comprehensive error handling and logging
- Automatic transaction rollback on failure

### Advanced Query Operations

#### `list_users(session, offset, limit, email, name, q, sort, order, created_after, created_before)`

Provides advanced user listing with filtering, searching, sorting, and pagination.

```python
# Example usage
users, total_count = await list_users(
    session=session,
    offset=0,
    limit=20,
    q="john",  # Search query
    sort="created_at",
    order="desc",
    created_after=datetime(2024, 1, 1),
    created_before=datetime(2024, 12, 31)
)
print(f"Found {len(users)} out of {total_count} total users")
```

**Query Features:**

- **Pagination**: Offset and limit support
- **Search**: Partial matching on email and name
- **Filtering**: Email, name, date range filters
- **Sorting**: Multiple sort fields with ascending/descending order
- **Performance**: Optimized queries with subquery counting

#### `search_users_by_name_or_email(session, query, offset, limit)`

Performs efficient text search across user email and name fields.

```python
# Example usage
search_results = await search_users_by_name_or_email(
    session=session,
    query="john.doe",
    offset=0,
    limit=10
)
```

### Rate-Limited Operations

#### `sensitive_user_action(session, user_id, action)`

Executes rate-limited sensitive actions with protection against abuse.

```python
# Example usage
try:
    await sensitive_user_action(session, user_id=123, action="password_reset")
except RateLimitExceededError:
    print("Rate limit exceeded, try again later")
```

**Rate Limiting Features:**

- Async rate limiter with 5 calls per 60 seconds per user
- Action-specific rate limiting keys
- Configurable limits and time windows
- Automatic cleanup of expired rate limit entries

### Bulk Operations

#### `bulk_create_users(session, users)`

Efficiently creates multiple users in a single database transaction.

```python
# Example usage
users = [
    User(email="user1@example.com", hashed_password="hash1"),
    User(email="user2@example.com", hashed_password="hash2"),
]
created_users = await bulk_create_users(session, users)
```

#### `bulk_update_users(session, user_ids, update_data)`

Updates multiple users with the same data in a single operation.

```python
# Example usage
updated_count = await bulk_update_users(
    session=session,
    user_ids=[1, 2, 3],
    update_data={"is_active": False}
)
print(f"Updated {updated_count} users")
```

#### `bulk_delete_users(session, user_ids)`

Deletes multiple users efficiently with transaction safety.

```python
# Example usage
deleted_count = await bulk_delete_users(session, user_ids=[1, 2, 3])
print(f"Deleted {deleted_count} users")
```

### User Lifecycle Management

#### `soft_delete_user(session, user_id)`

Marks a user as deleted without removing the record (GDPR compliance).

```python
# Example usage
success = await soft_delete_user(session, user_id=123)
if success:
    print("User soft deleted")
```

#### `restore_user(session, user_id)`

Restores a soft-deleted user account.

```python
# Example usage
success = await restore_user(session, user_id=123)
if success:
    print("User restored")
```

#### `deactivate_user(session, user_id)`

Deactivates a user account (sets `is_active=False`).

```python
# Example usage
success = await deactivate_user(session, user_id=123)
```

#### `reactivate_user(session, user_id)`

Reactivates a previously deactivated user account.

```python
# Example usage
success = await reactivate_user(session, user_id=123)
```

### Data Export and Import

#### `export_users_to_csv(session)`

Exports all users to CSV format for reporting and backup.

```python
# Example usage
csv_data = await export_users_to_csv(session)
with open("users_export.csv", "w") as f:
    f.write(csv_data)
```

#### `export_users_to_json(session)`

Exports all users to JSON format with proper datetime serialization.

```python
# Example usage
json_data = await export_users_to_json(session)
with open("users_export.json", "w") as f:
    f.write(json_data)
```

#### `import_users_from_dicts(session, user_dicts)`

Bulk imports users from dictionaries with validation.

```python
# Example usage
user_data = [
    {"email": "user1@example.com", "name": "User 1"},
    {"email": "user2@example.com", "name": "User 2"},
]
imported_users = await import_users_from_dicts(session, user_data)
```

### Advanced User Operations

#### `upsert_user(session, email, defaults)`

Insert or update a user based on email with merge logic.

```python
# Example usage
user = await upsert_user(
    session=session,
    email="user@example.com",
    defaults={"name": "Updated Name", "is_active": True}
)
```

#### `partial_update_user(session, user_id, update_data)`

Updates only specified fields for a user with selective updating.

```python
# Example usage
updated_user = await partial_update_user(
    session=session,
    user_id=123,
    update_data={"name": "New Name", "last_login_at": datetime.now()}
)
```

#### `anonymize_user(session, user_id)`

Anonymizes user data for GDPR compliance and privacy protection.

```python
# Example usage
success = await anonymize_user(session, user_id=123)
if success:
    print("User data anonymized")
```

**Anonymization Process:**

- Replaces email with anonymous format
- Clears password hash
- Deactivates and soft-deletes account
- Removes login timestamps
- Irreversible operation for privacy compliance

### Analytics and Reporting

#### `user_signups_per_month(session, year)`

Generates monthly signup statistics for a given year.

```python
# Example usage
stats = await user_signups_per_month(session, year=2024)
for month, count in stats.items():
    print(f"Month {month}: {count} signups")
```

#### `count_users(session, is_active=None)`

Counts users with optional filtering by active status.

```python
# Example usage
total_users = await count_users(session)
active_users = await count_users(session, is_active=True)
inactive_users = await count_users(session, is_active=False)
```

### Utility Functions

#### `user_exists(session, user_id)`

Efficiently checks if a user exists without loading full record.

```python
# Example usage
exists = await user_exists(session, user_id=123)
```

#### `is_email_unique(session, email, exclude_user_id=None)`

Validates email uniqueness with optional exclusion for updates.

```python
# Example usage
unique = await is_email_unique(session, "user@example.com", exclude_user_id=123)
```

#### `change_user_password(session, user_id, new_hashed_password)`

Updates user password with proper security handling.

```python
# Example usage
success = await change_user_password(session, user_id=123, new_hashed_password="hash")
```

#### `update_last_login(session, user_id, login_time=None)`

Updates the last login timestamp for user session tracking.

```python
# Example usage
success = await update_last_login(session, user_id=123)
```

## Context Managers

### Database Session Management

#### `db_session_context()`

Async context manager for database session lifecycle management.

```python
# Example usage
async with db_session_context() as session:
    user = await get_user_by_id(session, user_id=123)
    # Session automatically closed
```

#### `db_transaction(session)`

Async context manager for atomic transaction operations.

```python
# Example usage
async with db_transaction(session) as tx_session:
    await create_user_with_validation(tx_session, email, password)
    await audit_log_user_change(tx_session, user_id, "created")
    # Transaction automatically committed or rolled back
```

## Type Safety and Validation

### Type Definitions

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
```

### Error Handling

```python
# Common exception patterns
try:
    user = await create_user_with_validation(session, email, password)
except ValidationError as e:
    # Handle validation errors
    logger.warning(f"Validation error: {e}")
except UserAlreadyExistsError:
    # Handle duplicate user
    logger.warning(f"Duplicate user: {email}")
except Exception as e:
    # Handle database errors
    logger.error(f"Database error: {e}")
    await session.rollback()
```

## Performance Considerations

### Caching Strategy

- **User ID Caching**: Stores only user IDs to minimize memory usage
- **TTL Management**: 60-second cache expiration for data freshness
- **Cache Invalidation**: Automatic cache refresh on user updates
- **Performance Metrics**: Significant query reduction for frequently accessed users

### Query Optimization

- **Batch Operations**: Bulk operations for multiple users
- **Selective Loading**: Only load required fields
- **Index Usage**: Optimized queries for database indexes
- **Pagination**: Efficient offset/limit with count queries

### Rate Limiting

- **Async Implementation**: Non-blocking rate limit checks
- **Per-User Limits**: Individual user rate limiting
- **Action-Specific**: Different limits for different operations
- **Memory Efficient**: Automatic cleanup of expired entries

## Security Considerations

### Data Protection

- **Password Hashing**: Secure bcrypt hashing with configurable rounds
- **Email Validation**: Comprehensive email format validation
- **SQL Injection Prevention**: Parameterized queries throughout
- **Data Anonymization**: GDPR-compliant user data removal

### Access Control

- **Session Management**: Proper user session tracking
- **Audit Logging**: Comprehensive action logging
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Sanitization of all user inputs

## Testing Strategies

### Unit Testing

```python
async def test_create_user_with_validation():
    # Test successful user creation
    user = await create_user_with_validation(
        session, "test@example.com", "secure_password", "Test User"
    )
    assert user.email == "test@example.com"
    assert user.name == "Test User"
```

### Integration Testing

```python
async def test_user_lifecycle():
    # Test complete user lifecycle
    user = await create_user_with_validation(session, email, password)
    await deactivate_user(session, user.id)
    await reactivate_user(session, user.id)
    await soft_delete_user(session, user.id)
    await restore_user(session, user.id)
```

### Performance Testing

```python
async def test_bulk_operations():
    # Test bulk creation performance
    users = [User(email=f"user{i}@example.com") for i in range(1000)]
    start_time = time.time()
    created_users = await bulk_create_users(session, users)
    duration = time.time() - start_time
    assert len(created_users) == 1000
    assert duration < 5.0  # Should complete within 5 seconds
```

## Related Files

### Dependencies

- `src/models/user.py` - User SQLAlchemy model
- `src/utils/cache.py` - Async caching utilities
- `src/utils/rate_limit.py` - Rate limiting implementation
- `src/utils/validation.py` - Input validation functions
- `src/utils/errors.py` - Custom exception classes
- `src/utils/hashing.py` - Password hashing utilities

### Service Integration

- `src/services/user.py` - User business logic service
- `src/api/v1/users/` - User API endpoints
- `src/core/database.py` - Database session management

### Configuration

- `src/core/config.py` - Application configuration
- Cache TTL settings
- Rate limiting parameters
- Database connection settings

## Module Exports

```python
__all__ = [
    "safe_get_user_by_id",
    "create_user_with_validation",
    "sensitive_user_action",
    "anonymize_user",
    "user_signups_per_month",
    "UserNotFoundError",
    "select",
]
```

This user repository provides a comprehensive data access foundation for all user-related operations in the ReViewPoint application, ensuring data integrity, performance optimization, and security through well-designed repository patterns and proper database abstraction.
