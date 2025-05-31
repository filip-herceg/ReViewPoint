# Developer Setup Guide

This guide explains how to set up the ReViewPoint project from a fresh clone using `poetry`, `uv`, and isolated Python environments for each component.

---

## Requirements

You will need the following tools installed:

- Git
- Python **3.11.9**  
  Choose **one** of the following installation methods:
  - **System Python**
  - **pyenv (Linux/macOS)**: [pyenv](https://github.com/pyenv/pyenv)
  - **pyenv-win (Windows)**: [pyenv-win](https://github.com/pyenv-win/pyenv-win)
  - **Conda**: creates an isolated environment
- [Poetry](https://python-poetry.org/) (**installed once globally**)
- [uv](https://github.com/astral-sh/uv) (required inside venvs)
- Node.js (>= 18) + [PNPM](https://pnpm.io/)
- Docker (optional, for containerized modules)

---

## What Poetry Does

> **Poetry is installed globally**, but it creates and manages project-specific virtual environments for you.  
> These `.venv/` folders are created **automatically** when you run `poetry install`.

You do **not** need to manually create venvs or install pip packages directly.

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

## 2. Set up Python 3.11.9

Choose one method to install the required Python version (3.11.9).

### Option A: System Python

Ensure:

```bash
python --version
# → Must return exactly: 3.11.9
```

### Option B: pyenv / pyenv-win

```bash
pyenv install 3.11.9
pyenv local 3.11.9
```

### Option C: Conda

```bash
conda create -n reviewpoint python=3.11.9
conda activate reviewpoint
```


---

## 3. Install Poetry (globally)

Install Poetry once, using the Python environment you’re currently in.

```bash
pip install poetry
```

Then enable per-project venvs:

```bash
poetry config virtualenvs.in-project true
```

This ensures that `.venv/` folders are created **within each project component**.

For convenience please add the `shell` plugin for Poetry:
```bash
poetry self add poetry-plugin-shell

```

---

## 4. Install uv (per environment)

Once you're inside a Poetry-managed environment, install `uv`:

```bash
poetry run pip install uv
```

Repeat per component if needed.

---

## 5. Set up the Docs (MkDocs)

```bash
# From project root
poetry install --no-root
poetry run mkdocs serve
```

Docs available at: http://localhost:8000

This creates `.venv/` in the root directory.

---

## 6. Set up the Backend

```bash
cd backend/
poetry install
poetry run uvicorn main:app --reload
```

Backend available at: http://localhost:8000/docs

This creates `backend/.venv/`.

---

## 7. Set up the Frontend

```bash
cd frontend/
pnpm install
pnpm run dev
```

Frontend available at: http://localhost:5173

---

## 8. (Optional) Freeze dependencies with uv

```bash
uv pip freeze > requirements.lock
```

---

## Best Practices

- Use **Poetry only** to manage Python environments and install packages
- Install Poetry **once globally**, then use it per component
- Use `poetry config virtualenvs.in-project true` to keep `.venv/` local
- Never install pip packages manually
- Use `poetry shell` to activate environments for CLI work
- Use `pyenv`, `conda`, or exact system Python 3.11.9 for version consistency

---

## Related Pages

- [Architecture Overview](architecture.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)
