"""
Fast optimized upload endpoint tests using sync pattern.
Minimizes auth overhead and DB setup for maximum speed.
Uses the same pattern as working sync tests.
"""

from fastapi.testclient import TestClient

from tests.test_templates import ExportEndpointTestTemplate

UPLOAD_ENDPOINT = "/api/v1/uploads"
EXPORT_ENDPOINT = "/api/v1/uploads/export"
ALIVE_ENDPOINT = "/api/v1/uploads/test-alive"
ROOT_TEST_ENDPOINT = "/api/v1/uploads/root-test"
EXPORT_ALIVE_ENDPOINT = "/api/v1/uploads/export-alive"


class TestUploadsFast(ExportEndpointTestTemplate):
    """Fast sync tests - reuses client and optimizes auth for speed."""

    def test_uploads_router_registered(self, client: TestClient):
        """Test that uploads router is properly registered."""
        resp = self.safe_request(client.get, ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    def test_upload_file_authenticated(self, client: TestClient):
        """Test file upload with authentication - optimized version."""
        headers = self.get_auth_header(client)
        file_content = b"fast test upload"
        files = {"file": ("fast_test.txt", file_content, "text/plain")}

        # Test authenticated upload
        resp = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data = resp.json()
            assert data["filename"] == "fast_test.txt"

    def test_upload_file_unauthenticated(self, client: TestClient):
        """Test unauthenticated upload fails."""
        file_content = b"unauthorized upload"
        files = {"file": ("unauth.txt", file_content, "text/plain")}
        resp = self.safe_request(client.post, UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (401, 403))

    def test_upload_file_invalid_filename(self, client: TestClient):
        """Test upload with invalid filename."""
        headers = self.get_auth_header(client)
        file_content = b"bad name"
        files = {"file": ("../bad.txt", file_content, "text/plain")}
        resp = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, 400)

    def test_get_file_info(self, client: TestClient):
        """Test file info retrieval."""
        headers = self.get_auth_header(client)
        # Upload a file first
        file_content = b"info test file"
        files = {"file": ("info_test.txt", file_content, "text/plain")}
        self.safe_request(client.post, UPLOAD_ENDPOINT, files=files, headers=headers)

        # Get file info
        resp = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}/info_test.txt", headers=headers
        )
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["filename"] == "info_test.txt"

    def test_delete_file(self, client: TestClient):
        """Test file deletion."""
        headers = self.get_auth_header(client)
        # Upload a file first
        file_content = b"delete test file"
        files = {"file": ("delete_test.txt", file_content, "text/plain")}
        self.safe_request(client.post, UPLOAD_ENDPOINT, files=files, headers=headers)

        # Delete the file
        resp = self.safe_request(
            client.delete, f"{UPLOAD_ENDPOINT}/delete_test.txt", headers=headers
        )
        self.assert_status(resp, (204, 404))

    def test_list_files(self, client: TestClient):
        """Test file listing."""
        headers = self.get_auth_header(client)
        resp = self.safe_request(client.get, UPLOAD_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        assert "files" in data

    def test_export_files_csv_authenticated(self, client: TestClient):
        """Test CSV export with authentication."""
        headers = self.get_auth_header(client)
        resp = self.safe_request(client.get, EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")

    def test_export_files_csv_unauthenticated(self, client: TestClient):
        """Test CSV export without authentication fails."""
        resp = self.safe_request(client.get, EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_export_alive(self, client: TestClient):
        """Test export alive endpoint."""
        headers = self.get_auth_header(client)
        resp = self.safe_request(client.get, EXPORT_ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "uploads export alive"

    def test_test_alive(self, client: TestClient):
        """Test alive endpoint."""
        headers = self.get_auth_header(client)
        resp = self.safe_request(client.get, ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "alive"
