/**
 * Authentication API Module
 *
 * Provides authentication and authorization functionality for the ReViewPoint application.
 * This module mirrors the backend authentication endpoints and provides a consistent
 * interface for user authentication, registration, and session management.
 *
 * ## Endpoints
 * - `POST /v1/auth/register` - User registration
 * - `POST /v1/auth/login` - User login
 * - `POST /v1/auth/logout` - User logout
 * - `POST /v1/auth/refresh-token` - Token refresh
 * - `GET /v1/auth/me` - Get current user
 *
 * ## Usage
 *
 * ### User Registration
 * ```typescript
 * import { authApi } from '@/lib/api';
 *
 * const userData = {
 *   email: 'user@example.com',
 *   name: 'John Doe',
 *   password: 'securepassword123'
 * };
 *
 * try {
 *   const response = await authApi.register(userData);
 *   console.log('User registered:', response.user);
 *   // Store tokens for future requests
 *   localStorage.setItem('access_token', response.access_token);
 * } catch (error) {
 *   console.error('Registration failed:', error.message);
 * }
 * ```
 *
 * ### User Login
 * ```typescript
 * const credentials = {
 *   email: 'user@example.com',
 *   password: 'securepassword123'
 * };
 *
 * try {
 *   const response = await authApi.login(credentials);
 *   console.log('User logged in:', response.user);
 * } catch (error) {
 *   console.error('Login failed:', error.message);
 * }
 * ```
 *
 * ### Token Refresh
 * ```typescript
 * const refreshToken = localStorage.getItem('refresh_token');
 * try {
 *   const response = await authApi.refreshToken(refreshToken);
 *   localStorage.setItem('access_token', response.access_token);
 * } catch (error) {
 *   // Redirect to login
 *   window.location.href = '/login';
 * }
 * ```
 *
 * ## Error Handling
 * All authentication functions throw errors for failed requests:
 * - Invalid credentials
 * - Expired tokens
 * - Network errors
 * - Validation errors
 *
 * ## Security Features
 * - Secure token-based authentication
 * - Password validation
 * - Session management
 * - Automatic token refresh
 *
 * @see backend/src/api/v1/auth.py for corresponding backend implementation
 */

// User authentication API functions
// Mirrors backend/src/api/v1/auth.py

import logger from "@/logger";
import { request } from "./base";
import type {
  AuthLoginRequest,
  AuthRegisterRequest,
  AuthLoginResponse,
  AuthRegisterResponse,
  AuthLogoutResponse,
  AuthTokenRefreshResponse,
  AuthPasswordResetRequest,
  AuthPasswordResetResponse,
  AuthPasswordResetConfirmRequest,
  AuthPasswordResetConfirmResponse,
  User,
} from "@/lib/api/types";

export const authApi = {
  // Register a new user
  register: async (
    userData: AuthRegisterRequest,
  ): Promise<AuthRegisterResponse> => {
    logger.info("Registering user", { email: userData.email });

    // Ensure name is provided for registration
    const registrationData = {
      ...userData,
      name: userData.name || userData.email.split("@")[0], // Default name if not provided
    };

    const response = await request<AuthRegisterResponse>(
      "/api/v1/auth/register",
      {
        method: "POST",
        data: registrationData,
      },
    );

    if (response.error) {
      logger.warn("User registration failed", {
        error: response.error,
        email: userData.email,
      });
      throw new Error(response.error);
    }

    logger.info("User registered successfully", { email: userData.email });
    return {
      ...response.data!,
      token_type: "bearer", // Ensure token_type is included
    };
  },

  // User login
  login: async (loginData: AuthLoginRequest): Promise<AuthLoginResponse> => {
    logger.info("User login attempt", { email: loginData.email });
    const response = await request<AuthLoginResponse>("/api/v1/auth/login", {
      method: "POST",
      data: loginData,
    });

    if (response.error) {
      logger.warn("User login failed", {
        error: response.error,
        email: loginData.email,
      });
      throw new Error(response.error);
    }

    logger.info("User logged in successfully", { email: loginData.email });
    return {
      ...response.data!,
      token_type: "bearer", // Ensure token_type is included
    };
  },

  // User logout
  logout: async (): Promise<AuthLogoutResponse> => {
    logger.info("User logout attempt");
    const response = await request<AuthLogoutResponse>("/api/v1/auth/logout", {
      method: "POST",
    });

    if (response.error) {
      logger.warn("User logout failed", { error: response.error });
      throw new Error(response.error);
    }

    logger.info("User logged out successfully");
    return response.data!;
  },

  // Refresh JWT access token
  refreshToken: async (
    refreshToken: string,
  ): Promise<AuthTokenRefreshResponse> => {
    logger.info("Refreshing access token");
    const response = await request<AuthTokenRefreshResponse>(
      "/api/v1/auth/refresh-token",
      {
        method: "POST",
        data: { refresh_token: refreshToken },
      },
    );

    if (response.error) {
      logger.warn("Token refresh failed", { error: response.error });
      throw new Error(response.error);
    }

    logger.info("Token refreshed successfully");
    return {
      ...response.data!,
      token_type: "bearer", // Ensure token_type is included
    };
  },

  // Request password reset (alias for forgotPassword)
  forgotPassword: async (
    resetRequest: AuthPasswordResetRequest,
  ): Promise<AuthPasswordResetResponse> => {
    logger.info("Requesting password reset", { email: resetRequest.email });
    const response = await request<AuthPasswordResetResponse>(
      "/api/v1/auth/request-password-reset",
      {
        method: "POST",
        data: resetRequest,
      },
    );

    if (response.error) {
      logger.warn("Password reset request failed", {
        error: response.error,
        email: resetRequest.email,
      });
      throw new Error(response.error);
    }

    logger.info("Password reset requested successfully", {
      email: resetRequest.email,
    });
    return response.data!;
  },

  // Request password reset (original method name)
  requestPasswordReset: async (
    email: string,
  ): Promise<AuthPasswordResetResponse> => {
    return authApi.forgotPassword({ email });
  },

  // Reset password with token
  resetPassword: async (
    resetRequest: AuthPasswordResetConfirmRequest,
  ): Promise<AuthPasswordResetConfirmResponse> => {
    logger.info("Resetting password with token");
    const response = await request<AuthPasswordResetConfirmResponse>(
      "/api/v1/auth/reset-password",
      {
        method: "POST",
        data: resetRequest,
      },
    );

    if (response.error) {
      logger.warn("Password reset failed", { error: response.error });
      throw new Error(response.error);
    }

    logger.info("Password reset successfully");
    return response.data!;
  },

  // Get current user profile
  getCurrentUser: async (): Promise<User> => {
    logger.info("Getting current user profile");
    const response = await request<User>("/api/v1/auth/me");

    if (response.error) {
      logger.warn("Failed to get current user profile", {
        error: response.error,
      });
      throw new Error(response.error);
    }

    logger.info("Current user profile retrieved successfully");
    return response.data!;
  },
};
