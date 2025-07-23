import { beforeEach, describe, expect, it, vi } from "vitest";
import type { AxiosRequestConfig } from "axios";
import type { ApiResponse } from "@/lib/api/types/common";

// Define interfaces matching those in the health.ts file
interface PoolStats {
	size?: number;
	checkedin?: number;
	checkedout?: number;
	overflow?: number;
	awaiting?: number;
}

interface DBStatus {
	ok: boolean;
	error?: string;
	pool?: PoolStats;
}

interface Versions {
	python: string;
	fastapi?: string;
	sqlalchemy?: string;
}

interface HealthResponse {
	status: "ok" | "error";
	db: DBStatus;
	uptime: number;
	response_time: number;
	versions: Versions;
	detail?: string;
}

// Mock the logger and request modules to avoid hoisting issues
vi.mock("@/logger", () => ({
	default: {
		info: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	},
}));

vi.mock("@/lib/api/base", () => ({
	request: vi.fn(),
}));

describe("Health API", () => {
	// Define proper types for the API and mocks
	type HealthApi = {
		getHealth: () => Promise<HealthResponse>;
		getHealthStatus: () => Promise<HealthResponse>;
		getMetrics: () => Promise<string>;
	};
	
	let healthApi: HealthApi;
	let mockRequest: ReturnType<typeof vi.fn>;
	let mockLogger: {
		info: ReturnType<typeof vi.fn>;
		warn: ReturnType<typeof vi.fn>;
		error: ReturnType<typeof vi.fn>;
	};

	beforeEach(async () => {
		// Reset all mocks
		vi.resetAllMocks();

		// Dynamically import modules to avoid hoisting issues
		const { request } = await import("@/lib/api/base");
		const logger = (await import("@/logger")).default;
		const { healthApi: api } = await import("@/lib/api/health");

		// Store the values with proper casting for test mocks
		healthApi = api;
		mockRequest = request as unknown as ReturnType<typeof vi.fn>;
		mockLogger = logger as unknown as {
			info: ReturnType<typeof vi.fn>;
			warn: ReturnType<typeof vi.fn>;
			error: ReturnType<typeof vi.fn>;
		};
	});

	describe("getHealth", () => {
		const mockHealthResponse = {
			status: "ok" as const,
			db: {
				ok: true,
				error: null,
				pool: {
					size: 5,
					checkedin: 5,
					checkedout: 0,
					overflow: 0,
					awaiting: 0,
				},
			},
			uptime: 12345.67,
			response_time: 0.0012,
			versions: {
				python: "3.11.8",
				fastapi: "0.110.0",
				sqlalchemy: "2.0.29",
			},
		};

		it("should fetch health status successfully", async () => {
			mockRequest.mockResolvedValue({ data: mockHealthResponse });

			const result = await healthApi.getHealth();

			expect(mockRequest).toHaveBeenCalledWith("/health");
			expect(mockLogger.info).toHaveBeenCalledWith("Fetching health status");
			expect(mockLogger.info).toHaveBeenCalledWith(
				"Health status retrieved successfully",
				{
					status: mockHealthResponse.status,
				},
			);
			expect(result).toEqual(mockHealthResponse);
		});

		it("should handle error response from API", async () => {
			const errorMessage = "Database connection failed";
			mockRequest.mockResolvedValue({ error: errorMessage });

			await expect(healthApi.getHealth()).rejects.toThrow(errorMessage);

			expect(mockLogger.warn).toHaveBeenCalledWith(
				"Failed to get health status",
				{
					error: errorMessage,
				},
			);
		});

		it("should handle network errors", async () => {
			const networkError = new Error("Network timeout");
			mockRequest.mockRejectedValue(networkError);

			await expect(healthApi.getHealth()).rejects.toThrow("Network timeout");

			expect(mockLogger.warn).toHaveBeenCalledWith(
				"Failed to get health status",
				{
					error: networkError,
				},
			);
		});

		it("should handle unhealthy status", async () => {
			const unhealthyResponse = {
				status: "error" as const,
				db: {
					ok: false,
					error: "Database connection failed",
					pool: {},
				},
				uptime: 12345.67,
				response_time: 0.0023,
				versions: {
					python: "3.11.8",
					fastapi: "0.110.0",
					sqlalchemy: "2.0.29",
				},
				detail: "Database connection failed",
			};

			mockRequest.mockResolvedValue({ data: unhealthyResponse });

			const result = await healthApi.getHealth();

			expect(result).toEqual(unhealthyResponse);
			expect(result.status).toBe("error");
			expect(result.db.ok).toBe(false);
		});
	});

	describe("getMetrics", () => {
		const mockMetricsResponse = `app_uptime_seconds 12345.67
db_pool_size 5
db_pool_checkedin 5
db_pool_checkedout 0
db_pool_overflow 0
db_pool_awaiting 0`;

		it("should fetch metrics successfully", async () => {
			mockRequest.mockResolvedValue({ data: mockMetricsResponse });

			const result = await healthApi.getMetrics();

			expect(mockRequest).toHaveBeenCalledWith("/metrics", {
				headers: {
					Accept: "text/plain",
				},
			});
			expect(mockLogger.info).toHaveBeenCalledWith(
				"Fetching application metrics",
			);
			expect(mockLogger.info).toHaveBeenCalledWith(
				"Metrics retrieved successfully",
			);
			expect(result).toBe(mockMetricsResponse);
		});

		it("should handle error response from API", async () => {
			const errorMessage = "Service unavailable";
			mockRequest.mockResolvedValue({ error: errorMessage });

			await expect(healthApi.getMetrics()).rejects.toThrow(errorMessage);

			expect(mockLogger.warn).toHaveBeenCalledWith("Failed to get metrics", {
				error: errorMessage,
			});
		});

		it("should handle network errors", async () => {
			const networkError = new Error("Connection refused");
			mockRequest.mockRejectedValue(networkError);

			await expect(healthApi.getMetrics()).rejects.toThrow(
				"Connection refused",
			);

			expect(mockLogger.warn).toHaveBeenCalledWith("Failed to get metrics", {
				error: networkError,
			});
		});
	});
});
