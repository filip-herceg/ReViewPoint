# api/v1/users/exports.py - User Data Export API

## Purpose

The `api/v1/users/exports.py` module provides comprehensive user data export
functionality for the ReViewPoint platform. It implements secure CSV export
capabilities with different data granularity levels, health checking endpoints,
and debugging utilities for user data reporting, analytics, and system
integration needs.

## Key Components

### Core Imports and Dependencies

#### Essential Export Dependencies

```python
"""
User export endpoints: CSV, health, and simple export endpoints.
"""

import csv
from collections.abc import Mapping, Sequence
from io import StringIO
from typing import Final, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict

from src.api.deps import get_current_user_with_export_api_key, require_feature
from src.core.database import get_async_session
from src.models.user import User
from src.repositories.user import list_users

router: Final[APIRouter] = APIRouter()
```

#### Type Definitions for Export Data

```python
class UserMinimalRow(TypedDict):
    id: int
    email: str
    name: str

class UserFullRow(TypedDict):
    id: int
    email: str
    name: str
    created_at: str
    updated_at: str
    is_active: bool
    is_admin: bool

class ExportAliveResponse(TypedDict):
    status: Literal["users export alive"]

class ExportSimpleResponse(TypedDict):
    users: Literal["export simple status"]

# Export file constants
CSV_EXPORT_FILENAME: Final[Literal["users_export.csv"]] = "users_export.csv"
CSV_FULL_EXPORT_FILENAME: Final[Literal["users_full_export.csv"]] = "users_full_export.csv"
```

### Minimal User Export

#### Basic CSV Export with Essential Data

