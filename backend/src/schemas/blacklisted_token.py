from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BlacklistedTokenSchema(BaseModel):
    """Schema for a blacklisted JWT token."""

    jti: str
    expires_at: datetime
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
