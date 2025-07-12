// User test-only API functions
// Mirrors backend/src/api/v1/users/test_only_router.py

import logger from "@/logger";
import { request } from "../base";

export const usersTestOnlyApi = {
  // Test Utilities (only available in test/development mode)

  // Admin Promotion (Test only)
  promoteUserToAdmin: async (email: string) => {
    try {
      return await request<{ detail: string }>("/users/promote-admin", {
        method: "POST",
        data: { email },
      });
    } catch (err) {
      throw err;
    }
  },

  // Test Data Management
  createTestUser: async (userData?: {
    email?: string;
    password?: string;
    name?: string;
    is_admin?: boolean;
  }) => {
    try {
      const defaultData = {
        email: `test-user-${Date.now()}@example.com`,
        password: "test-password-123",
        name: "Test User",
        is_admin: false,
        ...userData,
      };

      return await request<{
        id: number;
        email: string;
        name: string;
        is_admin: boolean;
        created_at: string;
      }>("/users/test/create-user", {
        method: "POST",
        data: defaultData,
      });
    } catch (err) {
      throw err;
    }
  },

  createMultipleTestUsers: async (
    count: number = 5,
    baseData?: Partial<{
      email_prefix: string;
      password: string;
      name_prefix: string;
    }>,
  ) => {
    try {
      return await request<
        Array<{
          id: number;
          email: string;
          name: string;
          created_at: string;
        }>
      >("/users/test/create-multiple", {
        method: "POST",
        data: {
          count,
          ...baseData,
        },
      });
    } catch (err) {
      throw err;
    }
  },

  // Test Data Cleanup
  deleteAllTestUsers: async () => {
    try {
      return await request<{
        deleted_count: number;
        message: string;
      }>("/users/test/cleanup", {
        method: "DELETE",
      });
    } catch (err) {
      throw err;
    }
  },

  deleteTestUsersByPrefix: async (emailPrefix: string) => {
    try {
      return await request<{
        deleted_count: number;
        message: string;
      }>("/users/test/cleanup-by-prefix", {
        method: "DELETE",
        data: { email_prefix: emailPrefix },
      });
    } catch (err) {
      throw err;
    }
  },

  // Test Environment Info
  getTestEnvironmentInfo: async () => {
    try {
      return await request<{
        is_test_mode: boolean;
        environment: string;
        test_features_enabled: string[];
        test_user_count: number;
        last_cleanup: string | null;
      }>("/users/test/environment");
    } catch (err) {
      throw err;
    }
  },

  // Role and Permission Testing
  assignTestRole: async (userId: number, role: string) => {
    try {
      return await request<{
        user_id: number;
        role: string;
        assigned_at: string;
        message: string;
      }>(`/users/test/${userId}/assign-role`, {
        method: "POST",
        data: { role },
      });
    } catch (err) {
      throw err;
    }
  },

  removeTestRole: async (userId: number, role: string) => {
    try {
      return await request<{
        user_id: number;
        role: string;
        removed_at: string;
        message: string;
      }>(`/users/test/${userId}/remove-role`, {
        method: "DELETE",
        data: { role },
      });
    } catch (err) {
      throw err;
    }
  },

  // Test Data Population
  populateTestData: async (scenario: "basic" | "advanced" | "stress") => {
    try {
      return await request<{
        scenario: string;
        users_created: number;
        files_created: number;
        message: string;
        execution_time_ms: number;
      }>("/users/test/populate", {
        method: "POST",
        data: { scenario },
      });
    } catch (err) {
      throw err;
    }
  },

  // Test Authentication
  generateTestToken: async (userId: number, expirationMinutes?: number) => {
    try {
      return await request<{
        access_token: string;
        token_type: string;
        expires_in: number;
        user_id: number;
      }>("/users/test/generate-token", {
        method: "POST",
        data: {
          user_id: userId,
          expiration_minutes: expirationMinutes || 60,
        },
      });
    } catch (err) {
      throw err;
    }
  },

  validateTestToken: async (token: string) => {
    try {
      return await request<{
        valid: boolean;
        user_id?: number;
        expires_at?: string;
        error?: string;
      }>("/users/test/validate-token", {
        method: "POST",
        data: { token },
      });
    } catch (err) {
      throw err;
    }
  },

  // Test Feature Flags
  enableTestFeature: async (featureName: string) => {
    try {
      return await request<{
        feature: string;
        enabled: boolean;
        message: string;
      }>("/users/test/features/enable", {
        method: "POST",
        data: { feature_name: featureName },
      });
    } catch (err) {
      throw err;
    }
  },

  disableTestFeature: async (featureName: string) => {
    try {
      return await request<{
        feature: string;
        enabled: boolean;
        message: string;
      }>("/users/test/features/disable", {
        method: "POST",
        data: { feature_name: featureName },
      });
    } catch (err) {
      throw err;
    }
  },

  getTestFeatureFlags: async () => {
    try {
      return await request<{
        features: Record<string, boolean>;
        environment: string;
        test_mode: boolean;
      }>("/users/test/features");
    } catch (err) {
      throw err;
    }
  },

  // Test Database Operations
  resetTestDatabase: async () => {
    try {
      return await request<{
        message: string;
        tables_reset: string[];
        execution_time_ms: number;
      }>("/users/test/database/reset", {
        method: "POST",
      });
    } catch (err) {
      throw err;
    }
  },

  getTestDatabaseStats: async () => {
    try {
      return await request<{
        total_users: number;
        test_users: number;
        total_files: number;
        test_files: number;
        database_size_mb: number;
        last_reset: string | null;
      }>("/users/test/database/stats");
    } catch (err) {
      throw err;
    }
  },
};

export default usersTestOnlyApi;
