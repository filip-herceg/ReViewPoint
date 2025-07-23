# File Model Documentation

## Purpose

The `file.py` module defines the SQLAlchemy ORM model for file entities in the ReViewPoint application. This model provides comprehensive file metadata management including ownership tracking, file type validation, size monitoring, and relationship mapping to users, serving as the foundation for the file upload and management system.

## Architecture

The model follows a file metadata management pattern:

- **Metadata Layer**: File information storage including name, type, and size
- **Ownership Layer**: User-file relationship management and access control
- **Storage Layer**: File system integration with database metadata tracking
- **Type Safety Layer**: Content type validation and file classification
- **Performance Layer**: Optimized indexing and relationship management
- **Audit Layer**: Creation and modification tracking through BaseModel inheritance

## Core Model Class

### `File`

Comprehensive file metadata model with ownership and type management.

```python
# Example usage - File creation
file = File(
    filename="research_paper.pdf",
    content_type="application/pdf",
    size=2048576,  # 2MB in bytes
    user_id=123
)

# Save to database
session.add(file)
await session.commit()
```

**Table Configuration:**
- `__tablename__ = "files"` - Database table name
- `__table_args__` - Custom indexing for performance optimization
- Inherits from `BaseModel` (id, created_at, updated_at)

## Field Specifications

### File Identification

**Filename Storage:**
```python
filename: Mapped[str] = mapped_column(String(255), nullable=False)
```

- **Required Field**: All files must have a filename
- **Length Limit**: 255 characters supports comprehensive filenames
- **Storage Name**: May differ from original upload name for security
- **Cross-Platform**: Compatible with all major operating systems

### File Type Management

**Content Type Classification:**
```python
content_type: Mapped[str] = mapped_column(String(128), nullable=False)
```

- **MIME Type Storage**: Standard MIME type specification
- **Required Field**: All files must have content type identification
- **Length Support**: 128 characters covers comprehensive MIME types
- **Security**: Enables content validation and security filtering

**Common Content Types:**
- `application/pdf` - PDF documents
- `application/msword` - Microsoft Word documents
- `text/plain` - Plain text files
- `image/jpeg`, `image/png` - Image files
- `application/json` - JSON data files

### File Size Tracking

**Size Monitoring:**
```python
size: Mapped[int] = mapped_column(BigInteger, nullable=True, default=0)
```

- **BigInteger Type**: Supports large files up to 9 exabytes
- **Optional Field**: Nullable for files without size information
- **Byte Storage**: Size stored in bytes for precision
- **Default Value**: Defaults to 0 for unknown sizes

**Size Usage Examples:**
```python
# Convert bytes to human-readable format
def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

# Example: file.size = 2048576 -> "2.0 MB"
```

### Ownership Management

**User Relationship:**
```python
user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
```

- **Foreign Key**: Links to User model for ownership
- **Required Field**: All files must have an owner
- **Access Control**: Enables ownership-based permissions
- **Cascade Support**: Supports cascading operations

**Bidirectional Relationship:**
```python
user: Mapped[User] = relationship("User", back_populates="files")
```

- **Bidirectional**: Files reference users, users reference files
- **Type Safety**: Proper typing with conditional imports
- **Lazy Loading**: Efficient memory usage with on-demand loading
- **Navigation**: Easy access to file owner information

## Database Optimization

### Indexing Strategy

**Performance Indexes:**
```python
__table_args__ = (Index("ix_files_user_id", "user_id"),)
```

- **User ID Index**: Optimizes queries for user files
- **Performance**: Fast lookup of files by owner
- **Scalability**: Supports large numbers of files per user
- **Query Optimization**: Enables efficient file listing and filtering

**Additional Recommended Indexes:**
```python
# For large-scale deployments
__table_args__ = (
    Index("ix_files_user_id", "user_id"),
    Index("ix_files_content_type", "content_type"),
    Index("ix_files_created_at", "created_at"),
    Index("ix_files_size", "size"),
)
```

### Query Patterns

**Efficient File Queries:**
```python
# Get files by user
user_files = await session.execute(
    select(File).where(File.user_id == user_id).order_by(File.created_at.desc())
)

# Get files by type
pdf_files = await session.execute(
    select(File).where(File.content_type == "application/pdf")
)

# Get large files
large_files = await session.execute(
    select(File).where(File.size > 10 * 1024 * 1024)  # > 10MB
)
```

## Usage Patterns

### File Upload Processing

```python
async def create_file_record(
    filename: str,
    content_type: str,
    size: int,
    user_id: int
) -> File:
    """Create a new file record in the database."""
    
    # Validate inputs
    if not filename or len(filename) > 255:
        raise ValueError("Invalid filename")
    
    if not content_type or len(content_type) > 128:
        raise ValueError("Invalid content type")
    
    if size < 0:
        raise ValueError("Invalid file size")
    
    # Create file record
    file = File(
        filename=filename,
        content_type=content_type,
        size=size,
        user_id=user_id
    )
    
    session.add(file)
    await session.commit()
    
    logger.info(f"File record created: {file.filename} ({file.size} bytes)")
    return file
```

### File Retrieval

