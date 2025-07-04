# Tests for users/exports.py (export endpoints) - Async version with performance optimizations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from tests.test_templates import ExportEndpointTestTemplate

EXPORT_ENDPOINT = "/api/v1/users/export"
EXPORT_ALIVE_ENDPOINT = "/api/v1/users/export-alive"
EXPORT_FULL_ENDPOINT = "/api/v1/users/export-full"
EXPORT_SIMPLE_ENDPOINT = "/api/v1/users/export-simple"


@pytest_asyncio.fixture
async def async_client(test_app):
    """Shared async client fixture for all tests."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": "testkey"},
    ) as ac:
        yield ac


class TestUserExportsAsync(ExportEndpointTestTemplate):
    @pytest.mark.asyncio
    async def test_export_users_csv(
        self, async_client: AsyncClient, override_env_vars, monkeypatch
    ):
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function at the point where it's imported in the exports module
        async def mock_list_users(session):
            # Return mock user data
            from src.models.user import User

            mock_users = [
                User(id=1, email="test1@example.com", name="Test User 1"),
                User(id=2, email="test2@example.com", name="Test User 2"),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # With auth disabled, we can use any token - the security module will return a default admin payload
        headers = {"Authorization": "Bearer any_token", "X-API-Key": "testkey"}

        resp = await async_client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name" in resp.text

    @pytest.mark.asyncio
    async def test_users_export_alive(self, async_client: AsyncClient):
        # Use simple API key auth for alive endpoint
        headers = {"X-API-Key": "testkey"}
        resp = await async_client.get(EXPORT_ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "users export alive"

    @pytest.mark.asyncio
    async def test_export_users_full_csv(
        self, async_client: AsyncClient, override_env_vars, monkeypatch
    ):
        # Disable authentication to bypass JWT validation and database lookup issues
        override_env_vars({"REVIEWPOINT_AUTH_ENABLED": "false"})

        # Clear settings cache to pick up new environment variables
        from src.core.config import get_settings

        get_settings.cache_clear()

        # Mock the list_users function at the point where it's imported in the exports module
        async def mock_list_users(session):
            # Return mock user data with timestamps
            from datetime import datetime

            from src.models.user import User

            mock_users = [
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
        headers = {"Authorization": "Bearer any_token", "X-API-Key": "testkey"}

        resp = await async_client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name,created_at,updated_at" in resp.text

    @pytest.mark.asyncio
    async def test_export_users_csv_unauthenticated(
        self, async_client: AsyncClient, override_env_vars, monkeypatch
    ):
        # Disable API key authentication to test unauthenticated access
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})

        # Mock the list_users function to avoid database issues
        async def mock_list_users(session):
            from src.models.user import User

            mock_users = [
                User(id=1, email="test@example.com", name="Test User"),
            ]
            return mock_users, len(mock_users)

        monkeypatch.setattr("src.api.v1.users.exports.list_users", mock_list_users)

        # Test without any authentication headers
        resp = await async_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name" in resp.text


class TestUserExportsFeatureFlags:
    """Feature flags and test patterns - keeping original structure for reference."""

    @pytest.mark.asyncio
    async def test_feature_flags_disable_export(self):
        """Test that feature flags can disable user exports."""
        # TODO: Implement feature flag tests for exports
        pass

    @pytest.mark.asyncio
    async def test_feature_flags_export_permissions(self):
        """Test export permissions with feature flags."""
        # TODO: Implement permission tests for exports
        pass
