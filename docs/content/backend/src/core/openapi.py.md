# openapi.py - OpenAPI Schema Customization and Enhancement

## Purpose

Provides comprehensive OpenAPI schema customization for the ReViewPoint API, enhancing the auto-generated FastAPI schema with detailed metadata, security schemes, endpoint categorization, and testing-specific examples. This module transforms the basic OpenAPI schema into a production-ready API documentation with proper authentication, tagging, and detailed response examples.

## Key Components

### Schema Enhancement System

#### **setup_openapi() Function**

- **Purpose**: Main entry point for OpenAPI schema customization and FastAPI integration
- **Design**: Replaces FastAPI's default OpenAPI generation with enhanced custom schema
- **Features**: Adds contact information, license details, security schemes, and endpoint categorization
- **Integration**: Seamlessly integrates with FastAPI application factory pattern

#### **custom_openapi() Method**

- **Purpose**: Comprehensive OpenAPI schema customization with caching and error handling
- **Design**: Wraps original FastAPI schema generation with extensive enhancements
- **Features**: Security scheme addition, endpoint tagging, authentication configuration, response examples
- **Performance**: Schema caching to prevent redundant generation

### Type Safety System

#### **Comprehensive TypedDict Definitions**

- **Purpose**: Type-safe OpenAPI schema manipulation with complete structure definitions
- **Design**: Exhaustive TypedDict coverage for all OpenAPI components
- **Benefits**: Compile-time type checking, IDE support, runtime type safety
- **Coverage**: Contact, license, servers, security schemes, tags, operations, responses

#### **Security Schema Types**

- **Purpose**: Type-safe security scheme definitions for multiple authentication methods
- **Types**: Bearer JWT, API Key, OAuth2 Password Flow
- **Structure**: Hierarchical type definitions for complex security configurations
- **Validation**: Ensures proper security scheme structure and configuration

### Authentication and Security

#### **Multi-Authentication Support**

- **Bearer Authentication**: JWT-based authentication for user sessions
- **API Key Authentication**: Service-to-service authentication via headers
- **OAuth2 Password Flow**: OAuth2 integration for token-based authentication
- **Endpoint-Specific Security**: Granular security requirements per endpoint

#### **Security Configuration**

```python
# Security schemes definition
SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter JWT token"
    },
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API key for service-to-service authentication"
    },
    "OAuth2PasswordBearer": {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "/api/v1/auth/login",
                "scopes": {}
            }
        }
    }
}
```

## Dependencies

### External Libraries

- **fastapi**: Core FastAPI framework for OpenAPI integration
- **loguru**: Structured logging for schema generation tracking
- **typing_extensions**: Enhanced type definitions for Python compatibility

### Internal Dependencies

- **No internal dependencies**: Standalone module for schema customization
- **FastAPI integration**: Direct integration with FastAPI application instances

### Type System Dependencies

- **collections.abc**: Abstract base classes for type definitions
- **typing**: Core typing system for type safety and documentation

## OpenAPI Schema Structure

### Information and Metadata

```python
# Application metadata
CONTACT = {
    "name": "ReViewPoint Team",
    "url": "https://github.com/your-org/reviewpoint",
    "email": "support@reviewpoint.org"
}

LICENSE_INFO = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT"
}

# Server configuration
SERVERS = [
    {"url": "http://localhost:8000", "description": "Development server"},
    {"url": "https://api.reviewpoint.org", "description": "Production server"}
]
```

### Endpoint Categorization

```python
# Endpoint tags for organization
TAGS = [
    {"name": "Auth", "description": "Authentication operations"},
    {"name": "User Management", "description": "User management operations"},
    {"name": "Health", "description": "Health check and monitoring endpoints"},
    {"name": "File", "description": "File upload and management operations"}
]
```

### Security Configuration

```python
# Non-authenticated endpoints
NON_AUTH_ENDPOINTS = [
    ("/api/v1/auth/login", "post"),
    ("/api/v1/auth/logout", "post"),
    ("/api/v1/auth/request-password-reset", "post"),
    ("/api/v1/auth/reset-password", "post"),
    ("/api/v1/health", "get"),
    ("/api/v1/metrics", "get")
]
```

