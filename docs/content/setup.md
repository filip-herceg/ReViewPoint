# Developer Setup Guide

This guide explains how to set up the ReViewPoint project from a fresh clone using Hatch for Python environments and MkDocs for documentation.

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
- [Hatch](https://hatch.pypa.io/) (installed once globally)
- Node.js (>= 18) + [PNPM](https://pnpm.io/)
- Docker (optional, for containerized modules)

---

## Project Environment Strategy

| Component | Path        | Environment         | Tool    |
|-----------|-------------|---------------------|---------|
| Docs      | `/docs/`    | Hatch env           | Hatch   |
| Backend   | `/backend/` | Hatch env           | Hatch   |
| Frontend  | `/frontend/`| Node.js/PNPM        | PNPM    |

All Python components use **Hatch-managed virtual environments**.

---

## 1. Clone the repository

```bash
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

## 2. Set up Python 3.11.9

Ensure you are using Python 3.11.9 for all Python components. Use `pyenv`, `pyenv-win`, or Conda if needed.

---

## 3. Install Hatch (globally)

Install Hatch once, using the Python environment you’re currently in.

```bash
pip install hatch
```

---

## 4. Set up the Docs (MkDocs)

```bash
cd docs
hatch env create
hatch run mkdocs serve
```

Docs available at: http://localhost:8000

---

## 5. Set up the Backend

```bash
cd backend
hatch env create
hatch run uvicorn src.backend.main:app --reload
```

Backend available at: http://localhost:8000/docs

---

## 6. Set up the Frontend

```bash
cd ../frontend
pnpm install
pnpm run dev
```

Frontend available at: http://localhost:5173

---

## Best Practices

- Use **Hatch only** to manage Python environments and install packages
- Install Hatch **once globally**, then use it per component
- Never install pip packages manually
- Use `hatch shell` to activate environments for CLI work
- Use `pyenv`, `conda`, or exact system Python 3.11.9 for version consistency

---

## Related Pages

- [Architecture Overview](architecture.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)
