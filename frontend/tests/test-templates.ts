// Utility: Create a test error object for error handling tests
export function createTestError(message: string | Error = "Test error"): Error {
  // If the message is already an Error, return it directly instead of wrapping it
  if (message instanceof Error) {
    testLogger.debug("Returning existing error object", message);
    return message;
  }

  const err = new Error(message);
  testLogger.debug("Created test error object", err);
  return err;
}

// Centralized test data templates (factories) for frontend tests
// Use these to generate consistent test data in all tests
// You can import utilities from test-utils as needed

import type {
  ApiError,
  ApiResponse,
  AuthError,
  AuthLoginRequest,
  AuthRegisterRequest,
  AuthTokens,
  FileUploadResponse,
  PaginatedResponse,
  Upload,
  User,
  UserUpdateRequest,
} from "@/lib/api/types";
import { AuthErrorType } from "@/lib/api/types";
import {
  randomDate,
  randomDateWithOffset,
  randomInt,
  randomString,
  testLogger,
} from "./test-utils";

// Utility to clear all react-query caches for test isolation
export function clearReactQueryCache() {
  // If you use a global QueryClient, clear it here. Otherwise, clear all caches in your test setup.
  // This is a no-op placeholder for now, but you can call this in beforeEach/afterEach in tests.
  // If you use a custom QueryClient instance, call queryClient.clear() in your test file.
  // Example:
  // queryClient.clear();
  // For global cache: QueryClient.clear();
  // (No-op for now)
  testLogger.info("Cleared react-query cache (noop placeholder)");
}

// Update Upload type to match app (pending | uploading | completed | error)
export type TestUpload = {
  id: string;
  name: string;
  status: "pending" | "uploading" | "completed" | "error";
  progress: number;
  createdAt: string;
};

import { randomStatus } from "./test-utils";

// Pick a random status for TestUpload
export function randomUploadStatus(): TestUpload["status"] {
  const statuses: TestUpload["status"][] = [
    "pending",
    "uploading",
    "completed",
    "error",
  ];
  const status = statuses[randomInt(0, statuses.length - 1)];
  if (status === "error") {
    testLogger.warn("Picked random upload status: error");
  } else {
    testLogger.debug("Picked random upload status:", status);
  }
  return status;
}

export function createUpload(overrides: Partial<TestUpload> = {}): TestUpload {
  const upload: TestUpload = {
    id: overrides.id || randomString(6),
    name: overrides.name || `${randomString(4)}.pdf`,
    status: overrides.status || randomUploadStatus(),
    progress: overrides.progress ?? randomInt(0, 100),
    createdAt: overrides.createdAt || randomDate(),
    ...overrides,
  };
  if (upload.status === "error") {
    testLogger.error("Created upload with error status", upload);
  } else if (upload.progress === 0) {
    testLogger.info("Created upload with 0% progress", upload);
  } else {
    testLogger.debug("Created upload object", upload);
  }
  return upload;
}

// Create an array of uploads (for UploadList tests)
export function createUploadList(
  count = 3,
  overrides: Partial<TestUpload> = {},
): TestUpload[] {
  const list = Array.from({ length: count }, () => createUpload(overrides));
  if (count > 10) {
    testLogger.warn(`Created large upload list of length ${count}`);
  } else {
    testLogger.info(`Created upload list of length ${count}`, list);
  }
  return list;
}

// If you add user/auth features, add user templates here
// export function createUser(...) { ... }

export function createUser(overrides: Partial<User> = {}): User {
  const user: User = {
    id: overrides.id ?? Math.floor(Math.random() * 10000),
    email: overrides.email ?? `${randomString(5)}@example.com`,
    name:
      "name" in overrides
        ? (overrides.name ?? null)
        : `user_${randomString(4)}`,
    bio: overrides.bio ?? null,
    avatar_url: overrides.avatar_url ?? null,
    created_at: overrides.created_at ?? new Date().toISOString(),
    updated_at: overrides.updated_at ?? new Date().toISOString(),
  };
  if (user.name?.includes("admin")) {
    testLogger.info("Created admin user", user);
  } else {
    testLogger.debug("Created user", user);
  }
  return user;
}

// Template for upload form data (matches UploadForm initial state)
export type UploadFormData = {
  name: string;
  status: "pending";
  progress: number;
};

export function createUploadFormData(
  overrides: Partial<UploadFormData> = {},
): UploadFormData {
  const formData: UploadFormData = {
    ...overrides,
    name: overrides.name || `${randomString(8)}.pdf`,
    progress: 0,
    status: "pending", // Always force status to 'pending' to satisfy UploadFormData type
  };
  if (formData.name.endsWith(".pdf")) {
    testLogger.debug("Created upload form data for PDF", formData);
  } else {
    testLogger.info("Created upload form data", formData);
  }
  return formData;
}

// If you add forms, add form data templates here
// export function createUploadFormData(...) { ... }

// Template for plausible analytics event
export type AnalyticsEvent = {
  name: string;
  props?: Record<string, any>;
};

export function createAnalyticsEvent(
  overrides: Partial<AnalyticsEvent> = {},
): AnalyticsEvent {
  const event = {
    name: overrides.name || `test_event_${randomString(5)}`,
    props: overrides.props || { foo: randomString(3) },
    ...overrides,
  };
  if (event.name.startsWith("test_event_")) {
    testLogger.debug("Created test analytics event", event);
  } else {
    testLogger.info("Created analytics event", event);
  }
  return event;
}

// Template for button props (for UI tests)
export type ButtonProps = {
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
  children?: string;
  asChild?: boolean;
  [key: string]: any;
};

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
  const btn = {
    variant: overrides.variant || variants[randomInt(0, variants.length - 1)],
    size: overrides.size || sizes[randomInt(0, sizes.length - 1)],
    className: overrides.className || "",
    children: overrides.children || "Button",
    asChild: overrides.asChild ?? false,
    ...overrides,
  };
  if (btn.variant === "destructive") {
    testLogger.warn("Created destructive button props", btn);
  } else {
    testLogger.debug("Created button props", btn);
  }
  return btn;
}

// Template for input props (for UI tests)
export type InputProps = {
  className?: string;
  type?: string;
  value?: string;
  placeholder?: string;
  disabled?: boolean;
  [key: string]: any;
};

export function createInputProps(
  overrides: Partial<InputProps> = {},
): InputProps {
  const types = ["text", "email", "password", "number", "file"] as const;
  const input = {
    className: overrides.className || "",
    type: overrides.type || types[randomInt(0, types.length - 1)],
    value: overrides.value || randomString(8),
    placeholder: overrides.placeholder || "Enter value",
    disabled: overrides.disabled ?? false,
    ...overrides,
  };
  if (input.type === "password") {
    testLogger.info("Created password input props", input);
  } else {
    testLogger.debug("Created input props", input);
  }
  return input;
}

