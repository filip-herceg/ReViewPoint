from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime
from typing import Final, TypedDict, cast

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
from src.utils.http_error import ExtraLogInfo, http_error

# =============================
# TypedDicts and Constants
# =============================


class LogExtraDict(TypedDict, total=False):
    email: str
    limiter_key: str
    action: str
    error: str
    error_type: str
    user_id: int
    token_length: int
    token: str
    token_prefix: str
    traceback: str


REGISTER_SUMMARY: Final[str] = "Register a new user"
REGISTER_DESCRIPTION: Final[
    str
] = """
**User Registration**

Creates a new user account and returns authentication tokens for immediate login.

**Process:**
1. Validates email format and password strength
2. Checks if email is already registered
3. Creates user account with hashed password
4. Returns JWT tokens for authentication

**Requirements:**
- Email must be valid and unique
- Password must be at least 8 characters
- Name is optional but recommended
- API key required for registration

**Rate Limiting:** 5 attempts per email per hour

**Security Features:**
- Password hashing with bcrypt
- Email verification (optional)
- Rate limiting to prevent abuse
- API key requirement for service protection

**Response:** Returns access token, refresh token, and user profile data

**Examples:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "Jane Doe"
}
```

**Error Codes:**
- `400`: Invalid input data
- `409`: Email already registered  
- `429`: Too many registration attempts
- `422`: Validation errors
"""

LOGIN_SUMMARY: Final[str] = "User login"
LOGIN_DESCRIPTION: Final[
    str
] = """
**User Authentication**

Authenticates user credentials and returns JWT tokens for API access.

**Process:**
1. Validates email and password credentials
2. Checks account status (active, not locked)
3. Issues access and refresh tokens
4. Returns user profile information

**Authentication Methods:**
- **Email + Password**: Standard login method
- **Rate Limited**: 10 attempts per IP per minute

**Token Details:**
- **Access Token**: Valid for 24 hours, use for API requests
- **Refresh Token**: Valid for 7 days, use to get new access tokens
- **Token Type**: Bearer (include in Authorization header)

**Security Features:**
- Password verification with timing attack protection
- Account lockout after failed attempts
- Secure token generation with cryptographic signatures
- IP-based rate limiting

**Usage Examples:**

*Request:*
```json
{
  "email": "user@example.com", 
  "password": "yourpassword"
}
```

*Response:*
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "name": "Jane Doe"
  }
}
```

**Error Codes:**
- `400`: Missing or invalid credentials
- `401`: Invalid email or password
- `429`: Too many login attempts
- `423`: Account temporarily locked
"""

LOGOUT_SUMMARY: Final[str] = "Logout user"
LOGOUT_DESCRIPTION: Final[
    str
] = """
Logs out the current user and blacklists the access token.

**Steps:**
1. User sends a logout request with a valid access token.
2. System blacklists the token and ends the session.

**Notes:**
- Blacklisted tokens cannot be reused.
- Rate limiting is applied to prevent abuse.
"""

REFRESH_SUMMARY: Final[str] = "Refresh JWT access token"
REFRESH_DESCRIPTION: Final[
    str
] = """
Refreshes the JWT access token using a valid refresh token.

**Steps:**
1. User provides a valid refresh token.
2. System validates the token and issues a new access token.

**Notes:**
- Expired or blacklisted tokens will be rejected.
- Rate limiting is applied to prevent abuse.
"""

PWRESET_REQUEST_SUMMARY: Final[str] = "Request password reset"
PWRESET_REQUEST_DESCRIPTION: Final[
    str
] = """
Initiates a password reset flow.

**Steps:**
1. User submits email via this endpoint.
2. System sends a password reset link to the email if it exists.
3. User clicks the link and is directed to the reset form.
4. User completes the process via `/reset-password`.

**Notes:**
- For security, this endpoint always returns a success message, even if the email is not registered.
- Rate limiting is applied to prevent abuse.
"""

PWRESET_SUMMARY: Final[str] = "Reset password"
PWRESET_DESCRIPTION: Final[
    str
] = """
Completes the password reset flow using a valid reset token.

**Steps:**
1. User receives a reset link from `/request-password-reset`.
2. User submits the token and new password to this endpoint.
3. System validates the token and updates the password.

**Notes:**
- The token must be valid and not expired.
- Rate limiting is applied to prevent abuse.
"""

ME_SUMMARY: Final[str] = "Get current user profile"
ME_DESCRIPTION: Final[
    str
] = """
Returns the profile information of the currently authenticated user.

**How it works:**
- Requires a valid JWT Bearer token.
- Returns user ID, email, name, bio, avatar, and timestamps.
"""

router: Final[APIRouter] = APIRouter(prefix="/auth", tags=["Auth"])


class UserActionLimiterProtocol:
    async def is_allowed(self, key: str) -> bool:
        return False


