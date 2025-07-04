# Ruff: Remove unused import of relationship
# Black: Reformat file

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from .file import File

    files: Sequence[File]


class User(BaseModel):
    """
    User model.
    """

    __tablename__: ClassVar[Literal["users"]] = "users"

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
    preferences: Mapped[Mapping[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )  # Any is required for arbitrary JSON
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # created_at, updated_at inherited from BaseModel

    # The type: ignore is not allowed, so we use the most accurate type possible for SQLAlchemy relationships.
    files: Any = relationship(
        "File", back_populates="user"
    )  # SQLAlchemy returns a dynamic collection; Any is required here.

    @property
    def role(self: User) -> Literal["admin", "user"]:
        """
        Returns the role of the user.

        Returns:
            Literal["admin", "user"]: The user's role.
        """
        return "admin" if self.is_admin else "user"

    @role.setter
    def role(self: User, value: str) -> None:
        """
        Allows setting the role dynamically for test/deps purposes only.

        Args:
            value (str): The role to set ("admin" or "user").
        """
        self.is_admin = value == "admin"

    def __repr__(self: User) -> str:
        """
        Return a string representation of the User instance.

        Returns:
            str: String representation of the instance.
        """
        return f"<User id={self.id} email={self.email}>"
