# sonner.tsx - Toast Notification Component

## Purpose

The `Toaster` component provides toast notifications using the Sonner library, offering a themed and accessible notification system for user feedback. This component integrates with the application's theme system to provide consistent toast styling across light and dark modes.

## Key Components

### Main Component

- **Toaster**: Themed wrapper around Sonner's toast component
- **Theme Integration**: Automatic theme detection and application
- **Customizable Props**: Extends Sonner's ToasterProps for configuration

### Core Features

- **Theme Awareness**: Automatically adapts to light/dark theme changes
- **Semantic Styling**: Uses Tailwind semantic color classes for consistency
- **Accessibility**: Built-in ARIA support through Sonner library
- **Customizable Configuration**: Supports all Sonner configuration options

## Component Architecture

```tsx
import { useTheme } from "next-themes";
import { Toaster as Sonner, type ToasterProps } from "sonner";

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme();
  
  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group bg-popover text-popover-foreground border border-border"
      {...props}
    />
  );
};
```

### Design Philosophy

- **Theme Consistency**: Respects application theme settings automatically
- **Semantic Colors**: Uses CSS custom properties for theme-aware styling
- **Minimal Configuration**: Sensible defaults with customization options
- **Accessibility First**: Leverages Sonner's built-in accessibility features

## Usage Examples

### Basic Toast Setup

```tsx
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <>
      <YourAppContent />
      <Toaster />
    </>
  );
}
```

### Custom Configuration

```tsx
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <>
      <YourAppContent />
      <Toaster
        position="top-right"
        duration={4000}
        closeButton
        richColors
      />
    </>
  );
}
```

### Using Toast Notifications

```tsx
import { toast } from 'sonner';

// Success toast
toast.success('Operation completed successfully!');

// Error toast
toast.error('Something went wrong');

// Info toast
toast.info('Information message');

// Loading toast
const loadingToast = toast.loading('Processing...');
toast.success('Done!', { id: loadingToast });
```

## Theme Integration

### Automatic Theme Detection

```tsx
const { theme = "system" } = useTheme();
```

- **System Theme**: Respects user's operating system preference
- **Manual Override**: Supports explicit light/dark theme selection
- **Dynamic Updates**: Automatically updates when theme changes

### Semantic Color Classes

```tsx
className="toaster group bg-popover text-popover-foreground border border-border"
```

- **Background**: Uses `bg-popover` for consistent popup styling
- **Text**: Uses `text-popover-foreground` for proper contrast
- **Border**: Uses `border-border` for subtle boundaries
- **Group Styling**: Enables grouped toast animations

## Accessibility Features

### ARIA Support

- **Screen Reader Announcements**: Sonner provides automatic ARIA live regions
- **Keyboard Navigation**: Built-in keyboard support for dismissing toasts
- **Focus Management**: Proper focus handling for interactive toasts

### User Experience

- **Non-Intrusive**: Toasts don't block user interaction with main content
- **Auto-Dismissal**: Configurable timeout for automatic dismissal
- **Manual Dismissal**: Users can manually close toasts when needed

## Dependencies

### Theme Dependencies

- **next-themes**: Hook for theme detection and management
- **Theme Context**: Requires theme provider in application root

### UI Library

- **Sonner**: Core toast notification library
- **ToasterProps**: Type definitions for configuration options

### Styling

- **Tailwind CSS**: Uses Tailwind utility classes for styling
- **Semantic Variables**: Leverages CSS custom properties for theming

## Toast Types and States

### Standard Toast Types

```tsx
// Success states
toast.success('File uploaded successfully');

// Error states  
toast.error('Failed to save changes');

// Warning states
toast.warning('Please save your work');

// Information
toast.info('New feature available');
```

### Advanced Toast Features

```tsx
// Custom duration
toast.success('Saved!', { duration: 2000 });

// Action buttons
toast.error('Failed to delete', {
  action: {
    label: 'Retry',
    onClick: () => retryDelete()
  }
});

// Rich content
toast.custom((t) => (
  <div className="flex items-center gap-2">
    <img src="/avatar.jpg" alt="User" className="w-8 h-8 rounded" />
    <span>Custom notification content</span>
  </div>
));
```

## Integration Points

### Theme System

- **Theme Provider**: Requires `next-themes` ThemeProvider in app root
- **CSS Variables**: Uses semantic color variables for consistent styling
- **Dynamic Updates**: Automatically responds to theme changes

### Component Library

- **Consistent Styling**: Matches application's design system
- **Semantic Colors**: Uses same color tokens as other components
- **Responsive Design**: Works across different screen sizes

## Configuration Options

### Positioning

```tsx
<Toaster position="top-right" />     // Top right corner
<Toaster position="bottom-center" />  // Bottom center
<Toaster position="top-left" />      // Top left corner
```

### Behavior Settings

```tsx
<Toaster
  duration={5000}        // Auto-dismiss after 5 seconds
  closeButton={true}     // Show close button
  richColors={true}      // Use rich color variants
  expand={true}          // Allow toast expansion
  visibleToasts={5}      // Maximum visible toasts
/>
```

### Styling Customization

```tsx
<Toaster
  className="custom-toaster"
  toastOptions={{
    className: 'custom-toast',
    style: {
      // Custom inline styles if needed
    }
  }}
/>
```

## Best Practices

### Toast Usage Guidelines

- **Appropriate Timing**: Use for immediate feedback on user actions
- **Clear Messages**: Keep toast messages concise and actionable
- **Proper Types**: Use appropriate toast types for different scenarios
- **Non-Blocking**: Don't use for critical information that must be read

### Performance Considerations

- **Single Instance**: Use only one Toaster component per application
- **Efficient Rendering**: Sonner optimizes rendering for multiple toasts
- **Memory Management**: Automatic cleanup of dismissed toasts

### Accessibility Guidelines

- **Clear Messages**: Ensure toast content is clear and descriptive
- **Adequate Duration**: Provide sufficient time to read messages
- **Alternative Feedback**: Don't rely solely on toasts for critical feedback

## Related Files

- **[theme-provider.tsx](../../lib/theme/theme-provider.tsx.md)**: Theme provider for theme integration
- **[toast.ts](../../lib/utils/toast.ts.md)**: Utility functions for toast management
- **[button.tsx](button.tsx.md)**: Button components used in toast actions

## Error Handling

### Fallback Behavior

- **Theme Fallback**: Defaults to "system" theme if theme detection fails
- **Graceful Degradation**: Works without theme provider (uses default styling)
- **Error Boundaries**: Won't crash application if Sonner encounters errors

### Development Experience

- **Type Safety**: Full TypeScript support with proper type definitions
- **Hot Reload**: Supports development hot reload without losing toast state
- **Debug Mode**: Sonner provides debug information in development

## Performance Characteristics

### Rendering Optimization

- **Virtual Scrolling**: Efficient rendering of multiple toasts
- **Animation Performance**: Hardware-accelerated animations
- **Memory Usage**: Automatic cleanup prevents memory leaks

### Bundle Size

- **Tree Shaking**: Only imports necessary Sonner components
- **Minimal Footprint**: Lightweight wrapper with minimal overhead
- **Lazy Loading**: Can be code-split if needed
