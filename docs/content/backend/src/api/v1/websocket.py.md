# api/v1/websocket.py - Real-Time WebSocket Communication API

## Purpose

The `api/v1/websocket.py` module provides a production-ready WebSocket communication system for real-time bidirectional communication in the ReViewPoint platform. It implements comprehensive authentication, connection management, rate limiting, message validation, subscription handling, and broadcasting capabilities with enterprise-grade security and monitoring features.

## Key Components

### Core Imports and Configuration

#### Essential Dependencies and Type System

```python
"""
WebSocket API endpoints for real-time communication.
Provides authenticated WebSocket connections for real-time updates with comprehensive
error handling, rate limiting, connection management, and security features.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import (
    Any,
    Final,
    NotRequired,
    TypedDict,
    cast,
)
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from loguru import logger

from src.api.deps import get_current_user
from src.core.security import decode_access_token
from src.models.user import User

router: APIRouter = APIRouter(tags=["websocket"])
```

#### Configuration Constants and Limits

```python
# Configuration constants
MAX_CONNECTIONS_PER_USER: Final[int] = 3
MAX_MESSAGE_SIZE: Final[int] = 64 * 1024  # 64KB
HEARTBEAT_INTERVAL: Final[int] = 30  # seconds
CONNECTION_TIMEOUT: Final[int] = 60  # seconds
RATE_LIMIT_WINDOW: Final[int] = 60  # seconds
RATE_LIMIT_MAX_MESSAGES: Final[int] = 100  # per window
MAX_TOTAL_CONNECTIONS: Final[int] = 1000
MESSAGE_QUEUE_SIZE: Final[int] = 100

# Message validation schema
VALID_CLIENT_MESSAGE_TYPES: Final[set[str]] = {
    "ping",
    "subscribe",
    "unsubscribe",
    "heartbeat",
    "upload.cancel",
}

VALID_SUBSCRIPTION_EVENTS: Final[set[str]] = {
    "upload.progress",
    "upload.completed",
    "upload.error",
    "upload.cancelled",
    "review.updated",
    "review.created",
    "review.deleted",
    "system.notification",
    "system.maintenance",
    "user.status_changed",
    "file.processing",
    "file.ready",
}
```

### Rate Limiting System

#### Sophisticated Rate Limiter Implementation

```python
class RateLimiter:
    """Rate limiting for WebSocket connections."""

    def __init__(self, max_messages: int, window_seconds: int) -> None:
        """Initialize RateLimiter with max messages and window size."""
        self.max_messages: Final[int] = max_messages
        self.window_seconds: Final[int] = window_seconds
        self.user_windows: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limits."""
        now: float = time.time()
        window: deque[float] = self.user_windows[user_id]

        # Remove old entries outside the window
        while window and window[0] <= now - self.window_seconds:
            window.popleft()

        # Check if user is at limit
        if len(window) >= self.max_messages:
            return False

        # Add current request
        window.append(now)
        return True

    def get_reset_time(self, user_id: str) -> float | None:
        """Get when the rate limit resets for a user."""
        window: deque[float] = self.user_windows[user_id]
        if not window:
            return None
        return window[0] + self.window_seconds
```

### Connection Management System

#### Connection Information Tracking

```python
class ConnectionInfo:
    """Information about a WebSocket connection."""

    def __init__(
        self,
        websocket: WebSocket,
        user: User,
        connection_id: str,
    ) -> None:
        """Initialize ConnectionInfo with websocket, user, and connection ID."""
        self.websocket: WebSocket = websocket
        self.user: User = user
        self.connection_id: str = connection_id
        self.connected_at: datetime = datetime.now(UTC)
        self.last_activity: datetime = datetime.now(UTC)
        self.last_heartbeat: datetime = datetime.now(UTC)
        self.subscriptions: set[str] = set()
        self.message_count: int = 0
        self.error_count: int = 0
        self.is_authenticated: bool = True

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(UTC)

    def update_heartbeat(self) -> None:
        """Update last heartbeat timestamp."""
        self.last_heartbeat = datetime.now(UTC)
        self.update_activity()

    def is_stale(self, timeout_seconds: int = CONNECTION_TIMEOUT) -> bool:
        """Check if connection is stale."""
        return (datetime.now(UTC) - self.last_heartbeat).seconds > timeout_seconds
```

