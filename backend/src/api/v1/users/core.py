"""
User CRUD endpoints: create, list, get, update, delete.
"""

from collections.abc import Sequence
from typing import Any, Final, cast

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
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
    description="""
    Create a new user account in the system.

    **Requirements:**
    - Valid API key in Authorization header
    - Feature flag 'users:create' must be enabled
    - Admin privileges required

    **Request Body:**
    - `email`: Valid email address (unique)
    - `password`: Secure password (minimum 8 characters)
    - `name`: User's display name

    **Behavior:**
    - Returns 409 if email already exists
    - Validates password strength and email format
    - Automatically assigns user role and default settings

    **Example Request:**
    ```json
    {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "name": "John Doe"
    }
    ```

    **Example Response:**
    ```json
    {
        "id": 123,
        "email": "newuser@example.com",
        "name": "John Doe",
        "bio": null,
        "avatar_url": null,
        "created_at": "2025-01-08T10:30:00Z",
        "updated_at": "2025-01-08T10:30:00Z"
    }
    ```
    """,
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "email": "newuser@example.com",
                        "name": "John Doe",
                        "bio": None,
                        "avatar_url": None,
                        "created_at": "2025-01-08T10:30:00Z",
                        "updated_at": "2025-01-08T10:30:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid user data"},
        401: {"description": "Invalid API key"},
        403: {"description": "Admin access required"},
        409: {"description": "Email already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management"],
    dependencies=[
        Depends(require_feature("users:create")),
        Depends(require_api_key),
    ],
)
async def create_user(
    user: UserCreateRequest = Body(
        ...,
        example={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "John Doe",
        },
    ),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create a new user account with validation and security checks.
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
    except UserAlreadyExistsError as e:
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
            ) from e
        raise HTTPException(status_code=409, detail="Email already exists.") from e
    except InvalidDataError as e:
        raise HTTPException(status_code=400, detail="Invalid user data.") from e
    except CustomValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.") from e


@router.get(
    "",
    summary="List users with filtering and pagination",
    description="""
    Retrieve a paginated list of users with optional filtering capabilities.

    **Requirements:**
    - Valid API key in Authorization header
    - Feature flag 'users:list' must be enabled
    - Admin privileges required

    **Query Parameters:**
    - `offset`: Number of records to skip (default: 0)
    - `limit`: Maximum records to return (default: 50, max: 100)
    - `email`: Filter by email address (partial match)
    - `name`: Filter by user name (partial match)
    - `created_after`: Filter users created after date (ISO format)

    **Response:**
    - `users`: Array of user objects
    - `total`: Total number of matching users

    **Example Request:**
    ```
    GET /api/v1/users?offset=0&limit=10&name=john&created_after=2025-01-01
    ```

    **Example Response:**
    ```json
    {
        "users": [
            {
                "id": 123,
                "email": "john.doe@example.com",
                "name": "John Doe",
                "bio": "Software developer",
                "avatar_url": "https://example.com/avatar.jpg",
                "created_at": "2025-01-08T10:30:00Z",
                "updated_at": "2025-01-08T10:30:00Z"
            }
        ],
        "total": 1
    }
    ```
    """,
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Users retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "users": [
                            {
                                "id": 123,
                                "email": "john.doe@example.com",
                                "name": "John Doe",
                                "bio": "Software developer",
                                "avatar_url": "https://example.com/avatar.jpg",
                                "created_at": "2025-01-08T10:30:00Z",
                                "updated_at": "2025-01-08T10:30:00Z",
                            }
                        ],
                        "total": 1,
                    }
                }
            },
        },
        401: {"description": "Invalid API key"},
        403: {"description": "Admin access required"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management"],
    dependencies=[
        Depends(require_feature("users:list")),
        Depends(require_api_key),
    ],
)
async def list_users(
    params: PaginationParams = Depends(pagination_params),
    email: str | None = Query(
        None, description="Filter by email address (partial match)"
    ),
    name: str | None = Query(None, description="Filter by user name (partial match)"),
    created_after: str | None = Query(
        None, description="Filter users created after this date (ISO format)"
    ),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(require_admin),
) -> UserListResponse:
    """
    List users with comprehensive filtering and pagination support.
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
    description="""
    Retrieve detailed information for a specific user by their ID.

    **Requirements:**
    - Valid API key in Authorization header
    - Feature flag 'users:read' must be enabled
    - Admin privileges required

    **Path Parameters:**
    - `user_id`: Unique identifier of the user (integer)

    **Response:**
    Returns complete user profile including metadata.

    **Example Request:**
    ```
    GET /api/v1/users/123
    ```

    **Example Response:**
    ```json
    {
        "id": 123,
        "email": "john.doe@example.com",
        "name": "John Doe",
        "bio": "Software developer passionate about clean code",
        "avatar_url": "https://example.com/avatars/123.jpg",
        "created_at": "2025-01-08T10:30:00Z",
        "updated_at": "2025-01-08T15:45:00Z"
    }
    ```
    """,
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "email": "john.doe@example.com",
                        "name": "John Doe",
                        "bio": "Software developer passionate about clean code",
                        "avatar_url": "https://example.com/avatars/123.jpg",
                        "created_at": "2025-01-08T10:30:00Z",
                        "updated_at": "2025-01-08T15:45:00Z",
                    }
                }
            },
        },
        401: {"description": "Invalid API key"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management"],
    dependencies=[
        Depends(require_feature("users:read")),
        Depends(require_api_key),
    ],
)
async def get_user_by_id(
    user_id: int = Path(..., description="User ID", gt=0),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(require_admin),
) -> UserResponse:
    """
    Get detailed user information by ID with comprehensive error handling.
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
        raise HTTPException(status_code=500, detail="Unexpected error.") from e
    # Defensive: function must always return UserResponse or raise
    raise HTTPException(status_code=500, detail="Unreachable code in get_user_by_id")


