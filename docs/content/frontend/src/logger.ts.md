# logger.ts - Centralized Frontend Logging Service

## Purpose

The `logger.ts` file provides a centralized, configurable logging system for the ReViewPoint frontend application. It offers structured logging with multiple log levels, environment-aware configuration, and intelligent argument normalization for consistent log output across the entire application.

## Key Components

### **Log Level System**

```typescript
export type LogLevel = "error" | "warn" | "info" | "debug" | "trace";

const LOG_LEVELS: LogLevel[] = ["error", "warn", "info", "debug", "trace"];
```

### **Log Level Hierarchy**

```typescript
// Severity hierarchy (highest to lowest):
error   → Critical failures, exceptions, system errors
warn    → Warnings, deprecated usage, potential issues
info    → General information, application flow
debug   → Detailed debugging information
trace   → Granular execution tracking, stack traces
```

## Core Features

### **Environment-Aware Log Level Configuration**

```typescript
function getLogLevel(): LogLevel {
  // Priority order for log level determination:

  // 1. Browser window global (runtime configuration)
  if (typeof window !== "undefined" && window.LOG_LEVEL) {
    return window.LOG_LEVEL as LogLevel;
  }

  // 2. Global environment variable
  if (typeof globalThis !== "undefined" && globalThis.LOG_LEVEL) {
    return globalThis.LOG_LEVEL as LogLevel;
  }

  // 3. Process environment variable (Vite/Node.js)
  if (typeof process !== "undefined" && process.env?.LOG_LEVEL) {
    return process.env.LOG_LEVEL as LogLevel;
  }

  // 4. Test environment default
  if (typeof process !== "undefined" && process.env?.NODE_ENV === "test") {
    return "error"; // Minimize test output
  }

  // 5. Production default
  return "warn"; // Conservative default
}
```

### **Intelligent Log Filtering**

```typescript
function shouldLog(level: LogLevel): boolean {
  const currentLevel = getLogLevel();
  return LOG_LEVELS.indexOf(level) <= LOG_LEVELS.indexOf(currentLevel);
}

// Example filtering behavior:
// Current level: "warn"
// - logger.error() → ✅ Logged (error ≤ warn)
// - logger.warn()  → ✅ Logged (warn ≤ warn)
// - logger.info()  → ❌ Filtered (info > warn)
// - logger.debug() → ❌ Filtered (debug > warn)
```

### **Advanced Argument Normalization**

```typescript
function normalizeErrorArg(arg: unknown): unknown {
  // Error objects - preserve stack traces
  if (arg instanceof Error) return arg;

  // Objects and arrays - JSON serialization
  if (typeof arg === "object" && arg !== null) {
    try {
      return JSON.stringify(arg);
    } catch {
      return String(arg); // Fallback for circular references
    }
  }

  // Primitives - string conversion
  return String(arg);
}
```

## Logger Interface

### **Complete Logging API**

```typescript
const logger = {
  error: (...args: unknown[]) => {
    if (shouldLog("error"))
      console.error("[ERROR]", ...args.map(normalizeErrorArg));
  },

  warn: (...args: unknown[]) => {
    if (shouldLog("warn"))
      console.warn("[WARN]", ...args.map(normalizeErrorArg));
  },

  info: (...args: unknown[]) => {
    if (shouldLog("info"))
      console.info("[INFO]", ...args.map(normalizeErrorArg));
  },

  debug: (...args: unknown[]) => {
    if (shouldLog("debug"))
      console.debug("[DEBUG]", ...args.map(normalizeErrorArg));
  },

  trace: (...args: unknown[]) => {
    if (shouldLog("trace"))
      console.trace("[TRACE]", ...args.map(normalizeErrorArg));
  },
};
```

## Configuration Strategies

### **Development Environment Setup**

```typescript
// Method 1: Runtime configuration (dynamic)
window.LOG_LEVEL = "debug";

// Method 2: Environment variable (build-time)
// In .env.local:
LOG_LEVEL = debug;

// Method 3: Vite configuration
// In vite.config.ts:
export default defineConfig({
  define: {
    "process.env.LOG_LEVEL": JSON.stringify("debug"),
  },
});
```

### **Production Environment Setup**

```typescript
// Conservative production logging
// In .env.production:
LOG_LEVEL = warn;

// Or runtime configuration for specific debugging:
if (window.location.search.includes("debug=true")) {
  window.LOG_LEVEL = "debug";
}
```

