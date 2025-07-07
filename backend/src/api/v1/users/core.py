"""
User CRUD endpoints: create, list, get, update, delete.
"""

import traceback
from collections.abc import Sequence
from typing import Any, Final, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    PaginationParams,
    get_user_service,
    pagination_params,
    require_admin,
    require_api_key,
    require_feature,
)
from src.core.database import get_async_session
from src.schemas.user import UserCreateRequest, UserListResponse
from src.schemas.user import UserProfile as UserResponse
from src.services.user import (
    InvalidDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)
from src.utils.errors import ValidationError as CustomValidationError
from src.utils.http_error import ExtraLogInfo, http_error

router: Final[APIRouter] = APIRouter()


@router.post(
    "",
    summary="Create a new user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_feature("users:create")),
        Depends(require_api_key),
    ],
)
async def create_user(
    user: UserCreateRequest = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create a new user.
    Raises:
        HTTPException: If user already exists, data is invalid, or unexpected error occurs.
    """
    # db_user is likely an ORM User, not UserProfile, so we use Any and map to UserResponse
    db_user: Any
    try:
        db_user = await user_service.register_user(
            session,
            {
                "email": user.email,
                "password": user.password,
                "name": user.name,
            },
        )
        logger.info(
            "user_created", extra={"user_id": db_user.id, "email": db_user.email}
        )
        return UserResponse(id=db_user.id, email=db_user.email, name=db_user.name)
    except UserAlreadyExistsError:
        # Idempotent: fetch and return the existing user
        from src.repositories.user import list_users

        users: Sequence[Any]
        users, _ = await list_users(session, email=user.email, limit=1)
        if users:
            existing_user: Any = users[0]
            logger.info(
                "user_exists_idempotent",
                extra={"user_id": existing_user.id, "email": existing_user.email},
            )
            raise HTTPException(
                status_code=409,
                detail="Email already exists.",
            )
        raise HTTPException(status_code=409, detail="Email already exists.")
    except InvalidDataError:
        raise HTTPException(status_code=400, detail="Invalid user data.")
    except CustomValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


@router.get(
    "",
    summary="List users",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_feature("users:list")),
        Depends(require_api_key),
    ],
)
async def list_users(
    params: PaginationParams = Depends(pagination_params),
    email: str | None = Query(None, description="Filter by email"),
    name: str | None = Query(None, description="Filter by name"),
    created_after: str | None = Query(
        None, description="Filter by created_after datetime"
    ),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(require_admin),
) -> UserListResponse:
    """
    List users with optional filters.
    Raises:
        HTTPException: If an unexpected error occurs.
    """
    created_after_dt: Any | None = (
        None  # parse_flexible_datetime returns datetime, but type not imported here
    )
    # Parse created_after if provided
    if created_after:
        from src.utils.datetime import parse_flexible_datetime

        created_after_dt = parse_flexible_datetime(created_after)

    users = await user_service.list_users(
        session,
        offset=params.offset,
        limit=params.limit,
        email=email,
        name=name,
        created_after=created_after_dt,
    )
    logger.info(
        "users_listed",
        extra={
            "offset": params.offset,
            "limit": params.limit,
            "email": email,
            "name": name,
        },
    )
    return UserListResponse(
        users=[
            UserResponse(
                id=u.id,
                email=u.email,
                name=u.name,
                bio=u.bio,
                avatar_url=u.avatar_url,
                created_at=u.created_at.isoformat() if u.created_at else None,
                updated_at=u.updated_at.isoformat() if u.updated_at else None,
            )
            for u in users
        ],
        total=len(users),
    )


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_feature("users:read")),
        Depends(require_api_key),
    ],
)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(require_admin),
) -> UserResponse:
    """
    Get user by ID.
    Raises:
        HTTPException: If user not found or unexpected error occurs.
    """
    try:
        user: Any = await user_service.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Explicitly map ORM user to UserResponse
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    except HTTPException as exc:
        raise exc
    except Exception as e:
        logger.error(f"Unexpected error in get_user_by_id: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")
    # Defensive: function must always return UserResponse or raise
    raise HTTPException(status_code=500, detail="Unreachable code in get_user_by_id")


@router.put(
    "/{user_id}",
    summary="Update user information",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    user: UserCreateRequest = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(require_admin),
) -> UserResponse:
    """
    Update user information.
    Raises:
        HTTPException: If user not found, email exists, invalid data, or unexpected error occurs.
    """
    try:
        updated_user: Any = await user_service.update_user(
            session, user_id, user.model_dump()
        )
        logger.info("user_updated", extra={"user_id": user_id})
        return UserResponse(
            id=updated_user.id, email=updated_user.email, name=updated_user.name
        )
    except UserNotFoundError as e:
        http_error(404, "User not found.", logger.warning, cast(ExtraLogInfo, {"user_id": user_id}), e)
        raise HTTPException(status_code=404, detail="User not found.")
    except UserAlreadyExistsError as e:
        http_error(
            409, "Email already exists.", logger.warning, cast(ExtraLogInfo, {"email": user.email}), e
        )
        raise HTTPException(status_code=409, detail="Email already exists.")
    except InvalidDataError as e:
        http_error(400, "Invalid user data.", logger.warning, cast(ExtraLogInfo, {"user_id": user_id}), e)
        raise HTTPException(status_code=400, detail="Invalid user data.")
    except Exception as e:
        http_error(
            500,
            "Unexpected error.",
            logger.error,
            cast(ExtraLogInfo, {"user_id": user_id, "error": str(e)}),
            e,
        )
        raise HTTPException(status_code=500, detail="Unexpected error.")
    # Defensive: function must always return UserResponse or raise
    raise HTTPException(status_code=500, detail="Unreachable code in update_user")


@router.delete(
    "/{user_id}",
    summary="Delete user",
    status_code=204,
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(),
    current_user: UserResponse = Depends(require_admin),
) -> Response:
    """
    Delete user by ID.
    Raises:
        HTTPException: If user not found or unexpected error occurs.
    """
    STATUS_NO_CONTENT = 204
    try:
        result: None = await user_service.delete_user(session, user_id)
        logger.info("user_deleted", extra={"user_id": user_id})
        return Response(status_code=STATUS_NO_CONTENT)
    except UserNotFoundError as e:
        http_error(404, "User not found.", logger.warning, cast(ExtraLogInfo, {"user_id": user_id}), e)
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception as e:
        http_error(
            500,
            "Unexpected error.",
            logger.error,
            cast(ExtraLogInfo, {"user_id": user_id, "error": str(e)}),
            e,
        )
        raise HTTPException(status_code=500, detail="Unexpected error.")
    # Defensive: function must always return Response or raise
    raise HTTPException(status_code=500, detail="Unreachable code in delete_user")
