# Biome Linting Issues Analysis & Fixes

## Current Status: 227 Total Issues

## Issue Categories by Priority

### 🎯 High Priority: Correctness Issues (Critical for code quality)

1. **noUnusedVariables** - Remove or use unused variables
2. **noSwitchDeclarations** - Fix variable scoping in switch statements  
3. **noInvalidUseBeforeDeclaration** - Fix declaration order issues
4. **useExhaustiveDependencies** - Fix React hook dependencies

### 🔧 Medium Priority: Accessibility Issues (UX/Standards compliance)

1. **useButtonType** - Add explicit button types (type="button")
2. **useSemanticElements** - Replace role attributes with semantic HTML
3. **noStaticElementInteractions** - Add proper roles to interactive elements
4. **useKeyWithClickEvents** - Add keyboard event handlers
5. **useAriaPropsSupportedByRole** - Fix invalid ARIA attributes

### 🎨 Low Priority: Format Issues (Auto-fixable styling)

1. **format** - Code formatting and line endings

## 🔥 FIRST BATCH: Critical Correctness Issues (4-5 files)

### ✅ Target Files for Immediate Fix

1. **src/types/globals.d.ts** - Remove unused ImportMeta interface
2. **src/components/file-management/FileManagementDashboard.tsx** - Remove unused setPage variable  
3. **src/components/modules/ModuleConfigSidebar.tsx** - Fix switch case declaration scoping
4. **src/components/ui/file-upload.tsx** - Fix useCallback dependencies and declaration order

## Systematic Approach

- Fix 4-5 issues per batch for manageable progress
- Start with correctness issues (highest impact)
- Apply consistent patterns across similar issues
- Track progress with issue counts

## Key Patterns to Apply

1. **Unused Variables**: Remove or mark with underscore prefix if intentionally unused
2. **Switch Declarations**: Wrap case blocks in curly braces `case "value": { ... }`
3. **Button Types**: Add `type="button"` to all interactive buttons
4. **Hook Dependencies**: Add missing dependencies or use useCallback/useMemo properly

## Next Steps

1. Fix critical correctness issues first (4-5 files)
2. Move to accessibility improvements
3. Handle formatting issues with auto-fix
4. Track progress: 227 → target significant reduction
