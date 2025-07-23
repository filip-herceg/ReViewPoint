# OpenAPI Schema Module

**File:** `backend/src/core/openapi.py`  
**Purpose:** OpenAPI schema customization and enhancement for ReViewPoint API documentation  
**Lines of Code:** 367  
**Type:** Core Infrastructure Module

## Overview

The OpenAPI schema module provides comprehensive customization of FastAPI's automatically generated OpenAPI specification for the ReViewPoint backend. It enhances the API documentation with proper metadata, security schemes, authentication configurations, endpoint tagging, and response examples. The module transforms the default OpenAPI output into a production-ready API specification suitable for client code generation, testing, and comprehensive API documentation.

## Architecture

### Core Design Principles

1. **Schema Enhancement**: Extends FastAPI's default OpenAPI generation with additional metadata
2. **Security-First Configuration**: Comprehensive authentication and authorization documentation
3. **Type-Safe Implementation**: Full TypedDict definitions for OpenAPI schema structure
4. **Endpoint Classification**: Automatic tagging and security requirement assignment
5. **Example-Rich Documentation**: Realistic response examples for better developer experience
6. **Multi-Environment Support**: Different server configurations for dev/prod environments

### Key Components

#### TypedDict Schema Definitions

```python
class OpenAPISchemaDict(TypedDict, total=False):
    info: dict[str, object]
    servers: Sequence[ServerDict]
    components: dict[str, object]
    security: Sequence[Mapping[str, Sequence[str]]]
    tags: Sequence[TagDict]
    paths: dict[str, dict[str, OperationDict]]
```

**Comprehensive Type System:**

- Contact and license information structures
- Server configuration definitions
- Security scheme specifications (Bearer, API Key, OAuth2)
- Tag and example data structures
- Complete OpenAPI schema typing

#### Configuration Constants

```python
CONTACT: Final[ContactDict] = {
    "name": "ReViewPoint Team",
    "url": "https://github.com/your-org/reviewpoint",
    "email": "support@reviewpoint.org",
}

SERVERS: Final[Sequence[ServerDict]] = [
    {"url": "http://localhost:8000", "description": "Development server"},
    {"url": "https://api.reviewpoint.org", "description": "Production server"},
]
```

**Metadata Configuration:**

- Project contact information and support details
- License information (MIT License)
- Multi-environment server configurations
- Comprehensive endpoint tagging system

## Core Functions

### 🔧 **Primary Setup Function**

#### `setup_openapi()`

```python
def setup_openapi(app: FastAPI) -> None:
    """Set up the OpenAPI schema for testing."""
```

**Purpose:** Main entry point for configuring OpenAPI schema customization

**Configuration Process:**

1. **Contact Information**: Sets project contact and license details
2. **Custom Schema Function**: Replaces FastAPI's default OpenAPI generator
3. **Method Binding**: Properly binds custom function to FastAPI instance
4. **Error Handling**: Comprehensive exception handling for schema generation

**Usage Integration:**

```python
from fastapi import FastAPI
from src.core.openapi import setup_openapi

app = FastAPI()
setup_openapi(app)  # Enhanced OpenAPI schema now available
```

### 📝 **Schema Customization Function**

#### `custom_openapi()`

```python
def custom_openapi(self: FastAPI) -> dict[str, object]:
    """Customizes the OpenAPI schema for ReViewPoint."""
```

**Purpose:** Comprehensive OpenAPI schema enhancement and customization

**Enhancement Process:**

1. **Cache Check**: Returns cached schema if already generated
2. **Base Generation**: Calls original FastAPI OpenAPI generator
3. **Metadata Enhancement**: Adds contact, license, and server information
4. **Security Configuration**: Configures multiple authentication schemes
5. **Endpoint Tagging**: Automatically categorizes API endpoints
6. **Example Addition**: Adds realistic response examples
7. **Schema Caching**: Caches enhanced schema for performance

## Security Configuration

### 🔐 **Authentication Schemes**

#### Bearer Token Authentication

```python
"BearerAuth": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": "Enter JWT token",
}
```

**Configuration:**

- JWT token-based authentication
- Bearer token format specification
- Integration with FastAPI security dependencies

#### API Key Authentication

```python
"ApiKeyAuth": {
    "type": "apiKey",
    "in": "header",
    "name": "X-API-Key",
    "description": "API key for service-to-service authentication",
}
```

