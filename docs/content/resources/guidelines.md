# Resources & Guidelines

> **Your complete reference for development standards, guides, and project resources.**

## 📋 **Quick Links**

| Resource | Description | Link |
|----------|-------------|------|
| **Development Guidelines** | Code standards & workflow | [↓ See below](#development-guidelines) |
| **Testing Guide** | Complete testing documentation | [Testing Guide →](testing.md) |
| **API Reference** | Full API documentation | [API Docs →](api-reference.md) |
| **Contributing** | How to contribute to the project | [Contributing →](contributing.md) |
| **FAQ** | Common questions & troubleshooting | [FAQ →](faq.md) |

---

## 🛠️ **Development Guidelines**

### **Code Quality Standards**

| Language | Formatter | Linter | Type Checker |
|----------|-----------|--------|--------------|
| **Python** | `black` | `ruff` | `mypy` |
| **TypeScript** | `Biome` | `Biome` | `tsc` |
| **Markdown** | `Prettier` | `markdownlint` | - |

### **Testing Requirements**

| Component | Framework | Min Coverage | Command |
|-----------|-----------|--------------|---------|
| **Backend** | `pytest` | 85%+ | `pnpm run test:backend` |
| **Frontend** | `Vitest` | 80%+ | `cd frontend && pnpm test` |
| **E2E** | `Playwright` | Critical paths | `cd frontend && pnpm run test:e2e` |
- **Test Types**: Unit tests, integration tests, API tests
- **Database Testing**: Both SQLite (fast) and PostgreSQL (full) modes
- **Commands**:
  - Fast tests: `hatch run fast:test`
  - All tests: `hatch run pytest`
  - With coverage: `hatch run pytest --cov=src --cov-report=html`

### Frontend Testing

- **Unit Tests**: `Vitest` - Fast unit test runner
- **E2E Tests**: `Playwright` - End-to-end browser testing
- **Coverage Target**: 80%+ test coverage minimum
- **Commands**:
  - Unit tests: `pnpm test`
  - E2E tests: `pnpm run test:e2e`
  - With coverage: `pnpm run test:coverage`

## Git Workflow

### Branch Strategy

- **Feature Branches**: All changes must be made in feature branches
- **Naming Convention**: `feature/description`, `fix/bug-description`, `docs/update-description`
- **Pull Requests**: All changes must go through pull request review

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
type(scope): description

feat(auth): add JWT token refresh mechanism
fix(api): resolve CORS issue for file uploads
docs(readme): update installation instructions
test(user): add unit tests for user service
```

### Code Review

- **Small PRs**: Keep pull requests focused and small for easier review
- **All Tests Pass**: CI/CD pipeline must pass before merge
- **Code Coverage**: Maintain or improve test coverage
- **Documentation**: Update docs for API or behavior changes

## Development Environment

### Required Tools

- **Backend**: Python 3.11+, Hatch (environment management)
- **Frontend**: Node.js 18+, PNPM (package management)
- **Database**: PostgreSQL (production), SQLite (development)
- **Editor**: VS Code (recommended with configured tasks)

### Environment Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/filip-herceg/ReViewPoint.git
   cd ReViewPoint
   ```

2. **Install Dependencies**:
   ```bash
   pnpm run install  # Installs both backend and frontend dependencies
   ```

3. **Start Development**:
   ```bash
   pnpm run dev              # SQLite mode (simple)
   pnpm run dev:postgres     # PostgreSQL mode (production-like)
   ```

### VS Code Tasks

Use the integrated VS Code tasks for common operations:

- `ReViewPoint: Install Dependencies` - One-command setup
- `ReViewPoint: Start Both (Backend + Frontend) - PostgreSQL` - Full stack development
- `ReViewPoint: Run All Tests` - Comprehensive testing
- `ReViewPoint: Lint Backend` / `ReViewPoint: Lint Frontend` - Code quality checks

## Best Practices

### Code Quality

1. **Write Tests First**: Follow TDD principles where possible
2. **Type Safety**: Use TypeScript strictly, enable all type checks
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Use structured logging for debugging and monitoring
5. **Security**: Validate all inputs, use secure coding practices

### Performance

1. **Async Operations**: Use async/await patterns consistently
2. **Database Queries**: Optimize queries, use proper indexing
3. **Frontend**: Implement code splitting and lazy loading
4. **Caching**: Use appropriate caching strategies

### Documentation

1. **Code Comments**: Write clear, concise comments for complex logic
2. **API Documentation**: Keep OpenAPI specs up-to-date
3. **README Updates**: Update documentation with code changes
4. **Architecture Documentation**: Document significant architectural decisions

## CI/CD Pipeline

### Automated Checks

- **Code Quality**: Linting and formatting validation
- **Tests**: Full test suite execution
- **Security**: Dependency vulnerability scanning
- **Build**: Successful build verification

### Deployment

- **Staging**: Automatic deployment to staging environment
- **Production**: Manual approval for production deployment
- **Rollback**: Automated rollback capabilities

## Getting Help

- **Documentation**: Start with this documentation site
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Request help during pull request review
