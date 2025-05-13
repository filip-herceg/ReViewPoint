# Development Standards

This document outlines the coding, testing, formatting, and collaboration guidelines for the ReViewPoint project.

## Code Style

### Python

- Format: `black`
- Linter: `ruff`
- Type checking: `mypy`
- Dependency manager: `poetry`

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
