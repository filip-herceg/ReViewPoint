# Synchronous Database Module

**File:** `backend/src/core/sync_database.py`  
**Purpose:** Synchronous SQLAlchemy session management for blocking database operations  
**Lines of Code:** 53  
**Type:** Core Infrastructure Module

## Overview

The sync_database module provides synchronous SQLAlchemy session management for scenarios where blocking database operations are required or preferred. While the main application uses async database operations through `database.py`, this module enables synchronous database access for specific use cases such as database migrations, administrative scripts, testing utilities, and integration with synchronous third-party libraries. It ensures proper session lifecycle management with automatic cleanup and validates engine compatibility.

## Architecture

### Core Design Principles

1. **Engine Compatibility**: Validates that synchronous sessions are only created with synchronous engines
2. **Session Lifecycle Management**: Automatic session creation, yielding, and cleanup
3. **Resource Safety**: Guaranteed session closure even in case of exceptions
4. **Type Safety**: Full type annotations for session factory and session objects
5. **Error Handling**: Clear error messages for engine misconfigurations
6. **Separation of Concerns**: Focused on synchronous operations without async complexity

### Key Components

#### Engine Validation System

```python
def _validate_sync_engine(engine: Engine | AsyncEngine | None) -> Engine:
    """Helper function to validate and return a sync engine."""
```

**Validation Process:**

- Checks for engine existence (not None)
- Validates engine type (must be synchronous Engine, not AsyncEngine)
- Provides clear error messages for misconfigurations
- Returns validated synchronous engine

#### Session Factory Management

```python
def get_sync_session_factory() -> sessionmaker[Session]:
    """Returns a sessionmaker for synchronous SQLAlchemy engines."""
```

**Factory Features:**

- Creates sessionmaker bound to validated synchronous engine
- Ensures proper session configuration
- Type-safe session factory creation
- Integration with existing engine from `database.py`

## Core Functions

### 🔧 **Engine Validation Function**

#### `_validate_sync_engine()`

```python
def _validate_sync_engine(engine: Engine | AsyncEngine | None) -> Engine:
    """Helper function to validate and return a sync engine."""
```

**Purpose:** Ensures engine compatibility for synchronous operations

**Validation Logic:**

1. **Null Check**: Verifies engine is not None
2. **Type Validation**: Confirms engine is synchronous (not AsyncEngine)
3. **Error Reporting**: Provides clear guidance for misconfigurations
4. **Type Return**: Returns validated Engine with proper typing

**Error Scenarios:**

```python
# No engine configured
if engine is None:
    raise RuntimeError("No SQLAlchemy engine is configured.")

# Async engine provided for sync operations
if isinstance(engine, AsyncEngine):
    raise RuntimeError(
        "Synchronous session requested, but engine is an AsyncEngine. "
        "Use async session for AsyncEngine."
    )
```

**Benefits:**

- Prevents runtime errors from engine type mismatches
- Clear error messages for debugging
- Type safety for downstream session operations

### 🏭 **Session Factory Function**

#### `get_sync_session_factory()`

```python
def get_sync_session_factory() -> sessionmaker[Session]:
    """Returns a sessionmaker for synchronous SQLAlchemy engines."""
```

**Purpose:** Creates a configured sessionmaker for synchronous database operations

**Factory Creation Process:**

1. **Engine Import**: Gets engine from `database.py` module
2. **Engine Validation**: Validates engine compatibility for sync operations
3. **SessionMaker Creation**: Creates sessionmaker bound to validated engine
4. **Type Return**: Returns properly typed sessionmaker

**Usage Integration:**

```python
from src.core.sync_database import get_sync_session_factory

SessionLocal = get_sync_session_factory()
db_session = SessionLocal()
```

**Configuration Features:**

- Automatic binding to existing database engine
- Type-safe session creation
- Consistent configuration with async sessions
- No additional configuration required

### 📦 **Session Context Manager**

#### `get_session()`

```python
def get_session() -> Generator[Session, None, None]:
    """Yields a SQLAlchemy Session object. Closes the session after use."""
```

**Purpose:** Provides a context-managed database session with automatic cleanup

**Session Lifecycle:**

1. **Factory Creation**: Gets sessionmaker from validated engine
2. **Session Creation**: Creates new session instance
3. **Session Yielding**: Provides session to calling code
4. **Automatic Cleanup**: Ensures session closure in finally block
5. **Exception Propagation**: Allows exceptions to bubble up while ensuring cleanup

**Context Management:**

```python
try:
    yield db  # Provide session to calling code
finally:
    db.close()  # Always close session, even on exceptions
```

**Usage Pattern:**

```python
from src.core.sync_database import get_session

# Automatic session management
for db in get_session():
    # Perform database operations
    user = db.query(User).filter(User.email == "test@example.com").first()
    # Session automatically closed when exiting context
```

## Usage Patterns

### 🔧 **Database Migration Scripts**