```python
async def get_user_files(
    user_id: int,
    content_type: str = None,
    limit: int = 50,
    offset: int = 0
) -> list[File]:
    """Retrieve files for a specific user with optional filtering."""
    
    query = select(File).where(File.user_id == user_id)
    
    # Apply content type filter if provided
    if content_type:
        query = query.where(File.content_type == content_type)
    
    # Apply pagination
    query = query.order_by(File.created_at.desc()).offset(offset).limit(limit)
    
    result = await session.execute(query)
    return list(result.scalars().all())
```

### File Statistics

```python
async def get_file_statistics(user_id: int) -> dict:
    """Get comprehensive file statistics for a user."""
    
    # Total file count
    total_files = await session.scalar(
        select(func.count(File.id)).where(File.user_id == user_id)
    )
    
    # Total storage used
    total_size = await session.scalar(
        select(func.sum(File.size)).where(File.user_id == user_id)
    ) or 0
    
    # Files by content type
    content_type_stats = await session.execute(
        select(File.content_type, func.count(File.id))
        .where(File.user_id == user_id)
        .group_by(File.content_type)
    )
    
    # Recent files (last 30 days)
    recent_date = datetime.utcnow() - timedelta(days=30)
    recent_files = await session.scalar(
        select(func.count(File.id))
        .where(File.user_id == user_id, File.created_at >= recent_date)
    )
    
    return {
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_formatted": format_file_size(total_size),
        "content_types": {row[0]: row[1] for row in content_type_stats},
        "recent_files": recent_files
    }
```

### File Management Operations

```python
async def update_file_metadata(
    file_id: int,
    filename: str = None,
    content_type: str = None
) -> File:
    """Update file metadata."""
    
    file = await session.get(File, file_id)
    if not file:
        raise ValueError("File not found")
    
    # Update provided fields
    if filename is not None:
        if len(filename) > 255:
            raise ValueError("Filename too long")
        file.filename = filename
    
    if content_type is not None:
        if len(content_type) > 128:
            raise ValueError("Content type too long")
        file.content_type = content_type
    
    await session.commit()
    return file

async def delete_file_record(file_id: int, user_id: int) -> bool:
    """Delete a file record (ownership check included)."""
    
    file = await session.execute(
        select(File).where(File.id == file_id, File.user_id == user_id)
    )
    file = file.scalar_one_or_none()
    
    if not file:
        return False
    
    await session.delete(file)
    await session.commit()
    
    logger.info(f"File record deleted: {file.filename}")
    return True
```

## Security Considerations

### Access Control

**Ownership Verification:**
```python
async def verify_file_ownership(file_id: int, user_id: int) -> bool:
    """Verify that a user owns a specific file."""
    
    file = await session.execute(
        select(File).where(File.id == file_id, File.user_id == user_id)
    )
    return file.scalar_one_or_none() is not None
```

**Secure File Access:**
```python
async def get_file_for_user(file_id: int, user_id: int) -> File | None:
    """Securely retrieve file with ownership check."""
    
    result = await session.execute(
        select(File).where(File.id == file_id, File.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

### Content Validation

**Content Type Security:**
```python
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif"
}

def validate_content_type(content_type: str) -> bool:
    """Validate that content type is allowed."""
    return content_type in ALLOWED_CONTENT_TYPES
```

**Size Limits:**
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def validate_file_size(size: int) -> bool:
    """Validate file size against limits."""
    return 0 <= size <= MAX_FILE_SIZE
```

## Performance Considerations

### Database Performance

**Efficient Queries:**
```python
# Use indexes for filtering
async def get_files_by_type_efficiently(content_type: str, limit: int = 100):
    return await session.execute(
        select(File)
        .where(File.content_type == content_type)
        .order_by(File.created_at.desc())
        .limit(limit)
    )

# Batch operations for bulk updates
async def update_files_batch(file_updates: list[dict]):
    await session.execute(
        update(File),
        file_updates
    )
    await session.commit()
```

### Memory Management

**Large File Handling:**
```python
# Stream large file lists instead of loading all at once
async def stream_user_files(user_id: int, batch_size: int = 1000):
    offset = 0
    while True:
        files = await session.execute(
            select(File)
            .where(File.user_id == user_id)
            .offset(offset)
            .limit(batch_size)
        )
        file_batch = list(files.scalars())
        
        if not file_batch:
            break
            
        yield file_batch
        offset += batch_size
```

## Error Handling

### Database Constraints

```python
async def create_file_safely(file_data: dict) -> File:
    """Create file with comprehensive error handling."""
    try:
        file = File(**file_data)
        session.add(file)
        await session.commit()
        return file
        
    except IntegrityError as e:
        await session.rollback()
        if "foreign key constraint" in str(e).lower():
            raise ValueError("Invalid user ID")
        elif "check constraint" in str(e).lower():
            raise ValueError("Invalid file data")
        raise
        
    except Exception as e:
        await session.rollback()
        logger.error(f"File creation failed: {e}")
        raise
```

### Validation Errors