**Configuration:**

- Header-based API key authentication
- Service-to-service authentication support
- X-API-Key header specification

#### OAuth2 Password Flow

```python
"OAuth2PasswordBearer": {
    "type": "oauth2",
    "flows": {
        "password": {
            "tokenUrl": "/api/v1/auth/login",
            "scopes": {},
        }
    },
}
```

**Configuration:**

- OAuth2 password flow documentation
- Token endpoint specification
- Scope-based authorization ready

### 🛡️ **Security Requirements Assignment**

#### Non-Authenticated Endpoints

```python
NON_AUTH_ENDPOINTS: Final[Sequence[tuple[str, str]]] = [
    ("/api/v1/auth/login", "post"),
    ("/api/v1/auth/logout", "post"),
    ("/api/v1/auth/request-password-reset", "post"),
    ("/api/v1/auth/reset-password", "post"),
    ("/api/v1/health", "get"),
    ("/api/v1/metrics", "get"),
]
```

**Purpose:** Defines endpoints that don't require authentication

**Automatic Security Assignment:**

- Public endpoints: No security requirements
- Protected endpoints: Bearer token or API key required
- Special endpoints: Multiple authentication options

#### Security Requirement Logic

```python
# Default for protected endpoints
operation["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

# Special case for /auth/me endpoint
if path == "/api/v1/auth/me" and method == "get":
    operation["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []},
        {"OAuth2PasswordBearer": []},
    ]
```

**Security Configuration:**

- Most endpoints: Bearer token OR API key
- User profile endpoint: Bearer token OR API key OR OAuth2
- Public endpoints: No authentication required

## Endpoint Organization

### 🏷️ **Automatic Tagging System**

#### Tag Definitions

```python
TAGS: Final[Sequence[TagDict]] = [
    {"name": "Auth", "description": "Authentication operations"},
    {"name": "User Management", "description": "User management operations"},
    {"name": "Health", "description": "Health check and monitoring endpoints"},
    {"name": "File", "description": "File upload and management operations"},
]
```

**Tag Categories:**

- **Auth**: Login, logout, password reset, user registration
- **User Management**: User CRUD operations, profile management
- **Health**: System health checks and monitoring
- **File**: Upload, download, file management operations

#### Automatic Tag Assignment

```python
# Authentication endpoints
if "/api/v1/auth" in path:
    op["tags"] = ["Auth"]

# User management endpoints
elif "/api/v1/users" in path:
    op["tags"] = ["User Management"]

# Health and monitoring endpoints
elif "/api/v1/health" in path or "/api/v1/metrics" in path:
    op["tags"] = ["Health"]

# File operations
elif "/api/v1/uploads" in path:
    op["tags"] = ["File"]
```

**Benefits:**

- Organized API documentation sections
- Logical grouping for client code generation
- Easier navigation in Swagger UI
- Consistent categorization across all endpoints

## Response Examples

### 📋 **Realistic Response Examples**

#### User Export Example

```python
content_info["example"] = {
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
        }
    ]
}
```

#### File Upload Response Example

```python
content_info["example"] = {
    "filename": "example.jpg",
    "id": 1,
    "created_at": "2025-06-23T00:00:00Z",
    "file_url": "/api/v1/uploads/example.jpg",
}
```

#### File Export Example

```python
content_info["example"] = {
    "files": [
        {
            "id": 1,
            "filename": "example.jpg",
            "created_at": "2025-06-23T00:00:00Z",
        }
    ]
}
```

**Example Benefits:**

- Clear API response structure understanding
- Better client code generation with realistic data
- Enhanced developer experience in API documentation
- Testing support with expected response formats

## Server Configuration

### 🌐 **Multi-Environment Server Setup**

#### Development Server

```python
{"url": "http://localhost:8000", "description": "Development server"}
```

#### Production Server

```python
{"url": "https://api.reviewpoint.org", "description": "Production server"}
```

**Server Configuration Benefits:**

- Environment-specific API base URLs
- Swagger UI server selection dropdown
- Client code generation with multiple environments
- Clear separation of dev/prod endpoints

## Usage Patterns

### 🔧 **FastAPI Application Integration**

