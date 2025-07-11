from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.models.base import BaseModel


class File(BaseModel):
    """SQLAlchemy model for a file uploaded by a user.
    """

    __tablename__ = "files"
    __table_args__ = (Index("ix_files_user_id", "user_id"),)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size: Mapped[int] = mapped_column(
        BigInteger, nullable=True, default=0,
    )  # File size in bytes
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from src.models.user import User
    user: Mapped[User] = relationship("User", back_populates="files")
    # created_at, updated_at inherited from BaseModel

    def __repr__(self: File) -> str:
        """Return a string representation of the File instance.

        :raises AttributeError: If 'id' or 'filename' attributes are not set (e.g., before flush).
        :return: String representation of the File instance.
        """
        return f"<File id={self.id} filename={self.filename}>"
