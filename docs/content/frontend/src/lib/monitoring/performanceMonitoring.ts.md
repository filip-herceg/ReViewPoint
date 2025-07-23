# performanceMonitoring.ts - Advanced Performance Monitoring System

## Purpose

The `performanceMonitoring.ts` file provides comprehensive performance monitoring for the ReViewPoint frontend application. It tracks Core Web Vitals, resource timing, navigation metrics, and provides detailed performance analytics with automatic reporting and budget validation.

## Key Components

### **Performance Metric Interface**

```typescript
interface PerformanceMetric {
  id: string; // Unique metric identifier
  name: string; // Metric name (CLS, FCP, INP, LCP, TTFB)
  value: number; // Measured value
  rating: "good" | "needs-improvement" | "poor";
  timestamp: number; // Measurement timestamp
  url: string; // Page URL when measured
  navigationType: string; // Navigation type (navigate, reload, etc.)
  deviceType: "mobile" | "tablet" | "desktop";
}
```

### **Performance Configuration**

```typescript
interface PerformanceConfig {
  enableWebVitals: boolean; // Track Core Web Vitals
  enableResourceTiming: boolean; // Track resource load times
  enableNavigationTiming: boolean; // Track navigation metrics
  enableUserTiming: boolean; // Track custom user marks
  sampleRate: number; // Sampling rate (0.0 to 1.0)
  reportToAnalytics: boolean; // Send metrics to analytics
}
```

## Core Web Vitals Tracking

### **Supported Metrics**

- **CLS (Cumulative Layout Shift)**: Visual stability measurement
- **FCP (First Contentful Paint)**: Initial content rendering time
- **INP (Interaction to Next Paint)**: Responsiveness measurement (replaces FID)
- **LCP (Largest Contentful Paint)**: Loading performance
- **TTFB (Time to First Byte)**: Server response time

### **Web Vitals Implementation**

```typescript
private setupWebVitalsTracking(): void {
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

  // Core Web Vitals tracking
  onCLS(handleMetric);
  onFCP(handleMetric);
  onINP(handleMetric); // New standard replacing FID
  onLCP(handleMetric);
  onTTFB(handleMetric);
}
```

### **Performance Rating Thresholds**

```typescript
const thresholds = {
  CLS: { good: 0.1, poor: 0.25 }, // Layout stability
  FCP: { good: 1800, poor: 3000 }, // First paint (ms)
  INP: { good: 200, poor: 500 }, // Interaction response (ms)
  LCP: { good: 2500, poor: 4000 }, // Largest paint (ms)
  TTFB: { good: 800, poor: 1800 }, // Server response (ms)
};

// Rating classification:
// "good" - Meets performance standards
// "needs-improvement" - Minor performance issues
// "poor" - Significant performance problems
```

## Resource Timing Monitoring

### **Resource Performance Tracking**

```typescript
private setupResourceTimingTracking(): void {
  this.observer = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
      if (entry.entryType === "resource") {
        this.recordResourceTiming(entry);
      }
    });
  });

  this.observer.observe({ entryTypes: ["resource"] });
}
```

### **Resource Timing Analysis**

