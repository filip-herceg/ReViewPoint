# Base Model Documentation

## Purpose

The `base.py` module defines the foundational SQLAlchemy ORM base classes for the ReViewPoint application. This module provides the declarative base class and common model functionality that all database models inherit from, ensuring consistent database schema patterns, automatic timestamping, and standard utility methods across the entire data persistence layer.

## Architecture

The module follows a layered inheritance pattern for database models:

- **Declarative Base Layer**: `Base` - Pure SQLAlchemy declarative base
- **Common Model Layer**: `BaseModel` - Abstract base with shared fields and methods
- **Utility Layer**: Dictionary conversion and introspection methods
- **Type Safety Layer**: Proper typing annotations and Final declarations
- **Timestamp Management**: Automatic created_at and updated_at tracking

## Core Classes

### `Base`

Pure SQLAlchemy declarative base class for all ORM models.

```python
# Example usage - Model inheritance
class User(BaseModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # Inherits id, created_at, updated_at from BaseModel
```

**Key Features:**

- **Declarative Base**: Standard SQLAlchemy DeclarativeBase
- **No Additional Logic**: Clean separation of concerns
- **Type Foundation**: Provides basis for all model type checking
- **Import Safety**: Designed to avoid circular import issues

### `BaseModel`

Abstract base model with common fields and functionality for all application models.

```python
# Example model structure
class ExampleModel(BaseModel):
    __tablename__ = "example"
    name: Mapped[str] = mapped_column(String(100))
    # Automatically includes:
    # - id: Primary key
    # - created_at: Creation timestamp
    # - updated_at: Last modification timestamp
```

**Field Specifications:**

**Primary Key:**
- `id: Mapped[int]` - Auto-incrementing primary key (Integer, autoincrement=True)

**Timestamp Tracking:**
- `created_at: Mapped[datetime]` - Creation timestamp (DateTime with timezone, default=func.now())
- `updated_at: Mapped[datetime]` - Last update timestamp (DateTime with timezone, onupdate=func.now())

**Configuration:**
- `__abstract__ = True` - Prevents direct table creation
- `Final[bool]` typing for abstract declaration

## Core Functionality

### Automatic Timestamping

**Creation Tracking:**
```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    default=func.now(), 
    nullable=False
)
```

- **Timezone Aware**: All timestamps include timezone information
- **Automatic Default**: Set automatically on record creation
- **Database Level**: Uses `func.now()` for database-level timestamp generation
- **Non-nullable**: Ensures all records have creation timestamps

**Update Tracking:**
```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    default=func.now(), 
    onupdate=func.now(), 
    nullable=False
)
```

- **Automatic Updates**: Updates automatically on any record modification
- **Database Consistency**: Uses database functions for accurate timing
- **Audit Trail**: Provides complete modification history
- **Performance**: Minimal overhead with database-level updates

### Dictionary Conversion

**Complete Model Serialization:**
```python
def to_dict(self) -> Mapping[str, Any]:
    """Convert model instance to dictionary, including all mapped columns."""
    result: dict[str, Any] = {}
    for column in cast(Any, self.__table__).columns:
        value: Any = getattr(self, column.name, None)
        result[column.name] = value
    return result
```

**Key Features:**

- **Complete Coverage**: Includes all mapped columns automatically
- **Type Safety**: Proper typing with Mapping return type
- **Dynamic**: Works with any model that inherits from BaseModel
- **Error Handling**: Graceful handling of missing attributes
- **Introspection**: Uses SQLAlchemy table metadata for column discovery

## Usage Patterns

### Model Definition

```python
from src.models.base import BaseModel
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class User(BaseModel):
    """User model with automatic base functionality."""
    __tablename__ = "users"
    
    # Custom fields
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # BaseModel provides automatically:
    # - id: Primary key
    # - created_at: Creation timestamp
    # - updated_at: Modification timestamp
```

### Dictionary Conversion Usage

```python
# Create and convert model instance
user = User(email="user@example.com", is_active=True)
await session.add(user)
await session.commit()

# Convert to dictionary for API responses
user_dict = user.to_dict()
# Returns: {
#     'id': 1,
#     'email': 'user@example.com',
#     'is_active': True,
#     'created_at': datetime(2024, 7, 23, 14, 30, 0, tzinfo=UTC),
#     'updated_at': datetime(2024, 7, 23, 14, 30, 0, tzinfo=UTC)
# }

# Use in API responses
return {"user": user_dict}
```

### Timestamp Access Patterns

