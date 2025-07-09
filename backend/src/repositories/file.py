from datetime import datetime
from typing import Any, Literal

import sqlalchemy
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File
from src.utils.errors import ValidationError


async def get_file_by_filename(session: AsyncSession, filename: str) -> File | None:
    from typing import Any

    result: sqlalchemy.engine.Result[Any] = await session.execute(
        select(File).where(File.filename == filename)
    )
    return result.scalar_one_or_none()


async def create_file(
    session: AsyncSession, filename: str, content_type: str, user_id: int, size: int = 0
) -> File:
    """
    Create a new File record in the database.
    Raises:
        ValidationError: If filename is empty.
        Exception: If the database operation fails.
    """
    if not filename:
        raise ValidationError("Filename is required.")

    file: File = File(
        filename=filename, content_type=content_type, user_id=user_id, size=size
    )

    try:
        session.add(file)
        await session.flush()
    except Exception as exc:
        await session.rollback()
        raise exc

    return file


async def delete_file(session: AsyncSession, filename: str) -> bool:
    """
    Delete a file by filename.
    Returns:
        bool: True if file was deleted, False if not found.
    Raises:
        Exception: If the database operation fails.
    """
    file: File | None = await get_file_by_filename(session, filename)
    if not file:
        return False
    await session.delete(file)
    # Note: Don't flush here - let the endpoint handle the commit
    return True


async def bulk_delete_files(
    session: AsyncSession, filenames: list[str], user_id: int
) -> tuple[list[str], list[str]]:
    """
    Bulk delete files by filenames for a specific user.
    Returns:
        tuple[list[str], list[str]]: (successfully_deleted, failed_to_delete)
    Raises:
        Exception: If the database operation fails.
    """
    deleted: list[str] = []
    failed: list[str] = []

    for filename in filenames:
        try:
            # Check if file exists and belongs to the user
            result = await session.execute(
                select(File).where(File.filename == filename, File.user_id == user_id)
            )
            file: File | None = result.scalar_one_or_none()

            if file:
                await session.delete(file)
                deleted.append(filename)
            else:
                failed.append(filename)
        except Exception:
            failed.append(filename)

    return deleted, failed


async def list_files(
    session: AsyncSession,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
    q: str | None = None,
    sort: Literal["created_at", "filename"] = "created_at",
    order: Literal["desc", "asc"] = "desc",
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> tuple[list[File], int]:
    """
    List files for a user with optional filters and pagination.
    Returns:
        tuple[list[File], int]: (files, total count)
    Raises:
        Exception: If the database operation fails.
    """
    stmt: sqlalchemy.sql.Select[Any] = select(File).where(File.user_id == user_id)
    if q is not None:
        stmt = stmt.where(File.filename.ilike(f"%{q}%"))
    if created_after is not None:
        stmt = stmt.where(File.created_at >= created_after)
    if created_before is not None:
        stmt = stmt.where(File.created_at <= created_before)
    if sort in ("created_at", "filename"):
        col: sqlalchemy.sql.ColumnElement[Any] = getattr(File, sort)
        if order == "desc":
            col = col.desc()
        else:
            col = col.asc()
        stmt = stmt.order_by(col)
    count_stmt: sqlalchemy.sql.Select[Any] = select(func.count()).select_from(
        stmt.subquery()
    )
    total: int = (await session.execute(count_stmt)).scalar_one()
    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    files: list[File] = list(result.scalars().all())
    return files, total
