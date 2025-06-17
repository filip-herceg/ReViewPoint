from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegisterRequest,
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
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


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLoginRequest,
    request: Request,
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


@router.post("/logout", response_model=MessageResponse)
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


@router.post("/refresh-token", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
    limiter_key = f"refresh:{current_user.id}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning("refresh_rate_limited", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=429,
            detail="Too many token refresh attempts. Please try again later.",
        )
    # Check if refresh token is blacklisted
    try:
        payload = jwt.decode(
            refresh_token,
            str(settings.jwt_secret_key),
            algorithms=[settings.jwt_algorithm],
        )
        jti = payload.get("jti") or refresh_token
        if await is_token_blacklisted(session, jti):
            logger.warning(
                "refresh_token_blacklisted", extra={"user_id": current_user.id}
            )
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token."
            )
    except Exception as e:
        logger.warning(
            "refresh_token_decode_failed",
            extra={"user_id": current_user.id, "error": str(e)},
        )
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token."
        ) from e
    try:
        token = user_service.refresh_access_token(current_user.id, refresh_token)
        logger.info("refresh_success", extra={"user_id": current_user.id})
        return AuthResponse(access_token=token)
    except user_service.ValidationError as e:
        logger.warning("refresh_validation_error", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token."
        ) from e
    except Exception as e:
        logger.error(
            "refresh_unexpected_error",
            extra={"user_id": current_user.id, "error": str(e)},
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        ) from e


@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    data: PasswordResetRequest,
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


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirmRequest,
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    if len(data.token) < 8:
        logger.warning("pwreset_confirm_invalid_token_length", extra={"token": data.token})
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


@router.get("/me", response_model=UserProfile)
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
