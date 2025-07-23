/**
 * Token Service
 *
 * Centralized service for managing JWT tokens including refresh logic,
 * expiration detection, and secure storage management.
 *
 * Features:
 * - Automatic token refresh
 * - Expiration detection with buffer
 * - Concurrent request handling during refresh
 * - Secure token storage
 * - Comprehensive error handling
 * - Logging for debugging
 */

import { authApi } from "@/lib/api/auth";
import type { AuthTokens, JWTPayload } from "@/lib/api/types";
import { useAuthStore } from "@/lib/store/authStore";
import logger from "@/logger";

interface TokenRefreshState {
  isRefreshing: boolean;
  refreshPromise: Promise<string> | null;
  refreshQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: Error) => void;
  }>;
}

class TokenService {
  private refreshState: TokenRefreshState = {
    isRefreshing: false,
    refreshPromise: null,
    refreshQueue: [],
  };

  // Token expiration buffer in seconds (refresh 5 minutes before expiry)
  private readonly EXPIRATION_BUFFER = 5 * 60;

  /**
   * Decode JWT payload without verification
   * Used for extracting expiration time and user info
   */
  decodeJWTPayload(token: string): JWTPayload | null {
    try {
      const parts = token.split(".");
      if (parts.length !== 3) {
        logger.warn("[TokenService] Invalid JWT format", {
          tokenLength: token.length,
        });
        return null;
      }

      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
      const parsed = JSON.parse(decoded) as JWTPayload;

      logger.debug("[TokenService] JWT decoded successfully", {
        sub: parsed.sub,
        exp: parsed.exp,
        iat: parsed.iat,
      });

      return parsed;
    } catch (error) {
      logger.error("[TokenService] Failed to decode JWT", {
        error: error instanceof Error ? error.message : "Unknown error",
        tokenPrefix: `${token.substring(0, 20)}...`,
      });
      return null;
    }
  }

  /**
   * Check if token is expired or will expire soon
   */
  isTokenExpired(token: string): boolean {
    const payload = this.decodeJWTPayload(token);
    if (!payload) {
      logger.warn("[TokenService] Cannot check expiration - invalid token");
      return true;
    }

    const currentTime = Math.floor(Date.now() / 1000);
    const expirationTime = payload.exp;
    const isExpired = currentTime >= expirationTime - this.EXPIRATION_BUFFER;

    logger.debug("[TokenService] Token expiration check", {
      currentTime,
      expirationTime,
      bufferTime: this.EXPIRATION_BUFFER,
      timeToExpiry: expirationTime - currentTime,
      isExpired,
    });

    return isExpired;
  }

  /**
   * Get current access token from store
   */
  getCurrentAccessToken(): string | null {
    const tokens = useAuthStore.getState().tokens;
    if (!tokens?.access_token) {
      logger.debug("[TokenService] No access token available");
      return null;
    }
    return tokens.access_token;
  }

  /**
   * Get current refresh token from store
   */
  getCurrentRefreshToken(): string | null {
    const tokens = useAuthStore.getState().tokens;
    if (!tokens?.refresh_token) {
      logger.debug("[TokenService] No refresh token available");
      return null;
    }
    return tokens.refresh_token;
  }

  /**
   * Check if current access token needs refresh
   */
  needsRefresh(): boolean {
    const accessToken = this.getCurrentAccessToken();
    if (!accessToken) {
      logger.debug("[TokenService] No access token - refresh not needed");
      return false;
    }

    const expired = this.isTokenExpired(accessToken);
    logger.debug("[TokenService] Token refresh check", {
      needsRefresh: expired,
    });
    return expired;
  }

