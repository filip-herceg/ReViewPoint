# Test Documentation: backend/tests/utils/test_rate_limit.py

## Overview

This file documents the tests for backend rate limiting utilities, ensuring:

- Request counting and windowing
- Reset logic after window expires
- Handling of multiple users/keys

## Test Coverage

| Test Name                | Purpose                                         | Method                  | Expected Results                                                                 |
|--------------------------|-------------------------------------------------|-------------------------|----------------------------------------------------------------------------------|
| test_async_rate_limiter  | Validates async rate limiting, reset, and global reset | Async (pytest-asyncio)  | Allows up to max_calls, blocks after; reset allows again; global reset resets all |

## Best Practices

- Test for both allowed and blocked scenarios
- Simulate time passage if needed (e.g., with freezegun)

## Example Test Structure

```python
import pytest
from backend.src.utils.rate_limit import RateLimiter

def test_rate_limiter_blocks_excess_requests():
    limiter = RateLimiter(max_requests=2, window_seconds=10)
    assert limiter.allow("user1")
    assert limiter.allow("user1")
    assert not limiter.allow("user1")  # Should block on third request
```

## Related Docs

- [Rate Limit Utility Source](../../../src/utils/rate_limit.py.md)
- [Backend Source Guide](../../../../backend-source-guide.md)
