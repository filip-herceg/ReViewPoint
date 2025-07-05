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
# Install dependencies and set up Husky hooks
pnpm install

# This will automatically run "husky install" via the prepare script
```

## Git Hooks (Husky)

This repository uses Husky for pre-commit hooks that:

- Run ESLint on frontend code
- Format code with Biome
- Ensure code quality before commits

### Troubleshooting Git Hooks

If you get "cannot spawn .husky/pre-commit" error:

1. **Ensure proper setup**: Run `pnpm install` in the root directory
2. **Check Git configuration**: Verify `git config core.hooksPath` returns `.husky`
3. **Line endings**: The `.gitattributes` file ensures proper line endings
4. **Reinstall hooks**: Run `npx husky install` if needed

### For Windows Users

If you're using PowerShell or Command Prompt and hooks still fail:

- Git for Windows should handle shell script execution automatically
- Ensure Git for Windows is properly installed with Git Bash
- The hooks use npm scripts for cross-platform compatibility

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
- `.husky/` - Git hooks configuration
