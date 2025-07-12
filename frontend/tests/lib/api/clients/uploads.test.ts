/**
 * Tests for the type-safe upload API client
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { uploadApiClient } from "@/lib/api/clients/uploads";
import { server } from "../../../msw-server";
import { http, HttpResponse } from "msw";

// Mock the generated API client
vi.mock("@/lib/api/generated/client", () => ({
  generatedApiClient: {
    GET: vi.fn(),
    POST: vi.fn(),
    DELETE: vi.fn(),
  },
}));

describe("Type-Safe Upload API Client", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset MSW handlers to avoid interference
    server.resetHandlers();
  });

  describe("uploadFile", () => {
    it("should upload a file using fetch directly", async () => {
      // Set up MSW handler for the upload endpoint
      server.use(
        http.post("http://localhost:8000/api/v1/uploads", () => {
          return HttpResponse.json(
            {
              filename: "test.txt",
              url: "/uploads/test.txt",
            },
            { status: 200 },
          );
        }),
      );

      const file = new File(["test content"], "test.txt", {
        type: "text/plain",
      });
      const result = await uploadApiClient.uploadFile(file);

      expect(result).toEqual({
        filename: "test.txt",
        url: "/uploads/test.txt",
      });
    });

    it("should handle upload errors", async () => {
      // Set up MSW handler for error response
      server.use(
        http.post("http://localhost:8000/api/v1/uploads", () => {
          return HttpResponse.text("File too large", {
            status: 400,
            statusText: "Bad Request",
          });
        }),
      );

      const file = new File(["test content"], "test.txt", {
        type: "text/plain",
      });

      await expect(uploadApiClient.uploadFile(file)).rejects.toThrow(
        "Upload failed: 400 Bad Request",
      );
    });
  });

  describe("listFiles", () => {
    it("should list files using generated client", async () => {
      const { generatedApiClient } = await import("@/lib/api/generated/client");

      const mockFiles = {
        files: [
          { filename: "test1.txt", url: "/uploads/test1.txt" },
          { filename: "test2.txt", url: "/uploads/test2.txt" },
        ],
        total: 2,
      };

      (generatedApiClient.GET as any).mockResolvedValue({
        data: mockFiles,
        error: null,
      });

      const result = await uploadApiClient.listFiles();

      expect(generatedApiClient.GET).toHaveBeenCalledWith("/api/v1/uploads", {
        params: {
          query: {},
        },
      });
      expect(result).toEqual(mockFiles);
    });

    it("should handle list files errors", async () => {
      const { generatedApiClient } = await import("@/lib/api/generated/client");

      (generatedApiClient.GET as any).mockResolvedValue({
        data: null,
        error: { message: "Unauthorized" },
      });

      await expect(uploadApiClient.listFiles()).rejects.toThrow();
    });
  });

  describe("getFileInfo", () => {
    it("should get file info using generated client", async () => {
      const { generatedApiClient } = await import("@/lib/api/generated/client");

      const mockFileInfo = {
        filename: "test.txt",
        url: "/uploads/test.txt",
      };

      (generatedApiClient.GET as any).mockResolvedValue({
        data: mockFileInfo,
        error: null,
      });

      const result = await uploadApiClient.getFileInfo("test.txt");

      expect(generatedApiClient.GET).toHaveBeenCalledWith(
        "/api/v1/uploads/{filename}",
        {
          params: {
            path: { filename: "test.txt" },
          },
        },
      );
      expect(result).toEqual(mockFileInfo);
    });
  });

  describe("deleteFile", () => {
    it("should delete file using generated client", async () => {
      const { generatedApiClient } = await import("@/lib/api/generated/client");

      (generatedApiClient.DELETE as any).mockResolvedValue({
        data: {},
        error: null,
      });

      await uploadApiClient.deleteFile("test.txt");

      expect(generatedApiClient.DELETE).toHaveBeenCalledWith(
        "/api/v1/uploads/{filename}",
        {
          params: {
            path: { filename: "test.txt" },
          },
        },
      );
    });
  });

  describe("downloadFile", () => {
    it("should download file by first getting info then fetching content", async () => {
      // Set up MSW handler for file content download using the correct endpoint
      const mockBlob = new Blob(["file content"], { type: "text/plain" });
      server.use(
        http.get(
          "http://localhost:8000/api/v1/uploads/test.txt/download",
          () => {
            return new Response(mockBlob, { status: 200 });
          },
        ),
      );

      const result = await uploadApiClient.downloadFile("test.txt");

      expect(result).toBeDefined();
      expect(typeof result).toBe("object");
      expect(result.constructor.name).toBe("Blob");
      expect(result.size).toBeGreaterThan(0);
    });
  });
});
