# Shared fixtures and helpers for users/ tests
from pathlib import Path

# Use the same file-based SQLite DB as in original test_users.py
TEST_DB_PATH = Path(__file__).parent / "../test.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH.resolve()}"
