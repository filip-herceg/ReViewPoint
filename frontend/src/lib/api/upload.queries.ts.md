# Upload Queries Module

**File:** `frontend/src/lib/api/upload.queries.ts`  
**Purpose:** React Query integration hooks for upload operations  
**Lines of Code:** 96  
**Type:** React Query Integration Layer  

## Overview

The upload queries module provides React Query-powered hooks for file upload operations in the ReViewPoint application. It serves as the bridge between the raw API layer (`uploadsApi`) and React components, offering optimized caching, background synchronization, optimistic updates, and automatic error handling for file management operations.

## Architecture

### Dependencies

```typescript
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { uploadsApi } from "@/lib/api";
import { createTestError } from "../../../tests/test-templates";
```

### Core Components

1. **Query Hooks** - Data fetching with caching
2. **Mutation Hooks** - Data modification with optimistic updates  
3. **Cache Management** - Automatic invalidation and synchronization
4. **Error Handling** - Consistent error reporting across operations

## Available Hooks

### 📋 **useUploads()** - File List Query

Fetches and caches the complete list of uploaded files with automatic background synchronization.

```typescript
export function useUploads()
```

**Features:**
- **Automatic Background Sync**: Refetches data when window regains focus
- **Network Recovery**: Automatically refetches when connection is restored
- **Smart Caching**: 1-minute stale time for optimal performance
- **Data Transformation**: Converts API response to standardized Upload format
- **Retry Logic**: Attempts up to 2 retries on failure

**Usage Example:**
```typescript
const UploadList = () => {
    const { data: uploads, isLoading, error, refetch } = useUploads();
    
    if (isLoading) return <LoadingSpinner />;
    if (error) return <ErrorMessage error={error} onRetry={refetch} />;
    
    return (
        <div>
            {uploads?.map(upload => (
                <UploadItem key={upload.id} upload={upload} />
            ))}
        </div>
    );
};
```

### 📄 **useUpload(filename)** - Single File Query

Fetches details for a specific file by filename with conditional execution.

```typescript
export function useUpload(filename?: string)
```

**Features:**
- **Conditional Execution**: Only runs when filename is provided
- **Single Retry**: Conservative retry strategy for individual file queries
- **Null Safety**: Returns null for missing files gracefully
- **Query Key Isolation**: Separate cache entry per filename

**Usage Example:**
```typescript
const FileDetails = ({ filename }: { filename?: string }) => {
    const { data: file, isLoading, error } = useUpload(filename);
    
    if (!filename) return <div>No file selected</div>;
    if (isLoading) return <LoadingSpinner />;
    if (error) return <ErrorMessage error={error} />;
    if (!file) return <div>File not found</div>;
    
    return <FileDetailsView file={file} />;
};
```

### ⬆️ **useCreateUpload()** - File Upload Mutation

Handles file uploads with automatic cache invalidation and progress tracking.

```typescript
export function useCreateUpload()
```

**Features:**
- **Optimistic Updates**: Immediate UI feedback
- **Cache Invalidation**: Automatically refreshes file list after upload
- **Progress Integration**: Compatible with upload progress tracking
- **Error Recovery**: Handles upload failures gracefully

**Usage Example:**
```typescript
const FileUploader = () => {
    const uploadMutation = useCreateUpload();
    
    const handleFileSelect = async (file: File) => {
        try {
            await uploadMutation.mutateAsync(file);
            toast.success('File uploaded successfully!');
        } catch (error) {
            toast.error('Upload failed. Please try again.');
        }
    };
    
    return (
        <input 
            type="file" 
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            disabled={uploadMutation.isPending}
        />
    );
};
```

### ✏️ **useUpdateUpload()** - File Update Mutation (Deprecated)

Legacy hook maintained for backwards compatibility. Throws error as file updates are not supported.

```typescript
export function useUpdateUpload()
```

**Features:**
- **Backwards Compatibility**: Prevents breaking changes in existing code
- **Clear Error Messages**: Explains why operation is not supported
- **Migration Guidance**: Suggests alternative approach (delete + re-upload)

**Usage Example:**
```typescript
// This will throw an error with helpful message
const updateMutation = useUpdateUpload();

try {
    await updateMutation.mutateAsync({ id: 'file-id', data: newData });
} catch (error) {
    // Error: "File updates are not supported. Please delete and re-upload the file."
    showMigrationDialog();
}
```

### 🗑️ **useDeleteUpload()** - File Deletion Mutation

Handles file deletion with immediate cache cleanup and error recovery.

```typescript
export function useDeleteUpload()
```

