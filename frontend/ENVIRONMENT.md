# Environment Configuration Guide

This guide explains how to configure environment variables for the ReViewPoint frontend application.

## 📁 Environment Files Overview

The frontend uses multiple environment files for different scenarios:

```
frontend/
├── .env.example          # 📖 Comprehensive documentation template
├── .env.template         # 📚 Detailed configuration guide  
├── .env.local.example    # 🚀 Quick local development setup
├── .env.development      # 🛠️ Development environment defaults
├── .env.staging          # 🎭 Staging environment configuration
├── .env.production       # 🚀 Production environment configuration
├── .env.test             # 🧪 Testing environment configuration
└── .env.local            # 🔒 Your personal local configuration (not in git)
```

## 🚀 Quick Start

### For Local Development

1. **Copy the local development template:**

   ```bash
   cp .env.local.example .env.local
   ```

2. **Configure your backend URL:**
   Edit `.env.local` and uncomment the appropriate `VITE_API_BASE_URL`:

   ```bash
   # For local backend on port 8000
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start development server:**

   ```bash
   pnpm run dev
   ```

### For Team Development

1. **Use environment-specific files:**
   - `.env.development` - Shared development settings
   - `.env.staging` - Staging environment
   - `.env.production` - Production environment

2. **Override with local settings:**
   Create `.env.local` for personal overrides that won't be committed to git.

## 🔧 Configuration Options

### 🌐 API Configuration

| Variable | Description | Examples |
|----------|-------------|----------|
| `VITE_API_BASE_URL` | Backend API endpoint | `http://localhost:8000`<br>`https://api.reviewpoint.com` |
| `VITE_API_TIMEOUT` | Request timeout (ms) | `10000` (dev)<br>`20000` (prod) |
| `VITE_WS_URL` | WebSocket endpoint | `ws://localhost:8000/api/v1`<br>`wss://api.reviewpoint.com/api/v1` |

### 📊 Monitoring Configuration

| Variable | Description | Values |
|----------|-------------|--------|
| `VITE_SENTRY_DSN` | Error tracking service | Sentry DSN URL or empty |
| `VITE_ENABLE_ANALYTICS` | Usage analytics | `true` \| `false` |
| `VITE_LOG_LEVEL` | Console logging level | `error` \| `warn` \| `info` \| `debug` \| `trace` |
| `VITE_ENABLE_ERROR_REPORTING` | Auto error reporting | `true` \| `false` |
| `VITE_ENABLE_PERFORMANCE_MONITORING` | Performance tracking | `true` \| `false` |

### 🎛️ Feature Flags

All feature flags follow the pattern `VITE_FEATURE_ENABLE_*` and accept `true` or `false`.

#### Authentication Features

- `VITE_FEATURE_ENABLE_PASSWORD_RESET` - Password reset via email
- `VITE_FEATURE_ENABLE_SOCIAL_LOGIN` - OAuth social login  
- `VITE_FEATURE_ENABLE_TWO_FACTOR_AUTH` - Two-factor authentication

#### Upload Features

- `VITE_FEATURE_ENABLE_MULTIPLE_FILE_UPLOAD` - Multi-file upload
- `VITE_FEATURE_ENABLE_DRAG_DROP_UPLOAD` - Drag & drop interface
- `VITE_FEATURE_ENABLE_UPLOAD_PROGRESS` - Upload progress display
- `VITE_FEATURE_ENABLE_FILE_PREVIEW` - File preview functionality

#### Review Features

- `VITE_FEATURE_ENABLE_AI_REVIEWS` - AI-powered document analysis
- `VITE_FEATURE_ENABLE_COLLABORATIVE_REVIEWS` - Real-time collaboration
- `VITE_FEATURE_ENABLE_REVIEW_COMMENTS` - Comment system
- `VITE_FEATURE_ENABLE_REVIEW_EXPORT` - Export functionality

#### UI Features  

- `VITE_FEATURE_ENABLE_DARK_MODE` - Light/dark theme switching
- `VITE_FEATURE_ENABLE_NOTIFICATIONS` - Push notifications
- `VITE_FEATURE_ENABLE_BREADCRUMBS` - Navigation breadcrumbs
- `VITE_FEATURE_ENABLE_SIDEBAR` - Collapsible sidebar
- `VITE_FEATURE_ENABLE_WEBSOCKET` - Real-time features

#### Performance Features

- `VITE_FEATURE_ENABLE_VIRTUALIZATION` - Virtual scrolling for large lists
- `VITE_FEATURE_ENABLE_LAZY_LOADING` - Component lazy loading
- `VITE_FEATURE_ENABLE_CODE_SPLITTING` - Bundle code splitting

## 🌍 Environment-Specific Setup

### Development Environment

```bash
# .env.development or .env.local
NODE_ENV=development
VITE_API_BASE_URL=http://localhost:8000
VITE_LOG_LEVEL=debug
VITE_ENABLE_ANALYTICS=false
VITE_APP_NAME=ReViewPoint (Dev)
VITE_FEATURE_ENABLE_DEV_TOOLS=true
VITE_FEATURE_ENABLE_DEBUG_MODE=true
```

