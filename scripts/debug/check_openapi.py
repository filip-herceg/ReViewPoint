#!/usr/bin/env python3
"""Script to check the current OpenAPI schema implementation"""

import os

# Set required environment variables
os.environ["REVIEWPOINT_DB_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["REVIEWPOINT_SECRET_KEY"] = "test-secret-key"
os.environ["REVIEWPOINT_ENVIRONMENT"] = "test"

# Add backend to path
import sys

sys.path.insert(0, "../../backend/src")

from src.main import app


def main() -> dict[str, object]:
    """Check OpenAPI schema implementation"""
    # Get the OpenAPI schema
    schema = app.openapi()

    print("=== OpenAPI Schema Overview ===")
    info = schema.get("info", {})
    print(f"Title: {info.get('title')}")
    print(f"Version: {info.get('version')}")
    print(f"Description Length: {len(info.get('description', ''))} chars")
    print(f"Number of paths: {len(schema.get('paths', {}))}")
    print(f"Number of servers: {len(schema.get('servers', []))}")

    components = schema.get("components", {})
    security_schemes = components.get("securitySchemes", {})
    print(f"Security schemes: {list(security_schemes.keys())}")

    tags = schema.get("tags", [])
    print(f"Tags: {[tag['name'] for tag in tags]}")

    # Check if contact and license are present
    print(f"Has contact info: {'contact' in info}")
    print(f"Has license info: {'license' in info}")

    # Check specific paths
    paths = schema.get("paths", {})
    auth_paths = [p for p in paths.keys() if "/auth" in p]
    user_paths = [p for p in paths.keys() if "/users" in p]
    upload_paths = [p for p in paths.keys() if "/uploads" in p]
    health_paths = [p for p in paths.keys() if "/health" in p]

    print(f"Auth endpoints: {len(auth_paths)}")
    print(f"User endpoints: {len(user_paths)}")
    print(f"Upload endpoints: {len(upload_paths)}")
    print(f"Health endpoints: {len(health_paths)}")

    # Check if security is properly configured
    has_global_security = "security" in schema
    print(f"Has global security: {has_global_security}")

    # Check examples in components
    examples = components.get("examples", {})
    print(f"Number of examples: {len(examples)}")

    # Check for code samples in some endpoints
    has_code_samples = False
    for _path, methods in paths.items():
        for _method, operation in methods.items():
            if isinstance(operation, dict) and "x-codeSamples" in operation:
                has_code_samples = True
                break
        if has_code_samples:
            break

    print(f"Has code samples: {has_code_samples}")

    # Check for proper response examples
    has_response_examples = False
    for _path, methods in paths.items():
        for _method, operation in methods.items():
            if isinstance(operation, dict):
                responses = operation.get("responses", {})
                for _status, response in responses.items():
                    if isinstance(response, dict):
                        content = response.get("content", {})
                        for _media_type, media_info in content.items():
                            if (
                                isinstance(media_info, dict)
                                and "examples" in media_info
                            ):
                                has_response_examples = True
                                break
                        if has_response_examples:
                            break
                if has_response_examples:
                    break
        if has_response_examples:
            break

    print(f"Has response examples: {has_response_examples}")

    print("\n=== Servers Configuration ===")
    for server in schema.get("servers", []):
        print(f"- {server.get('url')}: {server.get('description')}")

    print("\n=== Security Schemes ===")
    for scheme_name, scheme in security_schemes.items():
        print(
            f"- {scheme_name}: {scheme.get('type')} ({scheme.get('description', 'No description')[:50]}...)",
        )

    return schema


if __name__ == "__main__":
    main()
