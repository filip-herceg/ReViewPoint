/**
 * File validation utilities
 * Comprehensive file validation with type detection and content validation
 */

import logger from "@/logger";

export interface FileValidation {
	/** Maximum file size in bytes */
	maxSize?: number;
	/** Minimum file size in bytes */
	minSize?: number;
	/** Allowed MIME types or file extensions */
	allowedTypes?: string[];
	/** Forbidden MIME types or file extensions */
	forbiddenTypes?: string[];
	/** Maximum number of files */
	maxFiles?: number;
	/** Minimum number of files */
	minFiles?: number;
	/** Custom validation function */
	customValidator?: (
		file: File,
	) => Promise<ValidationResult> | ValidationResult;
}

export interface ValidationResult {
	isValid: boolean;
	errors: string[];
	warnings: string[];
}

/**
 * Default validation rules
 */
export const DEFAULT_VALIDATION: FileValidation = {
	maxSize: 100 * 1024 * 1024, // 100MB
	minSize: 1, // 1 byte
	allowedTypes: ["*"], // Allow all types
	forbiddenTypes: [],
	maxFiles: 10,
	minFiles: 1,
};

/**
 * Common file type groups
 */
export const FILE_TYPE_GROUPS = {
	images: [
		"image/jpeg",
		"image/png",
		"image/gif",
		"image/webp",
		"image/svg+xml",
	] as string[],
	documents: [
		"application/pdf",
		"application/msword",
		"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	] as string[],
	spreadsheets: [
		"application/vnd.ms-excel",
		"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	] as string[],
	presentations: [
		"application/vnd.ms-powerpoint",
		"application/vnd.openxmlformats-officedocument.presentationml.presentation",
	] as string[],
	archives: [
		"application/zip",
		"application/x-rar-compressed",
		"application/x-7z-compressed",
	] as string[],
	text: [
		"text/plain",
		"text/csv",
		"text/html",
		"text/css",
		"text/javascript",
	] as string[],
	audio: ["audio/mpeg", "audio/wav", "audio/ogg", "audio/m4a"] as string[],
	video: ["video/mp4", "video/avi", "video/mov", "video/wmv"] as string[],
};

/**
 * Validate a single file
 */
export function validateFile(
	file: File,
	validation: FileValidation = DEFAULT_VALIDATION,
): ValidationResult {
	const errors: string[] = [];
	const warnings: string[] = [];

	logger.debug("Validating file", {
		fileName: file.name,
		fileSize: file.size,
		fileType: file.type,
	});

	try {
		// Size validation
		if (validation.maxSize && file.size > validation.maxSize) {
			errors.push(
				`File size (${formatFileSize(file.size)}) exceeds maximum allowed size (${formatFileSize(validation.maxSize)})`,
			);
		}

		if (validation.minSize && file.size < validation.minSize) {
			errors.push(
				`File size (${formatFileSize(file.size)}) is below minimum required size (${formatFileSize(validation.minSize)})`,
			);
		}

		// Type validation
		if (validation.allowedTypes && !validation.allowedTypes.includes("*")) {
			const isAllowed = validation.allowedTypes.some((allowedType) => {
				if (allowedType.startsWith(".")) {
					// Extension check
					return file.name.toLowerCase().endsWith(allowedType.toLowerCase());
				} else if (allowedType.includes("/")) {
					// MIME type check
					return (
						file.type === allowedType ||
						file.type.startsWith(`${allowedType.split("/")[0]}/`)
					);
				} else {
					// File type group check
					const typeGroup =
						FILE_TYPE_GROUPS[allowedType as keyof typeof FILE_TYPE_GROUPS];
					return typeGroup ? typeGroup.includes(file.type) : false;
				}
			});

			if (!isAllowed) {
				errors.push(
					`File type "${file.type}" is not allowed. Allowed types: ${validation.allowedTypes.join(", ")}`,
				);
			}
		}

		if (validation.forbiddenTypes && validation.forbiddenTypes.length > 0) {
			const isForbidden = validation.forbiddenTypes.some((forbiddenType) => {
				if (forbiddenType.startsWith(".")) {
					return file.name.toLowerCase().endsWith(forbiddenType.toLowerCase());
				} else if (forbiddenType.includes("/")) {
					return file.type === forbiddenType;
				} else {
					const typeGroup =
						FILE_TYPE_GROUPS[forbiddenType as keyof typeof FILE_TYPE_GROUPS];
					return typeGroup ? typeGroup.includes(file.type) : false;
				}
			});

			if (isForbidden) {
				errors.push(`File type "${file.type}" is forbidden`);
			}
		}

		// File name validation
		if (file.name.length === 0) {
			errors.push("File name cannot be empty");
		}

		if (file.name.length > 255) {
			errors.push("File name is too long (maximum 255 characters)");
		}

		// Check for dangerous file extensions
		const dangerousExtensions = [
			".exe",
			".bat",
			".cmd",
			".com",
			".pif",
			".scr",
			".vbs",
			".js",
		];
		const fileExtension = `.${file.name.split(".").pop()?.toLowerCase()}`;
		if (dangerousExtensions.includes(fileExtension)) {
			warnings.push("This file type could potentially be harmful");
		}

		// Empty file check
		if (file.size === 0) {
			warnings.push("File appears to be empty");
		}

		const result: ValidationResult = {
			isValid: errors.length === 0,
			errors,
			warnings,
		};

		logger.debug("File validation completed", {
			fileName: file.name,
			isValid: result.isValid,
			errorCount: errors.length,
			warningCount: warnings.length,
		});

		return result;
	} catch (error) {
		logger.error("File validation failed with exception", {
			fileName: file.name,
			error,
		});
		return {
			isValid: false,
			errors: ["Validation failed due to unexpected error"],
			warnings: [],
		};
	}
}

/**
 * Validate multiple files
 */
export function validateFiles(
	files: File[],
	validation: FileValidation = DEFAULT_VALIDATION,
): ValidationResult {
	const allErrors: string[] = [];
	const allWarnings: string[] = [];

	logger.debug("Validating multiple files", { fileCount: files.length });

	// File count validation
	if (validation.maxFiles && files.length > validation.maxFiles) {
		allErrors.push(
			`Too many files selected (${files.length}). Maximum allowed: ${validation.maxFiles}`,
		);
	}

	if (validation.minFiles && files.length < validation.minFiles) {
		allErrors.push(
			`Not enough files selected (${files.length}). Minimum required: ${validation.minFiles}`,
		);
	}

	// Validate each file
	files.forEach((file, index) => {
		const result = validateFile(file, validation);

		// Prefix errors and warnings with file info
		result.errors.forEach((error) => {
			allErrors.push(`File ${index + 1} (${file.name}): ${error}`);
		});

		result.warnings.forEach((warning) => {
			allWarnings.push(`File ${index + 1} (${file.name}): ${warning}`);
		});
	});

	// Check for duplicate file names
	const fileNames = files.map((file) => file.name.toLowerCase());
	const duplicates = fileNames.filter(
		(name, index) => fileNames.indexOf(name) !== index,
	);
	if (duplicates.length > 0) {
		allWarnings.push(
			`Duplicate file names detected: ${[...new Set(duplicates)].join(", ")}`,
		);
	}

	const result: ValidationResult = {
		isValid: allErrors.length === 0,
		errors: allErrors,
		warnings: allWarnings,
	};

	logger.debug("Multiple file validation completed", {
		fileCount: files.length,
		isValid: result.isValid,
		errorCount: allErrors.length,
		warningCount: allWarnings.length,
	});

	return result;
}

/**
 * Advanced content-based validation
 */
export async function validateFileContent(
	file: File,
): Promise<ValidationResult> {
	const errors: string[] = [];
	const warnings: string[] = [];

	logger.debug("Starting content validation", {
		fileName: file.name,
		fileType: file.type,
	});

	try {
		// Read file header to detect actual file type
		const fileHeader = await readFileHeader(file, 12);
		const detectedType = detectFileTypeFromHeader(fileHeader);

		// Check if detected type matches declared type
		if (
			detectedType &&
			file.type &&
			!isCompatibleType(file.type, detectedType)
		) {
			warnings.push(
				`File type mismatch: declared as "${file.type}" but appears to be "${detectedType}"`,
			);
		}

		// Validate specific file types
		if (file.type.startsWith("image/")) {
			await validateImageFile(file, errors, warnings);
		} else if (file.type === "application/pdf") {
			await validatePdfFile(file, errors, warnings);
		}

		return {
			isValid: errors.length === 0,
			errors,
			warnings,
		};
	} catch (error) {
		logger.error("Content validation failed", { fileName: file.name, error });
		return {
			isValid: false,
			errors: ["Content validation failed"],
			warnings: [],
		};
	}
}

/**
 * Read file header bytes
 */
async function readFileHeader(file: File, bytes: number): Promise<Uint8Array> {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();

		reader.onload = () => {
			const result = reader.result as ArrayBuffer;
			resolve(new Uint8Array(result));
		};

		reader.onerror = () => reject(reader.error);

		const blob = file.slice(0, bytes);
		reader.readAsArrayBuffer(blob);
	});
}

