# File Utilities Documentation

## Purpose

The `file.py` module provides secure file handling utilities for the ReViewPoint application. This module focuses on filename sanitization and validation to prevent path traversal attacks and ensure safe file operations. It implements strict static typing and comprehensive security checks to protect against malicious file names and maintain file system security throughout the application.

## Architecture

The file utilities system follows a security-first design:

- **Strict Typing**: Comprehensive type aliases and strict typing for all file operations
- **Path Security**: Prevention of path traversal attacks through filename sanitization
- **Character Validation**: Removal and replacement of dangerous filename characters
- **Cross-Platform Safety**: Consistent behavior across different operating systems
- **Performance Optimized**: Fast string operations with compiled regex patterns
- **Type Safety**: TypedDict structures for extensible return types

## Type System

### Type Aliases

**Filename and Sanitized Filename Types:**

```python
from typing import TypeAlias

Filename: TypeAlias = str                    # Original filename input
SanitizedFilename: TypeAlias = str          # Sanitized filename output
```

**Purpose:**
- **Type Clarity**: Clear distinction between original and sanitized filenames
- **Type Safety**: Enables type checking for function parameters and returns
- **Documentation**: Self-documenting code through meaningful type names
- **Future-Proofing**: Easy to extend with additional validation requirements

### TypedDict Structures

**Sanitized Result Structure:**

```python
from typing_extensions import TypedDict

class SanitizedResult(TypedDict):
    sanitized: SanitizedFilename           # Cleaned filename
    original: Filename                     # Original input filename
```

**Design Benefits:**
- **Extensibility**: Easy to add additional metadata fields
- **Type Safety**: Structured return type with validation
- **Future Enhancement**: Ready for additional sanitization information
- **API Consistency**: Standardized return format for complex operations

## Security Constants

### Path Traversal Protection

**Path Separator Constants:**

```python
from typing import Final, Literal

_PATH_SEPARATORS: Final[tuple[Literal["/"], Literal["\\"]]] = ("/", "\\")
```

**Security Purpose:**
- **Cross-Platform**: Handles both Unix and Windows path separators
- **Attack Prevention**: Prevents directory traversal through path separators
- **Type Safety**: Literal types ensure exact string matching
- **Immutability**: Final constants prevent modification

**Dangerous Component Constants:**

```python
_DANGEROUS_COMPONENTS: Final[tuple[Literal[".."], Literal["."]]] = ("..", ".")
```

**Protection Against:**
- **Parent Directory Access**: Prevents `../` path traversal
- **Current Directory Reference**: Removes `.` components
- **Path Manipulation**: Blocks relative path components
- **Directory Escape**: Prevents breaking out of intended directories

### Character Filtering

**Invalid Character Pattern:**

```python
_INVALID_CHARS_PATTERN: Final[Literal[r'[\\/*?:"<>|]']] = r'[\\/*?:"<>|]'
```

**Blocked Characters:**
- `\` - Backslash (Windows path separator)
- `/` - Forward slash (Unix path separator)
- `*` - Wildcard character
- `?` - Question mark wildcard
- `:` - Colon (Windows drive separator)
- `"` - Double quote
- `<` - Less than symbol
- `>` - Greater than symbol
- `|` - Pipe character

**Security Rationale:**
- **File System Compatibility**: Ensures filenames work across all file systems
- **Injection Prevention**: Blocks characters used in command injection
- **Shell Safety**: Prevents shell metacharacters from causing issues
- **Cross-Platform**: Consistent behavior across operating systems

## Core Functions

### Filename Sanitization

**sanitize_filename Function:**

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
```

**Sanitization Process:**

1. **Empty Input Handling:**
   ```python
   if not filename:
       unnamed: Final[SanitizedFilename] = "unnamed_file"
       return unnamed
   ```

2. **Path Component Splitting:**
   ```python
   parts: list[Filename] = [
       p for p in re.split(r"[\\/]+", filename) 
       if p and p not in _DANGEROUS_COMPONENTS
   ]
   ```

3. **Empty Result Handling:**
   ```python
   if not parts:
       empty: Final[SanitizedFilename] = "_"
       return empty
   ```

4. **Character Sanitization:**
   ```python
   safe_name: SanitizedFilename = "_".join(parts)
   safe_name = re.sub(_INVALID_CHARS_PATTERN, "_", safe_name)
   safe_name = safe_name.replace("..", "_")
   return safe_name
   ```

**Security Features:**
- **Path Traversal Prevention**: Removes `../` and `./` components
- **Character Replacement**: Replaces dangerous characters with underscores
- **Empty Name Handling**: Provides default names for empty inputs
- **Cross-Platform**: Works consistently across operating systems

### Filename Validation

**is_safe_filename Function:**

```python
def is_safe_filename(filename: Filename) -> Literal[True, False]:
    """
    Checks if a filename is safe (no path traversal).
    
    Args:
        filename: Filename (str) to check
    
    Returns:
        Literal[True] if the filename is safe, Literal[False] otherwise
    """
