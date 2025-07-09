"""
Tests for the OpenAPI documentation module

This module tests the comprehensive documentation configuration,
schema enhancement, and code sample generation.
"""

import pytest
from fastapi.testclient import TestClient

from src.core.documentation import (
    API_INFO,
    CODE_SAMPLES,
    EXAMPLE_AUTH_RESPONSE,
    EXAMPLE_FILE,
    EXAMPLE_USER,
    PUBLIC_ENDPOINTS,
    SECURITY_SCHEMES,
    SERVERS,
    TAGS,
    get_enhanced_openapi_schema,
)


class TestDocumentationModule:
    """Test the documentation module configuration and functions."""

    def test_api_info_structure(self) -> None:
        """Test that API info contains all required fields."""
        assert "title" in API_INFO
        assert "description" in API_INFO
        assert "version" in API_INFO
        assert "contact" in API_INFO
        assert "license" in API_INFO
        assert "terms_of_service" in API_INFO

        # Check contact info
        contact = API_INFO["contact"]
        assert "name" in contact
        assert "url" in contact
        assert "email" in contact
        assert contact["email"].endswith("@reviewpoint.org")

        # Check license info
        license_info = API_INFO["license"]
        assert "name" in license_info
        assert "url" in license_info
        assert license_info["name"] == "MIT License"

    def test_servers_configuration(self) -> None:
        """Test that servers are properly configured for different environments."""
        assert len(SERVERS) >= 3  # Production, staging, local

        from urllib.parse import urlparse

        server_urls = [server["url"] for server in SERVERS]
        assert any(
            urlparse(url).hostname
            and urlparse(url).hostname.lower() == "api.reviewpoint.org"
            for url in server_urls
        )  # Production
        assert any(
            urlparse(url).hostname and urlparse(url).hostname.lower() == "localhost"
            for url in server_urls
        )  # Local

        # Each server should have description and variables
        for server in SERVERS:
            assert "url" in server
            assert "description" in server
            assert "variables" in server

    def test_security_schemes(self) -> None:
        """Test that all security schemes are properly configured."""
        assert "BearerAuth" in SECURITY_SCHEMES
        assert "ApiKeyAuth" in SECURITY_SCHEMES
        assert "OAuth2PasswordBearer" in SECURITY_SCHEMES

        # Test Bearer Auth scheme
        bearer_auth = SECURITY_SCHEMES["BearerAuth"]
        assert bearer_auth.get("type") == "http"
        assert bearer_auth.get("scheme") == "bearer"
        assert bearer_auth.get("bearerFormat") == "JWT"
        assert "description" in bearer_auth

        # Test API Key scheme
        api_key_auth = SECURITY_SCHEMES["ApiKeyAuth"]
        assert api_key_auth.get("type") == "apiKey"
        assert api_key_auth.get("in_") == "header"
        assert api_key_auth.get("name") == "X-API-Key"

        # Test OAuth2 scheme
        oauth2_auth = SECURITY_SCHEMES["OAuth2PasswordBearer"]
        assert oauth2_auth.get("type") == "oauth2"
        assert "flows" in oauth2_auth
        assert "password" in oauth2_auth.get("flows", {})

    def test_tags_configuration(self) -> None:
        """Test that endpoint tags are properly configured."""
        tag_names = [tag["name"] for tag in TAGS]

        expected_tags = ["Auth", "User Management", "File", "Health", "WebSocket"]
        for expected_tag in expected_tags:
            assert expected_tag in tag_names

        # Each tag should have description and external docs
        for tag in TAGS:
            assert "name" in tag
            assert "description" in tag
            assert "externalDocs" in tag
            assert "url" in tag["externalDocs"]

    def test_public_endpoints(self) -> None:
        """Test that public endpoints are correctly identified."""
        # public_paths = [endpoint[0] for endpoint in PUBLIC_ENDPOINTS]  # unused

        # Auth endpoints should be public
        assert ("/api/v1/auth/login", "post") in PUBLIC_ENDPOINTS
        assert ("/api/v1/auth/register", "post") in PUBLIC_ENDPOINTS

        # Health endpoints should be public
        assert ("/api/v1/health", "get") in PUBLIC_ENDPOINTS

        # Documentation endpoints should be public
        assert ("/docs", "get") in PUBLIC_ENDPOINTS
        assert ("/openapi.json", "get") in PUBLIC_ENDPOINTS

    def test_example_data_structure(self) -> None:
        """Test that example data has proper structure."""
        # Test user example
        assert "id" in EXAMPLE_USER
        assert "email" in EXAMPLE_USER
        assert "name" in EXAMPLE_USER
        assert "created_at" in EXAMPLE_USER
        assert isinstance(EXAMPLE_USER["id"], int)

        # Test file example
        assert "id" in EXAMPLE_FILE
        assert "filename" in EXAMPLE_FILE
        assert "content_type" in EXAMPLE_FILE
        assert "size" in EXAMPLE_FILE
        assert "md5_hash" in EXAMPLE_FILE

        # Test auth response example
        assert "access_token" in EXAMPLE_AUTH_RESPONSE
        assert "refresh_token" in EXAMPLE_AUTH_RESPONSE
        assert "token_type" in EXAMPLE_AUTH_RESPONSE
        assert "user" in EXAMPLE_AUTH_RESPONSE

    def test_code_samples(self) -> None:
        """Test that code samples are available for key operations."""
        assert "auth_login" in CODE_SAMPLES
        assert "file_upload" in CODE_SAMPLES

        # Each code sample should have multiple languages
        for operation, samples in CODE_SAMPLES.items():
            # WebSocket operations don't have curl samples
            if operation != "websocket_connection":
                assert "curl" in samples
            assert "python" in samples
            assert "javascript" in samples

            # Each sample should be non-empty
            for _lang, code in samples.items():
                assert len(code.strip()) > 0
                # Check for API domain or localhost in the code using proper URL parsing
                from urllib.parse import urlparse

                def has_valid_domain(code_sample: str) -> bool:
                    import re

                    urls = re.findall(r'https?://[^\s"\']+', code_sample)
                    for url in urls:
                        hostname = urlparse(url).hostname
                        if hostname and hostname.lower() in (
                            "api.reviewpoint.org",
                            "localhost",
                        ):
                            return True
                    return False

                assert has_valid_domain(code)

    def test_enhanced_schema_generation(self) -> None:
        """Test the enhanced OpenAPI schema generation."""
        # Create a minimal base schema
        base_schema = {
            "openapi": "3.0.2",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/api/v1/auth/login": {
                    "post": {
                        "summary": "Login",
                        "operationId": "login",
                        "responses": {"200": {"description": "Success"}},
                    }
                },
                "/api/v1/users": {
                    "get": {
                        "summary": "List users",
                        "operationId": "list_users",
                        "responses": {"200": {"description": "Success"}},
                    }
                },
            },
        }

        # Enhance the schema
        enhanced_schema = get_enhanced_openapi_schema(base_schema)

        # Verify enhancements
        assert "contact" in enhanced_schema["info"]
        assert "license" in enhanced_schema["info"]
        assert "servers" in enhanced_schema
        assert "components" in enhanced_schema
        assert "securitySchemes" in enhanced_schema["components"]
        assert "security" in enhanced_schema
        assert "tags" in enhanced_schema

        # Verify endpoint enhancements
        paths = enhanced_schema["paths"]

        # Login endpoint should be public (no auth required)
        login_endpoint = paths["/api/v1/auth/login"]["post"]
        assert login_endpoint["security"] == []
        assert "Auth" in login_endpoint.get("tags", [])

        # Users endpoint should require auth
        users_endpoint = paths["/api/v1/users"]["get"]
        assert len(users_endpoint.get("security", [])) > 0
        assert "User Management" in users_endpoint.get("tags", [])

    def test_schema_enhancement_error_handling(self) -> None:
        """Test that schema enhancement handles malformed input gracefully."""
        # Test with empty schema
        empty_schema: dict[str, object] = {}
        enhanced = get_enhanced_openapi_schema(empty_schema)
        assert "info" in enhanced

        # Test with malformed paths
        malformed_schema = {"paths": "not_a_dict"}
        enhanced = get_enhanced_openapi_schema(malformed_schema)
        assert "info" in enhanced

    def test_documentation_content_quality(self) -> None:
        """Test that documentation content meets quality standards."""
        # API description should be comprehensive
        description = API_INFO["description"]
        assert len(description) > 500  # Should be detailed
        assert "authentication" in description.lower()
        assert "file" in description.lower()
        assert "user" in description.lower()

        # Tag descriptions should be informative
        for tag in TAGS:
            desc = tag["description"]
            assert len(desc) > 100  # Should be detailed
            assert "**" in desc  # Should use markdown formatting

    def test_security_documentation(self) -> None:
        """Test that security documentation is comprehensive."""
        for scheme_name, scheme in SECURITY_SCHEMES.items():
            assert "description" in scheme
            desc = scheme["description"]
            assert len(desc) > 50  # Should be detailed

            if scheme_name == "BearerAuth":
                assert "JWT" in desc
                assert "token" in desc.lower()
            elif scheme_name == "ApiKeyAuth":
                assert "X-API-Key" in desc
                assert "header" in desc.lower()

    def test_code_sample_quality(self) -> None:
        """Test that code samples are high quality and functional."""
        for operation, samples in CODE_SAMPLES.items():
            for lang, code in samples.items():
                # Should include proper API endpoint
                assert "/api/v1/" in code

                # Should include authentication (except for auth endpoints, health checks, and websocket)
                if operation not in (
                    "health_check",
                    "auth_login",
                    "websocket_connection",
                ):
                    assert any(
                        auth in code
                        for auth in [
                            "Bearer",
                            "X-API-Key",
                            "Authorization",
                            "YOUR_JWT_TOKEN",
                        ]
                    )

                # Language-specific checks
                if lang == "curl":
                    assert "curl" in code
                    assert "-X" in code or "--request" in code
                elif lang == "python":
                    assert "import" in code
                    # WebSocket samples use different libraries
                    if operation == "websocket_connection":
                        assert "websockets" in code or "asyncio" in code
                    else:
                        assert "requests" in code or "httpx" in code
                elif lang == "javascript":
                    # WebSocket samples use WebSocket API, others use fetch/axios
                    if operation == "websocket_connection":
                        assert "WebSocket" in code or "ws" in code
                    else:
                        assert "fetch" in code or "axios" in code
                        assert "await" in code or "then" in code


