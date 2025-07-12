// Utility: Simulate an error boundary for testing error handling in components

import * as React from "react";
import { getErrorMessage } from "@/lib/utils/errorHandling";

export function renderWithErrorBoundary(
	ui: React.ReactElement,
	onError?: (error: Error) => void,
) {
	class TestErrorBoundary extends React.Component<
		{ children: React.ReactNode },
		{ error: Error | null }
	> {
		constructor(props: { children: React.ReactNode }) {
			super(props);
			this.state = { error: null };
		}
		static getDerivedStateFromError(error: Error) {
			return { error };
		}
		componentDidCatch(error: Error) {
			if (onError) onError(error);
		}
		render(): React.ReactNode {
			if (this.state.error) {
				// Use JSX with explicit React import for TS/JSX support
				return React.createElement(
					"div",
					{ "data-testid": "test-error-boundary" },
					`Error: ${getErrorMessage(this.state.error)}`,
				);
			}
			return this.props.children;
		}
	}
	// Use customRender to ensure consistent provider usage in tests
	return customRender(React.createElement(TestErrorBoundary, null, ui));
}
// Logging utilities for tests with levels: debug, info, warn, error
type LogLevel = "debug" | "info" | "warn" | "error";
const LOG_PREFIX = "[TEST-LOG]";

function log(level: LogLevel, ...args: any[]) {
	const time = new Date().toISOString();
	switch (level) {
		case "debug":
			if (process.env.TEST_LOG_LEVEL === "debug") {
				// eslint-disable-next-line no-console
				console.debug(`${LOG_PREFIX} [${level}] [${time}]`, ...args);
			}
			break;
		case "info":
			// eslint-disable-next-line no-console
			console.info(`${LOG_PREFIX} [${level}] [${time}]`, ...args);
			break;
		case "warn":
			// eslint-disable-next-line no-console
			console.warn(`${LOG_PREFIX} [${level}] [${time}]`, ...args);
			break;
		case "error":
			// eslint-disable-next-line no-console
			console.error(`${LOG_PREFIX} [${level}] [${time}]`, ...args);
			break;
	}
}

export const testLogger = {
	debug: (...args: any[]) => log("debug", ...args),
	info: (...args: any[]) => log("info", ...args),
	warn: (...args: any[]) => log("warn", ...args),
	error: (...args: any[]) => log("error", ...args),
};

// Centralized test utilities for frontend tests
// Add more helpers as needed for your project

import { render } from "@testing-library/react";
import type { ReactElement } from "react";

// Example: Custom render with providers (expand as needed)
export function customRender(ui: ReactElement, options = {}) {
	testLogger.info("Rendering component with customRender", { ui, options });
	// You can wrap with context providers here if needed
	const result = render(ui, { ...options });
	testLogger.debug("customRender result:", result);
	return result;
}

// Utility: Generate a random string of given length
export function randomString(length: number): string {
	const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
	let result = "";
	for (let i = 0; i < length; i++) {
		result += chars.charAt(Math.floor(Math.random() * chars.length));
	}
	if (length < 4) {
		testLogger.warn("Generated very short random string:", result);
	} else {
		testLogger.debug("Generated random string:", result);
	}
	return result;
}

// Utility: Generate a random integer between min and max (inclusive)
export function randomInt(min: number, max: number): number {
	const value = Math.floor(Math.random() * (max - min + 1)) + min;
	if (min > max) {
		testLogger.error("randomInt called with min > max", { min, max });
	} else if (max - min > 1000000) {
		testLogger.warn("randomInt called with very large range", { min, max });
	} else {
		testLogger.debug(`Generated random int between ${min} and ${max}:`, value);
	}
	return value;
}

// Utility: Pick a random upload status
export function randomStatus(): "pending" | "completed" | "failed";
export function randomStatus<T extends readonly string[]>(
	options: T,
): T[number];
export function randomStatus<T extends readonly string[]>(
	options?: T,
): T[number] | "pending" | "completed" | "failed" {
	const defaultStatuses = ["pending", "completed", "failed"] as const;
	const statuses = options || defaultStatuses;
	const status = statuses[randomInt(0, statuses.length - 1)];

	if (status === "failed" || status === "error") {
		testLogger.warn("Picked random status:", status);
	} else {
		testLogger.debug("Picked random status:", status);
	}
	return status;
}

// Utility: Generate a random ISO date string
export function randomDate(): string {
	const now = Date.now();
	const offset = randomInt(-1000000000, 0); // up to ~11 days ago
	const date = new Date(now + offset).toISOString();
	if (offset < -900000000) {
		testLogger.info("Generated random date far in the past:", date);
	} else {
		testLogger.debug("Generated random date:", date);
	}
	return date;
}

// Utility: Generate a random ISO date string with specific day offset
export function randomDateWithOffset(daysOffset: number = 0): string {
	const now = Date.now();
	const dayInMs = 24 * 60 * 60 * 1000;
	const offset = daysOffset * dayInMs;
	const date = new Date(now + offset).toISOString();

	if (Math.abs(daysOffset) > 7) {
		testLogger.info(
			`Generated random date with ${daysOffset} days offset:`,
			date,
		);
	} else {
		testLogger.debug(
			`Generated random date with ${daysOffset} days offset:`,
			date,
		);
	}
	return date;
}

// Utility: Deep clone an object (for test isolation)
export function deepClone<T>(obj: T): T {
	const clone = JSON.parse(JSON.stringify(obj));
	if (Array.isArray(obj) && obj.length > 100) {
		testLogger.warn("Deep cloned large array object:", { length: obj.length });
	} else if (
		typeof obj === "object" &&
		obj !== null &&
		Object.keys(obj).length > 20
	) {
		testLogger.warn("Deep cloned large object:", {
			keys: Object.keys(obj).length,
		});
	} else {
		testLogger.debug("Deep cloned object:", clone);
	}
	return clone;
}

// Utility: Merge two objects (shallow)
export function merge<T, U>(a: T, b: U): T & U {
	const merged = { ...a, ...b };
	if (typeof b === "object" && b !== null && Object.keys(b).length === 0) {
		testLogger.info("merge called with empty object for b");
	} else if (
		typeof merged === "object" &&
		merged !== null &&
		Object.keys(merged).length > 20
	) {
		testLogger.warn("Merged object has many keys:", Object.keys(merged).length);
	} else {
		testLogger.debug("Merged objects:", merged);
	}
	return merged;
}
