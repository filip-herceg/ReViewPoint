# User Export API

**File:** `backend/src/api/v1/users/exports.py`  
**Purpose:** User data export functionality with CSV formats and health monitoring  
**Lines of Code:** 361  
**Type:** FastAPI Router Module

## Overview

The User Export API provides comprehensive data export capabilities for user information in multiple formats and detail levels. This module enables administrators to extract user data for reporting, backup, compliance, and integration purposes. It offers both minimal and full export formats with proper security controls, feature flag protection, and health monitoring endpoints for export system diagnostics.

## Architecture

### Core Design Principles

1. **Multiple Export Formats**: Support for different data export requirements
2. **Security Controls**: API key authentication and feature flag protection
3. **Flexible Data Levels**: Minimal and comprehensive export options
4. **Health Monitoring**: Diagnostic endpoints for export system status
5. **Proper File Handling**: CSV generation with appropriate headers and encoding
6. **Error Handling**: Comprehensive error responses and logging

### Export System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin User    │    │   Export        │    │   CSV          │
│   Request       │────┤   Controller    │────┤   Generator     │
│                 │    │                 │    │                 │
│ • Authentication│    │ • Feature Check │    │ • Data Format   │
│ • Export Type   │    │ • Data Query    │    │ • File Headers  │
│ • Filters       │    │ • Security      │    │ • Content Type  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Health        │
                    │   Monitoring    │
                    │                 │
                    │ • Status Check  │
                    │ • Diagnostics   │
                    │ • Feature Flags │
                    │ • Debug Endpoints│
                    └─────────────────┘
```

## Export Endpoints

### 📊 **Minimal CSV Export**

#### `GET /api/v1/users/export`

**Purpose:** Export user data in minimal CSV format for basic reporting

**Requirements:**

- Valid API key or export-specific API key
- Feature flag `users:export` must be enabled

**Query Parameters:**

```python
email: str | None = None        # Filter by specific email address
format: str | None = "csv"      # Export format (only csv supported)
```

**CSV Columns:**

```python
class UserMinimalRow(TypedDict):
    id: int         # User unique identifier
    email: str      # User email address
    name: str       # User display name
```

**Example Request:**

```http
GET /api/v1/users/export?format=csv&email=john@example.com
Authorization: Bearer your-api-key
```

**Example CSV Response:**

```csv
id,email,name
123,john.doe@example.com,John Doe
456,jane.smith@example.com,Jane Smith
```

**Implementation:**

```python
async def export_users_csv(
    session: AsyncSession,
    current_user: User | None,
    email: str | None = None,
    format: str | None = "csv",
) -> Response:
    """Export users in minimal CSV format."""

    # Validate format parameter
    if format and format.lower() != "csv":
        raise HTTPException(400, "Unsupported format. Only 'csv' is supported.")

    # Query users from database
    users_data, total_count = await list_users(session)

    # Apply email filter if provided
    if email:
        users_data = [user for user in users_data if user.email == email]

    # Generate CSV content
    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(["id", "email", "name"])

    for user in users_data:
        csv_writer.writerow([user.id, user.email, user.name])

    csv_content = output.getvalue()

    # Return with proper headers
    headers = {
        "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}"
    }

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers=headers
    )
```

**Response Headers:**

```http
Content-Type: text/csv
Content-Disposition: attachment; filename="users_export.csv"
```

**Use Cases:**

- Basic user reporting and analytics
- Simple data backup operations
- Third-party system integration
- Quick user audits and counts
- Lightweight data export for small datasets

### 📋 **Full CSV Export**

#### `GET /api/v1/users/export-full`

**Purpose:** Export comprehensive user data with all available fields

**Requirements:**

- Valid API key or export-specific API key
- Feature flag `users:export_full` must be enabled
- Higher privilege level than minimal export

**CSV Columns:**

```python
class UserFullRow(TypedDict):
    id: int             # User unique identifier
    email: str          # User email address
    name: str           # User display name
    created_at: str     # Account creation timestamp (ISO format)
    updated_at: str     # Last modification timestamp (ISO format)
    is_active: bool     # Account active status
    is_admin: bool      # Admin privileges flag
