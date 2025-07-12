# Button Component Standards

## Overview

All buttons in the ReViewPoint application must use the standardized `Button` component from `@/components/ui/button`. Individual `<button>` elements with custom styles are strictly prohibited to ensure consistency, maintainability, and accessibility.

## Available Variants

### Primary Actions
- `default` - Primary action buttons (blue background)
- `destructive` - Dangerous actions (red background, white text)
- `secondary` - Secondary actions (light background)

### Outline Variants
- `outline` - Standard outline button
- `outline-destructive` - Destructive outline (red border/text)
- `outline-success` - Success outline (green border/text)

### Utility Variants
- `ghost` - Transparent background, hover effect
- `link` - Text-only with underline
- `icon-sm` - Small icon-only buttons
- `tab` - Navigation tab buttons with active state
- `theme-option` - Theme selection cards
- `floating-icon` - Floating action buttons (e.g., camera icon)

## Available Sizes
- `default` - Standard button height (h-9)
- `sm` - Small buttons (h-8)
- `lg` - Large buttons (h-10)
- `icon` - Square icon buttons (size-9)
- `icon-sm` - Small square icon buttons (size-6)
- `floating` - Floating button padding
- `none` - No size classes (for variants that handle their own sizing)

## Props
- `variant` - Button style variant (see above)
- `size` - Button size (see above)
- `asChild` - Use with Radix Slot for composite components
- `active` - Boolean for active state (used with `tab` and `theme-option`)
- `loading` - Boolean to show loading spinner
- `disabled` - Standard disabled state

## Usage Examples

### Basic Button
```tsx
<Button>Click me</Button>
<Button variant="outline">Cancel</Button>
<Button variant="destructive">Delete</Button>
```

### With Icon
```tsx
<Button>
    <PlusIcon className="w-4 h-4 mr-2" />
    Add Item
</Button>
```

### Icon-only Button
```tsx
<Button variant="icon-sm" size="icon-sm">
    <X className="h-4 w-4" />
</Button>
```

### Loading State
```tsx
<Button loading disabled={isLoading}>
    Save Changes
</Button>
```

### Navigation Tabs
```tsx
<Button variant="tab" active={activeTab === 'overview'}>
    <Icon className="w-4 h-4" />
    <span>Overview</span>
</Button>
```

### Theme Selection
```tsx
<Button 
    variant="theme-option" 
    size="none" 
    active={theme === 'light'}
    onClick={() => setTheme('light')}
>
    <Sun className="w-6 h-6" />
    <span>Light</span>
</Button>
```

## Prohibited Patterns

❌ **DO NOT** use raw `<button>` elements:
```tsx
// WRONG
<button className="px-4 py-2 bg-blue-500 text-white rounded">
    Click me
</button>
```

❌ **DO NOT** override button variants with custom classes:
```tsx
// WRONG
<Button className="bg-red-500 text-white border-red-600">
    Delete
</Button>
```

✅ **DO** use the appropriate variant:
```tsx
// CORRECT
<Button variant="destructive">
    Delete
</Button>
```

## Extending the Button Component

If you need a new button style:

1. Add a new variant to `buttonVariantClasses` in `button.tsx`
2. Add any new sizes to `buttonSizeClasses` if needed
3. Update this documentation
4. Use CSS variables for colors to maintain theme consistency

## CSS Variables Used

The Button component uses these CSS variables for theming:
- `--destructive-foreground` - White text for destructive buttons
- `--text-inverse` - White text for floating buttons
- `--color-success` - Green color for success variants
- All standard Tailwind CSS variables for borders, backgrounds, etc.

## Code Review Guidelines

During code review, ensure:
- No raw `<button>` elements exist in the codebase
- All Button components use appropriate variants
- Custom className overrides are justified and documented
- New button styles are implemented as variants, not one-off custom styles

## Migration Checklist

When migrating existing buttons:
1. Replace `<button>` with `<Button>`
2. Choose appropriate `variant` and `size`
3. Remove custom className styling
4. Test active/disabled states
5. Verify accessibility (focus, keyboard navigation)