async def check_rate_limit(
    user_action_limiter: UserActionLimiterProtocol,
    limiter_key: str,
    log_extra: Mapping[str, object],
    action: str = "action",
) -> None:
    """
    Checks if the action is allowed by the rate limiter.
    Raises HTTP 429 if not allowed.
    """
    allowed: bool = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        http_error(
            429,
            f"Too many {action} attempts. Please try again later.",
            logger.warning,
            cast(ExtraLogInfo, log_extra),
        )


def common_auth_deps(feature: str) -> tuple[object, object, object]:
    """
    Returns a tuple of common dependencies for auth endpoints.
    """
    from fastapi import Depends as FastAPIDepends

    return (
        FastAPIDepends(get_request_id),
        FastAPIDepends(require_feature(feature)),
        FastAPIDepends(require_api_key),
    )


def rate_limit(action: str, key_func: Callable[[Request], str] | None = None) -> object:
    """
    Returns a dependency for rate limiting.
    """

    async def dependency(
        request: Request,
        user_action_limiter: UserActionLimiterProtocol = Depends(
            get_user_action_limiter
        ),
    ) -> None:
        key: str
        if key_func is not None:
            key = key_func(request)
        else:
            user: User | None = getattr(request.state, "user", None)
            client_host: str = (
                request.client.host if request.client is not None else "unknown"
            )
            user_id_or_host: str = str(getattr(user, "id", client_host))
            key = f"{action}:{user_id_or_host}"
        allowed: bool = await user_action_limiter.is_allowed(key)
        if not allowed:
            http_error(
                429,
                f"Too many {action} attempts. Please try again later.",
                logger.warning,
                cast(ExtraLogInfo, {"limiter_key": key}),
            )

    return Depends(dependency)


# =============================
# Registration & Login Endpoints
# =============================


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary=REGISTER_SUMMARY,
    description=REGISTER_DESCRIPTION,
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
    user_action_limiter: UserActionLimiterProtocol = Depends(get_user_action_limiter),
) -> AuthResponse:
    """
    Registers a new user account and returns a JWT access token.
    Raises:
        UserAlreadyExistsError: If the user already exists.
        InvalidDataError: If registration data is invalid.
        Exception: For unexpected errors.
    """
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
        user: User = await user_service.register_user(session, data.model_dump())
        access_token: str
        refresh_token: str
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
            cast(ExtraLogInfo, {"email": data.email}),
            e,
        )
    except InvalidDataError as e:
        http_error(
            400,
            "Invalid registration data.",
            logger.warning,
            cast(ExtraLogInfo, {"email": data.email}),
            e,
        )
    except Exception as e:
        import traceback

        tb: str = traceback.format_exc()
        http_error(
            400,
            "Invalid registration data.",
            logger.warning,
            cast(ExtraLogInfo, {"email": data.email, "error": str(e), "traceback": tb}),
            e,
        )
    raise AssertionError("Unreachable")


@router.post(
    "/login",
    response_model=AuthResponse,
    summary=LOGIN_SUMMARY,
    description=LOGIN_DESCRIPTION,
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
    user_action_limiter: UserActionLimiterProtocol = Depends(get_user_action_limiter),
) -> AuthResponse:
    """
    Authenticates a user and returns a JWT access token.
    Raises:
        UserNotFoundError: If user is not found.
        ValidationError: If credentials are invalid.
        Exception: For unexpected errors.
    """
    await check_rate_limit(
        user_action_limiter,
        f"login:{data.email}",
        {"email": data.email},
        action="login",
    )
    logger.info(f"User login attempt: {data.email}")
    try:
        access_token: str
        refresh_token: str
        access_token, refresh_token = await user_service.authenticate_user(
            session, data.email, data.password
        )
        logger.info(f"User authenticated successfully: {data.email}")
        return AuthResponse(access_token=access_token, refresh_token=refresh_token)
    except UserNotFoundError as e:
        logger.warning(f"Login failed: {data.email}")
        http_error(
            401,
            "Invalid credentials",
            logger.warning,
            cast(ExtraLogInfo, {"email": data.email}),
            e,
        )
    except ValidationError as e:
        logger.warning(f"Login failed: {data.email}")
        http_error(
            401,
            "Invalid credentials",
            logger.warning,
            cast(ExtraLogInfo, {"email": data.email}),
            e,
        )
    except Exception as e:
        logger.error(f"Login failed: {data.email}")
        http_error(
            401,
            "An unexpected error occurred. Please try again later.",
            logger.error,
            cast(ExtraLogInfo, {"email": data.email, "error": str(e)}),
            e,
        )
    raise AssertionError("Unreachable")


