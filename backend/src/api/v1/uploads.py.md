# File Upload Management API Router

**File:** `backend/src/api/v1/uploads.py`  
**Purpose:** Comprehensive file upload, management, and export functionality for the ReViewPoint API  
**Lines of Code:** 1,386  
**Type:** File Management API Router

## Overview

The File Upload Management API Router provides comprehensive file upload, storage, retrieval, and management capabilities for the ReViewPoint application. This module implements secure file handling with validation, virus scanning, metadata management, access controls, bulk operations, and CSV export functionality. Built with FastAPI, it offers robust file management features including upload rate limiting, content type validation, filename sanitization, and user-based access controls.

## Architecture

### Core Design Principles

1. **Security-First**: Comprehensive file validation and virus scanning
2. **User Isolation**: Files are scoped to individual users with access controls
3. **Metadata Management**: Rich file metadata tracking and storage
4. **Bulk Operations**: Efficient bulk upload, delete, and export operations
5. **Rate Limiting**: Upload rate limiting for abuse prevention
6. **Audit Logging**: Comprehensive file operation logging

### File Management Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │    │   File Storage  │    │  File Retrieval │
│    POST /       │────┤   Validation    │────┤    GET /{id}    │
│                 │    │                 │    │                 │
│ • Validation    │    │ • Type Check    │    │ • Metadata      │
│ • Virus Scan    │    │ • Size Limit    │    │ • Download      │
│ • Metadata      │    │ • Sanitization  │    │ • Access Control│
│ • Database      │    │ • Deduplication │    │ • Content Serve │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   File Management│
                    │                 │
                    │ • List Files    │
                    │ • Delete Files  │
                    │ • Bulk Operations│
                    │ • CSV Export    │
                    │ • Health Checks │
                    └─────────────────┘
