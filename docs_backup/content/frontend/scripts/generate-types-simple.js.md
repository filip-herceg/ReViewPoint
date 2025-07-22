# Generate Types Simple Script

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Type**           | Node.js Script                                                    |
| **Responsibility** | Generate TypeScript types from OpenAPI schema                     |
| **Status**         | 🟢 Active                                                          |

## 1. Purpose

This script generates TypeScript types from the backend OpenAPI schema for frontend API client usage. It provides a simplified, focused approach to type generation without complex configuration.

## 2. Usage

```bash
# Generate types from schema
cd frontend
node generate-types-simple.js

# As part of build process  
npm run generate:types
pnpm run generate:types
```

## 3. Configuration

### Input/Output
- **Input**: `openapi-schema.json` (from backend schema export)
- **Output Directory**: `src/lib/api/generated/`
- **Output File**: `src/lib/api/generated/schema.ts`

### Dependencies
- **openapi-typescript**: Core type generation library
- **fs/promises**: File system operations
- **path**: Path manipulation utilities

## 4. Generated Output

The script generates TypeScript interfaces and types for:

### API Schemas
```typescript
// User model types
interface User {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
}

// Request/Response types
interface CreateUserRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
```

### Path Operations
```typescript
// API endpoint types
interface paths {
  "/api/v1/users/me": {
    get: operations["get_current_user"];
    patch: operations["update_current_user"];
  };
  "/api/v1/auth/login": {
    post: operations["login_user"];
  };
}
```

## 5. Integration

### Frontend Usage
```typescript
import type { User, LoginResponse } from '@/lib/api/generated/schema';

// Type-safe API calls
const user: User = await apiClient.getCurrentUser();
const loginResult: LoginResponse = await apiClient.login(credentials);
```

### Build Process
- Automatically run during frontend build
- Triggered by schema changes
- Validates type compatibility

## 6. Error Handling

### Common Issues
- **Missing Schema**: Ensures `openapi-schema.json` exists
- **Output Directory**: Creates output directory automatically
- **Type Conflicts**: Handles overlapping type definitions

### Debugging
```bash
# Verbose output
DEBUG=1 node generate-types-simple.js

# Check generated types
cat src/lib/api/generated/schema.ts
```

## 7. Workflow Integration

### Development Workflow
1. Backend changes API schema
2. Export schema with `export-backend-schema.py`
3. Run this script to regenerate frontend types
4. Frontend code uses updated types

### CI/CD Integration
```yaml
- name: Generate API Types
  run: |
    cd frontend
    node generate-types-simple.js
    
- name: Verify Types
  run: |
    cd frontend
    npm run type-check
```

## 8. Related Files

- [Export Backend Schema](../../scripts/export-backend-schema.py.md) - Generates the input schema
- [API Reference](../../api-reference.md) - Complete API documentation
- [Frontend Type Safety](../docs/type-safety.md) - Type usage guidelines

## 9. Maintenance

### Schema Updates
- Re-run when backend API changes
- Validate generated types compile
- Update API client code as needed

### Version Compatibility
- Supports OpenAPI 3.x schemas
- Compatible with TypeScript 4.x+
- Works with Node.js 16+
