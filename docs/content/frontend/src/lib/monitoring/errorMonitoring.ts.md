# errorMonitoring.ts - Comprehensive Error Monitoring System

## Purpose

The `errorMonitoring.ts` file provides a comprehensive error monitoring and reporting system for the ReViewPoint frontend application. It handles error tracking, user feedback collection, error boundary management, and integration with external monitoring services.

## Key Components

### **Error Report Interface**

```typescript
interface ErrorReport {
  id: string; // Unique error identifier
  timestamp: Date; // Error occurrence time
  message: string; // Error message
  stack?: string; // Error stack trace
  componentStack?: string; // React component stack
  errorBoundary?: string; // Error boundary name
  props?: Record<string, unknown>; // Component props at error
  userAgent: string; // Browser information
  url: string; // Page URL where error occurred
  userId?: string; // User identifier (if authenticated)
  severity: "low" | "medium" | "high" | "critical";
  context?: Record<string, unknown>; // Additional error context
}
```

### **Error Monitoring Configuration**

```typescript
interface ErrorMonitoringConfig {
  enableConsoleTracking: boolean; // Track console errors
  enableUnhandledRejections: boolean; // Track promise rejections
  enableComponentErrors: boolean; // Track React component errors
  enableUserFeedback: boolean; // Enable user feedback collection
  maxErrors: number; // Maximum errors to store
  reportToSentry: boolean; // External service integration
}
```

## Core Features

### **Error Boundary Integration**

- **React Error Boundaries**: Comprehensive component error catching
- **Fallback UI**: User-friendly error displays with recovery options
- **Error Context**: Captures component props and state at error time
- **Recovery Mechanisms**: Allows users to retry or navigate away

### **Global Error Handling**

- **Unhandled Promise Rejections**: Automatic capture of async errors
- **Console Error Tracking**: Monitors console.error calls
- **Network Error Detection**: API and fetch error monitoring
- **Script Error Handling**: Captures JavaScript runtime errors

### **Error Classification**

```typescript
// Error severity classification
enum ErrorSeverity {
  LOW = "low", // Minor UI issues, non-blocking
  MEDIUM = "medium", // Functional issues, workarounds available
  HIGH = "high", // Significant functionality broken
  CRITICAL = "critical", // Application unusable, data loss risk
}
```

## Implementation Details

### **Error Capture Strategy**

```typescript
// Global error event listeners
window.addEventListener("error", (event) => {
  const errorReport = createErrorReport({
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error,
  });
  reportError(errorReport);
});

// Unhandled promise rejection tracking
window.addEventListener("unhandledrejection", (event) => {
  const errorReport = createErrorReport({
    message: "Unhandled Promise Rejection",
    error: event.reason,
  });
  reportError(errorReport);
});
```

### **React Error Boundary Integration**

```typescript
// Enhanced error boundary with monitoring
export class MonitoringErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorReport = createErrorReport({
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      errorBoundary: this.constructor.name,
    });

    reportError(errorReport);
  }
}
```

### **Error Context Collection**

```typescript
// Comprehensive error context gathering
function gatherErrorContext(): Record<string, unknown> {
  return {
    userAgent: navigator.userAgent,
    url: window.location.href,
    timestamp: new Date().toISOString(),
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
    },
    connection: (navigator as any).connection?.effectiveType,
    memory: (performance as any).memory?.usedJSHeapSize,
  };
}
```

## Error Reporting Pipeline

### **Report Creation**

```typescript
function createErrorReport(errorData: Partial<ErrorReport>): ErrorReport {
  return {
    id: generateErrorId(),
    timestamp: new Date(),
    severity: classifyErrorSeverity(errorData),
    context: gatherErrorContext(),
    ...errorData,
  };
}
```

### **Severity Classification Logic**

```typescript
function classifyErrorSeverity(error: Partial<ErrorReport>): ErrorSeverity {
  // Critical: Authentication failures, data corruption
  if (error.message?.includes("auth") || error.message?.includes("token")) {
    return ErrorSeverity.CRITICAL;
  }

  // High: Component crashes, API failures
  if (error.componentStack || error.message?.includes("Network Error")) {
    return ErrorSeverity.HIGH;
  }

  // Medium: Feature failures, recoverable errors
  if (error.stack?.includes("feature")) {
    return ErrorSeverity.MEDIUM;
  }

  // Low: Minor UI issues, console warnings
  return ErrorSeverity.LOW;
}
```

### **Reporting Strategies**

