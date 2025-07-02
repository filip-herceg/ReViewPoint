"""
Upload endpoints tests converted to async pattern.
Uses AsyncClient instead of TestClient for better async compatibility.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from tests.test_templates import ExportEndpointTestTemplate

UPLOAD_ENDPOINT = "/api/v1/uploads"
EXPORT_ENDPOINT = "/api/v1/uploads/export"
ALIVE_ENDPOINT = "/api/v1/uploads/test-alive"
ROOT_TEST_ENDPOINT = "/api/v1/uploads/root-test"
EXPORT_ALIVE_ENDPOINT = "/api/v1/uploads/export-alive"
EXPORT_TEST_ENDPOINT = "/api/v1/uploads/export-test"


class TestUploadsAsync(ExportEndpointTestTemplate):
    
    async def get_admin_headers(self, ac: AsyncClient, unique_suffix: str | None = None) -> dict[str, str]:
        """Get headers with admin authentication for async requests."""
        # Use unique email to avoid rate limiting
        if unique_suffix is None:
            import time
            unique_suffix = str(int(time.time() * 1000))[-6:]  # Last 6 digits of current timestamp
        email = f"admin{unique_suffix}@example.com"
        
        # Register a user
        register_resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "TestPass123!",
                "name": "Admin User",
            },
        )
        assert register_resp.status_code == 201
        token = register_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        
        # Promote user to admin
        promote_resp = await ac.post(
            "/api/v1/users/promote-admin",
            json={"email": email},
            headers=headers,
        )
        assert promote_resp.status_code == 200
        
        # Get new token with admin role
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": "TestPass123!",
            },
        )
        assert login_resp.status_code == 200
        admin_token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {admin_token}", "X-API-Key": "testkey"}

    @pytest.mark.asyncio
    async def test_uploads_router_registered(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.get(ROOT_TEST_ENDPOINT)
            self.assert_status(resp, 200)
            data = resp.json()
            assert data["status"] == "uploads root test"
            assert data["router"] == "uploads"

    @pytest.mark.asyncio
    async def test_upload_file_authenticated(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            headers = await self.get_admin_headers(ac)
            file_content = b"authenticated upload"
            files = {"file": ("auth.txt", file_content, "text/plain")}
            resp = await ac.post(UPLOAD_ENDPOINT, files=files, headers=headers)
            self.assert_status(resp, 201)
            data = resp.json()
            # Check the actual response structure - adjust expectations based on real response
            assert "file" in data or "filename" in data  # Flexible check for upload success

    @pytest.mark.asyncio
    async def test_upload_file_unauthenticated(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            file_content = b"unauthenticated upload"
            files = {"file": ("unauth.txt", file_content, "text/plain")}
            resp = await ac.post(UPLOAD_ENDPOINT, files=files)
            self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_upload_file_invalid_filename(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            headers = await self.get_admin_headers(ac)
            file_content = b"invalid filename"
            files = {"file": ("../../../etc/passwd", file_content, "text/plain")}
            resp = await ac.post(UPLOAD_ENDPOINT, files=files, headers=headers)
            self.assert_status(resp, 400)

    @pytest.mark.asyncio
    async def test_export_files_csv_authenticated(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            headers = await self.get_admin_headers(ac)
            resp = await ac.get(EXPORT_ENDPOINT, headers=headers)
            self.assert_status(resp, 200)
            assert resp.headers["content-type"] == "text/csv; charset=utf-8"

    @pytest.mark.asyncio
    async def test_export_files_csv_unauthenticated(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.get(EXPORT_ENDPOINT)
            self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_export_alive(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            headers = await self.get_admin_headers(ac)
            resp = await ac.get(EXPORT_ALIVE_ENDPOINT, headers=headers)
            self.assert_status(resp, 200)
            assert resp.json()["status"] == "uploads export alive"

    @pytest.mark.asyncio
    async def test_test_alive(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            headers = await self.get_admin_headers(ac)
            resp = await ac.get(ALIVE_ENDPOINT, headers=headers)
            self.assert_status(resp, 200)
            assert resp.json()["status"] == "alive"

    @pytest.mark.asyncio
    async def test_list_files_authenticated(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            headers = await self.get_admin_headers(ac)
            resp = await ac.get(UPLOAD_ENDPOINT, headers=headers)
            self.assert_status(resp, 200)
            data = resp.json()
            assert "files" in data
            assert isinstance(data["files"], list)

    @pytest.mark.asyncio
    async def test_list_files_unauthenticated(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            resp = await ac.get(UPLOAD_ENDPOINT)
            self.assert_status(resp, (401, 403))
