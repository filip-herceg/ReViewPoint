import { useState, useCallback, useRef } from 'react';
import { logger } from '@/lib/logger';
import type {
    UploadQueueItem,
    AdvancedUploadOptions,
    FileValidationResult,
    UploadChunkInfo
} from '@/lib/api/types/upload';
import { useUploadQueue } from './useUploadQueue';
import { useFileValidation } from './useFileValidation';
import { useUploadProgress } from './useUploadProgress';
import { chunkFile, combineChunks } from '@/lib/utils/chunkUtils';
import { uploadFile } from '@/lib/api/uploads';

/**
 * Advanced file upload hook with queue management, chunking, and progress tracking
 */
export function useAdvancedFileUpload(options: AdvancedUploadOptions = {}) {
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    const {
        addToQueue,
        updateQueueItem,
        removeFromQueue,
        getQueueItem,
        processQueue
    } = useUploadQueue({
        maxConcurrent: options.maxConcurrentChunks || 3,
        autoRetry: true,
        maxRetries: 3
    });

    const { validateFile, validateFiles } = useFileValidation();
    const { calculateProgress, calculateETA, calculateSpeed } = useUploadProgress();

    /**
     * Upload a single file with advanced options
     */
    const uploadSingleFile = useCallback(async (
        file: File,
        uploadOptions: Partial<AdvancedUploadOptions> = {}
    ): Promise<UploadQueueItem> => {
        const mergedOptions = { ...options, ...uploadOptions };
        logger.info('Starting advanced file upload', {
            filename: file.name,
            size: file.size,
            enableChunked: mergedOptions.enableChunked,
            chunkSize: mergedOptions.chunkSize
        });

        try {
            // Validate file
            const validation = await validateFile(file);
            if (!validation.isValid) {
                const errorMessage = validation.errors.map(e => e.message).join(', ');
                logger.error('File validation failed', { filename: file.name, errors: validation.errors });
                throw new Error(`File validation failed: ${errorMessage}`);
            }

            // Create queue item
            const queueItem: UploadQueueItem = {
                id: crypto.randomUUID(),
                file,
                priority: mergedOptions.priority || 5,
                status: 'pending',
                progress: 0,
                startTime: Date.now(),
                chunks: undefined
            };

            // Add to queue
            addToQueue(queueItem);

            // Start upload
            setIsUploading(true);
            setError(null);

            let result;
            if (mergedOptions.enableChunked && file.size > (mergedOptions.chunkSize || 1024 * 1024)) {
                result = await uploadFileChunked(queueItem, mergedOptions);
            } else {
                result = await uploadFileWhole(queueItem, mergedOptions);
            }

            // Update queue item with result
            updateQueueItem(queueItem.id, {
                status: 'completed',
                progress: 100,
                endTime: Date.now(),
                result
            });

            logger.info('File upload completed successfully', {
                filename: file.name,
                uploadId: queueItem.id
            });

            return getQueueItem(queueItem.id)!;

        } catch (uploadError) {
            const errorMessage = uploadError instanceof Error ? uploadError.message : 'Upload failed';
            logger.error('File upload failed', {
                filename: file.name,
                error: errorMessage
            });

            // Update queue item with error
            updateQueueItem(queueItem.id, {
                status: 'error',
                error: {
                    message: errorMessage,
                    code: 'UPLOAD_ERROR',
                    retryable: true,
                    retryCount: 0
                }
            });

            setError(errorMessage);
            throw uploadError;
        } finally {
            setIsUploading(false);
        }
    }, [options, addToQueue, updateQueueItem, getQueueItem, validateFile]);

    /**
     * Upload multiple files with queue management
     */
    const uploadMultipleFiles = useCallback(async (
        files: File[],
        uploadOptions: Partial<AdvancedUploadOptions> = {}
    ): Promise<UploadQueueItem[]> => {
        logger.info('Starting multiple file upload', { fileCount: files.length });

        try {
            // Validate all files first
            const validations = await validateFiles(files);
            const invalidFiles = validations.filter(v => !v.isValid);

            if (invalidFiles.length > 0) {
                const errorMessage = `${invalidFiles.length} files failed validation`;
                logger.error('Multiple file validation failed', {
                    invalidCount: invalidFiles.length,
                    totalCount: files.length
                });
                throw new Error(errorMessage);
            }

            // Upload files in queue
            const uploadPromises = files.map(file => uploadSingleFile(file, uploadOptions));
            const results = await Promise.allSettled(uploadPromises);

            // Process results
            const successfulUploads: UploadQueueItem[] = [];
            const failedUploads: string[] = [];

            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    successfulUploads.push(result.value);
                } else {
                    failedUploads.push(files[index].name);
                    logger.error('Individual file upload failed', {
                        filename: files[index].name,
                        error: result.reason
                    });
                }
            });

            if (failedUploads.length > 0) {
                logger.warn('Some files failed to upload', {
                    failed: failedUploads,
                    successful: successfulUploads.length
                });
            }

            return successfulUploads;

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Multiple upload failed';
            logger.error('Multiple file upload failed', { error: errorMessage });
            setError(errorMessage);
            throw error;
        }
    }, [uploadSingleFile, validateFiles]);

    /**
     * Upload file using chunked approach
     */
    const uploadFileChunked = useCallback(async (
        queueItem: UploadQueueItem,
        uploadOptions: AdvancedUploadOptions
    ) => {
        const { file } = queueItem;
        const chunkSize = uploadOptions.chunkSize || 1024 * 1024; // 1MB default

        logger.info('Starting chunked upload', {
            filename: file.name,
            fileSize: file.size,
            chunkSize
        });

        // Create chunks
        const chunks = await chunkFile(file, chunkSize);
        const chunkInfos: UploadChunkInfo[] = chunks.map((chunk, index) => ({
            index,
            start: index * chunkSize,
            end: Math.min((index + 1) * chunkSize - 1, file.size - 1),
            size: chunk.size,
            status: 'pending',
            progress: 0,
            retryCount: 0
        }));

        // Update queue item with chunks
        updateQueueItem(queueItem.id, { chunks: chunkInfos });

        // Upload chunks with concurrency control
        const maxConcurrent = uploadOptions.maxConcurrentChunks || 3;
        const uploadPromises: Promise<void>[] = [];
        let activeUploads = 0;
        let completedChunks = 0;

        const uploadChunk = async (chunkInfo: UploadChunkInfo, chunkBlob: Blob) => {
            try {
                logger.debug('Uploading chunk', {
                    filename: file.name,
                    chunkIndex: chunkInfo.index,
                    chunkSize: chunkBlob.size
                });

                // Update chunk status
                chunkInfo.status = 'uploading';
                updateQueueItem(queueItem.id, { chunks: chunkInfos });

                // Simulate chunk upload (replace with actual API call)
                // const result = await uploadChunk(chunkBlob, chunkInfo.index);
                await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));

                // Update chunk as completed
                chunkInfo.status = 'completed';
                chunkInfo.progress = 100;
                chunkInfo.etag = `"chunk-${chunkInfo.index}-etag"`;

                completedChunks++;
                const overallProgress = Math.round((completedChunks / chunks.length) * 100);

                updateQueueItem(queueItem.id, {
                    progress: overallProgress,
                    chunks: chunkInfos
                });

                // Call progress callback if provided
                if (uploadOptions.onChunkComplete) {
                    uploadOptions.onChunkComplete(chunkInfo.index, chunks.length);
                }

                logger.debug('Chunk upload completed', {
                    filename: file.name,
                    chunkIndex: chunkInfo.index,
                    overallProgress
                });

            } catch (error) {
                chunkInfo.status = 'error';
                chunkInfo.error = error instanceof Error ? error.message : 'Chunk upload failed';
                chunkInfo.retryCount++;

                logger.error('Chunk upload failed', {
                    filename: file.name,
                    chunkIndex: chunkInfo.index,
                    error: chunkInfo.error,
                    retryCount: chunkInfo.retryCount
                });

                updateQueueItem(queueItem.id, { chunks: chunkInfos });
                throw error;
            } finally {
                activeUploads--;
            }
        };

        // Process chunks with concurrency control
        for (let i = 0; i < chunks.length; i++) {
            while (activeUploads >= maxConcurrent) {
                await Promise.race(uploadPromises);
            }

            activeUploads++;
            const promise = uploadChunk(chunkInfos[i], chunks[i]);
            uploadPromises.push(promise);
        }

        // Wait for all chunks to complete
        await Promise.all(uploadPromises);

        // Combine chunks (simulate finalization)
        logger.info('All chunks uploaded, finalizing file', { filename: file.name });

        // This would typically call a backend endpoint to combine chunks
        const finalResult = {
            filename: file.name,
            url: `/uploads/${queueItem.id}/${file.name}`
        };

        logger.info('Chunked upload completed successfully', {
            filename: file.name,
            chunkCount: chunks.length
        });

        return finalResult;
    }, [updateQueueItem]);

    /**
     * Upload file as a whole (non-chunked)
     */
    const uploadFileWhole = useCallback(async (
        queueItem: UploadQueueItem,
        uploadOptions: AdvancedUploadOptions
    ) => {
        const { file } = queueItem;

        logger.info('Starting whole file upload', {
            filename: file.name,
            fileSize: file.size
        });

        try {
            // Create abort controller for this upload
            abortControllerRef.current = new AbortController();

            // Simulate progress tracking
            const progressInterval = setInterval(() => {
                const currentProgress = getQueueItem(queueItem.id)?.progress || 0;
                if (currentProgress < 90) {
                    const newProgress = Math.min(currentProgress + Math.random() * 20, 90);
                    updateQueueItem(queueItem.id, { progress: Math.round(newProgress) });

                    if (uploadOptions.onProgress) {
                        const speed = calculateSpeed(file.size, Date.now() - queueItem.startTime!);
                        const eta = calculateETA(file.size, currentProgress, speed);
                        uploadOptions.onProgress(newProgress, speed, eta);
                    }
                }
            }, 500);

            // Upload file (replace with actual API call)
            const result = await uploadFile(file, {
                signal: abortControllerRef.current.signal
            });

            clearInterval(progressInterval);

            logger.info('Whole file upload completed successfully', {
                filename: file.name,
                result
            });

            return result;

        } catch (error) {
            logger.error('Whole file upload failed', {
                filename: file.name,
                error: error instanceof Error ? error.message : 'Unknown error'
            });
            throw error;
        } finally {
            abortControllerRef.current = null;
        }
    }, [updateQueueItem, getQueueItem, calculateSpeed, calculateETA]);

    /**
     * Cancel current upload
     */
    const cancelUpload = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setIsUploading(false);
            setError(null);
            logger.info('Upload cancelled by user');
        }
    }, []);

    /**
     * Retry failed upload
     */
    const retryUpload = useCallback(async (queueItemId: string) => {
        const queueItem = getQueueItem(queueItemId);
        if (!queueItem || queueItem.status !== 'error') {
            logger.warn('Cannot retry upload - item not found or not in error state', { queueItemId });
            return;
        }

        logger.info('Retrying failed upload', {
            filename: queueItem.file.name,
            queueItemId
        });

        try {
            // Reset queue item status
            updateQueueItem(queueItemId, {
                status: 'pending',
                progress: 0,
                error: undefined,
                startTime: Date.now()
            });

            // Retry upload
            await uploadSingleFile(queueItem.file);

        } catch (error) {
            logger.error('Upload retry failed', {
                queueItemId,
                error: error instanceof Error ? error.message : 'Unknown error'
            });
            throw error;
        }
    }, [getQueueItem, updateQueueItem, uploadSingleFile]);

    return {
        // State
        isUploading,
        error,

        // Actions
        uploadSingleFile,
        uploadMultipleFiles,
        cancelUpload,
        retryUpload,

        // Queue management (re-export from useUploadQueue)
        addToQueue,
        updateQueueItem,
        removeFromQueue,
        getQueueItem,
        processQueue
    };
}
