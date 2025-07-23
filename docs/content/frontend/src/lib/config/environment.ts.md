# environment.ts - Environment Configuration Management

## Purpose

Centralized environment configuration with type safety and validation using Zod schemas. Manages all environment variables for the frontend application with comprehensive validation and test-specific overrides.

## Key Components

### Environment Configuration Schema

- **Type-Safe Environment Variables**: Zod schema validation for all config values
- **Environment Types**: Support for development, staging, production, and test environments
- **Default Values**: Sensible defaults for all configuration options
- **URL Validation**: Built-in validation for API endpoints and WebSocket URLs

### Configuration Categories

#### API Configuration

- **API_BASE_URL**: Backend API endpoint (default: <http://localhost:8000>)
- **API_TIMEOUT**: Request timeout in milliseconds (default: 5000ms)
- **WS_URL**: WebSocket endpoint (default: ws://localhost:8000/api/v1)

#### Monitoring & Analytics

- **SENTRY_DSN**: Error reporting service configuration
- **ENABLE_ANALYTICS**: Privacy-focused analytics toggle (default: true)
- **ENABLE_ERROR_REPORTING**: Global error reporting control (default: true)
- **ENABLE_PERFORMANCE_MONITORING**: Performance tracking toggle (default: true)

#### Application Metadata

- **APP_VERSION**: Application version string (default: 0.1.0)
- **APP_NAME**: Application display name (default: ReViewPoint)
- **LOG_LEVEL**: Logging verbosity control (default: error)

## Environment-Specific Overrides

### Test Environment Handling

```typescript
const isTestEnvironment = rawConfig.NODE_ENV === "test";
if (isTestEnvironment) {
  const testDefaults = {
    APP_VERSION: rawConfig.APP_VERSION || "0.1.0-test",
    APP_NAME: rawConfig.APP_NAME || "ReViewPoint (Test)",
    LOG_LEVEL: rawConfig.LOG_LEVEL || "error",
    API_TIMEOUT: rawConfig.API_TIMEOUT || "5000",
    WS_URL: rawConfig.WS_URL || "ws://localhost:8000/api/v1",
    ENABLE_ANALYTICS: rawConfig.ENABLE_ANALYTICS || "true",
  };
}
```

## Validation & Error Handling

- **Zod Schema Validation**: Comprehensive type checking and validation
- **URL Format Validation**: Ensures API endpoints are valid URLs
- **Numeric Range Validation**: API timeout constraints (1-30 seconds)
- **Enum Validation**: Environment and log level restrictions
- **Debug Logging**: Configuration loading and validation logging

## Usage Patterns

### Environment Variable Loading

- **Vite Integration**: Uses `import.meta.env` for Vite environment variables
- **VITE\_ Prefix**: All custom environment variables use VITE\_ prefix
- **Fallback Strategy**: Graceful degradation with sensible defaults

### Configuration Access

- Exported as validated `EnvironmentConfig` type
- Used throughout application for consistent configuration access
- Centralized configuration prevents scattered hardcoded values

## Security Considerations

- **Sensitive Data**: Only client-safe environment variables exposed
- **Production Hardening**: Different defaults for production environments
- **Validation**: Schema validation prevents configuration injection attacks

## Integration Points

- **API Clients**: Provides base URLs and timeout configurations
- **Monitoring**: Controls analytics and error reporting behavior
- **WebSocket**: Configures real-time communication endpoints
- **Feature Flags**: Works with feature flag system for environment-specific features

## Performance Optimizations

- **One-Time Parsing**: Configuration parsed once at application startup
- **Type Safety**: Compile-time type checking prevents runtime errors
- **Default Values**: Reduces conditional logic throughout application

## Related Files

- [`featureFlags.ts`](featureFlags.ts.md) - Feature-specific configuration
- [`lib/api/base.ts`](../api/base.ts.md) - API client configuration
- [`main.tsx`](../../main.tsx.md) - Environment initialization
- [`monitoring/`](../monitoring/) - Monitoring service configuration
