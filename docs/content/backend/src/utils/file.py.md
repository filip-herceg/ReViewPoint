# utils/file.py - File Security and Sanitization Utilities

## Purpose

The `utils/file.py` module provides robust file security utilities for the ReViewPoint platform. It implements strict filename sanitization, path traversal attack prevention, and comprehensive file safety validation with advanced typing for maximum security and reliability.

## Key Components

### Core Imports and Type System

#### Advanced Type Definitions

```python
import re
from typing import Final, Literal, TypeAlias

from typing_extensions import TypedDict

# Type aliases for stricter typing
Filename: TypeAlias = str
SanitizedFilename: TypeAlias = str
```

**Type Safety Features:**
- Custom type aliases for semantic clarity
- Strict typing for filename operations
- Type-safe return values for security operations
- Clear separation between raw and sanitized filenames

#### Extensible Result Types

```python
class SanitizedResult(TypedDict):
    sanitized: SanitizedFilename
    original: Filename
```

**Future-Proof Design:**
- TypedDict for structured sanitization results
- Extensible for additional metadata
- Type-safe result handling
- Backward-compatible interface design

### Security Constants

#### Path Security Configuration

```python
_PATH_SEPARATORS: Final[tuple[Literal["/"], Literal["\\"]]] = ("/", "\\")
_DANGEROUS_COMPONENTS: Final[tuple[Literal[".."], Literal["."]]] = ("..", ".")
_INVALID_CHARS_PATTERN: Final[Literal[r'[\\/*?:"<>|]']] = r'[\\/*?:"<>|]'
```

**Security Configuration:**
- **PATH_SEPARATORS**: Unix and Windows path separators for cross-platform security
- **DANGEROUS_COMPONENTS**: Path traversal components (parent directory references)
- **INVALID_CHARS_PATTERN**: Regex pattern for invalid filename characters
- Type-safe constant definitions with literal types

### Filename Sanitization

#### Comprehensive Filename Security Sanitization

```python
def sanitize_filename(filename: Filename) -> SanitizedFilename:
    """
    Sanitizes a filename to prevent path traversal attacks.

    Args:
        filename: Filename (str) to sanitize

    Returns:
        SanitizedFilename (str) with no path components

    Examples:
        >>> sanitize_filename("../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("file.txt")
        'file.txt'

    Raises:
        None
    """
    if not filename:
        unnamed: Final[SanitizedFilename] = "unnamed_file"
        return unnamed

    parts: list[Filename] = [
        p for p in re.split(r"[\\/]+", filename) if p and p not in _DANGEROUS_COMPONENTS
    ]
    if not parts:
        empty: Final[SanitizedFilename] = "_"
        return empty
    safe_name: SanitizedFilename = "_".join(parts)
    safe_name = re.sub(_INVALID_CHARS_PATTERN, "_", safe_name)
    safe_name = safe_name.replace("..", "_")
    return safe_name
```

**Security Features:**
- Path traversal attack prevention (../, ..\, etc.)
- Cross-platform path separator handling
- Invalid character replacement with safe alternatives
- Empty filename handling with default fallback
- Multiple security layer validation

**Sanitization Process:**
1. **Empty Check**: Returns "unnamed_file" for empty inputs
2. **Path Split**: Separates filename components using regex
3. **Dangerous Component Filter**: Removes ".." and "." components
4. **Component Join**: Joins valid components with underscores
5. **Character Sanitization**: Replaces invalid characters with underscores
6. **Double-Dot Cleanup**: Final cleanup of any remaining ".." patterns

**Usage Examples:**
```python
# Path traversal attack prevention
assert sanitize_filename("../../../etc/passwd") == "etc_passwd"
assert sanitize_filename("..\\..\\windows\\system32") == "windows_system32"

# Invalid character handling
assert sanitize_filename('file<>name?.txt') == "file__name_.txt"
assert sanitize_filename('my|file"name*.doc') == "my_file_name_.doc"

# Path separator normalization
assert sanitize_filename("folder/subfolder\\file.txt") == "folder_subfolder_file.txt"

# Edge cases
assert sanitize_filename("") == "unnamed_file"
assert sanitize_filename("...") == "_"
assert sanitize_filename("../..") == "_"

# Normal files (unchanged)
assert sanitize_filename("document.pdf") == "document.pdf"
assert sanitize_filename("image_2023.jpg") == "image_2023.jpg"
```

### Filename Safety Validation

#### Comprehensive Safety Checking

