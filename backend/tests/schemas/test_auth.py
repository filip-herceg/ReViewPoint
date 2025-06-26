import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from src.main import app
from src.schemas.auth import (
    AuthResponse,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    UserLoginRequest,
    UserRegisterRequest,
)


def test_user_register_request_valid():
    req = UserRegisterRequest(
        email="user@example.com", password="password123", name="Test User"
    )
    assert req.email == "user@example.com"
    assert req.password == "password123"
    assert req.name == "Test User"


def test_user_register_request_invalid_email():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="not-an-email", password="password123", name="Test User"
        )


def test_user_register_request_short_password():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="user@example.com", password="short", name="Test User"
        )


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
    resp = AuthResponse(access_token="abc123", refresh_token="def456")
    assert resp.access_token == "abc123"
    assert resp.refresh_token == "def456"
    assert resp.token_type == "bearer"


def test_message_response():
    resp = MessageResponse(message="ok")
    assert resp.message == "ok"


@pytest.mark.asyncio
async def test_register_success_branch(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": f"success_{uuid.uuid4()}@example.com",
                "password": "SecurePass123!",
                "name": "Success User",
            },
        )
        assert resp.status_code == 200 or resp.status_code == 201
        assert "access_token" in resp.json()
        assert "refresh_token" in resp.json()
        assert (
            isinstance(resp.json()["refresh_token"], str)
            and resp.json()["refresh_token"]
        )


@pytest.mark.asyncio
async def test_login_success_branch(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"login_success_{uuid.uuid4()}@example.com"
        password = "SecurePass123!"
        await ac.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "name": "Login Success User"},
        )
        resp = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert "refresh_token" in resp.json()
        assert (
            isinstance(resp.json()["access_token"], str) and resp.json()["access_token"]
        )
        assert (
            isinstance(resp.json()["refresh_token"], str)
            and resp.json()["refresh_token"]
        )


@pytest.mark.asyncio
async def test_logout_success_branch(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"logout_success_{uuid.uuid4()}@example.com"
        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "name": "Logout Success User",
            },
        )
        token = resp.json()["access_token"]
        resp2 = await ac.post(
            "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp2.status_code == 200
        assert resp2.json()["message"] == "Logged out successfully."
        # Optionally, try to use the token again (if /me endpoint exists)
        # resp3 = await ac.get(
        #     "/api/v1/auth/me",
        #     headers={"Authorization": f"Bearer {token}"}
        # )
        # assert resp3.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success_branch(
    async_session, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "testsecret")
    monkeypatch.setenv("REVIEWPOINT_DB_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REVIEWPOINT_AUTH_ENABLED", "true")
    monkeypatch.setenv("REVIEWPOINT_JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("REVIEWPOINT_JWT_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("REVIEWPOINT_ALLOWED_ORIGINS", '["*"]')
    monkeypatch.setenv("REVIEWPOINT_API_KEY_ENABLED", "false")
    monkeypatch.setenv("REVIEWPOINT_API_KEY", "testkey")
    import importlib

    import src.core.config

    importlib.reload(src.core.config)
    from src.core.config import settings

    print(
        f"DEBUG: jwt_secret_key={settings.jwt_secret_key}, jwt_secret={settings.jwt_secret}, jwt_algorithm={settings.jwt_algorithm}"
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"refresh_success_{uuid.uuid4()}@example.com"
        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "name": "Refresh Success User",
            },
        )
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        refresh_token = login_resp.json().get("refresh_token")
        print(f"DEBUG: login_resp={login_resp.json()}")
        print(f"DEBUG: refresh_token={refresh_token}")
        resp2 = await ac.post(
            "/api/v1/auth/refresh-token",
            json={"token": refresh_token},
        )
        print(f"DEBUG: refresh resp2: {resp2.status_code}, {resp2.text}")
        assert resp2.status_code == 200
        assert "access_token" in resp2.json()


@pytest.mark.asyncio
async def test_password_reset_request_success_branch(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"reset_request_{uuid.uuid4()}@example.com"
        await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "name": "Reset Request User",
            },
        )
        resp = await ac.post(
            "/api/v1/auth/request-password-reset",
            json={"email": email},
        )
        assert resp.status_code == 200
        assert "message" in resp.json()


def test_user_register_request_invalid_password_letter():
    # No letter
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(
            email="user@example.com", password="12345678", name="Test User"
        )
    assert "Password must contain at least one letter" in str(exc_info.value)


def test_user_register_request_invalid_password_digit():
    # No digit
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(
            email="user@example.com", password="abcdefgh", name="Test User"
        )
    assert "Password must contain at least one digit" in str(exc_info.value)


def test_password_reset_request_invalid_email():
    with pytest.raises(ValidationError) as exc_info:
        PasswordResetRequest(email="not-an-email")
    # Accept Pydantic's built-in error message
    assert "valid email address" in str(exc_info.value) or "@-sign" in str(
        exc_info.value
    )


def test_password_reset_confirm_request_invalid_password_letter():
    # No letter
    with pytest.raises(ValidationError) as exc_info:
        PasswordResetConfirmRequest(token="sometoken", new_password="12345678")
    assert "Password must contain at least one letter" in str(exc_info.value)


