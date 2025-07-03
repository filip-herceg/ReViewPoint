# Database Connection Debugging Guide

## Overview

We've implemented comprehensive database connection debugging to help identify and fix issues with pytest-xdist parallelization. The system provides detailed logging at every stage of database interaction.

## What Was Added

### 1. Enhanced Database Module (`src/core/database.py`)

**New Debug Features:**
- **Worker identification**: Tracks which pytest worker is making connections
- **Connection timing**: Measures time for engine creation, sessions, and queries
- **Pool state monitoring**: Logs connection pool size, checked out connections, overflow
- **Failure tracking**: Counts and logs connection failures with detailed context
- **Parallel-aware pool settings**: Automatically adjusts pool sizes for pytest workers

**Key Debug Functions:**
- `get_connection_debug_info()`: Returns current connection state
- `_log_worker_info()`: Logs worker/process/thread info
- `_log_engine_pool_state()`: Logs detailed pool statistics

### 2. Enhanced Test Configuration (`tests/conftest.py`)

**Container Management Debugging:**
- Detailed container startup timing
- Port connectivity testing with retry logic
- Database connection verification before tests start
- Worker-specific logging for parallel execution

**Engine Isolation Debugging:**
- Per-test engine creation timing
- Table creation performance tracking
- Engine disposal monitoring
- Worker-specific engine configuration

### 3. Pytest Configuration (`pyproject.toml`)

**Enhanced Logging:**
- CLI debug output enabled
- Detailed log format with timestamps
- File logging to `tests/test_debug.log`
- Better error reporting with `--tb=short`

### 4. Debug Test Script (`test_connection_debug.py`)

**Comprehensive Testing:**
- Basic health check validation
- Session creation and query testing
- Parallel connection stress testing
- Worker identification and timing analysis

## How to Use the Debugging System

### 1. Run Basic Connection Tests

```powershell
# Navigate to backend directory
cd backend

# Run the debug script directly
python test_connection_debug.py

# Run through pytest (single worker)
pytest test_connection_debug.py -v

# Run with parallel workers (this is where issues occur)
pytest test_connection_debug.py -n 2 -v
```

### 2. Run Your Actual Tests with Debug Logging

```powershell
# Run with 2 workers and full debug output
pytest tests/ -n 2 -v --log-cli-level=DEBUG

# Run specific test files with debugging
pytest tests/api/v1/test_auth.py -n 2 -v --log-cli-level=DEBUG

# Focus on database-related tests
pytest tests/core/test_database.py -n 2 -v --log-cli-level=DEBUG
```

### 3. Analyze Debug Output

Look for these key log prefixes:

**Container Management:**
- `[TESTCONTAINER_DEBUG]`: Container startup and connectivity
- `[testcontainers]`: Legacy container messages

**Database Connections:**
- `[DB_ENGINE_CREATE]`: Engine creation and configuration
- `[DB_POOL_STATE]`: Connection pool statistics
- `[DB_SESSION]`: Session lifecycle and performance
- `[DB_HEALTHCHECK]`: Health check results

**Test Infrastructure:**
- `[ENGINE_ISOLATED]`: Per-test engine management
- `[SESSION_ISOLATED]`: Test session creation

### 4. Debug Log File Analysis

All debug output is also written to `tests/test_debug.log`:

```powershell
# View recent debug logs
Get-Content backend/tests/test_debug.log -Tail 50

# Search for specific errors
Select-String "FAILED|ERROR" backend/tests/test_debug.log

# Track specific worker issues
Select-String "Worker: gw1" backend/tests/test_debug.log
```

## Common Issues to Look For

### 1. **Connection Pool Exhaustion**
```
[DB_POOL_STATE] Checked out: 5
[DB_POOL_STATE] Pool size: 5
[DB_POOL_STATE] Overflow: 0
```
- All connections are checked out
- New requests will timeout

### 2. **Container Startup Race Conditions**
```
[TESTCONTAINER_DEBUG] Connection attempt #1 failed: ConnectionRefusedError
```
- Container not ready when tests start
- Need longer wait times

### 3. **Worker Collision**
```
[DB_ENGINE_CREATE] Worker: gw0, PID: 1234
[DB_ENGINE_CREATE] Worker: gw1, PID: 5678
```
- Multiple workers trying to create engines
- Potential resource conflicts

### 4. **Session Leaks**
```
[DB_SESSION] Session #50 created
[DB_POOL_STATE] Checked out: 10
```
- High session numbers with many checked out connections
- Sessions not being properly closed

## Next Steps for Troubleshooting

### 1. **Test with Different Worker Counts**
```powershell
# Test scaling behavior
pytest test_connection_debug.py -n 1 -v  # Baseline
pytest test_connection_debug.py -n 2 -v  # Your target
pytest test_connection_debug.py -n 4 -v  # Stress test
```

### 2. **Isolate the Problem**
```powershell
# Test just the container setup
pytest tests/conftest.py::postgres_container -v

# Test just database connectivity
pytest test_connection_debug.py::test_basic_connection -v

# Test session management
pytest test_connection_debug.py::test_session_creation -v
```

### 3. **Adjust Pool Settings**
Edit `src/core/database.py` and modify the parallel worker pool settings:
```python
if os.environ.get('PYTEST_XDIST_WORKER'):
    # Try different values
    engine_kwargs["pool_size"] = 1      # Very conservative
    engine_kwargs["max_overflow"] = 1   # No overflow
```

### 4. **Container Resource Limits**
Edit `tests/conftest.py` and modify container settings:
```python
postgres.with_env("POSTGRES_MAX_CONNECTIONS", "500")  # Increase limit
postgres.with_env("POSTGRES_SHARED_BUFFERS", "1GB")   # More memory
```

## Expected Behavior

With this debugging system, you should see:

1. **Clear worker identification** in all log messages
2. **Detailed timing information** for all database operations
3. **Pool state monitoring** showing healthy connection usage
4. **Container startup confirmation** before tests begin
5. **Failure context** when things go wrong

This will help you pinpoint exactly where and why the database connections are failing during parallel test execution.
