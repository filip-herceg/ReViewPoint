# Type-Safe Upload API Client

**File:** `frontend/src/lib/api/clients/uploads.ts`  
**Purpose:** OpenAPI-generated type-safe upload client with error handling integration  
**Lines of Code:** 335  
**Type:** Type-Safe API Client Layer  

## Overview

The type-safe upload API client provides a fully type-safe interface to the ReViewPoint upload API using OpenAPI-generated types. It serves as a critical bridge between the raw HTTP layer and the application, ensuring compile-time type safety, runtime validation, and consistent error handling across all upload operations.

## Architecture

### Core Dependencies

```typescript
import { handleApiError } from "@/lib/api/errorHandling";
import logger from "@/logger";
import { generatedApiClient } from "../generated/client";
import type { components, paths } from "../generated/schema";
```

### Type System Integration

```typescript
// Extract types from generated OpenAPI schema
type UploadFileResponse = components["schemas"]["FileUploadResponse"];
type FileListResponse = components["schemas"]["FileListResponse"];
type FileDict = components["schemas"]["FileDict"];
type HTTPValidationError = components["schemas"]["HTTPValidationError"];

// API operation types for compile-time safety
type UploadFileOperation = paths["/api/v1/uploads"]["post"];
type ListFilesOperation = paths["/api/v1/uploads"]["get"];
type GetFileOperation = paths["/api/v1/uploads/{filename}"]["get"];
type DeleteFileOperation = paths["/api/v1/uploads/{filename}"]["delete"];
```

## Key Features

### 🛡️ **Compile-Time Type Safety**

- **OpenAPI Integration**: Types generated directly from API schema
- **Path Parameter Validation**: Compile-time checks for URL parameters
- **Request/Response Typing**: Fully typed request payloads and responses
- **Query Parameter Safety**: Type-safe query parameter handling

### 🔄 **Hybrid HTTP Approach**

- **Generated Client**: Uses `openapi-fetch` for standard operations
- **Direct Fetch**: Falls back to native fetch for file uploads and downloads
- **Multipart Handling**: Proper multipart/form-data support for file uploads
- **Stream Support**: Efficient handling of binary file data

### 📊 **Comprehensive Logging**

- **Operation Tracking**: Detailed logs for all API operations
- **Error Context**: Rich error information with operation context
- **Performance Metrics**: File size and operation timing data
- **Debug Support**: Structured logging for development and debugging

## API Operations

### 📤 **uploadFile(file: File)** - File Upload

Uploads a single file to the server with comprehensive error handling and logging.

```typescript
async uploadFile(file: File): Promise<UploadFileResponse>
```

**Features:**
- **Multipart Support**: Proper multipart/form-data handling
- **Progress Compatible**: Ready for progress tracking integration
- **Error Recovery**: Detailed error messages for upload failures
- **Validation**: Response format validation before return

**Implementation Details:**
```typescript
// Uses direct fetch for multipart handling
const formData = new FormData();
formData.append("file", file);

// Proper multipart handling without Content-Type header
const response = await fetch(`${baseUrl}/api/v1/uploads`, {
    method: "POST",
    body: formData,
    // Browser sets Content-Type with boundary automatically
});
```

**Usage Example:**
```typescript
try {
    const result = await uploadApiClient.uploadFile(selectedFile);
    console.log('Upload successful:', result.filename, result.url);
    toast.success(`File "${result.filename}" uploaded successfully`);
} catch (error) {
    console.error('Upload failed:', error.message);
    toast.error('Upload failed. Please try again.');
}
```

### 📋 **listFiles(params?)** - File Listing

Retrieves paginated file listings with advanced query parameters and filtering.

```typescript
async listFiles(params?: {
    limit?: number;
    offset?: number;
    q?: string;
    sort?: "created_at" | "filename";
    order?: "asc" | "desc";
    fields?: string;
    created_after?: string;
    created_before?: string;
}): Promise<FileListResponse>
```