### **Test Environment Configuration**

```typescript
// Automatic test environment detection
if (process.env.NODE_ENV === "test") {
  return "error"; // Minimize test console noise
}

// Override in specific test files:
beforeAll(() => {
  window.LOG_LEVEL = "debug"; // Enable detailed logging for debugging
});
```

## Usage Patterns

### **Basic Logging**

```typescript
import logger from "@/logger";

// Simple message logging
logger.info("User authentication successful");
logger.warn("API response took longer than expected");
logger.error("Failed to load user data");

// Multiple arguments
logger.debug("API call", { endpoint: "/users", method: "GET" });
logger.error("Request failed", error, { context: "user-profile" });
```

### **Structured Object Logging**

```typescript
// Complex object logging with automatic serialization
const userState = {
  id: "123",
  name: "John Doe",
  preferences: { theme: "dark", notifications: true },
};

logger.info("User state updated:", userState);
// Output: [INFO] User state updated: {"id":"123","name":"John Doe","preferences":{"theme":"dark","notifications":true}}

// Error object with preserved stack trace
try {
  riskyOperation();
} catch (error) {
  logger.error("Operation failed:", error);
  // Output: [ERROR] Operation failed: Error: Something went wrong
  //   at riskyOperation (file.js:10:5)
  //   at ...
}
```

### **API Integration Logging**

```typescript
import logger from "@/logger";

class ApiClient {
  async request(endpoint: string, options: RequestOptions) {
    logger.debug("API request started:", { endpoint, method: options.method });

    try {
      const response = await fetch(endpoint, options);

      if (!response.ok) {
        logger.warn("API request failed:", {
          endpoint,
          status: response.status,
          statusText: response.statusText,
        });
      } else {
        logger.info("API request successful:", { endpoint });
      }

      return response;
    } catch (error) {
      logger.error("API request error:", error, { endpoint });
      throw error;
    }
  }
}
```

### **Component Lifecycle Logging**

```typescript
import logger from '@/logger';
import { useEffect } from 'react';

function UserProfile({ userId }: { userId: string }) {
  useEffect(() => {
    logger.debug('UserProfile component mounted:', { userId });

    return () => {
      logger.debug('UserProfile component unmounted:', { userId });
    };
  }, [userId]);

  const handleUserUpdate = (userData: UserData) => {
    logger.info('User data updated:', { userId, fields: Object.keys(userData) });
  };

  return <div>...</div>;
}
```

## Advanced Logging Patterns

### **Conditional Debug Logging**

```typescript
import logger from "@/logger";

// Performance-sensitive logging
function expensiveOperation(data: LargeDataSet) {
  // Only serialize large objects if debug logging is enabled
  if (logger.debug.length > 0) {
    // Check if debug would actually log
    logger.debug("Processing large dataset:", {
      size: data.length,
      sample: data.slice(0, 3), // Log sample instead of full dataset
    });
  }

  return processData(data);
}
```

### **Context-Aware Logging**

```typescript
import logger from "@/logger";

class ContextualLogger {
  constructor(private context: string) {}

  info(message: string, ...args: unknown[]) {
    logger.info(`[${this.context}] ${message}`, ...args);
  }

  error(message: string, ...args: unknown[]) {
    logger.error(`[${this.context}] ${message}`, ...args);
  }
}

// Usage in different modules
const authLogger = new ContextualLogger("AUTH");
const apiLogger = new ContextualLogger("API");

authLogger.info("User login attempt"); // [INFO] [AUTH] User login attempt
apiLogger.error("Request timeout"); // [ERROR] [API] Request timeout
```

### **Feature Flag Integration**

```typescript
import logger from "@/logger";
import { isFeatureEnabled } from "@/lib/config/featureFlags";

function featureLogger(feature: string) {
  return {
    info: (message: string, ...args: unknown[]) => {
      if (isFeatureEnabled("enableDetailedLogging")) {
        logger.info(`[${feature}] ${message}`, ...args);
      }
    },
  };
}

const uploadLogger = featureLogger("UPLOAD");
uploadLogger.info("File upload started"); // Only logs if feature enabled
```

## Development and Debugging

### **Browser Console Integration**

