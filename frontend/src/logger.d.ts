declare module "@/logger" {
	type LogLevel = "error" | "warn" | "info" | "debug" | "trace";

	const logger: {
		error: (...args: unknown[]) => void;
		warn: (...args: unknown[]) => void;
		info: (...args: unknown[]) => void;
		debug: (...args: unknown[]) => void;
		trace: (...args: unknown[]) => void;
	};

	export default logger;
}
