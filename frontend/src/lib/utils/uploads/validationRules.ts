import type {
	FileMetadataExtract,
	FileValidationError,
	FileValidationResult,
	FileValidationWarning,
} from "@/lib/api/types/upload";
import {
	DEFAULT_UPLOAD_CONFIG,
	getFileCategory,
	getFileExtension,
	SUPPORTED_FILE_TYPES,
} from "@/lib/api/types/upload";
import logger from "@/logger";

/**
 * Custom validation rule function
 */
export type ValidationRule = (
	file: File,
) => Promise<FileValidationError[]> | FileValidationError[];

/**
 * Security validation configuration
 */
export interface SecurityValidationConfig {
	/** Check for malicious file patterns */
	checkMaliciousPatterns: boolean;
	/** Validate file headers */
	validateFileHeaders: boolean;
	/** Check for embedded scripts */
	checkEmbeddedScripts: boolean;
	/** Maximum filename length */
	maxFilenameLength: number;
	/** Blocked filename patterns */
	blockedPatterns: RegExp[];
}

/**
 * Content validation configuration
 */
export interface ContentValidationConfig {
	/** Extract file metadata */
	extractMetadata: boolean;
	/** Validate image dimensions */
	validateImageDimensions: boolean;
	/** Maximum image dimensions */
	maxImageDimensions: { width: number; height: number };
	/** Validate PDF structure */
	validatePdfStructure: boolean;
	/** Maximum PDF pages */
	maxPdfPages: number;
}

/**
 * Advanced validation rules configuration
 */
export interface ValidationConfig {
	/** Basic file validation */
	basic: {
		maxSize: number;
		allowedTypes: string[];
		allowedExtensions: string[];
	};
	/** Security validation */
	security: SecurityValidationConfig;
	/** Content validation */
	content: ContentValidationConfig;
	/** Custom validation rules */
	customRules: ValidationRule[];
}

/**
 * File signature patterns for header validation
 */
const FILE_SIGNATURES: Record<string, { pattern: number[]; offset: number }[]> =
	{
		"application/pdf": [{ pattern: [0x25, 0x50, 0x44, 0x46], offset: 0 }], // %PDF
		"image/jpeg": [
			{ pattern: [0xff, 0xd8, 0xff], offset: 0 }, // JPEG
		],
		"image/png": [
			{ pattern: [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a], offset: 0 },
		], // PNG
		"image/gif": [
			{ pattern: [0x47, 0x49, 0x46, 0x38, 0x37, 0x61], offset: 0 }, // GIF87a
			{ pattern: [0x47, 0x49, 0x46, 0x38, 0x39, 0x61], offset: 0 }, // GIF89a
		],
		"application/zip": [
			{ pattern: [0x50, 0x4b, 0x03, 0x04], offset: 0 }, // ZIP
			{ pattern: [0x50, 0x4b, 0x05, 0x06], offset: 0 }, // Empty ZIP
		],
	};

/**
 * Malicious file patterns to detect
 */
const MALICIOUS_PATTERNS = {
	filename: [
		/\.(exe|com|bat|cmd|scr|pif|vbs|js|jar|app|deb|pkg|dmg)$/i,
		/\.(php|asp|jsp|py|rb|pl)$/i,
		/\..*\.(exe|com|bat)$/i, // Double extension
		/\p{Cc}|\p{Cf}/u, // Control and format characters
	],
	content: [
		/<script[\s\S]*?>[\s\S]*?<\/script\s*>/gi,
		/<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi,
		/<object[\s\S]*?>[\s\S]*?<\/object>/gi,
		/<embed[\s\S]*?>/gi,
	],
};

/**
 * Default validation configuration
 */
const DEFAULT_VALIDATION_CONFIG: ValidationConfig = {
	basic: {
		maxSize: DEFAULT_UPLOAD_CONFIG.maxSize ?? 10 * 1024 * 1024, // 10MB fallback
		allowedTypes:
			DEFAULT_UPLOAD_CONFIG.accept ?? Object.values(SUPPORTED_FILE_TYPES),
		allowedExtensions: Object.keys(SUPPORTED_FILE_TYPES).map((k) =>
			k.toLowerCase(),
		),
	},
	security: {
		checkMaliciousPatterns: true,
		validateFileHeaders: true,
		checkEmbeddedScripts: true,
		maxFilenameLength: 255,
		blockedPatterns: MALICIOUS_PATTERNS.filename,
	},
	content: {
		extractMetadata: true,
		validateImageDimensions: true,
		maxImageDimensions: { width: 10000, height: 10000 },
		validatePdfStructure: true,
		maxPdfPages: 1000,
	},
	customRules: [],
};

