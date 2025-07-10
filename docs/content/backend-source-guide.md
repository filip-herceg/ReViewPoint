# Backend Source Guide

This comprehensive guide provides an overview of the backend source code structure, conventions, and best practices for the ReViewPoint project. The backend is built with FastAPI, SQLAlchemy, and follows modern Python development practices.

## Architecture Overview

The ReViewPoint backend follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────┐
│   API Layer        │  ← REST endpoints, request/response handling
├─────────────────────┤
│   Service Layer    │  ← Business logic, validation, orchestration
├─────────────────────┤
│   Repository Layer │  ← Data access, database operations
├─────────────────────┤
│   Model Layer      │  ← Database models, schemas
└─────────────────────┘
```

## Directory Structure

### Core Application Structure
- **`src/`** — Main backend source code
  - **`main.py`** — FastAPI application entry point and configuration
  - **`__about__.py`** — Project metadata and version information
  - **`__init__.py`** — Package initialization

### API Layer (`src/api/`)
- **`deps.py`** — Dependency injection for authentication, database sessions
- **`v1/`** — Version 1 API endpoints
  - **`auth.py`** — Authentication endpoints (login, register, token refresh)
  - **`users.py`** — User management endpoints (profile, settings)
  - **`uploads.py`** — File upload and management endpoints
  - **`health.py`** — Health check endpoints for monitoring
  - **`websocket.py`** — WebSocket endpoints for real-time communication

### Core Configuration (`src/core/`)
- **`config.py`** — Application configuration management with environment variables
- **`database.py`** — Database connection, session management, and ORM setup
- **`logging.py`** — Centralized logging configuration with loguru
- **`security.py`** — Authentication, authorization, and security utilities
- **`events.py`** — Application lifecycle events (startup/shutdown)
- **`documentation.py`** — OpenAPI schema enhancement and customization

### Database Models (`src/models/`)
- **`base.py`** — Base SQLAlchemy model with common fields and functionality
- **`user.py`** — User account and profile data model
- **`file.py`** — File metadata and upload tracking model
- **`used_password_reset_token.py`** — Single-use password reset token tracking
- **`__init__.py`** — Model exports and database table registration

### Data Access Layer (`src/repositories/`)
- **`user.py`** — User data access layer with authentication support
- **`file.py`** — File data access layer with CRUD operations
- **`blacklisted_token.py`** — JWT token blacklist management
- **`__init__.py`** — Repository exports and dependency injection setup

### Business Logic Layer (`src/services/`)
- **`user.py`** — User management business logic and operations
- **`upload.py`** — File upload business logic and validation
- **`__init__.py`** — Service exports and dependency injection setup

### Validation Schemas (`src/schemas/`)
- **`user.py`** — User data validation and serialization schemas
- **`auth.py`** — Authentication request/response validation schemas
- **`file.py`** — File operation validation and serialization schemas
- **`token.py`** — JWT and authentication token schemas
- **`blacklisted_token.py`** — Token blacklist validation schemas

### Utility Functions (`src/utils/`)
- **`hashing.py`** — Password hashing and cryptographic utilities
- **`validation.py`** — Data validation and sanitization utilities
- **`file.py`** — File processing, validation, and manipulation utilities
- **`errors.py`** — Custom exception classes and error handling utilities
- **`cache.py`** — Caching utilities and Redis integration
- **`rate_limit.py`** — Rate limiting and API throttling utilities
- **`http_error.py`** — HTTP error handling and response utilities
- **`environment.py`** — Environment variable management and configuration
- **`datetime.py`** — Date and time handling utilities with timezone awareness
- **`filters.py`** — Data filtering and query utilities

### Middleware (`src/middlewares/`)
- **`logging.py`** — Request/response logging and monitoring middleware
- **`__init__.py`** — Middleware exports and registration

### Database Migrations (`src/alembic_migrations/`)
- **`env.py`** — Alembic migration environment setup
- **`script.py.mako`** — Template for generating new migration scripts
- **`alembic.ini`** — Alembic configuration file
- **`versions/`** — Individual migration files for schema evolution

### Test Suite (`tests/`)
- **`conftest.py`** — Pytest configuration and fixtures
- **`factories.py`** — Test data generation and factory utilities
- **Unit tests** — Mirror the `src/` structure for comprehensive coverage
- **Integration tests** — End-to-end testing of API endpoints
- **Performance tests** — Load testing and performance benchmarking

## Key Design Patterns

### 1. Dependency Injection
The application uses FastAPI's dependency injection system for:
- Database session management
- Authentication and authorization
- Service layer instantiation
- Configuration access

```python
# Example dependency injection
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))
```

### 2. Repository Pattern
Data access is abstracted through repositories:
- Consistent interface for data operations
- Easy mocking for testing
- Database-agnostic business logic

### 3. Service Layer Pattern
Business logic is encapsulated in services:
- Orchestrates multiple repository calls
- Implements business rules and validation
- Handles complex operations and transactions

### 4. Schema Validation
Pydantic schemas ensure data integrity:
- Request/response validation
- Type safety and serialization
- Documentation generation

## Development Conventions

### Code Style
- **PEP 8** compliance with automated formatting via Ruff
- **Type hints** for all function signatures and class attributes
- **Docstrings** following Google/NumPy style for all public APIs
- **Import organization** with isort for consistent import ordering

### Error Handling
- **Custom exceptions** for business logic errors
- **HTTP exceptions** for API-specific errors
- **Global exception handler** for consistent error responses
- **Structured logging** for debugging and monitoring

### Testing Standards
- **Unit tests** for all business logic
- **Integration tests** for API endpoints
- **Test fixtures** for consistent test data
- **Mock objects** for external dependencies
- **Coverage requirements** of 80%+ for critical components

### Database Operations
- **Migration-first** approach for schema changes
- **Async operations** for all database interactions
- **Connection pooling** for performance optimization
- **Transaction management** for data consistency

## Configuration Management

### Environment Variables
```bash
# Core application settings
REVIEWPOINT_ENVIRONMENT=development
REVIEWPOINT_DEBUG=true
REVIEWPOINT_LOG_LEVEL=DEBUG

