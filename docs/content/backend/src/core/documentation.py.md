# documentation.py - Comprehensive OpenAPI Documentation Configuration

## Purpose

Provides extensive OpenAPI/Swagger documentation configuration for the ReViewPoint Core API, featuring enhanced metadata, detailed examples, code samples, and comprehensive developer experience optimizations. This module transforms basic API documentation into production-ready, developer-friendly documentation with extensive examples, code samples, and detailed descriptions.

## Key Components

### Documentation Metadata System

#### **API Information Configuration**

- **Purpose**: Comprehensive API metadata including title, description, contact, and license information
- **Design**: Structured TypedDict definitions for type-safe documentation configuration
- **Features**: Rich markdown descriptions, external links, SDK references, and support information
- **Content**: Detailed API overview, feature descriptions, usage patterns, and community resources

#### **Server Configuration**

- **Purpose**: Multi-environment server configuration with variables and descriptions
- **Environments**: Production, staging, and local development servers
- **Features**: Environment-specific URLs, version variables, and descriptive metadata
- **Flexibility**: Configurable server variables for different deployment scenarios

### Enhanced Documentation Features

#### **Tag System**

- **Purpose**: Comprehensive endpoint categorization with detailed descriptions and external documentation
- **Categories**: Authentication, User Management, File Management, Health Monitoring, WebSocket Communication
- **Enhancement**: Rich descriptions with feature lists, key capabilities, and external documentation links
- **Organization**: Logical grouping for improved API navigation and discoverability

#### **Security Scheme Documentation**

- **Purpose**: Detailed security scheme configuration with comprehensive authentication options
- **Methods**: Bearer JWT, API Key, OAuth2 Password Flow
- **Documentation**: Detailed descriptions, usage examples, scope definitions, and integration guides
- **Developer Experience**: Clear authentication instructions and code examples

### Code Sample Integration

#### **Multi-Language Code Samples**

- **Purpose**: Comprehensive code examples in multiple programming languages
- **Languages**: cURL, Python, JavaScript/TypeScript
- **Coverage**: Authentication, file upload, user management, health checks, WebSocket connections
- **Quality**: Production-ready code with error handling and best practices

#### **Example Data Definitions**

- **Purpose**: Realistic example data for requests and responses
- **Coverage**: Users, files, authentication responses, error responses, validation errors
- **Quality**: Comprehensive, realistic data that reflects actual API usage
- **Consistency**: Standardized example formats across all endpoints

## Dependencies

### External Libraries

- **loguru**: Structured logging for documentation generation and debugging
- **typing_extensions**: Enhanced type definitions for comprehensive type safety

### Internal Dependencies

- **No internal dependencies**: Standalone module for documentation configuration
- **FastAPI integration**: Designed for seamless FastAPI OpenAPI integration

### Type System Dependencies

- **collections.abc**: Abstract base classes for sequence and mapping types
- **typing**: Comprehensive type hints for documentation structures and configurations

## Documentation Structure

### API Information

```python
API_INFO = {
    "title": "ReViewPoint Core API",
    "description": """
# ReViewPoint Core API

A modular scientific paper review platform providing comprehensive APIs for:

## 🔐 Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- API key authentication for service-to-service communication
- Password reset and account management

## 👥 User Management
- User registration, profile management, and administration
- User export functionality for data portability
- Comprehensive user analytics and reporting

## 📁 File Management
- Secure file upload with validation
- File metadata and versioning
- Bulk operations and export
- Virus scanning and security checks
""",
    "version": "0.1.0",
    "terms_of_service": "https://reviewpoint.org/terms",
    "contact": {
        "name": "ReViewPoint Team",
        "url": "https://github.com/your-org/reviewpoint",
        "email": "support@reviewpoint.org"
    },
    "license": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
}
```

### Server Configuration

```python
SERVERS = [
    {
        "url": "https://api.reviewpoint.org",
        "description": "Production server",
        "variables": {"version": {"default": "v1", "description": "API version"}}
    },
    {
        "url": "https://staging-api.reviewpoint.org",
        "description": "Staging server for testing",
        "variables": {"version": {"default": "v1", "description": "API version"}}
    },
    {
        "url": "http://localhost:8000",
        "description": "Local development server",
        "variables": {"version": {"default": "v1", "description": "API version"}}
    }
]
```

### Tag System

