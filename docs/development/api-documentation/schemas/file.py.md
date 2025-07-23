# File Schema Documentation

## Purpose

The `file.py` schema module defines Pydantic data validation models for file metadata management in the ReViewPoint application. This schema provides structured validation, serialization, and type safety for file operations including uploads, metadata retrieval, and file management workflows, ensuring consistent file data representation across the API layer.

## Architecture

The schema follows a focused file metadata validation pattern:

- **Metadata Validation Layer**: File information structure and constraints
- **Type Safety Layer**: Strong typing with Field validation and constraints
- **ORM Integration Layer**: Seamless SQLAlchemy model conversion
- **API Serialization Layer**: Optimized JSON responses for file operations
- **Documentation Layer**: Comprehensive field documentation for OpenAPI

## Core Schema Class

### `FileSchema`

Comprehensive file metadata representation with validation and documentation.

```python
# Example usage
file_metadata = FileSchema(
    id=12345,
    filename="research_paper.pdf",
    content_type="application/pdf",
    user_id=678,
    created_at=datetime(2024, 7, 23, 14, 30, 0)
)

# API response usage
return {"file": file_metadata.model_dump()}
```

**Field Specifications:**

**Primary Identification:**
- `id: int` - Unique file identifier (primary key)
- `filename: str` - Stored filename (max 255 characters)
- `user_id: int` - Owner user ID (foreign key relationship)

**File Metadata:**
- `content_type: str` - MIME type specification (max 128 characters)
- `created_at: datetime` - File creation timestamp

**Field Documentation:**
```python
id: int = Field(..., description="Unique identifier for the file")
filename: str = Field(..., max_length=255, description="Name of the file")
content_type: str = Field(..., max_length=128, description="MIME type of the file")
user_id: int = Field(..., description="ID of the user who owns the file")
created_at: datetime = Field(..., description="Timestamp when the file was created")
```

## Validation Features

### Field Constraints

**Filename Validation:**
```python
filename: str = Field(..., max_length=255, description="Name of the file")
```

- **Length Limit**: 255 characters maximum (filesystem compatibility)
- **Required Field**: Cannot be null or empty
- **Database Compatibility**: Aligns with VARCHAR(255) database constraints
- **Cross-Platform**: Works with all major filesystems

**Content Type Validation:**
```python
content_type: str = Field(..., max_length=128, description="MIME type of the file")
```

- **MIME Type Format**: Standard MIME type specification
- **Length Constraint**: 128 characters for comprehensive MIME types
- **Required Field**: Ensures proper file type identification
- **Security**: Enables proper content handling and validation

**User Ownership:**
```python
user_id: int = Field(..., description="ID of the user who owns the file")
```

- **Foreign Key Reference**: Links to User model
- **Access Control**: Enables ownership-based permissions
- **Required Field**: Every file must have an owner
- **Integer Type**: Efficient database indexing

### Configuration Features

**ORM Integration:**
```python
model_config = ConfigDict(from_attributes=True)
```

- **SQLAlchemy Compatibility**: Direct conversion from ORM models
- **Attribute Mapping**: Automatic field mapping from database models
- **Performance**: Efficient object conversion
- **Type Safety**: Maintains type integrity during conversion

## Usage Patterns

### File Upload Response

```python
async def upload_file_endpoint(file: UploadFile, current_user: User):
    # Process file upload
    uploaded_file = await upload_service.upload_file(file, current_user.id)
    
    # Convert to schema for response
    file_response = FileSchema(
        id=uploaded_file.id,
        filename=uploaded_file.filename,
        content_type=uploaded_file.content_type,
        user_id=uploaded_file.user_id,
        created_at=uploaded_file.created_at
    )
    
    return {"message": "File uploaded successfully", "file": file_response}
```

### File Listing Response

