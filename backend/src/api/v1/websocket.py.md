# WebSocket Real-Time Communication API

**File:** `backend/src/api/v1/websocket.py`  
**Purpose:** Production-ready WebSocket endpoint for real-time bidirectional communication with comprehensive connection management  
**Lines of Code:** 1,588  
**Type:** WebSocket API Router  

## Overview

The WebSocket Real-Time Communication API provides a comprehensive, production-ready WebSocket implementation for the ReViewPoint application. This module enables real-time bidirectional communication between clients and the server with robust features including JWT authentication, connection pooling, rate limiting, heartbeat monitoring, event subscriptions, message validation, and comprehensive error handling. It's designed to handle high-concurrent real-time communication scenarios while maintaining security and performance.

## Architecture

### Core Design Principles

1. **Security-First**: JWT authentication and message validation
2. **Connection Management**: Sophisticated pooling and lifecycle management
3. **Rate Limiting**: Per-user message rate limiting and abuse prevention
4. **Event-Driven**: Subscription-based event broadcasting system
5. **High Performance**: Optimized for concurrent connections and low latency
6. **Fault Tolerance**: Comprehensive error handling and recovery mechanisms

### WebSocket Communication Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Client       │    │   Connection    │    │   Event System  │
│   Connection    │────┤    Manager      │────┤   Broadcasting  │
│                 │    │                 │    │                 │
│ • Authentication│    │ • Pool Management│    │ • Subscriptions │
│ • Message Send  │    │ • Rate Limiting │    │ • Event Routing │
│ • Event Sub     │    │ • Heartbeats    │    │ • Target Users  │
│ • Heartbeat     │    │ • Cleanup       │    │ • Broadcast All │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Message       │
                    │   Processing    │
                    │                 │
                    │ • Validation    │
                    │ • Type Checking │
                    │ • Size Limits   │
                    │ • Error Handling│
                    └─────────────────┘
```

## Core Components

### 🔗 **WebSocket Connection Manager**

#### `WebSocketConnectionManager`
```python
class WebSocketConnectionManager:
    """Enhanced WebSocket connection manager with comprehensive features."""
    
    def __init__(self) -> None:
        self.connections: dict[str, ConnectionInfo] = {}
        self.user_connections: dict[str, set[str]] = defaultdict(set)
        self.rate_limiter = RateLimiter(RATE_LIMIT_MAX_MESSAGES, RATE_LIMIT_WINDOW)
```

**Core Features:**
- **Connection Pooling**: Centralized connection management with limits
- **User Mapping**: Track multiple connections per user
- **Rate Limiting**: Integrated per-user message rate limiting
- **Background Cleanup**: Automatic cleanup of stale connections
- **Performance Monitoring**: Connection statistics and health metrics

#### Connection Lifecycle Management
```python
async def connect(self, websocket: WebSocket, user: User) -> str:
    """Accept new WebSocket connection with validation and limits."""
    
    # Enforce connection limits
    if len(self.connections) >= MAX_TOTAL_CONNECTIONS:
        raise HTTPException(503, "Server at maximum capacity")
    
    if len(self.user_connections[str(user.id)]) >= MAX_CONNECTIONS_PER_USER:
        raise HTTPException(429, "Maximum connections per user exceeded")
    
    # Create connection with unique ID
    connection_id = str(uuid4())
    connection_info = ConnectionInfo(websocket, user, connection_id)
    
    # Register connection
    self.connections[connection_id] = connection_info
    self.user_connections[str(user.id)].add(connection_id)
```

**Connection Limits:**
- **Per User**: 3 concurrent connections maximum
- **Server Total**: 1,000 total connections maximum
- **Timeout**: 60 seconds for inactive connections
- **Cleanup**: Automatic stale connection removal

### 📊 **Rate Limiting System**

#### `RateLimiter`
```python
class RateLimiter:
    """Rate limiting for WebSocket connections."""
    
    def __init__(self, max_messages: int, window_seconds: int) -> None:
        self.max_messages = max_messages  # 100 messages
        self.window_seconds = window_seconds  # 60 seconds
        self.user_windows: dict[str, deque[float]] = defaultdict(deque)
