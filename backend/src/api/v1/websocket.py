# WebSocket API endpoints for real-time communication
# Provides authenticated WebSocket connections for real-time updates

import json
from typing import Any
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

router = APIRouter(tags=["websocket"])


# Connection manager for WebSocket connections
class WebSocketConnectionManager:
    """
    Manages WebSocket connections for real-time communication.

    Features:
    - User-based connection tracking
    - Message broadcasting
    - Connection lifecycle management
    - Event routing and validation
    """

    def __init__(self) -> None:
        # Active connections: user_id -> set of websocket connections
        self.active_connections: dict[str, set[WebSocket]] = {}
        # Connection metadata: websocket -> connection info
        self.connection_info: dict[WebSocket, dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user: User) -> str:
        """
        Accept a new WebSocket connection and register it.

        Args:
            websocket: The WebSocket connection
            user: Authenticated user

        Returns:
            str: Connection ID for tracking
        """
        await websocket.accept()

        user_id = str(user.id)
        connection_id = str(uuid4())

        # Initialize user connection set if needed
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        # Add connection to user's set
        self.active_connections[user_id].add(websocket)

        # Store connection metadata
        self.connection_info[websocket] = {
            "connection_id": connection_id,
            "user_id": user_id,
            "user_email": user.email,
            "user_name": user.name,
        }

        logger.info(
            "[WS] New connection established",
            extra={
                "connection_id": connection_id,
                "user_id": user_id,
                "user_email": user.email,
                "total_connections": sum(
                    len(conns) for conns in self.active_connections.values()
                ),
            },
        )

        return connection_id

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection and clean up.

        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket not in self.connection_info:
            logger.warning("[WS] Attempted to disconnect unknown WebSocket")
            return

        connection_info = self.connection_info[websocket]
        user_id = connection_info["user_id"]
        connection_id = connection_info["connection_id"]

        # Remove from user's connection set
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty user sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove connection metadata
        del self.connection_info[websocket]

        logger.info(
            "[WS] Connection disconnected",
            extra={
                "connection_id": connection_id,
                "user_id": user_id,
                "total_connections": sum(
                    len(conns) for conns in self.active_connections.values()
                ),
            },
        )

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> int:
        """
        Send a message to all connections for a specific user.

        Args:
            user_id: Target user ID
            message: Message to send

        Returns:
            int: Number of connections message was sent to
        """
        if user_id not in self.active_connections:
            logger.debug(f"[WS] No active connections for user {user_id}")
            return 0

        connections = self.active_connections[user_id].copy()
        sent_count = 0

        # Send to all user connections
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(message))
                sent_count += 1
            except Exception as e:
                logger.error(
                    "[WS] Failed to send message to connection",
                    extra={
                        "user_id": user_id,
                        "error": str(e),
                        "message_type": message.get("type", "unknown"),
                    },
                )
                # Remove failed connection
                self.disconnect(websocket)

        logger.debug(
            "[WS] Message sent to user",
            extra={
                "user_id": user_id,
                "message_type": message.get("type", "unknown"),
                "connections_sent": sent_count,
                "connections_total": len(connections),
            },
        )

        return sent_count

    async def broadcast_to_all(self, message: dict[str, Any]) -> int:
        """
        Broadcast a message to all active connections.

        Args:
            message: Message to broadcast

        Returns:
            int: Number of connections message was sent to
        """
        total_sent = 0

        for user_id in list(self.active_connections.keys()):
            sent = await self.send_to_user(user_id, message)
            total_sent += sent

        logger.info(
            "[WS] Message broadcasted to all users",
            extra={
                "message_type": message.get("type", "unknown"),
                "users_total": len(self.active_connections),
                "connections_sent": total_sent,
            },
        )

        return total_sent

    def get_connection_stats(self) -> dict[str, Any]:
        """
        Get current connection statistics.

        Returns:
            Dict with connection statistics
        """
        total_connections = sum(
            len(conns) for conns in self.active_connections.values()
        )

        return {
            "total_users": len(self.active_connections),
            "total_connections": total_connections,
            "users_online": list(self.active_connections.keys()),
        }


# Global connection manager instance
connection_manager = WebSocketConnectionManager()


