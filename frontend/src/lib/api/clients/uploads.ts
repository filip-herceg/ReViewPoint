/**
 * Type-Safe Upload API Client
 *
 * Generated upload client that uses OpenAPI-generated types
 * and integrates with existing error handling patterns.
 */

import { handleApiError } from "@/lib/api/errorHandling";
import logger from "@/logger";
import { generatedApiClient } from "../generated/client";
import type { components, paths } from "../generated/schema";

// Extract types from generated schema
type UploadFileResponse = components["schemas"]["FileUploadResponse"];
type FileListResponse = components["schemas"]["FileListResponse"];
type FileDict = components["schemas"]["FileDict"];
type HTTPValidationError = components["schemas"]["HTTPValidationError"];

// API operation types
type UploadFileOperation = paths["/api/v1/uploads"]["post"];
type ListFilesOperation = paths["/api/v1/uploads"]["get"];
type GetFileOperation = paths["/api/v1/uploads/{filename}"]["get"];
type DeleteFileOperation = paths["/api/v1/uploads/{filename}"]["delete"];

/**
 * Type-safe upload API client using generated types
 */
export const uploadApiClient = {
	/**
	 * Upload a file to the server
	 * Note: Uses fetch directly for multipart/form-data since openapi-fetch doesn't handle File objects well
	 */
	async uploadFile(file: File): Promise<UploadFileResponse> {
		try {
			logger.info("🔼 Uploading file:", {
				name: file.name,
				size: file.size,
				type: file.type,
			});

			const formData = new FormData();
			formData.append("file", file);

			// Use fetch directly for file uploads since openapi-fetch expects string for binary files
			const baseUrl =
				import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000";
			const response = await fetch(`${baseUrl}/api/v1/uploads`, {
				method: "POST",
				body: formData,
				headers: {
					// Don't set Content-Type - let browser set it with boundary for multipart/form-data
					// Authorization will be added by the auth middleware
				},
			});

			if (!response.ok) {
				const errorText = await response.text();
				logger.error("❌ Upload failed:", {
					status: response.status,
					error: errorText,
				});
				throw new Error(
					`Upload failed: ${response.status} ${response.statusText}`,
				);
			}

			const data: UploadFileResponse = await response.json();

			if (!data || !data.filename || !data.url) {
				logger.error("❌ Upload failed: Invalid response format");
				throw new Error("Upload failed: Invalid response format from server");
			}

			logger.info("✅ Upload completed successfully:", data);
			return data;
		} catch (error) {
			logger.error("❌ Upload error:", error);
			throw error;
		}
	},

	/**
	 * List all uploaded files with query parameters
	 */
	async listFiles(params?: {
		limit?: number;
		offset?: number;
		q?: string;
		sort?: "created_at" | "filename";
		order?: "asc" | "desc";
		fields?: string;
		created_after?: string;
		created_before?: string;
	}): Promise<FileListResponse> {
		try {
			logger.info("📋 Fetching file list", params);

			const { data, error } = await generatedApiClient.GET("/api/v1/uploads", {
				params: {
					query: params || {},
				},
			});

			if (error) {
				logger.error("❌ Failed to fetch file list:", error);
				const handledError = handleApiError(error);
				throw handledError;
			}

			if (!data) {
				logger.error("❌ Failed to fetch file list: No data returned");
				throw new Error(
					"Failed to fetch file list: No data returned from server",
				);
			}

			logger.info("✅ File list fetched successfully:", {
				count: data.files?.length || 0,
			});
			return data;
		} catch (error) {
			logger.error("❌ File list fetch error:", error);
			throw error;
		}
	},

	/**
	 * Get file metadata by filename
	 */
	async getFileInfo(filename: string): Promise<UploadFileResponse> {
		try {
			logger.info("📥 Fetching file info:", { filename });

			const { data, error } = await generatedApiClient.GET(
				"/api/v1/uploads/{filename}",
				{
					params: {
						path: { filename },
					},
				},
			);

			if (error) {
				logger.error("❌ Failed to fetch file info:", error);
				const handledError = handleApiError(error);
				throw handledError;
			}

			if (!data) {
				logger.error("❌ Failed to fetch file info: No data returned");
				throw new Error(
					"Failed to fetch file info: No data returned from server",
				);
			}

			logger.info("✅ File info fetched successfully:", {
				filename,
				url: data.url,
			});
			return data;
		} catch (error) {
			logger.error("❌ File info fetch error:", error);
			throw error;
		}
	},

	/**
	 * Download file content by filename using the new download endpoint
	 */
	async downloadFile(filename: string): Promise<Blob> {
		try {
			logger.info("📥 Downloading file:", { filename });

			// Use the dedicated download endpoint
			const baseUrl =
				import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000";
			const response = await fetch(
				`${baseUrl}/api/v1/uploads/${filename}/download`,
				{
					headers: {
						// Authorization header will be added by interceptors if needed
					},
				},
			);

			if (!response.ok) {
				throw new Error(
					`Failed to download file: ${response.status} ${response.statusText}`,
				);
			}

			const blob = await response.blob();
			logger.info("✅ File downloaded successfully:", {
				filename,
				size: blob.size,
			});
			return blob;
		} catch (error) {
			logger.error("❌ File download error:", error);
			throw error;
		}
	},

	/**
	 * Delete a file by filename
	 */
	async deleteFile(filename: string): Promise<void> {
		try {
			logger.info("🗑️ Deleting file:", { filename });

			const { error } = await generatedApiClient.DELETE(
				"/api/v1/uploads/{filename}",
				{
					params: {
						path: { filename },
					},
				},
			);

			if (error) {
				logger.error("❌ Failed to delete file:", error);
				const handledError = handleApiError(error);
				throw handledError;
			}

			logger.info("✅ File deleted successfully:", { filename });
		} catch (error) {
			logger.error("❌ File deletion error:", error);
			throw error;
		}
	},

	/**
	 * Bulk delete files by filenames
	 */
	async bulkDeleteFiles(
		filenames: string[],
	): Promise<{ deleted: string[]; failed: string[] }> {
		try {
			logger.info("🗑️ Bulk deleting files:", {
				count: filenames.length,
				filenames,
			});

			const baseUrl =
				import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000";
			const response = await fetch(`${baseUrl}/api/v1/uploads/bulk-delete`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					// Authorization header will be added by interceptors if needed
				},
				body: JSON.stringify({ filenames }),
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(
					`Bulk delete failed: ${response.status} ${response.statusText} - ${errorText}`,
				);
			}

			const result = (await response.json()) as {
				deleted: string[];
				failed: string[];
			};

			logger.info("✅ Bulk delete completed:", {
				deleted: result.deleted.length,
				failed: result.failed.length,
				details: result,
			});

			return result;
		} catch (error) {
			logger.error("❌ Bulk delete error:", error);
			throw error;
		}
	},
};

