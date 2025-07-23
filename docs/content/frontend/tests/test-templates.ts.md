# test-templates.ts - Comprehensive Test Data Factory System

## Purpose

The `test-templates.ts` file provides a comprehensive factory system for generating consistent, realistic test data across all frontend tests. It includes factories for API types, UI components, configuration objects, monitoring data, and specialized test scenarios, ensuring consistent test data structure and reducing test setup boilerplate.

## Key Components

### **Core Factory Pattern**

```typescript
// Standard factory pattern with overrides
export function createUser(overrides: Partial<User> = {}): User {
  return {
    id: overrides.id ?? Math.floor(Math.random() * 10000),
    email: overrides.email ?? `${randomString(5)}@example.com`,
    name: overrides.name ?? `user_${randomString(4)}`,
    bio: overrides.bio ?? null,
    avatar_url: overrides.avatar_url ?? null,
    created_at: overrides.created_at ?? new Date().toISOString(),
    updated_at: overrides.updated_at ?? new Date().toISOString(),
    ...overrides,
  };
}
```

### **Template Categories**

The file organizes test templates into comprehensive categories:

- **Basic Data Types**: Users, uploads, files, forms
- **API Types**: Requests, responses, errors, pagination
- **Authentication**: Tokens, login/register requests, auth errors
- **UI Components**: Buttons, inputs, cards, form props
- **WebSocket**: Notifications, events, connection metadata
- **Configuration**: Environment config, feature flags
- **Monitoring**: Error reports, performance metrics
- **Specialized Scenarios**: Expired tokens, network errors, validation failures

## Core Template Factories

### **User Management Templates**

```typescript
// Basic user creation
export function createUser(overrides: Partial<User> = {}): User;

// API-specific user creation
export function createApiUser(overrides: Partial<User> = {}): User;

// User update request template
export function createUserUpdateRequest(
  overrides: Partial<UserUpdateRequest> = {},
): UserUpdateRequest;

// Usage examples:
const basicUser = createUser({ name: "John Doe" });
const adminUser = createUser({
  email: "admin@example.com",
  name: "Administrator",
});
const updateRequest = createUserUpdateRequest({ bio: "Updated biography" });
```

### **Upload System Templates**

```typescript
// Upload object with realistic progress and status
export function createUpload(overrides: Partial<TestUpload> = {}): TestUpload;

// Upload list generation
export function createUploadList(
  count = 3,
  overrides: Partial<TestUpload> = {},
): TestUpload[];

// API upload response
export function createApiUpload(overrides: Partial<Upload> = {}): Upload;

// File upload response
export function createFileUploadResponse(
  overrides: Partial<FileUploadResponse> = {},
): FileUploadResponse;

// Usage examples:
const pendingUpload = createUpload({ status: "pending" });
const uploadList = createUploadList(5, { status: "completed" });
const errorUpload = createUpload({ status: "error", progress: 0 });
```

### **Authentication Templates**

```typescript
// JWT token management
export function createAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens;

// Token lifecycle scenarios
export function createExpiredAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens;
export function createSoonToExpireAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens;
export function createValidAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens;

// Authentication requests
export function createAuthLoginRequest(
  overrides: Partial<AuthLoginRequest> = {},
): AuthLoginRequest;
export function createAuthRegisterRequest(
  overrides: Partial<AuthRegisterRequest> = {},
): AuthRegisterRequest;

// Error scenarios
export function createAuthError(
  type: AuthErrorType,
  overrides: Partial<AuthError> = {},
): AuthError;
```

## Advanced Template Patterns

### **JWT Token Testing Scenarios**

```typescript
// Expired tokens for refresh testing
export function createExpiredAuthTokens(): AuthTokens {
  const now = Math.floor(Date.now() / 1000);
  const exp = now - 3600; // 1 hour ago (expired)

  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = btoa(
    JSON.stringify({
      sub: randomInt(1, 1000).toString(),
      email: `user${randomString(4)}@example.com`,
      exp,
      iat: now - 7200, // 2 hours ago
      iss: "reviewpoint",
      roles: ["user"],
    }),
  );
  const signature = randomString(43);

  return {
    access_token: `${header}.${payload}.${signature}`,
    refresh_token: `rt_${randomString(64)}`,
    token_type: "bearer",
  };
}

// Soon-to-expire tokens for refresh buffer testing
export function createSoonToExpireAuthTokens(): AuthTokens {
  const now = Math.floor(Date.now() / 1000);
  const exp = now + 60; // 1 minute from now (within refresh buffer)
  // ... similar implementation with future expiry
}
```

