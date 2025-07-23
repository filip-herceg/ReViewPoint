/**
 * Tests for Feature Flags System
 * Comprehensive testing of feature flag management, validation, and runtime updates
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  getEnabledFeatures,
  getFeatureFlags,
  isFeatureEnabled,
  resetFeatureFlags,
  updateFeatureFlags,
} from "@/lib/config/featureFlags";
import {
  createDevelopmentFeatureFlags,
  createFeatureFlags,
  createFeatureFlagUpdates,
  createProductionFeatureFlags,
} from "../../test-templates";
import { testLogger } from "../../test-utils";

describe("Feature Flags System", () => {
  beforeEach(() => {
    testLogger.info("Setting up feature flags test");

    // Reset feature flags to default state
    resetFeatureFlags();

    // Clear any window feature flags
    if (typeof window !== "undefined") {
      delete (window as any).FEATURE_FLAGS;
    }

    testLogger.debug("Feature flags test setup complete");
  });

  describe("Feature Flag Loading", () => {
    it("should load default feature flags successfully", () => {
      testLogger.info("Testing default feature flags loading");

      const flags = getFeatureFlags();

      expect(flags).toBeDefined();
      expect(typeof flags).toBe("object");

      // Check that all required flags exist
      expect(flags).toHaveProperty("enablePasswordReset");
      expect(flags).toHaveProperty("enableDarkMode");
      expect(flags).toHaveProperty("enableAnalytics");
      expect(flags).toHaveProperty("enableTestMode");

      testLogger.debug("Default feature flags loaded", {
        totalFlags: Object.keys(flags).length,
        sampleFlags: {
          enablePasswordReset: flags.enablePasswordReset,
          enableDarkMode: flags.enableDarkMode,
        },
      });
    });

    it("should load feature flags from window object", () => {
      testLogger.info("Testing feature flags loading from window object");

      const windowFlags = {
        enableSocialLogin: true,
        enableAiReviews: true,
        enableVirtualization: true,
      };

      // Mock window.FEATURE_FLAGS
      (global as any).window = {
        FEATURE_FLAGS: windowFlags,
      };

      resetFeatureFlags(); // Force reload
      const flags = getFeatureFlags();

      expect(flags.enableSocialLogin).toBe(true);
      expect(flags.enableAiReviews).toBe(true);
      expect(flags.enableVirtualization).toBe(true);

      testLogger.debug("Window feature flags loaded correctly", {
        windowFlags,
        actualFlags: {
          enableSocialLogin: flags.enableSocialLogin,
          enableAiReviews: flags.enableAiReviews,
          enableVirtualization: flags.enableVirtualization,
        },
      });
    });

    it("should handle malformed window feature flags gracefully", () => {
      testLogger.info("Testing malformed window feature flags handling");

      // Mock console.error to capture error logs
      const consoleSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      // Mock malformed window feature flags
      (global as any).window = {
        FEATURE_FLAGS: {
          enableSocialLogin: "not-a-boolean",
          invalidFlag: "invalid",
        },
      };

      resetFeatureFlags();
      const flags = getFeatureFlags();

      // Should use defaults for invalid values
      expect(typeof flags.enableSocialLogin).toBe("boolean");

      consoleSpy.mockRestore();

      testLogger.debug("Malformed feature flags handled gracefully", flags);
    });
  });

  describe("Feature Flag Checking", () => {
    it("should correctly check enabled features", () => {
      testLogger.info("Testing enabled feature checking");

      // Set up specific test flags for this test
      const testFlags = createFeatureFlags({
        enablePasswordReset: true,
        enableSocialLogin: false,
        enableDarkMode: true,
        enableVirtualization: false,
      });

      // Mock the feature flags for testing
      (global as any).window = {
        FEATURE_FLAGS: testFlags,
      };

      resetFeatureFlags();

      expect(isFeatureEnabled("enablePasswordReset")).toBe(true);
      expect(isFeatureEnabled("enableDarkMode")).toBe(true);

      testLogger.debug("Enabled features checked correctly", {
        enablePasswordReset: isFeatureEnabled("enablePasswordReset"),
        enableDarkMode: isFeatureEnabled("enableDarkMode"),
      });
    });

    it("should correctly check disabled features", () => {
      testLogger.info("Testing disabled feature checking");

      // Set up specific test flags for this test
      const testFlags = createFeatureFlags({
        enablePasswordReset: true,
        enableSocialLogin: false,
        enableDarkMode: true,
        enableVirtualization: false,
      });

      // Mock the feature flags for testing
      (global as any).window = {
        FEATURE_FLAGS: testFlags,
      };

      resetFeatureFlags();

      expect(isFeatureEnabled("enableSocialLogin")).toBe(false);
      expect(isFeatureEnabled("enableVirtualization")).toBe(false);

      testLogger.debug("Disabled features checked correctly", {
        enableSocialLogin: isFeatureEnabled("enableSocialLogin"),
        enableVirtualization: isFeatureEnabled("enableVirtualization"),
      });
    });

    it("should return list of enabled features", () => {
      testLogger.info("Testing enabled features list");

      // Set up specific test flags for this test
      const testFlags = createFeatureFlags({
        enablePasswordReset: true,
        enableSocialLogin: false,
        enableDarkMode: true,
        enableVirtualization: false,
      });

      // Mock the feature flags for testing
      (global as any).window = {
        FEATURE_FLAGS: testFlags,
      };

      resetFeatureFlags();

      const enabledFeatures = getEnabledFeatures();

      expect(Array.isArray(enabledFeatures)).toBe(true);
      expect(enabledFeatures).toContain("enablePasswordReset");
      expect(enabledFeatures).toContain("enableDarkMode");
      expect(enabledFeatures).not.toContain("enableSocialLogin");
      expect(enabledFeatures).not.toContain("enableVirtualization");

      testLogger.debug("Enabled features list returned correctly", {
        count: enabledFeatures.length,
        features: enabledFeatures,
      });
    });
  });

  describe("Feature Flag Updates", () => {
    it("should update feature flags at runtime", () => {
      testLogger.info("Testing runtime feature flag updates");

      const initialFlags = getFeatureFlags();
      const initialValue = initialFlags.enableSocialLogin;

      const updates = createFeatureFlagUpdates({
        enableSocialLogin: !initialValue,
        enableAiReviews: true,
      });

      updateFeatureFlags(updates);

      expect(isFeatureEnabled("enableSocialLogin")).toBe(!initialValue);
      expect(isFeatureEnabled("enableAiReviews")).toBe(true);

      testLogger.debug("Feature flags updated successfully", {
        initialValue,
        newValue: isFeatureEnabled("enableSocialLogin"),
        updates,
      });
    });

    it("should validate updates and reject invalid values", () => {
      testLogger.info("Testing feature flag update validation");

      const consoleSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const invalidUpdates = {
        enableSocialLogin: "not-a-boolean" as any,
        invalidFlag: true as any,
      };

      updateFeatureFlags(invalidUpdates);

      // Feature flags should remain valid despite invalid updates
      const flags = getFeatureFlags();
      expect(typeof flags.enableSocialLogin).toBe("boolean");

      consoleSpy.mockRestore();

      testLogger.debug("Invalid updates rejected correctly", flags);
    });

    it("should handle partial updates correctly", () => {
      testLogger.info("Testing partial feature flag updates");

      const originalFlags = getFeatureFlags();
      const originalSocialLogin = originalFlags.enableSocialLogin;
      const originalDarkMode = originalFlags.enableDarkMode;

      updateFeatureFlags({
        enableSocialLogin: !originalSocialLogin,
      });

      // Only updated flag should change
      expect(isFeatureEnabled("enableSocialLogin")).toBe(!originalSocialLogin);
      expect(isFeatureEnabled("enableDarkMode")).toBe(originalDarkMode);

      testLogger.debug("Partial updates applied correctly", {
        originalSocialLogin,
        newSocialLogin: isFeatureEnabled("enableSocialLogin"),
        darkModeUnchanged:
          isFeatureEnabled("enableDarkMode") === originalDarkMode,
      });
    });
  });

  describe("Feature Flag Reset", () => {
    it("should reset feature flags to default values", () => {
      testLogger.info("Testing feature flag reset");

      // Update some flags
      updateFeatureFlags({
        enableSocialLogin: true,
        enableAiReviews: true,
      });

      const afterUpdate = getFeatureFlags();
      expect(afterUpdate.enableSocialLogin).toBe(true);
      expect(afterUpdate.enableAiReviews).toBe(true);

      // Reset flags
      resetFeatureFlags();

      const afterReset = getFeatureFlags();

      // Should use default values (not the updated ones)
      expect(typeof afterReset.enableSocialLogin).toBe("boolean");
      expect(typeof afterReset.enableAiReviews).toBe("boolean");

      testLogger.debug("Feature flags reset successfully", {
        beforeReset: {
          enableSocialLogin: afterUpdate.enableSocialLogin,
          enableAiReviews: afterUpdate.enableAiReviews,
        },
        afterReset: {
          enableSocialLogin: afterReset.enableSocialLogin,
          enableAiReviews: afterReset.enableAiReviews,
        },
      });
    });
  });

  describe("Environment-Specific Feature Flags", () => {
    it("should have appropriate development feature flags", () => {
      testLogger.info("Testing development environment feature flags");

      const devFlags = createDevelopmentFeatureFlags();

      expect(devFlags.enableDevTools).toBe(true);
      expect(devFlags.enableDebugMode).toBe(true);
      expect(devFlags.enableTestMode).toBe(true); // Will be true in test environment
      expect(devFlags.enableSocialLogin).toBe(false);
      expect(devFlags.enableAiReviews).toBe(false);

      testLogger.debug("Development feature flags verified", {
        devTools: devFlags.enableDevTools,
        debugMode: devFlags.enableDebugMode,
        socialLogin: devFlags.enableSocialLogin,
      });
    });

    it("should have appropriate production feature flags", () => {
      testLogger.info("Testing production environment feature flags");

      const prodFlags = createProductionFeatureFlags();

      expect(prodFlags.enableDevTools).toBe(false);
      expect(prodFlags.enableDebugMode).toBe(false);
      expect(prodFlags.enableTestMode).toBe(false);
      expect(prodFlags.enableSocialLogin).toBe(true);
      expect(prodFlags.enableTwoFactorAuth).toBe(true);
      expect(prodFlags.enableAiReviews).toBe(true);
      expect(prodFlags.enableVirtualization).toBe(true);
      expect(prodFlags.enableAnalytics).toBe(true);

      testLogger.debug("Production feature flags verified", {
        devTools: prodFlags.enableDevTools,
        socialLogin: prodFlags.enableSocialLogin,
        aiReviews: prodFlags.enableAiReviews,
        analytics: prodFlags.enableAnalytics,
      });
    });
  });

  describe("Feature Flag Caching", () => {
    it("should cache feature flags after first access", () => {
      testLogger.info("Testing feature flag caching");

      const firstCall = getFeatureFlags();
      const secondCall = getFeatureFlags();

      // Should be the same cached instance
      expect(firstCall).toBe(secondCall);

      testLogger.debug("Feature flags cached correctly");
    });

    it("should reload feature flags after reset", () => {
      testLogger.info("Testing feature flag reload after reset");

      const beforeReset = getFeatureFlags();

      resetFeatureFlags();

      const afterReset = getFeatureFlags();

      // Should be different instances after reset
      expect(beforeReset).not.toBe(afterReset);

      testLogger.debug("Feature flags reloaded after reset");
    });
  });

  describe("Feature Flag Categories", () => {
    it("should have all authentication feature flags", () => {
      testLogger.info("Testing authentication feature flag categories");

      const flags = getFeatureFlags();

      expect(flags).toHaveProperty("enablePasswordReset");
      expect(flags).toHaveProperty("enableSocialLogin");
      expect(flags).toHaveProperty("enableTwoFactorAuth");

      testLogger.debug("Authentication feature flags verified", {
        passwordReset: flags.enablePasswordReset,
        socialLogin: flags.enableSocialLogin,
        twoFactorAuth: flags.enableTwoFactorAuth,
      });
    });

    it("should have all upload feature flags", () => {
      testLogger.info("Testing upload feature flag categories");

      const flags = getFeatureFlags();

      expect(flags).toHaveProperty("enableMultipleFileUpload");
      expect(flags).toHaveProperty("enableDragDropUpload");
      expect(flags).toHaveProperty("enableUploadProgress");
      expect(flags).toHaveProperty("enableFilePreview");

      testLogger.debug("Upload feature flags verified", {
        multipleFileUpload: flags.enableMultipleFileUpload,
        dragDropUpload: flags.enableDragDropUpload,
        uploadProgress: flags.enableUploadProgress,
        filePreview: flags.enableFilePreview,
      });
    });

    it("should have all performance feature flags", () => {
      testLogger.info("Testing performance feature flag categories");

      const flags = getFeatureFlags();

      expect(flags).toHaveProperty("enableVirtualization");
      expect(flags).toHaveProperty("enableLazyLoading");
      expect(flags).toHaveProperty("enableCodeSplitting");

      testLogger.debug("Performance feature flags verified", {
        virtualization: flags.enableVirtualization,
        lazyLoading: flags.enableLazyLoading,
        codeSplitting: flags.enableCodeSplitting,
      });
    });

    it("should have all monitoring feature flags", () => {
      testLogger.info("Testing monitoring feature flag categories");

      const flags = getFeatureFlags();

      expect(flags).toHaveProperty("enableAnalytics");
      expect(flags).toHaveProperty("enableErrorReporting");
      expect(flags).toHaveProperty("enablePerformanceMonitoring");
      expect(flags).toHaveProperty("enableWebVitals");

      testLogger.debug("Monitoring feature flags verified", {
        analytics: flags.enableAnalytics,
        errorReporting: flags.enableErrorReporting,
        performanceMonitoring: flags.enablePerformanceMonitoring,
        webVitals: flags.enableWebVitals,
      });
    });
  });

  describe("Error Handling", () => {
    it("should handle missing environment configuration gracefully", () => {
      testLogger.info("Testing missing environment configuration handling");

      // Mock environment config to return undefined values
      vi.doMock("@/lib/config/environment", () => ({
        getEnvironmentConfig: () => ({
          NODE_ENV: undefined,
          ENABLE_ANALYTICS: undefined,
          ENABLE_ERROR_REPORTING: undefined,
          ENABLE_PERFORMANCE_MONITORING: undefined,
        }),
      }));

      resetFeatureFlags();
      const flags = getFeatureFlags();

      // Should use safe defaults
      expect(typeof flags.enableAnalytics).toBe("boolean");
      expect(typeof flags.enableErrorReporting).toBe("boolean");
      expect(typeof flags.enablePerformanceMonitoring).toBe("boolean");

      testLogger.debug(
        "Missing environment configuration handled gracefully",
        flags,
      );
    });
  });
});
