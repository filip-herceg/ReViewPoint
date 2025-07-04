"""
Test-only endpoints for user management (e.g., promote to admin).
"""

from typing import Final, TypedDict

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.routing import APIRouter as APIRouterType
from sqlalchemy import select
from sqlalchemy.engine import Result as SQLAlchemyResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.models.user import User
from src.utils.environment import is_test_mode

# Router instance is a constant and should not be mutated
router: Final[APIRouterType] = APIRouter()


class PromoteAdminResponse(TypedDict):
    detail: str


@router.post(
    "/promote-admin",
    tags=["Test Utilities"],
)
async def promote_user_to_admin_async(
    email: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_async_session),
) -> PromoteAdminResponse:
    """
    Promote a user to admin by email. Only allowed in test mode.

    Args:
        email (str): The email of the user to promote.
        session (AsyncSession): The SQLAlchemy async session.

    Returns:
        PromoteAdminResponse: A dict with a detail message.

    Raises:
        HTTPException: If not in test mode (403) or user not found (404).
    """
    if not is_test_mode():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed in production."
        )
    user: SQLAlchemyResult = await session.execute(
        select(User).where(User.email == email)
    )
    user_obj: User | None = user.scalars().first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    user_obj.is_admin = True
    await session.commit()
    response: PromoteAdminResponse = {"detail": f"User {email} promoted to admin."}
    return response
