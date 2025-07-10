# FastAPI Application Entry Point (`main.py`)

| Item               | Value                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------- |
| **Layer**          | Application Entry Point                                                                                             |
| **Responsibility** | FastAPI application factory, configuration, middleware setup, routing, and startup/shutdown event handling         |
| **Status**         | 🟢 Complete                                                                                                         |

## 1. Purpose

Creates and configures the FastAPI application instance, registers all routes, middleware, and event handlers. Serves as the main entry point for the ReViewPoint backend API service.

## 2. Public API

| Symbol | Type             | Description                         |
| ------ | ---------------- | ----------------------------------- |
| `app`  | FastAPI instance | The main FastAPI application object |
| `create_app()` | Function | Application factory function |

## 3. Key Features

### Application Configuration
- **Environment-based Configuration**: Uses `get_settings()` for environment-specific configuration
- **Debug Mode**: Configurable debug mode for development vs. production
- **CORS Configuration**: Cross-origin resource sharing setup for frontend integration
- **Static File Serving**: Serves static files and uploads

### Routing & API Structure
- **Versioned API Routes**: All endpoints under `/api/v1/` prefix
- **Authentication Routes**: User login, registration, and token management
- **Upload Routes**: File upload and management endpoints
- **User Routes**: User profile and management endpoints
- **Health Check Routes**: Application health monitoring
- **WebSocket Routes**: Real-time communication support

### Middleware Stack
- **Request Logging**: Comprehensive request/response logging with loguru
- **CORS Middleware**: Cross-origin request handling
- **Error Handling**: Global exception handling with structured JSON responses
- **Authentication Middleware**: JWT token validation and user context

### Event Handling
- **Startup Events**: Database connection initialization, migrations, configuration validation
- **Shutdown Events**: Graceful cleanup of resources and connections

## 4. Dependencies

### Internal Dependencies
- `src.api.v1.*`: All API route modules
- `src.core.config`: Application configuration management
- `src.core.logging`: Centralized logging setup
- `src.core.events`: Application lifecycle event handlers
- `src.core.documentation`: OpenAPI schema enhancement
- `src.middlewares.logging`: Request logging middleware

### External Dependencies
- `fastapi`: Web framework for building APIs
- `loguru`: Advanced logging library
- `uvicorn`: ASGI server for production deployment

## 5. Application Factory Pattern

The application uses the factory pattern for better testability and configuration flexibility:

```python
def create_app() -> FastAPI:
    """Create and configure FastAPI application instance"""
    app = FastAPI(
        title="ReViewPoint API",
        description="Modular, scalable, and LLM-powered platform for scientific paper review",
        version="1.0.0",
        debug=settings.debug_mode
    )
    
    # Configure middleware, routes, and event handlers
    setup_middleware(app)
    setup_routes(app)
    setup_events(app)
    
    return app
```

## 6. Error Handling Strategy

- **Global Exception Handler**: Catches all unhandled exceptions and returns structured JSON responses
- **HTTP Exception Handling**: Proper HTTP status codes and error messages
- **Validation Errors**: Pydantic validation error handling with detailed feedback
- **Logging Integration**: All errors are logged with full context for debugging

## 7. Production Considerations

- **Environment Variables**: All configuration through environment variables
- **Security Headers**: Security middleware for production deployment
- **Performance Monitoring**: Request timing and performance metrics
- **Health Checks**: Comprehensive health check endpoints for load balancers
- **Graceful Shutdown**: Proper cleanup of resources and connections

## 8. Testing Strategy

| Test Type | Coverage |
| --------- | -------- |
| Unit Tests | Application factory, configuration, middleware setup |
| Integration Tests | Full API endpoint testing with test database |
| E2E Tests | Complete application workflow testing |

## 9. Configuration Options

| Setting | Description | Default |
| ------- | ----------- | ------- |
| `DEBUG_MODE` | Enable debug mode and detailed error responses | `False` |
| `CORS_ORIGINS` | Allowed CORS origins for frontend integration | `["*"]` |
| `API_PREFIX` | API route prefix | `/api/v1` |
| `STATIC_FILES_PATH` | Static file serving path | `uploads/` |

## 10. Development & Deployment

### Development Server
```bash
# Run with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run with environment variables
REVIEWPOINT_DEBUG=true uvicorn src.main:app --reload
```

### Production Deployment
```bash
# Production server with multiple workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker deployment
docker run -p 8000:8000 reviewpoint:latest
```

## 11. API Documentation

- **OpenAPI Schema**: Automatically generated OpenAPI 3.0 schema
- **Interactive Docs**: Swagger UI available at `/docs`
- **ReDoc**: Alternative documentation at `/redoc`
- **Schema Export**: Programmatic access to API schema for frontend type generation

## 12. Monitoring & Observability

- **Request Logging**: All requests logged with timing and response status
- **Error Tracking**: Comprehensive error logging with stack traces
- **Performance Metrics**: Response time and throughput monitoring
- **Health Endpoints**: Application and dependency health checks

> **Note**: This file is the central configuration point for the entire FastAPI application. Any changes to routing, middleware, or global configuration should be made here.

## 13. Related Documentation

- [API Reference](api-reference.md) - Complete API endpoint documentation
- [Core Configuration](backend/src/core/config.py.md) - Application configuration management
- [Event Handlers](backend/src/core/events.py.md) - Application lifecycle events
- [Logging Configuration](backend/src/core/logging.py.md) - Centralized logging setup
- [Request Middleware](backend/src/middlewares/logging.py.md) - Request logging middleware
