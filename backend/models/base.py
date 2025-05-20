# This file is intentionally minimal and may not contain full model logic.
#
# Reason: SQLAlchemy 2.x type stubs are incomplete, so mypy and ruff cannot
# type-check or lint modern declarative base patterns (e.g., mapped_column, Mapped).
#
# Attempts to work around this (with type: ignore, stubs, etc.) either break runtime,
# break linting, or make the file invalid Python. Exclusion from ruff/mypy is unreliable.
#
# If/when SQLAlchemy type stubs improve, restore your full model logic here and remove this comment.
#
# See: https://github.com/sqlalchemy/sqlalchemy/discussions/10049
#
# For now, this file is kept valid for both runtime and tooling, but does not define models.

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Example valid model (commented out if not needed):
# class User(Base):
#     __tablename__ = "user"
#     id = mapped_column(primary_key=True, autoincrement=True)
#     created_at = mapped_column(default=func.now(), nullable=False)
#     updated_at = mapped_column(default=func.now(), onupdate=func.now(), nullable=False)