```

**Rate Limiting Features:**
- **Per-User Limits**: Individual rate limits per authenticated user
- **Sliding Window**: Time-based sliding window algorithm
- **Message Counting**: Track message frequency across time windows
- **Automatic Reset**: Self-cleaning time windows

**Rate Limit Configuration:**
```python
RATE_LIMIT_MAX_MESSAGES: Final[int] = 100    # per window
RATE_LIMIT_WINDOW: Final[int] = 60           # seconds
```

### 💓 **Heartbeat & Connection Monitoring**

#### `ConnectionInfo`
```python
class ConnectionInfo:
    """Information about a WebSocket connection."""
    
    def __init__(self, websocket: WebSocket, user: User, connection_id: str) -> None:
        self.websocket = websocket
        self.user = user
        self.connection_id = connection_id
        self.connected_at = datetime.now(UTC)
        self.last_activity = datetime.now(UTC)
        self.last_heartbeat = datetime.now(UTC)
        self.subscriptions: set[str] = set()
```

**Connection Tracking:**
- **Activity Monitoring**: Track last message and heartbeat times
- **Subscription Management**: Per-connection event subscriptions
- **Connection Metadata**: Creation time, user info, message counts
- **Stale Detection**: Identify inactive connections for cleanup

#### Heartbeat Configuration
```python
HEARTBEAT_INTERVAL: Final[int] = 30    # seconds
CONNECTION_TIMEOUT: Final[int] = 60    # seconds
```

## WebSocket Endpoint

### 🔌 **Main WebSocket Connection**

#### `POST /ws/{token}`
```python
@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
```

**Purpose:** Establish authenticated WebSocket connection for real-time communication

**Connection Process:**
1. **Token Authentication**: Validate JWT token from URL path
2. **User Verification**: Extract and validate user from token
3. **Connection Limits**: Enforce per-user and server-wide limits
4. **WebSocket Handshake**: Accept WebSocket connection
5. **Connection Registration**: Add to connection pool
6. **Welcome Message**: Send connection established confirmation
7. **Message Loop**: Enter persistent message handling loop

**Authentication:**
```python
async def authenticate_websocket(token: str) -> User:
    """Authenticate WebSocket connection using JWT token."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token: missing user ID")
        
        # Additional user validation...
        return user
    except Exception as e:
        raise HTTPException(401, f"Authentication failed: {e}")
```

**Connection Established Message:**
```json
{
  "type": "connection.established",
  "data": {
    "connection_id": "conn_xyz789",
    "user_id": "123",
    "server_time": "2025-01-08T10:30:00Z",
    "features": ["heartbeat", "subscriptions", "rate_limiting"]
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_001"
}
```

## Message Types

### 📨 **Client → Server Messages**

#### Ping/Heartbeat
```json
{
  "type": "ping",
  "data": {
    "pingId": "optional-ping-id"
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_123"
}
```

**Purpose:** Keep connection alive and measure latency

#### Event Subscription
```json
{
  "type": "subscribe",
  "data": {
    "events": [
      "upload.progress",
      "upload.completed", 
      "system.notification"
    ]
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_124"
}
```

**Purpose:** Subscribe to specific event types for targeted notifications

**Valid Subscription Events:**
```python
VALID_SUBSCRIPTION_EVENTS = {
    "upload.progress",      # File upload progress updates
    "upload.completed",     # Upload completion notifications
    "upload.error",         # Upload error notifications
    "upload.cancelled",     # Upload cancellation notifications
    "review.updated",       # Review modification events
    "review.created",       # New review creation
    "review.deleted",       # Review deletion events
    "system.notification",  # System-wide announcements
    "system.maintenance",   # Maintenance notifications
    "user.status_changed",  # User status updates
    "file.processing",      # File processing status
    "file.ready",          # File processing completion
}
```

#### Event Unsubscription
```json
{
  "type": "unsubscribe",
  "data": {
    "events": ["upload.progress"]
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_125"
}
```

#### Upload Cancellation
```json
{
  "type": "upload.cancel",
  "data": {
    "upload_id": "upload_456"
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_126"
}
```

### 📤 **Server → Client Messages**

#### Pong Response
```json
{
  "type": "pong",
  "data": {
    "timestamp": "2025-01-08T10:30:00Z",
    "pingId": "echo-of-ping-id"
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_002"
}
```

#### Upload Progress
```json
{
  "type": "upload.progress",
  "data": {
    "upload_id": "upload_456",
    "progress": 45,
    "bytes_uploaded": 4500000,
    "total_bytes": 10000000,
    "timestamp": "2025-01-08T10:30:00Z"
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_003"
}
```

#### System Notification
```json
{
  "type": "system.notification",
  "data": {
    "message": "System maintenance scheduled for tonight",
    "level": "info",
    "timestamp": "2025-01-08T10:30:00Z"
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_004"
}
```

#### Error Messages
```json
{
  "type": "error",
  "data": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many messages. Please slow down.",
    "retry_after": 30
  },
  "timestamp": "2025-01-08T10:30:00Z",
  "id": "msg_005"
}
```

## Message Broadcasting

### 🎯 **Targeted Broadcasting**

#### Send to Specific User
```python
async def send_to_user(
    self, 
    user_id: str, 
    message: dict[str, Any]
) -> bool:
    """Send message to all connections of a specific user."""
    
    connections_sent = 0
    user_connections = self.user_connections.get(user_id, set())
    
    for connection_id in user_connections.copy():
        success = await self.send_to_connection(connection_id, message)
        if success:
            connections_sent += 1
    
    return connections_sent > 0
```

#### Send to Connection
```python
async def send_to_connection(
    self,
    connection_id: str,
    message: dict[str, Any]
) -> bool:
    """Send message to specific connection with error handling."""
    
    connection = self.connections.get(connection_id)
    if not connection:
        return False
    
    try:
        # Validate message size
        message_json = json.dumps(message)
        if len(message_json.encode()) > MAX_MESSAGE_SIZE:
            raise ValueError("Message too large")
        
        await connection.websocket.send_text(message_json)
        connection.update_activity()
        return True
        
    except Exception as e:
        logger.error(f"[WS] Error sending to {connection_id}: {e}")
        await self._force_disconnect(connection_id, f"Send error: {e}")
        return False
```

### 📡 **Broadcast Operations**

#### Broadcast to All Connections
```python
async def broadcast_to_all(
    self,
    message: dict[str, Any]
) -> int:
    """Broadcast message to all active connections."""
    
    if not self.connections:
        return 0
    
    connection_ids = list(self.connections.keys())
    tasks = [
        self.send_to_connection(conn_id, message)
        for conn_id in connection_ids
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful_sends = sum(1 for result in results if result is True)
    
    return successful_sends
```

#### Broadcast to Subscribers
```python
async def broadcast_to_subscribers(
    self,
    event_type: str,
    message: dict[str, Any]
) -> int:
    """Broadcast message to connections subscribed to specific event."""
    
    subscriber_connections = [
        conn for conn in self.connections.values()
        if event_type in conn.subscriptions
    ]
    
    if not subscriber_connections:
        return 0
    
    tasks = [
        self.send_to_connection(conn.connection_id, message)
        for conn in subscriber_connections
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for result in results if result is True)
```

## Helper Functions

### 📢 **Broadcasting Utilities**

#### System Notifications
```python
async def broadcast_system_notification(
    message: str,
    level: str = "info",
    target_users: list[str] | None = None,
    **kwargs: Any,
) -> None:
    """Broadcast system notification to users."""
    
    notification = {
        "type": "system.notification",
        "data": {
            "message": message,
            "level": level,
            "timestamp": datetime.now(UTC).isoformat(),
            **kwargs
        },
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
    }
    
    if target_users:
        for user_id in target_users:
            await connection_manager.send_to_user(user_id, notification)
    else:
        await connection_manager.broadcast_to_all(notification)
```

#### Review Updates
```python
async def broadcast_review_updated(
    review_id: str,
    changes: dict[str, Any],
    target_users: list[str] | None = None,
) -> None:
    """Broadcast review update to relevant users."""
    
    message = {
        "type": "review.updated",
        "data": {
            "review_id": review_id,
            "changes": changes,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
    }
    
    if target_users:
        for user_id in target_users:
            await connection_manager.send_to_user(user_id, message)
    else:
        await connection_manager.broadcast_to_subscribers("review.updated", message)
```

#### File Processing Status
```python
async def broadcast_file_processing_status(
    user_id: str,
    file_id: str,
    status: str,
    progress: int | None = None,
    **kwargs: Any,
) -> None:
    """Broadcast file processing status to a user."""
    
    message_data = {
        "file_id": file_id,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    
    if progress is not None:
        message_data["progress"] = progress
    
    if status == "processing":
        message = {
            "type": "file.processing",
            "data": message_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }
    else:
        message = {
            "type": "file.ready",
            "data": message_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }
    
    await connection_manager.send_to_user(user_id, message)
```

## Security Features

### 🔐 **Authentication & Authorization**

#### JWT Token Validation
```python
async def authenticate_websocket(token: str) -> User:
    """Authenticate WebSocket connection using JWT token."""
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(401, "Invalid token: missing user ID")
        
        # Fetch user from database
        user = await get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(401, "User not found or inactive")
        
        return user
        
    except Exception as e:
        logger.warning(f"[WS] Authentication failed: {e}")
        raise HTTPException(401, f"Authentication failed: {e}")
```

#### Connection Security
```python
# Connection limits per user
if len(self.user_connections[str(user.id)]) >= MAX_CONNECTIONS_PER_USER:
    raise HTTPException(429, "Maximum connections per user exceeded")

# Server capacity limits
if len(self.connections) >= MAX_TOTAL_CONNECTIONS:
    raise HTTPException(503, "Server at maximum capacity")
```

### 🛡️ **Message Validation**

#### Message Size Limits
```python
MAX_MESSAGE_SIZE: Final[int] = 64 * 1024  # 64KB

# Validate message size
message_json = json.dumps(message)
if len(message_json.encode()) > MAX_MESSAGE_SIZE:
    raise ValueError("Message too large")
```

#### Message Type Validation
```python
VALID_CLIENT_MESSAGE_TYPES = {
    "ping",
    "subscribe", 
    "unsubscribe",
    "heartbeat",
    "upload.cancel",
}

# Validate message type
if message_type not in VALID_CLIENT_MESSAGE_TYPES:
    await self.send_to_connection(connection_id, {
        "type": "error",
        "data": {
            "code": "INVALID_MESSAGE_TYPE",
            "message": f"Unknown message type: {message_type}"
        }
    })
```

## Performance Considerations

### ⚡ **Connection Optimization**

#### Asynchronous Operations
```python
# Concurrent message sending
tasks = [
    self.send_to_connection(conn_id, message)
    for conn_id in connection_ids
]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

#### Connection Pooling
```python
# Efficient connection lookup
self.connections: dict[str, ConnectionInfo] = {}
self.user_connections: dict[str, set[str]] = defaultdict(set)
```

#### Background Cleanup
```python
async def _cleanup_stale_connections(self) -> None:
    """Background task to clean up stale connections."""
    while True:
        await asyncio.sleep(30)  # Check every 30 seconds
        
        stale_connections = [
            conn_id for conn_id, conn_info in self.connections.items()
            if conn_info.is_stale()
        ]
        
        for conn_id in stale_connections:
            await self._force_disconnect(conn_id, "Connection timeout")
```

### 📊 **Memory Management**

#### Rate Limiting Cleanup
```python
def is_allowed(self, user_id: str) -> bool:
    """Check if user is within rate limits with automatic cleanup."""
    now = time.time()
    window = self.user_windows[user_id]
    
    # Remove old entries outside the window
    while window and window[0] <= now - self.window_seconds:
        window.popleft()
    
    return len(window) < self.max_messages
```

#### Connection Metadata
```python
class ConnectionInfo:
    """Lightweight connection metadata tracking."""
    def __init__(self, websocket, user, connection_id):
        self.websocket = websocket
        self.user = user
        self.connection_id = connection_id
        self.subscriptions: set[str] = set()  # Memory-efficient sets
        self.message_count = 0
        self.error_count = 0
```

## Usage Patterns

### 🔧 **Client Connection**

```javascript
// JavaScript WebSocket client
class ReViewPointWebSocket {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.subscriptions = new Set();
        this.messageHandlers = new Map();
    }
    
    connect() {
        this.ws = new WebSocket(`wss://api.reviewpoint.org/api/v1/ws/${this.token}`);
        
        this.ws.onopen = (event) => {
            console.log('Connected to ReViewPoint WebSocket');
            this.startHeartbeat();
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.ws.onclose = (event) => {
            console.log('WebSocket connection closed:', event.code);
            this.reconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    subscribe(events) {
        events.forEach(event => this.subscriptions.add(event));
        
        this.send({
            type: 'subscribe',
            data: { events: Array.from(this.subscriptions) }
        });
    }
    
    send(message) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                ...message,
                timestamp: new Date().toISOString(),
                id: this.generateMessageId()
            }));
        }
    }
    
    startHeartbeat() {
        setInterval(() => {
            this.send({
                type: 'ping',
                data: { pingId: Date.now().toString() }
            });
        }, 30000); // 30 seconds
    }
}

// Usage
const ws = new ReViewPointWebSocket('your-jwt-token');
ws.connect();

// Subscribe to upload progress
ws.subscribe(['upload.progress', 'upload.completed']);

// Handle upload progress
ws.messageHandlers.set('upload.progress', (data) => {
    updateProgressBar(data.upload_id, data.progress);
});
```

### 📡 **Server-Side Broadcasting**

```python
# Broadcasting from other parts of the application
from src.api.v1.websocket import (
    broadcast_system_notification,
    broadcast_file_processing_status,
    broadcast_review_updated
)

# System maintenance notification
await broadcast_system_notification(
    message="System maintenance starting in 5 minutes",
    level="warning"
)

# File processing update
await broadcast_file_processing_status(
    user_id="123",
    file_id="file_456",
    status="processing",
    progress=75
)

# Review update notification
await broadcast_review_updated(
    review_id="review_789",
    changes={"status": "approved", "updated_by": "admin"},
    target_users=["123", "456"]
)
```

## Testing Strategies

### 🧪 **WebSocket Testing**

```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test basic WebSocket connection establishment."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/v1/ws/valid-jwt-token") as websocket:
        # Should receive connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection.established"
        assert "connection_id" in data["data"]

@pytest.mark.asyncio  
async def test_websocket_authentication():
    """Test WebSocket authentication validation."""
    client = TestClient(app)
    
    # Test invalid token
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/ws/invalid-token"):
            pass

@pytest.mark.asyncio
async def test_ping_pong():
    """Test ping/pong heartbeat mechanism."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/v1/ws/valid-jwt-token") as websocket:
        # Skip connection established message
        websocket.receive_json()
        
        # Send ping
        ping_message = {
            "type": "ping",
            "data": {"pingId": "test-ping-123"},
            "timestamp": "2025-01-08T10:30:00Z",
            "id": "msg_ping"
        }
        websocket.send_json(ping_message)
        
        # Should receive pong
        pong_response = websocket.receive_json()
        assert pong_response["type"] == "pong"
        assert pong_response["data"]["pingId"] == "test-ping-123"

