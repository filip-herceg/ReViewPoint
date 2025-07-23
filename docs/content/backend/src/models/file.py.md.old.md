# backend/src/models/file.py - File Model Definition

## Purpose

The `File` model represents uploaded files in the ReViewPoint platform, providing comprehensive file metadata management, relationship tracking, and business logic for file operations. This SQLAlchemy model handles PDF documents and other file types with full audit trails, security features, and integration with the user management system.

## Key Components

### File Model Class

The main SQLAlchemy model that defines the file entity structure:

```python
class File(BaseModel):
    """
    SQLAlchemy model for uploaded files.

    Represents files uploaded by users with comprehensive metadata,
    security tracking, and relationship management.
    """

    __tablename__ = "files"
    __table_args__ = (
        Index('ix_files_uploaded_by', 'uploaded_by'),
        Index('ix_files_filename', 'filename'),
        Index('ix_files_status', 'status'),
        Index('ix_files_uploaded_at', 'uploaded_at'),
        Index('ix_files_mime_type', 'mime_type'),
        UniqueConstraint('file_path', name='uq_files_path'),
        CheckConstraint('file_size > 0', name='ck_files_size_positive'),
        CheckConstraint('char_length(filename) > 0', name='ck_files_filename_not_empty')
    )

    # Primary identification
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
        comment="Unique file identifier"
    )

    # File metadata
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original filename as uploaded"
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        comment="Unique storage path for the file"
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type of the file"
    )

    file_hash: Mapped[Optional[str]] = mapped_column(
        String(64),  # SHA-256 hash
        nullable=True,
        comment="SHA-256 hash for file integrity verification"
    )
```

### File Status and Classification

```python
class FileStatus(str, Enum):
    """File processing status enumeration."""

    UPLOADING = "uploading"      # File upload in progress
    UPLOADED = "uploaded"        # Successfully uploaded, ready for processing
    PROCESSING = "processing"    # File being processed/analyzed
    PROCESSED = "processed"      # Processing completed successfully
    FAILED = "failed"           # Processing or upload failed
    QUARANTINED = "quarantined" # File flagged for security review
    DELETED = "deleted"         # Soft deleted (marked for removal)

class FileType(str, Enum):
    """Supported file type categories."""

    PDF = "pdf"
    DOCUMENT = "document"  # Word, RTF, etc.
    TEXT = "text"         # Plain text files
    IMAGE = "image"       # Image files for OCR
    ARCHIVE = "archive"   # ZIP, TAR, etc.
    OTHER = "other"       # Other supported types

# Add status and type to model
status: Mapped[FileStatus] = mapped_column(
    Enum(FileStatus),
    nullable=False,
    default=FileStatus.UPLOADING,
    comment="Current file processing status"
)

file_type: Mapped[FileType] = mapped_column(
    Enum(FileType),
    nullable=False,
    default=FileType.OTHER,
    comment="File type category"
)
```

### User Relationship and Ownership

```python
# User relationship
uploaded_by: Mapped[UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    comment="ID of user who uploaded the file"
)

user: Mapped["User"] = relationship(
    "User",
    back_populates="files",
    lazy="select",
    doc="User who uploaded this file"
)

# Access control
is_public: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=False,
    comment="Whether file is publicly accessible"
)

access_level: Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    default="private",
    comment="Access level: private, shared, public"
)
```

### File Processing and Analysis

```python
# Processing metadata
processing_started_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="When file processing began"
)

processing_completed_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="When file processing completed"
)

processing_error: Mapped[Optional[str]] = mapped_column(
    Text,
    nullable=True,
    comment="Error message if processing failed"
)

# Analysis results
analysis_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(
    JSON,
    nullable=True,
    comment="JSON storage for analysis results"
)

extracted_text: Mapped[Optional[str]] = mapped_column(
    Text,
    nullable=True,
    comment="Extracted text content for search/analysis"
)

page_count: Mapped[Optional[int]] = mapped_column(
    Integer,
    nullable=True,
    comment="Number of pages (for documents)"
)

word_count: Mapped[Optional[int]] = mapped_column(
    Integer,
    nullable=True,
    comment="Estimated word count"
)
```

### File Metadata and Tags

