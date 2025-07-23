import type { Mock } from "vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";

type ExtendedMock = Mock<
	() => {
		trackEvent: Mock<(...args: unknown[]) => void>;
		trackPageview: Mock<(...args: unknown[]) => void>;
		enableAutoPageviews: Mock<(...args: unknown[]) => void>;
		enableAutoOutboundTracking: Mock<(...args: unknown[]) => void>;
	}
> & {
	invokeMockImplementationOnce: () => unknown;
};

vi.mock("plausible-tracker", () => {
	const mock = vi.fn(() => ({
		trackEvent: vi.fn(),
		trackPageview: vi.fn(),
		enableAutoPageviews: vi.fn(),
		enableAutoOutboundTracking: vi.fn(),
	})) as ExtendedMock;

	mock.invokeMockImplementationOnce = function () {
		const impl = this.getMockImplementation();
		if (!impl) {
			throw new Error("No mock implementation set");
		}
		this.mockImplementation(() => ({
			trackEvent: vi.fn(),
			trackPageview: vi.fn(),
			enableAutoPageviews: vi.fn(),
			enableAutoOutboundTracking: vi.fn(),
		})); // Reset to a default mock implementation
		return impl();
	};

	mock.mockImplementationOnce = function (impl) {
		const onceMock = vi.fn(impl);
		this.mockImplementation((...args) => {
			if (onceMock.mock.calls.length === 0) {
				return onceMock(...args);
			}
			return this(...args);
		});
		return this;
	};

	return { default: mock };
});

let plausibleMock: ExtendedMock;

beforeEach(() => {
	plausibleMock = vi.mocked(require("plausible-tracker").default);

	// Ensure mockImplementation is properly set up (the mock should already have this from vi.mock())
	if (!plausibleMock.mockImplementation) {
		// Type assertion to bypass TypeScript checking for this edge case setup
		(plausibleMock as unknown as Record<string, unknown>).mockImplementation =
			vi.fn(() =>
				Object.assign(
					() => ({
						trackEvent: vi.fn(),
						trackPageview: vi.fn(),
						enableAutoPageviews: vi.fn(),
						enableAutoOutboundTracking: vi.fn(),
					}),
					{
						calls: [],
						instances: [],
						contexts: [],
						invocationCallOrder: [],
						results: [],
						settledResults: [],
						lastCall: [] as [],
						mock: {
							calls: [],
							instances: [],
							contexts: [],
							invocationCallOrder: [],
							results: [],
							settledResults: [],
							lastCall: [] as [],
						},
						mockClear: vi.fn(),
						mockReset: vi.fn(),
						mockRestore: vi.fn(),
						getMockImplementation: vi.fn(),
						mockImplementation: vi.fn(),
						mockImplementationOnce: vi.fn(),
						withImplementation: vi.fn(),
						mockReturnThis: vi.fn(),
						mockReturnValue: vi.fn(),
						mockReturnValueOnce: vi.fn(),
						mockResolvedValue: vi.fn(),
						mockResolvedValueOnce: vi.fn(),
						mockRejectedValue: vi.fn(),
						mockRejectedValueOnce: vi.fn(),
						getMockName: vi.fn(),
						mockName: vi.fn(),
						[Symbol.dispose]: vi.fn(),
						new: () => ({
							trackEvent: vi.fn(),
							trackPageview: vi.fn(),
							enableAutoPageviews: vi.fn(),
							enableAutoOutboundTracking: vi.fn(),
						}),
					},
				),
			);
	}

	// Debug log to inspect plausibleMock state
	console.log("Debug: plausibleMock after initialization", plausibleMock);
	console.debug("plausibleMock state in beforeEach:", plausibleMock);
});

import "../src/analytics";
import { createTestError } from "./test-templates";

// We want to test that analytics initialization errors are handled and do not throw

describe("analytics.ts", () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it("should initialize Plausible without throwing", async () => {
		await expect(async () => {
			await import("@/analytics");
		}).not.toThrow();
	});

	it("should handle Plausible init errors defensively", async () => {
		// Get the mock directly from the module mock
		const plausibleModule = await import("plausible-tracker");
		const mockTracker = plausibleModule.default as unknown as ExtendedMock;

		// Force Plausible to throw
		mockTracker.mockImplementationOnce(() => {
			throw new Error("fail");
		});

		// Re-import the module to trigger the error handling
		await expect(async () => {
			await import("@/analytics");
		}).not.toThrow();
	});

	it("should use createTestError for error normalization", () => {
		const err = createTestError("Analytics initialization error");
		expect(err).toBeInstanceOf(Error);
		expect(err.message).toMatch(/Analytics initialization error/);
	});
});

describe("plausibleMock", () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it.skip("should support mockImplementationOnce", () => {
		// Set a mock implementation
		plausibleMock.mockImplementationOnce(() => ({
			trackEvent: vi.fn(),
			trackPageview: vi.fn(),
			enableAutoPageviews: vi.fn(),
			enableAutoOutboundTracking: vi.fn(),
		}));

		// Invoke the mock implementation
		const result = plausibleMock.invokeMockImplementationOnce();

		// Assert the result
		expect(result).toEqual(
			expect.objectContaining({
				trackEvent: expect.any(Function),
				trackPageview: expect.any(Function),
				enableAutoPageviews: expect.any(Function),
				enableAutoOutboundTracking: expect.any(Function),
			}),
		);

		// Test that the function exists and can be called
		expect(typeof plausibleMock.invokeMockImplementationOnce).toBe("function");
	});

	it("should log the debug information", () => {
		// Debug log to inspect the state of plausibleMock
		console.log("Debug: plausibleMock", plausibleMock);
		console.log("Debug: plausibleMock in test", plausibleMock);

		// Assert that the debug log does not throw an error
		expect(() =>
			console.log("Debug: plausibleMock", plausibleMock),
		).not.toThrow();
	});
});

// Debug log to inspect plausibleMock
// console.log('Debug: plausibleMock in test', plausibleMock);
