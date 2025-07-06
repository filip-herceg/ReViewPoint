"""
Dependency injection utilities for FastAPI API endpoints.

This module provides robust, reusable dependencies for:
- Database session management (get_db)
- User authentication and active user checks (get_current_user, get_current_active_user, optional_get_current_user)
- Pagination parameter validation (pagination_params)
- Repository/service locator for testability (get_user_service, get_service)
- Request ID propagation for tracing (get_request_id, get_current_request_id)
- Feature flag checks
- Dependency health checks and metrics
- Dynamic config reloading

All dependencies use loguru for error and event logging, follow security best practices, and are designed for easy testing and mocking.
"""

import contextvars
import importlib
import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import lru_cache, wraps
from typing import (
    Final,
    Literal,
    TypedDict,
    TypeVar,
)

from fastapi import Depends, Header, HTTPException, Query, Request, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.database import get_async_session
from src.core.security import verify_access_token
from src.models.user import User
from src.repositories import user as user_repository
from src.repositories.user import get_user_by_id
from src.services.user import UserService
from src.utils.http_error import http_error

REQUEST_ID_HEADER: Final[str] = "X-Request-ID"


# Context variable to store request ID per request
request_id_ctx_var: Final[contextvars.ContextVar[str | None]] = contextvars.ContextVar(
    "request_id", default=None
)
current_user_id_ctx_var: Final[contextvars.ContextVar[int | None]] = (
    contextvars.ContextVar("user_id", default=None)
)

oauth2_scheme: Final[OAuth2PasswordBearer] = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)
api_key_header: Final[APIKeyHeader] = APIKeyHeader(name="X-API-Key", auto_error=False)

MAX_LIMIT: Final[int] = 100


def _get_dev_admin_user() -> User:
    """
    Return a development admin user when auth is disabled.
    """
    return User(
        id=0,
        email="dev@example.com",
        hashed_password="",
        is_active=True,
        is_deleted=False,
        name="Dev Admin",
        bio="Development admin user (auth disabled)",
        avatar_url=None,
        preferences=None,
        last_login_at=None,
        created_at=None,
        updated_at=None,
    )


def _check_user_is_valid(user: User | None) -> bool:
    return user is not None and user.is_active and not user.is_deleted


# --- Dependency Registry ---

K = TypeVar("K")
V = TypeVar("V")


class DependencyEntry(TypedDict, total=False):
    factory: Callable[[], object]
    singleton: bool
    cache_ttl: float | None
    instance: object | None
    last_access: float | None


class DependencyRegistry:
    _instances: dict[str, DependencyEntry] = {}

    @classmethod
    def register(
        cls,
        key: str,
        factory: Callable[[], object],
        singleton: bool = True,
        cache_ttl: float | None = None,
    ) -> None:
        cls._instances[key] = {
            "factory": factory,
            "singleton": singleton,
            "cache_ttl": cache_ttl,
            "instance": None,
            "last_access": None,
        }

    @classmethod
    def get(cls, key: str) -> object:
        if key not in cls._instances:
            raise KeyError(f"Dependency {key} not registered")
        entry: DependencyEntry = cls._instances[key]
        # Use .get() with defaults for all optional keys

        singleton: bool = entry.get("singleton", True)
        instance: object | None = entry.get("instance", None)
        factory: Callable[[], object] | None = entry.get("factory")
        if factory is None:
            raise RuntimeError(f"Dependency entry for '{key}' is missing a factory.")
        cache_ttl: float | None = entry.get("cache_ttl", None)
        last_access: float | None = entry.get("last_access", None)

        if not singleton or instance is None:
            instance = factory()
            entry["instance"] = instance
        if cache_ttl is not None and last_access is not None:
            now: float = time.time()
            if now - last_access > cache_ttl:
                instance = factory()
                entry["instance"] = instance
        entry["last_access"] = time.time()
        return entry.get("instance")


registry: Final[DependencyRegistry] = DependencyRegistry()
registry.register("user_service", lambda: importlib.import_module("src.services.user"))
registry.register("user_repository", lambda: user_repository)
registry.register(
    "blacklist_token",
    lambda: importlib.import_module(
        "src.repositories.blacklisted_token"
    ).blacklist_token,
)
registry.register(
    "user_action_limiter",
    lambda: importlib.import_module("src.repositories.user").user_action_limiter,
)
registry.register(
    "validate_email",
    lambda: importlib.import_module("src.utils.validation").validate_email,
)
registry.register(
    "password_validation_error",
    lambda: importlib.import_module(
        "src.utils.validation"
    ).get_password_validation_error,
)
registry.register(
    "async_refresh_access_token",
    lambda: importlib.import_module("src.services.user").async_refresh_access_token,
)