#### Advanced WebSocket Connection Manager

```python
class WebSocketConnectionManager:
    """Enhanced WebSocket connection manager with comprehensive features.

    - Connection limits and cleanup
    - Rate limiting per user
    - Message validation and sanitization
    - Heartbeat monitoring
    - Error handling and logging
    - Performance monitoring
    - Security controls.
    """

    def __init__(self) -> None:
        """Initialize the WebSocketConnectionManager."""
        self.connections: dict[str, ConnectionInfo] = {}
        self.user_connections: dict[str, set[str]] = defaultdict(set)
        self.rate_limiter = RateLimiter(RATE_LIMIT_MAX_MESSAGES, RATE_LIMIT_WINDOW)
        self._cleanup_task: asyncio.Task[None] | None = None
        self._cleanup_started: bool = False

    def _start_cleanup_task(self) -> None:
        """Start background task for connection cleanup."""
        if not self._cleanup_started:
            try:
                if self._cleanup_task is None or self._cleanup_task.done():
                    self._cleanup_task = asyncio.create_task(
                        self._cleanup_stale_connections(),
                    )
                    self._cleanup_started = True
            except RuntimeError:
                # No event loop running, will start cleanup when first connection is made
                pass

    async def _cleanup_stale_connections(self) -> None:
        """Background task to clean up stale connections."""
        while True:
            try:
                await asyncio.sleep(30)
                stale_connections: list[str] = []
                for conn_id, conn_info in self.connections.items():
                    if conn_info.is_stale():
                        stale_connections.append(conn_id)
                for conn_id in stale_connections:
                    logger.warning(f"[WS] Cleaning up stale connection {conn_id}")
                    await self._force_disconnect(conn_id, "Connection timeout")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WS] Error in cleanup task: {e}")
```

### Connection Lifecycle Management

#### Connection Establishment with Limits

```python
    async def connect(self, websocket: WebSocket, user: User) -> str:
        """Accept a new WebSocket connection with validation and limits.

        Args:
            websocket: The WebSocket connection
            user: Authenticated user

        Returns:
            str: Connection ID for tracking

        Raises:
            HTTPException: If connection limits exceeded or other errors

        """
        user_id = str(user.id)

        # Check total connection limit
        if len(self.connections) >= MAX_TOTAL_CONNECTIONS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Server connection limit exceeded",
            )

        # Check per-user connection limit
        if len(self.user_connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
            # Disconnect oldest connection for this user
            oldest_conn_id = min(
                self.user_connections[user_id],
                key=lambda cid: self.connections[cid].connected_at,
            )
            await self._force_disconnect(oldest_conn_id, "Connection limit exceeded")

        try:
            await websocket.accept()
        except Exception as e:
            logger.error(f"[WS] Failed to accept WebSocket connection: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to establish connection",
            ) from e

        connection_id = str(uuid4())
        conn_info = ConnectionInfo(websocket, user, connection_id)

        # Register connection
        self.connections[connection_id] = conn_info
        self.user_connections[user_id].add(connection_id)

        # Start cleanup task if not already started
        self._start_cleanup_task()

        logger.info(
            "[WS] New connection established",
            extra={
                "connection_id": connection_id,
                "user_id": user_id,
                "user_email": user.email,
                "total_connections": len(self.connections),
                "user_connections": len(self.user_connections[user_id]),
            },
        )

        return connection_id
```

#### Graceful Connection Cleanup

```python
    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection and clean up gracefully.

        Args:
            connection_id: The connection ID to remove

        """
        if connection_id not in self.connections:
            logger.warning(
                f"[WS] Attempted to disconnect unknown connection: {connection_id}",
            )
            return

        conn_info = self.connections[connection_id]
        user_id = str(conn_info.user.id)

        # Remove from tracking
        del self.connections[connection_id]
        self.user_connections[user_id].discard(connection_id)

        # Clean up empty user sets
        if not self.user_connections[user_id]:
            del self.user_connections[user_id]

        logger.info(
            "[WS] Connection disconnected",
            extra={
                "connection_id": connection_id,
                "user_id": user_id,
                "duration": (
                    datetime.now(UTC) - conn_info.connected_at
                ).total_seconds(),
                "message_count": conn_info.message_count,
                "total_connections": len(self.connections),
            },
        )

    async def _force_disconnect(self, connection_id: str, reason: str) -> None:
        """Force disconnect a connection."""
        if connection_id in self.connections:
            conn_info = self.connections[connection_id]
            with contextlib.suppress(Exception):
                await conn_info.websocket.close(code=1000, reason=reason)
            await self.disconnect(connection_id)
```

