"""
User export endpoints: CSV, health, and simple export endpoints.
"""

import csv
from collections.abc import Mapping, Sequence
from io import StringIO
from typing import Final, Literal, TypedDict

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user_with_export_api_key, require_feature
from src.core.database import get_async_session
from src.models.user import User
from src.repositories.user import list_users

router: Final[APIRouter] = APIRouter()


class UserMinimalRow(TypedDict):
    id: int
    email: str
    name: str


CSV_EXPORT_FILENAME: Final[Literal["users_export.csv"]] = "users_export.csv"


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
    email: str | None = Query(None, description="Filter by email"),
    format: str | None = Query("csv", description="Export format (only csv supported)"),
) -> Response:
    """
    Export users as CSV (minimal).
    Raises:
        HTTPException: If format is not 'csv'.
    """
    # Validate format parameter
    if format is not None and format.lower() != "csv":
        raise HTTPException(
            status_code=400, detail="Unsupported format. Only 'csv' is supported."
        )

    # Query users from database
    users_data: Sequence[User]
    total_count: int
    users_data, total_count = await list_users(session)

    # Filter by email if provided
    if email is not None:
        users_data = [user for user in users_data if user.email == email]

    # Generate CSV

    output: StringIO = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(["id", "email", "name"])

    for user in users_data:
        csv_writer.writerow([user.id, user.email, user.name])

    csv_content: str = output.getvalue()

    # Add content-disposition header for file download
    headers: Mapping[str, str] = {
        "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}"
    }

    return Response(content=csv_content, media_type="text/csv", headers=dict(headers))


EXPORT_ALIVE_STATUS: Final[Literal["users export alive"]] = "users export alive"


class ExportAliveResponse(TypedDict):
    status: Literal["users export alive"]


@router.get(
    "/export-alive",
    summary="Test endpoint for export router",
    dependencies=[
        Depends(require_feature("users:export_alive")),
    ],
)
async def export_alive() -> ExportAliveResponse:
    """
    Test endpoint for export router.
    Returns:
        ExportAliveResponse: Status dict.
    """
    return {"status": EXPORT_ALIVE_STATUS}


class UserFullRow(TypedDict):
    id: int
    email: str
    name: str
    created_at: str
    updated_at: str
    is_active: bool
    is_admin: bool


CSV_FULL_EXPORT_FILENAME: Final[Literal["users_full_export.csv"]] = (
    "users_full_export.csv"
)


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
    """
    Export users as CSV (full).
    Returns:
        Response: CSV file response.
    """
    # Query users from database
    users_data: Sequence[User]
    total_count: int
    users_data, total_count = await list_users(session)

    # Generate CSV with full user data

    output: StringIO = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(
        ["id", "email", "name", "created_at", "updated_at", "is_active", "is_admin"]
    )

    for user in users_data:
        csv_writer.writerow(
            [
                user.id,
                user.email,
                user.name,
                user.created_at.isoformat() if user.created_at else "",
                user.updated_at.isoformat() if user.updated_at else "",
                user.is_active,
                user.is_admin,
            ]
        )

    csv_content: str = output.getvalue()

    # Add content-disposition header for file download
    headers: Mapping[str, str] = {
        "Content-Disposition": f"attachment; filename={CSV_FULL_EXPORT_FILENAME}"
    }

    return Response(content=csv_content, media_type="text/csv", headers=dict(headers))


EXPORT_SIMPLE_STATUS: Final[Literal["export simple status"]] = "export simple status"


class ExportSimpleResponse(TypedDict):
    users: Literal["export simple status"]


@router.get(
    "/export-simple",
    summary="Simple test endpoint for debugging",
    dependencies=[
        Depends(require_feature("users:export_simple")),
    ],
)
async def export_simple() -> ExportSimpleResponse:
    """
    Simple test endpoint for debugging.
    Returns:
        ExportSimpleResponse: Status dict.
    """
    return {"users": EXPORT_SIMPLE_STATUS}
