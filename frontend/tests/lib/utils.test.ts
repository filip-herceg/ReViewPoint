import type { ClassValue } from "clsx";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock clsx with proper export structure
vi.mock("clsx", () => {
	const clsxMock = vi.fn((inputs: ClassValue) => {
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
	const twMergeMock = vi.fn((input: string) => input);
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
import { testLogger } from "../test-utils";

const clsxMock = vi.mocked(clsx);
const twMergeMock = vi.mocked(twMerge);
const loggerMock = vi.mocked(logger);

describe("utils.ts", () => {
	describe("cn", () => {
		beforeEach(() => {
			vi.clearAllMocks();
			// Setup default implementations
			clsxMock.mockImplementation((inputs: ClassValue) => {
				if (Array.isArray(inputs)) {
					return inputs.filter(Boolean).join(" ");
				}
				return String(inputs);
			});
			twMergeMock.mockImplementation((...args: unknown[]) => args.join(" "));
		});

		it("merges class names normally", () => {
			const result = cn("a", "b", "c");
			testLogger.info("Class names merged successfully", {
				inputs: ["a", "b", "c"],
				merged: result,
			});
			expect(result).toBe("a b c");
			expect(clsxMock).toHaveBeenCalledWith(["a", "b", "c"]);
			expect(twMergeMock).toHaveBeenCalledWith("a b c");
		});

		it("returns error class and logs if twMerge throws", () => {
			twMergeMock.mockImplementationOnce(() => {
				throw new Error("merge fail");
			});
			const result = cn("a", "b");
			expect(result).toBe("error error-class-merge");
			expect(loggerMock.error).toHaveBeenCalled();
		});

		it("returns error class and logs if clsx throws", () => {
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
	});
});
