from datetime import UTC, datetime, timedelta
from typing import Final

from src.schemas.user import (
    UserAvatarResponse,
    UserPreferences,
    UserPreferencesUpdate,
    UserProfile,
    UserProfileUpdate,
)
from tests.test_templates import ModelUnitTestTemplate


class TestUserProfileSchema(ModelUnitTestTemplate):
    """Strictly typed tests for the UserProfile schema."""

    def test_basic(self) -> None:
        """
        Test UserProfile with all fields set and correct values.
        """
        now: Final[datetime] = datetime.now(UTC)
        now_str: Final[str] = now.isoformat()
        profile: Final[UserProfile] = UserProfile(
            id=1,
            email="test@example.com",
            name="Test User",
            bio="Hello!",
            avatar_url="/uploads/avatars/1_avatar.png",
            created_at=now_str,
            updated_at=now_str,
        )
        expected: Final[dict[str, object]] = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "bio": "Hello!",
            "avatar_url": "/uploads/avatars/1_avatar.png",
            "created_at": now_str,
            "updated_at": now_str,
        }
        self.assert_model_attrs(profile, expected)

    def test_edge_cases(self) -> None:
        """
        Test UserProfile with missing and extra fields, expecting ValidationError.
        Raises:
            pydantic.ValidationError: If required fields are missing or extra fields are provided.
        """
        import pydantic

        self.assert_raises(pydantic.ValidationError, UserProfile, id=None, email=None)
        self.assert_raises(pydantic.ValidationError, UserProfile, id=1, email=None)
        self.assert_raises(
            pydantic.ValidationError,
            UserProfile,
            id=1,
            email="a@b.com",
            extra_field="ignored",
        )

    def test_boundary_values(self) -> None:
        """
        Test UserProfile and UserProfileUpdate with max length fields and overflows.
        Raises:
            ValueError: If fields exceed allowed length.
        """
        name: str = "n" * 128
        bio: str = "b" * 512
        profile: UserProfile = UserProfile(id=10, email="b@b.com", name=name, bio=bio)
        self.assert_equal(profile.name, name)
        self.assert_equal(profile.bio, bio)
        self.assert_raises(ValueError, UserProfileUpdate, name="n" * 129, bio=None)
        self.assert_raises(ValueError, UserProfileUpdate, name=None, bio="b" * 513)

    def test_unicode_and_special_characters(self) -> None:
        """
        Test UserProfile with unicode and special characters in all fields.
        """
        profile: UserProfile = UserProfile(
            id=11,
            email="üñîçødë@example.com",
            name="测试用户 🚀",
            bio="Résumé: naïve façade. 💡",
            avatar_url="/uploads/avatars/11_😀.png",
        )
        self.assert_in("üñîçødë", profile.email)
        self.assert_is_true(profile.name is not None and "测试用户" in profile.name)
        self.assert_is_true(profile.bio is not None and "💡" in profile.bio)
        self.assert_is_true(
            profile.avatar_url is not None and profile.avatar_url.endswith("😀.png")
        )

    def test_serialization(self) -> None:
        """
        Test model_dump and model_dump_json for UserProfile.
        """
        now: datetime = datetime.now(UTC)
        now_str: str = now.isoformat()
        profile: UserProfile = UserProfile(
            id=12,
            email="serial@example.com",
            name="Serial",
            bio="Test",
            avatar_url="/uploads/avatars/12.png",
            created_at=now_str,
            updated_at=now_str,
        )
        d: dict[str, object] = profile.model_dump()
        assert isinstance(d["created_at"], str)
        j: str = profile.model_dump_json()
        self.assert_in('"name":"Serial"', j)
        self.assert_in('"created_at":', j)

    def test_default_values(self) -> None:
        """
        Test UserProfile default values for optional fields.
        """
        profile: UserProfile = UserProfile(id=13, email="default@example.com")
        self.assert_is_none(profile.name)
        self.assert_is_none(profile.bio)
        self.assert_is_none(profile.avatar_url)
        self.assert_is_none(profile.created_at)
        self.assert_is_none(profile.updated_at)

    def test_invalid_types(self) -> None:
        """
        Test UserProfile with invalid types, expecting ValidationError.
        Raises:
            pydantic.ValidationError: If invalid types are provided for fields.
        """
        import pydantic

        self.assert_raises(
            pydantic.ValidationError,
            UserProfile,
            id=14,
            email="badtype@example.com",
            name=123,
        )
        self.assert_raises(
            pydantic.ValidationError,
            UserProfile,
            id=15,
            email="badtype@example.com",
            bio=object(),
        )
        self.assert_raises(pydantic.ValidationError, UserProfile, id=16, email=123)

    def test_extreme_id(self) -> None:
        """
        Test UserProfile with extreme id values.
        """
        profile: UserProfile = UserProfile(id=2**31 - 1, email="bigid@example.com")
        self.assert_equal(profile.id, 2**31 - 1)
        profile2: UserProfile = UserProfile(id=0, email="zeroid@example.com")
        self.assert_equal(profile2.id, 0)
        profile3: UserProfile = UserProfile(id=-1, email="negid@example.com")
        self.assert_equal(profile3.id, -1)

    def test_invalid_email_formats(self) -> None:
        """
        Test UserProfile with invalid email formats (no validation).
        """
        profile: UserProfile = UserProfile(id=100, email="notanemail")
        self.assert_equal(profile.email, "notanemail")
        profile2: UserProfile = UserProfile(id=101, email="")
        self.assert_equal(profile2.email, "")

    def test_empty_strings(self) -> None:
        """
        Test UserProfile with empty strings for optional fields.
        """
        profile: UserProfile = UserProfile(
            id=102, email="empty@example.com", name="", bio="", avatar_url=""
        )
        self.assert_equal(profile.name, "")
        self.assert_equal(profile.bio, "")
        self.assert_equal(profile.avatar_url, "")

    def test_whitespace_fields(self) -> None:
        """
        Test UserProfile with whitespace-only fields.
        """
        profile: UserProfile = UserProfile(
            id=103, email="ws@example.com", name="   ", bio="\t\n", avatar_url=" "
        )
        if profile.name is not None:
            self.assert_is_true(profile.name.isspace())
        if profile.bio is not None:
            self.assert_is_true(profile.bio.isspace())
        if profile.avatar_url is not None:
            self.assert_is_true(profile.avatar_url.isspace())

    def test_future_and_past_dates(self) -> None:
        """
        Test UserProfile with created_at in the future and updated_at in the past.
        """
        now: datetime = datetime.now(UTC)
        future: datetime = now + timedelta(days=365)
        past: datetime = now - timedelta(days=365)
        future_str: str = future.isoformat()
        past_str: str = past.isoformat()
        profile: UserProfile = UserProfile(
            id=104, email="date@example.com", created_at=future_str, updated_at=past_str
        )
        import dateutil.parser

        if profile.created_at is not None:
            created_at_dt: datetime = dateutil.parser.isoparse(profile.created_at)
            self.assert_is_true(created_at_dt > now)
        if profile.updated_at is not None:
            updated_at_dt: datetime = dateutil.parser.isoparse(profile.updated_at)
            self.assert_is_true(updated_at_dt < now)

    def test_unicode_everywhere(self) -> None:
        """
        Test UserProfile with unicode in all fields.
        """
        profile: UserProfile = UserProfile(
            id=105,
            email="用户@例子.公司",
            name="名字🌟",
            bio="简介💬",
            avatar_url="/uploads/avatars/用户🌟.png",
        )
        if profile.email is not None:
            self.assert_in("用户", profile.email)
        if profile.name is not None:
            self.assert_in("🌟", profile.name)
        if profile.bio is not None:
            self.assert_in("💬", profile.bio)
        if profile.avatar_url is not None:
            self.assert_in("用户", profile.avatar_url)


