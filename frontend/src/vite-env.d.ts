/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly NODE_ENV: string;
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_API_TIMEOUT?: string;
  readonly VITE_WS_URL?: string;
  readonly VITE_SENTRY_DSN?: string;
  readonly VITE_ENABLE_ANALYTICS?: string;
  readonly VITE_LOG_LEVEL?: string;
  readonly VITE_ENABLE_ERROR_REPORTING?: string;
  readonly VITE_ENABLE_PERFORMANCE_MONITORING?: string;
  readonly VITE_APP_VERSION?: string;
  readonly VITE_APP_NAME?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