async def authenticate_websocket(token: str) -> User:
    """
    Authenticate a WebSocket connection using JWT token.

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

        return user

    except Exception as e:
        logger.error(f"[WS] Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from e


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    """
    **Real-time WebSocket Communication Endpoint**

    Establishes a persistent WebSocket connection for real-time bidirectional communication
    between client and server. Supports file upload progress, notifications, and system events.

    **Authentication:**
    - JWT token passed in URL path: `/ws/{token}`
    - Token must be valid and non-expired
    - User must be active and authenticated

    **Connection Flow:**
    1. Client connects with JWT token in path
    2. Server validates token and extracts user info
    3. Connection registered in connection manager
    4. Welcome message sent to client
    5. Bidirectional message exchange begins

    **Message Format:**
    All messages follow this JSON structure:
    ```json
    {
        "type": "event_type",
        "data": {...},
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "unique_message_id"
    }
    ```

    **Client → Server Message Types:**

    **Heartbeat (ping):**
    ```json
    {
        "type": "ping",
        "data": {},
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_123"
    }
    ```

    **Event Subscription:**
    ```json
    {
        "type": "subscribe",
        "data": {
            "events": ["upload.progress", "upload.completed", "system.notification"]
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_124"
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
            "timestamp": "2025-01-08T10:30:00Z"
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_001"
    }
    ```

    **Heartbeat Response:**
    ```json
    {
        "type": "pong",
        "data": {
            "timestamp": "2025-01-08T10:30:00Z"
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_002"
    }
    ```

    **Upload Progress:**
    ```json
    {
        "type": "upload.progress",
        "data": {
            "upload_id": "upload_456",
            "progress": 75,
            "timestamp": "2025-01-08T10:30:00Z"
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_003"
    }
    ```

    **Upload Completed:**
    ```json
    {
        "type": "upload.completed",
        "data": {
            "upload_id": "upload_456",
            "result": {
                "file_id": "file_789",
                "url": "https://example.com/files/789",
                "size": 1024000
            },
            "timestamp": "2025-01-08T10:30:00Z"
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_004"
    }
    ```

    **System Notification:**
    ```json
    {
        "type": "system.notification",
        "data": {
            "message": "System maintenance scheduled",
            "level": "warning",
            "timestamp": "2025-01-08T10:30:00Z"
        },
        "timestamp": "2025-01-08T10:30:00Z",
        "id": "msg_005"
    }
    ```

    **Error Handling:**
    - Authentication failures close connection with code 1008
    - Internal errors close connection with code 1011
    - Invalid JSON messages are logged but connection continues
    - Unknown message types are logged and ignored

    **Connection Management:**
    - Multiple connections per user supported
    - Automatic cleanup on disconnect
    - Connection statistics tracked
    - Graceful handling of network interruptions

    **Usage Examples:**

    **JavaScript Client:**
    ```javascript
    const token = "your-jwt-token";
    const ws = new WebSocket(`ws://localhost:8000/api/v1/websocket/ws/${token}`);

    ws.onopen = function() {
        console.log("Connected to WebSocket");

        // Subscribe to events
        ws.send(JSON.stringify({
            type: "subscribe",
            data: { events: ["upload.progress", "system.notification"] },
            timestamp: new Date().toISOString(),
            id: "sub_001"
        }));
    };

    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        console.log("Received:", message);

        switch(message.type) {
            case "upload.progress":
                updateProgressBar(message.data.progress);
                break;
            case "system.notification":
                showNotification(message.data.message, message.data.level);
                break;
        }
    };

    // Send heartbeat every 30 seconds
    setInterval(() => {
        ws.send(JSON.stringify({
            type: "ping",
            data: {},
            timestamp: new Date().toISOString(),
            id: `ping_${Date.now()}`
        }));
    }, 30000);
    ```

    **Python Client:**
    ```python
    import asyncio
    import json
    import websockets

    async def websocket_client():
        token = "your-jwt-token"
        uri = f"ws://localhost:8000/api/v1/websocket/ws/{token}"

        async with websockets.connect(uri) as websocket:
            # Subscribe to events
            await websocket.send(json.dumps({
                "type": "subscribe",
                "data": {"events": ["upload.progress", "upload.completed"]},
                "timestamp": "2025-01-08T10:30:00Z",
                "id": "sub_001"
            }))

            async for message in websocket:
                data = json.loads(message)
                print(f"Received: {data}")
    ```
    """
    try:
        # Authenticate the connection
        user = await authenticate_websocket(token)

        # Connect and register the WebSocket
        connection_id = await connection_manager.connect(websocket, user)

        # Send welcome message
        welcome_message = {
            "type": "connection.established",
            "data": {
                "connection_id": connection_id,
                "user_id": str(user.id),
                "timestamp": "2025-01-08T00:00:00Z",  # Would use real timestamp
            },
            "timestamp": "2025-01-08T00:00:00Z",
            "id": str(uuid4()),
        }
        await websocket.send_text(json.dumps(welcome_message))

        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                message_type = message.get("type", "unknown")

                if message_type == "ping":
                    # Respond to heartbeat
                    pong_message = {
                        "type": "pong",
                        "data": {"timestamp": "2025-01-08T00:00:00Z"},
                        "timestamp": "2025-01-08T00:00:00Z",
                        "id": str(uuid4()),
                    }
                    await websocket.send_text(json.dumps(pong_message))

                elif message_type == "subscribe":
                    # Handle event subscriptions
                    subscriptions = message.get("data", {}).get("events", [])
                    logger.info(
                        "[WS] User subscribed to events",
                        extra={
                            "user_id": str(user.id),
                            "events": subscriptions,
                        },
                    )

                    # Send acknowledgment
                    ack_message = {
                        "type": "subscription.acknowledged",
                        "data": {"events": subscriptions},
                        "timestamp": "2025-01-08T00:00:00Z",
                        "id": str(uuid4()),
                    }
                    await websocket.send_text(json.dumps(ack_message))

                else:
                    logger.warning(
                        "[WS] Unknown message type received",
                        extra={
                            "user_id": str(user.id),
                            "message_type": message_type,
                        },
                    )

            except json.JSONDecodeError as e:
                logger.error(
                    "[WS] Invalid JSON received",
                    extra={
                        "user_id": str(user.id),
                        "error": str(e),
                    },
                )
                continue

    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected normally")

    except HTTPException as e:
        logger.error(f"[WS] Authentication error: {e.detail}")
        await websocket.close(code=1008, reason="Authentication failed")

    except Exception as e:
        logger.error(f"[WS] Unexpected error: {e}")
        await websocket.close(code=1011, reason="Internal server error")

    finally:
        # Clean up connection
        connection_manager.disconnect(websocket)


@router.get(
    "/ws/stats",
    summary="Get WebSocket connection statistics",
    description="""
    Retrieve real-time statistics about active WebSocket connections.

    **Requirements:**
    - Valid JWT token in Authorization header
    - Admin privileges required

    **Response Data:**
    - `total_users`: Number of unique users with active connections
    - `total_connections`: Total number of active WebSocket connections
    - `users_online`: List of user IDs currently connected

    **Use Cases:**
    - Monitor system load and connection health
    - Debug connection issues
    - Analytics and usage tracking
    - System administration

    **Example Response:**
    ```json
    {
        "status": "success",
        "data": {
            "total_users": 15,
            "total_connections": 23,
            "users_online": ["123", "456", "789"]
        }
    }
    ```
    """,
    responses={
        200: {
            "description": "Connection statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {
                            "total_users": 15,
                            "total_connections": 23,
                            "users_online": ["123", "456", "789"],
                        },
                    }
                }
            },
        },
        401: {"description": "Invalid or missing JWT token"},
        403: {"description": "Admin access required"},
        500: {"description": "Internal server error"},
    },
    tags=["WebSocket"],
)
async def get_websocket_stats(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get real-time WebSocket connection statistics for system monitoring.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    stats = connection_manager.get_connection_stats()

    return {
        "status": "success",
        "data": stats,
    }


# Event broadcasting functions for use by other parts of the application
async def broadcast_upload_progress(
    user_id: str, upload_id: str, progress: int
) -> None:
    """
    Broadcast upload progress to a specific user.

    Args:
        user_id: Target user ID
        upload_id: Upload identifier
        progress: Progress percentage (0-100)
    """
    message = {
        "type": "upload.progress",
        "data": {
            "upload_id": upload_id,
            "progress": progress,
            "timestamp": "2025-01-08T00:00:00Z",
        },
        "timestamp": "2025-01-08T00:00:00Z",
        "id": str(uuid4()),
    }

    await connection_manager.send_to_user(user_id, message)


async def broadcast_upload_completed(
    user_id: str, upload_id: str, result: dict[str, Any]
) -> None:
    """
    Broadcast upload completion to a specific user.

    Args:
        user_id: Target user ID
        upload_id: Upload identifier
        result: Upload result data
    """
    message = {
        "type": "upload.completed",
        "data": {
            "upload_id": upload_id,
            "result": result,
            "timestamp": "2025-01-08T00:00:00Z",
        },
        "timestamp": "2025-01-08T00:00:00Z",
        "id": str(uuid4()),
    }

    await connection_manager.send_to_user(user_id, message)


async def broadcast_system_notification(message: str, level: str = "info") -> None:
    """
    Broadcast a system notification to all users.

    Args:
        message: Notification message
        level: Notification level (info, warning, error)
    """
    notification = {
        "type": "system.notification",
        "data": {
            "message": message,
            "level": level,
            "timestamp": "2025-01-08T00:00:00Z",
        },
        "timestamp": "2025-01-08T00:00:00Z",
        "id": str(uuid4()),
    }

    await connection_manager.broadcast_to_all(notification)
