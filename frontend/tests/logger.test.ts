import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import logger from "@/logger";
import { createTestError } from "./test-templates";
import { testLogger } from "./test-utils";

// Helper to temporarily set window.LOG_LEVEL
function setLogLevel(level: string) {
  (globalThis as any).window = { LOG_LEVEL: level };
  testLogger.info("Set LOG_LEVEL", level);
}

describe("logger", () => {
  let errorSpy: ReturnType<typeof vi.spyOn>;
  let warnSpy: ReturnType<typeof vi.spyOn>;
  let infoSpy: ReturnType<typeof vi.spyOn>;
  let debugSpy: ReturnType<typeof vi.spyOn>;
  let traceSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    infoSpy = vi.spyOn(console, "info").mockImplementation(() => {});
    debugSpy = vi.spyOn(console, "debug").mockImplementation(() => {});
    traceSpy = vi.spyOn(console, "trace").mockImplementation(() => {});
    setLogLevel("debug");
  });
  afterEach(() => {
    errorSpy.mockRestore();
    warnSpy.mockRestore();
    infoSpy.mockRestore();
    debugSpy.mockRestore();
    traceSpy.mockRestore();
  });

  it("logs error, warn, info, debug, trace at debug level", () => {
    const errObj = createTestError("fail");
    logger.error("err", { foo: "bar" }, errObj);
    logger.warn("warn", 123);
    logger.info("info", true);
    logger.debug("debug", undefined);
    // Ensure log level is set to 'trace' so trace logs are emitted
    setLogLevel("trace");
    logger.trace("trace", null);
    expect(errorSpy).toHaveBeenCalledWith(
      "[ERROR]",
      "err",
      '{"foo":"bar"}',
      errObj,
    );
    expect(warnSpy).toHaveBeenCalledWith("[WARN]", "warn", "123");
    expect(infoSpy).toHaveBeenNthCalledWith(
      1,
      expect.stringMatching(/\[TEST-LOG\] \[info\] \[.*\]/),
      "Set LOG_LEVEL",
      "debug",
    );
    expect(infoSpy).toHaveBeenNthCalledWith(2, "[INFO]", "info", "true");
    expect(infoSpy).toHaveBeenNthCalledWith(
      3,
      expect.stringMatching(/\[TEST-LOG\] \[info\] \[.*\]/),
      "Set LOG_LEVEL",
      "trace",
    );
    expect(debugSpy).toHaveBeenCalledWith("[DEBUG]", "debug", "undefined");
    expect(traceSpy).toHaveBeenCalledWith("[TRACE]", "trace", "null");
    testLogger.info("Logger called all levels at debug");
  });

  it("does not log below current LOG_LEVEL", () => {
    setLogLevel("warn");
    // Clear the spy after setting log level so only logger output is counted
    infoSpy.mockClear();
    debugSpy.mockClear();
    traceSpy.mockClear();
    logger.info("should not log");
    logger.debug("should not log");
    logger.trace("should not log");
    expect(infoSpy).not.toHaveBeenCalled();
    expect(debugSpy).not.toHaveBeenCalled();
    expect(traceSpy).not.toHaveBeenCalled();
    logger.warn("should log");
    logger.error("should log");
    expect(warnSpy).toHaveBeenCalled();
    expect(errorSpy).toHaveBeenCalled();
    testLogger.info("Logger LOG_LEVEL filtering works");
  });

  it("normalizes error objects and primitives", () => {
    const err = createTestError("fail");
    logger.error(err);
    expect(errorSpy).toHaveBeenCalledWith("[ERROR]", err);
    logger.error({ message: "msg" });
    expect(errorSpy).toHaveBeenCalledWith("[ERROR]", '{"message":"msg"}');
    logger.error([1, 2, 3]);
    expect(errorSpy).toHaveBeenCalledWith("[ERROR]", "[1,2,3]");
    logger.error(undefined);
    expect(errorSpy).toHaveBeenCalledWith("[ERROR]", "undefined");
    logger.error(null);
    expect(errorSpy).toHaveBeenCalledWith("[ERROR]", "null");
    testLogger.info("Logger error normalization tested");
  });
});
