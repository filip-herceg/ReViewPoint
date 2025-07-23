import { describe, expect, it } from "vitest";
import { getErrorMessage } from "@/lib/utils/errorHandling";

describe("getErrorMessage", () => {
	it("returns string for string error", () => {
		expect(getErrorMessage("fail")).toBe("fail");
	});
	it("returns message for error object", () => {
		expect(getErrorMessage({ message: "bad" })).toBe("bad");
	});
	it("returns fallback for non-message object", () => {
		expect(getErrorMessage({ foo: 1 })).toBe("Unknown error type");
	});
	it("returns Unknown error for null/undefined", () => {
		expect(getErrorMessage(undefined)).toBe("Unknown error");
		expect(getErrorMessage(null as unknown)).toBe("Unknown error");
	});
	it("returns message for Error instance", () => {
		expect(getErrorMessage(new Error("fail"))).toBe("fail");
	});
	it("returns string representation for number", () => {
		expect(getErrorMessage(42 as unknown)).toBe("42");
	});
	it("returns string representation for boolean", () => {
		expect(getErrorMessage(true as unknown)).toBe("true");
		expect(getErrorMessage(false as unknown)).toBe("false");
	});
	it("returns fallback for array", () => {
		expect(getErrorMessage([1, 2, 3] as unknown)).toBe("Unknown error type");
	});
});