### **API Response Templates**

```typescript
// Generic API response wrapper
export function createApiResponse<T>(
  data: T,
  overrides: Partial<ApiResponse<T>> = {},
): ApiResponse<T> {
  return {
    data,
    error: overrides.error,
    ...overrides,
  };
}

// Error response factory
export function createApiErrorResponse(error: string): ApiResponse<never> {
  return {
    data: null,
    error,
  };
}

// Paginated response factory
export function createPaginatedResponse<T>(
  items: T[],
  overrides: Partial<PaginatedResponse<T>> = {},
): PaginatedResponse<T> {
  const total = overrides.total || items.length;
  const per_page = overrides.per_page || 10;
  const page = overrides.page || 1;
  const pages = Math.ceil(total / per_page);

  return {
    items,
    total,
    page,
    per_page,
    pages,
    ...overrides,
  };
}
```

## UI Component Templates

### **Form Component Testing**

```typescript
// Button props for UI testing
export function createButtonProps(
  overrides: Partial<ButtonProps> = {},
): ButtonProps {
  const variants = [
    "default",
    "destructive",
    "outline",
    "secondary",
    "ghost",
    "link",
  ] as const;
  const sizes = ["default", "sm", "lg", "icon"] as const;

  return {
    variant: overrides.variant || variants[randomInt(0, variants.length - 1)],
    size: overrides.size || sizes[randomInt(0, sizes.length - 1)],
    className: overrides.className || "",
    children: overrides.children || "Button",
    asChild: overrides.asChild ?? false,
    ...overrides,
  };
}

// Input props for form testing
export function createInputProps(
  overrides: Partial<InputProps> = {},
): InputProps {
  const types = ["text", "email", "password", "number", "file"] as const;

  return {
    className: overrides.className || "",
    type: overrides.type || types[randomInt(0, types.length - 1)],
    value: overrides.value || randomString(8),
    placeholder: overrides.placeholder || "Enter value",
    disabled: overrides.disabled ?? false,
    ...overrides,
  };
}
```

### **Upload Form Templates**

```typescript
// Upload form initial state
export function createUploadFormData(
  overrides: Partial<UploadFormData> = {},
): UploadFormData {
  return {
    name: overrides.name || `${randomString(8)}.pdf`,
    progress: 0,
    status: "pending", // Always force status to 'pending' for form state
    ...overrides,
  };
}

// Upload status variations
export function randomUploadStatus(): TestUpload["status"] {
  const statuses: TestUpload["status"][] = [
    "pending",
    "uploading",
    "completed",
    "error",
  ];
  return statuses[randomInt(0, statuses.length - 1)];
}
```

## WebSocket and Real-Time Templates

### **Notification System Templates**

```typescript
export function createTestNotification(
  overrides: Partial<{
    id: string;
    type: "info" | "success" | "warning" | "error";
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
    persistent?: boolean;
  }> = {},
) {
  return {
    id: randomString(16),
    type: "info",
    title: "Test Notification",
    message: "This is a test notification",
    timestamp: new Date(),
    read: false,
    persistent: false,
    ...overrides,
  };
}
```

### **WebSocket Event Templates**

```typescript
// Upload progress events
export function createTestUploadProgress(overrides = {}) {
  return {
    uploadId: randomString(16),
    progress: randomInt(0, 100),
    status: "uploading",
    timestamp: new Date(),
    ...overrides,
  };
}

// Generic WebSocket events
export function createTestWebSocketEvent(overrides = {}) {
  return {
    type: "test_event",
    data: { message: "Test event data" },
    timestamp: new Date(),
    ...overrides,
  };
}

// Connection metadata
export function createTestConnectionMetadata(overrides = {}) {
  return {
    connectionId: randomString(32),
    userId: randomString(16),
    connectedAt: new Date(),
    lastHeartbeat: new Date(),
    ...overrides,
  };
}
```

## Configuration and Environment Templates

### **Environment Configuration**