```python
# Accessing timestamp information
async def track_user_activity(user_id: int):
    user = await session.get(User, user_id)
    
    # Access creation time
    account_age = datetime.utcnow() - user.created_at
    
    # Access last modification
    last_modified = user.updated_at
    
    # Check if recently updated
    recently_updated = (datetime.utcnow() - user.updated_at).seconds < 3600
    
    return {
        "account_age_days": account_age.days,
        "last_modified": last_modified.isoformat(),
        "recently_updated": recently_updated
    }
```

### Inheritance Patterns

```python
# Simple model inheritance
class SimpleModel(BaseModel):
    __tablename__ = "simple"
    name: Mapped[str] = mapped_column(String(100))

# Complex model with relationships
class ComplexModel(BaseModel):
    __tablename__ = "complex"
    title: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Relationships work normally
    user: Mapped[User] = relationship("User", back_populates="complex_items")
```

## Database Integration

### Migration Compatibility

**Alembic Integration:**
```python
# Migrations automatically include base fields
def upgrade() -> None:
    op.create_table(
        'new_model',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        # Custom fields...
        sa.PrimaryKeyConstraint('id')
    )
```

### Index Optimization

**Automatic Indexing Considerations:**
```python
# Primary key automatically indexed
# Consider additional indexes for timestamps if needed
class AuditableModel(BaseModel):
    __tablename__ = "auditable"
    __table_args__ = (
        Index("ix_auditable_created_at", "created_at"),
        Index("ix_auditable_updated_at", "updated_at"),
    )
```

### Query Patterns

**Common Query Patterns:**
```python
# Query by creation time
recent_users = await session.execute(
    select(User).where(
        User.created_at >= datetime.utcnow() - timedelta(days=7)
    )
)

# Query by modification time
recently_updated = await session.execute(
    select(User).where(
        User.updated_at >= datetime.utcnow() - timedelta(hours=1)
    )
)

# Order by timestamps
latest_users = await session.execute(
    select(User).order_by(User.created_at.desc()).limit(10)
)
```

## Type Safety Features

### Type Annotations

**Comprehensive Typing:**
```python
from typing import Any, Final, cast
from collections.abc import Mapping

# Proper type annotations for all components
class BaseModel(Base):
    __abstract__: Final[bool] = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    def to_dict(self) -> Mapping[str, Any]:
        # Type-safe dictionary conversion
        pass
```

### Type Checking Compatibility

**MyPy Compatibility:**
- All fields properly typed with `Mapped[]`
- Return types specified for all methods
- Type casting used appropriately for SQLAlchemy introspection
- Final declarations for constants

**SQLAlchemy 2.0 Patterns:**
- Modern Mapped annotations
- Proper typing for database columns
- Type-safe relationship declarations

## Performance Considerations

### Memory Efficiency

**Optimized Base Class:**
- Minimal memory footprint with only essential fields
- Efficient datetime handling with database-level functions
- No unnecessary instance variables or methods
- Lazy evaluation of table introspection

### Database Performance

**Efficient Operations:**
```python
# Optimized timestamp handling
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    default=func.now(),  # Database-level default
    nullable=False
)
```

- **Database Functions**: Uses `func.now()` for better performance
- **Timezone Handling**: Consistent timezone-aware timestamps
- **Index Optimization**: Primary key automatically indexed
- **Bulk Operations**: Compatible with SQLAlchemy bulk operations

## Error Handling

### Common Error Patterns

```python
# Safe dictionary conversion with error handling
def safe_to_dict(model_instance: BaseModel) -> dict[str, Any]:
    try:
        return dict(model_instance.to_dict())
    except AttributeError as e:
        logger.error(f"Failed to convert model to dict: {e}")
        return {"error": "Model conversion failed"}
    except Exception as e:
        logger.error(f"Unexpected error in model conversion: {e}")
        return {"error": "Unexpected conversion error"}
```

### Validation Error Handling

```python
# Handle timestamp validation errors
try:
    model = SomeModel(created_at=None)  # This would fail
except ValueError as e:
    # Handle validation error appropriately
    raise HTTPException(status_code=400, detail="Invalid timestamp")
```

## Best Practices

### Model Design

- **Inherit from BaseModel**: All application models should inherit from BaseModel
- **Use Abstract Classes**: Mark intermediate base classes as abstract
- **Proper Typing**: Always use `Mapped[]` annotations for columns
- **Table Names**: Always specify `__tablename__` explicitly
- **Documentation**: Document all model classes and special fields

### Timestamp Usage

