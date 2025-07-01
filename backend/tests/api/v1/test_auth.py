"""
Authentication and authorization tests for FastAPI backend.
Uses DRY test templates for all test logic and fixture management.
"""

import pytest
from httpx import ASGITransport, AsyncClient, Response
from jose import JWTError

from src.core import security
from src.core.config import get_settings
from tests.test_templates import AuthEndpointTestTemplate, AuthUnitTestTemplate


class TestJWTUtils(AuthUnitTestTemplate):
    """
    Unit tests for JWT creation and verification utilities.
    Uses AuthUnitTestTemplate for monkeypatch and loguru_list_sink.
    """

    def test_create_and_verify_access_token(self):
        data = {"sub": "user123", "role": "admin"}
        token = security.create_access_token(data)
        assert isinstance(token, str)
        payload = security.verify_access_token(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_invalid_access_token_raises(self):
        token = security.create_access_token({"sub": "user123"})
        tampered = token + "x"
        with pytest.raises(JWTError):
            security.verify_access_token(tampered)

    def test_expired_access_token_raises(self):
        settings = get_settings()
        self.monkeypatch.setattr(settings, "jwt_expire_minutes", -1)
        token = security.create_access_token({"sub": "expired"})
        with pytest.raises(JWTError):
            security.verify_access_token(token)
        self.monkeypatch.setattr(settings, "jwt_expire_minutes", 30)

    def test_missing_secret_raises(self):
        settings = get_settings()
        self.monkeypatch.setattr(settings, "jwt_secret_key", None)
        with pytest.raises(ValueError):
            security.create_access_token({"sub": "user"})
        self.monkeypatch.setattr(settings, "jwt_secret_key", "testsecret")

    def test_jwt_with_custom_claims(self):
        data = {"sub": "user456", "role": "editor", "permissions": ["read", "write"]}
        token = security.create_access_token(data)
        payload = security.verify_access_token(token)
        assert payload["role"] == "editor"
        assert payload["permissions"] == ["read", "write"]

    def test_jwt_invalid_algorithm(self):
        settings = get_settings()
        token = security.create_access_token({"sub": "user789"})
        with pytest.raises(JWTError):
            from jose import jwt

            jwt.decode(token, str(settings.jwt_secret_key), algorithms=["HS512"])

    def test_jwt_empty_token(self):
        with pytest.raises(JWTError):
            security.verify_access_token("")


class TestAuthEndpoints(AuthEndpointTestTemplate):
    """
    Async endpoint tests for authentication routes.
    Uses AuthEndpointTestTemplate for async_session, test_app, and loguru_list_sink.
    """

    @staticmethod
    def debug_response(resp: Response, expected_status: int) -> Response:
        if resp.status_code != expected_status:
            print(f"[DEBUG] Unexpected status: {resp.status_code}")
            print(f"[DEBUG] Response text: {resp.text}")
            print(f"[DEBUG] Response headers: {resp.headers}")
        return resp

    @pytest.mark.asyncio
    async def test_register_and_login(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Register
            resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "user@example.com",
                    "password": "TestPass123!",
                    "name": "Test User",
                },
            )
            self.debug_response(resp, 201)
            self.assert_status(resp, 201)
            token = resp.json()["access_token"]
            # Login
            resp = await ac.post(
                "/api/v1/auth/login",
                json={"email": "user@example.com", "password": "TestPass123!"},
            )
            self.debug_response(resp, 200)
            self.assert_status(resp, 200)
            assert "access_token" in resp.json()
            # Invalid login
            resp = await ac.post(
                "/api/v1/auth/login",
                json={"email": "user@example.com", "password": "WrongPass!"},
            )
            self.debug_response(resp, 401)
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_me_and_logout(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Register and login
            resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "me@example.com",
                    "password": "TestPass123!",
                    "name": "Me User",
                },
            )
            token = resp.json()["access_token"]
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
    async def test_register_invalid_fields(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # Missing email
            resp = await ac.post(
                "/api/v1/auth/register",
                json={"password": "TestPass123!", "name": "No Email"},
            )
            self.assert_status(resp, 422)
            # Invalid email
            resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "notanemail",
                    "password": "TestPass123!",
                    "name": "Bad Email",
                },
            )
            self.assert_status(resp, 422)
            # Missing password
            resp = await ac.post(
                "/api/v1/auth/register",
                json={"email": "missingpass@example.com", "name": "No Pass"},
            )
            self.assert_status(resp, 422)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "dupe@example.com",
                    "password": "TestPass123!",
                    "name": "Dupe",
                },
            )
            resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "dupe@example.com",
                    "password": "TestPass123!",
                    "name": "Dupe Again",
                },
            )
            self.assert_status(resp, 400)
            assert "already exists" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_missing_fields(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.post(
                "/api/v1/auth/login",
                json={"email": "user@example.com"},
            )
            self.assert_status(resp, 422)
            resp = await ac.post(
                "/api/v1/auth/login",
                json={"password": "TestPass123!"},
            )
            self.assert_status(resp, 422)

    @pytest.mark.asyncio
    async def test_me_endpoint_no_token(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.get("/api/v1/auth/me")
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_me_endpoint_invalid_token(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer not.a.jwt.token"}
            )
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.post(
                "/api/v1/auth/logout",
                headers={"Authorization": "Bearer not.a.jwt.token"},
            )
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_password_reset_request_and_confirm(self):
        from src.services import user as user_service

        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "pwreset@example.com",
                    "password": "OldPassword123!",
                    "name": "PW Reset",
                },
            )
            # Request reset
            resp = await ac.post(
                "/api/v1/auth/request-password-reset",
                json={"email": "pwreset@example.com"},
            )
            self.assert_status(resp, 200)
            # Get token directly (simulate email)
            token = user_service.get_password_reset_token("pwreset@example.com")
            # Confirm reset
            resp = await ac.post(
                "/api/v1/auth/reset-password",
                json={"token": token, "new_password": "NewPassword456!"},
            )
            self.assert_status(resp, 200)
            # Try login with new password
            resp = await ac.post(
                "/api/v1/auth/login",
                json={"email": "pwreset@example.com", "password": "NewPassword456!"},
            )
            self.assert_status(resp, 200)
            # Try using token again (should fail)
            resp = await ac.post(
                "/api/v1/auth/reset-password",
                json={"token": token, "new_password": "AnotherPassword789!"},
            )
            self.assert_status(resp, 400)
            assert "already been used" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_request_nonexistent_email(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.post(
                "/api/v1/auth/request-password-reset",
                json={"email": "doesnotexist@example.com"},
            )
            self.assert_status(resp, 200)
            assert resp.json()["message"] == "Password reset link sent."

    @pytest.mark.asyncio
    async def test_refresh_token_expired_and_blacklisted(self):
        from datetime import datetime, timedelta

        from jose import jwt

        from src.core import security
        from src.repositories.blacklisted_token import blacklist_token

        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "refreshuser@example.com",
                    "password": "TestPass123!",
                    "name": "Refresh User",
                },
            )
            login_resp = await ac.post(
                "/api/v1/auth/login",
                json={"email": "refreshuser@example.com", "password": "TestPass123!"},
            )
            access_token = login_resp.json()["access_token"]
            payload = security.verify_access_token(access_token)
            import uuid

            # Expired refresh token
            expired_payload = {
                "sub": payload["sub"],
                "email": payload["email"],
                "jti": str(uuid.uuid4()),
                "exp": int((datetime.now(jwt.UTC) - timedelta(minutes=10)).timestamp()),
            }
            settings = get_settings()
            expired_token = jwt.encode(
                expired_payload,
                str(settings.jwt_secret_key or "dummy"),
                algorithm=settings.jwt_algorithm,
            )
            resp = await ac.post(
                "/api/v1/auth/refresh-token",
                json={"refresh_token": expired_token},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            self.assert_status(resp, 401)
            # Blacklisted refresh token
            valid_payload = {
                "sub": payload["sub"],
                "email": payload["email"],
                "jti": str(uuid.uuid4()),
                "exp": int((datetime.now(jwt.UTC) + timedelta(minutes=10)).timestamp()),
            }
            settings = get_settings()
            valid_token = jwt.encode(
                valid_payload,
                str(settings.jwt_secret_key or "dummy"),
                algorithm=settings.jwt_algorithm,
            )
            await blacklist_token(
                self.async_session,
                valid_payload["jti"],
                datetime.fromtimestamp(valid_payload["exp"]),
            )
            resp = await ac.post(
                "/api/v1/auth/refresh-token",
                json={"refresh_token": valid_token},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            self.assert_status(resp, 401)

    @pytest.mark.asyncio
    async def test_auth_disabled_allows_access(self):
        settings = get_settings()
        self.monkeypatch.setattr(settings, "auth_enabled", False)
        from src.api.deps import get_current_user

        user = await get_current_user(token="irrelevant", session=self.async_session)
        assert user.email == "dev@example.com"
        assert user.is_active
        self.monkeypatch.setattr(settings, "auth_enabled", True)


class TestAuthFeatureFlags(AuthEndpointTestTemplate):
    def test_register_feature_disabled(self):
        self.override_env_vars({"REVIEWPOINT_FEATURE_AUTH_REGISTER": "false"})
        transport = ASGITransport(app=self.test_app)

        async def run():
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                headers={"X-API-Key": "testkey"},
            ) as ac:
                resp = await ac.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "flag@example.com",
                        "password": "pw123456",
                        "name": "Flag",
                    },
                )
                self.assert_status(resp, (404, 403, 501))

        import asyncio

        asyncio.run(run())

    def test_login_feature_disabled(self):
        self.override_env_vars({"REVIEWPOINT_FEATURE_AUTH_LOGIN": "false"})
        transport = ASGITransport(app=self.test_app)

        async def run():
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                headers={"X-API-Key": "testkey"},
            ) as ac:
                resp = await ac.post(
                    "/api/v1/auth/login",
                    json={"email": "flag@example.com", "password": "pw123456"},
                )
                self.assert_status(resp, (404, 403, 501))

        import asyncio

        asyncio.run(run())

    def test_api_key_disabled(self):
        self.override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        transport = ASGITransport(app=self.test_app)

        async def run():
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "flag@example.com",
                        "password": "pw123456",
                        "name": "Flag",
                    },
                )
                self.assert_status(resp, (200, 401, 403))

        import asyncio

        asyncio.run(run())

    def test_api_key_wrong(self):
        self.override_env_vars({"REVIEWPOINT_API_KEY": "nottherightkey"})
        transport = ASGITransport(app=self.test_app)

        async def run():
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                headers={"X-API-Key": "wrongkey"},
            ) as ac:
                resp = await ac.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "flag@example.com",
                        "password": "pw123456",
                        "name": "Flag",
                    },
                )
                self.assert_status(resp, (401, 403))

        import asyncio

        asyncio.run(run())
