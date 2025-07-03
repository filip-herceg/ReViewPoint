from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.models.base import Base


class UsedPasswordResetToken(Base):
    __tablename__ = "used_password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    nonce: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    used_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    @validates("email", "nonce")
    def validate_not_empty(self, key: str, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        return value

    def __repr__(self) -> str:
        return f"<UsedPasswordResetToken email={self.email} nonce={self.nonce} used_at={self.used_at}>"
