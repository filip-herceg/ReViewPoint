import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore, getToken } from "@/lib/store/authStore";
import { createTestError, createAuthTokens } from "../test-templates";
import type { User } from "@/lib/api/types";

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
    expect(() => useAuthStore.getState().login(null as any, tokens)).toThrow(
      /user and tokens required/i,
    );
  });

  it("throws if login called with missing token", () => {
    expect(() => useAuthStore.getState().login(user, null as any)).toThrow(
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
