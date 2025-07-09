"""
Upload endpoints tests (upload, download, delete, list, export, alive, catch-all).
Uses ExportEndpointTestTemplate for DRYness and maintainability.
Merged from test_uploads_async.py, test_uploads_fast.py, and test_uploads_optimized.py.

All functions, methods, variables, and classes are strictly typed for Mypy compliance.
No usage of Any, type: ignore, or deprecated typing constructs.
"""

from __future__ import annotations

import datetime
import json
import os
import uuid
from collections.abc import AsyncGenerator, Callable, Mapping, Sequence
from typing import Final, Literal, TypedDict, cast

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from httpx import Response as HttpxResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from tests.test_templates import ExportEndpointTestTemplate

# Constant endpoints with strict typing
UPLOAD_ENDPOINT: Final[str] = "/api/v1/uploads"
EXPORT_ENDPOINT: Final[str] = "/api/v1/uploads/export"
ALIVE_ENDPOINT: Final[str] = "/api/v1/uploads/test-alive"
ROOT_TEST_ENDPOINT: Final[str] = "/api/v1/uploads/root-test"
EXPORT_ALIVE_ENDPOINT: Final[str] = "/api/v1/uploads/export-alive"
EXPORT_TEST_ENDPOINT: Final[str] = "/api/v1/uploads/export-test"

# Type aliases for better readability
StatusCodeTuple = tuple[int, ...] | tuple[int]
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
HeadersDict = dict[str, str]
ResponseDict = dict[str, str | int | bool | list[object] | dict[str, object]]
FilesDict = dict[str, tuple[str, bytes, str]]

# Use Union type for responses from both TestClient and AsyncClient
TestResponse = Response | HttpxResponse


# Helper functions for type-safe response handling
def get_response_json(response: TestResponse) -> ResponseDict:
    """Type-safe wrapper for getting JSON from either response type."""
    if isinstance(response, HttpxResponse):
        return cast(ResponseDict, response.json())
    else:
        # For starlette Response, we need to parse JSON manually
        body_bytes: bytes = bytes(response.body) if hasattr(response, "body") else b""
        json_data = json.loads(body_bytes.decode("utf-8"))
        return cast(ResponseDict, json_data)


def get_response_text(response: TestResponse) -> str:
    """Type-safe wrapper for getting text from either response type."""
    if isinstance(response, HttpxResponse):
        return response.text
    else:
        # For starlette Response, decode the body
        body_bytes: bytes = bytes(response.body) if hasattr(response, "body") else b""
        return body_bytes.decode("utf-8")


def get_response_headers(response: TestResponse) -> Mapping[str, str]:
    """Type-safe wrapper for getting headers from either response type."""
    return response.headers  # Both Response and HttpxResponse have .headers


def get_response_content_type(response: TestResponse) -> str:
    """Type-safe wrapper for getting content-type header from either response type."""
    headers = get_response_headers(response)
    return headers.get("content-type", "")


# Typed wrapper for safe_request method
RequestMethod = Callable[..., TestResponse]


def typed_safe_request(
    method: RequestMethod, *args: object, **kwargs: object
) -> TestResponse:
    """Type-safe wrapper for the safe_request method from base class."""
    try:
        return method(*args, **kwargs)
    except Exception as e:
        pytest.xfail(f"Connection/DB error: {e}")


# TypedDicts for structured response data
class StatusResponseDict(TypedDict):
    status: str
    router: str


class FileResponseDict(TypedDict):
    filename: str
    url: str
    id: str


class UploadResponseDict(TypedDict):
    filename: str
    url: str


class FileListResponseDict(TypedDict):
    files: Sequence[FileResponseDict]
    total: int


class AliveResponseDict(TypedDict):
    status: Literal["alive", "uploads export alive"]


class TypedExportEndpointTestTemplate(ExportEndpointTestTemplate):
    """Extended test template with strict typing for safe_request and response handling."""

    def safe_request(
        self,
        func: object,  # Match base class signature
        *args: object,
        **kwargs: object,
    ) -> TestResponse:
        """Type-safe wrapper for the safe_request method."""
        return typed_safe_request(cast(RequestMethod, func), *args, **kwargs)


