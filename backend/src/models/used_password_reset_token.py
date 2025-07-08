from collections.abc import Callable as ABCCallable
from datetime import UTC, datetime
from typing import ClassVar, Literal

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.models.base import BaseModel


class UsedPasswordResetToken(BaseModel):
    @validates("used_at")
    def _validate_used_at(self, key: str, value: datetime | None) -> datetime:
        # Always ensure used_at is timezone-aware (UTC)
        if value is None:
            raise ValueError("used_at cannot be None")
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    # ...existing code...

    # Model for used password reset tokens.

    __tablename__ = "used_password_reset_tokens"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    nonce: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # The default lambda is a callable with signature () -> datetime
    used_at_default: ClassVar[ABCCallable[[], datetime]] = lambda: datetime.now(UTC)
    used_at: Mapped[datetime] = mapped_column(
        "used_at", DateTime(timezone=True), default=used_at_default, nullable=False
    )

    @property
    def used_at_aware(self) -> datetime:
        """
        Always return used_at as a timezone-aware datetime (UTC).
        """
        value = self.used_at
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    def __init__(self, *args: object, **kwargs: object) -> None:
        used_at = kwargs.get("used_at")
        if isinstance(used_at, datetime):
            if used_at.tzinfo is None:
                # Convert naive datetime to UTC
                kwargs["used_at"] = used_at.replace(tzinfo=UTC)
        super().__init__(*args, **kwargs)

    @validates("email", "nonce")
    def validate_not_empty(self, key: str, value: str) -> str:
        """
        Validate that the given value is a non-empty string.

        Args:
            key (str): The name of the field being validated.
            value (str): The value to validate.

        Returns:
            str: The validated value.

        Raises:
            ValueError: If the value is not a non-empty string.
        """
        if not isinstance(key, str):
            raise ValueError("key must be a string")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        return value

    def __repr__(self: "UsedPasswordResetToken") -> str:
        """
        Return a string representation of the UsedPasswordResetToken instance.

        Returns:
            str: String representation of the instance.
        """
        return f"<UsedPasswordResetToken email={self.email} nonce={self.nonce} used_at={self.used_at}>"
