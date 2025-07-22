# Frontend Type Safety Guidelines

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Type**           | Documentation                                                      |
| **Responsibility** | TypeScript usage guidelines and type safety best practices        |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

This document provides guidelines for maintaining type safety in the ReViewPoint frontend application, including best practices for TypeScript usage, API type generation, and type-safe development patterns.

## 2. TypeScript Configuration

### Strict Type Checking
The project uses strict TypeScript configuration to ensure maximum type safety:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Type Safety Rules
- **No `any` types**: Use specific types or `unknown` when necessary
- **Strict null checks**: Handle null and undefined explicitly
- **No implicit returns**: All code paths must return a value
- **Exhaustive switch statements**: Handle all enum cases

## 3. API Type Generation

### Automated Type Generation
The frontend uses automated type generation from the backend OpenAPI schema:

```bash
# Generate types from backend schema
pnpm run generate:types

# Generate types with validation
pnpm run generate:all
```

### Generated Type Structure
```typescript
// Generated from backend OpenAPI schema
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreateRequest {
  email: string;
  password: string;
}

export interface UserResponse {
  user: User;
  message: string;
}
```

## 4. Component Type Safety

### Props Interface Definition
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick: (event: MouseEvent<HTMLButtonElement>) => void;
  children: ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant,
  size,
  disabled = false,
  onClick,
  children
}) => {
  // Implementation
};
```

### Event Handler Types
```typescript
// Form event handlers
const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  // Handle form submission
};

// Input change handlers
const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
  setValue(event.target.value);
};

// Click handlers
const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
  // Handle click
};
```

## 5. State Management Types

### Store Type Definitions
```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;
```

### Zustand Store Types
```typescript
import { create } from 'zustand';

export const useAuthStore = create<AuthStore>((set, get) => ({
  // State
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  // Actions
  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.login(credentials);
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error) {
      set({ 
        error: error.message, 
        isLoading: false 
      });
    }
  },
  // ... other actions
}));
```

## 6. API Client Type Safety

### Type-Safe API Calls
```typescript
import { ApiClient } from './generated/client';

// Type-safe API client
const apiClient = new ApiClient({
  baseUrl: '/api/v1',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Type-safe API calls
const getUser = async (id: string): Promise<UserResponse> => {
  return await apiClient.users.getUser({ id });
};

const createUser = async (data: UserCreateRequest): Promise<UserResponse> => {
  return await apiClient.users.createUser({ body: data });
};
```

### Error Handling Types
```typescript
interface ApiError {
  message: string;
  code: string;
  details?: Record<string, any>;
}

const handleApiError = (error: unknown): ApiError => {
  if (error instanceof ApiError) {
    return error;
  }
  
  if (error instanceof Error) {
    return {
      message: error.message,
      code: 'UNKNOWN_ERROR'
    };
  }
  
  return {
    message: 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR'
  };
};
```

## 7. Form Validation Types

### Form Schema Types
```typescript
import { z } from 'zod';

// Zod schema for form validation
const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters')
});

// Infer TypeScript type from schema
type LoginFormData = z.infer<typeof loginSchema>;

// Use in form component
const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  });
  
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    
    // Validate with type safety
    const result = loginSchema.safeParse(formData);
    if (result.success) {
      // Form data is valid and typed
      onSubmit(result.data);
    } else {
      // Handle validation errors
      setErrors(result.error.flatten());
    }
  };
};
```

## 8. Hook Type Safety

### Custom Hook Types
```typescript
interface UseApiOptions<T> {
  initialData?: T;
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError) => void;
}

interface UseApiResult<T> {
  data: T | null;
  isLoading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
}

function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(options.initialData || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  
  // Implementation
  
  return { data, isLoading, error, refetch };
}

// Usage with full type safety
const { data, isLoading, error } = useApi<UserResponse>(
  () => apiClient.users.getCurrentUser(),
  {
    onSuccess: (userData) => {
      // userData is fully typed as UserResponse
      console.log(`Welcome ${userData.user.email}`);
    },
    onError: (error) => {
      // error is typed as ApiError
      console.error(`Error: ${error.message}`);
    }
  }
);
```

## 9. Type Guards and Assertions

### Type Guards
```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as User).id === 'string' &&
    typeof (value as User).email === 'string'
  );
}

// Usage
if (isUser(response.data)) {
  // response.data is now typed as User
  console.log(response.data.email);
}
```

### Assertion Functions
```typescript
function assertIsUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new Error('Value is not a valid User');
  }
}

// Usage
assertIsUser(response.data);
// response.data is now typed as User
console.log(response.data.email);
```

## 10. Environment and Configuration Types

### Environment Variables
```typescript
interface EnvironmentConfig {
  apiBaseUrl: string;
  environment: 'development' | 'staging' | 'production';
  enableAnalytics: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

const config: EnvironmentConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  environment: (import.meta.env.VITE_ENVIRONMENT as EnvironmentConfig['environment']) || 'development',
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  logLevel: (import.meta.env.VITE_LOG_LEVEL as EnvironmentConfig['logLevel']) || 'info'
};
```

## 11. Testing Type Safety

### Test Type Definitions
```typescript
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

// Mock function types
const mockOnClick = vi.fn<[MouseEvent<HTMLButtonElement>], void>();

// Test props with full typing
const renderButton = (props: Partial<ButtonProps> = {}) => {
  const defaultProps: ButtonProps = {
    variant: 'primary',
    size: 'md',
    onClick: mockOnClick,
    children: 'Test Button'
  };
  
  return render(<Button {...defaultProps} {...props} />);
};
```

## 12. Best Practices

### Do's
- ✅ Use strict TypeScript configuration
- ✅ Generate types from API schemas
- ✅ Define explicit interfaces for props and state
- ✅ Use type guards for runtime validation
- ✅ Leverage TypeScript's type inference
- ✅ Use union types for controlled values
- ✅ Handle null and undefined explicitly

### Don'ts
- ❌ Use `any` type (use `unknown` instead)
- ❌ Disable TypeScript strict checks
- ❌ Use type assertions without validation
- ❌ Ignore TypeScript compiler errors
- ❌ Mix typed and untyped code
- ❌ Rely on implicit typing for complex objects

## 13. Common Patterns

### Conditional Types
```typescript
type ApiResponse<T> = T extends string 
  ? { message: T }
  : { data: T };

// Usage
type StringResponse = ApiResponse<string>; // { message: string }
type UserResponse = ApiResponse<User>;     // { data: User }
```

### Utility Types
```typescript
// Make all properties optional
type PartialUser = Partial<User>;

// Pick specific properties
type UserEmail = Pick<User, 'email'>;

// Omit specific properties
type UserWithoutId = Omit<User, 'id'>;

// Required properties
type RequiredUser = Required<Partial<User>>;
```

## 14. Integration with Development Tools

### VS Code Configuration
```json
{
  "typescript.preferences.strictness": "strict",
  "typescript.suggest.autoImports": true,
  "typescript.preferences.includePackageJsonAutoImports": "auto"
}
```

### ESLint TypeScript Rules
```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "@typescript-eslint/recommended-requiring-type-checking"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/prefer-nullish-coalescing": "error"
  }
}
```

## 15. Related Documentation

- [API Reference](../../api-reference.md) - Complete API documentation
- [Component Documentation](../src/components/) - Component-specific type information
- [State Management](../src/hooks/) - Hook and state typing patterns
- [Testing Guide](../tests/README.md) - Testing with TypeScript

---

**Note**: This guide is updated regularly as TypeScript best practices evolve. Always refer to the official TypeScript documentation for the latest features and recommendations.
