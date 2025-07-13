# Frontend API Structure

This directory contains the frontend API modules that mirror the backend API structure with 1:1 mapping.

## Structure Overview

```
frontend/src/lib/api/
├── auth.ts              # Maps to backend/src/api/v1/auth.py
├── health.ts            # Maps to backend/src/api/v1/health.py
├── uploads.ts           # Maps to backend/src/api/v1/uploads.py
├── users/               # Maps to backend/src/api/v1/users/
│   ├── core.ts          # Maps to backend/src/api/v1/users/core.py
│   ├── exports.ts       # Maps to backend/src/api/v1/users/exports.py
│   ├── testOnly.ts      # Maps to backend/src/api/v1/users/test_only_router.py
│   └── index.ts         # Combines all user APIs
├── base.ts              # Shared request logic (axios client, interceptors)
├── errorHandling.ts     # Centralized error handling
├── index.ts             # Main API export with structured & legacy APIs
├── upload.queries.ts    # React Query hooks for uploads
└── types/               # Type definitions
    ├── auth.ts          # Authentication types
    ├── common.ts        # Shared API types (ApiResponse, etc.)
    ├── upload.ts        # Upload/file types
    ├── user.ts          # User types
    └── index.ts         # Central type exports
```

## Design Principles

1. **1:1 Backend Mapping**: Each frontend API module directly corresponds to a backend API module
2. **DRY (Don't Repeat Yourself)**:
   - Shared request logic in `base.ts`
   - Centralized error handling
   - Removed redundant try/catch blocks
   - Used object spread for legacy API construction
3. **Type Safety**: Full TypeScript support with comprehensive type definitions
4. **Backwards Compatibility**: Legacy API object maintains old interface while using new modular structure
5. **Separation of Concerns**:
   - Pure API functions in modules
   - React Query hooks separated in `upload.queries.ts`
   - Types organized by domain

## Usage

### New Structured Approach (Recommended)

```typescript
import { authApi, uploadsApi, usersApi, healthApi } from "@/lib/api";
// or
import { structuredApi } from "@/lib/api";
const { auth, uploads, users, health } = structuredApi;
```

### Legacy Approach (Backwards Compatible)

```typescript
import api from "@/lib/api";
// All methods available at top level like before
```

## Benefits

- **Maintainability**: Clear module boundaries matching backend
- **Scalability**: Easy to add new API endpoints by extending appropriate modules
- **Type Safety**: Comprehensive TypeScript coverage
- **Performance**: Shared axios client with request/response interceptors
- **Developer Experience**: Auto-completion and IntelliSense support
- **Testing**: Modular structure makes mocking and testing easier
