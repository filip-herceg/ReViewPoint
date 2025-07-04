from collections.abc import Callable as ABCCallable
from datetime import UTC, datetime
from typing import ClassVar, Literal

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.models.base import BaseModel


class UsedPasswordResetToken(BaseModel):
    """
    Model for used password reset tokens.
    """

    __tablename__: ClassVar[Literal["used_password_reset_tokens"]] = (
        "used_password_reset_tokens"
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    nonce: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # The default lambda is a callable with signature () -> datetime
    used_at_default: ClassVar[ABCCallable[[], datetime]] = lambda: datetime.now(UTC)
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=used_at_default, nullable=False
    )

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