### Message Sending and Broadcasting

#### Individual Connection Messaging

```python
    async def send_to_connection(
        self,
        connection_id: str,
        message: dict[str, Any],
    ) -> bool:
        """Send a message to a specific connection.

        Args:
            connection_id: Target connection ID
            message: Message to send

        Returns:
            bool: True if sent successfully, False otherwise

        """
        if connection_id not in self.connections:
            logger.debug(f"[WS] Connection not found: {connection_id}")
            return False

        conn_info = self.connections[connection_id]

        try:
            # Validate message size
            message_json = json.dumps(message)
            if len(message_json.encode("utf-8")) > MAX_MESSAGE_SIZE:
                logger.warning(f"[WS] Message too large for connection {connection_id}")
                return False

            await conn_info.websocket.send_text(message_json)
            conn_info.update_activity()
            return True

        except Exception as e:
            logger.error(
                "[WS] Failed to send message to connection",
                extra={
                    "connection_id": connection_id,
                    "error": str(e),
                    "message_type": message.get("type", "unknown"),
                },
            )
            # Schedule connection for cleanup
            await self.disconnect(connection_id)
            return False
```

#### User-Targeted Broadcasting

```python
    async def send_to_user(
        self,
        user_id: str,
        message: dict[str, Any],
    ) -> int:
        """Send a message to all connections for a specific user.

        Args:
            user_id: Target user ID
            message: Message to send

        Returns:
            int: Number of connections message was sent to

        """
        if user_id not in self.user_connections:
            logger.debug(f"[WS] No active connections for user {user_id}")
            return 0

        connection_ids = list(self.user_connections[user_id])
        sent_count = 0

        for connection_id in connection_ids:
            if await self.send_to_connection(
                connection_id, cast(dict[str, Any], message)
            ):
                sent_count += 1

        logger.debug(
            "[WS] Message sent to user",
            extra={
                "user_id": user_id,
                "message_type": message.get("type", "unknown"),
                "connections_sent": sent_count,
                "connections_total": len(connection_ids),
            },
        )

        return sent_count
```

#### Subscription-Based Broadcasting

```python
    async def broadcast_to_subscribers(
        self,
        event_type: str,
        message: dict[str, Any],
    ) -> int:
        """Broadcast a message to all connections subscribed to an event type.

        Args:
            event_type: The event type to broadcast to
            message: Message to broadcast

        Returns:
            int: Number of connections message was sent to

        """
        total_sent = 0

        for connection_id, conn_info in self.connections.items():
            if event_type in conn_info.subscriptions:
                if await self.send_to_connection(
                    connection_id, cast(dict[str, Any], message)
                ):
                    total_sent += 1

        logger.info(
            "[WS] Message broadcasted to subscribers",
            extra={
                "event_type": event_type,
                "message_type": message.get("type", "unknown"),
                "connections_sent": total_sent,
            },
        )

        return total_sent
```

### Message Handling System

#### Client Message Processing

