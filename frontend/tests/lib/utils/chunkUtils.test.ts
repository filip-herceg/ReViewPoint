/**
 * Unit tests for chunkUtils.ts
 * Testing file chunking utilities with comprehensive coverage
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	type ChunkUploadProgress,
	calculateOptimalChunkSize,
	calculateProgress,
	calculateUploadMetrics,
	chunkFile,
	combineChunks,
	DEFAULT_CHUNK_SIZE,
	estimateUploadTime,
	type FileChunk,
	formatTimeRemaining,
	formatUploadSpeed,
	getChunkMetadata,
	MAX_CHUNK_SIZE,
	MIN_CHUNK_SIZE,
	shouldChunkFile,
} from "@/lib/utils/chunkUtils";
import { testLogger } from "../../test-utils";

// Test data templates
function createTestFile(size: number, content?: string): File {
	const data = content || "x".repeat(size);
	const file = new File([data], "test-file.txt", { type: "text/plain" });
	Object.defineProperty(file, "size", { value: size });
	testLogger.debug("Created test file", { size, actualSize: file.size });
	return file;
}

function createTestChunk(options: Partial<FileChunk> = {}): FileChunk {
	const defaults: FileChunk = {
		index: 0,
		start: 0,
		end: 1023,
		size: 1024,
		totalSize: 10240,
		totalChunks: 10,
		data: new Blob(["x".repeat(1024)], { type: "text/plain" }),
	};

	const chunk = { ...defaults, ...options };
	testLogger.debug("Created test chunk", chunk);
	return chunk;
}

function _createTestProgress(
	options: Partial<ChunkUploadProgress> = {},
): ChunkUploadProgress {
	const defaults: ChunkUploadProgress = {
		uploadedChunks: 0,
		totalChunks: 10,
		uploadedBytes: 0,
		totalBytes: 10240,
		percentage: 0,
		speed: 0,
		eta: 0,
		elapsedTime: 0,
	};

	const progress = { ...defaults, ...options };
	testLogger.debug("Created test progress", progress);
	return progress;
}

describe("chunkUtils", () => {
	beforeEach(() => {
		testLogger.info("Starting chunkUtils test");
		vi.clearAllMocks();
	});

	describe("chunkFile", () => {
		it("should create chunks from a file", () => {
			testLogger.info("Testing chunk creation from file");

			const file = createTestFile(5000);
			const chunkSize = 1024;

			const chunks = chunkFile(file, chunkSize);

			expect(chunks).toHaveLength(5); // ceil(5000/1024) = 5
			expect(chunks[0].start).toBe(0);
			expect(chunks[0].end).toBe(1023);
			expect(chunks[0].size).toBe(1024);
			expect(chunks[0].index).toBe(0);

			// Last chunk should be smaller
			expect(chunks[4].start).toBe(4096);
			expect(chunks[4].end).toBe(4999);
			expect(chunks[4].size).toBe(904); // 5000 - 4096
			expect(chunks[4].index).toBe(4);
		});

		it("should handle small files that fit in one chunk", () => {
			const file = createTestFile(500);
			const chunkSize = 1024;

			const chunks = chunkFile(file, chunkSize);

			expect(chunks).toHaveLength(1);
			expect(chunks[0].start).toBe(0);
			expect(chunks[0].end).toBe(499);
			expect(chunks[0].size).toBe(500);
		});

		it("should handle edge case of empty file", () => {
			const file = createTestFile(0);
			const chunks = chunkFile(file, 1024);

			expect(chunks).toHaveLength(0);
		});

		it("should handle exact multiple of chunk size", () => {
			const file = createTestFile(2048);
			const chunks = chunkFile(file, 1024);

			expect(chunks).toHaveLength(2);
			expect(chunks[1].start).toBe(1024);
			expect(chunks[1].end).toBe(2047);
			expect(chunks[1].size).toBe(1024);
		});

		it("should use default chunk size when not specified", () => {
			const file = createTestFile(DEFAULT_CHUNK_SIZE * 2);
			const chunks = chunkFile(file);

			expect(chunks).toHaveLength(2);
			expect(chunks[0].size).toBe(DEFAULT_CHUNK_SIZE);
		});
	});

	describe("calculateOptimalChunkSize", () => {
		it("should calculate appropriate chunk size for different file sizes", () => {
			testLogger.info("Testing optimal chunk size calculation");

			// Small file
			const smallChunkSize = calculateOptimalChunkSize(1024 * 100); // 100KB
			expect(smallChunkSize).toBeGreaterThanOrEqual(MIN_CHUNK_SIZE);
			expect(smallChunkSize).toBeLessThanOrEqual(MAX_CHUNK_SIZE);

			// Large file
			const largeChunkSize = calculateOptimalChunkSize(1024 * 1024 * 100); // 100MB
			expect(largeChunkSize).toBeGreaterThanOrEqual(MIN_CHUNK_SIZE);
			expect(largeChunkSize).toBeLessThanOrEqual(MAX_CHUNK_SIZE);

			// Very large file should use max chunk size
			const veryLargeChunkSize = calculateOptimalChunkSize(1024 * 1024 * 1024); // 1GB
			expect(veryLargeChunkSize).toBeLessThanOrEqual(MAX_CHUNK_SIZE);
		});

		it("should handle edge cases", () => {
			expect(calculateOptimalChunkSize(0)).toBeGreaterThan(0);
			expect(calculateOptimalChunkSize(-1)).toBeGreaterThan(0);
		});
	});

	describe("calculateProgress", () => {
		it("should calculate progress correctly", () => {
			testLogger.info("Testing progress calculation");

			const totalChunks = 10;
			const totalBytes = 10240;
			const uploadedChunks = 3;
			const uploadedBytes = 3072;
			const startTime = Date.now() - 5000; // 5 seconds ago

			const progress = calculateProgress(
				uploadedChunks,
				totalChunks,
				uploadedBytes,
				totalBytes,
				startTime,
			);

			expect(progress.uploadedChunks).toBe(3);
			expect(progress.totalChunks).toBe(10);
			expect(progress.uploadedBytes).toBe(3072);
			expect(progress.totalBytes).toBe(10240);
			expect(progress.percentage).toBe(30); // 3/10 * 100
			expect(progress.speed).toBeGreaterThan(0); // Should have calculated speed
			expect(progress.eta).toBeGreaterThan(0); // Should have calculated ETA
		});

		it("should handle no uploaded chunks", () => {
			const progress = calculateProgress(0, 5, 0, 5120, Date.now());

			expect(progress.uploadedChunks).toBe(0);
			expect(progress.percentage).toBe(0);
			expect(progress.uploadedBytes).toBe(0);
			expect(progress.speed).toBe(0);
			expect(progress.eta).toBe(0);
		});

		it("should handle all chunks uploaded", () => {
			const progress = calculateProgress(3, 3, 3072, 3072, Date.now() - 1000);

			expect(progress.uploadedChunks).toBe(3);
			expect(progress.percentage).toBe(100);
			expect(progress.eta).toBe(0); // No time remaining
		});
	});

	describe("createChunkHash", () => {
		it.skip("should generate hash for chunk", async () => {
			// Skipped: Crypto API limitations in test environment
			testLogger.info(
				"Skipping chunk hash test due to test environment limitations",
			);
		});
	});

	describe("verifyChunk", () => {
		it.skip("should verify chunk against hash", async () => {
			// Skipped: Crypto API limitations in test environment
			testLogger.info(
				"Skipping chunk verification test due to test environment limitations",
			);
		});
	});

	describe("combineChunks", () => {
		it("should combine chunks in correct order", () => {
			testLogger.info("Testing chunk combination");

			const chunk1 = createTestChunk({
				index: 0,
				data: new Blob(["Hello"], { type: "text/plain" }),
			});

			const chunk2 = createTestChunk({
				index: 1,
				data: new Blob([" World"], { type: "text/plain" }),
			});

			const chunks = [chunk1, chunk2];
			const combinedBlob = combineChunks(chunks);

			expect(combinedBlob.size).toBe(11); // 5 + 6
			expect(combinedBlob.type).toBe("text/plain");
		});

		it("should handle single chunk", () => {
			const chunk = createTestChunk({
				data: new Blob(["Hello"], { type: "text/plain" }),
			});

			const combinedBlob = combineChunks([chunk]);
			expect(combinedBlob.size).toBe(5);
		});

		it("should handle empty chunks array", () => {
			const combinedBlob = combineChunks([]);
			expect(combinedBlob.size).toBe(0);
		});
	});

	describe("getChunkMetadata", () => {
		it("should extract chunk metadata", () => {
			testLogger.info("Testing chunk metadata extraction");

			const chunk = createTestChunk({
				index: 5,
				start: 1024,
				end: 2047,
				size: 1024,
			});

			const metadata = getChunkMetadata(chunk);

			expect(metadata).toHaveProperty("index", "5");
			expect(metadata).toHaveProperty("start", "1024");
			expect(metadata).toHaveProperty("end", "2047");
			expect(metadata).toHaveProperty("size", "1024");
		});
	});

	describe("formatUploadSpeed", () => {
		it("should format upload speed correctly", () => {
			testLogger.info("Testing upload speed formatting");

			expect(formatUploadSpeed(1024)).toBe("1.00 KB/s");
			expect(formatUploadSpeed(1048576)).toBe("1.00 MB/s");
			expect(formatUploadSpeed(1073741824)).toBe("1.00 GB/s");
			expect(formatUploadSpeed(512)).toBe("512 B/s");
		});

		it("should handle edge cases", () => {
			expect(formatUploadSpeed(0)).toBe("0 B/s");
			expect(formatUploadSpeed(-1)).toBe("0 B/s"); // Should handle negative values
		});
	});

	describe("formatTimeRemaining", () => {
		it("should format time remaining correctly", () => {
			testLogger.info("Testing time remaining formatting");

			expect(formatTimeRemaining(30)).toBe("30s");
			expect(formatTimeRemaining(90)).toBe("1m 30s");
			expect(formatTimeRemaining(3661)).toBe("1h 1m 1s");
			expect(formatTimeRemaining(7200)).toBe("2h 0m 0s");
		});

		it("should handle edge cases", () => {
			expect(formatTimeRemaining(0)).toBe("0s");
			expect(formatTimeRemaining(-1)).toBe("0s"); // Should handle negative values
		});
	});

	describe("shouldChunkFile", () => {
		it("should determine if file should be chunked", () => {
			testLogger.info("Testing file chunking decision");

			const smallFile = createTestFile(1024); // 1KB
			const largeFile = createTestFile(DEFAULT_CHUNK_SIZE * 2); // 2MB

			expect(shouldChunkFile(smallFile)).toBe(false);
			expect(shouldChunkFile(largeFile)).toBe(true);
		});

		it("should use custom threshold", () => {
			const file = createTestFile(2048); // 2KB
			const threshold = 1024; // 1KB

			expect(shouldChunkFile(file, threshold)).toBe(true);
		});
	});

	describe("estimateUploadTime", () => {
		it("should estimate upload time correctly", () => {
			testLogger.info("Testing upload time estimation");

			const fileSize = 1024 * 1024; // 1MB
			const uploadSpeed = 1024 * 100; // 100KB/s

			const estimatedTime = estimateUploadTime(fileSize, uploadSpeed);
			expect(estimatedTime).toBe(10.24); // 1MB / 100KB/s = 10.24s
		});

		it("should handle edge cases", () => {
			expect(estimateUploadTime(1024, 0)).toBe(0); // No speed
			expect(estimateUploadTime(0, 1024)).toBe(0); // No file
		});
	});

	describe("calculateUploadMetrics", () => {
		it("should calculate upload metrics", () => {
			testLogger.info("Testing upload metrics calculation");

			const chunks = Array.from({ length: 10 }, (_, i) =>
				createTestChunk({ index: i, size: 1024 }),
			);

			const uploadedChunks = [0, 1, 2, 5]; // 4 chunks uploaded
			const failedChunks = [3, 4]; // 2 chunks failed

			const metrics = calculateUploadMetrics(
				chunks,
				uploadedChunks,
				failedChunks,
			);

			expect(metrics.totalChunks).toBe(10);
			expect(metrics.uploadedChunks).toBe(4);
			expect(metrics.failedChunks).toBe(2);
			expect(metrics.pendingChunks).toBe(4); // 10 - 4 - 2 = 4
			expect(metrics.uploadedBytes).toBe(4096); // 4 * 1024
			expect(metrics.totalBytes).toBe(10240); // 10 * 1024
		});

		it("should handle no uploaded or failed chunks", () => {
			const chunks = Array.from({ length: 5 }, (_, i) =>
				createTestChunk({ index: i }),
			);

			const metrics = calculateUploadMetrics(chunks, [], []);

			expect(metrics.uploadedChunks).toBe(0);
			expect(metrics.failedChunks).toBe(0);
			expect(metrics.pendingChunks).toBe(5);
		});
	});

	describe("constants", () => {
		it("should have valid chunk size constants", () => {
			testLogger.info("Testing chunk size constants");

			expect(typeof DEFAULT_CHUNK_SIZE).toBe("number");
			expect(typeof MAX_CHUNK_SIZE).toBe("number");
			expect(typeof MIN_CHUNK_SIZE).toBe("number");

			expect(DEFAULT_CHUNK_SIZE).toBeGreaterThan(0);
			expect(MAX_CHUNK_SIZE).toBeGreaterThanOrEqual(DEFAULT_CHUNK_SIZE);
			expect(MIN_CHUNK_SIZE).toBeLessThanOrEqual(DEFAULT_CHUNK_SIZE);
		});
	});

	describe("error handling", () => {
		it("should handle invalid inputs gracefully", () => {
			testLogger.info("Testing error handling for invalid inputs");

			// Test with null/undefined inputs
			expect(() => chunkFile(null as any, 1024)).not.toThrow();
			expect(() => calculateProgress(0, 0, 0, 0, Date.now())).not.toThrow();
			expect(() => combineChunks([])).not.toThrow();
		});

		it("should handle edge cases in calculations", () => {
			const progress = calculateProgress(0, 0, 0, 0, Date.now());

			expect(progress.percentage).toBe(0); // Should handle 0/0 case gracefully
		});
	});
});
