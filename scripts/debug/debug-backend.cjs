const http = require("http");

// Test the backend health endpoint first to make sure it's responding
const testHealth = () => {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: "localhost",
        port: 8000,
        path: "/api/v1/health",
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      },
      (res) => {
        console.log(`HEALTH STATUS: ${res.statusCode}`);
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          console.log("HEALTH RESPONSE:", data);
          resolve(res.statusCode === 200);
        });
      },
    );

    req.on("error", reject);
    req.end();
  });
};

// Test auth endpoint
const testAuth = () => {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      email: "test@example.com",
      password: "TestPassword123!",
      name: "Test User",
    });

    const req = http.request(
      {
        hostname: "localhost",
        port: 8000,
        path: "/api/v1/auth/register",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(postData),
          Accept: "application/json",
          "X-API-Key": "test-key",
        },
      },
      (res) => {
        console.log(`AUTH STATUS: ${res.statusCode}`);
        console.log(`AUTH HEADERS:`, res.headers);

        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          console.log("AUTH RESPONSE:", data);
          try {
            const parsed = JSON.parse(data);
            console.log("AUTH PARSED:", JSON.stringify(parsed, null, 2));
          } catch (e) {
            console.log("Failed to parse JSON:", e.message);
          }
          resolve(parsed);
        });
      },
    );

    req.on("error", reject);
    req.write(postData);
    req.end();
  });
};

// Run tests
(async () => {
  try {
    console.log("=== Testing Health Endpoint ===");
    const healthOk = await testHealth();

    if (healthOk) {
      console.log("\n=== Testing Auth Endpoint ===");
      await testAuth();
    } else {
      console.log("Health endpoint failed, skipping auth test");
    }
  } catch (error) {
    console.error("Test failed:", error);
  }
})();
