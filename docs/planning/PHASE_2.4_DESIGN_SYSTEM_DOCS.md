# ReViewPoint Design System Documentation

## Phase 2.4 Implementation Summary

This document provides comprehensive information about the ReViewPoint Design System implemented in Phase 2.4, including components, design tokens, and usage guidelines.

## 🎨 Design Tokens

### Colors

- **Theme Support**: Full light/dark mode support
- **Primary Colors**: Brand-consistent blue palette
- **Semantic Colors**: Success, warning, error, info states
- **Neutral Colors**: Comprehensive grayscale palette
- **Location**: `src/lib/theme/colors.ts`

### Typography

- **Scale**: Comprehensive size scale from xs to 9xl
- **Variants**: Display, text, body, caption, and code styles
- **Fonts**: Inter (primary), JetBrains Mono (code)
- **Location**: `src/lib/theme/typography.ts`

### Spacing

- **Scale**: Consistent spacing from 0.5 to 96 units
- **Usage**: Margin, padding, gaps throughout the system
- **Location**: `src/lib/theme/spacing.ts`

### Breakpoints

- **Responsive**: Mobile-first responsive design
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- **Location**: `src/lib/theme/breakpoints.ts`

## 🏗️ Architecture

### Theme Provider

- **Component**: `ThemeProvider` in `src/lib/theme/theme-provider.tsx`
- **Features**: System preference detection, persistence, theme switching
- **Integration**: Wrapped around entire app for global theme management

### UI Store (Enhanced)

- **Location**: `src/lib/store/uiStore.ts`
- **Features**: Theme state, notifications, modals, loading states
- **Persistence**: Theme preferences persisted to localStorage
- **Logging**: Comprehensive error handling and logging

## 🧩 Components

### Core UI Components

#### StatusBadge

- **Location**: `src/components/feedback/StatusBadge.tsx`
- **Purpose**: Consistent status indicators with icons
- **Variants**: success, error, warning, info, pending, etc.
- **Features**: Icon support, size variants, accessibility

#### DataTable

- **Location**: `src/components/ui/data-table.tsx`
- **Purpose**: Advanced data table with full feature set
- **Features**:
  - Sorting, filtering, pagination
  - Loading and error states
  - Empty state handling
  - Row selection
  - Responsive design
- **Tests**: Comprehensive test suite in `tests/components/ui/data-table.test.tsx`

#### FileUpload

- **Location**: `src/components/ui/file-upload.tsx`
- **Purpose**: Drag & drop file upload with validation
- **Features**:
  - Drag and drop interface
  - File validation (size, type, count)
  - Progress tracking
  - Preview capabilities
  - Error handling

#### Modal

- **Location**: `src/components/ui/modal.tsx`
- **Purpose**: Accessible modal dialogs
- **Features**:
  - Multiple sizes (sm, md, lg, xl, full)
  - Variant support
  - Accessibility features
  - Animation support
  - Convenience wrappers

#### FormField

- **Location**: `src/components/ui/form-field.tsx`
- **Purpose**: Consistent form field component
- **Features**:
  - Multiple input types (text, email, textarea, select)
  - Validation support
  - Error state handling
  - Accessibility features
- **Tests**: Comprehensive test suite in `tests/components/ui/form-field.test.tsx`

#### EmptyState

- **Location**: `src/components/ui/empty-state.tsx`
- **Purpose**: Consistent empty state messaging
- **Features**:
  - Icon support
  - Action buttons
  - Multiple variants
  - Accessibility
- **Tests**: Full test coverage in `tests/components/ui/empty-state.test.tsx`

#### ErrorBoundary

- **Location**: `src/components/ui/error-boundary.tsx`
- **Purpose**: Global error handling with fallback UI
- **Features**:
  - Fallback UI rendering
  - Error logging integration
  - Retry functionality
  - Reload option
- **Tests**: Error handling tests in `tests/components/ui/error-boundary.test.tsx`

#### SkeletonLoader

- **Location**: `src/components/ui/skeleton-loader.tsx`
- **Purpose**: Loading state placeholders
- **Features**:
  - Multiple variants (card, list, text, circular, rectangular)
  - Customizable dimensions
  - Smooth animations

#### Toast Notifications

- **Location**: `src/components/ui/toast.tsx`
- **Purpose**: Toast notification system using Sonner
- **Features**:
  - Multiple types (success, error, warning, info)
  - Auto-dismiss functionality
  - Action buttons
  - Design system integration

#### ThemeToggle

