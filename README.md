# ReViewPoint

[![Docs Build](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml/badge.svg "Docs Build Status")](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml)
[![Lint Status](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml/badge.svg?label=lint "Lint Status")](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml)
![Test Coverage](docs/content/images/coverage.svg "Test Coverage Badge")

> **Start Here:** For all contributors and users, please read the [Development Guidelines](https://filip-herceg.github.io/ReViewPoint/dev-guidelines/) before making changes or opening a Pull Request.

ReViewPoint is a modular, scalable platform for academic paper evaluation using Large Language Models (LLMs) and rule-based algorithms. It is designed for researchers, reviewers, and developers who want to automate, accelerate, and improve the quality of scientific paper review workflows.

---

## Quickstart

- **[Setup Guide](https://filip-herceg.github.io/ReViewPoint/setup/):** Step-by-step environment and installation instructions (Hatch-based, no pyenv/conda).
- **[System Architecture](https://filip-herceg.github.io/ReViewPoint/architecture/):** Visual overview, diagrams, and directory/file breakdowns.
- **[Backend Source Guide](https://filip-herceg.github.io/ReViewPoint/backend-source-guide/):** Layered, cross-referenced backend documentation.

## Development

- **[Developer Guidelines](https://filip-herceg.github.io/ReViewPoint/dev-guidelines/):** Coding standards, workflow, PR process, and test mapping.
- **[CI/CD](https://filip-herceg.github.io/ReViewPoint/ci-cd/):** Project-specific continuous integration and deployment info.
- **[How to Use the Docs](https://filip-herceg.github.io/ReViewPoint/how-to-use-docs/):** Navigation, search, and best practices for contributors.

## Modules

- **[Module Guide](https://filip-herceg.github.io/ReViewPoint/module-guide/):** How to build, test, and integrate modules.
- **[LLM Integration](https://filip-herceg.github.io/ReViewPoint/llm-integration/):** Adapters, prompt templating, and LLM usage.

## Resources

- **[FAQ](https://filip-herceg.github.io/ReViewPoint/faq/):** Common questions and troubleshooting.
- **[Changelog](https://filip-herceg.github.io/ReViewPoint/changelog/):** Major updates and documentation changes.
- **[Documentation Enhancements](https://filip-herceg.github.io/ReViewPoint/documentation-enhancements/):** Advanced features, plugins, and tips.

---

## Project Overview

ReViewPoint provides a flexible backend for:

- Automated evaluation of scientific papers (PDFs) using LLMs and rule-based algorithms
- Modular, plug-and-play analysis modules
- Secure user management and file uploads
- Extensible LLM adapters (OpenAI, vLLM, etc.)
- Async, production-grade backend with CI/CD and test infrastructure

**Main use-cases:**

- Academic peer review support
- Automated compliance and structure checks
- Custom module development for new evaluation criteria

## System Architecture

- **Frontend:** React + Vite + TailwindCSS (see docs)
- **Backend:** FastAPI core, async SQLAlchemy, modular dispatch
- **Modules:** Dockerized microservices, JSON I/O, independent CI
- **LLM Layer:** Pluggable adapters (OpenAI, vLLM), prompt templating
- **Storage:** PostgreSQL (metadata), MinIO/S3 (file storage)

See the [Architecture Diagram](https://filip-herceg.github.io/ReViewPoint/architecture/) for a visual overview.

## Features

- Modular backend with plug-and-play modules
- Async database and file storage
- Secure user authentication and management
- File upload and PDF parsing
- LLM integration (OpenAI, vLLM, Jinja2 prompts)
- Full test suite and CI/CD pipeline

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/reviewpoint.git
   cd reviewpoint
   ```

2. **Install dependencies:**

   ```bash
   hatch env create
   hatch run pip install -e .
   ```

3. **Activate the environment:**

   ```bash
   hatch shell
   ```

4. **Configure environment variables** as needed (see `backend/.env.example` if available).

For full setup details, see the [Setup Guide](https://filip-herceg.github.io/ReViewPoint/setup/).

## Documentation

- **Docs website:** [https://filip-herceg.github.io/ReViewPoint/](https://filip-herceg.github.io/ReViewPoint/)
- [Architecture](https://filip-herceg.github.io/ReViewPoint/architecture/)
- [Developer Guidelines](https://filip-herceg.github.io/ReViewPoint/dev-guidelines/)
- [Module Guide](https://filip-herceg.github.io/ReViewPoint/module-guide/)
- [LLM Integration](https://filip-herceg.github.io/ReViewPoint/llm-integration/)
- [Backend Docs](https://filip-herceg.github.io/ReViewPoint/backend/)

## Development Standards

- **Formatting:** [black](https://black.readthedocs.io/)
- **Linting:** [ruff](https://docs.astral.sh/ruff/)
- **Type checking:** [mypy](https://mypy-lang.org/)
- **Dependency management:** [hatch](https://hatch.pypa.io/)
- **Commit messages:** Conventional, see [Developer Guidelines](https://filip-herceg.github.io/ReViewPoint/dev-guidelines/)

## Contribution Workflow

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Install** dependencies with `hatch env create && hatch run pip install -e .`
4. **Create a new branch** for your feature or fix
5. **Write code and tests** (format, lint, type-check before commit)
6. **Push** your branch and open a **Pull Request**
7. **CI/CD** will run tests and checks automatically
8. **Discuss and revise** as needed

For questions or bugs, [open a GitHub Issue](https://github.com/filip-herceg/ReViewPoint/issues).

See [Developer Guidelines](https://filip-herceg.github.io/ReViewPoint/dev-guidelines/) for details.

## Testing

- Run all backend tests:

  ```bash
  hatch run pytest
  ```

- Run with coverage:

  ```bash
  hatch run pytest --cov=backend --cov-report=term --cov-report=xml
  ```

- See [Backend Test Instructions](https://filip-herceg.github.io/ReViewPoint/backend/test-instructions/) for more.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