```python
TAGS = [
    {
        "name": "Auth",
        "description": """
**Authentication and authorization endpoints**

Comprehensive authentication system supporting multiple methods:
- JWT tokens with refresh capability
- API key authentication for services
- OAuth2 password flow integration
- Password reset and account management

Key features:
- Secure token-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication support
- Session management and security
""",
        "externalDocs": {
            "description": "Authentication Guide",
            "url": "https://docs.reviewpoint.org/auth"
        }
    }
    # Additional tags for User Management, File Management, Health, WebSocket
]
```

## Security Documentation

### Security Schemes

```python
SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": """
**JWT Bearer Authentication**

Use JWT tokens for user authentication. Include the token in the Authorization header:

`Authorization: Bearer <your_jwt_token>`

**Token lifecycle:**
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Use `/api/v1/auth/refresh` to obtain new access tokens

**Security considerations:**
- Store tokens securely (never in localStorage for production)
- Implement proper token refresh logic
- Handle token expiration gracefully
"""
    },
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": """
**API Key Authentication**

Use API keys for service-to-service authentication. Include the key in the X-API-Key header:

`X-API-Key: <your_api_key>`

**Best practices:**
- Rotate API keys regularly
- Use different keys for different environments
- Monitor API key usage and revoke if compromised
- Never commit API keys to version control
"""
    },
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
        },
        "description": """
**OAuth2 Password Flow**

Standard OAuth2 password flow for third-party integrations.

**Supported scopes:**
- `read`: Read access to user data
- `write`: Write access to user data
- `admin`: Administrative access

**Usage:**
Use the `/api/v1/auth/login` endpoint to exchange credentials for tokens.
"""
    }
}
```

### Public Endpoints

```python
PUBLIC_ENDPOINTS = [
    ("/api/v1/auth/login", "post"),
    ("/api/v1/auth/register", "post"),
    ("/api/v1/auth/request-password-reset", "post"),
    ("/api/v1/auth/reset-password", "post"),
    ("/api/v1/health", "get"),
    ("/api/v1/metrics", "get"),
    ("/docs", "get"),
    ("/redoc", "get"),
    ("/openapi.json", "get")
]
```

## Example Data System

### Comprehensive Example Definitions

```python
EXAMPLE_USER = {
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

EXAMPLE_FILE = {
    "id": 456,
    "filename": "research_paper.pdf",
    "content_type": "application/pdf",
    "size": 2048576,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:22:00Z",
    "download_url": "https://api.reviewpoint.org/api/v1/files/456/download"
}

EXAMPLE_AUTH_RESPONSE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": EXAMPLE_USER
}
```

### Error Response Examples

```python
EXAMPLE_ERROR = {
    "detail": "The requested resource was not found",
    "error_code": "RESOURCE_NOT_FOUND",
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/users/999"
}

EXAMPLE_VALIDATION_ERROR = {
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "password"],
            "msg": "ensure this value has at least 8 characters",
            "type": "value_error.any_str.min_length",
            "ctx": {"limit_value": 8}
        }
    ]
}
```

## Code Sample System

### Multi-Language Code Examples

```python
CODE_SAMPLES = {
    "auth_login": {
        "curl": """
curl -X POST "https://api.reviewpoint.org/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
""".strip(),
        "python": """
import requests

response = requests.post(
    "https://api.reviewpoint.org/api/v1/auth/login",
    json={
        "email": "user@example.com",
        "password": "your_password"
    }
)

if response.status_code == 200:
    data = response.json()
    access_token = data["access_token"]
    print(f"Login successful! Token: {access_token[:20]}...")
else:
    print(f"Login failed: {response.json()}")
""".strip(),
        "javascript": """
const response = await fetch('https://api.reviewpoint.org/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'your_password'
  })
});

if (response.ok) {
  const data = await response.json();
  const accessToken = data.access_token;
  console.log(`Login successful! Token: ${accessToken.substring(0, 20)}...`);
} else {
  const error = await response.json();
  console.error('Login failed:', error);
}
""".strip()
    }
}
```

### File Upload Examples

