# API Error Handling Module

**File:** `frontend/src/lib/api/errorHandling.ts`  
**Purpose:** Centralized error handling infrastructure for the ReViewPoint API ecosystem  
**Lines of Code:** 124  
**Type:** Core Infrastructure Module

## Overview

The error handling module provides a robust, centralized error processing system for all API operations in the ReViewPoint application. It standardizes error categorization, logging, and message extraction across the entire API ecosystem, ensuring consistent error handling patterns and improved debugging capabilities.

## Architecture

### Core Components

#### Error Type Classification

```typescript
export type ErrorType = "network" | "4xx" | "5xx" | "unknown";

export interface HandledError {
  type: ErrorType;
  status?: number;
  message: string;
  original?: unknown;
}
```

#### Main Error Handler

```typescript
export function handleApiError(error: unknown): HandledError;
```

### Error Processing Pipeline

1. **Input Validation** - Handles null/undefined errors
2. **Type Detection** - Identifies error types (string, object, Error instance)
3. **Axios Error Processing** - Special handling for HTTP client errors
4. **Message Extraction** - Consistent message parsing from various formats
5. **Categorization** - Classifies errors by type and HTTP status
6. **Logging Integration** - Structured logging with appropriate levels

## Key Features

### 🔍 **Comprehensive Error Type Support**

- **Network Errors**: Connection failures, timeouts, DNS issues
- **4xx Client Errors**: Authentication, validation, not found errors
- **5xx Server Errors**: Internal server errors, service unavailable
- **Unknown Errors**: Fallback for unclassified error types

### 🎯 **Smart Message Extraction**

```typescript
function extractErrorMessage(data: unknown): string {
  // Handles multiple response formats:
  // - String responses
  // - Objects with 'error' property
  // - Objects with 'message' property
  // - Fallback to generic message
}
```

### 🔧 **Axios Integration**

- **Network Error Detection**: Identifies connection-level failures
- **HTTP Response Processing**: Extracts status codes and response data
- **Status Code Classification**: Automatic 4xx/5xx categorization

### 📊 **Integrated Logging**

- **Contextual Logging**: Different log levels based on error severity
- **Structured Data**: Consistent error object formatting
- **Debug Information**: Preserves original error for investigation

## Usage Examples

### Basic Error Handling

```typescript
import { handleApiError } from "@/lib/api/errorHandling";

try {
  const response = await apiCall();
  return response.data;
} catch (error) {
  const handledError = handleApiError(error);

  switch (handledError.type) {
    case "network":
      showNetworkErrorMessage();
      break;
    case "4xx":
      showClientErrorMessage(handledError.message);
      break;
    case "5xx":
      showServerErrorMessage();
      break;
    default:
      showGenericErrorMessage();
  }
}
```

### Status-Specific Handling

```typescript
const handleApiError = (error: unknown) => {
  const handled = handleApiError(error);

  if (handled.status === 401) {
    // Handle authentication errors
    redirectToLogin();
  } else if (handled.status === 403) {
    // Handle authorization errors
    showAccessDeniedMessage();
  } else if (handled.status === 429) {
    // Handle rate limiting
    showRateLimitMessage();
  }

  return handled;
};
```

### React Component Integration

```typescript
const useApiCall = () => {
  const [error, setError] = useState<HandledError | null>(null);

  const makeCall = async () => {
    try {
      setError(null);
      const result = await apiFunction();
      return result;
    } catch (err) {
      const handledError = handleApiError(err);
      setError(handledError);
      throw handledError;
    }
  };

  return { makeCall, error };
};
```

## Error Processing Logic

### Network Error Detection

```typescript
// Identifies Axios network errors (no response received)
if (isAxiosError && !response) {
  return { type: "network", message, original: error };
}
```

### HTTP Status Classification

```typescript
// 4xx Client Errors
if (status >= 400 && status < 500) {
  return { type: "4xx", status, message, original: error };
}

// 5xx Server Errors
if (status >= 500) {
  return { type: "5xx", status, message, original: error };
}
```

### Fallback Processing

```typescript
// Handles non-HTTP errors, Error instances, and unknown types
if (error instanceof Error) {
  return { type: "unknown", message: error.message, original: error };
}
```

## Integration Points

### API Base Module

- **HTTP Client Integration**: Used by `base.ts` for consistent error handling
- **Request/Response Pipeline**: Applied to all API calls automatically

### Authentication Module

- **Login Errors**: Handles authentication failures gracefully
- **Token Refresh**: Manages token expiration scenarios

### Upload Module

- **Progress Tracking**: Error handling during file uploads
- **Chunk Failures**: Recovers from partial upload failures