**Features:**
- **Pagination Support**: Limit/offset pagination for large file sets
- **Search Functionality**: Full-text search across filenames
- **Sorting Options**: Sort by creation date or filename
- **Date Filtering**: Filter files by creation date range
- **Field Selection**: Optimize response size with field selection

**Usage Example:**
```typescript
// Basic file listing
const files = await uploadApiClient.listFiles();

// Advanced filtering
const recentFiles = await uploadApiClient.listFiles({
    limit: 50,
    sort: "created_at",
    order: "desc",
    created_after: "2024-01-01T00:00:00Z",
    q: "report"
});
```

### 📄 **getFileInfo(filename)** - File Metadata

Retrieves detailed metadata for a specific file by filename.

```typescript
async getFileInfo(filename: string): Promise<UploadFileResponse>
```

**Features:**
- **Metadata Retrieval**: Get file URL, size, and creation date
- **Error Handling**: Proper 404 handling for missing files
- **Type Safety**: Fully typed response with validation
- **Logging Integration**: Detailed operation logging

**Usage Example:**
```typescript
try {
    const fileInfo = await uploadApiClient.getFileInfo('document.pdf');
    console.log('File URL:', fileInfo.url);
    console.log('File metadata:', fileInfo);
} catch (error) {
    if (error.message.includes('404')) {
        console.log('File not found');
    } else {
        console.error('Failed to get file info:', error.message);
    }
}
```

### 📥 **downloadFile(filename)** - File Download

Downloads file content as a Blob for client-side processing or saving.

```typescript
async downloadFile(filename: string): Promise<Blob>
```

**Features:**
- **Binary Content**: Returns file as Blob for flexible handling
- **Stream Efficient**: Memory-efficient streaming for large files
- **Error Recovery**: Comprehensive error handling for download failures
- **MIME Type Preservation**: Maintains original file MIME type

**Usage Example:**
```typescript
const downloadAndSave = async (filename: string) => {
    try {
        const blob = await uploadApiClient.downloadFile(filename);
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Download failed:', error.message);
    }
};
```

### 🗑️ **deleteFile(filename)** - File Deletion

Deletes a single file by filename with confirmation and error handling.

```typescript
async deleteFile(filename: string): Promise<void>
```

**Features:**
- **Safe Deletion**: No return value on success (void)
- **Error Propagation**: Clear error messages for deletion failures
- **Logging Integration**: Comprehensive operation logging
- **404 Handling**: Graceful handling of already-deleted files

**Usage Example:**
```typescript
const deleteWithConfirmation = async (filename: string) => {
    const confirmed = window.confirm(`Delete "${filename}"?`);
    if (!confirmed) return;
    
    try {
        await uploadApiClient.deleteFile(filename);
        toast.success('File deleted successfully');
    } catch (error) {
        console.error('Deletion failed:', error.message);
        toast.error('Failed to delete file');
    }
};
```

### 🗑️ **bulkDeleteFiles(filenames)** - Bulk Deletion

Deletes multiple files in a single operation with detailed results.

```typescript
async bulkDeleteFiles(filenames: string[]): Promise<{
    deleted: string[];
    failed: string[];
}>
```

**Features:**
- **Batch Processing**: Efficient bulk deletion in single request
- **Partial Success**: Returns both successful and failed deletions
- **Error Resilience**: Continues processing even if some deletions fail
- **Detailed Results**: Clear reporting of operation outcomes

**Usage Example:**
```typescript
const bulkDelete = async (selectedFiles: string[]) => {
    try {
        const result = await uploadApiClient.bulkDeleteFiles(selectedFiles);
        
        if (result.deleted.length > 0) {
            toast.success(`${result.deleted.length} files deleted`);
        }
        
        if (result.failed.length > 0) {
            toast.error(`${result.failed.length} files failed to delete`);
            console.error('Failed deletions:', result.failed);
        }
    } catch (error) {
        console.error('Bulk delete error:', error.message);
    }
};
```

