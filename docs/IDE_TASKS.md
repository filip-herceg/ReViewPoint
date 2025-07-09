# ReViewPoint IDE Tasks Documentation

This document describes the comprehensive suite of VS Code tasks available for the ReViewPoint project. These tasks streamline development, testing, and deployment workflows.

## Quick Start

1. **Open Command Palette**: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. **Type**: `Tasks: Run Task`
3. **Select** the task you want to run from the list

Alternatively, use the **Terminal → Run Task...** menu.

## Task Categories

### 🚀 Development Tasks

| Task | Description | Background |
|------|-------------|------------|
| **ReViewPoint: Start Backend** | Starts FastAPI server with hot reload on port 8000 | ✅ |
| **ReViewPoint: Start Frontend** | Starts Vite development server on port 3000 | ✅ |
| **ReViewPoint: Start Both (Backend + Frontend)** ⭐ | Starts both servers concurrently with colored output | ✅ |
| **ReViewPoint: Start Frontend with API Types** | Generates API types and starts frontend dev server | ✅ |

⭐ = Default build task (can be run with `Ctrl+Shift+P` → `Tasks: Run Build Task`)

### 🧪 Testing Tasks

| Task | Description | Coverage |
|------|-------------|----------|
| **ReViewPoint: Run All Backend Tests** | Runs all backend tests with pytest | ❌ |
| **ReViewPoint: Run Fast Backend Tests** | Runs only fast tests (excludes slow/integration) | ❌ |
| **ReViewPoint: Run Backend Tests with Coverage** | Runs backend tests with HTML coverage report | ✅ |
| **ReViewPoint: Run Frontend Tests** | Runs frontend unit tests with Vitest | ❌ |
| **ReViewPoint: Run Frontend E2E Tests** | Runs end-to-end tests with Playwright | ❌ |
| **ReViewPoint: Run Frontend Tests with Coverage** | Runs frontend tests with coverage report | ✅ |
| **ReViewPoint: Run All Tests** | Runs all backend and frontend tests concurrently | ❌ |

### 🔧 Quality & Linting Tasks

| Task | Description | Auto-fix |
|------|-------------|----------|
| **ReViewPoint: Lint Backend** | Lints backend code with Ruff | ✅ |
| **ReViewPoint: Format Backend** | Formats backend code with Ruff | ✅ |
| **ReViewPoint: Lint Frontend** | Lints frontend code with Biome | ❌ |
| **ReViewPoint: Format Frontend** | Formats frontend code with Biome | ✅ |
| **ReViewPoint: Type Check Frontend** | Type checks frontend with TypeScript | ❌ |

### 🏗️ Build & Deploy Tasks

| Task | Description | Output |
|------|-------------|--------|
| **ReViewPoint: Build Frontend** | Builds frontend for production | `frontend/dist/` |
| **ReViewPoint: Generate API Types** | Generates TypeScript types from OpenAPI schema | `frontend/src/types/` |
| **ReViewPoint: Export Backend Schema** | Exports OpenAPI schema from backend | `frontend/openapi-schema.json` |
| **ReViewPoint: Validate API Schema** | Validates OpenAPI schema consistency | Console output |

### 🗄️ Database Tasks

#### Auto-Setup Tasks (Recommended)

| Task | Description | Auto-Setup |
|------|-------------|------------|
| **ReViewPoint: Start Development with PostgreSQL (Auto-Setup)** ⭐ | Auto-starts PostgreSQL, runs migrations, starts both servers | ✅ |
| **ReViewPoint: Start PostgreSQL Container (Auto-Setup)** | Auto-starts PostgreSQL container with health checks and migrations | ✅ |
| **ReViewPoint: Check PostgreSQL Prerequisites** | Checks if Docker and other prerequisites are available | ❌ |
| **ReViewPoint: Stop PostgreSQL Container (pnpm)** | Stops PostgreSQL container using pnpm script | ❌ |
| **ReViewPoint: Switch to SQLite Database** | Switches database configuration to SQLite | ❌ |

