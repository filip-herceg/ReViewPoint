# uploads.ts - File Upload API Module

## Purpose

The `uploads.ts` file provides comprehensive file upload and management functionality for the ReViewPoint application. This module serves as the primary interface for all file operations including upload, download, listing, deletion, and export capabilities. It mirrors the backend upload endpoints while providing a consistent TypeScript interface with robust error handling, logging, and security features.

## Key Features

### Core File Operations

- **File Upload**: Secure file upload with validation and progress tracking
- **File Listing**: Paginated file listing with advanced search and filtering
- **File Retrieval**: Get specific files by filename or ID
- **File Deletion**: Safe file deletion with confirmation and logging
- **File Export**: Export file lists as CSV with customizable fields

### Advanced Capabilities

- **Search and Filtering**: Advanced search with multiple criteria and sorting
- **Pagination Support**: Efficient handling of large file collections
- **Security Validation**: File type and size validation before upload
- **Progress Tracking**: Real-time upload progress monitoring
- **Test Endpoints**: Comprehensive testing and debugging utilities

## API Functions

### File Upload Operations

#### Primary Upload (`uploadFile`)

Uploads a single file to the server with validation and progress tracking.

```typescript
async function uploadFile(file: File): Promise<FileUploadResponse>
```

**Parameters:**

- `file: File` - The file object to upload

**Returns:**

- `Promise<FileUploadResponse>` - Upload result with filename and URL

**Example Usage:**

```typescript
import { uploadsApi } from '@/lib/api';

async function handleFileUpload(file: File) {
  try {
    // Validate file before upload
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      throw new Error('File size exceeds 10MB limit');
    }

    const allowedTypes = ['application/pdf', 'text/plain', 'image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('File type not supported');
    }

    const response = await uploadsApi.uploadFile(file);
    
    console.log('File uploaded successfully:');
    console.log('- Filename:', response.filename);
    console.log('- URL:', response.url);
    
    return response;
  } catch (error) {
    if (error.message.includes('413')) {
      console.error('File too large. Please choose a smaller file.');
    } else if (error.message.includes('415')) {
      console.error('File type not supported. Please upload a PDF, text, or image file.');
    } else if (error.message.includes('403')) {
      console.error('Upload permission denied. Please check your account status.');
    } else {
      console.error('Upload failed:', error.message);
    }
    throw error;
  }
}

// Example with drag-and-drop
function setupDragAndDrop() {
  const dropZone = document.getElementById('drop-zone');
  
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });

  dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    
    for (const file of files) {
      try {
        await handleFileUpload(file);
        console.log(`${file.name} uploaded successfully`);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error.message);
      }
    }
  });
}
```

#### Advanced Upload (`createUpload`)

Creates a new upload with enhanced tracking and status management.

```typescript
async function createUpload(file: File): Promise<{
  id: string;
  name: string;
  status: string;
  progress: number;
  createdAt: string;
}>
```

**Example Usage:**

```typescript
async function advancedFileUpload(file: File) {
  try {
    const upload = await uploadsApi.createUpload(file);
    
    console.log('Upload created:', {
      id: upload.id,
      name: upload.name,
      status: upload.status,
      progress: upload.progress,
      created: upload.createdAt
    });
    
    return upload;
  } catch (error) {
    console.error('Advanced upload failed:', error.message);
    throw error;
  }
}
```

### File Listing and Search

#### List Files (`listFiles`)

Retrieves a paginated list of uploaded files with advanced filtering options.

```typescript
async function listFiles(params?: FileListParams): Promise<FileListResponse>
```

**Parameters:**

- `params?: FileListParams` - Optional search and pagination parameters

**Returns:**

- `Promise<FileListResponse>` - Object containing files array and total count

**Example Usage:**

