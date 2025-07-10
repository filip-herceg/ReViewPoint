# Export Backend Schema Script

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Type**           | Python Script                                                     |
| **Responsibility** | Export OpenAPI schema from running backend server                 |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

This script exports the OpenAPI schema from a running ReViewPoint backend server and saves it to a JSON file. This is used for API documentation generation, frontend type generation, and API contract validation.

## 2. Usage

```bash
# Export schema from running server
python scripts/export-backend-schema.py

# Export with custom output location
python scripts/export-backend-schema.py --output custom-schema.json

# Export from custom backend URL
python scripts/export-backend-schema.py --url http://localhost:8001
```

## 3. Configuration

### Default Settings
- **Backend URL**: `http://localhost:8000`
- **Output File**: `frontend/openapi-schema.json`
- **Schema Endpoint**: `/openapi.json`

### Command Line Options
- `--url`: Backend server URL (default: `http://localhost:8000`)
- `--output`: Output file path (default: `frontend/openapi-schema.json`)
- `--validate`: Validate schema after export
- `--pretty`: Pretty-print JSON output

## 4. Dependencies

- **requests**: HTTP client for API calls
- **json**: JSON processing
- **argparse**: Command line argument parsing

## 5. Integration

This script is typically run:
- As part of the build process
- When regenerating frontend API types
- During CI/CD pipeline for API validation
- When updating API documentation

## 6. Error Handling

- Validates backend server is running
- Checks schema endpoint accessibility
- Validates JSON schema format
- Provides clear error messages for common issues

## 7. Related

- [API Reference](../content/api-reference.md) - Complete API documentation
- [Frontend Type Generation](../frontend/scripts/generate-types-simple.js) - Uses exported schema
- [OpenAPI Configuration](../content/backend/src/core/openapi.py.md) - Backend schema configuration
