import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the logger and request modules to avoid hoisting issues
vi.mock("@/logger", () => ({
  default: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock("@/lib/api/base", () => ({
  request: vi.fn(),
}));

describe("Uploads API", () => {
  let uploadsApi: any;
  let mockRequest: any;
  let mockLogger: any;

  beforeEach(async () => {
    // Reset all mocks
    vi.resetAllMocks();

    // Dynamically import modules to avoid hoisting issues
    const { request } = await import("@/lib/api/base");
    const logger = (await import("@/logger")).default;
    const { uploadsApi: api } = await import("@/lib/api/uploads");

    uploadsApi = api;
    mockRequest = request as any;
    mockLogger = logger;
  });

  describe("Test and diagnostic endpoints", () => {
    it("should test root endpoint successfully", async () => {
      const mockResponse = { status: "ok", router: "uploads" };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.rootTest();

      expect(mockRequest).toHaveBeenCalledWith("/uploads/root-test");
      expect(mockLogger.info).toHaveBeenCalledWith(
        "Testing uploads root endpoint",
      );
      expect(mockLogger.info).toHaveBeenCalledWith("Root test successful");
      expect(result).toEqual(mockResponse);
    });

    it("should test alive endpoint successfully", async () => {
      const mockResponse = { status: "alive" };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.testAlive();

      expect(mockRequest).toHaveBeenCalledWith("/uploads/test-alive");
      expect(mockLogger.info).toHaveBeenCalledWith(
        "Testing uploads alive endpoint",
      );
      expect(mockLogger.info).toHaveBeenCalledWith("Test alive successful");
      expect(result).toEqual(mockResponse);
    });

    it("should test export alive endpoint successfully", async () => {
      const mockResponse = { status: "uploads export alive" };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.exportAlive();

      expect(mockRequest).toHaveBeenCalledWith("/uploads/export-alive");
      expect(mockLogger.info).toHaveBeenCalledWith(
        "Testing uploads export alive endpoint",
      );
      expect(mockLogger.info).toHaveBeenCalledWith("Export alive successful");
      expect(result).toEqual(mockResponse);
    });
  });

  describe("exportFiles", () => {
    it("should export files as CSV successfully", async () => {
      const csvData = "filename,url\ndocument.pdf,/uploads/document.pdf\n";
      mockRequest.mockResolvedValue({ data: csvData });

      const result = await uploadsApi.exportFiles();

      expect(mockRequest).toHaveBeenCalledWith("/uploads/export", {
        headers: {
          Accept: "text/csv",
        },
      });
      expect(mockLogger.info).toHaveBeenCalledWith("Exporting files as CSV", {
        params: undefined,
      });
      expect(mockLogger.info).toHaveBeenCalledWith(
        "Files exported successfully",
      );
      expect(result).toBe(csvData);
    });

    it("should export files with parameters", async () => {
      const params = {
        q: "test",
        sort: "filename" as const,
        order: "asc" as const,
      };
      const csvData = "filename,url\ntest.pdf,/uploads/test.pdf\n";
      mockRequest.mockResolvedValue({ data: csvData });

      const result = await uploadsApi.exportFiles(params);

      expect(mockRequest).toHaveBeenCalledWith(
        "/uploads/export?q=test&sort=filename&order=asc",
        {
          headers: {
            Accept: "text/csv",
          },
        },
      );
      expect(result).toBe(csvData);
    });

    it("should handle export error", async () => {
      const errorMessage = "Export failed";
      mockRequest.mockResolvedValue({ error: errorMessage });

      await expect(uploadsApi.exportFiles()).rejects.toThrow(errorMessage);

      expect(mockLogger.warn).toHaveBeenCalledWith("Export files failed", {
        error: errorMessage,
      });
    });
  });

  describe("uploadFile", () => {
    const mockFile = new File(["test content"], "test.pdf", {
      type: "application/pdf",
    });

    it("should upload file successfully", async () => {
      const mockResponse = { filename: "test.pdf", url: "/uploads/test.pdf" };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.uploadFile(mockFile);

      expect(mockRequest).toHaveBeenCalledWith("/uploads", {
        method: "POST",
        data: expect.any(FormData),
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      expect(mockLogger.info).toHaveBeenCalledWith("Uploading file", {
        filename: "test.pdf",
        size: mockFile.size,
      });
      expect(mockLogger.info).toHaveBeenCalledWith(
        "File uploaded successfully",
        {
          filename: "test.pdf",
          url: "/uploads/test.pdf",
        },
      );
      expect(result).toEqual(mockResponse);
    });

    it("should handle upload error", async () => {
      const errorMessage = "File too large";
      mockRequest.mockResolvedValue({ error: errorMessage });

      await expect(uploadsApi.uploadFile(mockFile)).rejects.toThrow(
        errorMessage,
      );

      expect(mockLogger.warn).toHaveBeenCalledWith("File upload failed", {
        error: errorMessage,
        filename: "test.pdf",
      });
    });
  });

  describe("getFiles", () => {
    it("should fetch files list successfully", async () => {
      const mockResponse = {
        files: [
          { filename: "doc1.pdf", url: "/uploads/doc1.pdf" },
          { filename: "doc2.pdf", url: "/uploads/doc2.pdf" },
        ],
        total: 2,
      };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.getFiles();

      expect(mockRequest).toHaveBeenCalledWith("/uploads");
      expect(mockLogger.info).toHaveBeenCalledWith("Fetching files list", {
        params: undefined,
      });
      expect(mockLogger.info).toHaveBeenCalledWith(
        "Files fetched successfully",
        {
          total: 2,
          count: 2,
        },
      );
      expect(result).toEqual(mockResponse);
    });

    it("should fetch files with parameters", async () => {
      const params = { q: "test", limit: 10, offset: 0 };
      const mockResponse = { files: [], total: 0 };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.getFiles(params);

      expect(mockRequest).toHaveBeenCalledWith(
        "/uploads?q=test&limit=10&offset=0",
      );
      expect(result).toEqual(mockResponse);
    });

    it("should handle fetch error", async () => {
      const errorMessage = "Failed to fetch files";
      mockRequest.mockResolvedValue({ error: errorMessage });

      await expect(uploadsApi.getFiles()).rejects.toThrow(errorMessage);

      expect(mockLogger.warn).toHaveBeenCalledWith("Failed to fetch files", {
        error: errorMessage,
      });
    });
  });

  describe("getFileByFilename", () => {
    it("should fetch file info successfully", async () => {
      const filename = "test.pdf";
      const mockResponse = { filename: "test.pdf", url: "/uploads/test.pdf" };
      mockRequest.mockResolvedValue({ data: mockResponse });

      const result = await uploadsApi.getFileByFilename(filename);

      expect(mockRequest).toHaveBeenCalledWith("/uploads/test.pdf");
      expect(mockLogger.info).toHaveBeenCalledWith("Fetching file info", {
        filename,
      });
      expect(mockLogger.info).toHaveBeenCalledWith(
        "File info fetched successfully",
        {
          filename: "test.pdf",
        },
      );
      expect(result).toEqual(mockResponse);
    });

    it("should handle file not found", async () => {
      const filename = "nonexistent.pdf";
      const errorMessage = "File not found";
      mockRequest.mockResolvedValue({ error: errorMessage });

      await expect(uploadsApi.getFileByFilename(filename)).rejects.toThrow(
        errorMessage,
      );

      expect(mockLogger.warn).toHaveBeenCalledWith(
        "Failed to fetch file info",
        {
          error: errorMessage,
          filename,
        },
      );
    });

    it("should encode filename properly", async () => {
      const filename = "file with spaces.pdf";
      const mockResponse = {
        filename,
        url: "/uploads/file%20with%20spaces.pdf",
      };
      mockRequest.mockResolvedValue({ data: mockResponse });

      await uploadsApi.getFileByFilename(filename);

      expect(mockRequest).toHaveBeenCalledWith(
        "/uploads/file%20with%20spaces.pdf",
      );
    });
  });

  describe("deleteFile", () => {
    it("should delete file successfully", async () => {
      const filename = "test.pdf";
      mockRequest.mockResolvedValue({ data: null });

      await uploadsApi.deleteFile(filename);

      expect(mockRequest).toHaveBeenCalledWith("/uploads/test.pdf", {
        method: "DELETE",
      });
      expect(mockLogger.info).toHaveBeenCalledWith("Deleting file", {
        filename,
      });
      expect(mockLogger.info).toHaveBeenCalledWith(
        "File deleted successfully",
        { filename },
      );
    });

    it("should handle deletion error", async () => {
      const filename = "test.pdf";
      const errorMessage = "File not found";
      mockRequest.mockResolvedValue({ error: errorMessage });

      await expect(uploadsApi.deleteFile(filename)).rejects.toThrow(
        errorMessage,
      );

      expect(mockLogger.warn).toHaveBeenCalledWith("File deletion failed", {
        error: errorMessage,
        filename,
      });
    });

    it("should encode filename properly for deletion", async () => {
      const filename = "file with spaces.pdf";
      mockRequest.mockResolvedValue({ data: null });

      await uploadsApi.deleteFile(filename);

      expect(mockRequest).toHaveBeenCalledWith(
        "/uploads/file%20with%20spaces.pdf",
        {
          method: "DELETE",
        },
      );
    });
  });
});
