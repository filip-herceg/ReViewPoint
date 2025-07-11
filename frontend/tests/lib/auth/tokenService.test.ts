/**
 * Token Service Tests
 * 
 * Comprehensive tests for JWT token refresh functionality including:
 * - Token expiration detection
 * - Token refresh logic
 * - Concurrent request handling
 * - Error scenarios
 * - Auth store integration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { tokenService, TokenService } from '@/lib/auth/tokenService';
import { useAuthStore } from '@/lib/store/authStore';
import { authApi } from '@/lib/api/auth';
import {
    createValidAuthTokens,
    createExpiredAuthTokens,
    createSoonToExpireAuthTokens,
    createTokenRefreshResponse,
    createUser,
    createTokenServiceMockState,
} from '../../test-templates';
import { testLogger } from '../../test-utils';

// Mock the auth API
vi.mock('@/lib/api/auth', () => ({
    authApi: {
        refreshToken: vi.fn(),
    },
}));

// Mock logger to prevent console output during tests
vi.mock('@/logger', () => ({
    default: {
        info: vi.fn(),
        debug: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
    },
}));

describe('TokenService', () => {
    let mockTokenService: TokenService;

    beforeEach(() => {
        testLogger.info('Setting up TokenService test');

        // Clear auth store
        useAuthStore.setState({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isRefreshing: false
        });

        // Clear all mocks
        vi.clearAllMocks();

        // Create fresh instance for each test
        mockTokenService = new TokenService();

        // Clear any existing refresh state
        tokenService.clearRefreshState();
    });

    afterEach(() => {
        vi.restoreAllMocks();
        tokenService.clearRefreshState();
    });

    describe('JWT Token Decoding', () => {
        it('should decode valid JWT token', () => {
            testLogger.info('Testing JWT token decoding');

            const validTokens = createValidAuthTokens();
            const payload = tokenService.decodeJWTPayload(validTokens.access_token);

            expect(payload).toBeTruthy();
            expect(payload?.sub).toMatch(/^\d+$/);
            expect(payload?.email).toMatch(/^user\w+@example\.com$/);
            expect(payload?.exp).toBeGreaterThan(Math.floor(Date.now() / 1000));
            expect(payload?.iss).toBe('reviewpoint');

            testLogger.debug('JWT decoding test passed', payload);
        });

        it('should return null for invalid JWT format', () => {
            testLogger.info('Testing invalid JWT format handling');

            const invalidToken = 'invalid.token';
            const payload = tokenService.decodeJWTPayload(invalidToken);

            expect(payload).toBeNull();

            testLogger.debug('Invalid JWT format test passed');
        });

        it('should return null for malformed JWT payload', () => {
            testLogger.info('Testing malformed JWT payload handling');

            const malformedToken = 'header.invalid-base64.signature';
            const payload = tokenService.decodeJWTPayload(malformedToken);

            expect(payload).toBeNull();

            testLogger.debug('Malformed JWT payload test passed');
        });
    });

    describe('Token Expiration Detection', () => {
        it('should detect expired tokens', () => {
            testLogger.info('Testing expired token detection');

            const expiredTokens = createExpiredAuthTokens();
            const isExpired = tokenService.isTokenExpired(expiredTokens.access_token);

            expect(isExpired).toBe(true);

            testLogger.debug('Expired token detection test passed');
        });

        it('should detect tokens expiring soon (within buffer)', () => {
            testLogger.info('Testing soon-to-expire token detection');

            const soonToExpireTokens = createSoonToExpireAuthTokens();
            const isExpired = tokenService.isTokenExpired(soonToExpireTokens.access_token);

            expect(isExpired).toBe(true); // Should be true due to buffer

            testLogger.debug('Soon-to-expire token detection test passed');
        });

        it('should not detect valid tokens as expired', () => {
            testLogger.info('Testing valid token detection');

            const validTokens = createValidAuthTokens();
            const isExpired = tokenService.isTokenExpired(validTokens.access_token);

            expect(isExpired).toBe(false);

            testLogger.debug('Valid token detection test passed');
        });
    });

    describe('Token Retrieval from Store', () => {
        it('should get current access token from store', () => {
            testLogger.info('Testing access token retrieval');

            const tokens = createValidAuthTokens();
            useAuthStore.setState({ tokens, isAuthenticated: true });

            const accessToken = tokenService.getCurrentAccessToken();

            expect(accessToken).toBe(tokens.access_token);

            testLogger.debug('Access token retrieval test passed');
        });

        it('should get current refresh token from store', () => {
            testLogger.info('Testing refresh token retrieval');

            const tokens = createValidAuthTokens();
            useAuthStore.setState({ tokens, isAuthenticated: true });

            const refreshToken = tokenService.getCurrentRefreshToken();

            expect(refreshToken).toBe(tokens.refresh_token);

            testLogger.debug('Refresh token retrieval test passed');
        });

        it('should return null when no tokens available', () => {
            testLogger.info('Testing token retrieval with no tokens');

            useAuthStore.setState({ tokens: null, isAuthenticated: false });

            const accessToken = tokenService.getCurrentAccessToken();
            const refreshToken = tokenService.getCurrentRefreshToken();

            expect(accessToken).toBeNull();
            expect(refreshToken).toBeNull();

            testLogger.debug('No tokens retrieval test passed');
        });
    });

    describe('Token Refresh Needs Assessment', () => {
        it('should indicate refresh needed for expired tokens', () => {
            testLogger.info('Testing refresh needs for expired tokens');

            const expiredTokens = createExpiredAuthTokens();
            useAuthStore.setState({ tokens: expiredTokens, isAuthenticated: true });

            const needsRefresh = tokenService.needsRefresh();

            expect(needsRefresh).toBe(true);

            testLogger.debug('Expired token refresh needs test passed');
        });

        it('should indicate refresh not needed for valid tokens', () => {
            testLogger.info('Testing refresh needs for valid tokens');

            const validTokens = createValidAuthTokens();
            useAuthStore.setState({ tokens: validTokens, isAuthenticated: true });

            const needsRefresh = tokenService.needsRefresh();

            expect(needsRefresh).toBe(false);

            testLogger.debug('Valid token refresh needs test passed');
        });

        it('should indicate refresh not needed when no tokens', () => {
            testLogger.info('Testing refresh needs with no tokens');

            useAuthStore.setState({ tokens: null, isAuthenticated: false });

            const needsRefresh = tokenService.needsRefresh();

            expect(needsRefresh).toBe(false);

            testLogger.debug('No tokens refresh needs test passed');
        });
    });

    describe('Token Refresh Process', () => {
        it('should successfully refresh tokens', async () => {
            testLogger.info('Testing successful token refresh');

            const user = createUser();
            const oldTokens = createExpiredAuthTokens();
            const newTokens = createTokenRefreshResponse();

            // Setup store with user and expired tokens
            useAuthStore.setState({
                user,
                tokens: oldTokens,
                isAuthenticated: true
            });

            // Mock API response
            vi.mocked(authApi.refreshToken).mockResolvedValue(newTokens);

            const newAccessToken = await tokenService.refreshAccessToken();

            expect(newAccessToken).toBe(newTokens.access_token);
            expect(authApi.refreshToken).toHaveBeenCalledWith(oldTokens.refresh_token);

            // Check store was updated
            const updatedState = useAuthStore.getState();
            expect(updatedState.tokens?.access_token).toBe(newTokens.access_token);
            expect(updatedState.tokens?.refresh_token).toBe(newTokens.refresh_token);

            testLogger.debug('Successful token refresh test passed');
        });

        it('should handle refresh failure', async () => {
            testLogger.info('Testing token refresh failure');

            const user = createUser();
            const oldTokens = createExpiredAuthTokens();

            useAuthStore.setState({
                user,
                tokens: oldTokens,
                isAuthenticated: true
            });

            const refreshError = new Error('Refresh token expired');
            vi.mocked(authApi.refreshToken).mockRejectedValue(refreshError);

            await expect(tokenService.refreshAccessToken()).rejects.toThrow('Refresh token expired');

            // Check user was logged out
            const updatedState = useAuthStore.getState();
            expect(updatedState.isAuthenticated).toBe(false);
            expect(updatedState.tokens).toBeNull();
            expect(updatedState.user).toBeNull();

            testLogger.debug('Token refresh failure test passed');
        });

        it('should handle missing refresh token', async () => {
            testLogger.info('Testing refresh with missing refresh token');

            useAuthStore.setState({
                tokens: null,
                isAuthenticated: false
            });

            await expect(tokenService.refreshAccessToken()).rejects.toThrow('No refresh token available');

            testLogger.debug('Missing refresh token test passed');
        });

        it('should handle concurrent refresh requests', async () => {
            testLogger.info('Testing concurrent token refresh requests');

            const user = createUser();
            const oldTokens = createExpiredAuthTokens();
            const newTokens = createTokenRefreshResponse();

            useAuthStore.setState({
                user,
                tokens: oldTokens,
                isAuthenticated: true
            });

            // Mock API with delay to simulate network
            vi.mocked(authApi.refreshToken).mockImplementation(
                () => new Promise(resolve => setTimeout(() => resolve(newTokens), 100))
            );

            // Start multiple concurrent refresh requests
            const refreshPromise1 = tokenService.refreshAccessToken();
            const refreshPromise2 = tokenService.refreshAccessToken();
            const refreshPromise3 = tokenService.refreshAccessToken();

            const results = await Promise.all([refreshPromise1, refreshPromise2, refreshPromise3]);

            // All should return the same new token
            expect(results[0]).toBe(newTokens.access_token);
            expect(results[1]).toBe(newTokens.access_token);
            expect(results[2]).toBe(newTokens.access_token);

            // API should only be called once
            expect(authApi.refreshToken).toHaveBeenCalledTimes(1);

            testLogger.debug('Concurrent refresh requests test passed');
        });
    });

    describe('Get Valid Access Token', () => {
        it('should return valid token without refresh', async () => {
            testLogger.info('Testing get valid token without refresh');

            const validTokens = createValidAuthTokens();
            useAuthStore.setState({ tokens: validTokens, isAuthenticated: true });

            const token = await tokenService.getValidAccessToken();

            expect(token).toBe(validTokens.access_token);
            expect(authApi.refreshToken).not.toHaveBeenCalled();

            testLogger.debug('Get valid token without refresh test passed');
        });

        it('should refresh and return new token when expired', async () => {
            testLogger.info('Testing get valid token with refresh');

            const user = createUser();
            const expiredTokens = createExpiredAuthTokens();
            const newTokens = createTokenRefreshResponse();

            useAuthStore.setState({
                user,
                tokens: expiredTokens,
                isAuthenticated: true
            });

            vi.mocked(authApi.refreshToken).mockResolvedValue(newTokens);

            const token = await tokenService.getValidAccessToken();

            expect(token).toBe(newTokens.access_token);
            expect(authApi.refreshToken).toHaveBeenCalledWith(expiredTokens.refresh_token);

            testLogger.debug('Get valid token with refresh test passed');
        });

        it('should return null when no tokens available', async () => {
            testLogger.info('Testing get valid token with no tokens');

            useAuthStore.setState({ tokens: null, isAuthenticated: false });

            const token = await tokenService.getValidAccessToken();

            expect(token).toBeNull();
            expect(authApi.refreshToken).not.toHaveBeenCalled();

            testLogger.debug('Get valid token with no tokens test passed');
        });

        it('should return null when refresh fails', async () => {
            testLogger.info('Testing get valid token with refresh failure');

            const user = createUser();
            const expiredTokens = createExpiredAuthTokens();

            useAuthStore.setState({
                user,
                tokens: expiredTokens,
                isAuthenticated: true
            });

            vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('Refresh failed'));

            const token = await tokenService.getValidAccessToken();

            expect(token).toBeNull();

            testLogger.debug('Get valid token with refresh failure test passed');
        });
    });

    describe('Refresh State Management', () => {
        it('should clear refresh state', () => {
            testLogger.info('Testing refresh state clearing');

            // Simulate some refresh state
            tokenService.clearRefreshState();

            // Test that no errors occur
            expect(() => tokenService.clearRefreshState()).not.toThrow();

            testLogger.debug('Refresh state clearing test passed');
        });
    });
});