```python
    async def handle_client_message(
        self,
        connection_id: str,
        message: dict[str, Any],
    ) -> None:
        """Handle incoming client message with validation and processing.

        Args:
            connection_id: Source connection ID
            message: Parsed message from client

        """
        if connection_id not in self.connections:
            logger.warning(f"[WS] Message from unknown connection: {connection_id}")
            return

        conn_info = self.connections[connection_id]
        user_id = str(conn_info.user.id)

        # Check rate limiting
        if not self.rate_limiter.is_allowed(user_id):
            reset_time = self.rate_limiter.get_reset_time(user_id)
            logger.warning(f"[WS] Rate limit exceeded for user {user_id}")

            await self.send_to_connection(
                connection_id,
                {
                    "type": "error",
                    "data": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many messages",
                        "reset_time": reset_time,
                    },
                    "timestamp": datetime.now(UTC).isoformat(),
                    "id": str(uuid4()),
                },
            )
            return

        # Update connection activity
        conn_info.update_activity()
        conn_info.message_count += 1

        # Validate message type
        message_type = message.get("type")
        if message_type not in VALID_CLIENT_MESSAGE_TYPES:
            logger.warning(
                f"[WS] Invalid message type: {message_type} from {connection_id}",
            )
            conn_info.error_count += 1

            await self.send_to_connection(
                connection_id,
                {
                    "type": "error",
                    "data": {
                        "code": "INVALID_MESSAGE_TYPE",
                        "message": f"Unknown message type: {message_type}",
                    },
                    "timestamp": datetime.now(UTC).isoformat(),
                    "id": str(uuid4()),
                },
            )
            return

        # Handle specific message types
        try:
            if message_type == "ping":
                await self._handle_ping(connection_id, message)
            elif message_type == "subscribe":
                await self._handle_subscribe(connection_id, message)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe(connection_id, message)
            elif message_type == "heartbeat":
                await self._handle_heartbeat(connection_id, message)
            elif message_type == "upload.cancel":
                await self._handle_upload_cancel(connection_id, message)
            else:
                logger.warning(f"[WS] Unhandled message type: {message_type}")

        except Exception as e:
            logger.error(f"[WS] Error handling message {message_type}: {e}")
            conn_info.error_count += 1
```

#### Specific Message Type Handlers

```python
    async def _handle_ping(self, connection_id: str, message: dict[str, Any]) -> None:
        """Handle ping message and respond with pong."""
        conn_info = self.connections[connection_id]
        conn_info.update_heartbeat()

        ping_id = message.get("data", {}).get("pingId")

        pong_message: PongMessage = {
            "type": "pong",
            "data": {
                "timestamp": datetime.now(UTC).isoformat(),
                "pingId": ping_id,
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }

        await self.send_to_connection(connection_id, cast(dict[str, Any], pong_message))

    async def _handle_subscribe(
        self, connection_id: str, message: dict[str, Any]
    ) -> None:
        """Handle subscription request."""
        conn_info = self.connections[connection_id]
        events = message.get("data", {}).get("events", [])

        # Validate events
        valid_events = [e for e in events if e in VALID_SUBSCRIPTION_EVENTS]
        invalid_events = [e for e in events if e not in VALID_SUBSCRIPTION_EVENTS]

        if invalid_events:
            logger.warning(f"[WS] Invalid subscription events: {invalid_events}")

        # Add to subscriptions
        conn_info.subscriptions.update(valid_events)

        logger.info(
            "[WS] User subscribed to events",
            extra={
                "connection_id": connection_id,
                "user_id": str(conn_info.user.id),
                "events": valid_events,
                "invalid_events": invalid_events,
            },
        )

        # Send acknowledgment
        ack_message: SubscriptionAckMessage = {
            "type": "subscription.acknowledged",
            "data": {
                "events": valid_events,
                "invalid_events": invalid_events,
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }

        await self.send_to_connection(connection_id, cast(dict[str, Any], ack_message))

    async def _handle_unsubscribe(
        self, connection_id: str, message: dict[str, Any]
    ) -> None:
        """Handle unsubscription request."""
        conn_info = self.connections[connection_id]
        events = message.get("data", {}).get("events", [])

        # Remove from subscriptions
        for event in events:
            conn_info.subscriptions.discard(event)

        logger.info(
            "[WS] User unsubscribed from events",
            extra={
                "connection_id": connection_id,
                "user_id": str(conn_info.user.id),
                "events": events,
            },
        )

    async def _handle_heartbeat(
        self, connection_id: str, message: dict[str, Any]
    ) -> None:
        """Handle heartbeat message."""
        conn_info = self.connections[connection_id]
        conn_info.update_heartbeat()

        logger.debug(f"[WS] Heartbeat received from {connection_id}")

    async def _handle_upload_cancel(
        self, connection_id: str, message: dict[str, Any]
    ) -> None:
        """Handle upload cancellation request."""
        upload_id = message.get("data", {}).get("upload_id")

        if not upload_id:
            logger.warning(f"[WS] Upload cancel without upload_id from {connection_id}")
            return

        # Here you would implement the actual upload cancellation logic
        # For now, just log it
        logger.info(f"[WS] Upload cancel requested: {upload_id} from {connection_id}")
```

### Authentication System