```

**Example Request:**

```http
GET /api/v1/users/export-full
Authorization: Bearer your-export-api-key
```

**Example CSV Response:**

```csv
id,email,name,created_at,updated_at,is_active,is_admin
123,john.doe@example.com,John Doe,2025-01-08T10:30:00Z,2025-01-08T15:45:00Z,true,false
456,jane.smith@example.com,Jane Smith,2025-01-07T14:20:00Z,2025-01-08T09:15:00Z,true,true
```

**Implementation:**

```python
async def export_users_full_csv(
    session: AsyncSession,
    current_user: User | None,
) -> Response:
    """Export comprehensive user data with all fields."""

    # Query all users
    users_data, total_count = await list_users(session)

    # Generate comprehensive CSV
    output = StringIO()
    csv_writer = csv.writer(output)

    # Write header with all columns
    csv_writer.writerow([
        "id", "email", "name", "created_at",
        "updated_at", "is_active", "is_admin"
    ])

    # Write user data with full details
    for user in users_data:
        csv_writer.writerow([
            user.id,
            user.email,
            user.name,
            user.created_at.isoformat() if user.created_at else "",
            user.updated_at.isoformat() if user.updated_at else "",
            user.is_active,
            user.is_admin,
        ])

    csv_content = output.getvalue()

    # Return with full export filename
    headers = {
        "Content-Disposition": f"attachment; filename={CSV_FULL_EXPORT_FILENAME}"
    }

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers=headers
    )
```

**Response Headers:**

```http
Content-Type: text/csv
Content-Disposition: attachment; filename="users_full_export.csv"
```

**Use Cases:**

- Complete data backup and archival
- Detailed analytics and business intelligence
- User account auditing and compliance
- System migration and data transfer
- Comprehensive reporting for stakeholders

## Health & Monitoring Endpoints

### 💚 **Export Health Check**

#### `GET /api/v1/users/export-alive`

**Purpose:** Health check endpoint for export router functionality

**Requirements:**

- Feature flag `users:export_alive` must be enabled
- No authentication required (health check endpoint)

**Response Schema:**

```python
class ExportAliveResponse(TypedDict):
    status: Literal["users export alive"]
```

**Example Request:**

```http
GET /api/v1/users/export-alive
```

**Example Response:**

```json
{
  "status": "users export alive"
}
```

**Implementation:**

```python
async def export_alive() -> ExportAliveResponse:
    """Health check for export router functionality."""
    return {"status": EXPORT_ALIVE_STATUS}
```

**Use Cases:**

- Service health monitoring and alerts
- Export feature availability testing
- System diagnostics and troubleshooting
- Load balancer health checks
- Continuous monitoring and uptime verification

### 🔧 **Simple Export Test**

#### `GET /api/v1/users/export-simple`

**Purpose:** Simple test endpoint for debugging export functionality

**Requirements:**

- Feature flag `users:export_simple` must be enabled
- No authentication required (debug endpoint)

**Response Schema:**

```python
class ExportSimpleResponse(TypedDict):
    users: Literal["export simple status"]
```

**Example Request:**

```http
GET /api/v1/users/export-simple
```

**Example Response:**

```json
{
  "users": "export simple status"
}
```

**Implementation:**

```python
async def export_simple() -> ExportSimpleResponse:
    """Simple test endpoint for debugging export functionality."""
    return {"users": EXPORT_SIMPLE_STATUS}
```

**Use Cases:**

- Development and debugging workflows
- Feature flag testing and validation
- Export system diagnostics
- Integration testing scenarios
- Quick connectivity verification

## Security Features

### 🔐 **Authentication Options**

#### Export API Key Support

```python
current_user: User | None = Depends(get_current_user_with_export_api_key)
```

**Authentication Methods:**

- **Standard API Key**: Regular API key authentication
- **Export-Specific API Key**: Specialized key for export operations
- **Flexible Authentication**: Supports both authentication methods

#### Feature Flag Protection

```python
dependencies=[
    Depends(require_feature("users:export")),        # Minimal export
    Depends(require_feature("users:export_full")),   # Full export
    Depends(require_feature("users:export_alive")),  # Health check
    Depends(require_feature("users:export_simple")), # Debug endpoint
]
```

### 🛡️ **Data Protection**

#### Format Validation

```python
# Strict format validation
if format and format.lower() != "csv":
    raise HTTPException(400, "Unsupported format. Only 'csv' is supported.")
