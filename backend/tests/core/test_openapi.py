from typing import Final, Literal

import httpx
import pytest

from tests.test_templates import OpenAPITestTemplate

# Test data constants with proper typing
_ENDPOINT_TEST_CASES: Final[list[tuple[str, str, str, int]]] = [
    ("/api/v1/auth/register", "post", "Register a new user", 201),
    ("/api/v1/auth/login", "post", "User login", 200),
    ("/api/v1/auth/logout", "post", "Logout user", 200),
    ("/api/v1/auth/me", "get", "Get current user profile", 200),
    ("/api/v1/users", "get", "List users", 200),
    ("/api/v1/users/{user_id}", "get", "Get user by ID", 200),
    ("/api/v1/uploads", "get", "List all uploaded files", 200),
    ("/api/v1/uploads", "post", "Upload a file", 201),
    ("/api/v1/health", "get", "Health check", 200),
]


class TestOpenAPI(OpenAPITestTemplate):
    @pytest.mark.parametrize(
        "path,method,summary,status_code",
        _ENDPOINT_TEST_CASES,
    )
    def test_endpoint_docs(
        self, 
        path: str, 
        method: Literal["get", "post", "put", "delete", "patch"], 
        summary: str, 
        status_code: int
    ) -> None:
        """Test that each endpoint has correct OpenAPI documentation."""
        self.assert_endpoint_doc(path, method, summary, status_code)

    def test_openapi_metadata(self) -> None:
        """Test that OpenAPI metadata contains expected information."""
        resp: httpx.Response = self.client.get("/openapi.json")
        self.assert_openapi_metadata(resp)

    def test_docs_accessible(self) -> None:
        """Test that API documentation endpoints are accessible."""
        self.assert_docs_accessible()

    def test_missing_endpoint(self) -> None:
        """Test that non-existent endpoints are properly reported as missing."""
        self.assert_endpoint_missing("/api/v1/doesnotexist")

    def test_invalid_docs(self) -> None:
        """Test that invalid documentation URLs return 404."""
        self.assert_invalid_docs("/not-a-docs-url")

    def test_openapi_schema_valid(self) -> None:
        """Test that the OpenAPI schema is valid according to the OpenAPI specification."""
        self.validate_openapi_schema()