class TestUserProfileUpdateSchema(ModelUnitTestTemplate):
    """Strictly typed tests for the UserProfileUpdate schema."""

    def test_valid_and_empty(self) -> None:
        """Test UserProfileUpdate with valid and empty values."""
        update: UserProfileUpdate = UserProfileUpdate(name="New Name", bio="New bio")
        self.assert_equal(update.name, "New Name")
        self.assert_equal(update.bio, "New bio")
        update2: UserProfileUpdate = UserProfileUpdate(name=None, bio=None)
        self.assert_is_true(update2.name is None and update2.bio is None)

    def test_max_and_overflow(self) -> None:
        """Test UserProfileUpdate with max and overflow values."""
        name: str = "x" * 128
        bio: str = "y" * 512
        update: UserProfileUpdate = UserProfileUpdate(name=name, bio=bio)
        self.assert_equal(update.name, name)
        self.assert_equal(update.bio, bio)
        self.assert_raises(ValueError, UserProfileUpdate, name="x" * 129, bio=None)
        self.assert_raises(ValueError, UserProfileUpdate, name=None, bio="y" * 513)

    def test_whitespace(self) -> None:
        """Test UserProfileUpdate with whitespace-only fields."""
        update: UserProfileUpdate = UserProfileUpdate(name="   ", bio="\n\t")
        if update.name is not None:
            self.assert_is_true(update.name.isspace())
        if update.bio is not None:
            self.assert_is_true(update.bio.isspace())


