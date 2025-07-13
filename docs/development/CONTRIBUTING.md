# Contributing to ReViewPoint Backend

Thank you for your interest in contributing! This guide will help you get started and ensure a smooth development experience.

## Environment Setup

1. **Copy the example environment file:**
   ```powershell
   Copy-Item .env.example .env
   ```
2. **Edit `.env`** and fill in all required secrets and configuration values. See comments in `.env.example` for details.
3. **Never commit your `.env` file** to version control. It is ignored by `.gitignore`.
4. **For CI/CD:** Set environment variables as secrets in your pipeline or deployment platform. Do not use real secrets in `.env.example`.

## Dependency Management
- Use [Poetry](https://python-poetry.org/) for installing and managing dependencies.
- If you add a new dependency, run `poetry install` and commit the updated `pyproject.toml` and `poetry.lock`.

## Coding Standards
- Format code with `black`.
- Lint with `ruff`.
- Type-check with `mypy`.
- Follow [Developer Guidelines](../docs/dev-guidelines.md).

## Testing
- Run tests with:
  ```powershell
  poetry run pytest
  ```
- For coverage:
  ```powershell
  poetry run pytest --cov=backend --cov-report=term --cov-report=xml
  ```

## Opening a Pull Request
1. Fork and clone the repository.
2. Create a new branch for your feature or fix.
3. Write code and tests.
4. Ensure all checks pass (format, lint, type-check, test).
5. Push and open a Pull Request.

For questions, open a GitHub Issue or see the [FAQ](../docs/faq.md).