````python
@router.get(
    "/export",
    summary="Export users as CSV (minimal format)",
    description="""
    Export user data in CSV format with minimal fields for basic reporting.

    **Requirements:**
    - Valid API key or export-specific API key
    - Feature flag 'users:export' must be enabled

    **Query Parameters:**
    - `email`: Filter export to specific email address
    - `format`: Export format (only 'csv' supported currently)

    **CSV Columns:**
    - `id`: User unique identifier
    - `email`: User email address
    - `name`: User display name

    **Response:**
    - Content-Type: text/csv
    - Content-Disposition: attachment; filename="users_export.csv"

    **Example Request:**
    ```
    GET /api/v1/users/export?format=csv&email=john@example.com
    ```

    **Example CSV Output:**
    ```csv
    id,email,name
    123,john.doe@example.com,John Doe
    456,jane.smith@example.com,Jane Smith
    ```

    **Use Cases:**
    - Basic user reporting
    - Data backup (minimal)
    - Third-party system integration
    - Quick user audits
    """,
    response_class=Response,
    responses={
        200: {
            "description": "CSV export successful",
            "content": {
                "text/csv": {
                    "example": "id,email,name\n123,john@example.com,John Doe\n" +
                               "456,jane@example.com,Jane Smith"
                }
            },
        },
        400: {"description": "Unsupported format or invalid parameters"},
        401: {"description": "Invalid or missing API key"},
        403: {"description": "Export feature not enabled"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management", "Export"],
    dependencies=[
        Depends(require_feature("users:export")),
    ],
)
async def export_users_csv(
    session: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(get_current_user_with_export_api_key),
    email: str | None = Query(None, description="Filter by specific email address"),
    format: str | None = Query("csv", description="Export format (only csv supported)"),
) -> Response:
    """
    Export users as CSV with minimal data for basic reporting needs.
    """
    # Validate format parameter
    if format is not None and format.lower() != "csv":
        raise HTTPException(
            status_code=400, detail="Unsupported format. Only 'csv' is supported."
        )

    # Query users from database
    users_data: Sequence[User]
    total_count: int
    users_data, total_count = await list_users(session)

    # Filter by email if provided
    if email is not None:
        users_data = [user for user in users_data if user.email == email]

    # Generate CSV
    output: StringIO = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(["id", "email", "name"])

    for user in users_data:
        csv_writer.writerow([user.id, user.email, user.name])

    csv_content: str = output.getvalue()

    # Add content-disposition header for file download
    headers: Mapping[str, str] = {
        "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}"
    }

    return Response(content=csv_content, media_type="text/csv", headers=dict(headers))
````

### Comprehensive User Export

#### Full CSV Export with Complete User Data

````python
@router.get(
    "/export-full",
    summary="Export users as CSV (complete format)",
    description="""
    Export comprehensive user data in CSV format with all available fields.

    **Requirements:**
    - Valid API key or export-specific API key
    - Feature flag 'users:export_full' must be enabled
    - Higher privilege level than minimal export

    **CSV Columns:**
    - `id`: User unique identifier
    - `email`: User email address
    - `name`: User display name
    - `created_at`: Account creation timestamp (ISO format)
    - `updated_at`: Last modification timestamp (ISO format)
    - `is_active`: Account active status (boolean)
    - `is_admin`: Admin privileges (boolean)

    **Response:**
    - Content-Type: text/csv
    - Content-Disposition: attachment; filename="users_full_export.csv"

    **Example Request:**
    ```
    GET /api/v1/users/export-full
    ```

    **Example CSV Output:**
    ```csv
    id,email,name,created_at,updated_at,is_active,is_admin
    123,john.doe@example.com,John Doe,2025-01-08T10:30:00Z,2025-01-08T15:45:00Z,true,false
    456,jane.smith@example.com,Jane Smith,2025-01-07T14:20:00Z,2025-01-08T09:15:00Z,true,true
    ```

    **Use Cases:**
    - Complete data backup
    - Detailed analytics and reporting
    - User account auditing
    - System migration
    - Compliance reporting
    """,
    response_class=Response,
    responses={
        200: {
            "description": "Full CSV export successful",
            "content": {
                "text/csv": {
                    "example": "id,email,name,created_at,updated_at," +
                               "is_active,is_admin\n" +
                               "123,john@example.com,John Doe," +
                               "2025-01-08T10:30:00Z," +
                               "2025-01-08T15:45:00Z,true,false"
                }
            },
        },
        401: {"description": "Invalid or missing API key"},
        403: {"description": "Export feature not enabled"},
        500: {"description": "Internal server error"},
    },
    tags=["User Management", "Export"],
    dependencies=[
        Depends(require_feature("users:export_full")),
    ],
)
async def export_users_full_csv(
    session: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(get_current_user_with_export_api_key),
) -> Response:
    """
    Export comprehensive user data as CSV with all available fields.
    """
    # Query users from database
    users_data: Sequence[User]
    total_count: int
    users_data, total_count = await list_users(session)

    # Generate CSV with full user data
    output: StringIO = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(
        ["id", "email", "name", "created_at", "updated_at", "is_active", "is_admin"]
    )

    for user in users_data:
        csv_writer.writerow(
            [
                user.id,
                user.email,
                user.name,
                user.created_at.isoformat() if user.created_at else "",
                user.updated_at.isoformat() if user.updated_at else "",
                user.is_active,
                user.is_admin,
            ]
        )

    csv_content: str = output.getvalue()

    # Add content-disposition header for file download
    headers: Mapping[str, str] = {
        "Content-Disposition": f"attachment; filename={CSV_FULL_EXPORT_FILENAME}"
    }

    return Response(content=csv_content, media_type="text/csv", headers=dict(headers))
````

### Health Check Endpoints

#### Export Service Health Monitoring

````python
EXPORT_ALIVE_STATUS: Final[Literal["users export alive"]] = "users export alive"

@router.get(
    "/export-alive",
    summary="Test export router health",
    description="""
    Health check endpoint for the user export router functionality.

    **Requirements:**
    - Feature flag 'users:export_alive' must be enabled
    - No authentication required (health check)

    **Response:**
    Returns a simple status message to confirm export endpoints are operational.

    **Example Response:**
    ```json
    {
        "status": "users export alive"
    }
    ```

    **Use Cases:**
    - Service health monitoring
    - Export feature availability testing
    - System diagnostics
    - Load balancer health checks
    """,
    responses={
        200: {
            "description": "Export router is operational",
            "content": {
                "application/json": {"example": {"status": "users export alive"}}
            },
        },
        403: {"description": "Export alive feature not enabled"},
    },
    tags=["Health", "Export"],
    dependencies=[
        Depends(require_feature("users:export_alive")),
    ],
)
async def export_alive() -> ExportAliveResponse:
    """
    Health check endpoint for export router functionality.
    """
    return {"status": EXPORT_ALIVE_STATUS}
````

#### Debug and Testing Endpoint

````python
EXPORT_SIMPLE_STATUS: Final[Literal["export simple status"]] = "export simple status"

@router.get(
    "/export-simple",
    summary="Simple export test endpoint",
    description="""
    Simple test endpoint for debugging export functionality.

    **Requirements:**
    - Feature flag 'users:export_simple' must be enabled
    - No authentication required (debug endpoint)

    **Response:**
    Returns a simple status message for debugging and testing purposes.

    **Example Response:**
    ```json
    {
        "users": "export simple status"
    }
    ```

    **Use Cases:**
    - Development and debugging
    - Feature flag testing
    - Export system diagnostics
    - Integration testing
    """,
    responses={
        200: {
            "description": "Simple export test successful",
            "content": {
                "application/json": {"example": {"users": "export simple status"}}
            },
        },
        403: {"description": "Export simple feature not enabled"},
    },
    tags=["Health", "Export"],
    dependencies=[
        Depends(require_feature("users:export_simple")),
    ],
)
async def export_simple() -> ExportSimpleResponse:
    """
    Simple test endpoint for debugging export functionality.
    """
    return {"users": EXPORT_SIMPLE_STATUS}
````

## Export Features and Capabilities

### CSV Generation Process

#### Efficient In-Memory CSV Creation

```python
# Standard CSV generation pattern across exports:

def generate_csv_export(users_data: Sequence[User], headers: list[str]) -> str:
    """Generate CSV content from user data."""
    output: StringIO = StringIO()
    csv_writer = csv.writer(output)

    # Write headers
    csv_writer.writerow(headers)

    # Write data rows
    for user in users_data:
        csv_writer.writerow([
            user.id,
            user.email,
            user.name,
            # Additional fields for full export
            user.created_at.isoformat() if (
                hasattr(user, 'created_at') and user.created_at
            ) else "",
            user.updated_at.isoformat() if (
                hasattr(user, 'updated_at') and user.updated_at
            ) else "",
            user.is_active if hasattr(user, 'is_active') else False,
            user.is_admin if hasattr(user, 'is_admin') else False,
        ])

    return output.getvalue()
```

### Authentication and Authorization

#### Export-Specific Authentication System

```python
# Export authentication patterns:

# Export-specific API key authentication
current_user: User | None = Depends(get_current_user_with_export_api_key)

# Feature flag gating for different export levels
dependencies=[
    Depends(require_feature("users:export")),        # Minimal export
    Depends(require_feature("users:export_full")),   # Full export
    Depends(require_feature("users:export_alive")),  # Health check
    Depends(require_feature("users:export_simple")), # Debug endpoint
]
```

### Response Headers and File Download

#### Proper File Download Configuration

```python
# CSV file download headers:

headers: Mapping[str, str] = {
    "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}"
}

return Response(
    content=csv_content,
    media_type="text/csv",
    headers=dict(headers)
)
```

## Export Data Formats

### Minimal Export Format

```csv
id,email,name
123,john.doe@example.com,John Doe
456,jane.smith@example.com,Jane Smith
789,admin@example.com,System Admin
```

### Full Export Format

```csv
id,email,name,created_at,updated_at,is_active,is_admin
123,john.doe@example.com,John Doe,2025-01-08T10:30:00Z,2025-01-08T15:45:00Z,true,false
456,jane.smith@example.com,Jane Smith,2025-01-07T14:20:00Z,2025-01-08T09:15:00Z,true,false
789,admin@example.com,System Admin,2025-01-01T12:00:00Z,2025-01-08T16:30:00Z,true,true
```

## Integration Patterns

### Database Repository Integration

```python
# Repository layer integration for data retrieval:

# Query all users from database
users_data: Sequence[User]
total_count: int
users_data, total_count = await list_users(session)

# Apply filtering logic at application level
if email is not None:
    users_data = [user for user in users_data if user.email == email]
```

### Feature Flag Integration

```python
# Feature flag system integration:

# Different feature flags for different export levels
@router.get("/export", dependencies=[Depends(require_feature("users:export"))])
@router.get("/export-full", dependencies=[Depends(require_feature("users:export_full"))])
@router.get("/export-alive", dependencies=[Depends(require_feature("users:export_alive"))])
@router.get("/export-simple", dependencies=[Depends(require_feature("users:export_simple"))])
```

## Use Case Scenarios

### Basic Reporting and Analytics

```python
# Minimal export for basic reporting needs:
# GET /api/v1/users/export?format=csv

# Returns essential user information
# Suitable for:
# - Basic user counts and statistics
# - Email list generation
# - Simple integrations with external systems
# - Quick user audits
```

### Comprehensive Data Backup

```python
# Full export for complete data backup:
# GET /api/v1/users/export-full

# Returns complete user information including:
# - Account timestamps (created_at, updated_at)
# - Status information (is_active, is_admin)
# - Suitable for:
#   - Complete system backup
#   - Detailed analytics and reporting
#   - Compliance and audit requirements
#   - System migration scenarios
```

### System Monitoring and Health Checks

```python
# Health monitoring endpoints:
# GET /api/v1/users/export-alive
# GET /api/v1/users/export-simple

# Returns status information for:
# - Service availability monitoring
# - Load balancer health checks
# - Feature flag validation
# - Development and debugging
```

## Best Practices

### Security and Access Control

- Use export-specific API keys for enhanced security
- Implement feature flag gating for operational flexibility
- Validate input parameters and format specifications
- Log export operations for security audit trails
- Consider rate limiting for large export operations

### Data Privacy and Compliance

- Export only necessary fields for specific use cases
- Implement filtering capabilities to limit data exposure
- Use proper file download headers for secure delivery
- Consider data anonymization for non-production exports
- Maintain audit logs of all export operations

### Performance and Scalability

- Use in-memory CSV generation for reasonable data volumes
- Consider streaming responses for very large datasets
- Implement pagination for large export operations
- Monitor memory usage during export generation
- Cache frequently requested export data when appropriate

### Error Handling and User Experience

- Validate export format parameters early
- Provide clear error messages for unsupported operations
- Handle database connection failures gracefully
- Implement proper HTTP status codes and responses
- Log export errors for monitoring and debugging

This user export API provides flexible and secure data export capabilities with
multiple granularity levels, comprehensive health monitoring, and robust
security controls essential for user data reporting and analytics in the
ReViewPoint platform.

## Related Files

- [`models/user.py.md`](../../../models/user.py.md) - User data models for export
- [`repositories/user.py.md`](../../../repositories/user.py.md) - User data retrieval
- [`api/deps.py.md`](../../deps.py.md) - Export authentication dependencies
- [`core/database.py.md`](../../../core/database.py.md) - Database session management
- [`api/v1/users/core.py.md`](core.py.md) - Core user management API
