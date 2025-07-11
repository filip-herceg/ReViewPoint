/**
 * File Upload API Module
 * 
 * Provides file upload and management functionality for the ReViewPoint application.
 * This module mirrors the backend upload endpoints and provides a consistent interface
 * for file operations including upload, download, listing, and deletion.
 * 
 * ## Endpoints
 * - `POST /uploads` - Upload a file
 * - `GET /uploads` - List uploaded files
 * - `GET /uploads/{filename}` - Get specific file
 * - `DELETE /uploads/{filename}` - Delete a file
 * - `GET /uploads/export` - Export file list as CSV
 * - `GET /uploads/test-alive` - Test endpoint availability
 * 
 * ## Usage
 * 
 * ### File Upload
 * ```typescript
 * import { uploadsApi } from '@/lib/api';
 * 
 * const handleFileUpload = async (file: File) => {
 *   try {
 *     const response = await uploadsApi.uploadFile(file);
 *     console.log('File uploaded:', response.filename);
 *     console.log('File URL:', response.url);
 *   } catch (error) {
 *     console.error('Upload failed:', error.message);
 *   }
 * };
 * 
 * // Example with file input
 * const fileInput = document.getElementById('file-input') as HTMLInputElement;
 * fileInput.addEventListener('change', (e) => {
 *   const file = e.target.files?.[0];
 *   if (file) {
 *     handleFileUpload(file);
 *   }
 * });
 * ```
 * 
 * ### File Listing
 * ```typescript
 * try {
 *   const files = await uploadsApi.listFiles({
 *     limit: 10,
 *     offset: 0,
 *     q: 'search term',
 *     sort: 'created_at',
 *     order: 'desc'
 *   });
 *   console.log('Files:', files.files);
 *   console.log('Total count:', files.total);
 * } catch (error) {
 *   console.error('Failed to list files:', error.message);
 * }
 * ```
 * 
 * ### File Deletion
 * ```typescript
 * try {
 *   await uploadsApi.deleteFile('example.pdf');
 *   console.log('File deleted successfully');
 * } catch (error) {
 *   console.error('Failed to delete file:', error.message);
 * }
 * ```
 * 
 * ### File Export
 * ```typescript
 * try {
 *   const csvBlob = await uploadsApi.exportFiles({
 *     fields: 'filename,created_at,size',
 *     sort: 'created_at',
 *     order: 'desc'
 *   });
 *   
 *   // Download CSV file
 *   const url = URL.createObjectURL(csvBlob);
 *   const a = document.createElement('a');
 *   a.href = url;
 *   a.download = 'files-export.csv';
 *   a.click();
 * } catch (error) {
 *   console.error('Export failed:', error.message);
 * }
 * ```
 * 
 * ## File Search and Filtering
 * The `listFiles` function supports various filtering options:
 * - `q`: Search query for filename
 * - `limit`: Maximum number of files to return
 * - `offset`: Number of files to skip (pagination)
 * - `sort`: Sort by 'created_at' or 'filename'
 * - `order`: Sort order 'asc' or 'desc'
 * - `created_after`: Filter by creation date
 * - `created_before`: Filter by creation date
 * - `fields`: Specify which fields to return
 * 
 * ## Error Handling
 * Upload functions throw errors for:
 * - File size limits exceeded
 * - Invalid file types
 * - Network errors
 * - Server storage issues
 * - Permission denied
 * 
 * ## Security Features
 * - File type validation
 * - Size limits
 * - User authentication required
 * - Secure file storage
 * 
 * @see backend/src/api/v1/uploads.py for corresponding backend implementation
 */

// File upload API functions
// Mirrors backend/src/api/v1/uploads.py

import logger from '@/logger';
import { request } from './base';

// Define the API_BASE_URL constant
const API_BASE_URL = '/api/uploads';

// Types that match the backend
interface FileUploadResponse {
    filename: string;
    url: string;
}

interface FileDict {
    filename: string;
    url: string;
    status?: string; // Add status field
    progress?: number; // Add progress field
    createdAt?: string; // Add createdAt field
}

interface FileListResponse {
    files: FileDict[];
    total: number;
}

interface FileResponse {
    filename: string;
    url: string;
    content_type?: string;
    size?: number;
    created_at?: string;
}

interface FileListParams {
    offset?: number;
    limit?: number;
    q?: string;
    fields?: string;
    sort?: 'created_at' | 'filename';
    order?: 'desc' | 'asc';
    created_after?: string;
    created_before?: string;
}

interface FileExportParams {
    q?: string;
    sort?: 'created_at' | 'filename';
    order?: 'desc' | 'asc';
    fields?: string;
    created_before?: string;
    created_after?: string;
}

