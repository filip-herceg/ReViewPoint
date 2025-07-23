/**
 * @file useAuth Hook Tests
 * @description Comprehensive test suite for the useAuth hook.
 * Tests all authentication operations, state management, and error handling.
 */

import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useAuth } from "@/hooks/useAuth";
import { authApi } from "@/lib/api/auth";
import type { AuthUser } from "@/lib/api/types";
import { extractUserFromToken } from "@/lib/api/types";
import { tokenService } from "@/lib/auth/tokenService";
import {
  createAuthError,
  createAuthLoginRequest,
  createAuthRegisterRequest,
  createAuthTokens,
  createUser,
} from "../test-templates";

// Helper function to create AuthUser from User
function createAuthUser(overrides: Partial<AuthUser> = {}): AuthUser {
  const defaultUser = createUser();
  return {
    id: String(defaultUser.id),
    email: defaultUser.email,
    name: defaultUser.name || undefined,
    roles: ["user"],
    ...overrides,
  };
}

// Mock dependencies
vi.mock("@/lib/api/auth");
vi.mock("@/lib/auth/tokenService");
vi.mock("@/lib/api/types");
vi.mock("react-router-dom", () => ({
  useNavigate: () => vi.fn(),
}));

const mockAuthApi = vi.mocked(authApi);
const mockTokenService = vi.mocked(tokenService);
const mockExtractUserFromToken = vi.mocked(extractUserFromToken);

// Mock auth store
const mockStore = {
  user: null as AuthUser | null,
  tokens: null as import("@/lib/api/types").AuthTokens | null,
  isAuthenticated: false,
  isLoading: false,
  error: null as string | null,
  login: vi.fn(),
  logout: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
  setTokens: vi.fn(),
  setRefreshing: vi.fn(),
};

vi.mock("@/lib/store/authStore", () => ({
  useAuthStore: () => mockStore,
}));