  /**
   * Refresh access token using refresh token
   * Handles concurrent requests and queuing
   */
  async refreshAccessToken(): Promise<string> {
    logger.info("[TokenService] Starting token refresh");

    // If already refreshing, queue the request
    if (this.refreshState.isRefreshing && this.refreshState.refreshPromise) {
      logger.debug(
        "[TokenService] Token refresh in progress - queuing request",
      );
      return this.refreshState.refreshPromise;
    }

    const refreshToken = this.getCurrentRefreshToken();
    if (!refreshToken) {
      const error = new Error("No refresh token available");
      logger.error("[TokenService] Refresh failed - no refresh token", {
        error: error.message,
      });
      this.handleRefreshFailure(error);
      throw error;
    }

    // Mark as refreshing and create promise
    this.refreshState.isRefreshing = true;
    this.refreshState.refreshPromise = this.performTokenRefresh(refreshToken);

    try {
      const newAccessToken = await this.refreshState.refreshPromise;
      logger.info("[TokenService] Token refresh successful");

      // Process queued requests
      this.processRefreshQueue(newAccessToken);

      return newAccessToken;
    } catch (error) {
      logger.error("[TokenService] Token refresh failed", {
        error: error instanceof Error ? error.message : "Unknown error",
      });

      // Handle refresh failure by logging out user
      this.handleRefreshFailure(error as Error);

      // Process queued requests with error
      this.processRefreshQueue(null, error as Error);

      throw error;
    } finally {
      // Reset refresh state
      this.refreshState.isRefreshing = false;
      this.refreshState.refreshPromise = null;
    }
  }

  /**
   * Perform the actual token refresh API call
   */
  private async performTokenRefresh(refreshToken: string): Promise<string> {
    try {
      logger.debug("[TokenService] Calling refresh API");
      const response = await authApi.refreshToken(refreshToken);

      // Update auth store with new tokens
      const authStore = useAuthStore.getState();
      const currentUser = authStore.user;

      // Convert AuthResponse to AuthTokens format
      const tokens: AuthTokens = {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: "bearer",
      };

      if (currentUser) {
        authStore.login(currentUser, tokens);
        logger.debug("[TokenService] Updated auth store with new tokens");
      } else {
        logger.warn("[TokenService] No current user - only updating tokens");
        authStore.setTokens(tokens);
      }

      return response.access_token;
    } catch (error) {
      logger.error("[TokenService] API refresh call failed", {
        error: error instanceof Error ? error.message : "Unknown error",
        refreshTokenPrefix: `${refreshToken.substring(0, 20)}...`,
      });
      throw error;
    }
  }

  /**
   * Process queued refresh requests
   */
  private processRefreshQueue(newToken: string | null, error?: Error): void {
    logger.debug("[TokenService] Processing refresh queue", {
      queueLength: this.refreshState.refreshQueue.length,
      hasToken: !!newToken,
      hasError: !!error,
    });

    while (this.refreshState.refreshQueue.length > 0) {
      const request = this.refreshState.refreshQueue.shift();
      if (!request) continue;

      if (newToken) {
        request.resolve(newToken);
      } else if (error) {
        request.reject(error);
      } else {
        request.reject(new Error("Token refresh failed"));
      }
    }
  }

  /**
   * Add request to refresh queue
   */
  private queueRefreshRequest(): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      this.refreshState.refreshQueue.push({ resolve, reject });
      logger.debug("[TokenService] Added request to refresh queue", {
        queueLength: this.refreshState.refreshQueue.length,
      });
    });
  }

  /**
   * Handle refresh failure - logout user and clear tokens
   */
  private handleRefreshFailure(error: Error): void {
    logger.warn("[TokenService] Handling refresh failure - logging out user", {
      error: error.message,
    });

    const authStore = useAuthStore.getState();
    authStore.logout();

    // Optionally redirect to login page
    // Note: Don't import router here to avoid circular dependencies
    // Let the calling component handle navigation
  }

  /**
   * Get valid access token - refresh if needed
   * This is the main method used by API interceptors
   */
  async getValidAccessToken(): Promise<string | null> {
    try {
      const currentToken = this.getCurrentAccessToken();

      if (!currentToken) {
        logger.debug("[TokenService] No access token available");
        return null;
      }

      if (!this.needsRefresh()) {
        logger.debug("[TokenService] Current token is valid");
        return currentToken;
      }

      logger.info("[TokenService] Token needs refresh - refreshing");
      return await this.refreshAccessToken();
    } catch (error) {
      logger.error("[TokenService] Failed to get valid access token", {
        error: error instanceof Error ? error.message : "Unknown error",
      });
      return null;
    }
  }

  /**
   * Clear all token refresh state
   * Used for cleanup during logout
   */
  clearRefreshState(): void {
    logger.debug("[TokenService] Clearing refresh state");

    // Reject all queued requests
    this.processRefreshQueue(null, new Error("Token refresh cancelled"));

    // Reset state
    this.refreshState.isRefreshing = false;
    this.refreshState.refreshPromise = null;
    this.refreshState.refreshQueue = [];
  }
}

// Export singleton instance
export const tokenService = new TokenService();

// Export class for testing
export { TokenService };
