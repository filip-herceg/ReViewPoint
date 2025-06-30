from datetime import UTC, datetime, timedelta

from src.schemas.user import (
    UserAvatarResponse,
    UserPreferences,
    UserPreferencesUpdate,
    UserProfile,
    UserProfileUpdate,
)
from tests.test_templates import ModelUnitTestTemplate


class TestUserProfileSchema(ModelUnitTestTemplate):
    def test_basic(self):
        now = datetime.now(UTC)
        profile = UserProfile(
            id=1,
            email="test@example.com",
            name="Test User",
            bio="Hello!",
            avatar_url="/uploads/avatars/1_avatar.png",
            created_at=now,
            updated_at=now,
        )
        self.assert_model_attrs(
            profile,
            {
                "id": 1,
                "email": "test@example.com",
                "name": "Test User",
                "bio": "Hello!",
                "avatar_url": "/uploads/avatars/1_avatar.png",
                "created_at": now,
                "updated_at": now,
            },
        )

    def test_edge_cases(self):
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

    def test_boundary_values(self):
        name = "n" * 128
        bio = "b" * 512
        profile = UserProfile(id=10, email="b@b.com", name=name, bio=bio)
        self.assert_equal(profile.name, name)
        self.assert_equal(profile.bio, bio)
        self.assert_raises(ValueError, UserProfileUpdate, name="n" * 129, bio=None)
        self.assert_raises(ValueError, UserProfileUpdate, name=None, bio="b" * 513)

    def test_unicode_and_special_characters(self):
        profile = UserProfile(
            id=11,
            email="üñîçødë@example.com",
            name="测试用户 🚀",
            bio="Résumé: naïve façade. 💡",
            avatar_url="/uploads/avatars/11_😀.png",
        )
        self.assert_in("üñîçødë", profile.email)
        self.assert_is_true(profile.name and "测试用户" in profile.name)
        self.assert_is_true(profile.bio and "💡" in profile.bio)
        self.assert_is_true(profile.avatar_url and profile.avatar_url.endswith("😀.png"))

    def test_serialization(self):
        now = datetime.now(UTC)
        profile = UserProfile(
            id=12,
            email="serial@example.com",
            name="Serial",
            bio="Test",
            avatar_url="/uploads/avatars/12.png",
            created_at=now,
            updated_at=now,
        )
        d = profile.model_dump()
        assert isinstance(d["created_at"], datetime)
        j = profile.model_dump_json()
        self.assert_in('"name":"Serial"', j)
        self.assert_in('"created_at":', j)

    def test_default_values(self):
        profile = UserProfile(id=13, email="default@example.com")
        self.assert_is_none(profile.name)
        self.assert_is_none(profile.bio)
        self.assert_is_none(profile.avatar_url)
        self.assert_is_none(profile.created_at)
        self.assert_is_none(profile.updated_at)

    def test_invalid_types(self):
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

    def test_extreme_id(self):
        profile = UserProfile(id=2**31 - 1, email="bigid@example.com")
        self.assert_equal(profile.id, 2**31 - 1)
        profile2 = UserProfile(id=0, email="zeroid@example.com")
        self.assert_equal(profile2.id, 0)
        profile3 = UserProfile(id=-1, email="negid@example.com")
        self.assert_equal(profile3.id, -1)

    def test_invalid_email_formats(self):
        profile = UserProfile(id=100, email="notanemail")
        self.assert_equal(profile.email, "notanemail")
        profile2 = UserProfile(id=101, email="")
        self.assert_equal(profile2.email, "")

    def test_empty_strings(self):
        profile = UserProfile(
            id=102, email="empty@example.com", name="", bio="", avatar_url=""
        )
        self.assert_equal(profile.name, "")
        self.assert_equal(profile.bio, "")
        self.assert_equal(profile.avatar_url, "")

    def test_whitespace_fields(self):
        profile = UserProfile(
            id=103, email="ws@example.com", name="   ", bio="\t\n", avatar_url=" "
        )
        if profile.name is not None:
            self.assert_is_true(profile.name.isspace())
        if profile.bio is not None:
            self.assert_is_true(profile.bio.isspace())
        if profile.avatar_url is not None:
            self.assert_is_true(profile.avatar_url.isspace())

    def test_future_and_past_dates(self):
        now = datetime.now(UTC)
        future = now + timedelta(days=365)
        past = now - timedelta(days=365)
        profile = UserProfile(
            id=104, email="date@example.com", created_at=future, updated_at=past
        )
        if profile.created_at is not None:
            self.assert_is_true(profile.created_at > now)
        if profile.updated_at is not None:
            self.assert_is_true(profile.updated_at < now)

    def test_unicode_everywhere(self):
        profile = UserProfile(
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
    def test_valid_and_empty(self):
        update = UserProfileUpdate(name="New Name", bio="New bio")
        self.assert_equal(update.name, "New Name")
        self.assert_equal(update.bio, "New bio")
        update2 = UserProfileUpdate(name=None, bio=None)
        self.assert_is_true(update2.name is None and update2.bio is None)

    def test_max_and_overflow(self):
        name = "x" * 128
        bio = "y" * 512
        update = UserProfileUpdate(name=name, bio=bio)
        self.assert_equal(update.name, name)
        self.assert_equal(update.bio, bio)
        self.assert_raises(ValueError, UserProfileUpdate, name="x" * 129, bio=None)
        self.assert_raises(ValueError, UserProfileUpdate, name=None, bio="y" * 513)

    def test_whitespace(self):
        update = UserProfileUpdate(name="   ", bio="\n\t")
        if update.name is not None:
            self.assert_is_true(update.name.isspace())
        if update.bio is not None:
            self.assert_is_true(update.bio.isspace())


class TestUserPreferencesSchema(ModelUnitTestTemplate):
    def test_valid_and_partial(self):
        prefs = UserPreferences(theme="dark", locale="en")
        self.assert_equal(prefs.theme, "dark")
        self.assert_equal(prefs.locale, "en")
        prefs2 = UserPreferences(theme="light", locale=None)
        self.assert_equal(prefs2.theme, "light")
        self.assert_is_none(prefs2.locale)
        prefs3 = UserPreferences(theme=None, locale=None)
        self.assert_is_none(prefs3.theme)
        self.assert_is_none(prefs3.locale)

    def test_edge_cases(self):
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
    def test_deeply_nested_and_empty(self):
        nested = {
            "theme": "dark",
            "settings": {"notifications": {"email": True, "sms": False}},
        }
        prefs = UserPreferencesUpdate(preferences=nested)
        self.assert_is_true(isinstance(prefs.preferences["settings"], dict))
        prefs2 = UserPreferencesUpdate(preferences={})
        self.assert_equal(prefs2.preferences, {})

    def test_non_string_keys_and_values(self):
        import pydantic
        import pytest
        with pytest.raises(pydantic.ValidationError):
            UserPreferencesUpdate(preferences={1: "one", "two": 2})
        prefs = UserPreferencesUpdate(preferences={"two": 2})
        self.assert_equal(prefs.preferences["two"], 2)


class TestUserAvatarResponseSchema(ModelUnitTestTemplate):
    def test_valid_and_special_characters(self):
        resp = UserAvatarResponse(avatar_url="/uploads/avatars/1_avatar.png")
        self.assert_is_true(resp.avatar_url.endswith("avatar.png"))
        resp2 = UserAvatarResponse(avatar_url="/uploads/avatars/!@#$%^&*().png")
        self.assert_is_true(any(c in resp2.avatar_url for c in "!@#$%^&*()"))
        resp3 = UserAvatarResponse(avatar_url="/uploads/avatars/😀.png")
        self.assert_in("😀", resp3.avatar_url)
        resp4 = UserAvatarResponse(avatar_url="/uploads/avatars/with space.png")
        self.assert_in(" ", resp4.avatar_url)
        resp5 = UserAvatarResponse(avatar_url="")
        self.assert_equal(resp5.avatar_url, "")

    def test_invalid(self):
        import pydantic

        self.assert_raises(
            pydantic.ValidationError, UserAvatarResponse, avatar_url=None
        )
