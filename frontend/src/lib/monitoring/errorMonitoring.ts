/**
 * Enhanced Error Monitoring System
 * Centralized error tracking, reporting, and user feedback
 */

import React, { type ErrorInfo, type ReactNode } from "react";
import {
	type FallbackProps,
	ErrorBoundary as ReactErrorBoundary,
} from "react-error-boundary";
import {
	getEnvironmentConfig,
	getMonitoringConfig,
} from "@/lib/config/environment";
import { isFeatureEnabled } from "@/lib/config/featureFlags";
import logger from "@/logger";

export interface ErrorReport {
	id: string;
	timestamp: Date;
	message: string;
	stack?: string;
	componentStack?: string;
	errorBoundary?: string;
	props?: Record<string, unknown>;
	userAgent: string;
	url: string;
	userId?: string;
	severity: "low" | "medium" | "high" | "critical";
	context?: Record<string, unknown>;
}

export interface ErrorMonitoringConfig {
	enableConsoleTracking: boolean;
	enableUnhandledRejections: boolean;
	enableComponentErrors: boolean;
	enableUserFeedback: boolean;
	maxErrors: number;
	reportToSentry: boolean;
}

/**
 * Error monitoring service
 */
class ErrorMonitoringService {
	private errors: ErrorReport[] = [];
	private config: ErrorMonitoringConfig | null = null;
	private isInitialized = false;
	private originalConsole: {
		error: typeof console.error;
		warn: typeof console.warn;
		log: typeof console.log;
		debug: typeof console.debug;
	} | null = null;

	/**
	 * Load configuration (called during initialize)
	 */
	private loadConfig(): ErrorMonitoringConfig {
		if (this.config) {
			return this.config;
		}

		try {
			const monitoringConfig = getMonitoringConfig();
			const env = getEnvironmentConfig();

			this.config = {
				enableConsoleTracking: isFeatureEnabled("enableErrorReporting"),
				enableUnhandledRejections: isFeatureEnabled("enableErrorReporting"),
				enableComponentErrors: isFeatureEnabled("enableErrorReporting"),
				enableUserFeedback: isFeatureEnabled("enableErrorReporting"),
				maxErrors: 100,
				reportToSentry:
					!!monitoringConfig.sentryDsn && env.NODE_ENV === "production",
			};

			return this.config;
		} catch (error) {
			// Use console.log to avoid potential recursion
			console.log("[ERROR] Failed to load error monitoring config", error);
			// Return default config as fallback
			return {
				enableConsoleTracking: false,
				enableUnhandledRejections: false,
				enableComponentErrors: false,
				enableUserFeedback: false,
				maxErrors: 100,
				reportToSentry: false,
			};
		}
	}

	/**
	 * Initialize error monitoring
	 */
	initialize(): void {
		if (this.isInitialized) {
			logger.warn("Error monitoring already initialized");
			return;
		}

		try {
			const config = this.loadConfig();

			if (config.enableConsoleTracking) {
				this.setupConsoleErrorTracking();
			}

			if (config.enableUnhandledRejections) {
				this.setupUnhandledRejectionTracking();
			}

			this.isInitialized = true;
			logger.info("Error monitoring initialized successfully", config);
		} catch (error) {
			// Use console.log to avoid potential recursion
			console.log("[ERROR] Failed to initialize error monitoring", error);
		}
	}

	/**
	 * Reset error monitoring (for testing purposes)
	 */
	reset(): void {
		// Restore original console methods if they were overridden
		if (this.originalConsole) {
			console.error = this.originalConsole.error;
			console.warn = this.originalConsole.warn;
			this.originalConsole = null;
		}

		this.isInitialized = false;
		this.config = null;
		this.errors = [];
		logger.debug("Error monitoring reset");
	}

	/**
	 * Reinitialize error monitoring (useful after configuration changes)
	 */
	reinitialize(): void {
		logger.debug("Reinitializing error monitoring...");
		this.reset();
		this.initialize();
	}

