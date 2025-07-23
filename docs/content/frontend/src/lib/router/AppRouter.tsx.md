# AppRouter.tsx - Central Application Routing

## Purpose

The `AppRouter.tsx` file defines the central routing configuration for the ReViewPoint frontend application using React Router v6. It implements lazy loading, protected routes, error boundaries, and provides a comprehensive navigation structure for all application features.

## Key Components

### **Route Configuration**

- **Browser Router**: Uses `createBrowserRouter` for modern routing with data APIs
- **Lazy Loading**: All page components are loaded asynchronously for optimal performance
- **Route Wrapping**: Combines error boundaries and suspense for robust error handling

### **Protected Route Structure**

- **Public Routes**: Authentication pages (login, register, password reset)
- **Protected Routes**: Dashboard, uploads, reviews, profile, settings
- **Admin Routes**: User management and administrative panels
- **Moderation Routes**: Content moderation interfaces
- **Marketplace Routes**: Module marketplace and management

### **Layout Integration**

- **AppShell**: Main application layout wrapper for authenticated users
- **AuthLayout**: Specialized layout for authentication pages
- **RouteWrapper**: Combines ErrorBoundary and Suspense for each route

## Route Structure

### **Public Routes**

```typescript
/login              - User authentication
/register           - User registration
/forgot-password    - Password recovery initiation
/reset-password     - Password reset completion
```

### **Protected Application Routes**

```typescript
/                   - Home page (dashboard redirect)
/dashboard          - Main dashboard view
/uploads            - File upload management
/uploads/:id        - Individual upload details
/uploads/new        - New upload creation
/reviews            - Review management
/reviews/:id        - Individual review details
/profile            - User profile management
/settings           - Application settings
```

### **Administrative Routes**

```typescript
/admin              - Admin panel (admin role required)
/admin/users        - User management interface
/moderation         - Moderation panel (moderator role required)
```

### **Marketplace Routes**

```typescript
/marketplace        - Module marketplace browse
/marketplace/:id    - Module detail view
/marketplace/my     - User's modules management
```

## Dependencies

### **Core Routing**

- `react-router-dom` - Modern React routing with data APIs
- `React.lazy()` - Dynamic imports for code splitting

### **Layout Components**

- [AppShell](../../components/layout/AppShell.tsx.md) - Main application layout
- [AuthLayout](../../components/layout/AuthLayout.tsx.md) - Authentication layout
- [ProtectedRoute](ProtectedRoute.tsx.md) - Route protection wrapper

### **UI Components**

- [ErrorBoundary](../../components/ui/error-boundary.tsx.md) - Error handling wrapper
- [SkeletonLoader](../../components/ui/skeleton-loader.tsx.md) - Loading state component

## Implementation Details

### **Lazy Loading Strategy**

```typescript
// Optimized imports for code splitting
const HomePage = React.lazy(() => import("@/pages/HomePage"));
const DashboardPage = React.lazy(
  () => import("@/pages/dashboard/DashboardPage"),
);
```

### **Route Protection**

- Uses `ProtectedRoute` component for authentication checks
- Automatic redirects for unauthorized access
- Role-based access control for admin/moderation features

### **Error Handling**

- ErrorBoundary wrapper catches and handles route-level errors
- Suspense provides loading states during component loading
- Graceful fallbacks for failed route loads

### **Performance Optimization**

- Code splitting reduces initial bundle size
- Lazy loading improves initial page load time
- Skeleton loaders provide immediate visual feedback

## Usage Examples

### **Basic Navigation**

```typescript
import { useNavigate } from "react-router-dom";

const navigate = useNavigate();
navigate("/dashboard");
navigate("/uploads/new");
```

### **Route Parameters**

```typescript
import { useParams } from "react-router-dom";

const { id } = useParams<{ id: string }>();
// Access upload ID or review ID from URL
```

## Related Files

- [ProtectedRoute.tsx](ProtectedRoute.tsx.md) - Authentication wrapper for protected routes
- [AppShell.tsx](../../components/layout/AppShell.tsx.md) - Main application layout component
- [AuthLayout.tsx](../../components/layout/AuthLayout.tsx.md) - Authentication pages layout
- [Navigation.tsx](../../components/navigation/Navigation.tsx.md) - Navigation components

## Configuration

### **Route Nesting Structure**

- Root level routes use AppShell layout
- Authentication routes use AuthLayout
- Protected routes require authentication via ProtectedRoute wrapper
- Admin routes require additional role verification

### **Loading Strategy**

- All page components use React.lazy for dynamic imports
- Suspense boundaries provide loading states
- Error boundaries catch and display routing errors

## Development Notes

### **Adding New Routes**

1. Create lazy-loaded import for new page component
2. Add route configuration to appropriate section
3. Include protection wrapper if authentication required
4. Update navigation components to include new route

### **Performance Considerations**

- Bundle analysis shows effective code splitting
- Route-based chunks optimize loading performance
- Preloading strategies can be implemented for critical routes

### **Error Handling Strategy**

- Route-level error boundaries prevent application crashes
- Fallback UI provides user-friendly error messages
- Error reporting integration tracks routing issues
