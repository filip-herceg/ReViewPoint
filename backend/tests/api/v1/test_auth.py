"""
Authentication and authorization tests for FastAPI backend.
Uses DRY test templates for all test logic and fixture management.
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping, MutableMapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Final, Literal, TypedDict, Union

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response
from jose import JWTError, jwt
from pytest import MonkeyPatch
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import security
from src.core.config import Settings, get_settings
from src.core.security import JWTPayload as SecurityJWTPayload
from src.models.user import User
from tests.test_templates import AuthEndpointTestTemplate, AuthUnitTestTemplate
from tests.test_data_generators import AuthTestDataGenerator

# TypedDict definitions for structured data
class RequiredJWTPayload(TypedDict):
    """Required JWT payload fields."""
    sub: str
    exp: int

class BaseJWTPayload(RequiredJWTPayload, total=False):
    """Base JWT payload structure with optional fields."""
    email: str
    role: str
    permissions: Sequence[str]
    jti: str

class CompleteJWTPayload(RequiredJWTPayload):
    """Complete JWT payload with all common fields."""
    email: str
    role: str
    permissions: Sequence[str]
    jti: str

class RegisterRequest(TypedDict):
    """Registration request structure."""
    email: str
    password: str
    name: str

class LoginRequest(TypedDict):
    """Login request structure."""
    email: str
    password: str

class PasswordResetRequest(TypedDict):
    """Password reset request structure."""
    email: str

class PasswordResetConfirm(TypedDict):
    """Password reset confirmation structure."""
    token: str
    new_password: str

class RefreshTokenRequest(TypedDict):
    """Refresh token request structure."""
    refresh_token: str

# Type aliases for better readability
TokenData = Mapping[str, str | int | bool]  # Match security module signature
OverrideEnvVarsFixture = Callable[[Mapping[str, str]], None]
StatusCodeUnion = Union[int, tuple[int, ...]]
JsonData = Mapping[str, object]
JWTPayload = SecurityJWTPayload  # Use the actual type from security module


class TestJWTUtils(AuthUnitTestTemplate):
    """
    Unit tests for JWT creation and verification utilities.
    Uses AuthUnitTestTemplate for monkeypatch and loguru_list_sink.
    """

    def test_create_and_verify_access_token(self) -> None:
        """Test creating and verifying a valid access token."""
        data: TokenData = {"sub": "user123", "role": "admin"}
        token: str = security.create_access_token(data)
        assert isinstance(token, str)
        payload: JWTPayload = security.verify_access_token(token)
        assert payload.get("sub") == "user123"
        assert payload.get("role") == "admin"
        assert "exp" in payload

    def test_invalid_access_token_raises(self) -> None:
        """Test that invalid tokens raise JWTError."""
        token: str = security.create_access_token({"sub": "user123"})
        tampered: str = token + "x"
        with pytest.raises(JWTError):
            security.verify_access_token(tampered)

    def test_expired_access_token_raises(self) -> None:
        """Test that expired tokens raise JWTError."""
        settings: Settings = get_settings()
        self.monkeypatch.setattr(settings, "jwt_expire_minutes", -1)
        token: str = security.create_access_token({"sub": "expired"})
        with pytest.raises(JWTError):
            security.verify_access_token(token)
        self.monkeypatch.setattr(settings, "jwt_expire_minutes", 30)

    def test_missing_secret_raises(self) -> None:
        """Test that missing secret key raises ValueError."""
        settings: Settings = get_settings()
        self.monkeypatch.setattr(settings, "jwt_secret_key", None)
        with pytest.raises(ValueError):
            security.create_access_token({"sub": "user"})
        self.monkeypatch.setattr(settings, "jwt_secret_key", "testsecret")

    def test_jwt_with_custom_claims(self) -> None:
        """Test JWT with custom claims."""
        data: TokenData = {
            "sub": "user456", 
            "role": "editor", 
            "permissions": "read,write"  # Store as comma-separated string
        }
        token: str = security.create_access_token(data)
        payload: JWTPayload = security.verify_access_token(token)
        assert payload.get("role") == "editor"
        assert payload.get("permissions") == "read,write"

    def test_jwt_invalid_algorithm(self) -> None:
        """Test JWT with invalid algorithm raises JWTError."""
        settings: Settings = get_settings()
        token: str = security.create_access_token({"sub": "user789"})
        with pytest.raises(JWTError):
            jwt.decode(token, str(settings.jwt_secret_key), algorithms=["HS512"])

    def test_jwt_empty_token(self) -> None:
        """Test that empty token raises JWTError."""
        with pytest.raises(JWTError):
            security.verify_access_token("")


class TestAuthEndpoints(AuthEndpointTestTemplate):
    """
    Async endpoint tests for authentication routes.
    Uses AuthEndpointTestTemplate for async_session, test_app, and loguru_list_sink.
    """

    @staticmethod
    def debug_response(resp: Response, expected_status: int) -> Response:
        """Debug helper to log response details when status doesn't match expected."""
        if resp.status_code != expected_status:
            pass
        return resp

    @pytest.mark.asyncio
    async def test_register_and_login(self) -> None:
        """Test user registration and login flow."""
        # Generate unique test data for isolation
        test_data = AuthTestDataGenerator('test_register_and_login')
        test_user = test_data.get_registration_user()
        
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Register
            register_data = test_user.to_register_dict()
            resp: Response = await ac.post(
                "/api/v1/auth/register",
                json=register_data,
            )
            self.debug_response(resp, 201)
            self.assert_status(resp, 201)
            token: str = resp.json()["access_token"]
            # Login
            login_data = test_user.to_login_dict()
            resp = await ac.post(
                "/api/v1/auth/login",
                json=login_data,
            )
            self.debug_response(resp, 200)
            self.assert_status(resp, 200)
            assert "access_token" in resp.json()
            # Invalid login
            invalid_login_data: LoginRequest = {"email": test_user.email, "password": "WrongPass!"}
            resp = await ac.post(
                "/api/v1/auth/login",
                json=invalid_login_data,
            )
            self.debug_response(resp, 401)
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_me_and_logout(self) -> None:
        """Test /me endpoint and logout functionality."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Register and login
            register_data: RegisterRequest = {
                "email": "me@example.com",
                "password": "TestPass123!",
                "name": "Me User",
            }
            resp: Response = await ac.post(
                "/api/v1/auth/register",
                json=register_data,
            )
            token: str = resp.json()["access_token"]
            # /me endpoint
            resp = await ac.get(
                "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
            )
            self.debug_response(resp, 200)
            self.assert_status(resp, 200)
            assert resp.json()["email"] == "me@example.com"
            # Logout
            resp = await ac.post(
                "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
            )
            self.debug_response(resp, 200)
            self.assert_status(resp, 200)
            # Token should now be invalid
            resp = await ac.get(
                "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
            )
            self.debug_response(resp, 401)
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_register_invalid_fields(self) -> None:
        """Test registration with invalid fields."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Missing email
            incomplete_data: Mapping[str, str] = {"password": "TestPass123!", "name": "No Email"}
            resp: Response = await ac.post(
                "/api/v1/auth/register",
                json=incomplete_data,
            )
            self.assert_status(resp, 422)
            # Invalid email
            invalid_email_data: Mapping[str, str] = {
                "email": "notanemail",
                "password": "TestPass123!",
                "name": "Bad Email",
            }
            resp = await ac.post(
                "/api/v1/auth/register",
                json=invalid_email_data,
            )
            self.assert_status(resp, 422)
            # Missing password
            missing_password_data: Mapping[str, str] = {"email": "missingpass@example.com", "name": "No Pass"}
            resp = await ac.post(
                "/api/v1/auth/register",
                json=missing_password_data,
            )
            self.assert_status(resp, 422)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self) -> None:
        """Test registration with duplicate email."""
        # Generate unique test data for isolation
        test_data = AuthTestDataGenerator('test_register_duplicate_email')
        test_user = test_data.get_registration_user()
        
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            first_registration = test_user.to_register_dict()
            await ac.post(
                "/api/v1/auth/register",
                json=first_registration,
            )
            # Try to register again with same email (but different name)
            duplicate_registration = {
                "email": test_user.email,
                "password": test_user.password,
                "name": "Dupe Again",
            }
            resp: Response = await ac.post(
                "/api/v1/auth/register",
                json=duplicate_registration,
            )
            self.assert_status(resp, 400)
            assert "already exists" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_missing_fields(self) -> None:
        """Test login with missing fields."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            missing_password: Mapping[str, str] = {"email": "user@example.com"}
            resp: Response = await ac.post(
                "/api/v1/auth/login",
                json=missing_password,
            )
            self.assert_status(resp, 422)
            missing_email: Mapping[str, str] = {"password": "TestPass123!"}
            resp = await ac.post(
                "/api/v1/auth/login",
                json=missing_email,
            )
            self.assert_status(resp, 422)

    @pytest.mark.asyncio
    async def test_me_endpoint_no_token(self) -> None:
        """Test /me endpoint without token."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp: Response = await ac.get("/api/v1/auth/me")
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_me_endpoint_invalid_token(self) -> None:
        """Test /me endpoint with invalid token."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp: Response = await ac.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer not.a.jwt.token"}
            )
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self) -> None:
        """Test logout with invalid token."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp: Response = await ac.post(
                "/api/v1/auth/logout",
                headers={"Authorization": "Bearer not.a.jwt.token"},
            )
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_password_reset_request_and_confirm(self) -> None:
        """Test password reset request and confirmation flow."""
        from src.services import user as user_service

        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Register user first
            register_data: RegisterRequest = {
                "email": "pwreset@example.com",
                "password": "OldPassword123!",
                "name": "PW Reset",
            }
            await ac.post(
                "/api/v1/auth/register",
                json=register_data,
            )
            # Request reset
            reset_request: PasswordResetRequest = {"email": "pwreset@example.com"}
            resp: Response = await ac.post(
                "/api/v1/auth/request-password-reset",
                json=reset_request,
            )
            self.assert_status(resp, 200)
            # Get token directly (simulate email)
            token: str = user_service.get_password_reset_token("pwreset@example.com")
            # Confirm reset
            reset_confirm: PasswordResetConfirm = {"token": token, "new_password": "NewPassword456!"}
            resp = await ac.post(
                "/api/v1/auth/reset-password",
                json=reset_confirm,
            )
            self.assert_status(resp, 200)
            # Try login with new password
            new_login: LoginRequest = {"email": "pwreset@example.com", "password": "NewPassword456!"}
            resp = await ac.post(
                "/api/v1/auth/login",
                json=new_login,
            )
            self.assert_status(resp, 200)
            # Try using token again (should fail)
            repeat_reset: PasswordResetConfirm = {"token": token, "new_password": "AnotherPassword789!"}
            resp = await ac.post(
                "/api/v1/auth/reset-password",
                json=repeat_reset,
            )
            self.assert_status(resp, 400)
            assert "already been used" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_request_nonexistent_email(self) -> None:
        """Test password reset request for nonexistent email."""
        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            nonexistent_request: PasswordResetRequest = {"email": "doesnotexist@example.com"}
            resp: Response = await ac.post(
                "/api/v1/auth/request-password-reset",
                json=nonexistent_request,
            )
            self.assert_status(resp, 200)
            assert resp.json()["message"] == "Password reset link sent."

    @pytest.mark.asyncio
    async def test_refresh_token_expired_and_blacklisted(self) -> None:
        """Test refresh token with expired and blacklisted tokens."""
        from src.repositories.blacklisted_token import blacklist_token

        transport: ASGITransport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Register and login
            register_data: RegisterRequest = {
                "email": "refreshuser@example.com",
                "password": "TestPass123!",
                "name": "Refresh User",
            }
            await ac.post(
                "/api/v1/auth/register",
                json=register_data,
            )
            login_data: LoginRequest = {"email": "refreshuser@example.com", "password": "TestPass123!"}
            login_resp: Response = await ac.post(
                "/api/v1/auth/login",
                json=login_data,
            )
            access_token: str = login_resp.json()["access_token"]
            payload: JWTPayload = security.verify_access_token(access_token)

            # Expired refresh token
            expired_payload_dict: MutableMapping[str, str | int] = {
                "sub": payload.get("sub", "unknown_user"),
                "email": "refreshuser@example.com",  # Use known email
                "jti": str(uuid.uuid4()),
                "exp": int((datetime.now(jwt.UTC) - timedelta(minutes=10)).timestamp()),
            }
            settings: Settings = get_settings()
            expired_token: str = jwt.encode(
                expired_payload_dict,
                str(settings.jwt_secret_key or "dummy"),
                algorithm=settings.jwt_algorithm,
            )
            refresh_request: RefreshTokenRequest = {"refresh_token": expired_token}
            resp: Response = await ac.post(
                "/api/v1/auth/refresh-token",
                json=refresh_request,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            self.assert_status(resp, 401)
            # Blacklisted refresh token
            valid_payload_dict: MutableMapping[str, str | int] = {
                "sub": payload.get("sub", "unknown_user"),
                "email": "refreshuser@example.com",  # Use known email
                "jti": str(uuid.uuid4()),
                "exp": int((datetime.now(jwt.UTC) + timedelta(minutes=10)).timestamp()),
            }
            settings = get_settings()
            valid_token: str = jwt.encode(
                valid_payload_dict,
                str(settings.jwt_secret_key or "dummy"),
                algorithm=settings.jwt_algorithm,
            )
            await blacklist_token(
                self.async_session,
                str(valid_payload_dict["jti"]),
                datetime.fromtimestamp(float(valid_payload_dict["exp"])),
            )
            blacklisted_request: RefreshTokenRequest = {"refresh_token": valid_token}
            resp = await ac.post(
                "/api/v1/auth/refresh-token",
                json=blacklisted_request,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_auth_disabled_allows_access(self) -> None:
        """Test that auth disabled allows access."""
        from src.api.deps import get_current_user
        from src.models.user import User

        settings: Settings = get_settings()
        self.monkeypatch.setattr(settings, "auth_enabled", False)
        
        user: User = await get_current_user(token="irrelevant", session=self.async_session)
        assert user.email == "dev@example.com"
        assert user.is_active
        self.monkeypatch.setattr(settings, "auth_enabled", True)


class TestAuthFeatureFlags(AuthEndpointTestTemplate):
    """Test authentication feature flag behaviors."""

    def test_register_feature_disabled(self) -> None:
        """Test registration when register feature is disabled."""
        self.override_env_vars({"REVIEWPOINT_FEATURE_AUTH_REGISTER": "false"})
        transport: ASGITransport = ASGITransport(app=self.test_app)

        async def run() -> None:
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                headers={"X-API-Key": "testkey"},
            ) as ac:
                register_data: RegisterRequest = {
                    "email": "flag@example.com",
                    "password": "pw123456",
                    "name": "Flag",
                }
                resp: Response = await ac.post(
                    "/api/v1/auth/register",
                    json=register_data,
                )
                self.assert_status(resp, (404, 403, 501))

        asyncio.run(run())

    def test_login_feature_disabled(self) -> None:
        """Test login when login feature is disabled."""
        self.override_env_vars({"REVIEWPOINT_FEATURE_AUTH_LOGIN": "false"})
        transport: ASGITransport = ASGITransport(app=self.test_app)

        async def run() -> None:
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                headers={"X-API-Key": "testkey"},
            ) as ac:
                login_data: LoginRequest = {"email": "flag@example.com", "password": "pw123456"}
                resp: Response = await ac.post(
                    "/api/v1/auth/login",
                    json=login_data,
                )
                self.assert_status(resp, (404, 403, 501))

        asyncio.run(run())

    @pytest.mark.asyncio
    async def test_api_key_disabled(self) -> None:
        """Test API key disabled behavior."""
        self.override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        transport: ASGITransport = ASGITransport(app=self.test_app)

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            register_data: RegisterRequest = {
                "email": "flag@example.com",
                "password": "pw123456",
                "name": "Flag",
            }
            resp: Response = await ac.post(
                "/api/v1/auth/register",
                json=register_data,
            )
            self.assert_status(
                resp, (201,)
            )  # Registration should succeed when API keys are disabled

    def test_api_key_wrong(self) -> None:
        """Test wrong API key behavior."""
        # Override environment variables for this test
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY": "nottherightkey",
                "REVIEWPOINT_API_KEY_ENABLED": "true",
            }
        )

        # Clear settings cache to pick up new environment variables
        from src.core.config import clear_settings_cache

        clear_settings_cache()

        transport: ASGITransport = ASGITransport(app=self.test_app)

        async def run() -> None:
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                headers={"X-API-Key": "wrongkey"},
            ) as ac:
                register_data: RegisterRequest = {
                    "email": "flag@example.com",
                    "password": "pw123456",
                    "name": "Flag",
                }
                resp: Response = await ac.post(
                    "/api/v1/auth/register",
                    json=register_data,
                )
                self.assert_status(resp, (401, 403))

        asyncio.run(run())
