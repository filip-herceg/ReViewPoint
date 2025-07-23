/**
 * File chunking utilities for handling large file uploads
 */

import logger from "@/logger";

export interface FileChunk {
	/** Chunk data */
	data: Blob;
	/** Chunk index (0-based) */
	index: number;
	/** Start byte position */
	start: number;
	/** End byte position */
	end: number;
	/** Chunk size in bytes */
	size: number;
	/** Total file size */
	totalSize: number;
	/** Total number of chunks */
	totalChunks: number;
}

export interface ChunkUploadProgress {
	/** Number of chunks uploaded */
	uploadedChunks: number;
	/** Total number of chunks */
	totalChunks: number;
	/** Total bytes uploaded */
	uploadedBytes: number;
	/** Total file size in bytes */
	totalBytes: number;
	/** Upload progress percentage (0-100) */
	percentage: number;
	/** Upload speed in bytes per second */
	speed: number;
	/** Estimated time remaining in seconds */
	eta: number;
	/** Elapsed time in milliseconds */
	elapsedTime: number;
}

/**
 * Default chunk size (1MB)
 */
export const DEFAULT_CHUNK_SIZE = 1024 * 1024;

/**
 * Maximum chunk size (10MB)
 */
export const MAX_CHUNK_SIZE = 10 * 1024 * 1024;

/**
 * Minimum chunk size (1KB) - reduced for testing flexibility
 */
export const MIN_CHUNK_SIZE = 1024;

/**
 * Split a file into chunks for upload
 */
export function chunkFile(
	file: File,
	chunkSize: number = DEFAULT_CHUNK_SIZE,
): FileChunk[] {
	// Handle null/undefined file gracefully
	if (!file) {
		logger.warn("chunkFile called with null/undefined file");
		return [];
	}

	// Handle empty file
	if (file.size === 0) {
		logger.debug("Empty file provided, returning empty chunks array");
		return [];
	}

	// Validate chunk size
	const validatedChunkSize = Math.max(
		MIN_CHUNK_SIZE,
		Math.min(MAX_CHUNK_SIZE, chunkSize),
	);

	if (validatedChunkSize !== chunkSize) {
		logger.warn("Chunk size adjusted to valid range", {
			requested: chunkSize,
			adjusted: validatedChunkSize,
		});
	}

	const chunks: FileChunk[] = [];
	const totalChunks = Math.ceil(file.size / validatedChunkSize);

	logger.debug("Chunking file", {
		fileName: file.name,
		fileSize: file.size,
		chunkSize: validatedChunkSize,
		totalChunks,
	});

	for (let i = 0; i < totalChunks; i++) {
		const start = i * validatedChunkSize;
		const sliceEnd = Math.min(start + validatedChunkSize, file.size);
		const chunkData = file.slice(start, sliceEnd);
		const end = sliceEnd - 1; // Convert to inclusive end for metadata

		chunks.push({
			data: chunkData,
			index: i,
			start,
			end,
			size: chunkData.size,
			totalSize: file.size,
			totalChunks,
		});
	}

	logger.debug("File chunked successfully", {
		fileName: file.name,
		chunks: chunks.length,
	});

	return chunks;
}

/**
 * Calculate optimal chunk size based on file size
 */
export function calculateOptimalChunkSize(fileSize: number): number {
	// Handle edge cases
	if (fileSize <= 0) {
		return MIN_CHUNK_SIZE;
	}

	// Small files: no chunking needed
	if (fileSize <= MIN_CHUNK_SIZE) {
		return fileSize;
	}

	// Medium files (< 10MB): 256KB chunks
	if (fileSize < 10 * 1024 * 1024) {
		return 256 * 1024;
	}

	// Large files (< 100MB): 1MB chunks
	if (fileSize < 100 * 1024 * 1024) {
		return DEFAULT_CHUNK_SIZE;
	}

	// Very large files (< 1GB): 5MB chunks
	if (fileSize < 1024 * 1024 * 1024) {
		return 5 * 1024 * 1024;
	}

	// Extremely large files: 10MB chunks
	return MAX_CHUNK_SIZE;
}

/**
 * Calculate upload progress across chunks
 */
export function calculateProgress(
	uploadedChunks: number,
	totalChunks: number,
	uploadedBytes: number,
	totalBytes: number,
	startTime: number,
): ChunkUploadProgress {
	// Calculate progress percentage
	const percentage =
		totalBytes > 0 ? Math.min(100, (uploadedBytes / totalBytes) * 100) : 0;

	// Calculate elapsed time and speed
	const elapsedTime = Date.now() - startTime;
	const elapsedSeconds = elapsedTime / 1000;
	const speed = elapsedSeconds > 0 ? uploadedBytes / elapsedSeconds : 0;

	// Calculate ETA
	const remainingBytes = totalBytes - uploadedBytes;
	const eta = speed > 0 ? remainingBytes / speed : 0;

	return {
		uploadedChunks,
		totalChunks,
		uploadedBytes,
		totalBytes,
		percentage,
		speed,
		eta,
		elapsedTime,
	};
}

/**
 * Calculate upload speed and estimated time remaining
 */
export function calculateUploadSpeed(
	startTime: number,
	currentTime: number,
	totalBytesUploaded: number,
	totalSize: number,
): { uploadSpeed: number; estimatedTimeRemaining: number } {
	const elapsedTime = (currentTime - startTime) / 1000; // seconds
	const uploadSpeed = elapsedTime > 0 ? totalBytesUploaded / elapsedTime : 0;

	const remainingBytes = totalSize - totalBytesUploaded;
	const estimatedTimeRemaining =
		uploadSpeed > 0 ? remainingBytes / uploadSpeed : 0;

	return {
		uploadSpeed,
		estimatedTimeRemaining,
	};
}

