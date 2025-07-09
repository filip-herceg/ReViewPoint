#!/usr/bin/env python3
"""
Unified test runner for ReViewPoint backend.

Provides easy access to both fast and full test suites.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list[str], description: str = "") -> int:
    """Run a command and return the result."""
    if description:
        print(f"🚀 {description}")
        print(f"📁 Running: {' '.join(cmd)}")
        print("=" * 60)

    start_time = time.time()
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    duration = time.time() - start_time

    print("=" * 60)
    print(f"⏱️  Duration: {duration:.2f} seconds")

    if result.returncode == 0:
        print("✅ Tests completed successfully")
    else:
        print("❌ Tests failed")

    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ReViewPoint Backend Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py fast                    # Run fast tests
  python test.py full                    # Run full test suite
  python test.py fast tests/test_auth.py # Run specific fast tests
  python test.py watch                   # Run fast tests in watch mode
  python test.py coverage                # Run fast tests with coverage
        """,
    )

    parser.add_argument(
        "mode", choices=["fast", "full", "watch", "coverage"], help="Test mode to run"
    )

    parser.add_argument(
        "args", nargs="*", help="Additional arguments to pass to pytest"
    )

    args = parser.parse_args()

    if args.mode == "fast":
        cmd = ["hatch", "run", "fast:test"] + args.args
        return run_command(cmd, "Running fast tests")

    elif args.mode == "full":
        cmd = ["hatch", "run", "pytest"] + args.args
        return run_command(cmd, "Running full test suite")

    elif args.mode == "watch":
        cmd = ["hatch", "run", "fast:watch"] + args.args
        return run_command(cmd, "Running fast tests in watch mode")

    elif args.mode == "coverage":
        cmd = ["hatch", "run", "fast:coverage"] + args.args
        return run_command(cmd, "Running fast tests with coverage")
    else:
        return 1  # Ensure all code paths return int


if __name__ == "__main__":
    sys.exit(main())