```python
"file_upload": {
    "curl": """
curl -X POST "https://api.reviewpoint.org/api/v1/uploads" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "file=@document.pdf" \\
  -F "description=Research paper for review"
""".strip(),
    "python": """
import requests

with open('document.pdf', 'rb') as file:
    response = requests.post(
        "https://api.reviewpoint.org/api/v1/uploads",
        headers={
            "Authorization": "Bearer YOUR_JWT_TOKEN"
        },
        files={"file": file},
        data={"description": "Research paper for review"}
    )

if response.status_code == 201:
    file_data = response.json()
    print(f"File uploaded successfully! ID: {file_data['id']}")
else:
    print(f"Upload failed: {response.json()}")
""".strip(),
    "javascript": """
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('description', 'Research paper for review');

const response = await fetch('https://api.reviewpoint.org/api/v1/uploads', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: formData
});

if (response.ok) {
  const fileData = await response.json();
  console.log(`File uploaded successfully! ID: ${fileData.id}`);
} else {
  const error = await response.json();
  console.error('Upload failed:', error);
}
""".strip()
}
```

## Documentation Enhancement Functions

### Schema Enhancement

```python
def enhance_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Enhance OpenAPI schema with comprehensive documentation.
    
    Args:
        schema: Base OpenAPI schema from FastAPI
        
    Returns:
        Enhanced schema with detailed documentation
    """
    try:
        # Add API information
        schema.update({
            "info": API_INFO,
            "servers": SERVERS,
            "tags": TAGS
        })
        
        # Add security schemes
        if "components" not in schema:
            schema["components"] = {}
        schema["components"]["securitySchemes"] = SECURITY_SCHEMES
        
        # Enhance paths with examples and code samples
        if "paths" in schema:
            _enhance_paths(schema["paths"])
        
        logger.info("OpenAPI schema enhancement completed successfully")
        return schema
        
    except Exception as e:
        logger.error(f"Failed to enhance OpenAPI schema: {e}")
        return schema
```

### Path Enhancement

```python
def _enhance_paths(paths: dict[str, Any]) -> None:
    """Enhance individual paths with examples and code samples."""
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            
            # Add code samples
            _add_code_samples(operation, path, method)
            
            # Add response examples
            if "responses" in operation:
                _add_response_examples(operation["responses"])
            
            # Configure security
            _configure_operation_security(operation, path, method)
```

### Code Sample Integration

```python
def _add_code_samples(operation: dict[str, Any], path: str, method: str) -> None:
    """Add relevant code samples to operations."""
    if "/auth/login" in path and method == "post":
        operation["x-codeSamples"] = [
            {"lang": "curl", "source": CODE_SAMPLES["auth_login"]["curl"]},
            {"lang": "python", "source": CODE_SAMPLES["auth_login"]["python"]},
            {"lang": "javascript", "source": CODE_SAMPLES["auth_login"]["javascript"]}
        ]
    elif "/uploads" in path and method == "post":
        operation["x-codeSamples"] = [
            {"lang": "curl", "source": CODE_SAMPLES["file_upload"]["curl"]},
            {"lang": "python", "source": CODE_SAMPLES["file_upload"]["python"]},
            {"lang": "javascript", "source": CODE_SAMPLES["file_upload"]["javascript"]}
        ]
    # Additional code sample mappings...
```

### Response Example Enhancement

```python
def _add_response_examples(responses: dict[str, Any]) -> None:
    """Add comprehensive examples to response schemas."""
    for status_code, response in responses.items():
        if not isinstance(response, dict) or "content" not in response:
            continue
        
        content = response["content"]
        for media_type, media_info in content.items():
            if not isinstance(media_info, dict):
                continue
            
            if "examples" not in media_info:
                media_info["examples"] = {}
            
            # Add appropriate examples based on status code and content
            if status_code in ["200", "201"]:
                if "user" in str(media_info).lower():
                    media_info["examples"]["default"] = {"value": EXAMPLE_USER}
                elif "file" in str(media_info).lower():
                    media_info["examples"]["default"] = {"value": EXAMPLE_FILE}
                elif "auth" in str(media_info).lower() or "token" in str(media_info).lower():
                    media_info["examples"]["default"] = {"value": EXAMPLE_AUTH_RESPONSE}
            elif status_code == "422":
                media_info["examples"]["default"] = {"value": EXAMPLE_VALIDATION_ERROR}
            elif status_code in ["400", "401", "403", "404", "429", "500"]:
                media_info["examples"]["default"] = {"value": EXAMPLE_ERROR}
```

## Type Safety System

### Comprehensive Type Definitions

