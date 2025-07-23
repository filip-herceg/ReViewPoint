import { describe, expect, it, vi } from "vitest";
import { cn } from "@/lib/utils";

// Mock twMerge and clsx for error simulation
vi.mock("tailwind-merge", () => ({
  twMerge: vi.fn((...args: any[]) => args.join(" ")),
}));
vi.mock("clsx", () => ({
  clsx: vi.fn((...args: any[]) => args.join(" ")),
}));

describe("utils.ts", () => {
  describe("cn", () => {
    it("merges class names normally", () => {
      expect(cn("a", "b", "c")).toMatch(/a.*b.*c/);
    });

    it("returns error class and logs if twMerge throws", () => {
      const { twMerge } = require("tailwind-merge");
      twMerge.mockImplementationOnce(() => {
        throw new Error("merge fail");
      });
      const result = cn("a", "b");
      expect(result).toMatch(/error-class-merge/);
    });

    it("returns error class and logs if clsx throws", () => {
      // Unmock twMerge to pass through
      const { twMerge } = require("tailwind-merge");
      twMerge.mockImplementation((...args: any[]) => args.join(" "));
      const { clsx } = require("clsx");
      clsx.mockImplementationOnce(() => {
        throw new Error("clsx fail");
      });
      const result = cn("a", "b");
      expect(result).toMatch(/error-class-merge/);
    });

    it("always returns a string", () => {
      expect(typeof cn("foo", undefined, null)).toBe("string");
    });

    it("handles empty input gracefully", () => {
      expect(cn()).toBe("");
    });
  });
});
