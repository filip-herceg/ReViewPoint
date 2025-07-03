# CI/CD

> **Automate, test, and deploy with confidence.**

---

## Pipeline Overview

- Automated tests and linting on every push/PR
- Build and deploy using GitHub Actions
- Coverage and quality gates

---

## CI/CD Pipeline Diagram

```mermaid
graph TD
    C1[Push/PR to GitHub] --> A1[Run Prettier, markdownlint, mkdocs-lint]
    A1 --> B1[Run Ruff, Black, Mypy, Pytest]
    B1 --> C2[Build Docs with MkDocs]
    C2 --> D1[Deploy Docs (GitHub Pages/Netlify)]
    B1 --> D2[Build & Deploy Backend]
    B1 --> D3[Build & Deploy Frontend]
    D1 --> E1[Docs Live Preview]
    D2 --> E2[Backend Live]
    D3 --> E3[Frontend Live]
```

---

## Quickstart

### Run All Checks

- Push your branch to GitHub
- Open a pull request
- All checks run automatically

---

## More Info

- [Developer Guidelines](dev-guidelines.md)
- [Backend Source Guide](backend-source-guide.md)
