# Documentation Configuration Module

**File:** `backend/src/core/documentation.py`  
**Purpose:** Comprehensive OpenAPI/Swagger documentation configuration with enhanced metadata, examples, and code samples  
**Lines of Code:** 959  
**Type:** Core Infrastructure Module  

## Overview

The documentation module provides comprehensive OpenAPI specification enhancement for the ReViewPoint API. It transforms FastAPI's automatically generated OpenAPI schema into a production-ready API specification with rich metadata, realistic examples, code samples in multiple languages, detailed security scheme documentation, and enhanced developer experience features. This module is essential for creating professional API documentation that serves both interactive exploration and client code generation.

## Architecture

### Core Design Principles

1. **Comprehensive Enhancement**: Detailed API metadata with contact information, licensing, and server configurations
2. **Developer Experience**: Multi-language code samples and realistic response examples
3. **Security-First Documentation**: Clear authentication and authorization documentation
4. **Example-Rich Content**: Realistic data examples for all major API responses
5. **Code Sample Integration**: Ready-to-use code snippets in curl, Python, and JavaScript
6. **Type-Safe Configuration**: Full TypedDict definitions for OpenAPI schema components

### Key Components

#### API Metadata Configuration
```python
API_INFO: Final[APIInfo] = {
    "title": "ReViewPoint Core API",
    "description": "...",  # Comprehensive API description with features
    "version": "0.1.0",
    "terms_of_service": "https://reviewpoint.org/terms",
    "contact": {...},
    "license": {...}
}
```

**Metadata Features:**
- Comprehensive API description with feature breakdown
- Contact information for support and development
- MIT license information with URL
- Terms of service reference
- Version tracking for API evolution

#### Server Environment Configuration
```python
SERVERS: Final[Sequence[ServerInfo]] = [
    {"url": "https://api.reviewpoint.org", "description": "Production server"},
    {"url": "https://staging-api.reviewpoint.org", "description": "Staging server"},
    {"url": "http://localhost:8000", "description": "Local development server"}
]
```

**Server Configuration:**
- Production, staging, and development environments
- API versioning support through URL variables
- Environment-specific descriptions for clarity

## Core Functions

### 🔧 **Primary Enhancement Function**

#### `get_enhanced_openapi_schema()`
```python
def get_enhanced_openapi_schema(base_schema: dict[str, Any]) -> dict[str, Any]:
    """Enhance the base OpenAPI schema with comprehensive documentation."""
```

**Purpose:** Main function for comprehensive OpenAPI schema enhancement

**Enhancement Process:**
1. **API Info Update**: Adds comprehensive metadata from API_INFO configuration
2. **Server Configuration**: Sets up multi-environment server information
3. **Security Schemes**: Configures detailed authentication documentation
4. **Global Security**: Sets default authentication requirements
5. **Tag Addition**: Adds endpoint categorization tags
6. **Endpoint Enhancement**: Enriches individual endpoint documentation
7. **Example Integration**: Adds realistic response examples

**Schema Enhancement Features:**
```python
# Update core API metadata
base_schema["info"].update(API_INFO)

# Configure server environments
base_schema["servers"] = list(SERVERS)

# Add comprehensive security schemes
base_schema["components"]["securitySchemes"] = SECURITY_SCHEMES

# Set global authentication requirements
base_schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]
```

### 📝 **Endpoint Documentation Enhancement**

#### `_enhance_endpoint_documentation()`
```python
def _enhance_endpoint_documentation(paths: dict[str, Any]) -> None:
    """Enhance individual endpoint documentation with better descriptions and examples."""
```

**Purpose:** Comprehensive enhancement of individual API endpoints

**Enhancement Process:**
1. **Tag Assignment**: Automatic categorization based on URL patterns
2. **Security Configuration**: Authentication requirements per endpoint
3. **Code Sample Addition**: Multi-language code examples
4. **Response Example Enhancement**: Realistic response data