```python
def validate_file_data(filename: str, content_type: str, size: int) -> None:
    """Comprehensive file data validation."""
    
    errors = []
    
    if not filename or len(filename) > 255:
        errors.append("Invalid filename length")
    
    if not content_type or len(content_type) > 128:
        errors.append("Invalid content type length")
    
    if not validate_content_type(content_type):
        errors.append("Content type not allowed")
    
    if size < 0 or size > MAX_FILE_SIZE:
        errors.append("Invalid file size")
    
    if errors:
        raise ValueError("; ".join(errors))
```

## Best Practices

### Model Design

- **Single Responsibility**: File model focuses on metadata storage
- **Security First**: Ownership verification for all file operations
- **Performance**: Proper indexing for common query patterns
- **Type Safety**: Strong typing throughout the model
- **Extensibility**: Designed to support future file features

### Data Management

- **Metadata Integrity**: Ensure file metadata matches physical files
- **Size Tracking**: Monitor storage usage for quota management
- **Content Validation**: Validate file types and sizes
- **Relationship Management**: Maintain user-file ownership consistency
- **Audit Trails**: Leverage BaseModel timestamps for file history

### Security Implementation

- **Access Control**: Always verify ownership before file operations
- **Content Filtering**: Validate file types against allowed lists
- **Size Limits**: Enforce file size restrictions
- **Input Validation**: Sanitize all file metadata inputs
- **Error Handling**: Provide secure error messages without information leakage

## Testing Strategies

### Unit Testing

```python
def test_file_model_creation():
    """Test basic file model creation."""
    file = File(
        filename="test.pdf",
        content_type="application/pdf",
        size=1024,
        user_id=1
    )
    
    assert file.filename == "test.pdf"
    assert file.content_type == "application/pdf"
    assert file.size == 1024
    assert file.user_id == 1

def test_file_string_representation():
    """Test file string representation."""
    file = File(filename="test.pdf", content_type="application/pdf", user_id=1)
    file.id = 123
    
    repr_str = repr(file)
    assert "File id=123 filename=test.pdf" in repr_str
```

### Integration Testing

```python
async def test_file_database_operations():
    """Test file database operations."""
    
    # Create user first
    user = User(email="test@example.com", hashed_password="hash")
    session.add(user)
    await session.commit()
    
    # Create file
    file = File(
        filename="integration_test.pdf",
        content_type="application/pdf",
        size=2048,
        user_id=user.id
    )
    session.add(file)
    await session.commit()
    
    # Verify creation
    assert file.id is not None
    assert file.created_at is not None
    
    # Test relationship
    assert file.user.email == "test@example.com"
    
    # Test file retrieval
    retrieved_file = await session.get(File, file.id)
    assert retrieved_file.filename == "integration_test.pdf"
```

### Performance Testing

```python
async def test_file_query_performance():
    """Test file query performance with indexes."""
    
    # Create multiple files
    files = [
        File(filename=f"test_{i}.pdf", content_type="application/pdf", 
             size=1024*i, user_id=1)
        for i in range(1000)
    ]
    session.add_all(files)
    await session.commit()
    
    # Test indexed query performance
    start_time = time.time()
    user_files = await session.execute(
        select(File).where(File.user_id == 1).limit(100)
    )
    query_time = time.time() - start_time
    
    # Verify performance (should be fast with index)
    assert query_time < 0.1  # Less than 100ms
    assert len(list(user_files.scalars())) == 100
```

## Related Files

### Dependencies

- `sqlalchemy` - ORM framework with Mapped, mapped_column, relationship for model definition
- `typing` - Type annotations including TYPE_CHECKING for conditional imports
- Index and ForeignKey imports for database constraints and optimization

### Model Integration

- `src.models.base` - BaseModel inheritance providing id, created_at, updated_at
- `src.models.user` - User model with bidirectional file relationship
- Database foreign key relationship ensures referential integrity

### Service Integration

- `src.services.upload` - File upload business logic and processing
- `src.repositories.file` - File data access patterns and queries
- `src.schemas.file` - File validation and serialization schemas
- `src.api.v1.uploads` - File upload and management endpoints

### Storage Integration

- File system storage for actual file content
- Database metadata for file information and relationships
- Backup and synchronization systems for file management

## Configuration

### File Model Settings

```python
# File field configuration
FILE_CONFIG = {
    "filename_max_length": 255,
    "content_type_max_length": 128,
    "max_file_size_bytes": 100 * 1024 * 1024,  # 100MB
    "default_file_size": 0
}
```

### Content Type Configuration

```python
# Allowed content types
ALLOWED_CONTENT_TYPES = {
    "documents": [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ],
    "images": [
        "image/jpeg",
        "image/png", 
        "image/gif"
    ],
    "data": [
        "text/csv",
        "application/json"
    ]
}
```

### Performance Settings

```python
# Performance optimization settings
PERFORMANCE_CONFIG = {
    "enable_file_indexing": True,
    "batch_size_limit": 1000,
    "query_timeout_seconds": 30,
    "cache_file_metadata": True
}
```

This file model provides comprehensive metadata management for file storage in the ReViewPoint application, supporting secure file operations, efficient querying, and robust relationship management through well-designed SQLAlchemy patterns and performance optimizations.