```typescript
export function createEnvironmentConfig(
  overrides: Partial<EnvironmentConfig> = {},
): EnvironmentConfig {
  return {
    NODE_ENV: "test",
    API_BASE_URL: "http://localhost:8000",
    API_TIMEOUT: 10000,
    WS_URL: "ws://localhost:8000/api/v1/ws",
    SENTRY_DSN: undefined,
    ENABLE_ANALYTICS: false,
    LOG_LEVEL: "debug",
    ENABLE_ERROR_REPORTING: true,
    ENABLE_PERFORMANCE_MONITORING: true,
    APP_VERSION: "0.1.0-test",
    APP_NAME: "ReViewPoint (Test)",
    ...overrides,
  };
}

// Environment-specific configurations
export function createDevelopmentEnvironmentConfig(): EnvironmentConfig;
export function createProductionEnvironmentConfig(): EnvironmentConfig;
```

### **Feature Flags Templates**

```typescript
export function createFeatureFlags(
  overrides: Partial<FeatureFlags> = {},
): FeatureFlags {
  return {
    enablePasswordReset: true,
    enableSocialLogin: false,
    enableTwoFactorAuth: false,
    enableMultipleFileUpload: true,
    enableDragDropUpload: true,
    enableUploadProgress: true,
    enableFilePreview: true,
    enableAiReviews: false,
    enableCollaborativeReviews: false,
    enableReviewComments: true,
    enableReviewExport: true,
    enableDarkMode: true,
    enableNotifications: true,
    enableBreadcrumbs: true,
    enableSidebar: true,
    enableWebSocket: true,
    enableVirtualization: false,
    enableLazyLoading: true,
    enableCodeSplitting: true,
    enableAnalytics: false,
    enableErrorReporting: true,
    enablePerformanceMonitoring: true,
    enableWebVitals: true,
    enableDevTools: false,
    enableDebugMode: false,
    enableTestMode: true,
    ...overrides,
  };
}

// Environment-specific feature flag sets
export function createDevelopmentFeatureFlags(): FeatureFlags;
export function createProductionFeatureFlags(): FeatureFlags;
```

## Error and Monitoring Templates

### **Error Report Templates**

```typescript
export function createErrorReport(
  overrides: Partial<ErrorReport> = {},
): ErrorReport {
  const severities: ErrorReport["severity"][] = [
    "low",
    "medium",
    "high",
    "critical",
  ];

  return {
    id: randomString(16),
    timestamp: new Date(),
    message: "Test error message",
    stack: `Error: Test error message\n    at TestFunction (test.js:1:1)`,
    componentStack: undefined,
    errorBoundary: undefined,
    props: undefined,
    userAgent: "Mozilla/5.0 (Test Browser)",
    url: "http://localhost:3000/test",
    userId: undefined,
    severity: severities[randomInt(0, severities.length - 1)],
    context: {},
    ...overrides,
  };
}
```

### **Performance Metric Templates**

```typescript
export function createPerformanceMetric(
  overrides: Partial<PerformanceMetric> = {},
): PerformanceMetric {
  const metricNames = ["CLS", "FCP", "INP", "LCP", "TTFB"];
  const ratings: PerformanceMetric["rating"][] = [
    "good",
    "needs-improvement",
    "poor",
  ];

  return {
    id: randomString(16),
    name: metricNames[randomInt(0, metricNames.length - 1)],
    value: randomInt(100, 3000),
    rating: ratings[randomInt(0, ratings.length - 1)],
    timestamp: Date.now(),
    url: "http://localhost:3000/test",
    navigationType: "navigate",
    deviceType: "desktop",
    ...overrides,
  };
}
```

## Specialized Error Templates

### **Validation Error Templates**

```typescript
export function createValidationError(
  field: string,
  message: string,
  code?: string,
): ApiError {
  return {
    message: "Validation failed",
    type: "validation_error",
    field_errors: [{ field, message, code }],
  };
}

export function createNetworkError(): ApiError {
  return {
    message: "Network error occurred",
    type: "network_error",
    details: {
      code: "NETWORK_ERROR",
      timestamp: new Date().toISOString(),
    },
  };
}
```

## Utility Functions

### **Test Infrastructure**

```typescript
// Error creation with type safety
export function createTestError(message: string | Error = "Test error"): Error {
  if (message instanceof Error) {
    return message; // Return existing error object
  }
  return new Error(message);
}

// React Query cache management
export function clearReactQueryCache() {
  // Placeholder for clearing all react-query caches
  // Implementation depends on QueryClient setup
}

// Analytics event templates
export function createAnalyticsEvent(
  overrides: Partial<AnalyticsEvent> = {},
): AnalyticsEvent {
  return {
    name: overrides.name || `test_event_${randomString(5)}`,
    props: overrides.props || { foo: randomString(3) },
    ...overrides,
  };
}
```

## Usage Patterns

### **Basic Test Setup**

