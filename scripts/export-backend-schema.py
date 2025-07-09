#!/usr/bin/env python3
"""
Backend OpenAPI Schema Export Script

This script exports the FastAPI OpenAPI schema to a JSON file for frontend type generation.
It reads the backend application and generates a complete OpenAPI 3.0 schema file.

Usage:
    python scripts/export-backend-schema.py

Output:
    frontend/openapi-schema.json - Complete OpenAPI schema for type generation
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add backend src to Python path
backend_root = Path(__file__).parent.parent / "backend"
backend_src = backend_root / "src"
sys.path.insert(0, str(backend_src))

try:
    from fastapi.openapi.utils import get_openapi
    from main import app  # Import the FastAPI app instance
except ImportError as e:
    print(f"Error: Could not import backend modules: {e}")
    print(
        "Make sure you're running this from the project root and backend dependencies are installed."
    )
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def export_openapi_schema() -> None:
    """
    Export OpenAPI schema from FastAPI app to JSON file.

    Raises:
        Exception: If schema export fails
    """
    try:
        logger.info("Starting OpenAPI schema export...")

        # Generate OpenAPI schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )

        # Ensure schema has required sections
        if not openapi_schema.get("components", {}).get("schemas"):
            logger.warning("No schemas found in OpenAPI specification")

        if not openapi_schema.get("paths"):
            logger.warning("No paths found in OpenAPI specification")

        # Output file path
        output_file = Path(__file__).parent.parent / "frontend" / "openapi-schema.json"
        output_file.parent.mkdir(exist_ok=True)

        # Write schema to file with pretty formatting
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

        # Log summary statistics
        schemas_count = len(openapi_schema.get("components", {}).get("schemas", {}))
        paths_count = len(openapi_schema.get("paths", {}))

        logger.info(f"✅ OpenAPI schema exported successfully to: {output_file}")
        logger.info(f"📊 Exported {schemas_count} schemas and {paths_count} paths")

        # Validate critical schemas exist
        required_schemas = ["UserProfile", "FileSchema", "ApiError"]
        available_schemas = (
            openapi_schema.get("components", {}).get("schemas", {}).keys()
        )

        missing_schemas = [
            schema for schema in required_schemas if schema not in available_schemas
        ]
        if missing_schemas:
            logger.warning(f"⚠️  Missing expected schemas: {missing_schemas}")
        else:
            logger.info("✅ All expected schemas present")

    except Exception as e:
        logger.error(f"❌ OpenAPI schema export failed: {e}")
        raise


def validate_schema_structure(schema: Dict[str, Any]) -> bool:
    """
    Validate that the exported schema has the expected structure.

    Args:
        schema: The OpenAPI schema dictionary

    Returns:
        True if schema is valid, False otherwise
    """
    required_keys = ["openapi", "info", "paths"]

    for key in required_keys:
        if key not in schema:
            logger.error(f"Missing required key in schema: {key}")
            return False

    if not isinstance(schema.get("paths"), dict):
        logger.error("Paths section is not a dictionary")
        return False

    return True


def main() -> None:
    """Main entry point for the script."""
    try:
        logger.info("🚀 Starting backend OpenAPI schema export")
        export_openapi_schema()
        logger.info("🎉 Schema export completed successfully")

    except KeyboardInterrupt:
        logger.info("❌ Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
