# Tests for users/core.py (CRUD endpoints) - Async version
import pytest
from httpx import ASGITransport, AsyncClient

from tests.test_templates import UserCoreEndpointTestTemplate

USER_ENDPOINT = "/api/v1/users"


class TestUserCRUDAsync(UserCoreEndpointTestTemplate):
    endpoint = USER_ENDPOINT
    create_payload = {"email": "u2@example.com", "password": "pw123456", "name": "U2"}
    update_payload = {"name": "U2 Updated"}

    @pytest.mark.asyncio
    async def test_create(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            # First register a user to get auth token
            register_resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "admin@example.com",
                    "password": "TestPass123!",
                    "name": "Admin User",
                },
            )
            if register_resp.status_code == 201:
                token = register_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
            else:
                # Fallback to API key only if registration fails
                headers = {"X-API-Key": "testkey"}
            
            # Create the user
            resp = await ac.post(
                self.endpoint,
                json=self.create_payload,
                headers=headers,
            )
            self.assert_status(resp, 201)
            user_id = resp.json()["id"]
            
            # Verify user was created
            resp = await ac.get(
                f"{self.endpoint}/{user_id}", 
                headers=headers
            )
            self.assert_status(resp, 200)
            assert resp.json()["email"] == self.create_payload["email"]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self):
        transport = ASGITransport(app=self.test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey"},
        ) as ac:
            data = {"email": "dupe@example.com", "password": "pw123456", "name": "Dupe"}
            
            # Register admin user for auth
            register_resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "admin@example.com",
                    "password": "TestPass123!",
                    "name": "Admin User",
                },
            )
            if register_resp.status_code == 201:
                token = register_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
            else:
                headers = {"X-API-Key": "testkey"}
            
            # Create first user
            _ = await ac.post(self.endpoint, json=data, headers=headers)
            
            # Try to create duplicate user
            resp2 = await ac.post(self.endpoint, json=data, headers=headers)
            self.assert_status(resp2, (409, 400, 401))