```

**Validation Checks:**

1. **Type and Existence Validation:**
   ```python
   if not isinstance(filename, str) or not filename:
       return False
   ```

2. **Path Traversal Detection:**
   ```python
   if any(sep in filename for sep in _PATH_SEPARATORS) or ".." in filename:
       return False
   ```

3. **Character Validation:**
   ```python
   if re.search(_INVALID_CHARS_PATTERN, filename):
       return False
   ```

4. **Success Return:**
   ```python
   return True
   ```

**Use Cases:**
- **Input Validation**: Check filenames before processing
- **Security Verification**: Validate user-submitted filenames
- **API Validation**: Ensure filename parameters are safe
- **Upload Validation**: Check file uploads before storage

## Usage Patterns

### File Upload Security

**Secure File Upload Handler:**

```python
from src.utils.file import sanitize_filename, is_safe_filename
from fastapi import HTTPException, UploadFile

async def secure_file_upload(file: UploadFile, user_id: str) -> dict:
    """Secure file upload with filename sanitization."""
    
    # Get original filename
    original_filename = file.filename or "unnamed_file"
    
    # Validate filename safety
    if not is_safe_filename(original_filename):
        # Sanitize dangerous filename
        safe_filename = sanitize_filename(original_filename)
        
        logger.warning(f"Sanitized unsafe filename: {original_filename} -> {safe_filename}", extra={
            "user_id": user_id,
            "original_filename": original_filename,
            "sanitized_filename": safe_filename
        })
    else:
        safe_filename = original_filename
    
    # Additional validation
    if not safe_filename or safe_filename == "_":
        raise HTTPException(
            status_code=400,
            detail="Invalid filename provided"
        )
    
    # Generate unique filename to prevent conflicts
    timestamp = int(time.time())
    unique_filename = f"{user_id}_{timestamp}_{safe_filename}"
    
    # Save file with secure filename
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "original_filename": original_filename,
            "stored_filename": unique_filename,
            "safe_filename": safe_filename,
            "file_size": len(content),
            "file_path": str(file_path)
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="File upload failed"
        )

# API endpoint using secure upload
@app.post("/upload")
async def upload_file(file: UploadFile, current_user: User = Depends(get_current_user)):
    """Upload file endpoint with security."""
    
    # Validate file type (additional security)
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )
    
    # Validate file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large"
        )
    
    return await secure_file_upload(file, current_user.id)
```

### Batch File Processing

**Secure Batch File Handler:**

```python
from pathlib import Path
from typing import List, Dict

async def process_file_batch(filenames: List[str], user_id: str) -> Dict[str, str]:
    """Process multiple filenames with security validation."""
    
    results = {}
    
    for original_filename in filenames:
        try:
            # Check if filename is safe
            if is_safe_filename(original_filename):
                safe_filename = original_filename
                status = "safe"
            else:
                # Sanitize unsafe filename
                safe_filename = sanitize_filename(original_filename)
                status = "sanitized"
            
            # Additional validation
            if not safe_filename or safe_filename == "_":
                status = "invalid"
                safe_filename = "unnamed_file"
            
            results[original_filename] = {
                "safe_filename": safe_filename,
                "status": status,
                "processed": True
            }
            
            logger.info(f"Processed filename: {original_filename} -> {safe_filename}", extra={
                "user_id": user_id,
                "status": status
            })
            
        except Exception as e:
            logger.error(f"Failed to process filename {original_filename}: {e}")
            results[original_filename] = {
                "safe_filename": "error_file",
                "status": "error",
                "processed": False,
                "error": str(e)
            }
    
    return results