- **Never Override Timestamps**: Let the base class handle created_at/updated_at
- **Query Optimization**: Index timestamp columns for frequent queries
- **Timezone Consistency**: Always use timezone-aware datetimes
- **Audit Trails**: Leverage timestamps for audit and debugging

### Dictionary Conversion

- **API Responses**: Use `to_dict()` for converting models to API responses
- **Logging**: Use dictionary conversion for structured logging
- **Serialization**: Combine with serialization libraries for data export
- **Testing**: Use dictionary comparison in tests for model validation

## Testing Strategies

### Unit Testing

```python
def test_base_model_inheritance():
    """Test that BaseModel provides required functionality."""
    
    # Create test model class
    class TestModel(BaseModel):
        __tablename__ = "test_model"
        name: Mapped[str] = mapped_column(String(100))
    
    # Verify inheritance
    assert hasattr(TestModel, 'id')
    assert hasattr(TestModel, 'created_at')
    assert hasattr(TestModel, 'updated_at')
    assert hasattr(TestModel, 'to_dict')

def test_to_dict_conversion():
    """Test dictionary conversion functionality."""
    
    # Create model instance
    instance = TestModel(name="test")
    instance.id = 1
    instance.created_at = datetime.utcnow()
    instance.updated_at = datetime.utcnow()
    
    # Convert to dictionary
    result = instance.to_dict()
    
    # Verify conversion
    assert isinstance(result, dict)
    assert result['id'] == 1
    assert result['name'] == "test"
    assert isinstance(result['created_at'], datetime)
    assert isinstance(result['updated_at'], datetime)
```

### Integration Testing

```python
async def test_timestamp_functionality():
    """Test automatic timestamp functionality."""
    
    # Create new record
    model = TestModel(name="timestamp_test")
    session.add(model)
    await session.commit()
    
    # Verify creation timestamp
    assert model.created_at is not None
    assert model.updated_at is not None
    assert model.created_at == model.updated_at
    
    # Update record
    original_created_at = model.created_at
    original_updated_at = model.updated_at
    
    await asyncio.sleep(0.1)  # Ensure time difference
    model.name = "updated_name"
    await session.commit()
    
    # Verify update timestamp
    assert model.created_at == original_created_at  # Unchanged
    assert model.updated_at > original_updated_at  # Updated
```

### Database Testing

```python
async def test_database_integration():
    """Test base model database integration."""
    
    # Test creation
    model = TestModel(name="db_test")
    session.add(model)
    await session.commit()
    
    # Verify database storage
    stored_model = await session.get(TestModel, model.id)
    assert stored_model is not None
    assert stored_model.name == "db_test"
    assert stored_model.created_at is not None
    
    # Test dictionary conversion with database data
    model_dict = stored_model.to_dict()
    assert model_dict['id'] == stored_model.id
    assert model_dict['name'] == "db_test"
```

## Related Files

### Dependencies

- `sqlalchemy` - ORM framework for DeclarativeBase, mapped_column, and database functions
- `datetime` - Timestamp handling for created_at and updated_at fields
- `typing` - Type annotations including Any, Final, cast for type safety
- `collections.abc` - Mapping interface for to_dict return type

### Model Integration

- `src.models.user` - User model inheriting from BaseModel
- `src.models.file` - File model inheriting from BaseModel
- `src.models.blacklisted_token` - Token security model with base functionality
- `src.models.used_password_reset_token` - Password reset tracking model

### Database Integration

- `src.core.database` - Database session and engine configuration
- `alembic` - Database migration system using BaseModel structure
- `src.repositories.*` - Repository pattern implementations using BaseModel

## Configuration

### Database Settings

```python
# Database column configuration
TIMESTAMP_CONFIG = {
    "timezone": True,
    "default": "func.now()",
    "nullable": False
}

PRIMARY_KEY_CONFIG = {
    "type": "Integer",
    "autoincrement": True,
    "nullable": False
}
```

### Type Safety Settings

```python
# Type checking configuration
TYPE_SAFETY = {
    "use_mapped_annotations": True,
    "enforce_final_declarations": True,
    "strict_typing": True
}
```

### Performance Settings

```python
# Performance optimization settings
PERFORMANCE_CONFIG = {
    "use_database_functions": True,  # func.now() vs Python datetime
    "lazy_table_reflection": True,   # Efficient to_dict() implementation
    "minimal_base_class": True       # Keep BaseModel lightweight
}
```

This base model module provides the essential foundation for all database models in the ReViewPoint application, ensuring consistent behavior, automatic timestamping, type safety, and utility methods through well-designed SQLAlchemy patterns and inheritance structures.
