import { useState, useCallback, useEffect, useRef } from 'react';
import logger from '@/logger';
import type {
    ChunkProgress,
    UploadProgress,
    UploadQueueItem
} from '@/lib/api/types/upload';

/**
 * Configuration for upload progress tracking
 */
export interface UploadProgressConfig {
    /** Update interval for progress calculations in milliseconds */
    updateInterval: number;
    /** Number of samples to keep for speed calculation */
    speedSamples: number;
    /** Minimum time to wait before calculating ETA (milliseconds) */
    minTimeForEta: number;
}

/**
 * Progress tracking state
 */
export interface ProgressState {
    /** Current upload progress for each file */
    fileProgress: Map<string, UploadProgress>;
    /** Overall progress across all files */
    overallProgress: UploadProgress;
    /** Upload speed in bytes per second */
    uploadSpeed: number;
    /** Estimated time remaining in seconds */
    estimatedTimeRemaining: number | null;
    /** Whether progress tracking is active */
    isTracking: boolean;
}

/**
 * Progress sample for speed calculation
 */
interface ProgressSample {
    timestamp: number;
    bytesTransferred: number;
}

/**
 * Hook for tracking upload progress and calculating ETAs
 */
export function useUploadProgress(config: Partial<UploadProgressConfig> = {}) {
    const [progressState, setProgressState] = useState<ProgressState>({
        fileProgress: new Map(),
        overallProgress: {
            bytesTransferred: 0,
            totalBytes: 0,
            percentage: 0,
            chunksCompleted: 0,
            totalChunks: 0,
            isComplete: false,
            startTime: null,
            endTime: null
        },
        uploadSpeed: 0,
        estimatedTimeRemaining: null,
        isTracking: false
    });

    const defaultConfig: UploadProgressConfig = {
        updateInterval: config.updateInterval || 1000,
        speedSamples: config.speedSamples || 10,
        minTimeForEta: config.minTimeForEta || 3000
    };

    const progressSamples = useRef<ProgressSample[]>([]);
    const updateInterval = useRef<NodeJS.Timeout | null>(null);
    const startTime = useRef<number | null>(null);

    /**
     * Initialize progress tracking for a file
     */
    const initializeFileProgress = useCallback((fileId: string, totalBytes: number, totalChunks: number) => {
        logger.debug('Initializing progress tracking', { fileId, totalBytes, totalChunks });

        setProgressState(prev => {
            const newFileProgress = new Map(prev.fileProgress);
            newFileProgress.set(fileId, {
                bytesTransferred: 0,
                totalBytes,
                percentage: 0,
                chunksCompleted: 0,
                totalChunks,
                isComplete: false,
                startTime: Date.now(),
                endTime: null
            });

            return {
                ...prev,
                fileProgress: newFileProgress,
                isTracking: true
            };
        });

        if (!startTime.current) {
            startTime.current = Date.now();
        }
    }, []);

    /**
     * Update progress for a specific file chunk
     */
    const updateChunkProgress = useCallback((fileId: string, chunkIndex: number, chunkProgress: ChunkProgress) => {
        setProgressState(prev => {
            const newFileProgress = new Map(prev.fileProgress);
            const fileProgress = newFileProgress.get(fileId);

            if (!fileProgress) {
                logger.warn('File progress not found for update', { fileId });
                return prev;
            }

            // Calculate new progress
            const chunkSize = chunkProgress.totalBytes;
            const chunkBytesTransferred = chunkProgress.bytesTransferred;
            const previousChunkBytes = (fileProgress.bytesTransferred / fileProgress.totalChunks) * chunkIndex;
            const newBytesTransferred = previousChunkBytes + chunkBytesTransferred;

            const updatedFileProgress: UploadProgress = {
                ...fileProgress,
                bytesTransferred: newBytesTransferred,
                percentage: (newBytesTransferred / fileProgress.totalBytes) * 100,
                chunksCompleted: chunkProgress.isComplete ? fileProgress.chunksCompleted + 1 : fileProgress.chunksCompleted,
                isComplete: fileProgress.chunksCompleted + (chunkProgress.isComplete ? 1 : 0) === fileProgress.totalChunks
            };

            if (updatedFileProgress.isComplete && !updatedFileProgress.endTime) {
                updatedFileProgress.endTime = Date.now();
                logger.info('File upload completed', {
                    fileId,
                    duration: updatedFileProgress.endTime - (updatedFileProgress.startTime || 0),
                    totalBytes: updatedFileProgress.totalBytes
                });
            }

            newFileProgress.set(fileId, updatedFileProgress);

            return {
                ...prev,
                fileProgress: newFileProgress
            };
        });
    }, []);

    /**
     * Calculate overall progress across all files
     */
    const calculateOverallProgress = useCallback(() => {
        setProgressState(prev => {
            const files = Array.from(prev.fileProgress.values());

            if (files.length === 0) {
                return prev;
            }

            const totalBytes = files.reduce((sum, file) => sum + file.totalBytes, 0);
            const bytesTransferred = files.reduce((sum, file) => sum + file.bytesTransferred, 0);
            const totalChunks = files.reduce((sum, file) => sum + file.totalChunks, 0);
            const chunksCompleted = files.reduce((sum, file) => sum + file.chunksCompleted, 0);
            const allComplete = files.every(file => file.isComplete);

            const overallProgress: UploadProgress = {
                bytesTransferred,
                totalBytes,
                percentage: totalBytes > 0 ? (bytesTransferred / totalBytes) * 100 : 0,
                chunksCompleted,
                totalChunks,
                isComplete: allComplete,
                startTime: startTime.current,
                endTime: allComplete ? Date.now() : null
            };

            return {
                ...prev,
                overallProgress
            };
        });
    }, []);

    /**
     * Calculate upload speed and ETA
     */
    const calculateSpeedAndEta = useCallback(() => {
        const now = Date.now();
        const currentBytes = progressState.overallProgress.bytesTransferred;

        // Add current sample
        progressSamples.current.push({
            timestamp: now,
            bytesTransferred: currentBytes
        });

        // Keep only recent samples
        progressSamples.current = progressSamples.current
            .filter(sample => now - sample.timestamp < defaultConfig.speedSamples * defaultConfig.updateInterval);

        if (progressSamples.current.length < 2) {
            return;
        }

        // Calculate speed
        const oldestSample = progressSamples.current[0];
        const newestSample = progressSamples.current[progressSamples.current.length - 1];
        const timeDiff = (newestSample.timestamp - oldestSample.timestamp) / 1000; // seconds
        const bytesDiff = newestSample.bytesTransferred - oldestSample.bytesTransferred;
        const speed = timeDiff > 0 ? bytesDiff / timeDiff : 0;

        // Calculate ETA
        let eta: number | null = null;
        const remainingBytes = progressState.overallProgress.totalBytes - currentBytes;

        if (speed > 0 && remainingBytes > 0 && startTime.current) {
            const elapsedTime = (now - startTime.current) / 1000;
            if (elapsedTime >= defaultConfig.minTimeForEta / 1000) {
                eta = remainingBytes / speed;
            }
        }

        setProgressState(prev => ({
            ...prev,
            uploadSpeed: Math.max(0, speed),
            estimatedTimeRemaining: eta
        }));

        logger.debug('Speed and ETA calculated', {
            speed: Math.round(speed),
            eta: eta ? Math.round(eta) : null,
            remainingBytes,
            samplesCount: progressSamples.current.length
        });
    }, [progressState.overallProgress, defaultConfig]);

    /**
     * Start progress tracking
     */
    const startTracking = useCallback(() => {
        if (updateInterval.current) {
            clearInterval(updateInterval.current);
        }

        updateInterval.current = setInterval(() => {
            calculateOverallProgress();
            calculateSpeedAndEta();
        }, defaultConfig.updateInterval);

        setProgressState(prev => ({
            ...prev,
            isTracking: true
        }));

        logger.info('Progress tracking started', { updateInterval: defaultConfig.updateInterval });
    }, [calculateOverallProgress, calculateSpeedAndEta, defaultConfig.updateInterval]);

    /**
     * Stop progress tracking
     */
    const stopTracking = useCallback(() => {
        if (updateInterval.current) {
            clearInterval(updateInterval.current);
            updateInterval.current = null;
        }

        setProgressState(prev => ({
            ...prev,
            isTracking: false
        }));

        logger.info('Progress tracking stopped');
    }, []);

    /**
     * Reset all progress tracking
     */
    const resetProgress = useCallback(() => {
        stopTracking();
        progressSamples.current = [];
        startTime.current = null;

        setProgressState({
            fileProgress: new Map(),
            overallProgress: {
                bytesTransferred: 0,
                totalBytes: 0,
                percentage: 0,
                chunksCompleted: 0,
                totalChunks: 0,
                isComplete: false,
                startTime: null,
                endTime: null
            },
            uploadSpeed: 0,
            estimatedTimeRemaining: null,
            isTracking: false
        });

        logger.info('Progress tracking reset');
    }, [stopTracking]);

    /**
     * Get progress for a specific file
     */
    const getFileProgress = useCallback((fileId: string): UploadProgress | null => {
        return progressState.fileProgress.get(fileId) || null;
    }, [progressState.fileProgress]);

    /**
     * Get progress for all files
     */
    const getAllFileProgress = useCallback(() => {
        return Array.from(progressState.fileProgress.entries()).map(([fileId, progress]) => ({
            fileId,
            progress
        }));
    }, [progressState.fileProgress]);

    /**
     * Remove file from progress tracking
     */
    const removeFileProgress = useCallback((fileId: string) => {
        setProgressState(prev => {
            const newFileProgress = new Map(prev.fileProgress);
            newFileProgress.delete(fileId);

            return {
                ...prev,
                fileProgress: newFileProgress
            };
        });

        logger.debug('File progress removed', { fileId });
    }, []);

    /**
     * Format time duration
     */
    const formatDuration = useCallback((seconds: number): string => {
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.round(seconds % 60);
            return `${minutes}m ${remainingSeconds}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }, []);

    /**
     * Format bytes
     */
    const formatBytes = useCallback((bytes: number): string => {
        if (bytes === 0) return '0 B';

        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    }, []);

    /**
     * Format upload speed
     */
    const formatSpeed = useCallback((bytesPerSecond: number): string => {
        return `${formatBytes(bytesPerSecond)}/s`;
    }, [formatBytes]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (updateInterval.current) {
                clearInterval(updateInterval.current);
            }
        };
    }, []);

    return {
        // State
        progressState,

        // File progress management
        initializeFileProgress,
        updateChunkProgress,
        getFileProgress,
        getAllFileProgress,
        removeFileProgress,

        // Overall progress
        calculateOverallProgress,

        // Tracking control
        startTracking,
        stopTracking,
        resetProgress,

        // Formatting utilities
        formatDuration,
        formatBytes,
        formatSpeed,

        // Computed values
        isTracking: progressState.isTracking,
        overallProgress: progressState.overallProgress,
        uploadSpeed: progressState.uploadSpeed,
        estimatedTimeRemaining: progressState.estimatedTimeRemaining
    };
}

export type UseUploadProgressReturn = ReturnType<typeof useUploadProgress>;
