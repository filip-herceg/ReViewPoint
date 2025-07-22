# Models Package - SQLAlchemy ORM Models

## Purpose

The models package defines the core SQLAlchemy ORM models for the ReViewPoint platform, providing a centralized location for all database entity definitions. This package exports all model classes and establishes the foundation for the application's data layer, supporting user management, file handling, authentication security, and password reset functionality.

## Key Components

### Exported Models

- **`Base`** - SQLAlchemy declarative base class for all models
- **`BlacklistedToken`** - JWT token blacklisting for secure logout operations
- **`File`** - File metadata and upload tracking with user relationships
- **`UsedPasswordResetToken`** - Password reset token tracking for security
- **`User`** - Core user entity with authentication and profile management

### Package Structure

The models are organized with clear separation of concerns:
- Base classes providing common functionality
- Domain-specific models for business entities
- Security-focused models for authentication operations
- Relationship definitions enabling data integrity

## Architecture Integration

### SQLAlchemy Foundation

The models package establishes the SQLAlchemy foundation through:
- Declarative base class inheritance
- Consistent column mapping patterns
- Standardized relationship configurations
- Common base model functionality

### Database Schema Management

Models define the complete database schema including:
- Primary key strategies with auto-increment
- Foreign key relationships with cascade behavior
- Unique constraints and database indexes
- Timezone-aware datetime handling

### ORM Integration Points

The models integrate with other application layers:
- **Repositories** use models for database operations
- **Schemas** provide API serialization/deserialization
- **Services** implement business logic using model operations
- **Migrations** manage schema evolution through Alembic

## Dependencies

### Core Dependencies

- `sqlalchemy` - ORM framework with declarative base and column types
- `collections.abc` - Abstract base classes for type definitions
- `datetime` - Timezone-aware datetime handling
- `typing` - Type annotations and forward references

### Internal Dependencies

- `src.models.base` - Base model classes and common functionality
- Cross-model relationships through forward references

## Common Patterns

### Base Model Inheritance

All models inherit from `BaseModel` providing:
- Automatic ID generation with integer primary keys
- Created/updated timestamp tracking with timezone awareness
- Dictionary conversion methods for serialization
- Consistent table naming and column patterns

### Relationship Definitions

Models use SQLAlchemy relationships for data integrity:
- Foreign key constraints with proper cascade behavior
- Back-population for bidirectional relationships
- WriteOnlyMapped for performance in large collections
- TYPE_CHECKING imports to avoid circular dependencies

### Validation and Security

Models implement validation and security features:
- Column-level validation through SQLAlchemy validators
- Timezone-aware datetime handling for security tokens
- Unique constraints for business rules enforcement
- Proper indexing for query performance

## Usage Examples

### Model Import and Usage

```python
from src.models import User, File, BlacklistedToken

# Models are available for repository operations
user = User(email="user@example.com", hashed_password="...")
file = File(filename="document.pdf", user_id=user.id)
```

### Base Model Functionality

```python
# All models inherit common functionality
instance = User(email="test@example.com")
dict_data = instance.to_dict()  # Convert to dictionary
```

## Integration with Application Layers

### Repository Layer Integration

The models package provides the foundation for repository operations:
- Type-safe database operations through mapped columns
- Relationship navigation for complex queries
- Consistent error handling through SQLAlchemy exceptions

### Schema Layer Coordination

Models coordinate with Pydantic schemas for API operations:
- ORM mode enables automatic schema population
- Column definitions align with schema field validation
- Relationship patterns support nested serialization

### Service Layer Operations

Service classes use models for business logic implementation:
- Transaction management through SQLAlchemy sessions
- Business rule enforcement through model validation
- Complex operations through relationship navigation

## Performance Considerations

### Query Optimization

Models are designed for efficient database operations:
- Strategic indexing on frequently queried columns
- Lazy loading relationships to prevent N+1 queries
- WriteOnlyMapped for large collections
- Proper foreign key constraints for referential integrity

### Memory Management

Models implement efficient memory usage patterns:
- Minimal attribute overhead through mapped columns
- Lazy relationship loading when appropriate
- Proper session management through repository layer

## Security Features

### Authentication Security

Models support secure authentication operations:
- Password hashing integration through user model
- JWT token blacklisting for secure logout
- Password reset token tracking with expiration
- Timezone-aware security token management

### Data Protection

Models implement data protection features:
- Soft deletion patterns through boolean flags
- Audit trail support through created/updated timestamps
- Secure relationship cascade behaviors
- Input validation through SQLAlchemy validators

## Testing Integration

### Model Testing Support

The models package supports comprehensive testing:
- Base model functionality testing through inheritance
- Relationship testing through foreign key constraints
- Validation testing through SQLAlchemy validators
- Integration testing with in-memory SQLite databases

### Test Database Configuration

Models work seamlessly with test configurations:
- SQLite compatibility for fast test execution
- Alembic migration support for test schema setup
- Transaction rollback support for test isolation

## Related Files

- [`base.py`](base.py.md) - Base classes and common model functionality
- [`user.py`](user.py.md) - User entity with authentication and profiles
- [`file.py`](file.py.md) - File metadata and upload management
- [`blacklisted_token.py`](blacklisted_token.py.md) - JWT security operations
- [`used_password_reset_token.py`](used_password_reset_token.py.md) - Password reset security
- [`../../repositories/`](../../repositories/__init__.py.md) - Repository layer using models
- [`../../schemas/`](../../schemas/__init__.py.md) - API schemas coordinating with models
