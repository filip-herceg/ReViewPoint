/**
 * Performance Monitoring System
 * Web vitals tracking, bundle analysis, and performance optimization
 */

import { onCLS, onFCP, onINP, onLCP, onTTFB, Metric } from "web-vitals";
import logger from "@/logger";
import {
  getEnvironmentConfig,
  getMonitoringConfig,
} from "@/lib/config/environment";
import { isFeatureEnabled } from "@/lib/config/featureFlags";

export interface PerformanceMetric {
  id: string;
  name: string;
  value: number;
  rating: "good" | "needs-improvement" | "poor";
  timestamp: number;
  url: string;
  navigationType: string;
  deviceType: "mobile" | "tablet" | "desktop";
}

export interface PerformanceConfig {
  enableWebVitals: boolean;
  enableResourceTiming: boolean;
  enableNavigationTiming: boolean;
  enableUserTiming: boolean;
  sampleRate: number;
  reportToAnalytics: boolean;
}

/**
 * Performance monitoring service
 */
class PerformanceMonitoringService {
  private metrics: PerformanceMetric[] = [];
  private config: PerformanceConfig;
  private isInitialized = false;
  private observer?: PerformanceObserver;

  constructor() {
    const monitoringConfig = getMonitoringConfig();

    this.config = {
      enableWebVitals: isFeatureEnabled("enableWebVitals"),
      enableResourceTiming: isFeatureEnabled("enablePerformanceMonitoring"),
      enableNavigationTiming: isFeatureEnabled("enablePerformanceMonitoring"),
      enableUserTiming: isFeatureEnabled("enablePerformanceMonitoring"),
      sampleRate: 1.0, // 100% sampling in dev, can be reduced in production
      reportToAnalytics: monitoringConfig.enableAnalytics,
    };
  }

  /**
   * Initialize performance monitoring
   */
  initialize(): void {
    if (this.isInitialized) {
      logger.warn("Performance monitoring already initialized");
      return;
    }

    try {
      if (this.config.enableWebVitals) {
        this.setupWebVitalsTracking();
      }

      if (this.config.enableResourceTiming) {
        this.setupResourceTimingTracking();
      }

      if (this.config.enableNavigationTiming) {
        this.setupNavigationTimingTracking();
      }

      this.isInitialized = true;
      logger.info(
        "Performance monitoring initialized successfully",
        this.config,
      );
    } catch (error) {
      logger.error("Failed to initialize performance monitoring", error);
    }
  }

  /**
   * Setup Web Vitals tracking
   */
  private setupWebVitalsTracking(): void {
    if (typeof window === "undefined") return;

    const handleMetric = (metric: Metric) => {
      this.recordMetric({
        id: metric.id,
        name: metric.name,
        value: metric.value,
        rating: this.getMetricRating(metric.name, metric.value),
        timestamp: Date.now(),
        url: window.location.href,
        navigationType: this.getNavigationType(),
        deviceType: this.getDeviceType(),
      });
    };

    // Core Web Vitals
    onCLS(handleMetric);
    onFCP(handleMetric);
    onINP(handleMetric); // Replaced FID with INP (new standard)
    onLCP(handleMetric);
    onTTFB(handleMetric);

    logger.debug("Web Vitals tracking setup complete");
  }

