/**
 * Feature Flags Management System
 * Centralized feature flag configuration with type safety
 */

import { z } from "zod";
import logger from "@/logger";
import { getEnvironmentConfig } from "@/lib/config/environment";

// Feature flag schema
const FeatureFlagsSchema = z.object({
  // Authentication features
  enablePasswordReset: z.boolean().default(true),
  enableSocialLogin: z.boolean().default(false),
  enableTwoFactorAuth: z.boolean().default(false),

  // Upload features
  enableMultipleFileUpload: z.boolean().default(true),
  enableDragDropUpload: z.boolean().default(true),
  enableUploadProgress: z.boolean().default(true),
  enableFilePreview: z.boolean().default(true),

  // Review features
  enableAiReviews: z.boolean().default(false),
  enableCollaborativeReviews: z.boolean().default(false),
  enableReviewComments: z.boolean().default(true),
  enableReviewExport: z.boolean().default(true),

  // UI features
  enableDarkMode: z.boolean().default(true),
  enableNotifications: z.boolean().default(true),
  enableBreadcrumbs: z.boolean().default(true),
  enableSidebar: z.boolean().default(true),
  enableWebSocket: z.boolean().default(true),

  // Performance features
  enableVirtualization: z.boolean().default(false),
  enableLazyLoading: z.boolean().default(true),
  enableCodeSplitting: z.boolean().default(true),

  // Monitoring features
  enableAnalytics: z.boolean().default(false),
  enableErrorReporting: z.boolean().default(true),
  enablePerformanceMonitoring: z.boolean().default(true),
  enableWebVitals: z.boolean().default(true),

  // Development features
  enableDevTools: z.boolean().default(false),
  enableDebugMode: z.boolean().default(false),
  enableTestMode: z.boolean().default(false),
});

export type FeatureFlags = z.infer<typeof FeatureFlagsSchema>;

/**
 * Load feature flags from environment or API
 */
function loadFeatureFlags(): FeatureFlags {
  try {
    const env = getEnvironmentConfig();

    // Default flags based on environment
    const defaultFlags: Partial<FeatureFlags> = {
      enableDevTools: env.NODE_ENV === "development",
      enableDebugMode: env.NODE_ENV === "development",
      enableTestMode: env.NODE_ENV === "test",
      enableAnalytics: env.ENABLE_ANALYTICS,
      enableErrorReporting: env.ENABLE_ERROR_REPORTING,
      enablePerformanceMonitoring: env.ENABLE_PERFORMANCE_MONITORING,
    };

    // Load from environment variables (prefixed with VITE_FEATURE_)
    const envFlags: Partial<FeatureFlags> = {};

    // Map environment variables to feature flags
    const envToFeatureMap: Record<string, keyof FeatureFlags> = {
      VITE_FEATURE_ENABLE_PASSWORD_RESET: "enablePasswordReset",
      VITE_FEATURE_ENABLE_SOCIAL_LOGIN: "enableSocialLogin",
      VITE_FEATURE_ENABLE_TWO_FACTOR_AUTH: "enableTwoFactorAuth",
      VITE_FEATURE_ENABLE_MULTIPLE_FILE_UPLOAD: "enableMultipleFileUpload",
      VITE_FEATURE_ENABLE_DRAG_DROP_UPLOAD: "enableDragDropUpload",
      VITE_FEATURE_ENABLE_UPLOAD_PROGRESS: "enableUploadProgress",
      VITE_FEATURE_ENABLE_FILE_PREVIEW: "enableFilePreview",
      VITE_FEATURE_ENABLE_AI_REVIEWS: "enableAiReviews",
      VITE_FEATURE_ENABLE_COLLABORATIVE_REVIEWS: "enableCollaborativeReviews",
      VITE_FEATURE_ENABLE_REVIEW_COMMENTS: "enableReviewComments",
      VITE_FEATURE_ENABLE_REVIEW_EXPORT: "enableReviewExport",
      VITE_FEATURE_ENABLE_DARK_MODE: "enableDarkMode",
      VITE_FEATURE_ENABLE_NOTIFICATIONS: "enableNotifications",
      VITE_FEATURE_ENABLE_BREADCRUMBS: "enableBreadcrumbs",
      VITE_FEATURE_ENABLE_SIDEBAR: "enableSidebar",
      VITE_FEATURE_ENABLE_WEBSOCKET: "enableWebSocket",
      VITE_FEATURE_ENABLE_VIRTUALIZATION: "enableVirtualization",
      VITE_FEATURE_ENABLE_LAZY_LOADING: "enableLazyLoading",
      VITE_FEATURE_ENABLE_CODE_SPLITTING: "enableCodeSplitting",
      VITE_FEATURE_ENABLE_ANALYTICS: "enableAnalytics",
      VITE_FEATURE_ENABLE_ERROR_REPORTING: "enableErrorReporting",
      VITE_FEATURE_ENABLE_PERFORMANCE_MONITORING: "enablePerformanceMonitoring",
      VITE_FEATURE_ENABLE_WEB_VITALS: "enableWebVitals",
      VITE_FEATURE_ENABLE_DEV_TOOLS: "enableDevTools",
      VITE_FEATURE_ENABLE_DEBUG_MODE: "enableDebugMode",
      VITE_FEATURE_ENABLE_TEST_MODE: "enableTestMode",
    };

    // Read feature flags from environment
    Object.entries(envToFeatureMap).forEach(([envKey, featureKey]) => {
      const envValue = import.meta.env[envKey];
      if (envValue !== undefined) {
        envFlags[featureKey] = envValue === "true" || envValue === true;
      }
    });

    // Check for environment-specific feature flags
    if (typeof window !== "undefined" && (window as any).FEATURE_FLAGS) {
      const windowFlags = (window as any).FEATURE_FLAGS;
      logger.debug("Loading feature flags from window object", windowFlags);
      Object.assign(envFlags, windowFlags);
    }

    // Merge default flags with environment flags
    const mergedFlags = { ...defaultFlags, ...envFlags };

    logger.debug("Raw feature flags before validation", mergedFlags);

    const validatedFlags = FeatureFlagsSchema.parse(mergedFlags);

    logger.info("Feature flags loaded and validated successfully", {
      environment: env.NODE_ENV,
      enabledFeatures: Object.entries(validatedFlags)
        .filter(([, enabled]) => enabled)
        .map(([feature]) => feature),
    });

    return validatedFlags;
  } catch (error) {
    logger.error("Failed to load feature flags", error);

    // Return default flags on error
    const defaultFlags = FeatureFlagsSchema.parse({});
    logger.warn("Using default feature flags", defaultFlags);

    return defaultFlags;
  }
}

