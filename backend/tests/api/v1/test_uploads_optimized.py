"""
Optimized async upload endpoint tests using fast JWT pattern.
Uses direct JWT token creation for maximum speed and reliability.
"""
import pytest
import pytest_asyncio
import uuid
from httpx import ASGITransport, AsyncClient

from tests.test_templates import ExportEndpointTestTemplate

UPLOAD_ENDPOINT = "/api/v1/uploads"
EXPORT_ENDPOINT = "/api/v1/uploads/export"
ALIVE_ENDPOINT = "/api/v1/uploads/test-alive"
ROOT_TEST_ENDPOINT = "/api/v1/uploads/root-test"
EXPORT_ALIVE_ENDPOINT = "/api/v1/uploads/export-alive"


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


def create_admin_headers() -> dict[str, str]:
    """Create headers with admin JWT token directly - much faster than full auth flow."""
    from src.core.security import create_access_token
    
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"sub": email, "role": "admin"}
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}


class TestUploadsAsync(ExportEndpointTestTemplate):
    """Fast async tests using direct JWT token creation."""

    @pytest.mark.asyncio
    async def test_uploads_router_registered(self, async_client: AsyncClient):
        """Test that uploads router is properly registered."""
        resp = await async_client.get(ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    @pytest.mark.asyncio
    async def test_upload_file_authenticated(self, async_client: AsyncClient):
        """Test file upload with authentication."""
        headers = create_admin_headers()
        file_content = b"async test upload"
        files = {"file": ("async_test.txt", file_content, "text/plain")}
        
        resp = await async_client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data = resp.json()
            assert data["filename"] == "async_test.txt"

    @pytest.mark.asyncio
    async def test_upload_file_unauthenticated(self, async_client: AsyncClient):
        """Test file upload without authentication fails."""
        file_content = b"unauthorized upload"
        files = {"file": ("unauth.txt", file_content, "text/plain")}
        resp = await async_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_upload_file_invalid_filename(self, async_client: AsyncClient):
        """Test upload with invalid filename fails."""
        headers = create_admin_headers()
        file_content = b"bad name"
        files = {"file": ("../bad.txt", file_content, "text/plain")}
        resp = await async_client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        self.assert_status(resp, 400)

    @pytest.mark.asyncio
    async def test_get_file_info(self, async_client: AsyncClient):
        """Test file info retrieval."""
        headers = create_admin_headers()
        # Upload a file first
        file_content = b"info test file"
        files = {"file": ("info_async.txt", file_content, "text/plain")}
        await async_client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        
        # Get file info
        resp = await async_client.get(f"{UPLOAD_ENDPOINT}/info_async.txt", headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["filename"] == "info_async.txt"

    @pytest.mark.asyncio
    async def test_delete_file(self, async_client: AsyncClient):
        """Test file deletion."""
        headers = create_admin_headers()
        # Upload a file first
        file_content = b"delete test file"
        files = {"file": ("delete_async.txt", file_content, "text/plain")}
        await async_client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        
        # Delete the file
        resp = await async_client.delete(f"{UPLOAD_ENDPOINT}/delete_async.txt", headers=headers)
        self.assert_status(resp, (204, 404))

    @pytest.mark.asyncio
    async def test_list_files(self, async_client: AsyncClient):
        """Test file listing."""
        headers = create_admin_headers()
        resp = await async_client.get(UPLOAD_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        assert "files" in data

    @pytest.mark.asyncio
    async def test_export_files_csv_authenticated(self, async_client: AsyncClient):
        """Test CSV export with authentication."""
        headers = create_admin_headers()
        resp = await async_client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")

    @pytest.mark.asyncio
    async def test_export_files_csv_unauthenticated(self, async_client: AsyncClient):
        """Test CSV export without authentication fails."""
        resp = await async_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_export_alive(self, async_client: AsyncClient):
        """Test export alive endpoint."""
        headers = create_admin_headers()
        resp = await async_client.get(EXPORT_ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "uploads export alive"

    @pytest.mark.asyncio
    async def test_test_alive(self, async_client: AsyncClient):
        """Test alive endpoint."""
        headers = create_admin_headers()
        resp = await async_client.get(ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "alive"