def get_user_service() -> UserService:
    return UserService()


def get_user_repository_func() -> object:
    return registry.get("user_repository")  # type: ignore[no-any-return]


def get_blacklist_token() -> Callable[..., Awaitable[None]]:
    return registry.get("blacklist_token")  # type: ignore[no-any-return]


def get_user_action_limiter() -> Callable[..., Awaitable[None]]:
    return registry.get("user_action_limiter")  # type: ignore[no-any-return]


def get_validate_email() -> Callable[[str], bool]:
    return registry.get("validate_email")  # type: ignore[no-any-return]


def get_password_validation_error() -> Callable[[str], str | None]:
    return registry.get("password_validation_error")  # type: ignore[no-any-return]


def get_async_refresh_access_token() -> (
    Callable[[AsyncSession, str], Awaitable[object]]
):
    async_refresh_access_token: Callable[[AsyncSession, str, str, str], Awaitable[object]] = registry.get("async_refresh_access_token")  # type: ignore[no-any-return]

    async def wrapper(session: AsyncSession, token: str) -> object:
        settings = get_settings()
        jwt_secret_key: str | None = settings.jwt_secret_key
        jwt_algorithm: str | None = settings.jwt_algorithm
        if jwt_secret_key is None or jwt_algorithm is None:
            raise RuntimeError("JWT secret key and algorithm must be set in settings.")
        return await async_refresh_access_token(
            session,
            token,
            jwt_secret_key,
            jwt_algorithm,
        )

    return wrapper


# --- Generic Service Provider ---


def get_service(module_path: str) -> object:
    return importlib.import_module(module_path)  # type: ignore[no-any-return]


# --- Feature Flags ---


from typing import Protocol


class FeatureFlagsProtocol(Protocol):
    def is_enabled(self, feature_name: str) -> bool: ...


def get_feature_flags() -> FeatureFlagsProtocol:
    from src.core.feature_flags import FeatureFlags

    return FeatureFlags()


def require_feature(
    feature_name: str,
) -> Callable[[FeatureFlagsProtocol], Awaitable[bool]]:
    async def dependency(
        flags: FeatureFlagsProtocol = Depends(get_feature_flags),
    ) -> bool:
        if not flags.is_enabled(feature_name):
            http_error(
                404,
                "This feature is not available",
                logger.warning,
                {"feature": feature_name},
            )
        return True

    return dependency


# --- Health Check System ---


class HealthCheck:
    _checks: dict[str, Callable[[], bool | Awaitable[bool]]] = {}

    @classmethod
    def register(
        cls, name: str, check_func: Callable[[], bool | Awaitable[bool]]
    ) -> None:
        cls._checks[name] = check_func

    @classmethod
    @classmethod
    async def check_all(cls) -> dict[str, dict[str, str | bool]]:
        results: dict[str, dict[str, str | bool]] = {}
        for name, check_func in cls._checks.items():
            try:
                result: bool | Awaitable[bool] = check_func()
                is_healthy: bool
                if isinstance(result, bool):
                    is_healthy = result
                elif hasattr(result, "__await__"):
                    is_healthy = await result  # type: ignore
                else:
                    raise RuntimeError(
                        f"Health check '{name}' did not return bool or Awaitable[bool]"
                    )
                results[name] = {"status": "healthy" if is_healthy else "unhealthy"}
            except Exception as exc:
                results[name] = {"status": "error", "message": str(exc)}
        return results


# Example health check registration (add more as needed)

HealthCheck.register("database", lambda: True)  # Replace with real DB check


# --- Dependency Metrics ---


class DependencyMetric(TypedDict):
    count: int
    errors: int
    total_time: float


dependency_metrics: dict[str, DependencyMetric] = {}


def measure_dependency(
    func: Callable[..., Awaitable[object]],
) -> Callable[..., Awaitable[object]]:
    @wraps(func)
    async def wrapper(*args: object, **kwargs: object) -> object:
        start: float = time.time()
        status: Literal["success", "error"] = "success"
        try:
            result: object = (
                await func(*args, **kwargs)
                if callable(getattr(func, "__await__", None))
                else func(*args, **kwargs)
            )
            status = "success"
        except Exception:
            status = "error"
            raise
        finally:
            duration: float = time.time() - start
            name: str = func.__name__
            if name not in dependency_metrics:
                dependency_metrics[name] = {"count": 0, "errors": 0, "total_time": 0.0}
            dependency_metrics[name]["count"] += 1
            dependency_metrics[name]["total_time"] += duration
            if status == "error":
                dependency_metrics[name]["errors"] += 1
        return result

    return wrapper