```typescript
async function searchFiles() {
  try {
    // Basic file listing
    const allFiles = await uploadsApi.listFiles();
    
    // Advanced search with filtering
    const searchResults = await uploadsApi.listFiles({
      q: 'research paper',        // Search query
      limit: 20,                  // Results per page
      offset: 0,                  // Skip count for pagination
      sort: 'created_at',         // Sort by creation date
      order: 'desc',              // Newest first
      created_after: '2024-01-01T00:00:00Z',  // Filter by date
      fields: 'filename,url,createdAt'         // Specific fields only
    });

    console.log(`Found ${searchResults.files.length} files`);
    console.log(`Total matching files: ${searchResults.total}`);
    
    // Process results
    searchResults.files.forEach(file => {
      console.log(`- ${file.filename} (${file.url})`);
    });
    
    return searchResults;
  } catch (error) {
    console.error('File search failed:', error.message);
    throw error;
  }
}

// Paginated file browser
async function buildPaginatedFileBrowser(pageSize: number = 10) {
  let currentPage = 0;
  let hasMore = true;

  const loadPage = async (page: number) => {
    try {
      const response = await uploadsApi.listFiles({
        limit: pageSize,
        offset: page * pageSize,
        sort: 'created_at',
        order: 'desc'
      });

      hasMore = (page + 1) * pageSize < response.total;
      
      return {
        files: response.files,
        currentPage: page,
        totalPages: Math.ceil(response.total / pageSize),
        hasNext: hasMore,
        hasPrev: page > 0,
        total: response.total
      };
    } catch (error) {
      console.error('Failed to load page:', error.message);
      throw error;
    }
  };

  return { loadPage };
}
```

### File Retrieval Operations

#### Get File (`getFile`)

Retrieves specific file information by filename.

```typescript
async function getFile(filename: string): Promise<FileUploadResponse>
```

**Example Usage:**

```typescript
async function getFileDetails(filename: string) {
  try {
    const file = await uploadsApi.getFile(filename);
    
    console.log('File details:', {
      filename: file.filename,
      url: file.url,
      downloadUrl: `${window.location.origin}${file.url}`
    });
    
    return file;
  } catch (error) {
    if (error.message.includes('404')) {
      console.error('File not found:', filename);
    } else if (error.message.includes('403')) {
      console.error('Access denied to file:', filename);
    } else {
      console.error('Failed to get file:', error.message);
    }
    throw error;
  }
}

// Download file helper
async function downloadFile(filename: string) {
  try {
    const file = await uploadsApi.getFile(filename);
    
    // Create download link
    const link = document.createElement('a');
    link.href = file.url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('Download initiated for:', filename);
  } catch (error) {
    console.error('Download failed:', error.message);
    throw error;
  }
}
```

### File Management Operations

#### Delete File (`deleteFile`)

Permanently removes a file from the server.

```typescript
async function deleteFile(filename: string): Promise<null>
```

**Example Usage:**

```typescript
async function safeDeleteFile(filename: string, confirmCallback?: () => boolean) {
  try {
    // Optional confirmation
    if (confirmCallback && !confirmCallback()) {
      console.log('File deletion cancelled by user');
      return;
    }

    await uploadsApi.deleteFile(filename);
    console.log('File deleted successfully:', filename);
    
    // Optionally refresh file list after deletion
    // await refreshFileList();
    
  } catch (error) {
    if (error.message.includes('404')) {
      console.error('File not found for deletion:', filename);
    } else if (error.message.includes('403')) {
      console.error('Permission denied for file deletion:', filename);
    } else if (error.message.includes('409')) {
      console.error('File is in use and cannot be deleted:', filename);
    } else {
      console.error('File deletion failed:', error.message);
    }
    throw error;
  }
}

// Batch delete with confirmation
async function batchDeleteFiles(filenames: string[]) {
  const results = {
    successful: [] as string[],
    failed: [] as { filename: string; error: string }[]
  };

  const confirmDelete = () => {
    return window.confirm(
      `Are you sure you want to delete ${filenames.length} files? This action cannot be undone.`
    );
  };

  if (!confirmDelete()) {
    return results;
  }

  for (const filename of filenames) {
    try {
      await uploadsApi.deleteFile(filename);
      results.successful.push(filename);
      console.log(`Deleted: ${filename}`);
    } catch (error) {
      results.failed.push({ filename, error: error.message });
      console.error(`Failed to delete ${filename}:`, error.message);
    }
  }

  console.log(`Batch delete completed: ${results.successful.length} successful, ${results.failed.length} failed`);
  return results;
}
```

#### Advanced File Updates (`patchFile`)

Updates file metadata and properties.

```typescript
async function patchFile(id: string, updates: Record<string, unknown>): Promise<void>
```

**Example Usage:**

```typescript
async function updateFileMetadata(fileId: string, metadata: Record<string, unknown>) {
  try {
    await uploadsApi.patchFile(fileId, metadata);
    console.log('File metadata updated:', fileId);
  } catch (error) {
    console.error('Failed to update file metadata:', error.message);
    throw error;
  }
}

// Example metadata updates
const metadataUpdates = {
  description: 'Research paper on AI applications',
  tags: ['research', 'ai', 'machine-learning'],
  category: 'academic',
  isPublic: false
};

await updateFileMetadata('file-123', metadataUpdates);
```

