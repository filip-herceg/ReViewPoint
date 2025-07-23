# Generated API Client

**File:** `frontend/src/lib/api/generated/client.ts`  
**Purpose:** Auto-generated type-safe HTTP client from OpenAPI schema  
**Lines of Code:** 76  
**Type:** Generated Infrastructure Module  
**Generated:** 2025-07-08T06:10:00.000Z  

## Overview

The generated API client provides a fully type-safe HTTP client generated directly from the OpenAPI schema. It serves as the foundational layer for type-safe API communication, ensuring that all API calls are validated at compile time against the actual backend API specification.

## Architecture

### Core Components

#### Generated Client Instance
```typescript
export const generatedApiClient = createClient<paths>({
    baseUrl: import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000",
    headers: {
        "Content-Type": "application/json",
    },
});
```

#### Request/Response Interceptors
```typescript
generatedApiClient.use({
    onRequest({ request }) {
        // Automatic request logging
    },
    onResponse({ response }) {
        // Automatic response logging
    }
});
```

#### Utility Functions
```typescript
export function isApiError(error: unknown): error is { message: string; status?: number }
export function getApiErrorMessage(error: unknown): string
```

## Key Features

### 🛡️ **Complete Type Safety**

- **Schema-Driven**: Types generated directly from OpenAPI specification
- **Compile-Time Validation**: Path parameters, query parameters, and request bodies validated at build time
- **Response Typing**: Fully typed responses with proper error handling
- **Path Safety**: URL paths validated against actual API endpoints

### 📊 **Automatic Logging**

- **Request Logging**: All outgoing requests logged with method, URL, and headers
- **Response Logging**: All responses logged with status, URL, and timing
- **Debug Level**: Uses debug log level to avoid production noise
- **Structured Data**: Consistent log format for monitoring and debugging

### 🔧 **Environment Configuration**

- **Base URL**: Configurable via `VITE_API_BASE_URL` environment variable
- **Default Headers**: Automatic `Content-Type: application/json` for all requests
- **Development Fallback**: Defaults to `http://localhost:8000` for local development

## Usage Patterns

### Type-Safe API Calls

```typescript
import { generatedApiClient } from '@/lib/api/generated/client';

// Fully typed GET request
const { data, error } = await generatedApiClient.GET("/api/v1/uploads");
if (error) {
    // error is typed based on API specification
    console.error('API Error:', error);
} else {
    // data is typed as FileListResponse
    console.log('Files:', data.files);
}

// Typed POST request with body validation
const { data, error } = await generatedApiClient.POST("/api/v1/uploads", {
    body: formData  // Body type validated at compile time
});
```

### Path Parameter Safety

```typescript
// Compile-time validation of path parameters
const { data, error } = await generatedApiClient.GET("/api/v1/uploads/{filename}", {
    params: {
        path: { filename: "document.pdf" }  // filename parameter required and typed
    }
});

// Query parameter validation
const { data, error } = await generatedApiClient.GET("/api/v1/uploads", {
    params: {
        query: {
            limit: 50,        // ✅ Valid query parameter
            offset: 0,        // ✅ Valid query parameter
            sort: "created_at" // ✅ Valid enum value
            // invalid: "test" // ❌ Compile error - invalid parameter
        }
    }
});
```

## Error Handling Utilities

### Type Guards

```typescript
// Safe error type checking
if (isApiError(error)) {
    // TypeScript knows error has message and optional status
    console.log('Error message:', error.message);
    console.log('Status code:', error.status);
}

// Extract error messages safely
const errorMessage = getApiErrorMessage(unknownError);
// Always returns a string, handles all error types
```

### Integration with Error Handling

```typescript
import { handleApiError } from '@/lib/api/errorHandling';

const makeApiCall = async () => {
    const { data, error } = await generatedApiClient.GET("/api/endpoint");
    
    if (error) {
        // Combine generated client error handling with centralized error processing
        const handledError = handleApiError(error);
        throw new Error(handledError.message);
    }
    
    return data;
};
```

## Logging Integration

### Request Logging

```typescript
// Automatically logs all requests
logger.debug("🔄 API Request:", {
    method: "GET",
    url: "http://localhost:8000/api/v1/uploads",
    headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer ..."
    }
});
```

### Response Logging

```typescript
// Automatically logs all responses
logger.debug("✅ API Response:", {
    status: 200,
    statusText: "OK",
    url: "http://localhost:8000/api/v1/uploads"
});
```

## Development Workflow

### Schema Synchronization

```bash
# Generate types from OpenAPI schema
npm run generate:api-types

# This updates both client.ts and schema.ts
# Ensuring frontend stays in sync with backend API
```

### Type Safety Benefits

