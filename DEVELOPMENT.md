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
