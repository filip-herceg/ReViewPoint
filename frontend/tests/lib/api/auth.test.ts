// Tests for auth API
// Mirrors backend/src/api/v1/auth.py

import { beforeEach, describe, expect, it, vi } from "vitest";
import { authApi } from "../../../src/lib/api/auth";
import { request } from "../../../src/lib/api/base";

// Mock the request function
vi.mock("../../../src/lib/api/base", () => ({
  request: vi.fn(),
}));

// Mock the logger
vi.mock("@/logger", () => ({
  default: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

const mockRequest = vi.mocked(request);

describe("authApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("register", () => {
    it("should register a user successfully", async () => {
      const mockResponse = {
        data: { access_token: "token123", refresh_token: "refresh123" },
        error: undefined,
      };
      mockRequest.mockResolvedValue(mockResponse);

      const userData = {
        email: "test@example.com",
        password: "password123",
        name: "Test User",
      };
      const result = await authApi.register(userData);

      expect(mockRequest).toHaveBeenCalledWith("/api/v1/auth/register", {
        method: "POST",
        data: userData,
      });
      expect(result).toEqual({
        ...mockResponse.data,
        token_type: "bearer",
      });
    });

    it("should throw error when registration fails", async () => {
      const mockResponse = {
        data: undefined,
        error: "Email already exists",
      };
      mockRequest.mockResolvedValue(mockResponse);

      const userData = {
        email: "test@example.com",
        password: "password123",
        name: "Test User",
      };

      await expect(authApi.register(userData)).rejects.toThrow(
        "Email already exists",
      );
    });
  });

  describe("login", () => {
    it("should login successfully", async () => {
      const mockResponse = {
        data: { access_token: "token123", refresh_token: "refresh123" },
        error: undefined,
      };
      mockRequest.mockResolvedValue(mockResponse);

      const loginData = { email: "test@example.com", password: "password123" };
      const result = await authApi.login(loginData);

      expect(mockRequest).toHaveBeenCalledWith("/api/v1/auth/login", {
        method: "POST",
        data: loginData,
      });
      expect(result).toEqual({
        ...mockResponse.data,
        token_type: "bearer",
      });
    });
  });

  describe("logout", () => {
    it("should logout successfully", async () => {
      const mockResponse = {
        data: { message: "Logged out successfully" },
        error: undefined,
      };
      mockRequest.mockResolvedValue(mockResponse);

      const result = await authApi.logout();

      expect(mockRequest).toHaveBeenCalledWith("/api/v1/auth/logout", {
        method: "POST",
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("refreshToken", () => {
    it("should refresh token successfully", async () => {
      const mockResponse = {
        data: { access_token: "newtoken123", refresh_token: "refresh123" },
        error: undefined,
      };
      mockRequest.mockResolvedValue(mockResponse);

      const result = await authApi.refreshToken("refresh123");

      expect(mockRequest).toHaveBeenCalledWith("/api/v1/auth/refresh-token", {
        method: "POST",
        data: { refresh_token: "refresh123" },
      });
      expect(result).toEqual({
        ...mockResponse.data,
        token_type: "bearer",
      });
    });
  });

  describe("getCurrentUser", () => {
    it("should get current user successfully", async () => {
      const mockResponse = {
        data: {
          id: 1,
          email: "test@example.com",
          name: "Test User",
          bio: "Test bio",
          created_at: "2024-01-01T00:00:00Z",
        },
        error: undefined,
      };
      mockRequest.mockResolvedValue(mockResponse);

      const result = await authApi.getCurrentUser();

      expect(mockRequest).toHaveBeenCalledWith("/api/v1/auth/me");
      expect(result).toEqual(mockResponse.data);
    });
  });
});