```python
# Extended metadata
title: Mapped[Optional[str]] = mapped_column(
    String(500),
    nullable=True,
    comment="Document title (extracted or user-provided)"
)

description: Mapped[Optional[str]] = mapped_column(
    Text,
    nullable=True,
    comment="File description or abstract"
)

tags: Mapped[Optional[List[str]]] = mapped_column(
    JSON,
    nullable=True,
    comment="User-defined tags for categorization"
)

metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
    JSON,
    nullable=True,
    comment="Additional file metadata"
)

# Document-specific fields
authors: Mapped[Optional[List[str]]] = mapped_column(
    JSON,
    nullable=True,
    comment="Document authors (for papers/articles)"
)

publication_date: Mapped[Optional[date]] = mapped_column(
    Date,
    nullable=True,
    comment="Publication date (for academic papers)"
)

doi: Mapped[Optional[str]] = mapped_column(
    String(100),
    nullable=True,
    comment="Digital Object Identifier"
)

journal: Mapped[Optional[str]] = mapped_column(
    String(200),
    nullable=True,
    comment="Journal or publication venue"
)
```

### Security and Audit Trail

```python
# Security tracking
virus_scan_status: Mapped[Optional[str]] = mapped_column(
    String(20),
    nullable=True,
    comment="Virus scan result: clean, infected, pending, failed"
)

virus_scan_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="When virus scan was performed"
)

quarantine_reason: Mapped[Optional[str]] = mapped_column(
    Text,
    nullable=True,
    comment="Reason for quarantine if applicable"
)

# Access tracking
download_count: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    default=0,
    comment="Number of times file was downloaded"
)

last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Last time file was accessed"
)

# Audit fields (inherited from BaseModel)
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    server_default=func.now(),
    comment="File upload timestamp"
)

updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    onupdate=func.now(),
    comment="Last modification timestamp"
)

uploaded_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    server_default=func.now(),
    comment="When file upload completed"
)
```

### Business Logic Methods

#### File Operations

```python
def get_file_extension(self) -> str:
    """
    Get file extension from filename.

    Returns:
        File extension in lowercase (without dot)
    """
    if '.' in self.filename:
        return self.filename.rsplit('.', 1)[1].lower()
    return ''

def get_display_name(self) -> str:
    """
    Get display-friendly filename.

    Returns:
        Title if available, otherwise filename
    """
    return self.title or self.filename

def is_pdf(self) -> bool:
    """Check if file is a PDF document."""
    return (
        self.mime_type == 'application/pdf' or
        self.get_file_extension() == 'pdf'
    )

def is_document(self) -> bool:
    """Check if file is a document type."""
    document_types = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/rtf',
        'text/plain'
    }
    return self.mime_type in document_types

def is_image(self) -> bool:
    """Check if file is an image."""
    return self.mime_type.startswith('image/')
```

#### Status Management

```python
def mark_as_uploaded(self) -> None:
    """Mark file as successfully uploaded."""
    self.status = FileStatus.UPLOADED
    self.uploaded_at = datetime.utcnow()

def mark_processing_started(self) -> None:
    """Mark file processing as started."""
    self.status = FileStatus.PROCESSING
    self.processing_started_at = datetime.utcnow()
    self.processing_error = None

def mark_processing_completed(self, results: Optional[Dict[str, Any]] = None) -> None:
    """Mark file processing as completed."""
    self.status = FileStatus.PROCESSED
    self.processing_completed_at = datetime.utcnow()
    self.processing_error = None

    if results:
        self.analysis_results = results

def mark_processing_failed(self, error: str) -> None:
    """Mark file processing as failed."""
    self.status = FileStatus.FAILED
    self.processing_error = error
    self.processing_completed_at = datetime.utcnow()

def quarantine(self, reason: str) -> None:
    """Quarantine file for security review."""
    self.status = FileStatus.QUARANTINED
    self.quarantine_reason = reason
```

#### Security and Validation

```python
def is_safe_to_process(self) -> bool:
    """
    Check if file is safe for processing.

    Returns:
        True if file can be safely processed
    """
    # Check virus scan status
    if self.virus_scan_status == "infected":
        return False

    # Check if quarantined
    if self.status == FileStatus.QUARANTINED:
        return False

    # Check file size limits
    if self.file_size > get_setting("MAX_FILE_SIZE", 100 * 1024 * 1024):  # 100MB default
        return False

    return True

def validate_file_hash(self, expected_hash: str) -> bool:
    """
    Validate file integrity using hash.

    Args:
        expected_hash: Expected SHA-256 hash

    Returns:
        True if hash matches
    """
    return self.file_hash == expected_hash

def increment_download_count(self) -> None:
    """Increment download counter and update last access."""
    self.download_count += 1
    self.last_accessed_at = datetime.utcnow()
```

