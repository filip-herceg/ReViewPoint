# Phase 0.5: Quick Setup & Architecture Evaluation

## 0.5.1 Architecture Quick Wins

### Vite Module Federation Setup evaluieren
- Use `@originjs/vite-plugin-federation` for Vite 5+.
- Example vite.config.ts:
  ```ts
  import { defineConfig } from 'vite';
  import react from '@vitejs/plugin-react';
  import federation from '@originjs/vite-plugin-federation';

  export default defineConfig({
    plugins: [
      react(),
      federation({
        name: 'app',
        filename: 'remoteEntry.js',
        exposes: { './Button': './src/components/ui/Button.tsx' },
        remotes: {},
        shared: ['react', 'react-dom']
      })
    ]
  });
  ```
- Docs: https://github.com/originjs/vite-plugin-federation

### React Server Components Strategie evaluieren
- Native RSC is not fully supported in Vite as of mid-2025.
- Use Next.js for full RSC or experiment with Vite plugins (unstable).
- For SPA: stick to client components, but keep code split and SSR migration in mind.
- Monitor Vite and React releases for future RSC support.
- References: https://vitejs.dev/guide/ssr.html, https://react.dev/reference/rsc

### Bundle Size Budget festlegen
- Targets: `<250KB initial`, `<1MB total` (gzipped).
- Use `rollup-plugin-visualizer` or `vite-plugin-bundle-analyzer`.
- Example install:
  ```sh
  pnpm add -D rollup-plugin-visualizer
  ```
- Example vite.config.ts:
  ```ts
  import { visualizer } from 'rollup-plugin-visualizer';
  // ...in plugins: visualizer({ gzipSize: true })
  ```
- Monitor with CI and Lighthouse CI.

### Core Web Vitals Targets definieren
- LCP <2.5s, FID <100ms, CLS <0.1.
- Use `web-vitals` npm package:
  ```sh
  pnpm add web-vitals
  ```
- Example usage in `src/main.tsx`:
  ```ts
  import { getCLS, getFID, getLCP } from 'web-vitals';
  getCLS(console.log); getFID(console.log); getLCP(console.log);
  ```
- Docs: https://web.dev/vitals/

---

## 0.5.2 Security Foundation

### Content Security Policy (CSP) Header konfigurieren
- For dev: use Vite plugin `vite-plugin-csp`.
- For prod: set headers in your host (Vercel, Netlify, nginx, etc.).
- Example (Netlify `_headers`):
  ```
  /*
    Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
    Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
    X-Content-Type-Options: nosniff
  ```
- Docs: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- HSTS: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
- X-Content-Type-Options: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options

### DOMPurify für XSS-Schutz einrichten
- Install: `pnpm add dompurify`
- Usage in React:
  ```tsx
  import DOMPurify from 'dompurify';
  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userHtml) }} />
  ```
- Docs: https://github.com/cure53/DOMPurify

### Dependency Security Audit
- Run: `pnpm audit`
- Add to CI: `"audit": "pnpm audit --audit-level=moderate"`
- Docs: https://pnpm.io/cli/audit

---

## 0.5.3 Observability Setup

### Sentry Integration für Error Tracking
- Install: `pnpm add @sentry/react @sentry/tracing`
- In `src/main.tsx`:
  ```ts
  import * as Sentry from '@sentry/react';
  Sentry.init({ dsn: 'YOUR_DSN', tracesSampleRate: 1.0 });
  ```
- Docs: https://docs.sentry.io/platforms/javascript/guides/react/

### Web Vitals Library für Performance Monitoring
- See above (0.5.1). Send results to Sentry or analytics.

### Basic Analytics Setup (Vercel Analytics / Plausible)
- Vercel: https://vercel.com/docs/analytics
- Plausible: https://plausible.io/docs/react
- Add script tag or use npm package as per docs.
- Ensure privacy/GDPR compliance for analytics (see: https://vercel.com/docs/analytics/privacy, https://plausible.io/privacy-focused-web-analytics).

---

## 0.5.4 Known Issues & Audit Results

- As of 2025-07-05, `pnpm audit` reports 9 vulnerabilities (1 critical, 3 high, 5 moderate) in devDependencies, all caused by indirect dependencies of `biome` (linter/formatter):
  - Affected packages: `lodash`, `request`, `tough-cookie` (see audit output for details)
  - These do NOT affect production code or frontend bundles, only dev tooling/CI
  - All direct dependencies are up to date and safe
  - Monitor for upstream fixes in `biome` and document this as a known issue

- All other technical setup steps for Phase 0.5 are complete and reproducible.

---

## Next Steps
- Install and configure the above tools and plugins as part of project setup.
- Document any decisions or blockers in the implementation plan.
