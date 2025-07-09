from collections.abc import Mapping
from datetime import datetime
from typing import Any, Final, cast

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # No additional attributes; serves as the declarative base.
    pass


# Note: Do not use 'Base' as a type annotation. For SQLAlchemy models,
# annotate with the specific model class or use 'Any' if needed.


class BaseModel(Base):
    __abstract__: Final[bool] = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> Mapping[str, Any]:
        """
        Convert model instance to dictionary, including all mapped columns.

        Returns
        -------
        Mapping[str, Any]
            Dictionary of column names to values.

        Raises
        ------
        AttributeError
            If a column attribute is missing on the instance.
        """
        result: dict[str, Any] = {}
        for column in cast(Any, self.__table__).columns:
            value: Any = getattr(self, column.name, None)
            result[column.name] = value
        return result


__all__: tuple[str, ...] = ("Base", "BaseModel")
