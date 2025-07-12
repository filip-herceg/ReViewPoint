import { describe, it, expect, beforeEach, afterEach } from "vitest";
import logger from "@/logger";
import {
  UploadErrorType,
  type Upload,
  type File,
  type FileUploadResponse,
  type FileListResponse,
  type FileListItem,
  type FileUploadConfig,
  type FileSearchParams,
  type FileDownloadRequest,
  type FileDeleteRequest,
  type BulkFileOperation,
  type FileSharing,
  type FileUpdateRequest,
  type UploadError,
  type UploadStatus,
  type PaginatedFileListResponse,
  isUpload,
  isFile,
  isUploadError,
  getFileExtension,
  getFileCategory,
  formatFileSize,
  isValidFileType,
  isValidFileSize,
  createUploadFromFile,
  isUploadInProgress,
  isUploadCompleted,
  isUploadFailed,
  SUPPORTED_FILE_TYPES,
  FILE_TYPE_CATEGORIES,
  DEFAULT_UPLOAD_CONFIG,
} from "@/lib/api/types/upload";

// Helper function to create test uploads
function createTestUpload(overrides: Partial<Upload> = {}): Upload {
  return {
    id: "upload-123",
    name: "test-file.pdf",
    status: "completed",
    progress: 100,
    createdAt: new Date().toISOString(),
    size: 1024000,
    type: "application/pdf",
    ...overrides,
  };
}

