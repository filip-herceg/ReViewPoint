# Frequently Asked Questions

Common questions and answers about ReViewPoint, covering setup, usage, troubleshooting, and best practices.

## General Questions

### What is ReViewPoint?

ReViewPoint is a modern, full-stack web application built with **FastAPI** (Python backend) and **React** (TypeScript frontend). It provides a robust foundation for web applications with features like:

- **User authentication and authorization** with JWT tokens
- **File upload and management system** with comprehensive security
- **Modern, responsive UI** built with React and shadcn/ui components
- **Comprehensive testing** with 135+ backend tests and growing frontend coverage
- **Developer-friendly tools** with VS Code integration and automated workflows
- **Production-ready architecture** with Docker support and CI/CD integration

### What makes ReViewPoint different?

ReViewPoint focuses on **developer experience** and **production readiness**:

1. **Complete Testing Coverage**: 135+ backend tests with both fast SQLite and production PostgreSQL modes
2. **Developer Tools**: Extensive VS Code tasks, automated setup scripts, comprehensive documentation
3. **Modern Architecture**: Clean separation of concerns, type safety, modern frameworks
4. **Security First**: JWT authentication, file validation, rate limiting, comprehensive error handling
5. **Documentation Driven**: Extensive documentation with interactive examples and API references

### Who should use ReViewPoint?

ReViewPoint is ideal for:

- **Development Teams** building modern web applications
- **Startups** needing a solid foundation with room to scale
- **Learning Projects** wanting to see best practices in action
- **API-First Applications** requiring robust backend APIs
- **File Management Applications** needing secure upload/download functionality

## Setup and Installation

### What are the system requirements?

**Minimum Requirements:**

- **Python 3.11+** for backend development
- **Node.js 18+** for frontend development
- **Docker** (optional, for PostgreSQL database)
- **Git** for version control
- **VS Code** (recommended for best developer experience)

**Recommended System:**

- 8GB+ RAM
- 4+ CPU cores
- 10GB+ free disk space
- Windows 10/11, macOS 10.15+, or Linux Ubuntu 20.04+

### How do I get started quickly?

**30-Second Quick Start:**

```bash
# Clone and setup
git clone <repository-url>
cd ReViewPoint
pnpm install

# Start development (SQLite - simple setup)
pnpm run dev

# Or start with PostgreSQL (auto-setup)
pnpm run dev:postgres
```

**VS Code Users:**

1. Open project in VS Code
2. Install recommended extensions when prompted
3. Use Command Palette: "Tasks: Run Task" → "ReViewPoint: Start Both (Backend + Frontend)"

### Why do I need both SQLite and PostgreSQL modes?

**SQLite Mode** (Fast Development):

- ✅ **No Docker required** - works immediately
- ✅ **Fast testing** - 30-60 seconds for full test suite
- ✅ **Simple setup** - perfect for development and CI
- ❌ Limited to development environments

**PostgreSQL Mode** (Production-Like):

- ✅ **Production database** - real constraints and behavior
- ✅ **Full feature testing** - complete integration testing
- ✅ **Docker automated** - auto-setup with health checks
- ❌ Slower startup - 2-5 minutes for full setup

**Use SQLite for development, PostgreSQL for integration testing and production.**

### How do I switch between databases?

**Switch to SQLite (Simple):**

```bash
pnpm run db:sqlite
# or manually edit backend/config/.env:
# REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db
```

**Switch to PostgreSQL (Production-like):**

```bash
pnpm run postgres:start  # Auto-starts container and runs migrations
# or use VS Code task: "ReViewPoint: Start PostgreSQL Container (Auto-Setup)"
```

The system automatically detects the database type and adjusts behavior accordingly.

## Development Workflow

### What's the recommended development workflow?

**Daily Development Cycle:**

1. **Start Development Environment:**

   ```bash
   # Quick start with SQLite
   pnpm run dev

   # Or full setup with PostgreSQL
   pnpm run dev:postgres
   ```

2. **Development with Testing:**

   ```bash
   # Fast tests during development (SQLite)
   cd backend && hatch run fast:test

   # Or use VS Code task: "ReViewPoint: Run Fast Backend Tests"
   ```

3. **Pre-commit Validation:**

   ```bash
   # Format and lint
   pnpm run lint:fix
   pnpm run format

   # Full test suite
   pnpm run test:all
   ```