```

#### Secure File Headers

```python
headers = {
    "Content-Disposition": f"attachment; filename={filename}",
    "Content-Type": "text/csv"
}
```

## Error Handling

### 🚨 **Comprehensive Error Responses**

#### Format Validation Errors

```python
# Unsupported format error
{
    "detail": "Unsupported format. Only 'csv' is supported.",
    "status_code": 400
}
```

#### Authentication Errors

```python
# Invalid API key
{
    "detail": "Invalid or missing API key",
    "status_code": 401
}
```

#### Feature Flag Errors

```python
# Feature not enabled
{
    "detail": "Export feature not enabled",
    "status_code": 403
}
```

### 📝 **Error Response Codes**

- **200 OK**: Export successful
- **400 Bad Request**: Invalid format or parameters
- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: Export feature not enabled
- **500 Internal Server Error**: Unexpected error

## Usage Patterns

### 📊 **Export Workflows**

#### Basic Export Operations

```python
import requests

# 1. Minimal user export
response = requests.get(
    "https://api.reviewpoint.org/api/v1/users/export?format=csv",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    # Save CSV content
    with open("users_minimal.csv", "w") as f:
        f.write(response.text)

# 2. Full user export with all fields
response = requests.get(
    "https://api.reviewpoint.org/api/v1/users/export-full",
    headers={"Authorization": f"Bearer {export_api_key}"}
)

if response.status_code == 200:
    # Save comprehensive CSV
    with open("users_complete.csv", "w") as f:
        f.write(response.text)

# 3. Filtered export (specific email)
response = requests.get(
    "https://api.reviewpoint.org/api/v1/users/export?email=admin@company.com",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    # Process filtered results
    csv_data = response.text
```

#### Health Monitoring

```python
import requests

# Check export system health
def check_export_health():
    try:
        response = requests.get(
            "https://api.reviewpoint.org/api/v1/users/export-alive",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return data["status"] == "users export alive"

        return False

    except requests.RequestException:
        return False

# Integration with monitoring systems
if check_export_health():
    print("✅ Export system operational")
else:
    print("❌ Export system offline")
```

### 🔄 **Automated Export Scheduling**

```python
import asyncio
import aiofiles
from datetime import datetime

async def scheduled_user_export():
    """Automated daily user export for backup purposes."""

    async with aiohttp.ClientSession() as session:
        # Export full user data
        async with session.get(
            "https://api.reviewpoint.org/api/v1/users/export-full",
            headers={"Authorization": f"Bearer {export_api_key}"}
        ) as response:

            if response.status == 200:
                # Generate timestamped filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"users_backup_{timestamp}.csv"

                # Save to backup directory
                csv_content = await response.text()
                async with aiofiles.open(f"backups/{filename}", "w") as f:
                    await f.write(csv_content)

                print(f"✅ User backup saved: {filename}")
                return True
            else:
                print(f"❌ Export failed: {response.status}")
                return False

# Schedule daily export
async def main():
    while True:
        await scheduled_user_export()
        await asyncio.sleep(86400)  # 24 hours
```

## Testing Strategies

### 🧪 **Export Testing**

```python
import pytest
import csv
from io import StringIO

class TestUserExports:

    @pytest.mark.asyncio
    async def test_minimal_csv_export(self, client, export_api_key):
        """Test minimal CSV export functionality."""

        response = client.get(
            "/api/v1/users/export?format=csv",
            headers={"Authorization": f"Bearer {export_api_key}"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

        # Validate CSV content
        csv_reader = csv.reader(StringIO(response.text))
        headers = next(csv_reader)
        assert headers == ["id", "email", "name"]

        # Check data rows
        rows = list(csv_reader)
        assert len(rows) > 0
        for row in rows:
            assert len(row) == 3  # id, email, name
            assert row[0].isdigit()  # id should be numeric
            assert "@" in row[1]     # email should contain @

    @pytest.mark.asyncio
    async def test_full_csv_export(self, client, export_api_key):
        """Test comprehensive CSV export functionality."""

        response = client.get(
            "/api/v1/users/export-full",
            headers={"Authorization": f"Bearer {export_api_key}"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # Validate comprehensive CSV headers
        csv_reader = csv.reader(StringIO(response.text))
        headers = next(csv_reader)
        expected_headers = [
            "id", "email", "name", "created_at",
            "updated_at", "is_active", "is_admin"
        ]
        assert headers == expected_headers

        # Check full data rows
        rows = list(csv_reader)
        for row in rows:
            assert len(row) == 7  # All columns
            assert row[5] in ["true", "false"]  # is_active boolean
            assert row[6] in ["true", "false"]  # is_admin boolean

    @pytest.mark.asyncio
    async def test_export_with_email_filter(self, client, export_api_key):
        """Test email filtering in export."""

        response = client.get(
            "/api/v1/users/export?email=test@example.com",
            headers={"Authorization": f"Bearer {export_api_key}"}
        )

        assert response.status_code == 200

        # Validate filtered results
        csv_reader = csv.reader(StringIO(response.text))
        next(csv_reader)  # Skip headers

        rows = list(csv_reader)
        for row in rows:
            assert row[1] == "test@example.com"  # email column

    @pytest.mark.asyncio
    async def test_unsupported_format(self, client, export_api_key):
        """Test handling of unsupported export formats."""

        response = client.get(
            "/api/v1/users/export?format=json",
            headers={"Authorization": f"Bearer {export_api_key}"}
        )

        assert response.status_code == 400
        assert "Unsupported format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_export_health_endpoints(self, client):
        """Test export system health monitoring."""

        # Test export alive endpoint
        response = client.get("/api/v1/users/export-alive")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "users export alive"

        # Test simple export endpoint
        response = client.get("/api/v1/users/export-simple")
        assert response.status_code == 200
        data = response.json()
        assert data["users"] == "export simple status"
```

### 🔄 **Integration Testing**

```python
@pytest.mark.asyncio
async def test_export_system_integration(client, export_api_key):
    """Test complete export system integration."""

    # 1. Check system health
    health_response = client.get("/api/v1/users/export-alive")
    assert health_response.status_code == 200

    # 2. Perform minimal export
    minimal_response = client.get(
        "/api/v1/users/export",
        headers={"Authorization": f"Bearer {export_api_key}"}
    )
    assert minimal_response.status_code == 200

    # 3. Perform full export
    full_response = client.get(
        "/api/v1/users/export-full",
        headers={"Authorization": f"Bearer {export_api_key}"}
    )
    assert full_response.status_code == 200

    # 4. Compare export consistency
    minimal_csv = csv.reader(StringIO(minimal_response.text))
    full_csv = csv.reader(StringIO(full_response.text))

    minimal_headers = next(minimal_csv)
    full_headers = next(full_csv)

    # Verify minimal headers are subset of full headers
    for header in minimal_headers:
        assert header in full_headers

    # Verify data consistency
    minimal_rows = list(minimal_csv)
    full_rows = list(full_csv)

    assert len(minimal_rows) == len(full_rows)
```

## Best Practices

### ✅ **Do's**

- **Validate Format Parameters**: Always validate export format inputs
- **Use Proper HTTP Headers**: Set correct Content-Type and Content-Disposition
- **Implement Health Checks**: Provide health monitoring endpoints
- **Support Multiple Export Levels**: Offer minimal and comprehensive exports
- **Use Feature Flags**: Protect all endpoints with feature flag controls
- **Handle Large Datasets**: Consider pagination for very large exports
- **Log Export Operations**: Maintain audit trail for export activities
- **Secure API Keys**: Use export-specific API keys when appropriate

### ❌ **Don'ts**

- **Don't Expose Sensitive Data**: Be careful with password hashes and tokens
- **Don't Skip Authentication**: Always authenticate export requests
- **Don't Ignore Error Handling**: Handle all error scenarios gracefully
- **Don't Hard-Code Filenames**: Use configurable export filenames
- **Don't Skip Validation**: Validate all input parameters
- **Don't Ignore Performance**: Consider memory usage for large exports
- **Don't Skip Feature Flags**: Always check feature flag status
- **Don't Leak Internal Data**: Sanitize exported data appropriately

## Related Files

- **`src/repositories/user.py`** - User data access for export queries
- **`src/models/user.py`** - User model definition and field mappings
- **`src/api/deps.py`** - Authentication and feature flag dependencies
- **`src/core/database.py`** - Database session management

## Dependencies

- **`fastapi`** - Web framework and response handling
- **`csv`** - CSV file generation and formatting
- **`io.StringIO`** - In-memory string handling for CSV generation
- **`sqlalchemy`** - Database access and user queries

---

_This User Export API provides secure, flexible, and comprehensive data export capabilities with multiple formats, health monitoring, and robust error handling for administrative and operational needs._