	/**
	 * Setup console error tracking
	 */
	private setupConsoleErrorTracking(): void {
		const originalError = console.error;
		const originalWarn = console.warn;

		// Store references to original console methods for internal use
		this.originalConsole = {
			error: originalError,
			warn: originalWarn,
			log: console.log,
			debug: console.debug,
		};

		console.error = (...args: unknown[]) => {
			const message = args.join(" ");

			// Don't capture expected warnings as errors, even if logged as errors
			if (!this.isExpectedWarning(message)) {
				this.captureError(new Error(message), {
					source: "console.error",
					args,
					severity: "high",
				});
			}

			originalError.apply(console, args);
		};

		console.warn = (...args: unknown[]) => {
			const message = args.join(" ");

			// Don't capture expected warnings as errors
			if (!this.isExpectedWarning(message)) {
				this.captureError(new Error(message), {
					source: "console.warn",
					args,
					severity: "medium",
				});
			} else {
				// Use original console to log that we're filtering this warning
				if (this.originalConsole) {
					this.originalConsole.debug(
						"[DEBUG] Filtered expected warning:",
						message,
					);
				}
			}

			originalWarn.apply(console, args);
		};

		logger.debug("Console error tracking setup complete");
	} /**
	 * Setup unhandled rejection tracking
	 */
	private setupUnhandledRejectionTracking(): void {
		window.addEventListener("unhandledrejection", (event) => {
			// Ignore source map related errors
			if (this.isSourceMapError(event.reason)) {
				return;
			}

			// Check if this is an expected warning
			const reasonString =
				typeof event.reason === "string" ? event.reason : String(event.reason);
			if (this.isExpectedWarning(reasonString)) {
				return;
			}

			this.captureError(
				new Error(`Unhandled promise rejection: ${event.reason}`),
				{
					source: "unhandledrejection",
					reason: event.reason,
					severity: "critical",
				},
			);
		});

		window.addEventListener("error", (event) => {
			// Ignore source map related errors
			if (
				this.isSourceMapError(event.error) ||
				this.isSourceMapError(event.message)
			) {
				return;
			}

			// Check if this is an expected warning
			if (this.isExpectedWarning(event.message)) {
				return;
			}

			this.captureError(event.error || new Error(event.message), {
				source: "window.error",
				filename: event.filename,
				lineno: event.lineno,
				colno: event.colno,
				severity: "high",
			});
		});

		logger.debug("Unhandled rejection tracking setup complete");
	}

	/**
	 * Check if error is related to source maps
	 */
	private isSourceMapError(error: any): boolean {
		if (!error) return false;

		const errorString = typeof error === "string" ? error : error.toString();
		const sourceMapIndicators = [
			"installHook.js.map",
			"Source-Map-Fehler",
			"JSON.parse: unexpected character",
			"sourcemap",
			".map",
		];

		return sourceMapIndicators.some((indicator) =>
			errorString.toLowerCase().includes(indicator.toLowerCase()),
		);
	}

	/**
	 * Check if this is an expected warning that shouldn't be captured as an error
	 */
	private isExpectedWarning(message: string): boolean {
		const expectedWarnings = [
			"Cannot connect - not authenticated",
			"WebSocket connection failed - not authenticated",
			"Authentication required for WebSocket connection",
			"User not authenticated",
			"No auth token available",
			"[WebSocket] Cannot connect - not authenticated", // Handle prefixed format
			"WebSocket] Cannot connect - not authenticated", // Handle cases where [ might be missing
		];

		return expectedWarnings.some((warning) =>
			message.toLowerCase().includes(warning.toLowerCase()),
		);
	}