// Helper function to create test files
function createTestFile(overrides: Partial<File> = {}): File {
  return {
    id: 123,
    filename: "test-file.pdf",
    content_type: "application/pdf",
    user_id: 456,
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

// Helper function to create browser File objects
function createBrowserFile(
  name = "test.pdf",
  type = "application/pdf",
  size = 1024,
): globalThis.File {
  const content = new Array(size).fill("a").join("");
  return new globalThis.File([content], name, { type });
}

describe("Upload Types", () => {
  beforeEach(() => {
    logger.info("Starting upload types test");
  });

  afterEach(() => {
    logger.info("Completed upload types test");
  });

  describe("Type Guards", () => {
    describe("isUpload", () => {
      it("should return true for valid upload objects", () => {
        const upload = createTestUpload();
        expect(isUpload(upload)).toBe(true);
      });

      it("should return false for invalid upload objects", () => {
        expect(isUpload(null)).toBe(false);
        expect(isUpload(undefined)).toBe(false);
        expect(isUpload({})).toBe(false);
        expect(isUpload({ id: "test" })).toBe(false);
      });

      it("should validate required fields", () => {
        const baseUpload = createTestUpload();

        // Test missing required fields
        const uploadWithoutId = { ...baseUpload } as any;
        delete uploadWithoutId.id;
        expect(isUpload(uploadWithoutId)).toBe(false);

        const uploadWithoutName = { ...baseUpload } as any;
        delete uploadWithoutName.name;
        expect(isUpload(uploadWithoutName)).toBe(false);

        const uploadWithoutStatus = { ...baseUpload } as any;
        delete uploadWithoutStatus.status;
        expect(isUpload(uploadWithoutStatus)).toBe(false);

        const uploadWithoutProgress = { ...baseUpload } as any;
        delete uploadWithoutProgress.progress;
        expect(isUpload(uploadWithoutProgress)).toBe(false);
      });
    });

    describe("isFile", () => {
      it("should return true for valid file objects", () => {
        const file = createTestFile();
        expect(isFile(file)).toBe(true);
      });

      it("should return false for invalid file objects", () => {
        expect(isFile(null)).toBe(false);
        expect(isFile(undefined)).toBe(false);
        expect(isFile({})).toBe(false);
        expect(isFile({ id: "test" })).toBe(false);
      });

      it("should validate required fields", () => {
        const baseFile = createTestFile();

        // Test missing required fields
        const fileWithoutId = { ...baseFile } as any;
        delete fileWithoutId.id;
        expect(isFile(fileWithoutId)).toBe(false);

        const fileWithoutFilename = { ...baseFile } as any;
        delete fileWithoutFilename.filename;
        expect(isFile(fileWithoutFilename)).toBe(false);
      });
    });

    describe("isUploadError", () => {
      it("should return true for valid upload error objects", () => {
        const error: UploadError = {
          type: UploadErrorType.FILE_TOO_LARGE,
          message: "File is too large",
        };
        expect(isUploadError(error)).toBe(true);
      });

      it("should return false for invalid upload error objects", () => {
        expect(isUploadError(null)).toBe(false);
        expect(isUploadError(undefined)).toBe(false);
        expect(isUploadError({})).toBe(false);
        expect(isUploadError({ type: "invalid", message: "test" })).toBe(false);
      });
    });
  });

  describe("Utility Functions", () => {
    describe("getFileExtension", () => {
      it("should extract file extensions correctly", () => {
        expect(getFileExtension("document.pdf")).toBe("pdf");
        expect(getFileExtension("image.jpeg")).toBe("jpeg");
        expect(getFileExtension("archive.tar.gz")).toBe("gz");
        expect(getFileExtension("noextension")).toBe("");
        expect(getFileExtension("")).toBe("");
      });
    });

    describe("getFileCategory", () => {
      it("should categorize file types correctly", () => {
        expect(getFileCategory(SUPPORTED_FILE_TYPES.PDF)).toBe("DOCUMENT");
        expect(getFileCategory(SUPPORTED_FILE_TYPES.JPEG)).toBe("IMAGE");
        expect(getFileCategory(SUPPORTED_FILE_TYPES.ZIP)).toBe("ARCHIVE");
        expect(getFileCategory(SUPPORTED_FILE_TYPES.CSV)).toBe("DATA");
        expect(getFileCategory("application/unknown")).toBe("OTHER");
      });
    });

    describe("formatFileSize", () => {
      it("should format file sizes correctly", () => {
        expect(formatFileSize(0)).toBe("0 B");
        expect(formatFileSize(1024)).toBe("1.0 KB");
        expect(formatFileSize(1048576)).toBe("1.0 MB");
        expect(formatFileSize(1073741824)).toBe("1.0 GB");
        expect(formatFileSize(1500)).toBe("1.5 KB");
      });
    });

    describe("isValidFileType", () => {
      it("should validate file types correctly", () => {
        const pdfFile = createBrowserFile("test.pdf", "application/pdf");
        const jpegFile = createBrowserFile("test.jpg", "image/jpeg");

        const allowedTypes = ["application/pdf", "image/jpeg"];

        expect(isValidFileType(pdfFile, allowedTypes)).toBe(true);
        expect(isValidFileType(jpegFile, allowedTypes)).toBe(true);

        const txtFile = createBrowserFile("test.txt", "text/plain");
        expect(isValidFileType(txtFile, allowedTypes)).toBe(false);

        // Test wildcard
        expect(isValidFileType(txtFile, ["*/*"])).toBe(true);
      });
    });

    describe("isValidFileSize", () => {
      it("should validate file sizes correctly", () => {
        const smallFile = createBrowserFile("small.txt", "text/plain", 1024);
        const largeFile = createBrowserFile(
          "large.txt",
          "text/plain",
          5 * 1024 * 1024,
        );

        const maxSize = 2 * 1024 * 1024; // 2 MB

        expect(isValidFileSize(smallFile, maxSize)).toBe(true);
        expect(isValidFileSize(largeFile, maxSize)).toBe(false);
      });
    });

    describe("createUploadFromFile", () => {
      it("should create upload objects from browser files", () => {
        const browserFile = createBrowserFile(
          "test.pdf",
          "application/pdf",
          1024000,
        );
        const upload = createUploadFromFile(browserFile);

        expect(upload.name).toBe("test.pdf");
        expect(upload.status).toBe("pending");
        expect(upload.progress).toBe(0);
        expect(upload.size).toBe(1024000);
        expect(upload.type).toBe("application/pdf");
        expect(typeof upload.id).toBe("string");
        expect(typeof upload.createdAt).toBe("string");
      });
    });

    describe("Upload Status Functions", () => {
      describe("isUploadInProgress", () => {
        it("should identify uploads in progress", () => {
          const uploadingUpload = createTestUpload({ status: "uploading" });
          const pendingUpload = createTestUpload({ status: "pending" });
          const completedUpload = createTestUpload({ status: "completed" });

          expect(isUploadInProgress(uploadingUpload)).toBe(true);
          expect(isUploadInProgress(pendingUpload)).toBe(true);
          expect(isUploadInProgress(completedUpload)).toBe(false);
        });
      });

      describe("isUploadCompleted", () => {
        it("should identify completed uploads", () => {
          const completedUpload = createTestUpload({ status: "completed" });
          const uploadingUpload = createTestUpload({ status: "uploading" });

          expect(isUploadCompleted(completedUpload)).toBe(true);
          expect(isUploadCompleted(uploadingUpload)).toBe(false);
        });
      });

      describe("isUploadFailed", () => {
        it("should identify failed uploads", () => {
          const failedUpload = createTestUpload({ status: "error" });
          const completedUpload = createTestUpload({ status: "completed" });

          expect(isUploadFailed(failedUpload)).toBe(true);
          expect(isUploadFailed(completedUpload)).toBe(false);
        });
      });
    });
  });

  describe("Constants", () => {
    describe("SUPPORTED_FILE_TYPES", () => {
      it("should contain expected file types", () => {
        expect(SUPPORTED_FILE_TYPES.PDF).toBe("application/pdf");
        expect(SUPPORTED_FILE_TYPES.JPEG).toBe("image/jpeg");
        expect(SUPPORTED_FILE_TYPES.PNG).toBe("image/png");
        expect(SUPPORTED_FILE_TYPES.DOC).toBe("application/msword");
        expect(SUPPORTED_FILE_TYPES.ZIP).toBe("application/zip");
      });
    });

    describe("FILE_TYPE_CATEGORIES", () => {
      it("should categorize file types correctly", () => {
        expect(FILE_TYPE_CATEGORIES.DOCUMENT).toContain(
          SUPPORTED_FILE_TYPES.PDF,
        );
        expect(FILE_TYPE_CATEGORIES.IMAGE).toContain(SUPPORTED_FILE_TYPES.JPEG);
        expect(FILE_TYPE_CATEGORIES.ARCHIVE).toContain(
          SUPPORTED_FILE_TYPES.ZIP,
        );
        expect(FILE_TYPE_CATEGORIES.DATA).toContain(SUPPORTED_FILE_TYPES.CSV);
      });
    });

    describe("DEFAULT_UPLOAD_CONFIG", () => {
      it("should have correct default values", () => {
        expect(DEFAULT_UPLOAD_CONFIG.multiple).toBe(true);
        expect(DEFAULT_UPLOAD_CONFIG.maxSize).toBe(10 * 1024 * 1024);
        expect(DEFAULT_UPLOAD_CONFIG.maxFiles).toBe(10);
        expect(DEFAULT_UPLOAD_CONFIG.autoUpload).toBe(false);
        expect(DEFAULT_UPLOAD_CONFIG.chunkSize).toBe(1024 * 1024);
        expect(DEFAULT_UPLOAD_CONFIG.accept).toBeInstanceOf(Array);
      });
    });
  });

  describe("Enums", () => {
    describe("UploadErrorType", () => {
      it("should contain all expected error types", () => {
        expect(UploadErrorType.FILE_TOO_LARGE).toBe("file_too_large");
        expect(UploadErrorType.INVALID_FILE_TYPE).toBe("invalid_file_type");
        expect(UploadErrorType.UPLOAD_FAILED).toBe("upload_failed");
        expect(UploadErrorType.NETWORK_ERROR).toBe("network_error");
        expect(UploadErrorType.SERVER_ERROR).toBe("server_error");
        expect(UploadErrorType.CANCELLED).toBe("cancelled");
        expect(UploadErrorType.QUOTA_EXCEEDED).toBe("quota_exceeded");
        expect(UploadErrorType.VIRUS_DETECTED).toBe("virus_detected");
        expect(UploadErrorType.INVALID_FILENAME).toBe("invalid_filename");
        expect(UploadErrorType.DUPLICATE_FILE).toBe("duplicate_file");
        expect(UploadErrorType.UNKNOWN).toBe("unknown");
      });
    });
  });

  describe("Complex Type Tests", () => {
    describe("FileUploadResponse", () => {
      it("should structure file upload response correctly", () => {
        const response: FileUploadResponse = {
          filename: "test-file.pdf",
          url: "https://example.com/files/test-file.pdf",
        };

        expect(response.filename).toBe("test-file.pdf");
        expect(response.url).toContain("https://");
      });
    });

    describe("FileListResponse", () => {
      it("should structure file list response correctly", () => {
        const response: FileListResponse = {
          files: [
            { filename: "file1.pdf", url: "https://example.com/file1.pdf" },
            { filename: "file2.pdf" },
          ],
          total: 2,
        };

        expect(response.files).toHaveLength(2);
        expect(response.total).toBe(2);
        expect(response.files[0].filename).toBe("file1.pdf");
        expect(response.files[0].url).toBe("https://example.com/file1.pdf");
        expect(response.files[1].filename).toBe("file2.pdf");
        expect(response.files[1].url).toBeUndefined();
      });
    });

    describe("FileSearchParams", () => {
      it("should structure search parameters correctly", () => {
        const params: FileSearchParams = {
          query: "test",
          content_type: "application/pdf",
          extension: "pdf",
          user_id: 123,
          sort_by: "created_at",
          sort_order: "desc",
        };

        expect(params.query).toBe("test");
        expect(params.content_type).toBe("application/pdf");
        expect(params.extension).toBe("pdf");
        expect(params.user_id).toBe(123);
        expect(params.sort_by).toBe("created_at");
        expect(params.sort_order).toBe("desc");
      });
    });

    describe("BulkFileOperation", () => {
      it("should structure bulk operation correctly", () => {
        const operation: BulkFileOperation = {
          file_ids: [1, 2, 3],
          operation: "delete",
          reason: "Cleanup old files",
        };

        expect(operation.file_ids).toEqual([1, 2, 3]);
        expect(operation.operation).toBe("delete");
        expect(operation.reason).toBe("Cleanup old files");
      });
    });

    describe("FileSharing", () => {
      it("should structure file sharing correctly", () => {
        const sharing: FileSharing = {
          file_id: 123,
          is_public: true,
          shared_users: [456, 789],
          expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          password: "secret123",
        };

        expect(sharing.file_id).toBe(123);
        expect(sharing.is_public).toBe(true);
        expect(sharing.shared_users).toEqual([456, 789]);
        expect(typeof sharing.expires_at).toBe("string");
        expect(sharing.password).toBe("secret123");
      });
    });

    describe("UploadError", () => {
      it("should structure upload error correctly", () => {
        const error: UploadError = {
          type: UploadErrorType.FILE_TOO_LARGE,
          message: "File size exceeds maximum allowed size",
          filename: "large-file.pdf",
          details: {
            maxSize: 10 * 1024 * 1024,
            actualSize: 15 * 1024 * 1024,
          },
        };

        expect(error.type).toBe(UploadErrorType.FILE_TOO_LARGE);
        expect(error.message).toContain("File size exceeds");
        expect(error.filename).toBe("large-file.pdf");
        expect(error.details?.maxSize).toBe(10 * 1024 * 1024);
        expect(error.details?.actualSize).toBe(15 * 1024 * 1024);
      });
    });
  });
});
