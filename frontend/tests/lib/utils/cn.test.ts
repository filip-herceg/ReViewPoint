import type { Mock } from "vitest";
import { describe, expect, it, vi } from "vitest";

// Mock clsx with proper export structure
vi.mock("clsx", () => {
	const clsxMock = vi.fn((inputs: unknown) => {
		if (Array.isArray(inputs)) {
			return inputs.filter(Boolean).join(" ");
		}
		return String(inputs);
	});
	return {
		clsx: clsxMock,
		default: clsxMock,
	};
});

// Mock tailwind-merge
vi.mock("tailwind-merge", () => {
	const twMergeMock = vi.fn((input: unknown) => String(input));
	return { twMerge: twMergeMock };
});

// Mock logger
vi.mock("@/logger", () => ({
	default: {
		debug: vi.fn(),
		info: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	},
}));

import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { cn } from "@/lib/utils";
import logger from "@/logger";
import { testLogger } from "../../test-utils";

const clsxMock = vi.mocked(clsx) as Mock;
const twMergeMock = vi.mocked(twMerge) as Mock;
const loggerMock = vi.mocked(logger);

describe("cn utility", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		console.log("[BeforeEach] twMergeMock state:", twMergeMock);
		clsxMock.mockImplementation((inputs: unknown) => {
			if (Array.isArray(inputs)) {
				return inputs.filter(Boolean).join(" ");
			}
			return String(inputs);
		});
		twMergeMock.mockImplementation((input: unknown) => String(input));
	});

	it("merges class names normally", () => {
		const result = cn("a", "b", "c");
		testLogger.info("Class names merged successfully", {
			inputs: ["a", "b", "c"],
			merged: result,
		});
		expect(result).toBe("a b c");
	});

	it("returns error class and logs if twMerge throws", () => {
		console.log("[Test] Simulating twMerge error");
		twMergeMock.mockImplementationOnce(() => {
			throw new Error("merge fail");
		});
		const result = cn("a", "b");
		expect(result).toBe("error error-class-merge");
		expect(loggerMock.error).toHaveBeenCalled();
	});

	it("returns error class and logs if clsx throws", () => {
		console.log("[Test] Simulating clsx error");
		clsxMock.mockImplementationOnce(() => {
			throw new Error("clsx fail");
		});
		const result = cn("a", "b");
		expect(result).toBe("error error-class-merge");
		expect(loggerMock.error).toHaveBeenCalled();
	});

	it("always returns a string", () => {
		expect(typeof cn("foo", undefined, null)).toBe("string");
	});

	it("handles empty input gracefully", () => {
		clsxMock.mockReturnValueOnce("");
		twMergeMock.mockReturnValueOnce("");
		expect(cn()).toBe("");
	});

	it("returns a space-separated string", () => {
		const result = cn("a", "b", "c");
		expect(result).toBe("a b c");
	});
});

describe("twMerge mock", () => {
	it("should support mockImplementationOnce", () => {
		twMergeMock.mockImplementationOnce(() => "mocked result");
		const result = twMergeMock("a b");
		expect(result).toBe("mocked result");

		// Ensure the mock is reset after use
		twMergeMock.mockImplementation((input: unknown) => String(input));
		expect(twMergeMock("a b")).toBe("a b");
	});
});
