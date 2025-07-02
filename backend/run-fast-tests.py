#!/usr/bin/env python3
"""
Fast test runner that handles conftest switching.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    """Run fast tests with proper conftest switching."""
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests"
    fast_conftest = backend_dir / "testing" / "fast" / "conftest.py"
    
    # Paths for conftest files
    original_conftest = tests_dir / "conftest.py"
    backup_conftest = tests_dir / "conftest_full.py"
    fast_conftest_target = tests_dir / "conftest.py"
    
    # Set up environment for fast tests
    env = os.environ.copy()
    env.update({
        "FAST_TESTS": "1",
        "REVIEWPOINT_ENVIRONMENT": "test",
        "REVIEWPOINT_LOG_LEVEL": "WARNING",
        "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
        "PYTHONPATH": str(backend_dir / "src"),
    })
    
    try:
        # Backup original conftest if it exists
        if original_conftest.exists():
            shutil.move(str(original_conftest), str(backup_conftest))
        
        # Copy fast conftest to tests directory
        shutil.copy2(str(fast_conftest), str(fast_conftest_target))
        
        # Run pytest with fast configuration
        cmd = [
            sys.executable, "-m", "pytest",
            "--tb=short",
            "--disable-warnings",
            "-x",
            "--fast",
            "-p", "no:cacheprovider",
        ] + sys.argv[1:]  # Pass through all arguments
        
        if not sys.argv[1:]:
            cmd.append("tests/")
        
        print(f"🚀 Running fast tests: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=backend_dir, env=env)
        return result.returncode
        
    finally:
        # Restore original conftest
        if fast_conftest_target.exists():
            fast_conftest_target.unlink()
        
        if backup_conftest.exists():
            shutil.move(str(backup_conftest), str(original_conftest))


if __name__ == "__main__":
    sys.exit(main())
