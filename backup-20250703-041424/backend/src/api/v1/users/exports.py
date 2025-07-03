"""
User export endpoints: CSV, health, and simple export endpoints.
"""

import csv
from io import StringIO
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user_with_export_api_key, require_feature
from src.core.database import get_async_session
from src.models.user import User
from src.repositories.user import get_active_users, list_users
from src.utils.datetime import parse_flexible_datetime

router = APIRouter()


@router.get(
    "/export",
    summary="Export users as CSV (debug minimal)",
    response_class=Response,
    dependencies=[
        Depends(require_feature("users:export")),
    ],
)
async def export_users_csv(
    session: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(get_current_user_with_export_api_key),
    email: Optional[str] = Query(None, description="Filter by email"),
    format: Optional[str] = Query("csv", description="Export format (only csv supported)"),
) -> Response:
    # Validate format parameter
    if format and format.lower() != "csv":
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unsupported format. Only 'csv' is supported.")
    
    # Query users from database
    users_data, total_count = await list_users(session)
    
    # Filter by email if provided
    if email:
        users_data = [user for user in users_data if user.email == email]
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "name"])
    
    for user in users_data:
        writer.writerow([user.id, user.email, user.name])
    
    csv_content = output.getvalue()
    
    # Add content-disposition header for file download
    headers = {
        "Content-Disposition": "attachment; filename=users_export.csv"
    }
    
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get(
    "/export-alive", 
    summary="Test endpoint for export router",
    dependencies=[
        Depends(require_feature("users:export_alive")),
    ],
)
async def export_alive() -> dict[str, str]:
    return {"status": "users export alive"}


@router.get(
    "/export-full",
    summary="Export users as CSV (full)",
    response_class=Response,
    dependencies=[
        Depends(require_feature("users:export_full")),
    ],
)
async def export_users_full_csv(
    session: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(get_current_user_with_export_api_key),
) -> Response:
    # Query users from database
    users_data, total_count = await list_users(session)
    
    # Generate CSV with full user data
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "name", "created_at", "updated_at", "is_active", "is_admin"])
    
    for user in users_data:
        writer.writerow([
            user.id,
            user.email,
            user.name,
            user.created_at.isoformat() if user.created_at else "",
            user.updated_at.isoformat() if user.updated_at else "",
            user.is_active,
            user.is_admin
        ])
    
    csv_content = output.getvalue()
    
    # Add content-disposition header for file download
    headers = {
        "Content-Disposition": "attachment; filename=users_full_export.csv"
    }
    
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get(
    "/export-simple", 
    summary="Simple test endpoint for debugging",
    dependencies=[
        Depends(require_feature("users:export_simple")),
    ],
)
async def export_simple() -> dict[str, str]:
    return {"users": "export simple status"}
