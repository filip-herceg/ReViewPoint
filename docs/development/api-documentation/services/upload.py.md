# Upload Service Documentation

## Purpose

The `upload.py` service module provides comprehensive file upload and management functionality for the ReViewPoint application. This service handles secure file upload workflows, storage management, metadata tracking, and file operations with proper access controls and validation. It serves as the primary business logic layer for all file-related operations.

## Architecture

The upload service follows a clean architecture pattern with clear separation of concerns:

- **Service Layer**: File operation orchestration and business logic
- **Storage Layer**: Physical file storage and retrieval
- **Repository Layer**: File metadata persistence
- **Validation Layer**: File security and integrity checks
- **Access Control**: User-based file ownership and permissions

## Core Components

### UploadService Class

The main service class that coordinates all file operations:

```python
class UploadService:
    """Service for handling file uploads and management."""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
```

**Key Features:**
- Automatic upload directory creation
- Configuration-driven storage paths
- Environment-based settings management
- Singleton pattern for service consistency

## Core Functions

### File Upload Operations

#### `upload_file(session, file, user_id)`

Handles complete file upload workflow with security validation and metadata storage.

```python
# Example usage
uploaded_file = await upload_service.upload_file(
    session=session,
    file=upload_file,  # FastAPI UploadFile object
    user_id=current_user.id
)
print(f"File uploaded: {uploaded_file.filename}")
```

**Upload Process:**
1. **Filename Validation**: Checks for valid filename presence
2. **Security Sanitization**: Sanitizes filename for safe storage
3. **Size Validation**: Enforces 10MB file size limit
4. **Unique Storage**: Generates UUID-based storage filename
5. **Physical Storage**: Saves file to configured upload directory
6. **Metadata Persistence**: Creates database record with file information
7. **User Association**: Links file to uploading user

**Security Features:**
- Filename sanitization to prevent path traversal
- File size limits to prevent storage abuse
- Safe filename validation using security utilities
- Unique filename generation to prevent conflicts
- Error handling for storage failures

### File Retrieval Operations

#### `get_file(session, filename)`

Retrieves file metadata by filename with database lookup.

```python
# Example usage
file_record = await upload_service.get_file(session, "example.pdf")
if file_record:
    print(f"File owner: {file_record.user_id}")
    print(f"Content type: {file_record.content_type}")
```

**Features:**
- Efficient database lookup by filename
- Complete metadata retrieval
- Null handling for non-existent files
- Type-safe return values

### File Deletion Operations

#### `delete_file(session, filename, user_id)`

Securely deletes files with ownership verification and cleanup.

```python
# Example usage
deleted = await upload_service.delete_file(
    session=session,
    filename="document.pdf",
    user_id=current_user.id
)
if deleted:
    print("File successfully deleted")
```

**Deletion Process:**
1. **File Lookup**: Retrieves file metadata from database
2. **Ownership Verification**: Confirms user owns the file
3. **Physical Deletion**: Removes file from storage directory
4. **Metadata Cleanup**: Removes database record
5. **Error Resilience**: Continues even if physical deletion fails

**Security Features:**
- Strict ownership verification
- Authorization checking before deletion
- Graceful handling of missing files
- Audit trail through database operations

### Utility Operations

#### `get_file_path(filename)`

Generates full filesystem path for file access.

```python
# Example usage
file_path = upload_service.get_file_path("document.pdf")
if file_path.exists():
    # Process file
    pass
```

**Features:**
- Path construction using configured upload directory
- Type-safe Path object returns
- Consistent path handling across platforms

## Security Considerations

### File Validation

**Filename Security:**
```python
# Sanitization process
safe_filename = sanitize_filename(file.filename)
if not is_safe_filename(safe_filename):
    raise HTTPException(status_code=400, detail="Invalid filename")
```

- Path traversal prevention
- Special character filtering
- Extension validation
- Length limit enforcement

### Storage Security

**Unique File Naming:**
```python
# UUID-based storage names prevent conflicts
file_id = str(uuid.uuid4())
file_extension = Path(safe_filename).suffix
stored_filename = f"{file_id}{file_extension}"
```

- Prevents filename-based attacks
- Eliminates file overwrites
- Maintains file type information
- Enables efficient organization

### Access Control

**Ownership Verification:**
```python
# Strict ownership checking
if file_record.user_id != user_id:
    raise HTTPException(
        status_code=403, 
        detail="Not authorized to delete this file"
    )
```

- User-based file ownership
- Authorization before operations
- Privacy protection
- Audit trail maintenance

### Size Limitations

