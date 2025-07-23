/**
 * WebSocket React Hooks
 *
 * Custom React hooks for WebSocket integration and real-time updates.
 * Provides easy-to-use interfaces for components to subscribe to WebSocket events.
 */

import { useCallback, useEffect, useMemo } from "react";
import { useWebSocketStore } from "@/lib/store/webSocketStore";
import type { WebSocketEventType } from "@/lib/websocket/config";
import { webSocketService } from "@/lib/websocket/webSocketService";
import logger from "@/logger";

// WebSocket event data types
interface UploadProgressData {
  upload_id: string;
  progress: number;
  status?: string;
}

interface UploadCompletedData {
  upload_id: string;
  result?: unknown;
}

interface UploadErrorData {
  upload_id: string;
  error: string;
}

interface SystemNotificationData {
  message: string;
  type?: string;
  severity?: string;
}

interface ReviewUpdateData {
  review_id: string;
  status?: string;
  data?: unknown;
}

/**
 * Hook for WebSocket connection management
 */
export function useWebSocket() {
  const {
    connectionState,
    isConnected,
    lastError,
    connect,
    disconnect,
    subscribe,
  } = useWebSocketStore();

  // Connect on mount if authenticated
  useEffect(() => {
    if (connectionState === "disconnected") {
      connect();
    }
  }, [connectionState, connect]);

  const stats = useMemo(() => {
    return webSocketService.getStats();
  }, []);

  return {
    connectionState,
    isConnected,
    lastError,
    stats,
    connect,
    disconnect,
    subscribe,
  };
}

/**
 * Hook for subscribing to specific WebSocket events
 */
export function useWebSocketEvent<T = unknown>(
  event: WebSocketEventType,
  handler: (data: T) => void,
  dependencies: unknown[] = [],
) {
  const { isConnected } = useWebSocketStore();

  useEffect(() => {
    if (!isConnected) return;

    logger.debug("[useWebSocketEvent] Subscribing to event", { event });

    const unsubscribe = webSocketService.on(event, handler);

    return () => {
      logger.debug("[useWebSocketEvent] Unsubscribing from event", { event });
      unsubscribe();
    };
  }, [event, isConnected, ...dependencies, handler]);
}

/**
 * Hook for managing real-time notifications
 */
export function useWebSocketNotifications() {
  const {
    notifications,
    clearNotifications,
    markNotificationRead,
    removeNotification,
  } = useWebSocketStore();

  const unreadCount = useMemo(() => {
    return notifications.filter((n) => !n.read).length;
  }, [notifications]);

  const hasUnread = unreadCount > 0;

  const markAllRead = useCallback(() => {
    notifications.forEach((notification) => {
      if (!notification.read) {
        markNotificationRead(notification.id);
      }
    });
  }, [notifications, markNotificationRead]);

  const removeAllRead = useCallback(() => {
    notifications.forEach((notification) => {
      if (notification.read && !notification.persistent) {
        removeNotification(notification.id);
      }
    });
  }, [notifications, removeNotification]);

  return {
    notifications,
    unreadCount,
    hasUnread,
    clearNotifications,
    markNotificationRead,
    removeNotification,
    markAllRead,
    removeAllRead,
  };
}

/**
 * Hook for tracking upload progress in real-time
 */
export function useWebSocketUploadProgress() {
  const { uploadProgress, activeUploads, getUploadProgress } =
    useWebSocketStore();

  const activeUploadsWithProgress = useMemo(() => {
    return activeUploads.map((uploadId) => {
      const progress = uploadProgress.get(uploadId);
      return {
        uploadId,
        progress: progress?.progress || 0,
        status: progress?.status || "uploading",
        error: progress?.error,
        timestamp: progress?.timestamp || new Date(),
      };
    });
  }, [activeUploads, uploadProgress]);

  const hasActiveUploads = activeUploads.length > 0;

  const getProgress = useCallback(
    (uploadId: string) => {
      return getUploadProgress(uploadId);
    },
    [getUploadProgress],
  );

  return {
    activeUploads: activeUploadsWithProgress,
    hasActiveUploads,
    getProgress,
  };
}

/**
 * Hook for connection status with automatic reconnection
 */
export function useWebSocketConnection() {
  const { connectionState, isConnected, lastError, connect } =
    useWebSocketStore();

  const reconnect = useCallback(() => {
    logger.info("[useWebSocketConnection] Manual reconnect triggered");
    connect();
  }, [connect]);

  // Auto-reconnect on visibility change (when tab becomes active)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && !isConnected) {
        logger.info(
          "[useWebSocketConnection] Tab became visible, attempting reconnect",
        );
        reconnect();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [isConnected, reconnect]);

  const connectionInfo = useMemo(() => {
    const metadata = webSocketService.getMetadata();
    return {
      state: connectionState,
      isConnected,
      error: lastError,
      connectionId: metadata.connectionId,
      userId: metadata.userId,
      connectedAt: metadata.connectedAt,
      lastHeartbeat: metadata.lastHeartbeat,
    };
  }, [connectionState, isConnected, lastError]);

  return {
    ...connectionInfo,
    reconnect,
  };
}

/**
 * Hook for subscribing to upload events for a specific upload
 */
export function useWebSocketUpload(uploadId: string) {
  const { getUploadProgress } = useWebSocketStore();

  const progress = useMemo(() => {
    return getUploadProgress(uploadId);
  }, [uploadId, getUploadProgress]);

  // Subscribe to upload events for this specific upload
  useWebSocketEvent<UploadProgressData>(
    "upload.progress",
    useCallback(
      (data) => {
        if (data.upload_id === uploadId) {
          logger.debug("[useWebSocketUpload] Progress update", {
            uploadId,
            progress: data.progress,
          });
        }
      },
      [uploadId],
    ),
    [uploadId],
  );

  useWebSocketEvent<UploadCompletedData>(
    "upload.completed",
    useCallback(
      (data) => {
        if (data.upload_id === uploadId) {
          logger.info("[useWebSocketUpload] Upload completed", { uploadId });
        }
      },
      [uploadId],
    ),
    [uploadId],
  );

  useWebSocketEvent<UploadErrorData>(
    "upload.error",
    useCallback(
      (data) => {
        if (data.upload_id === uploadId) {
          logger.error("[useWebSocketUpload] Upload error", {
            uploadId,
            error: data.error,
          });
        }
      },
      [uploadId],
    ),
    [uploadId],
  );

  return {
    progress: progress?.progress || 0,
    status: progress?.status || "uploading",
    error: progress?.error,
    isActive: progress?.status === "uploading",
    isCompleted: progress?.status === "completed",
    hasError: progress?.status === "error",
  };
}

/**
 * Hook for system-wide real-time updates
 */
export function useWebSocketSystem() {
  const { subscribe } = useWebSocketStore();

  // Subscribe to system events
  useEffect(() => {
    subscribe(["system.notification", "review.updated"]);
  }, [subscribe]);

  // Handle system notifications
  useWebSocketEvent<SystemNotificationData>(
    "system.notification",
    useCallback((data) => {
      logger.info("[useWebSocketSystem] System notification received", data);
    }, []),
    [],
  );

  // Handle review updates
  useWebSocketEvent<ReviewUpdateData>(
    "review.updated",
    useCallback((data) => {
      logger.info("[useWebSocketSystem] Review update received", data);
    }, []),
    [],
  );

  return {
    // Could return system-wide state here
  };
}