### Staging Environment

```bash
# .env.staging
NODE_ENV=staging
VITE_API_BASE_URL=https://api-staging.reviewpoint.com
VITE_WS_URL=wss://api-staging.reviewpoint.com/api/v1
VITE_LOG_LEVEL=info
VITE_ENABLE_ANALYTICS=true
VITE_APP_NAME=ReViewPoint (Staging)
```

### Production Environment

```bash
# .env.production
NODE_ENV=production
VITE_API_BASE_URL=https://api.reviewpoint.com
VITE_WS_URL=wss://api.reviewpoint.com/api/v1
VITE_LOG_LEVEL=warn
VITE_ENABLE_ANALYTICS=true
VITE_SENTRY_DSN=https://your-dsn@sentry.io/project
VITE_APP_NAME=ReViewPoint
```

### Testing Environment

```bash
# .env.test
NODE_ENV=test
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=5000
VITE_LOG_LEVEL=error
VITE_ENABLE_ANALYTICS=false
VITE_APP_NAME=ReViewPoint (Test)
VITE_FEATURE_ENABLE_TEST_MODE=true
```

## 📋 Common Configuration Scenarios

### 🏠 Local Development with Local Backend

```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/api/v1
VITE_LOG_LEVEL=debug
VITE_ENABLE_ANALYTICS=false
```

### 🐳 Docker Development

```bash
# .env.local
VITE_API_BASE_URL=http://host.docker.internal:8000
VITE_WS_URL=ws://host.docker.internal:8000/api/v1
```

### 🌐 Frontend-Only Development (Using Staging API)

```bash
# .env.local
VITE_API_BASE_URL=https://api-staging.reviewpoint.com
VITE_WS_URL=wss://api-staging.reviewpoint.com/api/v1
VITE_ENABLE_ANALYTICS=false
```

### 👥 Team Development (Shared Backend)

```bash
# .env.local
VITE_API_BASE_URL=http://dev-server.local:8000
VITE_WS_URL=ws://dev-server.local:8000/api/v1
```

## 🔍 Troubleshooting

### CORS Errors

**Problem:** API requests fail with CORS errors

**Solutions:**

1. Ensure backend CORS is configured for your frontend URL
2. Verify `VITE_API_BASE_URL` is correct and reachable
3. Use Vite proxy by leaving `VITE_API_BASE_URL` undefined in development

### WebSocket Connection Failed

**Problem:** Real-time features don't work

**Solutions:**

1. Verify `VITE_WS_URL` is correct
2. Check if backend WebSocket server is running
3. Temporarily disable WebSocket: `VITE_FEATURE_ENABLE_WEBSOCKET=false`

### 502/503 API Errors

**Problem:** All API requests fail

**Solutions:**

1. Check if backend server is running
2. Verify port number in `VITE_API_BASE_URL`
3. Test API URL directly in browser

### Slow Performance

**Problem:** App feels sluggish

**Solutions:**

1. Reduce logging: `VITE_LOG_LEVEL=warn`
2. Enable performance features:

   ```bash
   VITE_FEATURE_ENABLE_LAZY_LOADING=true
   VITE_FEATURE_ENABLE_VIRTUALIZATION=true
   VITE_FEATURE_ENABLE_CODE_SPLITTING=true
   ```

### Hot Reload Not Working

**Problem:** Changes don't reflect immediately

**Solutions:**

1. Ensure `VITE_REACT_DEVTOOLS=true`
2. Restart development server
3. Clear browser cache and `node_modules/.cache`

## 🔒 Security Best Practices

### Sensitive Data

- ✅ **Never commit `.env.local`** - Add to `.gitignore`
- ✅ **Use different Sentry DSNs** for each environment
- ✅ **Rotate API keys regularly** in production
- ✅ **Use HTTPS/WSS** in staging and production
- ❌ **Don't put secrets** in environment variables (use Vite only for public config)

### Production Checklist

- [ ] `NODE_ENV=production`
- [ ] HTTPS API URL (`https://`)
- [ ] Secure WebSocket URL (`wss://`)
- [ ] Analytics enabled (`VITE_ENABLE_ANALYTICS=true`)
- [ ] Error reporting configured (`VITE_SENTRY_DSN`)
- [ ] Debug features disabled (`VITE_FEATURE_ENABLE_DEBUG_MODE=false`)
- [ ] Appropriate log level (`VITE_LOG_LEVEL=warn`)

## 📚 Additional Resources

- [Vite Environment Variables Documentation](https://vitejs.dev/guide/env-and-mode.html)
- [ReViewPoint Backend Configuration](../backend/README.md)
- [Feature Flags Documentation](./docs/feature-flags.md)
- [Deployment Guide](./docs/deployment.md)

## 🆘 Getting Help

If you're having trouble with environment configuration:

1. Check this guide first
2. Look at existing environment files (`.env.development`, etc.)
3. Review the comprehensive documentation in `.env.template`
4. Ask in the team chat or create an issue

---

**Pro Tip:** Use `.env.local` for personal development settings that won't affect other team members!
