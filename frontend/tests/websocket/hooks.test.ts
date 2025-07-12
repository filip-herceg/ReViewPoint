/**
 * WebSocket Hooks Tests
 *
 * Tests for the WebSocket React hooks functionality.
 */

import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useWebSocketStore } from "@/lib/store/webSocketStore";
import {
	useWebSocket,
	useWebSocketConnection,
	useWebSocketEvent,
	useWebSocketNotifications,
	useWebSocketUpload,
} from "@/lib/websocket/hooks";
import { webSocketService } from "@/lib/websocket/webSocketService";
import {
	createTestNotification,
	createTestUploadProgress,
} from "../test-templates";
import { testLogger } from "../test-utils";

// Mock the WebSocket store
vi.mock("@/lib/store/webSocketStore", () => ({
	useWebSocketStore: vi.fn(),
}));

// Mock logger
vi.mock("@/logger", () => ({
	default: {
		info: vi.fn(),
		debug: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	},
}));

describe("WebSocket Hooks", () => {
	const mockStore = {
		connectionState: "disconnected" as const,
		isConnected: false,
		lastError: null,
		connect: vi.fn(),
		disconnect: vi.fn(),
		subscribe: vi.fn(),
		notifications: [],
		clearNotifications: vi.fn(),
		markNotificationRead: vi.fn(),
		removeNotification: vi.fn(),
		uploadProgress: new Map(),
		activeUploads: [],
		getUploadProgress: vi.fn(),
	};

	beforeEach(() => {
		// Reset all mocks
		vi.clearAllMocks();

		// Setup default mock store implementation
		(useWebSocketStore as any).mockReturnValue(mockStore);

		testLogger.debug("WebSocket hooks test setup complete");
	});

	afterEach(() => {
		testLogger.debug("WebSocket hooks test cleanup complete");
	});

	describe("useWebSocket", () => {
		it("should return connection state and methods", () => {
			const { result } = renderHook(() => useWebSocket());

			expect(result.current.connectionState).toBe("disconnected");
			expect(result.current.isConnected).toBe(false);
			expect(result.current.lastError).toBeNull();
			expect(typeof result.current.connect).toBe("function");
			expect(typeof result.current.disconnect).toBe("function");
			expect(typeof result.current.subscribe).toBe("function");
		});

		it("should connect on mount when disconnected", () => {
			renderHook(() => useWebSocket());

			expect(mockStore.connect).toHaveBeenCalledOnce();
		});

		it("should not connect if already connected", () => {
			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				connectionState: "connected",
			});

			renderHook(() => useWebSocket());

			expect(mockStore.connect).not.toHaveBeenCalled();
		});

		it("should return connection stats", () => {
			// Override the global mock for this test
			vi.mocked(webSocketService.getStats).mockReturnValue({
				state: "connected",
				reconnectAttempts: 0,
				queuedMessages: 0,
				activeListeners: [],
				subscriptions: [],
				metadata: {
					connectionId: "test-connection-id",
					userId: "test-user-id",
					connectedAt: new Date(),
					lastHeartbeat: new Date(),
					totalMessagesSent: 0,
					totalMessagesReceived: 0,
					totalReconnects: 0,
				},
				rateLimiting: {
					isLimited: false,
					messagesInWindow: 0,
					windowStart: new Date(),
				},
			});

			const { result } = renderHook(() => useWebSocket());

			expect(result.current.stats).toEqual({
				state: "connected",
				reconnectAttempts: 0,
				queuedMessages: 0,
				activeListeners: [],
				subscriptions: [],
				metadata: expect.any(Object),
				rateLimiting: {
					isLimited: false,
					messagesInWindow: 0,
					windowStart: expect.any(Date),
				},
			});
		});
	});

	describe("useWebSocketConnection", () => {
		it("should return connection information", () => {
			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				connectionState: "connected",
				isConnected: true,
				lastError: null,
			});

			const { result } = renderHook(() => useWebSocketConnection());

			expect(result.current.state).toBe("connected");
			expect(result.current.isConnected).toBe(true);
			expect(result.current.error).toBeNull();
			expect(result.current.connectionId).toBe("test-connection-id");
			expect(result.current.userId).toBe("test-user-id");
			expect(typeof result.current.reconnect).toBe("function");
		});

		it("should handle reconnection", () => {
			const { result } = renderHook(() => useWebSocketConnection());

			act(() => {
				result.current.reconnect();
			});

			expect(mockStore.connect).toHaveBeenCalledOnce();
		});

		it("should handle connection error state", () => {
			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				connectionState: "error",
				isConnected: false,
				lastError: "Connection failed",
			});

			const { result } = renderHook(() => useWebSocketConnection());

			expect(result.current.state).toBe("error");
			expect(result.current.isConnected).toBe(false);
			expect(result.current.error).toBe("Connection failed");
		});
	});

	describe("useWebSocketNotifications", () => {
		it("should return notification state and methods", () => {
			const notifications = [
				createTestNotification({ read: false }),
				createTestNotification({ read: true }),
				createTestNotification({ read: false }),
			];

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				notifications,
			});

			const { result } = renderHook(() => useWebSocketNotifications());

			expect(result.current.notifications).toEqual(notifications);
			expect(result.current.unreadCount).toBe(2);
			expect(result.current.hasUnread).toBe(true);
		});

		it("should calculate unread count correctly", () => {
			const notifications = [
				createTestNotification({ read: true }),
				createTestNotification({ read: true }),
				createTestNotification({ read: true }),
			];

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				notifications,
			});

			const { result } = renderHook(() => useWebSocketNotifications());

			expect(result.current.unreadCount).toBe(0);
			expect(result.current.hasUnread).toBe(false);
		});

		it("should mark all notifications as read", () => {
			const notification1 = createTestNotification({ read: false });
			const notification2 = createTestNotification({ read: false });
			const notifications = [notification1, notification2];
			const mockMarkNotificationRead = vi.fn();

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				notifications,
				markNotificationRead: mockMarkNotificationRead,
			});

			const { result } = renderHook(() => useWebSocketNotifications());

			act(() => {
				result.current.markAllRead();
			});

			expect(mockMarkNotificationRead).toHaveBeenCalledTimes(2);
			expect(mockMarkNotificationRead).toHaveBeenCalledWith(notification1.id);
			expect(mockMarkNotificationRead).toHaveBeenCalledWith(notification2.id);
		});

		it("should remove all read notifications", () => {
			const notification1 = createTestNotification({
				read: true,
				persistent: false,
			});
			const notification2 = createTestNotification({ read: false });
			const notification3 = createTestNotification({
				read: true,
				persistent: false,
			});
			const notifications = [notification1, notification2, notification3];
			const mockRemoveNotification = vi.fn();

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				notifications,
				removeNotification: mockRemoveNotification,
			});

			const { result } = renderHook(() => useWebSocketNotifications());

			act(() => {
				result.current.removeAllRead();
			});

			expect(mockRemoveNotification).toHaveBeenCalledTimes(2);
			expect(mockRemoveNotification).toHaveBeenCalledWith(notification1.id);
			expect(mockRemoveNotification).toHaveBeenCalledWith(notification3.id);
		});
	});

	describe("useWebSocketUpload", () => {
		it("should return upload progress", () => {
			const uploadId = "test-upload-123";
			const progressData = createTestUploadProgress({
				uploadId,
				progress: 75,
				status: "uploading",
			});

			const mockGetUploadProgress = vi.fn().mockReturnValue(progressData);
			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				getUploadProgress: mockGetUploadProgress,
			});

			const { result } = renderHook(() => useWebSocketUpload(uploadId));

			expect(result.current.progress).toBe(75); // Hook returns progress.progress, not the full object
			expect(result.current.status).toBe("uploading");
			expect(result.current.isActive).toBe(true);
			expect(mockGetUploadProgress).toHaveBeenCalledWith(uploadId);
		});

		it("should return null for non-existent upload", () => {
			const uploadId = "non-existent-upload";

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				getUploadProgress: vi.fn().mockReturnValue(null),
			});

			const { result } = renderHook(() => useWebSocketUpload(uploadId));

			expect(result.current.progress).toBe(0); // Default when no progress data
			expect(result.current.status).toBe("uploading"); // Default status
			expect(result.current.isActive).toBe(false); // Not active when progress is 0
		});

		it("should subscribe to upload events", () => {
			const uploadId = "test-upload-123";

			// Mock webSocketService.on
			const mockUnsubscribe = vi.fn();
			(webSocketService as any).on = vi.fn().mockReturnValue(mockUnsubscribe);

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				isConnected: true,
			});

			renderHook(() => useWebSocketUpload(uploadId));

			// Should subscribe to upload events
			expect(webSocketService.on).toHaveBeenCalledWith(
				"upload.progress",
				expect.any(Function),
			);
			expect(webSocketService.on).toHaveBeenCalledWith(
				"upload.completed",
				expect.any(Function),
			);
			expect(webSocketService.on).toHaveBeenCalledWith(
				"upload.error",
				expect.any(Function),
			);
		});
	});

	describe("useWebSocketEvent", () => {
		it("should subscribe to specified event", () => {
			const mockHandler = vi.fn();
			const event = "upload.progress";

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				isConnected: true,
			});

			// Mock webSocketService.on
			const mockUnsubscribe = vi.fn();
			(webSocketService as any).on = vi.fn().mockReturnValue(mockUnsubscribe);

			renderHook(() => useWebSocketEvent(event, mockHandler));

			expect(webSocketService.on).toHaveBeenCalledWith(event, mockHandler);
		});

		it("should not subscribe when disconnected", () => {
			const mockHandler = vi.fn();
			const event = "upload.progress";

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				isConnected: false,
			});

			(webSocketService as any).on = vi.fn();

			renderHook(() => useWebSocketEvent(event, mockHandler));

			expect(webSocketService.on).not.toHaveBeenCalled();
		});

		it("should unsubscribe on unmount", () => {
			const mockHandler = vi.fn();
			const event = "upload.progress";
			const mockUnsubscribe = vi.fn();

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				isConnected: true,
			});

			(webSocketService as any).on = vi.fn().mockReturnValue(mockUnsubscribe);

			const { unmount } = renderHook(() =>
				useWebSocketEvent(event, mockHandler),
			);

			unmount();

			expect(mockUnsubscribe).toHaveBeenCalled();
		});
	});

	describe("error handling", () => {
		it("should handle hook errors gracefully", () => {
			(useWebSocketStore as any).mockImplementation(() => {
				throw new Error("Store error");
			});

			expect(() => {
				renderHook(() => useWebSocket());
			}).toThrow("Store error");
		});

		it("should handle missing store methods", () => {
			(useWebSocketStore as any).mockReturnValue({
				connectionState: "disconnected",
				isConnected: false,
				lastError: null,
				connect: vi.fn(), // Provide minimal required methods
				disconnect: vi.fn(),
				subscribe: vi.fn(),
			});

			expect(() => {
				renderHook(() => useWebSocket());
			}).not.toThrow();
		});
	});

	describe("hook integration", () => {
		it("should work together with multiple hooks", () => {
			const notifications = [createTestNotification()];
			const uploadProgress = createTestUploadProgress();

			(useWebSocketStore as any).mockReturnValue({
				...mockStore,
				connectionState: "connected",
				isConnected: true,
				notifications,
				getUploadProgress: vi.fn().mockReturnValue(uploadProgress),
			});

			const { result: connectionResult } = renderHook(() =>
				useWebSocketConnection(),
			);
			const { result: notificationResult } = renderHook(() =>
				useWebSocketNotifications(),
			);
			const { result: uploadResult } = renderHook(() =>
				useWebSocketUpload("test-upload"),
			);

			expect(connectionResult.current.isConnected).toBe(true);
			expect(notificationResult.current.notifications).toEqual(notifications);
			expect(uploadResult.current.progress).toBe(uploadProgress.progress); // Hook returns the numeric progress value
		});
	});
});