## Schema Customization Process

### Enhanced Schema Generation

```python
def custom_openapi(self: FastAPI) -> dict[str, object]:
    """Comprehensive OpenAPI schema customization"""
    # Check for cached schema
    if hasattr(self, "openapi_schema") and self.openapi_schema is not None:
        return cast(dict[str, object], self.openapi_schema)

    # Generate base schema
    openapi_schema = original_openapi()
    logger.info("OpenAPI schema generated successfully")

    # Apply customizations
    enhance_metadata(openapi_schema)
    add_security_schemes(openapi_schema)
    configure_endpoint_security(openapi_schema)
    add_endpoint_tags(openapi_schema)
    add_response_examples(openapi_schema)

    # Cache and return
    self.openapi_schema = openapi_schema
    return openapi_schema
```

### Metadata Enhancement

```python
def enhance_metadata(schema: dict[str, object]) -> None:
    """Add contact information and license details"""
    if "info" in schema and isinstance(schema["info"], dict):
        info = schema["info"]
        info["contact"] = dict(CONTACT)
        info["license"] = dict(LICENSE_INFO)

    # Add server information
    schema["servers"] = list(SERVERS)
```

### Security Scheme Integration

```python
def add_security_schemes(schema: dict[str, object]) -> None:
    """Add comprehensive security schemes"""
    if "components" not in schema:
        schema["components"] = {}

    components = schema["components"]
    if isinstance(components, dict):
        components["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token"
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for service-to-service authentication"
            },
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/auth/login",
                        "scopes": {}
                    }
                }
            }
        }

    # Set global security requirements
    schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]
```

## Endpoint Security Configuration

### Authentication Requirements

```python
def configure_endpoint_security(schema: dict[str, object]) -> None:
    """Configure security requirements for each endpoint"""
    paths = schema.get("paths")
    if not isinstance(paths, dict):
        return

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue

            # Skip authentication for public endpoints
            if (path, method) in NON_AUTH_ENDPOINTS:
                operation["security"] = []
            # Special handling for /me endpoint (supports all auth methods)
            elif path == "/api/v1/auth/me" and method == "get":
                operation["security"] = [
                    {"BearerAuth": []},
                    {"ApiKeyAuth": []},
                    {"OAuth2PasswordBearer": []}
                ]
            # Standard endpoints require Bearer or API Key auth
            else:
                operation["security"] = [
                    {"BearerAuth": []},
                    {"ApiKeyAuth": []}
                ]
```

### Endpoint Tagging

```python
def add_endpoint_tags(schema: dict[str, object]) -> None:
    """Add tags to endpoints for organization"""
    paths = schema.get("paths")
    if not isinstance(paths, dict):
        return

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        # Determine tag based on path
        if "/api/v1/auth" in path:
            tag = "Auth"
        elif "/api/v1/users" in path:
            tag = "User Management"
        elif "/api/v1/health" in path or "/api/v1/metrics" in path:
            tag = "Health"
        elif "/api/v1/uploads" in path:
            tag = "File"
        else:
            tag = "General"

        # Apply tag to all methods
        for method in path_item:
            operation = path_item[method]
            if isinstance(operation, dict) and "tags" not in operation:
                operation["tags"] = [tag]
```

## Response Examples

### Example Data Definitions

```python
# User export example
EXAMPLE_USERS_EXPORT = {
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name"
        }
    ]
}

# File upload example
EXAMPLE_UPLOAD_RESPONSE = {
    "filename": "example.jpg",
    "id": 1,
    "created_at": "2025-06-23T00:00:00Z",
    "file_url": "/api/v1/uploads/example.jpg"
}

# File export example
EXAMPLE_UPLOADS_EXPORT = {
    "files": [
        {
            "id": 1,
            "filename": "example.jpg",
            "created_at": "2025-06-23T00:00:00Z"
        }
    ]
}
```

