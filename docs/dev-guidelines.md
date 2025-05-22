# Development Standards

> **Follow these guidelines for consistent, high-quality code and collaboration.**

---

## Code Style

**Python**
- Format: `black`
- Linter: `ruff`
- Type checking: `mypy`
- Dependency manager: `poetry`

---

## Handling Ruff E402 Errors

**E402: Module Level Import Not at Top of File**
1. **Preferred:** Move all imports to the top of your file.
2. **Auto-fix:**
    ```shell
    poetry run ruff check --fix path/to/your_file.py
    poetry run python -m autopep8 --in-place --aggressive --aggressive path/to/your_file.py
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

## More Resources

- [Setup Guide](setup.md)
- [Backend Source Guide](backend-source-guide.md)
- [CI/CD](ci-cd.md)
