from pydantic import BaseModel
from datetime import datetime

class BlacklistedTokenSchema(BaseModel):
    jti: str
    expires_at: datetime
    created_at: datetime | None = None

    class Config:
        from_attributes = True
