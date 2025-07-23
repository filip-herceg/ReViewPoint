# File Repository Documentation

## Purpose

The `file.py` repository module provides comprehensive data access layer functionality for file management operations in the ReViewPoint application. This repository implements efficient database operations for file metadata persistence, supporting file uploads, retrievals, deletions, and advanced querying with proper validation and error handling.

## Architecture

The repository follows a clean data access pattern with focused responsibilities:

- **Data Persistence Layer**: SQLAlchemy async ORM operations for file metadata
- **Validation Layer**: Input validation and error handling
- **Query Optimization Layer**: Efficient database queries with proper indexing
- **Bulk Operations Layer**: Batch processing for multiple file operations
- **Security Layer**: User-based access control and ownership verification

## Core Functions

### File Retrieval Operations

#### `get_file_by_filename(session, filename)`

Retrieves a file record by its filename with efficient database lookup.

```python
# Example usage
file_record = await get_file_by_filename(session, "document.pdf")
if file_record:
    print(f"File owner: {file_record.user_id}")
    print(f"Content type: {file_record.content_type}")
    print(f"File size: {file_record.size} bytes")
```

**Features:**
- Efficient single-query lookup by filename
- Type-safe return values with None handling
- Minimal database overhead
- Proper SQLAlchemy result handling

### File Creation Operations

#### `create_file(session, filename, content_type, user_id, size=0)`

Creates a new file record in the database with comprehensive validation.

```python
# Example usage
try:
    new_file = await create_file(
        session=session,
        filename="document.pdf",
        content_type="application/pdf",
        user_id=123,
        size=1024000  # 1MB
    )
    print(f"File created with ID: {new_file.id}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

**Validation Features:**
- **Filename Validation**: Ensures filename is not empty
- **Type Safety**: Strong typing for all parameters
- **Error Handling**: Comprehensive exception management
- **Transaction Safety**: Automatic rollback on failure
- **Database Flush**: Immediate ID generation for reference

**Error Handling:**
- `ValidationError`: Raised when filename is empty
- `Exception`: Generic database operation failures
- Automatic session rollback on errors
- Proper exception propagation

### File Deletion Operations

#### `delete_file(session, filename)`

Deletes a file record by filename with safe handling.

```python
# Example usage
deleted = await delete_file(session, "document.pdf")
if deleted:
    print("File successfully deleted from database")
else:
    print("File not found")
```

**Features:**
- Safe deletion with existence checking
- Boolean return for operation success
- No commit handling (delegated to caller)
- Proper error isolation

#### `bulk_delete_files(session, filenames, user_id)`

Efficiently deletes multiple files with user ownership verification.

```python
# Example usage
filenames_to_delete = ["file1.pdf", "file2.doc", "file3.jpg"]
deleted, failed = await bulk_delete_files(
    session=session,
    filenames=filenames_to_delete,
    user_id=123
)
print(f"Successfully deleted: {deleted}")
print(f"Failed to delete: {failed}")
```

**Security Features:**
- **Ownership Verification**: Only deletes files owned by the user
- **Batch Processing**: Efficient multi-file deletion
- **Error Resilience**: Continues processing despite individual failures
- **Detailed Results**: Returns lists of successful and failed deletions

**Return Value:**
- `tuple[list[str], list[str]]`: (successfully_deleted, failed_to_delete)
- Separate tracking of success and failure cases
- Comprehensive operation reporting

### Advanced Query Operations

#### `list_files(session, user_id, offset, limit, q, sort, order, created_after, created_before)`

Provides comprehensive file listing with filtering, searching, sorting, and pagination.

```python
# Example usage
files, total_count = await list_files(
    session=session,
    user_id=123,
    offset=0,
    limit=20,
    q="document",  # Search in filenames
    sort="created_at",
    order="desc",
    created_after=datetime(2024, 1, 1),
    created_before=datetime(2024, 12, 31)
)
print(f"Found {len(files)} files out of {total_count} total")
```

**Query Features:**

**Pagination Support:**
- `offset`: Starting position for results
- `limit`: Maximum number of results to return
- Efficient pagination with proper counting

**Search Capabilities:**
- `q` parameter: Partial filename matching with ILIKE
- Case-insensitive search
- Wildcard pattern matching

**Filtering Options:**
- `created_after`: Files created after specified datetime
- `created_before`: Files created before specified datetime
- User-specific filtering (always applied)

**Sorting Options:**
- `sort`: "created_at" or "filename"
- `order`: "desc" or "asc"
- Proper column mapping with type safety

**Performance Optimizations:**
- Subquery-based counting for accurate totals
- Efficient query construction with conditional clauses
- Proper indexing utilization
- Minimal data transfer

**Return Value:**
- `tuple[list[File], int]`: (files, total_count)
- Complete file objects with all metadata
- Accurate total count for pagination

## Database Schema Integration

### File Model Fields

The repository works with the File model containing:

```python
class File:
    id: int                    # Primary key
    filename: str             # Stored filename (UUID-based)
    content_type: str         # MIME type
    user_id: int             # Owner reference
    size: int                # File size in bytes
    created_at: datetime     # Creation timestamp
    updated_at: datetime     # Last modification timestamp
```

### Query Patterns

**Efficient Lookups:**
```python
# Single file lookup
stmt = select(File).where(File.filename == filename)

# User-specific queries
stmt = select(File).where(File.user_id == user_id)

# Complex filtering
stmt = select(File).where(
    File.user_id == user_id,
    File.filename.ilike(f"%{query}%"),
    File.created_at >= start_date
)
```

**Optimized Counting:**
```python
# Efficient count with subquery
count_stmt = select(func.count()).select_from(stmt.subquery())
total = (await session.execute(count_stmt)).scalar_one()
```

## Error Handling Patterns

### Validation Errors

```python
try:
    file = await create_file(session, filename, content_type, user_id)
