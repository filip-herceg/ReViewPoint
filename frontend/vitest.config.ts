import { resolve } from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      "@/logger": resolve(__dirname, "src/logger.ts"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/react-query-feature-flag.js", "./tests/setup.ts"],
    include: ["tests/**/*.{test,spec}.{ts,tsx}"], // Restrict to test files only
    exclude: [
      "e2e/**",
      "node_modules/**",
      "dist/**",
      "**/node_modules/**",
      "**/dist/**",
      "**/.*/**",
      // PERMANENTLY EXCLUDED - DO NOT REMOVE
      "tests/lib/monitoring/errorMonitoring.test.ts", // Causes infinite loops
    ],
    env: {
      // Set test-specific environment variables to ensure consistency
      NODE_ENV: "test",
      VITE_LOG_LEVEL: "error", // Only show errors during tests
      VITE_API_TIMEOUT: "5000", // Set consistent timeout for tests
      VITE_ENABLE_ANALYTICS: "true", // Set consistent analytics flag
      VITE_WS_URL: "ws://localhost:8000/api/v1", // Set consistent WebSocket URL
      VITE_APP_NAME: "ReViewPoint (Test)", // Set test-specific app name
      VITE_APP_VERSION: "0.1.0-test", // Set test-specific version
      VITE_SENTRY_DSN: "", // Empty for tests
    },
    coverage: {
      reporter: ["text", "html"],
    },
    // Remove verbose console logging
    silent: false,
    logHeapUsage: false,
    // Only show console logs for failed tests
    onConsoleLog: () => false,
    // Add timeout to prevent hanging tests
    testTimeout: 10000, // 10 seconds
    hookTimeout: 5000, // 5 seconds for setup/teardown
  },
});