```typescript
private recordResourceTiming(entry: PerformanceResourceTiming): void {
  // Filter significant resources (>100ms load time)
  if (entry.duration < 100) return;

  const metric: PerformanceMetric = {
    id: `resource_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    name: "resource-timing",
    value: entry.duration,
    rating: entry.duration < 500 ? "good" :
            entry.duration < 1000 ? "needs-improvement" : "poor",
    timestamp: Date.now(),
    url: entry.name,              // Resource URL
    navigationType: entry.initiatorType, // script, css, img, etc.
    deviceType: this.getDeviceType(),
  };
}
```

## Navigation Timing Analysis

### **Navigation Metrics**

```typescript
const navigationMetrics = [
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
```

### **Navigation Timing Thresholds**

```typescript
const navigationThresholds = {
  "dns-lookup": { good: 50, poor: 200 }, // DNS resolution time
  "tcp-connect": { good: 100, poor: 500 }, // TCP connection time
  "request-response": { good: 500, poor: 1500 }, // Server response time
  "dom-processing": { good: 1000, poor: 3000 }, // DOM parsing time
  "page-load": { good: 2000, poor: 5000 }, // Complete page load
};
```

## Device and Context Detection

### **Device Type Classification**

```typescript
private getDeviceType(): "mobile" | "tablet" | "desktop" {
  const width = window.innerWidth;
  if (width < 768) return "mobile";
  if (width < 1024) return "tablet";
  return "desktop";
}
```

### **Navigation Type Detection**

```typescript
private getNavigationType(): string {
  const types = ["navigate", "reload", "back_forward", "prerender"];
  return types[window.performance.navigation.type] || "unknown";
}
```

## Analytics Integration

### **External Analytics Reporting**

```typescript
private reportMetricToAnalytics(metric: PerformanceMetric): void {
  // Plausible Analytics integration
  if (window.plausible) {
    window.plausible("Performance Metric", {
      props: {
        metric_name: metric.name,
        metric_value: metric.value,
        metric_rating: metric.rating,
        device_type: metric.deviceType,
      },
    });
  }
}
```

### **Metric Storage Management**

```typescript
private recordMetric(metric: PerformanceMetric): void {
  this.metrics.push(metric);

  // Limit stored metrics to prevent memory issues
  if (this.metrics.length > 100) {
    this.metrics = this.metrics.slice(-50); // Keep latest 50
  }

  // Report to analytics if enabled
  if (this.config.reportToAnalytics) {
    this.reportMetricToAnalytics(metric);
  }
}
```

## Performance Analysis Tools

### **Performance Summary Generation**

```typescript
getPerformanceSummary(): {
  coreWebVitals: Record<string, PerformanceMetric | undefined>;
  averages: Record<string, number>;
  ratings: Record<string, number>;
} {
  return {
    coreWebVitals: {
      CLS: this.metrics.find(m => m.name === "CLS"),
      FCP: this.metrics.find(m => m.name === "FCP"),
      INP: this.metrics.find(m => m.name === "INP"),
      LCP: this.metrics.find(m => m.name === "LCP"),
      TTFB: this.metrics.find(m => m.name === "TTFB"),
    },
    averages: calculateAverages(),
    ratings: countRatings(),
  };
}
```

### **Performance Budget Validation**

```typescript
function checkPerformanceBudget(): {
  passed: boolean;
  violations: Array<{ metric: string; value: number; budget: number }>;
} {
  const budgets = {
    LCP: 2500, // 2.5 seconds
    INP: 200, // 200 milliseconds
    CLS: 0.1, // 0.1 shift score
    FCP: 1800, // 1.8 seconds
    TTFB: 800, // 800 milliseconds
  };

  const violations = [];
  // Check each metric against budget
  Object.entries(budgets).forEach(([metric, budget]) => {
    const metricData = summary.coreWebVitals[metric];
    if (metricData && metricData.value > budget) {
      violations.push({ metric, value: metricData.value, budget });
    }
  });

  return { passed: violations.length === 0, violations };
}
```

## Service Architecture

### **Singleton Performance Service**

```typescript
class PerformanceMonitoringService {
  private metrics: PerformanceMetric[] = [];
  private config: PerformanceConfig;
  private isInitialized = false;
  private observer?: PerformanceObserver;

  initialize(): void {
    if (this.isInitialized) return;

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
  }
}

export const performanceMonitoringService = new PerformanceMonitoringService();
```

### **React Hook Integration**

```typescript
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
```

## Dependencies

### **Core Dependencies**

- `web-vitals` - Official Google Web Vitals library
- `@/lib/config/environment` - Environment configuration
- `@/lib/config/featureFlags` - Feature flag management
- `@/logger` - Centralized logging service

### **Browser APIs**

- **Performance Observer API** - Resource and navigation timing
- **Navigation Timing API** - Page load metrics
- **Performance API** - High-resolution timing measurements

## Usage Examples

### **Application Initialization**

```typescript
import { initializePerformanceMonitoring } from '@/lib/monitoring/performanceMonitoring';

// Initialize monitoring on app startup
function App() {
  useEffect(() => {
    initializePerformanceMonitoring();
  }, []);

  return <YourApplication />;
}
```

### **Performance Dashboard Component**

```typescript
import { usePerformanceMonitoring } from '@/lib/monitoring/performanceMonitoring';

function PerformanceDashboard() {
  const { getPerformanceSummary } = usePerformanceMonitoring();
  const summary = getPerformanceSummary();

  return (
    <div>
      <h2>Core Web Vitals</h2>
      {Object.entries(summary.coreWebVitals).map(([name, metric]) => (
        <div key={name}>
          <span>{name}: {metric?.value}ms</span>
          <span className={`rating-${metric?.rating}`}>
            {metric?.rating}
          </span>
        </div>
      ))}
    </div>
  );
}
```

### **Performance Budget Monitoring**

```typescript
import { checkPerformanceBudget } from '@/lib/monitoring/performanceMonitoring';

function BudgetValidator() {
  const budgetCheck = checkPerformanceBudget();

  if (!budgetCheck.passed) {
    console.warn('Performance budget violations:', budgetCheck.violations);
    // Alert development team or show warning
  }

  return budgetCheck.passed ?
    <SuccessIndicator /> :
    <WarningIndicator violations={budgetCheck.violations} />;
}
```

## Performance Optimization Features

### **Metric Filtering**

```typescript
// Only track significant resource loads (>100ms)
if (entry.duration < 100) return;

// Filter out irrelevant metrics
const isRelevantMetric = (metric: PerformanceMetric) => {
  return (
    metric.name in ["CLS", "FCP", "INP", "LCP", "TTFB"] || metric.value > 50
  ); // Threshold for custom metrics
};
```

### **Memory Management**

```typescript
// Automatic metric rotation to prevent memory leaks
if (this.metrics.length > 100) {
  this.metrics = this.metrics.slice(-50); // Keep latest 50
}

// Cleanup on service destruction
cleanup(): void {
  if (this.observer) {
    this.observer.disconnect();
    this.observer = undefined;
  }
  this.isInitialized = false;
}
```

### **Sampling Control**

```typescript
// Configure sampling rate for production
const config: PerformanceConfig = {
  sampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0, // 10% in prod
  // ... other config
};
```

## Related Files

- [errorMonitoring.ts](errorMonitoring.ts.md) - Error tracking integration
- [environment.ts](../config/environment.ts.md) - Configuration management
- [featureFlags.ts](../config/featureFlags.ts.md) - Feature flag integration
- [logger.ts](../../logger.ts.md) - Centralized logging service

## Development Notes

### **Testing Performance Monitoring**

```typescript
// Development helpers for testing
if (process.env.NODE_ENV === "development") {
  window.performanceTest = {
    triggerSlowResource: () => {
      const img = new Image();
      img.src = "/slow-loading-image.jpg";
    },
    simulateLayoutShift: () => {
      // Trigger artificial layout shift for testing
      document.body.style.marginTop = "100px";
      setTimeout(() => {
        document.body.style.marginTop = "0px";
      }, 100);
    },
  };
}
```

### **Performance Monitoring Best Practices**

- **Selective Tracking**: Only monitor metrics that provide actionable insights
- **Budget Enforcement**: Set and enforce performance budgets for critical metrics
- **Real User Monitoring**: Track actual user experience rather than synthetic tests
- **Device-Specific Analysis**: Analyze performance across different device types
- **Continuous Monitoring**: Track performance trends over time, not just point-in-time measurements