/**
 * Advanced file validation utility
 */
export class FileValidator {
	private config: ValidationConfig;

	constructor(config: Partial<ValidationConfig> = {}) {
		this.config = {
			basic: { ...DEFAULT_VALIDATION_CONFIG.basic, ...config.basic },
			security: { ...DEFAULT_VALIDATION_CONFIG.security, ...config.security },
			content: { ...DEFAULT_VALIDATION_CONFIG.content, ...config.content },
			customRules: config.customRules || DEFAULT_VALIDATION_CONFIG.customRules,
		};

		logger.debug("File validator initialized", { config: this.config });
	}

	/**
	 * Validate a file with all configured rules
	 */
	async validateFile(file: File): Promise<FileValidationResult> {
		logger.info("Starting file validation", {
			fileName: file.name,
			fileSize: file.size,
			fileType: file.type,
		});

		const errors: FileValidationError[] = [];
		const warnings: FileValidationWarning[] = [];
		let metadata: FileMetadataExtract | undefined;

		try {
			// Basic validation
			errors.push(...this.validateBasic(file));

			// Security validation
			if (
				this.config.security.checkMaliciousPatterns ||
				this.config.security.validateFileHeaders ||
				this.config.security.checkEmbeddedScripts
			) {
				errors.push(...(await this.validateSecurity(file)));
			}

			// Content validation
			if (
				this.config.content.extractMetadata ||
				this.config.content.validateImageDimensions ||
				this.config.content.validatePdfStructure
			) {
				const contentResult = await this.validateContent(file);
				errors.push(...contentResult.errors);
				warnings.push(...contentResult.warnings);
				metadata = contentResult.metadata;
			}

			// Custom validation rules
			for (const rule of this.config.customRules) {
				try {
					const ruleErrors = await rule(file);
					errors.push(...ruleErrors);
				} catch (error) {
					logger.error("Custom validation rule failed", {
						error,
						fileName: file.name,
					});
					errors.push({
						code: "CUSTOM_VALIDATION_ERROR",
						message: "Custom validation rule failed",
						field: "custom",
						severity: "error",
					});
				}
			}
		} catch (error) {
			logger.error("File validation failed", { error, fileName: file.name });
			errors.push({
				code: "VALIDATION_ERROR",
				message: "Validation process failed",
				field: "validation",
				severity: "error",
			});
		}

		const result: FileValidationResult = {
			isValid: errors.filter((e) => e.severity === "error").length === 0,
			errors,
			warnings,
			metadata,
		};

		logger.info("File validation completed", {
			fileName: file.name,
			isValid: result.isValid,
			errorCount: errors.length,
			warningCount: warnings.length,
		});

		return result;
	}

	/**
	 * Basic file validation (size, type, extension)
	 */
	private validateBasic(file: File): FileValidationError[] {
		const errors: FileValidationError[] = [];

		// File size validation
		if (file.size > this.config.basic.maxSize) {
			errors.push({
				code: "FILE_TOO_LARGE",
				message: `File size ${this.formatBytes(file.size)} exceeds maximum allowed size of ${this.formatBytes(this.config.basic.maxSize)}`,
				field: "size",
				severity: "error",
			});
		}

		if (file.size === 0) {
			errors.push({
				code: "FILE_EMPTY",
				message: "File is empty",
				field: "size",
				severity: "error",
			});
		}

		// File type validation
		if (!this.config.basic.allowedTypes.includes(file.type)) {
			errors.push({
				code: "INVALID_FILE_TYPE",
				message: `File type '${file.type || "unknown"}' is not allowed`,
				field: "type",
				severity: "error",
			});
		}

		// File extension validation
		const extension = getFileExtension(file.name);
		if (
			extension &&
			!this.config.basic.allowedExtensions.includes(extension.toLowerCase())
		) {
			errors.push({
				code: "INVALID_FILE_EXTENSION",
				message: `File extension '.${extension}' is not allowed`,
				field: "extension",
				severity: "error",
			});
		}

		// Filename validation
		if (!file.name || file.name.trim().length === 0) {
			errors.push({
				code: "EMPTY_FILENAME",
				message: "File name cannot be empty",
				field: "name",
				severity: "error",
			});
		}

		if (file.name.length > this.config.security.maxFilenameLength) {
			errors.push({
				code: "FILENAME_TOO_LONG",
				message: `Filename is too long (${file.name.length} characters). Maximum allowed: ${this.config.security.maxFilenameLength}`,
				field: "name",
				severity: "error",
			});
		}

		logger.debug("Basic validation completed", {
			fileName: file.name,
			errorCount: errors.length,
		});

		return errors;
	}

