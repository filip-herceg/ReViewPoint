from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    id: int
    email: str
    name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    created_at: Any | None = None
    updated_at: Any | None = None

    model_config = ConfigDict(extra="forbid")


class UserProfileUpdate(BaseModel):
    name: str | None = Field(None, max_length=128)
    bio: str | None = Field(None, max_length=512)

    model_config = ConfigDict(extra="forbid")


class UserPreferences(BaseModel):
    theme: str | None = Field(None, description="UI theme, e.g. 'dark' or 'light'")
    locale: str | None = Field(None, description="User locale, e.g. 'en', 'fr'")
    # Add more preference fields as needed

    model_config = ConfigDict(extra="forbid")


class UserPreferencesUpdate(BaseModel):
    preferences: dict[str, Any]


class UserAvatarResponse(BaseModel):
    avatar_url: str