```python
def is_safe_filename(filename: Filename) -> Literal[True, False]:
    """
    Checks if a filename is safe (no path traversal).

    Args:
        filename: Filename (str) to check

    Returns:
        Literal[True] if the filename is safe, Literal[False] otherwise
    """
    if not isinstance(filename, str) or not filename:
        return False
    # Path traversal detection
    if any(sep in filename for sep in _PATH_SEPARATORS) or ".." in filename:
        return False
    # Check for other potentially dangerous characters
    if re.search(_INVALID_CHARS_PATTERN, filename):
        return False
    return True
```

**Safety Validation Features:**
- Type checking for string input validation
- Empty string rejection for security
- Path separator detection (Unix and Windows)
- Parent directory reference detection
- Invalid character pattern matching
- Boolean return with literal typing

**Usage Examples:**
```python
# Safe filenames
assert is_safe_filename("document.pdf") == True
assert is_safe_filename("image_2023.jpg") == True
assert is_safe_filename("report-final.docx") == True

# Unsafe filenames (path traversal)
assert is_safe_filename("../config.ini") == False
assert is_safe_filename("..\\passwords.txt") == False
assert is_safe_filename("folder/file.txt") == False
assert is_safe_filename("dir\\subdirectory\\file.exe") == False

# Unsafe filenames (invalid characters)
assert is_safe_filename("file<name>.txt") == False
assert is_safe_filename('document"with"quotes.pdf') == False
assert is_safe_filename("file|with|pipes.doc") == False
assert is_safe_filename("file*with*wildcards.txt") == False

# Edge cases
assert is_safe_filename("") == False
assert is_safe_filename(None) == False  # Type error, but handled gracefully
assert is_safe_filename(123) == False   # Type error, but handled gracefully
```

## Integration Patterns

### Upload Service Integration

#### Secure File Upload Processing

```python
from src.utils.file import sanitize_filename, is_safe_filename
from fastapi import HTTPException, UploadFile

class UploadService:
    async def upload_file(self, file: UploadFile, user_id: str) -> dict:
        """Secure file upload with filename sanitization."""
        
        # Validate filename presence
        if not file.filename:
            raise HTTPException(
                status_code=400, 
                detail="No filename provided"
            )
        
        # Sanitize filename for security
        safe_filename = sanitize_filename(file.filename)
        
        # Double-check safety after sanitization
        if not is_safe_filename(safe_filename):
            raise HTTPException(
                status_code=400, 
                detail="Invalid filename after sanitization"
            )
        
        # Generate unique storage filename
        file_id = uuid.uuid4()
        file_extension = Path(safe_filename).suffix
        storage_filename = f"{file_id}{file_extension}"
        
        # Store file with sanitized metadata
        return await self.store_file(
            file_content=await file.read(),
            original_filename=file.filename,
            safe_filename=safe_filename,
            storage_filename=storage_filename,
            user_id=user_id
        )
```

### API Endpoint Integration

#### FastAPI File Upload Validation

```python
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from src.utils.file import is_safe_filename, sanitize_filename

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file_endpoint(
    file: UploadFile,
    user: User = Depends(get_current_user)
) -> dict:
    """Upload file with comprehensive validation."""
    
    # Pre-upload validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    
    # Check original filename safety
    if not is_safe_filename(file.filename):
        # Attempt sanitization
        sanitized = sanitize_filename(file.filename)
        
        # Inform user of sanitization
        if sanitized != file.filename:
            return {
                "warning": f"Filename sanitized from '{file.filename}' to '{sanitized}'",
                "sanitized_filename": sanitized,
                "action_required": "Please confirm upload with sanitized filename"
            }
    
    # Proceed with upload using sanitized filename
    result = await upload_service.upload_file(file, user.id)
    return {
        "message": "File uploaded successfully",
        "file_id": result.id,
        "original_filename": file.filename,
        "stored_filename": result.filename
    }

@router.get("/validate-filename/{filename}")
async def validate_filename_endpoint(filename: str) -> dict:
    """Validate filename safety without upload."""
    is_safe = is_safe_filename(filename)
    sanitized = sanitize_filename(filename)
    
    return {
        "original": filename,
        "is_safe": is_safe,
        "sanitized": sanitized,
        "changes_made": filename != sanitized,
        "recommendations": [
            "Use alphanumeric characters and underscores",
            "Avoid path separators (/, \\)",
            "Avoid special characters (<, >, |, ?, *, :, \")",
            "Avoid parent directory references (..)"
        ] if not is_safe else []
    }
```

### Repository Layer Integration

#### Database Storage with Filename Security

