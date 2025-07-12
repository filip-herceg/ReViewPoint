// Tests for common API types and utilities
import { describe, it, expect } from "vitest";
import {
  HttpStatusCode,
  isApiError,
  isApiResponse,
  isPaginatedResponse,
  extractApiData,
  createApiResponse,
  createApiErrorResponse,
  type ApiResponse,
  type ApiError,
  type PaginatedResponse,
  type FieldError,
} from "@/lib/api/types/common";
import { testLogger } from "../../../test-utils";

describe("HttpStatusCode", () => {
  it("should have correct status code values", () => {
    testLogger.info("Testing HttpStatusCode enum values");

    expect(HttpStatusCode.OK).toBe(200);
    expect(HttpStatusCode.CREATED).toBe(201);
    expect(HttpStatusCode.BAD_REQUEST).toBe(400);
    expect(HttpStatusCode.UNAUTHORIZED).toBe(401);
    expect(HttpStatusCode.NOT_FOUND).toBe(404);
    expect(HttpStatusCode.INTERNAL_SERVER_ERROR).toBe(500);

    testLogger.debug("All HttpStatusCode values are correct");
  });
});

describe("isApiError", () => {
  it("should identify valid ApiError objects", () => {
    testLogger.info("Testing isApiError type guard with valid objects");

    const validError: ApiError = {
      message: "Test error",
      status: 400,
      type: "validation_error",
    };

    expect(isApiError(validError)).toBe(true);
    testLogger.debug("Valid ApiError correctly identified");

    const minimalError = { message: "Simple error" };
    expect(isApiError(minimalError)).toBe(true);
    testLogger.debug("Minimal ApiError correctly identified");
  });

  it("should reject invalid objects", () => {
    testLogger.info("Testing isApiError type guard with invalid objects");

    expect(isApiError(null)).toBe(false);
    expect(isApiError(undefined)).toBe(false);
    expect(isApiError("string error")).toBe(false);
    expect(isApiError({})).toBe(false);
    expect(isApiError({ error: "wrong field" })).toBe(false);

    testLogger.debug("Invalid objects correctly rejected");
  });
});

describe("isApiResponse", () => {
  it("should identify valid ApiResponse objects", () => {
    testLogger.info("Testing isApiResponse type guard with valid objects");

    const successResponse: ApiResponse<string> = { data: "test" };
    const errorResponse: ApiResponse<never> = { data: null, error: "error" };

    expect(isApiResponse(successResponse)).toBe(true);
    expect(isApiResponse(errorResponse)).toBe(true);

    testLogger.debug("Valid ApiResponse objects correctly identified");
  });

  it("should reject invalid objects", () => {
    testLogger.info("Testing isApiResponse type guard with invalid objects");

    expect(isApiResponse(null)).toBe(false);
    expect(isApiResponse(undefined)).toBe(false);
    expect(isApiResponse({})).toBe(false);
    expect(isApiResponse({ result: "wrong field" })).toBe(false);

    testLogger.debug("Invalid objects correctly rejected");
  });
});

describe("isPaginatedResponse", () => {
  it("should identify valid PaginatedResponse objects", () => {
    testLogger.info("Testing isPaginatedResponse type guard");

    const paginatedResponse: PaginatedResponse<string> = {
      items: ["item1", "item2"],
      total: 2,
      page: 1,
      per_page: 10,
      pages: 1,
    };

    expect(isPaginatedResponse(paginatedResponse)).toBe(true);
    testLogger.debug("Valid PaginatedResponse correctly identified");
  });

  it("should reject invalid objects", () => {
    testLogger.info("Testing isPaginatedResponse with invalid objects");

    expect(isPaginatedResponse(null)).toBe(false);
    expect(isPaginatedResponse({ total: 5 })).toBe(false);
    expect(isPaginatedResponse({ items: "not array", total: 5 })).toBe(false);

    testLogger.debug("Invalid objects correctly rejected");
  });
});

