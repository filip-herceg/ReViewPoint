// Global type declarations for frontend environment

// Window extensions for feature flags and external libraries
declare global {
	interface Window {
		FEATURE_FLAGS?: Record<string, boolean>;
		LOG_LEVEL?: string;
		Sentry?: {
			captureException: (
				error: unknown,
				context?: Record<string, unknown>,
			) => void;
		};
		plausible?: (eventName: string, options?: Record<string, unknown>) => void;
	}
}

export {};
