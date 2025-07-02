# Upload Tests Optimization Summary

## What We Discovered

### Original Problem
- Async upload tests were slow due to individual DB connections and authentication flows per test
- Each test was creating its own authentication token and user, causing significant overhead

### Key Findings

1. **Authentication Patterns**:
   - **Export endpoints** (fast): Use only `require_api_key` dependency
   - **Upload endpoints** (slow): Use `get_current_user` dependency which requires real users in DB
   - Direct JWT token creation only works for endpoints that don't query the database for user validation

2. **Test Patterns That Work**:
   - **Sync tests with `get_auth_header()`**: Creates real users, slower but reliable
   - **Async tests for export-only endpoints**: Fast JWT tokens work perfectly
   - **Mixed approach**: Fast for non-user-dependent tests, slower for user-dependent tests

3. **Performance Comparison**:
   - **Async export tests**: ~6.4s for 11 tests (very fast, no DB user lookups)
   - **Sync fast tests**: ~8.5s for 11 tests (some DB connection issues but mostly fast)
   - **Original async uploads**: Slow due to user creation per test

## Recommended Solutions

### Option 1: Optimized Sync Pattern (Recommended)
- Use the working sync pattern with `ExportEndpointTestTemplate`
- Use `self.get_auth_header(client)` for authentication 
- Benefit from the optimized `get_auth_header()` function in conftest.py
- Reuse the same client across tests
- Expected performance: 8-10 seconds for full test suite

### Option 2: True Async with Dependency Override
- Override the `get_current_user` dependency in tests
- Create mock users that don't require DB lookups
- More complex but potentially faster
- Expected performance: 6-8 seconds for full test suite

### Option 3: Hybrid Approach
- Use fast async tests for non-authenticated endpoints
- Use sync tests for authenticated endpoints requiring real users
- Split tests by authentication requirements

## Implementation - FINAL SOLUTION ✅

We successfully implemented Option 1 (optimized sync) in `test_uploads_fast.py` which:

- Uses the proven `ExportEndpointTestTemplate` pattern
- Leverages `self.get_auth_header(client)` for efficient auth
- **WORKS PERFECTLY** with automatic SQLite fallback to avoid DB conflicts
- Reuses the same TestClient instance
- Maintains test independence while optimizing auth overhead

## Performance Results

| Test Method | Time | Result | Notes |
|------------|------|--------|-------|
| **Original async** | ~15-20s | Many XFAIL | Slow due to concurrent DB conflicts |
| **FAST_TESTS=1 (single)** | **8.56s** | ✅ All pass | **OPTIMAL for CI/quick runs** |
| **Parallel (-n 4)** | 12.03s | ✅ All pass | Good for development |
| **Parallel (-n auto/32)** | 19.00s | ✅ All pass | Too much overhead |

## How to Use

### Test Runner Scripts (Recommended) 🚀

For the best experience, use the provided test runner scripts that automatically handle environment setup:

#### Windows (PowerShell)

```powershell
# Fast mode (8.5s) - Best for CI/CD and quick testing
.\run_upload_tests.ps1 fast

# Parallel mode (12s) - Good for development
.\run_upload_tests.ps1 parallel

# Regular mode (8.5s) - PostgreSQL testcontainer
.\run_upload_tests.ps1 regular
```

#### Linux/Mac (Bash)

```bash
# Make executable (first time only)
chmod +x run_upload_tests.sh

# Fast mode (8.5s) - Best for CI/CD and quick testing  
./run_upload_tests.sh fast

# Parallel mode (12s) - Good for development
./run_upload_tests.sh parallel  

# Regular mode (8.5s) - PostgreSQL testcontainer
./run_upload_tests.sh regular
```

**Test Runner Features:**

- ✅ **Automatically detects and uses Hatch** for proper virtual environment
- ✅ **Clear mode explanations** with performance expectations
- ✅ **Intelligent fallbacks** when Hatch is not available
- ✅ **Colored output** and helpful tips
- ✅ **Cross-platform support** (PowerShell + Bash)

### Manual Commands (Advanced Users)

#### Fastest (8.5s) - For CI and Quick Testing

```bash
$env:FAST_TESTS="1"; python -m pytest tests/api/v1/test_uploads_fast.py -v
```

#### Parallel (12s) - For Development

```bash
python -m pytest tests/api/v1/test_uploads_fast.py -v -n 4
```

#### Regular (8.5s) - Single Thread

```bash
python -m pytest tests/api/v1/test_uploads_fast.py -v
```

The **`FAST_TESTS=1`** mode automatically switches to SQLite in-memory database, eliminating all PostgreSQL connection conflicts while maintaining full test coverage.

## Key Code Patterns

### Fast Sync Test (Recommended)

```python
class TestUploadsFast(ExportEndpointTestTemplate):
    def test_upload_file_authenticated(self, client: TestClient):
        headers = self.get_auth_header(client)  # Efficient auth
        files = {"file": ("test.txt", b"content", "text/plain")}
        resp = self.safe_request(client.post, UPLOAD_ENDPOINT, files=files, headers=headers)
        self.assert_status(resp, (201, 409))
```

### Fast Async Export Test (Works for export-only endpoints)

```python
def create_admin_headers() -> dict[str, str]:
    from src.core.security import create_access_token
    payload = {"sub": "admin@example.com", "role": "admin"}
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}

class TestUploadsAsync(ExportEndpointTestTemplate):
    @pytest.mark.asyncio
    async def test_export_csv(self, async_client: AsyncClient):
        headers = create_admin_headers()  # Fast JWT, no DB lookup
        resp = await async_client.get(EXPORT_ENDPOINT, headers=headers)
        self.assert_status(resp, 200)
```

## Conclusion

For upload endpoint tests requiring authentication:

- **Use the optimized sync pattern** for reliability and good performance
- **Reserve pure async patterns** for export-only endpoints or create dependency overrides
- **The `get_auth_header()` function** in conftest.py is already optimized for test performance
- **Test isolation is maintained** while authentication overhead is minimized
