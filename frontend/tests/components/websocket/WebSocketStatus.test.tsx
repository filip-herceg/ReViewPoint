/**
 * WebSocket Status Component Tests
 *
 * Tests for the WebSocket status display component.
 */

import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	WebSocketIndicator,
	WebSocketStatus,
} from "@/components/websocket/WebSocketStatus";
import { useWebSocketConnection } from "@/lib/websocket/hooks";

// Mock the WebSocket hooks
vi.mock("@/lib/websocket/hooks", () => ({
	useWebSocketConnection: vi.fn(),
}));

// Mock Lucide React icons
vi.mock("lucide-react", () => ({
	WifiIcon: ({ className }: { className?: string }) => (
		<div data-testid="wifi-icon" className={className} />
	),
	WifiOffIcon: ({ className }: { className?: string }) => (
		<div data-testid="wifi-off-icon" className={className} />
	),
	LoaderIcon: ({ className }: { className?: string }) => (
		<div data-testid="loader-icon" className={className} />
	),
	AlertTriangleIcon: ({ className }: { className?: string }) => (
		<div data-testid="alert-triangle-icon" className={className} />
	),
	RefreshCwIcon: ({ className }: { className?: string }) => (
		<div data-testid="refresh-icon" className={className} />
	),
}));

describe("WebSocketStatus", () => {
	const mockConnectionData = {
		state: "connected" as const,
		isConnected: true,
		error: null,
		connectionId: "test-connection-123",
		userId: "user-456",
		connectedAt: new Date("2023-01-01T10:00:00Z"),
		lastHeartbeat: new Date("2023-01-01T10:05:00Z"),
		reconnect: vi.fn(),
	};

	beforeEach(() => {
		vi.clearAllMocks();
		(useWebSocketConnection as ReturnType<typeof vi.fn>).mockReturnValue(
			mockConnectionData,
		);
	});

	describe("connection states", () => {
		it("should display connected state", () => {
			render(<WebSocketStatus />);

			expect(screen.getByText("Connected")).toBeInTheDocument();
			expect(screen.getByText("Real-time updates active")).toBeInTheDocument();
			expect(screen.getByTestId("wifi-icon")).toBeInTheDocument();
		});

		it("should display connecting state", () => {
			(useWebSocketConnection as unknown).mockReturnValue({
				...mockConnectionData,
				state: "connecting",
				isConnected: false,
			});

			render(<WebSocketStatus />);

			expect(screen.getByText("Connecting")).toBeInTheDocument();
			expect(
				screen.getByText("Establishing connection..."),
			).toBeInTheDocument();
			expect(screen.getByTestId("loader-icon")).toBeInTheDocument();
		});

		it("should display disconnected state", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "disconnected",
				isConnected: false,
			});

			render(<WebSocketStatus />);

			expect(screen.getByText("Disconnected")).toBeInTheDocument();
			expect(
				screen.getByText("Real-time updates unavailable"),
			).toBeInTheDocument();
			expect(screen.getByTestId("wifi-off-icon")).toBeInTheDocument();
		});

		it("should display error state with reconnect button", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "error",
				isConnected: false,
				error: "Connection failed",
			});

			render(<WebSocketStatus />);

			expect(screen.getByText("Error")).toBeInTheDocument();
			expect(
				screen.getByText("Connection error: Connection failed"),
			).toBeInTheDocument();
			expect(screen.getAllByTestId("alert-triangle-icon")).toHaveLength(2); // One in status, one in alert
			expect(
				screen.getByRole("button", { name: /reconnect/i }),
			).toBeInTheDocument();
		});

		it("should display reconnecting state", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "reconnecting",
				isConnected: false,
			});

			render(<WebSocketStatus />);

			expect(screen.getByText("Reconnecting")).toBeInTheDocument();
			expect(
				screen.getByText("Attempting to reconnect..."),
			).toBeInTheDocument();
			expect(screen.getByTestId("loader-icon")).toBeInTheDocument();
		});
	});

	describe("interaction", () => {
		it("should call reconnect when reconnect button is clicked", () => {
			const mockReconnect = vi.fn();
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "error",
				isConnected: false,
				error: "Connection failed",
				reconnect: mockReconnect,
			});

			render(<WebSocketStatus />);

			const reconnectButton = screen.getByRole("button", {
				name: /reconnect/i,
			});
			fireEvent.click(reconnectButton);

			expect(mockReconnect).toHaveBeenCalledOnce();
		});

		it("should show reconnect button when disconnected", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "disconnected",
				isConnected: false,
			});

			render(<WebSocketStatus />);

			expect(
				screen.getByRole("button", { name: /reconnect/i }),
			).toBeInTheDocument();
		});

		it("should not show reconnect button when connected", () => {
			render(<WebSocketStatus />);

			expect(
				screen.queryByRole("button", { name: /reconnect/i }),
			).not.toBeInTheDocument();
		});
	});

	describe("details display", () => {
		it("should show connection details when showDetails is true", () => {
			render(<WebSocketStatus showDetails />);

			expect(screen.getByText("Connection ID:")).toBeInTheDocument();
			expect(
				screen.getByText(`${"test-connection-123".slice(0, 8)}...`),
			).toBeInTheDocument();
			expect(screen.getByText("Connected:")).toBeInTheDocument();
		});

		it("should not show connection details when showDetails is false", () => {
			render(<WebSocketStatus showDetails={false} />);

			expect(screen.queryByText("Connection ID:")).not.toBeInTheDocument();
			expect(screen.queryByText("Connected:")).not.toBeInTheDocument();
		});

		it("should not show details when disconnected", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "disconnected",
				isConnected: false,
			});

			render(<WebSocketStatus showDetails />);

			expect(screen.queryByText("Connection ID:")).not.toBeInTheDocument();
		});
	});

	describe("inline mode", () => {
		it("should render inline version when inline is true", () => {
			render(<WebSocketStatus inline />);

			// Should be more compact
			expect(screen.getByText("Connected")).toBeInTheDocument();
			expect(screen.getByTestId("wifi-icon")).toBeInTheDocument();
		});

		it("should render full version when inline is false", () => {
			render(<WebSocketStatus inline={false} />);

			expect(screen.getByText("Real-time Connection")).toBeInTheDocument();
			expect(screen.getByText("Real-time updates active")).toBeInTheDocument();
		});
	});

	describe("error handling", () => {
		it("should handle missing connection data gracefully", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				state: "disconnected",
				isConnected: false,
				error: null,
				connectionId: undefined,
				userId: undefined,
				connectedAt: undefined,
				lastHeartbeat: undefined,
				reconnect: vi.fn(),
			});

			expect(() => {
				render(<WebSocketStatus />);
			}).not.toThrow();
		});

		it("should handle null error gracefully", () => {
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				error: null,
			});

			expect(() => {
				render(<WebSocketStatus />);
			}).not.toThrow();
		});
	});

	describe("styling", () => {
		it("should apply custom className", () => {
			const { container } = render(
				<WebSocketStatus className="custom-class" />,
			);

			expect(container.firstChild).toHaveClass("custom-class");
		});

		it("should apply appropriate color classes for different states", () => {
			// Test connected state - use cleanup to avoid DOM conflicts
			const { unmount: unmount1 } = render(<WebSocketStatus />);
			expect(screen.getByTestId("wifi-icon")).toHaveClass("text-success");
			unmount1();

			// Test error state
			(useWebSocketConnection as jest.Mock).mockReturnValue({
				...mockConnectionData,
				state: "error",
				isConnected: false,
				error: "Connection failed",
			});

			const { unmount: unmount2 } = render(<WebSocketStatus />);
			const alertIcons = screen.getAllByTestId("alert-triangle-icon");
			expect(alertIcons[0]).toHaveClass("text-destructive"); // Status icon
			unmount2();
		});
	});
});

