// Base API functionality and request utilities
// Common functionality used across all API modules

import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";
import { handleApiError } from "./errorHandling";
import logger from "@/logger";
import type { ApiResponse } from "@/lib/api/types";

// Import token service for token management
import { tokenService } from "@/lib/auth/tokenService";
import { useAuthStore } from "@/lib/store/authStore";

// Remove automatic /api prefix - be explicit in endpoint calls
const API_BASE = "";

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Flag to prevent infinite refresh loops
let isRefreshingToken = false;

// Request interceptor: Attach token if available and handle refresh
import type { InternalAxiosRequestConfig } from "axios";
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip token injection for auth endpoints to prevent loops
    if (config.url?.includes("/auth/")) {
      logger.debug("[API] Skipping token injection for auth endpoint", {
        url: config.url,
      });
      return config;
    }

    try {
      // Get valid token (will refresh if needed)
      const token = await tokenService.getValidAccessToken();

      if (token && config.headers) {
        config.headers["Authorization"] = `Bearer ${token}`;
        logger.debug("[API] Added authorization header");
      } else {
        logger.debug("[API] No token available for request");
      }
    } catch (error) {
      logger.warn("[API] Failed to get valid token for request", {
        error: error instanceof Error ? error.message : "Unknown error",
        url: config.url,
      });
      // Continue with request even if token fetch fails
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor: Handle 401 responses with token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Handle 401 Unauthorized responses
    if (error.response?.status === 401 && !originalRequest._retry) {
      logger.info("[API] Received 401 - attempting token refresh", {
        url: originalRequest.url,
      });

      // Prevent infinite refresh loops
      if (isRefreshingToken) {
        logger.warn(
          "[API] Token refresh already in progress - rejecting request",
        );
        return Promise.reject(error);
      }

      // Skip refresh for auth endpoints
      if (originalRequest.url?.includes("/auth/")) {
        logger.debug("[API] 401 on auth endpoint - not attempting refresh");
        return Promise.reject(error);
      }

      try {
        isRefreshingToken = true;
        originalRequest._retry = true;

        // Update auth store refresh state
        useAuthStore.getState().setRefreshing(true);

        // Attempt token refresh
        const newToken = await tokenService.refreshAccessToken();

        if (newToken && originalRequest.headers) {
          originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
          logger.info("[API] Token refreshed - retrying original request");

          // Retry the original request with new token
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        logger.error("[API] Token refresh failed during 401 handling", {
          refreshError:
            refreshError instanceof Error
              ? refreshError.message
              : "Unknown error",
          originalUrl: originalRequest.url,
        });

        // If refresh fails, logout user
        useAuthStore.getState().logout();

        // You might want to redirect to login here
        // Note: Don't import router directly to avoid circular dependencies
        if (typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent("auth:logout"));
        }

        return Promise.reject(refreshError);
      } finally {
        isRefreshingToken = false;
        useAuthStore.getState().setRefreshing(false);
      }
    }

    // For other errors, proceed with normal error handling
    return Promise.reject(error);
  },
);

export async function request<T>(
  url: string,
  config: AxiosRequestConfig = {},
): Promise<ApiResponse<T>> {
  try {
    const res = await apiClient.request<T>({ url, ...config });
    logger.info("[API] request", { url, config, response: res.data });
    return { data: res.data as T };
  } catch (error: any) {
    // If the error has a response with data.error as a string, use that directly
    if (
      error?.response?.data &&
      (typeof error.response.data === "string" ||
        typeof error.response.data.error === "string" ||
        typeof error.response.data.message === "string")
    ) {
      const errorMessage =
        typeof error.response.data === "string"
          ? error.response.data
          : error.response.data.error || error.response.data.message;
      logger.error("[API] request ERROR", { url, config, error: errorMessage });
      return { data: null, error: errorMessage };
    }

    // Otherwise use our error handler
    const handled = handleApiError(error);
    logger.error("[API] request ERROR", {
      url,
      config,
      error: handled.message,
      handled,
    });
    return { data: null, error: handled.message };
  }
}