describe("useAuth Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset mock store state
    Object.assign(mockStore, {
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("initial state", () => {
    it("should return initial auth state", () => {
      const { result } = renderHook(() => useAuth());

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it("should return auth functions", () => {
      const { result } = renderHook(() => useAuth());

      expect(typeof result.current.login).toBe("function");
      expect(typeof result.current.register).toBe("function");
      expect(typeof result.current.logout).toBe("function");
      expect(typeof result.current.forgotPassword).toBe("function");
      expect(typeof result.current.resetPassword).toBe("function");
      expect(typeof result.current.clearError).toBe("function");
      expect(typeof result.current.refreshSession).toBe("function");
      expect(typeof result.current.hasRole).toBe("function");
      expect(typeof result.current.hasAnyRole).toBe("function");
      expect(typeof result.current.isSessionValid).toBe("function");
    });
  });

  describe("login", () => {
    it("should login successfully", async () => {
      const loginRequest = createAuthLoginRequest();
      const tokens = createAuthTokens();
      const user = createAuthUser();

      mockAuthApi.login.mockResolvedValue(tokens);
      mockExtractUserFromToken.mockReturnValue(user);

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login(loginRequest);
      });

      expect(mockStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockStore.clearError).toHaveBeenCalled();
      expect(mockAuthApi.login).toHaveBeenCalledWith(loginRequest);
      expect(mockExtractUserFromToken).toHaveBeenCalledWith(tokens);
      expect(mockStore.login).toHaveBeenCalledWith(user, tokens);
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });

    it("should handle remember me option", async () => {
      const loginRequest = createAuthLoginRequest();
      const tokens = createAuthTokens();
      const user = createAuthUser();

      mockAuthApi.login.mockResolvedValue(tokens);
      mockExtractUserFromToken.mockReturnValue(user);

      // Mock localStorage
      const localStorageMock = {
        setItem: vi.fn(),
        removeItem: vi.fn(),
      };
      Object.defineProperty(window, "localStorage", {
        value: localStorageMock,
      });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login(loginRequest, true);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "auth_remember_me",
        "true",
      );
    });

    it("should handle login errors", async () => {
      const loginRequest = createAuthLoginRequest();
      const error = createAuthError();

      mockAuthApi.login.mockRejectedValue(new Error(error.message));

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await expect(result.current.login(loginRequest)).rejects.toThrow(
          error.message,
        );
      });

      expect(mockStore.setError).toHaveBeenCalledWith(error.message);
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });

    it("should handle invalid token response", async () => {
      const loginRequest = createAuthLoginRequest();
      const tokens = createAuthTokens();

      mockAuthApi.login.mockResolvedValue(tokens);
      mockExtractUserFromToken.mockReturnValue(null); // Invalid token

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await expect(result.current.login(loginRequest)).rejects.toThrow(
          "Invalid authentication response",
        );
      });

      expect(mockStore.setError).toHaveBeenCalledWith(
        "Invalid authentication response",
      );
    });
  });

  describe("register", () => {
    it("should register successfully", async () => {
      const registerRequest = createAuthRegisterRequest();
      const tokens = createAuthTokens();
      const user = createAuthUser();

      mockAuthApi.register.mockResolvedValue(tokens);
      mockExtractUserFromToken.mockReturnValue(user);

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.register(registerRequest);
      });

      expect(mockStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockStore.clearError).toHaveBeenCalled();
      expect(mockAuthApi.register).toHaveBeenCalledWith(registerRequest);
      expect(mockExtractUserFromToken).toHaveBeenCalledWith(tokens);
      expect(mockStore.login).toHaveBeenCalledWith(user, tokens);
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });

    it("should handle registration errors", async () => {
      const registerRequest = createAuthRegisterRequest();
      const error = createAuthError();

      mockAuthApi.register.mockRejectedValue(new Error(error.message));

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await expect(result.current.register(registerRequest)).rejects.toThrow(
          error.message,
        );
      });

      expect(mockStore.setError).toHaveBeenCalledWith(error.message);
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });
  });

  describe("logout", () => {
    it("should logout successfully with tokens", async () => {
      const tokens = createAuthTokens();
      mockStore.tokens = tokens;

      mockAuthApi.logout.mockResolvedValue({ message: "Logged out" });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.logout();
      });

      expect(mockStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockAuthApi.logout).toHaveBeenCalled();
      expect(mockStore.logout).toHaveBeenCalled();
      expect(mockTokenService.clearRefreshState).toHaveBeenCalled();
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });

    it("should logout locally when server logout fails", async () => {
      const tokens = createAuthTokens();
      mockStore.tokens = tokens;

      mockAuthApi.logout.mockRejectedValue(new Error("Server error"));

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.logout();
      });

      expect(mockStore.logout).toHaveBeenCalled();
      expect(mockTokenService.clearRefreshState).toHaveBeenCalled();
    });

    it("should logout without calling server when no tokens", async () => {
      mockStore.tokens = null;

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.logout();
      });

      expect(mockAuthApi.logout).not.toHaveBeenCalled();
      expect(mockStore.logout).toHaveBeenCalled();
    });
  });

  describe("forgotPassword", () => {
    it("should send forgot password request successfully", async () => {
      const email = "test@example.com";
      mockAuthApi.forgotPassword.mockResolvedValue({
        message: "Reset email sent",
      });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.forgotPassword(email);
      });

      expect(mockStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockStore.clearError).toHaveBeenCalled();
      expect(mockAuthApi.forgotPassword).toHaveBeenCalledWith({ email });
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });

    it("should handle forgot password errors", async () => {
      const email = "test@example.com";
      const error = createAuthError();

      mockAuthApi.forgotPassword.mockRejectedValue(new Error(error.message));

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await expect(result.current.forgotPassword(email)).rejects.toThrow(
          error.message,
        );
      });

      expect(mockStore.setError).toHaveBeenCalledWith(error.message);
    });
  });

  describe("resetPassword", () => {
    it("should reset password successfully", async () => {
      const token = "reset-token-123";
      const newPassword = "newPassword123";
      mockAuthApi.resetPassword.mockResolvedValue({
        message: "Password reset",
      });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.resetPassword(token, newPassword);
      });

      expect(mockStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockStore.clearError).toHaveBeenCalled();
      expect(mockAuthApi.resetPassword).toHaveBeenCalledWith({
        token,
        new_password: newPassword,
      });
      expect(mockStore.setLoading).toHaveBeenCalledWith(false);
    });

    it("should handle reset password errors", async () => {
      const token = "reset-token-123";
      const newPassword = "newPassword123";
      const error = createAuthError();

      mockAuthApi.resetPassword.mockRejectedValue(new Error(error.message));

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await expect(
          result.current.resetPassword(token, newPassword),
        ).rejects.toThrow(error.message);
      });

      expect(mockStore.setError).toHaveBeenCalledWith(error.message);
    });
  });

  describe("clearError", () => {
    it("should clear authentication error", () => {
      const { result } = renderHook(() => useAuth());

      act(() => {
        result.current.clearError();
      });

      expect(mockStore.clearError).toHaveBeenCalled();
    });
  });

  describe("refreshSession", () => {
    it("should refresh session successfully", async () => {
      const tokens = createAuthTokens();
      mockStore.tokens = tokens;

      mockTokenService.refreshAccessToken.mockResolvedValue("new-access-token");

      const { result } = renderHook(() => useAuth());

      let refreshResult: boolean = false;
      await act(async () => {
        refreshResult = await result.current.refreshSession();
      });

      expect(refreshResult).toBe(true);
      expect(mockStore.setRefreshing).toHaveBeenCalledWith(true);
      expect(mockTokenService.refreshAccessToken).toHaveBeenCalled();
      expect(mockStore.setRefreshing).toHaveBeenCalledWith(false);
    });

    it("should handle refresh failure", async () => {
      const tokens = createAuthTokens();
      mockStore.tokens = tokens;

      mockTokenService.refreshAccessToken.mockRejectedValue(
        new Error("Refresh failed"),
      );

      const { result } = renderHook(() => useAuth());

      let refreshResult: boolean = false;
      await act(async () => {
        refreshResult = await result.current.refreshSession();
      });

      expect(refreshResult).toBe(false);
      expect(mockStore.setRefreshing).toHaveBeenCalledWith(false);
    });

    it("should return false when no refresh token", async () => {
      mockStore.tokens = null;

      const { result } = renderHook(() => useAuth());

      let refreshResult: boolean = false;
      await act(async () => {
        refreshResult = await result.current.refreshSession();
      });

      expect(refreshResult).toBe(false);
      expect(mockTokenService.refreshAccessToken).not.toHaveBeenCalled();
    });
  });

  describe("role utilities", () => {
    it("should check if user has specific role", () => {
      const user = createAuthUser({ roles: ["admin", "user"] });
      mockStore.user = user;

      const { result } = renderHook(() => useAuth());

      expect(result.current.hasRole("admin")).toBe(true);
      expect(result.current.hasRole("moderator")).toBe(false);
    });

    it("should return false when user has no roles", () => {
      const user = createAuthUser({ roles: [] });
      mockStore.user = user;

      const { result } = renderHook(() => useAuth());

      expect(result.current.hasRole("admin")).toBe(false);
    });

    it("should return false when no user", () => {
      mockStore.user = null;

      const { result } = renderHook(() => useAuth());

      expect(result.current.hasRole("admin")).toBe(false);
    });

    it("should check if user has any of multiple roles", () => {
      const user = createAuthUser({ roles: ["user", "editor"] });
      mockStore.user = user;

      const { result } = renderHook(() => useAuth());

      expect(result.current.hasAnyRole(["admin", "editor"])).toBe(true);
      expect(result.current.hasAnyRole(["admin", "moderator"])).toBe(false);
    });
  });

  describe("session validation", () => {
    it("should validate session when tokens exist", () => {
      const tokens = createAuthTokens();
      mockStore.tokens = tokens;

      mockTokenService.needsRefresh.mockReturnValue(false);

      const { result } = renderHook(() => useAuth());

      expect(result.current.isSessionValid()).toBe(true);
      expect(mockTokenService.needsRefresh).toHaveBeenCalled();
    });

    it("should invalidate session when token needs refresh", () => {
      const tokens = createAuthTokens();
      mockStore.tokens = tokens;

      mockTokenService.needsRefresh.mockReturnValue(true);

      const { result } = renderHook(() => useAuth());

      expect(result.current.isSessionValid()).toBe(false);
    });

    it("should invalidate session when no tokens", () => {
      mockStore.tokens = null;

      const { result } = renderHook(() => useAuth());

      expect(result.current.isSessionValid()).toBe(false);
      expect(mockTokenService.needsRefresh).not.toHaveBeenCalled();
    });
  });
});