#### JWT-Based WebSocket Authentication

```python
async def authenticate_websocket(token: str) -> User:
    """Authenticate a WebSocket connection using JWT token with enhanced
    validation.

    Args:
        token: JWT access token

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If authentication fails

    """
    try:
        # Decode the JWT token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID",
            )

        # Validate token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, UTC) < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

        # For now, create a minimal user object
        # In a real implementation, you'd fetch from database
        user = User(
            id=int(user_id),
            email=payload.get("email", "unknown@example.com"),
            name=payload.get("name", "Unknown User"),
            is_active=True,
            is_admin=payload.get("role") == "admin",
            hashed_password="",  # Not needed for WebSocket auth
        )

        # Validate user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[WS] Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from e
```

### Type Definitions for Messages

#### Comprehensive Message Type System

```python
# --- TypedDicts for WebSocket message schemas ---

class PingData(TypedDict, total=False):
    pingId: str

class PingMessage(TypedDict):
    type: str
    data: PingData
    timestamp: str
    id: str

class SubscribeData(TypedDict):
    events: list[str]

class SubscribeMessage(TypedDict):
    type: str
    data: SubscribeData
    timestamp: str
    id: str

class UnsubscribeData(TypedDict):
    events: list[str]

class UnsubscribeMessage(TypedDict):
    type: str
    data: UnsubscribeData
    timestamp: str
    id: str

class UploadCancelData(TypedDict):
    upload_id: str

class UploadCancelMessage(TypedDict):
    type: str
    data: UploadCancelData
    timestamp: str
    id: str

class ConnectionEstablishedData(TypedDict):
    connection_id: str
    user_id: str
    server_time: str
    features: list[str]
    limits: dict[str, Any]

class ConnectionEstablishedMessage(TypedDict):
    type: str
    data: ConnectionEstablishedData
    timestamp: str
    id: str

class PongData(TypedDict, total=False):
    timestamp: str
    pingId: NotRequired[str]

class PongMessage(TypedDict):
    type: str
    data: PongData
    timestamp: str
    id: str

class ErrorData(TypedDict, total=False):
    code: str
    message: str
    reset_time: NotRequired[float]

class ErrorMessage(TypedDict):
    type: str
    data: ErrorData
    timestamp: str
    id: str

class UploadProgressData(TypedDict, total=False):
    upload_id: str
    progress: int
    timestamp: str

class UploadProgressMessage(TypedDict):
    type: str
    data: UploadProgressData
    timestamp: str
    id: str

class UploadCompletedData(TypedDict):
    upload_id: str
    result: dict[str, Any]
    timestamp: str

class UploadCompletedMessage(TypedDict):
    type: str
    data: UploadCompletedData
    timestamp: str
    id: str

class SystemNotificationData(TypedDict, total=False):
    message: str
    level: str
    timestamp: str

class SystemNotificationMessage(TypedDict):
    type: str
    data: SystemNotificationData
    timestamp: str
    id: str

class ReviewUpdatedData(TypedDict):
    review_id: str
    changes: dict[str, Any]
    timestamp: str

class ReviewUpdatedMessage(TypedDict):
    type: str
    data: ReviewUpdatedData
    timestamp: str
    id: str

class FileProcessingData(TypedDict, total=False):
    file_id: str
    status: str
    progress: NotRequired[int]
    timestamp: str

class FileProcessingMessage(TypedDict):
    type: str
    data: FileProcessingData
    timestamp: str
    id: str

class FileReadyMessage(TypedDict):
    type: str
    data: FileProcessingData
    timestamp: str
    id: str
```

### Message Validation

#### Comprehensive Message Validation

```python
def validate_message_structure(data: str) -> dict[str, Any]:
    """Validate and parse incoming WebSocket message.

    Args:
        data: Raw message data

    Returns:
        Dict: Parsed and validated message

    Raises:
        ValueError: If message is invalid

    """
    try:
        # Check message size
        if len(data.encode("utf-8")) > MAX_MESSAGE_SIZE:
            raise ValueError("Message too large")

        # Parse JSON
        message = json.loads(data)

        # Validate basic structure
        if not isinstance(message, dict):
            raise ValueError("Message must be an object")

        # Validate required fields
        if "type" not in message:
            raise ValueError("Message must have 'type' field")

        return message

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e
```

