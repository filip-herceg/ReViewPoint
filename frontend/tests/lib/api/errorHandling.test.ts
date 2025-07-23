import { beforeEach, describe, expect, it, vi } from "vitest";
import { handleApiError } from "@/lib/api/errorHandling";
import logger from "@/logger";

vi.mock("@/logger", () => ({
  default: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

const networkError = Object.assign(new Error("Network error"), {
  isAxiosError: true,
});
const error4xx = {
  isAxiosError: true,
  response: { status: 404, data: { error: "Not found" } },
};
const error5xx = {
  isAxiosError: true,
  response: { status: 500, data: { message: "Server error" } },
};
const unknownError = { message: "Something went wrong" };

describe("handleApiError", () => {
  it("handles network error", () => {
    const result = handleApiError(networkError);
    expect(result.type).toBe("network");
    expect(result.message).toBe("Network error");
  });

  it("handles 4xx error", () => {
    const result = handleApiError(error4xx);
    expect(result.type).toBe("4xx");
    expect(result.status).toBe(404);
    expect(result.message).toBe("Not found");
  });

  it("handles 5xx error", () => {
    const result = handleApiError(error5xx);
    expect(result.type).toBe("5xx");
    expect(result.status).toBe(500);
    expect(result.message).toBe("Server error");
  });

  it("handles unknown error", () => {
    const result = handleApiError(unknownError);
    expect(result.type).toBe("unknown");
    expect(result.message).toBe("Something went wrong");
  });

  it("handles null/undefined error", () => {
    expect(handleApiError(undefined).type).toBe("unknown");
    expect(handleApiError(null as any).type).toBe("unknown");
  });
});

describe("handleApiError (logger and edge cases)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls logger.error for network error", () => {
    handleApiError(networkError);
    expect(logger.error).toHaveBeenCalledWith(
      "Network error",
      expect.any(Error),
    );
  });

  it("calls logger.warn for 4xx error", () => {
    handleApiError(error4xx);
    expect(logger.warn).toHaveBeenCalledWith(
      expect.stringMatching(/4xx error \(404\):/),
      expect.stringMatching(/not found/i),
      expect.any(Object),
    );
  });

  it("calls logger.error for 5xx error", () => {
    handleApiError(error5xx);
    expect(logger.error).toHaveBeenCalledWith(
      expect.stringMatching(/5xx error \(500\):/),
      expect.stringMatching(/server error/i),
      expect.any(Object),
    );
  });

  it("calls logger.error for unknown error type", () => {
    handleApiError(unknownError);
    expect(logger.warn).toHaveBeenCalledWith(
      "Object with error/message property:",
      "Something went wrong",
    );
  });

  it("handles non-Error thrown value (string)", () => {
    const result = handleApiError("fail");
    expect(result.type).toBe("unknown");
    expect(result.message).toBe("fail");
    expect(logger.error).toHaveBeenCalledWith("String error:", "fail");
  });

  it("handles non-Error thrown value (object)", () => {
    const result = handleApiError({ foo: "bar" });
    expect(result.type).toBe("unknown");
    expect(result.message).toMatch(/unknown error type/i);
    expect(logger.error).toHaveBeenCalledWith(
      "Unknown error type",
      expect.any(Error),
    );
  });

  it("handles unknown HTTP error", () => {
    const unknownHttpError = {
      isAxiosError: true,
      response: { status: 418, data: { message: "Client error" } },
    };
    const result = handleApiError(unknownHttpError);
    expect(result.type).toBe("4xx");
    expect(result.status).toBe(418);
    expect(result.message).toBe("Client error");
    expect(logger.warn).toHaveBeenCalledWith(
      "4xx error (418):",
      "Client error",
      unknownHttpError,
    );
  });
});
