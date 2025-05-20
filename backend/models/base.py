from __future__ import annotations

import datetime as dt
from typing import Any
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[dt.datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize model to dict."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
