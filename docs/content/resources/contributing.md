# Contributing to ReViewPoint

We welcome contributions to ReViewPoint! This guide will help you get started with contributing to our open-source PDF review platform.

## Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/ReViewPoint.git
cd ReViewPoint
```

### 2. Set Up Development Environment

```bash
# Install all dependencies
pnpm run install

# Start development with PostgreSQL (recommended)
pnpm run dev:postgres

# Or use SQLite for simpler setup
pnpm run dev
```

### 3. Make Your Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Write tests for your changes
# Ensure all tests pass

# Commit using conventional commits
git commit -m "feat(auth): add JWT token refresh mechanism"
```

### 4. Submit Pull Request

- Push your changes to your fork
- Create a pull request against the main branch
- Fill out the PR template completely
- Wait for review and address feedback

## Development Workflow

### Branch Strategy

We use a simplified Git Flow:

- **`main`**: Production-ready code
- **`feature/*`**: New features
- **`fix/*`**: Bug fixes
- **`docs/*`**: Documentation updates
- **`refactor/*`**: Code refactoring

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
type(scope): description

Examples:
feat(auth): add JWT token refresh mechanism
fix(api): resolve CORS issue for file uploads
docs(readme): update installation instructions
test(user): add unit tests for user service
refactor(db): optimize database queries
chore(deps): update dependencies to latest versions
```

### Code Quality Standards

#### Backend (Python)

- **Linting**: `ruff check` and `ruff format`
- **Type Checking**: `mypy` for static type analysis
- **Testing**: `pytest` with 85%+ coverage minimum
- **Documentation**: Docstrings for all public functions

#### Frontend (TypeScript)

- **Linting**: `@biomejs/biome` for formatting and linting
- **Type Checking**: TypeScript strict mode
- **Testing**: `Vitest` for unit tests, `Playwright` for E2E
- **Component Standards**: React best practices

### Running Tests

```bash
# Run all tests
pnpm run test:all

# Backend tests only
pnpm run test:backend

# Frontend tests only
cd frontend && pnpm test

# E2E tests
cd frontend && pnpm run test:e2e

# With coverage
pnpm run test:backend:coverage
cd frontend && pnpm run test:coverage
```

## Types of Contributions

### 🐛 Bug Reports

**Before submitting a bug report:**

1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Provide minimal reproduction steps

**Bug report template:**

```markdown
## Bug Description

Clear description of the bug

## Steps to Reproduce

1. Go to...
2. Click on...
3. See error

## Expected Behavior

What you expected to happen

## Actual Behavior

What actually happened

## Environment

- OS: [e.g., Windows 11, macOS 14]
- Browser: [e.g., Chrome 121, Firefox 122]
- ReViewPoint Version: [e.g., v1.2.0]

## Additional Context

Screenshots, logs, or additional information
```

### ✨ Feature Requests

**Before submitting a feature request:**

1. Check if the feature already exists
2. Search existing feature requests
3. Consider if it fits the project's scope

**Feature request template:**

```markdown
## Feature Description

Clear description of the proposed feature

## Problem Statement

What problem does this solve?

## Proposed Solution

How should this feature work?

## Alternatives Considered

What alternatives have you considered?

## Additional Context

