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


@pytest_asyncio.fixture
async def admin_user_setup(test_app, async_session):
    """Setup admin user and return client with proper authentication."""
    from src.api.deps import get_current_user
    from src.core.security import create_access_token
    from src.models.user import User
    
    # Create a real admin user in the database with unique email
    unique_email = f"optimized_admin_{uuid.uuid4().hex[:8]}@example.com"
    real_user = User(
        email=unique_email,
        name="Optimized Test Admin",
        hashed_password="hashed_password",  # Not used in tests
        is_active=True,
        is_admin=True
    )
    async_session.add(real_user)
    await async_session.commit()
    await async_session.refresh(real_user)
    
    # Override the auth dependency to return real user
    def override_get_current_user():
        return real_user
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Create a proper JWT token with the real user ID
    token_payload = {"sub": str(real_user.id), "role": "admin"}
    valid_token = create_access_token(token_payload)
    
    headers = {"Authorization": f"Bearer {valid_token}", "X-API-Key": "testkey"}
    
    try:
        yield headers
    finally:
        # Clean up the override
        test_app.dependency_overrides.pop(get_current_user, None)


def create_admin_headers() -> dict[str, str]:
    """Create headers with admin JWT token directly - much faster than full auth flow."""
    from src.core.security import create_access_token
    
    # Use a fixed UUID for testing - this won't require database lookup
    # in most test scenarios since we override the dependency
    fixed_user_id = "12345678-1234-5678-9abc-123456789012"
    payload = {"sub": fixed_user_id, "role": "admin"}
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
    async def test_upload_file_authenticated(self, async_client: AsyncClient, admin_user_setup):
        """Test file upload with authentication."""
        headers = admin_user_setup
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
    async def test_upload_file_invalid_filename(self, async_client: AsyncClient, admin_user_setup):
        """Test upload with invalid filename fails."""
        headers = admin_user_setup
        file_content = b"bad name"
        files = {"file": ("../bad.txt", file_content, "text/plain")}
        resp = await async_client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        self.assert_status(resp, 400)

    @pytest.mark.asyncio
    async def test_get_file_info(self, async_client: AsyncClient, admin_user_setup):
        """Test file info retrieval."""
        headers = admin_user_setup
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
    async def test_delete_file(self, async_client: AsyncClient, admin_user_setup):
        """Test file deletion."""
        headers = admin_user_setup
        # Upload a file first
        file_content = b"delete test file"
        files = {"file": ("delete_async.txt", file_content, "text/plain")}
        await async_client.post(UPLOAD_ENDPOINT, files=files, headers=headers)
        
        # Delete the file
        resp = await async_client.delete(f"{UPLOAD_ENDPOINT}/delete_async.txt", headers=headers)
        self.assert_status(resp, (204, 404))

    @pytest.mark.asyncio
    async def test_list_files(self, async_client: AsyncClient, admin_user_setup):
        """Test file listing."""
        headers = admin_user_setup
        resp = await async_client.get(UPLOAD_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        data = resp.json()
        assert "files" in data

    @pytest.mark.asyncio
    async def test_export_files_csv_authenticated(self, async_client: AsyncClient, admin_user_setup):
        """Test CSV export with authentication."""
        headers = admin_user_setup
        resp = await async_client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")

    @pytest.mark.asyncio
    async def test_export_files_csv_unauthenticated(self, async_client: AsyncClient):
        """Test CSV export without authentication fails."""
        resp = await async_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_export_alive(self, async_client: AsyncClient, admin_user_setup):
        """Test export alive endpoint."""
        headers = admin_user_setup
        resp = await async_client.get(EXPORT_ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "uploads export alive"

    @pytest.mark.asyncio
    async def test_test_alive(self, async_client: AsyncClient, admin_user_setup):
        """Test alive endpoint."""
        headers = admin_user_setup
        resp = await async_client.get(ALIVE_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "alive"
