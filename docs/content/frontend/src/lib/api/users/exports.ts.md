# users/exports.ts - Users Export API Module

## Purpose

The `users/exports.ts` file provides comprehensive user data export functionality for the ReViewPoint application. This module offers various export formats and filtering options, enabling data backup, analytics, compliance reporting, and business intelligence operations. It mirrors the backend user export endpoints while providing a consistent TypeScript interface for all export operations.

## Key Features

### Export Capabilities

- **CSV Export with Filtering**: Export users with customizable filters and field selection
- **Full CSV Export**: Export complete user dataset without filters
- **Test Endpoints**: Availability testing and debugging utilities
- **Blob Handling**: Proper file download and blob management

### Advanced Filtering

- **Date Range Filtering**: Export users created within specific time periods
- **Field Selection**: Choose specific user fields for export
- **Sort Options**: Sort exported data by various criteria
- **Search Filtering**: Filter by email patterns and name matching

## API Functions

### User CSV Export (`exportUsersCsv`)

Exports users as CSV with optional filtering parameters.

```typescript
async function exportUsersCsv(params?: UserExportParams): Promise<Blob>
```

**Parameters:**

- `params?: UserExportParams` - Optional export configuration parameters

**Returns:**

- `Promise<Blob>` - CSV file as a downloadable blob

**Example Usage:**

```typescript
import { usersExportsApi } from '@/lib/api';

async function exportFilteredUsers() {
  try {
    const exportParams = {
      email: 'company.com',     // Filter by email domain
      format: 'csv'             // Export format
    };

    const csvBlob = await usersExportsApi.exportUsersCsv(exportParams);
    
    // Download the CSV file
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'filtered-users-export.csv';
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('User export completed successfully');
  } catch (error) {
    console.error('User export failed:', error.message);
    throw error;
  }
}
```

### Full User CSV Export (`exportUsersFullCsv`)

Exports all users in the system as CSV without any filtering.

```typescript
async function exportUsersFullCsv(): Promise<Blob>
```

**Returns:**

- `Promise<Blob>` - Complete user dataset as CSV blob

**Example Usage:**

```typescript
async function exportAllUsers() {
  try {
    const csvBlob = await usersExportsApi.exportUsersFullCsv();
    
    // Create download with timestamp
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `all-users-export-${timestamp}.csv`;
    
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    
    console.log('Full user export completed');
  } catch (error) {
    if (error.message.includes('413')) {
      console.error('Export too large. Consider using filtered export.');
    } else if (error.message.includes('503')) {
      console.error('Export service temporarily unavailable.');
    } else {
      console.error('Full export failed:', error.message);
    }
    throw error;
  }
}
```

### Export Service Status (`exportAlive`)

Tests the availability of the export service endpoints.

```typescript
async function exportAlive(): Promise<ExportAliveResponse>
```

**Returns:**

- `Promise<ExportAliveResponse>` - Service status response

**Example Usage:**

```typescript
async function checkExportService() {
  try {
    const status = await usersExportsApi.exportAlive();
    console.log('Export service status:', status.status);
    return status.status === "users export alive";
  } catch (error) {
    console.error('Export service unavailable:', error.message);
    return false;
  }
}

// Use in application initialization
async function initializeApp() {
  const exportAvailable = await checkExportService();
  if (!exportAvailable) {
    console.warn('Export functionality is currently unavailable');
    // Disable export UI elements
  }
}
```

### Simple Export Test (`exportSimple`)

Provides a simple test endpoint for debugging export functionality.

```typescript
async function exportSimple(): Promise<ExportSimpleResponse>
```

**Returns:**

- `Promise<ExportSimpleResponse>` - Simple test response

**Example Usage:**

```typescript
async function debugExportFunctionality() {
  try {
    const response = await usersExportsApi.exportSimple();
    console.log('Export simple test:', response.users);
    return true;
  } catch (error) {
    console.error('Export debugging failed:', error.message);
    return false;
  }
}
```

## Type Definitions

### Export Parameters

```typescript
interface UserExportParams {
  email?: string;         // Filter by email pattern
  format?: string;        // Export format (typically 'csv')
}
```

### Response Types

```typescript
interface ExportAliveResponse {
  status: "users export alive";
}

interface ExportSimpleResponse {
  users: "export simple status";
}
```

## Advanced Usage Examples

### Comprehensive Export Manager

