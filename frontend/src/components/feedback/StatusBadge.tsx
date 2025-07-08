/**
 * Status Badge Component
 * Displays status indicators with consistent styling
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
    CheckCircle,
    Clock,
    AlertCircle,
    XCircle,
    Upload,
    Eye,
    RefreshCw,
    Pause
} from 'lucide-react';
import logger from '@/logger';

// Status type definitions
export type StatusType =
    | 'success'
    | 'pending'
    | 'warning'
    | 'error'
    | 'info'
    | 'uploading'
    | 'processing'
    | 'paused'
    | 'reviewing'
    | 'completed'
    | 'failed';

// Upload-specific status types
export type UploadStatus = 'pending' | 'uploading' | 'completed' | 'failed' | 'processing';

// Review-specific status types  
export type ReviewStatus = 'pending' | 'in-review' | 'completed' | 'rejected';

interface StatusBadgeProps {
    status: StatusType;
    variant?: 'default' | 'outline' | 'secondary';
    size?: 'sm' | 'default' | 'lg';
    showIcon?: boolean;
    iconOnly?: boolean;
    className?: string;
    children?: React.ReactNode; // Allow custom text override
}

// Status configuration mapping
const statusConfig: Record<StatusType, {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    variant: 'default' | 'destructive' | 'outline' | 'secondary';
    className: string;
}> = {
    success: {
        label: 'Success',
        icon: CheckCircle,
        variant: 'default',
        className: 'bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-200',
    },
    pending: {
        label: 'Pending',
        icon: Clock,
        variant: 'outline',
        className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-900 dark:text-yellow-200',
    },
    warning: {
        label: 'Warning',
        icon: AlertCircle,
        variant: 'outline',
        className: 'bg-orange-100 text-orange-800 hover:bg-orange-200 dark:bg-orange-900 dark:text-orange-200',
    },
    error: {
        label: 'Error',
        icon: XCircle,
        variant: 'destructive',
        className: 'bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900 dark:text-red-200',
    },
    info: {
        label: 'Info',
        icon: AlertCircle,
        variant: 'secondary',
        className: 'bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200',
    },
    uploading: {
        label: 'Uploading',
        icon: Upload,
        variant: 'outline',
        className: 'bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200',
    },
    processing: {
        label: 'Processing',
        icon: RefreshCw,
        variant: 'outline',
        className: 'bg-purple-100 text-purple-800 hover:bg-purple-200 dark:bg-purple-900 dark:text-purple-200',
    },
    paused: {
        label: 'Paused',
        icon: Pause,
        variant: 'secondary',
        className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200',
    },
    reviewing: {
        label: 'Reviewing',
        icon: Eye,
        variant: 'outline',
        className: 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-200',
    },
    completed: {
        label: 'Completed',
        icon: CheckCircle,
        variant: 'default',
        className: 'bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-200',
    },
    failed: {
        label: 'Failed',
        icon: XCircle,
        variant: 'destructive',
        className: 'bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900 dark:text-red-200',
    },
};

/**
 * Main StatusBadge component
 */
export function StatusBadge({
    status,
    variant,
    size = 'default',
    showIcon = true,
    iconOnly = false,
    className,
    children,
}: StatusBadgeProps) {
    const config = statusConfig[status];

    if (!config) {
        logger.warn('Invalid status provided to StatusBadge', { status });
        // Fallback to info status
        const fallbackConfig = statusConfig.info;
        return (
            <Badge
                variant={variant || fallbackConfig.variant}
                className={cn(fallbackConfig.className, className)}
            >
                <AlertCircle className="mr-1 h-3 w-3" />
                Unknown
            </Badge>
        );
    }

    const IconComponent = config.icon;
    const displayText = children || config.label;

    logger.debug('Rendering StatusBadge', { status, variant, size, showIcon, iconOnly });

    // Icon size based on badge size
    const iconSize = size === 'sm' ? 'h-3 w-3' : size === 'lg' ? 'h-4 w-4' : 'h-3 w-3';

    return (
        <Badge
            variant={variant || config.variant}
            className={cn(
                config.className,
                size === 'sm' && 'px-2 py-1 text-xs',
                size === 'lg' && 'px-3 py-1.5 text-sm',
                iconOnly && 'px-1.5',
                className
            )}
        >
            {showIcon && (
                <IconComponent
                    className={cn(
                        iconSize,
                        !iconOnly && 'mr-1',
                        status === 'processing' && 'animate-spin'
                    )}
                />
            )}
            {!iconOnly && displayText}
        </Badge>
    );
}

/**
 * Upload-specific status badge
 */
interface UploadStatusBadgeProps extends Omit<StatusBadgeProps, 'status'> {
    status: UploadStatus;
    progress?: number; // For uploading status
}

export function UploadStatusBadge({
    status,
    progress,
    ...props
}: UploadStatusBadgeProps) {
    // Map upload status to general status
    const mappedStatus: StatusType = status === 'in-review' ? 'reviewing' : status;

    // For uploading status with progress, show custom text
    const customText = status === 'uploading' && progress !== undefined
        ? `Uploading ${progress}%`
        : undefined;

    return (
        <StatusBadge
            status={mappedStatus}
            {...props}
        >
            {customText}
        </StatusBadge>
    );
}

/**
 * Review-specific status badge
 */
interface ReviewStatusBadgeProps extends Omit<StatusBadgeProps, 'status'> {
    status: ReviewStatus;
}

export function ReviewStatusBadge({
    status,
    ...props
}: ReviewStatusBadgeProps) {
    // Map review status to general status
    const statusMap: Record<ReviewStatus, StatusType> = {
        'pending': 'pending',
        'in-review': 'reviewing',
        'completed': 'completed',
        'rejected': 'failed',
    };

    const mappedStatus = statusMap[status];

    return (
        <StatusBadge
            status={mappedStatus}
            {...props}
        />
    );
}

/**
 * Animated status badge for loading/processing states
 */
export function AnimatedStatusBadge(props: StatusBadgeProps) {
    const { status } = props;

    // Add animation for certain statuses
    const isAnimated = ['uploading', 'processing', 'reviewing'].includes(status);

    return (
        <div className={cn(isAnimated && 'animate-pulse')}>
            <StatusBadge {...props} />
        </div>
    );
}

/**
 * Status badge with tooltip (requires additional tooltip component)
 */
interface StatusBadgeWithTooltipProps extends StatusBadgeProps {
    tooltip?: string;
}

export function StatusBadgeWithTooltip({
    tooltip,
    ...props
}: StatusBadgeWithTooltipProps) {
    // For now, just render the badge - tooltip integration would require tooltip component
    // TODO: Add tooltip when Tooltip component is available
    return <StatusBadge {...props} />;
}