export const uploadsApi = {
    // Test endpoints
    rootTest: async (): Promise<{ status: string; router: string }> => {
        logger.info('Testing uploads root endpoint');
        const response = await request<{ status: string; router: string }>('/uploads/root-test');

        if (response.error) {
            logger.warn('Root test failed', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Root test successful');
        return response.data!;
    },

    testAlive: async (): Promise<{ status: string }> => {
        logger.info('Testing uploads alive endpoint');
        const response = await request<{ status: string }>('/uploads/test-alive');

        if (response.error) {
            logger.warn('Test alive failed', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Test alive successful');
        return response.data!;
    },

    exportAlive: async (): Promise<{ status: string }> => {
        logger.info('Testing uploads export alive endpoint');
        const response = await request<{ status: string }>('/uploads/export-alive');

        if (response.error) {
            logger.warn('Export alive test failed', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Export alive successful');
        return response.data!;
    },

    exportTest: async (): Promise<{ status: string }> => {
        logger.info('Testing uploads export endpoint');
        const response = await request<{ status: string }>('/uploads/export-test');

        if (response.error) {
            logger.warn('Export test failed', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Export test successful');
        return response.data!;
    },

    // Export files as CSV
    exportFiles: async (params?: FileExportParams): Promise<Blob> => {
        logger.info('Exporting files as CSV', { params });
        const queryParams = params ? new URLSearchParams(params as any).toString() : '';
        const url = queryParams ? `/uploads/export?${queryParams}` : '/uploads/export';

        const response = await request<Blob>(url, {
            headers: {
                'Accept': 'text/csv',
            },
        });

        if (response.error) {
            logger.warn('Export files failed', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Files exported successfully');
        return response.data!;
    },

    // Upload a file
    uploadFile: async (file: File): Promise<FileUploadResponse> => {
        logger.info('Uploading file', { filename: file.name, size: file.size });
        const formData = new FormData();
        formData.append('file', file);

        const response = await request<FileUploadResponse>('/uploads', {
            method: 'POST',
            data: formData,
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        if (response.error) {
            logger.warn('File upload failed', { error: response.error, filename: file.name });
            throw new Error(response.error);
        }

        logger.info('File uploaded successfully', { filename: response.data!.filename, url: response.data!.url });
        return response.data!;
    },

    // List uploaded files
    listFiles: async (params?: FileListParams): Promise<FileListResponse> => {
        logger.info('Listing files', { params });
        const queryParams = params ? new URLSearchParams(params as any).toString() : '';
        const url = queryParams ? `/uploads?${queryParams}` : '/uploads';

        const response = await request<FileListResponse>(url);

        if (response.error) {
            logger.warn('Failed to list files', { error: response.error });
            throw new Error(response.error);
        }

        if (response.data) {
            logger.info('Files listed successfully', { total: response.data.total || 0 });
            return response.data;
        } else {
            logger.warn('Files list response has no data');
            throw new Error('No data in response');
        }
    },

    // Get file by filename
    getFile: async (filename: string): Promise<FileUploadResponse> => {
        logger.info('Getting file by filename', { filename });
        const response = await request<FileUploadResponse>(`/uploads/${encodeURIComponent(filename)}`);

        if (response.error) {
            logger.warn('Failed to get file', { error: response.error, filename });
            throw new Error(response.error);
        }

        logger.info('File retrieved successfully', { filename });
        return response.data!;
    },

    // Alias for backwards compatibility
    getFileByFilename: async (filename: string): Promise<FileUploadResponse> => {
        logger.info('Fetching file info', { filename });
        const response = await request<FileUploadResponse>(`/uploads/${encodeURIComponent(filename)}`);

        if (response.error) {
            logger.warn('Failed to fetch file info', { error: response.error, filename });
            throw new Error(response.error);
        }

        logger.info('File info fetched successfully', { filename });
        return response.data!;
    },

    // Alias for backwards compatibility
    getFiles: async (params?: FileListParams): Promise<FileListResponse> => {
        logger.info('Fetching files list', { params });
        const queryParams = params ? new URLSearchParams(params as any).toString() : '';
        const url = queryParams ? `/uploads?${queryParams}` : '/uploads';

        const response = await request<FileListResponse>(url);

        if (response.error) {
            logger.warn('Failed to fetch files', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Files fetched successfully', {
            total: response.data!.total,
            count: response.data!.files.length
        });
        return response.data!;
    },

    // Delete file by filename
    deleteFile: async (filename: string): Promise<null> => {
        logger.info('Deleting file', { filename });
        const response = await request<null>(`/uploads/${encodeURIComponent(filename)}`, {
            method: 'DELETE',
        });

        if (response.error) {
            logger.warn('File deletion failed', { error: response.error, filename });
            throw new Error(response.error);
        }

        logger.info('File deleted successfully', { filename });
        return null;
    },

    // Create a new upload (v2)
    createUpload: async (file: File): Promise<{ id: string; name: string; status: string; progress: number; createdAt: string }> => {
        logger.info('Creating new upload', { filename: file.name, size: file.size });
        const formData = new FormData();
        formData.append('file', file);

        const response = await request<{ id: string; name: string; status: string; progress: number; createdAt: string }>(`${API_BASE_URL}`, {
            method: 'POST',
            data: formData,
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        if (response.error) {
            logger.warn('Upload creation failed', { error: response.error, filename: file.name });
            throw new Error(response.error);
        }

        logger.info('Upload created successfully', { id: response.data!.id, filename: file.name });
        return response.data!;
    },

    // Patch an existing file (v2)
    patchFile: async (id: string, updates: Record<string, any>): Promise<void> => {
        logger.info('Patching file', { id, updates });
        const response = await request<void>(`${API_BASE_URL}/${id}`, {
            method: 'PATCH',
            data: updates,
        });

        if (response.error) {
            logger.warn('File patching failed', { error: response.error, id });
            throw new Error(response.error);
        }

        logger.info('File patched successfully', { id });
    },

    // Delete a file by ID (v2)
    deleteFileById: async (id: string): Promise<void> => {
        logger.info('Deleting file by ID', { id });
        const response = await request<void>(`${API_BASE_URL}/${id}`, {
            method: 'DELETE',
        });

        if (response.error) {
            logger.warn('File deletion failed', { error: response.error, id });
            throw new Error(response.error);
        }

        logger.info('File deleted successfully', { id });
    },
};

// Export the createUpload function for direct use
export const createUpload = uploadsApi.createUpload;
