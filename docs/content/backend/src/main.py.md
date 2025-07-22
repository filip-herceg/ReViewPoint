# main.py - FastAPI Application Entry Point

**File Location**: `backend/src/main.py`  
**Purpose**: Application factory and FastAPI configuration  
**Type**: Core Application Module

## Overview

This file serves as the main entry point for the ReViewPoint FastAPI application. It configures the application instance, sets up middleware, includes API routers, and defines the application lifecycle events.

## Key Components

### Application Factory

```python
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Returns:
        FastAPI: Configured application instance
    """
```

**Purpose**: Creates a configured FastAPI application with all necessary middleware, routers, and settings.

**Configuration Includes**:

- CORS middleware for cross-origin requests
- API router inclusion with versioning
- Exception handlers for consistent error responses
- OpenAPI documentation configuration
- Application metadata and versioning

### Middleware Configuration

**CORS Middleware**:

- Allows frontend communication from development and production origins
- Configures allowed methods (GET, POST, PUT, DELETE, OPTIONS)
- Handles preflight requests and credentials

**Custom Middleware**:

- Request logging and timing
- Error tracking and monitoring
- Request ID generation for tracing

### Router Inclusion

The application includes all API routers with proper prefixing:

```python
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(uploads_router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
```

### Lifecycle Events

**Startup Events**:

- Database connection initialization
- Cache connection verification
- Application readiness logging

**Shutdown Events**:

- Graceful database connection closure
- Cache connection cleanup
- Resource cleanup

## Dependencies

### Core Dependencies

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
```

### Internal Dependencies

```python
from src.core.config import settings
from src.core.database import init_db
from src.api.v1 import auth, users, uploads, health
```

## Configuration

### Environment Variables

- `ENVIRONMENT`: Application environment (development/production)
- `DEBUG`: Debug mode configuration
- `CORS_ORIGINS`: Allowed CORS origins
- `API_V1_STR`: API version prefix

### Application Settings

```python
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)
```

## Usage Examples

### Development Server

```bash
# Start with uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the Hatch environment
hatch run uvicorn src.main:app --reload
```

### Production Deployment

```bash
# Production server with Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Testing Integration

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
```

## Error Handling

### Global Exception Handlers

```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )
```

**Handled Exceptions**:

- Validation errors (422)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Internal server errors (500)

### Custom Error Responses

All error responses follow a consistent format:

```json
{
    "detail": "Human readable error message",
    "error_code": "MACHINE_READABLE_CODE",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Performance Considerations

### Async Operations

- All endpoints are async for non-blocking I/O
- Database operations use async SQLAlchemy
- File operations use async file handlers

### Connection Pooling

- Database connection pool managed by SQLAlchemy
- Connection lifecycle tied to request lifecycle
- Automatic connection cleanup on shutdown

### Response Optimization

- JSON response optimization with orjson
- Gzip compression for large responses
- ETags for caching static content

## Security Features

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### Security Headers

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HTTPS)

### Rate Limiting

- Global rate limiting middleware
- Endpoint-specific rate limits
- IP-based and user-based limiting

## Monitoring and Observability

### Health Checks

- Database connectivity check
- External service availability
- Application readiness probe

### Logging

```python
import logging
from src.core.logging import setup_logging

# Structured logging with JSON format
logger = logging.getLogger(__name__)
logger.info("Application started", extra={"component": "main"})
```

### Metrics Collection

- Request duration tracking
- Error rate monitoring
- Database query performance
- Memory and CPU usage

## Related Files

### Core Configuration

- [config.py](../core/config.py.md) - Application configuration and settings
- [database.py](../core/database.py.md) - Database connection and session management
- [logging.py](../core/logging.py.md) - Logging configuration and setup

### API Components

- [auth.py](../api/v1/auth.py.md) - Authentication endpoints
- [users.py](../api/v1/users/core.py.md) - User management endpoints
- [uploads.py](../api/v1/uploads.py.md) - File upload endpoints
- [health.py](../api/v1/health.py.md) - Health check endpoints

### Testing

- [test_main.py](../../tests/test_main.py.md) - Main application tests
- [conftest.py](../../tests/conftest.py.md) - Test configuration and fixtures

## Development Notes

### Code Style

- Follows PEP 8 with Ruff formatter
- Type hints for all function signatures
- Comprehensive docstrings for all public methods
- Async/await patterns throughout

### Testing Strategy

- Unit tests for individual functions
- Integration tests for complete workflows
- API tests for endpoint validation
- Performance tests for response times

### Deployment

- Docker containerization support
- Environment variable configuration
- Health check endpoints for load balancers
- Graceful shutdown handling

**This file is the foundation of the ReViewPoint backend application, providing a robust, scalable, and well-configured FastAPI server that serves as the backbone for all backend operations.**