// Template for card props (for UI tests)
export type CardProps = {
  className?: string;
  children?: React.ReactNode;
  [key: string]: any;
};

export function createCardProps(overrides: Partial<CardProps> = {}): CardProps {
  const card = {
    className: overrides.className || "",
    children: overrides.children || "Card Content",
    ...overrides,
  };
  if (card.className?.includes("highlight")) {
    testLogger.info("Created highlighted card props", card);
  } else {
    testLogger.debug("Created card props", card);
  }
  return card;
}

// API Types Templates
// Templates for testing API types and responses

// Auth Templates
export function createAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens {
  const tokens: AuthTokens = {
    access_token:
      overrides.access_token ||
      `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${randomString(32)}`,
    refresh_token: overrides.refresh_token || `refresh_${randomString(32)}`,
    token_type: "bearer",
    ...overrides,
  };
  testLogger.debug("Created auth tokens", {
    access_token: `${tokens.access_token.substring(0, 20)}...`,
    refresh_token: `${tokens.refresh_token.substring(0, 20)}...`,
    token_type: tokens.token_type,
  });
  return tokens;
}

export function createAuthRegisterRequest(
  overrides: Partial<AuthRegisterRequest> = {},
): AuthRegisterRequest {
  const request: AuthRegisterRequest = {
    email: overrides.email || `${randomString(5)}@example.com`,
    password: overrides.password || `securePassword${randomString(3)}`,
    name: overrides.name || `User ${randomString(4)}`,
    ...overrides,
  };
  testLogger.debug("Created auth register request", {
    email: request.email,
    name: request.name,
  });
  return request;
}

export function createAuthLoginRequest(
  overrides: Partial<AuthLoginRequest> = {},
): AuthLoginRequest {
  const request: AuthLoginRequest = {
    email: overrides.email || `${randomString(5)}@example.com`,
    password: overrides.password || "password123",
    ...overrides,
  };
  testLogger.debug("Created auth login request", { email: request.email });
  return request;
}

export function createAuthError(
  type: AuthErrorType = AuthErrorType.INVALID_CREDENTIALS,
  overrides: Partial<AuthError> = {},
): AuthError {
  const error: AuthError = {
    type,
    message: overrides.message || `Auth error: ${type}`,
    status:
      overrides.status || (type === AuthErrorType.TOKEN_EXPIRED ? 401 : 400),
    details: overrides.details,
    ...overrides,
  };
  testLogger.error("Created auth error", error);
  return error;
}

// User Templates
export function createApiUser(overrides: Partial<User> = {}): User {
  const user: User = {
    id: overrides.id || randomInt(1, 10000),
    email: overrides.email || `${randomString(5)}@example.com`,
    name: overrides.name || `User ${randomString(4)}`,
    bio: overrides.bio || null,
    avatar_url: overrides.avatar_url || null,
    created_at: overrides.created_at || randomDate(),
    updated_at: overrides.updated_at || randomDate(),
    ...overrides,
  };
  testLogger.debug("Created API user", {
    id: user.id,
    email: user.email,
    name: user.name,
  });
  return user;
}

export function createUserUpdateRequest(
  overrides: Partial<UserUpdateRequest> = {},
): UserUpdateRequest {
  const request: UserUpdateRequest = {
    name:
      overrides.name !== undefined
        ? overrides.name
        : `Updated User ${randomString(3)}`,
    bio:
      overrides.bio !== undefined
        ? overrides.bio
        : `Updated bio ${randomString(5)}`,
    ...overrides,
  };
  testLogger.debug("Created user update request", request);
  return request;
}

// Upload Templates
export function createApiUpload(overrides: Partial<Upload> = {}): Upload {
  const statuses: Upload["status"][] = [
    "pending",
    "uploading",
    "completed",
    "error",
    "cancelled",
  ];
  const upload: Upload = {
    id: overrides.id || randomString(8),
    name: overrides.name || `${randomString(5)}.pdf`,
    status: overrides.status || statuses[randomInt(0, statuses.length - 1)],
    progress:
      overrides.progress ??
      (overrides.status === "completed" ? 100 : randomInt(0, 99)),
    createdAt: overrides.createdAt || randomDate(),
    size: overrides.size || randomInt(1024, 10 * 1024 * 1024), // 1KB to 10MB
    type: overrides.type || "application/pdf",
    ...overrides,
  };

  if (upload.status === "error") {
    testLogger.warn("Created API upload with error status", upload);
  } else {
    testLogger.debug("Created API upload", upload);
  }
  return upload;
}

export function createFileUploadResponse(
  overrides: Partial<FileUploadResponse> = {},
): FileUploadResponse {
  const response: FileUploadResponse = {
    filename: overrides.filename || `${randomString(5)}.pdf`,
    url: overrides.url || `/uploads/${randomString(8)}.pdf`,
    ...overrides,
  };
  testLogger.debug("Created file upload response", response);
  return response;
}

// Generic API Response Templates
export function createApiResponse<T>(
  data: T,
  overrides: Partial<ApiResponse<T>> = {},
): ApiResponse<T> {
  const response: ApiResponse<T> = {
    data,
    error: overrides.error,
    ...overrides,
  };

  if (response.error) {
    testLogger.error("Created API error response", { error: response.error });
  } else {
    testLogger.debug("Created API success response", { dataType: typeof data });
  }
  return response;
}

export function createApiErrorResponse(error: string): ApiResponse<never> {
  const response: ApiResponse<never> = {
    data: null,
    error,
  };
  testLogger.error("Created API error response", response);
  return response;
}

export function createPaginatedResponse<T>(
  items: T[],
  overrides: Partial<PaginatedResponse<T>> = {},
): PaginatedResponse<T> {
  const total = overrides.total || items.length;
  const per_page = overrides.per_page || 10;
  const page = overrides.page || 1;
  const pages = Math.ceil(total / per_page);

  const response: PaginatedResponse<T> = {
    items,
    total,
    page,
    per_page,
    pages,
    ...overrides,
  };

  testLogger.debug("Created paginated response", {
    itemCount: items.length,
    total,
    page,
    pages,
  });
  return response;
}

// Validation Error Templates
export function createValidationError(
  field: string,
  message: string,
  code?: string,
): ApiError {
  const error: ApiError = {
    message: "Validation failed",
    type: "validation_error",
    field_errors: [
      {
        field,
        message,
        code,
      },
    ],
  };
  testLogger.error("Created validation error", error);
  return error;
}