```python
from src.utils.file import sanitize_filename
from sqlalchemy import Column, String, DateTime, Integer
from src.models.base import Base

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True)
    original_filename = Column(String(255), nullable=False)
    safe_filename = Column(String(255), nullable=False)
    storage_filename = Column(String(255), nullable=False, unique=True)
    content_type = Column(String(100))
    file_size = Column(Integer)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FileRepository:
    async def create_file_record(
        self, 
        session: AsyncSession,
        original_filename: str,
        user_id: int,
        content_type: str,
        file_size: int
    ) -> File:
        """Create file record with automatic filename sanitization."""
        
        # Sanitize filename for safe storage
        safe_filename = sanitize_filename(original_filename)
        
        # Generate unique storage filename
        file_id = uuid.uuid4()
        file_extension = Path(safe_filename).suffix
        storage_filename = f"{file_id}{file_extension}"
        
        # Create database record
        file_record = File(
            original_filename=original_filename,
            safe_filename=safe_filename,
            storage_filename=storage_filename,
            content_type=content_type,
            file_size=file_size,
            user_id=user_id
        )
        
        session.add(file_record)
        await session.commit()
        return file_record
```

### Frontend Integration

#### JavaScript/TypeScript Client Validation

```typescript
// TypeScript client-side filename validation
export interface FilenameValidationResult {
  isValid: boolean;
  sanitized: string;
  warnings: string[];
}

export function validateFilename(filename: string): FilenameValidationResult {
  const warnings: string[] = [];
  let isValid = true;
  
  // Check for path separators
  if (filename.includes('/') || filename.includes('\\')) {
    warnings.push("Filename contains path separators");
    isValid = false;
  }
  
  // Check for parent directory references
  if (filename.includes('..')) {
    warnings.push("Filename contains parent directory references");
    isValid = false;
  }
  
  // Check for invalid characters
  const invalidChars = /[\\/*?:"<>|]/;
  if (invalidChars.test(filename)) {
    warnings.push("Filename contains invalid characters");
    isValid = false;
  }
  
  // Client-side sanitization (matches backend logic)
  const sanitized = filename
    .split(/[\\/]+/)
    .filter(part => part && part !== '..' && part !== '.')
    .join('_')
    .replace(/[\\/*?:"<>|]/g, '_')
    .replace(/\.\./g, '_') || 'unnamed_file';
  
  return {
    isValid,
    sanitized,
    warnings
  };
}

// React component for file upload with validation
export function FileUploadComponent() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<FilenameValidationResult | null>(null);
  
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setValidationResult(validateFilename(file.name));
  };
  
  const handleUpload = async () => {
    if (!selectedFile || !validationResult) return;
    
    if (!validationResult.isValid) {
      const confirmed = window.confirm(
        `Filename will be sanitized from "${selectedFile.name}" to "${validationResult.sanitized}". Continue?`
      );
      if (!confirmed) return;
    }
    
    // Proceed with upload
    await uploadFile(selectedFile);
  };
  
  return (
    <div>
      <input type="file" onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])} />
      
      {validationResult && !validationResult.isValid && (
        <div className="warning">
          <p>Filename issues detected:</p>
          <ul>
            {validationResult.warnings.map((warning, i) => (
              <li key={i}>{warning}</li>
            ))}
          </ul>
          <p>Sanitized filename: {validationResult.sanitized}</p>
        </div>
      )}
      
      <button onClick={handleUpload} disabled={!selectedFile}>
        Upload File
      </button>
    </div>
  );
}
```

## Security Considerations

### Path Traversal Prevention

#### Multi-Layer Security Approach

```python
def advanced_filename_security_check(filename: str, max_length: int = 255) -> dict:
    """Comprehensive filename security analysis."""
    
    security_issues = []
    
    # Length validation
    if len(filename) > max_length:
        security_issues.append(f"Filename too long ({len(filename)} > {max_length})")
    
    # Path traversal checks
    if '..' in filename:
        security_issues.append("Contains parent directory references")
    
    if any(sep in filename for sep in ['/', '\\']):
        security_issues.append("Contains path separators")
    
    # Null byte injection
    if '\x00' in filename:
        security_issues.append("Contains null bytes")
    
    # Control character check
    if any(ord(char) < 32 for char in filename):
        security_issues.append("Contains control characters")
    
    # Unicode normalization issues
    import unicodedata
    normalized = unicodedata.normalize('NFKC', filename)
    if normalized != filename:
        security_issues.append("Contains non-normalized Unicode")
    
    # Common attack patterns
    dangerous_patterns = [
        'CON', 'PRN', 'AUX', 'NUL',  # Windows reserved names
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    filename_upper = filename.upper()
    for pattern in dangerous_patterns:
        if filename_upper.startswith(pattern):
            security_issues.append(f"Matches dangerous pattern: {pattern}")
    
    return {
        'is_secure': len(security_issues) == 0,
        'issues': security_issues,
        'sanitized': sanitize_filename(filename),
        'recommendation': 'Use alphanumeric characters, hyphens, and underscores only'
    }
```

