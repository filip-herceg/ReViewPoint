/**
 * Enhanced Auth Store Tests
 *
 * Tests for the enhanced auth store functionality including:
 * - Token management
 * - Refresh state tracking
 * - Enhanced login/logout logic
 * - Error handling
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { getRefreshToken, getToken, useAuthStore } from "@/lib/store/authStore";
import { createValidAuthTokens } from "../../test-templates";
import { testLogger } from "../../test-utils";

// Helper to create AuthUser compatible with the store
function createStoreAuthUser() {
	return {
		id: `user_${Math.floor(Math.random() * 10000)}`,
		email: `user${Math.floor(Math.random() * 1000)}@example.com`,
		name: `User ${Math.floor(Math.random() * 1000)}`,
		roles: ["user"],
	};
}

// Helper to create AuthTokens compatible with the store
function createStoreAuthTokens() {
	const tokens = createValidAuthTokens();
	return {
		...tokens,
		expires_in: 3600,
	};
}

// Mock logger to prevent console output during tests
vi.mock("@/logger", () => ({
	default: {
		info: vi.fn(),
		debug: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	},
}));

describe("Enhanced Auth Store", () => {
	beforeEach(() => {
		testLogger.info("Setting up auth store test");

		// Reset store state
		useAuthStore.setState({
			user: null,
			tokens: null,
			isAuthenticated: false,
			isRefreshing: false,
		});

		vi.clearAllMocks();
	});

	describe("Login Functionality", () => {
		it("should login user with valid data", () => {
			testLogger.info("Testing user login with valid data");

			const user = createStoreAuthUser();
			const tokens = createStoreAuthTokens();

			const authStore = useAuthStore.getState();
			authStore.login(user, tokens);

			const state = useAuthStore.getState();
			expect(state.user).toEqual(user);
			expect(state.tokens).toEqual(tokens);
			expect(state.isAuthenticated).toBe(true);
			expect(state.isRefreshing).toBe(false);

			testLogger.debug("User login test passed", {
				userId: user.id,
				email: user.email,
			});
		});

		it("should throw error for invalid user data", () => {
			testLogger.info("Testing login with invalid user data");

			const tokens = createStoreAuthTokens();
			const authStore = useAuthStore.getState();

			expect(() => authStore.login(null as unknown, tokens)).toThrow(
				"User and tokens required for login",
			);

			// Store should remain unchanged
			const state = useAuthStore.getState();
			expect(state.user).toBeNull();
			expect(state.tokens).toBeNull();
			expect(state.isAuthenticated).toBe(false);

			testLogger.debug("Invalid user login test passed");
		});

		it("should throw error for invalid tokens", () => {
			testLogger.info("Testing login with invalid tokens");

			const user = createStoreAuthUser();
			const authStore = useAuthStore.getState();

			expect(() => authStore.login(user, null as unknown)).toThrow(
				"User and tokens required for login",
			);

			// Store should remain unchanged
			const state = useAuthStore.getState();
			expect(state.user).toBeNull();
			expect(state.tokens).toBeNull();
			expect(state.isAuthenticated).toBe(false);

			testLogger.debug("Invalid tokens login test passed");
		});
	});

	describe("Logout Functionality", () => {
		it("should logout correctly", () => {
			testLogger.info("Testing logout flow");

			const user = createStoreAuthUser();
			const tokens = createStoreAuthTokens();			// First login
			const authStore = useAuthStore.getState();
			authStore.login(user, tokens);

			// Verify logged in
			expect(useAuthStore.getState().isAuthenticated).toBe(true);

			// Now logout
			authStore.logout();

			const state = useAuthStore.getState();
			expect(state.user).toBeNull();
			expect(state.tokens).toBeNull();
			expect(state.isAuthenticated).toBe(false);
			expect(state.isRefreshing).toBe(false);

			testLogger.debug("User logout test passed");
		});
	});

	describe("Token Management", () => {
		it("should set tokens with valid data", () => {
			testLogger.info("Testing token setting with valid data");

			const tokens = createStoreAuthTokens();
			const authStore = useAuthStore.getState();

			authStore.setTokens(tokens);

			const state = useAuthStore.getState();
			expect(state.tokens).toEqual(tokens);
			expect(state.isAuthenticated).toBe(true);

			testLogger.debug("Set tokens test passed");
		});

		it("should throw error for invalid tokens", () => {
			testLogger.info("Testing token setting with invalid data");

			const authStore = useAuthStore.getState();

			expect(() => authStore.setTokens(null as unknown)).toThrow(
				"Invalid tokens provided",
			);
			expect(() =>
				authStore.setTokens({
					access_token: "",
					refresh_token: "test",
					token_type: "bearer",
					expires_in: 3600,
				}),
			).toThrow("Invalid tokens provided");

			// Store should remain unchanged
			const state = useAuthStore.getState();
			expect(state.tokens).toBeNull();
			expect(state.isAuthenticated).toBe(false);

			testLogger.debug("Invalid tokens setting test passed");
		});

		it("should clear tokens", () => {
			testLogger.info("Testing token clearing");

			const tokens = createStoreAuthTokens();
			const authStore = useAuthStore.getState();

			// First set tokens
			authStore.setTokens(tokens);
			expect(useAuthStore.getState().isAuthenticated).toBe(true);

			// Now clear
			authStore.clearTokens();

			const state = useAuthStore.getState();
			expect(state.tokens).toBeNull();
			expect(state.isAuthenticated).toBe(false);

			testLogger.debug("Clear tokens test passed");
		});
	});

	describe("Refresh State Management", () => {
		it("should set refreshing state", () => {
			testLogger.info("Testing refresh state setting");

			const authStore = useAuthStore.getState();

			authStore.setRefreshing(true);
			expect(useAuthStore.getState().isRefreshing).toBe(true);

			authStore.setRefreshing(false);
			expect(useAuthStore.getState().isRefreshing).toBe(false);

			testLogger.debug("Refresh state setting test passed");
		});
	});

	describe("Token Utility Functions", () => {
		it("should get current access token", () => {
			testLogger.info("Testing access token utility");

			const tokens = createStoreAuthTokens();
			useAuthStore.setState({ tokens, isAuthenticated: true });

			const accessToken = getToken();
			expect(accessToken).toBe(tokens.access_token);

			testLogger.debug("Access token utility test passed");
		});

		it("should get current refresh token", () => {
			testLogger.info("Testing refresh token utility");

			const tokens = createStoreAuthTokens();
			useAuthStore.setState({ tokens, isAuthenticated: true });

			const refreshToken = getRefreshToken();
			expect(refreshToken).toBe(tokens.refresh_token);

			testLogger.debug("Refresh token utility test passed");
		});

		it("should return undefined when no tokens available", () => {
			testLogger.info("Testing token utilities with no tokens");

			useAuthStore.setState({ tokens: null, isAuthenticated: false });

			const accessToken = getToken();
			const refreshToken = getRefreshToken();

			expect(accessToken).toBeUndefined();
			expect(refreshToken).toBeUndefined();

			testLogger.debug("No tokens utility test passed");
		});
	});

	describe("State Consistency", () => {
		it("should maintain consistent state during login", () => {
			testLogger.info("Testing state consistency during login");

			const user = createStoreAuthUser();
			const tokens = createStoreAuthTokens();

			const authStore = useAuthStore.getState();
			authStore.login(user, tokens);

			const state = useAuthStore.getState();

			// All related fields should be consistent
			expect(state.isAuthenticated).toBe(true);
			expect(state.user).toBeTruthy();
			expect(state.tokens).toBeTruthy();
			expect(state.isRefreshing).toBe(false);

			testLogger.debug("Login state consistency test passed");
		});

		it("should maintain consistent state during logout", () => {
			testLogger.info("Testing state consistency during logout");

			const user = createStoreAuthUser();
			const tokens = createStoreAuthTokens();

			// First login
			const authStore = useAuthStore.getState();
			authStore.login(user, tokens);

			// Then logout
			authStore.logout();

			const state = useAuthStore.getState();

			// All related fields should be reset
			expect(state.isAuthenticated).toBe(false);
			expect(state.user).toBeNull();
			expect(state.tokens).toBeNull();
			expect(state.isRefreshing).toBe(false);

			testLogger.debug("Logout state consistency test passed");
		});

		it("should maintain consistent state during token operations", () => {
			testLogger.info("Testing state consistency during token operations");

			const tokens = createStoreAuthTokens();
			const authStore = useAuthStore.getState();

			// Set tokens
			authStore.setTokens(tokens);
			let state = useAuthStore.getState();
			expect(state.isAuthenticated).toBe(true);
			expect(state.tokens).toBeTruthy();

			// Clear tokens
			authStore.clearTokens();
			state = useAuthStore.getState();
			expect(state.isAuthenticated).toBe(false);
			expect(state.tokens).toBeNull();

			testLogger.debug("Token operations state consistency test passed");
		});
	});
});