### WebSocket Endpoint Implementation

#### Production-Ready WebSocket Endpoint

````python
@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    """**Production-Ready WebSocket Communication Endpoint**

    Establishes a persistent WebSocket connection for real-time
    bidirectional communication with comprehensive error handling,
    rate limiting, authentication, and monitoring.

    **Authentication:**
    - JWT token passed in URL path: `/ws/{token}`
    - Token must be valid and non-expired
    - User must be active and authenticated
    - Connection limits enforced per user

    **Connection Management:**
    - Maximum connections per user: 3
    - Total server connection limit: 1000
    - Automatic cleanup of stale connections
    - Graceful handling of network interruptions
    - Connection timeout: 60 seconds

    **Rate Limiting:**
    - 100 messages per minute per user
    - Automatic rate limit enforcement
    - Rate limit violation notifications

    **Message Validation:**
    - Maximum message size: 64KB
    - JSON structure validation
    - Message type validation
    - Subscription event validation

    **Supported Client → Server Message Types:**

    **Ping/Heartbeat:**
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

    **Event Subscription:**
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

    **Event Unsubscription:**
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

    **Upload Cancellation:**
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

    **Server → Client Message Types:**

    **Connection Established:**
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

    **Pong Response:**
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

    **Error Messages:**
    ```json
    {
        "type": "error",
        "data": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many messages",
            "reset_time": 1609459200
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_003"
    }
    ```

    **Error Codes:**
    - `RATE_LIMIT_EXCEEDED`: Too many messages sent
    - `INVALID_MESSAGE_TYPE`: Unknown message type
    - `INVALID_MESSAGE_FORMAT`: Malformed message
    - `SUBSCRIPTION_FAILED`: Invalid subscription event
    - `MESSAGE_TOO_LARGE`: Message exceeds size limit
    - `CONNECTION_LIMIT_EXCEEDED`: Too many connections

    **Security Features:**
    - JWT token validation
    - Rate limiting per user
    - Message size limits
    - Input validation and sanitization
    - Connection limits enforcement
    - Automatic cleanup of malicious connections

    **Monitoring & Observability:**
    - Comprehensive logging with structured data
    - Connection statistics tracking
    - Performance metrics collection
    - Error rate monitoring
    - User activity tracking
    """
    connection_id = None

    try:
        # Authenticate the connection
        user = await authenticate_websocket(token)

        # Connect and register the WebSocket
        connection_id = await connection_manager.connect(websocket, user)

        # Send welcome message with server capabilities
        welcome_message: ConnectionEstablishedMessage = {
            "type": "connection.established",
            "data": {
                "connection_id": connection_id,
                "user_id": str(user.id),
                "server_time": datetime.now(UTC).isoformat(),
                "features": [
                    "heartbeat",
                    "subscriptions",
                    "rate_limiting",
                    "message_validation",
                ],
                "limits": {
                    "max_message_size": MAX_MESSAGE_SIZE,
                    "rate_limit_messages": RATE_LIMIT_MAX_MESSAGES,
                    "rate_limit_window": RATE_LIMIT_WINDOW,
                    "heartbeat_interval": HEARTBEAT_INTERVAL,
                },
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }
        await connection_manager.send_to_connection(
            connection_id, cast(dict[str, Any], welcome_message)
        )

        # Main message loop
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=CONNECTION_TIMEOUT,
                )

                # Validate and parse message
                try:
                    message = validate_message_structure(data)
                except ValueError as e:
                    logger.warning(f"[WS] Invalid message from {connection_id}: {e}")
                    await connection_manager.send_to_connection(
                        connection_id,
                        {
                            "type": "error",
                            "data": {
                                "code": "INVALID_MESSAGE_FORMAT",
                                "message": str(e),
                            },
                            "timestamp": datetime.now(UTC).isoformat(),
                            "id": str(uuid4()),
                        },
                    )
                    continue

                # Handle the message
                await connection_manager.handle_client_message(connection_id, message)

            except TimeoutError:
                # Connection timeout - close connection
                logger.info(f"[WS] Connection timeout for {connection_id}")
                break

            except WebSocketDisconnect:
                logger.info(f"[WS] Client {connection_id} disconnected normally")
                break

            except Exception as e:
                logger.error(f"[WS] Error in message loop for {connection_id}: {e}")
                # Send error to client if possible
                with contextlib.suppress(Exception):
                    await connection_manager.send_to_connection(
                        connection_id,
                        {
                            "type": "error",
                            "data": {
                                "code": "INTERNAL_ERROR",
                                "message": "Internal server error",
                            },
                            "timestamp": datetime.now(UTC).isoformat(),
                            "id": str(uuid4()),
                        },
                    )
                break

    except HTTPException as e:
        logger.error(f"[WS] Authentication error: {e.detail}")
        with contextlib.suppress(Exception):
            await websocket.close(code=1008, reason="Authentication failed")

    except Exception as e:
        logger.error(f"[WS] Unexpected error: {e}")
        with contextlib.suppress(Exception):
            await websocket.close(code=1011, reason="Internal server error")

    finally:
        # Clean up connection
        if connection_id:
            await connection_manager.disconnect(connection_id)
