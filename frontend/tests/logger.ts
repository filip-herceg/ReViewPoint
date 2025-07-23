// Minimal test logger mock for Vitest test imports
const logger = {
	info: (..._args: unknown[]) => {},
	error: (..._args: unknown[]) => {},
	warn: (..._args: unknown[]) => {},
	debug: (..._args: unknown[]) => {},
	trace: (..._args: unknown[]) => {},
};
export default logger;
