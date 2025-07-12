import "@testing-library/jest-dom";
import { vi } from "vitest";
import { server } from "./msw-server";

// Mock WebSocket service globally
vi.mock("@/lib/websocket/webSocketService", () => ({
	webSocketService: {
		connect: vi.fn(),
		disconnect: vi.fn(),
		subscribe: vi.fn(),
		on: vi.fn(),
		off: vi.fn(),
		send: vi.fn(),
		getStats: vi.fn(() => ({
			state: "disconnected",
			reconnectAttempts: 0,
			queuedMessages: 0,
			activeListeners: [],
			subscriptions: [],
			metadata: {
				connectionId: "test-connection-id",
				userId: "test-user-id",
				connectedAt: new Date(),
				lastHeartbeat: new Date(),
			},
		})),
		getMetadata: vi.fn(() => ({
			connectionId: "test-connection-id",
			userId: "test-user-id",
			connectedAt: new Date(),
			lastHeartbeat: new Date(),
		})),
	},
}));

// Establish API mocking before all tests.
beforeAll(() => server.listen());
// Reset any request handlers that are declared as a part of our tests (i.e. for testing one-time error scenarios)
afterEach(() => server.resetHandlers());
// Clean up after the tests are finished.
afterAll(() => server.close());
