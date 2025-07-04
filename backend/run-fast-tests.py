#!/usr/bin/env python3
"""
Clean fast test runner that uses environment variables instead of file swapping.

This runner sets up the fast test environment (SQLite in-memory) and runs ALL tests,
including those marked as slow. The focus is on providing a complete test suite
with faster setup, not necessarily faster individual tests.

Use --fast-only flag to skip slow tests and run only the fast subset.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run fast tests using unified conftest with environment variables."""
    backend_dir = Path(__file__).parent
    
    # Check if --fast-only flag is present
    args = sys.argv[1:]
    use_fast_only = "--fast-only" in args
    if use_fast_only:
        args.remove("--fast-only")  # Remove our custom flag
    
    # Set up environment for fast tests
    env = os.environ.copy()
    
    # Get log level from environment variable, default to INFO
    test_log_level = env.get("REVIEWPOINT_TEST_LOG_LEVEL", "INFO")
    
    # Set fast test environment variables
    env.update({
        "FAST_TESTS": "1",
        "REVIEWPOINT_ENVIRONMENT": "test",
        "REVIEWPOINT_LOG_LEVEL": "DEBUG",
        "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
        "REVIEWPOINT_JWT_SECRET_KEY": "fasttestsecret123",
        "REVIEWPOINT_JWT_SECRET": "fasttestsecret123",
        "REVIEWPOINT_API_KEY_ENABLED": "false",
        "REVIEWPOINT_AUTH_ENABLED": "true",
        "REVIEWPOINT_API_KEY": "testkey",
        "PYTHONPATH": str(backend_dir / "src"),
    })
    
    # Run pytest with fast configuration
    cmd = [
        sys.executable, "-m", "pytest",
        "--tb=short",
        "--disable-warnings",
        "-p", "no:cacheprovider",
        f"--log-cli-level={test_log_level}",
    ]
    
    # Add --fast flag only if --fast-only was specified
    if use_fast_only:
        cmd.append("--fast")
        
    cmd.extend(args)  # Add remaining arguments
    
    if not args:
        cmd.append("tests/")
    
    test_type = "fast-only tests" if use_fast_only else "all tests (fast mode)"
    print(f"Running {test_type}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=backend_dir, env=env)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
