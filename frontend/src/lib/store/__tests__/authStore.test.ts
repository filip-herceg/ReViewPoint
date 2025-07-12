import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "../authStore";
import type { User, AuthTokens } from "@/lib/api/types";

// Helper to reset Zustand store state between tests
const resetAuthStore = () => {
  useAuthStore.setState({ user: null, tokens: null, isAuthenticated: false });
};

describe("authStore", () => {
  beforeEach(() => {
    resetAuthStore();
  });

  it("should have initial state", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.tokens).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it("should login and set user/tokens", () => {
    const user: User = {
      id: 1,
      email: "test@example.com",
      name: "Test User",
      bio: null,
      avatar_url: null,
      created_at: null,
      updated_at: null,
    };
    const tokens: AuthTokens = {
      access_token: "access123",
      refresh_token: "refresh123",
      token_type: "bearer",
    };
    useAuthStore.getState().login(user, tokens);
    const state = useAuthStore.getState();
    expect(state.user).toEqual(user);
    expect(state.tokens).toEqual(tokens);
    expect(state.isAuthenticated).toBe(true);
  });

  it("should logout and clear user/tokens", () => {
    const user: User = {
      id: 2,
      email: "test@example.com",
      name: "Test User",
      bio: null,
      avatar_url: null,
      created_at: null,
      updated_at: null,
    };
    const tokens: AuthTokens = {
      access_token: "access123",
      refresh_token: "refresh123",
      token_type: "bearer",
    };
    useAuthStore.getState().login(user, tokens);
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.tokens).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });
});
