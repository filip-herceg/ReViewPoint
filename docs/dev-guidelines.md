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

---

## Python Coding Standards & Linting

- **Formatting:** All Python code must be formatted with [Black](https://black.readthedocs.io/en/stable/).
- **Linting:** All Python code must pass [Ruff](https://docs.astral.sh/ruff/) checks.
- **Type Checking:** Use [mypy](http://mypy-lang.org/) for static type checks.
- **Run locally before PR:** For non-trivial changes, run `poetry run ruff check backend`, `poetry run black backend`, and `poetry run mypy backend` before pushing.
- **CI:** All PRs and pushes are checked by CI for lint, format, and type errors.
- **Configuration:** See `.ruff.toml` and `pyproject.toml` for tool settings.

---

## Python Linting & Formatting Configuration

Python code style and linting are enforced using two configuration files at the repository root:

- **`.ruff.toml`**: Contains project-specific overrides for [Ruff](https://docs.astral.sh/ruff/). By default, this file is minimal and only used for exclusions or custom rules that do not fit in `pyproject.toml`.
- **`pyproject.toml`**: The main configuration file for Python tools, including [Black](https://black.readthedocs.io/en/stable/) and Ruff. Most options for both tools should be set here for consistency and CI compatibility.

### How to Use and Customize

- **Ruff**
  - Most configuration (e.g., enabled rules, line length, select/ignore, target Python version) should be set in the `[tool.ruff]` section of `pyproject.toml`.
  - Use `.ruff.toml` only for settings that must be kept separate, such as file exclusions or overrides for specific subdirectories.
  - Example options for `[tool.ruff]` in `pyproject.toml`:
    ```toml
    [tool.ruff]
    line-length = 88
    select = ["E", "F", "W", "C90"]
    ignore = ["E501"]
    target-version = ["py311"]
    # See https://docs.astral.sh/ruff/configuration/ for all options
    ```
  - Example `.ruff.toml` for file exclusion:
    ```toml
    exclude = ["backend/models/base.py"]
    ```

- **Black**
  - Configure Black in the `[tool.black]` section of `pyproject.toml`.
  - Example options:
    ```toml
    [tool.black]
    line-length = 88
    target-version = ["py311"]
    include = '\\.(py)$'
    exclude = '''
    /(\.eggs|\.git|\.mypy_cache|\.tox|\.venv|_build|buck-out|build|dist)/
    '''
    # See https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-format for all options
    ```

- **Best Practices**
  - Keep most configuration in `pyproject.toml` for clarity and to ensure CI/CD tools pick up the correct settings.
  - Use `.ruff.toml` only for project-specific overrides or exclusions.
  - Always check in both files to version control.
  - For exhaustive configuration options, see the official documentation for [Ruff](https://docs.astral.sh/ruff/configuration/) and [Black](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-format).

---

## Troubleshooting & FAQ for Linting and Formatting

- **Common Issues:**
  - *Ruff or Black not running as expected?* Ensure you are using the correct Python environment and that both tools are installed (via Poetry or pip).
  - *CI fails on formatting or linting?* Run the local commands shown above and review the output for specific errors. Fix issues and re-commit.
  - *Conflicting rules?* Double-check both `pyproject.toml` and `.ruff.toml` for overlapping or contradictory settings. Prefer `pyproject.toml` for most options.
  - *Editor integration:* Most editors (VS Code, PyCharm, etc.) support auto-formatting and linting on save. Configure your editor to use the project’s settings for a smoother workflow.

- **Useful Commands:**
  - Auto-fix all files with Black: `poetry run black .`
  - Auto-fix all files with Ruff: `poetry run ruff check . --fix`
  - Auto-format with autopep8 (aggressive): `poetry run python -m autopep8 --in-place --aggressive --aggressive <file-or-directory>`
  - Check only for errors (no auto-fix): `poetry run ruff check .` and `poetry run black . --check`

- **Where to get help:**
  - See the [FAQ](./faq.md) for more troubleshooting tips.
  - Ask in project discussions or open an issue if you are stuck.

---

## Using GitHub Features Effectively

- **Issues & Tickets:**
  - Use GitHub Issues to report bugs, request features, or ask questions. This helps keep discussions organized and visible to all contributors.
  - Use the "New Issue" button on GitHub to quickly create tickets for anything that needs tracking.
  - Reference issues in your commits and pull requests using `#issue-number` for automatic linking.

- **Pull Requests:**
  - Use the "Compare & pull request" button on GitHub after pushing your branch to open a pull request.
  - Fill out the PR template and link related issues for better traceability.
  - Use GitHub’s review tools to request feedback, comment on code, and resolve conversations.

- **Automation:**
  - Take advantage of GitHub’s automation features, such as labels, assignees, and project boards, to organize and prioritize work.
  - Use draft pull requests to get early feedback before your work is finished.

---

## Example Workflow for New Contributors

1. Fork and clone the repository.
2. Install dependencies: `poetry install`
3. Create a new branch: `git checkout -b feature/my-feature`
4. Make your changes, following the code style and commit/branch rules above.
5. Run all checks locally:
    ```sh
    poetry run ruff check backend
    poetry run black backend
    poetry run mypy backend
    poetry run pytest
    ```
6. Commit using a conventional commit message.
7. Push your branch and use the GitHub UI to open a pull request (use the provided button for convenience).
8. Reference or create issues as needed using GitHub’s issue tracker.
9. Respond to code review and CI feedback.

---

## Commit Message & Branch Naming

- **Commit messages:** Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
  - `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
- **Branch naming:** Use `feature/<short-description>`, `bugfix/<short-description>`, or `chore/<short-description>`.
- **No direct pushes to `main`:** Always use feature branches and pull requests.

---

## Contribution Process

- Pull latest `main` before starting work.
- Push to feature branches only.
- Use pull requests with clear descriptions and request reviewers.
- Follow code review feedback and ensure all checks pass before merging.

---

## Awareness

- All contributors **must** follow linting and formatting requirements. PRs that do not pass CI will not be merged.
- For more details, see the [Development Standards](./docs/dev-guidelines.md).
