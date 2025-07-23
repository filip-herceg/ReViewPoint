import WebSocket from "ws";

async function testWebSocketConnection() {
  console.log("Testing WebSocket connection to backend...");

  const wsUrl = "ws://localhost:8000/api/v1/ws/test-token";
  console.log(`Connecting to: ${wsUrl}`);

  try {
    const ws = new WebSocket(wsUrl);

    ws.on("open", () => {
      console.log("✓ WebSocket connection opened successfully!");
      ws.close();
    });

    ws.on("error", (error) => {
      console.log("✗ WebSocket connection error:", error.message);
    });

    ws.on("close", (code, reason) => {
      console.log(
        `WebSocket connection closed with code ${code}: ${reason || "No reason"}`,
      );
    });

    // Wait a bit for connection
    await new Promise((resolve) => setTimeout(resolve, 2000));
  } catch (error) {
    console.log("✗ WebSocket test error:", error.message);
  }
}

testWebSocketConnection();
