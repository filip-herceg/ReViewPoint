# ReViewPoint Documentation

This directory contains the MkDocs-based documentation for the ReViewPoint project.

## Quick Start

1. **Install Hatch** (if not already installed):

   ```bash
   pip install hatch
   ```

2. **Create and activate the documentation environment**:

   ```bash
   cd docs
   hatch env create
   ```

3. **Serve the documentation locally**:

   ```bash
   hatch run serve
   ```

4. **Build the documentation**:

   ```bash
   hatch run build
   ```

## Environment Management

This documentation project uses Hatch for environment management:

- Virtual environment is created in `.venv/`
- All MkDocs dependencies are managed via `pyproject.toml`
- Scripts are available via `hatch run <script-name>`

## Structure

```text
docs/
├── pyproject.toml          # Hatch configuration and dependencies
├── mkdocs.yml             # MkDocs configuration
├── content/               # Documentation content
│   ├── index.md          # Homepage
│   ├── installation.md   # Installation guide
│   ├── vision-mission-goals.md
│   ├── current-status.md
│   ├── future-goals.md
│   ├── developer-overview.md
│   ├── backend/          # Backend documentation
│   ├── frontend/         # Frontend documentation
│   └── resources/        # References and resources
└── overrides/            # Theme customizations
```

## Available Scripts

- `hatch run serve` - Start development server
- `hatch run build` - Build static site
- `hatch run clean` - Clean build and start fresh

## Development

After making changes to the documentation:

1. Test locally with `hatch run serve`
2. Build to verify with `hatch run build`
3. Commit and push changes
