# Repositories Package

## Overview

The `repositories` package serves as the data access layer for the ReViewPoint application, implementing the Repository pattern to provide a clean abstraction between the business logic and data persistence layers. This package contains all database interaction logic, organized by domain entities, and serves as the single source of truth for data access patterns throughout the application.

**Package Purpose:**

- Centralized data access layer implementation
- Repository pattern for clean architecture separation
- Domain-driven organization of data access logic
- Consistent interface for database operations across the application

## Package Structure

The repositories package is organized by domain entities, with each repository module handling data access for a specific domain:

```
repositories/
├── __init__.py                    # Package initialization (empty)
├── user.py                       # User data access operations
├── file.py                       # File metadata operations
└── blacklisted_token.py          # Token blacklist operations
```

## Repository Modules

### 1. User Repository (`user.py`)

**Purpose:** Comprehensive user data access layer with advanced functionality

**Key Features:**

- Complete CRUD operations with validation
- Advanced querying with filtering and pagination
- Bulk operations for efficiency
- Data export/import (CSV/JSON)
- User lifecycle management (activation, deactivation, soft deletion)
- Rate limiting integration
- Caching support for performance
- Analytics and reporting capabilities
- GDPR compliance (anonymization)

**Primary Functions:**

- `get_user_by_id()` - Retrieve user with caching
- `create_user_with_validation()` - Secure user creation
- `list_users()` - Advanced filtering and pagination
- `bulk_create_users()` - Efficient batch operations
- `anonymize_user()` - GDPR compliance
- `user_signups_per_month()` - Analytics

### 2. File Repository (`file.py`)

**Purpose:** File metadata management with security-focused operations

**Key Features:**

- File metadata CRUD operations
- User-scoped operations for security
- Bulk deletion with detailed tracking
- Advanced file listing with filtering
- Performance-optimized querying
- Comprehensive validation

**Primary Functions:**

- `get_file_by_filename()` - File retrieval by name
- `create_file()` - File metadata creation with validation
- `delete_file()` - Safe file deletion
- `bulk_delete_files()` - Batch deletion with ownership validation
- `list_files()` - Advanced filtering and pagination

### 3. Blacklisted Token Repository (`blacklisted_token.py`)

**Purpose:** JWT token blacklisting for authentication security

**Key Features:**

- Token blacklisting for logout/revocation
- Automatic expiration handling
- Timezone-aware operations
- Performance-optimized validation
- Security-focused design

**Primary Functions:**

- `blacklist_token()` - Add token to blacklist
- `is_token_blacklisted()` - Validate token status

## Repository Pattern Implementation

### Design Principles

The repositories in this package follow consistent design principles:

#### 1. Domain-Driven Organization

```python
# Each repository handles a specific domain
user.py          # User domain operations
file.py          # File domain operations
blacklisted_token.py  # Authentication token domain
```

#### 2. Async-First Design

```python
# All repository functions are async
async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
async def create_file(session: AsyncSession, filename: str, ...) -> File:
async def blacklist_token(session: AsyncSession, jti: str, ...) -> None:
```

#### 3. Session Injection Pattern

```python
# Sessions passed as first parameter
async def repository_function(session: AsyncSession, ...):
    # Database operations using injected session
```

#### 4. Transaction Control

```python
# Repositories don't commit - callers control transactions
session.add(entity)
# await session.commit()  # Caller responsibility
```

### Common Patterns

#### Error Handling

```python
# Consistent error handling across repositories
try:
    session.add(entity)
    await session.flush()  # or commit if appropriate
except Exception as exc:
    await session.rollback()
    raise exc
```

#### Validation

```python
# Input validation with custom exceptions
if not required_field:
    raise ValidationError("Field is required")
```

#### Return Types

```python
# Consistent return type patterns
async def get_entity(session, id) -> Entity | None:  # Optional entity
async def list_entities(session, ...) -> tuple[list[Entity], int]:  # Data + count
async def delete_entity(session, id) -> bool:  # Success indicator
```

## Integration Patterns

### With API Layer

```python
# API endpoints use repositories for data access
from src.repositories.user import get_user_by_id, create_user_with_validation

@app.post("/users")
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await create_user_with_validation(
        session,
        user_data.email,
        user_data.password
    )
    await session.commit()
    return user
```

### With Service Layer

```python
# Services orchestrate multiple repository operations
async def user_service_create_with_file(session: AsyncSession, user_data, file_data):
    # Create user
    user = await create_user_with_validation(session, user_data.email, user_data.password)

    # Create initial file
    file = await create_file(session, file_data.filename, file_data.content_type, user.id)

    # Commit both operations
    await session.commit()

    return user, file
```

