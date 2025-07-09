# Base image for building dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Hatch and upgrade setuptools for security
RUN pip install --upgrade setuptools>=78.1.1 pip \
    && pip install hatch

# Copy dependency files
COPY pyproject.toml ./

# Use Hatch to install dependencies
RUN hatch env create && \
    cp -r $(hatch env find) ./.venv

# Runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and upgrade setuptools for security
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade setuptools>=78.1.1 pip

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Debug: List root directory contents
RUN echo "Root directory contents:" && ls -la /

# Copy all files from build context to /app
COPY . /app/

# Debug: List app directory contents
RUN echo "App directory contents:" && ls -la /app/

# Make entrypoint script executable if it exists
RUN if [ -f "/app/docker-entrypoint.sh" ]; then \
    chmod +x /app/docker-entrypoint.sh && \
    echo "Entrypoint script made executable"; \
    else \
    echo "WARNING: Entrypoint script not found"; \
    find /app -type f -name "*.sh" | sort; \
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

# Set the entrypoint script with fallback
CMD ["/bin/bash", "-c", "if [ -f /app/docker-entrypoint.sh ]; then /app/docker-entrypoint.sh python -m uvicorn src.main:app --host 0.0.0.0 --port 8000; else echo 'Entrypoint not found, running default command'; exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8000; fi"]

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set Python path and environment
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