# Service layer usage
class FileService:
    """File service with secure filename handling."""
    
    async def create_user_files(self, user_id: str, file_data: List[dict]) -> List[dict]:
        """Create multiple files for user with secure naming."""
        
        created_files = []
        
        for file_info in file_data:
            original_name = file_info.get('filename', 'unnamed_file')
            
            # Sanitize filename
            safe_name = sanitize_filename(original_name)
            
            # Create unique filename
            unique_name = f"{user_id}_{int(time.time())}_{safe_name}"
            
            # Store file metadata
            file_record = {
                "original_filename": original_name,
                "stored_filename": unique_name,
                "safe_filename": safe_name,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "file_size": file_info.get('size', 0)
            }
            
            created_files.append(file_record)
        
        return created_files
```

### Configuration File Handling

**Secure Configuration Loading:**

```python
import json
from pathlib import Path

class SecureConfigLoader:
    """Load configuration files with filename validation."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
    
    def load_config(self, config_name: str) -> dict:
        """Load configuration file with filename validation."""
        
        # Validate filename safety
        if not is_safe_filename(config_name):
            raise ValueError(f"Unsafe config filename: {config_name}")
        
        # Ensure .json extension
        if not config_name.endswith('.json'):
            config_name += '.json'
        
        config_path = self.config_dir / config_name
        
        # Validate path is within config directory
        try:
            config_path.resolve().relative_to(self.config_dir.resolve())
        except ValueError:
            raise ValueError(f"Config file path outside allowed directory: {config_name}")
        
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_name}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_name}: {e}")
    
    def list_available_configs(self) -> List[str]:
        """List available configuration files."""
        
        configs = []
        
        for config_file in self.config_dir.glob('*.json'):
            filename = config_file.name
            
            # Only include files with safe names
            if is_safe_filename(filename):
                configs.append(filename)
            else:
                logger.warning(f"Skipping unsafe config filename: {filename}")
        
        return sorted(configs)

# Usage in application
config_loader = SecureConfigLoader(Path('config'))

def load_app_config(config_name: str) -> dict:
    """Load application configuration securely."""
    
    try:
        return config_loader.load_config(config_name)
    except Exception as e:
        logger.error(f"Failed to load config {config_name}: {e}")
        raise
```

### File Download Security

**Secure File Download Handler:**

```python
from fastapi import HTTPException
from fastapi.responses import FileResponse

async def secure_file_download(requested_filename: str, user_id: str) -> FileResponse:
    """Secure file download with validation."""
    
    # Validate requested filename
    if not is_safe_filename(requested_filename):
        logger.warning(f"Unsafe download request: {requested_filename}", extra={
            "user_id": user_id,
            "requested_filename": requested_filename
        })
        raise HTTPException(
            status_code=400,
            detail="Invalid filename requested"
        )
    
    # Find file in user's directory
    user_upload_dir = UPLOAD_DIR / user_id
    file_path = user_upload_dir / requested_filename
    
    # Validate path is within user directory
    try:
        file_path.resolve().relative_to(user_upload_dir.resolve())
    except ValueError:
        logger.warning(f"Path traversal attempt: {requested_filename}", extra={
            "user_id": user_id
        })
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Check file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    # Return secure file response
    return FileResponse(
        path=file_path,
        filename=requested_filename,
        media_type='application/octet-stream'
    )

# API endpoint for file download
@app.get("/download/{filename}")
async def download_file(filename: str, current_user: User = Depends(get_current_user)):
    """Download file endpoint with security validation."""
    
    return await secure_file_download(filename, current_user.id)
```

## Security Considerations

### Path Traversal Prevention

**Attack Vectors Blocked:**
- `../../../etc/passwd` → `etc_passwd`
- `..\\..\\windows\\system32\\config` → `windows_system32_config`
- `/root/.ssh/id_rsa` → `root_.ssh_id_rsa`
- `file/../../../secret.txt` → `file_secret.txt`

**Implementation Strategy:**
```python
# Multi-layer protection approach
def secure_filename_processing(filename: str) -> str:
    """Multi-layer filename security processing."""
    
    # 1. Initial validation
    if not filename or not isinstance(filename, str):
        return "unnamed_file"
    
    # 2. Length validation
    if len(filename) > MAX_FILENAME_LENGTH:
        filename = filename[:MAX_FILENAME_LENGTH]
    
    # 3. Sanitization
    safe_filename = sanitize_filename(filename)
    
    # 4. Final validation
    if not is_safe_filename(safe_filename):
        logger.error(f"Sanitization failed for: {filename}")
        return "sanitized_file"
    
    return safe_filename
```

### Character Encoding Safety

**Unicode and Special Character Handling:**

```python
import unicodedata

def normalize_filename(filename: str) -> str:
    """Normalize filename for consistent handling."""
    
    # Normalize unicode characters
    normalized = unicodedata.normalize('NFKD', filename)
    
    # Remove non-ASCII characters
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    
    # Apply standard sanitization
    return sanitize_filename(ascii_only)

# Enhanced sanitization with encoding
def enhanced_sanitize_filename(filename: str) -> str:
    """Enhanced filename sanitization with encoding normalization."""
    
    if not filename:
        return "unnamed_file"
    
    # Normalize encoding
    normalized = normalize_filename(filename)
    
    # Standard sanitization
    sanitized = sanitize_filename(normalized)
    
    # Additional safety checks
    if not sanitized or sanitized in ['_', '.', '..']:
        return "safe_file"
    
    return sanitized
```

## Performance Optimization

### Regex Compilation

**Pre-compiled Pattern Usage:**

```python
import re
from typing import Pattern

# Pre-compile regex patterns for performance
_COMPILED_INVALID_CHARS: Pattern[str] = re.compile(_INVALID_CHARS_PATTERN)
_COMPILED_PATH_SPLIT: Pattern[str] = re.compile(r'[\\/]+')

def optimized_sanitize_filename(filename: Filename) -> SanitizedFilename:
    """Optimized version using pre-compiled regex."""
    
    if not filename:
        return "unnamed_file"
    
    # Use pre-compiled patterns
    parts = [
        p for p in _COMPILED_PATH_SPLIT.split(filename)
        if p and p not in _DANGEROUS_COMPONENTS
    ]
    
    if not parts:
        return "_"
    
    safe_name = "_".join(parts)
    safe_name = _COMPILED_INVALID_CHARS.sub("_", safe_name)
    safe_name = safe_name.replace("..", "_")
    
    return safe_name
```

### Caching Strategy

**Filename Validation Caching:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_is_safe_filename(filename: str) -> bool:
    """Cached filename validation for repeated checks."""
    return is_safe_filename(filename)

@lru_cache(maxsize=1000)
def cached_sanitize_filename(filename: str) -> str:
    """Cached filename sanitization for repeated filenames."""
    return sanitize_filename(filename)

# Usage in high-frequency scenarios
def process_many_filenames(filenames: List[str]) -> List[str]:
    """Process many filenames with caching."""
    
    return [
        cached_sanitize_filename(filename)
        for filename in filenames
    ]
```

## Testing Strategies

### Security Testing

**Comprehensive Security Test Suite:**

```python
import pytest
from src.utils.file import sanitize_filename, is_safe_filename

class TestFilenameSecurity:
    """Test suite for filename security validation."""
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        
        dangerous_filenames = [
            "../etc/passwd",
            "..\\windows\\system32\\config",
            "../../secret.txt",
            "/root/.ssh/id_rsa",
            "file/../../../escape.txt"
        ]
        
        for dangerous in dangerous_filenames:
            sanitized = sanitize_filename(dangerous)
            
            # Should not contain path separators
            assert "/" not in sanitized
            assert "\\" not in sanitized
            assert ".." not in sanitized
            
            # Should be marked as unsafe
            assert not is_safe_filename(dangerous)
    
    def test_character_filtering(self):
        """Test filtering of dangerous characters."""
        
        dangerous_chars = ['\\', '/', '*', '?', ':', '"', '<', '>', '|']
        
        for char in dangerous_chars:
            filename = f"file{char}name.txt"
            sanitized = sanitize_filename(filename)
            
            # Should replace dangerous character with underscore
            assert char not in sanitized
            assert "_" in sanitized
            
            # Should be marked as unsafe
            assert not is_safe_filename(filename)
    
    def test_empty_and_edge_cases(self):
        """Test edge cases and empty inputs."""
        
        edge_cases = ["", None, ".", "..", "...", " ", "\t", "\n"]
        
        for case in edge_cases:
            if case is None:
                continue
                
            sanitized = sanitize_filename(case)
            
            # Should handle gracefully
            assert sanitized is not None
            assert len(sanitized) > 0
            
            # Empty/whitespace should be unsafe
            if not case or case.isspace():
                assert not is_safe_filename(case)
    
    def test_safe_filenames(self):
        """Test that safe filenames pass validation."""
        
        safe_filenames = [
            "document.txt",
            "image.jpg",
            "data_file.csv",
            "report-2023.pdf",
            "my_file_name.docx"
        ]
        
        for safe in safe_filenames:
            # Should pass safety check
            assert is_safe_filename(safe)
            
            # Should remain unchanged after sanitization
            assert sanitize_filename(safe) == safe
    
    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        
        unicode_filenames = [
            "файл.txt",        # Cyrillic
            "文件.doc",         # Chinese
            "αρχείο.pdf",      # Greek
            "🎉party.jpg"      # Emoji
        ]
        
        for unicode_name in unicode_filenames:
            sanitized = sanitize_filename(unicode_name)
            
            # Should handle gracefully
            assert sanitized is not None
            assert len(sanitized) > 0
```

### Performance Testing

**Performance Benchmark Tests:**

```python
import time
import pytest
from src.utils.file import sanitize_filename, is_safe_filename

class TestFilenamePerformance:
    """Performance tests for filename utilities."""
    
    def test_sanitization_performance(self):
        """Test sanitization performance with many filenames."""
        
        filenames = [
            f"test_file_{i}.txt" for i in range(1000)
        ] + [
            f"../dangerous/file_{i}.txt" for i in range(100)
        ]
        
        start_time = time.time()
        
        for filename in filenames:
            sanitize_filename(filename)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 1100 filenames in under 1 second
        assert processing_time < 1.0
        
        # Calculate throughput
        throughput = len(filenames) / processing_time
        assert throughput > 1000  # More than 1000 filenames per second
    
    def test_validation_performance(self):
        """Test validation performance."""
        
        safe_filenames = [f"safe_file_{i}.txt" for i in range(500)]
        unsafe_filenames = [f"../unsafe_{i}.txt" for i in range(500)]
        
        start_time = time.time()
        
        for filename in safe_filenames + unsafe_filenames:
            is_safe_filename(filename)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should validate 1000 filenames quickly
        assert processing_time < 0.5
```

## Best Practices

### Filename Security

- **Always Sanitize**: Sanitize all user-provided filenames before use
- **Validate First**: Check filename safety before processing when possible
- **Log Suspicious Activity**: Log attempts to use dangerous filenames
- **Use Unique Names**: Generate unique filenames to prevent conflicts and attacks

### Error Handling

- **Graceful Degradation**: Provide default filenames for invalid inputs
- **Clear Logging**: Log sanitization actions for security monitoring
- **User Feedback**: Inform users when filenames are modified
- **Audit Trail**: Maintain records of filename changes for compliance

### Integration Guidelines

- **Consistent Usage**: Use utilities consistently across all file operations
- **Layer Integration**: Apply validation at multiple application layers
- **Configuration**: Make sanitization behavior configurable for different contexts
- **Testing**: Thoroughly test all filename handling code paths

## Related Files

### Dependencies

- `re` - Regular expression operations for pattern matching
- `typing.Final` - Immutable constant declarations
- `typing.Literal` - Exact string literal type definitions
- `typing_extensions.TypedDict` - Structured return type definitions

### Integration Points

- `src.api.v1.uploads` - File upload endpoint security
- `src.services.file` - File service layer operations
- `src.repositories.file` - File repository operations
- `src.core.security` - Application-wide security validation

### Related Security Modules

- Input validation utilities for additional security checks
- Authentication middleware for file access control
- Rate limiting for file operation security

## Configuration

### File Security Settings

```python
# File handling configuration
FILE_CONFIG = {
    "max_filename_length": 255,        # Maximum filename length
    "allow_unicode": False,            # Allow unicode characters
    "sanitization_mode": "strict",    # Sanitization strictness level
    "log_sanitization": True,         # Log filename sanitization
    "cache_validation": True,          # Cache validation results
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    '.txt', '.pdf', '.doc', '.docx', 
    '.jpg', '.jpeg', '.png', '.gif',
    '.csv', '.xlsx', '.json'
}

# Dangerous filename patterns
DANGEROUS_PATTERNS = [
    r'^\.',           # Hidden files
    r'.*\.exe$',      # Executable files
    r'.*\.bat$',      # Batch files
    r'.*\.sh$',       # Shell scripts
]
```

This file utilities module provides comprehensive filename security for the ReViewPoint application, ensuring safe file operations while maintaining usability and performance across all file handling scenarios.