	/**
	 * Capture and process an error
	 */
	captureError(
		error: Error,
		context: {
			source?: string;
			severity?: ErrorReport["severity"];
			componentStack?: string;
			errorBoundary?: string;
			props?: Record<string, unknown>;
			userId?: string;
			[key: string]: unknown;
		} = {},
	): ErrorReport {
		try {
			const errorReport: ErrorReport = {
				id: this.generateErrorId(),
				timestamp: new Date(),
				message: error.message || "Unknown error",
				stack: error.stack,
				componentStack: context.componentStack,
				errorBoundary: context.errorBoundary,
				props: context.props,
				userAgent: navigator.userAgent,
				url: window.location.href,
				userId: context.userId,
				severity: context.severity || "medium",
				context: {
					...context,
					environment: getEnvironmentConfig().NODE_ENV,
				},
			};

			this.storeError(errorReport);
			this.reportError(errorReport);

			// Use original console to avoid recursion loop
			if (this.originalConsole) {
				this.originalConsole.error("[ERROR] Error captured and processed", {
					id: errorReport.id,
					message: errorReport.message,
					severity: errorReport.severity,
					source: context.source,
				});
			} else {
				// Fallback if originalConsole not available (shouldn't happen)
				console.log("[ERROR] Error captured and processed", {
					id: errorReport.id,
					message: errorReport.message,
					severity: errorReport.severity,
					source: context.source,
				});
			}

			return errorReport;
		} catch (processingError) {
			// Use original console to avoid recursion loop
			if (this.originalConsole) {
				this.originalConsole.error(
					"[ERROR] Failed to process error",
					processingError,
				);
			} else {
				console.log("[ERROR] Failed to process error", processingError);
			}
			throw processingError;
		}
	}

	/**
	 * Store error locally
	 */
	private storeError(errorReport: ErrorReport): void {
		this.errors.unshift(errorReport);

		// Limit stored errors
		const config = this.loadConfig();
		if (this.errors.length > config.maxErrors) {
			this.errors = this.errors.slice(0, config.maxErrors);
		}

		// Store in localStorage for persistence
		try {
			const storedErrors = this.errors.slice(0, 10); // Only store last 10 errors
			localStorage.setItem("errorReports", JSON.stringify(storedErrors));
		} catch (error) {
			// Use original console to avoid recursion
			if (this.originalConsole) {
				this.originalConsole.warn(
					"[WARN] Failed to store errors in localStorage",
					error,
				);
			} else {
				console.log("[WARN] Failed to store errors in localStorage", error);
			}
		}
	}

	/**
	 * Report error to external services
	 */
	private reportError(errorReport: ErrorReport): void {
		const config = this.loadConfig();
		if (
			config.reportToSentry &&
			typeof window !== "undefined" &&
			window.Sentry
		) {
			try {
				window.Sentry.captureException(new Error(errorReport.message), {
					extra: errorReport.context,
					tags: {
						severity: errorReport.severity,
						errorBoundary: errorReport.errorBoundary,
					},
				});
			} catch (error) {
				// Use original console to avoid recursion
				if (this.originalConsole) {
					this.originalConsole.warn(
						"[WARN] Failed to report error to Sentry",
						error,
					);
				} else {
					console.log("[WARN] Failed to report error to Sentry", error);
				}
			}
		}
	}

	/**
	 * Generate unique error ID
	 */
	private generateErrorId(): string {
		return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
	}

	/**
	 * Get all stored errors
	 */
	getErrors(): ErrorReport[] {
		return [...this.errors];
	}

	/**
	 * Get errors by severity
	 */
	getErrorsBySeverity(severity: ErrorReport["severity"]): ErrorReport[] {
		return this.errors.filter((error) => error.severity === severity);
	}

	/**
	 * Clear all errors
	 */
	clearErrors(): void {
		this.errors = [];
		try {
			localStorage.removeItem("errorReports");
		} catch (error) {
			// Use original console to avoid recursion
			if (this.originalConsole) {
				this.originalConsole.warn(
					"[WARN] Failed to clear errors from localStorage",
					error,
				);
			} else {
				console.log("[WARN] Failed to clear errors from localStorage", error);
			}
		}
		logger.info("All errors cleared");
	}

