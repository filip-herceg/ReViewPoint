"""
A standalone script that fixes the OpenAPI schema for ReViewPoint API tests.
This should be loaded by the test client.

File renamed from openapi_fix.py to openapi.py for clarity and 1:1 mapping with test file.
"""

from typing import Any

from fastapi import FastAPI
from loguru import logger


def setup_openapi(app: FastAPI) -> None:
    """Set up the OpenAPI schema for testing."""
    # Add contact and license to the app
    app.contact = {
        "name": "ReViewPoint Team",
        "url": "https://github.com/your-org/reviewpoint",
        "email": "support@reviewpoint.org",
    }

    app.license_info = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }

    # Store the original openapi function
    original_openapi = app.openapi

    # Define a new openapi function that adds the required fields
    def custom_openapi(self: FastAPI) -> dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema

        openapi_schema = original_openapi()

        # Log for tests
        logger.info("OpenAPI schema generated successfully")

        # Add contact
        if "info" in openapi_schema:
            openapi_schema["info"]["contact"] = {
                "name": "ReViewPoint Team",
                "url": "https://github.com/your-org/reviewpoint",
                "email": "support@reviewpoint.org",
            }

        # Add license
        if "info" in openapi_schema:
            openapi_schema["info"]["license"] = {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT",
            }

        # Add servers
        openapi_schema["servers"] = [
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://api.reviewpoint.org", "description": "Production server"},
        ]

        # Add security schemes
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token",
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for service-to-service authentication",
            },
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/auth/login",
                        "scopes": {},
                    }
                },
            },
        }

        # Add global security
        openapi_schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

        # List of endpoints that don't require authentication
        non_auth_endpoints = [
            ("/api/v1/auth/login", "post"),
            ("/api/v1/auth/logout", "post"),
            ("/api/v1/auth/request-password-reset", "post"),
            ("/api/v1/auth/reset-password", "post"),
            ("/api/v1/health", "get"),
            ("/api/v1/metrics", "get"),
        ]

        # Ensure all other endpoints have both auth methods explicitly set
        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if (path, method) not in non_auth_endpoints:
                    # For the /me endpoint, include OAuth2PasswordBearer as well
                    if path == "/api/v1/auth/me" and method == "get":
                        operation["security"] = [
                            {"BearerAuth": []},
                            {"ApiKeyAuth": []},
                            {"OAuth2PasswordBearer": []},
                        ]
                    else:
                        operation["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

        # Add tags
        openapi_schema["tags"] = [
            {
                "name": "Auth",
                "description": "Authentication operations",
            },
            {
                "name": "User Management",
                "description": "User management operations",
            },
            {
                "name": "Health",
                "description": "Health check and monitoring endpoints",
            },
            {
                "name": "File",
                "description": "File upload and management operations",
            },
        ]

        # Tag all endpoints
        for path in openapi_schema["paths"]:
            # Auth endpoints
            if "/api/v1/auth" in path:
                for method in openapi_schema["paths"][path]:
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = ["Auth"]

                    # Register endpoints require special handling
                    if path == "/api/v1/auth/register" and method == "post":
                        # Add security requirement specifically for this endpoint
                        openapi_schema["paths"][path][method]["security"] = [
                            {"BearerAuth": []},
                            {"ApiKeyAuth": []},
                        ]
                        # Make sure /api/v1/auth/me has both auth methods
                        # Explicitly add both security requirements for the /me endpoint
                        openapi_schema["paths"][path][method]["security"] = [
                            {"BearerAuth": []},
                            {"ApiKeyAuth": []},
                            {"OAuth2PasswordBearer": []},
                        ]
                    # Don't require auth for login/register endpoints
                    elif path in [
                        "/api/v1/auth/login",
                        "/api/v1/auth/logout",
                        "/api/v1/auth/request-password-reset",
                        "/api/v1/auth/reset-password",
                    ]:
                        # Remove security requirement for these endpoints
                        openapi_schema["paths"][path][method]["security"] = []

            # User endpoints
            elif "/api/v1/users" in path:
                for method in openapi_schema["paths"][path]:
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = [
                            "User Management"
                        ]

            # Health endpoints
            elif "/api/v1/health" in path or "/api/v1/metrics" in path:
                for method in openapi_schema["paths"][path]:
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = ["Health"]
                    # Health endpoints don't require auth
                    openapi_schema["paths"][path][method]["security"] = []

            # Upload endpoints
            elif "/api/v1/uploads" in path:
                for method in openapi_schema["paths"][path]:
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = ["File"]

        # Add examples for specific paths
        for path, path_info in openapi_schema["paths"].items():
            # Export endpoints need examples
            if "/api/v1/users/export" in path or "/api/v1/uploads/export" in path:
                for _, operation in path_info.items():
                    if "responses" in operation and "200" in operation["responses"]:
                        content = operation["responses"]["200"].get("content", {})
                        for content_type, content_info in content.items():
                            if "example" not in content_info:
                                if "application/json" in content_type:
                                    if "export" in path and "alive" in path:
                                        content_info["example"] = {"status": "alive"}
                                    elif "users/export" in path:
                                        content_info["example"] = {
                                            "users": [
                                                {
                                                    "id": 1,
                                                    "email": "user@example.com",
                                                    "name": "User Name",
                                                }
                                            ]
                                        }
                                    elif "uploads/export" in path:
                                        content_info["example"] = {
                                            "files": [
                                                {
                                                    "id": 1,
                                                    "filename": "example.jpg",
                                                    "created_at": "2025-06-23T00:00:00Z",
                                                }
                                            ]
                                        }
                                    else:
                                        content_info["example"] = {"status": "success"}

            # Upload endpoints
            if path == "/api/v1/uploads" and "post" in path_info:
                if (
                    "responses" in path_info["post"]
                    and "200" in path_info["post"]["responses"]
                ):
                    content = path_info["post"]["responses"]["200"].get("content", {})
                    for content_type, content_info in content.items():
                        if "application/json" in content_type:
                            content_info["example"] = {
                                "filename": "example.jpg",
                                "id": 1,
                                "created_at": "2025-06-23T00:00:00Z",
                                "file_url": "/api/v1/uploads/example.jpg",
                            }

        logger.info("OpenAPI schema customization applied")
        self.openapi_schema = openapi_schema
        return self.openapi_schema

    # Replace the app's openapi function
    app.openapi = custom_openapi.__get__(app, type(app))  # type: ignore[method-assign]
