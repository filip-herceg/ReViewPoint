# Docker Configuration Guide

This directory contains Docker configurations for the ReViewPoint backend application.

## File Organization

| File                   | Purpose                                           | Security       | Use Case                   |
|------------------------|---------------------------------------------------|----------------|----------------------------|
| `dockerfile.prod`      | Production image with distroless runtime          | ★★★★★ (Best)   | Production deployment      |
| `dockerfile.dev`       | Development image with hot-reloading              | ★★★☆☆          | Local development          |
| `dockerfile.shell`     | Production image with shell access                | ★★★★☆          | Debugging in production    |
| `db-migrate.sh`        | Database migration script for distroless setup    | N/A            | Database migrations        |
| `entrypoint.sh`        | Docker entrypoint for shell-based images          | N/A            | Container initialization   |
| `docker-compose.prod.yml` | Production deployment with migrations          | ★★★★★          | Production orchestration   |

## Deployment Options

### 1. Production (Most Secure)

```bash
# Using docker directly
docker build -t reviewpoint-backend -f deployment/docker/dockerfile.prod .
docker run -p 8000:8000 -e REVIEWPOINT_DB_URL=... reviewpoint-backend

# Using docker-compose
cd deployment/docker
docker-compose -f docker-compose.prod.yml up
```

### 2. Development

```bash
# From project root
cd deployment
docker-compose up
```

### 3. Production with Shell Access

```bash
docker build -t reviewpoint-backend -f deployment/docker/dockerfile.shell .
docker run -p 8000:8000 -e REVIEWPOINT_DB_URL=... reviewpoint-backend
```

## Security Comparison

| Image                   | Vulnerabilities | Shell Access | Migration Support |
|-------------------------|----------------|--------------|-------------------|
| `dockerfile.prod`       | 0 HIGH         | ❌ No        | External          |
| `dockerfile.dev`        | 1 HIGH         | ✅ Yes       | Built-in          |
| `dockerfile.shell`      | 1 HIGH         | ✅ Yes       | Built-in          |

## CI/CD Integration

The GitHub workflows in `.github/workflows/security-scan.yaml` have been updated to work with the new file naming convention:

1. It will first try to use `dockerfile.prod` (most secure)
2. If not found, it will fall back to `dockerfile.dev`
3. It will use `entrypoint.sh` instead of the old `docker-entrypoint.sh`
4. It handles both distroless and shell-based images appropriately
