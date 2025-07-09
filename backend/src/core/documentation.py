"""
OpenAPI Documentation Configuration Module

This module provides comprehensive OpenAPI/Swagger documentation configuration
for the ReViewPoint Core API, including enhanced metadata, examples, and 
code samples for optimal developer experience.
"""

from collections.abc import Mapping, Sequence
from typing import Any, Final, Literal, TypedDict

from loguru import logger


# --- Documentation Metadata ---

class APIInfo(TypedDict):
    """API information for OpenAPI metadata."""
    title: str
    description: str
    version: str
    terms_of_service: str
    contact: "ContactInfo"
    license: "LicenseInfo"


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


# --- Configuration Constants ---

API_INFO: Final[APIInfo] = {
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
- Secure file upload with validation and virus scanning
- File metadata management and versioning
- Bulk operations and file export capabilities

## 🏥 Health & Monitoring
- Real-time health checks and system status
- Performance metrics and monitoring endpoints
- Service availability and dependency checks

## 🔌 Real-time Communication
- WebSocket support for real-time notifications
- Event-driven architecture for scalable communication

---

## Getting Started

### Authentication

Most endpoints require authentication. Use one of these methods:

1. **Bearer Token (Recommended for web apps):**
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" https://api.reviewpoint.org/api/v1/users
   ```

2. **API Key (For service-to-service):**
   ```bash
   curl -H "X-API-Key: YOUR_API_KEY" https://api.reviewpoint.org/api/v1/users
   ```

### Rate Limiting

API requests are rate-limited to ensure fair usage:
- Authentication endpoints: 10 requests per minute
- File uploads: 5 requests per minute  
- General endpoints: 100 requests per minute

### Error Handling

All errors follow a consistent format:
```json
{
  "detail": "Error description",
  "status": "error",
  "feedback": "User-friendly error message"
}
```

### Pagination

List endpoints support pagination:
```
GET /api/v1/users?page=1&size=20&sort=created_at&order=desc
```

---

## SDKs and Libraries

- **Python SDK:** [reviewpoint-python](https://github.com/your-org/reviewpoint-python)
- **JavaScript/TypeScript:** [reviewpoint-js](https://github.com/your-org/reviewpoint-js)
- **Go SDK:** [reviewpoint-go](https://github.com/your-org/reviewpoint-go)

## Support

- 📖 **Documentation:** [docs.reviewpoint.org](https://docs.reviewpoint.org)
- 💬 **Community:** [Discord](https://discord.gg/reviewpoint)
- 🐛 **Issues:** [GitHub Issues](https://github.com/your-org/reviewpoint/issues)
- 📧 **Email:** support@reviewpoint.org
""",
    "version": "0.1.0",
    "terms_of_service": "https://reviewpoint.org/terms",
    "contact": {
        "name": "ReViewPoint Team",
        "url": "https://github.com/your-org/reviewpoint",
        "email": "support@reviewpoint.org",
    },
    "license": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
}

SERVERS: Final[Sequence[ServerInfo]] = [
    {
        "url": "https://api.reviewpoint.org",
        "description": "Production server",
        "variables": {
            "version": {
                "default": "v1",
                "description": "API version"
            }
        }
    },
    {
        "url": "https://staging-api.reviewpoint.org", 
        "description": "Staging server for testing",
        "variables": {
            "version": {
                "default": "v1",
                "description": "API version"
            }
        }
    },
    {
        "url": "http://localhost:8000",
        "description": "Local development server",
        "variables": {
            "version": {
                "default": "v1", 
                "description": "API version"
            }
        }
    },
]

TAGS: Final[Sequence[TagInfo]] = [
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
    },
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
""",
        "externalDocs": {
            "description": "User Management Guide",
            "url": "https://docs.reviewpoint.org/users"
        }
    },
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
""",
        "externalDocs": {
            "description": "File Management Guide", 
            "url": "https://docs.reviewpoint.org/files"
        }
    },
    {
        "name": "Health",
        "description": """
**Health check and monitoring endpoints**

System health monitoring and performance metrics for ensuring service availability.
No authentication required for basic health checks.

Key features:
- Real-time health status
- Performance metrics
- Dependency checks
- Service availability monitoring
""",
        "externalDocs": {
            "description": "Monitoring Guide",
            "url": "https://docs.reviewpoint.org/monitoring"
        }
    },
    {
        "name": "WebSocket",
        "description": """
**Real-time communication via WebSocket**

WebSocket endpoints for real-time features like notifications and live updates.
Requires authentication for most channels.

Key features:
- Real-time notifications
- Live collaboration features
- Event-driven updates
- Connection management
""",
        "externalDocs": {
            "description": "WebSocket Guide",
            "url": "https://docs.reviewpoint.org/websocket"
        }
    },
]

SECURITY_SCHEMES: Final[dict[str, SecurityScheme]] = {
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

**Token lifecycle:**
- Access tokens expire in 24 hours
- Refresh tokens expire in 7 days
- Use `/api/v1/auth/refresh` to get new tokens
""",
    },
    "ApiKeyAuth": {
        "type": "apiKey",
        "in_": "header",
        "name": "X-API-Key",
        "description": """
**API Key Authentication**

Use this for service-to-service communication and automation.

**How to obtain an API key:**
1. Contact support@reviewpoint.org
2. Include the key in the X-API-Key header
3. Format: `X-API-Key: YOUR_API_KEY`

**Best practices:**
- Store keys securely (environment variables)
- Rotate keys regularly
- Use different keys for different environments
""",
    },
    "OAuth2PasswordBearer": {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "/api/v1/auth/login",
                "scopes": {
                    "read": "Read access to user data",
                    "write": "Write access to user data", 
                    "admin": "Administrative access",
                },
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
""",
    },
}

# --- Public Endpoints (No Authentication Required) ---

PUBLIC_ENDPOINTS: Final[Sequence[tuple[str, str]]] = [
    ("/api/v1/auth/login", "post"),
    ("/api/v1/auth/register", "post"),
    ("/api/v1/auth/request-password-reset", "post"),
    ("/api/v1/auth/reset-password", "post"),
    ("/api/v1/health", "get"),
    ("/api/v1/metrics", "get"),
    ("/docs", "get"),
    ("/redoc", "get"),
    ("/openapi.json", "get"),
]

# --- Common Examples ---

EXAMPLE_USER: Final[dict[str, Any]] = {
    "id": 123,
    "email": "user@example.com",
    "name": "Jane Doe",
    "bio": "Software developer passionate about scientific research",
    "avatar_url": "https://api.reviewpoint.org/files/avatars/123.jpg",
    "is_active": True,
    "is_admin": False,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:22:00Z",
}

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
    "updated_at": "2024-01-16T09:15:00Z",
}

EXAMPLE_AUTH_RESPONSE: Final[dict[str, Any]] = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": EXAMPLE_USER,
}

EXAMPLE_ERROR: Final[dict[str, Any]] = {
    "detail": "The provided credentials are invalid",
    "status": "error", 
    "feedback": "Please check your email and password and try again",
}

EXAMPLE_VALIDATION_ERROR: Final[dict[str, Any]] = {
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ["body", "password"],
            "msg": "ensure this value has at least 8 characters",
            "type": "value_error.any_str.min_length",
            "ctx": {"limit_value": 8},
        },
    ],
    "status": "error",
    "feedback": "Please correct the validation errors and try again",
}

# --- Code Samples ---

CODE_SAMPLES: Final[dict[str, dict[str, str]]] = {
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
        """.strip(),
    },
    "file_upload": {
        "curl": """
curl -X POST "https://api.reviewpoint.org/api/v1/uploads" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "file=@document.pdf" \\
  -F "description=Research paper draft"
        """.strip(),
        "python": """
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

files = {
    "file": ("document.pdf", open("document.pdf", "rb"), "application/pdf")
}

data = {
    "description": "Research paper draft"
}

response = requests.post(
    "https://api.reviewpoint.org/api/v1/uploads",
    headers=headers,
    files=files,
    data=data
)

if response.status_code == 201:
    file_data = response.json()
    print(f"Upload successful! File ID: {file_data['id']}")
else:
    print(f"Upload failed: {response.json()}")
        """.strip(),
        "javascript": """
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('description', 'Research paper draft');

const response = await fetch('https://api.reviewpoint.org/api/v1/uploads', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: formData
});

if (response.ok) {
  const fileData = await response.json();
  console.log(`Upload successful! File ID: ${fileData.id}`);
} else {
  const error = await response.json();
  console.error('Upload failed:', error);
}
        """.strip(),
    },
    "health_check": {
        "curl": """
curl -X GET "https://api.reviewpoint.org/api/v1/health"
        """.strip(),
        "python": """
import requests

response = requests.get("https://api.reviewpoint.org/api/v1/health")

if response.status_code == 200:
    health_data = response.json()
    print(f"API Status: {health_data['status']}")
    print(f"Version: {health_data['version']}")
else:
    print(f"Health check failed: {response.status_code}")
        """.strip(),
        "javascript": """
const response = await fetch('https://api.reviewpoint.org/api/v1/health');

if (response.ok) {
  const healthData = await response.json();
  console.log(`API Status: ${healthData.status}`);
  console.log(`Version: ${healthData.version}`);
} else {
  console.error(`Health check failed: ${response.status}`);
}
        """.strip(),
    },
    "user_management": {
        "curl": """
curl -X GET "https://api.reviewpoint.org/api/v1/users" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "X-API-Key: YOUR_API_KEY"
        """.strip(),
        "python": """
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "X-API-Key": "YOUR_API_KEY"
}

response = requests.get(
    "https://api.reviewpoint.org/api/v1/users",
    headers=headers,
    params={"limit": 10, "offset": 0}
)

if response.status_code == 200:
    users_data = response.json()
    print(f"Found {users_data['total']} users")
    for user in users_data['users']:
        print(f"- {user['name']} ({user['email']})")
else:
    print(f"Failed to fetch users: {response.json()}")
        """.strip(),
        "javascript": """
const response = await fetch('https://api.reviewpoint.org/api/v1/users?limit=10&offset=0', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'X-API-Key': 'YOUR_API_KEY'
  }
});

if (response.ok) {
  const usersData = await response.json();
  console.log(`Found ${usersData.total} users`);
  usersData.users.forEach(user => {
    console.log(`- ${user.name} (${user.email})`);
  });
} else {
  const error = await response.json();
  console.error('Failed to fetch users:', error);
}
        """.strip(),
    },
}


def get_enhanced_openapi_schema(base_schema: dict[str, Any]) -> dict[str, Any]:
    """
    Enhance the base OpenAPI schema with comprehensive documentation.
    
    Args:
        base_schema: Base OpenAPI schema from FastAPI
        
    Returns:
        Enhanced OpenAPI schema with better documentation
        
    Raises:
        Exception: If schema enhancement fails
    """
    try:
        logger.info("Enhancing OpenAPI schema with comprehensive documentation")
        
        # Update API info
        if "info" not in base_schema:
            base_schema["info"] = {}
            
        base_schema["info"].update(API_INFO)
        
        # Add servers
        base_schema["servers"] = list(SERVERS)
        
        # Add security schemes
        if "components" not in base_schema:
            base_schema["components"] = {}
            
        base_schema["components"]["securitySchemes"] = SECURITY_SCHEMES
        
        # Add global security (most endpoints require auth)
        base_schema["security"] = [
            {"BearerAuth": []},
            {"ApiKeyAuth": []},
        ]
        
        # Add tags
        base_schema["tags"] = list(TAGS)
        
        # Enhance endpoint documentation
        paths = base_schema.get("paths", {})
        if isinstance(paths, dict):
            _enhance_endpoint_documentation(paths)
            
        # Add examples to components
        if "examples" not in base_schema["components"]:
            base_schema["components"]["examples"] = {}
            
        base_schema["components"]["examples"].update({
            "UserExample": {"value": EXAMPLE_USER},
            "FileExample": {"value": EXAMPLE_FILE}, 
            "AuthResponseExample": {"value": EXAMPLE_AUTH_RESPONSE},
            "ErrorExample": {"value": EXAMPLE_ERROR},
            "ValidationErrorExample": {"value": EXAMPLE_VALIDATION_ERROR},
        })
        
        logger.info("OpenAPI schema enhancement completed successfully")
        return base_schema
        
    except Exception as e:
        logger.error(f"Failed to enhance OpenAPI schema: {e}")
        raise


def _enhance_endpoint_documentation(paths: dict[str, Any]) -> None:
    """
    Enhance individual endpoint documentation with better descriptions and examples.
    
    Args:
        paths: OpenAPI paths object to enhance
    """
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
            
        # Add tags based on path prefixes
        _add_tags_to_endpoints(path, path_item)
        
        # Configure security for endpoints
        _configure_endpoint_security(path, path_item)
        
        # Add enhanced examples and descriptions
        _add_endpoint_examples(path, path_item)


def _add_tags_to_endpoints(path: str, path_item: dict[str, Any]) -> None:
    """Add appropriate tags to endpoints based on their paths."""
    tags = []
    
    if "/auth" in path:
        tags = ["Auth"]
    elif "/users" in path:
        tags = ["User Management"]
    elif "/uploads" in path:
        tags = ["File"]
    elif "/health" in path or "/metrics" in path:
        tags = ["Health"]
    elif "/ws" in path or "/websocket" in path:
        tags = ["WebSocket"]
        
    for method, operation in path_item.items():
        if isinstance(operation, dict) and "tags" not in operation:
            operation["tags"] = tags


def _configure_endpoint_security(path: str, path_item: dict[str, Any]) -> None:
    """Configure security requirements for endpoints."""
    for method, operation in path_item.items():
        if not isinstance(operation, dict):
            continue
            
        # Public endpoints don't require authentication
        if (path, method) in PUBLIC_ENDPOINTS:
            operation["security"] = []
        # Special case for auth/me endpoint - show multiple auth options
        elif path == "/api/v1/auth/me" and method == "get":
            operation["security"] = [
                {"BearerAuth": []},
                {"ApiKeyAuth": []},
                {"OAuth2PasswordBearer": ["read"]},
            ]
        # Most endpoints require authentication
        elif "security" not in operation:
            operation["security"] = [
                {"BearerAuth": []},
                {"ApiKeyAuth": []},
            ]


def _add_endpoint_examples(path: str, path_item: dict[str, Any]) -> None:
    """Add code samples and enhanced examples to endpoints."""
    for method, operation in path_item.items():
        if not isinstance(operation, dict):
            continue
            
        # Add code samples for key endpoints
        if path == "/api/v1/auth/login" and method == "post":
            operation["x-codeSamples"] = [
                {"lang": "curl", "source": CODE_SAMPLES["auth_login"]["curl"]},
                {"lang": "python", "source": CODE_SAMPLES["auth_login"]["python"]},
                {"lang": "javascript", "source": CODE_SAMPLES["auth_login"]["javascript"]},
            ]
        elif path == "/api/v1/uploads" and method == "post":
            operation["x-codeSamples"] = [
                {"lang": "curl", "source": CODE_SAMPLES["file_upload"]["curl"]},
                {"lang": "python", "source": CODE_SAMPLES["file_upload"]["python"]},
                {"lang": "javascript", "source": CODE_SAMPLES["file_upload"]["javascript"]},
            ]
            
        # Enhance response examples
        if "responses" in operation:
            _add_response_examples(operation["responses"])


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
                
            # Add appropriate examples based on status code
            if status_code == "200" or status_code == "201":
                if "user" in str(media_info).lower():
                    media_info["examples"]["default"] = {"value": EXAMPLE_USER}
                elif "file" in str(media_info).lower():
                    media_info["examples"]["default"] = {"value": EXAMPLE_FILE}
                elif "auth" in str(media_info).lower() or "token" in str(media_info).lower():
                    media_info["examples"]["default"] = {"value": EXAMPLE_AUTH_RESPONSE}
            elif status_code in ["400", "401", "403", "404", "429", "500"]:
                if status_code == "422":
                    media_info["examples"]["default"] = {"value": EXAMPLE_VALIDATION_ERROR}
                else:
                    media_info["examples"]["default"] = {"value": EXAMPLE_ERROR}