```typescript
// Expose logger globally for debugging (development only)
if (process.env.NODE_ENV === "development") {
  window.logger = logger;

  // Enable runtime log level changes
  window.setLogLevel = (level: LogLevel) => {
    window.LOG_LEVEL = level;
    logger.info(`Log level changed to: ${level}`);
  };
}

// Browser console usage:
// window.setLogLevel('debug')
// window.logger.debug('Manual debug message')
```

### **Log Analytics and Monitoring**

```typescript
import logger from "@/logger";

// Enhanced logger with analytics
class AnalyticsLogger {
  private originalLogger = logger;

  error(message: string, ...args: unknown[]) {
    // Send to error monitoring service
    if (window.Sentry) {
      window.Sentry.captureException(new Error(message));
    }

    // Also send to analytics
    if (window.plausible) {
      window.plausible("Frontend Error", {
        props: { message: message.substring(0, 100) },
      });
    }

    return this.originalLogger.error(message, ...args);
  }
}
```

### **Performance Logging**

```typescript
import logger from "@/logger";

function performanceLogger<T>(operation: string, fn: () => T): T {
  const start = performance.now();
  logger.debug(`Starting operation: ${operation}`);

  try {
    const result = fn();
    const duration = performance.now() - start;

    logger.info(`Operation completed: ${operation}`, {
      duration: `${duration.toFixed(2)}ms`,
    });

    return result;
  } catch (error) {
    const duration = performance.now() - start;
    logger.error(`Operation failed: ${operation}`, error, {
      duration: `${duration.toFixed(2)}ms`,
    });
    throw error;
  }
}

// Usage
const userData = performanceLogger("fetch-user-data", () => {
  return fetchUserFromAPI(userId);
});
```

## Log Level Best Practices

### **Error Level Guidelines**

```typescript
// ❌ Overuse of error level
logger.error("User clicked button"); // This is not an error

// ✅ Appropriate error usage
logger.error("Authentication failed:", error);
logger.error("Failed to save user data:", error);
logger.error("Critical service unavailable:", serviceError);
```

### **Debug Level Guidelines**

```typescript
// ✅ Good debug usage
logger.debug("Function parameters:", { userId, options });
logger.debug("State before update:", currentState);
logger.debug("API response received:", response.headers);

// ❌ Sensitive information in logs
logger.debug("User password:", password); // Security risk!
logger.debug("API key:", apiKey); // Security risk!
```

### **Production Logging Strategy**

```typescript
// Production-appropriate logging levels:

// ERROR: Actual failures that impact functionality
logger.error("Payment processing failed:", error);

// WARN: Potential issues that don't break functionality
logger.warn("API response slow:", { duration: 5000 });

// INFO: Important business events
logger.info("User registration completed:", { userId });

// DEBUG/TRACE: Only in development
if (process.env.NODE_ENV === "development") {
  logger.debug("Component render cycle:", componentName);
  logger.trace("Detailed execution path:", executionSteps);
}
```

## Related Files

- [errorHandling.ts](api/errorHandling.ts.md) - Uses logger for structured error reporting
- [errorMonitoring.ts](lib/monitoring/errorMonitoring.ts.md) - Integrates with logger for error tracking
- [performanceMonitoring.ts](lib/monitoring/performanceMonitoring.ts.md) - Uses logger for performance metrics

## Dependencies

### **Environment Dependencies**

- **Browser Environment**: `window` object for runtime configuration
- **Node.js Environment**: `process.env` for build-time configuration
- **Vite Build System**: Environment variable processing

### **No External Dependencies**

The logger is implemented using only browser/Node.js built-ins:

- `console` API for output
- Native JavaScript for configuration and normalization
- TypeScript types for type safety

## Development Notes

### **Log Level Testing**

```typescript
// Test different log levels
describe("Logger", () => {
  beforeEach(() => {
    // Reset log level for each test
    delete window.LOG_LEVEL;
  });

  it("should filter logs based on level", () => {
    window.LOG_LEVEL = "warn";

    const consoleSpy = jest.spyOn(console, "info");
    logger.info("test message");

    expect(consoleSpy).not.toHaveBeenCalled(); // info > warn, should be filtered
  });
});
```

### **Security Considerations**

- **Sensitive Data**: Never log passwords, API keys, or personal information
- **Production Logs**: Use conservative log levels to avoid information leakage
- **Error Context**: Include helpful context without exposing internal system details
- **Log Sanitization**: Consider sanitizing user inputs before logging