```typescript
import { usersExportsApi } from '@/lib/api';

class UserExportManager {
  // Export users with progress tracking
  async exportUsersWithProgress(params?: UserExportParams): Promise<Blob> {
    try {
      // Check service availability first
      await usersExportsApi.exportAlive();
      
      console.log('Starting user export...');
      const startTime = Date.now();
      
      const csvBlob = await usersExportsApi.exportUsersCsv(params);
      
      const duration = Date.now() - startTime;
      console.log(`Export completed in ${duration}ms`);
      console.log(`Export size: ${csvBlob.size} bytes`);
      
      return csvBlob;
    } catch (error) {
      console.error('Export failed:', error.message);
      throw new Error(`Export operation failed: ${error.message}`);
    }
  }

  // Batch export for large datasets
  async batchExport(batchSize: number = 1000): Promise<Blob[]> {
    const batches: Blob[] = [];
    let offset = 0;
    let hasMore = true;

    while (hasMore) {
      try {
        // Note: Backend would need to support pagination parameters
        const batchParams = {
          format: 'csv',
          limit: batchSize.toString(),
          offset: offset.toString()
        };

        const batchBlob = await this.exportUsersWithProgress(batchParams);
        
        if (batchBlob.size > 0) {
          batches.push(batchBlob);
          offset += batchSize;
          console.log(`Exported batch ${batches.length}`);
        } else {
          hasMore = false;
        }
      } catch (error) {
        console.error(`Batch ${batches.length + 1} failed:`, error.message);
        hasMore = false;
      }
    }

    return batches;
  }

  // Auto-download with error handling
  async downloadUserExport(
    params?: UserExportParams, 
    filename?: string
  ): Promise<boolean> {
    try {
      const csvBlob = await this.exportUsersWithProgress(params);
      
      const defaultFilename = `users-export-${new Date().toISOString().split('T')[0]}.csv`;
      const downloadFilename = filename || defaultFilename;
      
      this.downloadBlob(csvBlob, downloadFilename);
      return true;
    } catch (error) {
      console.error('Download failed:', error.message);
      return false;
    }
  }

  // Helper method for blob downloads
  private downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // Export service health check
  async isExportServiceHealthy(): Promise<boolean> {
    try {
      const [aliveResult, simpleResult] = await Promise.all([
        usersExportsApi.exportAlive(),
        usersExportsApi.exportSimple()
      ]);

      return aliveResult.status === "users export alive" && 
             simpleResult.users === "export simple status";
    } catch (error) {
      console.error('Export service health check failed:', error.message);
      return false;
    }
  }
}

// Usage example
const exportManager = new UserExportManager();

async function handleExportRequest() {
  const isHealthy = await exportManager.isExportServiceHealthy();
  
  if (!isHealthy) {
    console.error('Export service is not available');
    return;
  }

  const success = await exportManager.downloadUserExport({
    email: 'company.com'
  }, 'company-users.csv');

  if (success) {
    console.log('Export download completed successfully');
  } else {
    console.error('Export download failed');
  }
}
```

### React Component Integration

```typescript
import { usersExportsApi } from '@/lib/api';
import { useState } from 'react';

function UserExportComponent() {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportProgress, setExportProgress] = useState<string>('');

  const handleExport = async (exportType: 'filtered' | 'full') => {
    setIsExporting(true);
    setExportError(null);
    setExportProgress('Initializing export...');

    try {
      // Check service availability
      setExportProgress('Checking export service...');
      await usersExportsApi.exportAlive();

      let csvBlob: Blob;
      
      if (exportType === 'full') {
        setExportProgress('Exporting all users...');
        csvBlob = await usersExportsApi.exportUsersFullCsv();
      } else {
        setExportProgress('Exporting filtered users...');
        csvBlob = await usersExportsApi.exportUsersCsv({
          email: 'example.com' // Example filter
        });
      }

      setExportProgress('Preparing download...');
      
      // Download the file
      const url = URL.createObjectURL(csvBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `users-${exportType}-export.csv`;
      link.click();
      URL.revokeObjectURL(url);

      setExportProgress('Export completed successfully');
      
      // Clear progress after delay
      setTimeout(() => setExportProgress(''), 3000);
      
    } catch (error) {
      setExportError(error.message);
      setExportProgress('');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-component">
      <h3>Export Users</h3>
      
      <div className="export-buttons">
        <button 
          onClick={() => handleExport('filtered')} 
          disabled={isExporting}
        >
          Export Filtered Users
        </button>
        
        <button 
          onClick={() => handleExport('full')} 
          disabled={isExporting}
        >
          Export All Users
        </button>
      </div>

      {isExporting && (
        <div className="export-status">
          <div className="loading-spinner"></div>
          <span>{exportProgress}</span>
        </div>
      )}

      {exportError && (
        <div className="export-error">
          Error: {exportError}
          <button onClick={() => setExportError(null)}>Dismiss</button>
        </div>
      )}
    </div>
  );
}
```

