/**
 * Users Test-Only API Module
 * 
 * Provides test-only user endpoints for development and testing purposes.
 * This module mirrors the backend user test router and provides endpoints
 * that should only be used in test/development environments.
 * 
 * ⚠️ **WARNING: TEST/DEVELOPMENT ONLY**
 * These endpoints should NEVER be enabled in production environments.
 * They provide privileged access for testing purposes only.
 * 
 * ## Endpoints
 * - `GET /users/test-alive` - Test endpoint availability
 * - `POST /users/test-create` - Create test user without validation
 * - `DELETE /users/test-delete-all` - Delete all users (DANGEROUS)
 * - `GET /users/test-count` - Get user count for testing
 * 
 * ## Usage
 * 
 * ### Test Endpoint Availability
 * ```typescript
 * import { usersTestOnlyApi } from '@/lib/api';
 * 
 * // Check if test endpoints are available
 * try {
 *   const status = await usersTestOnlyApi.testAlive();
 *   console.log('Test endpoints status:', status.status);
 * } catch (error) {
 *   console.log('Test endpoints not available (good for production)');
 * }
 * ```
 * 
 * ### Create Test User
 * ```typescript
 * // ⚠️ TEST ONLY - Bypasses normal validation
 * try {
 *   const testUser = await usersTestOnlyApi.createTestUser({
 *     email: 'test@example.com',
 *     name: 'Test User',
 *     password: 'testpass123'
 *   });
 *   console.log('Test user created:', testUser);
 * } catch (error) {
 *   console.error('Test user creation failed:', error.message);
 * }
 * ```
 * 
 * ### Get User Count (Testing)
 * ```typescript
 * try {
 *   const count = await usersTestOnlyApi.getUserCount();
 *   console.log('Total users for testing:', count.total);
 * } catch (error) {
 *   console.error('Could not get user count:', error.message);
 * }
 * ```
 * 
 * ### Delete All Users (VERY DANGEROUS)
 * ```typescript
 * // ⚠️ EXTREMELY DANGEROUS - Only for test cleanup
 * if (process.env.NODE_ENV === 'test') {
 *   try {
 *     await usersTestOnlyApi.deleteAllUsers();
 *     console.log('All test users deleted');
 *   } catch (error) {
 *     console.error('Failed to delete test users:', error.message);
 *   }
 * } else {
 *   throw new Error('deleteAllUsers should never be called outside tests!');
 * }
 * ```
 * 
 * ## Environment Guards
 * Always check the environment before using these endpoints:
 * ```typescript
 * const isTestEnvironment = process.env.NODE_ENV === 'test' || 
 *                          process.env.NODE_ENV === 'development';
 * 
 * if (!isTestEnvironment) {
 *   throw new Error('Test-only endpoints should not be used in production');
 * }
 * ```
 * 
 * ## Test Scenarios
 * These endpoints are useful for:
 * - Integration test setup and teardown
 * - Development environment seeding
 * - API endpoint testing
 * - Performance testing with known data
 * - Test isolation and cleanup
 * 
 * ## Security Warnings
 * - ⚠️ These endpoints bypass normal security checks
 * - ⚠️ They can delete all user data
 * - ⚠️ They should be disabled in production
 * - ⚠️ Access should be restricted to test environments only
 * 
 * ## Production Safety
 * In production deployments:
 * - These endpoints should return 404 or be completely disabled
 * - Environment variables should prevent their activation
 * - Consider removing this module entirely for production builds
 * 
 * @see backend/src/api/v1/users/test_only_router.py for corresponding backend implementation
 */

// User test-only API functions (TEST/DEVELOPMENT ONLY)
// Mirrors backend/src/api/v1/users/test_only_router.py

import logger from '@/logger';
import { request } from '../base';

// Types that match the backend
interface PromoteAdminResponse {
    detail: string;
}

interface PromoteAdminRequest {
    email: string;
}

export const usersTestOnlyApi = {
    // Promote a user to admin by email (test mode only)
    promoteUserToAdmin: async (email: string): Promise<PromoteAdminResponse> => {
        logger.info('Promoting user to admin', { email });
        const response = await request<PromoteAdminResponse>('/users/promote-admin', {
            method: 'POST',
            data: { email },
        });

        if (response.error) {
            logger.warn('Failed to promote user to admin', { error: response.error, email });
            throw new Error(response.error);
        }

        logger.info('User promoted to admin successfully', { email });
        return response.data!;
    },
};
