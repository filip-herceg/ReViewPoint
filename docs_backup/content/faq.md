# Frequently Asked Questions

> **Comprehensive FAQ covering setup, development, troubleshooting, and common issues in ReViewPoint development.**

---

## Getting Started

### How do I set up the project from scratch?

Follow the [Setup Guide](setup.md) for complete step-by-step instructions. The setup process uses Hatch for Python environment management and PNPM for frontend dependencies.

### What are the system requirements?

- **Python**: 3.11.9 (system installation recommended)
- **Node.js**: 18+ with PNPM package manager
- **Hatch**: For Python environment management
- **Docker**: Optional, for PostgreSQL and containerized modules
- **Git**: For version control

### Which database should I use for development?

- **SQLite**: Recommended for quick development and testing (zero setup)
- **PostgreSQL**: Recommended for production-like development (requires Docker)

Use the provided VS Code tasks to easily switch between database configurations.

---

## Development Workflow

### How do I run the development servers?

```bash
# Start both backend and frontend with SQLite
pnpm run dev

# Start with PostgreSQL (auto-setup)
pnpm run dev:postgres

# Start individual services
pnpm run backend:dev    # Backend only
pnpm run frontend:dev   # Frontend only
```

### How do I run tests?

```bash
# All backend tests
cd backend && hatch run pytest

# Fast backend tests only
cd backend && python run-fast-tests.py

# Frontend tests
cd frontend && pnpm test

# End-to-end tests
cd frontend && pnpm run test:e2e

# All tests across the project
pnpm run test:all
```

### How do I check code quality?

```bash
# Backend linting and formatting
cd backend
hatch run ruff check .
hatch run ruff format .

# Frontend linting and formatting
cd frontend
pnpm run lint
pnpm run format

# Type checking
cd frontend && pnpm run type-check
```

---

## Database & Environment

### How do I switch between SQLite and PostgreSQL?

Use the provided VS Code tasks or manual commands:

```bash
# Switch to SQLite (simpler)
pnpm run db:sqlite

# Switch to PostgreSQL (production-like)
pnpm run db:postgres
```

### How do I reset the database?

```bash
# Reset PostgreSQL completely
pnpm run postgres:reset

# For SQLite, simply delete the database file
rm backend/reviewpoint_dev.db
```

### How do I run database migrations?

```bash
cd backend
hatch run alembic upgrade head        # Apply all pending migrations
hatch run alembic revision --autogenerate -m "description"  # Create new migration
hatch run alembic downgrade -1        # Rollback one migration
```

---

## Troubleshooting

### Common Setup Issues

**Q: "Module not found" errors when running Python code**
A: Ensure you're in the Hatch environment:
```bash
cd backend
hatch shell
```

**Q: PNPM commands not working**
A: Install PNPM globally:
```bash
npm install -g pnpm
```

**Q: Docker PostgreSQL won't start**
A: Check if Docker is running and ports are available:
```bash
docker ps
pnpm run postgres:check
```

### Development Issues

**Q: Tests are failing unexpectedly**
A: Try these steps:
1. Ensure you're in the correct environment (`hatch shell` for backend)
2. Check for database connection issues
3. Run fast tests only: `python run-fast-tests.py`
4. Clear test databases and caches

**Q: Frontend build errors**
A: Common solutions:
```bash
# Clear node modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Clear Vite cache
pnpm run dev --force

# Check TypeScript issues
pnpm run type-check
```

**Q: API types are out of sync**
A: Regenerate API types:
```bash
cd frontend
pnpm run generate:types
```

### Performance Issues

**Q: Tests are running slowly**
A: Use the fast test runner which excludes slow integration tests:
```bash
cd backend
python run-fast-tests.py
```

**Q: Development server is slow**
A: Check these potential issues:
- Large number of files being watched
- Insufficient system resources
- Database connection pooling settings

---

## API & Integration

### How do I access the API documentation?

Start the backend server and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### How do I test API endpoints manually?

Use the interactive Swagger UI at `/docs` or tools like:
- **curl**: Command-line HTTP client
- **HTTPie**: User-friendly HTTP client
- **Postman**: GUI API testing tool
- **VS Code REST Client**: Extension for API testing

### How do I add authentication to API requests?

Include the JWT token in the Authorization header:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/v1/users/me
```

---

## Deployment & Production

### How do I build for production?

```bash
# Build frontend
cd frontend
pnpm run build

# Backend is deployed directly (no build step required)
# Ensure environment variables are properly configured
```

### How do I configure environment variables?

Copy the example environment files and customize:
```bash
cp backend/config/.env.example backend/config/.env
# Edit backend/config/.env with your settings
```

### What environment variables are required?

Key variables:
- `REVIEWPOINT_DB_URL`: Database connection string
- `REVIEWPOINT_JWT_SECRET`: JWT signing secret
- `REVIEWPOINT_ENVIRONMENT`: dev/test/prod
- `REVIEWPOINT_DEBUG`: Enable debug mode

---

## Contributing

### How do I contribute to the documentation?

1. Edit Markdown files in `docs/content/`
2. Follow the [Contributing to Docs](contributing-docs.md) guidelines
3. Test locally with `pnpm run docs:dev`
4. Submit a pull request

### How do I report bugs or request features?

Use the GitHub issue templates:
- **Bug Report**: Include reproduction steps and environment details
- **Feature Request**: Provide clear description and use cases
- **Documentation**: For documentation improvements

### What coding standards should I follow?

See [Developer Guidelines](dev-guidelines.md) for:
- Code formatting (Ruff for Python, Biome for TypeScript)
- Naming conventions
- Testing requirements
- Git commit message format

---

## Getting Help

### Where can I find more detailed documentation?

- [System Architecture](architecture.md) - Complete system overview
- [Developer Guidelines](dev-guidelines.md) - Coding standards and practices
- [Test Instructions](test-instructions.md) - Comprehensive testing guide
- [Backend Source Guide](backend-source-guide.md) - Backend codebase overview

### How do I get help with specific issues?

1. Check this FAQ first
2. Search existing GitHub issues
3. Review the relevant documentation section
4. Create a new GitHub issue with detailed information
5. Reach out to the development team

---

_This FAQ is continuously updated. Contribute additional questions and answers to help the development community!_
