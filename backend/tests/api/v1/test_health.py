"""Health endpoint tests (GET/POST/PUT/DELETE, auth/no-auth, response structure).
Uses HealthEndpointTestTemplate for maintainability and health-specific helpers.

Note: Do NOT use BaseAPITest directly for health checks—use HealthEndpointTestTemplate instead.
"""

import os
from collections.abc import Callable, Mapping, MutableMapping
from typing import Final, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from pytest import FixtureRequest

from tests.test_templates import HealthEndpointTestTemplate

# Constants with Final typing
HEALTH_ENDPOINT: Final[str] = "/api/v1/health"
CONTENT_TYPE_JSON: Final[str] = "application/json"
BEARER_INVALID_TOKEN: Final[str] = "Bearer not.a.jwt"

# Type aliases for better readability
StatusCodeUnion = int | tuple[int, ...]
HeadersDict = MutableMapping[str, str]
EnvVarsDict = Mapping[str, str]
HTTPMethod = Callable[..., Response]


class TestHealthEndpoint(HealthEndpointTestTemplate):
    """Test class for health endpoint functionality.
    Tests various HTTP methods, auth scenarios, and response validation.
    """

    def _safe_request_typed(
        self,
        method: HTTPMethod,
        *args: object,
        **kwargs: object,
    ) -> Response:
        """Type-safe wrapper for base class safe_request method."""
        safe_request_method: Callable[..., Response] = cast(
            "Callable[..., Response]",
            self.safe_request,
        )
        return safe_request_method(method, *args, **kwargs)

    def _assert_health_response_typed(self, resp: Response) -> None:
        """Type-safe wrapper for base class assert_health_response method."""
        assert_health_method: Callable[[Response], None] = cast(
            "Callable[[Response], None]",
            self.assert_health_response,
        )
        assert_health_method(resp)

    def _assert_content_type_typed(self, resp: Response, content_type: str) -> None:
        """Type-safe wrapper for base class assert_content_type method."""
        assert_content_type_method: Callable[[Response, str], None] = cast(
            "Callable[[Response, str], None]",
            self.assert_content_type,
        )
        assert_content_type_method(resp, content_type)

    def _assert_status_typed(self, resp: Response, status: StatusCodeUnion) -> None:
        """Type-safe wrapper for base class assert_status method."""
        assert_status_method: Callable[[Response, StatusCodeUnion], None] = cast(
            "Callable[[Response, StatusCodeUnion], None]",
            self.assert_status,
        )
        assert_status_method(resp, status)

    def _get_auth_header_typed(self, client: TestClient) -> HeadersDict:
        """Type-safe wrapper for base class get_auth_header method."""
        return cast("HeadersDict", self.get_auth_header(client))

    def _override_env_vars_typed(self, env_vars: EnvVarsDict) -> None:
        """Type-safe wrapper for base class override_env_vars method."""
        override_env_vars_method: Callable[[EnvVarsDict], None] = cast(
            "Callable[[EnvVarsDict], None]",
            self.override_env_vars,
        )
        override_env_vars_method(env_vars)

    @pytest.fixture(autouse=True)
    def _setup(self, set_remaining_env_vars: Callable[[], None]) -> None:
        """Setup fixture for test initialization."""

    def test_health_get_no_auth(self, client: TestClient) -> None:
        """Test health endpoint GET request without authentication.
        Expects 200 (success) or 401 (unauthorized).
        """
        resp: Response = self._safe_request_typed(client.get, HEALTH_ENDPOINT)
        if resp.status_code == 200:
            self._assert_health_response_typed(resp)
            self._assert_content_type_typed(resp, CONTENT_TYPE_JSON)
        else:
            self._assert_status_typed(resp, 401)

    def test_health_get_with_invalid_token(self, client: TestClient) -> None:
        """Test health endpoint GET request with invalid JWT token.
        Expects 200 (success) or 401 (unauthorized).
        """
        invalid_headers: HeadersDict = {"Authorization": BEARER_INVALID_TOKEN}
        resp: Response = self._safe_request_typed(
            client.get,
            HEALTH_ENDPOINT,
            headers=invalid_headers,
        )
        if resp.status_code == 200:
            self._assert_health_response_typed(resp)
            self._assert_content_type_typed(resp, CONTENT_TYPE_JSON)
        else:
            self._assert_status_typed(resp, 401)

    def test_health_get_with_valid_token(self, client: TestClient) -> None:
        """Test health endpoint GET request with valid authentication.
        Expects 200 (success), 401 (unauthorized), or 503 (service unavailable).
        """
        headers: HeadersDict = self._get_auth_header_typed(client)
        resp: Response = self._safe_request_typed(
            client.get,
            HEALTH_ENDPOINT,
            headers=headers,
        )
        if resp.status_code == 200:
            self._assert_health_response_typed(resp)
            self._assert_content_type_typed(resp, CONTENT_TYPE_JSON)
        else:
            self._assert_status_typed(resp, (401, 503))

    def test_health_post_method(self, client: TestClient) -> None:
        """Test health endpoint POST method (should not be allowed).
        Expects 404 (not found due to catch-all route) or 401 (unauthorized).
        """
        resp: Response = self._safe_request_typed(client.post, HEALTH_ENDPOINT)
        self._assert_status_typed(resp, (404, 401))

    def test_health_put_method(self, client: TestClient) -> None:
        """Test health endpoint PUT method (should not be allowed).
        Expects 404 (not found due to catch-all route) or 401 (unauthorized).
        """
        resp: Response = self._safe_request_typed(client.put, HEALTH_ENDPOINT)
        self._assert_status_typed(resp, (404, 401))

    def test_health_delete_method(self, client: TestClient) -> None:
        """Test health endpoint DELETE method (should not be allowed).
        Expects 404 (not found due to catch-all route) or 401 (unauthorized).
        """
        resp: Response = self._safe_request_typed(client.delete, HEALTH_ENDPOINT)
        self._assert_status_typed(resp, (404, 401))

    def test_health_get_missing_api_key(self, client: TestClient) -> None:
        """Test health endpoint GET request with missing API key.
        Expects 200 (success), 401 (unauthorized), or 403 (forbidden).
        """
        base_headers: HeadersDict = self._get_auth_header_typed(client)
        headers: HeadersDict = {
            k: v for k, v in base_headers.items() if k.lower() != "x-api-key"
        }
        resp: Response = self._safe_request_typed(
            client.get,
            HEALTH_ENDPOINT,
            headers=headers,
        )
        if resp.status_code == 200:
            self._assert_health_response_typed(resp)
            self._assert_content_type_typed(resp, CONTENT_TYPE_JSON)
        else:
            self._assert_status_typed(resp, (401, 403))