// Singleton feature flags instance
let featureFlags: FeatureFlags | null = null;

/**
 * Get current feature flags
 */
export function getFeatureFlags(): FeatureFlags {
  if (!featureFlags) {
    featureFlags = loadFeatureFlags();
  }
  return featureFlags;
}

/**
 * Check if a feature is enabled
 */
export function isFeatureEnabled(feature: keyof FeatureFlags): boolean {
  const flags = getFeatureFlags();
  const enabled = flags[feature];

  logger.debug(`Feature flag check: ${feature} = ${enabled}`);

  return enabled;
}

/**
 * Get enabled features list
 */
export function getEnabledFeatures(): Array<keyof FeatureFlags> {
  const flags = getFeatureFlags();
  return Object.entries(flags)
    .filter(([, enabled]) => enabled)
    .map(([feature]) => feature as keyof FeatureFlags);
}

/**
 * Update feature flags (for runtime configuration)
 */
export function updateFeatureFlags(updates: Partial<FeatureFlags>): void {
  try {
    if (!featureFlags) {
      featureFlags = loadFeatureFlags();
    }

    const updatedFlags = { ...featureFlags, ...updates };
    const validatedFlags = FeatureFlagsSchema.parse(updatedFlags);

    featureFlags = validatedFlags;

    logger.info("Feature flags updated successfully", {
      updates,
      newFlags: validatedFlags,
    });
  } catch (error) {
    logger.error("Failed to update feature flags", error);
  }
}

/**
 * Reset feature flags to default values
 */
export function resetFeatureFlags(): void {
  featureFlags = null;
  logger.info("Feature flags reset to default values");
}

/**
 * Feature flag hook for React components
 */
export function useFeatureFlag(feature: keyof FeatureFlags): boolean {
  return isFeatureEnabled(feature);
}

// Export feature flags instance
export const features = getFeatureFlags();

// Log feature flags on module load
logger.info("Feature flags module initialized", {
  totalFeatures: Object.keys(features).length,
  enabledFeatures: getEnabledFeatures().length,
});