#### Search and Analysis

```python
def get_searchable_content(self) -> str:
    """
    Get content for full-text search indexing.

    Returns:
        Combined searchable text
    """
    content_parts = []

    # Add basic metadata
    content_parts.append(self.filename)
    if self.title:
        content_parts.append(self.title)
    if self.description:
        content_parts.append(self.description)

    # Add extracted text
    if self.extracted_text:
        content_parts.append(self.extracted_text)

    # Add tags
    if self.tags:
        content_parts.extend(self.tags)

    # Add authors and journal
    if self.authors:
        content_parts.extend(self.authors)
    if self.journal:
        content_parts.append(self.journal)

    return ' '.join(content_parts)

def has_analysis_result(self, analysis_type: str) -> bool:
    """
    Check if specific analysis result exists.

    Args:
        analysis_type: Type of analysis to check

    Returns:
        True if analysis result exists
    """
    if not self.analysis_results:
        return False

    return analysis_type in self.analysis_results

def get_analysis_result(self, analysis_type: str, default=None):
    """
    Get specific analysis result.

    Args:
        analysis_type: Type of analysis result
        default: Default value if not found

    Returns:
        Analysis result or default
    """
    if not self.analysis_results:
        return default

    return self.analysis_results.get(analysis_type, default)
```

### Computed Properties

```python
@hybrid_property
def file_size_mb(self) -> float:
    """File size in megabytes."""
    return round(self.file_size / (1024 * 1024), 2)

@hybrid_property
def processing_duration(self) -> Optional[timedelta]:
    """Duration of file processing."""
    if not self.processing_started_at or not self.processing_completed_at:
        return None

    return self.processing_completed_at - self.processing_started_at

@hybrid_property
def is_processed(self) -> bool:
    """Check if file has been processed successfully."""
    return self.status == FileStatus.PROCESSED

@hybrid_property
def age_days(self) -> int:
    """Age of file in days since upload."""
    delta = datetime.utcnow() - self.uploaded_at
    return delta.days

@hybrid_property
def storage_path(self) -> Path:
    """Get Path object for file storage location."""
    return Path(self.file_path)
```

### Database Relationships

```python
# Relationship with analysis results (if separate table exists)
analysis_runs: Mapped[List["AnalysisRun"]] = relationship(
    "AnalysisRun",
    back_populates="file",
    cascade="all, delete-orphan",
    lazy="dynamic",
    doc="Analysis runs performed on this file"
)

# Relationship with file shares (if implementing sharing)
shares: Mapped[List["FileShare"]] = relationship(
    "FileShare",
    back_populates="file",
    cascade="all, delete-orphan",
    lazy="dynamic",
    doc="Sharing records for this file"
)

# Comments or annotations (if implemented)
annotations: Mapped[List["FileAnnotation"]] = relationship(
    "FileAnnotation",
    back_populates="file",
    cascade="all, delete-orphan",
    lazy="dynamic",
    doc="User annotations on this file"
)
```

## Dependencies

### Core Dependencies

```python
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, DateTime, Date, Text, JSON,
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Enum,
    func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, hybrid_property
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID, uuid4
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
from enum import Enum as PyEnum

# Internal Dependencies
from src.models.base import BaseModel
from src.core.config import get_setting
```

### File System Integration

- **Path**: File system path handling
- **Storage backends**: Local file system, S3, etc.
- **File validation**: MIME type detection, virus scanning
- **Hash computation**: File integrity verification

## Usage Examples

### Basic File Operations

```python
# Create new file record
new_file = File(
    filename="research_paper.pdf",
    file_path="/uploads/2024/01/uuid-filename.pdf",
    file_size=2048576,
    mime_type="application/pdf",
    uploaded_by=user.id,
    file_type=FileType.PDF
)

# Mark as uploaded
new_file.mark_as_uploaded()

# Start processing
new_file.mark_processing_started()

# Complete processing with results
analysis_results = {
    "text_extraction": {"success": True, "word_count": 5420},
    "classification": {"type": "research_paper", "confidence": 0.95}
}
new_file.mark_processing_completed(analysis_results)
```

### File Validation and Security

```python
# Check if file is safe to process
if file.is_safe_to_process():
    # Validate file hash
    if file.validate_file_hash(computed_hash):
        # Process file
        process_file(file)
    else:
        file.quarantine("Hash mismatch detected")
else:
    logger.warning(f"File {file.id} not safe for processing")
```

