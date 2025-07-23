/**
 * File utility functions for upload and file management
 * Centralized file operations with proper error handling and logging
 */

import logger from "@/logger";

/**
 * File type groups for categorization
 */
export type FileTypeGroup =
	| "image"
	| "document"
	| "spreadsheet"
	| "presentation"
	| "video"
	| "audio"
	| "archive"
	| "code"
	| "other";

/**
 * File validation result structure
 */
export interface FileValidationResult {
	isValid: boolean;
	errors: string[];
	warnings: string[];
}

/**
 * Common file extensions grouped by type
 */
export const FILE_TYPE_GROUPS: Record<FileTypeGroup, string[]> = {
	image: ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico", "tiff"],
	document: ["pdf", "doc", "docx", "txt", "rtf", "odt", "pages"],
	spreadsheet: ["xls", "xlsx", "csv", "ods", "numbers"],
	presentation: ["ppt", "pptx", "odp", "key"],
	video: ["mp4", "avi", "mov", "wmv", "flv", "webm", "mkv", "m4v"],
	audio: ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"],
	archive: ["zip", "rar", "7z", "tar", "gz", "bz2", "xz"],
	code: [
		"js",
		"ts",
		"jsx",
		"tsx",
		"py",
		"java",
		"cpp",
		"c",
		"cs",
		"php",
		"rb",
		"go",
		"rs",
	],
	other: [],
};

/**
 * MIME type mappings for common file types
 */
export const MIME_TYPE_MAP: Record<string, string> = {
	// Images
	jpg: "image/jpeg",
	jpeg: "image/jpeg",
	png: "image/png",
	gif: "image/gif",
	webp: "image/webp",
	svg: "image/svg+xml",
	bmp: "image/bmp",
	ico: "image/x-icon",
	tiff: "image/tiff",

	// Documents
	pdf: "application/pdf",
	doc: "application/msword",
	docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	txt: "text/plain",
	rtf: "application/rtf",
	odt: "application/vnd.oasis.opendocument.text",

	// Spreadsheets
	xls: "application/vnd.ms-excel",
	xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	csv: "text/csv",
	ods: "application/vnd.oasis.opendocument.spreadsheet",

	// Presentations
	ppt: "application/vnd.ms-powerpoint",
	pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
	odp: "application/vnd.oasis.opendocument.presentation",

	// Video
	mp4: "video/mp4",
	avi: "video/x-msvideo",
	mov: "video/quicktime",
	wmv: "video/x-ms-wmv",
	flv: "video/x-flv",
	webm: "video/webm",
	mkv: "video/x-matroska",

	// Audio
	mp3: "audio/mpeg",
	wav: "audio/wav",
	flac: "audio/flac",
	aac: "audio/aac",
	ogg: "audio/ogg",
	wma: "audio/x-ms-wma",

	// Archives
	zip: "application/zip",
	rar: "application/vnd.rar",
	"7z": "application/x-7z-compressed",
	tar: "application/x-tar",
	gz: "application/gzip",
	bz2: "application/x-bzip2",

	// Code
	js: "text/javascript",
	ts: "text/typescript",
	jsx: "text/jsx",
	tsx: "text/tsx",
	py: "text/x-python",
	java: "text/x-java-source",
	cpp: "text/x-c++src",
	c: "text/x-csrc",
	cs: "text/x-csharp",
	php: "text/x-php",
	rb: "text/x-ruby",
	go: "text/x-go",
	rs: "text/x-rust",
};

/**
 * File size units for human-readable formatting
 */
export const FILE_SIZE_UNITS = ["B", "KB", "MB", "GB", "TB"] as const;

/**
 * Extract file extension from filename
 */
export function getFileExtension(filename: string): string {
	try {
		const parts = filename.split(".");
		if (parts.length < 2) {
			logger.debug("No file extension found", { filename });
			return "";
		}

		const extension = parts[parts.length - 1].toLowerCase();
		logger.debug("File extension extracted", { filename, extension });
		return extension;
	} catch (error) {
		logger.error("Error extracting file extension", { error, filename });
		return "";
	}
}

/**
 * Get file type group based on extension
 */
export function getFileTypeGroup(filename: string): FileTypeGroup {
	try {
		const extension = getFileExtension(filename);

		for (const [group, extensions] of Object.entries(FILE_TYPE_GROUPS)) {
			if (extensions.includes(extension)) {
				logger.debug("File type group detected", {
					filename,
					extension,
					group,
				});
				return group as FileTypeGroup;
			}
		}

		logger.debug("Unknown file type, defaulting to other", {
			filename,
			extension,
		});
		return "other";
	} catch (error) {
		logger.error("Error determining file type group", { error, filename });
		return "other";
	}
}

/**
 * Get MIME type from file extension
 */
