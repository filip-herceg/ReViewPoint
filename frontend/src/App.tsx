import React, { useEffect } from "react";
import { AppRouter } from "@/lib/router/AppRouter";
import { useWebSocketStore } from "@/lib/store/webSocketStore";
import { ThemeProvider } from "@/lib/theme/theme-provider";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { Toaster } from "@/components/ui/sonner";

// Phase 4: Core UI Components
import { LiveRegionProvider } from "@/components/ui/aria-live-region";

// Configuration and monitoring
import { createEnhancedErrorBoundary } from "@/lib/monitoring/errorMonitoring";
import { useFeatureFlag } from "@/lib/config/featureFlags";
import logger from "@/logger";

// Create enhanced error boundary
const EnhancedErrorBoundary = createEnhancedErrorBoundary();

export default function App() {
  const { connect } = useWebSocketStore();

  // Feature flags
  const enableWebSocket = useFeatureFlag("enableWebSocket");
  const enableDarkMode = useFeatureFlag("enableDarkMode");

  // Initialize WebSocket connection on app start if feature is enabled
  useEffect(() => {
    if (enableWebSocket) {
      logger.info("Initializing WebSocket connection");
      connect();
    } else {
      logger.info("WebSocket feature disabled");
    }
  }, [connect, enableWebSocket]);

  // Log app initialization
  useEffect(() => {
    logger.info("App component initialized", {
      features: {
        webSocket: enableWebSocket,
        darkMode: enableDarkMode,
      },
    });
  }, [enableWebSocket, enableDarkMode]);

  return (
    <ThemeProvider defaultTheme={enableDarkMode ? "dark" : "light"}>
      <LiveRegionProvider>
        <EnhancedErrorBoundary>
          <ErrorBoundary>
            <AppRouter />
            <Toaster />
          </ErrorBoundary>
        </EnhancedErrorBoundary>
      </LiveRegionProvider>
    </ThemeProvider>
  );
}