class TestUserPreferencesSchema(ModelUnitTestTemplate):
    """Strictly typed tests for the UserPreferences schema."""

    def test_valid_and_partial(self) -> None:
        """Test UserPreferences with valid, partial, and empty values."""
        prefs: UserPreferences = UserPreferences(theme="dark", locale="en")
        self.assert_equal(prefs.theme, "dark")
        self.assert_equal(prefs.locale, "en")
        prefs2: UserPreferences = UserPreferences(theme="light", locale=None)
        self.assert_equal(prefs2.theme, "light")
        self.assert_is_none(prefs2.locale)
        prefs3: UserPreferences = UserPreferences(theme=None, locale=None)
        self.assert_is_none(prefs3.theme)
        self.assert_is_none(prefs3.locale)

    def test_edge_cases(self) -> None:
        """Test UserPreferences with invalid and extra fields, expecting ValidationError."""
        import pydantic

        self.assert_raises(
            pydantic.ValidationError,
            UserPreferences,
            **{"theme": "dark", "locale": "en", "unknown": "ignored"},
        )
        self.assert_raises(
            pydantic.ValidationError, UserPreferences, theme=123, locale=None
        )
        self.assert_raises(
            pydantic.ValidationError, UserPreferences, theme=None, locale=object()
        )
        self.assert_raises(pydantic.ValidationError, UserPreferences, preferences=None)
        self.assert_raises(
            pydantic.ValidationError, UserPreferences, preferences={"": ""}
        )
        self.assert_raises(
            pydantic.ValidationError, UserPreferences, preferences={"key": None}
        )
        self.assert_raises(
            pydantic.ValidationError, UserPreferences, preferences={None: "value"}
        )


class TestUserPreferencesUpdateSchema(ModelUnitTestTemplate):
    """Strictly typed tests for the UserPreferencesUpdate schema."""

    def test_deeply_nested_and_empty(self) -> None:
        """Test UserPreferencesUpdate with nested and empty preferences."""
        nested: dict[str, object] = {
            "theme": "dark",
            "settings": {"notifications": {"email": True, "sms": False}},
        }
        prefs: UserPreferencesUpdate = UserPreferencesUpdate(preferences=nested)
        self.assert_is_true(isinstance(prefs.preferences["settings"], dict))
        prefs2: UserPreferencesUpdate = UserPreferencesUpdate(preferences={})
        self.assert_equal(prefs2.preferences, {})

    def test_non_string_keys_and_values(self) -> None:
        """
        Test UserPreferencesUpdate with non-string keys/values, expecting ValidationError for non-string keys only.
        Raises:
            pydantic.ValidationError: If a non-string key is provided.
        """
        import pydantic
        import pytest

        def make_invalid_preferences() -> object:
            # This helper intentionally returns an invalid type for testing
            return {1: "one", "two": 2}

        # This should raise because 1 is not a string key
        with pytest.raises(pydantic.ValidationError):
            UserPreferencesUpdate(preferences=make_invalid_preferences())  # type: ignore[arg-type]

        # This should NOT raise, as all keys are strings (even if values are not)
        prefs: UserPreferencesUpdate = UserPreferencesUpdate(preferences={"two": 2})
        self.assert_equal(prefs.preferences["two"], 2)


class TestUserAvatarResponseSchema(ModelUnitTestTemplate):
    """Strictly typed tests for the UserAvatarResponse schema."""

    def test_valid_and_special_characters(self) -> None:
        """Test UserAvatarResponse with valid and special character avatar URLs."""
        resp: UserAvatarResponse = UserAvatarResponse(
            avatar_url="/uploads/avatars/1_avatar.png"
        )
        self.assert_is_true(resp.avatar_url.endswith("avatar.png"))
        resp2: UserAvatarResponse = UserAvatarResponse(
            avatar_url="/uploads/avatars/!@#$%^&*().png"
        )
        self.assert_is_true(any(c in resp2.avatar_url for c in "!@#$%^&*()"))
        resp3: UserAvatarResponse = UserAvatarResponse(
            avatar_url="/uploads/avatars/😀.png"
        )
        self.assert_in("😀", resp3.avatar_url)
        resp4: UserAvatarResponse = UserAvatarResponse(
            avatar_url="/uploads/avatars/with space.png"
        )
        self.assert_in(" ", resp4.avatar_url)
        resp5: UserAvatarResponse = UserAvatarResponse(avatar_url="")
        self.assert_equal(resp5.avatar_url, "")

    def test_invalid(self) -> None:
        """Test UserAvatarResponse with invalid avatar_url, expecting ValidationError."""
        import pydantic

        self.assert_raises(
            pydantic.ValidationError, UserAvatarResponse, avatar_url=None
        )