export function getMimeTypeFromExtension(filename: string): string {
	try {
		const extension = getFileExtension(filename);
		const mimeType = MIME_TYPE_MAP[extension] || "application/octet-stream";

		logger.debug("MIME type determined", { filename, extension, mimeType });
		return mimeType;
	} catch (error) {
		logger.error("Error determining MIME type", { error, filename });
		return "application/octet-stream";
	}
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
	try {
		if (bytes === 0) return "0 B";

		// Handle negative numbers and edge cases
		if (!Number.isFinite(bytes) || bytes < 0) {
			logger.warn("Invalid file size for formatting", { bytes });
			return `${bytes} B`;
		}

		const k = 1024;
		const dm = 2;
		const i = Math.floor(Math.log(bytes) / Math.log(k));

		if (i >= FILE_SIZE_UNITS.length) {
			logger.warn("File size too large for formatting", { bytes });
			return `${bytes} B`;
		}

		const size = parseFloat((bytes / k ** i).toFixed(dm));
		const unit = FILE_SIZE_UNITS[i];
		const formatted = `${size} ${unit}`;

		logger.debug("File size formatted", { bytes, formatted, unit, size });
		return formatted;
	} catch (error) {
		logger.error("Error formatting file size", { error, bytes });
		return `${bytes} B`;
	}
}

/**
 * Parse human-readable file size to bytes
 */
export function parseFileSize(sizeString: string): number {
	try {
		const match = sizeString.trim().match(/^(\d+(?:\.\d+)?)\s*([KMGT]?B)$/i);

		if (!match) {
			logger.warn("Invalid file size format", { sizeString });
			return 0;
		}

		const value = parseFloat(match[1]);
		const unit = match[2].toUpperCase();

		const multipliers: Record<string, number> = {
			B: 1,
			KB: 1024,
			MB: 1024 * 1024,
			GB: 1024 * 1024 * 1024,
			TB: 1024 * 1024 * 1024 * 1024,
		};

		const bytes = value * (multipliers[unit] || 1);
		logger.debug("File size parsed", { sizeString, value, unit, bytes });
		return bytes;
	} catch (error) {
		logger.error("Error parsing file size", { error, sizeString });
		return 0;
	}
}

/**
 * Generate unique filename to avoid conflicts
 */
export function generateUniqueFilename(
	originalName: string,
	existingNames: string[] = [],
): string {
	try {
		if (!existingNames.includes(originalName)) {
			logger.debug("Filename is unique", { originalName });
			return originalName;
		}

		const extension = getFileExtension(originalName);
		const nameWithoutExt = extension
			? originalName.substring(0, originalName.length - extension.length - 1)
			: originalName;

		let counter = 1;
		let uniqueName = "";

		do {
			const suffix = ` (${counter})`;
			uniqueName = extension
				? `${nameWithoutExt}${suffix}.${extension}`
				: `${nameWithoutExt}${suffix}`;
			counter++;
		} while (existingNames.includes(uniqueName) && counter < 1000);

		if (counter >= 1000) {
			// Fallback to timestamp-based naming
			const timestamp = Date.now();
			uniqueName = extension
				? `${nameWithoutExt}_${timestamp}.${extension}`
				: `${nameWithoutExt}_${timestamp}`;
		}

		logger.debug("Unique filename generated", {
			originalName,
			uniqueName,
			attempts: counter - 1,
		});
		return uniqueName;
	} catch (error) {
		logger.error("Error generating unique filename", { error, originalName });
		// Fallback to timestamp-based naming
		const timestamp = Date.now();
		return `${originalName}_${timestamp}`;
	}
}

/**
 * Validate filename for security and compatibility
 */
export function validateFilename(filename: string): FileValidationResult {
	try {
		const errors: string[] = [];
		const warnings: string[] = [];

		// Check filename length
		if (filename.length === 0) {
			errors.push("Filename cannot be empty");
		} else if (filename.length > 255) {
			errors.push("Filename too long (max 255 characters)");
		}

		// Check for dangerous characters
		const dangerousChars = /[<>:"/\\|?*\p{Cc}]/u;
		if (dangerousChars.test(filename)) {
			errors.push("Filename contains invalid characters");
		}

		// Check for reserved names (Windows)
		const reservedNames = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)/i;
		if (reservedNames.test(filename)) {
			errors.push("Filename uses reserved system name");
		}

		// Check for leading/trailing dots or spaces
		if (filename.startsWith(".") || filename.startsWith(" ")) {
			warnings.push("Filename starts with dot or space");
		}

		if (filename.endsWith(".") || filename.endsWith(" ")) {
			warnings.push("Filename ends with dot or space");
		}

		// Check for unicode characters
		const hasUnicode = /[^\p{ASCII}]/u.test(filename);
		if (hasUnicode) {
			warnings.push("Filename contains non-ASCII characters");
		}

		const isValid = errors.length === 0;
		const result: FileValidationResult = {
			isValid,
			errors,
			warnings,
		};

		logger.debug("Filename validation completed", { filename, result });
		return result;
	} catch (error) {
		logger.error("Error validating filename", { error, filename });
		return {
			isValid: false,
			errors: ["Validation error occurred"],
			warnings: [],
		};
	}
}

/**
 * Sanitize filename for safe usage
 */
