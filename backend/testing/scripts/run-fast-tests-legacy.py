
import os
import sys
import shutil
import subprocess
from pathlib import Path

def main() -> int:
    """Run fast tests with proper conftest switching."""
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests"
    fast_conftest = backend_dir / "testing" / "fast" / "conftest.py"

    # Check if --fast-only flag is present
    args = sys.argv[1:]
    use_fast_only = "--fast-only" in args
    if use_fast_only:
        args.remove("--fast-only")  # Remove our custom flag

    # Paths for conftest files
    original_conftest = tests_dir / "conftest.py"
    backup_conftest = tests_dir / "conftest_full.py"
    fast_conftest_target = tests_dir / "conftest.py"

    # Set up environment for fast tests
    env = os.environ.copy()

    # Get log level from environment variable, default to INFO
    test_log_level = env.get("REVIEWPOINT_TEST_LOG_LEVEL", "INFO")

    env.update(
        {
            "FAST_TESTS": "1",
            "REVIEWPOINT_ENVIRONMENT": "test",
            "REVIEWPOINT_LOG_LEVEL": "WARNING",
            "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
            "PYTHONPATH": str(backend_dir / "src"),
        }
    )

    try:
        # Backup original conftest if it exists
        if original_conftest.exists():
            shutil.move(str(original_conftest), str(backup_conftest))

        # Copy fast conftest to tests directory
        shutil.copy2(str(fast_conftest), str(fast_conftest_target))

        # Run pytest with fast configuration
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--tb=short",
            "--disable-warnings",
            "-p",
            "no:cacheprovider",
            f"--log-cli-level={test_log_level}",
        ]

        # Add --fast flag only if --fast-only was specified
        if use_fast_only:
            cmd.append("--fast")

        cmd.extend(args)  # Add remaining arguments

        if not args:
            cmd.append("tests/")

        test_type = "fast-only tests" if use_fast_only else "all tests"
        print(f"Running {test_type}: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=backend_dir, env=env)
        return result.returncode

    finally:
        # Restore original conftest
        if fast_conftest_target.exists():
            fast_conftest_target.unlink()

        if backup_conftest.exists():
            shutil.move(str(backup_conftest), str(original_conftest))

    # All code paths above return an int
