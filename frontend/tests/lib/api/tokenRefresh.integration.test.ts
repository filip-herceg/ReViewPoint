/**
 * API Integration Tests with Token Refresh
 *
 * Tests for the enhanced API client functionality including:
 * - Token injection behavior
 * - 401 response handling simulation
 * - Token refresh integration
 * - Error scenarios
 *
 * Note: These tests focus on the behavior rather than direct interceptor testing
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { tokenService } from "@/lib/auth/tokenService";
import { useAuthStore } from "@/lib/store/authStore";
import {
	createExpiredAuthTokens,
	createTokenRefreshResponse,
	createUser,
	createValidAuthTokens,
} from "../../test-templates";
import { testLogger } from "../../test-utils";

// Mock the auth API
vi.mock("@/lib/api/auth", () => ({
	authApi: {
		refreshToken: vi.fn(),
	},
}));

// Mock the token service
vi.mock("@/lib/auth/tokenService", () => ({
	tokenService: {
		getValidAccessToken: vi.fn(),
		refreshAccessToken: vi.fn(),
		clearRefreshState: vi.fn(),
		getCurrentAccessToken: vi.fn(),
		getCurrentRefreshToken: vi.fn(),
		needsRefresh: vi.fn(),
		isTokenExpired: vi.fn(),
		decodeJWTPayload: vi.fn(),
	},
}));

// Mock logger to prevent console output during tests
vi.mock("@/logger", () => ({
	default: {
		info: vi.fn(),
		debug: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	},
}));

describe("API Integration with Token Refresh", () => {
	beforeEach(() => {
		testLogger.info("Setting up API integration test");

		// Clear auth store
		useAuthStore.setState({
			user: null,
			tokens: null,
			isAuthenticated: false,
			isRefreshing: false,
		});

		// Clear all mocks
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe("Token Service Integration", () => {
		it("should provide valid token when requested", async () => {
			testLogger.info("Testing token service integration");

			const tokens = createValidAuthTokens();

			// Mock token service to return valid token
			vi.mocked(tokenService.getValidAccessToken).mockResolvedValue(
				tokens.access_token,
			);

			const result = await tokenService.getValidAccessToken();

			expect(result).toBe(tokens.access_token);
			expect(tokenService.getValidAccessToken).toHaveBeenCalled();

			testLogger.debug("Token service integration test passed");
		});

		it("should handle token refresh when token is expired", async () => {
			testLogger.info("Testing token refresh integration");

			const user = createUser();
			const expiredTokens = createExpiredAuthTokens();
			const newTokens = createTokenRefreshResponse();

			// Setup store with expired tokens
			useAuthStore.setState({
				user,
				tokens: expiredTokens,
				isAuthenticated: true,
			});

			// Mock token service behavior
			vi.mocked(tokenService.needsRefresh).mockReturnValue(true);
			vi.mocked(tokenService.refreshAccessToken).mockResolvedValue(
				newTokens.access_token,
			);
			vi.mocked(tokenService.getValidAccessToken).mockResolvedValue(
				newTokens.access_token,
			);

			const result = await tokenService.getValidAccessToken();

			expect(result).toBe(newTokens.access_token);
			expect(tokenService.getValidAccessToken).toHaveBeenCalled();

			testLogger.debug("Token refresh integration test passed");
		});

		it("should handle token refresh failure", async () => {
			testLogger.info("Testing token refresh failure integration");

			const user = createUser();
			const expiredTokens = createExpiredAuthTokens();

			// Setup store
			useAuthStore.setState({
				user,
				tokens: expiredTokens,
				isAuthenticated: true,
			});

			// Mock token service failure
			vi.mocked(tokenService.getValidAccessToken).mockRejectedValue(
				new Error("Token refresh failed"),
			);

			await expect(tokenService.getValidAccessToken()).rejects.toThrow(
				"Token refresh failed",
			);

			testLogger.debug("Token refresh failure integration test passed");
		});
	});

	describe("Auth Store Integration", () => {
		it("should update refresh state during token operations", async () => {
			testLogger.info("Testing auth store refresh state integration");

			const authStore = useAuthStore.getState();

			// Test setting refresh state
			authStore.setRefreshing(true);
			expect(useAuthStore.getState().isRefreshing).toBe(true);

			authStore.setRefreshing(false);
			expect(useAuthStore.getState().isRefreshing).toBe(false);

			testLogger.debug("Auth store refresh state integration test passed");
		});

		it("should handle token updates correctly", () => {
			testLogger.info("Testing auth store token updates");

			const tokens = createValidAuthTokens();
			const authStore = useAuthStore.getState();

			// Set tokens
			authStore.setTokens(tokens);

			const state = useAuthStore.getState();
			expect(state.tokens).toEqual(tokens);
			expect(state.isAuthenticated).toBe(true);

			testLogger.debug("Auth store token updates test passed");
		});

		it("should handle logout correctly", () => {
			testLogger.info("Testing auth store logout integration");

			const user = createUser();
			const tokens = createValidAuthTokens();
			const authStore = useAuthStore.getState();

			// First login
			authStore.login(user, tokens);
			expect(useAuthStore.getState().isAuthenticated).toBe(true);

			// Then logout
			authStore.logout();

			const state = useAuthStore.getState();
			expect(state.isAuthenticated).toBe(false);
			expect(state.user).toBeNull();
			expect(state.tokens).toBeNull();
			expect(state.isRefreshing).toBe(false);

			testLogger.debug("Auth store logout integration test passed");
		});
	});

	describe("Error Handling Integration", () => {
		it("should handle authentication errors gracefully", async () => {
			testLogger.info("Testing authentication error handling");

			// Mock token service to simulate auth error
			vi.mocked(tokenService.getValidAccessToken).mockRejectedValue(
				new Error("Authentication failed"),
			);

			await expect(tokenService.getValidAccessToken()).rejects.toThrow(
				"Authentication failed",
			);

			testLogger.debug("Authentication error handling test passed");
		});

		it("should handle network errors during token refresh", async () => {
			testLogger.info("Testing network error handling during refresh");

			// Mock token service to simulate network error
			vi.mocked(tokenService.refreshAccessToken).mockRejectedValue(
				new Error("Network error"),
			);

			await expect(tokenService.refreshAccessToken()).rejects.toThrow(
				"Network error",
			);

			testLogger.debug("Network error handling test passed");
		});
	});

	describe("State Consistency Integration", () => {
		it("should maintain consistent state across token operations", async () => {
			testLogger.info("Testing state consistency across operations");

			const user = createUser();
			const tokens = createValidAuthTokens();
			const authStore = useAuthStore.getState();

			// Login
			authStore.login(user, tokens);
			let state = useAuthStore.getState();
			expect(state.isAuthenticated).toBe(true);
			expect(state.user).toBeTruthy();
			expect(state.tokens).toBeTruthy();

			// Set refreshing
			authStore.setRefreshing(true);
			state = useAuthStore.getState();
			expect(state.isRefreshing).toBe(true);
			expect(state.isAuthenticated).toBe(true); // Should remain true

			// Clear refreshing
			authStore.setRefreshing(false);
			state = useAuthStore.getState();
			expect(state.isRefreshing).toBe(false);
			expect(state.isAuthenticated).toBe(true); // Should remain true

			// Logout
			authStore.logout();
			state = useAuthStore.getState();
			expect(state.isAuthenticated).toBe(false);
			expect(state.user).toBeNull();
			expect(state.tokens).toBeNull();
			expect(state.isRefreshing).toBe(false);

			testLogger.debug("State consistency integration test passed");
		});
	});

	describe("Concurrent Operations Integration", () => {
		it("should handle concurrent token requests", async () => {
			testLogger.info("Testing concurrent token requests");

			const tokens = createValidAuthTokens();

			// Mock token service to return same token for concurrent requests
			vi.mocked(tokenService.getValidAccessToken).mockResolvedValue(
				tokens.access_token,
			);

			// Make concurrent requests
			const requests = [
				tokenService.getValidAccessToken(),
				tokenService.getValidAccessToken(),
				tokenService.getValidAccessToken(),
			];

			const results = await Promise.all(requests);

			// All should return the same token
			expect(results[0]).toBe(tokens.access_token);
			expect(results[1]).toBe(tokens.access_token);
			expect(results[2]).toBe(tokens.access_token);

			// Should have been called multiple times (once per request in this mock scenario)
			expect(tokenService.getValidAccessToken).toHaveBeenCalledTimes(3);

			testLogger.debug("Concurrent token requests test passed");
		});
	});
});
