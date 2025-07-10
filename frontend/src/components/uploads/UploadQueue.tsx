import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
    Trash2,
    RefreshCw,
    Pause,
    Play,
    FileText,
    AlertCircle,
    CheckCircle,
    Clock,
    Loader2,
    X
} from 'lucide-react';
import logger from '@/logger';
import { useUploadQueue } from '@/hooks/uploads';
import type { UploadQueueItem, UploadStatus } from '@/lib/api/types/upload';

/**
 * Configuration for the upload queue component
 */
export interface UploadQueueConfig {
    /** Maximum number of items to display */
    maxDisplayItems?: number;
    /** Show progress for each item */
    showProgress?: boolean;
    /** Show detailed information */
    showDetails?: boolean;
    /** Enable queue controls */
    enableControls?: boolean;
    /** Auto-hide completed items after delay (ms) */
    autoHideCompleted?: number;
    /** Custom CSS classes */
    className?: string;
    /** Compact display mode */
    compact?: boolean;
}

/**
 * Props for the UploadQueue component
 */
export interface UploadQueueProps extends UploadQueueConfig {
    /** Callback when item is retried */
    onRetry?: (item: UploadQueueItem) => void;
    /** Callback when item is removed */
    onRemove?: (item: UploadQueueItem) => void;
    /** Callback when queue is cleared */
    onClear?: () => void;
    /** Callback when queue is paused/resumed */
    onTogglePause?: (paused: boolean) => void;
}

/**
 * Individual queue item component
 */
interface QueueItemProps {
    item: UploadQueueItem;
    showProgress?: boolean;
    showDetails?: boolean;
    enableControls?: boolean;
    compact?: boolean;
    onRetry?: (item: UploadQueueItem) => void;
    onRemove?: (item: UploadQueueItem) => void;
}