  /**
   * Setup resource timing tracking
   */
  private setupResourceTimingTracking(): void {
    if (typeof window === "undefined" || !window.PerformanceObserver) return;

    try {
      this.observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === "resource") {
            this.recordResourceTiming(entry as PerformanceResourceTiming);
          }
        });
      });

      this.observer.observe({ entryTypes: ["resource"] });
      logger.debug("Resource timing tracking setup complete");
    } catch (error) {
      logger.warn("Failed to setup resource timing tracking", error);
    }
  }

  /**
   * Setup navigation timing tracking
   */
  private setupNavigationTimingTracking(): void {
    if (typeof window === "undefined") return;

    window.addEventListener("load", () => {
      setTimeout(() => {
        this.recordNavigationTiming();
      }, 0);
    });

    logger.debug("Navigation timing tracking setup complete");
  }

  /**
   * Record a performance metric
   */
  private recordMetric(metric: PerformanceMetric): void {
    this.metrics.push(metric);

    // Limit stored metrics
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-50);
    }

    logger.debug("Performance metric recorded", {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
    });

    // Report to analytics if enabled
    if (this.config.reportToAnalytics) {
      this.reportMetricToAnalytics(metric);
    }
  }

  /**
   * Record resource timing data
   */
  private recordResourceTiming(entry: PerformanceResourceTiming): void {
    // Only track significant resources
    if (entry.duration < 100) return; // Skip resources that load very quickly

    const metric: PerformanceMetric = {
      id: `resource_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: "resource-timing",
      value: entry.duration,
      rating:
        entry.duration < 500
          ? "good"
          : entry.duration < 1000
            ? "needs-improvement"
            : "poor",
      timestamp: Date.now(),
      url: entry.name,
      navigationType: entry.initiatorType,
      deviceType: this.getDeviceType(),
    };

    this.recordMetric(metric);
  }

  /**
   * Record navigation timing data
   */
  private recordNavigationTiming(): void {
    if (typeof window === "undefined" || !window.performance?.navigation)
      return;

    const navigation = window.performance.navigation;
    const timing = window.performance.timing;

    const metrics = [
      {
        name: "dns-lookup",
        value: timing.domainLookupEnd - timing.domainLookupStart,
      },
      {
        name: "tcp-connect",
        value: timing.connectEnd - timing.connectStart,
      },
      {
        name: "request-response",
        value: timing.responseEnd - timing.requestStart,
      },
      {
        name: "dom-processing",
        value: timing.domComplete - timing.domLoading,
      },
      {
        name: "page-load",
        value: timing.loadEventEnd - timing.navigationStart,
      },
    ];

    metrics.forEach((metricData) => {
      if (metricData.value > 0) {
        const metric: PerformanceMetric = {
          id: `nav_${metricData.name}_${Date.now()}`,
          name: metricData.name,
          value: metricData.value,
          rating: this.getTimingRating(metricData.name, metricData.value),
          timestamp: Date.now(),
          url: window.location.href,
          navigationType: this.getNavigationType(),
          deviceType: this.getDeviceType(),
        };

        this.recordMetric(metric);
      }
    });
  }

  /**
   * Get metric rating based on thresholds
   */
  private getMetricRating(
    name: string,
    value: number,
  ): "good" | "needs-improvement" | "poor" {
    const thresholds: Record<string, { good: number; poor: number }> = {
      CLS: { good: 0.1, poor: 0.25 },
      FCP: { good: 1800, poor: 3000 },
      INP: { good: 200, poor: 500 }, // INP replaced FID
      LCP: { good: 2500, poor: 4000 },
      TTFB: { good: 800, poor: 1800 },
    };

    const threshold = thresholds[name];
    if (!threshold) return "good";

    if (value <= threshold.good) return "good";
    if (value <= threshold.poor) return "needs-improvement";
    return "poor";
  }

  /**
   * Get timing rating for navigation metrics
   */
  private getTimingRating(
    name: string,
    value: number,
  ): "good" | "needs-improvement" | "poor" {
    const thresholds: Record<string, { good: number; poor: number }> = {
      "dns-lookup": { good: 50, poor: 200 },
      "tcp-connect": { good: 100, poor: 500 },
      "request-response": { good: 500, poor: 1500 },
      "dom-processing": { good: 1000, poor: 3000 },
      "page-load": { good: 2000, poor: 5000 },
    };

    const threshold = thresholds[name] || { good: 1000, poor: 3000 };

    if (value <= threshold.good) return "good";
    if (value <= threshold.poor) return "needs-improvement";
    return "poor";
  }

  /**
   * Get navigation type
   */
  private getNavigationType(): string {
    if (typeof window === "undefined" || !window.performance?.navigation) {
      return "unknown";
    }

    const types = ["navigate", "reload", "back_forward", "prerender"];
    return types[window.performance.navigation.type] || "unknown";
  }

  /**
   * Get device type based on screen size
   */
  private getDeviceType(): "mobile" | "tablet" | "desktop" {
    if (typeof window === "undefined") return "desktop";

    const width = window.innerWidth;
    if (width < 768) return "mobile";
    if (width < 1024) return "tablet";
    return "desktop";
  }

  /**
   * Report metric to analytics service
   */
  private reportMetricToAnalytics(metric: PerformanceMetric): void {
    // This could be sent to Google Analytics, Plausible, or other services
    if (typeof window !== "undefined" && (window as any).plausible) {
      try {
        (window as any).plausible("Performance Metric", {
          props: {
            metric_name: metric.name,
            metric_value: metric.value,
            metric_rating: metric.rating,
            device_type: metric.deviceType,
          },
        });
      } catch (error) {
        logger.warn("Failed to report metric to analytics", error);
      }
    }
  }

  /**
   * Get all recorded metrics
   */
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  /**
   * Get metrics by name
   */
  getMetricsByName(name: string): PerformanceMetric[] {
    return this.metrics.filter((metric) => metric.name === name);
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary(): {
    coreWebVitals: Record<string, PerformanceMetric | undefined>;
    averages: Record<string, number>;
    ratings: Record<string, number>;
  } {
    const coreWebVitals = {
      CLS: this.metrics.find((m) => m.name === "CLS"),
      FCP: this.metrics.find((m) => m.name === "FCP"),
      INP: this.metrics.find((m) => m.name === "INP"),
      LCP: this.metrics.find((m) => m.name === "LCP"),
      TTFB: this.metrics.find((m) => m.name === "TTFB"),
    };

    const metricGroups = this.metrics.reduce(
      (acc, metric) => {
        if (!acc[metric.name]) acc[metric.name] = [];
        acc[metric.name].push(metric.value);
        return acc;
      },
      {} as Record<string, number[]>,
    );

    const averages = Object.entries(metricGroups).reduce(
      (acc, [name, values]) => {
        acc[name] = values.reduce((sum, val) => sum + val, 0) / values.length;
        return acc;
      },
      {} as Record<string, number>,
    );

    const ratings = this.metrics.reduce(
      (acc, metric) => {
        acc[metric.rating] = (acc[metric.rating] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    return { coreWebVitals, averages, ratings };
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics = [];
    logger.info("All performance metrics cleared");
  }

  /**
   * Cleanup monitoring
   */
  cleanup(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = undefined;
    }
    this.isInitialized = false;
    logger.info("Performance monitoring cleaned up");
  }
}

// Singleton performance monitoring service
export const performanceMonitoringService = new PerformanceMonitoringService();

/**
 * Initialize performance monitoring on app startup
 */
export function initializePerformanceMonitoring(): void {
  if (isFeatureEnabled("enablePerformanceMonitoring")) {
    performanceMonitoringService.initialize();
  }
}

/**
 * Hook to access performance monitoring functionality
 */
export function usePerformanceMonitoring() {
  return {
    getMetrics: performanceMonitoringService.getMetrics.bind(
      performanceMonitoringService,
    ),
    getPerformanceSummary:
      performanceMonitoringService.getPerformanceSummary.bind(
        performanceMonitoringService,
      ),
    clearMetrics: performanceMonitoringService.clearMetrics.bind(
      performanceMonitoringService,
    ),
  };
}

/**
 * Performance budget checker
 */
export function checkPerformanceBudget(): {
  passed: boolean;
  violations: Array<{ metric: string; value: number; budget: number }>;
} {
  const summary = performanceMonitoringService.getPerformanceSummary();
  const budgets = {
    LCP: 2500, // 2.5 seconds
    INP: 200, // 200 milliseconds (replaced FID)
    CLS: 0.1, // 0.1
    FCP: 1800, // 1.8 seconds
    TTFB: 800, // 800 milliseconds
  };

  const violations: Array<{ metric: string; value: number; budget: number }> =
    [];

  Object.entries(budgets).forEach(([metric, budget]) => {
    const metricData = summary.coreWebVitals[metric];
    if (metricData && metricData.value > budget) {
      violations.push({
        metric,
        value: metricData.value,
        budget,
      });
    }
  });

  return {
    passed: violations.length === 0,
    violations,
  };
}
