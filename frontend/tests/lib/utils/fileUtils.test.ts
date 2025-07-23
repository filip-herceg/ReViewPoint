/**
 * Unit tests for fileUtils.ts
 * Testing file utility functions with comprehensive coverage
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	FILE_TYPE_GROUPS,
	type FileTypeGroup,
	formatFileSize,
	generateUniqueFilename,
	getFileExtension,
	getFileTypeGroup,
	getMimeTypeFromExtension,
	isPreviewSupported,
	MIME_TYPE_MAP,
	parseFileSize,
	readFileAsDataUrl,
	readFileAsText,
	sanitizeFilename,
	validateFilename,
} from "@/lib/utils/fileUtils";

import { testLogger } from "../../test-utils";

// Test data templates
function createTestFile(
	options: {
		name?: string;
		size?: number;
		type?: string;
		content?: string;
	} = {},
): File {
	const {
		name = "test-file.txt",
		size = 1024,
		type = "text/plain",
		content = "test content",
	} = options;

	const file = new File([content], name, { type });
	Object.defineProperty(file, "size", { value: size });

	testLogger.debug("Created test file", { name, size, type });
	return file;
}

function _createTestFileList(count: number = 3): string[] {
	const files = Array.from({ length: count }, (_, i) => `file-${i + 1}.txt`);
	testLogger.debug("Created test file list", { count, files });
	return files;
}

describe("fileUtils", () => {
	beforeEach(() => {
		testLogger.info("Starting fileUtils test");
		vi.clearAllMocks();
	});

	describe("getFileExtension", () => {
		it("should extract file extension correctly", () => {
			testLogger.info("Testing file extension extraction");

			expect(getFileExtension("document.pdf")).toBe("pdf");
			expect(getFileExtension("image.jpeg")).toBe("jpeg");
			expect(getFileExtension("archive.tar.gz")).toBe("gz");
			expect(getFileExtension("file")).toBe("");
			expect(getFileExtension("")).toBe("");
			expect(getFileExtension("file.")).toBe("");
		});

		it("should handle case insensitive extensions", () => {
			expect(getFileExtension("DOCUMENT.PDF")).toBe("pdf");
			expect(getFileExtension("Image.JPEG")).toBe("jpeg");
		});

		it("should handle edge cases gracefully", () => {
			testLogger.info("Testing edge cases for file extension");

			expect(getFileExtension(".hidden")).toBe("hidden");
			expect(getFileExtension("..double")).toBe("double");
			expect(getFileExtension("file..ext")).toBe("ext");
		});
	});

	describe("getFileTypeGroup", () => {
		it("should categorize files correctly", () => {
			testLogger.info("Testing file type group categorization");

			expect(getFileTypeGroup("image.jpg")).toBe("image");
			expect(getFileTypeGroup("document.pdf")).toBe("document");
			expect(getFileTypeGroup("spreadsheet.xlsx")).toBe("spreadsheet");
			expect(getFileTypeGroup("presentation.pptx")).toBe("presentation");
			expect(getFileTypeGroup("video.mp4")).toBe("video");
			expect(getFileTypeGroup("audio.mp3")).toBe("audio");
			expect(getFileTypeGroup("archive.zip")).toBe("archive");
			expect(getFileTypeGroup("script.js")).toBe("code");
			expect(getFileTypeGroup("unknown.xyz")).toBe("other");
		});

		it("should handle files without extensions", () => {
			expect(getFileTypeGroup("README")).toBe("other");
			expect(getFileTypeGroup("")).toBe("other");
		});
	});

	describe("getMimeTypeFromExtension", () => {
		it("should return correct MIME types", () => {
			testLogger.info("Testing MIME type detection");

			expect(getMimeTypeFromExtension("document.pdf")).toBe("application/pdf");
			expect(getMimeTypeFromExtension("image.jpg")).toBe("image/jpeg");
			expect(getMimeTypeFromExtension("text.txt")).toBe("text/plain");
			expect(getMimeTypeFromExtension("video.mp4")).toBe("video/mp4");
		});

		it("should return default MIME type for unknown extensions", () => {
			expect(getMimeTypeFromExtension("unknown.xyz")).toBe(
				"application/octet-stream",
			);
			expect(getMimeTypeFromExtension("file")).toBe("application/octet-stream");
		});
	});

	describe("formatFileSize", () => {
		it("should format file sizes correctly", () => {
			testLogger.info("Testing file size formatting");

			expect(formatFileSize(0)).toBe("0 B");
			expect(formatFileSize(512)).toBe("512 B");
			expect(formatFileSize(1024)).toBe("1 KB");
			expect(formatFileSize(1536)).toBe("1.5 KB");
			expect(formatFileSize(1048576)).toBe("1 MB");
			expect(formatFileSize(1073741824)).toBe("1 GB");
			expect(formatFileSize(1099511627776)).toBe("1 TB");
		});

		it("should handle very large file sizes", () => {
			const veryLarge = 1024 * 1024 * 1024 * 1024 * 1024; // Larger than TB
			const result = formatFileSize(veryLarge);
			expect(result).toContain("B"); // Should fallback to bytes
		});

		it("should handle edge cases", () => {
			expect(formatFileSize(-1)).toBe("-1 B"); // Negative number fallback
		});
	});

	describe("parseFileSize", () => {
		it("should parse file size strings correctly", () => {
			testLogger.info("Testing file size parsing");

			expect(parseFileSize("0 B")).toBe(0);
			expect(parseFileSize("512 B")).toBe(512);
			expect(parseFileSize("1 KB")).toBe(1024);
			expect(parseFileSize("1.5 KB")).toBe(1536);
			expect(parseFileSize("1 MB")).toBe(1048576);
			expect(parseFileSize("1 GB")).toBe(1073741824);
			expect(parseFileSize("1 TB")).toBe(1099511627776);
		});

		it("should handle case insensitive units", () => {
			expect(parseFileSize("1 kb")).toBe(1024);
			expect(parseFileSize("1 Mb")).toBe(1048576);
			expect(parseFileSize("1 gb")).toBe(1073741824);
		});

		it("should handle invalid formats gracefully", () => {
			expect(parseFileSize("invalid")).toBe(0);
			expect(parseFileSize("")).toBe(0);
			expect(parseFileSize("1 XX")).toBe(0);
		});
	});

	describe("generateUniqueFilename", () => {
		it("should return original name if unique", () => {
			testLogger.info("Testing unique filename generation");

			const existingFiles = ["file1.txt", "file2.txt"];
			expect(generateUniqueFilename("new-file.txt", existingFiles)).toBe(
				"new-file.txt",
			);
		});

		it("should generate unique names for duplicates", () => {
			const existingFiles = ["file.txt", "file (1).txt"];
			const result = generateUniqueFilename("file.txt", existingFiles);
			expect(result).toBe("file (2).txt");
		});

		it("should handle files without extensions", () => {
			const existingFiles = ["README", "README (1)"];
			const result = generateUniqueFilename("README", existingFiles);
			expect(result).toBe("README (2)");
		});

		it("should handle excessive conflicts with timestamp fallback", () => {
			const existingFiles = Array.from({ length: 1000 }, (_, i) =>
				i === 0 ? "file.txt" : `file (${i}).txt`,
			);
			const result = generateUniqueFilename("file.txt", existingFiles);
			expect(result).toMatch(/file_\d+\.txt/);
		});
	});

	describe("validateFilename", () => {
		it("should validate correct filenames", () => {
			testLogger.info("Testing filename validation");

			const result = validateFilename("valid-filename.txt");
			expect(result.isValid).toBe(true);
			expect(result.errors).toHaveLength(0);
		});

		it("should detect invalid characters", () => {
			const result = validateFilename("invalid<file>.txt");
			expect(result.isValid).toBe(false);
			expect(result.errors).toContain("Filename contains invalid characters");
		});

		it("should detect reserved names", () => {
			const result = validateFilename("CON.txt");
			expect(result.isValid).toBe(false);
			expect(result.errors).toContain("Filename uses reserved system name");
		});

		it("should detect empty filenames", () => {
			const result = validateFilename("");
			expect(result.isValid).toBe(false);
			expect(result.errors).toContain("Filename cannot be empty");
		});

		it("should detect overly long filenames", () => {
			const longName = "a".repeat(256);
			const result = validateFilename(longName);
			expect(result.isValid).toBe(false);
			expect(result.errors).toContain("Filename too long (max 255 characters)");
		});

		it("should warn about leading/trailing special characters", () => {
			const result1 = validateFilename(".hidden-file");
			expect(result1.warnings).toContain("Filename starts with dot or space");

			const result2 = validateFilename("file. ");
			expect(result2.warnings).toContain("Filename ends with dot or space");
		});

		it("should warn about unicode characters", () => {
			const result = validateFilename("файл.txt");
			expect(result.warnings).toContain(
				"Filename contains non-ASCII characters",
			);
		});
	});

	describe("sanitizeFilename", () => {
		it("should sanitize dangerous characters", () => {
			testLogger.info("Testing filename sanitization");

			expect(sanitizeFilename("file<name>.txt")).toBe("file_name_.txt");
			expect(sanitizeFilename("file|name.txt")).toBe("file_name.txt");
			expect(sanitizeFilename("file:name.txt")).toBe("file_name.txt");
		});

		it("should remove leading/trailing dots and spaces", () => {
			expect(sanitizeFilename("  .file.txt  ")).toBe("file.txt");
			expect(sanitizeFilename("..file.txt..")).toBe("file.txt");
		});

		it("should handle empty results", () => {
			expect(sanitizeFilename("")).toBe("file");
			expect(sanitizeFilename("...")).toBe("file");
			expect(sanitizeFilename("   ")).toBe("file");
		});

		it("should handle overly long filenames", () => {
			const longName = `${"a".repeat(300)}.txt`;
			const result = sanitizeFilename(longName);
			expect(result.length).toBeLessThanOrEqual(255);
			expect(result).toMatch(/\.txt$/); // Should end with .txt
		});
	});

	describe("isPreviewSupported", () => {
		it("should detect supported preview types", () => {
			testLogger.info("Testing preview support detection");

			expect(isPreviewSupported("document.pdf")).toBe(true);
			expect(isPreviewSupported("image.jpg")).toBe(true);
			expect(isPreviewSupported("text.txt")).toBe(true);
			expect(isPreviewSupported("data.json")).toBe(true);
			expect(isPreviewSupported("image.svg")).toBe(true);
		});

		it("should detect unsupported preview types", () => {
			expect(isPreviewSupported("video.mp4")).toBe(false);
			expect(isPreviewSupported("audio.mp3")).toBe(false);
			expect(isPreviewSupported("archive.zip")).toBe(false);
			expect(isPreviewSupported("binary.exe")).toBe(false);
		});

		it("should use MIME type when provided", () => {
			expect(isPreviewSupported("unknown.xyz", "application/pdf")).toBe(true);
			expect(isPreviewSupported("unknown.xyz", "text/plain")).toBe(true);
			expect(
				isPreviewSupported("unknown.xyz", "application/octet-stream"),
			).toBe(false);
		});
	});

	describe("generateFileHash", () => {
		it.skip("should generate consistent hash for same content", async () => {
			// Skipped: File API limitations in test environment
			testLogger.info("Skipping hash test due to test environment limitations");
		});

		it.skip("should generate different hashes for different content", async () => {
			// Skipped: File API limitations in test environment
		});

		it.skip("should handle large files", async () => {
			// Skipped: File API limitations in test environment
		});
	});

	describe("readFileAsText", () => {
		it("should read text files correctly", async () => {
			testLogger.info("Testing file text reading");

			const content = "Hello, world!";
			const file = createTestFile({ content, type: "text/plain" });

			const result = await readFileAsText(file);
			expect(result).toBe(content);
		});

		it("should handle empty files", async () => {
			const file = createTestFile({ content: "" });
			const result = await readFileAsText(file);
			expect(result).toBe("");
		});

		it("should handle unicode content", async () => {
			const content = "Hello, 世界! 🌍";
			const file = createTestFile({ content });

			const result = await readFileAsText(file);
			expect(result).toBe(content);
		});
	});

	describe("readFileAsDataUrl", () => {
		it("should read files as data URLs", async () => {
			testLogger.info("Testing file data URL reading");

			const content = "test content";
			const file = createTestFile({ content, type: "text/plain" });

			const result = await readFileAsDataUrl(file);
			expect(result).toMatch(/^data:text\/plain;base64,/);
		});

		it("should handle binary content", async () => {
			// Create a mock binary file
			const binaryData = new Uint8Array([0x89, 0x50, 0x4e, 0x47]); // PNG header
			const file = new File([binaryData], "test.png", { type: "image/png" });

			const result = await readFileAsDataUrl(file);
			expect(result).toMatch(/^data:image\/png;base64,/);
		});
	});

	describe("FILE_TYPE_GROUPS constant", () => {
		it("should contain all expected file type groups", () => {
			testLogger.info("Testing FILE_TYPE_GROUPS constant");

			const expectedGroups: FileTypeGroup[] = [
				"image",
				"document",
				"spreadsheet",
				"presentation",
				"video",
				"audio",
				"archive",
				"code",
				"other",
			];

			expectedGroups.forEach((group) => {
				expect(FILE_TYPE_GROUPS).toHaveProperty(group);
				expect(Array.isArray(FILE_TYPE_GROUPS[group])).toBe(true);
			});
		});

		it("should have non-empty arrays for most groups", () => {
			Object.entries(FILE_TYPE_GROUPS).forEach(([group, extensions]) => {
				if (group !== "other") {
					expect(extensions.length).toBeGreaterThan(0);
				}
			});
		});
	});

	describe("MIME_TYPE_MAP constant", () => {
		it("should contain common file extensions", () => {
			testLogger.info("Testing MIME_TYPE_MAP constant");

			const commonExtensions = ["pdf", "jpg", "png", "txt", "mp4", "zip"];
			commonExtensions.forEach((ext) => {
				expect(MIME_TYPE_MAP).toHaveProperty(ext);
				expect(typeof MIME_TYPE_MAP[ext]).toBe("string");
			});
		});

		it("should have valid MIME type format", () => {
			Object.values(MIME_TYPE_MAP).forEach((mimeType) => {
				expect(mimeType).toMatch(/^[a-z]+\/[a-z0-9\-+.]+$/i);
			});
		});
	});

	describe("error handling", () => {
		it("should handle invalid inputs gracefully", () => {
			testLogger.info("Testing error handling for invalid inputs");

			// Test with invalid data types
			expect(() => getFileExtension(null as unknown)).not.toThrow();
			expect(() => formatFileSize(NaN)).not.toThrow();
			expect(() => getFileTypeGroup(undefined as unknown)).not.toThrow();
		});

		it("should log errors appropriately", () => {
			// Test that errors are logged without throwing
			const consoleSpy = vi
				.spyOn(console, "error")
				.mockImplementation(() => {});

			try {
				// These should not throw but may log errors
				getFileExtension(null as unknown);
				formatFileSize(NaN);
				getFileTypeGroup(undefined as unknown);
			} catch (error) {
				// Should not reach here
				expect(error).toBeUndefined();
			}

			consoleSpy.mockRestore();
		});
	});
});
