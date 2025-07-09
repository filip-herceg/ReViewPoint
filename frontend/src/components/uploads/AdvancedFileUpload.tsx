import React, { useCallback, useRef, useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
    Upload,
    X,
    FileText,
    AlertCircle,
    CheckCircle,
    Clock,
    Loader2,
    Plus
} from 'lucide-react';
import logger from '@/logger';
import {
    useAdvancedFileUpload,
    useFileValidation,
    useUploadProgress
} from '@/hooks/uploads';
import type {
    FileValidationResult,
    UploadQueueItem,
    UploadProgress
} from '@/lib/api/types/upload';

/**
 * Configuration for the advanced file upload component
 */
export interface AdvancedFileUploadConfig {
    /** Maximum file size in bytes */
    maxSize?: number;
    /** Allowed file types (MIME types) */
    accept?: string[];
    /** Maximum number of files */
    maxFiles?: number;
    /** Enable multiple file selection */
    multiple?: boolean;
    /** Enable drag and drop */
    dragAndDrop?: boolean;
    /** Show upload progress */
    showProgress?: boolean;
    /** Show file validation */
    showValidation?: boolean;
    /** Auto-start uploads */
    autoUpload?: boolean;
    /** Custom CSS classes */
    className?: string;
    /** Custom styling for different states */
    variant?: 'default' | 'compact' | 'minimal';
}

/**
 * Props for the AdvancedFileUpload component
 */
export interface AdvancedFileUploadProps extends AdvancedFileUploadConfig {
    /** Callback when files are selected */
    onFilesSelected?: (files: File[]) => void;
    /** Callback when upload starts */
    onUploadStart?: (item: UploadQueueItem) => void;
    /** Callback when upload progresses */
    onUploadProgress?: (item: UploadQueueItem) => void;
    /** Callback when upload completes */
    onUploadComplete?: (item: UploadQueueItem) => void;
    /** Callback when upload fails */
    onUploadError?: (item: UploadQueueItem, error: Error) => void;
    /** Callback when files are removed */
    onFilesRemoved?: (fileIds: string[]) => void;
    /** Custom validation rules */
    customValidation?: (file: File) => Promise<FileValidationResult>;
    /** Disabled state */
    disabled?: boolean;
    /** Loading state */
    loading?: boolean;
}

/**
 * File item display component
 */
interface FileItemProps {
    file: File;
    validation?: FileValidationResult;
    progress?: number;
    status?: 'pending' | 'uploading' | 'completed' | 'error';
    onRemove?: () => void;
    showValidation?: boolean;
    showProgress?: boolean;
}