### Example Integration

```python
def add_response_examples(schema: dict[str, object]) -> None:
    """Add realistic examples to response schemas"""
    paths = schema.get("paths")
    if not isinstance(paths, dict):
        return

    for path, path_info in paths.items():
        if not isinstance(path_info, dict):
            continue

        # Add examples for export endpoints
        if "/api/v1/users/export" in path:
            add_users_export_example(path_info)
        elif "/api/v1/uploads/export" in path:
            add_uploads_export_example(path_info)
        elif path == "/api/v1/uploads" and "post" in path_info:
            add_upload_response_example(path_info["post"])
```

## Integration Patterns

### FastAPI Application Integration

```python
from fastapi import FastAPI
from core.openapi import setup_openapi

def create_app() -> FastAPI:
    """FastAPI application factory with OpenAPI customization"""
    app = FastAPI(
        title="ReViewPoint API",
        description="Modular, scalable, and LLM-powered platform for scientific paper review",
        version="1.0.0"
    )

    # Apply OpenAPI customizations
    setup_openapi(app)

    return app
```

### Schema Export for Frontend

```python
# Export schema for TypeScript generation
def export_openapi_schema(app: FastAPI, output_path: str) -> None:
    """Export OpenAPI schema to file for frontend code generation"""
    import json

    # Generate customized schema
    schema = app.openapi()

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2)

    logger.info(f"OpenAPI schema exported to {output_path}")
```

## Type Safety Features

### Comprehensive Type Definitions

```python
# Security scheme types
class SecuritySchemeBearerDict(TypedDict):
    type: Literal["http"]
    scheme: Literal["bearer"]
    bearerFormat: Literal["JWT"]
    description: str

class SecuritySchemeApiKeyDict(TypedDict):
    type: Literal["apiKey"]
    in_: Literal["header"]
    name: Literal["X-API-Key"]
    description: str

# Operation and path types
class OperationDict(TypedDict, total=False):
    tags: Sequence[str]
    security: Sequence[Mapping[str, Sequence[str]]]
    responses: dict[str, dict[str, object]]

class OpenAPISchemaDict(TypedDict, total=False):
    info: dict[str, object]
    servers: Sequence[ServerDict]
    components: dict[str, object]
    security: Sequence[Mapping[str, Sequence[str]]]
    tags: Sequence[TagDict]
    paths: dict[str, dict[str, OperationDict]]
```

### Type-Safe Schema Manipulation

```python
def safe_schema_update(schema: dict[str, object], updates: OpenAPISchemaDict) -> None:
    """Type-safe schema updates with validation"""
    # Validate schema structure
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary")

    # Apply updates with type checking
    for key, value in updates.items():
        if key in schema:
            # Merge nested dictionaries safely
            if isinstance(schema[key], dict) and isinstance(value, dict):
                schema[key].update(value)
            else:
                schema[key] = value
        else:
            schema[key] = value
```

## Error Handling

### Schema Generation Safety

```python
def custom_openapi(self: FastAPI) -> dict[str, object]:
    """Safe OpenAPI schema generation with error handling"""
    try:
        # Generate base schema
        openapi_schema = original_openapi()
        logger.info("OpenAPI schema generated successfully")

        # Apply customizations with error handling
        try:
            enhance_schema(openapi_schema)
            logger.info("OpenAPI schema customization applied")
        except Exception as e:
            logger.error(f"Schema customization failed: {e}")
            # Return base schema if customization fails
            return openapi_schema

        # Cache successful schema
        self.openapi_schema = openapi_schema
        return openapi_schema

    except Exception as e:
        logger.error(f"OpenAPI schema generation failed: {e}")
        # Return minimal schema as fallback
        return {"openapi": "3.0.0", "info": {"title": "API", "version": "1.0.0"}}
```

### Path Validation

