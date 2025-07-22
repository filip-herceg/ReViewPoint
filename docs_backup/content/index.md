# Welcome to ReViewPoint

[![Docs Build](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml/badge.svg "Docs Build Status")](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml)
[![Lint Status](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml/badge.svg?label=lint "Lint Status")](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml)
![Test Coverage](images/coverage.svg "Test Coverage Badge")

> **Modular, scalable, and LLM-powered platform for scientific paper review.**

---

## Quick Links - Complete Documentation Index

*This homepage contains links to **ALL .md files** in the root docs/content/ directory (without subdirectories). For comprehensive backend and frontend file documentation, see the [System Architecture](architecture.md) page.*

### 🏗️ Core Documentation
- [System Architecture](architecture.md) - Complete system design with visual diagrams, file structure, and component interactions for both backend and frontend
- [API Reference](api-reference.md) - Complete REST API documentation with endpoint specifications and examples
- [Backend Source Guide](backend-source-guide.md) - Comprehensive overview of backend codebase structure, conventions, and file organization
- [Changelog](changelog.md) - Comprehensive version history, release notes, and change tracking
- [CI/CD](ci-cd.md) - Continuous integration and deployment pipeline documentation and workflows

### �️ Development & Setup
- [Contributing to Docs](contributing-docs.md) - Guidelines for contributing to and improving project documentation
- [Database Implementation](database-implementation.md) - Database schema design, migration strategies, and data modeling with PostgreSQL/SQLite
- [Developer Guidelines](dev-guidelines.md) - Coding standards, formatting rules, best practices, and contribution workflows
- [Documentation Enhancements](documentation-enhancements.md) - History of documentation improvements and enhancement tracking
- [FAQ](faq.md) - Frequently asked questions, troubleshooting, and common issues resolution
- [How to Use Docs](how-to-use-docs.md) - Complete guide to navigating and effectively using this documentation

### 🗄️ Integration & Extensions
- [LLM Integration](llm-integration.md) - Large Language Model integration patterns, adapters, and multi-provider support
- [Main Application Entry Point](main.py.md) - FastAPI application entry point, configuration, and startup logic
- [Module Guide](module-guide.md) - Creating, integrating, and deploying new analysis modules for paper review
- [Setup Guide](setup.md) - Complete installation and configuration instructions for development and production environments

### 📚 Testing & Quality
- [Test Instructions](test-instructions.md) - Complete guide to running tests, test structure, and testing methodologies across the project
- [Test Log Levels](test-log-levels.md) - Configuration and control of logging levels during testing and development
- [Test Log Levels Implementation](test-log-levels-implementation.md) - Technical implementation details of the test logging system

### ❓ Help & Support
- [404 Page](404.md) - Custom error page documentation and navigation assistance
- [FAQ](faq.md) - Frequently asked questions, troubleshooting, and common issues resolution
- [How to Use Docs](how-to-use-docs.md) - Complete guide to navigating and effectively using this documentation

---

<div class="grid cards">

<div class="card">
<h3>🚀 Quickstart</h3>
<ul>
  <li><a href="setup.md">Setup Guide</a> - Complete development environment setup with modern tooling</li>
  <li><a href="architecture.md">System Architecture</a> - Comprehensive system design with visual diagrams</li>
  <li><a href="backend-source-guide.md">Backend Source Guide</a> - Detailed navigation guide for the backend codebase</li>
</ul>
</div>

<div class="card">
<h3>🛠️ Development</h3>
<ul>
  <li><a href="dev-guidelines.md">Developer Guidelines</a> - Coding standards and contribution workflows</li>
  <li><a href="test-instructions.md">Test Instructions</a> - Complete guide to running and writing tests</li>
  <li><a href="test-log-levels.md">Test Log Level Control</a> - Configuration and control of logging during testing</li>
  <li><a href="ci-cd.md">CI/CD</a> - Continuous integration and deployment pipeline workflows</li>
  <li><a href="api-reference.md">API Reference</a> - Complete REST API documentation</li>
</ul>
</div>

<div class="card">
<h3>🧩 Modules & Integration</h3>
<ul>
  <li><a href="module-guide.md">Module Guide</a> - Creating and integrating new analysis modules</li>
  <li><a href="llm-integration.md">LLM Integration</a> - Large Language Model integration patterns</li>
  <li><a href="database-implementation.md">Database Implementation</a> - Database schema design and migration strategies</li>
</ul>
</div>

<div class="card">
<h3>📖 Resources & Help</h3>
<ul>
  <li><a href="faq.md">FAQ</a> - Frequently asked questions and troubleshooting</li>
  <li><a href="contributing-docs.md">Contributing to Documentation</a> - Guidelines for improving docs</li>
  <li><a href="how-to-use-docs.md">How to Use Docs</a> - Complete guide to navigating this documentation</li>
