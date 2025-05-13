# Developer Setup Guide

This guide walks you through the correct setup of the ReViewPoint project. It assumes that you just cloned the repository and have no virtual environments or dependencies installed yet.

---

## Requirements

- Git
- Python **3.11.9** (choose one of the following installation methods):
  - **pyenv (Linux/macOS)**: [pyenv](https://github.com/pyenv/pyenv)
  - **pyenv-win (Windows)**: [pyenv-win](https://github.com/pyenv-win/pyenv-win)
  - **Conda**: install Python 3.11.9 environment manually
  - **System Python**: ensure version is 3.11.9 exactly
- [Poetry](https://python-poetry.org/) (required)
- [uv](https://github.com/astral-sh/uv) (required)
- Node.js (>= 18) + [PNPM](https://pnpm.io/)
- Docker (optional, for module containerization)

---

## Project Environment Strategy

| Component | Path          | Environment         | Tool      |
|-----------|---------------|---------------------|-----------|
| Docs      | `/`           | `.venv/`            | Poetry    |
| Backend   | `/backend/`   | `backend/.venv/`    | Poetry    |
| Modules   | `/modules/`   | individually scoped | Poetry or other, per language |

All Python components use **in-project virtual environments**.

---

## 1. Clone the repository

```bash
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

## 2. Install Python 3.11.9

### Option A: pyenv (Linux/macOS)
```bash
pyenv install 3.11.9
pyenv local 3.11.9
```

### Option B: pyenv-win (Windows)
```powershell
pyenv install 3.11.9
pyenv local 3.11.9
```

### Option C: Conda (any OS)
```bash
conda create -n reviewpoint python=3.11.9
conda activate reviewpoint
```

### Option D: System Python
Ensure that `python --version` returns exactly `3.11.9`.

---

## 3. Install Poetry & uv

### Poetry
```bash
pip install poetry
poetry config virtualenvs.in-project true
```

### uv (inside the venv)
```bash
poetry run pip install uv
```

---

## 4. Setup the Docs (MkDocs)

```bash
# From project root
poetry install --no-root
poetry run mkdocs serve
```

Docs available at: http://localhost:8000

---

## 5. Setup the Backend

```bash
cd backend/
poetry init  # if not already present
poetry config virtualenvs.in-project true
poetry install
poetry run uvicorn main:app --reload
```

Backend available at: http://localhost:8000/docs

---

## 6. Setup the Frontend

```bash
cd frontend/
pnpm install
pnpm run dev
```

Frontend available at: http://localhost:5173

---

## 7. Using uv for locking (optional, recommended)

```bash
uv pip freeze > requirements.lock
```

---

## Best Practices

- Always use Poetry with `virtualenvs.in-project = true`
- Each component manages its own `.venv/`
- Do not install packages globally
- Use `pyenv`, `conda`, or system version **but ensure 3.11.9**
- Use `poetry shell` inside the component folders for CLI work
- Document all changes in the relevant `README.md` or `/docs/`

---

## Related Pages

- [Architecture Overview](architektur.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)
