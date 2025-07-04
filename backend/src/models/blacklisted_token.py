from datetime import datetime
from typing import Final

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class BlacklistedToken(BaseModel):
    __tablename__: Final[str] = "blacklisted_tokens"
    jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