4. **Feature Development:**
   - Use VS Code tasks for common operations
   - Run fast tests frequently during development
   - Use full PostgreSQL tests before committing
   - Regenerate API types when backend changes

### How do I run tests effectively?

**Backend Testing Strategy:**

```bash
# Fast development testing (SQLite, 30-60 seconds)
cd backend
hatch run fast:test

# Watch mode for TDD
hatch run fast:watch

# Full production testing (PostgreSQL, 2-5 minutes)
hatch run pytest

# Coverage reports
hatch run fast:coverage
```

**Frontend Testing:**

```bash
cd frontend

# Unit tests
pnpm run test

# Watch mode
pnpm run test:watch

# E2E tests
pnpm run test:e2e

# Coverage
pnpm run test:coverage
```

**VS Code Integration:**
Use the Tasks panel for one-click testing without terminal commands.

### How do I handle API changes?

**When Backend API Changes:**

1. **Export new schema:**

   ```bash
   hatch run python scripts/export-backend-schema.py
   ```

2. **Generate TypeScript types:**

   ```bash
   cd frontend
   pnpm run generate:all
   ```

3. **Update frontend code** to use new types

4. **Run tests** to ensure compatibility

**Automatic Type Generation:**
Use the VS Code task "ReViewPoint: Generate API Types" or the frontend script that combines both steps.

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Port already in use" errors

**Symptoms:**

- Backend fails to start on port 8000
- Frontend fails to start on port 3000

**Solutions:**

```bash
# Find and kill processes using ports
# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# macOS/Linux
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Use different ports
# Backend: Edit backend/config/.env
REVIEWPOINT_PORT=8001

# Frontend: Edit frontend/package.json dev script
"dev": "vite --port 3001"
```

#### Issue: Database connection errors

**Symptoms:**

- "could not connect to server" errors
- Migration failures

**Solutions:**

```bash
# Reset PostgreSQL completely
pnpm run postgres:stop
docker system prune -f
pnpm run postgres:start

# Check PostgreSQL status
docker ps | grep postgres
docker logs reviewpoint-postgres

# Reset to SQLite for development
pnpm run db:sqlite
```

#### Issue: Module import errors

**Symptoms:**

- Python import errors
- TypeScript module not found errors

**Solutions:**

```bash
# Backend: Recreate Hatch environment
cd backend
hatch env remove default
hatch env create

# Frontend: Clean install
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Root: Clean install everything
pnpm run clean
pnpm install
```

#### Issue: Test failures

**Symptoms:**

- Random test failures
- Database-related test errors

**Solutions:**

```bash
# Backend: Use fast testing mode for development
cd backend
hatch run fast:test  # Uses SQLite, more reliable

# Clear test caches
rm -rf .pytest_cache __pycache__
rm -f test.db

# Run specific failing test
hatch run pytest tests/test_specific.py -v

# Frontend: Clear test caches
cd frontend
rm -rf node_modules/.cache
pnpm run test:clear-cache
```

### Environment Issues

#### Issue: Hatch/Python environment problems

**Symptoms:**

- "hatch: command not found"
- Python package installation errors

**Solutions:**

```bash
# Install/update Hatch
pip install --upgrade hatch

# Recreate environment completely
cd backend
hatch env remove default
hatch env create
hatch shell  # Enter environment

# Check Python version
python --version  # Should be 3.11+
```

#### Issue: Node.js/pnpm problems

**Symptoms:**

- "pnpm: command not found"
- Package installation failures

**Solutions:**

```bash
# Install pnpm globally
npm install -g pnpm

# Clear pnpm cache
pnpm store prune

# Use Node version manager (if available)
nvm use 18  # or latest LTS

# Alternative: Use npm instead of pnpm
npm install
npm run dev
```

### Performance Issues

#### Issue: Slow startup times

**Symptoms:**

- Long wait times for services to start
- Timeouts during development

**Solutions:**

```bash
# Use SQLite for faster development
pnpm run dev  # Instead of dev:postgres

# Optimize Docker resources (if using PostgreSQL)
# Edit docker-compose.yml to reduce resource usage

# Check system resources
# Windows: Task Manager → Performance
# macOS: Activity Monitor
# Linux: htop or top
```

#### Issue: Test suite runs slowly

**Solutions:**