```python
from src.core.sync_database import get_session
from src.models.user import User

def migrate_user_data():
    """Example migration script using synchronous database access."""
    for db in get_session():
        # Perform bulk operations
        users = db.query(User).filter(User.legacy_field.is_(None)).all()

        for user in users:
            user.legacy_field = "migrated"
            db.add(user)

        db.commit()
        print(f"Migrated {len(users)} users")

# Run migration
if __name__ == "__main__":
    migrate_user_data()
```

### 🧪 **Testing Utilities**

```python
from src.core.sync_database import get_session
from src.models.user import User

def create_test_user(email: str, name: str) -> User:
    """Create a test user using synchronous database access."""
    for db in get_session():
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

def cleanup_test_data():
    """Clean up test data using synchronous operations."""
    for db in get_session():
        db.query(User).filter(User.email.like("%test%")).delete()
        db.commit()

# Test usage
def test_user_operations():
    user = create_test_user("test@example.com", "Test User")
    assert user.id is not None

    cleanup_test_data()
```

### 📊 **Administrative Scripts**

```python
from src.core.sync_database import get_session
from src.models.user import User
from src.models.file import File

def generate_usage_report():
    """Generate usage statistics using synchronous database queries."""
    for db in get_session():
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()

        # File statistics
        total_files = db.query(File).count()
        total_size = db.query(db.func.sum(File.size)).scalar() or 0

        print(f"Usage Report:")
        print(f"Total Users: {total_users}")
        print(f"Active Users: {active_users}")
        print(f"Total Files: {total_files}")
        print(f"Total Storage: {total_size / (1024*1024):.2f} MB")

# Run report
if __name__ == "__main__":
    generate_usage_report()
```

### 🔄 **Synchronous Library Integration**

```python
from src.core.sync_database import get_session
from src.models.user import User
import pandas as pd

def export_users_to_dataframe() -> pd.DataFrame:
    """Export user data to pandas DataFrame using synchronous database access."""
    for db in get_session():
        # Execute synchronous query
        users = db.query(User).all()

        # Convert to DataFrame
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'created_at': user.created_at,
                'is_active': user.is_active
            })

        return pd.DataFrame(data)

# Usage with synchronous libraries
df = export_users_to_dataframe()
df.to_csv("users_export.csv", index=False)
```

## Error Handling and Edge Cases

### 🛠️ **Engine Configuration Errors**

#### No Engine Configured

```python
# Error scenario
RuntimeError: No SQLAlchemy engine is configured.
```

**Resolution:**

- Ensure `database.py` module is properly initialized
- Verify environment configuration includes database URL
- Check application startup sequence

#### Async Engine Mismatch

```python
# Error scenario
RuntimeError: Synchronous session requested, but engine is an AsyncEngine.
Use async session for AsyncEngine.
```

**Resolution:**

- Use async sessions from `database.py` for async operations
- Configure synchronous engine if sync operations are required
- Review application architecture for operation type consistency

### 🔄 **Session Management Errors**

#### Session Creation Failures

```python
for db in get_session():
    try:
        # Database operations
        result = db.query(User).all()
    except Exception as e:
        # Session is automatically closed in finally block
        logger.error(f"Database operation failed: {e}")
        raise
```

**Error Handling Features:**

- Automatic session cleanup even on exceptions
- Exception propagation for proper error handling
- Resource leak prevention through guaranteed cleanup

#### Connection Pool Exhaustion

```python
# Proper usage to prevent connection leaks
def bulk_operation():
    """Proper session management for bulk operations."""
    for db in get_session():
        # Batch operations to minimize session duration
        batch_size = 100
        users = db.query(User).limit(batch_size).all()

        for user in users:
            # Process user
            pass

        db.commit()
    # Session automatically closed here
```

## Performance Considerations

### ⚡ **Session Lifecycle Optimization**

#### Short-Lived Sessions

```python
def efficient_data_access():
    """Use short-lived sessions for optimal performance."""
    # Create session only when needed
    for db in get_session():
        # Minimize session duration
        data = db.query(User).filter(User.is_active == True).all()
        # Process data quickly
        return [user.to_dict() for user in data]
    # Session closed immediately after use
```

#### Batch Operations

```python
def efficient_bulk_insert(user_data_list):
    """Efficient bulk operations with session management."""
    for db in get_session():
        # Use bulk operations for better performance
        db.bulk_insert_mappings(User, user_data_list)
        db.commit()
    # Single session for entire bulk operation
```

### 🔄 **Connection Pool Management**

#### Pool Configuration Awareness

```python
def pool_aware_operations():
    """Operations that consider connection pool limits."""
    # Avoid creating multiple concurrent sessions
    for db in get_session():
        # Perform all related operations in single session
        users = db.query(User).all()
        files = db.query(File).all()

        # Process data
        results = process_data(users, files)
        return results
    # Single connection used for all operations
```

## Testing Strategies

### 🧪 **Module Testing**

