/**
 * Generated API Client
 *
 * Type-safe API client generated from OpenAPI schema.
 * This file is auto-generated - do not edit manually.
 *
 * @generated 2025-07-08T06:10:00.000Z
 */

import createClient from "openapi-fetch";
import logger from "@/logger";
import type { paths } from "./schema";

/**
 * Type-safe API client instance
 * Configured with base URL from environment variables
 */
export const generatedApiClient = createClient<paths>({
  baseUrl: import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Add request/response logging interceptor
 */
generatedApiClient.use({
  onRequest({ request }) {
    logger.debug("🔄 API Request:", {
      method: request.method,
      url: request.url,
      headers: Object.fromEntries(request.headers.entries()),
    });
    return request;
  },

  onResponse({ response }) {
    logger.debug("✅ API Response:", {
      status: response.status,
      statusText: response.statusText,
      url: response.url,
    });
    return response;
  },
});

/**
 * Type-safe error handling utility
 */
export function isApiError(
  error: unknown,
): error is { message: string; status?: number } {
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof (error as Record<string, unknown>).message === "string"
  );
}

/**
 * Extract error message from API response
 */
export function getApiErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unknown API error occurred";
}
