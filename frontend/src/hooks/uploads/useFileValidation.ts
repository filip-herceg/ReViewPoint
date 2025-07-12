import { useState, useCallback } from "react";
import logger from "@/logger";
import type {
  FileValidationResult,
  FileValidationError,
  FileValidationWarning,
  FileMetadataExtract,
  FileTypeCategory,
} from "@/lib/api/types/upload";
import {
  getFileExtension,
  getFileCategory,
  isValidFileType,
  isValidFileSize,
  SUPPORTED_FILE_TYPES,
  DEFAULT_UPLOAD_CONFIG,
} from "@/lib/api/types/upload";

/**
 * Configuration for file validation
 */
export interface FileValidationConfig {
  /** Maximum file size in bytes */
  maxSize: number;
  /** Allowed file types (MIME types) */
  allowedTypes: string[];
  /** Maximum number of files */
  maxFiles: number;
  /** Enable content-based validation */
  enableContentValidation: boolean;
  /** Enable security scanning */
  enableSecurityScan: boolean;
  /** Custom validation rules */
  customValidators?: ((file: File) => Promise<FileValidationError[]>)[];
}

/**
 * Hook for advanced file validation with security checks
 */
export function useFileValidation(config: Partial<FileValidationConfig> = {}) {
  const [isValidating, setIsValidating] = useState(false);
  const [validationCache] = useState(new Map<string, FileValidationResult>());

  const defaultConfig: FileValidationConfig = {
    maxSize: config.maxSize || DEFAULT_UPLOAD_CONFIG.maxSize!,
    allowedTypes: config.allowedTypes || DEFAULT_UPLOAD_CONFIG.accept!,
    maxFiles: config.maxFiles || DEFAULT_UPLOAD_CONFIG.maxFiles!,
    enableContentValidation: config.enableContentValidation ?? true,
    enableSecurityScan: config.enableSecurityScan ?? true,
    customValidators: config.customValidators || [],
  };

  /**
   * Generate cache key for file validation
   */
  const getCacheKey = useCallback((file: File): string => {
    return `${file.name}-${file.size}-${file.lastModified}`;
  }, []);

  /**
   * Validate file size
   */
  const validateFileSize = useCallback(
    (file: File): FileValidationError[] => {
      const errors: FileValidationError[] = [];

      if (!isValidFileSize(file, defaultConfig.maxSize)) {
        errors.push({
          code: "FILE_TOO_LARGE",
          message: `File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds maximum allowed size of ${(defaultConfig.maxSize / 1024 / 1024).toFixed(2)}MB`,
          field: "size",
          severity: "error",
        });
      }

      // Add warning for very large files
      if (file.size > defaultConfig.maxSize * 0.8) {
        errors.push({
          code: "LARGE_FILE_WARNING",
          message: `File is quite large (${(file.size / 1024 / 1024).toFixed(2)}MB) and may take longer to upload`,
          field: "size",
          severity: "warning",
        } as FileValidationError);
      }

      return errors;
    },
    [defaultConfig.maxSize],
  );

  /**
   * Validate file type
   */
  const validateFileType = useCallback(
    (file: File): FileValidationError[] => {
      const errors: FileValidationError[] = [];

      if (!isValidFileType(file, defaultConfig.allowedTypes)) {
        errors.push({
          code: "INVALID_FILE_TYPE",
          message: `File type '${file.type}' is not allowed. Allowed types: ${defaultConfig.allowedTypes.join(", ")}`,
          field: "type",
          severity: "error",
        });
      }

      // Check file extension vs MIME type consistency
      const extension = getFileExtension(file.name);
      const category = getFileCategory(file.type);

      if (extension && file.type) {
        // Map common extensions to their expected MIME types
        const extensionToMimeMap: Record<string, string[]> = {
          pdf: [SUPPORTED_FILE_TYPES.PDF],
          doc: [SUPPORTED_FILE_TYPES.DOC],
          docx: [SUPPORTED_FILE_TYPES.DOCX],
          txt: [SUPPORTED_FILE_TYPES.TXT],
          jpg: [SUPPORTED_FILE_TYPES.JPEG],
          jpeg: [SUPPORTED_FILE_TYPES.JPEG],
          png: [SUPPORTED_FILE_TYPES.PNG],
          gif: [SUPPORTED_FILE_TYPES.GIF],
          svg: [SUPPORTED_FILE_TYPES.SVG],
          zip: [SUPPORTED_FILE_TYPES.ZIP],
          rar: [SUPPORTED_FILE_TYPES.RAR],
          csv: [SUPPORTED_FILE_TYPES.CSV],
          json: [SUPPORTED_FILE_TYPES.JSON],
          xml: [SUPPORTED_FILE_TYPES.XML],
        };

        const expectedTypes = extensionToMimeMap[extension.toLowerCase()] || [];

        if (expectedTypes.length > 0 && !expectedTypes.includes(file.type)) {
          errors.push({
            code: "TYPE_EXTENSION_MISMATCH",
            message: `File extension '.${extension}' does not match MIME type '${file.type}'. Expected: ${expectedTypes.join(" or ")}`,
            field: "type",
            severity: "warning",
          } as FileValidationError);
        }
      }

      return errors;
    },
    [defaultConfig.allowedTypes],
  );

  /**
   * Validate file name
   */
  const validateFileName = useCallback((file: File): FileValidationError[] => {
    const errors: FileValidationError[] = [];

    // Check for empty name
    if (!file.name || file.name.trim().length === 0) {
      errors.push({
        code: "EMPTY_FILENAME",
        message: "File name cannot be empty",
        field: "name",
        severity: "error",
      });
      return errors;
    }

    // Check for suspicious characters
    const suspiciousChars = /[<>:"|?*\x00-\x1f]/;
    if (suspiciousChars.test(file.name)) {
      errors.push({
        code: "INVALID_FILENAME_CHARS",
        message: "File name contains invalid characters",
        field: "name",
        severity: "error",
      });
    }

    // Check for very long names
    if (file.name.length > 255) {
      errors.push({
        code: "FILENAME_TOO_LONG",
        message: "File name is too long (maximum 255 characters)",
        field: "name",
        severity: "error",
      });
    }

    // Check for potential security risks
    const dangerousExtensions = [
      ".exe",
      ".bat",
      ".cmd",
      ".scr",
      ".pif",
      ".vbs",
      ".js",
    ];
    const extension = getFileExtension(file.name);
    if (dangerousExtensions.includes(`.${extension}`)) {
      errors.push({
        code: "POTENTIALLY_DANGEROUS_FILE",
        message: `File extension '.${extension}' may pose security risks`,
        field: "name",
        severity: "warning",
      } as FileValidationError);
    }

    return errors;
  }, []);

  /**
   * Perform content-based validation
   */
  const validateFileContent = useCallback(
    async (file: File): Promise<FileValidationError[]> => {
      const errors: FileValidationError[] = [];

      if (!defaultConfig.enableContentValidation) {
        return errors;
      }

      try {
        // Read first few bytes to check file signature
        const buffer = await file.slice(0, 1024).arrayBuffer();
        const bytes = new Uint8Array(buffer);

        // Check for common file signatures
        const signatures = {
          pdf: [0x25, 0x50, 0x44, 0x46], // %PDF
          jpeg: [0xff, 0xd8, 0xff],
          png: [0x89, 0x50, 0x4e, 0x47],
          zip: [0x50, 0x4b, 0x03, 0x04],
          rar: [0x52, 0x61, 0x72, 0x21],
        };

        // Verify signature matches declared MIME type
        const category = getFileCategory(file.type);
        let signatureMatches = false;

        for (const [type, signature] of Object.entries(signatures)) {
          if (signature.every((byte, index) => bytes[index] === byte)) {
            signatureMatches = true;

            // Check if signature matches declared type
            if (
              category === "DOCUMENT" &&
              type !== "pdf" &&
              file.type === "application/pdf"
            ) {
              errors.push({
                code: "CONTENT_TYPE_MISMATCH",
                message: "File content does not match declared PDF type",
                field: "content",
                severity: "error",
              });
            }
            break;
          }
        }

        // Check for empty files
        if (file.size === 0) {
          errors.push({
            code: "EMPTY_FILE",
            message: "File appears to be empty",
            field: "content",
            severity: "error",
          });
        }

        // Check for very small files that might be incomplete
        if (file.size > 0 && file.size < 100) {
          errors.push({
            code: "SUSPICIOUSLY_SMALL_FILE",
            message: "File is unusually small and may be incomplete",
            field: "content",
            severity: "warning",
          } as FileValidationError);
        }
      } catch (error) {
        logger.error("Content validation failed", {
          filename: file.name,
          error: error instanceof Error ? error.message : "Unknown error",
        });

        errors.push({
          code: "CONTENT_VALIDATION_ERROR",
          message: "Could not validate file content",
          field: "content",
          severity: "warning",
        } as FileValidationError);
      }

      return errors;
    },
    [defaultConfig.enableContentValidation],
  );

  /**
   * Perform security scanning
   */
  const performSecurityScan = useCallback(
    async (file: File): Promise<FileValidationError[]> => {
      const errors: FileValidationError[] = [];

      if (!defaultConfig.enableSecurityScan) {
        return errors;
      }

      try {
        // Simulate virus/malware scanning
        // In a real implementation, this would integrate with security APIs

        // Check for suspicious patterns in filename
        const suspiciousPatterns = [
          /virus/i,
          /malware/i,
          /trojan/i,
          /backdoor/i,
          /keylogger/i,
        ];

        for (const pattern of suspiciousPatterns) {
          if (pattern.test(file.name)) {
            errors.push({
              code: "SUSPICIOUS_FILENAME",
              message: "File name contains suspicious patterns",
              field: "security",
              severity: "error",
            });
            break;
          }
        }

        // Check file size anomalies
        if (file.type === "text/plain" && file.size > 10 * 1024 * 1024) {
          errors.push({
            code: "ANOMALOUS_SIZE",
            message: "Text file is unusually large for its type",
            field: "security",
            severity: "warning",
          } as FileValidationError);
        }

        // Simulate delay for security scan
        await new Promise((resolve) => setTimeout(resolve, 100));
      } catch (error) {
        logger.error("Security scan failed", {
          filename: file.name,
          error: error instanceof Error ? error.message : "Unknown error",
        });

        errors.push({
          code: "SECURITY_SCAN_ERROR",
          message: "Security scan could not be completed",
          field: "security",
          severity: "warning",
        } as FileValidationError);
      }

      return errors;
    },
    [defaultConfig.enableSecurityScan],
  );

  /**
   * Extract file metadata
   */
  const extractMetadata = useCallback(
    async (file: File): Promise<FileMetadataExtract> => {
      const extension = getFileExtension(file.name);
      const category = getFileCategory(file.type) as FileTypeCategory;

      const metadata: FileMetadataExtract = {
        size: file.size,
        mimeType: file.type,
        extension: extension ? `.${extension}` : "",
        category: category.toLowerCase() as FileTypeCategory,
        createdDate: new Date(file.lastModified).toISOString(),
        modifiedDate: new Date(file.lastModified).toISOString(),
      };

      // Extract additional metadata based on file type
      try {
        if (file.type.startsWith("image/")) {
          // For images, we could extract dimensions using canvas or FileReader
          // This is a simplified simulation
          metadata.dimensions = {
            width: 1920,
            height: 1080,
          };
        }

        if (file.type === "application/pdf") {
          // For PDFs, we could extract page count
          // This is a simplified simulation
          metadata.pageCount = Math.ceil(file.size / 50000); // Rough estimate
        }
      } catch (error) {
        logger.warn("Could not extract additional metadata", {
          filename: file.name,
          error: error instanceof Error ? error.message : "Unknown error",
        });
      }

      return metadata;
    },
    [],
  );

  /**
   * Run custom validators
   */
  const runCustomValidators = useCallback(
    async (file: File): Promise<FileValidationError[]> => {
      const errors: FileValidationError[] = [];

      for (const validator of defaultConfig.customValidators || []) {
        try {
          const customErrors = await validator(file);
          errors.push(...customErrors);
        } catch (error) {
          logger.error("Custom validator failed", {
            filename: file.name,
            error: error instanceof Error ? error.message : "Unknown error",
          });

          errors.push({
            code: "CUSTOM_VALIDATION_ERROR",
            message: "Custom validation failed",
            field: "custom",
            severity: "warning",
          } as FileValidationError);
        }
      }

      return errors;
    },
    [defaultConfig.customValidators],
  );

  /**
   * Validate a single file
   */
  const validateFile = useCallback(
    async (file: File): Promise<FileValidationResult> => {
      const cacheKey = getCacheKey(file);

      // Check cache first
      if (validationCache.has(cacheKey)) {
        const cached = validationCache.get(cacheKey)!;
        logger.debug("Using cached validation result", { filename: file.name });
        return cached;
      }

      logger.info("Starting file validation", {
        filename: file.name,
        size: file.size,
        type: file.type,
      });

      setIsValidating(true);

      try {
        const allErrors: FileValidationError[] = [];
        const allWarnings: FileValidationWarning[] = [];

        // Run all validation checks
        const [
          sizeErrors,
          typeErrors,
          nameErrors,
          contentErrors,
          securityErrors,
          customErrors,
        ] = await Promise.all([
          Promise.resolve(validateFileSize(file)),
          Promise.resolve(validateFileType(file)),
          Promise.resolve(validateFileName(file)),
          validateFileContent(file),
          performSecurityScan(file),
          runCustomValidators(file),
        ]);

        // Combine all errors
        allErrors.push(
          ...sizeErrors,
          ...typeErrors,
          ...nameErrors,
          ...contentErrors,
          ...securityErrors,
          ...customErrors,
        );

        // Separate errors and warnings
        const errors = allErrors.filter((e) => e.severity === "error");
        const warnings = allErrors.filter(
          (e) => e.severity === "warning",
        ) as FileValidationWarning[];

        // Extract metadata
        const metadata = await extractMetadata(file);

        const result: FileValidationResult = {
          isValid: errors.length === 0,
          errors,
          warnings,
          metadata,
        };

        // Cache result
        validationCache.set(cacheKey, result);

        logger.info("File validation completed", {
          filename: file.name,
          isValid: result.isValid,
          errorCount: errors.length,
          warningCount: warnings.length,
        });

        return result;
      } catch (error) {
        logger.error("File validation failed", {
          filename: file.name,
          error: error instanceof Error ? error.message : "Unknown error",
        });

        const result: FileValidationResult = {
          isValid: false,
          errors: [
            {
              code: "VALIDATION_FAILED",
              message: "File validation failed due to an error",
              severity: "error",
            },
          ],
          warnings: [],
        };

        return result;
      } finally {
        setIsValidating(false);
      }
    },
    [
      getCacheKey,
      validationCache,
      validateFileSize,
      validateFileType,
      validateFileName,
      validateFileContent,
      performSecurityScan,
      runCustomValidators,
      extractMetadata,
    ],
  );

  /**
   * Validate multiple files
   */
  const validateFiles = useCallback(
    async (files: File[]): Promise<FileValidationResult[]> => {
      logger.info("Starting multiple file validation", {
        fileCount: files.length,
      });

      // Check file count limit
      if (files.length > defaultConfig.maxFiles) {
        logger.warn("Too many files selected", {
          selected: files.length,
          maxAllowed: defaultConfig.maxFiles,
        });

        return files.map((file) => ({
          isValid: false,
          errors: [
            {
              code: "TOO_MANY_FILES",
              message: `Too many files selected. Maximum allowed: ${defaultConfig.maxFiles}`,
              severity: "error",
            },
          ],
          warnings: [],
        }));
      }

      try {
        setIsValidating(true);

        // Validate all files in parallel
        const results = await Promise.all(
          files.map((file) => validateFile(file)),
        );

        const validCount = results.filter((r) => r.isValid).length;
        logger.info("Multiple file validation completed", {
          totalFiles: files.length,
          validFiles: validCount,
          invalidFiles: files.length - validCount,
        });

        return results;
      } finally {
        setIsValidating(false);
      }
    },
    [defaultConfig.maxFiles, validateFile],
  );

  /**
   * Clear validation cache
   */
  const clearValidationCache = useCallback(() => {
    validationCache.clear();
    logger.debug("Validation cache cleared");
  }, [validationCache]);

  return {
    // State
    isValidating,

    // Actions
    validateFile,
    validateFiles,
    clearValidationCache,

    // Configuration
    config: defaultConfig,
  };
}
