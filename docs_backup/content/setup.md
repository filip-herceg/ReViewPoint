# Developer Setup Guide

This guide explains how to set up the ReViewPoint project from a fresh clone using **Hatch** for Python environments and **MkDocs** for documentation. All Python environment management is handled exclusively by Hatch.

---

## Requirements

You will need the following tools installed:

- Git
- Python **3.11.9** (system installation recommended)
- [Hatch](https://hatch.pypa.io/) (install once globally)
- Node.js (>= 18) + [PNPM](https://pnpm.io/)
- Docker (optional, for containerized modules)

> **Note:** Do not use `pyenv`, `conda`, or any other Python environment manager. Only Hatch is supported for Python components.

---

## Project Environment Strategy

| Component | Path         | Environment  | Tool  |
| --------- | ------------ | ------------ | ----- |
| Docs      | `/docs/`     | Hatch env    | Hatch |
| Backend   | `/backend/`  | Hatch env    | Hatch |
| Frontend  | `/frontend/` | Node.js/PNPM | PNPM  |

All Python components use **Hatch-managed virtual environments** defined in their respective `pyproject.toml` files.

---

## 1. Clone the repository

```pwsh
git clone https://github.com/your-org/reviewpoint.git
cd reviewpoint
```

---

## 2. Install Hatch (globally)

Install Hatch once, using your system Python:

```pwsh
pip install --user hatch
```

---

## 3. Set up the Docs (MkDocs)

```pwsh
cd docs
hatch env create
hatch run mkdocs serve
```

Docs available at: <http://localhost:8000>

---

## 4. Set up the Backend

```pwsh
cd ../backend
hatch env create
hatch run uvicorn src.main:app --reload
```

Backend available at: <http://localhost:8000/docs>

---

## 5. Set up the Frontend

```pwsh
cd ../frontend
pnpm install
pnpm run dev
```

Frontend available at: <http://localhost:5173>

---

## Best Practices

- Use **Hatch only** to manage Python environments and install packages
- Never install pip packages manually in project directories
- Use `hatch shell` to activate environments for CLI work
- Always use Python **3.11.9** (system install recommended)
- All dependencies are managed via `pyproject.toml` in each component

---

## Troubleshooting & Tips

- Always run commands in the correct directory (`docs`, `backend`, or `frontend`) as required.
- If you encounter issues with Hatch, try deactivating and reactivating your shell, or restart your terminal.
- If you see errors about missing dependencies, ensure you have run `hatch env create` in the relevant directory.
- For Windows users: All commands are shown for PowerShell (`pwsh`). If you use a different shell, adapt commands as needed.
- If you have issues with Node.js or PNPM, ensure you are using Node.js 18+ and the latest PNPM version.

---

## Related Pages

- [Architecture Overview](architecture.md)
- [Development Guidelines](dev-guidelines.md)
- [Module Guide](module-guide.md)

---

> **Please follow this setup guide exactly for a smooth onboarding experience. If you encounter any issues or have suggestions for improvement, open an issue or pull request in the repository.**