# --- Dynamic Config Reloader ---


def get_refreshable_settings() -> object:
    class RefreshableSettings:
        _last_refresh: float
        _refresh_interval: float
        _settings: object | None

        def __init__(self) -> None:
            self._last_refresh = 0.0
            self._refresh_interval = 60.0
            self._settings = None

        def _reload_if_needed(self) -> None:
            now: float = time.time()
            if (
                now - self._last_refresh > self._refresh_interval
                or self._settings is None
            ):
                import importlib

                import src.core.config

                importlib.reload(src.core.config)
                self._settings = src.core.config.settings
                self._last_refresh = now

        def __getattr__(self, name: str) -> object:
            self._reload_if_needed()
            if self._settings is None:
                raise AttributeError("Settings not loaded")
            return getattr(self._settings, name)

    return RefreshableSettings()


# --- Pagination ---


class PaginationParams:
    """
    Standardized pagination parameters for API endpoints.

    Args:
        offset (int): Number of items to skip (default 0, must be >= 0).
        limit (int): Number of items to return (default 20, 1 <= limit <= MAX_LIMIT).

    Usage:
        params = Depends(pagination_params)
        items = repo.list(offset=params.offset, limit=params.limit)
    """

    offset: int
    limit: int

    def __init__(self, offset: int = 0, limit: int = 20) -> None:
        self.offset: int = offset
        self.limit: int = limit


# PaginationParams and pagination_params already log errors for invalid input (no sensitive data).
# Add info log for successful pagination param usage.


def pagination_params(
    offset: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        20,
        ge=1,
        le=MAX_LIMIT,
        description=f"Max number of items to return (max {MAX_LIMIT})",
    ),
) -> PaginationParams:
    """
    Dependency to standardize and validate pagination query parameters.

    Parameters:
        offset (int): Number of items to skip (>=0, default 0)
        limit (int): Number of items to return (1 to MAX_LIMIT, default 20)
    Returns:
        PaginationParams: Validated pagination parameters.
    Raises:
        HTTPException(400): If offset or limit is out of bounds.
    Usage:
        params = Depends(pagination_params)
        items = repo.list(offset=params.offset, limit=params.limit)
    """
    if offset < 0:
        logger.error(f"Invalid offset: {offset}")
        http_error(400, "Offset must be >= 0", logger.error, {"offset": offset})
    if limit < 1 or limit > MAX_LIMIT:
        logger.error(f"Invalid limit: {limit}")
        http_error(
            400,
            f"Limit must be between 1 and {MAX_LIMIT}",
            logger.error,
            {"limit": limit},
        )
    logger.info(f"Pagination params accepted: offset={offset}, limit={limit}")
    return PaginationParams(offset=offset, limit=limit)