#### `_add_tags_to_endpoints()`
```python
def _add_tags_to_endpoints(path: str, path_item: dict[str, Any]) -> None:
    """Add appropriate tags to endpoints based on their paths."""
```

**Tag Assignment Logic:**
- `/auth` endpoints → "Auth" tag
- `/users` endpoints → "User Management" tag  
- `/uploads` endpoints → "File" tag
- `/health` or `/metrics` → "Health" tag
- `/ws` or `/websocket` → "WebSocket" tag

**Tag Benefits:**
- Logical endpoint grouping in Swagger UI
- Enhanced navigation and discoverability
- Consistent categorization across API

#### `_configure_endpoint_security()`
```python
def _configure_endpoint_security(path: str, path_item: dict[str, Any]) -> None:
    """Configure security requirements for endpoints."""
```

**Security Configuration Logic:**
- **Public Endpoints**: No authentication required (login, register, health)
- **User Profile Endpoint**: Multiple authentication options (Bearer, API Key, OAuth2)
- **Protected Endpoints**: Bearer token OR API key authentication
- **Special Cases**: Custom security requirements based on endpoint function

## Security Documentation

### 🔐 **Authentication Schemes**

#### Bearer Token Authentication
```python
"BearerAuth": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": """
**JWT Bearer Token Authentication**

Use this for web applications and user-specific operations.

**How to obtain a token:**
1. Register or login via `/api/v1/auth/login`
2. Include the token in the Authorization header
3. Format: `Authorization: Bearer YOUR_JWT_TOKEN`
"""
}
```

**JWT Documentation Features:**
- Clear token acquisition process
- Header format specification
- Token lifecycle information (24-hour access, 7-day refresh)
- Refresh token usage instructions

#### API Key Authentication
```python
"ApiKeyAuth": {
    "type": "apiKey",
    "in_": "header", 
    "name": "X-API-Key",
    "description": """
**API Key Authentication**

Use this for service-to-service communication and automation.

**Best practices:**
- Store keys securely (environment variables)
- Rotate keys regularly
- Use different keys for different environments
"""
}
```

**API Key Documentation Features:**
- Service-to-service authentication guidance
- Security best practices
- Header configuration details
- Key management recommendations

#### OAuth2 Flow Configuration
```python
"OAuth2PasswordBearer": {
    "type": "oauth2",
    "flows": {
        "password": {
            "tokenUrl": "/api/v1/auth/login",
            "scopes": {
                "read": "Read access to user data",
                "write": "Write access to user data", 
                "admin": "Administrative access"
            }
        }
    }
}
```

**OAuth2 Documentation Features:**
- Standard OAuth2 password flow
- Scope-based authorization documentation
- Token endpoint specification
- Clear scope descriptions

## Code Sample Integration

### 💻 **Multi-Language Code Examples**

#### Authentication Example
```python
CODE_SAMPLES["auth_login"] = {
    "curl": "curl -X POST...",      # Complete curl command
    "python": "import requests...", # Python requests example
    "javascript": "const response = await fetch..." # Modern JS/TS
}
```

#### File Upload Example
```python
CODE_SAMPLES["file_upload"] = {
    "curl": "curl -X POST ... -F 'file=@document.pdf'",
    "python": "files = {'file': ('document.pdf', open('document.pdf', 'rb'))}",
    "javascript": "formData.append('file', fileInput.files[0])"
}
```

#### WebSocket Connection Example
```python
CODE_SAMPLES["websocket_connection"] = {
    "python": """
import asyncio
import websockets
import json

async def connect_websocket():
    uri = "ws://localhost:8000/api/v1/ws/YOUR_JWT_TOKEN"
    async with websockets.connect(uri) as websocket:
        # Real-time communication example
    """,
    "javascript": """
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/YOUR_JWT_TOKEN');
ws.onopen = function(event) {
    console.log('Connected to WebSocket');
};
"""
}
```

**Code Sample Features:**
- Production-ready code examples
- Error handling demonstrations
- Best practices integration
- Environment-specific configurations