### File Export Operations

#### Export Files (`exportFiles`)

Exports file listings as CSV with customizable fields and filtering.

```typescript
async function exportFiles(params?: FileExportParams): Promise<Blob>
```

**Example Usage:**

```typescript
async function exportFileList() {
  try {
    const exportParams = {
      fields: 'filename,created_at,size,url',
      sort: 'created_at',
      order: 'desc',
      created_after: '2024-01-01T00:00:00Z'
    };

    const csvBlob = await uploadsApi.exportFiles(exportParams);
    
    // Download CSV file
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `files-export-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
    
    console.log('File export completed successfully');
  } catch (error) {
    console.error('File export failed:', error.message);
    throw error;
  }
}

// Advanced export with user selection
async function customFileExport() {
  try {
    // Let user choose export parameters
    const exportConfig = {
      fields: prompt('Enter fields to export (comma-separated):', 'filename,created_at,size') || 'filename,created_at',
      sort: 'created_at',
      order: 'desc'
    };

    const csvBlob = await uploadsApi.exportFiles(exportConfig);
    
    // Create custom filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `custom-files-export-${timestamp}.csv`;
    
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Custom export failed:', error.message);
    throw error;
  }
}
```

## Type Definitions

### Core Upload Types

```typescript
interface FileUploadResponse {
  filename: string;        // Name of the uploaded file
  url: string;             // Access URL for the file
}

interface FileDict {
  filename: string;        // File name
  url: string;             // File URL
  status?: string;         // Upload status (pending, completed, failed)
  progress?: number;       // Upload progress percentage (0-100)
  createdAt?: string;      // ISO timestamp of creation
}

interface FileListResponse {
  files: FileDict[];       // Array of file objects
  total: number;           // Total number of files matching criteria
}
```

### Search and Filter Parameters

```typescript
interface FileListParams {
  offset?: number;                    // Number of files to skip (pagination)
  limit?: number;                     // Maximum number of files to return
  q?: string;                         // Search query for filename
  fields?: string;                    // Comma-separated list of fields to return
  sort?: "created_at" | "filename";   // Sort criteria
  order?: "desc" | "asc";             // Sort order
  created_after?: string;             // Filter by creation date (ISO string)
  created_before?: string;            // Filter by creation date (ISO string)
}

interface FileExportParams {
  q?: string;                         // Search query for export filtering
  sort?: "created_at" | "filename";   // Sort criteria for export
  order?: "desc" | "asc";             // Sort order for export
  fields?: string;                    // Fields to include in export
  created_before?: string;            // Date filter for export
  created_after?: string;             // Date filter for export
}
```

## Advanced Usage Examples

### Comprehensive File Manager Class

```typescript
import { uploadsApi } from '@/lib/api';

class FileManager {
  private cache: Map<string, FileDict> = new Map();
  private eventEmitter = new EventTarget();