```python
import pytest
from unittest.mock import patch, MagicMock
from src.core.sync_database import get_sync_session_factory, get_session, _validate_sync_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

def test_validate_sync_engine_success():
    """Test successful sync engine validation."""
    engine = create_engine("sqlite:///:memory:")
    result = _validate_sync_engine(engine)
    assert result is engine

def test_validate_sync_engine_none():
    """Test validation with None engine."""
    with pytest.raises(RuntimeError, match="No SQLAlchemy engine is configured"):
        _validate_sync_engine(None)

def test_validate_sync_engine_async():
    """Test validation with async engine."""
    async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    with pytest.raises(RuntimeError, match="Synchronous session requested"):
        _validate_sync_engine(async_engine)

def test_get_sync_session_factory():
    """Test session factory creation."""
    with patch('src.core.database.engine') as mock_engine:
        mock_engine.return_value = create_engine("sqlite:///:memory:")
        factory = get_sync_session_factory()
        assert factory is not None

def test_get_session_context_manager():
    """Test session context manager."""
    with patch('src.core.database.engine') as mock_engine:
        mock_engine.return_value = create_engine("sqlite:///:memory:")

        sessions_created = []
        for db in get_session():
            sessions_created.append(db)
            assert db is not None

        assert len(sessions_created) == 1
        # Session should be closed after context
```

### 🔄 **Integration Testing**

```python
def test_session_lifecycle():
    """Test complete session lifecycle."""
    session_closed = False

    class MockSession:
        def close(self):
            nonlocal session_closed
            session_closed = True

    with patch('src.core.sync_database.get_sync_session_factory') as mock_factory:
        mock_factory.return_value = lambda: MockSession()

        try:
            for db in get_session():
                assert isinstance(db, MockSession)
                raise Exception("Test exception")
        except Exception:
            pass

        # Session should be closed even after exception
        assert session_closed

def test_multiple_session_usage():
    """Test multiple session operations."""
    with patch('src.core.database.engine') as mock_engine:
        mock_engine.return_value = create_engine("sqlite:///:memory:")

        # Each call should create a new session
        session_count = 0

        for db in get_session():
            session_count += 1

        for db in get_session():
            session_count += 1

        assert session_count == 2
```

## Best Practices

### ✅ **Do's**

- **Use Context Manager**: Always use `get_session()` for automatic cleanup
- **Keep Sessions Short**: Minimize session duration for better performance
- **Handle Exceptions**: Properly handle database exceptions in calling code
- **Batch Operations**: Use single session for related database operations
- **Validate Engine**: Ensure synchronous engine is configured before use
- **Test Session Management**: Test both success and failure scenarios

### ❌ **Don'ts**

- **Don't Mix Engine Types**: Don't use sync sessions with async engines
- **Don't Keep Sessions Open**: Avoid long-lived sessions that hold connections
- **Don't Ignore Exceptions**: Always handle database operation exceptions
- **Don't Create Multiple Sessions**: Use single session for related operations
- **Don't Skip Validation**: Always validate engine configuration
- **Don't Leak Sessions**: Rely on context manager for session cleanup

## Comparison with Async Database Module

### 🔄 **Sync vs Async Database Access**

#### Synchronous Database Module (`sync_database.py`)

```python
# Synchronous operation
for db in get_session():
    user = db.query(User).filter(User.id == 1).first()
    return user
```

**Use Cases:**

- Database migrations and administrative scripts
- Integration with synchronous libraries (pandas, etc.)
- Testing utilities and fixtures
- Blocking operations where async is not beneficial

#### Asynchronous Database Module (`database.py`)

```python
# Asynchronous operation
async with get_db() as db:
    user = await db.get(User, 1)
    return user
```

**Use Cases:**

- Web API endpoints and request handling
- High-concurrency operations
- Real-time features and WebSocket connections
- Main application business logic

### 📊 **Feature Comparison**

| Feature                | Sync Database       | Async Database           |
| ---------------------- | ------------------- | ------------------------ |
| **Concurrency**        | Blocking operations | Non-blocking operations  |
| **Performance**        | Lower concurrency   | Higher concurrency       |
| **Complexity**         | Simpler syntax      | More complex syntax      |
| **Use Cases**          | Scripts, migrations | Web APIs, real-time      |
| **Session Management** | Context manager     | Async context manager    |
| **Error Handling**     | Standard exceptions | Async exception handling |

## Related Files

- **`database.py`** - Main async database module (provides engine for sync operations)
- **`models/`** - SQLAlchemy models used with both sync and async sessions
- **Migration scripts** - Administrative scripts using sync database access
- **Testing utilities** - Test fixtures and utilities using sync sessions
- **Admin scripts** - Management scripts requiring blocking database operations

## Dependencies

- **`sqlalchemy`** - Core ORM and database abstraction layer
- **`sqlalchemy.orm`** - Session management and query capabilities
- **`sqlalchemy.engine`** - Engine types and database connection management

---

_This module provides essential synchronous database access for scenarios requiring blocking database operations while maintaining proper session lifecycle management and resource cleanup. It complements the main async database module for comprehensive database access patterns._
