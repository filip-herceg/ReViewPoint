from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Index
from backend.models.base import Base


class File(Base):
    __tablename__ = "files"
    __table_args__ = (Index("ix_files_user_id", "user_id"),)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", backref="files")
    # created_at, updated_at inherited from Base

    def __repr__(self) -> str:
        return f"<File id={self.id} filename={self.filename}>"
