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

## More Resources

- [Setup Guide](setup.md)
- [Backend Source Guide](backend-source-guide.md)
- [CI/CD](ci-cd.md)