export function sanitizeFilename(filename: string): string {
	try {
		let sanitized = filename;

		// Replace dangerous characters
		sanitized = sanitized.replace(/[<>:"/\\|?*\p{Cc}]/gu, "_");

		// Remove leading/trailing dots and spaces
		sanitized = sanitized.replace(/^[.\s]+|[.\s]+$/g, "");

		// Ensure not empty after sanitization
		if (sanitized.length === 0) {
			sanitized = "file";
		}

		// Limit length
		if (sanitized.length > 255) {
			const extension = getFileExtension(sanitized);
			const maxNameLength = 255 - (extension ? extension.length + 1 : 0);
			const nameWithoutExt = extension
				? sanitized.substring(0, sanitized.length - extension.length - 1)
				: sanitized;

			sanitized = extension
				? `${nameWithoutExt.substring(0, maxNameLength)}.${extension}`
				: nameWithoutExt.substring(0, 255);
		}

		logger.debug("Filename sanitized", { original: filename, sanitized });
		return sanitized;
	} catch (error) {
		logger.error("Error sanitizing filename", { error, filename });
		return "file";
	}
}

/**
 * Check if file type is supported for preview
 */
export function isPreviewSupported(
	filename: string,
	mimeType?: string,
): boolean {
	try {
		const extension = getFileExtension(filename);
		const type = mimeType || getMimeTypeFromExtension(filename);

		// Supported preview types
		const previewableExtensions = [
			"pdf",
			"txt",
			"md",
			"json",
			"csv",
			"jpg",
			"jpeg",
			"png",
			"gif",
			"webp",
			"svg",
		];

		const previewableMimeTypes = [
			"application/pdf",
			"text/plain",
			"text/markdown",
			"application/json",
			"text/csv",
			"image/jpeg",
			"image/png",
			"image/gif",
			"image/webp",
			"image/svg+xml",
		];

		const isSupported =
			previewableExtensions.includes(extension) ||
			previewableMimeTypes.includes(type);

		logger.debug("Preview support check", {
			filename,
			extension,
			mimeType: type,
			isSupported,
		});
		return isSupported;
	} catch (error) {
		logger.error("Error checking preview support", {
			error,
			filename,
			mimeType,
		});
		return false;
	}
}

/**
 * Generate file hash for integrity checking
 */
export async function generateFileHash(file: File): Promise<string> {
	try {
		logger.debug("Generating file hash", {
			filename: file.name,
			size: file.size,
		});

		// Check if crypto.subtle is available
		if (!globalThis.crypto?.subtle) {
			logger.warn("crypto.subtle not available, using fallback hash", {
				filename: file.name,
			});
			// Fallback to simple hash for environments without crypto.subtle
			const text = await readFileAsText(file);
			const simpleHash = Array.from(text)
				.reduce(
					(acc, char, index) =>
						((acc << 5) - acc + char.charCodeAt(0) + index) & 0xffffffff,
					0,
				)
				.toString(16)
				.padStart(8, "0");
			return simpleHash;
		}

		const buffer = await file.arrayBuffer();
		const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
		const hashArray = Array.from(new Uint8Array(hashBuffer));
		const hashHex = hashArray
			.map((b) => b.toString(16).padStart(2, "0"))
			.join("");

		logger.debug("File hash generated", { filename: file.name, hash: hashHex });
		return hashHex;
	} catch (error) {
		logger.error("Error generating file hash", { error, filename: file.name });
		throw new Error("Failed to generate file hash");
	}
}

/**
 * Read file as text (for text files)
 */
export async function readFileAsText(file: File): Promise<string> {
	try {
		logger.debug("Reading file as text", {
			filename: file.name,
			size: file.size,
		});

		return new Promise((resolve, reject) => {
			const reader = new FileReader();

			reader.onload = () => {
				const text = reader.result as string;
				logger.debug("File read as text", {
					filename: file.name,
					length: text.length,
				});
				resolve(text);
			};

			reader.onerror = () => {
				const error = new Error("Failed to read file as text");
				logger.error("Error reading file as text", {
					error,
					filename: file.name,
				});
				reject(error);
			};

			reader.readAsText(file);
		});
	} catch (error) {
		logger.error("Error reading file as text", { error, filename: file.name });
		throw new Error("Failed to read file as text");
	}
}

/**
 * Read file as data URL (for images)
 */
export async function readFileAsDataUrl(file: File): Promise<string> {
	try {
		logger.debug("Reading file as data URL", {
			filename: file.name,
			size: file.size,
		});

		return new Promise((resolve, reject) => {
			const reader = new FileReader();

			reader.onload = () => {
				const dataUrl = reader.result as string;
				logger.debug("File read as data URL", {
					filename: file.name,
					dataUrlLength: dataUrl.length,
				});
				resolve(dataUrl);
			};

			reader.onerror = () => {
				const error = new Error("Failed to read file as data URL");
				logger.error("Error reading file as data URL", {
					error,
					filename: file.name,
				});
				reject(error);
			};

			reader.readAsDataURL(file);
		});
	} catch (error) {
		logger.error("Error reading file as data URL", {
			error,
			filename: file.name,
		});
		throw new Error("Failed to read file as data URL");
	}
}

/**
 * Generate a unique upload ID
 */
export function generateUploadId(): string {
	return `upload_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
}
