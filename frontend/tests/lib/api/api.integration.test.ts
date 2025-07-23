import axios from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { authApi, uploadsApi } from "@/lib/api";
import type { FileListItem } from "@/lib/api/types";
import { testLogger } from "../../test-utils";

vi.mock("axios", () => {
  const request = vi.fn();
  return {
    default: {
      create: () => ({
        request,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      }),
    },
    create: () => ({
      request,
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
    request,
  };
});
const mockedAxios = axios.create();
const getMockedRequest = () =>
  mockedAxios.request as unknown as ReturnType<typeof vi.fn>;

beforeEach(() => {
  testLogger.info("Resetting mocked Axios request");
  getMockedRequest().mockReset();
});

describe("api utility", () => {
  it("should handle successful login", async () => {
    testLogger.info("Testing successful login");
    const authResponse = {
      access_token: "token123",
      refresh_token: "refresh123",
    };
    getMockedRequest().mockResolvedValueOnce({ data: authResponse });

    const res = await authApi.login({
      email: "test@example.com",
      password: "pw",
    });
    testLogger.debug("Login response", res);
    expect(res.access_token).toBe("token123");
    expect(res.refresh_token).toBe("refresh123");
  });

  it("should handle login error (object)", async () => {
    testLogger.info("Testing login error (object)");
    getMockedRequest().mockRejectedValueOnce({
      response: { data: { error: "Invalid credentials" } },
    });

    await expect(
      authApi.login({ email: "test", password: "badpw" }),
    ).rejects.toThrow("Invalid credentials");
  });

  it("should handle login error (string)", async () => {
    testLogger.info("Testing login error (string)");
    getMockedRequest().mockRejectedValueOnce({ response: { data: "fail" } });

    await expect(
      authApi.login({ email: "test", password: "badpw" }),
    ).rejects.toThrow("fail");
  });

  it("should handle network error", async () => {
    testLogger.info("Testing network error");
    getMockedRequest().mockRejectedValueOnce(new Error("Network error"));

    await expect(
      authApi.login({ email: "test", password: "pw" }),
    ).rejects.toThrow("Network error");
  });

  it("should get files", async () => {
    testLogger.info("Testing listFiles");
    const files: FileListItem[] = [
      { filename: "file.pdf", url: "http://example.com/file.pdf" },
    ];
    const fileListResponse = { files, total: 1 };
    getMockedRequest().mockResolvedValueOnce({ data: fileListResponse });

    const res = await uploadsApi.listFiles();
    testLogger.debug("listFiles response", res);
    expect(res.files).toEqual(files);
    expect(res.total).toBe(1);
  });

  it("should upload file", async () => {
    testLogger.info("Testing uploadFile");
    const fileResponse = {
      filename: "new.pdf",
      url: "http://example.com/new.pdf",
    };
    getMockedRequest().mockResolvedValueOnce({ data: fileResponse });

    const file = new File(["test content"], "new.pdf", {
      type: "application/pdf",
    });
    const res = await uploadsApi.uploadFile(file);
    testLogger.debug("uploadFile response", res);
    expect(res.filename).toBe("new.pdf");
    expect(res.url).toBe("http://example.com/new.pdf");
  });

  it("should handle error on getFile", async () => {
    testLogger.info("Testing error on getFile");
    getMockedRequest().mockRejectedValueOnce({
      response: { data: { message: "Not found" } },
    });

    await expect(uploadsApi.getFile("badfile.pdf")).rejects.toThrow(
      "Not found",
    );
  });

  it("should handle API request failure", async () => {
    testLogger.info("Testing API request failure");
    getMockedRequest().mockRejectedValueOnce(new Error("API request failed"));

    await expect(
      authApi.login({ email: "test", password: "pw" }),
    ).rejects.toThrow("API request failed");
  });
});
