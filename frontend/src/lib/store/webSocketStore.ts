/**
 * WebSocket Store
 * 
 * Zustand store for managing WebSocket connection state and real-time events.
 * Integrates with the WebSocket service to provide reactive state management.
 */

import { create } from 'zustand';
import logger from '@/logger';
import { webSocketService } from '@/lib/websocket/webSocketService';
import type { 
    ConnectionState, 
    WebSocketEventType 
} from '@/lib/websocket/config';

export interface Notification {
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
    persistent?: boolean;
}

export interface UploadProgress {
    uploadId: string;
    progress: number;
    status: 'uploading' | 'completed' | 'error';
    error?: string;
    timestamp: Date;
}

interface WebSocketState {
    // Connection state
    connectionState: ConnectionState;
    connectionId: string | null;
    isConnected: boolean;
    reconnectAttempts: number;
    lastError: string | null;

    // Real-time data
    notifications: Notification[];
    uploadProgress: Map<string, UploadProgress>;
    activeUploads: string[];

    // Actions
    connect: () => void;
    disconnect: () => void;
    subscribe: (events: WebSocketEventType[]) => void;
    clearNotifications: () => void;
    markNotificationRead: (id: string) => void;
    removeNotification: (id: string) => void;
    getUploadProgress: (uploadId: string) => UploadProgress | null;
}

export const useWebSocketStore = create<WebSocketState>((set, get) => {
    // Initialize WebSocket event listeners
    const initializeEventListeners = () => {
        // Connection events
        webSocketService.on('connection.established', (data) => {
            logger.info('[WebSocketStore] Connection established', data);
            set({
                connectionState: 'connected',
                isConnected: true,
                connectionId: data.connection_id,
                reconnectAttempts: 0,
                lastError: null,
            });
        });

        webSocketService.on('connection.lost', (data) => {
            logger.warn('[WebSocketStore] Connection lost', data);
            set({
                connectionState: 'reconnecting',
                isConnected: false,
                lastError: data.reason || 'Connection lost',
            });
        });

        webSocketService.on('connection.error', (data) => {
            logger.error('[WebSocketStore] Connection error', data);
            set({
                connectionState: 'error',
                isConnected: false,
                lastError: data.error || 'Connection error',
            });
        });

        // Upload events
        webSocketService.on('upload.progress', (data) => {
            logger.debug('[WebSocketStore] Upload progress', data);
            const { upload_id: uploadId, progress } = data;

            set((state) => {
                const newUploadProgress = new Map(state.uploadProgress);
                newUploadProgress.set(uploadId, {
                    uploadId,
                    progress,
                    status: 'uploading',
                    timestamp: new Date(),
                });

                const newActiveUploads = state.activeUploads.includes(uploadId)
                    ? state.activeUploads
                    : [...state.activeUploads, uploadId];

                return {
                    uploadProgress: newUploadProgress,
                    activeUploads: newActiveUploads,
                };
            });
        });

        webSocketService.on('upload.completed', (data) => {
            logger.info('[WebSocketStore] Upload completed', data);
            const { upload_id: uploadId, result } = data;

            set((state) => {
                const newUploadProgress = new Map(state.uploadProgress);
                newUploadProgress.set(uploadId, {
                    uploadId,
                    progress: 100,
                    status: 'completed',
                    timestamp: new Date(),
                });

                const newActiveUploads = state.activeUploads.filter(id => id !== uploadId);

                // Add success notification
                const notification: Notification = {
                    id: crypto.randomUUID(),
                    type: 'success',
                    title: 'Upload Completed',
                    message: `File upload completed successfully`,
                    timestamp: new Date(),
                    read: false,
                };

                return {
                    uploadProgress: newUploadProgress,
                    activeUploads: newActiveUploads,
                    notifications: [...state.notifications, notification],
                };
            });
        });

        webSocketService.on('upload.error', (data) => {
            logger.error('[WebSocketStore] Upload error', data);
            const { upload_id: uploadId, error } = data;

            set((state) => {
                const newUploadProgress = new Map(state.uploadProgress);
                newUploadProgress.set(uploadId, {
                    uploadId,
                    progress: 0,
                    status: 'error',
                    error: error || 'Upload failed',
                    timestamp: new Date(),
                });

                const newActiveUploads = state.activeUploads.filter(id => id !== uploadId);

                // Add error notification
                const notification: Notification = {
                    id: crypto.randomUUID(),
                    type: 'error',
                    title: 'Upload Failed',
                    message: `File upload failed: ${error || 'Unknown error'}`,
                    timestamp: new Date(),
                    read: false,
                    persistent: true,
                };

                return {
                    uploadProgress: newUploadProgress,
                    activeUploads: newActiveUploads,
                    notifications: [...state.notifications, notification],
                };
            });
        });

        // System notifications
        webSocketService.on('system.notification', (data) => {
            logger.info('[WebSocketStore] System notification', data);
            const { message, level = 'info' } = data;

            const notification: Notification = {
                id: crypto.randomUUID(),
                type: level as Notification['type'],
                title: 'System Notification',
                message,
                timestamp: new Date(),
                read: false,
                persistent: level === 'error' || level === 'warning',
            };

            set((state) => ({
                notifications: [...state.notifications, notification],
            }));
        });

        // Review updates (placeholder for future implementation)
        webSocketService.on('review.updated', (data) => {
            logger.info('[WebSocketStore] Review updated', data);

            const notification: Notification = {
                id: crypto.randomUUID(),
                type: 'info',
                title: 'Review Updated',
                message: 'A review has been updated',
                timestamp: new Date(),
                read: false,
            };

            set((state) => ({
                notifications: [...state.notifications, notification],
            }));
        });

        logger.info('[WebSocketStore] Event listeners initialized');
    };

    // Initialize listeners immediately
    initializeEventListeners();

    return {
        // Initial state
        connectionState: 'disconnected',
        connectionId: null,
        isConnected: false,
        reconnectAttempts: 0,
        lastError: null,
        notifications: [],
        uploadProgress: new Map(),
        activeUploads: [],

        // Actions
        connect: () => {
            logger.info('[WebSocketStore] Connecting via store action');
            webSocketService.connect();
            set({ connectionState: 'connecting' });
        },

        disconnect: () => {
            logger.info('[WebSocketStore] Disconnecting via store action');
            webSocketService.disconnect();
            set({
                connectionState: 'disconnected',
                isConnected: false,
                connectionId: null,
                reconnectAttempts: 0,
                lastError: null,
            });
        },

        subscribe: (events: WebSocketEventType[]) => {
            logger.info('[WebSocketStore] Subscribing to events', { events });
            webSocketService.subscribe(events);
        },

        clearNotifications: () => {
            logger.info('[WebSocketStore] Clearing all notifications');
            set({ notifications: [] });
        },

        markNotificationRead: (id: string) => {
            logger.debug('[WebSocketStore] Marking notification as read', { id });
            set((state) => ({
                notifications: state.notifications.map(notification =>
                    notification.id === id
                        ? { ...notification, read: true }
                        : notification
                ),
            }));
        },

        removeNotification: (id: string) => {
            logger.debug('[WebSocketStore] Removing notification', { id });
            set((state) => ({
                notifications: state.notifications.filter(notification => notification.id !== id),
            }));
        },

        getUploadProgress: (uploadId: string) => {
            const state = get();
            return state.uploadProgress.get(uploadId) || null;
        },
    };
});

// Store is ready and exports types above
