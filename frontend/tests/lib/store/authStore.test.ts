import { beforeEach, describe, expect, it } from "vitest";
import type { User } from "@/lib/api/types";
import { useAuthStore } from "@/lib/store/authStore";
import { createAuthTokens, createUser } from "../../test-templates";
import { testLogger } from "../../test-utils";

// Helper to reset Zustand store state between tests
const resetAuthStore = () => {
  testLogger.info("Resetting auth store state");
  useAuthStore.setState({ user: null, tokens: null, isAuthenticated: false });
};

describe("authStore", () => {
  beforeEach(() => {
    resetAuthStore();
  });

  it("should have initial state", () => {
    testLogger.info("Checking initial auth store state");
    const state = useAuthStore.getState();
    testLogger.debug("Initial state", state);
    expect(state.user).toBeNull();
    expect(state.tokens).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it("should login and set user/token", () => {
    testLogger.info("Testing login sets user and token");
    const user: User = createUser();
    const tokens = createAuthTokens();
    useAuthStore.getState().login(user, tokens);
    const state = useAuthStore.getState();
    testLogger.debug("State after login", state);
    expect(state.user).toEqual(user);
    expect(state.tokens).toEqual(tokens);
    expect(state.isAuthenticated).toBe(true);
  });

  it("should logout and clear user/token", () => {
    testLogger.info("Testing logout clears user and token");
    const user: User = createUser();
    const tokens = createAuthTokens();
    useAuthStore.getState().login(user, tokens);
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    testLogger.debug("State after logout", state);
    expect(state.user).toBeNull();
    expect(state.tokens).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });
});
