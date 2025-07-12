// Minimal test logger mock for Vitest test imports
const logger = {
	info: (..._args: any[]) => {},
	error: (..._args: any[]) => {},
	warn: (..._args: any[]) => {},
	debug: (..._args: any[]) => {},
	trace: (..._args: any[]) => {},
};
export default logger;