```bash
# Use fast test mode for development
cd backend
hatch run fast:test  # SQLite-based, much faster

# Run only specific tests
hatch run pytest tests/test_auth.py

# Skip slow tests during development
hatch run pytest -m "not slow"

# Use parallel testing (if available)
hatch run pytest -n auto
```

## API and Integration

### How do I authenticate with the API?

**Basic Authentication Flow:**

```javascript
// 1. Login to get tokens
const response = await fetch("/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "your-username",
    password: "your-password",
  }),
});

const { access_token, refresh_token } = await response.json();

// 2. Use access token for API requests
const apiResponse = await fetch("/api/v1/users/me", {
  headers: {
    Authorization: `Bearer ${access_token}`,
    "Content-Type": "application/json",
  },
});

// 3. Refresh token when expired
const refreshResponse = await fetch("/api/v1/auth/refresh", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ refresh_token }),
});
```

### How do I upload files?

**File Upload Example:**

```javascript
const uploadFile = async (file, description) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("description", description);

  const response = await fetch("/api/v1/uploads/", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      // Don't set Content-Type for FormData
    },
    body: formData,
  });

  return await response.json();
};

// Usage
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
const result = await uploadFile(file, "My important document");
```

### What file types are supported?

**Supported File Types:**

- **Documents**: PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
- **Images**: JPEG, PNG, GIF, WebP
- **Text**: Plain text, CSV, JSON, XML
- **Archives**: ZIP, RAR

**File Limits:**

- Maximum file size: **10 MB per file**
- Total storage per user: **100 MB** (default)
- Concurrent uploads: **3 per user**

**Security Features:**

- File content validation against declared MIME type
- Malware scanning for all uploads
- Filename sanitization to prevent path traversal
- Virus scanning integration (ClamAV)

### How do I handle API errors?

**Error Handling Best Practices:**

```javascript
const apiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorData = await response.json();

      switch (response.status) {
        case 401:
          // Handle authentication errors
          redirectToLogin();
          break;
        case 403:
          // Handle permission errors
          showPermissionError();
          break;
        case 422:
          // Handle validation errors
          displayValidationErrors(errorData.detail);
          break;
        case 429:
          // Handle rate limiting
          const retryAfter = response.headers.get("Retry-After");
          showRateLimitError(retryAfter);
          break;
        default:
          // Handle other errors
          showGenericError(errorData.detail);
      }

      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
};
```

## Security and Best Practices

### How secure is ReViewPoint?

**Security Features:**

1. **Authentication & Authorization:**
   - JWT tokens with configurable expiration
   - Refresh token rotation
   - Role-based access control
   - Secure password hashing with bcrypt

2. **File Security:**
   - File type validation and content verification
   - Malware and virus scanning
   - Secure file storage with sanitized names
   - Size and quota limits

3. **API Security:**
   - Rate limiting on all endpoints
   - CORS protection
   - Input validation and sanitization
   - Comprehensive error handling without data leaks

4. **Infrastructure Security:**
   - Docker container isolation
   - Environment variable configuration
   - Database connection security
   - HTTPS-ready configuration

### What are the security best practices?

**For Development:**

1. **Environment Variables:**
   - Never commit secrets to version control
   - Use `.env` files for local development
   - Rotate JWT secrets regularly

2. **Database Security:**
   - Use strong database passwords
   - Enable database encryption in production
   - Regular backup and recovery testing

3. **API Security:**
   - Always validate input data
   - Use HTTPS in production
   - Implement proper rate limiting
   - Log security events

**For Production:**

1. **Infrastructure:**
   - Use HTTPS with valid certificates
   - Implement reverse proxy (nginx/Apache)
   - Set up monitoring and alerting
   - Regular security updates

2. **Configuration:**
   - Strong JWT secrets (256-bit minimum)
   - Appropriate token expiration times
   - Rate limiting tuned for your use case
   - File upload limits based on requirements

### How do I report security issues?

**Security Issue Reporting:**

1. **Do NOT** create public GitHub issues for security vulnerabilities
2. **Email** security issues to the maintainers privately
3. **Include** detailed reproduction steps
4. **Wait** for acknowledgment before public disclosure

**Security Response Process:**

- Issues acknowledged within 48 hours
- Fix timeline communicated within 1 week
- Security patches released as soon as possible
- Public disclosure coordinated with fix release