/**
 * Legacy compatibility wrapper
 * Maintains compatibility with existing upload API usage
 */
export const uploadApi = uploadApiClient;

/**
 * Type guards for API responses
 */
export function isUploadResponse(data: unknown): data is UploadFileResponse {
	return (
		typeof data === "object" &&
		data !== null &&
		"filename" in data &&
		"url" in data &&
		typeof (data as Record<string, unknown>).filename === "string" &&
		typeof (data as Record<string, unknown>).url === "string"
	);
}

export function isFileListResponse(data: unknown): data is FileListResponse {
	return (
		typeof data === "object" &&
		data !== null &&
		"files" in data &&
		"total" in data &&
		Array.isArray((data as Record<string, unknown>).files) &&
		typeof (data as Record<string, unknown>).total === "number"
	);
}

export function isValidationError(data: unknown): data is HTTPValidationError {
	return (
		typeof data === "object" &&
		data !== null &&
		"detail" in data &&
		Array.isArray((data as Record<string, unknown>).detail)
	);
}

/**
 * Export types for use in other modules
 */
export type {
	UploadFileResponse,
	FileListResponse,
	FileDict,
	HTTPValidationError,
	UploadFileOperation,
	ListFilesOperation,
	GetFileOperation,
	DeleteFileOperation,
};