/**
 * Detect file type from header bytes
 */
function detectFileTypeFromHeader(header: Uint8Array): string | null {
	const headerHex = Array.from(header)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");

	// Common file signatures
	const signatures: Record<string, string> = {
		ffd8ff: "image/jpeg",
		"89504e47": "image/png",
		"47494638": "image/gif",
		"52494646": "image/webp",
		"25504446": "application/pdf",
		"504b0304": "application/zip",
		d0cf11e0: "application/msword",
	};

	for (const [signature, mimeType] of Object.entries(signatures)) {
		if (headerHex.startsWith(signature)) {
			return mimeType;
		}
	}

	return null;
}

/**
 * Check if two MIME types are compatible
 */
function isCompatibleType(declared: string, detected: string): boolean {
	// Exact match
	if (declared === detected) return true;

	// Generic matches
	const declaredBase = declared.split("/")[0];
	const detectedBase = detected.split("/")[0];

	return declaredBase === detectedBase;
}

/**
 * Validate image file
 */
async function validateImageFile(
	file: File,
	errors: string[],
	warnings: string[],
): Promise<void> {
	return new Promise((resolve) => {
		// eslint-disable-next-line no-undef
		const img = new Image();

		img.onload = () => {
			// Check image dimensions
			if (img.width === 0 || img.height === 0) {
				errors.push("Invalid image: zero dimensions");
			} else if (img.width > 10000 || img.height > 10000) {
				warnings.push("Very large image dimensions detected");
			}

			URL.revokeObjectURL(img.src);
			resolve();
		};

		img.onerror = () => {
			errors.push("Invalid or corrupted image file");
			URL.revokeObjectURL(img.src);
			resolve();
		};

		img.src = URL.createObjectURL(file);

		// Timeout after 5 seconds
		setTimeout(() => {
			warnings.push("Image validation timed out");
			URL.revokeObjectURL(img.src);
			resolve();
		}, 5000);
	});
}

