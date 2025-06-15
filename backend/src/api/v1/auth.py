from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
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
from src.services import user as user_service
from src.repositories.user import user_action_limiter
from src.utils.errors import RateLimitExceededError

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
        logger.warning(f"Rate limit exceeded for registration: {data.email}")
        raise HTTPException(status_code=429, detail="Too many registration attempts. Please try again later.")
    logger.info("User registration attempt", email=data.email)
    try:
        user = await user_service.register_user(session, data.model_dump())
        token = user_service.create_access_token(
            {"sub": str(user.id), "email": user.email}
        )
        logger.info("User registered", user_id=user.id)
        return AuthResponse(access_token=token)
    except user_service.UserAlreadyExistsError as e:
        logger.warning(f"Registration failed for {data.email}: {e}")
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        ) from e
    except user_service.InvalidDataError as e:
        logger.warning(f"Invalid registration data for {data.email}: {e}")
        raise HTTPException(status_code=400, detail="Invalid registration data.") from e
    except Exception as e:
        logger.error(f"Unexpected error during registration for {data.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        ) from e


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLoginRequest,
    session: AsyncSession = Depends(get_async_session),
) -> AuthResponse:
    limiter_key = f"login:{data.email}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning(f"Rate limit exceeded for login: {data.email}")
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    logger.info("User login attempt", email=data.email)
    try:
        token = await user_service.authenticate_user(session, data.email, data.password)
        logger.info("User logged in", email=data.email)
        return AuthResponse(access_token=token)
    except user_service.UserNotFoundError as e:
        logger.warning(f"Login failed for {data.email}: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials") from e
    except user_service.ValidationError as e:
        logger.warning(f"Login failed for {data.email}: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials") from e
    except Exception as e:
        logger.error(f"Unexpected error during login for {data.email}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.") from e


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    limiter_key = f"logout:{current_user.id}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning(f"Rate limit exceeded for logout: {current_user.id}")
        raise HTTPException(status_code=429, detail="Too many logout attempts. Please try again later.")
    logger.info("User logout", user_id=current_user.id)
    await user_service.logout_user(session, current_user.id)
    logger.info("User logged out", user_id=current_user.id)
    return MessageResponse(message="Logged out successfully.")


@router.post("/refresh-token", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str,
    current_user: User = Depends(get_current_user),
) -> AuthResponse:
    limiter_key = f"refresh:{current_user.id}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning(f"Rate limit exceeded for refresh: {current_user.id}")
        raise HTTPException(status_code=429, detail="Too many token refresh attempts. Please try again later.")
    try:
        token = user_service.refresh_access_token(current_user.id, refresh_token)
        logger.info("Token refreshed", user_id=current_user.id)
        return AuthResponse(access_token=token)
    except user_service.ValidationError as e:
        logger.warning(f"Refresh token failed for {current_user.id}: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.") from e
    except Exception as e:
        logger.error(f"Unexpected error during token refresh for {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.") from e


@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    data: PasswordResetRequest,
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    limiter_key = f"pwreset:{data.email}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning(f"Rate limit exceeded for password reset request: {data.email}")
        return MessageResponse(message="Password reset link sent.")
    logger.info("Password reset requested", email=data.email)
    try:
        token = user_service.get_password_reset_token(data.email)
        logger.info(f"Password reset link for {data.email}: /reset-password?token=***hidden***")
        return MessageResponse(message="Password reset link sent.")
    except Exception as e:
        logger.warning(f"Password reset request failed for {data.email}: {e}")
        return MessageResponse(message="Password reset link sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirmRequest,
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    limiter_key = f"pwreset-confirm:{data.token[:8]}"
    allowed = await user_action_limiter.is_allowed(limiter_key)
    if not allowed:
        logger.warning(f"Rate limit exceeded for password reset confirm: {data.token[:8]}")
        raise HTTPException(status_code=429, detail="Too many password reset attempts. Please try again later.")
    logger.info("Password reset confirm attempt")
    try:
        await user_service.reset_password(session, data.token, data.new_password)
        logger.info("Password reset successful")
        return MessageResponse(message="Password has been reset.")
    except user_service.ValidationError as e:
        logger.warning(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.warning(f"Password reset failed: {e}")
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