- **Location**: `src/components/ui/theme-toggle.tsx`
- **Purpose**: Theme switching interface
- **Features**:
  - Light/dark mode toggle
  - System preference option
  - Icon indicators

## 🛠️ Installation & Setup

### Dependencies Added

```bash
pnpm add sonner
```

### Shadcn Components Installed

```bash
npx shadcn@latest add dialog sonner skeleton dropdown-menu select textarea label form progress
```

### File Structure

```
src/
├── lib/
│   ├── theme/
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   ├── spacing.ts
│   │   ├── breakpoints.ts
│   │   └── theme-provider.tsx
│   └── store/
│       └── uiStore.ts (enhanced)
├── components/
│   ├── ui/
│   │   ├── data-table.tsx
│   │   ├── file-upload.tsx
│   │   ├── modal.tsx
│   │   ├── form-field.tsx
│   │   ├── empty-state.tsx
│   │   ├── error-boundary.tsx
│   │   ├── skeleton-loader.tsx
│   │   ├── toast.tsx
│   │   └── theme-toggle.tsx
│   └── feedback/
│       └── StatusBadge.tsx
└── pages/
    └── DesignSystemPage.tsx (demo)
```

## 🧪 Testing

### Test Coverage

- **DataTable**: 14 comprehensive tests covering behavior, state, interactions, loading, errors, accessibility, performance, and edge cases
- **FormField**: 13 tests covering rendering, validation, interactions, and accessibility
- **EmptyState**: 10 tests covering variants, actions, and accessibility
- **ErrorBoundary**: 8 tests covering error handling, fallback UI, and recovery
- **UIStore**: Enhanced tests for new notification system

### Running Tests

```bash
# Run all tests
pnpm test

# Run with bail on first failure
pnpm test -- --bail=1

# Run specific component tests
pnpm test data-table
pnpm test form-field
pnpm test empty-state
pnpm test error-boundary
```

## 📋 Usage Guidelines

### Design Principles

1. **Consistency**: Use design tokens for consistent spacing, colors, and typography
2. **Accessibility**: All components include proper ARIA attributes and keyboard navigation
3. **Responsiveness**: Mobile-first responsive design with breakpoint utilities
4. **Performance**: Optimized components with proper loading states
5. **Error Handling**: Comprehensive error handling with logging integration

### Best Practices

#### Theme Usage

```tsx
import { useTheme } from '@/lib/theme/theme-provider';

function MyComponent() {
  const { mode, toggleMode, colors } = useTheme();
  
  return (
    <div className={`bg-${colors.background} text-${colors.foreground}`}>
      Current theme: {mode}
    </div>
  );
}
```

#### Notifications

```tsx
import { useUIStore } from '@/lib/store/uiStore';

function MyComponent() {
  const { addNotification } = useUIStore();
  
  const handleSuccess = () => {
    addNotification({
      type: 'success',
      title: 'Success!',
      message: 'Operation completed successfully',
      duration: 3000
    });
  };
}
```

#### Path Aliases

All new components use path aliases to avoid relative imports:

```tsx
import { Component } from '@/components/ui/component';
import { useStore } from '@/lib/store/store';
import { utility } from '@/lib/utils/utility';
```

## 🚀 Demo & Examples

### Design System Demo Page

- **Location**: `src/pages/DesignSystemPage.tsx`
- **Purpose**: Comprehensive showcase of all components and design tokens
- **Features**: Interactive examples, theme switching, component demonstrations

### Integration Examples

The design system is integrated into:

- **App Component**: ThemeProvider and ErrorBoundary
- **Router**: Enhanced loading states and error boundaries
- **Global CSS**: Design token integration

## 🔄 Migration & Integration

### Existing Components

- Enhanced existing components to use new design tokens
- Integrated new error boundary throughout the application
- Updated global styles to include design system tokens

### Breaking Changes

- None - all changes are additive and backward compatible

### Future Enhancements

- Additional component variants
- Extended animation system
- Advanced form validation
- More comprehensive responsive utilities

## 📝 Maintenance

### Code Quality

- **TypeScript**: Full type safety throughout
- **Error Handling**: Centralized logging using `logger.ts`
- **Testing**: Comprehensive test coverage for all components
- **Documentation**: Inline JSDoc comments and README files

### Performance

- **Code Splitting**: Components support lazy loading
- **Optimized Renders**: Proper memoization and state management
- **Bundle Size**: Tree-shakeable components and utilities

---

This design system provides a solid foundation for consistent, accessible, and maintainable UI development in the ReViewPoint application.
