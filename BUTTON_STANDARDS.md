# Button Standards Guide

## Overview

This document defines the standardized button system for ReViewPoint. **All buttons must use the centralized `<Button>` component** - raw `<button>` elements are not allowed.

## Button Component API

### Basic Usage

```tsx
import { Button } from '@/components/ui/button';

// Standard button
<Button>Click me</Button>

// With variant and size
<Button variant="outline" size="lg">Large Outline Button</Button>

// As child (for routing/navigation)
<Button asChild>
  <Link to="/somewhere">Navigate</Link>
</Button>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `"default"` | Button style variant |
| `size` | `string` | `"default"` | Button size |
| `asChild` | `boolean` | `false` | Render as child component (for routing) |
| `active` | `boolean` | `false` | Active state |
| `loading` | `boolean` | `false` | Loading state with spinner |
| `disabled` | `boolean` | `false` | Disabled state |

## Variants

### Primary Actions

- **`default`** - Primary action buttons (signup, save, submit)
- **`destructive`** - Dangerous actions (delete, remove)

### Secondary Actions  

- **`outline`** - Secondary actions (cancel, back)
- **`secondary`** - Alternative secondary styling
- **`ghost`** - Minimal actions (close, dismiss)

### Special Purpose

- **`link`** - Text-like buttons with underline
- **`outline-destructive`** - Destructive actions with outline
- **`outline-success`** - Success actions with outline

### Layout/Navigation

- **`tab`** - Tab navigation buttons
- **`theme-option`** - Theme selector buttons
- **`floating-icon`** - Floating action buttons

### Icon Buttons

- **`icon-sm`** - Small icon-only buttons

## Sizes

- **`sm`** - Small buttons (h-8)
- **`default`** - Standard buttons (h-9)
- **`lg`** - Large buttons (h-10)
- **`icon`** - Icon buttons (9x9)
- **`icon-sm`** - Small icon buttons (6x6)
- **`floating`** - Floating buttons
- **`none`** - No size constraints

## Usage Examples

### Navigation Buttons (asChild Pattern)

✅ **CORRECT - Single child element:**

```tsx
<Button asChild size="lg">
  <Link to="/auth/register" className="flex items-center">
    Get Started Free
    <ArrowRight className="ml-2 h-4 w-4" />
  </Link>
</Button>
```

❌ **INCORRECT - Multiple children:**

```tsx
<Button asChild size="lg">
  <Link to="/auth/register">Get Started Free</Link>
  <ArrowRight className="ml-2 h-4 w-4" />
</Button>
```

### Form Buttons

```tsx
// Primary form submission
<Button type="submit" loading={isSubmitting}>
  Save Changes
</Button>

// Secondary form action  
<Button type="button" variant="outline" onClick={handleCancel}>
  Cancel
</Button>

// Destructive form action
<Button type="button" variant="destructive" onClick={handleDelete}>
  Delete Item
</Button>
```

### Icon Buttons

```tsx
// Icon-only button
<Button variant="ghost" size="icon">
  <Settings className="h-4 w-4" />
</Button>

// Icon with text
<Button variant="outline" size="sm">
  <Plus className="mr-2 h-4 w-4" />
  Add Item
</Button>
```

### Loading States

```tsx
<Button loading={isLoading} disabled={isLoading}>
  {isLoading ? 'Saving...' : 'Save'}
</Button>
```

## Accessibility Guidelines

1. **Always provide descriptive text or aria-label**
2. **Use semantic HTML when possible**
3. **Ensure sufficient color contrast**
4. **Support keyboard navigation**
5. **Provide loading/disabled states**

## Anti-Patterns

❌ **Do not use raw `<button>` elements:**

```tsx
// WRONG
<button className="bg-blue-500 text-white px-4 py-2">
  Click me
</button>
```

❌ **Do not apply custom styling outside the component:**

```tsx
// WRONG  
<Button className="bg-red-500 hover:bg-red-600">
  Custom styled
</Button>
```

❌ **Do not use asChild with multiple elements:**

```tsx
// WRONG - Causes React.Children.only error
<Button asChild>
  <div>First</div>
  <div>Second</div>
</Button>
```

## Design Tokens

The button system uses semantic color variables:

- `--primary` / `--primary-foreground`
- `--destructive` / `--destructive-foreground`  
- `--secondary` / `--secondary-foreground`
- `--background` / `--foreground`
- `--border`
- `--accent` / `--accent-foreground`

## ESLint Rules

To enforce these standards, add this ESLint rule:

```json
{
  "rules": {
    "no-restricted-syntax": [
      "error",
      {
        "selector": "JSXElement[openingElement.name.name='button']",
        "message": "Use the Button component from @/components/ui/button instead of raw <button> elements"
      }
    ]
  }
}
```

## Contributing

When adding new button variants:

1. **Add the variant to `buttonVariantClasses`**
2. **Use semantic color variables only**
3. **Update this documentation**
4. **Add examples to the style guide**
5. **Test accessibility compliance**

## Migration Checklist

- [ ] Replace all raw `<button>` elements with `<Button>`
- [ ] Fix all `asChild` usage to have single children
- [ ] Update custom styling to use variants
- [ ] Test for React.Children.only errors
- [ ] Verify accessibility compliance
- [ ] Add ESLint rule to prevent future violations
