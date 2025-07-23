# errorHandling.ts - API Error Handling Utilities

## Purpose

The `errorHandling.ts` file provides centralized error handling strategies for the ReViewPoint frontend API layer. This module offers consistent error processing for network errors, HTTP status codes (4xx, 5xx), and various error types that can occur during API communications. It ensures standardized error handling patterns across all API operations while maintaining comprehensive logging and type safety.

## Key Features

### Error Classification

- **Network Errors**: Connection failures, timeouts, and network-related issues
- **4xx Client Errors**: Authentication, authorization, validation, and client-side errors
- **5xx Server Errors**: Backend failures, database issues, and server-side problems
- **Unknown Errors**: Unexpected error types and edge cases

### Comprehensive Error Processing

- **Message Extraction**: Intelligent extraction of error messages from various response formats
- **Type Identification**: Automatic classification of error types based on context
- **Logging Integration**: Consistent logging with appropriate severity levels
- **Original Error Preservation**: Maintains access to original error objects for debugging

## Type Definitions

### Error Type Classification

```typescript
export type ErrorType = "network" | "4xx" | "5xx" | "unknown";
```

**Error Types:**

- `"network"` - Connection failures, DNS issues, timeout errors
- `"4xx"` - Client-side errors (401, 403, 404, 422, etc.)
- `"5xx"` - Server-side errors (500, 502, 503, etc.)
- `"unknown"` - Unclassified or unexpected error types

### Handled Error Interface

```typescript
export interface HandledError {
  type: ErrorType;           // Classification of the error
  status?: number;           // HTTP status code (if available)
  message: string;           // Human-readable error message
  original?: unknown;        // Original error object for debugging
}
```

**Properties:**

- `type` - Categorizes the error for appropriate handling strategies
- `status` - HTTP status code for HTTP-related errors
- `message` - Extracted or formatted error message for user display
- `original` - Preserved original error object for detailed debugging

## Core Functions

### Error Message Extraction (`extractErrorMessage`)

Intelligently extracts meaningful error messages from various response data formats.

```typescript
function extractErrorMessage(data: unknown): string
```

**Message Extraction Logic:**

1. **String Response**: Returns the string directly if it's a meaningful message
2. **Object with `error` Property**: Extracts the error field if it's a string
3. **Object with `message` Property**: Extracts the message field if it's a string
4. **Fallback**: Returns "HTTP error" for unrecognizable formats
  return "HTTP error";
}
```

### **Comprehensive Error Handler**

```typescript
export function handleApiError(error: unknown): HandledError {
  // Handles all error types:
  // - Axios network and HTTP errors
  // - Standard JavaScript Error instances
  // - String and primitive error values
  // - Plain objects with error information
  // - Unknown/unexpected error types
}
```

## Error Processing Logic

### **Axios Error Detection**

```typescript
// Axios error identification
const isAxiosError = typeof error === "object" && 
                    error !== null && 
                    "isAxiosError" in error;

// Response extraction with type safety
const getAxiosResponse = (err: unknown): { status?: number; data?: unknown } | undefined => {
  if (typeof err === "object" && err !== null && "response" in err) {
    const response = (err as { response?: unknown }).response;
    if (typeof response === "object" && response !== null) {
      return response as { status?: number; data?: unknown };
    }
  }
  return undefined;
};
```

### **Network Error Handling**

```typescript
// Network failures (no response received)
if (isAxiosError && !response) {
  const message = error instanceof Error ? error.message : "Network error";
  logger.error("Network error", error);
  return { 
    type: "network", 
    message, 
    original: error 
  };
}
```

### **HTTP Status Error Processing**

```typescript
// 4xx Client Errors (400-499)
if (status && status >= 400 && status < 500) {
  logger.warn(`4xx error (${status}):`, message, error);
  return { 
    type: "4xx", 
    status, 
    message, 
    original: error 
  };
}

// 5xx Server Errors (500-599)
if (status && status >= 500) {
  logger.error(`5xx error (${status}):`, message, error);
  return { 
    type: "5xx", 
    status, 
    message, 
    original: error 
  };
}
```

## Error Type Strategies

### **Network Error Strategy**

```typescript
// Connection failures, timeouts, DNS issues
Network Error → {
  type: "network",
  message: "Connection failed" | "Network timeout" | "DNS resolution failed",
  original: AxiosError
}

// Common network error scenarios:
// - Offline connectivity
// - Server unreachable
// - Request timeout
// - DNS lookup failure
```

### **4xx Client Error Strategy**

```typescript
// Client-side request errors
4xx Error → {
  type: "4xx",
  status: 400-499,
  message: Server-provided error message,
  original: AxiosError
}

// Common 4xx scenarios:
// - 400 Bad Request: Invalid request data
// - 401 Unauthorized: Authentication required
// - 403 Forbidden: Access denied
// - 404 Not Found: Resource doesn't exist
// - 422 Unprocessable Entity: Validation errors
```

### **5xx Server Error Strategy**

```typescript
// Server-side processing errors
5xx Error → {
  type: "5xx",
  status: 500-599,
  message: Server error description,
  original: AxiosError
}

// Common 5xx scenarios:
// - 500 Internal Server Error
// - 502 Bad Gateway
// - 503 Service Unavailable
// - 504 Gateway Timeout
```

### **Unknown Error Fallback**

```typescript
// Unclassified or unexpected errors
Unknown Error → {
  type: "unknown",
  message: "Unknown error type" | extracted message,
  original: original error object
}

