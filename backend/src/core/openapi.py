"""
A standalone script that fixes the OpenAPI schema for ReViewPoint API tests.
This should be loaded by the test client.

File renamed from openapi_fix.py to openapi.py for clarity and 1:1 mapping with test file.
"""

from collections.abc import Callable, Mapping, Sequence
from typing import Final, Literal, TypedDict, cast

from fastapi import FastAPI
from loguru import logger


# --- TypedDicts for OpenAPI structure ---
class ContactDict(TypedDict):
    name: str
    url: str
    email: str


class LicenseDict(TypedDict):
    name: str
    url: str


class ServerDict(TypedDict):
    url: str
    description: str


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


class OAuth2PasswordFlowDict(TypedDict):
    tokenUrl: str
    scopes: Mapping[str, str]


class OAuth2FlowsDict(TypedDict):
    password: OAuth2PasswordFlowDict


class SecuritySchemeOAuth2Dict(TypedDict):
    type: Literal["oauth2"]
    flows: OAuth2FlowsDict


class SecuritySchemesDict(TypedDict):
    BearerAuth: SecuritySchemeBearerDict
    ApiKeyAuth: dict[str, str | Literal["apiKey", "header", "X-API-Key"]]
    OAuth2PasswordBearer: SecuritySchemeOAuth2Dict


class TagDict(TypedDict):
    name: str
    description: str


class ExampleUserDict(TypedDict):
    id: int
    email: str
    name: str


class ExampleFileDict(TypedDict):
    id: int
    filename: str
    created_at: str


class ExampleUsersExportDict(TypedDict):
    users: Sequence[ExampleUserDict]


class ExampleUploadsExportDict(TypedDict):
    files: Sequence[ExampleFileDict]


class ExampleUploadResponseDict(TypedDict):
    filename: str
    id: int
    created_at: str
    file_url: str


class OperationDict(TypedDict, total=False):
    tags: Sequence[str]
    security: Sequence[Mapping[str, Sequence[str]]]
    responses: dict[str, dict[str, object]]


class PathItemDict(TypedDict):
    # e.g. "get", "post", etc.
    __root__: dict[str, OperationDict]


class OpenAPISchemaDict(TypedDict, total=False):
    info: dict[str, object]
    servers: Sequence[ServerDict]
    components: dict[str, object]
    security: Sequence[Mapping[str, Sequence[str]]]
    tags: Sequence[TagDict]
    paths: dict[str, dict[str, OperationDict]]


# --- Constants ---
CONTACT: Final[ContactDict] = {
    "name": "ReViewPoint Team",
    "url": "https://github.com/your-org/reviewpoint",
    "email": "support@reviewpoint.org",
}

LICENSE_INFO: Final[LicenseDict] = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT",
}

SERVERS: Final[Sequence[ServerDict]] = [
    {"url": "http://localhost:8000", "description": "Development server"},
    {"url": "https://api.reviewpoint.org", "description": "Production server"},
]

NON_AUTH_ENDPOINTS: Final[Sequence[tuple[str, str]]] = [
    ("/api/v1/auth/login", "post"),
    ("/api/v1/auth/logout", "post"),
    ("/api/v1/auth/request-password-reset", "post"),
    ("/api/v1/auth/reset-password", "post"),
    ("/api/v1/health", "get"),
    ("/api/v1/metrics", "get"),
]

TAGS: Final[Sequence[TagDict]] = [
    {"name": "Auth", "description": "Authentication operations"},
    {"name": "User Management", "description": "User management operations"},
    {"name": "Health", "description": "Health check and monitoring endpoints"},
    {"name": "File", "description": "File upload and management operations"},
]


