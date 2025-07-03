from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, Request, status
from jose import jwt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    get_async_refresh_access_token,
    get_blacklist_token,
    get_current_user,
    get_password_validation_error,
    get_request_id,
    get_user_action_limiter,
    get_user_service,
    get_validate_email,
    require_api_key,
    require_feature,
)
from src.core.config import get_settings
from src.core.database import get_async_session
from src.models.user import User
from src.schemas.auth import (
    AuthResponse,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from src.schemas.user import UserProfile
from src.services.user import (
    InvalidDataError,
    RefreshTokenBlacklistedError,
    RefreshTokenError,
    RefreshTokenRateLimitError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
    ValidationError,
)
from src.utils.http_error import http_error

router = APIRouter(prefix="/auth", tags=["Auth"])


# Shared async helper for rate limiting
async def check_rate_limit(
    user_action_limiter, limiter_key: str, log_extra: dict, action: str = "action"
):
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        http_error(
            429,
            f"Too many {action} attempts. Please try again later.",
            logger.warning,
            log_extra,
        )


# Common dependency group for endpoints
def common_auth_deps(feature: str):
    return [
        Depends(get_request_id),
        Depends(require_feature(feature)),
        Depends(require_api_key),
    ]


# Reusable async dependency for rate limiting


def rate_limit(action: str, key_func=None):
    async def dependency(
        request: Request,
        user_action_limiter: Any = Depends(get_user_action_limiter),
    ):
        # Compute limiter key
        if key_func:
            key = key_func(request)
        else:
            # Default: use user id or IP if available
            user = request.state.user if hasattr(request.state, "user") else None
            key = f"{action}:{getattr(user, 'id', request.client.host)}"
        allowed = await user_action_limiter.is_allowed(key)
        if not allowed:
            http_error(
                429,
                f"Too many {action} attempts. Please try again later.",
                logger.warning,
                {"limiter_key": key},
            )

    return Depends(dependency)


# =============================
# Registration & Login Endpoints
# =============================


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Registers a new user account and returns a JWT access token.

    **Steps:**
    1. User submits registration data (email, password, name).
    2. System validates input and checks for duplicate email.
    3. On success, a new user is created and a JWT access token is returned.

    **Notes:**
    - Duplicate emails are not allowed.
    - Password must meet security requirements.
    - Rate limiting is applied to prevent abuse.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:register")),
        Depends(require_api_key),
    ],
)
async def register(
    data: UserRegisterRequest = Body(
        ...,
        examples=[
            {
                "summary": "A typical registration",
                "value": {
                    "email": "user@example.com",
                    "password": "strongpassword123",
                    "name": "Jane Doe",
                },
            }
        ],
    ),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    user_action_limiter: Any = Depends(get_user_action_limiter),
) -> AuthResponse:
    await check_rate_limit(
        user_action_limiter,
        f"register:{data.email}",
        {"email": data.email},
        action="registration",
    )
    logger.info(
        f"User registration attempt: {data.email}, name: {getattr(data, 'name', None)}"
    )
    logger.debug(f"Registration payload: {data}")
    try:
        user = await user_service.register_user(session, data.model_dump())
        access_token, refresh_token = await user_service.authenticate_user(
            session, data.email, data.password
        )
        logger.info(f"User registered successfully: {user.email}")
        return AuthResponse(access_token=access_token, refresh_token=refresh_token)
    except UserAlreadyExistsError as e:
        http_error(
            400,
            "User with this email already exists.",
            logger.warning,
            {"email": data.email},
            e,
        )
    except InvalidDataError as e:
        http_error(
            400, "Invalid registration data.", logger.warning, {"email": data.email}, e
        )
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        logger.error(f"Registration failed for {data.email}: {e}\nTraceback: {tb}")
        http_error(
            400,
            "An unexpected error occurred. Please try again later.",
            logger.error,
            {"email": data.email, "error": str(e), "traceback": tb},
            e,
        )
    raise AssertionError("Unreachable")


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="""
    Authenticates a user and returns a JWT access token.

    **Steps:**
    1. User submits email and password.
    2. System validates credentials and rate limits attempts.
    3. On success, a JWT access token is returned.

    **Notes:**
    - Invalid credentials or too many attempts will result in errors.
    - Use the returned token for authenticated requests.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:login")),
        Depends(require_api_key),
    ],
)
async def login(
    data: UserLoginRequest,
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    user_action_limiter: Any = Depends(get_user_action_limiter),
) -> AuthResponse:
    await check_rate_limit(
        user_action_limiter,
        f"login:{data.email}",
        {"email": data.email},
        action="login",
    )
    logger.info(f"User login attempt: {data.email}")
    try:
        access_token, refresh_token = await user_service.authenticate_user(
            session, data.email, data.password
        )
        logger.info(f"User authenticated successfully: {data.email}")
        return AuthResponse(access_token=access_token, refresh_token=refresh_token)
    except UserNotFoundError as e:
        logger.warning(f"Login failed: {data.email}")
        http_error(401, "Invalid credentials", logger.warning, {"email": data.email}, e)
    except ValidationError as e:
        logger.warning(f"Login failed: {data.email}")
        http_error(401, "Invalid credentials", logger.warning, {"email": data.email}, e)
    except Exception as e:
        logger.error(f"Login failed: {data.email}")
        http_error(
            401,
            "An unexpected error occurred. Please try again later.",
            logger.error,
            {"email": data.email, "error": str(e)},
            e,
        )
    raise AssertionError("Unreachable")


# =============================
# Logout Endpoint
# =============================


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="""
    Logs out the current user and blacklists the access token.

    **Steps:**
    1. User sends a logout request with a valid access token.
    2. System blacklists the token and ends the session.

    **Notes:**
    - Blacklisted tokens cannot be reused.
    - Rate limiting is applied to prevent abuse.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:logout")),
        Depends(require_api_key),
    ],
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    blacklist_token: Callable[[AsyncSession, str, datetime], Awaitable[None]] = Depends(
        get_blacklist_token
    ),
) -> MessageResponse:
    logger.info("logout_attempt", extra={"user_id": current_user.id})
    auth_header = request.headers.get("authorization") if request else None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            settings = get_settings()
            if not settings.jwt_secret_key:
                raise ValueError("JWT secret key is not configured.")
            payload = jwt.decode(
                token, str(settings.jwt_secret_key), algorithms=[settings.jwt_algorithm]
            )
            jti = payload.get("jti") or token
            exp = payload.get("exp")
            if exp:
                expires_at = datetime.fromtimestamp(exp, tz=UTC)
                await blacklist_token(session, jti, expires_at)
                logger.info(
                    "logout_token_blacklisted", extra={"user_id": current_user.id}
                )
        except Exception as e:
            logger.error(
                "logout_token_blacklist_error", 
                extra={
                    "error": str(e), 
                    "error_type": type(e).__name__,
                    "user_id": current_user.id,
                    "token_length": len(token) if token else 0
                }
            )
            http_error(
                401, "Invalid or expired token.", logger.warning, {"error": str(e)}
            )
    await user_service.logout_user(session, current_user.id)
    logger.info("logout_success", extra={"user_id": current_user.id})
    return MessageResponse(message="Logged out successfully.")