except ValidationError as e:
    # Handle validation failures
    return {"error": "Invalid file data", "details": str(e)}
```

### Database Errors

```python
try:
    await session.flush()
except Exception as e:
    await session.rollback()
    logger.error(f"Database error in file operation: {e}")
    raise
```

### Bulk Operation Errors

```python
# Graceful handling of partial failures
deleted, failed = await bulk_delete_files(session, filenames, user_id)
if failed:
    logger.warning(f"Some files could not be deleted: {failed}")
return {
    "deleted": deleted,
    "failed": failed,
    "partial_success": len(deleted) > 0
}
```

## Usage Patterns

### File Upload Workflow

```python
async def upload_workflow(session: AsyncSession, upload_file: UploadFile, user_id: int):
    # 1. Save physical file
    stored_filename = save_physical_file(upload_file)
    
    # 2. Create database record
    try:
        file_record = await create_file(
            session=session,
            filename=stored_filename,
            content_type=upload_file.content_type,
            user_id=user_id,
            size=get_file_size(upload_file)
        )
        await session.commit()
        return file_record
    except Exception:
        # Cleanup physical file on database failure
        cleanup_physical_file(stored_filename)
        raise
```

### File Listing Workflow

```python
async def list_user_files(session: AsyncSession, user_id: int, page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    files, total = await list_files(
        session=session,
        user_id=user_id,
        offset=offset,
        limit=per_page,
        sort="created_at",
        order="desc"
    )
    
    return {
        "files": [file_to_dict(f) for f in files],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

### File Deletion Workflow

```python
async def delete_workflow(session: AsyncSession, filename: str, user_id: int):
    # 1. Get file record with ownership check
    file_record = await get_file_by_filename(session, filename)
    if not file_record or file_record.user_id != user_id:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 2. Delete database record
    deleted = await delete_file(session, filename)
    if deleted:
        await session.commit()
        # 3. Delete physical file
        cleanup_physical_file(filename)
        return True
    return False
```

## Performance Considerations

### Query Optimization

**Indexing Strategy:**
- Primary key index on `id`
- Unique index on `filename`
- Composite index on `(user_id, created_at)` for user file listings
- Index on `user_id` for ownership queries

**Efficient Pagination:**
```python
# Avoid COUNT(*) on large tables with subquery approach
count_stmt = select(func.count()).select_from(stmt.subquery())
```

**Conditional Query Building:**
```python
# Only add WHERE clauses when needed
if q is not None:
    stmt = stmt.where(File.filename.ilike(f"%{q}%"))
```

### Memory Management

- **Streaming Results**: Use `scalars().all()` efficiently
- **Batch Processing**: Bulk operations for multiple files
- **Minimal Data Transfer**: Select only required columns when possible
- **Connection Pooling**: Proper async session management

## Security Considerations

### Access Control

**User Ownership Verification:**
```python
# Always verify user owns the file
stmt = select(File).where(File.filename == filename, File.user_id == user_id)
```

**Input Validation:**
- Filename validation to prevent empty values
- User ID validation for proper access control
- Size validation for storage limits
- Content type validation for security

### SQL Injection Prevention

- **Parameterized Queries**: All queries use SQLAlchemy ORM
- **Type Safety**: Strong typing prevents injection
- **Input Sanitization**: Validation before database operations

## Testing Strategies

### Unit Testing

```python
async def test_create_file():
    # Test successful file creation
    file = await create_file(
        session=session,
        filename="test.pdf",
        content_type="application/pdf",
        user_id=123,
        size=1024
    )
    assert file.filename == "test.pdf"
    assert file.user_id == 123
```

### Integration Testing

```python
async def test_file_lifecycle():
    # Test complete file lifecycle
    created = await create_file(session, "test.pdf", "application/pdf", 123)
    retrieved = await get_file_by_filename(session, "test.pdf")
    assert retrieved.id == created.id
    
    deleted = await delete_file(session, "test.pdf")
    assert deleted is True
    
    not_found = await get_file_by_filename(session, "test.pdf")
    assert not_found is None
```

### Performance Testing

```python
async def test_bulk_operations_performance():
    # Test bulk deletion performance
    filenames = [f"file_{i}.txt" for i in range(1000)]
    start_time = time.time()
    deleted, failed = await bulk_delete_files(session, filenames, user_id=123)
    duration = time.time() - start_time
    assert duration < 2.0  # Should complete within 2 seconds
```

## Related Files

### Dependencies

- `src/models/file.py` - File SQLAlchemy model definition
- `src/utils/errors.py` - Custom exception classes
- `sqlalchemy` - Database ORM and query building
- `datetime` - Timestamp handling

### Service Integration

- `src/services/upload.py` - File upload business logic
- `src/api/v1/uploads.py` - File upload API endpoints
- `src/core/database.py` - Database session management

### Model Relationships

- `src/models/user.py` - User model for ownership relationships
- Foreign key relationship: `File.user_id` → `User.id`

## Configuration

### Database Settings

```python
# File-related database configuration
FILE_TABLE_NAME = "files"
MAX_FILENAME_LENGTH = 255
INDEX_CONFIGURATION = {
    "filename_unique": True,
    "user_files_composite": ("user_id", "created_at"),
    "user_id_index": True
}
```

### Query Limits

```python
# Query performance settings
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_SORT_FIELD = "created_at"
DEFAULT_SORT_ORDER = "desc"
```

This file repository provides a robust, efficient data access layer for file management operations in the ReViewPoint application, ensuring data integrity, performance optimization, and security through well-designed repository patterns and proper database abstraction.
