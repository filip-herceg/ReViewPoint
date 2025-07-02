# Tests for users/exports.py (export endpoints)

from fastapi.testclient import TestClient

from tests.test_templates import ExportEndpointTestTemplate

EXPORT_ENDPOINT = "/api/v1/users/export"
EXPORT_ALIVE_ENDPOINT = "/api/v1/users/export-alive"
EXPORT_FULL_ENDPOINT = "/api/v1/users/export-full"
EXPORT_SIMPLE_ENDPOINT = "/api/v1/users/export-simple"


class TestUserExports(ExportEndpointTestTemplate):
    def test_export_users_csv(self, client: TestClient):
        # Create a JWT token directly instead of trying to register/login
        # This bypasses the database connection issues during test setup
        import uuid
        from src.core.security import create_access_token
        
        email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"sub": email, "role": "admin"}
        token = create_access_token(payload)
        headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        
        resp = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name" in resp.text

    def test_users_export_alive(self, client: TestClient):
        resp = client.get(EXPORT_ALIVE_ENDPOINT, headers=self.get_auth_header(client))
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "users export alive"

    def test_export_users_full_csv(self, client: TestClient):
        import uuid

        from src.core.security import create_access_token

        email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"sub": email, "role": "admin"}
        token = create_access_token(payload)
        headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        resp = client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "id,email,name,created_at,updated_at" in resp.text

    def test_export_users_csv_unauthenticated(
        self, override_env_vars, client: TestClient
    ):
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp = client.get(EXPORT_ENDPOINT)
        # When API keys are disabled, endpoint should be accessible
        self.assert_status(resp, 200)

    def test_export_users_full_csv_unauthenticated(
        self, override_env_vars, client: TestClient
    ):
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp = client.get(EXPORT_FULL_ENDPOINT)
        # When API keys are disabled, endpoint should be accessible
        self.assert_status(resp, 200)

    def test_export_alive_unauthenticated(self, override_env_vars, client: TestClient):
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp = client.get(EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "users export alive"

    def test_export_simple_unauthenticated(self, override_env_vars, client: TestClient):
        override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp = client.get(EXPORT_SIMPLE_ENDPOINT)
        self.assert_status(resp, 200)

    def test_export_users_csv_content(self, client: TestClient):
        resp = client.get(EXPORT_ENDPOINT, headers=self.get_auth_header(client))
        self.assert_status(resp, 200)
        lines = resp.text.splitlines()
        assert lines[0].startswith("id,email,name")
        assert any("," in line for line in lines[1:])  # At least one user row

    def test_export_users_csv_with_query_params(self, client: TestClient):
        resp = client.get(f"{EXPORT_ENDPOINT}?fields=id,email", headers=self.get_auth_header(client))
        self.assert_status(resp, 200)
        assert resp.text.splitlines()[0].startswith("id,email")

    def test_export_users_csv_empty_db(self, client: TestClient):
        # Assume DB is empty after fixture reset or use a filter that returns nothing
        resp = client.get(
            f"{EXPORT_ENDPOINT}?email=doesnotexist@example.com", headers=self.get_auth_header(client)
        )
        self.assert_status(resp, 200)
        lines = resp.text.splitlines()
        assert lines[0].startswith("id,email,name")
        assert len(lines) == 1  # Only header

    def test_export_users_csv_content_disposition(self, client: TestClient):
        resp = client.get(EXPORT_ENDPOINT, headers=self.get_auth_header(client))
        self.assert_status(resp, 200)
        cd = resp.headers.get("content-disposition", "")
        assert "attachment" in cd and ".csv" in cd

    def test_export_users_csv_unsupported_format(self, client: TestClient):
        resp = client.get(f"{EXPORT_ENDPOINT}?format=xml", headers=self.get_auth_header(client))
        self.assert_status(resp, (400, 422))

    def test_export_users_csv_invalid_token(self, client: TestClient):
        headers = {"Authorization": "Bearer not.a.jwt.token", "X-API-Key": "testkey"}
        resp = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, (401, 403))

    def test_export_users_csv_missing_api_key(self, client: TestClient):
        auth_headers = self.get_auth_header(client)
        headers = {k: v for k, v in auth_headers.items() if k.lower() != "x-api-key"}
        resp = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, (401, 403))

    def test_export_alive_with_auth(self, client: TestClient):
        resp = client.get(EXPORT_ALIVE_ENDPOINT, headers=self.get_auth_header(client))
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "users export alive"

    def test_export_simple_with_auth(self, client: TestClient):
        resp = client.get(EXPORT_SIMPLE_ENDPOINT, headers=self.get_auth_header(client))
        self.assert_status(resp, 200)
        assert "users" in resp.json() or resp.headers["content-type"].startswith(
            "text/csv"
        )

    def test_export_full_csv_invalid_token(self, client: TestClient):
        headers = {"Authorization": "Bearer not.a.jwt.token", "X-API-Key": "testkey"}
        resp = client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, (401, 403))

    def test_export_full_csv_missing_api_key(self, client: TestClient):
        auth_headers = self.get_auth_header(client)
        headers = {k: v for k, v in auth_headers.items() if k.lower() != "x-api-key"}
        resp = client.get(EXPORT_FULL_ENDPOINT, headers=headers)
        self.assert_status(resp, (401, 403))


class TestUserExportsFeatureFlags(ExportEndpointTestTemplate):
    def test_export_users_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_USERS_EXPORT": "false"})
        resp = client.get("/api/v1/users/export", headers=self.get_auth_header(client))
        assert resp.status_code in (404, 403, 501)

    def test_export_full_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_USERS_EXPORT_FULL": "false"})
        resp = client.get(
            "/api/v1/users/export-full", headers=self.get_auth_header(client)
        )
        assert resp.status_code in (404, 403, 501)

    def test_export_alive_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_USERS_EXPORT_ALIVE": "false"})
        resp = client.get(
            "/api/v1/users/export-alive", headers=self.get_auth_header(client)
        )
        assert resp.status_code in (404, 403, 501)

    def test_export_simple_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_USERS_EXPORT_SIMPLE": "false"})
        resp = client.get(
            "/api/v1/users/export-simple", headers=self.get_auth_header(client)
        )
        assert resp.status_code in (404, 403, 501)

    def test_api_key_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        resp = client.get("/api/v1/users/export", headers=self.get_auth_header(client))
        assert resp.status_code in (200, 401, 403)

    def test_api_key_wrong(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_API_KEY": "nottherightkey"})
        headers = self.get_auth_header(client)
        headers["X-API-Key"] = "wrongkey"
        resp = client.get("/api/v1/users/export", headers=headers)
        assert resp.status_code in (401, 403)
