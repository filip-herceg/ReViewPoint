# Developer Setup Guide

This guide explains how to set up the ReViewPoint project from a fresh clone using `poetry`, `uv`, and properly isolated environments for each component.

---

## Requirements

- Git
- Python **3.11.9**  
  Choose **one** of the following installation methods:
  - **System Python**
  - **pyenv (Linux/macOS)**: [pyenv](https://github.com/pyenv/pyenv)
  - **pyenv-win (Windows)**: [pyenv-win](https://github.com/pyenv-win/pyenv-win)
  - **Conda**: creates a dedicated environment
- [Poetry](https://python-poetry.org/) (required)
- [uv](https://github.com/astral-sh/uv) (required)
- Node.js (>= 18) + [PNPM](https://pnpm.io/)
- Docker (optional, for containerized modules)

---

## Project Environment Strategy

| Component | Path        | Environment         | Tool    |
|-----------|-------------|---------------------|---------|
| Docs      | `/`         | `.venv/`             | Poetry  |
| Backend   | `/backend/` | `backend/.venv/`     | Poetry  |
| Modules   | `/modules/` | Optional, per-module | Poetry or other |

All Python components use **in-project virtual environments**.

---

## 1. Clone the repository

```bash
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

## 2. Set up Python 3.11.9 and install Poetry

Choose one method below to install Python 3.11.9.  
Then install Poetry **inside the selected environment**.

---

### Option A: pyenv / pyenv-win

```bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m pip install poetry
```

> Poetry is installed globally under your `pyenv`-managed interpreter.

---

### Option B: Conda (recommended for Windows users)

```bash
conda create -n reviewpoint python=3.11.9
conda activate reviewpoint
python -m pip install poetry
```

> Poetry is installed inside the active Conda environment.

---

### Option C: System Python

```bash
python --version  # Must return 3.11.9
python -m pip install poetry
```

> ⚠️ This installs Poetry globally – acceptable for quick setup, but not ideal for managing multiple projects.

---

### After installing Poetry:

Configure in-project environments and install uv:

```bash
poetry config virtualenvs.in-project true
poetry run pip install uv
```

---

## 3. Set up Documentation Environment

```bash
# From project root
poetry install --no-root
poetry run mkdocs serve
```

Docs available at: http://localhost:8000

---

## 4. Set up Backend Environment

```bash
cd backend/
poetry install
poetry run uvicorn main:app --reload
```

Backend available at: http://localhost:8000/docs

---

## 5. Set up Frontend

```bash
cd frontend/
pnpm install
pnpm run dev
```

Frontend available at: http://localhost:5173

---

## 6. (Optional) Freeze dependencies with uv

```bash
uv pip freeze > requirements.lock
```

---

## Best Practices

- Always use `poetry config virtualenvs.in-project true`
- Never install Python packages globally unless using `pipx`
- Each component (docs, backend, modules) has its own `.venv/`
- Use `pyenv`, `conda`, or system Python (exact version: 3.11.9)
- Use `poetry shell` when working interactively
- Document all environment-specific behavior clearly in `README.md` or `setup.md`

---

## Related Pages

- [Architecture Overview](architektur.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)