```typescript
// Compile-time catching of API changes
const response = await generatedApiClient.GET("/api/v1/uploads");

// If backend changes response structure, TypeScript will error
response.data.files.forEach(file => {
    console.log(file.filename);  // ✅ Type-safe access
    // console.log(file.invalid); // ❌ Compile error if property doesn't exist
});
```

## Environment Configuration

### Development Setup

```typescript
// .env.development
VITE_API_BASE_URL=http://localhost:8000

// .env.production  
VITE_API_BASE_URL=https://api.reviewpoint.com
```

### Runtime Configuration

```typescript
// Client automatically uses environment-specific base URL
const baseUrl = import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000";

// Headers can be modified at runtime if needed
generatedApiClient.headers = {
    ...generatedApiClient.headers,
    'Authorization': `Bearer ${token}`
};
```

## Performance Considerations

### ⚡ **Optimization Features**

- **Tree Shaking**: Only imports types and functions that are used
- **Minimal Runtime**: Lightweight client with minimal overhead
- **Efficient Logging**: Debug-level logging only when enabled
- **Connection Reuse**: Single client instance for connection pooling

### 📈 **Scalability**

- **Type Generation**: Compile-time type checking, no runtime overhead
- **Request Batching**: Compatible with request batching strategies
- **Caching Integration**: Works with HTTP caching and React Query

## Integration Points

### Upload Operations

```typescript
// Used by type-safe upload client
import { generatedApiClient } from "../generated/client";

const { data, error } = await generatedApiClient.GET("/api/v1/uploads");
// Provides foundation for upload operations
```

### Authentication

```typescript
// Integration with auth system
generatedApiClient.use({
    onRequest({ request }) {
        // Add auth headers automatically
        const token = getAuthToken();
        if (token) {
            request.headers.set('Authorization', `Bearer ${token}`);
        }
        return request;
    }
});
```

## Generated Code Characteristics

### 🤖 **Auto-Generated Properties**

- **Timestamp**: Generation timestamp for tracking schema versions
- **Schema Sync**: Automatically updated when backend API changes
- **Type Definitions**: All types derived from actual API specification
- **Path Mappings**: URL paths mapped to TypeScript types

### 🔄 **Regeneration Process**

1. Backend API schema exported (OpenAPI/Swagger)
2. Frontend build process generates types and client
3. Type checking ensures compatibility
4. Deploy with guaranteed API compatibility

## Testing Support

### Mock Integration

```typescript
// Testing with typed mocks
const mockClient = {
    GET: jest.fn().mockResolvedValue({
        data: {
            files: [],
            total: 0
        } as FileListResponse
    })
};
```

### Type Validation Testing

```typescript
// Test that API responses match expected types
test('API response matches schema', async () => {
    const { data } = await generatedApiClient.GET("/api/v1/uploads");
    
    expect(data).toHaveProperty('files');
    expect(data).toHaveProperty('total');
    expect(Array.isArray(data.files)).toBe(true);
});
```

## Migration Benefits

### From Manual API Calls

```typescript
// Before: Manual HTTP calls with no type safety
const response = await fetch('/api/uploads');
const data = await response.json(); // Unknown type

// After: Generated client with full type safety
const { data, error } = await generatedApiClient.GET("/api/v1/uploads");
// data is fully typed as FileListResponse
```

### API Evolution

```typescript
// When backend API changes:
// 1. Regenerate client from new schema
// 2. TypeScript compiler catches breaking changes
// 3. Fix issues at compile time before deployment
// 4. Guaranteed runtime compatibility
```

## Best Practices

### ✅ **Do's**

- **Regenerate Regularly**: Keep client in sync with backend changes
- **Use Type Guards**: Leverage provided error checking utilities
- **Environment Variables**: Configure base URL per environment
- **Error Integration**: Combine with centralized error handling
- **Log Monitoring**: Use debug logs for API call monitoring

### ❌ **Don'ts**

- **Don't Edit Manually**: File is auto-generated and will be overwritten
- **Don't Bypass Types**: Use the provided type-safe interfaces
- **Don't Hardcode URLs**: Use environment configuration
- **Don't Ignore Errors**: Always handle error responses
- **Don't Skip Regeneration**: Keep types synchronized with backend

## Related Documentation

- **OpenAPI Schema**: `schema.ts` - Generated type definitions
- **Type-Safe Upload Client**: `clients/uploads.ts.md` - Uses this client
- **Error Handling**: `errorHandling.ts.md` - Error processing integration
- **Base API**: `base.ts.md` - Alternative HTTP client
- **API Index**: `index.ts.md` - Main API orchestration

## Dependencies

- **openapi-fetch**: Type-safe fetch client library
- **@/logger**: Structured logging system
- **schema.ts**: Generated OpenAPI type definitions

---

*This module provides the auto-generated foundation for type-safe API communication, ensuring compile-time validation and runtime consistency between frontend and backend systems.*
