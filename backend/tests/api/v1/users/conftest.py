# Shared fixtures and helpers for users/ tests
from pathlib import Path

# Use the same PostgreSQL test DB as the rest of the suite
TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint_test"