const FileItem: React.FC<FileItemProps> = ({
    file,
    validation,
    progress = 0,
    status = 'pending',
    onRemove,
    showValidation = true,
    showProgress = true
}) => {
    const formatFileSize = useCallback((bytes: number): string => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    }, []);

    const getStatusIcon = useCallback(() => {
        switch (status) {
            case 'uploading':
                return <Loader2 className="h-4 w-4 animate-spin" />;
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'error':
                return <AlertCircle className="h-4 w-4 text-red-500" />;
            default:
                return <Clock className="h-4 w-4 text-gray-400" />;
        }
    }, [status]);

    const getStatusColor = useCallback(() => {
        switch (status) {
            case 'uploading':
                return 'bg-blue-50 border-blue-200';
            case 'completed':
                return 'bg-green-50 border-green-200';
            case 'error':
                return 'bg-red-50 border-red-200';
            default:
                return 'bg-gray-50 border-gray-200';
        }
    }, [status]);

    return (
        <div className={cn(
            "relative flex items-center gap-3 p-3 rounded-lg border-2 border-dashed transition-all",
            getStatusColor()
        )}>
            {/* File Icon */}
            <div className="flex-shrink-0">
                <FileText className="h-8 w-8 text-gray-400" />
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                    </p>
                    {getStatusIcon()}
                </div>

                <p className="text-xs text-gray-500">
                    {formatFileSize(file.size)}
                </p>

                {/* Validation Messages */}
                {showValidation && validation && (
                    <div className="mt-1 space-y-1">
                        {validation.errors.map((error, index) => (
                            <div key={index} className="flex items-center gap-1">
                                <AlertCircle className="h-3 w-3 text-red-500" />
                                <span className="text-xs text-red-600">{error.message}</span>
                            </div>
                        ))}
                        {validation.warnings.map((warning, index) => (
                            <div key={index} className="flex items-center gap-1">
                                <AlertCircle className="h-3 w-3 text-yellow-500" />
                                <span className="text-xs text-yellow-600">{warning.message}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Progress Bar */}
                {showProgress && status === 'uploading' && (
                    <div className="mt-2">
                        <Progress value={progress} className="h-2" />
                        <p className="text-xs text-gray-500 mt-1">
                            {progress.toFixed(1)}% uploaded
                        </p>
                    </div>
                )}
            </div>

            {/* Status Badge */}
            <div className="flex-shrink-0">
                <Badge variant={
                    status === 'completed' ? 'default' :
                        status === 'error' ? 'destructive' :
                            status === 'uploading' ? 'secondary' : 'outline'
                }>
                    {status}
                </Badge>
            </div>

            {/* Remove Button */}
            {onRemove && status !== 'uploading' && (
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onRemove}
                    className="flex-shrink-0 h-8 w-8 p-0"
                >
                    <X className="h-4 w-4" />
                </Button>
            )}
        </div>
    );
};

/**
 * Advanced File Upload Component
 * 
 * A comprehensive file upload component with drag-and-drop support,
 * validation, progress tracking, and queue management.
 */
export const AdvancedFileUpload: React.FC<AdvancedFileUploadProps> = ({
    maxSize = 10 * 1024 * 1024, // 10MB default
    accept = ['application/pdf'],
    maxFiles = 10,
    multiple = true,
    dragAndDrop = true,
    showProgress = true,
    showValidation = true,
    autoUpload = false,
    className,
    variant = 'default',
    onFilesSelected,
    onUploadStart,
    onUploadProgress,
    onUploadComplete,
    onUploadError,
    onFilesRemoved,
    customValidation,
    disabled = false,
    loading = false
}) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [isDragOver, setIsDragOver] = useState(false);
    const [fileValidations, setFileValidations] = useState<Map<string, FileValidationResult>>(new Map());

    // Hooks
    const {
        uploadSingleFile,
        uploadMultipleFiles,
        isUploading,
        error: uploadError,
        cancelUpload,
        retryUpload
    } = useAdvancedFileUpload({
        enableChunked: true,
        chunkSize: 1024 * 1024, // 1MB chunks
        maxConcurrentChunks: 3,
        enableBackground: false,
        priority: 5
    });

    const { validateFile } = useFileValidation({
        maxSize,
        allowedTypes: accept,
        maxFiles,
        enableContentValidation: true,
        enableSecurityScan: true
    });

    const {
        progressState,
        initializeFileProgress,
        updateChunkProgress,
        getFileProgress,
        startTracking,
        stopTracking,
        resetProgress,
        formatBytes,
        formatSpeed,
        formatDuration
    } = useUploadProgress();

    /**
     * Generate unique file key
     */
    const getFileKey = useCallback((file: File): string => {
        return `${file.name}-${file.size}-${file.lastModified}`;
    }, []);

    /**
     * Validate selected files
     */
    const validateFiles = useCallback(async (files: File[]) => {
        const validations = new Map<string, FileValidationResult>();

        for (const file of files) {
            try {
                let validation = await validateFile(file);

                // Apply custom validation if provided
                if (customValidation) {
                    const customResult = await customValidation(file);
                    validation = {
                        isValid: validation.isValid && customResult.isValid,
                        errors: [...validation.errors, ...customResult.errors],
                        warnings: [...validation.warnings, ...customResult.warnings],
                        metadata: { ...validation.metadata, ...customResult.metadata }
                    };
                }

                validations.set(getFileKey(file), validation);
            } catch (error) {
                logger.error('File validation failed', {
                    error,
                    fileName: file.name
                });

                validations.set(getFileKey(file), {
                    isValid: false,
                    errors: [{
                        code: 'VALIDATION_ERROR',
                        message: 'Validation failed',
                        field: 'validation',
                        severity: 'error'
                    }],
                    warnings: []
                });
            }
        }

        setFileValidations(validations);
        return validations;
    }, [validateFile, customValidation, getFileKey]);

    /**
     * Handle file selection
     */
    const handleFileSelection = useCallback(async (files: File[]) => {
        if (disabled || loading) return;

        // Check file count limit
        if (selectedFiles.length + files.length > maxFiles) {
            logger.warn('File count limit exceeded', {
                current: selectedFiles.length,
                adding: files.length,
                limit: maxFiles
            });
            return;
        }

        logger.info('Files selected', { count: files.length });

        // Validate files
        await validateFiles(files);

        // Add to selected files
        setSelectedFiles(prev => [...prev, ...files]);

        // Notify parent
        onFilesSelected?.(files);

        // Auto-upload if enabled
        if (autoUpload) {
            handleUpload(files);
        }
    }, [disabled, loading, selectedFiles.length, maxFiles, validateFiles, onFilesSelected, autoUpload]);

    /**
     * Handle file input change
     */
    const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files || []);
        if (files.length > 0) {
            handleFileSelection(files);
        }
        // Reset input value to allow selecting the same file again
        event.target.value = '';
    }, [handleFileSelection]);

    /**
     * Handle drag and drop events
     */
    const handleDragOver = useCallback((event: React.DragEvent) => {
        if (!dragAndDrop || disabled || loading) return;

        event.preventDefault();
        event.stopPropagation();
        setIsDragOver(true);
    }, [dragAndDrop, disabled, loading]);

    const handleDragLeave = useCallback((event: React.DragEvent) => {
        if (!dragAndDrop) return;

        event.preventDefault();
        event.stopPropagation();
        setIsDragOver(false);
    }, [dragAndDrop]);

    const handleDrop = useCallback((event: React.DragEvent) => {
        if (!dragAndDrop || disabled || loading) return;

        event.preventDefault();
        event.stopPropagation();
        setIsDragOver(false);

        const files = Array.from(event.dataTransfer.files);
        if (files.length > 0) {
            handleFileSelection(files);
        }
    }, [dragAndDrop, disabled, loading, handleFileSelection]);

    /**
     * Handle file removal
     */
    const handleRemoveFile = useCallback((file: File) => {
        const fileKey = getFileKey(file);

        setSelectedFiles(prev => prev.filter(f => getFileKey(f) !== fileKey));
        setFileValidations(prev => {
            const newValidations = new Map(prev);
            newValidations.delete(fileKey);
            return newValidations;
        });

        onFilesRemoved?.([fileKey]);

        logger.info('File removed', { fileName: file.name });
    }, [getFileKey, onFilesRemoved]);

    /**
     * Handle upload
     */
    const handleUpload = useCallback(async (filesToUpload?: File[]) => {
        const files = filesToUpload || selectedFiles;
        const validFiles = files.filter(file => {
            const validation = fileValidations.get(getFileKey(file));
            return validation?.isValid;
        });

        if (validFiles.length === 0) {
            logger.warn('No valid files to upload');
            return;
        }

        try {
            startTracking();

            if (validFiles.length === 1) {
                const file = validFiles[0];
                const fileKey = getFileKey(file);

                // Initialize progress tracking
                initializeFileProgress(fileKey, file.size, 1);

                const queueItem = await uploadSingleFile(file, {
                    onProgress: (progress: number, speed: number, eta: number) => {
                        // Update chunk progress for better tracking
                        updateChunkProgress(fileKey, 0, {
                            index: 0,
                            bytesTransferred: Math.round(file.size * progress / 100),
                            totalBytes: file.size,
                            isComplete: progress >= 100
                        });

                        // Update queue item with progress
                        const progressObj: UploadProgress = {
                            bytesTransferred: Math.round(file.size * progress / 100),
                            totalBytes: file.size,
                            percentage: progress,
                            chunksCompleted: progress >= 100 ? 1 : 0,
                            totalChunks: 1,
                            isComplete: progress >= 100,
                            startTime: Date.now(),
                            endTime: progress >= 100 ? Date.now() : null
                        };

                        const updatedItem: UploadQueueItem = {
                            ...queueItem,
                            progress: progressObj,
                            status: progress >= 100 ? 'completed' : 'uploading'
                        };
                        onUploadProgress?.(updatedItem);
                    }
                });
                onUploadStart?.(queueItem);
            } else {
                // Initialize progress tracking for multiple files
                validFiles.forEach(file => {
                    const fileKey = getFileKey(file);
                    initializeFileProgress(fileKey, file.size, 1);
                });

                const queueItems = await uploadMultipleFiles(validFiles, {
                    onProgress: (progress: number, speed: number, eta: number) => {
                        // For multiple files, this is overall progress
                        logger.debug('Multiple files upload progress', { progress, speed, eta });
                    }
                });
                queueItems.forEach(item => onUploadStart?.(item));
            }
        } catch (error) {
            logger.error('Upload failed', { error });
            stopTracking();
            // onUploadError will be called by the upload hook
        }
    }, [
        selectedFiles,
        fileValidations,
        getFileKey,
        uploadSingleFile,
        uploadMultipleFiles,
        onUploadStart,
        onUploadProgress,
        startTracking,
        stopTracking,
        initializeFileProgress,
        updateChunkProgress
    ]);

    /**
     * Open file picker
     */
    const openFilePicker = useCallback(() => {
        if (disabled || loading) return;
        fileInputRef.current?.click();
    }, [disabled, loading]);

    /**
     * Clear all files
     */
    const clearFiles = useCallback(() => {
        setSelectedFiles([]);
        setFileValidations(new Map());
        onFilesRemoved?.(selectedFiles.map(getFileKey));
    }, [selectedFiles, getFileKey, onFilesRemoved]);

    // Component styling based on variant
    const getDropzoneClasses = useCallback(() => {
        const baseClasses = "relative border-2 border-dashed rounded-lg transition-all duration-200";

        if (disabled || loading) {
            return cn(baseClasses, "border-gray-200 bg-gray-50 cursor-not-allowed");
        }

        if (isDragOver) {
            return cn(baseClasses, "border-blue-400 bg-blue-50");
        }

        switch (variant) {
            case 'compact':
                return cn(baseClasses, "border-gray-300 hover:border-gray-400 cursor-pointer p-4");
            case 'minimal':
                return cn(baseClasses, "border-gray-200 hover:border-gray-300 cursor-pointer p-2");
            default:
                return cn(baseClasses, "border-gray-300 hover:border-gray-400 cursor-pointer p-8");
        }
    }, [disabled, loading, isDragOver, variant]);

    const hasValidFiles = selectedFiles.some(file =>
        fileValidations.get(getFileKey(file))?.isValid
    );

    const hasInvalidFiles = selectedFiles.some(file =>
        !fileValidations.get(getFileKey(file))?.isValid
    );

    return (
        <div className={cn("space-y-4", className)}>
            {/* File input */}
            <input
                ref={fileInputRef}
                type="file"
                multiple={multiple}
                accept={accept.join(',')}
                onChange={handleInputChange}
                className="hidden"
                disabled={disabled || loading}
            />

            {/* Drop zone */}
            <div
                className={getDropzoneClasses()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={openFilePicker}
            >
                <div className="text-center">
                    <Upload className={cn(
                        "mx-auto h-12 w-12 mb-4",
                        disabled || loading ? "text-gray-300" : "text-gray-400"
                    )} />

                    <div className="space-y-2">
                        <p className={cn(
                            "text-sm font-medium",
                            disabled || loading ? "text-gray-400" : "text-gray-700"
                        )}>
                            {dragAndDrop ? 'Drag and drop files here, or click to browse' : 'Click to browse files'}
                        </p>

                        <p className="text-xs text-gray-500">
                            Supports {accept.join(', ')} • Max {maxFiles} files • {(maxSize / 1024 / 1024).toFixed(0)}MB per file
                        </p>
                    </div>
                </div>

                {loading && (
                    <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
                        <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                    </div>
                )}
            </div>

            {/* Selected files list */}
            {selectedFiles.length > 0 && (
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-gray-900">
                            Selected Files ({selectedFiles.length})
                        </h3>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={clearFiles}
                            disabled={disabled || loading || isUploading}
                        >
                            Clear All
                        </Button>
                    </div>

                    <div className="space-y-2">
                        {selectedFiles.map((file) => {
                            const fileKey = getFileKey(file);
                            const validation = fileValidations.get(fileKey);
                            const fileProgress = progressState.fileProgress.get(fileKey);

                            return (
                                <FileItem
                                    key={fileKey}
                                    file={file}
                                    validation={validation}
                                    progress={fileProgress?.percentage || 0}
                                    status={fileProgress?.isComplete ? 'completed' :
                                        fileProgress ? 'uploading' :
                                            validation?.isValid === false ? 'error' : 'pending'}
                                    onRemove={() => handleRemoveFile(file)}
                                    showValidation={showValidation}
                                    showProgress={showProgress}
                                />
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Upload controls */}
            {selectedFiles.length > 0 && !autoUpload && (
                <div className="flex items-center justify-between pt-4 border-t">
                    <div className="text-sm text-gray-600">
                        {hasValidFiles && (
                            <span className="text-green-600">
                                {selectedFiles.filter(f => fileValidations.get(getFileKey(f))?.isValid).length} valid files
                            </span>
                        )}
                        {hasValidFiles && hasInvalidFiles && <span className="mx-2">•</span>}
                        {hasInvalidFiles && (
                            <span className="text-red-600">
                                {selectedFiles.filter(f => !fileValidations.get(getFileKey(f))?.isValid).length} invalid files
                            </span>
                        )}
                    </div>

                    <Button
                        onClick={() => handleUpload()}
                        disabled={!hasValidFiles || disabled || loading || isUploading}
                        className="min-w-[120px]"
                    >
                        {isUploading ? (
                            <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Uploading...
                            </>
                        ) : (
                            <>
                                <Plus className="h-4 w-4 mr-2" />
                                Upload Files
                            </>
                        )}
                    </Button>
                </div>
            )}

            {/* Overall progress */}
            {showProgress && progressState.isTracking && (
                <div className="space-y-2 pt-4 border-t">
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Overall Progress</span>
                        <span className="text-gray-900 font-medium">
                            {progressState.overallProgress.percentage.toFixed(1)}%
                        </span>
                    </div>

                    <Progress value={progressState.overallProgress.percentage} className="h-2" />

                    <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>
                            Speed: {progressState.uploadSpeed > 0 ?
                                `${(progressState.uploadSpeed / 1024 / 1024).toFixed(1)} MB/s` :
                                'Calculating...'
                            }
                        </span>
                        <span>
                            ETA: {progressState.estimatedTimeRemaining ?
                                `${Math.round(progressState.estimatedTimeRemaining)}s` :
                                'Calculating...'
                            }
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdvancedFileUpload;
