"""
Reusable test data factories for fast, consistent test data creation.
Use these factories in tests to avoid slow DB setup and reduce duplication.
"""



from datetime import UTC, datetime
from typing import TypedDict
from factory.base import Factory
from factory.declarations import Sequence, LazyFunction



class UserDict(TypedDict, total=False):
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime


class UserFactory(Factory):
    """Factory for building user dicts for tests (not DB objects)."""
    model = dict

    email = Sequence(lambda n: f"user{n}@example.com")
    password_hash = "hashed_password"
    is_active = True
    created_at = LazyFunction(lambda: datetime.now(UTC))

    @classmethod
    def build_obj(cls, **overrides: object) -> dict[str, object]:
        """
        Return a dict representing a user, with optional overrides.
        Args:
            **overrides: Fields to override in the user dict.
        Returns:
            dict[str, object]: A user dictionary with the specified overrides applied.
        """
        data: dict[str, object] = cls.build()
        data.update(overrides)
        return data


# Add more factories as needed for other models
