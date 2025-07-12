/**
 * Environment Configuration Management
 * Centralized configuration with type safety and validation
 */

import { z } from "zod";
import logger from "@/logger";

// Environment types
export type Environment = "development" | "staging" | "production" | "test";

// Zod schema for environment validation
const EnvironmentConfigSchema = z.object({
  NODE_ENV: z
    .enum(["development", "staging", "production", "test"])
    .default("development"),
  API_BASE_URL: z.string().min(1).url().default("http://localhost:8000"),
  API_TIMEOUT: z.coerce.number().min(1000).max(30000).default(10000),
  WS_URL: z.string().min(1).default("ws://localhost:8000/api/v1/ws"),
  SENTRY_DSN: z.string().optional(),
  ENABLE_ANALYTICS: z.coerce.boolean().default(false),
  LOG_LEVEL: z
    .enum(["error", "warn", "info", "debug", "trace"])
    .default("info"),
  ENABLE_ERROR_REPORTING: z.coerce.boolean().default(true),
  ENABLE_PERFORMANCE_MONITORING: z.coerce.boolean().default(true),
  APP_VERSION: z.string().min(1).default("0.1.0"),
  APP_NAME: z.string().min(1).default("ReViewPoint"),
});

export type EnvironmentConfig = z.infer<typeof EnvironmentConfigSchema>;

/**
 * Parse and validate environment variables
 */
function parseEnvironmentConfig(): EnvironmentConfig {
  try {
    // Get environment variables from Vite's import.meta.env
    const rawConfig = {
      NODE_ENV: import.meta.env.NODE_ENV || "development",
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
      API_TIMEOUT: import.meta.env.VITE_API_TIMEOUT,
      WS_URL: import.meta.env.VITE_WS_URL,
      SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
      ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS,
      LOG_LEVEL: import.meta.env.VITE_LOG_LEVEL,
      ENABLE_ERROR_REPORTING: import.meta.env.VITE_ENABLE_ERROR_REPORTING,
      ENABLE_PERFORMANCE_MONITORING: import.meta.env
        .VITE_ENABLE_PERFORMANCE_MONITORING,
      APP_VERSION: import.meta.env.VITE_APP_VERSION,
      APP_NAME: import.meta.env.VITE_APP_NAME,
    };

    logger.debug("Raw environment config loaded", rawConfig);

    const validatedConfig = EnvironmentConfigSchema.parse(rawConfig);

    logger.info("Environment configuration validated successfully", {
      environment: validatedConfig.NODE_ENV,
      apiBaseUrl: validatedConfig.API_BASE_URL,
      logLevel: validatedConfig.LOG_LEVEL,
    });

    return validatedConfig;
  } catch (error) {
    logger.error("Failed to parse environment configuration", error);

    // Return default configuration on error
    const defaultConfig = EnvironmentConfigSchema.parse({});
    logger.warn("Using default environment configuration", defaultConfig);

    return defaultConfig;
  }
}

// Singleton configuration instance
let environmentConfig: EnvironmentConfig | null = null;

/**
 * Get the current environment configuration
 */
export function getEnvironmentConfig(): EnvironmentConfig {
  if (!environmentConfig) {
    environmentConfig = parseEnvironmentConfig();
  }
  return environmentConfig;
}

/**
 * Reset the configuration cache (for testing purposes)
 */
export function resetEnvironmentConfig(): void {
  environmentConfig = null;
}

/**
 * Check if the current environment is development
 */
export function isDevelopment(): boolean {
  return getEnvironmentConfig().NODE_ENV === "development";
}

/**
 * Check if the current environment is production
 */
export function isProduction(): boolean {
  return getEnvironmentConfig().NODE_ENV === "production";
}

/**
 * Check if the current environment is staging
 */
export function isStaging(): boolean {
  return getEnvironmentConfig().NODE_ENV === "staging";
}

/**
 * Check if the current environment is test
 */
export function isTest(): boolean {
  return getEnvironmentConfig().NODE_ENV === "test";
}

/**
 * Get API configuration
 */
export function getApiConfig() {
  const config = getEnvironmentConfig();
  return {
    baseURL: config.API_BASE_URL,
    timeout: config.API_TIMEOUT,
    wsUrl: config.WS_URL,
  };
}

/**
 * Get monitoring configuration
 */
export function getMonitoringConfig() {
  const config = getEnvironmentConfig();
  return {
    sentryDsn: config.SENTRY_DSN,
    enableAnalytics: config.ENABLE_ANALYTICS,
    enableErrorReporting: config.ENABLE_ERROR_REPORTING,
    enablePerformanceMonitoring: config.ENABLE_PERFORMANCE_MONITORING,
  };
}

/**
 * Get application metadata
 */
export function getAppMetadata() {
  const config = getEnvironmentConfig();
  return {
    name: config.APP_NAME,
    version: config.APP_VERSION,
    environment: config.NODE_ENV,
  };
}

// Export the configuration for direct access if needed
export const env = getEnvironmentConfig();

// Log configuration on module load
logger.info("Environment configuration module initialized", {
  environment: env.NODE_ENV,
  hasApiUrl: !!env.API_BASE_URL,
  hasWsUrl: !!env.WS_URL,
});