#### Manual Database Tasks

| Task | Description | Interactive |
|------|-------------|-------------|
| **ReViewPoint: Start PostgreSQL (Docker)** | Manually starts PostgreSQL container | ❌ |
| **ReViewPoint: Stop PostgreSQL (Docker)** | Manually stops PostgreSQL container | ❌ |
| **ReViewPoint: Switch to PostgreSQL** | Switches database configuration to PostgreSQL | ❌ |
| **ReViewPoint: Switch to SQLite** | Switches database configuration to SQLite | ❌ |
| **ReViewPoint: Run Database Migrations** | Applies all pending Alembic migrations | ❌ |
| **ReViewPoint: Create New Migration** | Creates new database migration | ✅ |

⭐ = Recommended for PostgreSQL development

### 🛠️ Utility Tasks

| Task | Description | Scope |
|------|-------------|-------|
| **ReViewPoint: Install Dependencies** | Installs all project dependencies | All modules |
| **ReViewPoint: Clean All** | Removes cache, deps, and build artifacts | All modules |
| **ReViewPoint: Audit Dependencies** | Audits dependencies for security vulnerabilities | All modules |

### 🔒 Security Tasks

| Task | Description | Output |
|------|-------------|--------|
| **ReViewPoint: Run Security Scan** | Runs Trivy security scan on the project | Console table |

## Recommended Workflows

### 🎯 First-time Setup

#### Option A: SQLite (Easiest for development)

1. `ReViewPoint: Install Dependencies`
2. `ReViewPoint: Switch to SQLite Database` (already configured by default)
3. `ReViewPoint: Run Database Migrations`
4. `ReViewPoint: Generate API Types`
5. `ReViewPoint: Start Both (Backend + Frontend)`

#### Option B: PostgreSQL with Auto-Setup (Recommended)

1. `ReViewPoint: Install Dependencies`
2. `ReViewPoint: Check PostgreSQL Prerequisites` (ensure Docker is running)
3. `ReViewPoint: Start Development with PostgreSQL (Auto-Setup)` ⭐

**That's it!** This one task will:

- Start PostgreSQL container automatically
- Wait for health check to pass
- Run database migrations
- Start both backend and frontend servers

#### Option C: PostgreSQL Manual Setup (Advanced)

1. `ReViewPoint: Install Dependencies`
2. `ReViewPoint: Start PostgreSQL (Docker)` (requires Docker)
3. `ReViewPoint: Switch to PostgreSQL`
4. `ReViewPoint: Run Database Migrations`
5. `ReViewPoint: Generate API Types`
6. `ReViewPoint: Start Both (Backend + Frontend)`

### 🔄 Daily Development

#### With PostgreSQL Auto-Setup

1. `ReViewPoint: Start Development with PostgreSQL (Auto-Setup)` (one-command startup)
2. `ReViewPoint: Run Fast Backend Tests` (after backend changes)
3. `ReViewPoint: Run Frontend Tests` (after frontend changes)
4. `ReViewPoint: Lint Backend` + `ReViewPoint: Lint Frontend` (before commits)

#### With SQLite or Manual Setup

1. `ReViewPoint: Start Both (Backend + Frontend)` (morning startup)
2. `ReViewPoint: Run Fast Backend Tests` (after backend changes)
3. `ReViewPoint: Run Frontend Tests` (after frontend changes)
4. `ReViewPoint: Lint Backend` + `ReViewPoint: Lint Frontend` (before commits)

### 🗄️ Database Management

- **SQLite**: Simpler for development, no external dependencies
- **PostgreSQL**: Production-like, requires Docker or local PostgreSQL installation
- Switch between them anytime using the "Switch to SQLite/PostgreSQL" tasks
- Migrations work with both database types

### 🧹 Pre-commit Checklist

