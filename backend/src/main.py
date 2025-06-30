import os
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.api.v1.uploads import router as uploads_router
from src.api.v1.users import all_routers
from src.core.config import settings
from src.core.events import on_shutdown, on_startup
from src.core.logging import init_logging
from src.middlewares.logging import RequestLoggingMiddleware

if "PYTEST_CURRENT_TEST" not in os.environ:
    logger.remove()
    logger.add(sys.stdout, level="INFO")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ReViewPoint Core API",
        description="API for modular scientific paper review platform. Provides authentication, user management, file upload, and LLM integration.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={
            "persistAuthorization": True,  # Keep auth tokens between reloads
            "syntaxHighlight.theme": "obsidian",  # Dark theme for code
            "defaultModelsExpandDepth": 1,  # Show models collapsed by default
            "defaultModelExpandDepth": 2,  # Expand model properties
            "docExpansion": "list",  # Expand all endpoints as a list
            "displayRequestDuration": True,  # Show request duration
            "filter": True,  # Enable endpoint filtering
            "showExtensions": True,  # Show vendor extensions (x-*
            "tryItOutEnabled": True,  # Enable Try it Out by default
            "deepLinking": True,  # Allow deep linking to endpoints
            "showCommonExtensions": True,  # Show common OpenAPI extensions
            "displayOperationId": True,  # Show operationId for each endpoint
            "customCssUrl": "/static/swagger-custom.css",
            "customfavIcon": "/static/favicon.ico",
            "customSiteTitle": "ReViewPoint API Docs",
        },
    )
    # Initialize logging system
    init_logging(level=settings.log_level)
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    # Register authentication router
    app.include_router(auth_router, prefix="/api/v1")
    # Register health check endpoint
    app.include_router(health_router, prefix="/api/v1")
    # Mount static files directory
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
        name="static",
    )

    # Register user routers (modularized)
    for router in all_routers:
        app.include_router(router, prefix="/api/v1/users")
    # Register uploads router
    app.include_router(uploads_router, prefix="/api/v1")

    # Print registered routes for debugging with more details
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
    # Sort routes by specificity - routes with fewer path parameters are more specific
    routes_by_specificity = sorted(
        [r for r in app.routes if getattr(r, "path", None) is not None],
        key=lambda r: (
            getattr(r, "path", "").count("{"),  # Fewer params = higher specificity
            -len(
                getattr(r, "path", "")
            ),  # Longer path = higher specificity when param count is equal
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

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        if isinstance(exc, HTTPException):
            # Let FastAPI handle HTTPExceptions (like 404, 422, etc.)
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

    # Add handler for custom ValidationError to return 400
    from src.utils.errors import ValidationError

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    return app


def custom_openapi() -> dict[str, Any]:
    """Generate custom OpenAPI schema with additional features like:
    - Global security scheme
    - Tags with descriptions
    - Operation ID generation
    - Improved descriptions
    """
    try:
        # Create OpenAPI schema from routes
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Add contact information
        if "info" in openapi_schema and "contact" not in openapi_schema["info"]:
            openapi_schema["info"]["contact"] = {
                "name": "ReViewPoint Team",
                "url": "https://github.com/your-org/reviewpoint",
                "email": "support@reviewpoint.org",
            }
        # Add license information
        if "info" in openapi_schema and "license" not in openapi_schema["info"]:
            openapi_schema["info"]["license"] = {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            }

        # Add servers information
        if "servers" not in openapi_schema:
            openapi_schema["servers"] = [
                {"url": "http://localhost:8000", "description": "Development server"},
                {
                    "url": "https://api.reviewpoint.org",
                    "description": "Production server",
                },
            ]

        # Add security schemes
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Enter JWT token",
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

        # Add global security requirement
        openapi_schema["security"] = [{"BearerAuth": []}]

        # Add tags
        openapi_schema["tags"] = [
            {
                "name": "Auth",
                "description": "Authentication operations",
            },
            {
                "name": "Users",
                "description": "User management operations",
            },
            {
                "name": "Health",
                "description": "Health check and monitoring endpoints",
            },
            {
                "name": "Files",
                "description": "File upload and management operations",
            },
        ]

        # Add tags to specific paths/operations
        for path in openapi_schema["paths"]:
            # Auth endpoints
            if "/api/v1/auth" in path:
                for method in openapi_schema["paths"][path]:
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = ["Auth"]

                    # Don't require auth for login/register endpoints
                    if path in [
                        "/api/v1/auth/login",
                        "/api/v1/auth/register",
                        "/api/v1/auth/request-password-reset",
                        "/api/v1/auth/reset-password",
                    ]:
                        # Remove security requirement for these endpoints
                        openapi_schema["paths"][path][method]["security"] = []

            # User endpoints
            elif "/api/v1/users" in path:
                for method in openapi_schema["paths"][path]:
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = ["Users"]

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
                        openapi_schema["paths"][path][method]["tags"] = ["Files"]

        logger.info("OpenAPI schema generated successfully")
        return openapi_schema
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI schema: {e}")
        raise


app = create_app()

# Set custom_openapi function on app
app.openapi = custom_openapi  # type: ignore

# Register event handlers
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


def print_routes(app: FastAPI) -> None:
    import logging

    logging.info("REGISTERED ROUTES:")
    for route in app.routes:
        route_path = getattr(route, "path", None)
        if route_path is None:
            continue
        logging.info(f"{route_path} -> {getattr(route, 'endpoint', None)}")


# Conditionally print routes and router info only in development environment
if os.getenv("ENVIRONMENT", "production") == "development":
    print_routes(app)
    # print_all_routes(app)  # Disabled: function not defined at this point
    print(f"UPLOADS ROUTER: {uploads_router}")


def print_all_routes(app: FastAPI) -> None:
    import logging

    logging.info("REGISTERED ROUTES:")
    for route in app.routes:
        route_path = getattr(route, "path", None)
        if route_path is None:
            continue
        logging.info(f"{route_path} -> {getattr(route, 'endpoint', None)}")


# Conditionally print all routes only in development environment
if os.getenv("ENVIRONMENT", "production") == "development":
    print_all_routes(app)