```typescript
// Multi-channel error reporting
async function reportError(errorReport: ErrorReport) {
  // Local storage for offline scenarios
  storeErrorLocally(errorReport);

  // External monitoring service (Sentry, LogRocket, etc.)
  if (config.reportToSentry && isFeatureEnabled("error-reporting")) {
    await sendToExternalService(errorReport);
  }

  // Internal analytics
  await sendToInternalAPI(errorReport);

  // User notification (for high/critical errors)
  if (errorReport.severity === "high" || errorReport.severity === "critical") {
    showUserNotification(errorReport);
  }
}
```

## User Feedback Integration

### **Error Feedback Collection**

```typescript
interface ErrorFeedback {
  errorId: string;
  userDescription: string;
  expectedBehavior: string;
  stepsToReproduce: string[];
  userEmail?: string;
}

function collectUserFeedback(errorReport: ErrorReport): Promise<ErrorFeedback> {
  return new Promise((resolve) => {
    showFeedbackModal({
      errorId: errorReport.id,
      onSubmit: (feedback) => resolve(feedback),
    });
  });
}
```

### **Recovery Actions**

```typescript
// Provide recovery options to users
const recoveryActions = {
  reload: () => window.location.reload(),
  goHome: () => (window.location.href = "/"),
  clearStorage: () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.reload();
  },
  reportBug: (errorId: string) => openBugReportForm(errorId),
};
```

## Dependencies

### **Core Dependencies**

- `react-error-boundary` - Enhanced React error boundary components
- `@/lib/config/environment` - Environment configuration access
- `@/lib/config/featureFlags` - Feature flag integration
- `@/logger` - Centralized logging service

### **External Services**

- **Sentry** - Error tracking and performance monitoring
- **LogRocket** - Session replay and error investigation
- **Custom Analytics** - Internal error tracking API

## Usage Examples

### **Component Error Boundary**

```typescript
import { MonitoringErrorBoundary } from '@/lib/monitoring/errorMonitoring';

function App() {
  return (
    <MonitoringErrorBoundary>
      <YourApplication />
    </MonitoringErrorBoundary>
  );
}
```

### **Manual Error Reporting**

```typescript
import { reportError } from "@/lib/monitoring/errorMonitoring";

try {
  riskyOperation();
} catch (error) {
  reportError({
    message: "Risk operation failed",
    error,
    severity: "medium",
    context: { operation: "user-data-processing" },
  });
}
```

### **Error Analytics Dashboard**

```typescript
import { getErrorMetrics } from '@/lib/monitoring/errorMonitoring';

function ErrorDashboard() {
  const metrics = getErrorMetrics();

  return (
    <div>
      <div>Total Errors: {metrics.totalErrors}</div>
      <div>Critical Errors: {metrics.criticalErrors}</div>
      <div>Error Rate: {metrics.errorRate}%</div>
    </div>
  );
}
```

## Performance Considerations

### **Error Storage Management**

```typescript
// Efficient error storage with rotation
class ErrorStorage {
  private maxErrors = 100;

  store(error: ErrorReport) {
    const stored = this.getStoredErrors();
    if (stored.length >= this.maxErrors) {
      stored.shift(); // Remove oldest error
    }
    stored.push(error);
    localStorage.setItem("error-reports", JSON.stringify(stored));
  }
}
```

### **Throttling and Deduplication**

```typescript
// Prevent error spam
const errorThrottler = new Map<string, number>();

function shouldReportError(errorReport: ErrorReport): boolean {
  const key = errorReport.message + errorReport.stack;
  const lastReported = errorThrottler.get(key) || 0;
  const now = Date.now();

  if (now - lastReported < 5000) {
    // 5 second throttle
    return false;
  }

  errorThrottler.set(key, now);
  return true;
}
```

## Related Files

- [performanceMonitoring.ts](performanceMonitoring.ts.md) - Performance tracking integration
- [logger.ts](../../logger.ts.md) - Centralized logging service
- [environment.ts](../config/environment.ts.md) - Configuration management
- [featureFlags.ts](../config/featureFlags.ts.md) - Feature flag integration

## Development Notes

### **Testing Error Monitoring**

```typescript
// Trigger test errors for validation
if (process.env.NODE_ENV === "development") {
  window.triggerTestError = (type: string) => {
    switch (type) {
      case "component":
        throw new Error("Test component error");
      case "async":
        Promise.reject(new Error("Test async error"));
      case "network":
        fetch("/nonexistent-endpoint");
    }
  };
}
```

### **Error Monitoring Best Practices**

- **Selective Reporting**: Only report actionable errors
- **Context Preservation**: Include relevant state and props
- **User Privacy**: Avoid capturing sensitive user data
- **Performance Impact**: Minimize monitoring overhead
- **Recovery Focus**: Provide clear recovery paths for users