@pytest.mark.asyncio
async def test_subscription_system():
    """Test event subscription functionality."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/v1/ws/valid-jwt-token") as websocket:
        websocket.receive_json()  # Skip connection message
        
        # Subscribe to events
        subscribe_message = {
            "type": "subscribe",
            "data": {"events": ["upload.progress", "system.notification"]},
            "timestamp": "2025-01-08T10:30:00Z",
            "id": "msg_sub"
        }
        websocket.send_json(subscribe_message)
        
        # Should receive subscription confirmation
        response = websocket.receive_json()
        assert response["type"] == "subscription.confirmed"

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test WebSocket rate limiting enforcement."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/v1/ws/valid-jwt-token") as websocket:
        websocket.receive_json()  # Skip connection message
        
        # Send messages rapidly to trigger rate limit
        for i in range(105):  # Exceed 100 message limit
            ping_message = {
                "type": "ping", 
                "data": {"pingId": f"ping-{i}"},
                "id": f"msg-{i}"
            }
            websocket.send_json(ping_message)
        
        # Should receive rate limit error
        while True:
            response = websocket.receive_json()
            if response["type"] == "error":
                assert response["data"]["code"] == "RATE_LIMIT_EXCEEDED"
                break
```

### 🔄 **Integration Testing**

```python
@pytest.mark.asyncio
async def test_full_websocket_workflow():
    """Test complete WebSocket communication workflow."""
    client = TestClient(app)
    
    # Connect WebSocket
    with client.websocket_connect("/api/v1/ws/valid-jwt-token") as websocket:
        # 1. Receive connection confirmation
        connection_msg = websocket.receive_json()
        assert connection_msg["type"] == "connection.established"
        connection_id = connection_msg["data"]["connection_id"]
        
        # 2. Subscribe to events
        websocket.send_json({
            "type": "subscribe",
            "data": {"events": ["upload.progress"]},
            "id": "sub_1"
        })
        
        # 3. Trigger server-side broadcast
        from src.api.v1.websocket import broadcast_file_processing_status
        await broadcast_file_processing_status(
            user_id="test-user-123",
            file_id="file_456", 
            status="processing",
            progress=50
        )
        
        # 4. Receive broadcast message
        broadcast_msg = websocket.receive_json()
        assert broadcast_msg["type"] == "file.processing"
        assert broadcast_msg["data"]["file_id"] == "file_456"
        assert broadcast_msg["data"]["progress"] == 50
```

## Best Practices

### ✅ **Do's**

- **Implement Heartbeats**: Use ping/pong for connection health monitoring
- **Validate Messages**: Always validate message size, type, and structure
- **Handle Disconnections**: Implement graceful disconnect handling and cleanup
- **Use Rate Limiting**: Prevent abuse with per-user message rate limits
- **Monitor Connections**: Track connection count and implement limits
- **Log WebSocket Events**: Comprehensive logging for debugging and monitoring
- **Implement Reconnection**: Client-side automatic reconnection logic
- **Use Subscriptions**: Event-based subscriptions for efficient broadcasting

### ❌ **Don'ts**

- **Don't Skip Authentication**: Always validate JWT tokens for WebSocket connections
- **Don't Ignore Rate Limits**: Implement and enforce message rate limiting
- **Don't Leak Connections**: Ensure proper connection cleanup and resource management
- **Don't Send Large Messages**: Respect message size limits to prevent memory issues
- **Don't Block Event Loop**: Use async operations for all WebSocket operations
- **Don't Ignore Errors**: Handle all WebSocket errors gracefully
- **Don't Mix User Data**: Ensure message isolation between different users

## Related Files

- **`src/core/security.py`** - JWT token validation and security utilities
- **`src/api/deps.py`** - Authentication dependencies
- **`src/models/user.py`** - User model for authentication
- **`src/core/events.py`** - Application lifecycle event handling

## Dependencies

- **`fastapi`** - WebSocket support and API framework
- **`loguru`** - Structured logging for WebSocket events
- **`asyncio`** - Asynchronous programming support
- **`uuid`** - Unique connection and message ID generation

---

*This WebSocket router provides production-ready, secure, and scalable real-time communication capabilities for the ReViewPoint application, implementing industry best practices for WebSocket management, security, and performance.*