# =============================
# Token Refresh Endpoint
# =============================


@router.post(
    "/refresh-token",
    response_model=AuthResponse,
    summary="Refresh JWT access token",
    description="""
    Refreshes the JWT access token using a valid refresh token.

    **Steps:**
    1. User provides a valid refresh token.
    2. System validates the token and issues a new access token.

    **Notes:**
    - Expired or blacklisted tokens will be rejected.
    - Rate limiting is applied to prevent abuse.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:refresh_token")),
        Depends(require_api_key),
    ],
)
async def refresh_token(
    body: dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_async_session),
    async_refresh_access_token: Callable[[AsyncSession, str], Awaitable[str]] = Depends(
        get_async_refresh_access_token
    ),
) -> AuthResponse:
    """
    Accepts either {"token": ...} or {"refresh_token": ...} for compatibility with tests.
    """
    token_val = body.get("token") or body.get("refresh_token")
    if not isinstance(token_val, str):
        http_error(422, "Missing refresh token.", logger.warning, {})
    assert isinstance(token_val, str)
    token = token_val  # type: str
    try:
        new_token = await async_refresh_access_token(session, token)
        logger.info("refresh_success", extra={"token": token})
        return AuthResponse(access_token=new_token, refresh_token=token)
    except RefreshTokenRateLimitError:
        http_error(
            429,
            "Too many token refresh attempts. Please try again later.",
            logger.warning,
            {"token": token},
        )
    except RefreshTokenBlacklistedError:
        http_error(
            401, "Invalid or expired refresh token.", logger.warning, {"token": token}
        )
    except RefreshTokenError:
        http_error(
            401, "Invalid or expired refresh token.", logger.warning, {"token": token}
        )
    except (ValueError, Exception) as e:
        # Treat ValueError (from verify_refresh_token) as 401 Unauthorized
        http_error(
            401,
            "Invalid or expired refresh token.",
            logger.warning,
            {"token": token, "error": str(e)},
            e,
        )
    raise AssertionError("Unreachable")


# =============================
# Password Reset Endpoints
# =============================


@router.post(
    "/request-password-reset",
    response_model=MessageResponse,
    summary="Request password reset",
    description="""
    Initiates a password reset flow.

    **Steps:**
    1. User submits email via this endpoint.
    2. System sends a password reset link to the email if it exists.
    3. User clicks the link and is directed to the reset form.
    4. User completes the process via `/reset-password`.

    **Notes:**
    - For security, this endpoint always returns a success message, even if the email is not registered.
    - Rate limiting is applied to prevent abuse.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:request_password_reset")),
        Depends(require_api_key),
    ],
)
async def request_password_reset(
    data: PasswordResetRequest,
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    user_action_limiter: Any = Depends(get_user_action_limiter),
    validate_email: Callable[[str], bool] = Depends(get_validate_email),
) -> MessageResponse:
    await check_rate_limit(
        user_action_limiter,
        f"pwreset:{data.email}",
        {"email": data.email},
        action="pwreset",
    )
    logger.info(f"Password reset requested: {data.email}")
    try:
        user_service.get_password_reset_token(data.email)
        logger.info("pwreset_link_generated", extra={"email": data.email})
        return MessageResponse(message="Password reset link sent.")
    except Exception as e:
        logger.warning(
            f"Password reset request failed: {data.email}", extra={"error": str(e)}
        )
        return MessageResponse(message="Password reset link sent.")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="""
    Completes the password reset flow using a valid reset token.

    **Steps:**
    1. User receives a reset link from `/request-password-reset`.
    2. User submits the token and new password to this endpoint.
    3. System validates the token and updates the password.

    **Notes:**
    - The token must be valid and not expired.
    - Rate limiting is applied to prevent abuse.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:reset_password")),
        Depends(require_api_key),
    ],
)
async def reset_password(
    data: PasswordResetConfirmRequest = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    get_password_validation_error: Callable[[str], str | None] = Depends(
        get_password_validation_error
    ),
) -> MessageResponse:
    pw_error = get_password_validation_error(data.new_password)
    if pw_error:
        http_error(400, pw_error, logger.warning, {"token_prefix": data.token[:8]})
    logger.info(f"Password reset confirm attempt: {data.token[:8]}")
    try:
        await user_service.reset_password(session, data.token, data.new_password)
        logger.info(f"Password reset successful: {data.token[:8]}")
        return MessageResponse(message="Password has been reset.")
    except ValidationError as e:
        http_error(
            400,
            str(e),
            logger.warning,
            {"token_prefix": data.token[:8], "error": str(e)},
            e,
        )
    except Exception as e:
        http_error(
            400,
            "An error occurred while resetting the password. Please try again later.",
            logger.error,
            {"token_prefix": data.token[:8], "error": str(e)},
            e,
        )
    raise AssertionError("Unreachable")


# =============================
# Profile Endpoint
# =============================


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
    description="""
    Returns the profile information of the currently authenticated user.

    **How it works:**
    - Requires a valid JWT Bearer token.
    - Returns user ID, email, name, bio, avatar, and timestamps.
    """,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:me")),
        Depends(require_api_key),
    ],
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    """
    Returns the profile information of the currently authenticated user.
    """
    logger.info("Get current user info", extra={"user_id": current_user.id})
    # Convert SQLAlchemy User ORM object to dict for Pydantic validation
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }
    return UserProfile.model_validate(user_dict)