describe("WebSocketIndicator", () => {
	const mockConnectionData = {
		state: "connected" as const,
		isConnected: true,
		error: null,
		connectionId: "test-connection-123",
		userId: "user-456",
		connectedAt: new Date("2023-01-01T10:00:00Z"),
		lastHeartbeat: new Date("2023-01-01T10:05:00Z"),
		reconnect: vi.fn(),
	};

	beforeEach(() => {
		vi.clearAllMocks();
		(useWebSocketConnection as jest.Mock).mockReturnValue(mockConnectionData);
	});

	it("should render connection indicator", () => {
		render(<WebSocketIndicator />);

		expect(screen.getByText("Live")).toBeInTheDocument();
		expect(screen.getByTitle("WebSocket: connected")).toBeInTheDocument();
	});

	it("should show disconnected icon when not connected", () => {
		(useWebSocketConnection as jest.Mock).mockReturnValue({
			...mockConnectionData,
			state: "disconnected",
			isConnected: false,
		});

		render(<WebSocketIndicator />);

		expect(screen.getByText("Offline")).toBeInTheDocument();
		expect(screen.getByTitle("WebSocket: disconnected")).toBeInTheDocument();
	});

	it("should apply custom className", () => {
		const { container } = render(
			<WebSocketIndicator className="custom-indicator" />,
		);

		expect(container.firstChild).toHaveClass("custom-indicator");
	});

	it("should be more compact than full status", () => {
		render(<WebSocketIndicator />);

		// Should not show detailed text
		expect(screen.queryByText("Real-time Connection")).not.toBeInTheDocument();
		expect(
			screen.queryByText("Real-time updates active"),
		).not.toBeInTheDocument();
	});
});
