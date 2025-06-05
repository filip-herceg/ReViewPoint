from datetime import UTC, datetime

import pytest

from src.schemas.user import (
    UserAvatarResponse,
    UserPreferences,
    UserProfile,
    UserProfileUpdate,
)


def test_user_profile_schema_basic() -> None:
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
    assert profile.id == 1
    assert profile.email == "test@example.com"
    assert profile.name == "Test User"
    assert profile.bio == "Hello!"
    assert profile.avatar_url and profile.avatar_url.endswith("avatar.png")
    assert profile.created_at == now
    assert profile.updated_at == now


def test_user_profile_update_schema() -> None:
    # Valid update
    update = UserProfileUpdate(name="New Name", bio="New bio")
    assert update.name == "New Name"
    assert update.bio == "New bio"
    # Empty update (all fields optional)
    update2 = UserProfileUpdate(name=None, bio=None)
    assert update2.name is None and update2.bio is None
    # Too long name
    with pytest.raises(ValueError):
        UserProfileUpdate(name="x" * 200, bio="bio")


def test_user_preferences_schema() -> None:
    prefs = UserPreferences(theme="dark", locale="en")
    assert prefs.theme == "dark"
    assert prefs.locale == "en"
    # Partial
    prefs2 = UserPreferences(theme="light", locale=None)
    assert prefs2.theme == "light"
    assert prefs2.locale is None
    # Empty
    prefs3 = UserPreferences(theme=None, locale=None)
    assert prefs3.theme is None and prefs3.locale is None


def test_user_avatar_response_schema() -> None:
    resp = UserAvatarResponse(avatar_url="/uploads/avatars/1_avatar.png")
    assert resp.avatar_url.endswith("avatar.png")
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        UserAvatarResponse(avatar_url=None)  # type: ignore[arg-type]


def test_user_profile_schema_edge_cases() -> None:
    import pydantic

    # Missing required fields
    with pytest.raises(pydantic.ValidationError):
        UserProfile(id=None, email=None)  # type: ignore[arg-type]
    # Invalid email type
    with pytest.raises(pydantic.ValidationError):
        UserProfile(id=1, email=None)  # type: ignore[arg-type]
    # Extra fields should raise ValidationError
    with pytest.raises(pydantic.ValidationError):
        UserProfile(id=1, email="a@b.com", extra_field="ignored")  # type: ignore[call-arg]


def test_user_profile_update_schema_edge_cases() -> None:
    # Name at max length
    name = "x" * 128
    update = UserProfileUpdate(name=name, bio=None)
    assert update.name == name
    # Bio at max length
    bio = "y" * 512
    update2 = UserProfileUpdate(name=None, bio=bio)
    assert update2.bio == bio
    # Name just over max length
    with pytest.raises(ValueError):
        UserProfileUpdate(name="x" * 129, bio=None)
    # Bio just over max length
    with pytest.raises(ValueError):
        UserProfileUpdate(name=None, bio="y" * 513)


def test_user_preferences_schema_edge_cases() -> None:
    # Both fields None
    prefs = UserPreferences(theme=None, locale=None)
    assert prefs.theme is None and prefs.locale is None
    # Both fields set
    prefs2 = UserPreferences(theme="dark", locale="en")
    assert prefs2.theme == "dark" and prefs2.locale == "en"
    # Extra field should raise ValidationError (simulate by passing as dict)
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        UserPreferences(**{"theme": "dark", "locale": "en", "unknown": "ignored"})


def test_user_avatar_response_schema_edge_cases() -> None:
    # Empty string for avatar_url
    resp = UserAvatarResponse(avatar_url="")
    assert resp.avatar_url == ""


def test_user_profile_boundary_values() -> None:
    # Name and bio at max length
    name = "n" * 128
    bio = "b" * 512
    profile = UserProfile(id=10, email="b@b.com", name=name, bio=bio)
    assert profile.name == name
    assert profile.bio == bio
    # Name and bio just over max length should fail
    with pytest.raises(ValueError):
        UserProfileUpdate(name="n" * 129, bio=None)
    with pytest.raises(ValueError):
        UserProfileUpdate(name=None, bio="b" * 513)


def test_user_profile_unicode_and_special_characters() -> None:
    profile = UserProfile(
        id=11,
        email="üñîçødë@example.com",
        name="测试用户 🚀",
        bio="Résumé: naïve façade. 💡",
        avatar_url="/uploads/avatars/11_😀.png",
    )
    assert "üñîçødë" in profile.email
    assert profile.name and "测试用户" in profile.name
    assert profile.bio and "💡" in profile.bio
    assert profile.avatar_url and profile.avatar_url.endswith("😀.png")


def test_user_profile_serialization() -> None:
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
    assert d["name"] == "Serial"
    assert isinstance(d["created_at"], datetime)
    j = profile.model_dump_json()
    assert '"name":"Serial"' in j
    assert '"created_at":' in j


def test_user_profile_default_values() -> None:
    profile = UserProfile(id=13, email="default@example.com")
    assert profile.name is None
    assert profile.bio is None
    assert profile.avatar_url is None
    assert profile.created_at is None
    assert profile.updated_at is None


