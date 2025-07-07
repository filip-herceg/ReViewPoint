// Minimal test logger mock for Vitest test imports
const logger = {
    info: (...args: any[]) => { },
    error: (...args: any[]) => { },
    warn: (...args: any[]) => { },
    debug: (...args: any[]) => { },
    trace: (...args: any[]) => { },
};
export default logger;