1. `ReViewPoint: Format Backend`
2. `ReViewPoint: Format Frontend`
3. `ReViewPoint: Type Check Frontend`
4. `ReViewPoint: Run All Tests`
5. `ReViewPoint: Audit Dependencies`

### 🚀 Pre-deployment

1. `ReViewPoint: Run All Tests`
2. `ReViewPoint: Build Frontend`
3. `ReViewPoint: Run Security Scan`
4. `ReViewPoint: Validate API Schema`

## Task Details

### Background Tasks

Tasks marked as "Background" (`isBackground: true`) will continue running and won't block the VS Code interface. These are perfect for development servers.

### Problem Matchers

Most tasks don't use problem matchers to avoid conflicts, but you can add them if needed for specific error highlighting.

### Panel Organization

- **Development tasks**: Use dedicated panels for better separation
- **Testing/Build tasks**: Use shared panels to save screen space
- **Concurrent tasks**: Use colored prefixes for easy identification

## Keyboard Shortcuts

You can add custom keyboard shortcuts for frequently used tasks:

1. Open **File → Preferences → Keyboard Shortcuts** (`Ctrl+K Ctrl+S`)
2. Search for "workbench.action.tasks.runTask"
3. Add your preferred key binding
4. In the args, specify: `"args": "ReViewPoint: Start Both (Backend + Frontend)"`

Example `keybindings.json`:

```json
[
    {
        "key": "ctrl+shift+r",
        "command": "workbench.action.tasks.runTask",
        "args": "ReViewPoint: Start Both (Backend + Frontend)"
    },
    {
        "key": "ctrl+shift+t",
        "command": "workbench.action.tasks.runTask",
        "args": "ReViewPoint: Run All Tests"
    }
]
```

## Customization

### Environment Variables

Add environment variables to tasks by modifying the `options.env` property:

```json
{
    "options": {
        "cwd": "${workspaceFolder}/backend",
        "env": {
            "ENVIRONMENT": "development",
            "DEBUG": "true"
        }
    }
}
```

### Conditional Tasks

Use the `when` property to make tasks conditional:

```json
{
    "when": "resourceExtname == .py"
}
```

### Task Dependencies

Make tasks depend on others using `dependsOn`:

```json
{
    "dependsOn": ["ReViewPoint: Generate API Types"]
}
```

## Troubleshooting

### Common Issues

1. **Command not found**: Ensure tools are installed and in PATH
   - Backend: Python, pip, uvicorn
   - Frontend: Node.js, pnpm
   - Root: concurrently (automatically installed via `pnpm add -D concurrently -w`)

2. **Permission denied**: On Unix systems, make scripts executable

   ```bash
   chmod +x backend/scripts/*.sh
   ```

3. **Port already in use**: Change ports in tasks or kill existing processes

   ```bash
   # Kill process on port 8000
   kill -9 $(lsof -t -i:8000)
   # Windows PowerShell
   Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
   ```

4. **Environment variables**: Ensure `.env` files exist where needed

5. **Concurrent startup fails**: The "Start Both" task uses the `concurrently` package for reliable cross-platform execution. If it fails:
   - Ensure dependencies are installed: `pnpm install`
   - Check individual tasks work: Try "Start Backend" and "Start Frontend" separately
   - Verify paths in workspace root `package.json` dev script

### Debug Mode

Add `"options": {"shell": {"args": ["-x"]}}` to see detailed command execution.

## Contributing

When adding new tasks:

1. Follow the naming convention: `ReViewPoint: <Action> <Target>`
2. Add appropriate descriptions and details
3. Use consistent presentation settings
4. Update this documentation
5. Test on multiple platforms (Windows, macOS, Linux)

## Platform Compatibility

These tasks are designed to work across platforms, but some commands may need adjustments:

- **Windows**: Uses PowerShell by default
- **macOS/Linux**: Uses bash/sh by default
- **Cross-platform**: Uses Node.js tools when possible

For Windows-specific tasks, you may need to adjust shell commands or use `.cmd` extensions.
