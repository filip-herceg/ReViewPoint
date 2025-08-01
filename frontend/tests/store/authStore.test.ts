import { beforeEach, describe, expect, it } from "vitest";
import type { User } from "@/lib/api/types";
import { getToken, useAuthStore } from "@/lib/store/authStore";
import { createAuthTokens } from "../test-templates";

// Create a test user using the new API User type
const user: User = {
	id: 1,
	email: "test@example.com",
	name: "Test User",
	bio: null,
	avatar_url: null,
	created_at: "2025-01-01T00:00:00Z",
	updated_at: "2025-01-01T00:00:00Z",
};
const tokens = createAuthTokens();

describe("authStore error handling", () => {
	beforeEach(() => {
		useAuthStore.setState({ user: null, tokens: null, isAuthenticated: false });
	});

	it("throws if login called with missing user", () => {
		expect(() => useAuthStore.getState().login(null as never, tokens)).toThrow(
			/user and tokens required/i,
		);
	});

	it("throws if login called with missing token", () => {
		expect(() => useAuthStore.getState().login(user, null as never)).toThrow(
			/user and tokens required/i,
		);
	});

	it("sets user, token, isAuthenticated on successful login", () => {
		useAuthStore.getState().login(user, tokens);
		const state = useAuthStore.getState();
		expect(state.user).toEqual(user);
		expect(state.tokens).toEqual(tokens);
		expect(state.isAuthenticated).toBe(true);
	});

	it("clears user, token, isAuthenticated on logout", () => {
		useAuthStore.getState().login(user, tokens);
		useAuthStore.getState().logout();
		const state = useAuthStore.getState();
		expect(state.user).toBeNull();
		expect(state.tokens).toBeNull();
		expect(state.isAuthenticated).toBe(false);
	});

	it("getToken returns current token", () => {
		useAuthStore.getState().login(user, tokens);
		expect(getToken()).toBe(tokens.access_token);

		useAuthStore.getState().logout();
		expect(getToken()).toBeUndefined();
	});
});