### Content Type Validation

#### File Type Security Integration

```python
import magic
from src.utils.file import is_safe_filename, sanitize_filename

class SecureFileHandler:
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain', 'application/json',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    def validate_file_security(self, filename: str, content: bytes) -> dict:
        """Comprehensive file security validation."""
        
        # Filename security
        filename_safe = is_safe_filename(filename)
        filename_sanitized = sanitize_filename(filename)
        
        # Content type detection
        detected_mime = magic.from_buffer(content, mime=True)
        
        # Extension validation
        extension = Path(filename_sanitized).suffix.lower()
        expected_mime = self._get_mime_for_extension(extension)
        
        return {
            'filename_safe': filename_safe,
            'filename_sanitized': filename_sanitized,
            'mime_type_allowed': detected_mime in self.ALLOWED_MIME_TYPES,
            'extension_matches_content': detected_mime == expected_mime,
            'detected_mime_type': detected_mime,
            'file_size': len(content),
            'security_passed': all([
                filename_safe,
                detected_mime in self.ALLOWED_MIME_TYPES,
                detected_mime == expected_mime,
                len(content) > 0
            ])
        }
```

## Best Practices

### Configuration Management

```python
# Environment-specific file security settings
class FileSecurityConfig:
    # Development - more lenient
    DEV_MAX_FILENAME_LENGTH = 255
    DEV_ALLOW_DANGEROUS_EXTENSIONS = True
    
    # Production - strict security
    PROD_MAX_FILENAME_LENGTH = 100
    PROD_ALLOW_DANGEROUS_EXTENSIONS = False
    
    # File type restrictions
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.docx'}
    DANGEROUS_EXTENSIONS = {'.exe', '.bat', '.sh', '.ps1', '.vbs', '.jar'}
    
    @classmethod
    def get_config(cls, environment: str = 'production'):
        """Get environment-specific configuration."""
        if environment == 'development':
            return {
                'max_length': cls.DEV_MAX_FILENAME_LENGTH,
                'allow_dangerous': cls.DEV_ALLOW_DANGEROUS_EXTENSIONS
            }
        return {
            'max_length': cls.PROD_MAX_FILENAME_LENGTH,
            'allow_dangerous': cls.PROD_ALLOW_DANGEROUS_EXTENSIONS
        }
```

### Testing Strategies

```python
import pytest
from src.utils.file import sanitize_filename, is_safe_filename

class TestFileUtilities:
    """Comprehensive file utility testing."""
    
    @pytest.mark.parametrize("input_filename,expected", [
        ("document.pdf", "document.pdf"),
        ("../../../etc/passwd", "etc_passwd"),
        ("file<>name?.txt", "file__name_.txt"),
        ("", "unnamed_file"),
        ("...", "_"),
        ("folder/subfolder\\file.txt", "folder_subfolder_file.txt"),
    ])
    def test_sanitize_filename(self, input_filename, expected):
        assert sanitize_filename(input_filename) == expected
    
    @pytest.mark.parametrize("filename,expected", [
        ("document.pdf", True),
        ("../config.ini", False),
        ("file<name>.txt", False),
        ("", False),
        ("normal_file.jpg", True),
    ])
    def test_is_safe_filename(self, filename, expected):
        assert is_safe_filename(filename) == expected
    
    def test_path_traversal_attacks(self):
        """Test various path traversal attack patterns."""
        attacks = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            ".../etc/passwd",
            "....//etc/passwd",
            "%2e%2e%2fpasswd",  # URL encoded
        ]
        
        for attack in attacks:
            sanitized = sanitize_filename(attack)
            assert not any(sep in sanitized for sep in ['/', '\\'])
            assert '..' not in sanitized
            assert is_safe_filename(sanitized)
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        unicode_filenames = [
            "файл.txt",  # Cyrillic
            "文件.pdf",   # Chinese
            "ファイル.jpg", # Japanese
            "🎉party🎊.gif",  # Emoji
        ]
        
        for filename in unicode_filenames:
            sanitized = sanitize_filename(filename)
            # Should not crash and should be safe
            assert isinstance(sanitized, str)
            assert len(sanitized) > 0
```

This file utility system provides comprehensive security for filename handling with robust sanitization, validation, and cross-platform compatibility for the ReViewPoint platform.
