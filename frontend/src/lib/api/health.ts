/**
 * Health Check API Module
 *
 * Provides health check and system monitoring functionality for the ReViewPoint application.
 * This module mirrors the backend health endpoints and provides a consistent interface
 * for monitoring application health, system status, and performance metrics.
 *
 * ## Endpoints
 * - `GET /health` - Basic health check
 * - `GET /health/metrics` - Detailed system metrics
 *
 * ## Usage
 *
 * ### Basic Health Check
 * ```typescript
 * import { healthApi } from '@/lib/api';
 *
 * try {
 *   const status = await healthApi.getHealthStatus();
 *   console.log('System status:', status.status);
 *   console.log('Uptime:', status.uptime);
 *   console.log('Timestamp:', status.timestamp);
 * } catch (error) {
 *   console.error('Health check failed:', error.message);
 *   // System may be down or experiencing issues
 * }
 * ```
 *
 * ### System Metrics
 * ```typescript
 * try {
 *   const metrics = await healthApi.getMetrics();
 *   console.log('System metrics:', metrics);
 *   // Parse metrics string for detailed system information
 * } catch (error) {
 *   console.error('Metrics unavailable:', error.message);
 * }
 * ```
 *
 * ## Health Status Response
 * The health status endpoint returns:
 * - `status`: "ok" | "error" - Overall system status
 * - `uptime`: number - System uptime in seconds
 * - `timestamp`: string - Current timestamp
 * - `details`: object - Additional system information
 *
 * ## Use Cases
 * - Application startup checks
 * - Monitoring dashboards
 * - Load balancer health checks
 * - System diagnostics
 * - Performance monitoring
 *
 * ## Error Handling
 * Health check functions throw errors for:
 * - Network connectivity issues
 * - Server errors
 * - Service unavailability
 *
 * @see backend/src/api/v1/health.py for corresponding backend implementation
 */

// Health check API functions
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
  getHealth: async (): Promise<HealthResponse> => {
    logger.info("Fetching health status");
    try {
      const response = await request<HealthResponse>("/health");

      if (response.error) {
        logger.warn("Failed to get health status", { error: response.error });
        throw new Error(response.error);
      }

      logger.info("Health status retrieved successfully", {
        status: response.data!.status,
      });
      return response.data!;
    } catch (error) {
      logger.warn("Failed to get health status", { error });
      throw error;
    }
  },

  // Alias for backwards compatibility
  getHealthStatus: async (): Promise<HealthResponse> => {
    return healthApi.getHealth();
  },

  // Get Prometheus metrics
  getMetrics: async (): Promise<string> => {
    logger.info("Fetching application metrics");
    try {
      const response = await request<string>("/metrics", {
        headers: {
          Accept: "text/plain",
        },
      });

      if (response.error) {
        logger.warn("Failed to get metrics", { error: response.error });
        throw new Error(response.error);
      }

      logger.info("Metrics retrieved successfully");
      return response.data!;
    } catch (error) {
      logger.warn("Failed to get metrics", { error });
      throw error;
    }
  },
};