# --- Auth Dependencies ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Dependency to extract and validate a JWT token from the request and fetch the current user from the database.

    Parameters:
        token (str): JWT access token from the Authorization header.
        session (AsyncSession): SQLAlchemy async session.
    Returns:
        User: The authenticated and active user instance.
    Raises:
        HTTPException(401): If token is invalid/expired, or user is not found/inactive/deleted.
    Usage:
        user = Depends(get_current_user)
    """
    settings = get_settings()
    if not settings.auth_enabled:
        logger.warning("Authentication is DISABLED! Returning development admin user.")
        return _get_dev_admin_user()
    user_id = None
    role = None
    try:
        payload = verify_access_token(token)
        if not payload:
            logger.error("Token verification returned empty payload")
            raise ValueError("Empty payload")
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id:
            logger.error("Token payload missing 'sub' (user id)")
            raise ValueError("Missing user id")
    except (JWTError, ValueError, TypeError) as err:
        logger.error(f"Token validation failed: {err}")
        http_error(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid token",
            logger.error,
            {"error": str(err)},
            err,
        )
    # Support both int and str (email) user_id
    user = None
    if user_id is not None:
        from sqlalchemy import select

        from src.models.user import User

        if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
            user = await get_user_by_id(session, int(user_id))
        else:
            result = await session.execute(
                select(User).where(User.email == str(user_id))
            )
            user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_deleted:
        logger.error(f"User not found or inactive/deleted: user_id={user_id}")
        http_error(
            status.HTTP_401_UNAUTHORIZED,
            "User not found or inactive",
            logger.warning,
            {"user_id": user_id},
        )
        raise ValueError("User not found or inactive")
    # Attach role from JWT if present
    if role:
        user.role = role
    logger.info(f"User authenticated: user_id={user_id}, role={role}")
    return user


async def optional_get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """
    Like get_current_user, but returns None instead of raising if token is invalid/missing.

    Parameters:
        token (str): JWT access token from the Authorization header.
        session (AsyncSession): SQLAlchemy async session.
    Returns:
        User | None: The authenticated user, or None if not authenticated.
    Usage:
        user = Depends(optional_get_current_user)
    """
    settings = get_settings()
    if not settings.auth_enabled:
        return _get_dev_admin_user()
    try:
        payload = verify_access_token(
            token
        )  # Only pass token, matches function signature
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            return None
        user_id = int(user_id_raw)
        user = await get_user_by_id(session, user_id)
        if not user or not user.is_active or user.is_deleted:
            return None
        return user
    except Exception:
        return None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a SQLAlchemy AsyncSession for database operations.

    Yields:
        AsyncSession: SQLAlchemy async session for DB operations.
    Raises:
        HTTPException(500): If database session cannot be established or used.
    Usage:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    from src.core.database import AsyncSessionLocal

    session = AsyncSessionLocal()
    logger.info("Database session created.")
    try:
        yield session
    except Exception as exc:
        logger.error(f"Database session error: {exc}")
        await session.rollback()
        http_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error. Please try again later.",
            logger.error,
            {"error": str(exc)},
            exc,
        )
    finally:
        await session.close()
        logger.info("Database session closed.")


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the current user is active.

    Parameters:
        user (User): The user instance from get_current_user.
    Returns:
        User: The active user instance.
    Raises:
        HTTPException(403): If the user is inactive or deleted.
    Usage:
        user = Depends(get_current_active_user)
    """
    if not user.is_active or user.is_deleted:
        logger.error(f"Inactive or deleted user tried to access: user_id={user.id}")
        http_error(
            status.HTTP_403_FORBIDDEN,
            "Inactive or deleted user.",
            logger.warning,
            {"user_id": user.id},
        )
    logger.info(f"Active user check passed: user_id={user.id}")
    return user


def get_request_id(request: Request) -> str:
    """
    Dependency to extract or generate a request ID for tracing.

    Parameters:
        request (Request): FastAPI request object.
    Returns:
        str: The request ID (from header or generated UUID).
    Usage:
        request_id = Depends(get_request_id)
    """
    req_id = request.headers.get(REQUEST_ID_HEADER)
    # Basic validation: must be a valid UUID or a string of reasonable length
    try:
        if req_id:
            uuid.UUID(str(req_id))
        else:
            raise ValueError
    except (ValueError, TypeError):
        req_id = str(uuid.uuid4())
    request_id_ctx_var.set(req_id)
    return req_id


def get_current_request_id() -> str | None:
    """
    Helper to get the current request ID from contextvar.

    Returns:
        str | None: The current request ID, or None if not set.
    Usage:
        req_id = get_current_request_id()
    """
    return request_id_ctx_var.get()


# --- API key security scheme
async def validate_api_key(
    api_key: str = Security(api_key_header),
) -> bool:
    """
    Validate the API key from the X-API-Key header.

    Parameters:
        api_key (str): API key from the X-API-Key header.
    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    settings = get_settings()

    if not settings.api_key_enabled:
        # API key validation is disabled, always return True
        return True

    # If API key validation is enabled but no key provided
    if not api_key:
        logger.warning(
            "API key validation is enabled but no API key provided in request"
        )
        return False

    # Get the configured API key from settings
    configured_api_key = settings.api_key
    if not configured_api_key:
        logger.warning("API key validation is enabled but no API key is configured")
        return False

    # Check if the provided API key matches the configured one
    return api_key == configured_api_key


async def require_api_key(
    api_key: str = Security(api_key_header),
) -> None:
    """
    Dependency to require a valid API key.

    Parameters:
        api_key (str): API key from the X-API-Key header.
    Raises:
        HTTPException(401): If the API key is missing or invalid.
    Usage:
        _ = Depends(require_api_key)
    """
    validation_result = await validate_api_key(api_key)

    if not validation_result:
        http_error(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or missing API key",
            logger.warning,
            {"api_key": api_key},
        )


# Updated get_current_user that requires API key
async def get_current_user_with_api_key(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_api_key),
) -> User:
    """
    Like get_current_user, but also requires a valid API key.
    This function should be used for endpoints that require both
    JWT authentication and API key validation.
    """
    return await get_current_user(token, session)


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency that ensures the current user is an admin.
    Raises 403 if not.
    """
    if not current_user or not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )
    return current_user


