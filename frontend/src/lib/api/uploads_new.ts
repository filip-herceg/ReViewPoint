// File upload API functions
// Mirrors backend/src/api/v1/uploads.py

import logger from '@/logger';
import { request } from './base';

// Types that match the backend
interface FileUploadResponse {
    filename: string;
    url: string;
}

interface FileDict {
    filename: string;
    url: string;
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

        logger.info('Export alive test successful');
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
            responseType: 'blob',
        });

        if (response.error) {
            logger.warn('Failed to export files CSV', { error: response.error });
            throw new Error(response.error);
        }

        logger.info('Files CSV exported successfully');
        return response.data!;
    },

    // Upload a file
    uploadFile: async (file: File): Promise<FileUploadResponse> => {
        logger.info('Uploading file', { filename: file.name });
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

        logger.info('File uploaded successfully', { filename: response.data!.filename });
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

        logger.info('Files listed successfully', { total: response.data!.total });
        return response.data!;
    },

    // Get file by filename
    getFile: async (filename: string): Promise<FileUploadResponse> => {
        logger.info('Getting file by filename', { filename });
        const response = await request<FileUploadResponse>(`/uploads/${filename}`);

        if (response.error) {
            logger.warn('Failed to get file', { error: response.error, filename });
            throw new Error(response.error);
        }

        logger.info('File retrieved successfully', { filename });
        return response.data!;
    },

    // Delete file by filename
    deleteFile: async (filename: string): Promise<void> => {
        logger.info('Deleting file', { filename });
        const response = await request<null>(`/uploads/${filename}`, {
            method: 'DELETE',
        });

        if (response.error) {
            logger.warn('File deletion failed', { error: response.error, filename });
            throw new Error(response.error);
        }

        logger.info('File deleted successfully', { filename });
    },
};