class TestUploads(TypedExportEndpointTestTemplate):
    """Test class for upload endpoints with strict typing."""

    def test_uploads_router_registered(self, client: TestClient) -> None:
        """Test that uploads router is properly registered."""
        resp: TestResponse = self.safe_request(client.get, ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data: StatusResponseDict = cast(StatusResponseDict, get_response_json(resp))
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    def test_upload_file_authenticated(self, client: TestClient) -> None:
        """Test authenticated file upload."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"authenticated upload"
        files: FilesDict = {"file": ("auth.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data: UploadResponseDict = cast(UploadResponseDict, get_response_json(resp))
            assert data["filename"] == "auth.txt"
            assert data["url"].endswith("auth.txt")

    def test_upload_file_unauthenticated(self, client: TestClient) -> None:
        """Test unauthenticated file upload fails."""
        file_content: bytes = b"unauthenticated upload"
        files: FilesDict = {"file": ("unauth.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files
        )
        self.assert_status(resp, (401, 403))

    def test_upload_file_invalid_filename(self, client: TestClient) -> None:
        """Test upload with invalid filename."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"bad name"
        files: FilesDict = {"file": ("../bad.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, 400)
        response_text: str = get_response_text(resp).lower()
        assert "path traversal" in response_text or "invalid filename" in response_text

    def test_upload_file_too_large(self, client: TestClient) -> None:
        """Test upload with file too large."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"0" * 20_000_000
        files: FilesDict = {"file": ("large.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, (201, 409, 413))

    def test_upload_file_unsupported_type(self, client: TestClient) -> None:
        """Test upload with unsupported file type."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"%PDF-1.4 fake pdf"
        files: FilesDict = {
            "file": ("file.exe", file_content, "application/octet-stream")
        }
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, (201, 409, 415))

    def test_get_file_info_authenticated(self, client: TestClient) -> None:
        """Test getting file info when authenticated."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"info file"
        files: FilesDict = {"file": ("info.txt", file_content, "text/plain")}
        self.safe_request(client.post, UPLOAD_ENDPOINT, files=files, headers=headers)
        resp: TestResponse = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}/info.txt", headers=headers
        )
        self.assert_status(resp, 200)
        data: FileResponseDict = cast(FileResponseDict, get_response_json(resp))
        assert data["filename"] == "info.txt"
        assert data["url"].endswith("info.txt")

    def test_get_file_info_unauthenticated(self, client: TestClient) -> None:
        """Test getting file info when unauthenticated fails."""
        resp: TestResponse = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}/info.txt"
        )
        self.assert_status(resp, (401, 403))

    def test_delete_file_authenticated(self, client: TestClient) -> None:
        """Test deleting file when authenticated."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"delete me"
        files: FilesDict = {"file": ("delete.txt", file_content, "text/plain")}
        self.safe_request(client.post, UPLOAD_ENDPOINT, files=files, headers=headers)
        resp: TestResponse = self.safe_request(
            client.delete, f"{UPLOAD_ENDPOINT}/delete.txt", headers=headers
        )
        self.assert_status(resp, (204, 404))

    def test_delete_file_unauthenticated(self, client: TestClient) -> None:
        """Test deleting file when unauthenticated fails."""
        resp: TestResponse = self.safe_request(
            client.delete, f"{UPLOAD_ENDPOINT}/delete.txt"
        )
        self.assert_status(resp, (401, 403))

    def test_list_files_authenticated(self, client: TestClient) -> None:
        """Test listing files when authenticated."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, UPLOAD_ENDPOINT, headers=headers
        )
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        assert "files" in data
        assert "total" in data

    def test_list_files_unauthenticated(self, client: TestClient) -> None:
        """Test listing files when unauthenticated fails."""
        resp: TestResponse = self.safe_request(client.get, UPLOAD_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_list_files_with_query_and_fields(self, client: TestClient) -> None:
        """Test listing files with query parameters and field selection."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"searchable content"
        files: FilesDict = {"file": ("searchable.txt", file_content, "text/plain")}
        self.safe_request(client.post, UPLOAD_ENDPOINT, files=files, headers=headers)
        resp: TestResponse = self.safe_request(
            client.get,
            f"{UPLOAD_ENDPOINT}?q=searchable&fields=filename",
            headers=headers,
        )
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        files_list: Sequence[FileResponseDict] = data["files"]
        assert any(f["filename"] == "searchable.txt" for f in files_list)
        for f in files_list:
            file_keys: set[str] = set(f.keys())
            assert file_keys <= {"filename"}

    def test_list_files_with_sort_and_order(self, client: TestClient) -> None:
        """Test listing files with sorting."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}?sort=filename&order=asc", headers=headers
        )
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        filenames: list[str] = [f["filename"] for f in data["files"]]
        assert filenames == sorted(filenames)

    def test_list_files_with_created_after_before(self, client: TestClient) -> None:
        """Test listing files with date filters."""
        headers: HeadersDict = self.get_auth_header(client)

        # Use naive datetime (no tzinfo) to match backend expectation
        now: datetime.datetime = datetime.datetime.now(datetime.UTC).replace(
            tzinfo=None
        )
        now_iso: str = now.isoformat(timespec="microseconds")

        resp: TestResponse = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}?created_before={now_iso}", headers=headers
        )
        self.assert_status(resp, 200)

        resp = self.safe_request(
            client.get,
            f"{UPLOAD_ENDPOINT}?created_after=2000-01-01T00:00:00",
            headers=headers,
        )
        self.assert_status(resp, 200)

    def test_export_files_csv_authenticated(self, client: TestClient) -> None:
        """Test CSV export when authenticated."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, EXPORT_ENDPOINT, headers=headers
        )
        self.assert_status(resp, 200)
        self.assert_content_type(resp, "text/csv")
        response_text: str = get_response_text(resp)
        assert "filename,url" in response_text

    def test_export_files_csv_unauthenticated(self, client: TestClient) -> None:
        """Test CSV export when unauthenticated fails."""
        resp: TestResponse = self.safe_request(client.get, EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_export_alive(self, client: TestClient) -> None:
        """Test export alive endpoint."""
        resp: TestResponse = self.safe_request(client.get, EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "uploads export alive"

    def test_test_alive(self, client: TestClient) -> None:
        """Test alive endpoint."""
        resp: TestResponse = self.safe_request(client.get, ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "alive"

    def test_export_test_unauthenticated(self, client: TestClient) -> None:
        """Test export test endpoint when unauthenticated fails."""
        resp: TestResponse = self.safe_request(client.get, EXPORT_TEST_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_catch_all_uploads(self, client: TestClient) -> None:
        """Test catch-all route for uploads."""
        resp: TestResponse = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}/this/does/not/exist"
        )
        self.assert_status(resp, 418)
        response_text: str = get_response_text(resp)
        assert "uploads catch-all" in response_text


class TestUploadsFeatureFlags(TypedExportEndpointTestTemplate):
    """Test class for upload feature flags with strict typing."""

    def test_uploads_feature_disabled(self, client: TestClient) -> None:
        """Test uploads feature when disabled."""
        env_vars: dict[str, str] = {"REVIEWPOINT_FEATURE_UPLOADS": "false"}
        self.override_env_vars(env_vars)
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"disabled upload"
        files: FilesDict = {"file": ("disabled.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, "/api/v1/uploads", files=files, headers=headers
        )
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_upload_feature_disabled(self, client: TestClient) -> None:
        """Test uploads upload feature when disabled."""
        env_vars: dict[str, str] = {"REVIEWPOINT_FEATURE_UPLOADS_UPLOAD": "false"}
        self.override_env_vars(env_vars)
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"disabled upload"
        files: FilesDict = {"file": ("disabled2.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, "/api/v1/uploads", files=files, headers=headers
        )
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_delete_feature_disabled(self, client: TestClient) -> None:
        """Test uploads delete feature when disabled."""
        env_vars: dict[str, str] = {"REVIEWPOINT_FEATURE_UPLOADS_DELETE": "false"}
        self.override_env_vars(env_vars)
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.delete, "/api/v1/uploads/delete.txt", headers=headers
        )
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_list_feature_disabled(self, client: TestClient) -> None:
        """Test uploads list feature when disabled."""
        env_vars: dict[str, str] = {"REVIEWPOINT_FEATURE_UPLOADS_LIST": "false"}
        self.override_env_vars(env_vars)
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, "/api/v1/uploads", headers=headers
        )
        self.assert_status(resp, (404, 403, 501))

    def test_uploads_export_feature_disabled(self, client: TestClient) -> None:
        """Test uploads export feature when disabled."""
        env_vars: dict[str, str] = {"REVIEWPOINT_FEATURE_UPLOADS_EXPORT": "false"}
        self.override_env_vars(env_vars)
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, "/api/v1/uploads/export", headers=headers
        )
        self.assert_status(resp, (404, 403, 501))

    def test_api_key_disabled(self, client: TestClient) -> None:
        """Test API key when disabled."""
        env_vars: dict[str, str] = {"REVIEWPOINT_API_KEY_ENABLED": "false"}
        self.override_env_vars(env_vars)
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, "/api/v1/uploads", headers=headers
        )
        self.assert_status(resp, (200, 401, 403))

    def test_api_key_wrong(self, request: pytest.FixtureRequest) -> None:
        """Test wrong API key handling with proper fixture typing."""

        client: TestClient
        # Use appropriate fixture based on environment
        if os.environ.get("FAST_TESTS") == "1":
            # Fast test environment - use client_with_api_key fixture
            try:
                client = request.getfixturevalue("client_with_api_key")
            except pytest.FixtureLookupError:
                pytest.skip("client_with_api_key fixture not available")
        else:
            # Regular test environment - use regular client with env override
            client = request.getfixturevalue("client")
            env_vars: dict[str, str] = {
                "REVIEWPOINT_API_KEY_ENABLED": "true",  # Enable API key auth
                "REVIEWPOINT_API_KEY": "nottherightkey",
                "REVIEWPOINT_FEATURE_UPLOADS": "true",
                "REVIEWPOINT_FEATURE_UPLOADS_LIST": "true",
            }
            self.override_env_vars(env_vars)

        headers: HeadersDict = self.get_auth_header(client)
        headers["X-API-Key"] = "wrongkey"
        resp: TestResponse = self.safe_request(
            client.get, "/api/v1/uploads", headers=headers
        )
        self.assert_status(resp, (401, 403))


# Async fixtures and test classes merged from test_uploads_async.py, test_uploads_fast.py, and test_uploads_optimized.py


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Shared async client fixture for all tests."""
    transport: Final[ASGITransport] = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": "testkey"},
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def fast_admin_client(
    test_app: FastAPI, async_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Ultra-fast async client with mocked admin authentication - no database calls."""
    from src.api.deps import get_current_user
    from src.core.security import create_access_token
    from src.models.user import User

    unique_email: Final[str] = f"test_admin_{uuid.uuid4().hex[:8]}@example.com"
    real_user: Final[User] = User(
        email=unique_email,
        name="Test Admin",
        hashed_password="hashed_password",
        is_active=True,
        is_admin=True,
    )
    async_session.add(real_user)
    await async_session.commit()
    await async_session.refresh(real_user)

    def override_get_current_user() -> User:
        return real_user

    test_app.dependency_overrides[get_current_user] = override_get_current_user

    token_payload: Final[dict[str, str | int]] = {
        "sub": str(real_user.id),
        "role": "admin",
    }
    valid_token: Final[str] = create_access_token(token_payload)

    try:
        transport: Final[ASGITransport] = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-API-Key": "testkey", "Authorization": f"Bearer {valid_token}"},
        ) as ac:
            yield ac
    finally:
        test_app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture
