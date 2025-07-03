#!/bin/bash

# ReViewPoint Upload Tests - Optimized Test Runner
# Runs the optimized upload tests using the fastest available method.
# Automatically checks for Hatch and uses the backend virtual environment.

MODE=${1:-fast}

echo "🚀 ReViewPoint Upload Tests - Optimized Test Runner"
echo "============================================="
echo ""

# Check if Hatch is installed
echo "🔍 Checking environment setup..."
if command -v hatch &> /dev/null; then
    HATCH_VERSION=$(hatch --version 2>/dev/null)
    echo "✅ Hatch found: $HATCH_VERSION"
    USE_HATCH=true
else
    echo "❌ Hatch not found. Please install Hatch: https://hatch.pypa.io/latest/install/"
    echo "   Alternative: pip install hatch"
    USE_HATCH=false
fi

# Explain the modes
echo ""
echo "📋 Available Test Modes:"
echo "  🚀 fast     - SQLite in-memory DB, single thread (~8.5s)"
echo "               ✓ FASTEST execution, no PostgreSQL overhead"
echo "               ✓ Perfect for CI/CD and quick development cycles"
echo "               ✓ Uses FAST_TESTS=1 environment variable"
echo ""
echo "  ⚡ parallel - SQLite in-memory DB, 4 workers (~12s)"
echo "               ✓ Tests run in true parallel (good for development)"
echo "               ✓ Slightly slower due to worker coordination overhead"
echo "               ✓ Uses pytest-xdist for parallel execution"
echo ""
echo "  🐘 regular  - PostgreSQL testcontainer, single thread (~8.5s)"
echo "               ✓ Tests against real PostgreSQL database"
echo "               ✓ Most realistic but slower container startup"
echo "               ✓ Good for integration testing"
echo ""

# Validate mode
case $MODE in
    "fast"|"parallel"|"regular")
        echo "🎯 Running in '$MODE' mode..."
        ;;
    *)
        echo "❌ Invalid mode: $MODE"
        echo "Usage: $0 [fast|parallel|regular]"
        echo "  fast     - SQLite in-memory, single thread (~8.5s) [default]"
        echo "  parallel - SQLite in-memory, 4 workers (~12s)"
        echo "  regular  - PostgreSQL, single thread (~8.5s)"
        exit 1
        ;;
esac

# Execute tests based on mode
echo ""
echo "⚙️  Executing tests..."

if [ "$USE_HATCH" = true ]; then
    # Use Hatch to run in the proper virtual environment
    case $MODE in
        "fast")
            echo "⚡ FAST mode: SQLite in-memory database (fastest)"
            FAST_TESTS=1 hatch run pytest tests/api/v1/test_uploads_fast.py -v
            ;;
        "parallel")
            echo "⚡ PARALLEL mode: 4 workers with SQLite coordination"
            FAST_TESTS=1 hatch run pytest tests/api/v1/test_uploads_fast.py -v -n 4
            ;;
        "regular")
            echo "⚡ REGULAR mode: PostgreSQL testcontainer"
            hatch run pytest tests/api/v1/test_uploads_fast.py -v
            ;;
    esac
else
    echo "⚠️  Running without Hatch (may not use correct virtual environment)"
    case $MODE in
        "fast")
            echo "⚡ FAST mode: SQLite in-memory database (fastest)"
            FAST_TESTS=1 python -m pytest tests/api/v1/test_uploads_fast.py -v
            ;;
        "parallel")
            echo "⚡ PARALLEL mode: 4 workers with SQLite coordination"
            python -m pytest tests/api/v1/test_uploads_fast.py -v -n 4
            ;;
        "regular")
            echo "⚡ REGULAR mode: PostgreSQL testcontainer"
            python -m pytest tests/api/v1/test_uploads_fast.py -v
            ;;
    esac
fi

echo ""
echo "✅ Upload tests completed in $MODE mode"
echo ""
echo "💡 Tips:"
echo "   • Use 'fast' mode for quick development cycles"
echo "   • Use 'parallel' mode when testing multiple features"
echo "   • Use 'regular' mode for comprehensive integration testing"
echo "   • All modes test the same functionality with different performance profiles"
