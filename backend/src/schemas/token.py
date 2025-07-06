"""Token-related schemas for authentication and authorization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Response schema for authentication endpoints that return tokens."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Request schema for refresh token endpoint."""
    
    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")


class TokenData(BaseModel):
    """Token payload data schema."""
    
    user_id: str = Field(..., description="User ID from token")
    email: Optional[str] = Field(None, description="User email from token")
    exp: Optional[datetime] = Field(None, description="Token expiration timestamp")
    jti: Optional[str] = Field(None, description="JWT ID for token tracking")