// Handles edge cases:
// - Non-standard error objects
// - Primitive error values
// - Custom error types
// - Malformed responses
```

## Logging Integration

### **Structured Error Logging**

```typescript
import logger from "@/logger";

// Network errors - highest priority
logger.error("Network error", error);

// Server errors - high priority  
logger.error(`5xx error (${status}):`, message, error);

// Client errors - medium priority
logger.warn(`4xx error (${status}):`, message, error);

// Unknown errors - debug priority
logger.error("Unknown error type", wrappedError);
```

### **Log Level Strategy**

- **ERROR**: Network failures, 5xx server errors, unknown error types
- **WARN**: 4xx client errors, malformed responses
- **DEBUG**: Detailed error context and stack traces (development)

## Usage Patterns

### **API Layer Integration**

```typescript
import { handleApiError, type HandledError } from './errorHandling';

// In API service methods
async function fetchUserData(userId: string): Promise<User> {
  try {
    const response = await axios.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    const handledError = handleApiError(error);
    
    // Use standardized error for UI feedback
    throw new Error(handledError.message);
  }
}
```

### **Component Error Handling**

```typescript
import { handleApiError } from '@/lib/api/errorHandling';

function UserProfile({ userId }: { userId: string }) {
  const [error, setError] = useState<string | null>(null);

  const loadUser = async () => {
    try {
      const user = await fetchUserData(userId);
      setUser(user);
    } catch (error) {
      const handled = handleApiError(error);
      
      // Display appropriate error message based on type
      switch (handled.type) {
        case 'network':
          setError('Connection problem. Please check your internet connection.');
          break;
        case '4xx':
          setError(handled.message); // Use server-provided message
          break;
        case '5xx':
          setError('Server error. Please try again later.');
          break;
        default:
          setError('An unexpected error occurred.');
      }
    }
  };
}
```

### **React Query Integration**

```typescript
import { useQuery } from '@tanstack/react-query';
import { handleApiError } from '@/lib/api/errorHandling';

function useUserData(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUserData(userId),
    onError: (error) => {
      const handled = handleApiError(error);
      
      // Log structured error information
      console.error('User data fetch failed:', {
        type: handled.type,
        status: handled.status,
        message: handled.message
      });
    }
  });
}
```

## Error Recovery Strategies

### **Retry Logic Integration**

```typescript
import { handleApiError } from '@/lib/api/errorHandling';

async function apiWithRetry<T>(
  apiCall: () => Promise<T>, 
  maxRetries: number = 3
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      const handled = handleApiError(error);
      
      // Only retry on network or 5xx errors
      if (handled.type === 'network' || handled.type === '5xx') {
        if (attempt < maxRetries) {
          await delay(attempt * 1000); // Exponential backoff
          continue;
        }
      }
      
      // Don't retry 4xx errors (client errors)
      throw error;
    }
  }
}
```

### **Circuit Breaker Pattern**

```typescript
class ApiCircuitBreaker {
  private failureCount = 0;
  private lastFailureTime = 0;
  private readonly threshold = 5;
  private readonly timeout = 60000; // 1 minute

  async execute<T>(apiCall: () => Promise<T>): Promise<T> {
    if (this.isOpen()) {
      throw new Error('Circuit breaker is open');
    }

    try {
      const result = await apiCall();
      this.onSuccess();
      return result;
    } catch (error) {
      const handled = handleApiError(error);
      
      // Only count 5xx and network errors as circuit breaker failures
      if (handled.type === '5xx' || handled.type === 'network') {
        this.onFailure();
      }
      
      throw error;
    }
  }
}
```

## Dependencies

### **Core Dependencies**

- `@/logger` - Centralized logging service for error reporting
- `axios` - HTTP client library (error detection and response handling)

### **Type Dependencies**

- Standard TypeScript types for error classification
- Custom interfaces for structured error handling

## Related Files

- [base.ts](base.ts.md) - Base API client using error handling utilities
- [logger.ts](../../logger.ts.md) - Centralized logging service integration
- [performanceMonitoring.ts](../monitoring/performanceMonitoring.ts.md) - Performance impact tracking
- [errorMonitoring.ts](../monitoring/errorMonitoring.ts.md) - Error analytics and reporting

## Development Notes

### **Error Message Best Practices**

- **User-Friendly**: Messages should be understandable by end users
- **Actionable**: Provide guidance on how to resolve the issue when possible
- **Consistent**: Use standardized language across all error scenarios
- **Contextual**: Include relevant context without exposing sensitive information

### **Testing Error Handling**

```typescript
// Unit tests for error handling scenarios
describe('handleApiError', () => {
  it('should handle network errors correctly', () => {
    const networkError = { isAxiosError: true, message: 'Network Error' };
    const result = handleApiError(networkError);
    
    expect(result.type).toBe('network');
    expect(result.message).toBe('Network Error');
  });

  it('should categorize 4xx errors properly', () => {
    const clientError = {
      isAxiosError: true,
      response: { status: 404, data: 'User not found' }
    };
    const result = handleApiError(clientError);
    
    expect(result.type).toBe('4xx');
    expect(result.status).toBe(404);
    expect(result.message).toBe('User not found');
  });
});
```

### **Security Considerations**

- **Error Message Sanitization**: Avoid exposing sensitive server information
- **Rate Limiting**: Implement error-based rate limiting for suspicious patterns  
- **Audit Logging**: Log security-relevant errors for monitoring and analysis
- **Input Validation**: Ensure error handling doesn't bypass input validation