describe("extractApiData", () => {
  it("should extract data from successful response", () => {
    testLogger.info("Testing extractApiData with successful response");

    const response: ApiResponse<{ id: number; name: string }> = {
      data: { id: 1, name: "test" },
    };

    const result = extractApiData(response);
    expect(result).toEqual({ id: 1, name: "test" });

    testLogger.debug("Data successfully extracted from response");
  });

  it("should throw error for error response", () => {
    testLogger.info("Testing extractApiData with error response");

    const errorResponse: ApiResponse<never> = {
      data: null,
      error: "Something went wrong",
    };

    expect(() => extractApiData(errorResponse)).toThrow("Something went wrong");
    testLogger.debug("Error correctly thrown for error response");
  });

  it("should throw error for null data", () => {
    testLogger.info("Testing extractApiData with null data");

    const nullResponse: ApiResponse<string> = { data: null };

    expect(() => extractApiData(nullResponse)).toThrow(
      "API response data is null",
    );
    testLogger.debug("Error correctly thrown for null data");
  });
});

describe("createApiResponse", () => {
  it("should create successful response", () => {
    testLogger.info("Testing createApiResponse");

    const data = { id: 1, name: "test" };
    const response = createApiResponse(data);

    expect(response).toEqual({ data });
    expect(response.error).toBeUndefined();

    testLogger.debug("Successful response created correctly");
  });
});

describe("createApiErrorResponse", () => {
  it("should create error response", () => {
    testLogger.info("Testing createApiErrorResponse");

    const errorMessage = "Test error";
    const response = createApiErrorResponse(errorMessage);

    expect(response).toEqual({
      data: null,
      error: errorMessage,
    });

    testLogger.debug("Error response created correctly");
  });
});

describe("Type integration tests", () => {
  it("should work with complex nested types", () => {
    testLogger.info("Testing complex type integration");

    interface TestData {
      users: Array<{ id: number; name: string }>;
      metadata: { count: number };
    }

    const complexResponse: ApiResponse<TestData> = {
      data: {
        users: [
          { id: 1, name: "John" },
          { id: 2, name: "Jane" },
        ],
        metadata: { count: 2 },
      },
    };

    expect(isApiResponse(complexResponse)).toBe(true);

    const extractedData = extractApiData(complexResponse);
    expect(extractedData.users).toHaveLength(2);
    expect(extractedData.metadata.count).toBe(2);

    testLogger.debug("Complex type integration working correctly");
  });

  it("should work with FieldError arrays", () => {
    testLogger.info("Testing FieldError array handling");

    const fieldErrors: FieldError[] = [
      {
        field: "email",
        message: "Invalid email format",
        code: "INVALID_EMAIL",
      },
      { field: "password", message: "Password too short", code: "TOO_SHORT" },
    ];

    const apiError: ApiError = {
      message: "Validation failed",
      type: "validation_error",
      field_errors: fieldErrors,
    };

    expect(isApiError(apiError)).toBe(true);
    expect(apiError.field_errors).toHaveLength(2);
    expect(apiError.field_errors![0].field).toBe("email");

    testLogger.debug("FieldError array handling working correctly");
  });
});

describe("Error handling edge cases", () => {
  it("should handle empty strings and zero values", () => {
    testLogger.info("Testing edge cases with empty values");

    const emptyStringResponse = createApiResponse("");
    expect(extractApiData(emptyStringResponse)).toBe("");

    const zeroResponse = createApiResponse(0);
    expect(extractApiData(zeroResponse)).toBe(0);

    const falseResponse = createApiResponse(false);
    expect(extractApiData(falseResponse)).toBe(false);

    testLogger.debug("Edge cases handled correctly");
  });

  it("should handle nested error objects", () => {
    testLogger.info("Testing nested error object handling");

    const nestedError: ApiError = {
      message: "Complex error",
      details: {
        nested: {
          property: "value",
          array: [1, 2, 3],
        },
      },
    };

    expect(isApiError(nestedError)).toBe(true);
    expect(nestedError.details?.nested).toBeDefined();

    testLogger.debug("Nested error objects handled correctly");
  });
});
