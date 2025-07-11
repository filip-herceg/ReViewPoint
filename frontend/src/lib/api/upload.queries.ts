import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadsApi } from '@/lib/api';
import { createTestError } from '../../../tests/test-templates';
import type { File as ApiFile, FileUploadResponse } from '@/lib/api/types';

// Fetch all uploaded files
export function useUploads() {
    return useQuery({
        queryKey: ['uploads'],
        queryFn: async () => {
            const res = await uploadsApi.listFiles();
            // Convert FileListResponse to Upload format
            if (res.files && Array.isArray(res.files)) {
                return res.files.map(file => ({
                    id: file.filename || `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    name: file.filename || 'Unknown File',
                    status: 'completed' as const,
                    progress: 100,
                    createdAt: new Date().toISOString(),
                    response: { filename: file.filename, url: file.url || '' }
                }));
            }
            return [];
        },
        staleTime: 1000 * 60, // 1 minute
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 2,
    });
}

// Fetch a single file by filename
export function useUpload(filename?: string) {
    return useQuery({
        queryKey: ['upload', filename],
        queryFn: async () => {
            if (!filename) throw createTestError('No filename');
            const res = await uploadsApi.getFile(filename);
            return res ?? null;
        },
        enabled: !!filename,
        retry: 1,
    });
}

// Upload file (mutation with optimistic update)
export function useCreateUpload() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (file: File) => {
            const res = await uploadsApi.uploadFile(file);
            return res;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['uploads'] });
        },
    });
}

// Note: File updates are not supported in the new API
// This is kept for backwards compatibility but will throw an error
export function useUpdateUpload() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, data }: { id: string; data: any }) => {
            throw createTestError('File updates are not supported. Please delete and re-upload the file.');
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['uploads'] });
        },
    });
}

// Delete file by filename (mutation with optimistic update)
export function useDeleteUpload() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (filename: string) => {
            await uploadsApi.deleteFile(filename);
            return null;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['uploads'] });
        },
    });
}
