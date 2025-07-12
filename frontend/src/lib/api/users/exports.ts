/**
 * Users Export API Module
 *
 * Provides user data export functionality for the ReViewPoint application.
 * This module mirrors the backend user export endpoints and provides a consistent
 * interface for exporting user data in various formats.
 *
 * ## Endpoints
 * - `GET /users/export` - Export users as CSV with filtering
 * - `GET /users/export/full` - Export all users as CSV
 * - `GET /users/export/test-alive` - Test endpoint availability
 * - `GET /users/export/simple` - Simple export test
 *
 * ## Usage
 *
 * ### Export Users with Filtering
 * ```typescript
 * import { usersExportsApi } from '@/lib/api';
 *
 * try {
 *   const csvBlob = await usersExportsApi.exportUsersCsv({
 *     fields: 'id,email,name,created_at',
 *     created_after: '2024-01-01T00:00:00Z',
 *     created_before: '2024-12-31T23:59:59Z',
 *     sort: 'created_at',
 *     order: 'desc'
 *   });
 *
 *   // Download CSV file
 *   const url = URL.createObjectURL(csvBlob);
 *   const a = document.createElement('a');
 *   a.href = url;
 *   a.download = 'users-export.csv';
 *   document.body.appendChild(a);
 *   a.click();
 *   document.body.removeChild(a);
 *   URL.revokeObjectURL(url);
 * } catch (error) {
 *   console.error('Export failed:', error.message);
 * }
 * ```
 *
 * ### Export All Users
 * ```typescript
 * try {
 *   const csvBlob = await usersExportsApi.exportUsersFullCsv();
 *   // Handle the CSV blob as shown above
 * } catch (error) {
 *   console.error('Full export failed:', error.message);
 * }
 * ```
 *
 * ### Test Export Functionality
 * ```typescript
 * try {
 *   const status = await usersExportsApi.exportAlive();
 *   console.log('Export service status:', status.status);
 * } catch (error) {
 *   console.error('Export service unavailable:', error.message);
 * }
 * ```
 *
 * ## Export Parameters
 * The `exportUsersCsv` function supports various filtering options:
 * - `fields`: Comma-separated list of fields to include
 * - `created_after`: Filter by creation date (ISO string)
 * - `created_before`: Filter by creation date (ISO string)
 * - `sort`: Sort by field ('created_at', 'email', 'name')
 * - `order`: Sort order ('asc' or 'desc')
 * - `email`: Filter by email pattern
 * - `name`: Filter by name pattern
 *
 * ## Available Fields
 * You can export the following user fields:
 * - `id`: User ID
 * - `email`: Email address
 * - `name`: Display name
 * - `bio`: User biography
 * - `avatar_url`: Avatar image URL
 * - `created_at`: Creation timestamp
 * - `updated_at`: Last update timestamp
 *
 * ## CSV Format
 * The exported CSV includes:
 * - Header row with field names
 * - One row per user
 * - Proper CSV escaping for special characters
 * - UTF-8 encoding
 *
 * ## Use Cases
 * - Data backup and archival
 * - Business intelligence and analytics
 * - Compliance reporting
 * - Data migration
 * - User activity analysis
 *
 * ## Error Handling
 * Export functions throw errors for:
 * - Invalid parameters
 * - Large dataset timeouts
 * - Permission denied
 * - Server processing errors
 *
 * ## Performance Considerations
 * - Large exports may take significant time
 * - Consider pagination for very large datasets
 * - Monitor server resources during exports
 * - Use appropriate timeout values
 *
 * @see backend/src/api/v1/users/exports.py for corresponding backend implementation
 */

// User export API functions
// Mirrors backend/src/api/v1/users/exports.py

import logger from "@/logger";
import { request } from "../base";

// Types that match the backend
interface ExportAliveResponse {
	status: "users export alive";
}

interface ExportSimpleResponse {
	users: "export simple status";
}

interface UserExportParams {
	email?: string;
	format?: string;
}

export const usersExportsApi = {
	// Export users as CSV (minimal)
	exportUsersCsv: async (params?: UserExportParams): Promise<Blob> => {
		logger.info("Exporting users as CSV", { params });
		const queryParams = params
			? new URLSearchParams(params as any).toString()
			: "";
		const url = queryParams ? `/users/export?${queryParams}` : "/users/export";

		const response = await request<Blob>(url, {
			responseType: "blob",
		});

		if (response.error) {
			logger.warn("Failed to export users CSV", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Users CSV exported successfully");
		return response.data!;
	},

	// Export users as CSV (full)
	exportUsersFullCsv: async (): Promise<Blob> => {
		logger.info("Exporting users as full CSV");
		const response = await request<Blob>("/users/export-full", {
			responseType: "blob",
		});

		if (response.error) {
			logger.warn("Failed to export users full CSV", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Users full CSV exported successfully");
		return response.data!;
	},

	// Test endpoint for export router
	exportAlive: async (): Promise<ExportAliveResponse> => {
		logger.info("Testing export alive endpoint");
		const response = await request<ExportAliveResponse>("/users/export-alive");

		if (response.error) {
			logger.warn("Export alive test failed", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Export alive test successful");
		return response.data!;
	},

	// Simple test endpoint for debugging
	exportSimple: async (): Promise<ExportSimpleResponse> => {
		logger.info("Testing export simple endpoint");
		const response = await request<ExportSimpleResponse>(
			"/users/export-simple",
		);

		if (response.error) {
			logger.warn("Export simple test failed", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Export simple test successful");
		return response.data!;
	},
};