export function createNetworkError(): ApiError {
  const error: ApiError = {
    message: "Network error occurred",
    type: "network_error",
    details: {
      code: "NETWORK_ERROR",
      timestamp: new Date().toISOString(),
    },
  };
  testLogger.error("Created network error", error);
  return error;
}

// Enhanced Auth Token Templates for JWT Testing

// Create expired auth tokens for testing refresh scenarios
export function createExpiredAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens {
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

  const tokens: AuthTokens = {
    access_token: overrides.access_token || `${header}.${payload}.${signature}`,
    refresh_token: overrides.refresh_token || `rt_${randomString(64)}`,
    token_type: "bearer",
    ...overrides,
  };
  testLogger.debug("Created expired auth tokens", {
    hasAccessToken: !!tokens.access_token,
    hasRefreshToken: !!tokens.refresh_token,
    expiry: exp,
  });
  return tokens;
}

// Create tokens that will expire soon (for testing refresh buffer)
export function createSoonToExpireAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens {
  const now = Math.floor(Date.now() / 1000);
  const exp = now + 60; // 1 minute from now (within refresh buffer)

  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = btoa(
    JSON.stringify({
      sub: randomInt(1, 1000).toString(),
      email: `user${randomString(4)}@example.com`,
      exp,
      iat: now - 60, // 1 minute ago
      iss: "reviewpoint",
      roles: ["user"],
    }),
  );
  const signature = randomString(43);

  const tokens: AuthTokens = {
    access_token: overrides.access_token || `${header}.${payload}.${signature}`,
    refresh_token: overrides.refresh_token || `rt_${randomString(64)}`,
    token_type: "bearer",
    ...overrides,
  };
  testLogger.debug("Created soon-to-expire auth tokens", {
    hasAccessToken: !!tokens.access_token,
    hasRefreshToken: !!tokens.refresh_token,
    expiry: exp,
    timeToExpiry: exp - now,
  });
  return tokens;
}

// Create valid long-lived auth tokens (for testing normal scenarios)
export function createValidAuthTokens(
  overrides: Partial<AuthTokens> = {},
): AuthTokens {
  const now = Math.floor(Date.now() / 1000);
  const exp = now + 3600; // 1 hour from now

  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = btoa(
    JSON.stringify({
      sub: randomInt(1, 1000).toString(),
      email: `user${randomString(4)}@example.com`,
      exp,
      iat: now,
      iss: "reviewpoint",
      roles: ["user"],
    }),
  );
  const signature = randomString(43);

  const tokens: AuthTokens = {
    access_token: overrides.access_token || `${header}.${payload}.${signature}`,
    refresh_token: overrides.refresh_token || `rt_${randomString(64)}`,
    token_type: "bearer",
    ...overrides,
  };
  testLogger.debug("Created valid auth tokens", {
    hasAccessToken: !!tokens.access_token,
    hasRefreshToken: !!tokens.refresh_token,
    expiry: exp,
    timeToExpiry: exp - now,
  });
  return tokens;
}

// Token Refresh Test Templates
export function createTokenRefreshRequest(refreshToken?: string) {
  const request = {
    refresh_token: refreshToken || `rt_${randomString(64)}`,
  };
  testLogger.debug("Created token refresh request", {
    hasRefreshToken: !!request.refresh_token,
  });
  return request;
}

export function createTokenRefreshResponse(
  overrides: Partial<AuthTokens> = {},
): AuthTokens {
  const tokens = createValidAuthTokens(overrides);
  testLogger.debug("Created token refresh response", {
    hasAccessToken: !!tokens.access_token,
    hasRefreshToken: !!tokens.refresh_token,
  });
  return tokens;
}

// Mock token service state for testing
export function createTokenServiceMockState() {
  return {
    isRefreshing: false,
    refreshPromise: null,
    refreshQueue: [],
  };
}

