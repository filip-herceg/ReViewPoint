import type React from "react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useWebSocketStore } from "../../lib/store/webSocketStore";
import { getWebSocketConfig } from "../../lib/websocket/config";
import { useWebSocket } from "../../lib/websocket/hooks";
import { webSocketService } from "../../lib/websocket/webSocketService";

interface ConnectionLog {
	id: string;
	timestamp: Date;
	type: "connect" | "disconnect" | "message" | "error" | "heartbeat";
	data: unknown;
}

export const WebSocketDebug: React.FC = () => {
	const { connectionState, lastError, connect, disconnect } = useWebSocket();
	const store = useWebSocketStore();
	const [logs, setLogs] = useState<ConnectionLog[]>([]);
	const [showLogs, setShowLogs] = useState(false);
	const [testMessage, setTestMessage] = useState(
		'{"type": "ping", "data": "test"}',
	);
	const [lastMessage, setLastMessage] = useState<unknown>(null);
	const config = getWebSocketConfig();

	// Log connection events
	useEffect(() => {
		const addLog = (type: ConnectionLog["type"], data: unknown) => {
			const log: ConnectionLog = {
				id: Date.now().toString(),
				timestamp: new Date(),
				type,
				data,
			};
			setLogs((prev) => [log, ...prev.slice(0, 49)]); // Keep last 50 logs
		};

		// Log connection state changes
		addLog("connect", { state: connectionState });

		// Listen to WebSocket events for logging
		const unsubscribes: (() => void)[] = [];

		if (store.isConnected) {
			// Listen to all events for debugging
			const messageHandler = (event: unknown) => {
				setLastMessage(event);
				addLog("message", event);
			};

			const errorHandler = (error: unknown) => {
				addLog("error", error);
			};

			unsubscribes.push(
				webSocketService.on("connection.established", messageHandler),
				webSocketService.on("upload.progress", messageHandler),
				webSocketService.on("upload.completed", messageHandler),
				webSocketService.on("upload.error", messageHandler),
				webSocketService.on("system.notification", messageHandler),
				webSocketService.on("pong", messageHandler),
				webSocketService.on("error", errorHandler),
			);
		}

		return () => {
			unsubscribes.forEach((fn) => fn());
		};
	}, [connectionState, store.isConnected]);

	const handleSendTestMessage = () => {
		try {
			const message = JSON.parse(testMessage);
			// Use webSocketService.send directly since it's not exposed in hooks
			if (store.isConnected) {
				// For now, just log the attempt since we don't have direct send access
				console.log("Would send message:", message);
				addLog("message", { type: "outgoing", data: message });
			}
		} catch (e) {
			console.error("Invalid JSON:", e);
		}
	};

	const addLog = (type: ConnectionLog["type"], data: unknown) => {
		const log: ConnectionLog = {
			id: Date.now().toString(),
			timestamp: new Date(),
			type,
			data,
		};
		setLogs((prev) => [log, ...prev.slice(0, 49)]); // Keep last 50 logs
	};

	const getStatusColor = (state: string) => {
		switch (state) {
			case "connected":
				return "text-green-600 bg-green-50 border-green-200";
			case "connecting":
				return "text-yellow-600 bg-yellow-50 border-yellow-200";
			case "disconnected":
				return "text-red-600 bg-red-50 border-red-200";
			case "reconnecting":
				return "text-blue-600 bg-blue-50 border-blue-200";
			default:
				return "text-muted-foreground bg-muted border-border";
		}
	};

	const getLogTypeColor = (type: ConnectionLog["type"]) => {
		switch (type) {
			case "connect":
				return "text-green-600 bg-green-50";
			case "disconnect":
				return "text-red-600 bg-red-50";
			case "message":
				return "text-blue-600 bg-blue-50";
			case "error":
				return "text-red-600 bg-red-100";
			case "heartbeat":
				return "text-purple-600 bg-purple-50";
			default:
				return "text-muted-foreground bg-muted";
		}
	};

	return (
		<div className="fixed bottom-4 right-4 w-96 bg-background border border-border rounded-lg shadow-lg p-4 z-50">
			<div className="flex items-center justify-between mb-4">
				<h3 className="text-lg font-semibold text-foreground">
					WebSocket Debug
				</h3>
				<Button
					type="button"
					onClick={() => setShowLogs(!showLogs)}
					variant="secondary"
					size="sm"
				>
					{showLogs ? "Hide Logs" : "Show Logs"}
				</Button>
			</div>

			{/* Connection Status */}
			<div className="mb-4">
				<div className="flex items-center gap-2 mb-2">
					<span className="text-sm font-medium text-foreground">Status:</span>
					<span
						className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(connectionState)}`}
					>
						{connectionState.toUpperCase()}
					</span>
				</div>

				{lastError && (
					<div className="text-xs text-destructive bg-destructive/10 border border-destructive/20 rounded p-2 mb-2">
						<strong>Error:</strong> {lastError}
					</div>
				)}
			</div>

			{/* Configuration Info */}
			<div className="mb-4 text-xs">
				<div className="bg-muted rounded p-2 space-y-1">
					<div>
						<strong>URL:</strong>{" "}
						<code className="text-muted-foreground">{config.url}</code>
					</div>
					<div>
						<strong>Max Reconnects:</strong> {config.maxReconnectAttempts}
					</div>
					<div>
						<strong>Heartbeat:</strong> {config.heartbeatInterval}ms
					</div>
					<div>
						<strong>Rate Limit:</strong> {config.rateLimitMaxMessages}/window
					</div>
				</div>
			</div>

			{/* Connection Controls */}
			<div className="flex gap-2 mb-4">
				<Button
					type="button"
					onClick={connect}
					disabled={
						connectionState === "connected" || connectionState === "connecting"
					}
					variant="default"
					size="sm"
					className="flex-1"
				>
					Connect
				</Button>
				<Button
					type="button"
					onClick={disconnect}
					disabled={connectionState === "disconnected"}
					variant="destructive"
					size="sm"
					className="flex-1"
				>
					Disconnect
				</Button>
			</div>

			{/* Test Message */}
			<div className="mb-4">
				<label
					htmlFor="test-message-input"
					className="block text-xs font-medium text-foreground mb-1"
				>
					Test Message:
				</label>
				<div className="flex gap-2">
					<input
						id="test-message-input"
						type="text"
						value={testMessage}
						onChange={(e) => setTestMessage(e.target.value)}
						className="flex-1 px-2 py-1 text-xs border border-input bg-background text-foreground rounded focus:outline-none focus:ring-2 focus:ring-ring"
						placeholder="JSON message"
					/>
					<Button
						type="button"
						onClick={handleSendTestMessage}
						disabled={connectionState !== "connected"}
						variant="secondary"
						size="sm"
					>
						Send
					</Button>
				</div>
			</div>
			{/* Last Message */}
			{lastMessage && (
				<div className="mb-4">
					<div className="block text-xs font-medium text-foreground mb-1">
						Last Message:
					</div>
					<div className="bg-muted rounded p-2 text-xs">
						<pre className="text-muted-foreground whitespace-pre-wrap break-all">
							{typeof lastMessage === "string"
								? lastMessage
								: JSON.stringify(lastMessage, null, 2)}
						</pre>
					</div>
				</div>
			)}

			{/* Connection Logs */}
			{showLogs && (
				<div className="border-t border-border pt-4">
					<div className="flex items-center justify-between mb-2">
						<h4 className="text-sm font-medium text-foreground">
							Connection Logs
						</h4>
						<Button
							type="button"
							onClick={() => setLogs([])}
							variant="ghost"
							size="sm"
							className="text-xs"
						>
							Clear
						</Button>
					</div>
					<div className="max-h-48 overflow-y-auto space-y-1">
						{logs.length === 0 ? (
							<div className="text-xs text-muted-foreground italic">
								No logs yet...
							</div>
						) : (
							logs.map((log) => (
								<div
									key={log.id}
									className="text-xs border border-border rounded p-2"
								>
									<div className="flex items-center gap-2 mb-1">
										<span
											className={`px-1 py-0.5 rounded text-xs font-medium ${getLogTypeColor(log.type)}`}
										>
											{log.type}
										</span>
										<span className="text-muted-foreground">
											{log.timestamp.toLocaleTimeString()}
										</span>
									</div>
									<pre className="text-muted-foreground whitespace-pre-wrap break-all">
										{typeof log.data === "object"
											? JSON.stringify(log.data, null, 2)
											: String(log.data)}
									</pre>
								</div>
							))
						)}
					</div>
				</div>
			)}
		</div>
	);
};
