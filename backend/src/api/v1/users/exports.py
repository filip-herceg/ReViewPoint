"""
User export endpoints: CSV, health, and simple export endpoints.
"""

import csv
from io import StringIO

from fastapi import APIRouter, Response

from src.utils.datetime import parse_flexible_datetime

router = APIRouter()


@router.get(
    "/export",
    summary="Export users as CSV (debug minimal)",
    response_class=Response,
)
async def export_users_csv() -> Response:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "name"])
    writer.writerow([1, "dummy@example.com", "Dummy User"])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.get("/export-alive", summary="Test endpoint for export router")
async def export_alive() -> dict[str, str]:
    return {"status": "users export alive"}


@router.get(
    "/export-full",
    summary="Export users as CSV (full)",
    response_class=Response,
)
async def export_users_full_csv() -> Response:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "name", "created_at", "updated_at"])
    created_time = parse_flexible_datetime("2023-01-01T00:00:00")
    writer.writerow([1, "dummy@example.com", "Dummy User", created_time, created_time])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.get("/export-simple", summary="Simple test endpoint for debugging")
async def export_simple() -> dict[str, str]:
    return {"status": "users export simple"}