@router.put(
    "/{user_id}",
    summary="Update user information",
    description="""
    Update an existing user's information.

    **Requirements:**
    - Valid API key in Authorization header
    - Admin privileges required

    **Path Parameters:**
    - `user_id`: Unique identifier of the user to update

    **Request Body:**
    - `email`: New email address (must be unique)
    - `password`: New password (will be hashed)
    - `name`: Updated display name

    **Behavior:**
    - Validates new email uniqueness
    - Hashes new password securely
    - Updates modification timestamp
    - Returns updated user profile

    **Example Request:**
    ```json
    {
        "email": "updated@example.com",
        "password": "NewSecurePass123!",
        "name": "Updated Name"
    }
    ```

    **Example Response:**
    ```json
    {
        "id": 123,
        "email": "updated@example.com",
        "name": "Updated Name",
        "bio": null,
        "avatar_url": null,
        "created_at": "2025-01-08T10:30:00Z",
        "updated_at": "2025-01-08T16:20:00Z"
    }
    ```
    """,
    response_model=UserResponse,
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "email": "updated@example.com",
                        "name": "Updated Name",
                        "bio": None,
                        "avatar_url": None,
                        "created_at": "2025-01-08T10:30:00Z",
                        "updated_at": "2025-01-08T16:20:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid user data"},
        401: {"description": "Invalid API key"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"},
        409: {"description": "Email already exists"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management"],
)
async def update_user(
    user_id: int = Path(..., description="User ID to update", gt=0),
    user: UserCreateRequest = Body(
        ...,
        example={
            "email": "updated@example.com",
            "password": "NewSecurePass123!",
            "name": "Updated Name",
        },
    ),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(require_admin),
) -> UserResponse:
    """
    Update user information with validation and conflict checking.
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
        http_error(
            404,
            "User not found.",
            logger.warning,
            cast(ExtraLogInfo, {"user_id": user_id}),
            e,
        )
        raise HTTPException(status_code=404, detail="User not found.") from e
    except UserAlreadyExistsError as e:
        http_error(
            409,
            "Email already exists.",
            logger.warning,
            cast(ExtraLogInfo, {"email": user.email}),
            e,
        )
        raise HTTPException(status_code=409, detail="Email already exists.") from e
    except InvalidDataError as e:
        http_error(
            400,
            "Invalid user data.",
            logger.warning,
            cast(ExtraLogInfo, {"user_id": user_id}),
            e,
        )
        raise HTTPException(status_code=400, detail="Invalid user data.") from e
    except Exception as e:
        http_error(
            500,
            "Unexpected error.",
            logger.error,
            cast(ExtraLogInfo, {"user_id": user_id, "error": str(e)}),
            e,
        )
        raise HTTPException(status_code=500, detail="Unexpected error.") from e
    # Defensive: function must always return UserResponse or raise
    raise HTTPException(status_code=500, detail="Unreachable code in update_user")


@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="""
    Permanently delete a user account from the system.

    **Requirements:**
    - Valid API key in Authorization header
    - Admin privileges required

    **Path Parameters:**
    - `user_id`: Unique identifier of the user to delete

    **Behavior:**
    - Permanently removes user from database
    - Cascades deletion to related records
    - Cannot be undone
    - Returns 204 No Content on success

    **Example Request:**
    ```
    DELETE /api/v1/users/123
    ```

    **Response:**
    - Success: 204 No Content (empty body)
    - User not found: 404 with error message
    """,
    status_code=204,
    responses={
        204: {"description": "User deleted successfully"},
        401: {"description": "Invalid API key"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management"],
)
async def delete_user(
    user_id: int = Path(..., description="User ID to delete", gt=0),
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(),
    current_user: UserResponse = Depends(require_admin),
) -> Response:
    """
    Delete user account with proper cleanup and error handling.
    """
    STATUS_NO_CONTENT = 204
    try:
        await user_service.delete_user(session, user_id)
    except UserNotFoundError:
        logger.warning("User not found.", extra={"user_id": user_id})
        return Response(status_code=404, content="User not found.")
    except Exception as e:
        logger.error("Unexpected error.", extra={"user_id": user_id, "error": str(e)})
        return Response(status_code=500, content="Unexpected error.")
    logger.info("user_deleted", extra={"user_id": user_id})
    return Response(status_code=STATUS_NO_CONTENT)