	/**
	 * Get error statistics
	 */
	getErrorStats(): {
		total: number;
		bySeverity: Record<ErrorReport["severity"], number>;
		recent: number;
	} {
		const now = Date.now();
		const oneHourAgo = now - 60 * 60 * 1000;

		const bySeverity = this.errors.reduce(
			(acc, error) => {
				acc[error.severity] = (acc[error.severity] || 0) + 1;
				return acc;
			},
			{} as Record<ErrorReport["severity"], number>,
		);

		const recent = this.errors.filter(
			(error) => error.timestamp.getTime() > oneHourAgo,
		).length;

		return {
			total: this.errors.length,
			bySeverity,
			recent,
		};
	}
}

// Singleton error monitoring service
export const errorMonitoringService = new ErrorMonitoringService();

/**
 * Error fallback component factory
 */
export function createErrorFallback() {
	return function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
		React.useEffect(() => {
			errorMonitoringService.captureError(error, {
				source: "ErrorFallback",
				severity: "high",
			});
		}, [error]);

		return React.createElement(
			"div",
			{
				className:
					"error-fallback p-6 bg-red-50 border border-red-200 rounded-lg",
			},
			React.createElement(
				"h2",
				{ className: "text-lg font-semibold text-red-800 mb-2" },
				"Something went wrong",
			),
			React.createElement(
				"details",
				{ className: "mb-4" },
				React.createElement(
					"summary",
					{ className: "cursor-pointer text-red-600 mb-2" },
					"Error details",
				),
				React.createElement(
					"pre",
					{
						className:
							"text-sm text-red-700 bg-red-100 p-2 rounded overflow-auto",
					},
					error.message,
				),
			),
			React.createElement(
				"button",
				{
					type: "button",
					onClick: resetErrorBoundary,
					className:
						"px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors",
				},
				"Try again",
			),
		);
	};
}

/**
 * Enhanced Error Boundary Component Factory
 */
export interface EnhancedErrorBoundaryProps {
	children: ReactNode;
	onError?: (error: Error, errorInfo: ErrorInfo) => void;
	isolateErrors?: boolean;
}

export function createEnhancedErrorBoundary() {
	return function EnhancedErrorBoundary({
		children,
		onError,
		isolateErrors = true,
	}: EnhancedErrorBoundaryProps) {
		const handleError = React.useCallback(
			(error: Error, errorInfo: ErrorInfo) => {
				errorMonitoringService.captureError(error, {
					source: "ErrorBoundary",
					componentStack: errorInfo.componentStack || undefined,
					errorBoundary: "EnhancedErrorBoundary",
					severity: "high",
				});

				if (onError) {
					onError(error, errorInfo);
				}
			},
			[onError],
		);

		if (isolateErrors) {
			return React.createElement(
				ReactErrorBoundary,
				{
					FallbackComponent: createErrorFallback(),
					onError: handleError,
				},
				children,
			);
		}

		return React.createElement(React.Fragment, null, children);
	};
}

/**
 * Initialize error monitoring on app startup
 */
export function initializeErrorMonitoring(): void {
	errorMonitoringService.initialize();
}

/**
 * Hook to access error monitoring functionality
 */
export function useErrorMonitoring() {
	return {
		captureError: errorMonitoringService.captureError.bind(
			errorMonitoringService,
		),
		getErrors: errorMonitoringService.getErrors.bind(errorMonitoringService),
		getErrorStats: errorMonitoringService.getErrorStats.bind(
			errorMonitoringService,
		),
		clearErrors: errorMonitoringService.clearErrors.bind(
			errorMonitoringService,
		),
		reinitialize: errorMonitoringService.reinitialize.bind(
			errorMonitoringService,
		),
	};
}
