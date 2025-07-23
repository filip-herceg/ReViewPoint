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
			? new URLSearchParams(params as Record<string, string>).toString()
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
		if (!response.data) {
			throw new Error("Export succeeded but no data returned");
		}
		return response.data;
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
		if (!response.data) {
			throw new Error("Full export succeeded but no data returned");
		}
		return response.data;
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
		if (!response.data) {
			throw new Error("Export alive test succeeded but no data returned");
		}
		return response.data;
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
		if (!response.data) {
			throw new Error("Export simple test succeeded but no data returned");
		}
		return response.data;
	},
};