Mockups, examples, or additional context
```

### 🔧 Code Contributions

#### Backend Contributions

**Common areas for contribution:**

- API endpoint improvements
- Database optimization
- Authentication enhancements
- File processing features
- Background task improvements

**Backend structure:**

```text
backend/
├── src/
│   ├── api/            # API endpoints
│   ├── core/           # Core business logic
│   ├── db/             # Database models and operations
│   ├── services/       # Business services
│   └── utils/          # Utility functions
├── tests/              # Test files
└── alembic/           # Database migrations
```

#### Frontend Contributions

**Common areas for contribution:**

- UI/UX improvements
- Component library expansion
- Performance optimizations
- Accessibility enhancements
- Mobile responsiveness

**Frontend structure:**

```text
frontend/src/
├── components/         # Reusable UI components
├── pages/             # Page components
├── hooks/             # Custom React hooks
├── services/          # API service layer
├── stores/            # State management
├── utils/             # Utility functions
└── types/             # TypeScript type definitions
```

### 📚 Documentation Contributions

**Documentation needs:**

- API documentation improvements
- Tutorial creation
- Code example additions
- Translation support
- Video tutorials

**Documentation structure:**

```text
docs/
├── content/
│   ├── index.md           # Homepage
│   ├── installation.md   # Installation guide
│   ├── developer-overview.md
│   └── resources/         # Additional resources
└── mkdocs.yml            # Documentation configuration
```

## Code Review Process

### Review Criteria

**All pull requests must:**

1. ✅ Pass all automated tests
2. ✅ Meet code quality standards (linting, formatting)
3. ✅ Include appropriate tests for new functionality
4. ✅ Update documentation if needed
5. ✅ Follow security best practices
6. ✅ Maintain backward compatibility when possible

### Review Timeline

- **Initial Response**: Within 2 business days
- **Full Review**: Within 1 week for standard PRs
- **Hot Fixes**: Within 24 hours for critical issues

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainer reviews code quality and design
3. **Testing**: Reviewer tests the functionality
4. **Approval**: PR approved and merged

## Security Considerations

### Security-First Development

- **Authentication**: Secure JWT implementation
- **Authorization**: Proper permission checks
- **Input Validation**: Validate all user inputs
- **File Uploads**: Secure file handling practices
- **SQL Injection**: Use parameterized queries
- **XSS Prevention**: Proper output escaping

### Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Instead, email security issues to: [security@reviewpoint.dev](mailto:security@reviewpoint.dev)

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Schedule

- **Patch Releases**: As needed for bug fixes
- **Minor Releases**: Monthly feature releases
- **Major Releases**: When breaking changes are necessary

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](https://github.com/filip-herceg/ReViewPoint/blob/main/CODE_OF_CONDUCT.md).

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Email**: security@reviewpoint.dev for security issues

### Recognition

Contributors are recognized in:

- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- GitHub contributor graph
- Special recognition for long-term contributors

## Getting Help

### Development Questions

1. Check the [Developer Documentation](../developer-overview.md)
2. Search existing GitHub issues
3. Create a new discussion on GitHub
4. Ask specific questions in your PR

### Common Setup Issues

**PostgreSQL Connection Issues:**

```bash
# Check if PostgreSQL is running
pnpm run postgres:check

# Restart PostgreSQL container
pnpm run postgres:start
```

**Node/Python Version Issues:**

```bash
# Check versions
node --version  # Should be 18+
python --version  # Should be 3.11+

# Use version managers if needed
nvm use 18
pyenv local 3.11
```

**Dependency Issues:**

```bash
# Clean install
pnpm run clean
pnpm run install
```

### Advanced Development

**Database Migrations:**

```bash
# Create new migration
cd backend && hatch run alembic revision --autogenerate -m "add new table"

# Apply migrations
pnpm run db:migrate
```

**API Schema Updates:**

```bash
# Export backend schema
pnpm run api:export-schema

# Generate frontend types
cd frontend && pnpm run generate:types
```

## Contributing Checklist

Before submitting your contribution:

- [ ] Fork and clone the repository
- [ ] Create a feature branch from `main`
- [ ] Install dependencies with `pnpm run install`
- [ ] Make your changes with appropriate tests
- [ ] Run `pnpm run test:all` to ensure all tests pass
- [ ] Run linting: `pnpm run lint:backend` and `pnpm run lint:frontend`
- [ ] Follow conventional commit format
- [ ] Update documentation if needed
- [ ] Create pull request with clear description
- [ ] Respond to review feedback promptly

## Thank You! 🙏

Your contributions help make ReViewPoint better for everyone. Whether you're fixing a bug, adding a feature, or improving documentation, every contribution matters.

For questions about contributing, feel free to create a GitHub discussion or reach out to the maintainers.