```python
def validate_paths(paths: dict[str, object]) -> bool:
    """Validate OpenAPI paths structure"""
    if not isinstance(paths, dict):
        logger.error("OpenAPI schema missing 'paths' or not a dict")
        return False

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            logger.warning(f"Invalid path item for {path}")
            continue

        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                logger.warning(f"Invalid operation for {path} {method}")
                continue

    return True
```

## Performance Considerations

### Schema Caching

```python
def custom_openapi(self: FastAPI) -> dict[str, object]:
    """Optimized schema generation with caching"""
    # Check cache first
    if hasattr(self, "openapi_schema") and self.openapi_schema is not None:
        return cast(dict[str, object], self.openapi_schema)

    # Generate and cache schema
    schema = generate_enhanced_schema()
    self.openapi_schema = schema
    return schema
```

### Lazy Loading

- **On-demand generation**: Schema is only generated when first requested
- **Single generation**: Subsequent requests use cached schema
- **Memory efficient**: Schema is stored in FastAPI instance memory

### Efficient Updates

```python
def efficient_schema_update(schema: dict[str, object]) -> None:
    """Efficient schema updates minimizing object creation"""
    # Reuse existing objects where possible
    # Minimize deep copying
    # Use in-place updates for performance
```

## Usage Examples

### Basic Setup

```python
from fastapi import FastAPI
from core.openapi import setup_openapi

app = FastAPI()
setup_openapi(app)

# Schema is now enhanced with:
# - Contact information
# - License details
# - Security schemes
# - Endpoint tags
# - Response examples
```

### Custom Authentication

```python
@app.get("/api/v1/protected", tags=["Custom"])
def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Protected endpoint with automatic security documentation"""
    return {"message": "Protected data"}

# OpenAPI schema automatically includes:
# - Bearer authentication requirement
# - API key authentication alternative
# - Proper security documentation
```

### Schema Export

```python
# Export for frontend TypeScript generation
import json

schema = app.openapi()
with open("frontend/openapi-schema.json", "w") as f:
    json.dump(schema, f, indent=2)
```

## Testing Integration

### Schema Validation

```python
def test_openapi_schema():
    """Test OpenAPI schema generation and structure"""
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Validate schema structure
    assert "info" in schema
    assert "components" in schema
    assert "securitySchemes" in schema["components"]
    assert "BearerAuth" in schema["components"]["securitySchemes"]
```

### Security Scheme Testing

```python
def test_security_schemes():
    """Test security scheme configuration"""
    schema = app.openapi()
    security_schemes = schema["components"]["securitySchemes"]

    # Validate Bearer auth
    assert security_schemes["BearerAuth"]["type"] == "http"
    assert security_schemes["BearerAuth"]["scheme"] == "bearer"

    # Validate API key auth
    assert security_schemes["ApiKeyAuth"]["type"] == "apiKey"
    assert security_schemes["ApiKeyAuth"]["in"] == "header"
```

## Related Files

- **[main.py](../main.py.md)**: FastAPI application factory and OpenAPI setup
- **[config.py](config.py.md)**: Configuration settings for API metadata
- **[security.py](security.py.md)**: Authentication implementation matching OpenAPI security schemes
- **[../api/v1/auth.py](../api/v1/auth.py.md)**: Authentication endpoints with OpenAPI documentation

## Future Enhancements

### Planned Features

- **API versioning support**: Multiple API versions in single schema
- **Advanced examples**: Request/response examples from test data
- **Custom validators**: Runtime schema validation
- **Documentation themes**: Custom styling for API documentation

### Enhancement Patterns

```python
# Future: API versioning
def setup_versioned_openapi(app: FastAPI, version: str) -> None:
    """Enhanced OpenAPI setup with versioning support"""
    # Implementation for API versioning
    pass

# Future: Dynamic examples
def add_dynamic_examples(schema: dict[str, object]) -> None:
    """Add examples generated from test data"""
    # Implementation for dynamic example generation
    pass
```

The openapi.py module provides comprehensive OpenAPI schema enhancement, transforming FastAPI's auto-generated documentation into production-ready API documentation with proper security, organization, and examples for the ReViewPoint API.
