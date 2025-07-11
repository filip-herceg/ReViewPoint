/**
 * User Avatar Component
 * Displays user profile avatar with fallback to initials
 * Part of Phase 4: Core UI Components
 */

import React from 'react';
import { cn } from '@/lib/utils';
import logger from '@/logger';

interface UserAvatarProps {
    user?: {
        name?: string;
        email?: string;
        avatar?: string;
    };
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
    showOnlineStatus?: boolean;
    isOnline?: boolean;
    onClick?: () => void;
}

const sizeClasses = {
    sm: 'h-6 w-6 text-xs',
    md: 'h-8 w-8 text-sm',
    lg: 'h-10 w-10 text-base',
    xl: 'h-12 w-12 text-lg'
};

const statusSizeClasses = {
    sm: 'h-2 w-2',
    md: 'h-2.5 w-2.5',
    lg: 'h-3 w-3',
    xl: 'h-3.5 w-3.5'
};

/**
 * Generate initials from user name or email
 */
function getInitials(name?: string, email?: string): string {
    if (name) {
        const nameParts = name.trim().split(' ');
        if (nameParts.length >= 2) {
            return `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase();
        }
        return name.slice(0, 2).toUpperCase();
    }

    if (email) {
        return email.slice(0, 2).toUpperCase();
    }

    return 'U';
}

/**
 * Generate a consistent background color based on user identifier
 */
function getAvatarColor(identifier: string): string {
    const colors = [
        'bg-red-500',
        'bg-blue-500',
        'bg-green-500',
        'bg-yellow-500',
        'bg-purple-500',
        'bg-pink-500',
        'bg-indigo-500',
        'bg-teal-500'
    ];

    const hash = identifier.split('').reduce((acc, char) => {
        return acc + char.charCodeAt(0);
    }, 0);

    return colors[hash % colors.length];
}

/**
 * User Avatar Component
 * 
 * @example
 * ```tsx
 * // Basic avatar
 * <UserAvatar user={user} />
 * 
 * // Avatar with online status
 * <UserAvatar 
 *   user={user} 
 *   size="lg" 
 *   showOnlineStatus={true} 
 *   isOnline={true} 
 * />
 * 
 * // Clickable avatar
 * <UserAvatar 
 *   user={user} 
 *   onClick={() => openUserProfile()} 
 * />
 * ```
 */
export function UserAvatar({
    user,
    size = 'md',
    className,
    showOnlineStatus = false,
    isOnline = false,
    onClick
}: UserAvatarProps) {
    const initials = getInitials(user?.name, user?.email);
    const identifier = user?.email || user?.name || 'unknown';
    const avatarColor = getAvatarColor(identifier);

    const handleClick = () => {
        if (onClick) {
            onClick();
            logger.info('UserAvatar: Avatar clicked', { user: user?.email });
        }
    };

    const handleImageError = (event: React.SyntheticEvent<HTMLImageElement>) => {
        logger.warn('UserAvatar: Failed to load avatar image', {
            src: event.currentTarget.src,
            user: user?.email
        });
        // Hide the image and show initials fallback
        event.currentTarget.style.display = 'none';
    };

    return (
        <div className={cn('relative inline-flex', className)}>
            <div
                className={cn(
                    'rounded-full flex items-center justify-center font-medium text-white relative overflow-hidden',
                    sizeClasses[size],
                    avatarColor,
                    onClick && 'cursor-pointer hover:opacity-80 transition-opacity',
                    className
                )}
                onClick={handleClick}
                role={onClick ? 'button' : undefined}
                tabIndex={onClick ? 0 : undefined}
                onKeyDown={onClick ? (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleClick();
                    }
                } : undefined}
                aria-label={user ? `${user.name || user.email} avatar` : 'User avatar'}
            >
                {/* Profile image */}
                {user?.avatar && (
                    <img
                        src={user.avatar}
                        alt={`${user.name || user.email} avatar`}
                        className="w-full h-full object-cover"
                        onError={handleImageError}
                    />
                )}

                {/* Initials fallback */}
                <span
                    data-testid="avatar-initials"
                    className="absolute inset-0 flex items-center justify-center"
                >
                    {initials}
                </span>
            </div>

            {/* Online status indicator */}
            {showOnlineStatus && (
                <div
                    data-testid="online-status"
                    className={cn(
                        'absolute -bottom-0.5 -right-0.5 rounded-full border-2 border-white dark:border-gray-800',
                        statusSizeClasses[size],
                        isOnline ? 'bg-green-500' : 'bg-gray-400'
                    )}
                    aria-label={isOnline ? 'Online' : 'Offline'}
                />
            )}
        </div>
    );
}

/**
 * Avatar Group Component
 * Displays multiple avatars in a stacked layout
 */
interface AvatarGroupProps {
    users: Array<{
        name?: string;
        email?: string;
        avatar?: string;
    }>;
    max?: number;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
    onOverflowClick?: () => void;
}

export function AvatarGroup({
    users,
    max = 3,
    size = 'md',
    className,
    onOverflowClick
}: AvatarGroupProps) {
    const visibleUsers = users.slice(0, max);
    const overflowCount = Math.max(0, users.length - max);

    React.useEffect(() => {
        logger.debug('AvatarGroup: Rendered', {
            totalUsers: users.length,
            visibleUsers: visibleUsers.length,
            overflowCount: Math.max(0, overflowCount)
        });
    }, [users.length, visibleUsers.length, overflowCount]);

    return (
        <div className={cn('flex -space-x-2', className)}>
            {visibleUsers.map((user, index) => (
                <UserAvatar
                    key={user.email || index}
                    user={user}
                    size={size}
                    className="ring-2 ring-white dark:ring-gray-800"
                />
            ))}

            {overflowCount > 0 && (
                <div
                    className={cn(
                        'rounded-full flex items-center justify-center font-medium text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-300 ring-2 ring-white dark:ring-gray-800',
                        sizeClasses[size],
                        onOverflowClick && 'cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors'
                    )}
                    onClick={onOverflowClick}
                    role={onOverflowClick ? 'button' : undefined}
                    tabIndex={onOverflowClick ? 0 : undefined}
                    onKeyDown={onOverflowClick ? (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            onOverflowClick();
                        }
                    } : undefined}
                    aria-label={`${overflowCount} more users`}
                >
                    +{overflowCount}
                </div>
            )}
        </div>
    );
}

/**
 * Hook for managing user avatar state and utilities
 */
export function useUserAvatar(user?: { name?: string; email?: string; avatar?: string }) {
    const [imageLoaded, setImageLoaded] = React.useState(false);
    const [imageError, setImageError] = React.useState(false);

    const handleImageLoad = React.useCallback(() => {
        setImageLoaded(true);
        setImageError(false);
        logger.debug('UserAvatar: Image loaded successfully', { user: user?.email });
    }, [user?.email]);

    const handleImageError = React.useCallback(() => {
        setImageLoaded(false);
        setImageError(true);
        logger.warn('UserAvatar: Image failed to load', { user: user?.email });
    }, [user?.email]);

    React.useEffect(() => {
        if (user?.avatar) {
            setImageLoaded(false);
            setImageError(false);
        }
    }, [user?.avatar]);

    // Utility functions for external use
    const getInitials = React.useCallback((name?: string, email?: string): string => {
        if (name) {
            const nameParts = name.trim().split(' ');
            if (nameParts.length >= 2) {
                return `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase();
            }
            return name.slice(0, 2).toUpperCase();
        }

        if (email) {
            return email.slice(0, 2).toUpperCase();
        }

        return 'U';
    }, []);

    const getAvatarColor = React.useCallback((identifier: string): string => {
        const colors = [
            'bg-red-500',
            'bg-blue-500',
            'bg-green-500',
            'bg-yellow-500',
            'bg-purple-500',
            'bg-pink-500',
            'bg-indigo-500',
            'bg-teal-500'
        ];

        const hash = identifier.split('').reduce((acc, char) => {
            return acc + char.charCodeAt(0);
        }, 0);

        return colors[hash % colors.length];
    }, []);

    return {
        imageLoaded,
        imageError,
        handleImageLoad,
        handleImageError,
        showInitials: !imageLoaded || imageError || !user?.avatar,
        getInitials,
        getAvatarColor
    };
}
