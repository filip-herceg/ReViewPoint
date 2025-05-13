# Developer Setup Guide

This document guides you through setting up ReViewPoint on your local development machine.

---

## Prerequisites

- Git
- Python 3.11.9
  - **Linux/macOS:** via [pyenv](https://github.com/pyenv/pyenv)
  - **Windows:** via [pyenv-win](https://github.com/pyenv-win/pyenv-win)
- [Poetry](https://python-poetry.org/)
- [uv](https://github.com/astral-sh/uv) (optional but recommended)
- Node.js (≥18) + [PNPM](https://pnpm.io/)
- Docker (optional, for module/container orchestration)

---

## Step-by-step Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

### 2. Set Python version

#### Linux/macOS (using `pyenv`)

```bash
pyenv install 3.11.9
pyenv local 3.11.9
```

#### Windows (using `pyenv-win`)

```powershell
pyenv install 3.11.9
pyenv local 3.11.9
```

---

### 3. Install Poetry

```bash
pip install poetry
```

Check:

```bash
poetry --version
```

---

### 4. Create virtual environment & install dependencies

```bash
poetry install
poetry shell
```

---

### 5. (Optional) Install and use `uv` for lock management

```bash
poetry run pip install uv
```

If needed:

```bash
uv pip freeze > requirements.lock
```

This creates a `requirements.lock` file for reproducible installs in Docker or CI environments.

---

### 6. Launch documentation (MkDocs)

```bash
mkdocs serve
```

Then open [http://localhost:8000](http://localhost:8000)

---

### 7. Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

---

### 8. Backend Setup

```bash
cd backend
poetry install
uvicorn main:app --reload
```

---

### 9. Docker (Optional)

```bash
docker-compose up --build
```

---

## Tips

- Always activate the poetry shell before running backend commands
- Avoid installing Python packages globally — use `poetry` and `.venv` only
- Use `uv` for high-speed dependency locking if needed