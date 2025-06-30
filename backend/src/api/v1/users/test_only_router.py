"""
Test-only endpoints for user management (e.g., promote to admin).
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.models.user import User
from src.utils.environment import is_test_mode

router = APIRouter()


@router.post("/promote-admin", tags=["Test Utilities"])
async def promote_user_to_admin_async(
    email: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_async_session),
):
    if not is_test_mode():
        raise HTTPException(status_code=403, detail="Not allowed in production.")
    user = await session.execute(select(User).where(User.email == email))
    user_obj = user.scalars().first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found.")
    user_obj.is_admin = True
    await session.commit()
    return {"detail": f"User {email} promoted to admin."}
