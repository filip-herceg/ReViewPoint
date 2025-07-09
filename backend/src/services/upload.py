"""Upload service for handling file uploads and management."""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.models.file import File
from src.repositories.file import create_file, delete_file, get_file_by_filename
from src.utils.file import is_safe_filename, sanitize_filename


class UploadService:
    """Service for handling file uploads and management."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self, session: AsyncSession, file: UploadFile, user_id: uuid.UUID
    ) -> File:
        """Upload a file and save it to storage."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)
        if not is_safe_filename(safe_filename):
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Check file size
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File too large")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(safe_filename).suffix
        stored_filename = f"{file_id}{file_extension}"

        # Save file to disk
        file_path = self.upload_dir / stored_filename
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save file: {str(e)}"
            ) from e

        # Save file metadata to database
        file_record = await create_file(
            session=session,
            filename=stored_filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=int(user_id),
        )

        return file_record

    async def get_file(self, session: AsyncSession, filename: str) -> File | None:
        """Get file metadata by filename."""
        return await get_file_by_filename(session, filename)

    async def delete_file(
        self, session: AsyncSession, filename: str, user_id: uuid.UUID
    ) -> bool:
        """Delete a file from storage and database."""
        file_record = await get_file_by_filename(session, filename)
        if not file_record:
            return False

        # Check ownership
        if file_record.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this file"
            )

        # Delete from disk
        file_path = self.upload_dir / filename
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # Continue even if file deletion fails

        # Delete from database
        return await delete_file(session, filename)

    def get_file_path(self, filename: str) -> Path:
        """Get the full path to a file."""
        return self.upload_dir / filename
