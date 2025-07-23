# aria-live-region.tsx - Accessibility Live Region Components

## Purpose

The `AriaLiveRegion` component and related utilities provide comprehensive accessibility support for dynamic content announcements to screen readers. This component system implements ARIA live regions with specialized components for different use cases including status updates, form validation, and global announcements.

## Key Components

### Core Components

- **AriaLiveRegion**: Main live region component for accessibility announcements
- **StatusAnnouncer**: Specialized component for status updates (loading, success, error, info)
- **FormValidationAnnouncer**: Dedicated component for form validation messages
- **LiveRegionProvider**: Context provider for global announcement management

### Hooks and Utilities

- **useAriaLive**: Hook for managing live region announcements programmatically
- **useLiveRegion**: Hook for accessing global live region context
- **Multiple Politeness Levels**: Support for "polite", "assertive", and "off" announcement modes

## Component Architecture

```tsx
interface AriaLiveRegionProps {
  message?: string;
  politeness?: "polite" | "assertive" | "off";
  clearDelay?: number;
  className?: string;
  id?: string;
}

// Main component
export function AriaLiveRegion({ ... }: AriaLiveRegionProps)

// Status announcer with predefined configurations
export function StatusAnnouncer({ ... }: StatusAnnouncerProps)

// Form validation with error handling
export function FormValidationAnnouncer({ ... }: FormValidationAnnouncerProps)
```

### Design Philosophy

- **Screen Reader First**: Designed primarily for screen reader accessibility
- **Non-Visual**: Uses `sr-only` class to hide from visual users
- **Semantic Styling**: Uses semantic color variables for consistent theming
- **Flexible Configuration**: Supports various announcement patterns and timings

## Core Features

### ARIA Live Region Implementation

```tsx
<div
  id={id}
  aria-live={politeness}
  aria-atomic="true"
  className="sr-only text-[color:var(--foreground-muted,inherit)]"
>
  {currentMessage}
</div>
```

- **ARIA Live**: Proper `aria-live` attribute for screen reader announcements
- **Atomic Updates**: `aria-atomic="true"` ensures entire message is read
- **Screen Reader Only**: Visually hidden but accessible to assistive technology
- **Semantic Colors**: Uses CSS custom properties for theme consistency

### Announcement Management

- **Auto-Clear**: Configurable delay for automatic message clearing
- **Timeout Handling**: Proper cleanup of timeouts to prevent memory leaks
- **Message Queuing**: Handles rapid message updates gracefully
- **Logging Integration**: Debug logging for announcement tracking

## Usage Examples

### Basic Live Region

```tsx
import { AriaLiveRegion } from "@/components/ui/aria-live-region";

function MyComponent() {
  const [message, setMessage] = useState("");

  const handleSave = () => {
    setMessage("Changes saved successfully");
  };

  return (
    <>
      <button onClick={handleSave}>Save</button>
      <AriaLiveRegion message={message} />
    </>
  );
}
```

### Status Announcements

```tsx
import { StatusAnnouncer } from "@/components/ui/aria-live-region";

function DataLoader() {
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading",
  );

  return (
    <>
      <div>Loading data...</div>
      <StatusAnnouncer
        status={status}
        message="User data loaded successfully"
      />
    </>
  );
}
```

### Form Validation

```tsx
import { FormValidationAnnouncer } from "@/components/ui/aria-live-region";

function LoginForm() {
  const [errors, setErrors] = useState<string[]>([]);

  return (
    <form>
      <input name="email" />
      <FormValidationAnnouncer errors={errors} fieldName="email" />
    </form>
  );
}
```

### Global Live Region with Context

```tsx
import {
  LiveRegionProvider,
  useLiveRegion,
} from "@/components/ui/aria-live-region";

function App() {
  return (
    <LiveRegionProvider>
      <YourAppContent />
    </LiveRegionProvider>
  );
}

function SomeComponent() {
  const { announceSuccess, announceError } = useLiveRegion();

  const handleAction = async () => {
    try {
      await performAction();
      announceSuccess("Action completed successfully");
    } catch (error) {
      announceError("Action failed. Please try again.");
    }
  };

  return <button onClick={handleAction}>Perform Action</button>;
}
```

## Live Region Hook

### useAriaLive Hook

```tsx
export function useAriaLive(
  defaultPoliteness: LiveRegionPoliteness = "polite",
) {
  const { announce, announcePolite, announceAssertive, clear } = useAriaLive();

  // Usage examples
  announce("Custom message", "assertive");
  announcePolite("Polite announcement");
  announceAssertive("Urgent announcement");
  clear(); // Clear current message
}
```

### Hook Features

- **Flexible Announcements**: Support for different politeness levels
- **Convenience Methods**: Pre-configured methods for common use cases
- **Message Management**: Clear function for removing announcements
- **Debug Logging**: Automatic logging of all announcements

## Specialized Components

### StatusAnnouncer Configuration

```tsx
const STATUS_CONFIG = {
  loading: { politeness: "polite", prefix: "Loading:" },
  success: { politeness: "polite", prefix: "Success:" },
  error: { politeness: "assertive", prefix: "Error:" },
  info: { politeness: "polite", prefix: "Info:" },
};
```

