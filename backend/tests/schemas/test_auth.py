import pytest
from tests.test_templates import AuthEndpointTestTemplate
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from src.schemas.auth import (
    AuthResponse,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from src.api.deps import get_async_refresh_access_token
from src.services.user import RefreshTokenBlacklistedError, RefreshTokenRateLimitError, RefreshTokenError


class TestAuthSchemas:
    def test_user_register_request_valid(self):
        req = UserRegisterRequest(
            email="user@example.com", password="password123", name="Test User"
        )
        assert req.email == "user@example.com"
        assert req.password == "password123"
        assert req.name == "Test User"

    @pytest.mark.parametrize(
        "email,password,name",
        [
            ("not-an-email", "password123", "Test User"),
            ("user@example.com", "short", "Test User"),
            ("user@example.com", "password123", None),
        ],
    )
    def test_user_register_request_invalid(self, email, password, name):
        with pytest.raises(ValidationError):
            UserRegisterRequest(email=email, password=password, name=name)

    def test_user_login_request_valid(self):
        req = UserLoginRequest(email="user@example.com", password="password123")
        assert req.email == "user@example.com"
        assert req.password == "password123"

    def test_password_reset_request_valid(self):
        req = PasswordResetRequest(email="user@example.com")
        assert req.email == "user@example.com"

    def test_password_reset_confirm_request_valid(self):
        req = PasswordResetConfirmRequest(
            token="sometoken", new_password="newpassword123"
        )
        assert req.token == "sometoken"
        assert req.new_password == "newpassword123"

    def test_password_reset_confirm_request_short_password(self):
        with pytest.raises(ValidationError):
            PasswordResetConfirmRequest(token="sometoken", new_password="short")

    def test_auth_response(self):
        resp = AuthResponse(access_token="abc123", refresh_token="def456")
        assert resp.access_token == "abc123"
        assert resp.refresh_token == "def456"
        assert resp.token_type == "bearer"

    def test_message_response(self):
        resp = MessageResponse(message="ok")
        assert resp.message == "ok"


class TestAuthEndpoints(AuthEndpointTestTemplate):
    @pytest.mark.asyncio
    async def test_register_success(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REGISTER": "true",
                "REVIEWPOINT_FEATURES": "auth:register",
            }
        )
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": f"success_{uuid.uuid4()}@example.com",
                    "password": "SecurePass123!",
                    "name": "Success User",
                },
            )
            assert resp.status_code in (200, 201)
            data = resp.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_success(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGIN": "true",
                "REVIEWPOINT_FEATURES": "auth:login",
            }
        )
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = f"login_success_{uuid.uuid4()}@example.com"
            password = "SecurePass123!"
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "name": "Login Success User",
                },
            )
            resp = await ac.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_logout_success(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
                "REVIEWPOINT_FEATURES": "auth:logout",
            }
        )
        import uuid

        transport = ASGITransport(app=self.test_app)
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

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )
        import uuid

        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            email = f"refresh_success_{uuid.uuid4()}@example.com"
            await ac.post(
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
            resp2 = await ac.post(
                "/api/v1/auth/refresh-token",
                json={"token": refresh_token},
            )
            assert resp2.status_code == 200
            assert "access_token" in resp2.json()

    @pytest.mark.asyncio
    async def test_password_reset_request_success(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REQUEST_PASSWORD_RESET": "true",
                "REVIEWPOINT_FEATURES": "auth:request_password_reset",
            }
        )
        import uuid

        transport = ASGITransport(app=self.test_app)
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

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
                "REVIEWPOINT_FEATURES": "auth:logout",
            }
        )
        import uuid

        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": f"logoutinvalidtoken_{uuid.uuid4()}@example.com",
                    "password": "SecurePass123!",
                    "name": "Logout Invalid Token",
                },
            )
            resp = await ac.post(
                "/api/v1/auth/logout",
                headers={"Authorization": "Bearer not.a.jwt.token"},
            )
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid token"

    @pytest.mark.asyncio
    async def test_logout_without_authorization_header(self):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
                "REVIEWPOINT_FEATURES": "auth:logout",
            }
        )
        import uuid

        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": f"logoutnoauth_{uuid.uuid4()}@example.com",
                    "password": "SecurePass123!",
                    "name": "Logout No Auth",
                },
            )
            resp = await ac.post("/api/v1/auth/logout")
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_refresh_token_blacklisted(self):
        # Best practice: Disable API key enforcement for this test
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )
        transport = ASGITransport(app=self.test_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise RefreshTokenBlacklistedError("blacklisted")

        self.test_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = f"refresh_blacklisted_{uuid.uuid4()}@example.com"
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Blacklisted",
                },
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
        self.test_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_refresh_token_rate_limited(self):
        # Best practice: Disable API key enforcement and enable refresh token feature
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )
        transport = ASGITransport(app=self.test_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise RefreshTokenRateLimitError("rate limited")

        self.test_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = f"refresh_ratelimit_{uuid.uuid4()}@example.com"
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "RateLimit",
                },
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
        self.test_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_refresh_token_decode_error(self):
        # Best practice: Disable API key enforcement and enable refresh token feature
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )
        transport = ASGITransport(app=self.test_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise RefreshTokenError("decode error")

        self.test_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = f"refresh_decode_{uuid.uuid4()}@example.com"
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Decode Error",
                },
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
        self.test_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_refresh_token_unexpected_error(self):
        # Best practice: Disable API key enforcement and enable refresh token feature
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )
        transport = ASGITransport(app=self.test_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise Exception("fail")

        self.test_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = f"refresh_unexpected_{uuid.uuid4()}@example.com"
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Unexpected",
                },
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
        self.test_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_password_reset_confirm_success_branch(
        self,
    ):
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_RESET_PASSWORD": "true",
                "REVIEWPOINT_FEATURES": "auth:reset_password",
            }
        )
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = f"pwreset_success_{uuid.uuid4()}@example.com"
            password = "SecurePass123!"
            new_password = "NewSecurePass123!"
            # Register user
            await ac.post(
                "/api/v1/auth/register",
                json={"email": email, "password": password, "name": "PW Reset Success"},
            )
            # Request password reset to get a token
            from unittest.mock import AsyncMock, patch

            with patch(
                "src.services.user.get_password_reset_token",
                return_value="testtoken123",
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