def test_password_reset_confirm_request_invalid_password_digit():
    # No digit
    with pytest.raises(ValidationError) as exc_info:
        PasswordResetConfirmRequest(token="sometoken", new_password="abcdefgh")
    assert "Password must contain at least one digit" in str(exc_info.value)


@pytest.mark.asyncio
async def test_logout_with_invalid_token(async_session):
    """Test logout endpoint with an invalid/malformed token in the Authorization header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register and login
        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": f"logoutinvalidtoken_{uuid.uuid4()}@example.com",
                "password": "SecurePass123!",
                "name": "Logout Invalid Token",
            },
        )
        # Try logout with a malformed token
        resp = await ac.post(
            "/api/v1/auth/logout", headers={"Authorization": "Bearer not.a.jwt.token"}
        )
        # Should return 401 (unauthorized) if token is invalid
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_logout_without_authorization_header(async_session):
    """Test logout endpoint with no Authorization header present."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register and login
        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": f"logoutnoauth_{uuid.uuid4()}@example.com",
                "password": "SecurePass123!",
                "name": "Logout No Auth",
            },
        )
        # Logout without Authorization header
        resp = await ac.post("/api/v1/auth/logout")
        # Should return 401 (unauthorized) if no token is present
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_refresh_token_blacklisted(async_session):
    """Test refresh token endpoint with a blacklisted token (should return 401)."""
    from src.api.deps import get_async_refresh_access_token
    from src.services.user import RefreshTokenBlacklistedError

    transport = ASGITransport(app=app)

    class MockRefresh:
        async def __call__(self, session, token):
            raise RefreshTokenBlacklistedError("blacklisted")

    app.dependency_overrides[get_async_refresh_access_token] = lambda: MockRefresh()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"refresh_blacklisted_{uuid.uuid4()}@example.com"
        await ac.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePass123!", "name": "Blacklisted"},
        )
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        refresh_token = login_resp.json().get("refresh_token")
        resp = await ac.post(
            "/api/v1/auth/refresh-token",
            json={"token": refresh_token},
        )
        assert resp.status_code == 401
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_refresh_token_rate_limited(async_session):
    """Test refresh token endpoint with a rate-limited token (should return 429)."""
    from src.api.deps import get_async_refresh_access_token
    from src.services.user import RefreshTokenRateLimitError

    transport = ASGITransport(app=app)

    class MockRefresh:
        async def __call__(self, session, token):
            raise RefreshTokenRateLimitError("rate limited")

    app.dependency_overrides[get_async_refresh_access_token] = lambda: MockRefresh()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"refresh_ratelimit_{uuid.uuid4()}@example.com"
        await ac.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePass123!", "name": "RateLimit"},
        )
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        refresh_token = login_resp.json().get("refresh_token")
        resp = await ac.post(
            "/api/v1/auth/refresh-token",
            json={"token": refresh_token},
        )
        assert resp.status_code == 429
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_refresh_token_decode_error(async_session):
    """Test refresh token endpoint with a malformed/invalid token (should return 401)."""
    from src.api.deps import get_async_refresh_access_token
    from src.services.user import RefreshTokenError

    transport = ASGITransport(app=app)

    class MockRefresh:
        async def __call__(self, session, token):
            raise RefreshTokenError("decode error")

    app.dependency_overrides[get_async_refresh_access_token] = lambda: MockRefresh()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"refresh_decode_{uuid.uuid4()}@example.com"
        await ac.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePass123!", "name": "Decode Error"},
        )
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        refresh_token = login_resp.json().get("refresh_token")
        resp = await ac.post(
            "/api/v1/auth/refresh-token",
            json={"token": refresh_token},
        )
        assert resp.status_code == 401
        assert "Invalid or expired refresh token" in resp.text
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_refresh_token_unexpected_error(async_session):
    """Test refresh token endpoint with a generic exception (should return 500)."""
    from src.api.deps import get_async_refresh_access_token

    transport = ASGITransport(app=app)

    class MockRefresh:
        async def __call__(self, session, token):
            raise Exception("fail")

    app.dependency_overrides[get_async_refresh_access_token] = lambda: MockRefresh()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"refresh_unexpected_{uuid.uuid4()}@example.com"
        await ac.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePass123!", "name": "Unexpected"},
        )
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        refresh_token = login_resp.json().get("refresh_token")
        resp = await ac.post(
            "/api/v1/auth/refresh-token",
            json={"token": refresh_token},
        )
        assert resp.status_code == 500
        assert "unexpected error" in resp.text.lower()
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_password_reset_confirm_success_branch(async_session):
    """Test password reset confirm endpoint with valid token and password (success path)."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"pwreset_success_{uuid.uuid4()}@example.com"
        password = "SecurePass123!"
        new_password = "NewSecurePass123!"
        # Register user
        await ac.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "name": "PW Reset Success"},
        )
        # Request password reset to get a token
        with patch(
            "src.services.user.get_password_reset_token", return_value="testtoken123"
        ):
            await ac.post(
                "/api/v1/auth/request-password-reset",
                json={"email": email},
            )
        # Patch reset_password to simulate success
        with patch(
            "src.services.user.reset_password", new=AsyncMock(return_value=None)
        ):
            resp = await ac.post(
                "/api/v1/auth/reset-password",
                json={"token": "testtoken123", "new_password": new_password},
            )
            assert resp.status_code == 200
            assert resp.json()["message"] == "Password has been reset."
