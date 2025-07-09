# Base image for building dependencies
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

# Install system dependencies and upgrade all packages to latest security patches
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Install pip and upgrade setuptools for security
RUN pip install --no-cache-dir --upgrade setuptools>=78.1.1 pip

# Copy dependency files
COPY pyproject.toml ./

# Create a simple README.md and modify pyproject.toml if needed
RUN echo "Contents of current directory:" && ls -la && \
    echo "# Backend Project" > README.md && \
    echo "This is a placeholder README file for Docker build." >> README.md && \
    echo "Created README.md successfully" && \
    cat README.md && \
    echo "Checking pyproject.toml:" && \
    if grep -q "readme =" pyproject.toml; then \
    echo "Removing readme reference from pyproject.toml"; \
    sed -i '/readme =/d' pyproject.toml; \
    fi && \
    if grep -q "dynamic =" pyproject.toml; then \
    echo "Ensuring proper version handling in pyproject.toml"; \
    sed -i '/dynamic =/d' pyproject.toml; \
    echo "Adding static version to pyproject.toml"; \
    sed -i '/name = "backend"/a version = "0.1.0"' pyproject.toml; \
    echo "Removing any tool.hatch.version section if it exists"; \
    sed -i '/\[tool\.hatch\.version\]/,+1d' pyproject.toml; \
    fi

# Use pip directly for installation
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir .

FROM python:3.11-slim-bullseye AS runtime

WORKDIR /app

# Install runtime dependencies, upgrade all packages to latest security patches, and upgrade setuptools for security
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade setuptools>=78.1.1 pip && \
    pip install --no-cache-dir --upgrade setuptools>=78.1.1 pip

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code and configuration files from build context to /app
COPY . /app/

# Debug: List app directory contents
RUN echo "App directory contents:" && ls -la /app/ && \
    if [ -d "/app/src" ]; then echo "Source directory found"; else echo "Source directory missing!"; fi && \
    if [ -f "/app/alembic.ini" ]; then echo "Alembic config found"; else echo "Alembic config missing!"; fi

# Make entrypoint script executable if it exists
RUN if [ -f "/app/docker-entrypoint.sh" ]; then \
    chmod +x /app/docker-entrypoint.sh && \
    echo "Entrypoint script made executable"; \
    else \
    echo "WARNING: Entrypoint script not found, creating a fallback"; \
    echo '#!/bin/bash' > /app/docker-entrypoint.sh && \
    echo 'set -e' >> /app/docker-entrypoint.sh && \
    echo '' >> /app/docker-entrypoint.sh && \
    echo '# Wait for database if configured' >> /app/docker-entrypoint.sh && \
    echo 'if [ -n "$REVIEWPOINT_DB_URL" ]; then' >> /app/docker-entrypoint.sh && \
    echo '    echo "Waiting for database to be ready..."' >> /app/docker-entrypoint.sh && \
    echo '    until pg_isready -h $(echo $REVIEWPOINT_DB_URL | sed "s/.*@\([^:]*\):.*/\1/") -p $(echo $REVIEWPOINT_DB_URL | sed "s/.*:\([0-9]*\)\/.*/\1/") -U postgres; do' >> /app/docker-entrypoint.sh && \
    echo '        echo "Database is unavailable - sleeping"' >> /app/docker-entrypoint.sh && \
    echo '        sleep 2' >> /app/docker-entrypoint.sh && \
    echo '    done' >> /app/docker-entrypoint.sh && \
    echo '    echo "Database is ready!"' >> /app/docker-entrypoint.sh && \
    echo 'fi' >> /app/docker-entrypoint.sh && \
    echo '' >> /app/docker-entrypoint.sh && \
    echo '# Run database migrations if alembic.ini exists' >> /app/docker-entrypoint.sh && \
    echo 'if [ -f alembic.ini ]; then' >> /app/docker-entrypoint.sh && \
    echo '    echo "Running database migrations..."' >> /app/docker-entrypoint.sh && \
    echo '    alembic upgrade head' >> /app/docker-entrypoint.sh && \
    echo 'fi' >> /app/docker-entrypoint.sh && \
    echo '' >> /app/docker-entrypoint.sh && \
    echo '# Execute the main command' >> /app/docker-entrypoint.sh && \
    echo 'exec "$@"' >> /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh && \
    echo "Created fallback entrypoint script"; \
    fi

# Make scripts in scripts directory executable
RUN if [ -d "/app/scripts" ]; then \
    find /app/scripts -type f -name "*.sh" -exec chmod +x {} \; || \
    echo "No .sh files found in scripts directory"; \
    else \
    echo "Scripts directory not found"; \
    mkdir -p /app/scripts; \
    fi

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set Python path and environment
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
