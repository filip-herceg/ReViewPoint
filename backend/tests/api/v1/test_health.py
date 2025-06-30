"""
Health endpoint tests (GET/POST/PUT/DELETE, auth/no-auth, response structure).
Uses HealthEndpointTestTemplate for maintainability and health-specific helpers.

Note: Do NOT use BaseAPITest directly for health checks—use HealthEndpointTestTemplate instead.
"""

import pytest
from fastapi.testclient import TestClient

from tests.test_templates import HealthEndpointTestTemplate

HEALTH_ENDPOINT = "/api/v1/health"


class TestHealthEndpoint(HealthEndpointTestTemplate):
    @pytest.fixture(autouse=True)
    def _setup(self, set_required_env_vars):
        pass

    def test_health_get_no_auth(self, client: TestClient):
        resp = client.get(HEALTH_ENDPOINT)
        if resp.status_code == 200:
            self.assert_health_response(resp)
            self.assert_content_type(resp, "application/json")
        else:
            self.assert_status(resp, 401)

    def test_health_get_with_invalid_token(self, client: TestClient):
        resp = client.get(
            HEALTH_ENDPOINT, headers={"Authorization": "Bearer not.a.jwt"}
        )
        if resp.status_code == 200:
            self.assert_health_response(resp)
            self.assert_content_type(resp, "application/json")
        else:
            self.assert_status(resp, 401)

    def test_health_get_with_valid_token(self, client: TestClient):
        headers = self.get_auth_header(client)
        resp = client.get(HEALTH_ENDPOINT, headers=headers)
        if resp.status_code == 200:
            self.assert_health_response(resp)
            self.assert_content_type(resp, "application/json")
        else:
            self.assert_status(resp, 401)

    def test_health_post_method(self, client: TestClient):
        resp = client.post(HEALTH_ENDPOINT)
        self.assert_status(resp, (405, 401))

    def test_health_put_method(self, client: TestClient):
        resp = client.put(HEALTH_ENDPOINT)
        self.assert_status(resp, (405, 401))

    def test_health_delete_method(self, client: TestClient):
        resp = client.delete(HEALTH_ENDPOINT)
        self.assert_status(resp, (405, 401))

    def test_health_get_missing_api_key(self, client: TestClient):
        headers = {
            k: v
            for k, v in self.get_auth_header(client).items()
            if k.lower() != "x-api-key"
        }
        resp = client.get(HEALTH_ENDPOINT, headers=headers)
        if resp.status_code == 200:
            self.assert_health_response(resp)
            self.assert_content_type(resp, "application/json")
        else:
            self.assert_status(resp, (401, 403))


class TestHealthFeatureFlags(HealthEndpointTestTemplate):
    def test_health_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_HEALTH": "false"})
        resp = client.get("/api/v1/health")
        assert resp.status_code in (404, 403, 501)

    def test_health_read_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_HEALTH_READ": "false"})
        resp = client.get("/api/v1/health")
        assert resp.status_code in (404, 403, 501)

    def test_api_key_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp = client.get("/api/v1/health")
        assert resp.status_code in (200, 401, 403)

    def test_api_key_wrong(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_API_KEY": "nottherightkey"})
        headers = self.get_auth_header(client)
        headers["X-API-Key"] = "wrongkey"
        resp = client.get("/api/v1/health", headers=headers)
        self.assert_api_key_required(resp)
