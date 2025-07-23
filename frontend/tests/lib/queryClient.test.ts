import { describe, expect, it } from "vitest";
import { handleApiError } from "@/lib/api/errorHandling";
import { queryClient } from "@/lib/queryClient";
import logger from "@/logger";
// import { createTestError } from '../../../tests/test-templates';
import { createTestError } from "../test-templates"; // Update the path as needed to the correct location

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
		// Define a specific interface for query cache events
		interface QueryCacheEvent {
			type: string;
			action?: { 
				type: string;
				error?: Error;
			};
		}
		
		const errors: Error[] = [];
		const unsubscribe = queryClient.getQueryCache().subscribe((event: QueryCacheEvent) => {
			logger.info("Event captured:", event);
			if (event?.type === "updated" && event.action) {
				logger.info("Updated event action type:", event.action.type);
				if (event.action.type === "error" && event.action.error) {
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
		// Define mutation cache event type
		interface MutationCacheEvent {
			type: string;
			action?: { 
				type: string;
				error?: Error;
			};
		}
		
		const errors: Error[] = [];
		const unsubscribe = queryClient.getMutationCache().subscribe((event: MutationCacheEvent) => {
			if (event?.type === "updated" && event.action && event.action.type === "error" && event.action.error) {
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
		} catch {
			// Expected error for testing error handling
		}
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
		// Define event interfaces
		interface QueryCacheEvent {
			type: string;
			action?: { 
				type: string;
				error?: Error;
			};
			query?: unknown;
		}
		
		interface MutationCacheEvent {
			type: string;
			action?: { 
				type: string;
				error?: Error;
			};
			mutation?: unknown;
		}
		
		// Setup spies for global listeners
		const queryEvents: QueryCacheEvent[] = [];
		const mutationEvents: MutationCacheEvent[] = [];
		const queryListener = (event: QueryCacheEvent) => queryEvents.push(event);
		const mutationListener = (event: MutationCacheEvent) => mutationEvents.push(event);

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
		} catch {
			// Expected error for testing error handling
		}

		// Simulate a mutation error by building a mutation that throws
		const mutation = queryClient.getMutationCache().build(queryClient, {
			mutationFn: async () => {
				throw createTestError("mutation fail");
			},
		});
		try {
			await mutation.execute(undefined);
		} catch {
			// Expected error for testing error handling
		}

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
		const handled = handleApiError(unknownError as unknown);
		expect(handled.type).toBe("unknown");
		expect(handled.message).toBe("Unknown error type");

		// String thrown
		const stringError = "fail string";
		const handledStr = handleApiError(stringError as unknown);
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
		// Need to cast null to string to match function signature
		expect(createTestError(null as unknown as string)).toBeInstanceOf(Error);
		expect(createTestError(null as unknown as string).message).toBe("null");
	});
});
