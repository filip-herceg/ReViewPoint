"""
User API endpoints using advanced dependency management patterns.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.api.deps import (
    get_user_service,
    get_current_active_user,
    pagination_params,
    require_feature,
    get_request_id,
    require_api_key,
)
from src.models.user import User
from src.schemas.user import UserOut

router = APIRouter()

@router.get("/users", response_model=List[UserOut], summary="List users", tags=["users"])
async def list_users(
    user_service=Depends(get_user_service),
    params=Depends(pagination_params),
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("users:list")),
    api_key_ok: None = Depends(require_api_key),
):
    """
    List users with pagination, feature flag, request ID, and API key enforcement.
    """
    users = await user_service.list(offset=params.offset, limit=params.limit)
    return users

@router.get("/users/me", response_model=UserOut, summary="Get current user", tags=["users"])
async def get_me(
    current_user: User = Depends(get_current_active_user),
    request_id: str = Depends(get_request_id),
):
    """
    Get the current authenticated user with request ID tracing.
    """
    return current_user

@router.get("/users/{user_id}", response_model=UserOut, summary="Get user by ID", tags=["users"])
async def get_user_by_id(
    user_id: int,
    user_service=Depends(get_user_service),
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("users:read")),
    api_key_ok: None = Depends(require_api_key),
):
    """
    Get a user by ID with feature flag and API key enforcement.
    """
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