```python
async def list_user_files(user_id: int, page: int = 1, per_page: int = 20):
    # Get files from repository
    files, total = await file_repository.list_files(
        user_id=user_id,
        offset=(page - 1) * per_page,
        limit=per_page
    )
    
    # Convert to schemas
    file_schemas = [
        FileSchema(
            id=file.id,
            filename=file.filename,
            content_type=file.content_type,
            user_id=file.user_id,
            created_at=file.created_at
        )
        for file in files
    ]
    
    return {
        "files": file_schemas,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

### File Metadata Retrieval

```python
async def get_file_metadata(filename: str, current_user: User):
    # Retrieve file from repository
    file_record = await file_repository.get_file_by_filename(filename)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check ownership
    if file_record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Return validated schema
    return FileSchema(
        id=file_record.id,
        filename=file_record.filename,
        content_type=file_record.content_type,
        user_id=file_record.user_id,
        created_at=file_record.created_at
    )
```

### ORM Model Conversion

```python
# Direct conversion from SQLAlchemy model
from src.models.file import File

def convert_file_model_to_schema(file_model: File) -> FileSchema:
    """Convert File ORM model to FileSchema."""
    return FileSchema.model_validate(file_model)

# Bulk conversion
def convert_file_models_to_schemas(file_models: list[File]) -> list[FileSchema]:
    """Convert multiple File ORM models to FileSchema list."""
    return [FileSchema.model_validate(file) for file in file_models]
```

## Security Considerations

### Data Validation

**Input Sanitization:**
- Field length limits prevent buffer overflow attacks
- Required field validation prevents null pointer issues
- Type validation ensures data integrity
- MIME type validation enables security checks

**Access Control Support:**
- User ID field enables ownership verification
- File ID provides unique resource identification
- Created timestamp supports audit trails
- Content type enables security filtering

### Privacy Protection

**Metadata Security:**
- Only essential metadata exposed in schema
- No sensitive file content in metadata
- User ownership clearly identified
- Timestamps support compliance requirements

**API Security:**
- Schema validation prevents injection attacks
- Field constraints limit resource consumption
- Type safety prevents data corruption
- Documentation supports secure API usage

## Performance Considerations

### Serialization Optimization

**Efficient Conversion:**
```python
# Fast ORM to schema conversion
file_schema = FileSchema.model_validate(file_orm_object)

# Bulk conversion optimization
file_schemas = [FileSchema.model_validate(f) for f in file_list]
```

**Memory Management:**
- Minimal memory footprint with only essential fields
- Efficient datetime handling
- String field length optimization
- Integer fields for numerical data

### Database Integration

**Query Optimization:**
- Schema aligns with database indexes
- Efficient foreign key relationships
- Minimal data transfer requirements
- Support for pagination queries

## Error Handling

### Validation Error Patterns

```python
# File schema validation errors
try:
    file_schema = FileSchema(**file_data)
except ValidationError as e:
    # Handle specific validation failures
    for error in e.errors():
        field = error["loc"][-1]
        error_type = error["type"]
        
        if field == "filename" and "max_length" in error_type:
            raise HTTPException(
                status_code=400, 
                detail="Filename too long (maximum 255 characters)"
            )
        elif field == "content_type" and "max_length" in error_type:
            raise HTTPException(
                status_code=400,
                detail="Content type too long (maximum 128 characters)"
            )
        elif field == "user_id" and "int_parsing" in error_type:
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID format"
            )
```

### ORM Conversion Errors

```python
# Handle ORM to schema conversion errors
try:
    file_schema = FileSchema.model_validate(file_orm)
except ValidationError as e:
    logger.error(f"Failed to convert file ORM to schema: {e}")
    raise HTTPException(
        status_code=500,
        detail="Internal error processing file metadata"
    )
