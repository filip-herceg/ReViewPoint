import pytest

from tests.test_data_generators import get_unique_email, get_test_user
from tests.test_templates import AuthEndpointTestTemplate



from typing import Final, Optional, Literal, TypedDict, Callable, Generator, Any
from collections.abc import Sequence, AsyncGenerator
from fastapi import FastAPI
import pytest

from tests.test_templates import AuthEndpointTestTemplate

class UserRegisterRequestDict(TypedDict, total=False):
    email: str
    password: str
    name: Optional[str]

class AuthResponseDict(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str

class MessageResponseDict(TypedDict):
    message: str

class PasswordResetConfirmRequestDict(TypedDict):
    token: str
    new_password: str

class TestAuthSchemas(AuthEndpointTestTemplate):
    def test_user_register_request_valid(self: "TestAuthSchemas") -> None:
        """
        Verifies that UserRegisterRequest accepts valid input and sets all fields correctly.
        """
        from src.schemas.auth import UserRegisterRequest
        req: UserRegisterRequest = UserRegisterRequest(
            email=get_unique_email(), password="password123", name="Test User"
        )
        assert req.email.endswith("@example.com")  # Check it's a unique email
        assert req.password == "password123"
        assert req.name == "Test User"

    @pytest.mark.parametrize(
        "email,password,name",
        [
            ("not-an-email", "password123", "Test User"),
            (get_unique_email(), "short", "Test User"),
        ],
    )
    def test_user_register_request_invalid(
        self: "TestAuthSchemas", email: str, password: str, name: Optional[str]
    ) -> None:
        """
        Verifies that UserRegisterRequest raises ValidationError for invalid input.
        """
        from pydantic import ValidationError
        from src.schemas.auth import UserRegisterRequest
        with pytest.raises(ValidationError):
            UserRegisterRequest(email=email, password=password, name=name)

    def test_user_login_request_valid(self: "TestAuthSchemas") -> None:
        """
        Verifies that UserLoginRequest accepts valid input and sets all fields correctly.
        """
        from src.schemas.auth import UserLoginRequest
        req: UserLoginRequest = UserLoginRequest(email=get_unique_email(), password="password123")
        assert req.email.endswith("@example.com")  # Check it's a unique email
        assert req.password == "password123"

    def test_password_reset_request_valid(self: "TestAuthSchemas") -> None:
        """
        Verifies that PasswordResetRequest accepts valid input and sets the email field correctly.
        """
        from src.schemas.auth import PasswordResetRequest
        req: PasswordResetRequest = PasswordResetRequest(email=get_unique_email())
        assert req.email.endswith("@example.com")  # Check it's a unique email

    def test_password_reset_confirm_request_valid(self: "TestAuthSchemas") -> None:
        """
        Verifies that PasswordResetConfirmRequest accepts valid input and sets all fields correctly.
        """
        from src.schemas.auth import PasswordResetConfirmRequest
        req: PasswordResetConfirmRequest = PasswordResetConfirmRequest(
            token="sometoken", new_password="newpassword123"
        )
        assert req.token == "sometoken"
        assert req.new_password == "newpassword123"

    def test_password_reset_confirm_request_short_password(self: "TestAuthSchemas") -> None:
        """
        Verifies that PasswordResetConfirmRequest raises ValidationError for a too-short password.
        """
        from pydantic import ValidationError
        from src.schemas.auth import PasswordResetConfirmRequest
        with pytest.raises(ValidationError):
            PasswordResetConfirmRequest(token="t", new_password="short")

    def test_auth_response(self: "TestAuthSchemas") -> None:
        """
        Verifies that AuthResponse sets all fields correctly.
        """
        from src.schemas.auth import AuthResponse
        resp: AuthResponse = AuthResponse(access_token="abc123", refresh_token="def456")
        assert resp.access_token == "abc123"
        assert resp.refresh_token == "def456"
        assert resp.token_type == "bearer"

    def test_message_response(self: "TestAuthSchemas") -> None:
        """
        Verifies that MessageResponse sets the message field correctly.
        """
        from src.schemas.auth import MessageResponse
        resp: MessageResponse = MessageResponse(message="ok")
        assert resp.message == "ok"


class TestAuthEndpoints(AuthEndpointTestTemplate):
    def create_fresh_app(self: "TestAuthEndpoints") -> FastAPI:
        """
        Create a fresh FastAPI app with current environment variables and override the async session dependency.
        Ensures config cache is cleared after setting env vars, before app creation.
        Also overrides require_api_key to a no-op for test isolation.
        """
        import sys
        # Remove config module from sys.modules to force reload
        if "src.core.config" in sys.modules:
            del sys.modules["src.core.config"]
        # Import and clear the settings cache
        from src.core.config import clear_settings_cache
        clear_settings_cache()
        # Now import other dependencies
        from src.core.database import get_async_session
        from src.main import create_app
        from fastapi import FastAPI
        # Create the app
        app: FastAPI = create_app()
        # Override the database dependency
        async def _override_get_async_session() -> AsyncGenerator[object, None]:
            yield self.async_session
        app.dependency_overrides[get_async_session] = _override_get_async_session
        # Override require_api_key to a no-op for all tests in this class
        try:
            from src.api.deps import require_api_key
            def _no_api_key(api_key: str | None = None) -> None:
                pass
            app.dependency_overrides[require_api_key] = _no_api_key
        except ImportError:
            pass
        return app

    @pytest.mark.asyncio
    async def test_register_success(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REGISTER": "true",
                "REVIEWPOINT_FEATURES": "auth:register",
            }
        )

        fresh_app = self.create_fresh_app()
        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": get_unique_email(),
                    "password": "SecurePass123!",
                    "name": "Success User",
                },
            )
            assert resp.status_code in (200, 201)
            data = resp.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_success(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGIN": "true",
                "REVIEWPOINT_FEATURES": "auth:login",
            }
        )

        fresh_app = self.create_fresh_app()
        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = get_unique_email()
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
    async def test_logout_success(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
                "REVIEWPOINT_FEATURES": "auth:logout",
            }
        )

        fresh_app = self.create_fresh_app()
        import uuid

        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            email = get_unique_email()
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
    @pytest.mark.skip_if_fast_tests(
        "Refresh token tests not reliable in fast test mode"
    )
    async def test_refresh_token_success(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )

        fresh_app = self.create_fresh_app()
        import uuid

        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            email = get_unique_email()
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
    async def test_password_reset_request_success(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REQUEST_PASSWORD_RESET": "true",
                "REVIEWPOINT_FEATURES": "auth:request_password_reset",
            }
        )

        fresh_app = self.create_fresh_app()
        import uuid

        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            email = get_unique_email()
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
    async def test_logout_with_invalid_token(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
                "REVIEWPOINT_FEATURES": "auth:logout",
            }
        )

        fresh_app = self.create_fresh_app()
        import uuid

        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": get_unique_email(),
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
    async def test_logout_without_authorization_header(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_LOGOUT": "true",
                "REVIEWPOINT_FEATURES": "auth:logout",
            }
        )

        fresh_app = self.create_fresh_app()
        import uuid

        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": get_unique_email(),
                    "password": "SecurePass123!",
                    "name": "Logout No Auth",
                },
            )
            resp = await ac.post("/api/v1/auth/logout")
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_refresh_token_blacklisted(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        from src.api.deps import get_async_refresh_access_token
        from src.services.user import RefreshTokenBlacklistedError

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )

        fresh_app = self.create_fresh_app()
        transport = ASGITransport(app=fresh_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise RefreshTokenBlacklistedError("blacklisted")

        fresh_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = get_unique_email()
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
        fresh_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_refresh_token_rate_limited(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        from src.api.deps import get_async_refresh_access_token
        from src.services.user import RefreshTokenRateLimitError

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )

        fresh_app = self.create_fresh_app()

        transport = ASGITransport(app=fresh_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise RefreshTokenRateLimitError("rate limited")

        fresh_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = get_unique_email()
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
        fresh_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_refresh_token_decode_error(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        from src.api.deps import get_async_refresh_access_token
        from src.services.user import RefreshTokenError

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )

        fresh_app = self.create_fresh_app()
        transport = ASGITransport(app=fresh_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise RefreshTokenError("decode error")

        fresh_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = get_unique_email()
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
        fresh_app.dependency_overrides = {}

    @pytest.mark.asyncio
    @pytest.mark.skip_if_fast_tests(
        "Refresh token tests not reliable in fast test mode"
    )
    async def test_refresh_token_unexpected_error(self: "TestAuthEndpoints") -> None:
        from httpx import ASGITransport, AsyncClient

        from src.api.deps import get_async_refresh_access_token

        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN": "true",
                "REVIEWPOINT_FEATURES": "auth:refresh_token",
            }
        )

        fresh_app = self.create_fresh_app()

        transport = ASGITransport(app=fresh_app)

        class MockRefresh:
            async def __call__(self, session: object, token: str) -> None:
                raise Exception("fail")

        fresh_app.dependency_overrides[get_async_refresh_access_token] = (
            lambda: MockRefresh()
        )
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            import uuid

            email = get_unique_email()
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
            assert resp.status_code == 401
            resp_json = resp.json()
            assert "detail" in resp_json
            assert "invalid or expired refresh token" in resp_json["detail"].lower()
        fresh_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_password_reset_confirm_success_branch(self: "TestAuthEndpoints") -> None:
        """
        Test the password reset confirm endpoint (success branch) using only in-method imports and the test template.
        """
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_FEATURE_AUTH_RESET_PASSWORD": "true",
                "REVIEWPOINT_FEATURES": "auth:reset_password",
            }
        )

        fresh_app = self.create_fresh_app()
        # All config-dependent imports must be inside the test method
        import uuid
        from unittest.mock import AsyncMock, patch

        from httpx import ASGITransport, AsyncClient

        transport = ASGITransport(app=fresh_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            email = get_unique_email()
            password = "SecurePass123!"
            new_password = "NewSecurePass123!"
            # Register user
            await ac.post(
                "/api/v1/auth/register",
                json={"email": email, "password": password, "name": "PW Reset Success"},
            )
            # Request password reset to get a token
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

