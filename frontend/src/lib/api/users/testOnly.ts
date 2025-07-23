// User test-only API functions
// Mirrors backend/src/api/v1/users/test_only_router.py

import { request } from "../base";

export const usersTestOnlyApi = {
  // Test Utilities (only available in test/development mode)

  // Admin Promotion (Test only)
  promoteUserToAdmin: async (email: string) => {
    return await request<{ detail: string }>("/users/promote-admin", {
      method: "POST",
      data: { email },
    });
  },

  // Test Data Management
  createTestUser: async (userData?: {
    email?: string;
    password?: string;
    name?: string;
    is_admin?: boolean;
  }) => {
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
  },

  createMultipleTestUsers: async (
    count: number = 5,
    baseData?: Partial<{
      email_prefix: string;
      password: string;
      name_prefix: string;
    }>,
  ) => {
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
  },

  // Test Data Cleanup
  deleteAllTestUsers: async () => {
    return await request<{
      deleted_count: number;
      message: string;
    }>("/users/test/cleanup", {
      method: "DELETE",
    });
  },

  deleteTestUsersByPrefix: async (emailPrefix: string) => {
    return await request<{
      deleted_count: number;
      message: string;
    }>("/users/test/cleanup-by-prefix", {
      method: "DELETE",
      data: { email_prefix: emailPrefix },
    });
  },

  // Test Environment Info
  getTestEnvironmentInfo: async () => {
    return await request<{
      is_test_mode: boolean;
      environment: string;
      test_features_enabled: string[];
      test_user_count: number;
      last_cleanup: string | null;
    }>("/users/test/environment");
  },

  // Role and Permission Testing
  assignTestRole: async (userId: number, role: string) => {
    return await request<{
      user_id: number;
      role: string;
      assigned_at: string;
      message: string;
    }>(`/users/test/${userId}/assign-role`, {
      method: "POST",
      data: { role },
    });
  },

  removeTestRole: async (userId: number, role: string) => {
    return await request<{
      user_id: number;
      role: string;
      removed_at: string;
      message: string;
    }>(`/users/test/${userId}/remove-role`, {
      method: "DELETE",
      data: { role },
    });
  },

  // Test Data Population
  populateTestData: async (scenario: "basic" | "advanced" | "stress") => {
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
  },

  // Test Authentication
  generateTestToken: async (userId: number, expirationMinutes?: number) => {
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
  },

  validateTestToken: async (token: string) => {
    return await request<{
      valid: boolean;
      user_id?: number;
      expires_at?: string;
      error?: string;
    }>("/users/test/validate-token", {
      method: "POST",
      data: { token },
    });
  },

  // Test Feature Flags
  enableTestFeature: async (featureName: string) => {
    return await request<{
      feature: string;
      enabled: boolean;
      message: string;
    }>("/users/test/features/enable", {
      method: "POST",
      data: { feature_name: featureName },
    });
  },

  disableTestFeature: async (featureName: string) => {
    return await request<{
      feature: string;
      enabled: boolean;
      message: string;
    }>("/users/test/features/disable", {
      method: "POST",
      data: { feature_name: featureName },
    });
  },

  getTestFeatureFlags: async () => {
    return await request<{
      features: Record<string, boolean>;
      environment: string;
      test_mode: boolean;
    }>("/users/test/features");
  },

  // Test Database Operations
  resetTestDatabase: async () => {
    return await request<{
      message: string;
      tables_reset: string[];
      execution_time_ms: number;
    }>("/users/test/database/reset", {
      method: "POST",
    });
  },

  getTestDatabaseStats: async () => {
    return await request<{
      total_users: number;
      test_users: number;
      total_files: number;
      test_files: number;
      database_size_mb: number;
      last_reset: string | null;
    }>("/users/test/database/stats");
  },
};

export default usersTestOnlyApi;
