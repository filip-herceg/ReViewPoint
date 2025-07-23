# Base Models - SQLAlchemy Foundation Classes

## Purpose

The base module provides the foundational SQLAlchemy classes for the ReViewPoint platform, establishing the declarative base and common model functionality. This module defines the `Base` class for SQLAlchemy's declarative system and `BaseModel` with shared attributes and methods used across all application models, ensuring consistency and reducing code duplication.

## Key Components

### Base Class

**`Base`** - SQLAlchemy declarative base class
- Inherits from `DeclarativeBase` for modern SQLAlchemy 2.0+ patterns
- Serves as the foundation for all model class definitions
- Provides the metaclass functionality for ORM mapping
- Contains no additional attributes, maintaining clean inheritance

### BaseModel Abstract Class

**`BaseModel`** - Abstract base class with common model functionality
- Inherits from `Base` and marked as abstract with `__abstract__ = True`
- Provides standard primary key with auto-increment integer ID
- Implements automatic timestamp tracking for created_at and updated_at
- Includes `to_dict()` method for serialization support

### Core Attributes

#### Primary Key Strategy
```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
```

#### Timestamp Tracking
```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=func.now(), nullable=False
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
)
```

## Architecture Integration

### SQLAlchemy 2.0+ Patterns

The base module implements modern SQLAlchemy patterns:
- `DeclarativeBase` for the latest declarative system
- `Mapped` type annotations for enhanced type safety
- `mapped_column` for explicit column definition
- Timezone-aware datetime handling with `DateTime(timezone=True)`

### Database Function Integration

Leverages SQLAlchemy database functions:
- `func.now()` for server-side timestamp defaults
- Automatic `onupdate` triggers for modification tracking
- Timezone-aware operations for global application support

## Dependencies

### External Dependencies

- `sqlalchemy` - Core ORM functionality and column types
- `collections.abc.Mapping` - Type hints for dictionary-like objects
- `datetime.datetime` - Timestamp handling
- `typing` - Type annotations including `Any`, `Final`, and `cast`

### SQLAlchemy Components

- `DeclarativeBase` - Modern declarative base class
- `DateTime`, `Integer` - Column type definitions
- `func` - Database function support
- `Mapped`, `mapped_column` - Type-safe column mapping

## BaseModel Functionality

### Serialization Support

The `to_dict()` method provides model serialization:

```python
def to_dict(self) -> Mapping[str, Any]:
    """Convert model instance to dictionary, including all mapped columns."""
    result: dict[str, Any] = {}
    for column in cast(Any, self.__table__).columns:
        value: Any = getattr(self, column.name, None)
        result[column.name] = value
    return result
```

#### Features:
- Iterates through all table columns dynamically
- Handles missing attributes gracefully with None default
- Returns immutable Mapping interface for safety
- Uses type casting for SQLAlchemy table access

#### Error Handling:
- Raises `AttributeError` if column attributes are missing
- Provides clear documentation of potential exceptions
- Maintains type safety through proper annotations

### Timestamp Management

Automatic timestamp handling ensures audit trail consistency:

#### Created Timestamp:
- Set automatically on record creation using `default=func.now()`
- Timezone-aware to support global deployments
- Immutable after creation (no onupdate trigger)

#### Updated Timestamp:
- Set on creation and automatically updated on modifications
- Uses `onupdate=func.now()` for automatic maintenance
- Tracks any change to the model instance

## Usage Patterns

### Model Inheritance

All application models inherit from BaseModel:

```python
class User(BaseModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # id, created_at, updated_at inherited automatically
```

### Serialization Usage

Convert model instances to dictionaries for API responses:

```python
user = User(email="test@example.com")
user_dict = user.to_dict()
# Returns: {"id": 1, "email": "test@example.com", "created_at": "...", "updated_at": "..."}
```

## Type Safety Considerations

### Type Annotation Guidelines

The module includes important type safety guidance:
- Avoid using `Base` as a type annotation
- Use specific model classes for type hints
- Use `Any` type when model type is unknown
- Leverage `Mapped` annotations for column type safety

### SQLAlchemy Integration

Type safety integration with SQLAlchemy:
- `cast(Any, self.__table__)` for accessing table metadata
- `Final` annotation for abstract class marker
- Proper return type annotations for all methods

## Performance Considerations

### Database Operations

The base model design optimizes database performance:
- Server-side timestamp generation reduces Python overhead
- Minimal attribute overhead through mapped columns
- Efficient primary key strategy with auto-increment
- Timezone-aware operations without Python conversion

### Memory Efficiency

BaseModel maintains efficient memory usage:
- Minimal attribute definitions in base class
- Lazy evaluation of table metadata access
- Efficient dictionary creation in to_dict method

## Testing Integration

### Test Database Support

Base models support comprehensive testing scenarios:
- Compatible with SQLite for fast test execution
- Timezone handling works across database backends
- Serialization methods facilitate test assertions
- Abstract class pattern allows focused unit testing

### Common Testing Patterns

```python
# Test inheritance and base functionality
def test_base_model_inheritance():
    user = User(email="test@example.com")
    assert hasattr(user, 'id')
    assert hasattr(user, 'created_at')
    assert hasattr(user, 'updated_at')

# Test serialization
def test_to_dict_serialization():
    user = User(email="test@example.com")
    user_dict = user.to_dict()
    assert "email" in user_dict
    assert user_dict["email"] == "test@example.com"
```

## Security Considerations

### Timestamp Integrity

Timestamp management provides security benefits:
- Server-side timestamp generation prevents client manipulation
- Timezone-aware storage prevents time-based attacks
- Automatic update tracking for audit trails
- Immutable creation timestamps for forensic analysis

### Data Access Patterns

The base model promotes secure data access:
- Controlled serialization through to_dict method
- Type-safe attribute access through Mapped annotations
- Clear separation between base functionality and business logic

## Related Files

- [`user.py`](user.py.md) - User model inheriting from BaseModel
- [`file.py`](file.py.md) - File model with BaseModel functionality
- [`blacklisted_token.py`](blacklisted_token.py.md) - Security model using base patterns
- [`used_password_reset_token.py`](used_password_reset_token.py.md) - Password reset with base inheritance
- [`../core/database.py`](../core/database.py.md) - Database configuration using Base
- [`../repositories/`](../repositories/__init__.py.md) - Repository layer using BaseModel patterns