// WebSocket-related test data factories

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
): {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  persistent?: boolean;
} {
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

export function createTestUploadProgress(
  overrides: Partial<{
    uploadId: string;
    progress: number;
    status: "uploading" | "completed" | "error";
    error?: string;
    timestamp: Date;
  }> = {},
): {
  uploadId: string;
  progress: number;
  status: "uploading" | "completed" | "error";
  error?: string;
  timestamp: Date;
} {
  return {
    uploadId: randomString(16),
    progress: randomInt(0, 100),
    status: "uploading",
    timestamp: new Date(),
    ...overrides,
  };
}

export function createTestWebSocketEvent(
  overrides: Partial<{
    type: string;
    data: any;
    timestamp: Date;
  }> = {},
): {
  type: string;
  data: any;
  timestamp: Date;
} {
  return {
    type: "test_event",
    data: { message: "Test event data" },
    timestamp: new Date(),
    ...overrides,
  };
}

export function createTestConnectionMetadata(
  overrides: Partial<{
    connectionId: string;
    userId: string;
    connectedAt: Date;
    lastHeartbeat: Date;
  }> = {},
): {
  connectionId: string;
  userId: string;
  connectedAt: Date;
  lastHeartbeat: Date;
} {
  return {
    connectionId: randomString(32),
    userId: randomString(16),
    connectedAt: new Date(),
    lastHeartbeat: new Date(),
    ...overrides,
  };
}

// Configuration and Monitoring Test Templates

import type { EnvironmentConfig } from "@/lib/config/environment";
import type { FeatureFlags } from "@/lib/config/featureFlags";
import type { ErrorReport } from "@/lib/monitoring/errorMonitoring";
import type { PerformanceMetric } from "@/lib/monitoring/performanceMonitoring";

// Environment Configuration Templates
export function createEnvironmentConfig(
  overrides: Partial<EnvironmentConfig> = {},
): EnvironmentConfig {
  const config: EnvironmentConfig = {
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

  testLogger.debug("Created environment config", {
    environment: config.NODE_ENV,
    apiBaseUrl: config.API_BASE_URL,
    logLevel: config.LOG_LEVEL,
  });

  return config;
}

export function createDevelopmentEnvironmentConfig(): EnvironmentConfig {
  return createEnvironmentConfig({
    NODE_ENV: "development",
    LOG_LEVEL: "debug",
    ENABLE_ANALYTICS: false,
    APP_NAME: "ReViewPoint (Dev)",
  });
}

export function createProductionEnvironmentConfig(): EnvironmentConfig {
  return createEnvironmentConfig({
    NODE_ENV: "production",
    API_BASE_URL: "https://api.reviewpoint.com",
    WS_URL: "wss://api.reviewpoint.com/api/v1/ws",
    LOG_LEVEL: "warn",
    ENABLE_ANALYTICS: true,
    SENTRY_DSN: "https://test-dsn@sentry.io/123",
    APP_VERSION: "1.0.0",
    APP_NAME: "ReViewPoint",
  });
}

// Feature Flags Templates
export function createFeatureFlags(
  overrides: Partial<FeatureFlags> = {},
): FeatureFlags {
  const flags: FeatureFlags = {
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

  const enabledFeatures = Object.entries(flags)
    .filter(([, enabled]) => enabled)
    .map(([feature]) => feature);

  testLogger.debug("Created feature flags", {
    totalFeatures: Object.keys(flags).length,
    enabledFeatures: enabledFeatures.length,
    enabledList: enabledFeatures,
  });

  return flags;
}

export function createDevelopmentFeatureFlags(): FeatureFlags {
  return createFeatureFlags({
    enableDevTools: true,
    enableDebugMode: true,
    enableSocialLogin: false,
    enableAiReviews: false,
    enableVirtualization: false,
  });
}

export function createProductionFeatureFlags(): FeatureFlags {
  return createFeatureFlags({
    enableDevTools: false,
    enableDebugMode: false,
    enableTestMode: false,
    enableSocialLogin: true,
    enableTwoFactorAuth: true,
    enableAiReviews: true,
    enableCollaborativeReviews: true,
    enableVirtualization: true,
    enableAnalytics: true,
  });
}

// Error Report Templates
export function createErrorReport(
  overrides: Partial<ErrorReport> = {},
): ErrorReport {
  const severities: ErrorReport["severity"][] = [
    "low",
    "medium",
    "high",
    "critical",
  ];
  const error: ErrorReport = {
    id: randomString(16),
    timestamp: new Date(),
    message: "Test error message",
    stack: `Error: Test error message\n    at TestFunction (test.js:1:1)\n    at Object.<anonymous> (test.js:5:1)`,
    componentStack: undefined,
    errorBoundary: undefined,
    props: undefined,
    userAgent: "Mozilla/5.0 (Test Browser)",
    url: "http://localhost:3000/test",
    userId: undefined,
    severity: severities[randomInt(0, severities.length - 1)],
    context: {
      source: "test",
      environment: "test",
    },
    ...overrides,
  };

  if (error.severity === "critical") {
    testLogger.error("Created critical error report", {
      id: error.id,
      message: error.message,
      severity: error.severity,
    });
  } else {
    testLogger.debug("Created error report", {
      id: error.id,
      severity: error.severity,
    });
  }

  return error;
}

export function createConsoleErrorReport(): ErrorReport {
  return createErrorReport({
    severity: "high",
    context: {
      source: "console.error",
      environment: "test",
    },
  });
}

export function createUnhandledRejectionErrorReport(): ErrorReport {
  return createErrorReport({
    message: "Unhandled promise rejection: Something went wrong",
    severity: "critical",
    context: {
      source: "unhandledrejection",
      reason: "Something went wrong",
      environment: "test",
    },
  });
}

export function createComponentErrorReport(): ErrorReport {
  return createErrorReport({
    componentStack:
      "    in ErrorComponent (at Error.tsx:1:1)\n    in App (at App.tsx:10:5)",
    errorBoundary: "EnhancedErrorBoundary",
    severity: "high",
    context: {
      source: "ErrorBoundary",
      environment: "test",
    },
  });
}

// Performance Metric Templates
export function createPerformanceMetric(
  overrides: Partial<PerformanceMetric> = {},
): PerformanceMetric {
  const metricNames = [
    "CLS",
    "FCP",
    "INP",
    "LCP",
    "TTFB",
    "resource-timing",
    "dns-lookup",
    "tcp-connect",
  ];
  const ratings: PerformanceMetric["rating"][] = [
    "good",
    "needs-improvement",
    "poor",
  ];
  const deviceTypes: PerformanceMetric["deviceType"][] = [
    "mobile",
    "tablet",
    "desktop",
  ];
  const navigationTypes = ["navigate", "reload", "back_forward", "prerender"];

  const metric: PerformanceMetric = {
    id: randomString(16),
    name: metricNames[randomInt(0, metricNames.length - 1)],
    value: randomInt(100, 5000),
    rating: ratings[randomInt(0, ratings.length - 1)],
    timestamp: Date.now(),
    url: "http://localhost:3000/test",
    navigationType: navigationTypes[randomInt(0, navigationTypes.length - 1)],
    deviceType: deviceTypes[randomInt(0, deviceTypes.length - 1)],
    ...overrides,
  };

  if (metric.rating === "poor") {
    testLogger.warn("Created poor performance metric", {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
    });
  } else {
    testLogger.debug("Created performance metric", {
      name: metric.name,
      rating: metric.rating,
    });
  }

  return metric;
}

export function createCLSMetric(
  rating: PerformanceMetric["rating"] = "good",
): PerformanceMetric {
  const values = {
    good: 0.05,
    "needs-improvement": 0.15,
    poor: 0.3,
  };

  return createPerformanceMetric({
    name: "CLS",
    value: values[rating],
    rating,
  });
}

export function createLCPMetric(
  rating: PerformanceMetric["rating"] = "good",
): PerformanceMetric {
  const values = {
    good: 2000,
    "needs-improvement": 3500,
    poor: 5000,
  };

  return createPerformanceMetric({
    name: "LCP",
    value: values[rating],
    rating,
  });
}

export function createINPMetric(
  rating: PerformanceMetric["rating"] = "good",
): PerformanceMetric {
  const values = {
    good: 150,
    "needs-improvement": 350,
    poor: 600,
  };

  return createPerformanceMetric({
    name: "INP",
    value: values[rating],
    rating,
  });
}

export function createWebVitalsMetrics(): PerformanceMetric[] {
  return [
    createCLSMetric("good"),
    createPerformanceMetric({ name: "FCP", value: 1500, rating: "good" }),
    createINPMetric("good"),
    createLCPMetric("good"),
    createPerformanceMetric({ name: "TTFB", value: 600, rating: "good" }),
  ];
}

export function createPoorWebVitalsMetrics(): PerformanceMetric[] {
  return [
    createCLSMetric("poor"),
    createPerformanceMetric({ name: "FCP", value: 4000, rating: "poor" }),
    createINPMetric("poor"),
    createLCPMetric("poor"),
    createPerformanceMetric({ name: "TTFB", value: 2500, rating: "poor" }),
  ];
}

// Mock Environment Variables Template (subset of ImportMetaEnv)
export function createMockImportMetaEnv(
  overrides: Partial<{
    NODE_ENV: string;
    VITE_API_BASE_URL?: string;
    VITE_API_TIMEOUT?: string;
    VITE_WS_URL?: string;
    VITE_SENTRY_DSN?: string;
    VITE_ENABLE_ANALYTICS?: string;
    VITE_LOG_LEVEL?: string;
    VITE_ENABLE_ERROR_REPORTING?: string;
    VITE_ENABLE_PERFORMANCE_MONITORING?: string;
    VITE_APP_VERSION?: string;
    VITE_APP_NAME?: string;
  }> = {},
) {
  const env = {
    NODE_ENV: "test",
    VITE_API_BASE_URL: "http://localhost:8000",
    VITE_API_TIMEOUT: "5000", // Changed from 10000 to match test expectations
    VITE_WS_URL: "ws://localhost:8000/api/v1", // Removed /ws suffix to match test expectations
    VITE_SENTRY_DSN: "",
    VITE_ENABLE_ANALYTICS: "true", // Changed from false to true to match test expectations
    VITE_LOG_LEVEL: "error", // Changed from debug to error to match test expectations
    VITE_ENABLE_ERROR_REPORTING: "true",
    VITE_ENABLE_PERFORMANCE_MONITORING: "true",
    VITE_APP_VERSION: "0.1.0-test",
    VITE_APP_NAME: "ReViewPoint (Test)",
    ...overrides,
  };

  testLogger.debug("Created mock import.meta.env", {
    nodeEnv: env.NODE_ENV,
    apiBaseUrl: env.VITE_API_BASE_URL,
    logLevel: env.VITE_LOG_LEVEL,
  });

  return env;
}

// Monitoring Service State Templates
export function createErrorMonitoringConfig() {
  return {
    enableConsoleTracking: true,
    enableUnhandledRejections: true,
    enableComponentErrors: true,
    enableUserFeedback: true,
    maxErrors: 100,
    reportToSentry: false,
  };
}

export function createPerformanceMonitoringConfig() {
  return {
    enableWebVitals: true,
    enableResourceTiming: true,
    enableNavigationTiming: true,
    enableUserTiming: true,
    sampleRate: 1.0,
    reportToAnalytics: false,
  };
}

// Feature Flag Update Templates
export function createFeatureFlagUpdates(
  overrides: Partial<FeatureFlags> = {},
): Partial<FeatureFlags> {
  const updates: Partial<FeatureFlags> = {
    enableAiReviews: true,
    enableSocialLogin: true,
    enableVirtualization: true,
    ...overrides,
  };

  testLogger.debug("Created feature flag updates", updates);
  return updates;
}

// ===========================
// Authentication Form Test Templates
// ===========================

// Login form data template
export interface LoginFormData {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export function createLoginFormData(
  overrides: Partial<LoginFormData> = {},
): LoginFormData {
  const formData: LoginFormData = {
    email: overrides.email ?? `user${randomString(4)}@example.com`,
    password: overrides.password ?? `Password${randomInt(100, 999)}!`,
    rememberMe: overrides.rememberMe ?? false,
    ...overrides,
  };
  testLogger.debug("Created login form data", {
    email: formData.email,
    hasPassword: !!formData.password,
    rememberMe: formData.rememberMe,
  });
  return formData;
}

// Register form data template
export interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export function createRegisterFormData(
  overrides: Partial<RegisterFormData> = {},
): RegisterFormData {
  const password = overrides.password ?? `Password${randomInt(100, 999)}!`;
  const formData: RegisterFormData = {
    name: overrides.name ?? `User ${randomString(4)}`,
    email: overrides.email ?? `user${randomString(6)}@example.com`,
    password,
    confirmPassword: overrides.confirmPassword ?? password,
    ...overrides,
  };
  testLogger.debug("Created register form data", {
    name: formData.name,
    email: formData.email,
    hasPassword: !!formData.password,
    passwordsMatch: formData.password === formData.confirmPassword,
  });
  return formData;
}

// Forgot password form data template
export interface ForgotPasswordFormData {
  email: string;
}

export function createForgotPasswordFormData(
  overrides: Partial<ForgotPasswordFormData> = {},
): ForgotPasswordFormData {
  const formData: ForgotPasswordFormData = {
    email: overrides.email ?? `user${randomString(6)}@example.com`,
    ...overrides,
  };
  testLogger.debug("Created forgot password form data", {
    email: formData.email,
  });
  return formData;
}

// Reset password form data template
export interface ResetPasswordFormData {
  token: string;
  password: string;
  confirmPassword: string;
}

export function createResetPasswordFormData(
  overrides: Partial<ResetPasswordFormData> = {},
): ResetPasswordFormData {
  const password = overrides.password ?? `NewPassword${randomInt(100, 999)}!`;
  const formData: ResetPasswordFormData = {
    token: overrides.token ?? `reset_${randomString(32)}`,
    password,
    confirmPassword: overrides.confirmPassword ?? password,
    ...overrides,
  };
  testLogger.debug("Created reset password form data", {
    hasToken: !!formData.token,
    hasPassword: !!formData.password,
    passwordsMatch: formData.password === formData.confirmPassword,
  });
  return formData;
}

// Invalid form data templates for testing validation
export function createInvalidLoginFormData(
  invalidField: "email" | "password" | "both" = "email",
): LoginFormData {
  const baseData = createLoginFormData();

  switch (invalidField) {
    case "email":
      return { ...baseData, email: "invalid-email" };
    case "password":
      return { ...baseData, password: "" };
    case "both":
      return { ...baseData, email: "invalid-email", password: "" };
    default:
      return baseData;
  }
}

export function createInvalidRegisterFormData(
  invalidField: "email" | "password" | "confirmPassword" | "name" = "email",
): RegisterFormData {
  const baseData = createRegisterFormData();

  switch (invalidField) {
    case "email":
      return { ...baseData, email: "invalid-email" };
    case "password":
      return { ...baseData, password: "123" }; // Too short
    case "confirmPassword":
      return { ...baseData, confirmPassword: "different-password" };
    case "name":
      return { ...baseData, name: "" };
    default:
      return baseData;
  }
}

// Form validation error templates
export interface FormValidationError {
  field: string;
  message: string;
}

export function createFormValidationError(
  field: string,
  message?: string,
): FormValidationError {
  const defaultMessages: Record<string, string> = {
    email: "Please enter a valid email address",
    password: "Password must be at least 8 characters long",
    confirmPassword: "Passwords do not match",
    name: "Name is required",
  };

  const error: FormValidationError = {
    field,
    message: message ?? defaultMessages[field] ?? `${field} is invalid`,
  };
  testLogger.debug("Created form validation error", error);
  return error;
}

// Enhanced upload templates for Phase 5.2 File Upload Interface

import type {
  AdvancedUploadOptions,
  FileMetadataExtract,
  FilePreviewInfo,
  FileValidationError,
  FileValidationResult,
  FileValidationWarning,
  UploadChunkInfo,
  UploadQueueItem,
} from "@/lib/api/types/upload";

/**
 * Create mock File object for testing
 */
export function createMockFile(
  overrides: Partial<{
    name: string;
    size: number;
    type: string;
    lastModified: number;
  }> = {},
): File {
  const fileName = overrides.name || `test-file-${randomString(6)}.pdf`;
  const size = overrides.size || randomInt(1024, 10 * 1024 * 1024); // 1KB to 10MB
  const type = overrides.type || "application/pdf";
  const lastModified = overrides.lastModified || Date.now();

  // Create a proper mock that matches the File interface
  const mockFile = Object.create(File.prototype);
  Object.defineProperties(mockFile, {
    name: { value: fileName, writable: false },
    size: { value: size, writable: false },
    type: { value: type, writable: false },
    lastModified: { value: lastModified, writable: false },
    slice: {
      value: vi.fn().mockReturnValue(new Blob()),
      writable: false,
    },
    stream: {
      value: vi.fn().mockReturnValue(new ReadableStream()),
      writable: false,
    },
    text: {
      value: vi.fn().mockResolvedValue("mock file content"),
      writable: false,
    },
    arrayBuffer: {
      value: vi.fn().mockResolvedValue(new ArrayBuffer(size)),
      writable: false,
    },
  });

  testLogger.debug("Created mock file", { name: fileName, size, type });
  return mockFile as File;
}

/**
 * Create upload queue item for testing
 */
export function createUploadQueueItem(
  overrides: Partial<UploadQueueItem> = {},
): UploadQueueItem {
  const id = overrides.id || `queue-item-${randomString(8)}`;
  const file = overrides.file || createMockFile();
  const statusOptions = [
    "pending",
    "uploading",
    "completed",
    "error",
    "cancelled",
    "paused",
  ] as const;
  const status = overrides.status || randomStatus(statusOptions);

  const queueItem: UploadQueueItem = {
    id,
    file,
    priority: overrides.priority ?? randomInt(1, 10),
    status,
    progress:
      overrides.progress ?? (status === "completed" ? 100 : randomInt(0, 99)),
    startTime:
      overrides.startTime ||
      (status !== "pending" ? Date.now() - randomInt(1000, 60000) : undefined),
    endTime:
      overrides.endTime || (status === "completed" ? Date.now() : undefined),
    speed:
      overrides.speed ??
      (status === "uploading" ? randomInt(100000, 5000000) : undefined),
    eta:
      overrides.eta ?? (status === "uploading" ? randomInt(5, 300) : undefined),
    error:
      overrides.error ||
      (status === "error"
        ? {
            message: `Upload failed: ${randomString(10)}`,
            code: "UPLOAD_ERROR",
            retryable: true,
            retryCount: randomInt(0, 3),
          }
        : undefined),
    result:
      overrides.result ||
      (status === "completed"
        ? {
            filename: file.name,
            url: `https://example.com/files/${file.name}`,
          }
        : undefined),
    chunks: overrides.chunks,
    ...overrides,
  };

  testLogger.debug("Created upload queue item", {
    id,
    status,
    progress: queueItem.progress,
  });
  return queueItem;
}

/**
 * Create upload chunk info for testing
 */
export function createUploadChunkInfo(
  overrides: Partial<UploadChunkInfo> = {},
): UploadChunkInfo {
  const index = overrides.index ?? randomInt(0, 10);
  const chunkSize = 1024 * 1024; // 1MB chunks
  const start = overrides.start ?? index * chunkSize;
  const end = overrides.end ?? start + chunkSize - 1;
  const statusOptions = ["pending", "uploading", "completed", "error"] as const;
  const status = overrides.status || randomStatus(statusOptions);

  const chunkInfo: UploadChunkInfo = {
    index,
    start,
    end,
    size: end - start + 1,
    status,
    progress:
      overrides.progress ?? (status === "completed" ? 100 : randomInt(0, 99)),
    error:
      overrides.error ||
      (status === "error" ? `Chunk ${index} failed` : undefined),
    retryCount:
      overrides.retryCount ?? (status === "error" ? randomInt(1, 3) : 0),
    etag:
      overrides.etag ||
      (status === "completed" ? `"${randomString(32)}"` : undefined),
    ...overrides,
  };

  testLogger.debug("Created upload chunk info", {
    index,
    status,
    progress: chunkInfo.progress,
  });
  return chunkInfo;
}

/**
 * Create file validation result for testing
 */
export function createFileValidationResult(
  overrides: Partial<FileValidationResult> = {},
): FileValidationResult {
  const isValid = overrides.isValid ?? Math.random() > 0.2; // 80% valid by default
  const errors =
    overrides.errors || (isValid ? [] : [createFileValidationError()]);
  const warnings =
    overrides.warnings ||
    (Math.random() > 0.7 ? [createFileValidationWarning()] : []);

  const result: FileValidationResult = {
    isValid,
    errors,
    warnings,
    metadata: overrides.metadata || createFileMetadataExtract(),
    ...overrides,
  };

  testLogger.debug("Created file validation result", {
    isValid,
    errorCount: errors.length,
    warningCount: warnings.length,
  });
  return result;
}

/**
 * Create file validation error for testing
 */
export function createFileValidationError(
  overrides: Partial<FileValidationError> = {},
): FileValidationError {
  const codes = [
    "FILE_TOO_LARGE",
    "INVALID_TYPE",
    "CORRUPTED_FILE",
    "VIRUS_DETECTED",
    "ENCRYPTED_FILE",
  ];
  const code = overrides.code || codes[randomInt(0, codes.length - 1)];

  const error: FileValidationError = {
    code,
    message:
      overrides.message ||
      `Validation error: ${code.toLowerCase().replace(/_/g, " ")}`,
    field: overrides.field || "file",
    severity: overrides.severity || "error",
    ...overrides,
  };

  testLogger.warn("Created file validation error", error);
  return error;
}

/**
 * Create file validation warning for testing
 */
export function createFileValidationWarning(
  overrides: Partial<FileValidationWarning> = {},
): FileValidationWarning {
  const codes = [
    "LARGE_FILE_SIZE",
    "UNUSUAL_FORMAT",
    "OLD_FORMAT",
    "NO_METADATA",
    "POTENTIAL_SECURITY_RISK",
  ];
  const code = overrides.code || codes[randomInt(0, codes.length - 1)];

  const warning: FileValidationWarning = {
    code,
    message:
      overrides.message || `Warning: ${code.toLowerCase().replace(/_/g, " ")}`,
    field: overrides.field || "file",
    suggestion:
      overrides.suggestion || "Consider reviewing this file before proceeding",
    ...overrides,
  };

  testLogger.debug("Created file validation warning", warning);
  return warning;
}

/**
 * Create file metadata extract for testing
 */
export function createFileMetadataExtract(
  overrides: Partial<FileMetadataExtract> = {},
): FileMetadataExtract {
  const categories = [
    "document",
    "image",
    "video",
    "audio",
    "pdf",
    "text",
  ] as const;
  const category =
    overrides.category || categories[randomInt(0, categories.length - 1)];

  const metadata: FileMetadataExtract = {
    size: overrides.size ?? randomInt(1024, 50 * 1024 * 1024),
    mimeType: overrides.mimeType || "application/pdf",
    extension: overrides.extension || ".pdf",
    category,
    dimensions:
      overrides.dimensions ||
      (category === "image" || category === "video"
        ? {
            width: randomInt(640, 1920),
            height: randomInt(480, 1080),
          }
        : undefined),
    duration:
      overrides.duration ||
      (category === "audio" || category === "video"
        ? randomInt(30, 3600)
        : undefined),
    pageCount:
      overrides.pageCount ||
      (category === "document" || category === "pdf"
        ? randomInt(1, 50)
        : undefined),
    isEncrypted: overrides.isEncrypted ?? Math.random() > 0.9, // 10% encrypted
    createdDate: overrides.createdDate || randomDate(),
    modifiedDate: overrides.modifiedDate || randomDate(),
    ...overrides,
  };

  testLogger.debug("Created file metadata extract", {
    category,
    size: metadata.size,
    mimeType: metadata.mimeType,
  });
  return metadata;
}

/**
 * Create advanced upload options for testing
 */
export function createAdvancedUploadOptions(
  overrides: Partial<AdvancedUploadOptions> = {},
): AdvancedUploadOptions {
  const options: AdvancedUploadOptions = {
    enableChunked: overrides.enableChunked ?? true,
    chunkSize: overrides.chunkSize ?? 1024 * 1024, // 1MB
    maxConcurrentChunks: overrides.maxConcurrentChunks ?? 3,
    enableBackground: overrides.enableBackground ?? false,
    priority: overrides.priority ?? randomInt(1, 10),
    metadata: overrides.metadata || { source: "test", timestamp: Date.now() },
    onProgress: overrides.onProgress || vi.fn(),
    onChunkComplete: overrides.onChunkComplete || vi.fn(),
    ...overrides,
  };

  testLogger.debug("Created advanced upload options", {
    enableChunked: options.enableChunked,
    chunkSize: options.chunkSize,
    priority: options.priority,
  });
  return options;
}

/**
 * Create file preview info for testing
 */
export function createFilePreviewInfo(
  overrides: Partial<FilePreviewInfo> = {},
): FilePreviewInfo {
  const types = ["image", "pdf", "text", "video", "audio", "none"] as const;
  const type = overrides.type || types[randomInt(0, types.length - 1)];
  const available = overrides.available ?? type !== "none";

  const preview: FilePreviewInfo = {
    available,
    type,
    url:
      overrides.url ||
      (available
        ? `https://example.com/preview/${randomString(8)}`
        : undefined),
    thumbnailUrl:
      overrides.thumbnailUrl ||
      (available ? `https://example.com/thumb/${randomString(8)}` : undefined),
    dimensions:
      overrides.dimensions ||
      (type === "image" || type === "video"
        ? {
            width: randomInt(200, 800),
            height: randomInt(150, 600),
          }
        : undefined),
    ...overrides,
  };

  testLogger.debug("Created file preview info", { available, type });
  return preview;
}

/**
 * Create multiple upload queue items for testing
 */
export function createUploadQueueItemList(
  count = 3,
  overrides: Partial<UploadQueueItem> = {},
): UploadQueueItem[] {
  const items = Array.from({ length: count }, (_, index) =>
    createUploadQueueItem({
      ...overrides,
      priority: overrides.priority ?? count - index,
    }),
  );

  testLogger.info(`Created upload queue item list of ${count} items`);
  return items;
}

/**
 * Create multiple upload chunks for testing
 */
export function createUploadChunkList(
  totalChunks = 5,
  overrides: Partial<UploadChunkInfo> = {},
): UploadChunkInfo[] {
  const chunkSize = 1024 * 1024; // 1MB
  const chunks = Array.from({ length: totalChunks }, (_, index) =>
    createUploadChunkInfo({
      ...overrides,
      index,
      start: index * chunkSize,
      end: (index + 1) * chunkSize - 1,
    }),
  );

  testLogger.info(`Created upload chunk list of ${totalChunks} chunks`);
  return chunks;
}

// File Management Templates

/**
 * File item template for file management tests
 */
export type TestFileItem = {
  filename: string;
  url: string;
  status?: string;
  progress?: number;
  createdAt?: string;
  size?: number;
  contentType?: string;
};

export function createTestFileItem(
  overrides: Partial<TestFileItem> = {},
): TestFileItem {
  const extensions = [".pdf", ".jpg", ".png", ".docx", ".txt"];
  const statuses = ["pending", "uploading", "completed", "error"];
  const contentTypes = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
  ];

  const extIndex = randomInt(0, extensions.length - 1);
  const extension = extensions[extIndex];
  const contentType = contentTypes[extIndex];

  const file: TestFileItem = {
    filename: overrides.filename || `test-file-${randomString(6)}${extension}`,
    url: overrides.url || `/uploads/${randomString(10)}${extension}`,
    status: overrides.status || statuses[randomInt(0, statuses.length - 1)],
    progress:
      overrides.progress ??
      (overrides.status === "completed" ? 100 : randomInt(0, 99)),
    createdAt: overrides.createdAt || randomDate(),
    size: overrides.size || randomInt(1024, 10 * 1024 * 1024), // 1KB to 10MB
    contentType: overrides.contentType || contentType,
    ...overrides,
  };

  if (file.status === "error") {
    testLogger.error("Created file item with error status", file);
  } else if (file.progress === 100) {
    testLogger.info("Created completed file item", file);
  } else {
    testLogger.debug("Created file item", file);
  }

  return file;
}

/**
 * File list response template
 */
export type TestFileListResponse = {
  files: TestFileItem[];
  total: number;
};

export function createTestFileListResponse(
  overrides: Partial<TestFileListResponse> = {},
): TestFileListResponse {
  const count = overrides.files?.length || randomInt(3, 15);
  const files =
    overrides.files ||
    Array.from({ length: count }, () => createTestFileItem());

  const response: TestFileListResponse = {
    files,
    total: overrides.total || files.length,
    ...overrides,
  };

  testLogger.info(
    `Created file list response with ${response.files.length} files (total: ${response.total})`,
  );
  return response;
}

/**
 * File management state template
 */
export type TestFileManagementState = {
  selectedFiles: string[];
  viewMode: "list" | "grid" | "table";
  filters: Record<string, any>;
  sort: {
    field?: string;
    order?: "asc" | "desc";
  };
  bulkOperation: {
    type: string | null;
    inProgress: boolean;
    error: string | null;
  };
};

export function createTestFileManagementState(
  overrides: Partial<TestFileManagementState> = {},
): TestFileManagementState {
  const viewModes = ["list", "grid", "table"] as const;
  const sortFields = ["filename", "created_at", "size", "content_type"];
  const sortOrders = ["asc", "desc"] as const;
  const bulkOperations = ["delete", "archive", "restore"];

  const state: TestFileManagementState = {
    selectedFiles: overrides.selectedFiles || [],
    viewMode:
      overrides.viewMode || viewModes[randomInt(0, viewModes.length - 1)],
    filters: overrides.filters || {},
    sort: {
      field:
        overrides.sort?.field ||
        sortFields[randomInt(0, sortFields.length - 1)],
      order:
        overrides.sort?.order ||
        sortOrders[randomInt(0, sortOrders.length - 1)],
    },
    bulkOperation: {
      type:
        overrides.bulkOperation?.type ??
        (randomInt(0, 1)
          ? bulkOperations[randomInt(0, bulkOperations.length - 1)]
          : null),
      inProgress: overrides.bulkOperation?.inProgress ?? false,
      error: overrides.bulkOperation?.error ?? null,
    },
    ...overrides,
  };

  if (state.selectedFiles.length > 0) {
    testLogger.info(
      `Created file management state with ${state.selectedFiles.length} selected files`,
    );
  } else {
    testLogger.debug("Created file management state with no selection");
  }

  return state;
}

/**
 * File action result template
 */
export type TestFileActionResult = {
  success: boolean;
  message: string;
  count?: number;
  processedIds?: string[];
  failedIds?: string[];
};

export function createTestFileActionResult(
  overrides: Partial<TestFileActionResult> = {},
): TestFileActionResult {
  const success = overrides.success ?? randomInt(0, 1) === 1;
  const count = overrides.count || randomInt(1, 10);

  const result: TestFileActionResult = {
    success,
    message:
      overrides.message ||
      (success ? "Operation completed successfully" : "Operation failed"),
    count: overrides.count || count,
    processedIds:
      overrides.processedIds ||
      (success
        ? Array.from({ length: count }, () => `file-${randomString(8)}`)
        : []),
    failedIds:
      overrides.failedIds ||
      (!success
        ? Array.from({ length: count }, () => `file-${randomString(8)}`)
        : []),
    ...overrides,
  };

  if (result.success) {
    testLogger.info("Created successful file action result", result);
  } else {
    testLogger.error("Created failed file action result", result);
  }

  return result;
}

/**
 * File management config template
 */
export type TestFileManagementConfig = {
  pageSize: number;
  realTimeUpdates: boolean;
  bulkOperations: boolean;
  previews: boolean;
  maxBulkSelection: number;
  refreshInterval?: number;
};

export function createTestFileManagementConfig(
  overrides: Partial<TestFileManagementConfig> = {},
): TestFileManagementConfig {
  const config: TestFileManagementConfig = {
    pageSize: overrides.pageSize || randomInt(10, 50),
    realTimeUpdates: overrides.realTimeUpdates ?? true,
    bulkOperations: overrides.bulkOperations ?? true,
    previews: overrides.previews ?? true,
    maxBulkSelection: overrides.maxBulkSelection || randomInt(10, 100),
    refreshInterval: overrides.refreshInterval || randomInt(10000, 60000),
    ...overrides,
  };

  testLogger.debug("Created file management config", config);
  return config;
}

/**
 * File selection helper template
 */
export function createTestFileSelection(
  files: TestFileItem[],
  selectCount = 0,
): string[] {
  if (selectCount === 0) {
    return [];
  }

  const actualCount = Math.min(selectCount, files.length);
  const selectedFilenames = files.slice(0, actualCount).map((f) => f.filename);

  testLogger.debug(
    `Created file selection with ${selectedFilenames.length} files`,
  );
  return selectedFilenames;
}

/**
 * File search/filter params template
 */
export type TestFileSearchParams = {
  query?: string;
  content_type?: string;
  extension?: string;
  created_after?: string;
  created_before?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
};

export function createTestFileSearchParams(
  overrides: Partial<TestFileSearchParams> = {},
): TestFileSearchParams {
  const contentTypes = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
  ];
  const extensions = [".pdf", ".jpg", ".png", ".txt"];
  const sortFields = ["filename", "created_at", "size", "content_type"];
  const sortOrders = ["asc", "desc"] as const;

  const params: TestFileSearchParams = {
    query:
      overrides.query ||
      (randomInt(0, 1) ? `search-${randomString(5)}` : undefined),
    content_type:
      overrides.content_type ||
      (randomInt(0, 1)
        ? contentTypes[randomInt(0, contentTypes.length - 1)]
        : undefined),
    extension:
      overrides.extension ||
      (randomInt(0, 1)
        ? extensions[randomInt(0, extensions.length - 1)]
        : undefined),
    created_after:
      overrides.created_after ||
      (randomInt(0, 1) ? randomDateWithOffset(-30) : undefined),
    created_before:
      overrides.created_before ||
      (randomInt(0, 1) ? randomDateWithOffset(0) : undefined),
    sort_by:
      overrides.sort_by || sortFields[randomInt(0, sortFields.length - 1)],
    sort_order:
      overrides.sort_order || sortOrders[randomInt(0, sortOrders.length - 1)],
    ...overrides,
  };

  const activeFilters = Object.values(params).filter(
    (v) => v !== undefined,
  ).length;
  testLogger.debug(
    `Created file search params with ${activeFilters} active filters`,
  );

  return params;
}
