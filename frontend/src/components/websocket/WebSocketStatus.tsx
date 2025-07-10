/**
 * WebSocket Connection Status Component
 * 
 * Displays the current WebSocket connection status with visual indicators.
 * Provides reconnection controls and connection information.
 */

import React from 'react';
import { useWebSocketConnection } from '@/lib/websocket/hooks';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
    WifiIcon,
    WifiOffIcon,
    LoaderIcon,
    AlertTriangleIcon,
    RefreshCwIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface WebSocketStatusProps {
    className?: string;
    showDetails?: boolean;
    inline?: boolean;
}

export function WebSocketStatus({
    className,
    showDetails = false,
    inline = false
}: WebSocketStatusProps) {
    const {
        state,
        isConnected,
        error,
        connectionId,
        connectedAt,
        reconnect
    } = useWebSocketConnection();

    // Status configuration
    const statusConfig = {
        connected: {
            icon: WifiIcon,
            label: 'Connected',
            color: 'success' as const,
            description: 'Real-time updates active',
        },
        connecting: {
            icon: LoaderIcon,
            label: 'Connecting',
            color: 'warning' as const,
            description: 'Establishing connection...',
        },
        reconnecting: {
            icon: LoaderIcon,
            label: 'Reconnecting',
            color: 'warning' as const,
            description: 'Attempting to reconnect...',
        },
        disconnected: {
            icon: WifiOffIcon,
            label: 'Disconnected',
            color: 'secondary' as const,
            description: 'Real-time updates unavailable',
        },
        error: {
            icon: AlertTriangleIcon,
            label: 'Error',
            color: 'destructive' as const,
            description: 'Connection failed',
        },
    };

    const config = statusConfig[state];
    const Icon = config.icon;

    // Inline compact version
    if (inline) {
        return (
            <div className={cn('flex items-center gap-2', className)}>
                <Icon
                    className={cn(
                        'h-4 w-4',
                        config.color === 'success' && 'text-success',
                        config.color === 'warning' && 'text-warning animate-spin',
                        config.color === 'destructive' && 'text-destructive',
                        config.color === 'secondary' && 'text-muted-foreground'
                    )}
                />
                <Badge variant={config.color} className="text-xs">
                    {config.label}
                </Badge>
                {state === 'error' && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={reconnect}
                        className="h-6 px-2"
                    >
                        <RefreshCwIcon className="h-3 w-3" />
                    </Button>
                )}
            </div>
        );
    }

    // Full status component
    return (
        <div className={cn('space-y-4', className)}>
            {/* Status Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Icon
                        className={cn(
                            'h-5 w-5',
                            config.color === 'success' && 'text-success',
                            config.color === 'warning' && 'text-warning animate-spin',
                            config.color === 'destructive' && 'text-destructive',
                            config.color === 'secondary' && 'text-muted-foreground'
                        )}
                    />
                    <div>
                        <h3 className="font-medium text-sm text-foreground">Real-time Connection</h3>
                        <p className="text-xs text-muted-foreground">
                            {config.description}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <Badge variant={config.color}>
                        {config.label}
                    </Badge>

                    {!isConnected && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={reconnect}
                            className="h-8"
                        >
                            <RefreshCwIcon className="h-4 w-4 mr-1" />
                            Reconnect
                        </Button>
                    )}
                </div>
            </div>

            {/* Error Alert */}
            {error && (
                <Alert variant="destructive">
                    <AlertTriangleIcon className="h-4 w-4 text-destructive" />
                    <AlertDescription>
                        Connection error: {error}
                    </AlertDescription>
                </Alert>
            )}

            {/* Details */}
            {showDetails && isConnected && (
                <div className="bg-muted/50 p-3 rounded-lg">
                    <div className="grid grid-cols-2 gap-4 text-xs">
                        {connectionId && (
                            <div>
                                <span className="font-medium text-muted-foreground">
                                    Connection ID:
                                </span>
                                <div className="font-mono text-foreground mt-1">
                                    {connectionId.slice(0, 8)}...
                                </div>
                            </div>
                        )}

                        {connectedAt && (
                            <div>
                                <span className="font-medium text-muted-foreground">
                                    Connected:
                                </span>
                                <div className="text-foreground mt-1">
                                    {connectedAt.toLocaleTimeString()}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

/**
 * Simple connection indicator for header/navbar
 */
export function WebSocketIndicator({ className }: { className?: string }) {
    const { isConnected, state } = useWebSocketConnection();

    return (
        <div
            className={cn(
                'flex items-center gap-2 text-xs text-muted-foreground',
                className
            )}
            title={`WebSocket: ${state}`}
        >
            <div
                className={cn(
                    'h-2 w-2 rounded-full',
                    isConnected ? 'bg-success animate-pulse' : 'bg-muted-foreground'
                )}
            />
            <span className="hidden sm:inline">
                {isConnected ? 'Live' : 'Offline'}
            </span>
        </div>
    );
}
