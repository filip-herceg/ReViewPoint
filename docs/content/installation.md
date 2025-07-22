# Installation Guide

This guide will help you get ReViewPoint running on your local development environment.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or later) - [Download here](https://nodejs.org/)
- **pnpm** (v8 or later) - Install with `npm install -g pnpm`
- **Python** (3.11 or later) - [Download here](https://python.org/)
- **Hatch** (Python project manager) - Install with `pipx install hatch`
- **Docker** (optional, for PostgreSQL) - [Download here](https://docker.com/)

## Quick Start (SQLite)

The fastest way to get started is using SQLite for the database:

```bash
# Clone the repository
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint

# Install dependencies
pnpm run install

# Start both backend and frontend (SQLite mode)
pnpm run dev
```

This will:

- Install all dependencies for both backend and frontend
- Start the FastAPI backend on `http://localhost:8000`
- Start the Vite frontend on `http://localhost:3000`
- Use SQLite database (no Docker required)

## PostgreSQL Setup (Recommended)

For a production-like environment, use PostgreSQL:

```bash
# Clone the repository
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint

# Install dependencies
pnpm run install

# Start with PostgreSQL (auto-setup)
pnpm run dev:postgres
```

This will:

- Check for Docker availability
- Start PostgreSQL container automatically
- Run database migrations
- Start both backend and frontend services

## Manual Setup

If you prefer manual control over each step:

### 1. Install Dependencies

```bash
# Root dependencies
pnpm install

# Backend dependencies (Python)
cd backend
hatch env create
cd ..

# Frontend dependencies (Node.js)
cd frontend
pnpm install
cd ..
```

### 2. Database Setup

#### Option A: SQLite (Simple)

```bash
# Switch to SQLite mode
pnpm run db:sqlite

# Run migrations
cd backend
hatch run alembic upgrade head
cd ..
```

#### Option B: PostgreSQL (Recommended)

```bash
# Start PostgreSQL container
pnpm run postgres:start

# Run migrations
cd backend
hatch run alembic upgrade head
cd ..
```

### 3. Start Services

```bash
# Terminal 1: Start backend
cd backend
hatch run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
pnpm run dev
```

## Environment Configuration

### Backend Configuration

The backend uses environment variables from `backend/config/.env`:

```env
# Database URL (automatically set by scripts)
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db

# OR for PostgreSQL:
# REVIEWPOINT_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint

# Other settings
SECRET_KEY=your-secret-key
DEBUG=true
```

### Frontend Configuration

The frontend automatically connects to the backend API. No configuration needed for development.

## Verification

Once everything is running, verify the installation:

1. **Backend API**: Visit `http://localhost:8000/docs` for the FastAPI Swagger UI
2. **Frontend App**: Visit `http://localhost:3000` for the React application
3. **Health Check**: The frontend should successfully connect to the backend

## Common Issues

### Docker Not Found

If you see "Docker not found" but want to use PostgreSQL:

1. Install Docker Desktop
2. Ensure Docker is running
3. Run `pnpm run postgres:check` to verify

### Port Conflicts

Default ports:

- Backend: `8000`
- Frontend: `3000`
- PostgreSQL: `5432`

If these ports are busy, modify the configuration or stop conflicting services.

### Permission Issues

On Linux/macOS, you might need to run Docker commands with `sudo` or add your user to the Docker group.

## Development Workflow

### Running Tests

```bash
# Backend tests
pnpm run test:backend

# Frontend tests
pnpm run test:frontend

# All tests
pnpm run test
```

### Code Quality

```bash
# Lint and format backend
pnpm run lint:backend
pnpm run format:backend

# Lint and format frontend
pnpm run lint:frontend
pnpm run format:frontend
```

### Database Migrations

```bash
# Create new migration
cd backend
hatch run alembic revision --autogenerate -m "Description"

# Apply migrations
hatch run alembic upgrade head
```

## Next Steps

- Read the [Developer Overview](developer-overview.md) for architecture details
- Explore the [Backend Documentation](backend/index.md) for API details
- Check out the [Frontend Documentation](frontend/index.md) for UI components
- Review [Contributing Guidelines](resources/contributing.md) to start contributing

## Getting Help

- **Documentation**: Browse this documentation for detailed guides
- **Issues**: Report problems on GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