- **Status-Specific Behavior**: Different politeness levels for different status types
- **Consistent Prefixes**: Standardized message prefixes for clarity
- **Semantic Styling**: Status-appropriate color classes using semantic variables

### Form Validation Features

```tsx
export function FormValidationAnnouncer({
  errors = [],
  fieldName,
  className,
}: FormValidationAnnouncerProps) {
  const message = React.useMemo(() => {
    if (errors.length === 0) return "";

    const prefix = fieldName ? `${fieldName} field:` : "Validation error:";
    const errorText =
      errors.length === 1
        ? errors[0]
        : `${errors.length} errors: ${errors.join(", ")}`;

    return `${prefix} ${errorText}`;
  }, [errors, fieldName]);
}
```

- **Multiple Error Support**: Handles single and multiple validation errors
- **Field Context**: Includes field name for context when provided
- **Error Aggregation**: Summarizes multiple errors appropriately
- **Assertive Announcements**: Uses assertive politeness for immediate attention

## Accessibility Best Practices

### ARIA Live Region Guidelines

- **Politeness Levels**: "polite" for general updates, "assertive" for errors/urgent info
- **Message Timing**: Appropriate delays for auto-clearing messages
- **Non-Interrupting**: Polite announcements don't interrupt screen reader flow
- **Clear Content**: Concise, descriptive messages for screen reader users

### Screen Reader Optimization

```tsx
// Visually hidden but accessible
className="sr-only text-muted-foreground"

// Atomic announcements
aria-atomic="true"

// Proper live region setup
aria-live={politeness}
```

### User Experience

- **Non-Visual Feedback**: Provides feedback without visual distraction
- **Consistent Messaging**: Standardized announcement patterns
- **Context Preservation**: Maintains user's place in content flow
- **Flexible Timing**: Configurable announcement duration

## Integration Points

### Theme System

- **Semantic Colors**: Uses CSS custom properties for theme consistency
- **Screen Reader Only**: Styling focuses on accessibility, not visual appearance
- **Color Semantics**: Status-appropriate colors for different announcement types

### Logging Integration

```tsx
logger.debug("AriaLiveRegion: Announcing message", {
  message,
  politeness,
  clearDelay,
});
```

- **Debug Information**: Logs all announcements for development debugging
- **Structured Logging**: Consistent log format with context information
- **Development Tools**: Helps track announcement behavior during development

### Form Integration

- **Validation Workflow**: Seamless integration with form validation libraries
- **Error Handling**: Specialized components for form error announcements
- **Field Context**: Proper association with form fields and labels

## Performance Considerations

### Memory Management

```tsx
useEffect(() => {
  // Cleanup timeouts on unmount
  return () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };
}, []);
```

- **Timeout Cleanup**: Proper cleanup prevents memory leaks
- **Effect Management**: Efficient useEffect patterns for message handling
- **Component Lifecycle**: Handles mounting/unmounting gracefully

### Rendering Optimization

- **Memoized Messages**: Uses useMemo for expensive message formatting
- **Conditional Rendering**: Only renders content when messages exist
- **Minimal DOM Impact**: Lightweight DOM footprint for accessibility

## Dependencies

### React Dependencies

- **React Hooks**: useState, useEffect, useRef, useMemo for state management
- **React Context**: Context API for global live region management
- **Component Lifecycle**: Proper handling of component mounting/unmounting

### Accessibility Libraries

- **ARIA Standards**: Follows WAI-ARIA specifications for live regions
- **Screen Reader Testing**: Tested with common screen reader software
- **Accessibility Guidelines**: Implements WCAG 2.1 accessibility standards

### Utilities

- **Logger**: Centralized logging for debugging and monitoring
- **Semantic Styling**: CSS custom properties for consistent theming

## Related Files

- **[logger.ts](../../lib/logger.ts.md)**: Centralized logging service for announcement tracking
- **[theme-provider.tsx](../../lib/theme/theme-provider.tsx.md)**: Theme system for semantic color support
- **[form-validation.ts](../../lib/validation/form-validation.ts.md)**: Form validation utilities

## Error Handling

### Graceful Degradation

- **Fallback Behavior**: Works without JavaScript for basic accessibility
- **Error Recovery**: Handles component errors without breaking announcement system
- **Safe Defaults**: Sensible default values for all configuration options

### Development Experience

- **TypeScript Support**: Full type safety for all component props and hooks
- **Debug Logging**: Comprehensive logging for development troubleshooting
- **Hot Reload**: Maintains state during development hot reloads

## Live Region Context

### Global Provider Implementation

```tsx
export function LiveRegionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { announce, announcePolite, announceAssertive } = useAriaLive();

  const contextValue = React.useMemo(
    () => ({
      announce,
      announceSuccess: announcePolite,
      announceError: announceAssertive,
    }),
    [announce, announcePolite, announceAssertive],
  );

  return (
    <LiveRegionContext.Provider value={contextValue}>
      {children}
      <AriaLiveRegion id="global-live-region" className="sr-only" />
    </LiveRegionContext.Provider>
  );
}
```

- **Context Management**: Provides app-wide announcement capabilities
- **Memoized Context**: Optimized context value for performance
- **Global Live Region**: Single live region for application-wide announcements
- **Error Boundaries**: Proper error handling for context usage