class TestOpenAPIIntegration:
    """Test OpenAPI documentation integration with FastAPI."""

    def test_documentation_endpoints_accessible(self) -> None:
        """Test that documentation endpoints are accessible."""
        from src.main import app

        client = TestClient(app)

        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Verify enhanced schema is being used
        assert "contact" in schema["info"]
        assert "license" in schema["info"]
        assert len(schema["servers"]) > 1
        assert "securitySchemes" in schema["components"]

    def test_swagger_ui_accessible(self) -> None:
        """Test that Swagger UI is accessible and properly configured."""
        from src.main import app

        client = TestClient(app)

        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        content = response.text

        # Should include custom title and configuration
        assert "ReViewPoint API Docs" in content
        assert "swagger-ui" in content.lower()

    def test_redoc_accessible(self) -> None:
        """Test that ReDoc is accessible."""
        from src.main import app

        client = TestClient(app)

        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        content = response.text

        assert "redoc" in content.lower()
        assert "ReViewPoint" in content

    def test_enhanced_endpoint_documentation(self) -> None:
        """Test that endpoints have enhanced documentation."""
        from src.main import app

        client = TestClient(app)

        response = client.get("/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        # Test auth endpoints
        auth_paths = [path for path in paths.keys() if "/auth" in path]
        assert len(auth_paths) > 0

        for path in auth_paths:
            path_item = paths[path]
            for _method, operation in path_item.items():
                if isinstance(operation, dict):
                    assert "tags" in operation
                    assert "Auth" in operation["tags"]

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/uploads",
            "/api/v1/health",
        ],
    )
    def test_endpoint_has_proper_documentation(self, endpoint: str) -> None:
        """Test that specific endpoints have proper documentation."""
        from src.main import app

        client = TestClient(app)

        response = client.get("/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        if endpoint in paths:
            path_item = paths[endpoint]

            # Should have at least one method documented
            assert len(path_item) > 0

            for _method, operation in path_item.items():
                if isinstance(operation, dict):
                    # Should have summary and description
                    assert "summary" in operation

                    # Should have proper tags
                    assert "tags" in operation
                    assert len(operation["tags"]) > 0

                    # Should have responses
                    assert "responses" in operation
                    assert len(operation["responses"]) > 0