### 📋 **Response Examples**

#### User Data Example
```python
EXAMPLE_USER: Final[dict[str, Any]] = {
    "id": 123,
    "email": "user@example.com",
    "name": "Jane Doe",
    "bio": "Software developer passionate about scientific research",
    "avatar_url": "https://api.reviewpoint.org/files/avatars/123.jpg",
    "is_active": True,
    "is_admin": False,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:22:00Z"
}
```

#### File Metadata Example
```python
EXAMPLE_FILE: Final[dict[str, Any]] = {
    "id": 456,
    "filename": "research_paper.pdf",
    "content_type": "application/pdf",
    "size": 2048576,
    "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
    "upload_url": "https://api.reviewpoint.org/api/v1/uploads/456",
    "download_url": "https://api.reviewpoint.org/api/v1/uploads/456/download",
    "is_public": False,
    "uploaded_by": 123,
    "created_at": "2024-01-16T09:15:00Z",
    "updated_at": "2024-01-16T09:15:00Z"
}
```

#### Authentication Response Example
```python
EXAMPLE_AUTH_RESPONSE: Final[dict[str, Any]] = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": EXAMPLE_USER
}
```

#### Error Response Examples
```python
EXAMPLE_ERROR: Final[dict[str, Any]] = {
    "detail": "The provided credentials are invalid",
    "status": "error", 
    "feedback": "Please check your email and password and try again"
}

EXAMPLE_VALIDATION_ERROR: Final[dict[str, Any]] = {
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ],
    "status": "error",
    "feedback": "Please correct the validation errors and try again"
}
```

## Tag Organization

### 🏷️ **Endpoint Categorization**

#### Authentication Operations
```python
{
    "name": "Auth",
    "description": """
**Authentication operations**

Handle user authentication, registration, and session management.
All authentication endpoints use JWT tokens for secure access.

Key features:
- User registration and login
- JWT token management with refresh tokens
- Password reset functionality
- Rate limiting for security
""",
    "externalDocs": {
        "description": "Authentication Guide",
        "url": "https://docs.reviewpoint.org/auth"
    }
}
```

#### User Management Operations
```python
{
    "name": "User Management", 
    "description": """
**User profile and account management**

Comprehensive user management including profiles, preferences, and administration.
Supports role-based access control and user analytics.

Key features:
- User CRUD operations
- Profile management
- User analytics and reporting
- Data export capabilities
"""
}
```

#### File Operations
```python
{
    "name": "File",
    "description": """
**File upload and management operations**

Secure file handling with validation, virus scanning, and metadata management.
Supports various file types with size and content restrictions.

Key features:
- Secure file upload with validation
- File metadata and versioning
- Bulk operations and export
- Virus scanning and security checks
"""
}
```

## Usage Patterns

### 🔧 **FastAPI Integration**

```python
from fastapi import FastAPI
from src.core.documentation import get_enhanced_openapi_schema

def create_app() -> FastAPI:
    """Create FastAPI application with enhanced documentation."""
    app = FastAPI(
        title="ReViewPoint API",
        description="Scientific paper review platform",
        version="1.0.0"
    )
    
    # Override default OpenAPI schema generation
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        # Get base schema from FastAPI
        base_schema = app.openapi()
        
        # Enhance with comprehensive documentation
        enhanced_schema = get_enhanced_openapi_schema(base_schema)
        
        app.openapi_schema = enhanced_schema
        return enhanced_schema
    
    app.openapi = custom_openapi
    return app
```

### 📊 **Documentation Access**

```python
# Access enhanced schema
app = create_app()
enhanced_schema = app.openapi()

# Export for client generation
import json
with open("enhanced_openapi.json", "w") as f:
    json.dump(enhanced_schema, f, indent=2)

# Validate enhancement
assert "x-codeSamples" in enhanced_schema["paths"]["/api/v1/auth/login"]["post"]
assert enhanced_schema["info"]["contact"]["name"] == "ReViewPoint Team"
```

