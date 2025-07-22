# ReViewPoint Documentation Module

This directory contains the full documentation and developer manual for the ReViewPoint project, managed as a minimal Python project for reproducible environment management with Hatch.

## Structure

- `content/` — All Markdown documentation, images, and guides (used by MkDocs)
- `overrides/` — Custom MkDocs theme overrides
- `mkdocs.yml` — MkDocs configuration
- `.markdownlint.json` — Markdown linting configuration
- `src/docs/` — Minimal Python package (required for Hatch, not for documentation content)
- `tests/` — (Optional) Python tests for documentation tools or extensions
- `pyproject.toml` — Project and environment configuration (see below)
- `README.md` — This file

## Environment Management

- All documentation dependencies (MkDocs, plugins, linters) are managed via Hatch and specified in `[tool.hatch.envs.default]` in `pyproject.toml`.
- No documentation content is inside `src/` — only Python package code for Hatch compatibility.

## Usage

```sh
cd docs
hatch env create
hatch run mkdocs serve  # or mkdocs build
```

## License

`docs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
