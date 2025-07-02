#!/usr/bin/env python3
"""
Test Log Level Configuration Helper

This script helps developers configure logging levels for pytest runs.
It can update environment variables and provide guidance on available log levels.
"""

import os
import sys


LOG_LEVELS = {
    "CRITICAL": "Only critical errors (application crashes)",
    "ERROR": "Error messages (failed operations, exceptions)",
    "WARNING": "Warning messages (deprecated features, recoverable issues)",
    "INFO": "General information (test progress, basic operations)",
    "DEBUG": "Detailed debugging information (SQL queries, internal state)",
}


def show_log_levels():
    """Display available log levels and their descriptions."""
    print("Available pytest log levels:")
    print("=" * 50)
    for level, description in LOG_LEVELS.items():
        print(f"{level:8} - {description}")
    print()
    print("Current configuration:")
    current_main = os.environ.get("REVIEWPOINT_TEST_LOG_LEVEL", "INFO")
    current_fast = os.environ.get("REVIEWPOINT_TEST_LOG_LEVEL", "INFO")
    print(f"  Main tests:  {current_main}")
    print(f"  Fast tests:  {current_fast}")


def set_log_level(level: str):
    """Set the log level for tests."""
    level = level.upper()
    if level not in LOG_LEVELS:
        print(f"Error: Invalid log level '{level}'")
        print("Valid levels are:", ", ".join(LOG_LEVELS.keys()))
        return False
    
    # Update environment variable for current session
    os.environ["REVIEWPOINT_TEST_LOG_LEVEL"] = level
    
    print(f"Log level set to {level} for current session.")
    print("\nTo make this permanent, add to your shell profile:")
    print(f"  export REVIEWPOINT_TEST_LOG_LEVEL={level}")
    print("\nOr set it when running tests:")
    print(f"  $env:REVIEWPOINT_TEST_LOG_LEVEL='{level}'; python run-fast-tests.py")
    print(f"  $env:REVIEWPOINT_TEST_LOG_LEVEL='{level}'; hatch run test")
    return True


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) == 1:
        show_log_levels()
        return
    
    if sys.argv[1] in ["-h", "--help", "help"]:
        print(__doc__)
        print("\nUsage:")
        print("  python set-test-log-level.py              # Show current levels")
        print("  python set-test-log-level.py DEBUG        # Set to DEBUG level")
        print("  python set-test-log-level.py INFO         # Set to INFO level")
        print("  python set-test-log-level.py --show       # Show available levels")
        return
    
    if sys.argv[1] in ["--show", "-s"]:
        show_log_levels()
        return
    
    level = sys.argv[1]
    set_log_level(level)


if __name__ == "__main__":
    main()
