// Error handling strategies for network, 4xx, 5xx errors
// Uses logger and provides helpers for consistent error handling in API calls

import logger from "@/logger";

export type ErrorType = "network" | "4xx" | "5xx" | "unknown";

export interface HandledError {
  type: ErrorType;
  status?: number;
  message: string;
  original?: unknown;
}

/**
 * Extract error message from response data
 */
function extractErrorMessage(data: unknown): string {
  if (typeof data === "string") {
    return data;
  }
  if (typeof data === "object" && data !== null) {
    if ("error" in data && typeof data.error === "string") {
      return data.error;
    }
    if ("message" in data && typeof data.message === "string") {
      return data.message;
    }
  }
  return "HTTP error";
}

export function handleApiError(error: unknown): HandledError {
  if (!error) {
    logger.error("Unknown error: no error object");
    return { type: "unknown", message: "Unknown error", original: error };
  }

  // Handle primitive values that are not errors
  if (typeof error === "string") {
    // Use the string as the message if it's meaningful, otherwise default message
    const message = error.trim() || "Unknown error";
    logger.error("String error:", message);
    return { type: "unknown", message, original: error };
  }

  if (typeof error === "number" || typeof error === "boolean") {
    const message = String(error);
    logger.error("Primitive error:", message);
    return { type: "unknown", message, original: error };
  }

  // Check for Axios error first (both network and HTTP errors)
  const isAxiosError =
    typeof error === "object" && error !== null && "isAxiosError" in error;

  // Type guard for axios error with response
  const getAxiosResponse = (
    err: unknown,
  ): { status?: number; data?: unknown } | undefined => {
    if (typeof err === "object" && err !== null && "response" in err) {
      const response = (err as { response?: unknown }).response;
      if (typeof response === "object" && response !== null) {
        return response as { status?: number; data?: unknown };
      }
    }
    return undefined;
  };

  const response = isAxiosError ? getAxiosResponse(error) : undefined;

  // Axios network error (isAxiosError is true but no response)
  if (isAxiosError && !response) {
    const message = error instanceof Error ? error.message : "Network error";
    logger.error("Network error", error);
    return { type: "network", message, original: error };
  }

  // Axios HTTP error (isAxiosError is true and has response)
  if (isAxiosError && response) {
    const status = response?.status;
    const message = extractErrorMessage(response?.data);

    if (status && status >= 400 && status < 500) {
      logger.warn(`4xx error (${status}):`, message, error);
      return { type: "4xx", status, message, original: error };
    }
    if (status && status >= 500) {
      logger.error(`5xx error (${status}):`, message, error);
      return { type: "5xx", status, message, original: error };
    }

    // Axios error with response but no status or unknown status
    logger.warn("HTTP error (unknown status):", message, error);
    return { type: "unknown", message, original: error };
  }

  // Handle Error instance - this covers standard JS errors and custom ones
  if (error instanceof Error) {
    logger.error("Error instance:", error.message);
    return { type: "unknown", message: error.message, original: error };
  }

  // Handle plain objects that might contain error information
  if (typeof error === "object" && error !== null && !Array.isArray(error)) {
    // Use the same extraction logic for consistency
    const message = extractErrorMessage(error);
    if (message !== "HTTP error") {
      // Successfully extracted a meaningful error message
      logger.warn("Object with error/message property:", message);
      return { type: "unknown", message, original: error };
    }
    // Fall through to final fallback if no meaningful message found
  }

  // Fallback for any other type
  const wrappedError =
    error instanceof Error ? error : new Error("Unknown error type");
  logger.error("Unknown error type", wrappedError);
  return { type: "unknown", message: "Unknown error type", original: error };
}

// Usage: in API layer, call handleApiError(error) and use the returned object for UI or further logging