</ul>
</div>

</div>

---

## Project Overview

ReViewPoint is a comprehensive, modular platform designed to streamline and enhance the scientific paper review process through advanced automation and AI integration. The system combines modern backend services, an intuitive frontend interface, and seamless Large Language Model (LLM) integration to provide efficient, scalable, and extensible paper analysis capabilities.

### Key Features

- **🏗️ Modular Backend Architecture** - FastAPI-based services with PostgreSQL persistence and comprehensive API design
- **🔌 Pluggable Analysis System** - Extensible module framework for custom evaluation logic and analysis workflows  
- **🤖 Multi-Provider LLM Support** - Unified adapters for OpenAI, Anthropic, local models, and custom providers
- **🔄 Comprehensive CI/CD Pipeline** - Automated testing, quality assurance, and deployment workflows
- **⚡ Developer-Friendly Setup** - Streamlined onboarding process with modern tooling (PNPM, Docker, VS Code tasks)
- **🚀 Production-Ready Infrastructure** - Containerized deployment with monitoring and observability features
- **📡 Extensible API Design** - Versioned REST API with comprehensive OpenAPI documentation
- **💻 Modern Frontend Stack** - React-based UI with TypeScript, Tailwind CSS, and responsive design

### Technology Stack

| Component | Technologies |
|-----------|-------------|
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL, Alembic, PyJWT, Pydantic |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite, Zustand |
| **Database** | PostgreSQL (production), SQLite (development) |
| **Testing** | Pytest, Vitest, Playwright |
| **Documentation** | MkDocs, Markdown, Python-Markdown |
| **Deployment** | Docker, Docker Compose, GitHub Actions |
| **Development** | VS Code, PNPM, Ruff, Biome |

---

## Documentation Structure

This documentation is organized into comprehensive sections covering all aspects of the ReViewPoint platform:

### 🏛️ **System Architecture**
Complete architectural overview with visual diagrams, component interactions, and detailed file structure documentation for both backend and frontend codebases.

### 🛠️ **Development Environment** 
Comprehensive setup instructions, coding standards, testing methodologies, and CI/CD pipeline documentation for contributing to the project.

### 🔗 **Integration & Extensions**
Module creation workflows, LLM integration patterns, database design, and third-party service integration guides.

### 📚 **Reference & Resources**
API documentation, troubleshooting guides, contribution guidelines, and project maintenance documentation.

---

## Getting Started

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/reviewpoint.git
   cd reviewpoint
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Start development servers**
   ```bash
   # Option 1: SQLite (simplest)
   pnpm run dev
   
   # Option 2: PostgreSQL (recommended for production-like development)
   pnpm run dev:postgres
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Workflow

1. **Read the Setup Guide** - [Complete setup instructions](setup.md)
2. **Understand the Architecture** - [System architecture overview](architecture.md)
3. **Follow Development Guidelines** - [Coding standards and best practices](dev-guidelines.md)
4. **Run Tests** - [Testing instructions and strategies](test-instructions.md)
5. **Contribute** - [Documentation contribution guidelines](contributing-docs.md)

---

## Project Status

| Component | Status | Coverage | Quality |
|-----------|---------|----------|---------|
| **Backend** | ✅ Complete | 85%+ | Production Ready |
| **Frontend** | ✅ Complete | 80%+ | Production Ready |
| **Database** | ✅ Complete | 90%+ | Production Ready |
| **API** | ✅ Complete | 95%+ | Production Ready |
| **Documentation** | ✅ Complete | 100% | Comprehensive |
| **Testing** | ✅ Complete | 85%+ | Robust |
| **CI/CD** | ✅ Complete | 100% | Automated |
| **Deployment** | ✅ Complete | 90%+ | Docker Ready |

---

## Community and Support

- **📖 Documentation**: You're reading it! This comprehensive guide covers everything you need to know.
- **🐛 Issues**: Report bugs and request features on [GitHub Issues](https://github.com/your-org/reviewpoint/issues)
- **💡 Discussions**: Join community discussions on [GitHub Discussions](https://github.com/your-org/reviewpoint/discussions)
- **🔧 Contributing**: See [Contributing Guidelines](contributing-docs.md) for how to contribute to the project
- **📧 Support**: For support questions, please use GitHub Discussions or create an issue

---

## License

ReViewPoint is open source software licensed under the [MIT License](../../LICENSE).

---

> **Ready to dive in?** Start with the [Setup Guide](setup.md) to get your development environment running, then explore the [System Architecture](architecture.md) to understand how everything fits together.
