# Database Layer Implementation

This document provides a comprehensive overview of the database layer implementation in ReViewPoint, covering architecture, design patterns, testing strategies, and operational considerations.

## Architecture Overview

ReViewPoint implements a robust, scalable database layer using SQLAlchemy's async ORM with support for multiple database backends. The architecture follows industry best practices with clear separation of concerns and comprehensive testing coverage.

### Technology Stack

- **ORM**: SQLAlchemy 2.0+ with async support
- **Primary Database**: PostgreSQL (production)
- **Development/Testing**: SQLite with async support
- **Migration Tool**: Alembic for schema version control
- **Connection Pool**: Configurable async connection pooling
- **Type Safety**: Full type annotations and Pydantic integration

### Core Design Principles

1. **Async-First Architecture**: All database operations are non-blocking
2. **Repository Pattern**: Clean separation between data access and business logic
3. **Environment Awareness**: Different configurations for development, testing, and production
4. **Comprehensive Testing**: Over 86% test coverage with isolated test environments
5. **Type Safety**: Strong typing throughout the data layer
6. **Observability**: Built-in health checks and monitoring capabilities

1. **Core Database Module**: Connection management, session factories, and health checks
2. **Base Model**: Common fields and methods for all models
3. **Entity Models**: Application-specific models like User and File
4. **Migrations**: Schema version control using Alembic

## Key Components

### Database Connection Management

The `backend/core/database.py` module handles:

- Async database engine configuration
- Connection pooling (sized appropriately for environment)
- Session management through context managers
- Error handling and transaction management

Configuration is environment-aware, with different settings for development, testing, and production environments.

### Model Structure

All models inherit from a common `Base` class (`backend/models/base.py`) that provides:

- Standard ID field
- Automatic timestamps (created_at, updated_at)
- Serialization methods

### Entity Models

Currently implemented models:

- **User**: Authentication and user management (`backend/models/user.py`)
- **File**: Document metadata for uploaded files (`backend/models/file.py`)

### Schema Management

Database schema migrations are handled by Alembic:

- `alembic_migrations/env.py`: Configuration linking SQLAlchemy models to migrations
- `alembic_migrations/versions/`: Version-controlled migration scripts

The initial migration (`9fc3acc47815_initial_migration_users_and_files_tables.py`) establishes the core schema:

1. **Users table**: For authentication and user management
   - Primary fields: email, hashed_password, is_active
   - Standard fields: id, created_at, updated_at
   - Indexes: Unique index on email
2. **Files table**: For document metadata tracking
   - Primary fields: filename, content_type, user_id
   - Relationship: Foreign key to users.id
   - Indexes: Index on user_id for filtering by user

Migration commands:

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Roll back the most recent migration
alembic downgrade -1
```

## Testing Strategy

The database layer is tested comprehensively with over 86% coverage:

1. **Connection Tests**:

   - Verify database connectivity and health checks
   - Test both successful and failed connection scenarios
   - Exercise the database engine with real queries

2. **Session Tests**:

   - Ensure proper session management and error handling
   - Test session lifecycle (creation, use, closure)
   - Test error scenarios and automatic rollback
   - Verify session context manager behavior

3. **Model Tests**:
   - Test CRUD operations (Create, Read, Update, Delete)
   - Verify relationships between models
   - Test constraints and indexes
   - Test helper methods like to_dict() and **repr**()

### Test Fixtures Architecture

Test fixtures in `tests/conftest.py` provide:

- **Isolated in-memory databases**: Each test function gets a unique database
- **Multiple fixture scopes**:
  - `async_engine`: Session-scoped for shared access
  - `async_engine_function`: Function-scoped for isolation
  - `async_session`: For direct database access in tests
- **Automatic environment configuration**: Environment variables set consistently
- **Automated cleanup**: Test databases are disposed after use

### Test Implementation Pattern

Our tests follow a consistent pattern:

```python
@pytest.mark.asyncio
async def test_example(async_session):
    # 1. Setup - Create test data
    item = Item(name="test")
    async_session.add(item)
    await async_session.commit()

    # 2. Execute - Perform the operation being tested
    result = await async_session.execute(select(Item).where(Item.name == "test"))
    found = result.scalar_one()

    # 3. Verify - Check the results
    assert found.name == "test"

    # 4. Cleanup (handled automatically by fixture)
```

## Environment Configuration

The database connection is configured through environment variables:

| Variable                  | Description                 | Default                        |
| ------------------------- | --------------------------- | ------------------------------ |
| `REVIEWPOINT_DB_URL`      | Database connection string  | `postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint` |
| `REVIEWPOINT_ENVIRONMENT` | Environment (dev/test/prod) | `dev`                          |
| `REVIEWPOINT_DEBUG`       | Enable debug mode           | `false`                        |

Connection URL formats:

- SQLite: `sqlite+aiosqlite:///./backend_dev.db`
- PostgreSQL: `postgresql+asyncpg://user:pass@localhost:5432/dbname`

Environment-specific configurations:

- **Production**: Larger connection pool (size=10, max_overflow=20)
- **Development**: Smaller connection pool (size=5, max_overflow=10)
- **Testing**: In-memory SQLite database, no pooling

## Design Decisions

1. **Async First**: All database operations are async to prevent blocking I/O
2. **Repository Pattern**: Future implementation will use repositories to encapsulate data access logic
3. **Session Management**: Sessions are provided through dependency injection
4. **Error Handling**: Comprehensive error catching and logging
5. **Environment Awareness**: Different configurations for dev, test, and prod
6. **Type Safety**: Comprehensive type annotations for better IDE support and safety

## Usage Examples

### Database Session in FastAPI Endpoint

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_session

@router.get("/items")
async def get_items(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Item))
    items = result.scalars().all()
    return items
```

### Health Check Integration

```python
from backend.core.database import db_healthcheck

@router.get("/health")
async def health():
    db_status = await db_healthcheck()
    return {"database": "healthy" if db_status else "unhealthy"}
```

## Future Enhancements

1. Connection pooling metrics and monitoring
2. More sophisticated retry logic for transient errors
3. Read/write splitting for high-traffic applications
4. Additional models for application features
5. Comprehensive repository layer implementation