/**
 * Validate PDF file
 */
async function validatePdfFile(
	file: File,
	errors: string[],
	warnings: string[],
): Promise<void> {
	try {
		const text = await file.text();

		// Basic PDF structure check
		if (!text.startsWith("%PDF-")) {
			errors.push("Invalid PDF: missing PDF header");
		}

		if (!text.includes("%%EOF")) {
			warnings.push("PDF may be incomplete: missing EOF marker");
		}
	} catch {
		warnings.push("Could not read PDF content for validation");
	}
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
	if (bytes === 0) return "0 B";

	const units = ["B", "KB", "MB", "GB", "TB"];
	const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
	const size = bytes / 1024 ** unitIndex;

	return `${size.toFixed(1)} ${units[unitIndex]}`;
}

/**
 * Get file type group
 */
export function getFileTypeGroup(file: File): string {
	for (const [group, types] of Object.entries(FILE_TYPE_GROUPS)) {
		if (types.includes(file.type)) {
			return group;
		}
	}
	return "other";
}

/**
 * Check if file is an image
 */
export function isImageFile(file: File): boolean {
	return file.type.startsWith("image/");
}

/**
 * Check if file is a document
 */
export function isDocumentFile(file: File): boolean {
	return (
		FILE_TYPE_GROUPS.documents.includes(file.type) ||
		FILE_TYPE_GROUPS.spreadsheets.includes(file.type) ||
		FILE_TYPE_GROUPS.presentations.includes(file.type)
	);
}

/**
 * Get file extension
 */
export function getFileExtension(fileName: string): string {
	const lastDotIndex = fileName.lastIndexOf(".");
	return lastDotIndex === -1 ? "" : fileName.substring(lastDotIndex);
}

/**
 * Get filename without extension
 */
export function getFileNameWithoutExtension(fileName: string): string {
	const lastDotIndex = fileName.lastIndexOf(".");
	return lastDotIndex === -1 ? fileName : fileName.substring(0, lastDotIndex);
}