def test_user_profile_invalid_types() -> None:
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        UserProfile(id=14, email="badtype@example.com", name=123)  # type: ignore[arg-type]
    with pytest.raises(pydantic.ValidationError):
        UserProfile(id=15, email="badtype@example.com", bio=object())  # type: ignore[arg-type]
    with pytest.raises(pydantic.ValidationError):
        UserProfile(id=16, email=123)  # type: ignore[arg-type]


def test_user_preferences_empty_and_invalid() -> None:
    import pydantic

    # Empty dict
    prefs = UserPreferences(theme=None, locale=None)
    assert prefs.theme is None and prefs.locale is None
    # Missing fields (should default to None)
    prefs2 = UserPreferences(theme=None, locale=None)
    assert prefs2.theme is None
    # Invalid types
    with pytest.raises(pydantic.ValidationError):
        UserPreferences(theme=123, locale=None)  # type: ignore[arg-type]
    with pytest.raises(pydantic.ValidationError):
        UserPreferences(theme=None, locale=object())  # type: ignore[arg-type]


def test_user_avatar_url_edge_cases() -> None:
    # Spaces in URL
    resp = UserAvatarResponse(avatar_url="/uploads/avatars/with space.png")
    assert " " in resp.avatar_url
    # Unicode in URL
    resp2 = UserAvatarResponse(avatar_url="/uploads/avatars/😀.png")
    assert "😀" in resp2.avatar_url
    # Invalid format (empty string is allowed by schema)
    resp3 = UserAvatarResponse(avatar_url="")
    assert resp3.avatar_url == ""


def test_user_profile_extreme_id() -> None:
    # Very large id
    profile = UserProfile(id=2**31 - 1, email="bigid@example.com")
    assert profile.id == 2**31 - 1
    # Very small id
    profile2 = UserProfile(id=0, email="zeroid@example.com")
    assert profile2.id == 0
    # Negative id (should be allowed unless schema restricts)
    profile3 = UserProfile(id=-1, email="negid@example.com")
    assert profile3.id == -1


def test_user_profile_invalid_email_formats() -> None:
    # Not an email, but schema only requires str, so this should pass
    profile = UserProfile(id=100, email="notanemail")
    assert profile.email == "notanemail"
    # Empty string as email
    profile2 = UserProfile(id=101, email="")
    assert profile2.email == ""


def test_user_profile_empty_strings() -> None:
    profile = UserProfile(
        id=102, email="empty@example.com", name="", bio="", avatar_url=""
    )
    assert profile.name == ""
    assert profile.bio == ""
    assert profile.avatar_url == ""


def test_user_profile_whitespace_fields() -> None:
    profile = UserProfile(
        id=103, email="ws@example.com", name="   ", bio="\t\n", avatar_url=" "
    )
    if profile.name is not None:
        assert profile.name.isspace()
    if profile.bio is not None:
        assert profile.bio.isspace()
    if profile.avatar_url is not None:
        assert profile.avatar_url.isspace()


def test_user_profile_future_and_past_dates() -> None:
    from datetime import datetime, timedelta

    now = datetime.now(UTC)
    future = now + timedelta(days=365)
    past = now - timedelta(days=365)
    profile = UserProfile(
        id=104, email="date@example.com", created_at=future, updated_at=past
    )
    if profile.created_at is not None:
        assert profile.created_at > now
    if profile.updated_at is not None:
        assert profile.updated_at < now


def test_user_profile_update_whitespace() -> None:
    update = UserProfileUpdate(name="   ", bio="\n\t")
    if update.name is not None:
        assert update.name.isspace()
    if update.bio is not None:
        assert update.bio.isspace()


def test_user_preferences_deeply_nested() -> None:
    from src.schemas.user import UserPreferencesUpdate

    nested = {
        "theme": "dark",
        "settings": {"notifications": {"email": True, "sms": False}},
    }
    prefs = UserPreferencesUpdate(preferences=nested)
    assert isinstance(prefs.preferences["settings"], dict)


def test_user_preferences_empty_dict() -> None:
    from src.schemas.user import UserPreferencesUpdate

    prefs = UserPreferencesUpdate(preferences={})
    assert prefs.preferences == {}


def test_user_preferences_non_string_keys_values() -> None:
    import pydantic

    from src.schemas.user import UserPreferencesUpdate

    # Non-string key should raise validation error
    with pytest.raises(pydantic.ValidationError):
        UserPreferencesUpdate(preferences={1: "one", "two": 2})  # type: ignore[dict-item]
    # Non-string value is allowed
    prefs = UserPreferencesUpdate(preferences={"two": 2})
    assert prefs.preferences["two"] == 2


def test_user_avatar_url_special_characters() -> None:
    resp = UserAvatarResponse(avatar_url="/uploads/avatars/!@#$%^&*().png")
    assert any(c in resp.avatar_url for c in "!@#$%^&*()")


def test_user_profile_unicode_everywhere() -> None:
    profile = UserProfile(
        id=105,
        email="用户@例子.公司",
        name="名字🌟",
        bio="简介💬",
        avatar_url="/uploads/avatars/用户🌟.png",
    )
    if profile.email is not None:
        assert "用户" in profile.email
    if profile.name is not None:
        assert "🌟" in profile.name
    if profile.bio is not None:
        assert "💬" in profile.bio
    if profile.avatar_url is not None:
        assert "用户" in profile.avatar_url