### With Caching Layer

```python
# Repositories integrate with caching systems
async def get_user_by_id(session: AsyncSession, user_id: int, use_cache: bool = True):
    if use_cache:
        cached_data = await cache.get(f"user:{user_id}")
        if cached_data:
            return hydrate_from_cache(session, cached_data)

    # Fallback to database
    user = await fetch_from_database(session, user_id)

    if user and use_cache:
        await cache.set(f"user:{user_id}", user.id, ttl=60)

    return user
```

## Performance Considerations

### Query Optimization

```python
# Efficient querying patterns
stmt = select(User).where(User.id.in_(user_ids))  # Batch queries
count_stmt = select(func.count()).select_from(stmt.subquery())  # Subquery counting
```

### Bulk Operations

```python
# Batch processing for efficiency
session.add_all(entities)  # Bulk inserts
await session.commit()     # Single transaction
```

### Pagination Support

```python
# Consistent pagination pattern
async def list_entities(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 20,
    ...
) -> tuple[list[Entity], int]:
    # Query with pagination
    stmt = stmt.offset(offset).limit(limit)
    return entities, total_count
```

## Security Implementation

### User Ownership

```python
# All operations scoped to users where applicable
stmt = select(File).where(File.user_id == user_id)  # User can only access own files
```

### Input Validation

```python
# Comprehensive validation
if not validate_email(email):
    raise ValidationError("Invalid email format")
```

### Rate Limiting

```python
# Rate limiting for sensitive operations
limiter_key = f"user:{user_id}:{action}"
allowed = await rate_limiter.is_allowed(limiter_key)
if not allowed:
    raise RateLimitExceededError("Too many attempts")
```

## Testing Strategy

### Repository Testing

```python
# Test repository functions with real database
@pytest.mark.asyncio
async def test_user_repository():
    async with test_session() as session:
        user = await create_user_with_validation(session, "test@example.com", "password")
        await session.commit()

        retrieved = await get_user_by_id(session, user.id)
        assert retrieved.email == "test@example.com"
```

### Mock Testing

```python
# Test business logic with mocked repositories
@patch('src.repositories.user.get_user_by_id')
async def test_business_logic(mock_get_user):
    mock_get_user.return_value = User(id=1, email="test@example.com")
    result = await business_function()
    assert result.status == "success"
```

## Migration and Evolution

### Adding New Repositories

```python
# New domain repositories follow established patterns
# src/repositories/new_domain.py

async def get_entity_by_id(session: AsyncSession, entity_id: int) -> Entity | None:
    result = await session.execute(select(Entity).where(Entity.id == entity_id))
    return result.scalar_one_or_none()

async def create_entity(session: AsyncSession, data: dict) -> Entity:
    if not data.get('required_field'):
        raise ValidationError("Required field missing")

    entity = Entity(**data)
    session.add(entity)
    await session.flush()
    return entity
```

### Repository Enhancement

```python
# Enhance existing repositories with new functionality
async def enhanced_list_users(
    session: AsyncSession,
    # ... existing parameters ...
    new_filter: str | None = None  # New functionality
) -> tuple[list[User], int]:
    stmt = select(User)

    # ... existing filters ...

    # New filter logic
    if new_filter:
        stmt = stmt.where(User.new_field.ilike(f"%{new_filter}%"))

    # ... rest of implementation ...
```

## Related Modules

- **`src.models`** - ORM model definitions used by repositories
- **`src.core.database`** - Database session management and configuration
- **`src.utils.errors`** - Custom exception classes for validation and errors
- **`src.utils.cache`** - Caching utilities for performance optimization
- **`src.api`** - API endpoints that consume repository functions
- **`src.services`** - Business logic layer that orchestrates repository operations

## Configuration Dependencies

- Database connection configuration for session management
- Caching configuration for performance optimization
- Security configuration for validation and rate limiting
- Logging configuration for audit trails and debugging

## Summary

The repositories package implements a comprehensive data access layer following the Repository pattern, providing clean separation between business logic and data persistence. The package emphasizes consistency through common patterns, security through user-scoped operations and validation, performance through caching and query optimization, and maintainability through clear interfaces and comprehensive error handling.

The repositories serve as the foundation for all data operations in the ReViewPoint application, ensuring reliable, secure, and efficient access to persistent data while maintaining clean architecture principles and enabling easy testing and maintenance.
