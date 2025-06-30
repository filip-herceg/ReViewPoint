import pytest
from tests.test_templates import OpenAPITestTemplate


class TestOpenAPI(OpenAPITestTemplate):
    @pytest.mark.parametrize(
        "path,method,summary,status_code",
        [
            ("/api/v1/auth/register", "post", "Register a new user", 201),
            ("/api/v1/auth/login", "post", "User login", 200),
            ("/api/v1/auth/logout", "post", "User logout", 200),
            ("/api/v1/users/me", "get", "Get current user", 200),
            ("/api/v1/users", "get", "List users", 200),
            ("/api/v1/users/{user_id}", "get", "Get user by ID", 200),
            ("/api/v1/uploads", "get", "List uploads", 200),
            ("/api/v1/uploads", "post", "Upload file", 201),
            ("/api/v1/health", "get", "Health check", 200),
        ],
    )
    def test_endpoint_docs(
        self, path: str, method: str, summary: str, status_code: int
    ):
        self.assert_endpoint_doc(path, method, summary, status_code)

    def test_openapi_metadata(self):
        resp = self.client.get("/openapi.json")
        self.assert_openapi_metadata(resp)

    def test_docs_accessible(self):
        self.assert_docs_accessible()

    def test_missing_endpoint(self):
        self.assert_endpoint_missing("/api/v1/doesnotexist")

    def test_invalid_docs(self):
        self.assert_invalid_docs("/not-a-docs-url")

    def test_openapi_schema_valid(self):
        self.validate_openapi_schema()
