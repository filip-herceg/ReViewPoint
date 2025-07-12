import { describe, it, expect } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { handleApiError } from "@/lib/api/errorHandling";
// import { createTestError } from '../../../tests/test-templates';
import { createTestError } from "../test-templates"; // Update the path as needed to the correct location
import { queryClient } from "@/lib/queryClient";

import logger from "@/logger";

describe("queryClient error handling config", () => {
  it("has correct defaultOptions for queries", () => {
    const opts = queryClient.getDefaultOptions();
    expect(opts.queries?.retry).toBe(1);
    expect(opts.queries?.refetchOnWindowFocus).toBe(false);
    expect(opts.queries?.staleTime).toBe(1000 * 60);
  });

  it("has correct defaultOptions for mutations", () => {
    const opts = queryClient.getDefaultOptions();
    expect(opts.mutations?.retry).toBe(0);
  });

  it("can be used to handle errors in hooks/components", () => {
    // Simulate a hook/component using handleApiError
    const error = new Error("fail");
    const handled = handleApiError(error);
    expect(handled.message).toMatch(/fail/i);
  });

  it("can use createTestError for normalization", () => {
    const err = createTestError("fail");
    expect(err).toBeInstanceOf(Error);
    expect(err.message).toBe("fail");
  });

  it("can subscribe to global query errors via queryCache", async () => {
    const errors: any[] = [];
    const unsubscribe = queryClient.getQueryCache().subscribe((event) => {
      logger.info("Event captured:", event);
      if (event?.type === "updated") {
        logger.info("Updated event action type:", event.action.type);
        if (event.action.type === "error") {
          logger.error("Captured error event:", event.action.error);
          errors.push(event.action.error);
        }
      }
    });
    // Simulate a query error
    const query = queryClient.getQueryCache().build(queryClient, {
      queryKey: ["test"],
      queryFn: async () => {
        throw new Error("global error");
      },
    });
    logger.info("Query built:", query);
    logger.info("Query state before fetch:", query.state);
    try {
      await query.fetch();
    } catch (err) {
      logger.error("Error thrown during fetch:", err);
    }
    logger.info("Query state after fetch:", query.state);
    logger.info("Errors array after fetch:", errors);
    unsubscribe();
    logger.info("Errors captured after unsubscribe:", errors);
    // Check that we captured at least one error
    expect(errors.length).toBeGreaterThan(0);
  });

  it("can subscribe to global mutation errors via mutationCache", async () => {
    const errors: any[] = [];
    const unsubscribe = queryClient.getMutationCache().subscribe((event) => {
      if (event?.type === "updated" && event.action.type === "error") {
        errors.push(event.action.error);
      }
    });
    // Simulate a mutation error
    const mutation = queryClient.getMutationCache().build(queryClient, {
      mutationKey: ["test-mutation"],
      mutationFn: async () => {
        throw new Error("mutation error");
      },
    });
    try {
      await mutation.execute(undefined);
    } catch {}
    unsubscribe();
    // Check that we captured at least one error
    expect(errors.length).toBeGreaterThan(0);
  });

  it("handles advanced error normalization scenarios", () => {
    // Non-Error thrown value
    const handled = handleApiError("not an error");
    expect(handled.message).toBe("not an error");
    // Axios-like error
    const axiosError = {
      isAxiosError: true,
      response: { status: 500, data: { error: "fail" } },
    };
    const handledAxios = handleApiError(axiosError);
    expect(handledAxios.type).toBe("5xx");
    expect(handledAxios.message).toMatch(/fail/i);
  });
  it("invokes global queryCache and mutationCache listeners and handles errors", async () => {
    // Setup spies for global listeners
    const queryEvents: any[] = [];
    const mutationEvents: any[] = [];
    const queryListener = (event: any) => queryEvents.push(event);
    const mutationListener = (event: any) => mutationEvents.push(event);

    // Register listeners
    const unsubscribeQuery = queryClient
      .getQueryCache()
      .subscribe(queryListener);
    const unsubscribeMutation = queryClient
      .getMutationCache()
      .subscribe(mutationListener);

    // Simulate a query error by building a query that throws
    const query = queryClient.getQueryCache().build(queryClient, {
      queryKey: ["test-listener"],
      queryFn: async () => {
        throw createTestError("query fail");
      },
    });
    try {
      await query.fetch();
    } catch {}

    // Simulate a mutation error by building a mutation that throws
    const mutation = queryClient.getMutationCache().build(queryClient, {
      mutationFn: async () => {
        throw createTestError("mutation fail");
      },
    });
    try {
      await mutation.execute(undefined);
    } catch {}

    unsubscribeQuery();
    unsubscribeMutation();

    // Check that listeners received error events
    // For query, look for event.type === 'updated' && event.action.type === 'error'
    expect(
      queryEvents.some(
        (e) => e?.type === "updated" && e.action?.type === "error",
      ),
    ).toBe(true);
    // For mutation, look for event.type === 'updated' && e.action.type === 'error'
    expect(
      mutationEvents.some(
        (e) => e?.type === "updated" && e.action?.type === "error",
      ),
    ).toBe(true);
  });

  it("normalizes unknown and non-Error types in error handling", () => {
    // Unknown thrown value
    const unknownError = { foo: "bar" };
    const handled = handleApiError(unknownError as any);
    expect(handled.type).toBe("unknown");
    expect(handled.message).toBe("Unknown error type");

    // String thrown
    const stringError = "fail string";
    const handledStr = handleApiError(stringError as any);
    expect(handledStr.type).toBe("unknown");
    expect(handledStr.message).toBe("fail string");
  });

  it("handles edge cases for createTestError", () => {
    // Passing an Error instance
    const err = new Error("already error");
    const result = createTestError(err);
    expect(result).toBe(err);

    // Passing undefined
    expect(createTestError(undefined)).toBeInstanceOf(Error);
    // Passing null (cast to any to bypass TS)
    expect(createTestError(null as any)).toBeInstanceOf(Error);
    expect(createTestError(null as any).message).toBe("null");
  });
});