### Search and Analysis

```python
# Get searchable content
content = file.get_searchable_content()

# Check for specific analysis
if file.has_analysis_result("sentiment_analysis"):
    sentiment = file.get_analysis_result("sentiment_analysis")
    print(f"Sentiment: {sentiment}")

# Update download statistics
file.increment_download_count()
```

### File Metadata Management

```python
# Update file metadata
file.title = "Advanced Machine Learning Techniques"
file.authors = ["Dr. Jane Smith", "Prof. John Doe"]
file.publication_date = date(2024, 1, 15)
file.tags = ["machine learning", "AI", "research"]
file.description = "Comprehensive study on advanced ML techniques"

# Add custom metadata
file.metadata = {
    "conference": "ICML 2024",
    "keywords": ["neural networks", "deep learning"],
    "impact_factor": 3.2
}
```

## Testing

### Model Testing

```python
import pytest
from datetime import datetime, timedelta

def test_file_creation():
    """Test basic file model creation."""
    file = File(
        filename="test.pdf",
        file_path="/test/path.pdf",
        file_size=1024,
        mime_type="application/pdf",
        uploaded_by=user_id
    )

    assert file.filename == "test.pdf"
    assert file.file_size_mb == 0.001
    assert file.is_pdf() is True
    assert file.get_file_extension() == "pdf"

def test_file_status_transitions():
    """Test file status management."""
    file = File(
        filename="test.pdf",
        file_path="/test/path.pdf",
        file_size=1024,
        mime_type="application/pdf",
        uploaded_by=user_id
    )

    # Initial status
    assert file.status == FileStatus.UPLOADING

    # Mark as uploaded
    file.mark_as_uploaded()
    assert file.status == FileStatus.UPLOADED
    assert file.uploaded_at is not None

    # Start processing
    file.mark_processing_started()
    assert file.status == FileStatus.PROCESSING
    assert file.processing_started_at is not None

    # Complete processing
    results = {"test": "data"}
    file.mark_processing_completed(results)
    assert file.status == FileStatus.PROCESSED
    assert file.analysis_results == results
    assert file.processing_completed_at is not None

def test_file_security_validation():
    """Test file security features."""
    file = File(
        filename="test.pdf",
        file_path="/test/path.pdf",
        file_size=1024,
        mime_type="application/pdf",
        uploaded_by=user_id,
        virus_scan_status="clean"
    )

    # Should be safe to process
    assert file.is_safe_to_process() is True

    # Quarantine file
    file.quarantine("Suspicious content detected")
    assert file.status == FileStatus.QUARANTINED
    assert file.is_safe_to_process() is False
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_file_with_user_relationship(async_db_session):
    """Test file with user relationship."""
    # Create user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed"
    )
    async_db_session.add(user)
    await async_db_session.commit()

    # Create file
    file = File(
        filename="test.pdf",
        file_path="/test/path.pdf",
        file_size=1024,
        mime_type="application/pdf",
        uploaded_by=user.id
    )
    async_db_session.add(file)
    await async_db_session.commit()

    # Test relationship
    await async_db_session.refresh(file, ["user"])
    assert file.user.email == "test@example.com"
```

## Related Files

- [User Model](user.py.md) - User model with file relationship
- [Upload Service](../services/upload.py.md) - Business logic for file uploads
- [File Repository](../repositories/file.py.md) - Data access layer for files
- [File Schemas](../schemas/file.py.md) - Pydantic schemas for file operations
- [Upload API](../api/v1/uploads.py.md) - REST API endpoints for file operations
- [Base Model](base.py.md) - Common model functionality and audit fields

## Performance Considerations

### Database Optimization

- **Indexes**: Strategic indexes on commonly queried fields
- **File path uniqueness**: Prevents duplicate storage
- **Relationship loading**: Lazy loading for large collections
- **JSON fields**: Efficient storage for metadata and analysis results

### File Storage

- **Path organization**: Hierarchical storage structure
- **Large file handling**: Streaming uploads for large files
- **Cleanup processes**: Automated removal of orphaned files
- **Storage backends**: Pluggable storage systems (local, S3, etc.)

## Security Features

- **File validation**: MIME type and extension verification
- **Virus scanning**: Integration with antivirus systems
- **Hash verification**: File integrity checking
- **Access control**: User-based file permissions
- **Quarantine system**: Isolation of suspicious files
- **Audit trail**: Complete tracking of file operations
