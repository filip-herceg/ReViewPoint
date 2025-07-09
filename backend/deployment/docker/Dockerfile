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

FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and upgrade setuptools for security
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade setuptools>=78.1.1 pip

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY docker-entrypoint.sh ./

# Make scripts executable
RUN chmod +x docker-entrypoint.sh || true
RUN if [ -d "scripts" ] && [ -n "$(find scripts -name '*.sh' 2>/dev/null)" ]; then chmod +x scripts/*.sh; fi

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