```python
from fastapi import FastAPI
from src.core.openapi import setup_openapi

def create_app() -> FastAPI:
    """Create FastAPI application with enhanced OpenAPI schema."""
    app = FastAPI(
        title="ReViewPoint API",
        description="Modular, scalable, and LLM-powered platform for scientific paper review",
        version="1.0.0"
    )

    # Setup enhanced OpenAPI schema
    setup_openapi(app)

    # Add routers and middleware
    return app
```

### 📊 **OpenAPI Schema Access**

```python
# Access enhanced schema programmatically
app = create_app()
openapi_schema = app.openapi()

# Export schema for client generation
import json
with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)
```

### 🧪 **Testing Integration**

```python
from fastapi.testclient import TestClient
from src.main import app

def test_openapi_schema():
    """Test that OpenAPI schema is properly customized."""
    client = TestClient(app)

    # Test schema endpoint
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()

    # Verify custom metadata
    assert "contact" in schema["info"]
    assert schema["info"]["contact"]["name"] == "ReViewPoint Team"

    # Verify security schemes
    assert "securitySchemes" in schema["components"]
    security_schemes = schema["components"]["securitySchemes"]
    assert "BearerAuth" in security_schemes
    assert "ApiKeyAuth" in security_schemes
    assert "OAuth2PasswordBearer" in security_schemes

    # Verify tags
    tags = schema["tags"]
    tag_names = [tag["name"] for tag in tags]
    assert "Auth" in tag_names
    assert "User Management" in tag_names
    assert "Health" in tag_names
    assert "File" in tag_names
```

### 🔗 **Client Code Generation**

```bash
# Generate TypeScript client from enhanced OpenAPI schema
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o frontend/src/lib/api/generated

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o clients/python
```

**Generated Client Benefits:**

- Type-safe client code with proper interfaces
- Authentication handling for all security schemes
- Realistic mock data from examples
- Environment-aware base URL configuration

## API Documentation Enhancement

### 📚 **Swagger UI Improvements**

#### Enhanced Documentation Features

- **Contact Information**: Direct links to support and documentation
- **License Information**: Clear license terms and compliance
- **Server Selection**: Easy switching between development and production
- **Security Configuration**: Try-it-out functionality with authentication
- **Organized Endpoints**: Logical grouping by functionality
- **Response Examples**: Clear expected response formats

#### Developer Experience Features

```python
# Enhanced endpoint documentation with examples
operation["responses"]["200"]["content"]["application/json"]["example"] = {
    "realistic": "response data",
    "that": "helps developers",
    "understand": "expected format"
}
```

### 🎯 **API Testing Support**

#### Authentication Testing

- **Bearer Token**: JWT token input field in Swagger UI
- **API Key**: X-API-Key header configuration
- **OAuth2**: Password flow testing capability

#### Response Validation

- **Schema Validation**: Automatic response format validation
- **Example Verification**: Response examples match actual API responses
- **Error Documentation**: Comprehensive error response examples

## Performance Considerations

### ⚡ **Schema Generation Optimization**

#### Caching Strategy

```python
if hasattr(self, "openapi_schema") and self.openapi_schema is not None:
    return cast(dict[str, object], self.openapi_schema)
```

**Performance Benefits:**

- Single schema generation per application instance
- Cached schema for subsequent requests
- Reduced CPU overhead for /openapi.json requests

#### Memory Efficiency

```python
# Efficient schema modification in-place
openapi_schema["servers"] = list(SERVERS)
openapi_schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]
```

**Optimization Features:**

- In-place schema modification
- Minimal memory allocation for constants
- Efficient dictionary operations

### 🔄 **Runtime Performance**

#### Lazy Schema Generation

- Schema generated only when first requested
- No startup performance impact
- On-demand enhancement application

#### Efficient Type Checking

```python
if not isinstance(paths, dict):
    logger.error("OpenAPI schema missing 'paths' or not a dict")
    return self.openapi_schema
```

**Type Safety Features:**

- Runtime type validation for schema components
- Graceful handling of unexpected schema structures
- Comprehensive error logging for debugging

## Error Handling and Validation

### 🛠️ **Schema Validation**

#### Type Safety Enforcement

```python
if not isinstance(operation, dict):
    continue  # Skip invalid operations

if not isinstance(path_item, dict):
    continue  # Skip invalid path items
```

**Validation Features:**

