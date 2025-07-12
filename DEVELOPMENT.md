# ReViewPoint Development Setup

## Prerequisites for ALL Developers

### 1. Node.js & pnpm

- Install Node.js 18+ from [nodejs.org](https://nodejs.org/)
- Install pnpm: `npm install -g pnpm`

### 2. Git Configuration (Important for hooks)

Set up Git to handle line endings properly:

```bash
# For Windows users
git config --global core.autocrlf true

# For macOS/Linux users  
git config --global core.autocrlf input
```

### 3. Initial Setup

After cloning the repository:

```bash
# Install dependencies
pnpm install
```

### 4. Choose Your Development Database

**Option A: SQLite (Recommended for beginners)**

- No Docker required
- Fast startup
- File-based database

```bash
pnpm dev
```

**Option B: PostgreSQL (Production-like)**

- Requires Docker Desktop
- Auto-setup with containers
- Production database engine

```bash
pnpm dev:postgres
```

For detailed PostgreSQL setup and troubleshooting, see [PostgreSQL Setup Guide](docs/POSTGRES_SETUP.md).

## Git Hooks

This project no longer uses Husky or pre-commit Git hooks. Please run linting and formatting manually before committing.

## Development Workflow

1. Make your changes
2. Stage files: `git add .`
3. Commit: `git commit -m "your message"`
   - Pre-commit hooks will run automatically
   - Linting and formatting will be applied
4. Push: `git push`

## Directory Structure

- `frontend/` - React frontend application
- `backend/` - Python FastAPI backend
- `docs/` - Documentation

## Frontend Development Standards

### Button Usage Policy

All buttons must use the standardized `Button` component from `@/components/ui/button`. Raw `<button>` elements are prohibited to ensure:

- Consistent visual design
- Proper accessibility
- Maintainable codebase
- Theme consistency

See [Button Standards Documentation](docs/development/BUTTON_STANDARDS.md) for complete guidelines.

Quick examples:

```tsx
// ✅ CORRECT
<Button variant="destructive">Delete</Button>
<Button variant="outline" size="sm">Cancel</Button>

// ❌ PROHIBITED
<button className="px-4 py-2 bg-red-500">Delete</button>
```

The ESLint configuration will automatically flag violations of this policy.
