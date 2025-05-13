# Developer Setup Guide

This guide explains how to set up the ReViewPoint project from a fresh clone, using `poetry`, `uv`, and isolated environments for each component.

---

## Requirements

- Git
- Python **3.11.9**  
  Choose **one** of the following:
  - **System-wide installation** (make sure `python --version` is 3.11.9)
  - **pyenv** (Linux/macOS): [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv)
  - **pyenv-win** (Windows): [https://github.com/pyenv-win/pyenv-win](https://github.com/pyenv-win/pyenv-win)
  - **Conda**: `conda create -n reviewpoint python=3.11.9`
- [Poetry](https://python-poetry.org/) (required)
- [uv](https://github.com/astral-sh/uv) (required)
- Node.js (>= 18) + [PNPM](https://pnpm.io/)
- Docker (optional, for module containerization)

---

## Component Environments

| Component | Path        | Environment          | Tool    |
|-----------|-------------|----------------------|---------|
| Docs      | `/`         | `.venv/`             | Poetry  |
| Backend   | `/backend/` | `backend/.venv/`     | Poetry  |
| Modules   | `/modules/` | Optional, per-module | Poetry or other (language dependent) |

---

## 1. Clone the repository

```bash
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

## 2. Set up Python 3.11.9

### Option A: pyenv / pyenv-win

```bash
pyenv install 3.11.9
pyenv local 3.11.9
```

### Option B: Conda

```bash
conda create -n reviewpoint python=3.11.9
conda activate reviewpoint
```

### Option C: System Python

Ensure:
```bash
python --version
# → must output: 3.11.9
```

---

## 3. Install Poetry & uv

```bash
pip install poetry
poetry config virtualenvs.in-project true
poetry run pip install uv
```

---

## 4. Set up Documentation Environment

```bash
# From project root
poetry install --no-root
poetry run mkdocs serve
```

Docs available at: http://localhost:8000

---

## 5. Set up Backend Environment

```bash
cd backend/
poetry init  # only if pyproject.toml doesn't exist
poetry config virtualenvs.in-project true
poetry install
poetry run uvicorn main:app --reload
```

Backend available at: http://localhost:8000/docs

---

## 6. Set up Frontend

```bash
cd frontend/
pnpm install
pnpm run dev
```

Frontend available at: http://localhost:5173

---

## 7. (Optional) Lock dependencies with uv

```bash
uv pip freeze > requirements.lock
```

---

## Best Practices

- Always use `poetry config virtualenvs.in-project true`
- Do not install packages globally
- Each Python component manages its own `.venv/`
- Use `pyenv`, `pyenv-win`, Conda, or System Python — but ensure version 3.11.9
- Activate Poetry environments using `poetry shell`
- Always install `uv` inside the Poetry environment

---

## Related Pages

- [Architecture Overview](architektur.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)