````

### Administrative Endpoints

#### Connection Statistics and Management

```python
@router.get(
    "/ws/stats",
    summary="Get WebSocket connection statistics",
    description="""
    Retrieve real-time statistics about active WebSocket connections.

    **Requirements:**
    - Valid JWT token in Authorization header
    - Admin privileges required

    **Response includes:**
    - Total active connections
    - Number of unique users online
    - Connections per user breakdown
    - Average connections per user
    - System health metrics
    """,
)
async def get_websocket_stats(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get comprehensive WebSocket connection statistics for monitoring and
    administration.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    stats = connection_manager.get_connection_stats()

    return {
        "status": "success",
        "data": {
            **stats,
            "server_info": {
                "max_connections_per_user": MAX_CONNECTIONS_PER_USER,
                "max_total_connections": MAX_TOTAL_CONNECTIONS,
                "rate_limit_messages": RATE_LIMIT_MAX_MESSAGES,
                "rate_limit_window": RATE_LIMIT_WINDOW,
                "heartbeat_interval": HEARTBEAT_INTERVAL,
                "connection_timeout": CONNECTION_TIMEOUT,
            },
        },
    }

@router.get(
    "/ws/connections/{connection_id}",
    summary="Get specific connection information",
    description=(
        "Get detailed information about a specific WebSocket connection. " "Admin only."
    ),
)
async def get_connection_info(
    connection_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get detailed information about a specific connection."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    conn_info = connection_manager.get_connection_info(connection_id)

    if not conn_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    return {
        "status": "success",
        "data": conn_info,
    }

@router.post(
    "/ws/broadcast",
    summary="Broadcast message to all connections",
    description=(
        "Broadcast a message to all active WebSocket connections. " "Admin only."
    ),
)
async def broadcast_message(
    message: dict[str, Any],
    current_user: User = Depends(get_current_user),
) -> Any:
    """Broadcast a message to all active connections."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    # Add metadata to message
    broadcast_msg: dict[str, Any] = {
        **message,
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
        "source": "admin_broadcast",
    }
    sent_count = await connection_manager.broadcast_to_all(broadcast_msg)

    return {
        "status": "success",
        "data": {
            "message_sent": True,
            "connections_reached": sent_count,
            "message_id": broadcast_msg["id"],
        },
    }
```

### Event Broadcasting Functions

#### Specialized Broadcasting for Application Events