```python
class APIInfo(TypedDict):
    """API information for OpenAPI metadata."""
    title: str
    description: str
    version: str
    terms_of_service: str
    contact: ContactInfo
    license: LicenseInfo

class ContactInfo(TypedDict):
    """Contact information for API documentation."""
    name: str
    url: str
    email: str

class LicenseInfo(TypedDict):
    """License information for API documentation."""
    name: str
    url: str

class ServerInfo(TypedDict):
    """Server information for different environments."""
    url: str
    description: str
    variables: dict[str, dict[str, str]]

class TagInfo(TypedDict):
    """Tag information for endpoint grouping."""
    name: str
    description: str
    externalDocs: dict[str, str]

class SecurityScheme(TypedDict, total=False):
    """Security scheme configuration."""
    type: Literal["http", "apiKey", "oauth2", "openIdConnect"]
    scheme: str
    bearerFormat: str
    description: str
    name: str
    in_: Literal["query", "header", "cookie"]
    flows: dict[str, Any]

class ExampleValue(TypedDict):
    """Example value for request/response."""
    summary: str
    description: str
    value: dict[str, Any]
```

## Integration Patterns

### FastAPI Integration

```python
from fastapi import FastAPI
from core.documentation import enhance_openapi_schema

def create_documented_app() -> FastAPI:
    """Create FastAPI app with enhanced documentation."""
    app = FastAPI()
    
    # Override OpenAPI schema generation
    original_openapi = app.openapi
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        # Generate base schema
        openapi_schema = original_openapi()
        
        # Apply enhancements
        enhanced_schema = enhance_openapi_schema(openapi_schema)
        
        app.openapi_schema = enhanced_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    return app
```

### Development Server Integration

```python
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    # Apply documentation enhancements
    enhanced_app = create_documented_app()
    
    # Serve with comprehensive documentation
    uvicorn.run(
        enhanced_app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

## Performance Considerations

### Schema Caching

- **Lazy generation**: Documentation is only generated when first requested
- **Caching**: Enhanced schema is cached to prevent redundant processing
- **Memory efficiency**: Type-safe structures minimize memory overhead

### Code Sample Optimization

```python
# Efficient code sample storage and retrieval
CODE_SAMPLES_CACHE = {}

def get_code_samples(endpoint_key: str) -> list[dict[str, str]]:
    """Retrieve code samples with caching."""
    if endpoint_key not in CODE_SAMPLES_CACHE:
        CODE_SAMPLES_CACHE[endpoint_key] = _generate_code_samples(endpoint_key)
    
    return CODE_SAMPLES_CACHE[endpoint_key]
```

## Usage Examples

### Basic Documentation Enhancement

```python
from fastapi import FastAPI
from core.documentation import enhance_openapi_schema

app = FastAPI()

# Apply comprehensive documentation
@app.on_event("startup")
async def enhance_docs():
    schema = app.openapi()
    app.openapi_schema = enhance_openapi_schema(schema)
```

### Custom Code Sample Addition

```python
# Add custom code samples for specific endpoints
custom_samples = {
    "my_endpoint": {
        "curl": "curl -X GET ...",
        "python": "import requests...",
        "javascript": "fetch('...')..."
    }
}

# Merge with existing samples
CODE_SAMPLES.update(custom_samples)
```

## Related Files

- **[openapi.py](openapi.py.md)**: Basic OpenAPI schema customization and setup
- **[main.py](../main.py.md)**: FastAPI application factory and documentation integration
- **[config.py](config.py.md)**: Configuration settings for API metadata and documentation
- **[../api/v1/auth.py](../api/v1/auth.py.md)**: Authentication endpoints with enhanced documentation

## Future Enhancements

### Planned Features

- **Interactive tutorials**: Step-by-step API integration guides
- **SDK generation**: Automatic client SDK generation from enhanced schema
- **Localization**: Multi-language documentation support
- **Advanced examples**: Real-world use case examples and tutorials

### Enhancement Patterns

```python
# Future: Interactive tutorial integration
def add_interactive_tutorials(schema: dict[str, Any]) -> None:
    """Add interactive tutorials to API documentation."""
    # Implementation for interactive documentation features
    pass

# Future: SDK documentation
def generate_sdk_documentation(schema: dict[str, Any]) -> dict[str, Any]:
    """Generate SDK-specific documentation."""
    # Implementation for SDK documentation generation
    pass
```

The documentation.py module provides comprehensive, production-ready OpenAPI documentation enhancement, transforming basic API schemas into developer-friendly documentation with extensive examples, code samples, and detailed descriptions for the ReViewPoint API.
