import * as Icons from "lucide-react";
import type React from "react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useWebSocketStore } from "../../lib/store/webSocketStore";
import { getWebSocketConfig } from "../../lib/websocket/config";
import { useWebSocket } from "../../lib/websocket/hooks";
import { webSocketService } from "../../lib/websocket/webSocketService";

interface ConnectionLog {
	id: string;
	timestamp: Date;
	type: "connect" | "disconnect" | "message" | "error" | "heartbeat";
	data: any;
}

interface WebSocketSidebarDebugProps {
	className?: string;
}

export const WebSocketSidebarDebug: React.FC<WebSocketSidebarDebugProps> = ({
	className,
}) => {
	const { connectionState, lastError, connect, disconnect } = useWebSocket();
	const store = useWebSocketStore();
	const [logs, setLogs] = useState<ConnectionLog[]>([]);
	const [showDetails, setShowDetails] = useState(false);
	const [lastMessage, setLastMessage] = useState<any>(null);
	const config = getWebSocketConfig();

	// Log connection events
	useEffect(() => {
		const addLog = (type: ConnectionLog["type"], data: any) => {
			const log: ConnectionLog = {
				id: Date.now().toString(),
				timestamp: new Date(),
				type,
				data,
			};
			setLogs((prev) => [log, ...prev.slice(0, 19)]); // Keep last 20 logs for sidebar
		};

		// Log connection state changes
		addLog("connect", { state: connectionState });

		// Listen to WebSocket events for logging
		const unsubscribes: (() => void)[] = [];

		if (store.isConnected) {
			// Listen to all events for debugging
			const messageHandler = (event: any) => {
				setLastMessage(event);
				addLog("message", event);
			};

			const errorHandler = (error: any) => {
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

	const _getStatusColor = (state: string) => {
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

	const getLogTypeIcon = (type: ConnectionLog["type"]) => {
		switch (type) {
			case "connect":
				return <Icons.Wifi className="h-3 w-3 text-green-600" />;
			case "disconnect":
				return <Icons.WifiOff className="h-3 w-3 text-red-600" />;
			case "message":
				return <Icons.MessageSquare className="h-3 w-3 text-blue-600" />;
			case "error":
				return <Icons.AlertTriangle className="h-3 w-3 text-red-600" />;
			case "heartbeat":
				return <Icons.Heart className="h-3 w-3 text-purple-600" />;
			default:
				return <Icons.Circle className="h-3 w-3 text-muted-foreground" />;
		}
	};

	const getStatusIcon = (state: string) => {
		switch (state) {
			case "connected":
				return <Icons.Wifi className="h-4 w-4 text-green-600" />;
			case "connecting":
				return (
					<Icons.RotateCw className="h-4 w-4 text-yellow-600 animate-spin" />
				);
			case "disconnected":
				return <Icons.WifiOff className="h-4 w-4 text-red-600" />;
			case "reconnecting":
				return (
					<Icons.RotateCw className="h-4 w-4 text-blue-600 animate-spin" />
				);
			default:
				return <Icons.AlertCircle className="h-4 w-4 text-muted-foreground" />;
		}
	};

	return (
		<div className={cn("space-y-3", className)}>
			{/* WebSocket Status Header */}
			<div className="px-3 py-1">
				<h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
					WebSocket Debug
				</h4>
			</div>

			{/* Status Summary */}
			<div className="px-3 py-2 rounded-lg bg-accent/50">
				<div className="flex items-center justify-between">
					<div className="flex items-center space-x-2">
						{getStatusIcon(connectionState)}
						<span className="text-sm font-medium">
							{connectionState.toUpperCase()}
						</span>
					</div>
					<Button
						variant="ghost"
						size="sm"
						onClick={() => setShowDetails(!showDetails)}
						className="h-6 w-6 p-0"
					>
						{showDetails ? (
							<Icons.ChevronUp className="h-3 w-3" />
						) : (
							<Icons.ChevronDown className="h-3 w-3" />
						)}
					</Button>
				</div>

				{lastError && (
					<div className="mt-2 text-xs text-destructive bg-destructive/10 border border-destructive/20 rounded p-2">
						<strong>Error:</strong> {lastError}
					</div>
				)}
			</div>

			{/* Connection Controls */}
			<div className="flex gap-2 px-3">
				<Button
					onClick={connect}
					disabled={
						connectionState === "connected" || connectionState === "connecting"
					}
					size="sm"
					variant="outline"
					className="flex-1 h-7 text-xs"
				>
					<Icons.Play className="h-3 w-3 mr-1" />
					Connect
				</Button>
				<Button
					onClick={disconnect}
					disabled={connectionState === "disconnected"}
					size="sm"
					variant="outline"
					className="flex-1 h-7 text-xs"
				>
					<Icons.Square className="h-3 w-3 mr-1" />
					Stop
				</Button>
			</div>

			{/* Detailed Info (Collapsible) */}
			{showDetails && (
				<div className="space-y-3 px-3">
					{/* Configuration Info */}
					<div className="bg-muted rounded p-2 text-xs space-y-1">
						<div>
							<strong>URL:</strong>{" "}
							<code className="text-muted-foreground break-all">
								{config.url}
							</code>
						</div>
						<div>
							<strong>Heartbeat:</strong> {config.heartbeatInterval}ms
						</div>
						<div>
							<strong>Rate Limit:</strong> {config.rateLimitMaxMessages}/window
						</div>
					</div>

					{/* Last Message */}
					{lastMessage && (
						<div className="bg-muted rounded p-2">
							<div className="text-xs font-medium mb-1">Last Message:</div>
							<pre className="text-xs text-muted-foreground whitespace-pre-wrap break-all max-h-20 overflow-y-auto">
								{JSON.stringify(lastMessage, null, 2)}
							</pre>
						</div>
					)}

					{/* Recent Logs */}
					<div className="space-y-1">
						<div className="flex items-center justify-between">
							<div className="text-xs font-medium">Recent Activity</div>
							<Button
								onClick={() => setLogs([])}
								variant="ghost"
								size="sm"
								className="h-5 w-5 p-0 text-muted-foreground hover:text-foreground"
							>
								<Icons.X className="h-3 w-3" />
							</Button>
						</div>
						<div className="max-h-32 overflow-y-auto space-y-1">
							{logs.length === 0 ? (
								<div className="text-xs text-muted-foreground italic px-2 py-1">
									No activity yet...
								</div>
							) : (
								logs.slice(0, 5).map((log) => (
									<div
										key={log.id}
										className="flex items-start gap-2 text-xs p-2 bg-background rounded border"
									>
										{getLogTypeIcon(log.type)}
										<div className="flex-1 min-w-0">
											<div className="flex items-center gap-1">
												<span className="font-medium capitalize">
													{log.type}
												</span>
												<span className="text-muted-foreground">
													{log.timestamp.toLocaleTimeString("en-US", {
														hour12: false,
														hour: "2-digit",
														minute: "2-digit",
														second: "2-digit",
													})}
												</span>
											</div>
											{typeof log.data === "object" && log.data !== null && (
												<div className="text-muted-foreground truncate">
													{JSON.stringify(log.data).substring(0, 50)}...
												</div>
											)}
										</div>
									</div>
								))
							)}
						</div>
					</div>
				</div>
			)}
		</div>
	);
};
