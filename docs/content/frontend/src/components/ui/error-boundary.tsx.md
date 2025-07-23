# error-boundary.tsx - React Error Boundary Component

## Purpose

The `ErrorBoundary` component provides comprehensive error handling for React applications, catching JavaScript errors in component trees and displaying fallback UIs. This component implements React's error boundary pattern with enhanced features including error logging, retry mechanisms, and customizable fallback rendering.

## Key Components

### Main Component

- **ErrorBoundary**: Class component implementing React error boundary lifecycle methods
- **Error State Management**: Tracks error state, error details, and component stack information
- **Recovery Mechanisms**: Provides retry and page reload options for error recovery

### Core Features

- **Error Catching**: Implements `componentDidCatch` and `getDerivedStateFromError` lifecycle methods
- **Logging Integration**: Uses centralized logger for error tracking and debugging
- **Fallback UI**: Renders user-friendly error messages with recovery options
- **Developer Tools**: Optional detailed error information display for development

## Component Architecture

```tsx
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: React.ErrorInfo, retry: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  testId?: string;
  retryText?: string;
  showDetails?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}
```

### Error Boundary Lifecycle

1. **Normal Operation**: Renders children components normally
2. **Error Detection**: `getDerivedStateFromError` catches errors and updates state
3. **Error Handling**: `componentDidCatch` logs errors and triggers callbacks
4. **Fallback Rendering**: Displays fallback UI with recovery options
5. **Recovery**: Provides retry mechanism to reset error state

## Error Handling Strategy

### Logging Integration

```tsx
componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
  logger.error("Error boundary caught an error", {
    error: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
  });
}
```

### Fallback UI Features

- **User-Friendly Messages**: Clear error descriptions without technical jargon
- **Recovery Actions**: "Try Again" and "Reload Page" buttons
- **Developer Information**: Optional detailed error stack traces
- **Accessibility**: ARIA labels and semantic HTML structure

### Error Recovery

```tsx
handleRetry = () => {
  logger.info("Error boundary retry attempted");
  this.setState({
    hasError: false,
    error: undefined,
    errorInfo: undefined,
  });
};
```

## Usage Examples

### Basic Error Boundary

```tsx
import { ErrorBoundary } from '@/components/ui/error-boundary';

function App() {
  return (
    <ErrorBoundary>
      <ComponentThatMightFail />
    </ErrorBoundary>
  );
}
```

### Custom Fallback Component

```tsx
<ErrorBoundary
  fallback={(error, errorInfo, retry) => (
    <CustomErrorDisplay error={error} onRetry={retry} />
  )}
  onError={(error, errorInfo) => {
    // Custom error handling
    analytics.track('error_boundary_triggered', { error: error.message });
  }}
>
  <App />
</ErrorBoundary>
```

### Development Mode with Details

```tsx
<ErrorBoundary
  showDetails={process.env.NODE_ENV === 'development'}
  retryText="Try Again"
  testId="app-error-boundary"
>
  <Router />
</ErrorBoundary>
```

## Accessibility Features

### ARIA Support

- **Error Icons**: Semantic SVG icons with proper ARIA labels
- **Screen Reader Support**: Accessible error messages and action buttons
- **Focus Management**: Proper focus handling for error state

### Testing Support

- **Test IDs**: Comprehensive data-testid attributes for component testing
- **Predictable Behavior**: Consistent error handling for automated testing

## Dependencies

### React Dependencies

- **React**: Component, ReactNode types for React component architecture
- **React Error Info**: React.ErrorInfo for detailed error information

### UI Components

- **Alert System**: Alert, AlertDescription, AlertTitle for error display
- **Button Component**: Button for retry and reload actions
- **Card Component**: Card for error container styling

### Utilities

- **Logger**: Centralized logging service for error tracking
- **Theme Integration**: Uses semantic CSS variables for theming

## Integration Points

### Error Monitoring

- **Logger Integration**: Automatically logs all caught errors with context
- **Error Callbacks**: Supports custom error handling through onError prop
- **Development Tools**: Detailed error information for debugging

### UI Framework

- **Theme Compatibility**: Uses semantic color variables for consistent theming
- **Component Library**: Integrates with UI component system
- **Accessibility**: Follows WCAG guidelines for error handling

## Best Practices

### Error Boundary Placement

```tsx
// Wrap major application sections
<ErrorBoundary testId="main-app">
  <Router />
</ErrorBoundary>

// Wrap critical components
<ErrorBoundary testId="data-table" onError={handleTableError}>
  <DataTable />
</ErrorBoundary>
```

### Implementation Strategy

- **Graceful Degradation**: Provides meaningful fallbacks without breaking user flow
- **Error Context**: Captures component stack for debugging
- **Recovery Options**: Multiple recovery mechanisms for different scenarios
- **User Experience**: Clear, non-technical error messages for end users

## Related Files

- **[logger.ts](../../lib/logger.ts.md)**: Centralized logging service used for error tracking
- **[alert.tsx](alert.tsx.md)**: Alert components used in fallback UI
- **[button.tsx](button.tsx.md)**: Button components for error recovery actions
- **[card.tsx](card.tsx.md)**: Card component for error container styling

## Error Types Handled

### JavaScript Errors

- **Runtime Errors**: Undefined variables, null reference errors
- **Component Errors**: React component lifecycle errors
- **Async Errors**: Promise rejections in component context (when caught by React)

### Error Information Captured

- **Error Message**: Human-readable error description
- **Stack Trace**: Complete JavaScript error stack
- **Component Stack**: React component hierarchy where error occurred
- **Error Context**: Additional context for debugging

## Performance Considerations

### Error Boundary Overhead

- **Minimal Impact**: Error boundaries only affect performance when errors occur
- **Logging Efficiency**: Structured logging with appropriate log levels
- **Recovery Speed**: Fast state reset for error recovery

### Memory Management

- **Error State Cleanup**: Proper cleanup of error state on recovery
- **Component Unmounting**: Handles cleanup on component unmount
- **Timeout Management**: Proper timeout cleanup to prevent memory leaks