class TestHealthFeatureFlags(HealthEndpointTestTemplate):
    """Test class for health endpoint feature flag behaviors.
    Tests various feature flag scenarios and API key configurations.
    """

    def _safe_request_typed(
        self,
        method: HTTPMethod,
        *args: object,
        **kwargs: object,
    ) -> Response:
        """Type-safe wrapper for base class safe_request method."""
        safe_request_method: Callable[..., Response] = cast(
            "Callable[..., Response]",
            self.safe_request,
        )
        return safe_request_method(method, *args, **kwargs)

    def _get_auth_header_typed(self, client: TestClient) -> HeadersDict:
        """Type-safe wrapper for base class get_auth_header method."""
        return cast("HeadersDict", self.get_auth_header(client))

    def _assert_api_key_required_typed(self, resp: Response) -> None:
        """Type-safe wrapper for base class assert_api_key_required method."""
        assert_api_key_required_method: Callable[[Response], None] = cast(
            "Callable[[Response], None]",
            self.assert_api_key_required,
        )
        assert_api_key_required_method(resp)

    def _override_env_vars_typed(self, env_vars: EnvVarsDict) -> None:
        """Type-safe wrapper for base class override_env_vars method."""
        override_env_vars_method: Callable[[EnvVarsDict], None] = cast(
            "Callable[[EnvVarsDict], None]",
            self.override_env_vars,
        )
        override_env_vars_method(env_vars)

    def test_health_feature_disabled(self, client: TestClient) -> None:
        """Test health endpoint when health feature is disabled.
        Expects 404, 403, or 501.
        """
        feature_env: EnvVarsDict = {"REVIEWPOINT_FEATURE_HEALTH": "false"}
        self._override_env_vars_typed(feature_env)
        resp: Response = self._safe_request_typed(client.get, "/api/v1/health")
        assert resp.status_code in (404, 403, 501)

    def test_health_read_feature_disabled(self, client: TestClient) -> None:
        """Test health endpoint when health read feature is disabled.
        Expects 404, 403, or 501.
        """
        read_feature_env: EnvVarsDict = {"REVIEWPOINT_FEATURE_HEALTH_READ": "false"}
        self._override_env_vars_typed(read_feature_env)
        resp: Response = self._safe_request_typed(client.get, "/api/v1/health")
        assert resp.status_code in (404, 403, 501)

    def test_api_key_disabled(self, client: TestClient) -> None:
        """Test health endpoint when API key authentication is disabled.
        Expects 200 (success) or 503 (service unavailable).
        """
        api_key_env: EnvVarsDict = {"REVIEWPOINT_API_KEY_ENABLED": "false"}
        self._override_env_vars_typed(api_key_env)
        resp: Response = self._safe_request_typed(client.get, "/api/v1/health")
        assert resp.status_code in (200, 503)

    def test_api_key_wrong(self, request: FixtureRequest) -> None:
        """Test health endpoint with wrong API key.
        Expects 401 or 403, or skips if fixture is not available in fast test mode.

        Raises:
            pytest.FixtureLookupError: If required fixture is not available in fast test mode.

        """
        fast_test_env: str | None = os.environ.get("FAST_TESTS")
        if fast_test_env == "1":
            try:
                client: TestClient = request.getfixturevalue("client_with_api_key")
            except pytest.FixtureLookupError:
                pytest.skip("client_with_api_key fixture not available")
        else:
            regular_env: EnvVarsDict = {
                "REVIEWPOINT_API_KEY_ENABLED": "true",
                "REVIEWPOINT_API_KEY": "nottherightkey",
                "REVIEWPOINT_FEATURE_HEALTH": "true",
                "REVIEWPOINT_FEATURE_HEALTH_READ": "true",
            }
            self._override_env_vars_typed(regular_env)
            from src.core.database import get_async_session
            from src.main import create_app

            async_session = request.getfixturevalue("async_session")
            fresh_app = create_app()
            from collections.abc import AsyncGenerator

            async def _override_get_async_session() -> AsyncGenerator[object, None]:
                yield async_session

            fresh_app.dependency_overrides[get_async_session] = (
                _override_get_async_session
            )
            test_client: TestClient = TestClient(fresh_app)
            client = test_client
        headers: HeadersDict = self._get_auth_header_typed(client)
        headers["X-API-Key"] = "wrongkey"
        resp: Response = self._safe_request_typed(
            client.get,
            "/api/v1/health",
            headers=headers,
        )
        self._assert_api_key_required_typed(resp)
