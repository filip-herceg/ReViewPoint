from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict

class UserProfile(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None

    model_config = ConfigDict(extra="forbid")

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    bio: Optional[str] = Field(None, max_length=512)

    model_config = ConfigDict(extra="forbid")

class UserPreferences(BaseModel):
    theme: Optional[str] = Field(None, description="UI theme, e.g. 'dark' or 'light'")
    locale: Optional[str] = Field(None, description="User locale, e.g. 'en', 'fr'")
    # Add more preference fields as needed

    model_config = ConfigDict(extra="forbid")

class UserPreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]

class UserAvatarResponse(BaseModel):
    avatar_url: str
