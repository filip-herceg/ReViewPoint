# ReViewPoint

[![Docs Build](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml/badge.svg "Docs Build Status")](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml)
[![Lint Status](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml/badge.svg?label=lint "Lint Status")](https://github.com/filip-herceg/ReViewPoint/actions/workflows/docs.yaml)
![Test Coverage](docs/content/images/coverage.svg "Test Coverage Badge")

> **Modular, scalable, and LLM-powered platform for scientific paper review.**

ReViewPoint empowers development teams with intuitive tools that make code review efficient, comprehensive, and collaborative. Built for researchers, reviewers, and developers who want to automate, accelerate, and improve the quality of scientific paper review workflows.

---

## 🎬 **Project Tour**

<!-- � **Video Tour** (Coming Soon)

Get a quick overview of ReViewPoint's features and capabilities in this guided tour.

[Watch Video Tour →](link-to-video)

--- -->

*📹 Video tour coming soon - will showcase the complete ReViewPoint workflow*

---

## 🚀 **Quick Start**

### **⚡ Get Running in Under 30 Minutes**

**For fresh Windows machines - 100% automated with safety checks:**

```powershell
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint
powershell -ExecutionPolicy Bypass -File scripts/install-prerequisites.ps1
```

**For other platforms or existing environments:**

```bash
# Clone and start everything
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint

# Option A: SQLite (Simple, no containers)
pnpm run dev

# Option B: PostgreSQL (Production-like, auto-setup)
pnpm run dev:postgres
```

**🌐 Access Your Running Application:**

- **📱 Main Application**: [http://localhost:5173](http://localhost:5173)
- **📚 Documentation Site**: [http://127.0.0.1:8001/ReViewPoint/](http://127.0.0.1:8001/ReViewPoint/)
- **🔧 Backend API**: [http://localhost:8000](http://localhost:8000)
- **📖 API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

**🎯 [Complete Installation Guide →](https://filip-herceg.github.io/ReViewPoint/installation/)**

---

## 🌐 **📚 Online Documentation**

> **🔥 Want to explore ReViewPoint without installing? Check out our comprehensive online documentation!**

<div align="center">

### **🚀 [https://filip-herceg.github.io/ReViewPoint](https://filip-herceg.github.io/ReViewPoint)**

**📖 Browse the full documentation site • 🧭 Interactive guides • 📊 Architecture details**

*Always up-to-date with the latest features and developments*

</div>

---

## 🌟 **What is ReViewPoint?**

ReViewPoint is a **production-ready platform** that streamlines scientific paper review through:

### **🔬 Core Capabilities**

- **AI-Powered Analysis** - LLM integration for automated paper evaluation
- **Secure File Management** - Robust PDF upload and processing
- **User Management** - Complete authentication and authorization system
- **Modular Architecture** - Extensible design for custom analysis modules
- **Developer Experience** - Comprehensive tooling and VS Code integration

### **🏆 Production Highlights**

| Component         | Technology             | Status                    |
| ----------------- | ---------------------- | ------------------------- |
| **Backend**       | FastAPI + Python 3.11+ | ✅ **86%+ test coverage** |
| **Frontend**      | React 18 + TypeScript  | ✅ **80%+ test coverage** |
| **Database**      | PostgreSQL/SQLite      | ✅ **Production ready**   |
| **CI/CD**         | GitHub Actions         | ✅ **Automated pipeline** |

| **Documentation** | MkDocs Material        | ✅ **968+ pages**         |

---

## 🎯 **Vision & Mission**

### **Our Vision**

ReViewPoint envisions becoming the **premier platform for collaborative code review** that transforms how development teams work together, creating an environment where code quality, team collaboration, and project transparency are seamlessly integrated.

### **Our Mission**

**To empower development teams with intuitive tools that make code review efficient, comprehensive, and collaborative.**

We believe great software is built through:

- **Collaborative Review Processes** - Multiple perspectives lead to better code
- **Transparent Communication** - Clear feedback loops and decision tracking  
- **Quality-Driven Development** - Built-in tools that promote best practices
- **Inclusive Team Dynamics** - Accessible interfaces for all skill levels

**📖 [Full Vision & Mission →](https://filip-herceg.github.io/ReViewPoint/vision-mission-goals/)**

---

## 📚 **Essential Documentation**

### **🎯 Getting Started**

<div align="center">

| 🚀 **Quick Start** | 👩‍💻 **For Developers** | 📖 **Resources** | ℹ️ **About** |
|---|---|---|---|
| Get running in under 30 minutes | Technical docs & guides | Guidelines, API, FAQ | Vision, status, roadmap |
| [Installation Guide →](https://filip-herceg.github.io/ReViewPoint/installation/) | [Developer Docs →](https://filip-herceg.github.io/ReViewPoint/developer-overview/) | [Browse Resources →](https://filip-herceg.github.io/ReViewPoint/resources/guidelines/) | [Project Overview →](https://filip-herceg.github.io/ReViewPoint/vision-mission-goals/) |

</div>

### **🔧 Key Resources**

- **📘 [Complete Documentation](https://filip-herceg.github.io/ReViewPoint/)** - Full documentation site
- **🏗️ [System Architecture](https://filip-herceg.github.io/ReViewPoint/developer-overview/)** - Technical architecture and design
- **🧩 [Plugins Guide](https://filip-herceg.github.io/ReViewPoint/plugins/)** - Modular plugin ecosystem
- **📊 [Current Status](https://filip-herceg.github.io/ReViewPoint/current-status/)** - Development progress and roadmap
- **🛠️ [Developer Guidelines](https://filip-herceg.github.io/ReViewPoint/resources/guidelines/)** - Coding standards and workflow

---

## 🏗️ **System Architecture**

### **Technology Stack**

- **Frontend:** React 18 + TypeScript + Vite + TailwindCSS
- **Backend:** FastAPI + Python 3.11+ + async SQLAlchemy  
- **Database:** PostgreSQL (production) / SQLite (development)
- **LLM Integration:** Pluggable adapters (OpenAI, vLLM), prompt templating
- **Storage:** File upload with validation and metadata management
- **DevOps:** Docker, GitHub Actions CI/CD, automated testing

### **Key Features**

✅ **Async Operations** - Full async/await support throughout  
✅ **Type Safety** - Complete TypeScript coverage, Pydantic validation  
✅ **Security** - JWT authentication, rate limiting, comprehensive error handling  
✅ **Testing** - 86%+ backend coverage, 80%+ frontend coverage  
✅ **Documentation** - Auto-generated API docs, comprehensive guides  
✅ **Developer Experience** - VS Code integration, hot reload, automated setup  

---

## 🛠️ **Development**

### **🔧 Developer Experience**

- **VS Code Integration**: Pre-configured tasks for all operations
- **Package Management**: PNPM (frontend) + Hatch (backend)  
- **Hot Reload**: Instant development feedback
- **Automated Setup**: One-command PostgreSQL setup with Docker
- **Quality Tools**: Black, Ruff, Biome, comprehensive linting

### **🧪 Testing**

```bash
# Run all tests
pnpm run test:all

# Backend tests only
pnpm run test:backend

# Frontend tests only  
pnpm run test:frontend

# With coverage
pnpm run test:coverage
```

### **📋 Development Standards**

| Language       | Formatter  | Linter    | Type Checker |
| -------------- | ---------- | --------- | ------------ |
| **Python**     | `black`    | `ruff`    | `mypy`       |
| **TypeScript** | `Biome`    | `Biome`   | `tsc`        |
| **Markdown**   | `Prettier` | `markdownlint` | -      |

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### **🎯 Quick Contribution Guide**

1. **📖 Read the [Contributing Guidelines](https://filip-herceg.github.io/ReViewPoint/resources/contributing/)**
2. **🍴 Fork** the repository on GitHub
3. **📥 Clone** your fork locally
4. **🛠️ Install** dependencies: `pnpm install`
5. **🌿 Create** a feature branch: `git checkout -b feature/amazing-feature`
6. **✍️ Write** code and tests
7. **✅ Test** your changes: `pnpm run test:all`
8. **📤 Push** and open a Pull Request

### **💡 Contribution Areas**

- 🐛 **Bug fixes** and performance improvements
- ✨ **New features** and enhancements  
- 📝 **Documentation** improvements
- 🧩 **Plugin development** for analysis modules
- 🧪 **Testing** and quality assurance
- 🎨 **UI/UX** improvements

---

## 📊 **Project Status**

### **🚧 Current Development Phase: Beta**

- **Backend**: Production-ready core with 135+ tests
- **Frontend**: Active development, foundation complete
- **Documentation**: Comprehensive (968+ pages)
- **CI/CD**: Fully automated pipeline
- **Plugins**: Modular architecture with sample plugins

### **🔄 Recent Updates**

- ✅ Complete plugin documentation system
- ✅ Enhanced VS Code task integration
- ✅ Automated PostgreSQL setup with Docker
- ✅ Comprehensive testing infrastructure
- ✅ Production-ready authentication system

**📈 [Full Status Report →](https://filip-herceg.github.io/ReViewPoint/current-status/)**

---

## 🔗 **Links & Resourcs**

### **📚 Documentation**

- **🏠 [Main Documentation](https://filip-herceg.github.io/ReViewPoint/)** - Complete documentation site
- **📖 [API Reference](https://filip-herceg.github.io/ReViewPoint/resources/api-reference/)** - Full API documentation
- **❓ [FAQ](https://filip-herceg.github.io/ReViewPoint/resources/faq/)** - Common questions & troubleshooting

### **🛠️ Development**

- **🐛 [Issues](https://github.com/filip-herceg/ReViewPoint/issues)** - Report bugs & request features
- **🔄 [Pull Requests](https://github.com/filip-herceg/ReViewPoint/pulls)** - View active contributions
- **📋 [Projects](https://github.com/filip-herceg/ReViewPoint/projects)** - Development roadmap

### **🌐 Community**

- **💬 [Discussions](https://github.com/filip-herceg/ReViewPoint/discussions)** - Community Q&A
- **📧 [Contact](mailto:contact@reviewpoint.dev)** - Direct communication

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

[🚀 Get Started](https://filip-herceg.github.io/ReViewPoint/installation/) | [📖 Docs](https://filip-herceg.github.io/ReViewPoint/) | [🤝 Contribute](https://filip-herceg.github.io/ReViewPoint/resources/contributing/)

</div>