### 🧪 **Testing Integration**

```python
from fastapi.testclient import TestClient
from src.main import app

def test_enhanced_documentation():
    """Test that documentation enhancements are applied."""
    client = TestClient(app)
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    
    # Test enhanced metadata
    assert schema["info"]["contact"]["name"] == "ReViewPoint Team"
    assert schema["info"]["license"]["name"] == "MIT License"
    
    # Test server configuration
    servers = schema["servers"]
    assert len(servers) == 3
    assert any("production" in s["description"].lower() for s in servers)
    
    # Test security schemes
    security_schemes = schema["components"]["securitySchemes"]
    assert "BearerAuth" in security_schemes
    assert "ApiKeyAuth" in security_schemes
    assert "OAuth2PasswordBearer" in security_schemes
    
    # Test tags
    tags = schema["tags"]
    tag_names = [tag["name"] for tag in tags]
    assert "Auth" in tag_names
    assert "User Management" in tag_names
    assert "File" in tag_names
    assert "Health" in tag_names
    
    # Test code samples
    auth_login = schema["paths"]["/api/v1/auth/login"]["post"]
    assert "x-codeSamples" in auth_login
    code_samples = auth_login["x-codeSamples"]
    languages = [sample["lang"] for sample in code_samples]
    assert "curl" in languages
    assert "python" in languages
    assert "javascript" in languages

def test_response_examples():
    """Test that response examples are properly added."""
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    
    # Check component examples
    examples = schema["components"]["examples"]
    assert "UserExample" in examples
    assert "FileExample" in examples
    assert "AuthResponseExample" in examples
    assert "ErrorExample" in examples
```

## Configuration Management

### ⚙️ **Environment-Specific Configuration**

#### Development Configuration
```python
# Development server with detailed debugging
SERVERS[2] = {
    "url": "http://localhost:8000",
    "description": "Local development server",
    "variables": {
        "version": {"default": "v1", "description": "API version"}
    }
}
```

#### Production Configuration
```python
# Production server with SSL and CDN
SERVERS[0] = {
    "url": "https://api.reviewpoint.org", 
    "description": "Production server",
    "variables": {
        "version": {"default": "v1", "description": "API version"}
    }
}
```

#### Staging Configuration
```python
# Staging environment for testing
SERVERS[1] = {
    "url": "https://staging-api.reviewpoint.org",
    "description": "Staging server for testing",
    "variables": {
        "version": {"default": "v1", "description": "API version"}
    }
}
```

## Performance Considerations

### ⚡ **Schema Generation Optimization**

#### Efficient Enhancement Process
```python
try:
    logger.info("Enhancing OpenAPI schema with comprehensive documentation")
    
    # Batch updates for efficiency
    base_schema["info"].update(API_INFO)
    base_schema["servers"] = list(SERVERS)
    base_schema["components"]["securitySchemes"] = SECURITY_SCHEMES
    
    logger.info("OpenAPI schema enhancement completed successfully")
    return base_schema
    
except Exception as e:
    logger.error(f"Failed to enhance OpenAPI schema: {e}")
    raise
```

**Performance Features:**
- Single-pass schema enhancement
- Batch dictionary updates
- Minimal object creation
- Error handling without performance impact

#### Memory Efficiency
```python
# Reuse constant objects
base_schema["servers"] = list(SERVERS)  # Convert tuple to list once
base_schema["tags"] = list(TAGS)        # Efficient list creation
```

**Memory Optimization:**
- Constant object reuse
- Efficient list/dict operations
- Minimal memory allocation during enhancement

## Error Handling and Validation

### 🛠️ **Schema Validation**

#### Enhancement Error Handling
```python
try:
    # Schema enhancement operations
    enhanced_schema = get_enhanced_openapi_schema(base_schema)
    logger.info("Schema enhancement successful")
    return enhanced_schema
    
except Exception as e:
    logger.error(f"Schema enhancement failed: {e}")
    # Return base schema as fallback
    return base_schema
```

