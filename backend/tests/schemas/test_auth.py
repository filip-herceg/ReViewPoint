from src.schemas.auth import UserRegisterRequest, UserLoginRequest, PasswordResetRequest, PasswordResetConfirmRequest, AuthResponse, MessageResponse
import pytest
from pydantic import ValidationError


def test_user_register_request_valid():
    req = UserRegisterRequest(email="user@example.com", password="password123", name="Test User")
    assert req.email == "user@example.com"
    assert req.password == "password123"
    assert req.name == "Test User"


def test_user_register_request_invalid_email():
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="not-an-email", password="password123", name="Test User")


def test_user_register_request_short_password():
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="user@example.com", password="short", name="Test User")


def test_user_login_request_valid():
    req = UserLoginRequest(email="user@example.com", password="password123")
    assert req.email == "user@example.com"
    assert req.password == "password123"


def test_password_reset_request_valid():
    req = PasswordResetRequest(email="user@example.com")
    assert req.email == "user@example.com"


def test_password_reset_confirm_request_valid():
    req = PasswordResetConfirmRequest(token="sometoken", new_password="newpassword123")
    assert req.token == "sometoken"
    assert req.new_password == "newpassword123"


def test_password_reset_confirm_request_short_password():
    with pytest.raises(ValidationError):
        PasswordResetConfirmRequest(token="sometoken", new_password="short")


def test_auth_response():
    resp = AuthResponse(access_token="abc123")
    assert resp.access_token == "abc123"
    assert resp.token_type == "bearer"


def test_message_response():
    resp = MessageResponse(message="ok")
    assert resp.message == "ok"