```typescript
import {
  createUser,
  createUpload,
  createAuthTokens,
  createApiResponse
} from '@/tests/test-templates';

describe('UserProfile Component', () => {
  it('should display user information', () => {
    const user = createUser({
      name: 'John Doe',
      email: 'john@example.com'
    });

    render(<UserProfile user={user} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### **API Testing**

```typescript
import {
  createApiResponse,
  createUser,
  createApiErrorResponse,
} from "@/tests/test-templates";

describe("User API", () => {
  it("should handle successful user fetch", async () => {
    const user = createUser();
    const response = createApiResponse(user);

    mockAxios.get.mockResolvedValue({ data: response });

    const result = await fetchUser(user.id);
    expect(result).toEqual(user);
  });

  it("should handle API error", async () => {
    const errorResponse = createApiErrorResponse("User not found");

    mockAxios.get.mockResolvedValue({ data: errorResponse });

    await expect(fetchUser(999)).rejects.toThrow("User not found");
  });
});
```

### **Authentication Testing**

```typescript
import {
  createAuthTokens,
  createExpiredAuthTokens,
  createAuthLoginRequest,
} from "@/tests/test-templates";

describe("Token Service", () => {
  it("should refresh expired tokens", async () => {
    const expiredTokens = createExpiredAuthTokens();
    const newTokens = createAuthTokens();

    mockRefreshTokens.mockResolvedValue(newTokens);

    const result = await tokenService.refreshIfNeeded(expiredTokens);
    expect(result).toEqual(newTokens);
  });

  it("should handle login request", async () => {
    const loginRequest = createAuthLoginRequest({
      email: "user@example.com",
      password: "password123",
    });

    const tokens = createAuthTokens();
    mockLogin.mockResolvedValue(tokens);

    const result = await authService.login(loginRequest);
    expect(result).toEqual(tokens);
  });
});
```

### **Component Props Testing**

```typescript
import { createButtonProps, createInputProps } from '@/tests/test-templates';

describe('Button Component', () => {
  it('should render with different variants', () => {
    const destructiveProps = createButtonProps({ variant: 'destructive' });
    const outlineProps = createButtonProps({ variant: 'outline' });

    render(<Button {...destructiveProps} />);
    render(<Button {...outlineProps} />);

    expect(screen.getByRole('button', { name: destructiveProps.children }))
      .toHaveClass('destructive');
  });
});
```

## Dependencies

### **Core Dependencies**

- `@/lib/api/types` - API type definitions for template creation
- `@/lib/config/environment` - Environment configuration types
- `@/lib/config/featureFlags` - Feature flag type definitions
- `@/lib/monitoring/errorMonitoring` - Error report type definitions
- `@/lib/monitoring/performanceMonitoring` - Performance metric types
- `./test-utils` - Random data generation utilities

### **Test Utility Integration**

```typescript
import {
  randomDate,
  randomDateWithOffset,
  randomInt,
  randomString,
  testLogger,
  randomStatus,
} from "./test-utils";
```

## Related Files

- [test-utils.ts](test-utils.ts.md) - Random data generation utilities
- [api/types.ts](../src/lib/api/types.ts.md) - API type definitions
- [environment.ts](../src/lib/config/environment.ts.md) - Environment configuration
- [featureFlags.ts](../src/lib/config/featureFlags.ts.md) - Feature flag definitions

## Development Notes

### **Factory Pattern Best Practices**

- **Consistent Overrides**: All factories accept partial overrides for customization
- **Realistic Defaults**: Default values should represent realistic data
- **Type Safety**: Full TypeScript support with proper type inference
- **Logging Integration**: All factories include appropriate test logging
- **Deterministic Randomization**: Use controlled randomization for reproducible tests

### **Extending Templates**

```typescript
// Adding new template categories
export function createNewEntityTemplate(
  overrides: Partial<NewEntity> = {},
): NewEntity {
  const entity: NewEntity = {
    // Default properties with realistic values
    ...overrides,
  };

  testLogger.debug("Created new entity template", entity);
  return entity;
}

// Specialized scenario templates
export function createNewEntityErrorScenario(): NewEntity {
  return createNewEntityTemplate({
    // Error-specific property overrides
  });
}
```

### **Performance Considerations**

- **Memory Efficiency**: Large object creation is optimized for test environments
- **Generation Speed**: Fast template creation for large test suites
- **Cleanup**: Templates don't hold references to prevent memory leaks
- **Batch Creation**: List generation functions for bulk test data needs
