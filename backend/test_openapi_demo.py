#!/usr/bin/env python3
"""Quick test to verify OpenAPI schema enhancement."""

import os

# Set minimal environment for testing
os.environ.update(
    {
        "REVIEWPOINT_DB_URL": "sqlite:///test.db",
        "REVIEWPOINT_SECRET_KEY": "test-secret-key-for-demo",
        "REVIEWPOINT_CORS_ORIGINS": '["http://localhost:3000"]',
        "REVIEWPOINT_FEATURE_FLAGS": "{}",
        "REVIEWPOINT_ENVIRONMENT": "test",
    }
)


def test_openapi_schema() -> bool:
    """Test that OpenAPI schema is properly enhanced."""
    try:
        from src.core.documentation import get_enhanced_openapi_schema

        # Mock base schema
        base_schema = {
            "openapi": "3.0.2",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
            "components": {},
        }

        # Enhance schema
        enhanced = get_enhanced_openapi_schema(base_schema)

        print("✅ OpenAPI Schema Enhancement Test")
        print(f"Title: {enhanced['info']['title']}")
        print(f"Version: {enhanced['info']['version']}")
        print(f"Description length: {len(enhanced['info']['description'])} chars")
        print(f"Contact: {enhanced['info']['contact']['name']}")
        print(f"License: {enhanced['info']['license']['name']}")
        print(f"Servers: {len(enhanced['servers'])} environments")
        print(f"Tags: {len(enhanced['tags'])} categories")
        print(
            f"Security schemes: {list(enhanced['components']['securitySchemes'].keys())}"
        )
        print(f"Examples: {list(enhanced['components']['examples'].keys())}")

        # Verify critical components
        assert "ReViewPoint" in enhanced["info"]["title"]
        assert "BearerAuth" in enhanced["components"]["securitySchemes"]
        assert "ApiKeyAuth" in enhanced["components"]["securitySchemes"]
        assert len(enhanced["tags"]) >= 5
        assert "UserExample" in enhanced["components"]["examples"]

        print("\n✅ All OpenAPI documentation enhancements verified!")
        return True
    except Exception as e:
        print(f"❌ Error testing OpenAPI schema: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> None:
    success: bool = test_openapi_schema()
    if not success:
        exit(1)
    print("\n🎉 OpenAPI documentation enhancement is working perfectly!")


if __name__ == "__main__":
    main()