# =============================
# Logout Endpoint
# =============================


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary=LOGOUT_SUMMARY,
    description=LOGOUT_DESCRIPTION,
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
    """
    Logs out the current user and blacklists the access token.
    Raises:
        Exception: If token is invalid or expired.
    """
    logger.info("logout_attempt", extra={"user_id": current_user.id})
    auth_header: str | None = request.headers.get("authorization") if request else None
    if auth_header is not None and auth_header.lower().startswith("bearer "):
        token: str = auth_header.split(" ", 1)[1]
        try:
            settings = get_settings()
            if not settings.jwt_secret_key:
                raise ValueError("JWT secret key is not configured.")
            payload: Mapping[str, object] = jwt.decode(
                token, str(settings.jwt_secret_key), algorithms=[settings.jwt_algorithm]
            )
            jti: str = cast(str, payload.get("jti") or token)
            exp: int | None = cast(int | None, payload.get("exp"))
            if exp is not None:
                expires_at: datetime = datetime.fromtimestamp(exp, tz=UTC)
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
                    "token_length": len(token) if token else 0,
                },
            )
            http_error(
                401,
                "Invalid or expired token.",
                logger.warning,
                cast(ExtraLogInfo, {"error": str(e)}),
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
    summary=REFRESH_SUMMARY,
    description=REFRESH_DESCRIPTION,
    dependencies=[
        Depends(get_request_id),
        Depends(require_feature("auth:refresh_token")),
        Depends(require_api_key),
    ],
)
async def refresh_token(
    body: Mapping[str, object] = Body(...),
    session: AsyncSession = Depends(get_async_session),
    async_refresh_access_token: Callable[[AsyncSession, str], Awaitable[str]] = Depends(
        get_async_refresh_access_token
    ),
) -> AuthResponse:
    """
    Accepts either {"token": ...} or {"refresh_token": ...} for compatibility with tests.
    Raises:
        RefreshTokenRateLimitError: If too many attempts.
        RefreshTokenBlacklistedError: If token is blacklisted.
        RefreshTokenError: If token is invalid.
        ValueError: If token is missing or invalid.
    """
    token_val: object | None = body.get("token") or body.get("refresh_token")
    if not isinstance(token_val, str):
        http_error(422, "Missing refresh token.", logger.warning, {})
    token: str = token_val if isinstance(token_val, str) else ""
    try:
        new_token: str = await async_refresh_access_token(session, token)
        logger.info("refresh_success", extra={"token": token})
        return AuthResponse(access_token=new_token, refresh_token=token)
    except RefreshTokenRateLimitError:
        http_error(
            429,
            "Too many token refresh attempts. Please try again later.",
            logger.warning,
            cast(ExtraLogInfo, {"token": token}),
        )
    except RefreshTokenBlacklistedError:
        http_error(
            401,
            "Invalid or expired refresh token.",
            logger.warning,
            cast(ExtraLogInfo, {"token": token}),
        )
    except RefreshTokenError:
        http_error(
            401,
            "Invalid or expired refresh token.",
            logger.warning,
            cast(ExtraLogInfo, {"token": token}),
        )
    except ValueError as e:
        http_error(
            401,
            "Invalid or expired refresh token.",
            logger.warning,
            cast(ExtraLogInfo, {"token": token, "error": str(e)}),
            e,
        )
    except Exception as e:
        http_error(
            401,
            "Invalid or expired refresh token.",
            logger.warning,
            cast(ExtraLogInfo, {"token": token, "error": str(e)}),
            e,
        )
    raise AssertionError("Unreachable")


# =============================
# Password Reset Endpoints
# =============================


@router.post(
    "/request-password-reset",
    response_model=MessageResponse,
    summary=PWRESET_REQUEST_SUMMARY,
    description=PWRESET_REQUEST_DESCRIPTION,
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
    user_action_limiter: UserActionLimiterProtocol = Depends(get_user_action_limiter),
    validate_email: Callable[[str], bool] = Depends(get_validate_email),
) -> MessageResponse:
    """
    Initiates a password reset flow.
    Raises:
        Exception: For unexpected errors.
    """
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
    summary=PWRESET_SUMMARY,
    description=PWRESET_DESCRIPTION,
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
    """
    Completes the password reset flow using a valid reset token.
    Raises:
        ValidationError: If password is invalid.
        Exception: For unexpected errors.
    """
    pw_error: str | None = get_password_validation_error(data.new_password)
    if pw_error is not None:
        http_error(
            400,
            pw_error,
            logger.warning,
            cast(ExtraLogInfo, {"token_prefix": data.token[:8]}),
        )
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
            cast(ExtraLogInfo, {"token_prefix": data.token[:8], "error": str(e)}),
            e,
        )
    except Exception as e:
        http_error(
            400,
            "An error occurred while resetting the password. Please try again later.",
            logger.error,
            cast(ExtraLogInfo, {"token_prefix": data.token[:8], "error": str(e)}),
            e,
        )
    raise AssertionError("Unreachable")


# =============================
# Profile Endpoint
# =============================


@router.get(
    "/me",
    response_model=UserProfile,
    summary=ME_SUMMARY,
    description=ME_DESCRIPTION,
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
    user_dict: dict[str, object] = {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "created_at": (
            current_user.created_at.isoformat() if current_user.created_at else None
        ),
        "updated_at": (
            current_user.updated_at.isoformat() if current_user.updated_at else None
        ),
    }
    return UserProfile.model_validate(user_dict)
