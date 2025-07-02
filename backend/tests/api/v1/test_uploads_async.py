"""
Upload endpoints tests converted to async pattern with performance optimizations.
Uses AsyncClient with dependency overrides for ultra-fast test execution.
"""

import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport

from tests.test_templates import ExportEndpointTestTemplate

UPLOAD_ENDPOINT = "/api/v1/uploads"
EXPORT_ENDPOINT = "/api/v1/uploads/export"
ALIVE_ENDPOINT = "/api/v1/uploads/test-alive"
ROOT_TEST_ENDPOINT = "/api/v1/uploads/root-test"
EXPORT_ALIVE_ENDPOINT = "/api/v1/uploads/export-alive"
EXPORT_TEST_ENDPOINT = "/api/v1/uploads/export-test"


def create_mock_admin_user():
    """Create a mock admin user for dependency injection - fastest possible auth."""
    from src.services.user import UserRole
    
    # Create a simple mock user object with the minimum required attributes
    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
            self.name = "Test Admin"
            self.role = UserRole.ADMIN
            self.is_active = True
            self.is_deleted = False
            self.hashed_password = "mock_hash"
    
    return MockUser()


@pytest_asyncio.fixture
async def fast_admin_client(test_app):
    """Ultra-fast async client with mocked admin authentication - no database calls."""
    from src.api.deps import get_current_user
    
    # Override the auth dependency to return mock admin user
    mock_admin = create_mock_admin_user()
    
    def override_get_current_user():
        return mock_admin
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    
    try:
        transport = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey", "Authorization": "Bearer mock_token"},
        ) as ac:
            yield ac
    finally:
        # Clean up the override
        test_app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture
async def fast_anon_client(test_app):
    """Ultra-fast async client without authentication."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": "testkey"},
    ) as ac:
        yield ac


class TestUploadsAsync(ExportEndpointTestTemplate):
    
    @pytest.mark.asyncio
    async def test_uploads_router_registered(self, fast_anon_client: AsyncClient):
        resp = await fast_anon_client.get(ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data = resp.json()
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    @pytest.mark.asyncio
    async def test_upload_file_authenticated(self, fast_admin_client: AsyncClient):
        file_content = b"authenticated upload"
        files = {"file": ("auth.txt", file_content, "text/plain")}
        resp = await fast_admin_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, 201)
        data = resp.json()
        # Check the actual response structure - adjust expectations based on real response
        assert "file" in data or "filename" in data  # Flexible check for upload success

    @pytest.mark.asyncio
    async def test_upload_file_unauthenticated(self, fast_anon_client: AsyncClient):
        file_content = b"unauthenticated upload"
        files = {"file": ("unauth.txt", file_content, "text/plain")}
        resp = await fast_anon_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_upload_file_invalid_filename(self, fast_admin_client: AsyncClient):
        file_content = b"invalid filename"
        files = {"file": ("../../../etc/passwd", file_content, "text/plain")}
        resp = await fast_admin_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, 400)

    @pytest.mark.asyncio
    async def test_export_files_csv_authenticated(self, fast_admin_client: AsyncClient):
        resp = await fast_admin_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, 200)
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"

    @pytest.mark.asyncio
    async def test_export_files_csv_unauthenticated(self, fast_anon_client: AsyncClient):
        resp = await fast_anon_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_export_alive(self, fast_admin_client: AsyncClient):
        resp = await fast_admin_client.get(EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "uploads export alive"

    @pytest.mark.asyncio
    async def test_test_alive(self, fast_admin_client: AsyncClient):
        resp = await fast_admin_client.get(ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        assert resp.json()["status"] == "alive"

    @pytest.mark.asyncio
    async def test_list_files_authenticated(self, fast_admin_client: AsyncClient):
        resp = await fast_admin_client.get(UPLOAD_ENDPOINT)
        self.assert_status(resp, 200)
        data = resp.json()
        assert "files" in data
        assert isinstance(data["files"], list)

    @pytest.mark.asyncio
    async def test_list_files_unauthenticated(self, fast_anon_client: AsyncClient):
        resp = await fast_anon_client.get(UPLOAD_ENDPOINT)
        self.assert_status(resp, (401, 403))