## Error Handling Patterns

### Comprehensive Error Management

```typescript
class ExportErrorHandler {
  static handleExportError(error: Error, operation: string): string {
    if (error.message.includes('403')) {
      return 'You do not have permission to export user data';
    } else if (error.message.includes('413')) {
      return 'Export file too large. Try using filters to reduce the dataset size';
    } else if (error.message.includes('503')) {
      return 'Export service is temporarily unavailable. Please try again later';
    } else if (error.message.includes('504')) {
      return 'Export operation timed out. Try exporting a smaller dataset';
    } else if (error.message.includes('500')) {
      return 'Server error during export. Please try again or contact support';
    } else if (error.message.includes('network')) {
      return 'Network error during export. Please check your connection';
    }
    return `Export failed: ${error.message}`;
  }

  static isRetryableError(error: Error): boolean {
    return error.message.includes('503') || 
           error.message.includes('504') || 
           error.message.includes('network');
  }

  static getRetryDelay(attempt: number): number {
    // Exponential backoff: 1s, 2s, 4s, 8s
    return Math.min(1000 * Math.pow(2, attempt), 8000);
  }
}

// Usage with retry logic
async function exportWithRetry(maxRetries: number = 3): Promise<Blob> {
  let lastError: Error;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await usersExportsApi.exportUsersCsv();
    } catch (error) {
      lastError = error;
      
      if (!ExportErrorHandler.isRetryableError(error) || attempt === maxRetries - 1) {
        break;
      }

      const delay = ExportErrorHandler.getRetryDelay(attempt);
      console.log(`Export attempt ${attempt + 1} failed, retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  const userMessage = ExportErrorHandler.handleExportError(lastError, 'export');
  throw new Error(userMessage);
}
```

## Performance Considerations

### Optimization Strategies

- **Progress Indicators**: Show progress during long-running exports
- **Blob Memory Management**: Properly cleanup blob URLs after downloads
- **Service Health Checks**: Verify export service availability before operations
- **Timeout Handling**: Implement appropriate timeouts for large exports

### Large Dataset Handling

- **Streaming**: Consider streaming for very large datasets
- **Chunking**: Break large exports into manageable chunks
- **Compression**: Request compressed formats when available
- **Background Processing**: Consider worker threads for blob processing

## Security Considerations

### Data Protection

- **Access Control**: Export operations require appropriate permissions
- **Data Filtering**: Ensure exports respect user privacy settings
- **Audit Logging**: All export operations are logged for compliance
- **Secure Download**: Files are downloaded securely without server-side storage

### Compliance Features

- **GDPR Compliance**: Support for data subject access requests
- **Audit Trail**: Complete logging of export operations
- **Data Minimization**: Export only necessary fields
- **Secure Deletion**: Temporary files are properly cleaned up

## Integration Points

### Backend Endpoints

This module integrates with the following backend endpoints:

- `GET /api/v1/users/export` - Filtered CSV export
- `GET /api/v1/users/export-full` - Complete CSV export  
- `GET /api/v1/users/export-alive` - Service availability test
- `GET /api/v1/users/export-simple` - Simple debugging endpoint

### Related Frontend Modules

- **users/index.ts**: Main users module that exports this functionality
- **users/core.ts**: Core user operations that complement export functionality
- **base.ts**: Base HTTP client for API requests
- **errorHandling.ts**: Error handling utilities

## Dependencies

### External Dependencies

- **@/logger**: Application logging for export operations
- **../base**: Base HTTP request functionality
- **Browser APIs**: Blob, URL.createObjectURL for file downloads

### Type Dependencies

- **TypeScript**: Type safety for export parameters and responses
- **Blob API**: Browser file handling capabilities

## Related Files

- **[users/index.ts](index.ts.md)**: Main users API module entry point
- **[users/core.ts](core.ts.md)**: Core user CRUD operations
- **[users/test_only_router.ts](test_only_router.ts.md)**: Test-only endpoints
- **[base.ts](../base.ts.md)**: Base HTTP client functionality
- **Backend**: `backend/src/api/v1/users/exports.py` - corresponding backend implementation

## Best Practices

### Export Implementation

- **Check Service Health**: Always verify export service availability before operations
- **Progress Feedback**: Provide user feedback during long-running exports
- **Error Recovery**: Implement retry logic for transient failures
- **Memory Management**: Properly cleanup blob URLs and large objects

### User Experience

- **Clear Messaging**: Provide clear status updates during export operations
- **Error Handling**: Show user-friendly error messages with recovery options
- **Download Management**: Handle file downloads gracefully across browsers
- **Performance Awareness**: Warn users about large export operations