def require_api_key_for_exports(
    api_key: str | None = Header(None, alias="X-API-Key"),
) -> None:
    """
    Dependency to validate API key for export endpoints based on global settings.
    If REVIEWPOINT_API_KEY_ENABLED is true, this requires a valid API key.
    If REVIEWPOINT_API_KEY_ENABLED is false, this function does nothing and allows access.

    NOTE: This function is deprecated. Use get_current_user_with_export_api_key instead
    which handles both JWT and API key validation in one dependency.

    Parameters:
        api_key (str): API key from the X-API-Key header.
    Raises:
        HTTPException(401): If API keys are enabled and the API key is missing or invalid.
    Usage:
        _ = Depends(require_api_key_for_exports)
    """
    settings = get_settings()

    # If API key validation is disabled globally, allow access
    if not settings.api_key_enabled:
        return

    # API key validation is enabled, so require it
    if not api_key:
        logger.warning(
            "Export endpoint accessed without API key when API key validation is enabled"
        )
        http_error(
            status.HTTP_401_UNAUTHORIZED,
            "API key required for export endpoints",
            logger.warning,
            {"endpoint": "export"},
        )

    # Get the configured API key from settings
    configured_api_key = settings.api_key
    if not configured_api_key:
        logger.warning("API key validation required but no API key is configured")
        http_error(
            status.HTTP_401_UNAUTHORIZED,
            "API key validation is not properly configured",
            logger.warning,
            {"endpoint": "export"},
        )

    # Check if the provided API key matches the configured one
    if api_key != configured_api_key:
        logger.warning("Invalid API key provided for export endpoint")
        http_error(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid API key",
            logger.warning,
            {"endpoint": "export"},
        )


async def get_current_user_with_export_api_key(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """
    Authentication dependency for export endpoints that respects global API key settings.

    When REVIEWPOINT_AUTH_ENABLED is false:
        - Returns development admin user regardless of token validity

    When REVIEWPOINT_AUTH_ENABLED is true and REVIEWPOINT_API_KEY_ENABLED is true:
        - Requires both valid JWT token and API key
        - Returns the authenticated User

    When REVIEWPOINT_AUTH_ENABLED is true and REVIEWPOINT_API_KEY_ENABLED is false:
        - Only requires JWT token (if provided)
        - If JWT token is provided, validates it and returns User
        - If JWT token is invalid, raises 401 error
        - If no JWT token is provided, returns None (unauthenticated access allowed)
    """
    settings = get_settings()

    # Check if authentication is disabled globally
    if not settings.auth_enabled:
        logger.warning("Authentication is DISABLED! Returning development admin user.")
        return _get_dev_admin_user()

    # Check JWT token first (regardless of API key setting)
    authorization = request.headers.get("Authorization")

    if authorization:
        # If Authorization header is provided, validate it
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                http_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "Invalid authentication scheme",
                    logger.warning,
                    {"endpoint": "export"},
                )
                return None  # This line will never be reached due to http_error, but helps with type checking
        except ValueError:
            http_error(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid authorization header format",
                logger.warning,
                {"endpoint": "export"},
            )
            return None  # This line will never be reached due to http_error, but helps with type checking

        # Validate JWT token - always do full validation when auth is enabled
        current_user = await get_current_user(token, session)

        # If API key validation is enabled, also check API key
        if settings.api_key_enabled:
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                logger.warning(
                    "Export endpoint accessed without API key when API key validation is enabled"
                )
                http_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "API key required for export endpoints",
                    logger.warning,
                    {"endpoint": "export"},
                )

            # Get the configured API key from settings
            configured_api_key = settings.api_key
            if not configured_api_key:
                logger.warning(
                    "API key validation required but no API key is configured"
                )
                http_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "API key validation is not properly configured",
                    logger.warning,
                    {"endpoint": "export"},
                )

            # Check if the provided API key matches the configured one
            if api_key != configured_api_key:
                logger.warning("Invalid API key provided for export endpoint")
                http_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "Invalid API key",
                    logger.warning,
                    {"endpoint": "export"},
                )

        return current_user
    else:
        # No Authorization header provided
        if settings.api_key_enabled:
            # API key validation is enabled, so authentication is required
            http_error(
                status.HTTP_401_UNAUTHORIZED,
                "Authentication required",
                logger.warning,
                {"endpoint": "export"},
            )
        else:
            # API key validation is disabled, allow unauthenticated access
            return None


get_user_repository: Callable[[], object] = lru_cache()(get_user_repository_func)