## Deployment and Production

### How do I deploy ReViewPoint?

**Production Deployment Options:**

1. **Docker Deployment (Recommended):**

   ```bash
   # Build production images
   docker build -t reviewpoint-backend ./backend
   docker build -t reviewpoint-frontend ./frontend

   # Deploy with docker-compose
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Traditional Server Deployment:**

   ```bash
   # Backend deployment
   cd backend
   hatch build
   pip install dist/*.whl

   # Frontend deployment
   cd frontend
   pnpm run build
   # Serve dist/ with nginx or similar
   ```

3. **Cloud Platform Deployment:**
   - Use provided deployment guides for AWS, Azure, GCP
   - Container registry integration
   - Environment-specific configurations

### What are the production requirements?

**Minimum Production Requirements:**

- **CPU**: 2 cores (4+ recommended)
- **RAM**: 4GB (8GB+ recommended)
- **Storage**: 50GB+ depending on file uploads
- **Database**: PostgreSQL 12+ (managed service recommended)
- **Reverse Proxy**: nginx, Apache, or cloud load balancer
- **SSL Certificate**: Let's Encrypt or commercial certificate

**Recommended Production Setup:**

- **Application**: Docker containers with orchestration
- **Database**: Managed PostgreSQL service
- **File Storage**: Object storage (S3, Azure Blob, GCS)
- **Monitoring**: Application and infrastructure monitoring
- **Backup**: Automated database and file backups
- **CDN**: For static assets and file downloads

### How do I monitor ReViewPoint in production?

**Monitoring Setup:**

1. **Application Monitoring:**
   - Health check endpoints at `/health`
   - Application metrics and logging
   - Error tracking and alerting
   - Performance monitoring

2. **Infrastructure Monitoring:**
   - Server resource usage
   - Database performance
   - Network and storage metrics
   - Container health and resources

3. **Security Monitoring:**
   - Failed authentication attempts
   - Rate limiting triggers
   - Unusual file upload patterns
   - Security scan results

**Sample Monitoring Configuration:**

```yaml
# docker-compose.monitoring.yml
version: "3.8"
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## Contributing and Development

### How can I contribute to ReViewPoint?

**Ways to Contribute:**

1. **Code Contributions:**
   - Bug fixes and feature additions
   - Test coverage improvements
   - Documentation enhancements
   - Performance optimizations

2. **Documentation:**
   - API documentation improvements
   - Tutorial and guide creation
   - Example applications
   - Translation efforts

3. **Testing:**
   - Bug reports with reproduction steps
   - Testing on different platforms
   - Security issue identification
   - Performance testing

**Contribution Process:**

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Make** changes with comprehensive tests
4. **Ensure** all tests pass: `pnpm run test:all`
5. **Create** pull request with detailed description

### What's the development roadmap?

**Current Focus Areas:**

1. **Core Stability:**
   - Comprehensive test coverage (target: 95%+)
   - Performance optimization
   - Security enhancements
   - Documentation completion

2. **Feature Enhancements:**
   - Advanced file management features
   - Real-time collaboration tools
   - Enhanced API capabilities
   - Mobile-responsive improvements

3. **Developer Experience:**
   - Improved development tools
   - Better error messages
   - Enhanced debugging capabilities
   - Streamlined deployment process

**Upcoming Features:**

- File sharing and collaboration
- Advanced search capabilities
- API versioning and backwards compatibility
- Enhanced admin dashboard
- Mobile app support

### How do I set up a development environment?

**Complete Development Setup:**

```bash
# 1. Clone and install dependencies
git clone <repository-url>
cd ReViewPoint
pnpm install

# 2. Set up backend environment
cd backend
hatch env create
hatch shell

# 3. Set up database (choose one)
# Option A: SQLite (simple)
echo "REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db" > config/.env

# Option B: PostgreSQL (production-like)
cd ..
pnpm run postgres:start

# 4. Run migrations
hatch run alembic upgrade head

# 5. Start development servers
cd ..
pnpm run dev  # Starts both backend and frontend
```

**VS Code Setup:**

1. Install recommended extensions when prompted
2. Use integrated terminal and tasks
3. Set up debugging configurations
4. Use built-in testing integration

---

**Still have questions?** Check the [comprehensive documentation](../developer-overview.md) or [API reference](./api-reference.md) for detailed technical information.