	/**
	 * Security validation (malicious patterns, headers)
	 */
	private async validateSecurity(file: File): Promise<FileValidationError[]> {
		const errors: FileValidationError[] = [];

		// Check malicious filename patterns
		if (this.config.security.checkMaliciousPatterns) {
			for (const pattern of this.config.security.blockedPatterns) {
				if (pattern.test(file.name)) {
					errors.push({
						code: "MALICIOUS_FILENAME",
						message: "Filename contains suspicious patterns",
						field: "name",
						severity: "error",
					});
					break;
				}
			}
		}

		// Validate file headers
		if (this.config.security.validateFileHeaders) {
			try {
				const headerErrors = await this.validateFileHeader(file);
				errors.push(...headerErrors);
			} catch (error) {
				logger.error("File header validation failed", {
					error,
					fileName: file.name,
				});
				errors.push({
					code: "HEADER_VALIDATION_ERROR",
					message: "Could not validate file header",
					field: "header",
					severity: "warning",
				} as FileValidationError);
			}
		}

		// Check for embedded scripts (for text-based files)
		if (
			this.config.security.checkEmbeddedScripts &&
			this.isTextBasedFile(file)
		) {
			try {
				const scriptErrors = await this.checkEmbeddedScripts(file);
				errors.push(...scriptErrors);
			} catch (error) {
				logger.error("Script validation failed", {
					error,
					fileName: file.name,
				});
			}
		}

		logger.debug("Security validation completed", {
			fileName: file.name,
			errorCount: errors.length,
		});

		return errors;
	}

	/**
	 * Content validation (dimensions, structure)
	 */
	private async validateContent(file: File): Promise<{
		errors: FileValidationError[];
		warnings: FileValidationWarning[];
		metadata?: FileMetadataExtract;
	}> {
		const errors: FileValidationError[] = [];
		const warnings: FileValidationWarning[] = [];
		let metadata: FileMetadataExtract | undefined;

		const category = getFileCategory(file.type);

		try {
			if (category === "IMAGE" && this.config.content.validateImageDimensions) {
				const imageResult = await this.validateImage(file);
				errors.push(...imageResult.errors);
				warnings.push(...imageResult.warnings);
				metadata = { ...metadata, ...imageResult.metadata };
			}

			if (
				file.type === "application/pdf" &&
				this.config.content.validatePdfStructure
			) {
				const pdfResult = await this.validatePdf(file);
				errors.push(...pdfResult.errors);
				warnings.push(...pdfResult.warnings);
				metadata = { ...metadata, ...pdfResult.metadata };
			}

			if (this.config.content.extractMetadata) {
				const extractedMetadata = await this.extractFileMetadata(file);
				metadata = { ...metadata, ...extractedMetadata };
			}
		} catch (error) {
			logger.error("Content validation failed", { error, fileName: file.name });
			errors.push({
				code: "CONTENT_VALIDATION_ERROR",
				message: "Content validation failed",
				field: "content",
				severity: "warning",
			} as FileValidationError);
		}

		logger.debug("Content validation completed", {
			fileName: file.name,
			errorCount: errors.length,
			warningCount: warnings.length,
		});

		return { errors, warnings, metadata };
	}

	/**
	 * Validate file header against expected signature
	 */
	private async validateFileHeader(file: File): Promise<FileValidationError[]> {
		const errors: FileValidationError[] = [];

		if (!file.type || !FILE_SIGNATURES[file.type]) {
			return errors;
		}

		try {
			const header = await this.readFileHeader(file, 20); // Read first 20 bytes
			const signatures = FILE_SIGNATURES[file.type];

			let signatureValid = false;
			for (const sig of signatures) {
				if (this.matchesSignature(header, sig.pattern, sig.offset)) {
					signatureValid = true;
					break;
				}
			}

			if (!signatureValid) {
				errors.push({
					code: "INVALID_FILE_HEADER",
					message: `File header does not match expected signature for type '${file.type}'`,
					field: "header",
					severity: "error",
				});
			}
		} catch (error) {
			logger.error("Header validation error", { error, fileName: file.name });
		}

		return errors;
	}

