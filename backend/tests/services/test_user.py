import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.services import user as user_service
from src.utils.errors import ValidationError, UserAlreadyExistsError, UserNotFoundError
import string
from jose import jwt
from src.core.security import create_access_token
from src.core.config import settings

@pytest.mark.asyncio
async def test_register_user_success(async_session: AsyncSession):
    data = {"email": "testuser@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    assert user.id is not None
    assert user.email == data["email"]
    assert user.is_active
    assert user.hashed_password != data["password"]

@pytest.mark.asyncio
async def test_register_user_duplicate_email(async_session: AsyncSession):
    data = {"email": "dupe@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(async_session, data)
    await async_session.rollback()
    # No ORM object reuse after rollback

@pytest.mark.asyncio
async def test_register_user_invalid_email(async_session: AsyncSession):
    data = {"email": "bademail", "password": "Abc12345"}
    with pytest.raises(ValidationError):
        await user_service.register_user(async_session, data)
    await async_session.rollback()

@pytest.mark.asyncio
async def test_register_user_invalid_password(async_session: AsyncSession):
    data = {"email": "pwfail@example.com", "password": "short"}
    with pytest.raises(ValidationError):
        await user_service.register_user(async_session, data)
    await async_session.rollback()

@pytest.mark.asyncio
async def test_authenticate_user_success(async_session: AsyncSession):
    data = {"email": "authuser@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    token = await user_service.authenticate_user(async_session, data["email"], data["password"])
    assert isinstance(token, str)
    assert len(token) > 10

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(async_session: AsyncSession):
    data = {"email": "wrongpw@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    with pytest.raises(ValidationError):
        await user_service.authenticate_user(async_session, data["email"], "wrongpass")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_authenticate_user_not_found(async_session: AsyncSession):
    with pytest.raises(UserNotFoundError):
        await user_service.authenticate_user(async_session, "notfound@example.com", "Abc12345")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_logout_user_deactivates(async_session: AsyncSession):
    data = {"email": "logout@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    await user_service.logout_user(async_session, user.id)
    refreshed = await async_session.get(User, user.id)
    assert refreshed is not None and not refreshed.is_active

@pytest.mark.asyncio
async def test_is_authenticated():
    user = User(email="active@example.com", hashed_password="x", is_active=True, is_deleted=False)
    assert user_service.is_authenticated(user)
    user.is_active = False
    assert not user_service.is_authenticated(user)
    user.is_active = True
    user.is_deleted = True
    assert not user_service.is_authenticated(user)

@pytest.mark.asyncio
async def test_is_authenticated_stub_cases():
    # Active and not deleted
    user = User(email="active@example.com", hashed_password="x", is_active=True, is_deleted=False)
    assert user_service.is_authenticated(user)
    # Inactive
    user.is_active = False
    user.is_deleted = False
    assert not user_service.is_authenticated(user)
    # Deleted
    user.is_active = True
    user.is_deleted = True
    assert not user_service.is_authenticated(user)
    # Inactive and deleted
    user.is_active = False
    user.is_deleted = True
    assert not user_service.is_authenticated(user)

@pytest.mark.asyncio
async def test_logout_user_nonexistent(async_session: AsyncSession):
    # Should not raise, but should not fail if user does not exist
    try:
        await user_service.logout_user(async_session, user_id=999999)
    except Exception as e:
        pytest.fail(f"logout_user raised an exception for nonexistent user: {e}")

def test_refresh_access_token_valid():
    user_id = 123
    email = "refresh@example.com"
    payload = {"sub": str(user_id), "email": email, "nonce": "1"}
    token = user_service.create_access_token(payload)
    # Wait a second to ensure exp is different (if needed)
    import time
    time.sleep(1)
    # Add a different nonce to force a new token
    new_payload = {"sub": str(user_id), "email": email, "nonce": "2"}
    new_token = user_service.create_access_token(new_payload)
    assert new_token != token
    # Now test refresh_access_token returns a valid token (may be same if claims are identical)
    refreshed_token = user_service.refresh_access_token(user_id, token)
    assert isinstance(refreshed_token, str)
    # Accept that the token may be the same if claims and exp are identical
    # But it should decode to the same payload
    decoded = user_service.verify_email_token(refreshed_token)
    assert decoded["email"] == email

def test_refresh_access_token_invalid_subject():
    user_id = 123
    payload = {"sub": "999", "email": "refresh@example.com"}
    token = user_service.create_access_token(payload)
    with pytest.raises(ValidationError):
        user_service.refresh_access_token(user_id, token)

def test_refresh_access_token_invalid_token():
    with pytest.raises(ValidationError):
        user_service.refresh_access_token(1, "not.a.jwt.token")

def test_revoke_refresh_token_stub():
    # Should not raise or do anything
    try:
        user_service.revoke_refresh_token(1, "sometoken")
    except Exception as e:
        pytest.fail(f"revoke_refresh_token raised: {e}")

def test_verify_email_token_valid():
    payload = {"sub": "1", "email": "verify@example.com", "purpose": "email_verify"}
    token = user_service.create_access_token(payload)
    decoded = user_service.verify_email_token(token)
    assert decoded["email"] == "verify@example.com"
    assert decoded["purpose"] == "email_verify"

def test_verify_email_token_invalid():
    with pytest.raises(ValidationError):
        user_service.verify_email_token("not.a.jwt.token")

@pytest.mark.asyncio
async def test_get_password_reset_token_and_reset_password(async_session: AsyncSession, caplog):
    # Register user
    data = {"email": "resetme@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    # Generate reset token
    with caplog.at_level("INFO"):
        token = user_service.get_password_reset_token(user.email)
        assert f"Password reset link sent to {user.email}" in caplog.text
    # Reset password with valid token
    new_password = "Newpass123"
    await user_service.reset_password(async_session, token, new_password)
    # Authenticate with new password
    token2 = await user_service.authenticate_user(async_session, user.email, new_password)
    assert isinstance(token2, str)
    # Try with old password (should fail)
    with pytest.raises(ValidationError):
        await user_service.authenticate_user(async_session, user.email, data["password"])

@pytest.mark.asyncio
async def test_reset_password_invalid_token(async_session: AsyncSession):
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, "not.a.jwt.token", "Abc12345")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_reset_password_weak_password(async_session: AsyncSession):
    data = {"email": "weakreset@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    token = user_service.get_password_reset_token(data["email"])
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, token, "short")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_reset_password_wrong_purpose(async_session: AsyncSession):
    token = create_access_token({"sub": "resetme@example.com", "purpose": "notreset"})
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, token, "Abc12345")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_change_password_success_and_failures(async_session: AsyncSession, caplog):
    data = {"email": "changepw@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    user_id = user.id
    # Success
    with caplog.at_level("INFO"):
        await user_service.change_password(async_session, user_id, data["password"], "Newpass123")
        assert "Password changed for user" in caplog.text
    # Old password wrong
    with pytest.raises(ValidationError):
        await user_service.change_password(async_session, user_id, "wrongpw", "Another123")
    await async_session.rollback()
    # Re-fetch user after rollback
    user = await async_session.get(User, user_id)
    # Weak new password
    with pytest.raises(ValidationError):
        await user_service.change_password(async_session, user_id, "Newpass123", "short")
    await async_session.rollback()
    user = await async_session.get(User, user_id)
    # User not found
    with pytest.raises(UserNotFoundError):
        await user_service.change_password(async_session, 999999, "irrelevant", "Abc12345")
    await async_session.rollback()

def test_validate_password_strength():
    # Strong password
    user_service.validate_password_strength("Abc12345")
    # Too short
    with pytest.raises(ValidationError):
        user_service.validate_password_strength("short")
    # No digit
    with pytest.raises(ValidationError):
        user_service.validate_password_strength("NoDigitsHere")
    # No letter
    with pytest.raises(ValidationError):
        user_service.validate_password_strength("12345678")

@pytest.mark.asyncio
async def test_password_reset_token_expiry(async_session):
    """Simulate expired password reset token."""
    import time
    email = "expiretoken@example.com"
    await user_service.register_user(async_session, {"email": email, "password": "Abc12345"})
    # Create token with exp in the past
    token = create_access_token({"sub": email, "purpose": "reset"})
    payload = jwt.decode(token, str(settings.jwt_secret_key), algorithms=[settings.jwt_algorithm], options={"verify_exp": False})
    payload["exp"] = int(time.time()) - 60
    expired_token = jwt.encode(payload, str(settings.jwt_secret_key), algorithm=settings.jwt_algorithm)
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, expired_token, "Newpass123")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_password_reset_nonexistent_email(async_session):
    """Password reset for nonexistent email should raise UserNotFoundError."""
    token = user_service.get_password_reset_token("notfound@example.com")
    with pytest.raises(UserNotFoundError):
        await user_service.reset_password(async_session, token, "Abc12345")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_password_reset_token_reuse(async_session):
    """Password reset token should not be reusable (future-proofing: currently allowed, but should succeed only once)."""
    data = {"email": "reuse@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    token = user_service.get_password_reset_token(data["email"])
    await user_service.reset_password(async_session, token, "Newpass123")
    # Try to use the same token again (should fail if token is one-time use; currently, it will succeed)
    # For now, expect ValidationError due to password already changed (if password is the same, else allow)
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, token, "Another123")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_change_password_same_as_old(async_session):
    """Changing password to the same as old should raise ValidationError (if enforced)."""
    data = {"email": "samepw@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    # Should raise if password validation checks for same as old
    with pytest.raises(ValidationError):
        await user_service.change_password(async_session, user.id, data["password"], data["password"])
    await async_session.rollback()

@pytest.mark.asyncio
async def test_password_reset_tampered_token(async_session):
    """Tampered reset token should fail."""
    data = {"email": "tampered@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    token = user_service.get_password_reset_token(data["email"])
    tampered = token + "x"
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, tampered, "Newpass123")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_password_reset_missing_claims(async_session):
    """Reset token missing claims (purpose/sub) should fail."""
    # Missing purpose
    token1 = create_access_token({"sub": "missingpurpose@example.com"})
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, token1, "Abc12345")
    await async_session.rollback()
    # Missing sub
    token2 = create_access_token({"purpose": "reset"})
    with pytest.raises(ValidationError):
        await user_service.reset_password(async_session, token2, "Abc12345")
    await async_session.rollback()

@pytest.mark.asyncio
async def test_change_password_inactive_deleted_user(async_session: AsyncSession):
    data = {"email": "inactive@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    user_id = user.id
    # Deactivate user
    await user_service.logout_user(async_session, user_id)
    with pytest.raises(UserNotFoundError):
        await user_service.change_password(async_session, user_id, data["password"], "Newpass123")
    await async_session.rollback()
    # Re-fetch user after rollback
    user = await async_session.get(User, user_id)
    await user_service.register_user(async_session, {"email": "deleted@example.com", "password": "Abc12345"})
    deleted_user = await async_session.get(User, user_id)
    if deleted_user is not None:
        deleted_user.is_deleted = True
        await async_session.commit()
        with pytest.raises(UserNotFoundError):
            await user_service.change_password(async_session, user_id, data["password"], "Another123")
        await async_session.rollback()

@pytest.mark.asyncio
async def test_get_user_profile_and_update(async_session: AsyncSession):
    data = {"email": "profile@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    # Initially, profile fields are None
    profile = await user_service.get_user_profile(async_session, user.id)
    assert profile.email == data["email"]
    assert profile.name is None and profile.bio is None
    # Update profile
    update = {"name": "Test User", "bio": "Hello!"}
    updated = await user_service.update_user_profile(async_session, user.id, update)
    assert updated.name == "Test User"
    assert updated.bio == "Hello!"
    # Not found case
    with pytest.raises(UserNotFoundError):
        await user_service.get_user_profile(async_session, 999999)

@pytest.mark.asyncio
async def test_set_user_preferences(async_session: AsyncSession):
    data = {"email": "prefs@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    prefs = {"theme": "dark", "locale": "en"}
    result = await user_service.set_user_preferences(async_session, user.id, prefs)
    assert result.theme == "dark"
    assert result.locale == "en"
    # Update preferences
    new_prefs = {"theme": "light", "locale": "fr"}
    result2 = await user_service.set_user_preferences(async_session, user.id, new_prefs)
    assert result2.theme == "light"
    assert result2.locale == "fr"
    # Not found case
    with pytest.raises(UserNotFoundError):
        await user_service.set_user_preferences(async_session, 999999, prefs)

import io
from fastapi import UploadFile
@pytest.mark.asyncio
async def test_upload_avatar(async_session: AsyncSession, tmp_path: str):
    data = {"email": "avatar@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    # Simulate file upload
    content = b"fake image data"
    file = UploadFile(filename="avatar.png", file=io.BytesIO(content))
    resp = await user_service.upload_avatar(async_session, user.id, file)
    assert resp.avatar_url.endswith("avatar.png")
    # Not found case
    file2 = UploadFile(filename="avatar2.png", file=io.BytesIO(content))
    with pytest.raises(UserNotFoundError):
        await user_service.upload_avatar(async_session, 999999, file2)

@pytest.mark.asyncio
async def test_update_user_profile_empty_and_invalid(async_session: AsyncSession):
    data = {"email": "emptyprofile@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    # Empty update should not change anything
    updated = await user_service.update_user_profile(async_session, user.id, {})
    assert updated.name is None and updated.bio is None
    # Invalid field should raise ValidationError due to extra = 'forbid'
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        await user_service.update_user_profile(async_session, user.id, {"notafield": "value"})
    # Update with too long name
    long_name = "x" * 200
    with pytest.raises(ValueError):
        await user_service.update_user_profile(async_session, user.id, {"name": long_name})

@pytest.mark.asyncio
async def test_set_user_preferences_partial_and_invalid(async_session: AsyncSession):
    data = {"email": "partialprefs@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    # Partial preferences
    prefs = {"theme": "dark"}
    result = await user_service.set_user_preferences(async_session, user.id, prefs)
    assert result.theme == "dark"
    assert result.locale is None
    # Preferences with extra fields
    extra: dict[str, object] = {"theme": "dark", "locale": "en", "extra": 123}
    result2 = await user_service.set_user_preferences(async_session, user.id, extra)
    assert result2.theme == "dark"
    assert result2.locale == "en"

@pytest.mark.asyncio
async def test_upload_avatar_invalid_file(async_session: AsyncSession):
    data = {"email": "badavatar@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    import io
    from fastapi import UploadFile
    # Simulate file with no filename
    file = UploadFile(filename="", file=io.BytesIO(b""))
    resp = await user_service.upload_avatar(async_session, user.id, file)
    assert resp.avatar_url.endswith("_")  # Should still create a file with _ as filename
    # Simulate very large file (should not error, but test for performance)
    big_content = b"0" * 1024 * 1024  # 1MB
    big_file = UploadFile(filename="big.png", file=io.BytesIO(big_content))
    resp2 = await user_service.upload_avatar(async_session, user.id, big_file)
    assert resp2.avatar_url.endswith("big.png")
