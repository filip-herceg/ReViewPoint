# Ruff: Remove unused import of relationship
# Black: Reformat file

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from .file import File

    files: list[File]


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Profile fields
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(512), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferences: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # created_at, updated_at inherited from BaseModel

    files = relationship("File", back_populates="user")

    # Add a dynamic property for role (not persisted)
    @property
    def role(self) -> str:
        return "admin" if self.is_admin else "user"

    @role.setter
    def role(self, value: str):
        # Allow setting role dynamically for test/deps purposes only
        self.is_admin = value == "admin"

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