#### Response Example Validation
```python
def _add_response_examples(responses: dict[str, Any]) -> None:
    """Add comprehensive examples to response schemas."""
    for status_code, response in responses.items():
        if not isinstance(response, dict) or "content" not in response:
            continue  # Skip invalid response structures
            
        # Safe example addition with validation
        content = response["content"]
        for media_type, media_info in content.items():
            if isinstance(media_info, dict):
                # Add appropriate examples based on context
                _add_contextual_examples(status_code, media_info)
```

## Best Practices

### ✅ **Do's**

- **Use Early**: Apply documentation enhancement during app initialization
- **Test Thoroughly**: Validate enhanced schema structure and content
- **Keep Examples Current**: Update examples when API changes
- **Provide Code Samples**: Include multi-language examples for key endpoints
- **Document Security**: Clearly explain authentication requirements and methods
- **Version Consistently**: Keep API version in sync across documentation

### ❌ **Don'ts**

- **Don't Hardcode URLs**: Use configuration for server URLs
- **Don't Skip Validation**: Always validate schema enhancement results
- **Don't Over-Enhance**: Keep enhancements focused and maintainable
- **Don't Ignore Errors**: Handle enhancement failures gracefully
- **Don't Break Standards**: Ensure enhanced schema remains OpenAPI 3.0 compliant
- **Don't Forget Updates**: Keep documentation in sync with code changes

## Testing Strategies

### 🧪 **Documentation Testing**

```python
def test_comprehensive_schema_enhancement():
    """Test all aspects of schema enhancement."""
    base_schema = {"info": {}, "paths": {}}
    enhanced = get_enhanced_openapi_schema(base_schema)
    
    # Test metadata enhancement
    assert enhanced["info"]["title"] == "ReViewPoint Core API"
    assert enhanced["info"]["contact"]["email"] == "support@reviewpoint.org"
    
    # Test server configuration
    assert len(enhanced["servers"]) == 3
    server_urls = [s["url"] for s in enhanced["servers"]]
    assert "https://api.reviewpoint.org" in server_urls
    
    # Test security configuration
    security_schemes = enhanced["components"]["securitySchemes"]
    assert "BearerAuth" in security_schemes
    assert security_schemes["BearerAuth"]["type"] == "http"
    
    # Test examples
    examples = enhanced["components"]["examples"]
    assert "UserExample" in examples
    assert examples["UserExample"]["value"]["email"] == "user@example.com"

def test_code_sample_integration():
    """Test that code samples are properly integrated."""
    # Mock FastAPI path structure
    paths = {
        "/api/v1/auth/login": {
            "post": {"operationId": "login"}
        }
    }
    
    _add_endpoint_examples("/api/v1/auth/login", paths["/api/v1/auth/login"])
    
    operation = paths["/api/v1/auth/login"]["post"]
    assert "x-codeSamples" in operation
    
    code_samples = operation["x-codeSamples"]
    languages = [sample["lang"] for sample in code_samples]
    assert "curl" in languages
    assert "python" in languages
    assert "javascript" in languages
```

## Related Files

- **`openapi.py`** - Basic OpenAPI schema customization (this module extends it)
- **`main.py`** - FastAPI application setup using enhanced documentation
- **API routers** - All routers benefit from enhanced documentation
- **Frontend type generation** - Uses enhanced schema for client code generation
- **Testing utilities** - API testing using documented endpoints and examples

## Dependencies

- **`fastapi`** - Core web framework with OpenAPI generation
- **`loguru`** - Logging for enhancement process monitoring
- **`typing_extensions`** - Enhanced type annotations for schema structures

---

*This module provides comprehensive OpenAPI documentation enhancement for the ReViewPoint backend, creating production-ready API documentation with rich metadata, multi-language code samples, realistic examples, and enhanced developer experience features essential for professional API consumption.*