### User Management

- **Validation Errors**: Processes form validation failures
- **Permission Errors**: Handles access control violations

## Logging Strategy

### Error Severity Levels

- **Network Errors**: `logger.error()` - Critical connectivity issues
- **4xx Errors**: `logger.warn()` - Client-side issues requiring attention
- **5xx Errors**: `logger.error()` - Server-side issues requiring investigation
- **Unknown Errors**: `logger.error()` - Unexpected errors requiring analysis

### Contextual Information

```typescript
logger.error("Network error", error);
logger.warn(`4xx error (${status}):`, message, error);
logger.error(`5xx error (${status}):`, message, error);
```

## Best Practices

### ✅ **Do's**

- **Always Use Handler**: Process all API errors through `handleApiError()`
- **Check Error Types**: Use type discrimination for appropriate responses
- **Preserve Original**: Keep original error for debugging purposes
- **Log Appropriately**: Use consistent logging levels and formats

### ❌ **Don'ts**

- **Don't Ignore Errors**: Always handle or propagate processed errors
- **Don't Hardcode Messages**: Use extracted messages from responses
- **Don't Skip Logging**: Ensure all errors are logged for monitoring
- **Don't Assume Types**: Use type guards for safe error processing

## Error Message Extraction

### Supported Response Formats

1. **String Responses**

   ```typescript
   "Authentication failed";
   ```

2. **Error Object Format**

   ```typescript
   {
     error: "Invalid credentials";
   }
   ```

3. **Message Object Format**

   ```typescript
   {
     message: "User not found";
   }
   ```

4. **Complex Response Format**
   ```typescript
   {
       error: "Validation failed",
       details: { field: "email", reason: "invalid format" }
   }
   ```

## Performance Considerations

### ⚡ **Optimization Features**

- **Efficient Type Checking**: Minimal overhead for error classification
- **Lazy Evaluation**: Only processes error details when needed
- **Memory Management**: Proper cleanup of error references
- **Logging Throttling**: Prevents log spam from repeated errors

### 📈 **Scalability**

- **Stateless Processing**: No shared state between error handling calls
- **Thread Safety**: Safe for concurrent use across components
- **Resource Cleanup**: Automatic cleanup of temporary error objects

## Development Workflow

### Testing Error Scenarios

```typescript
// Mock network errors
const networkError = { isAxiosError: true, message: "Network Error" };
const handled = handleApiError(networkError);
expect(handled.type).toBe("network");

// Mock HTTP errors
const httpError = {
  isAxiosError: true,
  response: { status: 404, data: { error: "Not found" } },
};
const handledHttp = handleApiError(httpError);
expect(handledHttp.type).toBe("4xx");
```

### Debugging Support

```typescript
// Error object provides full context for debugging
const handledError = handleApiError(originalError);
console.log("Error type:", handledError.type);
console.log("Status code:", handledError.status);
console.log("User message:", handledError.message);
console.log("Original error:", handledError.original);
```

## Migration Guide

### From Manual Error Handling

```typescript
// Before: Manual error processing
try {
  const response = await api.call();
} catch (error) {
  if (error.response?.status === 401) {
    // Handle auth error
  } else if (error.code === "NETWORK_ERROR") {
    // Handle network error
  }
  // Inconsistent error handling
}

// After: Centralized error handling
try {
  const response = await api.call();
} catch (error) {
  const handled = handleApiError(error);
  switch (handled.type) {
    case "4xx":
      if (handled.status === 401) {
        // Handle auth error
      }
      break;
    case "network":
      // Handle network error
      break;
  }
}
```

### Legacy Error Compatibility

```typescript
// Maintains compatibility with existing error handling patterns
const legacyErrorHandler = (error: unknown) => {
  const handled = handleApiError(error);

  // Convert to legacy format if needed
  return {
    isNetworkError: handled.type === "network",
    isServerError: handled.type === "5xx",
    statusCode: handled.status,
    errorMessage: handled.message,
  };
};
```

## Related Documentation

- **API Base Module**: `base.ts.md` - HTTP client integration
- **Authentication API**: `auth.ts.md` - Auth-specific error handling
- **Upload API**: `uploads.ts.md` - File upload error scenarios
- **User API**: `users/index.ts.md` - User management errors
- **Type System**: `types/index.ts.md` - Error-related type definitions

## Dependencies

- **Logger**: `@/logger` - Structured logging integration
- **Axios**: Implicit through error type detection
- **TypeScript**: Strong typing for error categorization

---

_This module provides the foundation for consistent, reliable error handling across the entire ReViewPoint API ecosystem, ensuring robust error management and improved debugging capabilities._
