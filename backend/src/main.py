import os
import sys
import time
from typing import Any, Final

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.api.v1.uploads import router as uploads_router
from src.api.v1.users import all_routers
from src.api.v1.websocket import router as websocket_router
from src.core.app_logging import init_logging
from src.core.config import get_settings
from src.core.documentation import get_enhanced_openapi_schema
from src.core.events import on_shutdown, on_startup
from src.middlewares.logging import RequestLoggingMiddleware

PYTEST_ENV_VAR: Final = "PYTEST_CURRENT_TEST"
if PYTEST_ENV_VAR not in os.environ:
    logger.remove()
    logger.add(sys.stdout, level="INFO")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

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
        # Enhanced Swagger UI configuration
        swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_ui_init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": "reviewpoint-docs",
            "realm": "reviewpoint",
            "appName": "ReViewPoint API Documentation",
        },
    )
    # Initialize logging system
    settings = get_settings()
    init_logging(level=settings.log_level)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # DEBUG: Add comprehensive request tracing middleware
    @app.middleware("http")
    async def trace_all_requests(request: Request, call_next: Any) -> Any:
        logger.critical(
            f"🔍 TRACE: {request.method} {request.url.path} | "
            f"query: {request.url.query}",
        )
        response = await call_next(request)
        logger.critical(
            f"🔍 RESPONSE: {response.status_code} for "
            f"{request.method} {request.url.path}",
        )
        return response

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # DEBUG: Add a simple test endpoint to verify the server is working
    @app.get("/debug/test")
    async def debug_test() -> dict[str, Any]:
        logger.info("DEBUG: Test endpoint hit successfully")
        return {"message": "Server is working", "timestamp": time.time()}

    @app.post("/debug/test-post")
    async def debug_test_post() -> dict[str, Any]:
        logger.info("DEBUG: Test POST endpoint hit successfully")
        return {"message": "POST is working", "timestamp": time.time()}

    # Register authentication router
    app.include_router(auth_router, prefix="/api/v1/auth")
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

    # DEBUG: Catch-all route to log unmatched paths (MUST BE LAST!)
    @app.api_route(
        "/{full_path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    )
    async def catch_all(request: Request, full_path: str) -> Response:
        logger.critical(
            f"🚨 CATCH-ALL: {request.method} /{full_path} - NO ROUTE MATCHED!",
        )
        content = {
            "error": "Route not found",
            "method": request.method,
            "path": f"/{full_path}",
            "message": "This request was caught by the catch-all handler",
        }
        return JSONResponse(status_code=404, content=content)

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
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handles all uncaught exceptions.

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
            f"Unhandled exception for {request.method} {request.url.path}: {exc}",
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
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        """Handles custom validation errors.

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


def custom_openapi() -> dict[str, Any]:
    """Generate custom OpenAPI schema with comprehensive documentation.

    Features:
    - Enhanced API metadata with contact and license info
    - Multiple server environments (dev, staging, prod)
    - Comprehensive security schemes (JWT, API Key, OAuth2)
    - Detailed endpoint tags and descriptions
    - Code samples and examples for common operations
    - Proper error response documentation

    Returns:
        dict[str, Any]: Enhanced OpenAPI schema dictionary

    Raises:
        Exception: If schema generation fails

    """
    try:
        logger.info("Generating custom OpenAPI schema with enhanced documentation")

        # Generate base schema from FastAPI
        base_schema: dict[str, Any] = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=[
                {"name": "Auth", "description": "Authentication operations"},
                {
                    "name": "User Management",
                    "description": "User management operations",
                },
                {
                    "name": "File",
                    "description": "File upload and management operations",
                },
                {
                    "name": "Health",
                    "description": "Health check and monitoring endpoints",
                },
                {
                    "name": "WebSocket",
                    "description": "Real-time communication endpoints",
                },
            ],
        )

        # Use comprehensive documentation module to enhance schema
        enhanced_schema = get_enhanced_openapi_schema(base_schema)

        logger.info(
            "Custom OpenAPI schema generated successfully with enhanced documentation",
        )
        return enhanced_schema

    except Exception as e:
        logger.error(f"Failed to generate custom OpenAPI schema: {e}")
        # Fallback to basic schema if enhancement fails
        logger.warning("Falling back to basic OpenAPI schema")
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )


app: Final[FastAPI] = create_app()

# Set custom_openapi function on app
app.openapi = custom_openapi  # type: ignore[method-assign]

# Register event handlers
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


def print_routes(app: FastAPI) -> None:
    """Print all registered routes for the FastAPI app.

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
    """Print all registered routes for the FastAPI app (detailed).

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
