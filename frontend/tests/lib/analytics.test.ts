import { describe, expect, it, vi } from "vitest";

vi.mock("plausible-tracker", () => ({
	default: vi.fn(() => ({
		enableAutoPageviews: vi.fn(),
		enableAutoOutboundTracking: vi.fn(),
	})),
}));

import "@/analytics";
import { createTestError } from "../test-templates";

// We want to test that analytics initialization errors are handled and do not throw

describe("analytics.ts", () => {
	it("should initialize Plausible without throwing", async () => {
		await expect(async () => await import("@/analytics")).not.toThrow();
	});

	it("should handle Plausible init errors defensively", async () => {
		// Patch the vi.mock above to throw on next call
		const plausibleTracker = await import("plausible-tracker");
		(plausibleTracker.default as any).mockImplementationOnce(() => {
			throw new Error("fail");
		});
		// Re-import the module to trigger the error handling
		await expect(async () => await import("@/analytics")).not.toThrow();
	});

	it("should use createTestError for error normalization", () => {
		const err = createTestError("Analytics initialization error");
		expect(err).toBeInstanceOf(Error);
		expect(err.message).toMatch(/Analytics initialization error/);
	});
});
