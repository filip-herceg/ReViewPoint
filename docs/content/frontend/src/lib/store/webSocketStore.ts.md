# webSocketStore.ts - Real-time WebSocket State Management

## Purpose

The `webSocketStore.ts` file provides centralized state management for WebSocket connections in the ReViewPoint application. It implements a Zustand-based store that manages real-time communication, notifications, upload progress tracking, and connection state handling.

## Key Components

### **WebSocket State Interface**

```typescript
interface WebSocketState {
  // Connection Management
  connectionState: ConnectionState; // Current connection status
  connectionId: string | null; // Unique connection identifier
  isConnected: boolean; // Simple connection flag
  reconnectAttempts: number; // Retry attempt counter
  lastError: string | null; // Last connection error

  // Real-time Data
  notifications: Notification[]; // Live notification queue
  uploadProgress: Map<string, UploadProgress>; // Upload tracking
  activeUploads: string[]; // Currently active uploads
}
```

### **Core Data Types**

#### **Notification Interface**

```typescript
interface Notification {
  id: string; // Unique notification ID
  type: "info" | "success" | "warning" | "error";
  title: string; // Notification headline
  message: string; // Detailed notification content
  timestamp: Date; // Creation timestamp
  read: boolean; // Read status flag
  persistent?: boolean; // Whether notification persists
}
```

#### **Upload Progress Interface**

```typescript
interface UploadProgress {
  uploadId: string; // Unique upload identifier
  progress: number; // Upload percentage (0-100)
  status: "uploading" | "completed" | "error";
  error?: string; // Error message if failed
  timestamp: Date; // Last update timestamp
}
```

## State Management Actions

### **Connection Management**

- `connect()` - Establish WebSocket connection
- `disconnect()` - Close WebSocket connection
- `subscribe(events)` - Subscribe to specific event types

### **Notification Management**

- `clearNotifications()` - Remove all notifications
- `markNotificationRead(id)` - Mark specific notification as read
- `removeNotification(id)` - Remove specific notification

### **Upload Tracking**

- `getUploadProgress(uploadId)` - Retrieve upload progress data
- Real-time upload status updates via WebSocket events

## Dependencies

### **Core Dependencies**

- `zustand` - State management library
- `@/lib/websocket/webSocketService` - WebSocket service integration
- `@/logger` - Event logging and error tracking

### **Type Definitions**

- [ConnectionState](../websocket/config.ts.md) - WebSocket connection state types
- [WebSocketEventType](../websocket/config.ts.md) - Event type definitions

## Implementation Details

### **Event Listener Integration**

The store automatically sets up WebSocket event listeners:

```typescript
// Connection state tracking
webSocketService.on("connect", (connectionId) => {
  set({
    isConnected: true,
    connectionId,
    connectionState: "connected",
    reconnectAttempts: 0,
  });
});

// Real-time notification handling
webSocketService.on("notification", (notification) => {
  set((state) => ({
    notifications: [notification, ...state.notifications],
  }));
});
```

### **Upload Progress Tracking**

```typescript
// Real-time upload progress updates
webSocketService.on("upload_progress", (progress) => {
  set((state) => {
    const newProgress = new Map(state.uploadProgress);
    newProgress.set(progress.uploadId, progress);
    return { uploadProgress: newProgress };
  });
});
```

### **Connection Recovery**

```typescript
// Automatic reconnection handling
webSocketService.on("disconnect", () => {
  set((state) => ({
    isConnected: false,
    connectionState: "disconnected",
    reconnectAttempts: state.reconnectAttempts + 1,
  }));
});
```

## Usage Examples

### **Component Integration**

```typescript
import { useWebSocketStore } from '@/lib/store/webSocketStore';

function NotificationCenter() {
  const {
    notifications,
    markNotificationRead,
    removeNotification
  } = useWebSocketStore();

  return (
    <div>
      {notifications.map(notification => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRead={() => markNotificationRead(notification.id)}
          onRemove={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
}
```

### **Upload Progress Display**

```typescript
function UploadTracker({ uploadId }: { uploadId: string }) {
  const { getUploadProgress } = useWebSocketStore();
  const progress = getUploadProgress(uploadId);

  if (!progress) return null;

  return (
    <div>
      <div>Progress: {progress.progress}%</div>
      <div>Status: {progress.status}</div>
      {progress.error && <div>Error: {progress.error}</div>}
    </div>
  );
}
```

### **Connection Status Monitoring**

```typescript
function ConnectionIndicator() {
  const { isConnected, connectionState, lastError } = useWebSocketStore();

  return (
    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
      <span>Status: {connectionState}</span>
      {lastError && <span>Error: {lastError}</span>}
    </div>
  );
}
```

## Event Subscription Management

### **Selective Event Subscription**

```typescript
// Subscribe to specific event types
const { subscribe } = useWebSocketStore();

// Subscribe to upload-related events only
subscribe(["upload_progress", "upload_complete", "upload_error"]);

// Subscribe to notification events
subscribe(["notification", "user_message"]);
```

### **Event Type Management**

The store handles various WebSocket event types:

- **Connection Events**: `connect`, `disconnect`, `error`
- **Upload Events**: `upload_progress`, `upload_complete`, `upload_error`
- **Notification Events**: `notification`, `user_message`, `system_alert`
- **Review Events**: `review_complete`, `review_update`, `review_assigned`

## Performance Optimization

### **Efficient State Updates**

```typescript
// Optimized notification updates
set((state) => ({
  notifications: [newNotification, ...state.notifications.slice(0, 99)],
})); // Limit to 100 notifications for performance
```

### **Memory Management**

```typescript
// Cleanup completed uploads
set((state) => {
  const activeUploads = state.activeUploads.filter(
    (id) => state.uploadProgress.get(id)?.status === "uploading",
  );
  return { activeUploads };
});
```

## Related Files

- [webSocketService.ts](../websocket/webSocketService.ts.md) - Core WebSocket service implementation
- [config.ts](../websocket/config.ts.md) - WebSocket configuration and types
- [authStore.ts](authStore.ts.md) - Authentication state integration
- [NotificationCenter.tsx](../../components/ui/notification-center.tsx.md) - UI component for notifications

## Development Notes

### **State Persistence**

The WebSocket store uses in-memory state only and does not persist data:

- **Notifications**: Lost on page refresh (intentional for real-time data)
- **Upload Progress**: Restored from server on reconnection
- **Connection State**: Re-established automatically

### **Error Handling Strategy**

```typescript
// Comprehensive error handling
webSocketService.on("error", (error) => {
  logger.error("WebSocket error:", error);
  set({
    lastError: error.message,
    connectionState: "error",
  });
});
```

### **Testing Considerations**

- Mock WebSocket service for unit tests
- Test connection recovery scenarios
- Verify notification queue management
- Test upload progress tracking accuracy
