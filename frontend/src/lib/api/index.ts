/**
 * API Module - Main Entry Point
 *
 * This module provides a comprehensive API interface for the ReViewPoint application.
 * It mirrors the backend API structure with a 1:1 mapping for consistency and maintainability.
 *
 * ## Structure
 * The API is organized into modules that correspond to backend router files:
 * - `auth` - Authentication and authorization endpoints
 * - `health` - Health check and system status endpoints
 * - `uploads` - File upload and management endpoints
 * - `users` - User management endpoints (core, exports, test-only)
 *
 * ## Usage
 *
 * ### Named Exports (Recommended)
 * ```typescript
 * import { authApi, usersApi, uploadsApi, healthApi } from '@/lib/api';
 *
 * // Authentication
 * const user = await authApi.login({ email, password });
 * const current = await authApi.getCurrentUser();
 *
 * // User management
 * const users = await usersApi.core.listUsers();
 * const user = await usersApi.core.createUser(userData);
 *
 * // File uploads
 * const files = await uploadsApi.listFiles();
 * const result = await uploadsApi.uploadFile(file);
 *
 * // Health checks
 * const status = await healthApi.getHealthStatus();
 * ```
 *
 * ### Default Export (Backwards Compatibility)
 * ```typescript
 * import api from '@/lib/api';
 *
 * // All APIs are available as flat methods
 * const user = await api.login({ email, password });
 * const files = await api.listFiles();
 * ```
 *
 * ## Error Handling
 * All API functions use consistent error handling:
 * - Throw errors for failed requests
 * - Log appropriate messages for debugging
 * - Return typed responses for successful requests
 *
 * ## Type Safety
 * All API functions are fully typed with interfaces that match the backend schemas.
 * Import types from '@/lib/api/types' for additional type definitions.
 *
 * @example
 * ```typescript
 * import { authApi } from '@/lib/api';
 * import type { User, AuthTokens } from '@/lib/api/types';
 *
 * const handleLogin = async (credentials: LoginCredentials): Promise<User> => {
 *   try {
 *     const response = await authApi.login(credentials);
 *     return response.user;
 *   } catch (error) {
 *     console.error('Login failed:', error.message);
 *     throw error;
 *   }
 * };
 * ```
 */

// Main API exports
// This provides a clean structure mirroring the backend API organization

export { authApi } from "./auth";
export { healthApi } from "./health";
export { uploadsApi } from "./uploads";

// Type-safe generated API clients
export { uploadApiClient } from "./clients/uploads";
export { generatedApiClient } from "./generated/client";

// Users sub-module exports
export { usersCoreApi } from "./users/core";
export { usersExportsApi } from "./users/exports";
export { usersTestOnlyApi } from "./users/test_only_router";
export { usersApi } from "./users";

// Re-export base utilities
export { request } from "./base";

// Legacy exports for backwards compatibility
export { createUpload } from "./uploads";

// Create a default export for backwards compatibility
import { authApi } from "./auth";
import { healthApi } from "./health";
import { uploadsApi, createUpload } from "./uploads";
import { usersApi } from "./users";

const api = {
  ...authApi,
  ...uploadsApi,
  ...usersApi,
  ...healthApi,
  createUpload,
};

export default api;
