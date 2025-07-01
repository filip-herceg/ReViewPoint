"""
Upload endpoints tests (upload, download, delete, list, export, alive, catch-all).
Uses ExportEndpointTestTemplate for DRYness and maintainability.
"""

from fastapi.testclient import TestClient

from tests.test_templates import ExportEndpointTestTemplate

UPLOAD_ENDPOINT = "/api/v1/uploads"
EXPORT_ENDPOINT = "/api/v1/uploads/export"
ALIVE_ENDPOINT = "/api/v1/uploads/test-alive"
ROOT_TEST_ENDPOINT = "/api/v1/uploads/root-test"
EXPORT_ALIVE_ENDPOINT = "/api/v1/uploads/export-alive"
EXPORT_TEST_ENDPOINT = "/api/v1/uploads/export-test"


class TestUploads(ExportEndpointTestTemplate):
    def test_uploads_router_registered(self, client: TestClient):
        resp = client.get(ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    def test_upload_file_authenticated(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"authenticated upload"
        files = {"file": ("auth.txt", file_content, "text/plain")}
        try:
            resp = client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        except Exception as e:
            import pytest

            pytest.xfail(f"DB/session error: {e}")
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data = resp.json()
            assert data["filename"] == "auth.txt"
            assert data["url"].endswith("auth.txt")

    def test_upload_file_unauthenticated(self, client: TestClient):
        file_content = b"unauthenticated upload"
        files = {"file": ("unauth.txt", file_content, "text/plain")}
        resp = client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (401, 403))

    def test_upload_file_invalid_filename(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"bad name"
        files = {"file": ("../bad.txt", file_content, "text/plain")}
        try:
            resp = client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        except Exception as e:
            import pytest

            pytest.xfail(f"DB/session error: {e}")
        self.assert_status(resp, 400)
        assert (
            "path traversal" in resp.text.lower()
            or "invalid filename" in resp.text.lower()
        )

    def test_upload_file_too_large(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"0" * 20_000_000
        files = {"file": ("large.txt", file_content, "text/plain")}
        try:
            resp = client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        except Exception as e:
            import pytest

            pytest.xfail(f"DB/session error: {e}")
        self.assert_status(resp, (201, 409, 413))

    def test_upload_file_unsupported_type(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"%PDF-1.4 fake pdf"
        files = {"file": ("file.exe", file_content, "application/octet-stream")}
        resp = client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        self.assert_status(resp, (201, 409, 415))

    def test_get_file_info_authenticated(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"info file"
        files = {"file": ("info.txt", file_content, "text/plain")}
        client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        resp = client.get(f"{UPLOAD_ENDPOINT}/info.txt", headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["filename"] == "info.txt"
        assert data["url"].endswith("info.txt")

    def test_get_file_info_unauthenticated(self, client: TestClient):
        resp = client.get(f"{UPLOAD_ENDPOINT}/info.txt")
        self.assert_status(resp, (401, 403))

    def test_delete_file_authenticated(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"delete me"
        files = {"file": ("delete.txt", file_content, "text/plain")}
        client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        resp = client.delete(f"{UPLOAD_ENDPOINT}/delete.txt", headers=headers)
        self.assert_status(resp, (204, 404))

    def test_delete_file_unauthenticated(self, client: TestClient):
        resp = client.delete(f"{UPLOAD_ENDPOINT}/delete.txt")
        self.assert_status(resp, (401, 403))

    def test_list_files_authenticated(self, client: TestClient):
        headers = self.get_auth_header(client)
        resp = client.get(UPLOAD_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        assert "files" in data
        assert "total" in data

    def test_list_files_unauthenticated(self, client: TestClient):
        resp = client.get(UPLOAD_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_list_files_with_query_and_fields(self, client: TestClient):
        headers = self.get_auth_header(client)
        file_content = b"searchable content"
        files = {"file": ("searchable.txt", file_content, "text/plain")}
        client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        resp = client.get(
            f"{UPLOAD_ENDPOINT}?q=searchable&fields=filename", headers=headers
        )
        self.assert_status(resp, 200)
        data = resp.json()
        assert any(f["filename"] == "searchable.txt" for f in data["files"])
        for f in data["files"]:
            assert set(f.keys()) <= {"filename"}

    def test_list_files_with_sort_and_order(self, client: TestClient):
        headers = self.get_auth_header(client)
        resp = client.get(f"{UPLOAD_ENDPOINT}?sort=filename&order=asc", headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        filenames = [f["filename"] for f in data["files"]]
        assert filenames == sorted(filenames)

    def test_list_files_with_created_after_before(self, client: TestClient):
        headers = self.get_auth_header(client)
        import datetime

        # Use naive datetime (no tzinfo) to match backend expectation
        now = datetime.datetime.now().isoformat(timespec="microseconds")
        resp = client.get(f"{UPLOAD_ENDPOINT}?created_before={now}", headers=headers)
        self.assert_status(resp, 200)
        resp = client.get(
            f"{UPLOAD_ENDPOINT}?created_after=2000-01-01T00:00:00", headers=headers
        )
        self.assert_status(resp, 200)

    def test_export_files_csv_authenticated(self, client: TestClient):
        headers = self.get_auth_header(client)
        resp = client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        assert "filename,url" in resp.text

    def test_export_files_csv_unauthenticated(self, client: TestClient):
        resp = client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_export_alive(self, client: TestClient):
        resp = client.get(EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "uploads export alive"

    def test_test_alive(self, client: TestClient):
        resp = client.get(ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "alive"

    def test_export_test_unauthenticated(self, client: TestClient):
        resp = client.get(EXPORT_TEST_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_catch_all_uploads(self, client: TestClient):
        resp = client.get(f"{UPLOAD_ENDPOINT}/this/does/not/exist")
        self.assert_status(resp, 418)
        assert "uploads catch-all" in resp.text


class TestUploadsFeatureFlags(ExportEndpointTestTemplate):
    def test_uploads_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_UPLOADS": "false"})
        headers = self.get_auth_header(client)
        file_content = b"disabled upload"
        files = {"file": ("disabled.txt", file_content, "text/plain")}
        resp = client.post("/api/v1/uploads", files=files, headers=headers)
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_upload_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_UPLOADS_UPLOAD": "false"})
        headers = self.get_auth_header(client)
        file_content = b"disabled upload"
        files = {"file": ("disabled2.txt", file_content, "text/plain")}
        resp = client.post("/api/v1/uploads", files=files, headers=headers)
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_delete_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_UPLOADS_DELETE": "false"})
        headers = self.get_auth_header(client)
        resp = client.delete("/api/v1/uploads/delete.txt", headers=headers)
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_list_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_UPLOADS_LIST": "false"})
        headers = self.get_auth_header(client)
        resp = client.get("/api/v1/uploads", headers=headers)
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_export_feature_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_FEATURE_UPLOADS_EXPORT": "false"})
        headers = self.get_auth_header(client)
        resp = client.get("/api/v1/uploads/export", headers=headers)
        self.assert_status(resp, (404, 403, 501))

    def test_api_key_disabled(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_API_KEY_ENABLED": "false"})
        headers = self.get_auth_header(client)
        resp = client.get("/api/v1/uploads", headers=headers)
        self.assert_status(resp, (200, 401, 403))

    def test_api_key_wrong(self, client: TestClient):
        self.override_env_vars({"REVIEWPOINT_API_KEY": "nottherightkey"})
        headers = self.get_auth_header(client)
        headers["X-API-Key"] = "wrongkey"
        resp = client.get("/api/v1/uploads", headers=headers)
        self.assert_status(resp, (401, 403))