/**
 * Calculate comprehensive upload metrics for chunks
 */
export function calculateUploadMetrics(
	allChunks: FileChunk[],
	uploadedChunkIndices: number[],
	failedChunkIndices: number[],
): {
	totalChunks: number;
	uploadedChunks: number;
	failedChunks: number;
	pendingChunks: number;
	uploadedBytes: number;
	totalBytes: number;
} {
	const totalChunks = allChunks.length;
	const uploadedChunks = uploadedChunkIndices.length;
	const failedChunks = failedChunkIndices.length;
	const pendingChunks = totalChunks - uploadedChunks - failedChunks;

	// Calculate uploaded bytes
	const uploadedBytes = uploadedChunkIndices.reduce((sum, index) => {
		const chunk = allChunks[index];
		return sum + (chunk ? chunk.size : 0);
	}, 0);

	// Calculate total bytes
	const totalBytes = allChunks.reduce((sum, chunk) => sum + chunk.size, 0);

	return {
		totalChunks,
		uploadedChunks,
		failedChunks,
		pendingChunks,
		uploadedBytes,
		totalBytes,
	};
}

/**
 * Create chunk hash for verification
 */
export async function createChunkHash(chunk: FileChunk): Promise<string> {
	try {
		const arrayBuffer = await chunk.data.arrayBuffer();
		const hashBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
		const hashArray = Array.from(new Uint8Array(hashBuffer));
		const hashHex = hashArray
			.map((b) => b.toString(16).padStart(2, "0"))
			.join("");

		return hashHex;
	} catch (error) {
		logger.error("Failed to create chunk hash", {
			chunkIndex: chunk.index,
			error,
		});
		throw new Error("Chunk hash creation failed");
	}
}

/**
 * Verify chunk integrity
 */
export async function verifyChunk(
	chunk: FileChunk,
	expectedHash: string,
): Promise<boolean> {
	try {
		const actualHash = await createChunkHash(chunk);
		return actualHash === expectedHash;
	} catch (error) {
		logger.error("Chunk verification failed", {
			chunkIndex: chunk.index,
			error,
		});
		return false;
	}
}

/**
 * Combine chunks back into a file (for verification purposes)
 */
export function combineChunks(chunks: FileChunk[]): Blob {
	// Handle empty chunks array
	if (chunks.length === 0) {
		return new Blob([]);
	}

	// Sort chunks by index to ensure correct order
	const sortedChunks = [...chunks].sort((a, b) => a.index - b.index);

	// Verify all chunks are present
	for (let i = 0; i < sortedChunks.length; i++) {
		if (sortedChunks[i].index !== i) {
			throw new Error(`Missing chunk at index ${i}`);
		}
	}

	// Combine chunk data and preserve MIME type from first chunk
	const chunkData = sortedChunks.map((chunk) => chunk.data);
	const firstChunkType = sortedChunks[0]?.data?.type || "";

	return new Blob(chunkData, { type: firstChunkType });
}

/**
 * Get chunk metadata for upload
 */
export function getChunkMetadata(chunk: FileChunk): Record<string, string> {
	return {
		index: chunk.index.toString(),
		start: chunk.start.toString(),
		end: chunk.end.toString(),
		size: chunk.size.toString(),
		totalSize: chunk.totalSize.toString(),
		totalChunks: chunk.totalChunks.toString(),
	};
}

/**
 * Format upload speed for display
 */
export function formatUploadSpeed(bytesPerSecond: number): string {
	if (bytesPerSecond <= 0) return "0 B/s";

	const units = ["B/s", "KB/s", "MB/s", "GB/s"];
	const unitIndex = Math.floor(Math.log(bytesPerSecond) / Math.log(1024));
	const speed = bytesPerSecond / 1024 ** unitIndex;

	// Handle bytes per second case (no decimal)
	if (unitIndex === 0) {
		return `${Math.round(speed)} ${units[unitIndex]}`;
	}

	return `${speed.toFixed(2)} ${units[unitIndex]}`;
}

/**
 * Format time remaining for display
 */
export function formatTimeRemaining(seconds: number): string {
	if (seconds <= 0 || !Number.isFinite(seconds)) {
		return seconds <= 0 ? "0s" : "Unknown";
	}

	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	const remainingSeconds = Math.floor(seconds % 60);

	if (hours > 0) {
		return `${hours}h ${minutes}m ${remainingSeconds}s`;
	} else if (minutes > 0) {
		return `${minutes}m ${remainingSeconds}s`;
	} else {
		return `${remainingSeconds}s`;
	}
}

/**
 * Check if file should be chunked
 */
export function shouldChunkFile(
	file: File,
	threshold: number = DEFAULT_CHUNK_SIZE,
): boolean {
	return file.size > threshold;
}

/**
 * Estimate upload time
 */
export function estimateUploadTime(
	fileSize: number,
	uploadSpeed: number,
): number {
	if (uploadSpeed <= 0 || fileSize <= 0) return 0;
	return fileSize / uploadSpeed;
}

/**
 * Get progress bar segments for chunked upload visualization
 */
export function getProgressSegments(
	totalChunks: number,
	completedChunks: number,
	currentChunkProgress: number,
): Array<{ completed: boolean; progress: number }> {
	const segments: Array<{ completed: boolean; progress: number }> = [];

	for (let i = 0; i < totalChunks; i++) {
		if (i < completedChunks) {
			// Completed chunk
			segments.push({ completed: true, progress: 100 });
		} else if (i === completedChunks) {
			// Current chunk
			segments.push({ completed: false, progress: currentChunkProgress });
		} else {
			// Pending chunk
			segments.push({ completed: false, progress: 0 });
		}
	}

	return segments;
}