## Type Guards and Validation

### Response Type Guards

```typescript
export function isUploadResponse(data: unknown): data is UploadFileResponse {
    return (
        typeof data === "object" &&
        data !== null &&
        "filename" in data &&
        "url" in data &&
        typeof (data as Record<string, unknown>).filename === "string" &&
        typeof (data as Record<string, unknown>).url === "string"
    );
}

export function isFileListResponse(data: unknown): data is FileListResponse {
    return (
        typeof data === "object" &&
        data !== null &&
        "files" in data &&
        "total" in data &&
        Array.isArray((data as Record<string, unknown>).files) &&
        typeof (data as Record<string, unknown>).total === "number"
    );
}

export function isValidationError(data: unknown): data is HTTPValidationError {
    return (
        typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        Array.isArray((data as Record<string, unknown>).detail)
    );
}
```

### Runtime Validation Usage

```typescript
const handleApiResponse = (response: unknown) => {
    if (isUploadResponse(response)) {
        // TypeScript knows this is UploadFileResponse
        console.log('File uploaded:', response.filename, response.url);
    } else if (isValidationError(response)) {
        // TypeScript knows this is HTTPValidationError
        console.error('Validation errors:', response.detail);
    } else {
        console.error('Unexpected response format');
    }
};
```

## Error Handling Integration

### Centralized Error Processing

```typescript
// Integrates with global error handling system
const { data, error } = await generatedApiClient.GET("/api/v1/uploads");

if (error) {
    const handledError = handleApiError(error);
    throw new Error(handledError.message);
}
```

### Error Categories

- **Network Errors**: Connection timeouts, DNS failures
- **4xx Client Errors**: File not found, validation errors, authentication
- **5xx Server Errors**: Internal server errors, service unavailable
- **Validation Errors**: File size limits, unsupported formats

### Error Context Enhancement

```typescript
// Enhanced error messages with operation context
logger.error("❌ Upload failed:", {
    status: response.status,
    error: errorText,
    filename: file.name,
    fileSize: file.size
});
```

## Logging Strategy

### Structured Logging

```typescript
// Operation start
logger.info("🔼 Uploading file:", {
    name: file.name,
    size: file.size,
    type: file.type,
});

// Operation success
logger.info("✅ Upload completed successfully:", {
    filename: data.filename,
    url: data.url,
    duration: Date.now() - startTime
});

// Operation error
logger.error("❌ Upload error:", {
    error: error.message,
    filename: file.name,
    operation: 'uploadFile'
});
```

### Log Categories

- **🔼 Upload Operations**: File upload tracking
- **📋 List Operations**: File listing and search
- **📥 Download Operations**: File download tracking
- **🗑️ Delete Operations**: File deletion tracking
- **❌ Error Operations**: Error logging with context

## Performance Considerations

### ⚡ **Optimization Features**

- **Direct Fetch for Uploads**: Bypasses unnecessary layers for file uploads
- **Generated Client for Queries**: Leverages optimized generated code
- **Streaming Downloads**: Memory-efficient file downloads
- **Batch Operations**: Efficient bulk operations

### 📊 **Memory Management**

```typescript
// Efficient blob handling
const blob = await response.blob();

// Proper cleanup after file operations
URL.revokeObjectURL(objectUrl);
```

### 🔄 **Request Optimization**

- **Query Parameter Optimization**: Only send required parameters
- **Header Management**: Automatic auth header injection
- **Response Validation**: Early validation to prevent downstream errors

## Development Workflow

### Type Safety Benefits

```typescript
// Compile-time path safety
const result = await uploadApiClient.listFiles({
    sort: "created_at",  // ✅ Valid sort option
    order: "asc",        // ✅ Valid order option
    // sort: "invalid"   // ❌ Compile error - invalid sort option
});

// Response type safety
result.files.forEach(file => {
    console.log(file.filename);  // ✅ Type-safe property access
    // console.log(file.invalid); // ❌ Compile error - property doesn't exist
});
```

