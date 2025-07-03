#!/usr/bin/env python3
"""
Test script to verify conditional skips for fast tests.

This script runs tests in both regular and fast test modes to confirm
that the conditional skip markers are working correctly.

Run this script from the backend directory with:
python verify_conditional_skip.py
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, env=None, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    env = env or os.environ.copy()
    result = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    """Run tests in both modes to verify conditional skips."""
    backend_dir = Path(__file__).parent.absolute()
    
    # Set up environments for testing
    base_env = os.environ.copy()
    
    # Regular mode environment
    regular_env = base_env.copy()
    regular_env.update({
        "FAST_TESTS": "0",
        "REVIEWPOINT_ENVIRONMENT": "test"
    })
    
    # Fast mode environment
    fast_env = base_env.copy()
    fast_env.update({
        "FAST_TESTS": "1",
        "REVIEWPOINT_ENVIRONMENT": "test",
        "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:"
    })
    
    # Test file with conditional skips to verify
    test_file = "tests/utils/test_cache.py::TestAsyncInMemoryCache::test_ttl_expiry"
    
    print("\n=== Testing in Regular Mode (should run) ===")
    code, stdout, stderr = run_command(
        ["pytest", "-xvs", test_file],
        env=regular_env,
        cwd=backend_dir
    )
    print(stdout)
    if "SKIPPED" in stdout:
        print("❌ Test was incorrectly skipped in regular mode!")
    else:
        print("✅ Test ran successfully in regular mode!")
    
    print("\n=== Testing in Fast Mode (should skip) ===")
    code, stdout, stderr = run_command(
        ["pytest", "-xvs", test_file],
        env=fast_env,
        cwd=backend_dir
    )
    print(stdout)
    if "SKIPPED" in stdout:
        print("✅ Test was correctly skipped in fast mode!")
    else:
        print("❌ Test didn't skip in fast mode!")
    
    # Try with our run-fast-tests script
    print("\n=== Testing with run-fast-tests.py ===")
    code, stdout, stderr = run_command(
        [sys.executable, "run-fast-tests.py", "-xvs", test_file],
        cwd=backend_dir
    )
    print(stdout)
    if "SKIPPED" in stdout:
        print("✅ Test was correctly skipped with run-fast-tests.py!")
    else:
        print("❌ Test didn't skip with run-fast-tests.py!")

if __name__ == "__main__":
    main()
