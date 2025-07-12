// Health API functions
// Mirrors backend/src/api/v1/health.py

import logger from "@/logger";
import { request } from "./base";

// Types that match the backend
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

export const healthApi = {
  // Get API and database health status
  getHealthStatus: async (): Promise<HealthResponse> => {
    logger.info("Checking health status");
    const response = await request<HealthResponse>("/health");

    if (response.error) {
      logger.warn("Health check failed", { error: response.error });
      throw new Error(response.error);
    }

    logger.info("Health check completed", { status: response.data!.status });
    return response.data!;
  },

  // Get Prometheus metrics
  getMetrics: async (): Promise<string> => {
    logger.info("Fetching Prometheus metrics");
    const response = await request<string>("/metrics", {
      responseType: "text",
    });

    if (response.error) {
      logger.warn("Failed to fetch metrics", { error: response.error });
      throw new Error(response.error);
    }

    logger.info("Metrics fetched successfully");
    return response.data!;
  },
};
