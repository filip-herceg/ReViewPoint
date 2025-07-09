"""Token-related schemas for authentication and authorization."""

from datetime import datetime

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Response schema for authentication endpoints that return tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int | None = Field(None, description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Request schema for refresh token endpoint."""

    refresh_token: str = Field(
        ..., description="Refresh token to exchange for new access token"
    )


class TokenData(BaseModel):
    """Token payload data schema."""

    user_id: str = Field(..., description="User ID from token")
    email: str | None = Field(None, description="User email from token")
    exp: datetime | None = Field(None, description="Token expiration timestamp")
    jti: str | None = Field(None, description="JWT ID for token tracking")
