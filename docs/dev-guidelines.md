# Development Standards

This document outlines the coding, testing, formatting, and collaboration guidelines for the ReViewPoint project.

## Code Style

### Python

- Format: `black`
- Linter: `ruff`
- Type checking: `mypy`
- Dependency manager: `poetry`

---

## Handling Ruff E402 Errors (Module Level Import Not at Top of File)

If you encounter Ruff's `E402` error ("module level import not at top of file"), follow these steps:

1. **Preferred Solution:**
   - Move all import statements to the very top of your Python file, after any module-level docstring or comments.
   - This is the best practice and ensures your code is clean and compliant.

2. **Automatic Fix:**
   - Run the following command to let Ruff attempt to fix the import order automatically:
     ```sh
     poetry run ruff check --fix path/to/your_file.py
     ```
   - If Ruff cannot fix it, use autopep8 for aggressive auto-formatting:
     ```sh
     poetry run python -m autopep8 --in-place --aggressive --aggressive path/to/your_file.py
     ```
   - After running these, re-run Ruff to confirm the error is resolved.

3. **Suppressing the Error (Not Recommended):**
   - Only if absolutely necessary, you can add `# noqa: E402` to the offending import line to silence the warning.

---

## When to Run Ruff, Mypy, Black, and Pytest

Our CI workflow will automatically run the following checks on every pull request and push:
- Ruff (linting)
- Black (formatting)
- Mypy (type checking)
- Pytest (tests and coverage)

**You only need to run these locally if:**
- You want to catch issues before pushing (recommended for larger or more complex changes).
- You are preparing a pull request and want to avoid unnecessary CI failures and extra commits.
- You are refactoring, adding new features, or fixing bugs that might affect code style, types, or tests.

**How to run all checks locally:**
```sh
poetry run ruff check backend
poetry run black backend --check
poetry run mypy backend
poetry run pytest --maxfail=1 --disable-warnings --cov=backend --cov-report=xml --cov-report=term
```

**Tip:**
- For small or trivial changes, you may rely on CI, but for anything non-trivial, running these checks locally will save you time and help keep the codebase clean.

---

### JavaScript/TypeScript (Frontend)

- Format: `Prettier`
- Linter: `ESLint`
- React with Zustand + TailwindCSS

---

## Linting Commands

```bash
# Backend and Modules
ruff check .
black .

# Frontend
pnpm run lint
pnpm run format
```

---

## Testing

### Backend

```bash
pytest
pytest --cov
```

### Frontend

```bash
pnpm run test
pnpm run coverage
```

---

## Coverage

Minimum coverage target: 80%  
Tools: `coverage.py`, `c8`, `pytest`, `vitest`

---

## CI/CD

- GitHub Actions
- Lint + Test on every push to `main`
- Separate CI for docs, backend, modules, frontend

---

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```text
feat:     add new feature
fix:      fix bug
docs:     documentation only
style:    formatting only
refactor: code change without behavior change
test:     add or change tests
chore:    CI, build, meta changes
```

---

## Collaboration Rules

- Always pull latest `main` before starting work
- Push to feature branches only
- Use pull requests with description and reviewers
- Do not push directly to `main`
