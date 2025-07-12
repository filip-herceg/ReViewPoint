### RENAMED: See run-fast-tests-legacy.py for the previous implementation.
"""Clean fast test runner that uses environment variables instead of file swapping.

This runner sets up the fast test environment (SQLite in-memory) and runs ALL tests,
including those marked as slow. The focus is on providing a complete test suite
with faster setup, not necessarily faster individual tests.

Use --fast-only flag to skip slow tests and run only the fast subset.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import MutableMapping
from pathlib import Path
from typing import (
    Final,
    Literal,
)

# --- Constants ---
BACKEND_DIR: Final[Path] = Path(__file__).parent.parent.parent
FAST_TESTS_ENV: Final[dict[str, str]] = {
    "FAST_TESTS": "1",
    "REVIEWPOINT_ENVIRONMENT": "test",
    "REVIEWPOINT_LOG_LEVEL": "DEBUG",
    "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
    "REVIEWPOINT_JWT_SECRET_KEY": "fasttestsecret123",
    "REVIEWPOINT_JWT_SECRET": "fasttestsecret123",
    "REVIEWPOINT_API_KEY_ENABLED": "false",
    "REVIEWPOINT_AUTH_ENABLED": "true",
    "REVIEWPOINT_API_KEY": "testkey",
    "PYTHONPATH": str(BACKEND_DIR / "src"),
}


def main() -> int:
    """Run fast tests using unified conftest with environment variables.

    Returns:
        int: The exit code from the pytest process.

    Raises:
        subprocess.SubprocessError: If the subprocess fails to start.

    """
    args: list[str] = sys.argv[1:]
    use_fast_only: bool = "--fast-only" in args
    if use_fast_only:
        args.remove("--fast-only")  # Remove our custom flag

    env: MutableMapping[str, str] = os.environ.copy()

    test_log_level: str = env.get("REVIEWPOINT_TEST_LOG_LEVEL", "INFO")

    env.update(FAST_TESTS_ENV)

    cmd: list[str] = [
        sys.executable,
        "-m",
        "pytest",
        "--tb=short",
        "--disable-warnings",
        "-p",
        "no:cacheprovider",
        f"--log-cli-level={test_log_level}",
    ]

    if use_fast_only:
        cmd.extend(["-m", "fast"])

    cmd.extend(args)

    if not args:
        cmd.append("tests/")

    test_type: Literal["fast-only tests", "all tests (fast mode)"] = (
        "fast-only tests" if use_fast_only else "all tests (fast mode)"
    )
    print(f"Running {test_type}: {' '.join(cmd)}")
    result: subprocess.CompletedProcess[bytes] = subprocess.run(
        cmd,
        check=False,
        cwd=BACKEND_DIR,
        env=env,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
