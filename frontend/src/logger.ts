// Centralized logger utility for the frontend
// Usage: import logger from './logger';
// logger.info('message');

export type LogLevel = 'error' | 'warn' | 'info' | 'debug' | 'trace';

const LOG_LEVELS: LogLevel[] = ['error', 'warn', 'info', 'debug', 'trace'];

// Set log level from environment or default to 'info'
// Use window global or fallback to 'info'. Set window.LOG_LEVEL in index.html or via Vite define if needed.

function getLogLevel(): LogLevel {
    if (typeof window !== 'undefined' && (window as any).LOG_LEVEL) {
        return (window as any).LOG_LEVEL;
    }
    if (typeof globalThis !== 'undefined' && (globalThis as any).LOG_LEVEL) {
        return (globalThis as any).LOG_LEVEL;
    }
    return 'info';
}

function shouldLog(level: LogLevel): boolean {
    const currentLevel = getLogLevel();
    return LOG_LEVELS.indexOf(level) <= LOG_LEVELS.indexOf(currentLevel);
}


function normalizeErrorArg(arg: unknown): unknown {
    if (arg instanceof Error) return arg;
    // For objects and arrays, always JSON.stringify (except Error)
    if (typeof arg === 'object' && arg !== null) {
        try {
            return JSON.stringify(arg);
        } catch {
            return String(arg);
        }
    }
    // For primitives (string, number, boolean, undefined, null)
    return String(arg);
}

const logger = {
    error: (...args: any[]) => {
        if (shouldLog('error')) console.error('[ERROR]', ...args.map(normalizeErrorArg));
    },
    warn: (...args: any[]) => {
        if (shouldLog('warn')) console.warn('[WARN]', ...args.map(normalizeErrorArg));
    },
    info: (...args: any[]) => {
        if (shouldLog('info')) console.info('[INFO]', ...args.map(normalizeErrorArg));
    },
    debug: (...args: any[]) => {
        if (shouldLog('debug')) console.debug('[DEBUG]', ...args.map(normalizeErrorArg));
    },
    trace: (...args: any[]) => {
        if (shouldLog('trace')) console.trace('[TRACE]', ...args.map(normalizeErrorArg));
    },
};

export default logger;
