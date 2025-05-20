# type: ignore
# Ruff: Remove unused import of relationship
# Black: Reformat file

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore[attr-defined]

from backend.models.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # created_at, updated_at inherited from Base

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