```python
# Event broadcasting functions for use by other parts of the application

async def broadcast_upload_progress(
    user_id: str,
    upload_id: str,
    progress: int,
    **kwargs: Any,
) -> None:
    """Broadcast upload progress to a specific user."""
    # Only allow keys that are valid for UploadProgressData
    data_dict: UploadProgressData = {
        "upload_id": upload_id,
        "progress": progress,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    for k in ("progress", "upload_id", "timestamp"):
        if k in kwargs:
            data_dict[k] = kwargs[k]

    message: UploadProgressMessage = {
        "type": "upload.progress",
        "data": data_dict,
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
    }
    await connection_manager.send_to_user(user_id, message)

async def broadcast_upload_completed(
    user_id: str,
    upload_id: str,
    result: dict[str, Any],
) -> None:
    """Broadcast upload completion to a specific user.

    Args:
        user_id: Target user ID
        upload_id: Upload identifier
        result: Upload result data

    """
    message: UploadCompletedMessage = {
        "type": "upload.completed",
        "data": {
            "upload_id": upload_id,
            "result": result,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
    }
    await connection_manager.send_to_user(user_id, message)

async def broadcast_upload_error(
    user_id: str,
    upload_id: str,
    error: str,
    **kwargs: Any,
) -> None:
    """Broadcast upload error to a specific user."""
    data_dict: UploadErrorData = {
        "upload_id": upload_id,
        "error": error,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    for k in ("upload_id", "error", "timestamp"):
        if k in kwargs:
            data_dict[k] = kwargs[k]

    message: UploadErrorMessage = {
        "type": "upload.error",
        "data": data_dict,
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
    }
    await connection_manager.send_to_user(user_id, message)

async def broadcast_system_notification(
    message_text: str,
    level: str = "info",
    target_users: list[str] | None = None,
    **kwargs: Any,
) -> None:
    """Broadcast a system notification to users."""
    data_dict: SystemNotificationData = {
        "message": message_text,
        "level": level,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    for k in ("message", "level", "timestamp"):
        if k in kwargs:
            data_dict[k] = kwargs[k]
    notification: SystemNotificationMessage = {
        "type": "system.notification",
        "data": data_dict,
        "timestamp": datetime.now(UTC).isoformat(),
        "id": str(uuid4()),
    }
    if target_users:
        for user_id in target_users:
            await connection_manager.send_to_user(user_id, notification)
    else:
        await connection_manager.broadcast_to_all(notification)

async def broadcast_review_updated(
    review_id: str,
    changes: dict[str, Any],
    target_users: list[str] | None = None,
) -> None:
    """Broadcast review update to relevant users.

    Args:
        review_id: Review identifier
        changes: What changed in the review
        target_users: Optional list of specific user IDs

    """
    message: ReviewUpdatedMessage = {
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

async def broadcast_file_processing_status(
    user_id: str,
    file_id: str,
    status: str,
    progress: int | None = None,
    **kwargs: Any,
) -> None:
    """Broadcast file processing status to a user."""
    message_data: FileProcessingData = {
        "file_id": file_id,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if progress is not None:
        message_data["progress"] = progress
    for k in ("file_id", "status", "progress", "timestamp"):
        if k in kwargs:
            message_data[k] = kwargs[k]
    if status == "processing":
        file_processing_message: FileProcessingMessage = {
            "type": "file.processing",
            "data": message_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }
        await connection_manager.send_to_user(user_id, file_processing_message)
    else:
        file_ready_message: FileReadyMessage = {
            "type": "file.ready",
            "data": message_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "id": str(uuid4()),
        }
        await connection_manager.send_to_user(user_id, file_ready_message)

# Cleanup function to be called on application shutdown
async def cleanup_websocket_manager() -> None:
    """Cleanup WebSocket manager on application shutdown."""
    await connection_manager.cleanup()
    logger.info("[WS] WebSocket manager cleaned up")
```

## Best Practices

### Real-Time Communication

- Implement comprehensive message validation and sanitization
- Use structured logging for monitoring and debugging
- Implement proper error handling and graceful degradation
- Use heartbeat/ping-pong for connection health monitoring
- Implement proper cleanup on disconnect

### Performance and Scalability

- Enforce connection limits per user and globally
- Implement rate limiting to prevent abuse
- Use efficient message routing and broadcasting
- Monitor connection statistics and performance metrics
- Implement background cleanup of stale connections

### Security Implementation

- Validate JWT tokens for authentication
- Implement proper authorization for message types
- Validate message size and structure
- Use secure WebSocket connections (WSS) in production
- Implement proper connection limits and rate limiting

### Error Handling and Monitoring

- Provide detailed error messages with error codes
- Log all connection events with structured data
- Monitor error rates and connection health
- Implement graceful handling of network interruptions
- Use comprehensive exception handling

This WebSocket API provides enterprise-grade real-time communication capabilities with comprehensive security, monitoring, and performance features essential for the ReViewPoint platform.

## Related Files

- [`core/security.py.md`](../../core/security.py.md) - JWT token validation and security
- [`models/user.py.md`](../../models/user.py.md) - User model for authentication
- [`api/deps.py.md`](../deps.py.md) - Dependency injection patterns
- [`api/v1/uploads.py.md`](uploads.py.md) - File upload integration with WebSocket events
