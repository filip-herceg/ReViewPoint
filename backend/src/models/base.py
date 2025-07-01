# mypy: disable-error-code=misc
# Note: Mypy will report errors for SQLAlchemy declarative base patterns in this file.
# These errors are expected due to SQLAlchemy's dynamic base class creation and are safe to ignore at runtime.
# See:
# https://mypy.readthedocs.io/en/stable/common_issues.html#declarative-base-classes
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


# Note: Do not use 'Base' as a type annotation. For SQLAlchemy models,
# annotate with the specific model class or use 'Any' if needed.
class BaseModel(Base):
    __abstract__ = True
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


__all__ = ["Base", "BaseModel"]