  // Upload with progress tracking
  async uploadWithProgress(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<FileUploadResponse> {
    try {
      // Validate file
      this.validateFile(file);
      
      // Create upload
      const upload = await uploadsApi.createUpload(file);
      
      // Track progress (if supported by backend)
      if (onProgress) {
        this.trackUploadProgress(upload.id, onProgress);
      }

      // Update cache
      this.cache.set(upload.name, {
        filename: upload.name,
        url: `/uploads/${upload.name}`,
        status: upload.status,
        progress: upload.progress,
        createdAt: upload.createdAt
      });

      this.emitEvent('fileUploaded', { file: upload });
      return { filename: upload.name, url: `/uploads/${upload.name}` };
    } catch (error) {
      this.emitEvent('uploadError', { file: file.name, error: error.message });
      throw error;
    }
  }

  // Smart file search with caching
  async searchFiles(query: string, options: {
    useCache?: boolean;
    maxAge?: number;
  } = {}): Promise<FileListResponse> {
    const cacheKey = `search:${query}:${JSON.stringify(options)}`;
    
    if (options.useCache && this.isCacheValid(cacheKey, options.maxAge)) {
      return this.getCachedResult(cacheKey);
    }

    try {
      const results = await uploadsApi.listFiles({
        q: query,
        sort: 'created_at',
        order: 'desc',
        limit: 50
      });

      this.setCachedResult(cacheKey, results);
      return results;
    } catch (error) {
      console.error('File search failed:', error.message);
      throw error;
    }
  }

  // Bulk operations
  async bulkUpload(files: File[]): Promise<{
    successful: FileUploadResponse[];
    failed: { file: string; error: string }[];
  }> {
    const results = {
      successful: [] as FileUploadResponse[],
      failed: [] as { file: string; error: string }[]
    };

    const uploadPromises = files.map(async (file) => {
      try {
        const result = await this.uploadWithProgress(file);
        results.successful.push(result);
      } catch (error) {
        results.failed.push({ file: file.name, error: error.message });
      }
    });

    await Promise.allSettled(uploadPromises);
    
    this.emitEvent('bulkUploadComplete', results);
    return results;
  }

  // File organization
  async organizeFilesByDate(): Promise<{ [date: string]: FileDict[] }> {
    try {
      const allFiles = await uploadsApi.listFiles({ limit: 1000 });
      const organized: { [date: string]: FileDict[] } = {};

      allFiles.files.forEach(file => {
        if (file.createdAt) {
          const date = file.createdAt.split('T')[0]; // Get date part
          if (!organized[date]) {
            organized[date] = [];
          }
          organized[date].push(file);
        }
      });

      return organized;
    } catch (error) {
      console.error('File organization failed:', error.message);
      throw error;
    }
  }

  // Helper methods
  private validateFile(file: File): void {
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'image/jpeg',
      'image/png',
      'image/gif',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (file.size > maxSize) {
      throw new Error(`File size exceeds ${maxSize / 1024 / 1024}MB limit`);
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type ${file.type} is not supported`);
    }
  }

  private trackUploadProgress(uploadId: string, callback: (progress: number) => void): void {
    // Implementation would depend on backend WebSocket or polling support
    // This is a placeholder for progress tracking functionality
    const interval = setInterval(async () => {
      try {
        // Poll upload status (if supported by backend)
        // const status = await uploadsApi.getUploadStatus(uploadId);
        // callback(status.progress);
        
        // For now, simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
          progress += 10;
          callback(progress);
          if (progress >= 100) {
            clearInterval(progressInterval);
            clearInterval(interval);
          }
        }, 100);
      } catch (error) {
        clearInterval(interval);
        console.error('Progress tracking failed:', error.message);
      }
    }, 1000);
  }

  private emitEvent(eventType: string, data: any): void {
    this.eventEmitter.dispatchEvent(new CustomEvent(eventType, { detail: data }));
  }

  private isCacheValid(key: string, maxAge: number = 300000): boolean {
    // Implementation for cache validation
    return false; // Placeholder
  }

  private getCachedResult(key: string): any {
    // Implementation for cache retrieval
    return null; // Placeholder
  }

  private setCachedResult(key: string, data: any): void {
    // Implementation for cache storage
  }

  // Event listeners
  addEventListener(type: string, listener: EventListener): void {
    this.eventEmitter.addEventListener(type, listener);
  }

  removeEventListener(type: string, listener: EventListener): void {
    this.eventEmitter.removeEventListener(type, listener);
  }
}
```

### React Component Integration

```typescript
import { uploadsApi } from '@/lib/api';
import { useState, useEffect } from 'react';

function FileUploadComponent() {
  const [files, setFiles] = useState<FileDict[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ [filename: string]: number }>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFiles();
  }, [searchQuery]);

  const loadFiles = async () => {
    try {
      const response = await uploadsApi.listFiles({
        q: searchQuery,
        limit: 20,
        sort: 'created_at',
        order: 'desc'
      });
      setFiles(response.files);
    } catch (error) {
      setError('Failed to load files: ' + error.message);
    }
  };

  const handleFileUpload = async (fileList: FileList) => {
    setUploading(true);
    setError(null);

    try {
      const uploadPromises = Array.from(fileList).map(async (file) => {
        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));
        
        try {
          const result = await uploadsApi.uploadFile(file);
          setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
          return result;
        } catch (error) {
          setUploadProgress(prev => ({ ...prev, [file.name]: -1 })); // Error state
          throw error;
        }
      });

      await Promise.allSettled(uploadPromises);
      await loadFiles(); // Refresh file list
      
      // Clear progress after delay
      setTimeout(() => setUploadProgress({}), 3000);
      
    } catch (error) {
      setError('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileDelete = async (filename: string) => {
    if (!window.confirm(`Are you sure you want to delete ${filename}?`)) {
      return;
    }

    try {
      await uploadsApi.deleteFile(filename);
      await loadFiles(); // Refresh file list
    } catch (error) {
      setError('Delete failed: ' + error.message);
    }
  };

  const handleExport = async () => {
    try {
      const csvBlob = await uploadsApi.exportFiles({
        q: searchQuery,
        fields: 'filename,created_at,url'
      });
      
      const url = URL.createObjectURL(csvBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'files-export.csv';
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setError('Export failed: ' + error.message);
    }
  };

  return (
    <div className="file-upload-component">
      <div className="upload-area">
        <input
          type="file"
          multiple
          onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
          disabled={uploading}
        />
        
        <div className="search-area">
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button onClick={handleExport}>Export CSV</button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {Object.keys(uploadProgress).length > 0 && (
        <div className="upload-progress">
          {Object.entries(uploadProgress).map(([filename, progress]) => (
            <div key={filename} className="progress-item">
              <span>{filename}</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${Math.max(0, progress)}%`,
                    backgroundColor: progress === -1 ? 'red' : 'green'
                  }}
                />
              </div>
              <span>{progress === -1 ? 'Error' : `${progress}%`}</span>
            </div>
          ))}
        </div>
      )}

      <div className="file-list">
        {files.map((file) => (
          <div key={file.filename} className="file-item">
            <span className="filename">{file.filename}</span>
            <span className="file-date">{file.createdAt}</span>
            <div className="file-actions">
              <a href={file.url} download>Download</a>
              <button onClick={() => handleFileDelete(file.filename)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Testing and Debugging

### Test Endpoints

The uploads API includes several test endpoints for debugging and monitoring:

```typescript
// Test basic connectivity
async function runDiagnostics() {
  const tests = {
    rootTest: () => uploadsApi.rootTest(),
    aliveTest: () => uploadsApi.testAlive(),
    exportAlive: () => uploadsApi.exportAlive(),
    exportTest: () => uploadsApi.exportTest()
  };

  for (const [testName, testFunc] of Object.entries(tests)) {
    try {
      const result = await testFunc();
      console.log(`✅ ${testName}:`, result);
    } catch (error) {
      console.error(`❌ ${testName}:`, error.message);
    }
  }
}

// Health check for file upload service
async function checkUploadHealth(): Promise<boolean> {
  try {
    const [rootTest, aliveTest, exportTest] = await Promise.all([
      uploadsApi.rootTest(),
      uploadsApi.testAlive(),
      uploadsApi.exportAlive()
    ]);

    const isHealthy = 
      rootTest.status === 'uploads root test alive' &&
      aliveTest.status === 'uploads alive' &&
      exportTest.status === 'uploads export alive';

    console.log('Upload service health:', isHealthy ? 'HEALTHY' : 'UNHEALTHY');
    return isHealthy;
  } catch (error) {
    console.error('Health check failed:', error.message);
    return false;
  }
}
```

## Error Handling Patterns

### Comprehensive Error Management

```typescript
class UploadErrorHandler {
  static handleUploadError(error: Error, file?: File): string {
    const filename = file?.name || 'unknown file';
    
    if (error.message.includes('413')) {
      return `File "${filename}" is too large. Maximum size is 50MB.`;
    } else if (error.message.includes('415')) {
      return `File type for "${filename}" is not supported. Please upload PDF, text, or image files.`;
    } else if (error.message.includes('403')) {
      return 'You do not have permission to upload files. Please check your account status.';
    } else if (error.message.includes('507')) {
      return 'Server storage is full. Please try again later or contact support.';
    } else if (error.message.includes('409')) {
      return `A file named "${filename}" already exists. Please rename the file or delete the existing one.`;
    } else if (error.message.includes('network')) {
      return 'Network error during upload. Please check your connection and try again.';
    }
    return `Upload failed for "${filename}": ${error.message}`;
  }

  static handleListError(error: Error): string {
    if (error.message.includes('403')) {
      return 'You do not have permission to view files.';
    } else if (error.message.includes('503')) {
      return 'File service is temporarily unavailable. Please try again later.';
    }
    return `Failed to load files: ${error.message}`;
  }

  static handleDeleteError(error: Error, filename: string): string {
    if (error.message.includes('404')) {
      return `File "${filename}" not found. It may have already been deleted.`;
    } else if (error.message.includes('403')) {
      return `You do not have permission to delete "${filename}".`;
    } else if (error.message.includes('409')) {
      return `File "${filename}" is currently in use and cannot be deleted.`;
    }
    return `Failed to delete "${filename}": ${error.message}`;
  }
}

// Usage in error handling
try {
  await uploadsApi.uploadFile(file);
} catch (error) {
  const userMessage = UploadErrorHandler.handleUploadError(error, file);
  showUserNotification(userMessage, 'error');
}
```

## Performance Considerations

### Optimization Strategies

- **File Validation**: Client-side validation before upload to prevent unnecessary requests
- **Chunked Uploads**: For large files, consider implementing chunked upload functionality
- **Progress Tracking**: Real-time progress feedback for better user experience
- **Caching**: Intelligent caching of file lists and metadata
- **Batch Operations**: Efficient handling of multiple file operations

### Memory Management

```typescript
// Efficient file handling for large uploads
function processLargeFiles(files: FileList) {
  const processFile = async (file: File) => {
    try {
      // Process file in chunks if needed
      if (file.size > 10 * 1024 * 1024) { // 10MB threshold
        console.log(`Large file detected: ${file.name} (${file.size} bytes)`);
        // Implement chunked upload or compression
      }
      
      const result = await uploadsApi.uploadFile(file);
      return result;
    } finally {
      // Cleanup file references
      // (Files are automatically garbage collected, but this is good practice)
    }
  };

  // Process files sequentially to avoid memory issues
  return Array.from(files).reduce(async (previous, file) => {
    await previous;
    return processFile(file);
  }, Promise.resolve());
}
```

## Security Considerations

### File Upload Security

- **File Type Validation**: Both client and server-side validation of file types
- **Size Limits**: Enforced file size limitations to prevent abuse
- **Content Scanning**: Server-side scanning for malicious content
- **Access Control**: Proper authentication and authorization for all operations
- **Audit Logging**: Complete logging of all file operations for security tracking

### Best Practices

```typescript
// Secure file upload practices
function secureFileUpload(file: File): Promise<FileUploadResponse> {
  // 1. Validate file type
  const allowedTypes = [
    'application/pdf',
    'text/plain',
    'image/jpeg',
    'image/png',
    'image/gif'
  ];
  
  if (!allowedTypes.includes(file.type)) {
    throw new Error('File type not allowed for security reasons');
  }
  
  // 2. Check file size
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (file.size > maxSize) {
    throw new Error('File size exceeds security limits');
  }
  
  // 3. Sanitize filename
  const sanitizedName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
  
  // 4. Create secure file object
  const secureFile = new File([file], sanitizedName, { type: file.type });
  
  return uploadsApi.uploadFile(secureFile);
}
```

## Backend Integration

### Corresponding Backend Endpoints

This module integrates with the following backend endpoints:

- `POST /api/v1/uploads` - File upload
- `GET /api/v1/uploads` - File listing with filtering
- `GET /api/v1/uploads/{filename}` - File retrieval
- `DELETE /api/v1/uploads/{filename}` - File deletion
- `PATCH /api/v1/uploads/{id}` - File metadata updates
- `GET /api/v1/uploads/export` - CSV export
- `GET /api/v1/uploads/test-alive` - Health check

### Data Synchronization

- **Type Consistency**: Frontend types match backend data models exactly
- **Validation Alignment**: Client-side validation mirrors server-side rules
- **Error Code Mapping**: HTTP status codes are consistently handled
- **Schema Compatibility**: API requests/responses follow OpenAPI schema

## Dependencies

### External Dependencies

- **@/logger**: Application logging service for upload tracking
- **./base**: Base HTTP client providing the `request` function
- **Browser APIs**: File, FormData, Blob for file handling

### Internal Dependencies

- **TypeScript**: Type safety for upload operations
- **File API**: Browser file handling capabilities
- **HTTP Client**: Axios-based request handling through base module

## Related Files

- **[index.ts](index.ts.md)**: Main API module that exports uploads functionality
- **[base.ts](base.ts.md)**: Base HTTP client used for all requests
- **[errorHandling.ts](errorHandling.ts.md)**: Error handling utilities
- **[auth.ts](auth.ts.md)**: Authentication for protected upload operations
- **Backend**: `backend/src/api/v1/uploads.py` - corresponding backend implementation

## Implementation Best Practices

### Upload Implementation

- **Validate Early**: Perform client-side validation before upload attempts
- **Progress Feedback**: Always provide upload progress to users
- **Error Recovery**: Implement retry logic for network-related failures
- **Security First**: Never trust client-side validation alone

### User Experience

- **Clear Feedback**: Provide clear status updates during all operations
- **Error Messages**: Show user-friendly error messages with recovery options
- **Performance**: Handle large files and bulk operations efficiently
- **Accessibility**: Ensure upload components work with screen readers and keyboards
