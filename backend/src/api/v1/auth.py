from datetime import UTC, datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from jose import jwt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.core.config import settings
from src.core.database import get_async_session
from src.models.user import User
from src.repositories.blacklisted_token import blacklist_token, is_token_blacklisted
from src.repositories.user import user_action_limiter
from src.schemas.auth import (
    AuthResponse,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from src.schemas.user import UserProfile
from src.services import user as user_service


# Define JWTError class
class JWTError(Exception):
    """JWTError class for handling JWT exceptions"""

    pass


router = APIRouter(prefix="/auth", tags=["Auth"])


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
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {"example": {"access_token": "<jwt_token>"}}
            },
        },
        400: {
            "description": "Validation error or duplicate email",
            "content": {
                "application/json": {
                    "example": {"detail": "User with this email already exists."}
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        409: {
            "description": "Conflict. Email already exists.",
            "content": {
                "application/json": {"example": {"detail": "Email already registered."}}
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {"application/json": {"example": {"detail": "Invalid input."}}},
        },
        429: {
            "description": "Too many registration attempts",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Too many registration attempts. Please try again later."
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred. Please try again later."
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": 'curl -X POST \'https://api.reviewpoint.org/api/v1/auth/register\' \\\n  -H \'Content-Type: application/json\' \\\n  -d \'{"email":"user@example.com","password":"strongpassword123","name":"Jane Doe"}\'',
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\nurl = \'https://api.reviewpoint.org/api/v1/auth/register\'\ndata = {"email": "user@example.com", "password": "strongpassword123", "name": "Jane Doe"}\nresponse = requests.post(url, json=data)\nprint(response.json())',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/auth/register', {\n  method: 'POST',\n  headers: { 'Content-Type': 'application/json' },\n  body: JSON.stringify({\n    email: 'user@example.com',\n    password: 'strongpassword123',\n    name: 'Jane Doe'\n  })\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "bytes"\n  "net/http"\n)\nfunc main() {\n  body := []byte(`{\\"email\\":\\"user@example.com\\",\\"password\\":\\"strongpassword123\\",\\"name\\":\\"Jane Doe\\"}`)\n  req, _ := http.NewRequest("POST", "https://api.reviewpoint.org/api/v1/auth/register", bytes.NewBuffer(body))\n  req.Header.Set("Content-Type", "application/json")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nMediaType mediaType = MediaType.parse("application/json");\nRequestBody body = RequestBody.create(mediaType, "{\\"email\\":\\"user@example.com\\",\\"password\\":\\"strongpassword123\\",\\"name\\":\\"Jane Doe\\"}");\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/auth/register")\n  .post(body)\n  .addHeader("Content-Type", "application/json")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/auth/register');\ncurl_setopt($ch, CURLOPT_POST, 1);\ncurl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['email' => 'user@example.com', 'password' => 'strongpassword123', 'name' => 'Jane Doe']));\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nrequire 'json'\nuri = URI('https://api.reviewpoint.org/api/v1/auth/register')\nreq = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')\nreq.body = {email: 'user@example.com', password: 'strongpassword123', name: 'Jane Doe'}.to_json\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http POST https://api.reviewpoint.org/api/v1/auth/register email=user@example.com password=strongpassword123 name='Jane Doe'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$body = @{email='user@example.com'; password='strongpassword123'; name='Jane Doe'} | ConvertTo-Json\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/auth/register' -Method Post -Body $body -ContentType 'application/json'",
            },
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "password": "strongpassword123",
                        "name": "Jane Doe",
                    }
                }
            }
        },
    },
    tags=["Auth"],
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
) -> AuthResponse:
    """
    Registers a new user.
    - **data**: User registration data (email, password, name)
    - **session**: Database session
    Returns a JWT access token on success.
    """
    limiter_key = f"register:{data.email}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning("registration_rate_limited", extra={"email": data.email})
        raise HTTPException(
            status_code=429,
            detail="Too many registration attempts. Please try again later.",
        )
    # Enhanced validation
    from src.utils.validation import get_password_validation_error, validate_email

    if not validate_email(data.email):
        logger.warning("registration_invalid_email", extra={"email": data.email})
        raise HTTPException(status_code=400, detail="Invalid email format.")
    pw_error = get_password_validation_error(data.password)
    if pw_error:
        logger.warning("registration_invalid_password", extra={"email": data.email})
        raise HTTPException(status_code=400, detail=pw_error)
    logger.info("registration_attempt", extra={"email": data.email})
    try:
        user = await user_service.register_user(session, data.model_dump())
        token = user_service.create_access_token(
            {"sub": str(user.id), "email": user.email}
        )
        logger.info(
            "registration_success", extra={"user_id": user.id, "email": user.email}
        )
        return AuthResponse(access_token=token)
    except user_service.UserAlreadyExistsError as e:
        logger.warning("registration_duplicate_email", extra={"email": data.email})
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        ) from e
    except user_service.InvalidDataError as e:
        logger.warning("registration_invalid_data", extra={"email": data.email})
        raise HTTPException(status_code=400, detail="Invalid registration data.") from e
    except Exception as e:
        logger.error(
            "registration_unexpected_error",
            extra={"email": data.email, "error": str(e)},
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        ) from e


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
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {"example": {"access_token": "<jwt_token>"}}
            },
        },
        400: {
            "description": "Invalid email format",
            "content": {
                "application/json": {"example": {"detail": "Invalid email format."}}
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "Invalid credentials"}}
            },
        },
        429: {
            "description": "Too many login attempts",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Too many login attempts. Please try again later."
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred. Please try again later."
                    }
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": 'curl -X POST \'https://api.reviewpoint.org/api/v1/auth/login\' \\\n  -H \'Content-Type: application/json\' \\\n  -d \'{"email":"user@example.com","password":"mypassword"}\'',
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\nurl = \'https://api.reviewpoint.org/api/v1/auth/login\'\ndata = {"email": "user@example.com", "password": "mypassword"}\nresponse = requests.post(url, json=data)\nprint(response.json())',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/auth/login', {\n  method: 'POST',\n  headers: { 'Content-Type': 'application/json' },\n  body: JSON.stringify({\n    email: 'user@example.com',\n    password: 'mypassword'\n  })\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {"email": "user@example.com", "password": "mypassword"}
                }
            }
        },
    },
    tags=["Auth"],
)
async def login(
    request: Request,
    data: UserLoginRequest = Body(
        ...,
        description="User login credentials.",
        examples=[{"summary": "User login", "value": {"email": "user@example.com"}}],
    ),
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
    limiter_key = f"login:{data.email}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning("login_rate_limited", extra={"email": data.email})
        raise HTTPException(
            status_code=429, detail="Too many login attempts. Please try again later."
        )
    # Enhanced validation
    from src.utils.validation import validate_email

    if not validate_email(data.email):
        logger.warning("login_invalid_email", extra={"email": data.email})
        raise HTTPException(status_code=400, detail="Invalid email format.")
    logger.info("login_attempt", extra={"email": data.email})
    try:
        token = await user_service.authenticate_user(session, data.email, data.password)
        logger.info("login_success", extra={"email": data.email})
        return AuthResponse(access_token=token)
    except user_service.UserNotFoundError as e:
        logger.warning("login_user_not_found", extra={"email": data.email})
        raise HTTPException(status_code=401, detail="Invalid credentials") from e
    except user_service.ValidationError as e:
        logger.warning("login_validation_error", extra={"email": data.email})
        raise HTTPException(status_code=401, detail="Invalid credentials") from e
    except Exception as e:
        logger.error(
            "login_unexpected_error", extra={"email": data.email, "error": str(e)}
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        ) from e


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
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {"example": {"message": "Logged out successfully."}}
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        429: {
            "description": "Too many logout attempts",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Too many logout attempts. Please try again later."
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred. Please try again later."
                    }
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -X POST 'https://api.reviewpoint.org/api/v1/auth/logout' \\\n  -H 'Authorization: Bearer <token>'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/auth/logout'\nheaders = {'Authorization': 'Bearer <token>'}\nresponse = requests.post(url, headers=headers)\nprint(response.json())",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/auth/logout', {\n  method: 'POST',\n  headers: { 'Authorization': 'Bearer <token>' }\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
        ]
    },
    tags=["Auth"],
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    limiter_key = f"logout:{current_user.id}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning("logout_rate_limited", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=429, detail="Too many logout attempts. Please try again later."
        )
    logger.info("logout_attempt", extra={"user_id": current_user.id})
    # Blacklist the current access token if present
    auth_header = request.headers.get("authorization") if request else None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            if not settings.jwt_secret_key:
                raise ValueError("JWT secret key is not configured.")
            payload = jwt.decode(
                token, str(settings.jwt_secret_key), algorithms=[settings.jwt_algorithm]
            )
            jti = payload.get("jti") or token  # fallback to token string if no jti
            exp = payload.get("exp")
            if exp:
                expires_at = datetime.fromtimestamp(exp, tz=UTC)
                await blacklist_token(session, jti, expires_at)
                logger.info(
                    "logout_token_blacklisted", extra={"user_id": current_user.id}
                )
        except Exception as e:
            logger.error("logout_token_blacklist_error", extra={"error": str(e)})
    await user_service.logout_user(session, current_user.id)
    logger.info("logout_success", extra={"user_id": current_user.id})
    return MessageResponse(message="Logged out successfully.")