- Runtime type checking for all schema modifications
- Graceful handling of malformed schema components
- Comprehensive logging for debugging schema issues

#### Error Recovery

```python
try:
    # Schema enhancement operations
    openapi_schema = original_openapi()
    logger.info("OpenAPI schema generated successfully")
except Exception as e:
    logger.error(f"Failed to generate OpenAPI schema: {e}")
    raise
```

**Error Handling:**

- Graceful fallback to original schema on errors
- Comprehensive error logging for debugging
- Exception propagation for critical failures

## Best Practices

### ✅ **Do's**

- **Call Early**: Setup OpenAPI enhancement during application initialization
- **Validate Schema**: Test that enhanced schema is valid OpenAPI 3.0 format
- **Monitor Changes**: Verify schema enhancement after FastAPI updates
- **Document Examples**: Provide realistic response examples for all endpoints
- **Test Security**: Verify authentication schemes work in Swagger UI
- **Version Control**: Include generated openapi.json in version control for reference

### ❌ **Don'ts**

- **Don't Modify Runtime**: Don't change OpenAPI configuration after app startup
- **Don't Hardcode URLs**: Use configuration for server URLs in different environments
- **Don't Skip Validation**: Always validate schema modifications
- **Don't Ignore Errors**: Log and handle schema generation errors properly
- **Don't Over-Customize**: Keep customizations maintainable and clear
- **Don't Break Standards**: Ensure enhanced schema remains OpenAPI 3.0 compliant

## Testing Strategies

### 🧪 **Schema Testing**

```python
def test_enhanced_openapi_schema():
    """Test comprehensive OpenAPI schema enhancement."""
    app = create_app()
    schema = app.openapi()

    # Test metadata enhancement
    assert schema["info"]["contact"]["name"] == "ReViewPoint Team"
    assert schema["info"]["license"]["name"] == "MIT License"

    # Test server configuration
    servers = schema["servers"]
    assert len(servers) == 2
    assert any(s["url"] == "http://localhost:8000" for s in servers)
    assert any(s["url"] == "https://api.reviewpoint.org" for s in servers)

    # Test security schemes
    security_schemes = schema["components"]["securitySchemes"]
    assert "BearerAuth" in security_schemes
    assert security_schemes["BearerAuth"]["type"] == "http"
    assert security_schemes["BearerAuth"]["scheme"] == "bearer"

    # Test endpoint tagging
    paths = schema["paths"]
    auth_login = paths["/api/v1/auth/login"]["post"]
    assert "Auth" in auth_login["tags"]
    assert auth_login["security"] == []  # No auth required for login

def test_endpoint_security_assignment():
    """Test automatic security requirement assignment."""
    app = create_app()
    schema = app.openapi()
    paths = schema["paths"]

    # Test protected endpoint
    users_endpoint = paths["/api/v1/users"]["get"]
    expected_security = [{"BearerAuth": []}, {"ApiKeyAuth": []}]
    assert users_endpoint["security"] == expected_security

    # Test public endpoint
    health_endpoint = paths["/api/v1/health"]["get"]
    assert health_endpoint["security"] == []
```

### 📋 **Integration Testing**

```python
def test_swagger_ui_accessibility():
    """Test that Swagger UI works with enhanced schema."""
    client = TestClient(app)

    # Test Swagger UI page
    response = client.get("/docs")
    assert response.status_code == 200

    # Test OpenAPI JSON endpoint
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    # Verify schema is valid OpenAPI 3.0
    assert "openapi" in schema
    assert schema["openapi"].startswith("3.")
```

## Related Files

- **`main.py`** - FastAPI application setup using OpenAPI enhancement
- **`api/`** - API endpoints that benefit from enhanced documentation
- **`security.py`** - JWT authentication integrated with OpenAPI security schemes
- **`config.py`** - Configuration values used in server and contact information
- **Frontend API client** - Generated from enhanced OpenAPI schema

## Dependencies

- **`fastapi`** - Core web framework with OpenAPI generation
- **`loguru`** - Logging for schema generation monitoring
- **`typing_extensions`** - Enhanced type annotations for schema structures

---

_This module provides comprehensive OpenAPI schema enhancement for the ReViewPoint backend, creating production-ready API documentation with proper security schemes, realistic examples, and enhanced developer experience features._
