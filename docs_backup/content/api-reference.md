# API Reference

This comprehensive reference provides detailed documentation for all REST API endpoints in the ReViewPoint platform. The API follows RESTful conventions and provides JSON responses with proper HTTP status codes.

## API Overview

- **Base URL**: `http://localhost:8000` (development) / `https://api.reviewpoint.com` (production)
- **API Version**: v1
- **Content Type**: `application/json`
- **Authentication**: JWT Bearer tokens
- **Rate Limiting**: Configurable per endpoint (see [Rate Limit Utils](backend/src/utils/rate_limit.py.md))

## Authentication

All API endpoints (except registration and login) require JWT authentication via the `Authorization` header:

```bash
Authorization: Bearer <your-jwt-token>
```

## API Endpoints by Category

### Authentication & Security
- [Authentication API](backend/src/api/v1/auth.py.md) - User login, registration, password reset, and token management
- [Dependencies](backend/src/api/deps.py.md) - Authentication dependencies and security middleware

### User Management
- [User API](backend/src/api/v1/auth.py.md) - User profile management, preferences, and account operations

### File Operations
- [Upload API](backend/src/api/v1/uploads.py.md) - File upload, validation, storage, and metadata management

### Core API Infrastructure
- [API Router Configuration](backend/src/api/__init__.py.md) - API routing setup and middleware configuration
- [V1 API Structure](backend/src/api/v1/__init__.py.md) - Version 1 API endpoint organization

## Data Models & Validation

All API requests and responses use Pydantic schemas for validation:

- [Authentication Schemas](backend/src/schemas/auth.py.md) - Login, registration, and token schemas
- [User Schemas](backend/src/schemas/user.py.md) - User profile and preference validation schemas  
- [File Schemas](backend/src/schemas/file.py.md) - File upload and metadata validation schemas
- [Token Schemas](backend/src/schemas/token.py.md) - JWT and authentication token schemas

## Error Handling

The API provides consistent error responses with appropriate HTTP status codes:

- **400 Bad Request**: Invalid request data or validation errors
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors with detailed field information
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side errors

See [Error Utils](backend/src/utils/errors.py.md) for detailed error handling implementation.

## Testing & Development

- [Backend API Tests](backend/tests/README.md) - Complete test suite for API endpoints
- **OpenAPI Documentation**: Available at `/docs` (Swagger UI) and `/redoc` endpoints
- **Schema Export**: Use [Export Backend Schema](scripts/export-backend-schema.py.md) script

## Rate Limiting & Performance

- Configurable rate limiting per endpoint
- Request/response logging via [Logging Middleware](backend/src/middlewares/logging.py.md)
- Caching support through [Cache Utils](backend/src/utils/cache.py.md)

---

*This API reference is automatically updated as new endpoints are added or modified. For the most current API schema, visit the `/docs` endpoint on your running backend server.*
