import React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import logger from '@/logger';

export interface EmptyStateProps {
    /** Title for the empty state */
    title: string;
    /** Description text */
    description?: string;
    /** Icon to display (can be a React component or string) */
    icon?: React.ReactNode;
    /** Primary action button */
    action?: {
        label: string;
        onClick: () => void;
        variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
    };
    /** Secondary action button */
    secondaryAction?: {
        label: string;
        onClick: () => void;
        variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
    };
    /** Size variant */
    size?: 'sm' | 'md' | 'lg';
    /** Additional CSS classes */
    className?: string;
    /** Test ID for testing */
    testId?: string;
}

/**
 * EmptyState component for displaying when no data is available
 * Provides consistent UI for empty states with optional actions
 */
export function EmptyState({
    title,
    description,
    icon,
    action,
    secondaryAction,
    size = 'md',
    className,
    testId = 'empty-state',
}: EmptyStateProps) {
    const handleActionClick = (actionType: 'primary' | 'secondary') => {
        try {
            logger.debug('Empty state action clicked', { actionType, title });
            if (actionType === 'primary') {
                action?.onClick();
            } else {
                secondaryAction?.onClick();
            }
        } catch (err) {
            logger.error('Error in empty state action click', err);
        }
    };

    const sizeClasses = {
        sm: 'py-8 px-4',
        md: 'py-12 px-6',
        lg: 'py-16 px-8',
    };

    const iconSizeClasses = {
        sm: 'w-12 h-12',
        md: 'w-16 h-16',
        lg: 'w-20 h-20',
    };

    const titleSizeClasses = {
        sm: 'text-lg',
        md: 'text-xl',
        lg: 'text-2xl',
    };

    const descriptionSizeClasses = {
        sm: 'text-sm',
        md: 'text-base',
        lg: 'text-lg',
    };

    const defaultIcon = (
        <div
            className={cn(
                'rounded-full bg-muted flex items-center justify-center text-muted-foreground mx-auto',
                iconSizeClasses[size]
            )}
        >
            <svg
                className="w-1/2 h-1/2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8V4a1 1 0 00-1-1H6a1 1 0 00-1 1v1m16 0H2"
                />
            </svg>
        </div>
    );

    return (
        <Card
            className={cn(
                'border-dashed border-2 border-muted',
                sizeClasses[size],
                className
            )}
            data-testid={testId}
        >
            <div className="text-center space-y-4">
                {/* Icon */}
                <div data-testid={`${testId}-icon`}>
                    {icon || defaultIcon}
                </div>

                {/* Title */}
                <div className="space-y-2">
                    <h3
                        className={cn(
                            'font-semibold text-foreground',
                            titleSizeClasses[size]
                        )}
                        data-testid={`${testId}-title`}
                    >
                        {title}
                    </h3>

                    {description && (
                        <p
                            className={cn(
                                'text-muted-foreground max-w-md mx-auto',
                                descriptionSizeClasses[size]
                            )}
                            data-testid={`${testId}-description`}
                        >
                            {description}
                        </p>
                    )}
                </div>

                {/* Actions */}
                {(action || secondaryAction) && (
                    <div
                        className="flex flex-col sm:flex-row gap-2 justify-center"
                        data-testid={`${testId}-actions`}
                    >
                        {action && (
                            <Button
                                variant={action.variant || 'default'}
                                onClick={() => handleActionClick('primary')}
                                data-testid={`${testId}-primary-action`}
                            >
                                {action.label}
                            </Button>
                        )}

                        {secondaryAction && (
                            <Button
                                variant={secondaryAction.variant || 'outline'}
                                onClick={() => handleActionClick('secondary')}
                                data-testid={`${testId}-secondary-action`}
                            >
                                {secondaryAction.label}
                            </Button>
                        )}
                    </div>
                )}
            </div>
        </Card>
    );
}

export default EmptyState;
