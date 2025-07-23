// Simple WebSocket connection test for debugging
const token = "test-token-placeholder"; // Replace with actual JWT token
const wsUrl = `ws://localhost:8000/api/v1/ws/${token}`;

console.log("Testing WebSocket connection to:", wsUrl);

const ws = new WebSocket(wsUrl);

ws.onopen = function (event) {
  console.log("✅ WebSocket connection opened");
  console.log("Event:", event);

  // Send a ping message
  const pingMessage = {
    type: "ping",
    data: { pingId: "test-ping-123" },
    timestamp: new Date().toISOString(),
    id: "test-msg-001",
  };

  console.log("Sending ping message:", pingMessage);
  ws.send(JSON.stringify(pingMessage));
};

ws.onmessage = function (event) {
  console.log("📨 Received message:", event.data);
  try {
    const message = JSON.parse(event.data);
    console.log("Parsed message:", message);
  } catch (e) {
    console.error("Failed to parse message:", e);
  }
};

ws.onerror = function (error) {
  console.error("❌ WebSocket error:", error);
};

ws.onclose = function (event) {
  console.log("🔌 WebSocket connection closed");
  console.log(
    "Code:",
    event.code,
    "Reason:",
    event.reason,
    "WasClean:",
    event.wasClean,
  );
};

// Close connection after 10 seconds
setTimeout(() => {
  console.log("Closing WebSocket connection...");
  ws.close();
}, 10000);
