# theme-provider.tsx - Application Theme Management

## Purpose

The `theme-provider.tsx` file provides centralized theme management for the ReViewPoint application, handling light/dark mode switching, theme persistence, and system preference detection. It implements a React context-based theme system with automatic color scheme management.

## Key Components

### **ThemeContext Interface**

```typescript
interface ThemeContextType {
  mode: ThemeMode;           // Current theme mode ('light' | 'dark' | 'system')
  setMode: (mode: ThemeMode) => void;  // Manual theme setter
  toggleMode: () => void;    // Toggle between light/dark
  colors: ThemeColors;       // Current color palette
}
```

### **Theme Provider Component**

- **Theme Persistence**: Automatically saves theme preference to localStorage
- **System Detection**: Respects user's system color scheme preference
- **Color Management**: Provides current color palette based on selected theme
- **Theme Switching**: Supports manual and automatic theme transitions

### **Theme Modes**

- **Light**: Default light theme with bright color palette
- **Dark**: Dark theme with dimmed color palette optimized for low-light usage
- **System**: Automatically follows system color scheme preference

## Implementation Details

### **Theme Initialization**

```typescript
// Priority order for theme detection:
1. localStorage saved preference
2. System color scheme (if enableSystem is true)
3. Default theme (light)
```

### **Color Palette Management**

The provider automatically selects the appropriate color palette:

```typescript
const colors = mode === 'dark' 
  ? themeColors.dark 
  : themeColors.light;
```

### **System Theme Detection**

```typescript
// Detects system preference using media query
const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
  ? 'dark' 
  : 'light';
```

## Dependencies

### **Core Dependencies**

- `React` - Context API and state management
- `@/logger` - Theme change logging and error tracking

### **Theme Configuration**

- [colors.ts](colors.ts.md) - Theme color definitions and palette management
- [ThemeMode](../../types/theme.ts.md) - Theme mode type definitions

## Usage Examples

### **Basic Theme Provider Setup**

```typescript
import { ThemeProvider } from '@/lib/theme/theme-provider';

function App() {
  return (
    <ThemeProvider defaultTheme="light" enableSystem={true}>
      <YourApplication />
    </ThemeProvider>
  );
}
```

### **Using Theme Context**

```typescript
import { useTheme } from '@/lib/theme/theme-provider';

function ThemeToggle() {
  const { mode, toggleMode, setMode } = useTheme();
  
  return (
    <button onClick={toggleMode}>
      Current: {mode}
    </button>
  );
}
```

### **Accessing Theme Colors**

```typescript
function ThemedComponent() {
  const { colors } = useTheme();
  
  return (
    <div style={{ 
      backgroundColor: colors.background,
      color: colors.foreground 
    }}>
      Themed content
    </div>
  );
}
```

## Theme Persistence

### **Local Storage Integration**

- **Storage Key**: `reviewpoint-theme`
- **Automatic Saving**: Theme changes are immediately persisted
- **Cross-Session**: Theme preference maintained across browser sessions

### **Error Handling**

```typescript
// Graceful fallback for localStorage issues
try {
  localStorage.setItem(THEME_STORAGE_KEY, newMode);
} catch (error) {
  logger.warn('Theme persistence failed', error);
  // Continue with in-memory theme state
}
```

## System Integration

### **CSS Variables**

The theme provider updates CSS custom properties for global theme application:

```css
:root {
  --background: theme-colors-background;
  --foreground: theme-colors-foreground;
  --primary: theme-colors-primary;
  /* Additional theme variables */
}
```

### **Media Query Sync**

```typescript
// Listens for system theme changes
window.matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', handleSystemThemeChange);
```

## Configuration Options

### **ThemeProvider Props**

```typescript
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: ThemeMode;     // Initial theme mode
  enableSystem?: boolean;       // Enable system preference detection
}
```

### **Default Configuration**

- **Default Theme**: `light`
- **System Detection**: `enabled`
- **Storage Persistence**: `enabled`

## Related Files

- [colors.ts](colors.ts.md) - Theme color definitions and palette configuration
- [useTheme.ts](../hooks/useTheme.ts.md) - Theme context hook for component usage
- [ThemeToggle.tsx](../../components/ui/theme-toggle.tsx.md) - UI component for theme switching

## Performance Considerations

### **Theme Switching Optimization**

- **Immediate Updates**: Theme changes are applied instantly without flicker
- **Minimal Re-renders**: Context updates only trigger re-renders for consuming components
- **Efficient Storage**: localStorage operations are optimized and error-handled

### **Memory Management**

- **Event Cleanup**: Media query listeners are properly cleaned up on unmount
- **Lightweight Context**: Theme context contains minimal state for optimal performance

## Development Notes

### **Adding New Themes**

1. Define new theme colors in `colors.ts`
2. Update `ThemeMode` type definition
3. Add theme detection logic in provider
4. Update theme switching logic

### **Theme Testing**

```typescript
// Test theme persistence
localStorage.setItem('reviewpoint-theme', 'dark');
// Reload page to verify theme restoration

// Test system theme detection
// Change system preference and verify automatic update
```

### **Debugging Theme Issues**

- Check browser console for theme-related logs
- Verify localStorage contains correct theme value
- Ensure CSS custom properties are updated correctly
- Test theme switching across different components
