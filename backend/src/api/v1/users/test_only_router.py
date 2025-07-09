"""
Test-only endpoints for user management (e.g., promote to admin).
"""

from typing import Final, TypedDict

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.routing import APIRouter as APIRouterType
from sqlalchemy import select
from sqlalchemy.engine import Result
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
    summary="Promote user to admin (TEST ONLY)",
    description="""
    **🚨 TEST ENVIRONMENT ONLY - NOT AVAILABLE IN PRODUCTION 🚨**
    
    Promote a regular user to admin status by email address.
    This endpoint is restricted to test environments for testing admin functionality.
    
    **Requirements:**
    - Must be running in test mode (TEST_MODE=true)
    - User must exist in the database
    - No authentication required (test endpoint)
    
    **Request Body:**
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Behavior:**
    - Finds user by email address
    - Sets `is_admin` flag to `true`
    - Commits changes to database
    - Returns confirmation message
    
    **Example Request:**
    ```json
    {
        "email": "john.doe@example.com"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "detail": "User john.doe@example.com promoted to admin."
    }
    ```
    
    **Security Notes:**
    - Automatically disabled in production environments
    - Returns 403 Forbidden if not in test mode
    - Use only for test setup and automation
    - Never expose in production APIs
    """,
    responses={
        200: {
            "description": "User promoted to admin successfully",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User john.doe@example.com promoted to admin."
                    }
                }
            }
        },
        403: {"description": "Not allowed in production environment"},
        404: {"description": "User not found"},
        422: {"description": "Invalid email format"},
        500: {"description": "Internal server error"}
    },
    tags=["Test Utilities"],
)
async def promote_user_to_admin_async(
    email: str = Body(..., embed=True, description="Email address of user to promote", example="john.doe@example.com"),
    session: AsyncSession = Depends(get_async_session),
) -> PromoteAdminResponse:
    """
    Promote a user to admin status - TEST ENVIRONMENT ONLY.
    
    This endpoint is designed for test automation and setup.
    It's automatically disabled in production environments.
    """
    if not is_test_mode():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed in production."
        )
    user: Result[tuple[User]] = await session.execute(
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