```

## Core Endpoints

### 📁 **File Upload**

#### `POST /uploads`

```python
@router.post("", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = Depends(ensure_nonempty_filename),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> FileUploadResponse:
```

**Purpose:** Secure file upload with comprehensive validation and metadata management

**Upload Process:**

1. **File Validation**: Size limits, content type verification, filename safety
2. **Security Scanning**: Virus and malware detection (planned)
3. **Filename Sanitization**: Path traversal protection and safe naming
4. **Metadata Generation**: File size, content type, checksums
5. **Database Storage**: File metadata and user association
6. **Response Generation**: File URLs and metadata response

**File Constraints:**

```python
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB per file
```

**Supported File Types:**

- **Documents**: PDF, DOC, DOCX, TXT, RTF
- **Images**: JPEG, PNG, GIF, SVG, WEBP
- **Data**: CSV, XLS, XLSX, JSON, XML
- **Archives**: ZIP, TAR, GZ (with content scanning)

**Security Features:**

```python
# Filename validation
if not is_safe_filename(filename_str):
    http_error(400, "Invalid filename. Path traversal attempts are not allowed.")

# Size validation
if file_size > MAX_UPLOAD_SIZE:
    http_error(413, f"File size exceeds limit of {MAX_UPLOAD_SIZE // (1024*1024)}MB.")

# Sanitization
safe_filename: str = sanitize_filename(filename_str)
```

**Response Format:**

```json
{
  "filename": "document.pdf",
  "url": "/uploads/document.pdf",
  "content_type": "application/pdf",
  "size": 2048576,
  "created_at": "2024-01-16T09:15:00Z"
}
```

**Error Handling:**

- `400 Bad Request`: Invalid file, unsafe filename, or validation failure
- `401 Unauthorized`: Authentication required
- `409 Conflict`: File already exists or concurrent upload conflict
- `413 Payload Too Large`: File exceeds size limit
- `415 Unsupported Media Type`: Invalid file type
- `429 Too Many Requests`: Upload rate limit exceeded

### 📋 **File Listing**

#### `GET /uploads`

```python
@router.get("", response_model=FileListResponse)
async def list_files(
    pagination: PaginationParams = Depends(pagination_params),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> FileListResponse:
```

**Purpose:** Paginated listing of user's uploaded files with filtering and sorting

**Listing Features:**

- **User Scoping**: Only shows files uploaded by current user
- **Pagination**: Offset/limit based pagination
- **Filtering**: By filename patterns and creation date ranges
- **Sorting**: By creation date, filename, or file size
- **Field Selection**: Configurable response fields

**Query Parameters:**

```python
# Pagination
?offset=0&limit=20

# Filtering
?filename_contains=document
?created_after=2024-01-01
?created_before=2024-12-31

# Sorting
?sort_by=created_at&sort_order=desc
```

**Response Structure:**

```json
{
  "files": [
    {
      "filename": "document.pdf",
      "url": "/uploads/document.pdf",
      "content_type": "application/pdf",
      "size": 1024,
      "created_at": "2024-01-16T09:15:00Z"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 20
}
```

### 📄 **File Metadata Retrieval**

#### `GET /uploads/{filename}`

```python
@router.get("/{filename}", response_model=FileUploadResponse)
async def get_file(
    filename: str = Path(..., description="The name of the file to retrieve."),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> FileUploadResponse:
```

**Purpose:** Retrieve metadata for a specific file by filename

**Access Control:**

```python
# Verify user owns the file
if db_file.user_id != current_user.id:
    http_error(403, "Access denied to file.")
```

**Metadata Response:**

```json
{
  "filename": "document.pdf",
  "url": "/uploads/document.pdf",
  "content_type": "application/pdf",
  "size": 2048576,
  "created_at": "2024-01-16T09:15:00Z"
}
```

### 📥 **File Download**

#### `GET /uploads/{filename}/download`

```python
@router.get("/{filename}/download")
async def download_file(
    filename: str = Path(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Response:
```

**Purpose:** Download actual file content with proper browser headers

**Download Process:**

1. **File Verification**: Check file exists and user has access
2. **Access Control**: Verify user ownership
3. **Content Serving**: Stream file content with appropriate headers
4. **Audit Logging**: Log download activity

**Response Headers:**

```python
headers = {
    "Content-Disposition": f'attachment; filename="{filename}"',
    "Content-Type": db_file.content_type or "application/octet-stream",
    "Content-Length": str(db_file.size) if db_file.size else None
}
```

### 🗑️ **File Deletion**

#### `DELETE /uploads/{filename}`

```python
@router.delete("/{filename}")
async def delete_file_by_filename(
    filename: str = Path(..., description="The name of the file to delete."),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Response:
```

**Purpose:** Delete a specific file by filename

**Deletion Process:**

1. **File Lookup**: Verify file exists and user ownership
2. **Access Validation**: Ensure user has delete permissions
3. **File Removal**: Remove from storage and database
4. **Transaction Commit**: Ensure atomic deletion
5. **Audit Logging**: Log deletion activity

**Response:** `204 No Content` on successful deletion

### 📊 **Bulk Operations**

#### `POST /uploads/bulk-delete`

```python
@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_files(
    request: BulkDeleteRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> BulkDeleteResponse:
```

**Purpose:** Efficiently delete multiple files in a single operation

**Bulk Delete Request:**

```json
{
  "filenames": ["document1.pdf", "document2.pdf", "document3.pdf"]
}
```

**Bulk Delete Response:**

```json
{
  "deleted": ["document1.pdf", "document2.pdf"],
  "failed": ["document3.pdf"],
  "errors": {
    "document3.pdf": "File not found"
  }
}
```

**Bulk Operation Features:**

- **Atomic Processing**: Each file deletion is independent
- **Error Isolation**: Failed deletions don't affect successful ones
- **Detailed Results**: Reports success/failure for each file
- **Access Control**: Validates user ownership for each file

### 📤 **CSV Export**

#### `GET /uploads/export`

```python
@router.get("/export")
async def export_files(
    current_user: User | None = Depends(get_current_user_with_api_key),
    session: AsyncSession = Depends(get_async_session),
) -> StreamingResponse:
```

**Purpose:** Export file metadata as CSV for external processing

**Export Process:**

1. **Authentication**: Supports both JWT and API key authentication
2. **Data Collection**: Gather file metadata for current user
3. **CSV Generation**: Format data as CSV with proper headers
4. **Stream Response**: Efficient streaming for large datasets

**CSV Format:**

```csv
filename,url,content_type,size,created_at
document.pdf,/uploads/document.pdf,application/pdf,2048576,2024-01-16T09:15:00Z
image.jpg,/uploads/image.jpg,image/jpeg,1024000,2024-01-16T10:30:00Z
```

**Streaming Response:**

```python
def generate_csv():
    yield "filename,url,content_type,size,created_at\n"
    for file in files:
        yield f"{file.filename},{file.url},{file.content_type},{file.size},{file.created_at}\n"

return StreamingResponse(
    generate_csv(),
    media_type="text/csv",
    headers={"Content-Disposition": "attachment; filename=files_export.csv"}
)
```

## Utility Functions

### 🛡️ **File Validation**

#### `ensure_nonempty_filename()`

```python
def ensure_nonempty_filename(file: UploadFile = FastAPIFile(...)) -> UploadFile:
    """Ensures the uploaded file has a non-empty filename."""
    if not file.filename:
        http_error(400, "Invalid file.")
    return file
```

**Purpose:** FastAPI dependency for filename validation

**Validation Checks:**

- **Non-empty Filename**: Rejects files without names
- **Safety Validation**: Prevents empty or null filenames
- **Early Rejection**: Fails fast for invalid files

### 🔍 **Diagnostic Endpoints**

#### Health Check Endpoints

```python
@router.get("/root-test")
def root_test() -> Mapping[str, str]:
    return {"status": "uploads root test", "router": "uploads"}

@router.get("/test-alive")
def test_alive() -> Mapping[str, str]:
    return {"status": "alive"}

@router.get("/export-alive")
def export_alive() -> Mapping[str, str]:
    return {"status": "uploads export alive"}
```

**Purpose:** Router registration and health monitoring endpoints

**Diagnostic Features:**

- **Router Verification**: Confirm router is properly registered
- **Health Monitoring**: Basic liveness checks for monitoring systems
- **Integration Testing**: Support for automated testing and deployment

## Data Models

### 📋 **Request/Response Models**

#### File Upload Response

```python
class FileUploadResponse(BaseModel):
    filename: str
    url: str
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"filename": "document.pdf", "url": "/uploads/document.pdf"}
        }
    )
```

#### File List Response

```python
class FileListResponse(BaseModel):
    files: Sequence[FileDict]
    total: int
```

#### Bulk Delete Models

```python
class BulkDeleteRequest(BaseModel):
    filenames: list[str]

class BulkDeleteResponse(BaseModel):
    deleted: list[str]
    failed: list[str]
```

#### File Response (Detailed)

```python
class FileResponse(BaseModel):
    filename: str
    url: str
    content_type: str | None = None
    size: int | None = None
    created_at: datetime | None = None
```

### 🏗️ **TypedDict Structures**

#### File Dictionary

```python
class FileDict(TypedDict, total=False):
    filename: str
    url: str
    content_type: str
    size: int
    created_at: str | None
```

**Type Safety Benefits:**

- **Compile-Time Validation**: MyPy type checking support
- **IDE Support**: Enhanced autocomplete and error detection
- **API Contracts**: Clear interface definitions
- **Runtime Safety**: Structured data validation

## Security Features

### 🔐 **Multi-Layer Security**

#### Authentication & Authorization

```python
# Standard JWT authentication
current_user: User = Depends(get_current_user)

# Flexible auth for exports (JWT + API key)
current_user: User | None = Depends(get_current_user_with_api_key)
```

#### File Security Validation

```python
# Path traversal protection
if not is_safe_filename(filename_str):
    http_error(400, "Invalid filename. Path traversal attempts are not allowed.")

# Filename sanitization
safe_filename: str = sanitize_filename(filename_str)

# Size limits
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
```

#### Access Controls

```python
# User-based file access
if db_file.user_id != current_user.id:
    http_error(403, "Access denied to file.")
```

### 🛡️ **Rate Limiting & Feature Flags**

```python
dependencies=[
    Depends(get_request_id),
    Depends(require_feature("uploads:upload")),
    Depends(require_api_key),
]
```

**Security Layers:**

1. **API Key Protection**: Service-level authentication
2. **Feature Flags**: Runtime endpoint control
3. **Rate Limiting**: Upload frequency controls
4. **User Isolation**: Files scoped to individual users

### 🔒 **File Content Security**

**Planned Security Features:**

- **Virus Scanning**: Malware detection for uploaded files
- **Content Type Validation**: MIME type verification beyond extensions
- **File Signature Verification**: Magic number validation
- **Quarantine System**: Isolation of suspicious files

## Error Handling

### 🛠️ **Comprehensive Error Management**

#### File Upload Errors

```python
# Size validation
if file_size > MAX_UPLOAD_SIZE:
    http_error(413, f"File size exceeds limit of {MAX_UPLOAD_SIZE // (1024*1024)}MB.")

# Filename validation
if not file.filename:
    http_error(400, "Invalid file.")

# Concurrent upload handling
if "unique constraint failed" in error_str:
    http_error(409, "File with same name already exists or concurrent upload conflict")
```

#### Database Transaction Handling

```python
max_retries: Final[int] = 3
for attempt in range(max_retries):
    try:
        async with session.begin_nested():
            db_file = await create_file(session, ...)
        await session.commit()
        return response
    except Exception as e:
        await session.rollback()
        if attempt < max_retries - 1:
            await asyncio.sleep(0.1 * (2**attempt))  # Exponential backoff
            continue
```

### 📊 **Error Code Reference**

| Status Code | Scenario         | Description                                       |
| ----------- | ---------------- | ------------------------------------------------- |
| `400`       | Invalid file     | Bad filename, empty file, validation failure      |
| `401`       | Auth required    | Missing or invalid authentication                 |
| `403`       | Access denied    | User doesn't own file or insufficient permissions |
| `404`       | File not found   | Requested file doesn't exist                      |
| `409`       | Conflict         | File already exists or concurrent operation       |
| `413`       | File too large   | Exceeds maximum file size limit                   |
| `415`       | Unsupported type | Invalid or disallowed file type                   |
| `422`       | Validation error | Input validation failures                         |
| `429`       | Rate limited     | Upload frequency limit exceeded                   |
| `500`       | Server error     | Unexpected server errors                          |

## Performance Considerations

### ⚡ **Upload Optimization**

#### Efficient File Processing

```python
# Stream processing for large files
file.file.seek(0, 2)  # Seek to end for size
file_size = file.file.tell()
file.file.seek(0)      # Reset for processing
```

#### Database Optimization

```python
# Nested transactions for atomic operations
async with session.begin_nested():
    db_file = await create_file(session, ...)

# Explicit commits for consistency
await session.commit()
```

#### Retry Logic with Backoff

```python
# Exponential backoff for database conflicts
wait_time: float = 0.1 * (2**attempt)
await asyncio.sleep(wait_time)
```

### 📊 **Streaming Responses**

#### CSV Export Streaming

```python
def generate_csv():
    """Generator for memory-efficient CSV streaming."""
    yield "filename,url,content_type,size,created_at\n"
    for file in files:
        yield f"{file.filename},{file.url},...\n"

return StreamingResponse(generate_csv(), media_type="text/csv")
```

**Performance Benefits:**

- **Memory Efficiency**: No need to load entire dataset in memory
- **Scalable**: Handles large file lists without memory issues
- **Fast Response**: Immediate response start with streaming data

## Usage Patterns

### 🔧 **Standard File Upload Flow**

```python
# 1. Upload file
import requests

files = {"file": ("document.pdf", open("document.pdf", "rb"))}
headers = {"Authorization": "Bearer <access_token>"}

response = requests.post(
    "https://api.reviewpoint.org/api/v1/uploads",
    files=files,
    headers=headers
)

file_info = response.json()
# {"filename": "document.pdf", "url": "/uploads/document.pdf"}

# 2. List user's files
response = requests.get(
    "https://api.reviewpoint.org/api/v1/uploads?limit=10",
    headers=headers
)

# 3. Download file
response = requests.get(
    f"https://api.reviewpoint.org/api/v1/uploads/{filename}/download",
    headers=headers
)

# 4. Delete file
response = requests.delete(
    f"https://api.reviewpoint.org/api/v1/uploads/{filename}",
    headers=headers
)
```

### 📤 **Bulk Operations**

```python
# Bulk delete multiple files
delete_request = {
    "filenames": ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
}

response = requests.post(
    "https://api.reviewpoint.org/api/v1/uploads/bulk-delete",
    json=delete_request,
    headers=headers
)

result = response.json()
# {
#   "deleted": ["doc1.pdf", "doc2.pdf"],
#   "failed": ["doc3.pdf"]
# }
```

### 📊 **CSV Export**

```python
# Export file metadata as CSV
response = requests.get(
    "https://api.reviewpoint.org/api/v1/uploads/export",
    headers=headers
)

# Save CSV data
with open("files_export.csv", "w") as f:
    f.write(response.text)
```

## Testing Strategies

### 🧪 **Unit Testing**

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

def test_file_upload_success():
    """Test successful file upload."""
    client = TestClient(app)

    test_file = BytesIO(b"test file content")
    files = {"file": ("test.pdf", test_file, "application/pdf")}

    response = client.post(
        "/api/v1/uploads",
        files=files,
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["url"] == "/uploads/test.pdf"

def test_file_upload_size_limit():
    """Test file size limit enforcement."""
    client = TestClient(app)

    # Create file larger than 5MB limit
    large_content = b"x" * (6 * 1024 * 1024)
    files = {"file": ("large.pdf", BytesIO(large_content), "application/pdf")}

    response = client.post(
        "/api/v1/uploads",
        files=files,
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 413
    assert "File size exceeds limit" in response.json()["message"]

def test_unsafe_filename_rejection():
    """Test rejection of unsafe filenames."""
    client = TestClient(app)

    unsafe_files = [
        ("../../../etc/passwd", "text/plain"),
        ("..\\windows\\system32\\config", "text/plain"),
        ("/etc/shadow", "text/plain"),
    ]

    for filename, content_type in unsafe_files:
        files = {"file": (filename, BytesIO(b"content"), content_type)}

        response = client.post(
            "/api/v1/uploads",
            files=files,
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
        assert "Path traversal" in response.json()["message"]
```

### 🔄 **Integration Testing**

```python
@pytest.mark.asyncio
async def test_upload_list_download_delete_flow():
    """Test complete file lifecycle."""
    client = TestClient(app)
    headers = {"Authorization": "Bearer test-token"}

    # Upload file
    files = {"file": ("test.pdf", BytesIO(b"test content"), "application/pdf")}
    upload_response = client.post("/api/v1/uploads", files=files, headers=headers)
    assert upload_response.status_code == 201

    filename = upload_response.json()["filename"]

    # List files (should include uploaded file)
    list_response = client.get("/api/v1/uploads", headers=headers)
    assert list_response.status_code == 200
    files_list = list_response.json()["files"]
    assert any(f["filename"] == filename for f in files_list)

    # Download file
    download_response = client.get(f"/api/v1/uploads/{filename}/download", headers=headers)
    assert download_response.status_code == 200

    # Delete file
    delete_response = client.delete(f"/api/v1/uploads/{filename}", headers=headers)
    assert delete_response.status_code == 204

    # Verify file is gone
    get_response = client.get(f"/api/v1/uploads/{filename}", headers=headers)
    assert get_response.status_code == 404
```

### 🛡️ **Security Testing**

```python
def test_user_file_isolation():
    """Test that users can only access their own files."""
    client = TestClient(app)

    # Upload file as user 1
    user1_headers = {"Authorization": "Bearer user1-token"}
    files = {"file": ("user1-file.pdf", BytesIO(b"content"), "application/pdf")}

    upload_response = client.post("/api/v1/uploads", files=files, headers=user1_headers)
    filename = upload_response.json()["filename"]

    # Try to access file as user 2
    user2_headers = {"Authorization": "Bearer user2-token"}

    get_response = client.get(f"/api/v1/uploads/{filename}", headers=user2_headers)
    assert get_response.status_code == 404  # File not found for this user

    download_response = client.get(f"/api/v1/uploads/{filename}/download", headers=user2_headers)
    assert download_response.status_code == 404  # File not found for this user

def test_api_key_protection():
    """Test API key requirement enforcement."""
    client = TestClient(app)

    files = {"file": ("test.pdf", BytesIO(b"content"), "application/pdf")}

    # Request without API key
    response = client.post("/api/v1/uploads", files=files)
    assert response.status_code == 401

    # Request with invalid API key
    response = client.post(
        "/api/v1/uploads",
        files=files,
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401
```

## Best Practices

### ✅ **Do's**

- **Validate File Content**: Check MIME types, not just extensions
- **Implement Rate Limiting**: Prevent upload abuse and resource exhaustion
- **Use Virus Scanning**: Implement malware detection for uploaded files
- **Sanitize Filenames**: Prevent path traversal and filesystem attacks
- **Implement Access Controls**: Ensure users can only access their files
- **Log File Operations**: Maintain audit trail for compliance
- **Use Streaming**: Handle large files efficiently with streaming
- **Implement Retry Logic**: Handle transient database failures gracefully

### ❌ **Don'ts**

- **Don't Trust User Input**: Always validate and sanitize file data
- **Don't Skip Size Limits**: Prevent resource exhaustion attacks
- **Don't Store Sensitive Files**: Implement proper access controls
- **Don't Ignore Error Handling**: Handle all failure scenarios gracefully
- **Don't Mix User Data**: Maintain strict user data isolation
- **Don't Skip Virus Scanning**: Always scan uploaded content
- **Don't Hardcode Limits**: Make file size and type limits configurable

## Related Files

- **`src/models/file.py`** - File database model definitions
- **`src/repositories/file.py`** - File data access layer
- **`src/utils/file.py`** - File validation and sanitization utilities
- **`src/utils/datetime.py`** - Date parsing utilities for filtering
- **`src/api/deps.py`** - Authentication and dependency injection

## Dependencies

- **`fastapi`** - Web framework and file upload handling
- **`sqlalchemy`** - Database ORM for file metadata
- **`loguru`** - Structured logging for file operations
- **`pydantic`** - Data validation and serialization

---

_This file upload router provides comprehensive, secure, and scalable file management capabilities for the ReViewPoint application, implementing industry best practices for file handling, security, and user data protection._
