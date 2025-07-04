"""
Reusable test data factories for fast, consistent test data creation.
Use these factories in tests to avoid slow DB setup and reduce duplication.
"""

from datetime import UTC, datetime

import factory


# Example: UserFactory for dicts (not DB objects)
class UserFactory(factory.Factory):
    class Meta:
        model = dict

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password_hash = "hashed_password"
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))

    @classmethod
    def build_obj(cls, **overrides):
        """Return a dict representing a user, with optional overrides."""
        data = cls.build()
        data.update(overrides)
        return data


# Add more factories as needed for other models
