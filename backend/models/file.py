# type: ignore
from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import (  # type: ignore[attr-defined]
    Mapped,
    mapped_column,
    relationship,
)

from backend.models.base import BaseModel


class File(BaseModel):
    __tablename__ = "files"
    __table_args__ = (Index("ix_files_user_id", "user_id"),)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", backref="files")
    # created_at, updated_at inherited from BaseModel

    def __repr__(self) -> str:
        return f"<File id={self.id} filename={self.filename}>"
