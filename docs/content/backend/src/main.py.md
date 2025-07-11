# Backend Main Application (main.py)

The main entry point for the ReViewPoint FastAPI backend application.

## Overview

This module contains the FastAPI application factory and startup configuration for the ReViewPoint backend. It handles:

- Application creation and configuration
- Database initialization
- API routing setup
- Middleware configuration
- CORS setup
- Static file serving
- Application lifecycle events

## Key Components

### Application Factory

The main application factory creates and configures the FastAPI application with:

- **OpenAPI Configuration**: Swagger/OpenAPI documentation setup
- **Database Integration**: SQLAlchemy database session management
- **Authentication**: JWT-based authentication middleware
- **File Uploads**: Multipart file upload handling
- **Error Handling**: Custom exception handlers
- **Security**: CORS and security header configuration

### Startup Events

- **Database Connection**: Establishes database connection on startup
- **Migration Check**: Optionally runs database migrations
- **Cache Initialization**: Sets up Redis cache if configured
- **Health Check**: Configures health monitoring endpoints

### API Routing

- **V1 API**: `/api/v1/` - Current API version endpoints
- **Authentication**: `/api/v1/auth/` - User authentication endpoints
- **Users**: `/api/v1/users/` - User management endpoints
- **Uploads**: `/api/v1/uploads/` - File upload endpoints
- **Health**: `/api/v1/health/` - Health check endpoints

## Configuration

The application uses environment-based configuration from `core.config`:

- **Database URL**: PostgreSQL or SQLite connection string
- **JWT Secret**: Authentication token signing key
- **CORS Origins**: Allowed frontend origins
- **Upload Settings**: File size limits and allowed types
- **Cache Settings**: Redis configuration for caching

## Usage

```python
# Development server
uvicorn src.main:app --reload

# Production server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Dependencies

- FastAPI for web framework
- SQLAlchemy for ORM
- Alembic for database migrations
- Pydantic for data validation
- Python-multipart for file uploads
- PyJWT for authentication tokens

## Related Files

- [`core/config.py`](core/config.py.md) - Application configuration
- [`core/database.py`](core/database.py.md) - Database setup
- [`api/v1/`](api/v1/) - API endpoint definitions
- [`models/`](models/README.md) - Database models
