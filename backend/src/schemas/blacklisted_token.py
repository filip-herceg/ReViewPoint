from datetime import datetime
from typing import Final

from pydantic import BaseModel, ConfigDict


class BlacklistedTokenSchema(BaseModel):
    """
    Schema for a blacklisted JWT token.

    Attributes:
        jti (str): The JWT ID (unique identifier for the token).
        expires_at (datetime): The expiration datetime of the token.
        created_at (Optional[datetime]): The creation datetime of the token, if available.
    """

    jti: str
    expires_at: datetime
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
