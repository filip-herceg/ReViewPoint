import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.models.base import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    # Ensure no subclassing of both Column and datetime