```

## Best Practices

### Schema Design

- **Single Responsibility**: Schema focused solely on file metadata
- **Comprehensive Documentation**: All fields clearly documented
- **Type Safety**: Strong typing throughout the schema
- **Validation**: Appropriate constraints for all fields
- **ORM Integration**: Seamless database model conversion

### API Integration

- **Consistent Response Format**: Standardized file metadata structure
- **Error Handling**: Clear validation error messages
- **Performance**: Efficient serialization and validation
- **Security**: Proper field validation and constraints
- **Documentation**: OpenAPI schema generation support

### Database Compatibility

- **Field Alignment**: Schema fields match database columns
- **Constraint Consistency**: Validation rules align with DB constraints
- **Type Mapping**: Proper Python to SQL type mapping
- **Index Support**: Schema supports efficient database queries

## Testing Strategies

### Unit Testing

```python
def test_file_schema_creation():
    # Test valid file schema creation
    file_data = {
        "id": 1,
        "filename": "test.pdf",
        "content_type": "application/pdf",
        "user_id": 123,
        "created_at": datetime(2024, 1, 1, 12, 0, 0)
    }
    
    file_schema = FileSchema(**file_data)
    assert file_schema.id == 1
    assert file_schema.filename == "test.pdf"
    assert file_schema.content_type == "application/pdf"
    assert file_schema.user_id == 123

def test_file_schema_validation():
    # Test filename length constraint
    with pytest.raises(ValidationError):
        FileSchema(
            id=1,
            filename="x" * 256,  # Too long
            content_type="text/plain",
            user_id=123,
            created_at=datetime.now()
        )
    
    # Test content type length constraint
    with pytest.raises(ValidationError):
        FileSchema(
            id=1,
            filename="test.txt",
            content_type="x" * 129,  # Too long
            user_id=123,
            created_at=datetime.now()
        )
```

### ORM Integration Testing

```python
def test_orm_to_schema_conversion():
    # Test conversion from ORM model
    from src.models.file import File
    
    # Create mock ORM object
    file_orm = File(
        id=1,
        filename="test.pdf",
        content_type="application/pdf",
        user_id=123,
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    # Convert to schema
    file_schema = FileSchema.model_validate(file_orm)
    
    # Verify conversion
    assert file_schema.id == file_orm.id
    assert file_schema.filename == file_orm.filename
    assert file_schema.content_type == file_orm.content_type
    assert file_schema.user_id == file_orm.user_id
    assert file_schema.created_at == file_orm.created_at
```

### API Integration Testing

```python
async def test_file_upload_response_schema():
    # Test complete file upload workflow
    upload_data = {
        "filename": "integration_test.pdf",
        "content_type": "application/pdf",
        "user_id": 123
    }
    
    # Simulate file upload
    uploaded_file = await upload_file_service(upload_data)
    
    # Convert to schema
    file_response = FileSchema.model_validate(uploaded_file)
    
    # Verify response structure
    assert isinstance(file_response.id, int)
    assert file_response.filename == "integration_test.pdf"
    assert file_response.content_type == "application/pdf"
    assert file_response.user_id == 123
    assert isinstance(file_response.created_at, datetime)
```

## Related Files

### Dependencies

- `datetime` - Timestamp handling for file creation
- `pydantic` - Schema validation framework with Field and ConfigDict
- `typing` - Type annotations for schema fields

### Model Integration

- `src.models.file` - File SQLAlchemy ORM model
- `src.repositories.file` - File data access layer
- `src.services.upload` - File upload business logic

### API Integration

- `src.api.v1.uploads` - File upload endpoints
- `src.api.v1.users.core` - User file management endpoints
- `src.api.deps` - Dependency injection for current user

## Configuration

### Schema Settings

```python
# File schema configuration
FILE_SCHEMA_CONFIG = {
    "max_filename_length": 255,
    "max_content_type_length": 128,
    "from_attributes": True,
    "validate_assignment": True
}
```

### Field Constraints

```python
# Standard file metadata limits
MAX_FILENAME_LENGTH = 255      # Filesystem compatibility
MAX_CONTENT_TYPE_LENGTH = 128  # Comprehensive MIME type support
REQUIRED_FIELDS = ["id", "filename", "content_type", "user_id", "created_at"]
```

### MIME Type Support

```python
# Common supported MIME types
SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/jpeg",
    "image/png",
    "image/gif"
]
```

This file schema module provides a focused, efficient foundation for file metadata validation and serialization in the ReViewPoint application, ensuring data integrity, type safety, and seamless integration between the API layer and database models through well-designed Pydantic validation patterns.
