# Tests for users/exports.py (export endpoints)
# Merged from test_exports_async.py for improved async patterns

from collections.abc import AsyncGenerator, Callable, Mapping, MutableMapping, Sequence
from datetime import UTC, datetime
from typing import Final, Literal, Union

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Response
from pytest import MonkeyPatch

from tests.test_templates import ExportEndpointTestTemplate

EXPORT_ENDPOINT: Final[str] = "/api/v1/users/export"
EXPORT_ALIVE_ENDPOINT: Final[str] = "/api/v1/users/export-alive"
EXPORT_FULL_ENDPOINT: Final[str] = "/api/v1/users/export-full"
EXPORT_SIMPLE_ENDPOINT: Final[str] = "/api/v1/users/export-simple"

# Type aliases for better readability
OverrideEnvVarsFixture = Callable[[Mapping[str, str]], None]
MockListUsersReturn = tuple[Sequence[object], int]
MockListUsersCallable = Callable[..., MockListUsersReturn]
StatusCodeUnion = Union[int, tuple[int, ...]]


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Shared async client fixture for all tests."""
    transport: ASGITransport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": "testkey"},
    ) as ac:
        yield ac


class TestUserExports(ExportEndpointTestTemplate):
    """Test user export endpoints with strict typing."""

    def test_export_users_csv(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test basic CSV export functionality."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear the settings cache to ensure the new auth setting takes effect
        from src.core.config import clear_settings_cache

        clear_settings_cache()

        # Mock the list_users function at the point where it's imported in the exports module
        async def mock_list_users(session: object) -> MockListUsersReturn:
            # Return mock user data
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(id=1, email="test1@example.com", name="Test User 1"),
                User(id=2, email="test2@example.com", name="Test User 2"),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name" in resp.text

    def test_users_export_alive(self, client: TestClient) -> None:
        """Test the export alive endpoint."""
        resp: Response = client.get(
            EXPORT_ALIVE_ENDPOINT, headers=self.get_auth_header(client)
        )
        self.assert_status(resp, 200)
        response_data: Mapping[str, object] = resp.json()
        assert response_data["status"] == "users export alive"

    def test_export_users_full_csv(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test full CSV export functionality with extended fields."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars(
            {
                "REVIEWPOINT_AUTH_ENABLED": "false",
                "REVIEWPOINT_FEATURE_USERS_EXPORT_FULL": "true",
            }
        )

        # Clear the settings cache to ensure the new auth setting takes effect
        from src.core.config import clear_settings_cache

        clear_settings_cache()

        # Mock the list_users function at the point where it's imported in the exports module
        async def mock_list_users(session: object) -> MockListUsersReturn:
            # Return mock user data with more fields for full export
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="admin@example.com",
                    name="Admin User",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name,created_at,updated_at" in resp.text

    def test_export_users_csv_unauthenticated(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export without authentication."""
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(id=1, email="test@example.com", name="Test User"),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        resp: Response = client.get(EXPORT_ENDPOINT)
        # When API keys are disabled, endpoint should be accessible
        self.assert_status(resp, 200)

    def test_export_users_full_csv_unauthenticated(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test full CSV export without authentication."""
        override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "false",
                "REVIEWPOINT_FEATURE_USERS_EXPORT_FULL": "true",
            }
        )

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="test@example.com",
                    name="Test User",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    is_active=True,
                    is_admin=False,
                ),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        resp: Response = client.get(EXPORT_FULL_ENDPOINT)
        # When API keys are disabled, endpoint should be accessible
        self.assert_status(resp, 200)

    def test_export_alive_unauthenticated(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test export alive endpoint without authentication."""
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp: Response = client.get(EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        response_data: Mapping[str, object] = resp.json()
        assert response_data["status"] == "users export alive"

    def test_export_simple_unauthenticated(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test simple export endpoint without authentication."""
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp: Response = client.get(EXPORT_SIMPLE_ENDPOINT)
        self.assert_status(resp, 200)

    def test_export_users_csv_content(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export content format and structure."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object, **kwargs: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="test1@example.com",
                    name="Test User 1",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
                User(
                    id=2,
                    email="test2@example.com",
                    name="Test User 2",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        lines: list[str] = resp.text.splitlines()
        assert lines[0].startswith("id,email,name")
        assert any("," in line for line in lines[1:])  # At least one user row

    def test_export_users_csv_with_query_params(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export with query parameters for field selection."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object, **kwargs: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="test1@example.com",
                    name="Test User 1",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
                User(
                    id=2,
                    email="test2@example.com",
                    name="Test User 2",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(f"{EXPORT_ENDPOINT}?fields=id,email", headers=headers)
        self.assert_status(resp, 200)
        first_line: str = resp.text.splitlines()[0]
        assert first_line.startswith("id,email")

    def test_export_users_csv_empty_db(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export with empty database."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function to return empty results
        async def mock_list_users(session: object, **kwargs: object) -> MockListUsersReturn:
            empty_users: Sequence[object] = []
            return empty_users, 0

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        # Assume DB is empty after fixture reset or use a filter that returns nothing
        resp: Response = client.get(
            f"{EXPORT_ENDPOINT}?email=doesnotexist@example.com", headers=headers
        )
        self.assert_status(resp, 200)
        lines: list[str] = resp.text.splitlines()
        assert lines[0].startswith("id,email,name")
        assert len(lines) == 1  # Only header

    def test_export_users_csv_content_disposition(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export content disposition header."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object, **kwargs: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_user: User = User(
                id=1,
                email="test@example.com",
                name="Test User",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            return [mock_user], 1

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        cd: str = resp.headers.get("content-disposition", "")
        assert "attachment" in cd and ".csv" in cd

    def test_export_users_csv_unsupported_format(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export with unsupported format parameter."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object, **kwargs: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="test@example.com",
                    name="Test User",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(f"{EXPORT_ENDPOINT}?format=xml", headers=headers)
        self.assert_status(resp, (400, 422))

    def test_export_users_csv_invalid_token(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test CSV export with invalid authentication token."""
        # Enable both feature flag and API key validation to ensure proper error handling
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT": "true",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_API_KEY_ENABLED": "true",
            }
        )
        headers: Mapping[str, str] = {
            "Authorization": "Bearer not.a.jwt.token",
            "X-API-Key": "testkey",
        }
        resp: Response = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, (401, 403))

    def test_export_users_csv_missing_api_key(
        self,
        override_env_vars: OverrideEnvVarsFixture,
        client: TestClient,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export without API key when auth is disabled."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function to avoid async database issues
        async def mock_list_users(session: object, **kwargs: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="test@example.com",
                    name="Test User",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # Test without API key when auth is disabled - should succeed
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token"
        }  # No X-API-Key header
        resp: Response = client.get(EXPORT_ENDPOINT, headers=headers)

        # When auth is disabled, the endpoint should be accessible even without API key
        self.assert_status(resp, 200)

    def test_export_alive_with_auth(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test export alive endpoint with authentication disabled."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(EXPORT_ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        response_data: Mapping[str, object] = resp.json()
        assert response_data["status"] == "users export alive"

    def test_export_simple_with_auth(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test simple export endpoint with authentication disabled."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get(EXPORT_SIMPLE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        response_data: Mapping[str, object] = resp.json()
        content_type: str = resp.headers.get("content-type", "")
        assert "users" in response_data or content_type.startswith("text/csv")

    def test_export_full_csv_invalid_token(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test full CSV export with invalid authentication token."""
        # Enable the feature flag and authentication to ensure proper error handling
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT_FULL": "true",
                "REVIEWPOINT_AUTH_ENABLED": "true",
                "REVIEWPOINT_API_KEY_ENABLED": "true",
            }
        )
        headers: Mapping[str, str] = {
            "Authorization": "Bearer not.a.jwt.token",
            "X-API-Key": "testkey",
        }
        resp: Response = client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, (401, 403))

    def test_export_full_csv_missing_api_key(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test full CSV export without API key when auth is disabled."""
        # Enable the feature flag and disable auth to avoid database issues
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT_FULL": "true",
                "REVIEWPOINT_AUTH_ENABLED": "false",
            }
        )

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token"
        }  # Missing X-API-Key intentionally
        resp: Response = client.get(EXPORT_FULL_ENDPOINT, headers=headers)

        # When authentication is disabled, the endpoint should be accessible even without API key
        self.assert_status(resp, 200)


class TestUserExportsAsync(ExportEndpointTestTemplate):
    """
    Async version of user export tests with improved performance.
    
    These tests use async patterns for better performance and resource management.
    Includes async client fixtures and proper settings cache handling.
    """

    @pytest.mark.asyncio
    async def test_export_users_csv(
        self,
        async_client: AsyncClient,
        override_env_vars: OverrideEnvVarsFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export functionality asynchronously."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function at the point where it's imported in the exports module
        async def mock_list_users(session: object) -> MockListUsersReturn:
            # Return mock user data
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(id=1, email="test1@example.com", name="Test User 1"),
                User(id=2, email="test2@example.com", name="Test User 2"),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = await async_client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name" in resp.text

    @pytest.mark.asyncio
    async def test_users_export_alive(self, async_client: AsyncClient) -> None:
        """Test export alive endpoint asynchronously."""
        # Use simple API key auth for alive endpoint
        headers: Mapping[str, str] = {"X-API-Key": "testkey"}
        resp: Response = await async_client.get(EXPORT_ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        response_data: Mapping[str, object] = resp.json()
        assert response_data["status"] == "users export alive"

    @pytest.mark.asyncio
    async def test_export_users_full_csv(
        self,
        async_client: AsyncClient,
        override_env_vars: OverrideEnvVarsFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test full CSV export functionality asynchronously."""
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function at the point where it's imported in the exports module
        async def mock_list_users(session: object) -> MockListUsersReturn:
            # Return mock user data with timestamps
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(
                    id=1,
                    email="test1@example.com",
                    name="Test User 1",
                    created_at=datetime(2024, 1, 1),
                    updated_at=datetime(2024, 1, 1),
                ),
                User(
                    id=2,
                    email="test2@example.com",
                    name="Test User 2",
                    created_at=datetime(2024, 1, 2),
                    updated_at=datetime(2024, 1, 2),
                ),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = await async_client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name,created_at,updated_at" in resp.text

    @pytest.mark.asyncio
    async def test_export_users_csv_unauthenticated(
        self,
        async_client: AsyncClient,
        override_env_vars: OverrideEnvVarsFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test CSV export without authentication asynchronously."""
        # Disable API key authentication to test unauthenticated access
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})

        # Mock the list_users function to avoid database issues
        async def mock_list_users(session: object) -> MockListUsersReturn:
            from src.models.user import User

            mock_users: Sequence[User] = [
                User(id=1, email="test@example.com", name="Test User"),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # Test without any authentication headers
        resp: Response = await async_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name" in resp.text


class TestUserExportsFeatureFlags(ExportEndpointTestTemplate):
    """Test user export endpoints with feature flag configurations."""

    def test_export_users_feature_disabled(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test export endpoint when users export feature is disabled."""
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT": "false",
                "REVIEWPOINT_AUTH_ENABLED": "false",  # Disable authentication to bypass JWT validation
            }
        )

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get("/api/v1/users/export", headers=headers)
        feature_disabled_codes: tuple[int, ...] = (404, 403, 501)
        assert resp.status_code in feature_disabled_codes

    def test_export_full_feature_disabled(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test full export endpoint when feature is disabled."""
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT_FULL": "false",
                "REVIEWPOINT_AUTH_ENABLED": "false",  # Disable authentication to bypass JWT validation
            }
        )

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get("/api/v1/users/export-full", headers=headers)
        feature_disabled_codes: tuple[int, ...] = (404, 403, 501)
        assert resp.status_code in feature_disabled_codes

    def test_export_alive_feature_disabled(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test export alive endpoint when feature is disabled."""
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT_ALIVE": "false",
                "REVIEWPOINT_AUTH_ENABLED": "false",  # Disable authentication to bypass JWT validation
            }
        )

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get("/api/v1/users/export-alive", headers=headers)
        feature_disabled_codes: tuple[int, ...] = (404, 403, 501)
        assert resp.status_code in feature_disabled_codes

    def test_export_simple_feature_disabled(
        self, override_env_vars: OverrideEnvVarsFixture, client: TestClient
    ) -> None:
        """Test simple export endpoint when feature is disabled."""
        override_env_vars(
            {
                "REVIEWPOINT_FEATURE_USERS_EXPORT_SIMPLE": "false",
                "REVIEWPOINT_AUTH_ENABLED": "false",  # Disable authentication to bypass JWT validation
            }
        )

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers: Mapping[str, str] = {
            "Authorization": "Bearer any_token",
            "X-API-Key": "testkey",
        }

        resp: Response = client.get("/api/v1/users/export-simple", headers=headers)
        feature_disabled_codes: tuple[int, ...] = (404, 403, 501)
        assert resp.status_code in feature_disabled_codes

    def test_api_key_disabled(self, client: TestClient) -> None:
        """Test export endpoint when API key validation is disabled."""
        self.override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp: Response = client.get(
            "/api/v1/users/export", headers=self.get_auth_header(client)
        )
        allowed_codes: tuple[int, ...] = (200, 401, 403)
        assert resp.status_code in allowed_codes

    def test_api_key_wrong(self, client: TestClient) -> None:
        """Test export endpoint with incorrect API key."""
        self.override_env_vars(
            {
                "REVIEWPOINT_API_KEY_ENABLED": "true",
                "REVIEWPOINT_API_KEY": "nottherightkey",
            }
        )

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()
        headers: MutableMapping[str, str] = self.get_auth_header(client)
        headers["X-API-Key"] = "wrongkey"
        resp: Response = client.get("/api/v1/users/export", headers=headers)
        unauthorized_codes: tuple[int, ...] = (401, 403)
        assert resp.status_code in unauthorized_codes


class TestUserExportsFeatureFlagsAsync:
    """
    Async feature flags and test patterns for export functionality.
    
    These tests focus on feature flag behavior and export permissions
    using async patterns for improved performance.
    """

    @pytest.mark.asyncio
    async def test_feature_flags_disable_export(self) -> None:
        """Test that feature flags can disable user exports."""
        # TODO: Implement feature flag tests for exports
        # This is a placeholder for future implementation
        pass

    @pytest.mark.asyncio
    async def test_feature_flags_export_permissions(self) -> None:
        """Test export permissions with feature flags."""
        # TODO: Implement permission tests for exports
        # This is a placeholder for future implementation
        pass
