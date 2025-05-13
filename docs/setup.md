# Developer Setup Guide

This document explains how to set up ReViewPoint locally using `poetry`, `uv`, and proper environment isolation.

---

## Requirements

- Git
- Python 3.11.9
  - **Linux/macOS**: via [pyenv](https://github.com/pyenv/pyenv)
  - **Windows**: via [pyenv-win](https://github.com/pyenv-win/pyenv-win)
- [Poetry](https://python-poetry.org/) (required)
- [uv](https://github.com/astral-sh/uv) (optional, recommended for dependency locking and freezing)
- Node.js (≥18) + [PNPM](https://pnpm.io/)
- Docker (optional, for containerized module execution)

---

## Project Structure and Environments

Each major component has its own environment:

| Component | Location       | Environment        |
|-----------|----------------|--------------------|
| Docs      | `/`            | `.venv/`           |
| Backend   | `/backend/`    | `.venv/` inside `backend/` |
| Modules   | `/modules/...` | optional per module|

We recommend using `poetry` with **in-project virtual environments** to make environments visible and fully isolated.

---

## 1. Clone the repository

```bash
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

## 2. Set Python version

### Linux/macOS (`pyenv`)

```bash
pyenv install 3.11.9
pyenv local 3.11.9
```

### Windows (`pyenv-win`)

```powershell
pyenv install 3.11.9
pyenv local 3.11.9
```

---

## 3. Setup MkDocs documentation (root level)

```bash
# Activate poetry in-project virtualenvs
poetry config virtualenvs.in-project true

# Install docs dependencies
poetry install --no-root

# Start documentation server
poetry run mkdocs serve
```

Docs will be served at: [http://localhost:8000](http://localhost:8000)

---

## 4. Setup Backend

```bash
cd backend/

# Activate poetry in-project venv for backend
poetry config virtualenvs.in-project true

# Install dependencies
poetry install

# Activate environment
poetry shell

# Run API locally
uvicorn main:app --reload
```

Backend API available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Setup Frontend

```bash
cd frontend/
pnpm install
pnpm run dev
```

Frontend available at: [http://localhost:5173](http://localhost:5173)

---

## 6. Optional: Install and use `uv`

```bash
poetry run pip install uv
```

You can use `uv` to freeze dependencies:

```bash
uv pip freeze > requirements.lock
```

---

## Best Practices

- Use `poetry shell` inside each component folder when working
- Do not install Python packages globally
- Use `.venv` directories per component to keep environments isolated
- Use consistent Python version across all components

---

## See also

- [Architecture Overview](architektur.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)