# Database configuration
REVIEWPOINT_DB_URL=postgresql+asyncpg://user:pass@localhost/db

# Security settings
REVIEWPOINT_JWT_SECRET=your-secret-key
REVIEWPOINT_JWT_ALGORITHM=HS256
REVIEWPOINT_JWT_EXPIRE_MINUTES=30

# External services
REVIEWPOINT_STORAGE_URL=s3://bucket-name
REVIEWPOINT_REDIS_URL=redis://localhost:6379
```

### Configuration Loading
- Environment-specific configuration files
- Validation of required settings at startup
- Default values for optional configurations
- Type conversion and validation

## Running the Backend

### Development Server
```bash
# Install dependencies
pip install -e .

# Run with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run with specific environment
REVIEWPOINT_ENVIRONMENT=development uvicorn src.main:app --reload
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (development only)
alembic downgrade base && alembic upgrade head
```

### Testing
```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run integration tests only
```

## Performance Considerations

### Database Optimization
- **Connection pooling** with appropriate pool sizes
- **Query optimization** with SQLAlchemy ORM best practices
- **Eager loading** for related data to avoid N+1 queries
- **Database indexing** for frequently queried columns

### Caching Strategy
- **Redis caching** for frequently accessed data
- **Application-level caching** for expensive computations
- **HTTP caching headers** for static content
- **Cache invalidation** strategies for data consistency

### Async Operations
- **Async database operations** for non-blocking I/O
- **Background tasks** for long-running operations
- **Queue systems** for processing uploads and analysis
- **Connection pooling** for external services

## Security Best Practices

### Authentication & Authorization
- **JWT tokens** with proper expiration and refresh
- **Password hashing** with bcrypt and salt
- **Rate limiting** to prevent brute force attacks
- **Role-based access control** for different user types

### Data Protection
- **Input validation** and sanitization
- **SQL injection prevention** through ORM usage
- **CORS configuration** for secure cross-origin requests
- **HTTPS enforcement** in production environments

### Monitoring & Logging
- **Structured logging** with correlation IDs
- **Error tracking** with detailed context
- **Performance monitoring** with request timing
- **Security event logging** for audit trails

## Related Documentation

### API Documentation
- [API Reference](api-reference.md) - Complete REST API documentation
- [OpenAPI Schema](backend/api-reference.md) - Interactive API documentation

### Source Code Documentation
- [Main Application](main.py.md) - Application entry point and configuration
- [Core Configuration](backend/src/core/config.py.md) - Configuration management
- [Database Models](backend/src/models/) - All database model documentation
- [API Endpoints](backend/src/api/) - All API endpoint documentation
- [Business Services](backend/src/services/) - All service layer documentation
- [Utilities](backend/src/utils/) - All utility function documentation

### Testing Documentation
- [Test Overview](backend/tests/README.md) - Testing strategy and organization
- [Test Configuration](backend/tests/conftest.py.md) - Test fixtures and setup
- [Test Utilities](backend/tests/factories.py.md) - Test data generation

### Deployment Documentation
- [Docker Configuration](backend/deployment/) - Container deployment setup
- [Database Migrations](backend/src/alembic_migrations/) - Schema evolution management

---

> **Note**: This guide is updated regularly as the backend evolves. For the most current information, always refer to the source code and its accompanying documentation.