**Features:**
- **Immediate Cache Cleanup**: Removes file from UI instantly
- **Background Synchronization**: Ensures server state consistency
- **Error Recovery**: Reverts optimistic updates on failure
- **Confirmation Integration**: Compatible with confirmation dialogs

**Usage Example:**
```typescript
const FileManager = () => {
    const deleteMutation = useDeleteUpload();
    
    const handleDelete = async (filename: string) => {
        const confirmed = await confirmDialog('Delete this file?');
        if (!confirmed) return;
        
        try {
            await deleteMutation.mutateAsync(filename);
            toast.success('File deleted successfully');
        } catch (error) {
            toast.error('Failed to delete file');
        }
    };
    
    return (
        <button 
            onClick={() => handleDelete(file.filename)}
            disabled={deleteMutation.isPending}
        >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
        </button>
    );
};
```

## Data Transformation

### API Response to Upload Format

The `useUploads()` hook transforms raw API responses into a standardized format:

```typescript
// API Response Format (FileListResponse)
{
    files: [
        { filename: "document.pdf", url: "/uploads/document.pdf" }
    ]
}

// Transformed Upload Format
[
    {
        id: "file-12345-abc789",           // Generated unique ID
        name: "document.pdf",               // User-friendly name
        status: "completed",                // Upload status
        progress: 100,                      // Progress percentage
        createdAt: "2024-01-15T10:30:00Z", // ISO timestamp
        response: {                         // Original API response
            filename: "document.pdf",
            url: "/uploads/document.pdf"
        }
    }
]
```

### Benefits of Transformation

- **Consistent Interface**: Uniform data structure across components
- **Backwards Compatibility**: Maintains compatibility with existing components
- **Enhanced Metadata**: Adds useful fields like progress and timestamps
- **Type Safety**: Full TypeScript support for all transformed fields

## Query Configuration

### Caching Strategy

```typescript
// useUploads() configuration
{
    staleTime: 1000 * 60,        // 1 minute - reduces unnecessary requests
    refetchOnWindowFocus: true,   // Sync when user returns to tab
    refetchOnReconnect: true,     // Sync when network reconnects
    retry: 2                      // Retry failed requests twice
}

// useUpload() configuration  
{
    enabled: !!filename,          // Only run when filename exists
    retry: 1                      // Single retry for individual files
}
```

### Query Keys

- **File List**: `["uploads"]` - Global file list cache
- **Individual Files**: `["upload", filename]` - Per-file cache entries

## Error Handling

### Error Types and Recovery

```typescript
// Network errors (connection issues)
if (error?.type === 'network') {
    showNetworkErrorMessage();
    // React Query will automatically retry
}

// API errors (4xx/5xx responses)
if (error?.type === '4xx' || error?.type === '5xx') {
    showApiErrorMessage(error.message);
    // User can manually retry with refetch()
}

// Test errors (development/testing)
if (error?.message?.includes('test error')) {
    showTestErrorDialog();
}
```

### Mutation Error Recovery

```typescript
const uploadMutation = useCreateUpload();

// Handle errors with context
uploadMutation.mutate(file, {
    onError: (error) => {
        if (error.status === 413) {
            showFileTooLargeError();
        } else if (error.status === 415) {
            showUnsupportedFileTypeError();
        } else {
            showGenericUploadError();
        }
    }
});
```

## Performance Optimization

### ⚡ **Caching Benefits**

- **Reduced API Calls**: 1-minute stale time prevents unnecessary requests
- **Background Updates**: Fresh data without blocking UI
- **Shared Cache**: Multiple components share same cached data
- **Memory Efficient**: Automatic garbage collection of unused cache entries

### 🔄 **Optimistic Updates**

```typescript
// File appears in UI immediately
const optimisticUpload = {
    id: `temp-${Date.now()}`,
    name: file.name,
    status: 'uploading',
    progress: 0
};

// Background upload confirms or reverts
uploadMutation.mutate(file);
```

### 📊 **Background Synchronization**

- **Window Focus**: Automatically syncs when user returns to application
- **Network Recovery**: Refetches data when connection is restored
- **Smart Invalidation**: Only updates changed data, preserves selections

## Integration Examples

### File Upload with Progress

```typescript
const FileUploadWithProgress = () => {
    const [uploadProgress, setUploadProgress] = useState(0);
    const uploadMutation = useCreateUpload();
    
    const handleUpload = async (file: File) => {
        // Show immediate progress feedback
        setUploadProgress(0);
        
        try {
            // Upload with progress tracking
            await uploadsApi.uploadFile(file, {
                onUploadProgress: (progress) => {
                    setUploadProgress(progress.percentage);
                }
            });
            
            // Mutation will auto-invalidate cache
            toast.success('Upload complete!');
        } catch (error) {
            setUploadProgress(0);
            toast.error('Upload failed');
        }
    };
    
    return (
        <div>
            <input type="file" onChange={handleUpload} />
            {uploadProgress > 0 && (
                <ProgressBar value={uploadProgress} />
            )}
        </div>
    );
};
```