**Storage Abuse Prevention:**
```python
# 10MB file size limit
max_size = 10 * 1024 * 1024
content = await file.read()
if len(content) > max_size:
    raise HTTPException(status_code=413, detail="File too large")
```

## Error Handling

### Exception Patterns

```python
# Common error scenarios
try:
    file_record = await upload_service.upload_file(session, file, user_id)
except HTTPException as e:
    if e.status_code == 400:
        # Handle validation errors
        return {"error": "Invalid file"}
    elif e.status_code == 413:
        # Handle size limit errors
        return {"error": "File too large"}
    elif e.status_code == 500:
        # Handle storage errors
        return {"error": "Upload failed"}
```

### Error Response Types

- **400 Bad Request**: Invalid filename or file format
- **403 Forbidden**: Insufficient permissions for operation
- **413 Payload Too Large**: File exceeds size limits
- **500 Internal Server Error**: Storage or database failures

## Usage Patterns

### Upload Workflow

```python
async def upload_endpoint(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends()
):
    try:
        result = await upload_service.upload_file(session, file, current_user.id)
        return {"message": "Upload successful", "file_id": result.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")
```

### File Serving Workflow

```python
async def download_endpoint(
    filename: str,
    session: AsyncSession = Depends(get_session),
    upload_service: UploadService = Depends()
):
    file_record = await upload_service.get_file(session, filename)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = upload_service.get_file_path(filename)
    return FileResponse(
        path=file_path,
        media_type=file_record.content_type,
        filename=file_record.original_name
    )
```

### Deletion Workflow

```python
async def delete_endpoint(
    filename: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends()
):
    deleted = await upload_service.delete_file(session, filename, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}
```

## Best Practices

### Service Design

- **Single Responsibility**: Each method handles one specific operation
- **Error Isolation**: Comprehensive exception handling
- **Resource Management**: Proper file handle cleanup
- **Type Safety**: Strong typing throughout the service
- **Configuration Driven**: Environment-based settings

### Storage Management

- **Directory Structure**: Organized file storage hierarchy
- **Cleanup Strategies**: Regular maintenance of orphaned files
- **Backup Considerations**: Integration with backup systems
- **Monitoring**: File system usage tracking
- **Archival Policies**: Long-term storage strategies

### Performance Optimization

- **Async Operations**: Non-blocking file I/O
- **Streaming**: Large file handling without memory overflow
- **Caching**: Metadata caching for frequently accessed files
- **Compression**: Optional file compression for storage efficiency
- **CDN Integration**: Content delivery network support

## Testing Strategies

### Unit Testing

```python
async def test_upload_file():
    # Test successful file upload
    mock_file = create_mock_upload_file("test.pdf", b"test content")
    result = await upload_service.upload_file(session, mock_file, user_id)
    assert result.filename.endswith(".pdf")
    assert result.user_id == user_id
```

### Integration Testing

```python
async def test_upload_download_cycle():
    # Test complete upload and download workflow
    uploaded = await upload_service.upload_file(session, test_file, user_id)
    retrieved = await upload_service.get_file(session, uploaded.filename)
    assert retrieved.id == uploaded.id
```

### Security Testing

```python
async def test_path_traversal_protection():
    # Test security against path traversal attacks
    malicious_file = create_mock_upload_file("../../../etc/passwd", b"content")
    with pytest.raises(HTTPException) as exc_info:
        await upload_service.upload_file(session, malicious_file, user_id)
    assert exc_info.value.status_code == 400
```

## Related Files

### Dependencies

- `src/repositories/file.py` - File metadata persistence
- `src/models/file.py` - File database model
- `src/utils/file.py` - File validation utilities
- `src/core/config.py` - Service configuration

### API Integration

- `src/api/v1/uploads.py` - File upload endpoints
- `src/api/deps.py` - Dependency injection setup

### Utilities

- `src/utils/storage.py` - Storage backend utilities
- `src/utils/validation.py` - File validation helpers

## Configuration

### Environment Variables

```bash
# Storage Configuration
UPLOAD_DIR=/var/uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,png

# Security Settings
ENABLE_VIRUS_SCANNING=true
QUARANTINE_DIR=/var/quarantine
```

### Service Settings

```python
# Upload service configuration
class UploadSettings:
    upload_dir: str = "/var/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = ["pdf", "doc", "txt", "jpg", "png"]
    enable_compression: bool = False
```

This upload service provides a secure, scalable foundation for file management in the ReViewPoint application, ensuring proper handling of user uploads with comprehensive validation, security measures, and access controls.
