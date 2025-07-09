# Secure Docker Configuration

This directory contains an improved Docker configuration that significantly reduces security vulnerabilities.

## Security Improvements

### Before (python:3.11-slim-bullseye)

- **4 HIGH vulnerabilities** in the Docker image
- Older Python version with known security issues
- Less secure base image

### After (Distroless Runtime)

- **0 HIGH vulnerabilities** in runtime image (using distroless)
- **1 HIGH vulnerability** in builder stage only (python:3.13-slim-bookworm)
- Upgraded to Python 3.13 for latest security patches
- Using Google's distroless image for minimal attack surface

## Files Overview

- `dockerfile.prod` - Production Docker image with distroless runtime (most secure)
- `dockerfile.dev` - Development Docker image with shell access
- `dockerfile.shell` - Alternative production image with shell access
- `db-migrate.sh` - Database migration script for distroless setup
- `entrypoint.sh` - Traditional entrypoint script (used by dockerfile.shell)
- `docker-compose.prod.yml` - Production docker-compose with init container for migrations
- `README.md` - This file

## Usage Options

### Option 1: Distroless Runtime (Recommended for Production)

This is the most secure option using the current `dockerfile.prod`:

```bash
# Build the image
docker build -t reviewpoint-backend -f deployment/docker/dockerfile.prod .

# Run with separate migration
docker run --rm -e REVIEWPOINT_DB_URL=... reviewpoint-backend:builder ./deployment/docker/db-migrate.sh
docker run -p 8000:8000 -e REVIEWPOINT_DB_URL=... reviewpoint-backend
```

Or use the docker-compose example:

```bash
cd deployment/docker
docker-compose -f docker-compose.prod.yml up
```

### Option 2: Development Image

For development with hot-reloading and shell access:

```bash
cd deployment
docker-compose up
```

### Option 3: Shell-based Production (If you need shell access)

If you need shell access for debugging or more complex startup scripts, use `dockerfile.shell`:

```bash
docker build -t reviewpoint-backend -f deployment/docker/dockerfile.shell .
```

This will give you:

- **1 HIGH vulnerability** in runtime (vs 0 with distroless)
- Full shell access
- Built-in migration capabilities

## Trade-offs

### Distroless Advantages

- ✅ Zero vulnerabilities in runtime image
- ✅ Minimal attack surface
- ✅ Smaller image size
- ✅ No shell access for attackers

### Distroless Disadvantages

- ❌ No shell access for debugging
- ❌ Cannot run startup scripts
- ❌ Requires external migration handling
- ❌ Limited debugging capabilities

## Migration Strategy

For production environments, we recommend:

1. **Use the distroless runtime** for the main application
2. **Run migrations as init containers** or separate jobs
3. **Use the builder stage** for any shell-based operations
4. **Consider using Kubernetes init containers** for complex setups

## Environment Variables

The application expects these environment variables:

- `REVIEWPOINT_DB_URL` - Database connection string
- `PYTHONPATH` - Set to `/app` (handled automatically)
- `PATH` - Includes virtual environment (handled automatically)

## Security Best Practices Implemented

1. **Non-root user** - Application runs as `nonroot` user
2. **Minimal base image** - Distroless contains only essential files
3. **Latest Python version** - Using Python 3.13 with latest security patches
4. **Clean build process** - Removing temporary files and caches
5. **Explicit dependency management** - Using virtual environments
6. **Certificate management** - Including ca-certificates for SSL
7. **Multi-stage builds** - Separating build and runtime environments