	/**
	 * Check for embedded scripts in text-based files
	 */
	private async checkEmbeddedScripts(
		file: File,
	): Promise<FileValidationError[]> {
		const errors: FileValidationError[] = [];

		try {
			const content = await this.readFileAsText(file);

			for (const pattern of MALICIOUS_PATTERNS.content) {
				if (pattern.test(content)) {
					errors.push({
						code: "EMBEDDED_SCRIPT_DETECTED",
						message: "File contains potentially malicious embedded scripts",
						field: "content",
						severity: "error",
					});
					break;
				}
			}
		} catch (error) {
			logger.error("Script check error", { error, fileName: file.name });
		}

		return errors;
	}

	/**
	 * Validate image file
	 */
	private async validateImage(file: File): Promise<{
		errors: FileValidationError[];
		warnings: FileValidationWarning[];
		metadata: Partial<FileMetadataExtract>;
	}> {
		const errors: FileValidationError[] = [];
		const warnings: FileValidationWarning[] = [];
		const metadata: Partial<FileMetadataExtract> = {};

		try {
			const dimensions = await this.getImageDimensions(file);
			metadata.dimensions = dimensions;

			if (
				dimensions.width > this.config.content.maxImageDimensions.width ||
				dimensions.height > this.config.content.maxImageDimensions.height
			) {
				errors.push({
					code: "IMAGE_TOO_LARGE",
					message: `Image dimensions ${dimensions.width}x${dimensions.height} exceed maximum allowed ${this.config.content.maxImageDimensions.width}x${this.config.content.maxImageDimensions.height}`,
					field: "dimensions",
					severity: "error",
				});
			}

			// Warn about very large images
			if (dimensions.width * dimensions.height > 25000000) {
				// 25 megapixels
				warnings.push({
					code: "LARGE_IMAGE_WARNING",
					message: "Image is very large and may consume significant memory",
					field: "dimensions",
					severity: "warning",
				});
			}
		} catch (error) {
			logger.error("Image validation error", { error, fileName: file.name });
			errors.push({
				code: "IMAGE_VALIDATION_ERROR",
				message: "Could not validate image",
				field: "image",
				severity: "warning",
			} as FileValidationError);
		}

		return { errors, warnings, metadata };
	}

	/**
	 * Validate PDF file
	 */
	private async validatePdf(file: File): Promise<{
		errors: FileValidationError[];
		warnings: FileValidationWarning[];
		metadata: Partial<FileMetadataExtract>;
	}> {
		const errors: FileValidationError[] = [];
		const warnings: FileValidationWarning[] = [];
		const metadata: Partial<FileMetadataExtract> = {};

		try {
			// Basic PDF structure validation would go here
			// For now, we'll just extract some basic metadata
			const content = await this.readFileAsText(file, "utf-8", 1024); // Read first 1KB

			// Simple page count estimation (very basic)
			const pageMatches = content.match(/%Page/g);
			if (pageMatches) {
				const estimatedPages = pageMatches.length;
				metadata.pageCount = estimatedPages;

				if (estimatedPages > this.config.content.maxPdfPages) {
					errors.push({
						code: "PDF_TOO_MANY_PAGES",
						message: `PDF has too many pages (${estimatedPages}). Maximum allowed: ${this.config.content.maxPdfPages}`,
						field: "pages",
						severity: "error",
					});
				}
			}
		} catch (error) {
			logger.error("PDF validation error", { error, fileName: file.name });
			errors.push({
				code: "PDF_VALIDATION_ERROR",
				message: "Could not validate PDF structure",
				field: "pdf",
				severity: "warning",
			} as FileValidationError);
		}

		return { errors, warnings, metadata };
	}

	/**
	 * Extract basic file metadata
	 */
	private async extractFileMetadata(
		file: File,
	): Promise<Partial<FileMetadataExtract>> {
		const metadata: Partial<FileMetadataExtract> = {};

		try {
			// Extract basic metadata
			metadata.createdDate = new Date(file.lastModified);
			metadata.modifiedDate = new Date(file.lastModified);

			// For text files, extract preview
			if (this.isTextBasedFile(file) && file.size < 1024 * 1024) {
				// Only for files < 1MB
				const content = await this.readFileAsText(file, "utf-8", 500);
				metadata.preview = content.substring(0, 200);
			}
		} catch (error) {
			logger.error("Metadata extraction error", { error, fileName: file.name });
		}

		return metadata;
	}