### Testing Integration

```typescript
// Mock responses with proper types
const mockUploadResponse: UploadFileResponse = {
    filename: 'test.pdf',
    url: '/uploads/test.pdf',
    size: 1024,
    created_at: '2024-01-15T10:30:00Z'
};

// Type-safe test assertions
expect(isUploadResponse(mockUploadResponse)).toBe(true);
expect(mockUploadResponse.filename).toBe('test.pdf');
```

## Integration Examples

### React Component Integration

```typescript
const FileUploadComponent = () => {
    const [isUploading, setIsUploading] = useState(false);
    
    const handleUpload = async (file: File) => {
        setIsUploading(true);
        try {
            const result = await uploadApiClient.uploadFile(file);
            // result is fully typed as UploadFileResponse
            setUploadedFiles(prev => [...prev, result]);
            toast.success(`"${result.filename}" uploaded successfully`);
        } catch (error) {
            toast.error('Upload failed: ' + error.message);
        } finally {
            setIsUploading(false);
        }
    };
    
    return (
        <FileDropzone 
            onDrop={handleUpload}
            disabled={isUploading}
        />
    );
};
```

### Async Operations

```typescript
const FileManager = () => {
    const [files, setFiles] = useState<UploadFileResponse[]>([]);
    
    useEffect(() => {
        const loadFiles = async () => {
            try {
                const response = await uploadApiClient.listFiles();
                setFiles(response.files);
            } catch (error) {
                console.error('Failed to load files:', error);
            }
        };
        
        loadFiles();
    }, []);
    
    return <FileGrid files={files} />;
};
```

## Migration Guide

### From Legacy Upload API

```typescript
// Before: Untyped API calls
const uploadFile = async (file) => {
    const response = await fetch('/api/uploads', {
        method: 'POST',
        body: formData
    });
    const data = await response.json(); // No type safety
    return data;
};

// After: Type-safe API client
const uploadFile = async (file: File): Promise<UploadFileResponse> => {
    return await uploadApiClient.uploadFile(file);
    // Fully typed response, compile-time safety
};
```

### Type Migration

```typescript
// Before: Manual type definitions
interface OldUploadResponse {
    filename?: string;
    url?: string;
}

// After: Generated types from OpenAPI
import type { UploadFileResponse } from './clients/uploads';
// Types are automatically kept in sync with backend
```

## Best Practices

### ✅ **Do's**

- **Use Type Guards**: Validate responses with provided type guards
- **Handle All Error Cases**: Check for network, client, and server errors
- **Log Operations**: Use structured logging for all operations
- **Leverage TypeScript**: Take advantage of compile-time type safety
- **Validate Inputs**: Check file sizes and types before upload

### ❌ **Don'ts**

- **Don't Bypass Type Safety**: Avoid using `any` or type assertions
- **Don't Ignore Errors**: Always handle potential error scenarios
- **Don't Skip Validation**: Use type guards for runtime safety
- **Don't Mix HTTP Clients**: Use this client consistently for uploads
- **Don't Hardcode URLs**: Use environment variables for API endpoints

## Related Documentation

- **Generated API Client**: `generated/client.ts` - OpenAPI generated client
- **OpenAPI Schema**: `generated/schema.ts` - Type definitions
- **Error Handling**: `errorHandling.ts.md` - Error processing integration
- **Upload API**: `uploads.ts.md` - Higher-level upload operations
- **Upload Queries**: `upload.queries.ts.md` - React Query integration

## Dependencies

- **@/lib/api/errorHandling**: Centralized error processing
- **@/logger**: Structured logging system
- **generated/client**: OpenAPI-generated HTTP client
- **generated/schema**: OpenAPI-generated type definitions

---

*This module provides the type-safe foundation for all upload operations in the ReViewPoint application, ensuring compile-time safety, runtime validation, and consistent error handling across the entire upload ecosystem.*
