import Plausible from 'plausible-tracker';

// Initialize Plausible analytics (replace 'your-domain.com' with your actual domain)
const plausible = Plausible({ domain: 'your-domain.com' });
plausible.enableAutoPageviews();
plausible.enableAutoOutboundTracking();

// ...existing code (Sentry, web-vitals, React app bootstrap)