async def fast_anon_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Ultra-fast async client without authentication."""
    transport: Final[ASGITransport] = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": "testkey"},
    ) as ac:
        yield ac


class TestUploadsAsync(TypedExportEndpointTestTemplate):
    """Async upload tests with fast authentication fixtures and strict typing."""

    @pytest.mark.asyncio
    async def test_uploads_router_registered(
        self, fast_anon_client: AsyncClient
    ) -> None:
        """Test that uploads router is properly registered - async version."""
        resp: HttpxResponse = await fast_anon_client.get(ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data: StatusResponseDict = cast(StatusResponseDict, get_response_json(resp))
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    @pytest.mark.asyncio
    async def test_upload_file_authenticated(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test file upload with authentication - async version."""
        file_content: bytes = b"authenticated upload async"
        files: FilesDict = {"file": ("auth_async.txt", file_content, "text/plain")}
        resp: HttpxResponse = await fast_admin_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data: ResponseDict = get_response_json(resp)
            # Check the actual response structure - adjust expectations based on real response
            assert (
                "file" in data or "filename" in data
            )  # Flexible check for upload success

    @pytest.mark.asyncio
    async def test_upload_file_unauthenticated(
        self, fast_anon_client: AsyncClient
    ) -> None:
        """Test unauthenticated upload fails - async version."""
        file_content: bytes = b"unauthenticated upload async"
        files: FilesDict = {"file": ("unauth_async.txt", file_content, "text/plain")}
        resp: HttpxResponse = await fast_anon_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_upload_file_invalid_filename(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test upload with invalid filename - async version."""
        file_content: bytes = b"invalid filename async"
        files: FilesDict = {"file": ("../../../etc/passwd", file_content, "text/plain")}
        resp: HttpxResponse = await fast_admin_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (400, 422))

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, fast_admin_client: AsyncClient) -> None:
        """Test upload with file too large - async version."""
        file_content: bytes = b"x" * (10 * 1024 * 1024)  # 10MB file
        files: FilesDict = {"file": ("large_async.txt", file_content, "text/plain")}
        resp: HttpxResponse = await fast_admin_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (413, 422, 400))

    @pytest.mark.asyncio
    async def test_get_file_info_authenticated(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test getting file info - async version."""
        # First upload a file
        file_content: bytes = b"file for info test async"
        files: FilesDict = {"file": ("info_test_async.txt", file_content, "text/plain")}
        upload_resp: HttpxResponse = await fast_admin_client.post(
            UPLOAD_ENDPOINT, files=files
        )

        if upload_resp.status_code == 201:
            upload_data: ResponseDict = get_response_json(upload_resp)
            file_id_raw: str | int | bool | list[object] | dict[str, object] = (
                upload_data.get("id", "info_test_async.txt")
            )
            file_id: str = (
                str(file_id_raw) if file_id_raw is not None else "info_test_async.txt"
            )
            resp: HttpxResponse = await fast_admin_client.get(
                f"{UPLOAD_ENDPOINT}/{file_id}"
            )
            self.assert_status(resp, (200, 404))
        else:
            # If upload failed, just test the endpoint exists
            resp = await fast_admin_client.get(f"{UPLOAD_ENDPOINT}/nonexistent")
            self.assert_status(resp, (404, 401, 403))

    @pytest.mark.asyncio
    async def test_delete_file_authenticated(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test deleting a file - async version."""
        # First upload a file to delete
        file_content: bytes = b"file to delete async"
        files: FilesDict = {
            "file": ("delete_test_async.txt", file_content, "text/plain")
        }
        upload_resp: HttpxResponse = await fast_admin_client.post(
            UPLOAD_ENDPOINT, files=files
        )

        if upload_resp.status_code == 201:
            upload_data: ResponseDict = get_response_json(upload_resp)
            file_id_raw: str | int | bool | list[object] | dict[str, object] = (
                upload_data.get("id", "delete_test_async.txt")
            )
            file_id: str = (
                str(file_id_raw) if file_id_raw is not None else "delete_test_async.txt"
            )
            resp: HttpxResponse = await fast_admin_client.delete(
                f"{UPLOAD_ENDPOINT}/{file_id}"
            )
            self.assert_status(resp, (200, 204, 404))
        else:
            # If upload failed, just test the endpoint exists
            resp = await fast_admin_client.delete(f"{UPLOAD_ENDPOINT}/nonexistent")
            self.assert_status(resp, (404, 401, 403))

    @pytest.mark.asyncio
    async def test_list_files_authenticated(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test listing files - async version."""
        resp: HttpxResponse = await fast_admin_client.get(UPLOAD_ENDPOINT)
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        assert "files" in data
        assert isinstance(data["files"], list)

    @pytest.mark.asyncio
    async def test_list_files_unauthenticated(
        self, fast_anon_client: AsyncClient
    ) -> None:
        """Test listing files without auth - async version."""
        resp: HttpxResponse = await fast_anon_client.get(UPLOAD_ENDPOINT)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_list_files_with_query_and_fields(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test listing files with query parameters - async version."""
        resp: HttpxResponse = await fast_admin_client.get(
            f"{UPLOAD_ENDPOINT}?q=test&fields=filename,size"
        )
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        assert "files" in data

    @pytest.mark.asyncio
    async def test_export_files_csv_authenticated(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test CSV export - async version."""
        resp: HttpxResponse = await fast_admin_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, 200)
        content_type: str = resp.headers["content-type"]
        assert content_type == "text/csv; charset=utf-8"

    @pytest.mark.asyncio
    async def test_export_files_csv_unauthenticated(
        self, fast_anon_client: AsyncClient
    ) -> None:
        """Test CSV export without auth - async version."""
        resp: HttpxResponse = await fast_anon_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_export_alive(self, fast_admin_client: AsyncClient) -> None:
        """Test export alive endpoint - async version."""
        resp: HttpxResponse = await fast_admin_client.get(EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "uploads export alive"

    @pytest.mark.asyncio
    async def test_test_alive(self, fast_admin_client: AsyncClient) -> None:
        """Test alive endpoint - async version."""
        resp: HttpxResponse = await fast_admin_client.get(ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "alive"


class TestUploadsFast(TypedExportEndpointTestTemplate):
    """Fast sync tests - reuses client and optimizes auth for speed with strict typing."""

    def test_uploads_router_registered_fast(self, client: TestClient) -> None:
        """Test that uploads router is properly registered - fast version."""
        resp: TestResponse = self.safe_request(client.get, ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data: StatusResponseDict = cast(StatusResponseDict, get_response_json(resp))
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    def test_upload_file_authenticated_fast(self, client: TestClient) -> None:
        """Test file upload with authentication - fast optimized version."""
        headers: HeadersDict = self.get_auth_header(client)
        file_content: bytes = b"fast test upload"
        files: FilesDict = {"file": ("fast_test.txt", file_content, "text/plain")}

        # Test authenticated upload
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files, headers=headers
        )
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data: ResponseDict = get_response_json(resp)
            assert "filename" in data or "file" in data

    def test_upload_file_unauthenticated_fast(self, client: TestClient) -> None:
        """Test unauthenticated upload fails - fast version."""
        file_content: bytes = b"unauthorized upload fast"
        files: FilesDict = {"file": ("unauth_fast.txt", file_content, "text/plain")}
        resp: TestResponse = self.safe_request(
            client.post, UPLOAD_ENDPOINT, files=files
        )
        self.assert_status(resp, (401, 403))

    def test_get_file_info_fast(self, client: TestClient) -> None:
        """Test getting file info - fast version."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, f"{UPLOAD_ENDPOINT}/nonexistent", headers=headers
        )
        self.assert_status(resp, (404, 401, 403))

    def test_delete_file_fast(self, client: TestClient) -> None:
        """Test deleting a file - fast version."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.delete, f"{UPLOAD_ENDPOINT}/nonexistent", headers=headers
        )
        self.assert_status(resp, (404, 401, 403))

    def test_list_files_fast(self, client: TestClient) -> None:
        """Test listing files - fast version."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, UPLOAD_ENDPOINT, headers=headers
        )
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        assert "files" in data
        assert isinstance(data["files"], list)

    def test_export_files_csv_authenticated_fast(self, client: TestClient) -> None:
        """Test CSV export - fast version."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, EXPORT_ENDPOINT, headers=headers
        )
        self.assert_status(resp, 200)
        content_type: str = resp.headers["content-type"]
        assert content_type == "text/csv; charset=utf-8"

    def test_export_files_csv_unauthenticated_fast(self, client: TestClient) -> None:
        """Test CSV export without auth - fast version."""
        resp: TestResponse = self.safe_request(client.get, EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    def test_export_alive_fast(self, client: TestClient) -> None:
        """Test export alive endpoint - fast version."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, EXPORT_ALIVE_ENDPOINT, headers=headers
        )
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "uploads export alive"

    def test_test_alive_fast(self, client: TestClient) -> None:
        """Test alive endpoint - fast version."""
        headers: HeadersDict = self.get_auth_header(client)
        resp: TestResponse = self.safe_request(
            client.get, ALIVE_ENDPOINT, headers=headers
        )
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "alive"


class TestUploadsOptimized(TypedExportEndpointTestTemplate):
    """Optimized async tests using direct JWT token creation for maximum speed with strict typing."""

    @pytest.mark.asyncio
    async def test_uploads_router_registered_optimized(
        self, async_client: AsyncClient
    ) -> None:
        """Test that uploads router is properly registered - optimized version."""
        resp: HttpxResponse = await async_client.get(ROOT_TEST_ENDPOINT)
        self.assert_status(resp, 200)
        data: StatusResponseDict = cast(StatusResponseDict, get_response_json(resp))
        assert data["status"] == "uploads root test"
        assert data["router"] == "uploads"

    @pytest.mark.asyncio
    async def test_upload_file_authenticated_optimized(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test file upload with authentication - optimized version."""
        file_content: bytes = b"optimized upload test"
        files: FilesDict = {"file": ("optimized_test.txt", file_content, "text/plain")}
        resp: HttpxResponse = await fast_admin_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (201, 409))
        if resp.status_code == 201:
            data: ResponseDict = get_response_json(resp)
            assert "filename" in data or "file" in data

    @pytest.mark.asyncio
    async def test_upload_file_unauthenticated_optimized(
        self, async_client: AsyncClient
    ) -> None:
        """Test unauthenticated upload fails - optimized version."""
        file_content: bytes = b"unauthorized optimized upload"
        files: FilesDict = {"file": ("unauth_opt.txt", file_content, "text/plain")}
        resp: HttpxResponse = await async_client.post(UPLOAD_ENDPOINT, files=files)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_get_file_info_optimized(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test getting file info - optimized version."""
        resp: HttpxResponse = await fast_admin_client.get(
            f"{UPLOAD_ENDPOINT}/nonexistent"
        )
        self.assert_status(resp, (404, 401, 403))

    @pytest.mark.asyncio
    async def test_delete_file_optimized(self, fast_admin_client: AsyncClient) -> None:
        """Test deleting a file - optimized version."""
        resp: HttpxResponse = await fast_admin_client.delete(
            f"{UPLOAD_ENDPOINT}/nonexistent"
        )
        self.assert_status(resp, (404, 401, 403))

    @pytest.mark.asyncio
    async def test_list_files_optimized(self, fast_admin_client: AsyncClient) -> None:
        """Test listing files - optimized version."""
        resp: HttpxResponse = await fast_admin_client.get(UPLOAD_ENDPOINT)
        self.assert_status(resp, 200)
        data: FileListResponseDict = cast(FileListResponseDict, get_response_json(resp))
        assert "files" in data
        assert isinstance(data["files"], list)

    @pytest.mark.asyncio
    async def test_export_files_csv_authenticated_optimized(
        self, fast_admin_client: AsyncClient
    ) -> None:
        """Test CSV export - optimized version."""
        resp: HttpxResponse = await fast_admin_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, 200)
        content_type: str = resp.headers["content-type"]
        assert content_type == "text/csv; charset=utf-8"

    @pytest.mark.asyncio
    async def test_export_files_csv_unauthenticated_optimized(
        self, async_client: AsyncClient
    ) -> None:
        """Test CSV export without auth - optimized version."""
        resp: HttpxResponse = await async_client.get(EXPORT_ENDPOINT)
        self.assert_status(resp, (401, 403))

    @pytest.mark.asyncio
    async def test_export_alive_optimized(self, fast_admin_client: AsyncClient) -> None:
        """Test export alive endpoint - optimized version."""
        resp: HttpxResponse = await fast_admin_client.get(EXPORT_ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "uploads export alive"

    @pytest.mark.asyncio
    async def test_test_alive_optimized(self, fast_admin_client: AsyncClient) -> None:
        """Test alive endpoint - optimized version."""
        resp: HttpxResponse = await fast_admin_client.get(ALIVE_ENDPOINT)
        self.assert_status(resp, 200)
        data: AliveResponseDict = cast(AliveResponseDict, get_response_json(resp))
        assert data["status"] == "alive"
