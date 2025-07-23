import Plausible from "plausible-tracker";
import { createTestError } from "../tests/test-templates";

// Initialize Plausible analytics (replace 'your-domain.com' with your actual domain)
try {
  const plausible = Plausible({ domain: "your-domain.com" });
  plausible.enableAutoPageviews();
  plausible.enableAutoOutboundTracking();
} catch {
  // Defensive: log analytics init error, do not break app
  const _error = createTestError("Analytics initialization error");
  // Optionally, send to logger or Sentry here
}

// ...existing code (Sentry, web-vitals, React app bootstrap)