### Bulk Operations

```typescript
const BulkFileManager = () => {
    const { data: uploads } = useUploads();
    const deleteMutation = useDeleteUpload();
    
    const deleteSelected = async (selectedFiles: string[]) => {
        const promises = selectedFiles.map(filename => 
            deleteMutation.mutateAsync(filename)
        );
        
        try {
            await Promise.all(promises);
            toast.success(`Deleted ${selectedFiles.length} files`);
        } catch (error) {
            toast.error('Some deletions failed');
        }
    };
    
    return <BulkOperationInterface onDelete={deleteSelected} />;
};
```

### Real-time Updates

```typescript
const RealTimeFileList = () => {
    const { data: uploads, refetch } = useUploads();
    
    // Set up WebSocket for real-time updates
    useEffect(() => {
        const ws = new WebSocket('/ws/uploads');
        
        ws.onmessage = (event) => {
            const { type } = JSON.parse(event.data);
            
            if (type === 'file_uploaded' || type === 'file_deleted') {
                // Invalidate cache to refetch latest data
                refetch();
            }
        };
        
        return () => ws.close();
    }, [refetch]);
    
    return <FileList uploads={uploads} />;
};
```

## Testing Support

### Mock Data Integration

```typescript
// Uses createTestError for consistent test error handling
const testError = createTestError("Upload failed in test");

// Test mutation error scenarios
const TestUploadError = () => {
    const uploadMutation = useCreateUpload();
    
    const triggerTestError = () => {
        uploadMutation.mutate(mockFile, {
            onError: (error) => {
                expect(error.message).toContain('test');
            }
        });
    };
};
```

### Query Testing

```typescript
// Test query hooks with React Query Testing Library
import { renderHook, waitFor } from '@testing-library/react';
import { QueryWrapper } from '../../../tests/test-utils';

test('useUploads fetches file list', async () => {
    const { result } = renderHook(() => useUploads(), {
        wrapper: QueryWrapper
    });
    
    await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.data).toHaveLength(2);
    });
});
```

## Migration Guide

### From Direct API Calls

```typescript
// Before: Direct API usage
const [uploads, setUploads] = useState([]);
const [loading, setLoading] = useState(false);

useEffect(() => {
    setLoading(true);
    uploadsApi.listFiles()
        .then(setUploads)
        .finally(() => setLoading(false));
}, []);

// After: React Query hooks
const { data: uploads, isLoading } = useUploads();
```

### From Manual Cache Management

```typescript
// Before: Manual state management
const [uploads, setUploads] = useState([]);

const deleteFile = async (filename: string) => {
    await uploadsApi.deleteFile(filename);
    // Manual cache update
    setUploads(prev => prev.filter(f => f.filename !== filename));
};

// After: Automatic cache management
const deleteMutation = useDeleteUpload();

const deleteFile = (filename: string) => {
    deleteMutation.mutate(filename);
    // Cache automatically updated
};
```

## Best Practices

### ✅ **Do's**

- **Use Mutation Callbacks**: Handle success/error states appropriately
- **Implement Loading States**: Show feedback during async operations
- **Handle Edge Cases**: Check for null/undefined data
- **Leverage Caching**: Let React Query manage data freshness
- **Test Error Scenarios**: Verify error handling works correctly

### ❌ **Don'ts**

- **Don't Bypass Cache**: Avoid direct API calls when hooks exist
- **Don't Ignore Errors**: Always handle mutation failures
- **Don't Manual Invalidation**: Let hooks manage cache updates
- **Don't Duplicate Queries**: Reuse existing hooks across components

## Related Documentation

- **Upload API**: `uploads.ts.md` - Core upload functionality
- **Base API**: `base.ts.md` - HTTP client foundation
- **Error Handling**: `errorHandling.ts.md` - Error processing
- **Type System**: `types/index.ts.md` - Upload-related types
- **React Query**: Official documentation for advanced usage patterns

## Dependencies

- **@tanstack/react-query**: Query and mutation management
- **uploadsApi**: Core upload API functions
- **createTestError**: Testing utilities for consistent error handling

---

*This module provides the React integration layer for upload operations, offering optimized caching, automatic synchronization, and seamless error handling for file management in the ReViewPoint application.*