@router.post(
    "/refresh-token",
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
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {"example": {"access_token": "<jwt_token>"}}
            },
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired refresh token."}
                }
            },
        },
        429: {
            "description": "Too many token refresh attempts",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Too many token refresh attempts. Please try again later."
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred. Please try again later."
                    }
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -X POST 'https://api.reviewpoint.org/api/v1/auth/refresh-token' \\\n  -H 'Authorization: Bearer <refresh_token>'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/auth/refresh-token'\nheaders = {'Authorization': 'Bearer <refresh_token>'}\nresponse = requests.post(url, headers=headers)\nprint(response.json())",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/auth/refresh-token', {\n  method: 'POST',\n  headers: { 'Authorization': 'Bearer <refresh_token>' }\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
        ]
    },
    tags=["Auth"],
)
async def refresh_token(
    refresh_token: str = Body(
        None,
        description="The refresh token to use for obtaining a new access token.",
        examples=[{"summary": "A refresh token", "value": "<refresh_token>"}],
    ),
    refresh_token_query: str = Query(
        None, description="The refresh token (alternative, via query param)."
    ),
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
    token = refresh_token or refresh_token_query
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    # Decode token to get user_id for rate limiting
    try:
        # Decode the refresh token
        payload = jwt.decode(
            token,
            str(settings.jwt_secret_key),
            algorithms=[settings.jwt_algorithm],
        )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token format.")

        # Apply rate limiting
        limiter_key = f"refresh:{user_id}"
        # Check if rate limiting is enabled and function is callable
        if callable(user_action_limiter):
            is_allowed = await user_action_limiter(
                limiter_key, max_attempts=15, window_seconds=3600
            )
            if not is_allowed:
                logger.warning("refresh_rate_limited", extra={"user_id": user_id})
                raise HTTPException(
                    status_code=429,
                    detail="Too many token refresh attempts. Please try again later.",
                )
        # Check if refresh token is blacklisted
        jti = payload.get("jti") or token
        if await is_token_blacklisted(session, jti):
            logger.warning("refresh_token_blacklisted", extra={"user_id": user_id})
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token."
            )  # Get new token
        new_token = user_service.refresh_access_token(user_id, token)
        logger.info("refresh_success", extra={"user_id": user_id})
        return AuthResponse(access_token=new_token)

    except JWTError as e:
        # Handle JWT decoding errors
        user_id = None if "payload" not in locals() else payload.get("user_id")
        logger.warning(
            "refresh_token_decode_failed",
            extra={
                "user_id": user_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token."
        ) from e
    except Exception as e:
        # Only handle exceptions that are not JWTError
        if isinstance(e, JWTError):
            # This should never happen as JWTError is caught above
            raise

        # Handle all other unexpected errors
        user_id = None if "payload" not in locals() else payload.get("user_id")
        logger.error(
            "refresh_unexpected_error",
            extra={
                "user_id": user_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        ) from e


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
    responses={
        200: {
            "description": "Password reset link sent",
            "content": {
                "application/json": {
                    "example": {"message": "Password reset link sent."}
                }
            },
        },
        429: {
            "description": "Too many password reset requests",
            "content": {
                "application/json": {
                    "example": {"message": "Password reset link sent."}
                }
            },
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {"application/json": {"example": {"email": "user@example.com"}}}
        }
    },
)
async def request_password_reset(
    data: PasswordResetRequest = Body(
        ...,
        description="The email address to send the password reset link to.",
        examples=[{"summary": "User email", "value": "user@example.com"}],
    ),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    limiter_key = f"pwreset:{data.email}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning("pwreset_rate_limited", extra={"email": data.email})
        return MessageResponse(message="Password reset link sent.")
    # Enhanced validation
    from src.utils.validation import validate_email

    if not validate_email(data.email):
        logger.warning("pwreset_invalid_email", extra={"email": data.email})
        return MessageResponse(message="Password reset link sent.")
    logger.info("pwreset_requested", extra={"email": data.email})
    try:
        user_service.get_password_reset_token(data.email)
        logger.info("pwreset_link_generated", extra={"email": data.email})
        return MessageResponse(message="Password reset link sent.")
    except Exception as e:
        logger.warning(
            "pwreset_request_failed", extra={"email": data.email, "error": str(e)}
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
    responses={
        200: {
            "description": "Password has been reset",
            "content": {
                "application/json": {"example": {"message": "Password has been reset."}}
            },
        },
        400: {
            "description": "Invalid token or password",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token. Token must be at least 8 characters long."
                    }
                }
            },
        },
        429: {
            "description": "Too many password reset attempts",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Too many password reset attempts. Please try again later."
                    }
                }
            },
        },
    },
)
async def reset_password(
    data: PasswordResetConfirmRequest = Body(
        ...,
        description="The password reset token and new password.",
        examples=[
            {
                "summary": "Reset password",
                "value": {
                    "token": "reset-token-123",
                    "new_password": "newsecurepassword",
                },
            }
        ],
    ),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    if len(data.token) < 8:
        logger.warning(
            "pwreset_confirm_invalid_token_length", extra={"token": data.token}
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid token. Token must be at least 8 characters long.",
        )
    limiter_key = f"pwreset-confirm:{data.token[:8]}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning(
            "pwreset_confirm_rate_limited", extra={"token_prefix": data.token[:8]}
        )
        raise HTTPException(
            status_code=429,
            detail="Too many password reset attempts. Please try again later.",
        )
    # Enhanced validation
    from src.utils.validation import get_password_validation_error

    pw_error = get_password_validation_error(data.new_password)
    if pw_error:
        logger.warning(
            "pwreset_confirm_invalid_password", extra={"token_prefix": data.token[:8]}
        )
        raise HTTPException(status_code=400, detail=pw_error)
    logger.info("pwreset_confirm_attempt", extra={"token_prefix": data.token[:8]})
    try:
        await user_service.reset_password(session, data.token, data.new_password)
        logger.info("pwreset_confirm_success", extra={"token_prefix": data.token[:8]})
        return MessageResponse(message="Password has been reset.")
    except user_service.ValidationError as e:
        logger.warning(
            "pwreset_confirm_validation_error", extra={"token_prefix": data.token[:8]}
        )
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.warning(
            "pwreset_confirm_failed",
            extra={"token_prefix": data.token[:8], "error": str(e)},
        )
        raise HTTPException(
            status_code=400,
            detail="An error occurred while resetting the password. Please try again later.",
        ) from e


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
    responses={
        200: {
            "description": "User profile returned",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "name": "Jane Doe",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -X GET 'https://api.reviewpoint.org/api/v1/auth/me' \\\n  -H 'Authorization: Bearer <token>'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/auth/me'\nheaders = {'Authorization': 'Bearer <token>'}\nresponse = requests.get(url, headers=headers)\nprint(response.json())",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/auth/me', {\n  method: 'GET',\n  headers: { 'Authorization': 'Bearer <token>' }\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
        ],
        "security": [{"BearerAuth": []}],
    },
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserProfile:
    logger.info("Get current user info", user_id=current_user.id)
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
