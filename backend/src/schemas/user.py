from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    id: int
    email: str
    name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    created_at: str | None = None  # Use str for ISO datetime, or datetime if available
    updated_at: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserProfileUpdate(BaseModel):
    name: str | None = Field(None, max_length=128)
    bio: str | None = Field(None, max_length=512)

    model_config = ConfigDict(extra="forbid")


class UserPreferences(BaseModel):
    theme: Literal["dark", "light"] | None = Field(
        None, description="UI theme, e.g. 'dark' or 'light'"
    )
    locale: str | None = Field(None, description="User locale, e.g. 'en', 'fr'")
    # Add more preference fields as needed

    model_config = ConfigDict(extra="forbid")


class UserPreferencesUpdate(BaseModel):
    preferences: Mapping[str, object]  # Use object for arbitrary values, not Any


class UserAvatarResponse(BaseModel):
    avatar_url: str


class UserRead(UserProfile):
    pass


# --- User Creation Request Schema ---
class UserCreateRequest(BaseModel):
    email: str
    password: str
    name: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "strongpassword123",
                    "name": "Jane Doe",
                }
            ]
        }
    )


# --- User List Response Schema ---
class UserListResponse(BaseModel):
    users: Sequence[UserProfile]
    total: int


# NOTE: UserResponse is typically UserProfile or UserRead, already defined above.
# If needed, update the reference accordingly.

# --- Fix for Pydantic forward references ---
UserResponse = UserProfile  # or UserRead if needed
UserListResponse.model_rebuild()
