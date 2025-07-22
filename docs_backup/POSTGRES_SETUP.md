# PostgreSQL Development Setup

This document explains how to set up and use PostgreSQL for development with ReViewPoint.

## Quick Start

### Option 1: Automatic PostgreSQL Setup (Recommended)

```bash
# Start development with PostgreSQL (auto-setup)
pnpm dev:postgres
# or
pnpm dev:pg
```

This command will:

1. ✅ Check if Docker is running
2. ✅ Start PostgreSQL container automatically
3. ✅ Wait for the database to be healthy
4. ✅ Update environment configuration
5. ✅ Run database migrations
6. ✅ Start backend and frontend servers

### Option 2: Manual PostgreSQL Setup

```bash
# Start PostgreSQL container manually
pnpm postgres:start

# Start development servers
pnpm dev
```

### Option 3: Regular SQLite Development

```bash
# Use SQLite (default, no containers needed)
pnpm dev

# Or explicitly switch back to SQLite
pnpm db:sqlite
pnpm dev
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `pnpm dev:postgres` | Start development with PostgreSQL (auto-setup) |
| `pnpm dev:pg` | Alias for `dev:postgres` |
| `pnpm postgres:start` | Start PostgreSQL container only |
| `pnpm postgres:stop` | Stop PostgreSQL container |
| `pnpm db:sqlite` | Switch configuration back to SQLite |
| `pnpm dev` | Start development (current database config) |

## Prerequisites

- **Docker Desktop**: Must be installed and running
- **Node.js & pnpm**: For running the scripts
- **Python environment**: For running migrations

## What Happens During Auto-Setup

1. **Docker Check**: Verifies Docker is running
2. **Container Management**:
   - Checks if `reviewpoint_postgres` container exists
   - Starts container if not running
   - Waits for health check to pass
3. **Environment Update**:
   - Updates `backend/.env` to use PostgreSQL URL
   - Sets: `REVIEWPOINT_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint`
4. **Database Setup**:
   - Runs Alembic migrations: `alembic upgrade head`
   - Creates tables and applies schema
5. **Server Startup**:
   - Starts backend server on port 8000
   - Starts frontend server on port 5173

## Database Configuration

### PostgreSQL (Container)

```env
REVIEWPOINT_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint
```

### SQLite (File-based)

```env
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db
```

## Manual Docker Commands

If you prefer using Docker directly:

```bash
# Start PostgreSQL container
docker compose -f backend/deployment/docker-compose.yml up -d postgres

# Check container status
docker ps | grep reviewpoint_postgres

# Check container health
docker inspect reviewpoint_postgres --format="{{.State.Health.Status}}"

# Stop container
docker compose -f backend/deployment/docker-compose.yml down

# View logs
docker logs reviewpoint_postgres
```

## Manual Migration Commands

If you need to run migrations manually:

```bash
cd backend

# Run pending migrations
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "description"

# Rollback last migration
python -m alembic downgrade -1
```

## Troubleshooting

### Docker Not Running

```
[ERROR] Docker is not running. Please start Docker Desktop.
```

**Solution**: Start Docker Desktop and wait for it to be ready.

### Port 5432 Already in Use

```
Error: bind: address already in use
```

**Solution**: Stop other PostgreSQL instances or change the port in `docker-compose.yml`.

### Migration Fails

```
[ERROR] Migration failed (exit code: 1)
```

**Solutions**:

1. Check database connection
2. Verify migrations are not conflicting
3. Check if database schema is corrupted

### Container Won't Start

```
[ERROR] Container failed to start
```

**Solutions**:

1. Check Docker Desktop is running
2. Verify no port conflicts
3. Try: `docker system prune` to clean up
4. Check Docker logs: `docker logs reviewpoint_postgres`

### Switch Back to SQLite

If PostgreSQL setup fails or you want to go back to SQLite:

```bash
pnpm db:sqlite
pnpm dev
```

## Container Configuration

The PostgreSQL container (`backend/deployment/docker-compose.yml`) uses:

- **Image**: `postgres:17-alpine`
- **Port**: `5432:5432`
- **Database**: `reviewpoint`
- **User**: `postgres`
- **Password**: `postgres`
- **Health Check**: `pg_isready` every 10 seconds

## Development Workflow

### Typical Day with PostgreSQL

1. **Start Development**:

   ```bash
   pnpm dev:postgres
   ```

2. **Make Database Changes**:
   - Modify models in `backend/src/models/`
   - Generate migration: `cd backend && python -m alembic revision --autogenerate -m "add new field"`
   - Restart development server (migrations auto-apply)

3. **End Development**:
   - Press `Ctrl+C` to stop servers
   - Container keeps running (persistent data)

### Database Reset

To completely reset the database:

```bash
# Stop and remove container with data
docker compose -f backend/deployment/docker-compose.yml down -v

# Start fresh
pnpm dev:postgres
```

## Performance Notes

- **Cold Start**: ~10-15 seconds for container + migration
- **Warm Start**: ~2-3 seconds if container already running
- **SQLite Alternative**: ~1 second startup (no container needed)

## VS Code Integration

The project includes VS Code tasks for manual control:

- `ReViewPoint: Start PostgreSQL (Docker)`
- `ReViewPoint: Stop PostgreSQL (Docker)`
- `ReViewPoint: Switch to PostgreSQL`
- `ReViewPoint: Switch to SQLite`

Access via: `Ctrl+Shift+P` → `Tasks: Run Task`
