#!/usr/bin/env python3
"""
Fast test runner for ReViewPoint backend.

This script sets up the fast test environment and runs pytest with optimized configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_fast_test_environment():
    """Set up the fast test environment by copying the fast conftest."""
    backend_dir = Path(__file__).parent.parent.parent
    fast_conftest = Path(__file__).parent / "conftest.py"
    tests_dir = backend_dir / "tests"
    
    # Backup original conftest if it exists
    original_conftest = tests_dir / "conftest.py"
    backup_conftest = tests_dir / "conftest.py.backup"
    
    if original_conftest.exists() and not backup_conftest.exists():
        shutil.copy2(original_conftest, backup_conftest)
        print(f"✓ Backed up original conftest to {backup_conftest}")
    
    # Copy fast conftest
    shutil.copy2(fast_conftest, original_conftest)
    print(f"✓ Using fast test configuration from {fast_conftest}")

def restore_original_conftest():
    """Restore the original conftest after tests."""
    backend_dir = Path(__file__).parent.parent.parent
    tests_dir = backend_dir / "tests"
    
    original_conftest = tests_dir / "conftest.py"
    backup_conftest = tests_dir / "conftest.py.backup"
    
    if backup_conftest.exists():
        shutil.copy2(backup_conftest, original_conftest)
        print(f"✓ Restored original conftest from {backup_conftest}")

def main():
    """Run fast tests with proper environment setup."""
    backend_dir = Path(__file__).parent.parent.parent
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    try:
        # Set up fast test environment
        setup_fast_test_environment()
        
        # Set environment variables for fast tests
        os.environ.update({
            "FAST_TESTS": "1",
            "REVIEWPOINT_ENVIRONMENT": "test",
            "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
            "REVIEWPOINT_LOG_LEVEL": "WARNING",
        })
        
        # Run pytest with fast configuration
        pytest_args = [
            sys.executable, "-m", "pytest",
            "--tb=short",
            "-v",
            "--no-cov",  # Disable coverage for speed
        ] + sys.argv[1:]  # Pass through any additional arguments
        
        print(f"Running: {' '.join(pytest_args)}")
        result = subprocess.run(pytest_args)
        
        return result.returncode
        
    finally:
        # Always restore the original conftest
        restore_original_conftest()

if __name__ == "__main__":
    sys.exit(main())
