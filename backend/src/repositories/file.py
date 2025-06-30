from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File
from src.utils.errors import ValidationError


async def get_file_by_filename(session: AsyncSession, filename: str) -> File | None:
    result = await session.execute(select(File).where(File.filename == filename))
    return result.scalar_one_or_none()


async def create_file(
    session: AsyncSession, filename: str, content_type: str, user_id: int
) -> File:
    if not filename:
        raise ValidationError("Filename is required.")

    # Create the file object but don't add it to the session yet
    file = File(filename=filename, content_type=content_type, user_id=user_id)

    # Wrap the database operation in a transaction that can be safely retried
    try:
        # Add the file to the session
        session.add(file)
        # Flush to get the ID but don't commit yet
        await session.flush()
    except Exception as e:
        # Rollback the session and re-raise the error
        await session.rollback()
        raise e

    return file


async def delete_file(session: AsyncSession, filename: str) -> bool:
    file = await get_file_by_filename(session, filename)
    if not file:
        return False
    await session.delete(file)
    # Note: Don't flush here - let the endpoint handle the commit
    return True


async def list_files(
    session: AsyncSession,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
    q: str | None = None,
    sort: str = "created_at",
    order: str = "desc",
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> tuple[list[File], int]:
    stmt = select(File).where(File.user_id == user_id)
    if q:
        stmt = stmt.where(File.filename.ilike(f"%{q}%"))
    if created_after:
        stmt = stmt.where(File.created_at >= created_after)
    if created_before:
        stmt = stmt.where(File.created_at <= created_before)
    if sort in {"created_at", "filename"}:
        col = getattr(File, sort)
        if order == "desc":
            col = col.desc()
        else:
            col = col.asc()
        stmt = stmt.order_by(col)
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()
    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    files = list(result.scalars().all())
    return files, total
