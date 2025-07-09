#!/usr/bin/env node

/**
 * Simple logger utility for development scripts
 * Provides colored output with consistent formatting
 */

const colors = {
    backend: '\x1b[34m',  // Blue
    frontend: '\x1b[32m', // Green
    postgres: '\x1b[36m', // Cyan
    info: '\x1b[32m',     // Green
    warn: '\x1b[33m',     // Yellow
    error: '\x1b[31m',    // Red
    debug: '\x1b[90m',    // Gray
    success: '\x1b[92m',  // Bright Green
    reset: '\x1b[0m'
};

class Logger {
    constructor(prefix = '', defaultColor = colors.info) {
        this.prefix = prefix;
        this.defaultColor = defaultColor;
    }

    _log(level, color, message, data = '') {
        const timestamp = new Date().toLocaleTimeString();
        const prefixStr = this.prefix ? `[${this.prefix}]` : '';
        const levelStr = level ? `[${level}]` : '';

        if (data && typeof data === 'object') {
            console.log(`${color}${prefixStr}${levelStr}${colors.reset} ${message}`);
            console.log(JSON.stringify(data, null, 2));
        } else if (data) {
            // Handle multiline data (like process output)
            const lines = data.toString().split('\n').filter(line => line.trim());
            lines.forEach(line => {
                console.log(`${color}${prefixStr}${colors.reset} ${line}`);
            });
        } else {
            console.log(`${color}${prefixStr}${levelStr}${colors.reset} ${message}`);
        }
    }

    info(message, data) {
        this._log('INFO', colors.info, message, data);
    }

    warn(message, data) {
        this._log('WARN', colors.warn, message, data);
    }

    error(message, data) {
        this._log('ERROR', colors.error, message, data);
    }

    debug(message, data) {
        this._log('DEBUG', colors.debug, message, data);
    }

    success(message, data) {
        this._log('SUCCESS', colors.success, message, data);
    }

    // Service-specific loggers
    backend(message, data) {
        this._log('BACKEND', colors.backend, message, data);
    }

    frontend(message, data) {
        this._log('FRONTEND', colors.frontend, message, data);
    }

    postgres(message, data) {
        this._log('POSTGRES', colors.postgres, message, data);
    }

    // For process output (without level prefix)
    logOutput(prefix, color, data) {
        const lines = data.toString().split('\n').filter(line => line.trim());
        lines.forEach(line => {
            console.log(`${color}[${prefix}]${colors.reset} ${line}`);
        });
    }
}

// Create default logger instance
const logger = new Logger();

// Export both the class and a default instance
export { Logger, logger, colors };
export default logger;
