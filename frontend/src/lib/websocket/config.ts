/**
 * WebSocket Configuration
 *
 * Centralized configuration for WebSocket connections with proper typing and validation.
 */

import { z } from "zod";

// WebSocket configuration schema
const WebSocketConfigSchema = z.object({
	url: z.string().min(1),
	maxReconnectAttempts: z.number().min(1).max(50).default(10),
	reconnectDelay: z.number().min(100).max(10000).default(1000),
	maxReconnectDelay: z.number().min(1000).max(300000).default(30000),
	heartbeatInterval: z.number().min(5000).max(120000).default(30000),
	messageQueueMaxSize: z.number().min(10).max(1000).default(100),
	connectionTimeout: z.number().min(1000).max(30000).default(10000),
	pingTimeout: z.number().min(1000).max(15000).default(5000),
	maxConnectionsPerUser: z.number().min(1).max(10).default(3),
	enableAutoReconnect: z.boolean().default(true),
	enableHeartbeat: z.boolean().default(true),
	enableMessageQueue: z.boolean().default(true),
	enableRateLimiting: z.boolean().default(true),
	rateLimitWindow: z.number().min(1000).max(60000).default(1000), // 1 second window
	rateLimitMaxMessages: z.number().min(1).max(100).default(10), // 10 messages per second
});

export type WebSocketConfig = z.infer<typeof WebSocketConfigSchema>;

// Default configuration
export const DEFAULT_WEBSOCKET_CONFIG: WebSocketConfig = {
	url: "ws://localhost:8000/api/v1/ws",
	maxReconnectAttempts: 10,
	reconnectDelay: 1000,
	maxReconnectDelay: 30000,
	heartbeatInterval: 30000,
	messageQueueMaxSize: 100,
	connectionTimeout: 10000,
	pingTimeout: 5000,
	maxConnectionsPerUser: 3,
	enableAutoReconnect: true,
	enableHeartbeat: true,
	enableMessageQueue: true,
	enableRateLimiting: true,
	rateLimitWindow: 1000,
	rateLimitMaxMessages: 10,
};

// Environment-specific configuration
export function getWebSocketConfig(environment?: string): WebSocketConfig {
	const env = environment || import.meta.env.NODE_ENV || "development";

	const baseConfig = { ...DEFAULT_WEBSOCKET_CONFIG };

	// Override based on environment
	switch (env) {
		case "development":
			return {
				...baseConfig,
				url:
					import.meta.env.VITE_WS_URL ||
					"ws://localhost:8000/api/v1/websocket/ws",
				maxReconnectAttempts: 20, // More attempts in dev
				reconnectDelay: 500, // Faster reconnect in dev
			};

		case "staging":
			return {
				...baseConfig,
				url:
					import.meta.env.VITE_WS_URL || "wss://staging-api.reviewpoint.com/ws",
				maxReconnectAttempts: 15,
				reconnectDelay: 2000,
			};

		case "production":
			return {
				...baseConfig,
				url: import.meta.env.VITE_WS_URL || "wss://api.reviewpoint.com/ws",
				maxReconnectAttempts: 10,
				reconnectDelay: 3000,
				maxReconnectDelay: 60000, // Longer max delay in production
			};

		case "test":
			return {
				...baseConfig,
				url: "ws://localhost:8001/api/v1/websocket/ws",
				enableAutoReconnect: false, // Disable auto-reconnect in tests
				enableHeartbeat: false, // Disable heartbeat in tests
				connectionTimeout: 1000, // Faster timeout in tests
			};

		default:
			return baseConfig;
	}
}

// Validate configuration
export function validateWebSocketConfig(
	config: Partial<WebSocketConfig>,
): WebSocketConfig {
	return WebSocketConfigSchema.parse(config);
}

// Connection states
export type ConnectionState =
	| "disconnected"
	| "connecting"
	| "connected"
	| "reconnecting"
	| "error"
	| "rate_limited"
	| "authentication_failed";

// WebSocket event types (expanded)
export type WebSocketEventType =
	| "connection.established"
	| "connection.lost"
	| "connection.error"
	| "connection.rate_limited"
	| "connection.authentication_failed"
	| "ping"
	| "pong"
	| "subscribe"
	| "unsubscribe"
	| "subscription.acknowledged"
	| "upload.progress"
	| "upload.completed"
	| "upload.error"
	| "upload.cancelled"
	| "review.updated"
	| "review.created"
	| "review.deleted"
	| "system.notification"
	| "system.maintenance"
	| "user.status_changed"
	| "file.processing"
	| "file.ready"
	| "error";

// Message validation schemas
export const WebSocketMessageSchema = z.object({
	type: z.string(),
	data: z.any().optional().default({}),
	timestamp: z.string(),
	id: z.string(),
});

export const WebSocketIncomingMessageSchema = z.object({
	type: z.enum([
		"ping",
		"subscribe",
		"unsubscribe",
		"upload.cancel",
		"heartbeat",
	]),
	data: z.any().optional().default({}),
	timestamp: z.string().optional(),
	id: z.string().optional(),
});

export type WebSocketMessage = z.infer<typeof WebSocketMessageSchema>;
export type WebSocketIncomingMessage = z.infer<
	typeof WebSocketIncomingMessageSchema
>;

// Error types
export interface WebSocketError {
	code: string;
	message: string;
	details?: any;
	timestamp: Date;
	retryable: boolean;
}

// Connection statistics
export interface ConnectionStats {
	state: ConnectionState;
	reconnectAttempts: number;
	queuedMessages: number;
	activeListeners: Array<{
		event: WebSocketEventType;
		count: number;
	}>;
	subscriptions: WebSocketEventType[];
	metadata: {
		connectionId?: string;
		userId?: string;
		connectedAt?: Date;
		lastHeartbeat?: Date;
		lastMessageSent?: Date;
		lastMessageReceived?: Date;
		totalMessagesSent: number;
		totalMessagesReceived: number;
		totalReconnects: number;
		averageLatency?: number;
	};
	rateLimiting: {
		isLimited: boolean;
		messagesInWindow: number;
		windowStart: Date;
		limitResetTime?: Date;
	};
}
