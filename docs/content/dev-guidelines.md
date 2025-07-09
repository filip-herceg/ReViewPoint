# Development Standards

> **Follow these guidelines for consistent, high-quality code and collaboration.**

---

## Code Style

### Python

- Format: `black`
- Linter: `ruff`
- Type checking: `mypy`
- Dependency manager: `hatch`

---

## Handling Ruff E402 Errors

### E402: Module Level Import Not at Top of File

1. **Preferred:** Move all imports to the top of your file.
2. **Auto-fix:**

   ```shell
   hatch run ruff check --fix path/to/your_file.py
   hatch run python -m autopep8 --in-place --aggressive --aggressive path/to/your_file.py
   ```

3. **Suppress (not recommended):** Add `# noqa: E402` to the import line.

---

## When to Run Ruff, Mypy, Black, and Pytest

- CI runs all checks on every PR and push:
  - Ruff (linting)
  - Black (formatting)
  - Mypy (type checking)
  - Pytest (tests and coverage)

**Tip:** Run these locally before pushing for faster feedback and fewer CI failures.

---

## Git & Collaboration

- Use feature branches for all changes.
- Write clear, descriptive commit messages.
- Keep PRs focused and small for easier review.

---

## Markdown & Documentation Standards

### Markdown Formatting & Linting

- Format all Markdown files in `docs/` using [Prettier](https://prettier.io/) and [markdownlint](https://github.com/DavidAnson/markdownlint).
- Use the following commands to auto-format and lint:

  ```bash
  npx prettier --write "docs/**/*.md"
  npx markdownlint-cli2 "docs/**/*.md"
  ```

- The CI workflow will run these checks on every PR and push.
- To auto-fix most issues, run Prettier. For detailed linting, use markdownlint (see `.markdownlint.json` for rules).
- MkDocs config is checked with `mkdocs-lint`.

### Pre-commit Hooks

- You can set up pre-commit hooks to run Prettier and markdownlint before each commit (see `pyproject.toml`).

### Docs Build

- Docs must pass all lint/format checks before merging.
- See [Documentation Enhancements](documentation-enhancements.md) for more tips and tools.

---

## Environment Variables Setup

- Before running the backend, you must create your own environment file:
  1. Copy the template: `backend/.env.template` to `backend/.env`.
  2. Fill in all required secrets and configuration values in `backend/.env`.
  3. **Never commit your `.env` file** to version control. It is ignored by `.gitignore`.
  4. For CI/CD, set environment variables as secrets in your pipeline or deployment platform. Do not use real secrets in `.env.template`.

Example (PowerShell):
```powershell
Copy-Item backend/.env.template backend/.env
# Then edit backend/.env to set your secrets and config
```

See comments in `backend/.env.template` for descriptions of each variable.

---

## Testing & Logging

### Running Tests

ReViewPoint provides multiple testing modes for different scenarios:

```bash
# Default development testing (recommended)
hatch run fast:test                    # All tests with fast SQLite environment

# Quick feedback during TDD
hatch run fast:fast-only              # Skip slow tests for maximum speed

# Production validation
hatch run pytest                     # Full PostgreSQL integration tests
```

### Test Logging Configuration

Configure test log levels using pytest CLI flags for different debugging needs:

```bash
# CLI flags (recommended approach)
hatch run pytest --log-level=DEBUG          # Detailed SQL queries and internal state
hatch run pytest --log-level=INFO           # General test progress
hatch run pytest --log-level=WARNING        # Minimal output (default)

# Using convenient hatch scripts
hatch run test-debug                         # DEBUG level with live output
hatch run test-quiet                         # WARNING level, minimal noise
hatch run test                               # INFO level, balanced output

# Live log output during test execution
hatch run pytest --log-cli-level=DEBUG -s   # Show logs in real-time
```

**Available Log Levels:**

- **DEBUG**: Detailed debugging (SQL queries, internal state, all framework logs)
- **INFO**: General information (default for development testing)
- **WARNING**: Minimal output (default for fast tests, recommended for CI/CD)
- **ERROR**: Only error messages
- **CRITICAL**: Only critical errors

**Key Points:**

- Default log level is **WARNING** to reduce test noise
- Use CLI flags to override - no need to manually set environment variables
- Fast tests (`FAST_TESTS=1`) default to WARNING for speed
- All log levels work with both fast and slow test modes

**Legacy Method (still supported):**

```powershell
# PowerShell - if you prefer environment variables
$env:REVIEWPOINT_LOG_LEVEL = 'DEBUG'
hatch run pytest

# Bash/Linux  
export REVIEWPOINT_LOG_LEVEL=DEBUG
hatch run pytest
```

📖 **See [backend/TESTING.md](../backend/TESTING.md) and [backend/TEST_LOGGING.md](../backend/TEST_LOGGING.md) for complete testing documentation.**

---

## More Resources

- [Setup Guide](setup.md)
- [Backend Source Guide](backend-source-guide.md)
- [CI/CD](ci-cd.md)
