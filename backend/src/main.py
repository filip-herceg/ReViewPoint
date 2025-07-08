import os
import sys
from collections.abc import Callable
from typing import Final, Literal, TypedDict

from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.api.v1.uploads import router as uploads_router
from src.api.v1.users import all_routers
from src.api.v1.websocket import router as websocket_router
from src.core.config import get_settings
from src.core.events import on_shutdown, on_startup
from src.core.logging import init_logging
from src.middlewares.logging import RequestLoggingMiddleware

PYTEST_ENV_VAR: Final[Literal["PYTEST_CURRENT_TEST"]] = "PYTEST_CURRENT_TEST"
if PYTEST_ENV_VAR not in os.environ:
    logger.remove()
    logger.add(sys.stdout, level="INFO")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns:
        FastAPI: The configured FastAPI app instance.
    Raises:
        Exception: If any error occurs during app creation.
    """
    swagger_ui_parameters: dict[str, str | bool | int] = {
        "persistAuthorization": True,
        "syntaxHighlight.theme": "obsidian",
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 2,
        "docExpansion": "list",
        "displayRequestDuration": True,
        "filter": True,
        "showExtensions": True,
        "tryItOutEnabled": True,
        "deepLinking": True,
        "showCommonExtensions": True,
        "displayOperationId": True,
        "customCssUrl": "/static/swagger-custom.css",
        "customfavIcon": "/static/favicon.ico",
        "customSiteTitle": "ReViewPoint API Docs",
    }
    app: Final[FastAPI] = FastAPI(
        title="ReViewPoint Core API",
        description="API for modular scientific paper review platform. Provides authentication, user management, file upload, and LLM integration.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters=swagger_ui_parameters,
    )
    # Initialize logging system
    settings = get_settings()
    init_logging(level=settings.log_level)
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    # Register authentication router
    app.include_router(auth_router, prefix="/api/v1")
    # Register health check endpoint
    app.include_router(health_router, prefix="/api/v1")
    # Mount static files directory
    static_dir: str = os.path.join(os.path.dirname(__file__), "static")
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )

    # Register user routers (modularized)
    for router in all_routers:
        app.include_router(router, prefix="/api/v1/users")
    # Register uploads router
    app.include_router(uploads_router, prefix="/api/v1")
    # Register WebSocket router
    app.include_router(websocket_router, prefix="/api/v1")

    import logging

    logging.warning("REGISTERED ROUTES (in registration order):")
    for route in app.routes:
        route_path = getattr(route, "path", None)
        if route_path is None:
            continue
        route_methods = getattr(route, "methods", None)
        methods_str = f" [{','.join(route_methods)}]" if route_methods else ""
        endpoint_name = getattr(route, "endpoint", None)
        if endpoint_name is not None and hasattr(endpoint_name, "__name__"):
            endpoint_str = endpoint_name.__name__
        else:
            endpoint_str = str(endpoint_name)
        logging.warning(f"{route_path}{methods_str} -> {endpoint_str}")

    # Log routes sorted by specificity (how FastAPI matches routes)
    logging.warning("ROUTES BY MATCHING SPECIFICITY (most specific first):")
    routes_by_specificity = sorted(
        [r for r in app.routes if getattr(r, "path", None) is not None],
        key=lambda r: (
            getattr(r, "path", "").count("{"),
            -len(getattr(r, "path", "")),
        ),
    )
    for route in routes_by_specificity:
        route_path = getattr(route, "path", None)
        if route_path is None:
            continue
        route_methods = getattr(route, "methods", None)
        methods_str = f" [{','.join(route_methods)}]" if route_methods else ""
        endpoint_name = getattr(route, "endpoint", None)
        if endpoint_name is not None and hasattr(endpoint_name, "__name__"):
            endpoint_str = endpoint_name.__name__
        else:
            endpoint_str = str(endpoint_name)
        logging.warning(f"{route_path}{methods_str} -> {endpoint_str}")

    # Check routers
    logging.warning(f"UPLOADS ROUTER: {uploads_router}")

    # Print uploads router routes specifically with path parameters highlighted
    logging.warning("UPLOADS ROUTER ROUTES (with path params highlighted):")
    for route in uploads_router.routes:
        route_path = getattr(route, "path", None)
        if route_path is None:
            continue
        route_methods = getattr(route, "methods", None)
        methods_str = f" [{','.join(route_methods)}]" if route_methods else ""
        param_count = route_path.count("{")
        path_highlight = f"[PARAM:{param_count}]" if param_count > 0 else ""
        endpoint_name = getattr(route, "endpoint", None)
        if endpoint_name is not None and hasattr(endpoint_name, "__name__"):
            endpoint_str = endpoint_name.__name__
        else:
            endpoint_str = str(endpoint_name)
        logging.warning(f"{route_path}{methods_str} {path_highlight} -> {endpoint_str}")

    from src.utils.errors import ValidationError

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handles all uncaught exceptions.
        Args:
            request (Request): The incoming request.
            exc (Exception): The exception raised.
        Returns:
            JSONResponse: 500 error response.
        Raises:
            HTTPException: If the exception is an HTTPException.
        """
        if isinstance(exc, HTTPException):
            raise exc
        logger.exception(
            f"Unhandled exception for {request.method} {request.url.path}: {exc}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "feedback": "An unexpected error occurred. Please try again later.",
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """
        Handles custom validation errors.
        Args:
            request (Request): The incoming request.
            exc (ValidationError): The validation error.
        Returns:
            JSONResponse: 400 error response.
        """
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    return app


# --- TypedDicts for OpenAPI schema (for documentation only, not for runtime type checking) ---
class ContactInfoDict(TypedDict):
    name: str
    url: str
    email: str


class LicenseInfoDict(TypedDict):
    name: str
    url: str


class ServerInfoDict(TypedDict):
    url: str
    description: str


class SecuritySchemeDict(TypedDict, total=False):
    type: str
    scheme: str
    bearerFormat: str
    description: str
    flows: dict[str, dict[str, str | dict[str, str]]]


# Note: OpenAPISchemaDict is for documentation only. At runtime, use dict[str, Any] for compatibility with FastAPI.


from typing import Any, cast


def custom_openapi() -> dict[str, Any]:
    """
    Generate custom OpenAPI schema with additional features like:
    - Global security scheme
    - Tags with descriptions
    - Operation ID generation
    - Improved descriptions
    Returns:
        dict[str, Any]: The OpenAPI schema dictionary.
    Raises:
        Exception: If schema generation fails.
    """
    try:
        openapi_schema: dict[str, Any] = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Use TypedDicts for structure, but cast at assignment for type safety in IDEs
        if "info" in openapi_schema and "contact" not in openapi_schema["info"]:
            openapi_schema["info"]["contact"] = cast(
                ContactInfoDict,
                {
                    "name": "ReViewPoint Team",
                    "url": "https://github.com/your-org/reviewpoint",
                    "email": "support@reviewpoint.org",
                },
            )
        if "info" in openapi_schema and "license" not in openapi_schema["info"]:
            openapi_schema["info"]["license"] = cast(
                LicenseInfoDict,
                {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT",
                },
            )

        if "servers" not in openapi_schema:
            openapi_schema["servers"] = [
                cast(
                    ServerInfoDict,
                    {
                        "url": "http://localhost:8000",
                        "description": "Development server",
                    },
                ),
                cast(
                    ServerInfoDict,
                    {
                        "url": "https://api.reviewpoint.org",
                        "description": "Production server",
                    },
                ),
            ]

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {
                "BearerAuth": cast(
                    SecuritySchemeDict,
                    {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "Enter JWT token",
                    },
                ),
                "OAuth2PasswordBearer": cast(
                    SecuritySchemeDict,
                    {
                        "type": "oauth2",
                        "flows": {
                            "password": {
                                "tokenUrl": "/api/v1/auth/login",
                                "scopes": {},
                            }
                        },
                    },
                ),
            }

        openapi_schema["security"] = [{"BearerAuth": []}]

        openapi_schema["tags"] = [
            {"name": "Auth", "description": "Authentication operations"},
            {"name": "Users", "description": "User management operations"},
            {"name": "Health", "description": "Health check and monitoring endpoints"},
            {"name": "Files", "description": "File upload and management operations"},
        ]

        # Defensive: check for 'paths' key before iterating
        paths = openapi_schema.get("paths")
        if isinstance(paths, dict):
            for path, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue
                if "/api/v1/auth" in path:
                    for method, method_item in path_item.items():
                        if not isinstance(method_item, dict):
                            continue
                        if "tags" not in method_item:
                            method_item["tags"] = ["Auth"]
                        if path in [
                            "/api/v1/auth/login",
                            "/api/v1/auth/register",
                            "/api/v1/auth/request-password-reset",
                            "/api/v1/auth/reset-password",
                        ]:
                            method_item["security"] = []
                elif "/api/v1/users" in path:
                    for method, method_item in path_item.items():
                        if not isinstance(method_item, dict):
                            continue
                        if "tags" not in method_item:
                            method_item["tags"] = ["Users"]
                elif "/api/v1/health" in path or "/api/v1/metrics" in path:
                    for method, method_item in path_item.items():
                        if not isinstance(method_item, dict):
                            continue
                        if "tags" not in method_item:
                            method_item["tags"] = ["Health"]
                        method_item["security"] = []
                elif "/api/v1/uploads" in path:
                    for method, method_item in path_item.items():
                        if not isinstance(method_item, dict):
                            continue
                        if "tags" not in method_item:
                            method_item["tags"] = ["Files"]

        logger.info("OpenAPI schema generated successfully")
        return openapi_schema
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI schema: {e}")
        raise


app: Final[FastAPI] = create_app()

# Set custom_openapi function on app
app.openapi = custom_openapi  # type: ignore[method-assign]

# Register event handlers
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


def print_routes(app: FastAPI) -> None:
    """
    Print all registered routes for the FastAPI app.
    Args:
        app (FastAPI): The FastAPI app instance.
    Returns:
        None
    """
    import logging

    logging.info("REGISTERED ROUTES:")
    for route in app.routes:
        route_path: str | None = getattr(route, "path", None)
        if route_path is None:
            continue
        logging.info(f"{route_path} -> {getattr(route, 'endpoint', None)}")


# Conditionally print routes and router info only in development environment
ENVIRONMENT: Final[str] = os.getenv("ENVIRONMENT", "production")
if ENVIRONMENT == "development":
    print_routes(app)


def print_all_routes(app: FastAPI) -> None:
    """
    Print all registered routes for the FastAPI app (detailed).
    Args:
        app (FastAPI): The FastAPI app instance.
    Returns:
        None
    """
    import logging

    logging.info("REGISTERED ROUTES:")
    for route in app.routes:
        route_path: str | None = getattr(route, "path", None)
        if route_path is None:
            continue
        logging.info(f"{route_path} -> {getattr(route, 'endpoint', None)}")


# Conditionally print all routes only in development environment
if ENVIRONMENT == "development":
    print_all_routes(app)
