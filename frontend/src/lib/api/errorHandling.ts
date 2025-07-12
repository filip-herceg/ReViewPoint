// Error handling strategies for network, 4xx, 5xx errors
// Uses logger and provides helpers for consistent error handling in API calls

import logger from "@/logger";
import type { AxiosError } from "axios";
import { createTestError } from "../../../tests/test-templates";

export type ErrorType = "network" | "4xx" | "5xx" | "unknown";

export interface HandledError {
  type: ErrorType;
  status?: number;
  message: string;
  original?: unknown;
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
  const response = isAxiosError ? (error as any).response : undefined;

  // Axios network error (isAxiosError is true but no response)
  if (isAxiosError && !response) {
    const message = error instanceof Error ? error.message : "Network error";
    logger.error("Network error", error);
    return { type: "network", message, original: error };
  }

  // Axios HTTP error (isAxiosError is true and has response)
  if (isAxiosError && response) {
    const status = response?.status;
    let message = "HTTP error";

    // Get error message from response data
    const data = response?.data;
    if (data) {
      if (typeof data === "string") {
        message = data;
      } else if (typeof data === "object" && data !== null) {
        if ("error" in data && typeof data.error === "string") {
          message = data.error;
        } else if ("message" in data && typeof data.message === "string") {
          message = data.message;
        }
      }
    }

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
    // Direct error/message property access for objects like { error: 'message' }
    if ("error" in error && typeof (error as any).error === "string") {
      const message = (error as any).error;
      logger.warn("Object with error property:", message);
      return { type: "unknown", message, original: error };
    }

    if ("message" in error && typeof (error as any).message === "string") {
      const message = (error as any).message;
      logger.warn("Object with message property:", message);
      return { type: "unknown", message, original: error };
    }

    // Handle other object types without error/message properties
    // This will fall through to the final fallback
  }

  // Axios HTTP error
  if (isAxiosError && response) {
    const status = response?.status;
    let message = "HTTP error";

    // Get error message from response data
    const data = response?.data;
    if (data) {
      if (typeof data === "string") {
        message = data;
      } else if (typeof data === "object" && data !== null) {
        if ("error" in data && typeof data.error === "string") {
          message = data.error;
        } else if ("message" in data && typeof data.message === "string") {
          message = data.message;
        }
      }
    }

    if (status && status >= 400 && status < 500) {
      logger.warn(`4xx error (${status}):`, message, error);
      return { type: "4xx", status, message, original: error };
    }
    if (status && status >= 500) {
      logger.error(`5xx error (${status}):`, message, error);
      return { type: "5xx", status, message, original: error };
    }
  }

  // Fallback for any other type
  const wrappedError =
    error instanceof Error ? error : new Error("Unknown error type");
  logger.error("Unknown error type", wrappedError);
  return { type: "unknown", message: "Unknown error type", original: error };
}

// Usage: in API layer, call handleApiError(error) and use the returned object for UI or further logging
