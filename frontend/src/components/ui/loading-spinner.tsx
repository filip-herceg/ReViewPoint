import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
};

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
    return (
        <div
            className={cn(
                // Use only Tailwind semantic color classes for spinner border
                'animate-spin rounded-full border-2 border-border border-t-primary',
                sizeClasses[size],
                className
            )}
            aria-label="Loading"
        />
    );
}