const QueueItem: React.FC<QueueItemProps> = ({
    item,
    showProgress = true,
    showDetails = true,
    enableControls = true,
    compact = false,
    onRetry,
    onRemove
}) => {
    const formatFileSize = useCallback((bytes: number): string => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    }, []);

    const formatDuration = useCallback((ms: number): string => {
        if (ms < 1000) return '< 1s';
        const seconds = Math.floor(ms / 1000);
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    }, []);

    const getStatusIcon = useCallback(() => {
        switch (item.status) {
            case 'uploading':
                return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-success" />;
            case 'error':
                return <AlertCircle className="h-4 w-4 text-destructive" />;
            case 'cancelled':
                return <X className="h-4 w-4 text-muted-foreground" />;
            default:
                return <Clock className="h-4 w-4 text-muted-foreground" />;
        }
    }, [item.status]);

    const getStatusColor = useCallback(() => {
        switch (item.status) {
            case 'uploading':
                return 'border-primary/20 bg-primary/10';
            case 'completed':
                return 'border-success/20 bg-success/10';
            case 'error':
                return 'border-destructive/20 bg-destructive/10';
            case 'cancelled':
                return 'border-border bg-muted';
            default:
                return 'border-border bg-muted';
        }
    }, [item.status]);

    const getStatusBadgeVariant = useCallback(() => {
        switch (item.status) {
            case 'completed':
                return 'default' as const;
            case 'error':
                return 'destructive' as const;
            case 'uploading':
                return 'secondary' as const;
            default:
                return 'outline' as const;
        }
    }, [item.status]);

    const uploadDuration = item.completedAt && item.startedAt
        ? item.completedAt.getTime() - item.startedAt.getTime()
        : null;

    return (
        <div className={cn(
            "relative border rounded-lg p-3 transition-all",
            getStatusColor(),
            compact ? "py-2" : "py-3"
        )}>
            <div className="flex items-center gap-3">
                {/* File Icon */}
                <div className="flex-shrink-0">
                    <FileText className="h-6 w-6 text-muted-foreground" />
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <p className={cn(
                            "font-medium text-foreground truncate",
                            compact ? "text-sm" : "text-base"
                        )}>
                            {item.file.name}
                        </p>
                        {getStatusIcon()}
                    </div>

                    {/* File Details */}
                    {showDetails && !compact && (
                        <div className="mt-1 space-y-1">
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                <span>{formatFileSize(item.file.size)}</span>
                                <span>{item.file.type}</span>
                                {item.priority !== 5 && (
                                    <span>Priority: {item.priority}</span>
                                )}
                                {uploadDuration && (
                                    <span>Duration: {formatDuration(uploadDuration)}</span>
                                )}
                            </div>

                            {/* Error Message */}
                            {item.error && (
                                <div className="flex items-center gap-1 text-destructive-foreground">
                                    <AlertCircle className="h-3 w-3" />
                                    <span className="text-xs">{item.error.message}</span>
                                </div>
                            )}

                            {/* Retry Information */}
                            {item.retryCount > 0 && (
                                <div className="text-xs text-muted-foreground">
                                    Retry {item.retryCount}/{item.maxRetries}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Progress */}
                    {showProgress && item.status === 'uploading' && (
                        <div className="mt-2 space-y-1">
                            <Progress value={item.progress.percentage} className="h-2" />
                            <div className="flex justify-between text-xs text-muted-foreground">
                                <span>{item.progress.percentage.toFixed(1)}%</span>
                                <span>
                                    {formatFileSize(item.progress.bytesTransferred)} / {formatFileSize(item.progress.totalBytes)}
                                </span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Status Badge */}
                <div className="flex-shrink-0">
                    <Badge variant={getStatusBadgeVariant()}>
                        {item.status}
                    </Badge>
                </div>

                {/* Controls */}
                {enableControls && (
                    <div className="flex-shrink-0 flex items-center gap-1">
                        {/* Retry Button */}
                        {item.status === 'error' && onRetry && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onRetry(item)}
                                className="h-8 w-8 p-0"
                                title="Retry upload"
                            >
                                <RefreshCw className="h-4 w-4" />
                            </Button>
                        )}

                        {/* Remove Button */}
                        {(item.status !== 'uploading') && onRemove && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onRemove(item)}
                                className="h-8 w-8 p-0"
                                title="Remove from queue"
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

/**
 * Upload Queue Component
 * 
 * Displays and manages the upload queue with progress tracking,
 * retry functionality, and queue controls.
 */
export const UploadQueue: React.FC<UploadQueueProps> = ({
    maxDisplayItems = 10,
    showProgress = true,
    showDetails = true,
    enableControls = true,
    autoHideCompleted,
    className,
    compact = false,
    onRetry,
    onRemove,
    onClear,
    onTogglePause
}) => {
    const [isPaused, setIsPaused] = useState(false);

    const {
        queue,
        isProcessing,
        removeFromQueue,
        clearQueue,
        pauseQueueItem,
        resumeQueueItem,
        retryFailedItems,
        getQueueStats,
        processQueue
    } = useUploadQueue({
        maxConcurrent: 3,
        autoRetry: true,
        maxRetries: 3
    });

    const stats = getQueueStats();
    const displayItems = queue.slice(0, maxDisplayItems);

    const handleRetry = useCallback(async (item: UploadQueueItem) => {
        try {
            logger.info('Retrying upload', { fileId: item.id, fileName: item.file.name });

            // Resume the specific queue item if it's in error state
            if (item.status === 'error') {
                resumeQueueItem(item.id);
            }

            // Trigger retry for failed items
            retryFailedItems();

            onRetry?.(item);
        } catch (error) {
            logger.error('Failed to retry upload', {
                fileId: item.id,
                error: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    }, [resumeQueueItem, retryFailedItems, onRetry]);

    const handleRemove = useCallback((item: UploadQueueItem) => {
        logger.info('Removing item from queue', { fileId: item.id, fileName: item.file.name });
        removeFromQueue(item.id);
        onRemove?.(item);
    }, [removeFromQueue, onRemove]);

    const handleClear = useCallback(() => {
        logger.info('Clearing upload queue');
        clearQueue();
        onClear?.();
    }, [clearQueue, onClear]);

    const handleTogglePause = useCallback(() => {
        const newPausedState = !isPaused;
        setIsPaused(newPausedState);

        if (newPausedState) {
            // Pause all pending/uploading items
            queue.forEach(item => {
                if (item.status === 'pending' || item.status === 'uploading') {
                    pauseQueueItem(item.id);
                }
            });
            logger.info('Upload queue paused');
        } else {
            // Resume all paused items
            queue.forEach(item => {
                if (item.status === 'cancelled') { // Using cancelled as paused state
                    resumeQueueItem(item.id);
                }
            });
            // Restart queue processing
            processQueue();
            logger.info('Upload queue resumed');
        }

        onTogglePause?.(newPausedState);
    }, [isPaused, queue, pauseQueueItem, resumeQueueItem, processQueue, onTogglePause]);

    // Auto-hide completed items
    React.useEffect(() => {
        if (!autoHideCompleted) return;

        const completedItems = queue.filter(item => item.status === 'completed');
        if (completedItems.length === 0) return;

        const timeouts = completedItems.map(item =>
            setTimeout(() => {
                removeFromQueue(item.id);
            }, autoHideCompleted)
        );

        return () => {
            timeouts.forEach(timeout => clearTimeout(timeout));
        };
    }, [queue, autoHideCompleted, removeFromQueue]);

    if (queue.length === 0) {
        return (
            <div className={cn(
                "text-center py-8 text-muted-foreground",
                className
            )}>
                <FileText className="h-12 w-12 mx-auto mb-4 text-muted" />
                <p className="text-sm">No files in upload queue</p>
            </div>
        );
    }

    return (
        <div className={cn("space-y-4", className)}>
            {/* Queue Header */}
            <div className="flex items-center justify-between">
                <div className="space-y-1">
                    <h3 className="text-lg font-semibold text-foreground">
                        Upload Queue
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>{stats.total} total</span>
                        <span>{stats.pending} pending</span>
                        <span>{stats.uploading} uploading</span>
                        <span>{stats.completed} completed</span>
                        {stats.error > 0 && (
                            <span className="text-destructive-foreground">{stats.error} failed</span>
                        )}
                    </div>
                </div>

                {/* Queue Controls */}
                {enableControls && (
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleTogglePause}
                            disabled={stats.uploading === 0 && stats.pending === 0}
                        >
                            {isPaused ? (
                                <>
                                    <Play className="h-4 w-4 mr-2" />
                                    Resume
                                </>
                            ) : (
                                <>
                                    <Pause className="h-4 w-4 mr-2" />
                                    Pause
                                </>
                            )}
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleClear}
                            disabled={isProcessing}
                        >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Clear
                        </Button>
                    </div>
                )}
            </div>

            {/* Queue Items */}
            <div className="space-y-2">
                {displayItems.map((item) => (
                    <QueueItem
                        key={item.id}
                        item={item}
                        showProgress={showProgress}
                        showDetails={showDetails}
                        enableControls={enableControls}
                        compact={compact}
                        onRetry={handleRetry}
                        onRemove={handleRemove}
                    />
                ))}

                {/* Show More Indicator */}
                {queue.length > maxDisplayItems && (
                    <div className="text-center py-2 text-sm text-muted-foreground">
                        ... and {queue.length - maxDisplayItems} more items
                    </div>
                )}
            </div>
        </div>
    );
};

export default UploadQueue;