def setup_openapi(app: FastAPI) -> None:
    """
    Set up the OpenAPI schema for testing.

    :param app: FastAPI application instance
    :raises Exception: If OpenAPI schema cannot be generated
    """
    # Assigning to FastAPI attributes; do not annotate, and use dict[str, str] for compatibility
    app.contact = dict(CONTACT)
    app.license_info = dict(LICENSE_INFO)

    original_openapi: Callable[[], dict[str, object]] = app.openapi

    def custom_openapi(self: FastAPI) -> dict[str, object]:
        """
        Customizes the OpenAPI schema for ReViewPoint.

        :param self: FastAPI application instance
        :return: Customized OpenAPI schema
        :raises Exception: If OpenAPI schema cannot be generated
        """

        if hasattr(self, "openapi_schema") and self.openapi_schema is not None:
            # FastAPI expects openapi_schema to be dict[str, Any] | None
            return cast(dict[str, object], self.openapi_schema)

        openapi_schema: dict[str, object] = original_openapi()

        logger.info("OpenAPI schema generated successfully")

        # Add contact
        if "info" in openapi_schema:
            info = openapi_schema["info"]
            if isinstance(info, dict):
                info["contact"] = dict(CONTACT)
                info["license"] = dict(LICENSE_INFO)

        # Add servers
        openapi_schema["servers"] = list(SERVERS)

        # Add security schemes
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        components = openapi_schema["components"]
        if isinstance(components, dict):
            components["securitySchemes"] = {
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

        # Ensure all other endpoints have both auth methods explicitly set
        paths = openapi_schema.get("paths")
        if not isinstance(paths, dict):
            logger.error("OpenAPI schema missing 'paths' or not a dict")
            self.openapi_schema = openapi_schema
            return self.openapi_schema
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue
                if (path, method) not in NON_AUTH_ENDPOINTS:
                    if path == "/api/v1/auth/me" and method == "get":
                        operation["security"] = [
                            {"BearerAuth": []},
                            {"ApiKeyAuth": []},
                            {"OAuth2PasswordBearer": []},
                        ]
                    else:
                        operation["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

        # Add tags
        openapi_schema["tags"] = list(TAGS)

        # Tag all endpoints
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            if "/api/v1/auth" in path:
                for method in path_item:
                    op = path_item[method]
                    if not isinstance(op, dict):
                        continue
                    if "tags" not in op:
                        op["tags"] = ["Auth"]
                    if path == "/api/v1/auth/register" and method == "post":
                        op["security"] = [
                            {"BearerAuth": []},
                            {"ApiKeyAuth": []},
                        ]
                        op["security"] = [
                            {"BearerAuth": []},
                            {"ApiKeyAuth": []},
                            {"OAuth2PasswordBearer": []},
                        ]
                    elif path in [
                        "/api/v1/auth/login",
                        "/api/v1/auth/logout",
                        "/api/v1/auth/request-password-reset",
                        "/api/v1/auth/reset-password",
                    ]:
                        op["security"] = []
            elif "/api/v1/users" in path:
                for method in path_item:
                    op = path_item[method]
                    if not isinstance(op, dict):
                        continue
                    if "tags" not in op:
                        op["tags"] = ["User Management"]
            elif "/api/v1/health" in path or "/api/v1/metrics" in path:
                for method in path_item:
                    op = path_item[method]
                    if not isinstance(op, dict):
                        continue
                    if "tags" not in op:
                        op["tags"] = ["Health"]
                    op["security"] = []
            elif "/api/v1/uploads" in path:
                for method in path_item:
                    op = path_item[method]
                    if not isinstance(op, dict):
                        continue
                    if "tags" not in op:
                        op["tags"] = ["File"]

        # Add examples for specific paths
        for path, path_info in paths.items():
            if not isinstance(path_info, dict):
                continue
            if "/api/v1/users/export" in path or "/api/v1/uploads/export" in path:
                for _, operation in path_info.items():
                    if not isinstance(operation, dict):
                        continue
                    if "responses" in operation and "200" in operation["responses"]:
                        content = operation["responses"]["200"].get("content", {})
                        if not isinstance(content, dict):
                            continue
                        for content_type, content_info in content.items():
                            if not isinstance(content_info, dict):
                                continue
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
            if path == "/api/v1/uploads" and "post" in path_info:
                post_op = path_info["post"]
                if not isinstance(post_op, dict):
                    continue
                if "responses" in post_op and "200" in post_op["responses"]:
                    content = post_op["responses"]["200"].get("content", {})
                    if not isinstance(content, dict):
                        continue
                    for content_type, content_info in content.items():
                        if not isinstance(content_info, dict):
                            continue
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

    # Assign the custom_openapi method to the app
    app.openapi = custom_openapi.__get__(app, type(app))  # type: ignore[method-assign]
