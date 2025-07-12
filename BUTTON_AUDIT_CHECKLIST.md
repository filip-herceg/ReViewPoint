# 🔍 BUTTON AUDIT - Raw HTML Button Elements Found

**Generated:** July 11, 2025  
**Status:** 🔴 Multiple Raw Buttons Found - Fixing Required

---

## ❌ **Critical Issues Found**

### 1. **Password Toggle Buttons**
📁 `frontend/src/pages/auth/ResetPasswordPage.tsx` - **Lines ~193-201**
```tsx
<button
    type="button"
    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
    disabled={isLoading}
>
    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
</button>
```
**Action:** Replace with `<Button variant="ghost" size="icon-sm">`

### 2. **Dropdown Menu Buttons**
📁 `frontend/src/components/file-management/FileBulkActions.tsx` - **Lines ~135-175**
```tsx
<button className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted">
    <span className="mr-2">⭐</span>
    Add to Favorites
</button>
<!-- Multiple similar buttons -->
```
**Action:** Replace with `<Button variant="ghost" size="sm" className="w-full justify-start">`

### 3. **File Management Dropdowns**
📁 `frontend/src/components/file-management/FileTable.tsx` - **Lines ~190-220**
📁 `frontend/src/components/file-management/FileList.tsx` - **Lines ~170-200**  
📁 `frontend/src/components/file-management/FileGrid.tsx` - **Lines ~170-200**
```tsx
<button className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted">
    <Eye className="mr-2 h-4 w-4" />
    Preview
</button>
```
**Action:** Replace with `<Button variant="ghost" size="sm" className="w-full justify-start">`

### 4. **File Toolbar Sort Buttons**
📁 `frontend/src/components/file-management/FileToolbar.tsx` - **Lines ~123-140**
```tsx
<button
    className={cn('flex items-center w-full px-4 py-2 text-sm hover:bg-muted')}
    onClick={() => handleSortClick(field)}
>
    <span className="flex-1 text-left">{label}</span>
</button>
```
**Action:** Replace with `<Button variant="ghost" size="sm" className="w-full justify-between">`

### 5. **Test File Raw Buttons**
📁 Various test files contain raw buttons for testing purposes
**Action:** Update test utilities to use `<Button>` component

---

## 🎯 **Refactoring Plan**

### **Priority 1: Authentication Components** 🔴
- Fix password toggle buttons in auth forms
- Ensure accessibility with proper focus management

### **Priority 2: File Management Components** 🟡  
- Replace dropdown menu buttons with Button component
- Maintain dropdown functionality with proper event handling

### **Priority 3: Test Files** 🟢
- Update test utilities and mocks
- Ensure tests still pass after migration

---

## 📝 **Next Steps**
1. [ ] Fix ResetPasswordPage.tsx password toggle buttons
2. [ ] Fix FileBulkActions.tsx dropdown buttons  
3. [ ] Fix FileTable.tsx dropdown buttons
4. [ ] Fix FileList.tsx dropdown buttons
5. [ ] Fix FileGrid.tsx dropdown buttons
6. [ ] Fix FileToolbar.tsx sort buttons
7. [ ] Update test files
8. [ ] Run comprehensive tests
9. [ ] Verify no accessibility regressions

**Estimated Time:** 2-3 hours  
**Files to Modify:** ~8-10 files  
**Risk Level:** Low (mostly styling/consistency improvements)
