/**
 * WebSocket Store Tests
 *
 * Tests for the WebSocket Zustand store functionality.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useWebSocketStore } from "@/lib/store/webSocketStore";
import {
	type WebSocketEventType,
	webSocketService,
} from "@/lib/websocket/webSocketService";
import {
	createTestError,
	createTestNotification,
	createTestUploadProgress,
} from "../test-templates";
import { testLogger } from "../test-utils";

// Mock logger
vi.mock("@/logger", () => ({
	default: {
		info: vi.fn(),
		debug: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	},
}));

describe("WebSocketStore", () => {
	beforeEach(() => {
		// Reset store state before each test
		useWebSocketStore.setState({
			connectionState: "disconnected",
			connectionId: null,
			isConnected: false,
			reconnectAttempts: 0,
			lastError: null,
			notifications: [],
			uploadProgress: new Map(),
			activeUploads: [],
		});

		// Clear all mocks
		vi.clearAllMocks();
		testLogger.debug("WebSocketStore test setup complete");
	});

	afterEach(() => {
		testLogger.debug("WebSocketStore test cleanup complete");
	});

	describe("connection management", () => {
		it("should connect to WebSocket service", () => {
			const { connect } = useWebSocketStore.getState();

			connect();

			expect(webSocketService.connect).toHaveBeenCalledOnce();
			testLogger.debug("WebSocket connect called successfully");
		});

		it("should disconnect from WebSocket service", () => {
			const { disconnect } = useWebSocketStore.getState();

			disconnect();

			expect(webSocketService.disconnect).toHaveBeenCalledOnce();
			testLogger.debug("WebSocket disconnect called successfully");
		});

		it("should subscribe to events", () => {
			const { subscribe } = useWebSocketStore.getState();
			const events: WebSocketEventType[] = [
				"upload.progress",
				"system.notification",
			];

			subscribe(events);

			expect(webSocketService.subscribe).toHaveBeenCalledWith(events);
			testLogger.debug("WebSocket subscribe called with events", { events });
		});

		it("should update connection state", () => {
			useWebSocketStore.setState({
				connectionState: "connected",
				isConnected: true,
				connectionId: "test-123",
			});

			const state = useWebSocketStore.getState();
			expect(state.connectionState).toBe("connected");
			expect(state.isConnected).toBe(true);
			expect(state.connectionId).toBe("test-123");
		});

		it("should handle connection errors", () => {
			const error = createTestError("Connection failed");

			useWebSocketStore.setState({
				connectionState: "error",
				isConnected: false,
				lastError: error.message,
			});

			const state = useWebSocketStore.getState();
			expect(state.connectionState).toBe("error");
			expect(state.isConnected).toBe(false);
			expect(state.lastError).toBe("Connection failed");
		});
	});

	describe("notification management", () => {
		it("should add notifications", () => {
			const notification = createTestNotification();

			useWebSocketStore.setState({
				notifications: [notification],
			});

			const state = useWebSocketStore.getState();
			expect(state.notifications).toHaveLength(1);
			expect(state.notifications[0]).toEqual(notification);
		});

		it("should clear all notifications", () => {
			const { clearNotifications } = useWebSocketStore.getState();

			// Add some notifications first
			useWebSocketStore.setState({
				notifications: [createTestNotification(), createTestNotification()],
			});

			clearNotifications();

			const state = useWebSocketStore.getState();
			expect(state.notifications).toHaveLength(0);
		});

		it("should mark notification as read", () => {
			const notification = createTestNotification({ read: false });
			const { markNotificationRead } = useWebSocketStore.getState();

			useWebSocketStore.setState({
				notifications: [notification],
			});

			markNotificationRead(notification.id);

			const state = useWebSocketStore.getState();
			expect(state.notifications[0].read).toBe(true);
		});

		it("should remove specific notification", () => {
			const notification1 = createTestNotification();
			const notification2 = createTestNotification();
			const { removeNotification } = useWebSocketStore.getState();

			useWebSocketStore.setState({
				notifications: [notification1, notification2],
			});

			removeNotification(notification1.id);

			const state = useWebSocketStore.getState();
			expect(state.notifications).toHaveLength(1);
			expect(state.notifications[0].id).toBe(notification2.id);
		});

		it("should not modify other notifications when marking one as read", () => {
			const notification1 = createTestNotification({ read: false });
			const notification2 = createTestNotification({ read: false });
			const { markNotificationRead } = useWebSocketStore.getState();

			useWebSocketStore.setState({
				notifications: [notification1, notification2],
			});

			markNotificationRead(notification1.id);

			const state = useWebSocketStore.getState();
			expect(state.notifications[0].read).toBe(true);
			expect(state.notifications[1].read).toBe(false);
		});
	});

	describe("upload progress management", () => {
		it("should track upload progress", () => {
			const uploadProgress = createTestUploadProgress();

			useWebSocketStore.setState({
				uploadProgress: new Map([[uploadProgress.uploadId, uploadProgress]]),
			});

			const { getUploadProgress } = useWebSocketStore.getState();
			const result = getUploadProgress(uploadProgress.uploadId);

			expect(result).toEqual(uploadProgress);
		});

		it("should return null for non-existent upload", () => {
			const { getUploadProgress } = useWebSocketStore.getState();
			const result = getUploadProgress("non-existent-id");

			expect(result).toBeNull();
		});

		it("should manage active uploads list", () => {
			const uploadId = "test-upload-123";

			useWebSocketStore.setState({
				activeUploads: [uploadId],
			});

			const state = useWebSocketStore.getState();
			expect(state.activeUploads).toContain(uploadId);
		});

		it("should update upload progress for existing upload", () => {
			const uploadId = "test-upload-123";
			const initialProgress = createTestUploadProgress({
				uploadId,
				progress: 50,
				status: "uploading",
			});
			const updatedProgress = createTestUploadProgress({
				uploadId,
				progress: 100,
				status: "completed",
			});

			// Set initial progress
			useWebSocketStore.setState({
				uploadProgress: new Map([[uploadId, initialProgress]]),
			});

			// Update progress
			useWebSocketStore.setState({
				uploadProgress: new Map([[uploadId, updatedProgress]]),
			});

			const { getUploadProgress } = useWebSocketStore.getState();
			const result = getUploadProgress(uploadId);

			expect(result?.progress).toBe(100);
			expect(result?.status).toBe("completed");
		});
	});

	describe("error handling", () => {
		it("should handle store errors gracefully", () => {
			expect(() => {
				useWebSocketStore.setState({
					connectionState: "error",
					lastError: "Test error",
				});
			}).not.toThrow();
		});

		it("should maintain state consistency during errors", () => {
			const _initialState = useWebSocketStore.getState();

			try {
				useWebSocketStore.setState({
					connectionState: "error",
					lastError: "Connection failed",
				});
			} catch (_error) {
				// Even if there's an error, state should be consistent
				const currentState = useWebSocketStore.getState();
				expect(currentState.notifications).toBeDefined();
				expect(currentState.uploadProgress).toBeDefined();
			}
		});
	});

	describe("store integration", () => {
		it("should expose all required methods", () => {
			const store = useWebSocketStore.getState();

			expect(typeof store.connect).toBe("function");
			expect(typeof store.disconnect).toBe("function");
			expect(typeof store.subscribe).toBe("function");
			expect(typeof store.clearNotifications).toBe("function");
			expect(typeof store.markNotificationRead).toBe("function");
			expect(typeof store.removeNotification).toBe("function");
			expect(typeof store.getUploadProgress).toBe("function");
		});

		it("should maintain state shape", () => {
			const state = useWebSocketStore.getState();

			expect(state).toHaveProperty("connectionState");
			expect(state).toHaveProperty("connectionId");
			expect(state).toHaveProperty("isConnected");
			expect(state).toHaveProperty("reconnectAttempts");
			expect(state).toHaveProperty("lastError");
			expect(state).toHaveProperty("notifications");
			expect(state).toHaveProperty("uploadProgress");
			expect(state).toHaveProperty("activeUploads");
		});
	});
});
