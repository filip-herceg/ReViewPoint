"""
Reusable test data factories for fast, consistent test data creation.
Use these factories in tests to avoid slow DB setup and reduce duplication.
"""

from datetime import UTC, datetime
from typing import Any

from factory.base import Factory
from factory.declarations import LazyFunction, Sequence
from typing_extensions import TypedDict


class UserDict(TypedDict, total=False):
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime


class UserFactory(Factory[dict[str, Any]]):
    """Factory for building user dicts for tests (not DB objects)."""

    model = dict

    email = Sequence(lambda n: f"user{n}@example.com")  # type: ignore
    password_hash = "hashed_password"
    is_active = True
    created_at = LazyFunction(lambda: datetime.now(UTC))  # type: ignore

    @classmethod
    def build_obj(cls, **overrides: object) -> dict[str, Any]:
        """
        Return a dict representing a user, with optional overrides.
        Args:
            **overrides: Fields to override in the user dict.
        Returns:
            dict[str, object]: A user dictionary with the specified overrides applied.
        """
        data: dict[str, Any] = cls.build()
        data.update(overrides)
        return data


# Add more factories as needed for other models