	// Helper methods

	private async readFileHeader(file: File, bytes: number): Promise<Uint8Array> {
		return new Promise((resolve, reject) => {
			const slice = file.slice(0, bytes);
			const reader = new FileReader();

			reader.onload = () => {
				if (reader.result instanceof ArrayBuffer) {
					resolve(new Uint8Array(reader.result));
				} else {
					reject(new Error("Failed to read file header"));
				}
			};

			reader.onerror = () => reject(reader.error);
			reader.readAsArrayBuffer(slice);
		});
	}

	private async readFileAsText(
		file: File,
		encoding = "utf-8",
		maxBytes?: number,
	): Promise<string> {
		return new Promise((resolve, reject) => {
			const slice = maxBytes ? file.slice(0, maxBytes) : file;
			const reader = new FileReader();

			reader.onload = () => {
				if (typeof reader.result === "string") {
					resolve(reader.result);
				} else {
					reject(new Error("Failed to read file as text"));
				}
			};

			reader.onerror = () => reject(reader.error);
			reader.readAsText(slice, encoding);
		});
	}

	private async getImageDimensions(
		file: File,
	): Promise<{ width: number; height: number }> {
		return new Promise((resolve, reject) => {
			// eslint-disable-next-line no-undef
			const img = new Image();
			const url = URL.createObjectURL(file);

			img.onload = () => {
				URL.revokeObjectURL(url);
				resolve({ width: img.naturalWidth, height: img.naturalHeight });
			};

			img.onerror = () => {
				URL.revokeObjectURL(url);
				reject(new Error("Failed to load image"));
			};

			img.src = url;
		});
	}

	private matchesSignature(
		header: Uint8Array,
		pattern: number[],
		offset: number,
	): boolean {
		if (header.length < offset + pattern.length) {
			return false;
		}

		for (let i = 0; i < pattern.length; i++) {
			if (header[offset + i] !== pattern[i]) {
				return false;
			}
		}

		return true;
	}

	private isTextBasedFile(file: File): boolean {
		return (
			file.type.startsWith("text/") ||
			file.type === "application/json" ||
			file.type === "application/xml" ||
			file.type.includes("svg")
		);
	}

	private formatBytes(bytes: number): string {
		if (bytes === 0) return "0 B";
		const k = 1024;
		const sizes = ["B", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return `${parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`;
	}
}

/**
 * Create validation rules for specific file types
 */
export const createFileTypeRules = {
	/**
	 * PDF-specific validation rules
	 */
	pdf: (): ValidationRule => async (file: File) => {
		const errors: FileValidationError[] = [];

		if (file.type !== "application/pdf") {
			return errors;
		}

		// Add PDF-specific validation logic here
		if (file.size > 50 * 1024 * 1024) {
			// 50MB
			errors.push({
				code: "PDF_TOO_LARGE",
				message: "PDF files should be smaller than 50MB for optimal processing",
				field: "size",
				severity: "warning",
			} as FileValidationError);
		}

		return errors;
	},

	/**
	 * Image-specific validation rules
	 */
	image:
		(maxMegapixels = 25): ValidationRule =>
		async (file: File) => {
			const errors: FileValidationError[] = [];

			if (!file.type.startsWith("image/")) {
				return errors;
			}

			// Add image-specific validation logic here
			try {
				// eslint-disable-next-line no-undef
				const img = new Image();
				const url = URL.createObjectURL(file);

				await new Promise((resolve, reject) => {
					img.onload = resolve;
					img.onerror = reject;
					img.src = url;
				});

				const megapixels = (img.naturalWidth * img.naturalHeight) / 1000000;
				if (megapixels > maxMegapixels) {
					errors.push({
						code: "IMAGE_HIGH_RESOLUTION",
						message: `Image resolution is very high (${megapixels.toFixed(1)} megapixels). Consider resizing for better performance.`,
						field: "resolution",
						severity: "warning",
					} as FileValidationError);
				}

				URL.revokeObjectURL(url);
			} catch {
				// Non-critical error
			}

			return errors;
		},
};

/**
 * Create a new file validator instance
 */
export function createFileValidator(
	config?: Partial<ValidationConfig>,
): FileValidator {
	return new FileValidator(config);
}

/**
 * Default file validator instance
 */
export const defaultFileValidator = createFileValidator();
