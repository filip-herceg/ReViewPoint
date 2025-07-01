# Backend Test Suite

## Parallel Test Execution

To run tests in parallel for maximum speed, install `pytest-xdist`:

```sh
pip install pytest-xdist
```

Then run:

```sh
pytest -n auto
```

- Use `-m "not slow"` to skip slow tests (e.g., those that hit the real database).
- Use `FAST_TESTS=1` to enable in-memory SQLite for most tests.

## Test Markers
- `@pytest.mark.slow` — marks slow/integration tests
- `@pytest.mark.fast` — marks fast/unit tests

## Test Data Factories
See `tests/factories.py` for reusable test data factories.

---

For more details, see the main documentation or ask the team.
