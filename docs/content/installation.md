# Get Started with ReViewPoint

> **Fresh Windows mac💡**Docker Note\*\*: Docker Desktop requires manual installation but isn't required for basic development (SQLite mode works without it).

---

## 🔍 **What Tools Get Installed? (Complete Transparency)**

The automated installer is completely transparent about what it installs:

### **Core Tools Installed via Chocolatey:**

| Tool             | Package  | Purpose                     | Disk Space |
| ---------------- | -------- | --------------------------- | ---------- |
| **Chocolatey**   | `choco`  | Package manager for Windows | ~50MB      |
| **Git**          | `git`    | Version control system      | ~300MB     |
| **Node.js 18+**  | `nodejs` | JavaScript runtime + npm    | ~200MB     |
| **Python 3.11+** | `python` | Backend runtime + pip       | ~150MB     |

### **Package Managers Installed via Native Tools:**

| Tool      | Install Method                      | Purpose                    | Size  |
| --------- | ----------------------------------- | -------------------------- | ----- |
| **pnpm**  | `npm install -g pnpm`               | Fast package manager       | ~20MB |
| **pipx**  | `python -m pip install --user pipx` | Python app installer       | ~10MB |
| **Hatch** | `pipx install hatch`                | Python environment manager | ~15MB |

### **Manual Installation Required:**

| Tool               | Why Manual?                                 | Required For                      |
| ------------------ | ------------------------------------------- | --------------------------------- |
| **Docker Desktop** | Large download, requires license acceptance | PostgreSQL development (optional) |

### **🛡️ Security & Privacy:**

- **All tools are official**: Downloaded from official sources (chocolatey.org, nodejs.org, python.org)
- **No data collection**: The installer only installs tools, no telemetry
- **PATH modifications**: Tools are added to Windows PATH for command-line access
- **Admin privileges**: Some installations may require administrator rights

### **📋 Before Installation Checklist:**

Before running the automated installer, you'll see a **complete list** of what will be installed:

```
📦 TOOLS THAT WILL BE INSTALLED:
  1. Chocolatey - Package manager for Windows
  2. Git - Version control system
  3. Node.js 18+ - JavaScript runtime
  4. pnpm - Fast package manager (via npm)
  5. Python 3.11+ - Backend runtime
  6. pipx - Python application installer
  7. Hatch - Python environment manager (via pipx)

⚠️  Docker Desktop - Requires MANUAL installation (guidance provided)
```

**You must confirm before any installation begins!**

---

## 🔒 **VS Code Task Safety System**

**All VS Code development tasks now check prerequisites first:**

### **Tasks with Prerequisite Checks:**

| Task Name                | Checks For     | Behavior on Failure                 |
| ------------------------ | -------------- | ----------------------------------- |
| **Start Backend**        | Node.js        | ❌ Stops with helpful error message |
| **Start Frontend**       | pnpm           | ❌ Stops with helpful error message |
| **Start Both Services**  | pnpm           | ❌ Stops with helpful error message |
| **Run Backend Tests**    | Node.js, hatch | ❌ Stops with helpful error message |
| **Install Dependencies** | pnpm, hatch    | ❌ Stops with helpful error message |
| **Generate API Types**   | pnpm           | ❌ Stops with helpful error message |

### **Error Message Examples:**

If you try to run a task without prerequisites:

```
❌ pnpm not found! Run "Setup Fresh Windows Machine" task first
💡 Or run: .\scripts\install-prerequisites.ps1
```

### **Success Message Examples:**

When prerequisites are found:

```
✅ Prerequisites OK, starting frontend...
```

**This ensures you can never accidentally run a task that will fail due to missing tools!**

---

## 🛠️ **Manual Installation (If Automatic Fails)**

**⏱️ Expected time: 15-20 minutes**et ReViewPoint running in just 3 steps!\*\*

## 🚀 **Quick Start for Fresh Windows Machines**

**⏱️ Total time: 5-10 minutes (fully automated)**

### Method 1: Automatic Setup (Recommended)

Perfect for **fresh Windows machines** or **professor grading scenarios**:

1. **Download the project:**

   ```powershell
   git clone https://github.com/filip-herceg/ReViewPoint.git
   cd ReViewPoint
   ```

2. **Run the automated installer:**

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/install-prerequisites.ps1
   ```

3. **Start development:**

   ```powershell
   pnpm run dev
   ```

**That's it!** The script automatically installs Git, Node.js, Python, pnpm, hatch, and provides Docker guidance.

### Method 2: VS Code Tasks (If VS Code is available)

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` → Type "Tasks: Run Task"
3. Select **"ReViewPoint: Setup Fresh Windows Machine"**
4. Wait for automatic installation to complete
5. Run **"ReViewPoint: Start Both (Backend + Frontend) - SQLite"**

---

## 🛠️ **What Gets Installed Automatically**

The automated installer handles all prerequisites:

| Tool               | Purpose                    | Auto-Installed |
| ------------------ | -------------------------- | -------------- |
| **Chocolatey**     | Package manager            | ✅             |
| **Git**            | Version control            | ✅             |
| **Node.js 18+**    | JavaScript runtime         | ✅             |
| **pnpm**           | Fast package manager       | ✅             |
| **Python 3.11+**   | Backend runtime            | ✅             |
| **pipx**           | Python app installer       | ✅             |
| **Hatch**          | Python environment manager | ✅             |
| **Docker Desktop** | Container platform         | ⚠️ Manual      |

💡 **Docker Note**: Docker Desktop requires manual installation but isn't required for basic development (SQLite mode works without it).

---

## � **Manual Installation (If Automatic Fails)**

**⏱️ Expected time: 15-20 minutes**

Install these tools in order. **Don't skip any steps!**

| #   | Tool               | Purpose              | Install Method                                                    | Verification       |
| --- | ------------------ | -------------------- | ----------------------------------------------------------------- | ------------------ |
| 1   | **Git**            | Version control      | [Download installer](https://git-scm.com/download/win)            | `git --version`    |
| 2   | **Node.js** (18+)  | JavaScript runtime   | [Download LTS](https://nodejs.org/)                               | `node --version`   |
| 3   | **pnpm**           | Fast package manager | `npm install -g pnpm`                                             | `pnpm --version`   |
| 4   | **Python** (3.11+) | Backend runtime      | [Download from python.org](https://python.org/downloads/)         | `python --version` |
| 5   | **pipx**           | Python app installer | `python -m pip install --user pipx`                               | `pipx --version`   |
| 6   | **Hatch**          | Python env manager   | `pipx install hatch`                                              | `hatch --version`  |
| 7   | **Docker Desktop** | Container platform   | [Download installer](https://docker.com/products/docker-desktop/) | `docker --version` |

### 🚨 **Critical Windows Notes:**

- **Python**: ✅ Check "Add Python to PATH" during installation
- **Docker Desktop**: ✅ Must be **running** (started) before proceeding
- **PowerShell**: ✅ Run commands in PowerShell (not Command Prompt)

---

## 🔍 **Step 2: Verify Installation**

**Run this VS Code task to check everything:**

1. Open VS Code in the project folder
2. Run task: **"ReViewPoint: Check PostgreSQL Prerequisites"**

Or manually verify with:

```powershell
# Check all tools are installed
git --version
node --version
pnpm --version
python --version
hatch --version
docker --version

# Critical: Check Docker is RUNNING
docker info
```

**❌ If any command fails**, go back to Step 1 and reinstall that tool.

---

## ⚡ **Step 3: Super Quick Start** (2 minutes)

**Once prerequisites are verified, get everything running:**

```bash
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint
pnpm run dev:postgres
```

**🎉 That's it!** Your ReViewPoint development environment is now running!

### **🌐 Access Your Application:**

- **📱 Main Application**: [http://localhost:5173](http://localhost:5173) ← **Start here!**
- **📚 This Documentation**: [http://127.0.0.1:8000/ReViewPoint/](http://127.0.0.1:8000/ReViewPoint/)
- **🔧 Backend API**: [http://localhost:8000](http://localhost:8000)
- **📖 API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## � **Alternative Installation Methods**

### **Method 1: VS Code Tasks** (Recommended for beginners)

**Step-by-step using VS Code interface:**

1. **Install Dependencies**:
   - Run task: **"ReViewPoint: Install Dependencies"**
   - ✅ Installs all project dependencies automatically

2. **Choose Database & Start**:
   - **PostgreSQL** (production-like): Run **"ReViewPoint: Start Both (Backend + Frontend) - PostgreSQL"**
   - **SQLite** (simpler): Run **"ReViewPoint: Start Both (Backend + Frontend) - SQLite"**

### **Method 2: Manual Commands**

```bash
# 1. Clone and navigate
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint

# 2. Install dependencies
pnpm install                    # Root dependencies
cd backend && hatch env create  # Backend Python environment
cd ../frontend && pnpm install  # Frontend dependencies
cd ..

# 3. Choose your setup:

# Option A: PostgreSQL (recommended)
pnpm run dev:postgres

# Option B: SQLite (simpler)
pnpm run dev
```

### **Method 3: Individual Components**

If you want to start backend and frontend separately:

```bash
# Terminal 1: Start Backend
pnpm run postgres:start  # Start PostgreSQL container
# Then run VS Code task: "ReViewPoint: Start Backend"

# Terminal 2: Start Frontend
# Run VS Code task: "ReViewPoint: Start Frontend"
```

---

## 📋 **Available VS Code Tasks**

**Essential tasks for development:**

### **🚀 Development Tasks**

| Task Name                          | Purpose                          | When to Use                 |
| ---------------------------------- | -------------------------------- | --------------------------- |
| **Install Dependencies**           | Install all project dependencies | First time setup            |
| **Start Both - PostgreSQL**        | Full stack with PostgreSQL       | Production-like development |
| **Start Both - SQLite**            | Full stack with SQLite           | Simple development          |
| **Start Backend**                  | Backend only                     | Backend development         |
| **Start Frontend**                 | Frontend only                    | Frontend development        |
| **Check PostgreSQL Prerequisites** | Verify Docker & tools            | Troubleshooting             |

### **🧪 Testing Tasks**

| Task Name                  | Purpose                         | Test Type             |
| -------------------------- | ------------------------------- | --------------------- |
| **Run All Backend Tests**  | Full backend test suite         | Comprehensive testing |
| **Run Fast Backend Tests** | Quick backend tests only        | Rapid feedback        |
| **Run Frontend Tests**     | Frontend unit tests             | Frontend validation   |
| **Run Frontend E2E Tests** | End-to-end browser tests        | Full user flows       |
| **Run All Tests**          | Everything (backend + frontend) | Complete validation   |

### **🔧 Utility Tasks**

| Task Name              | Purpose                          | Usage             |
| ---------------------- | -------------------------------- | ----------------- |
| **Lint Backend**       | Check Python code style          | Code quality      |
| **Format Backend**     | Auto-format Python code          | Code cleanup      |
| **Lint Frontend**      | Check TypeScript code style      | Code quality      |
| **Format Frontend**    | Auto-format TypeScript           | Code cleanup      |
| **Generate API Types** | Create TypeScript types from API | After API changes |
| **Clean All**          | Remove cache/build files         | Troubleshooting   |

### **🗄️ Database Tasks**

| Task Name                      | Purpose                   | When to Use           |
| ------------------------------ | ------------------------- | --------------------- |
| **Start PostgreSQL Container** | Start database only       | Database setup        |
| **Stop PostgreSQL Container**  | Stop database             | Cleanup               |
| **Run Database Migrations**    | Apply schema changes      | After pulling updates |
| **Switch to PostgreSQL**       | Change to PostgreSQL      | Production-like setup |
| **Switch to SQLite**           | Change to SQLite          | Simple setup          |
| **Reset PostgreSQL Database**  | Completely reset database | Clean slate           |

---

## ✅ **Verification Steps**

**After installation, verify everything works:**

### **1. Check Services are Running**

```bash
# Frontend should be accessible
curl http://localhost:5173

# Backend should respond
curl http://localhost:8000/health

# API docs should load
# Visit: http://localhost:8000/docs
```

### **2. Run Quick Tests**

```bash
# Run a quick test to verify setup
# Use VS Code task: "ReViewPoint: Run Fast Backend Tests"
# Use VS Code task: "ReViewPoint: Run Frontend Tests"
```

### **3. Check Database Connection**

- Backend logs should show successful database connection
- No error messages in terminal outputs

---

## 🐛 **Common Issues & Solutions**

### **Docker Issues**

```bash
# Problem: "docker: command not found"
# Solution: Install Docker Desktop and ensure it's running

# Problem: "Cannot connect to the Docker daemon"
# Solution: Start Docker Desktop application

# Problem: "docker info" fails
# Solution: Restart Docker Desktop, wait for it to fully start
```

### **Python/Hatch Issues**

```bash
# Problem: "hatch: command not found"
# Solution:
pipx install hatch
# Then restart terminal

# Problem: "Python version not found"
# Solution: Reinstall Python, check "Add to PATH"
```

### **Node.js/pnpm Issues**

```bash
# Problem: "pnpm: command not found"
# Solution:
npm install -g pnpm

# Problem: Permission errors on Windows
# Solution: Run PowerShell as Administrator
```

### **Port Conflicts**

```bash
# Problem: Port 5173 or 8000 already in use
# Solution: Kill existing processes:
npx kill-port 5173
npx kill-port 8000
```

---

## 🎯 **Next Steps**

**After successful installation:**

1. **Explore the API**: Visit <http://localhost:8000/docs>
2. **Check Documentation**: Browse to the [Developer Documentation](developer-overview.md)
3. **Run Tests**: Execute tests to ensure everything works
4. **Start Developing**: Read [Development Guidelines](resources/guidelines.md)

**Ready to contribute?** See our [Contributing Guide](resources/contributing.md).

---

## 📞 **Need Help?**

**If you encounter issues:**

1. **Check Prerequisites**: Run the "Check PostgreSQL Prerequisites" task
2. **Review Logs**: Look at terminal output for error messages
3. **Clean & Retry**: Run "Clean All" task and restart
4. **Ask for Help**: Create an issue on GitHub with your error message

**Most issues are caused by missing prerequisites or Docker not running!**

````

### **Option 2: Simple SQLite Setup**

**Best for**: Quick testing, no Docker needed

```bash
# Simpler setup with SQLite database
pnpm run dev
````

### **Option 3: Manual Step-by-Step**

**Best for**: Understanding the setup process

```bash
# 1. Install dependencies
pnpm run install

# 2. Choose your database option:

# Option A: PostgreSQL (production-like)
pnpm run postgres:start  # Starts PostgreSQL container
pnpm run db:migrate     # Runs database migrations

# Option B: SQLite (simple)
# Nothing needed - SQLite file created automatically

# 3. Start the development servers
pnpm run backend &      # Start FastAPI backend
pnpm run frontend       # Start Vite frontend
```

---

## ✅ **Verify Installation**

**Check that everything is working correctly:**

1. **📱 Main App**: [http://localhost:5173](http://localhost:5173) shows the ReViewPoint login page
2. **📚 Documentation**: [http://127.0.0.1:8000/ReViewPoint/](http://127.0.0.1:8000/ReViewPoint/) shows this documentation site
3. **🔧 Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs) shows Swagger documentation
4. **💚 Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) returns `{"status": "healthy"}`

---

## 🛠️ **VS Code Integration** (Recommended)

ReViewPoint includes **24 VS Code tasks** for streamlined development:

1. **Open ReViewPoint in VS Code**
2. **Press `Ctrl+Shift+P`** (Cmd+Shift+P on Mac)
3. **Type "Tasks: Run Task"**
4. **Choose from available tasks:**

| Task                               | Purpose                  |
| ---------------------------------- | ------------------------ |
| **Install Dependencies**           | One-command setup        |
| **Start Development (PostgreSQL)** | Full stack development   |
| **Start Development (SQLite)**     | Simple development       |
| **Run All Tests**                  | Backend + Frontend tests |
| **Format All Code**                | Code formatting          |

---

## 🎯 **Next Steps**

**Now that you're up and running:**

1. **📖 Read the [Developer Documentation](developer-overview.md)** - Understand the architecture
2. **🧪 Run the tests**: `pnpm run test:all` - Verify everything works
3. **🎨 Explore the code** - Check out `backend/src/` and `frontend/src/`
4. **🚀 Make your first change** - Follow the [Contributing Guide](resources/contributing.md)

---

## 🆘 **Troubleshooting**

### **Common Issues**

**Port conflicts:**

```bash
# Check what's using the ports
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port
lsof -i :5432  # PostgreSQL port

# Kill processes if needed
kill -9 <PID>
```

**Database connection issues:**

```bash
# Reset PostgreSQL
pnpm run postgres:stop
pnpm run postgres:start

# Or switch to SQLite
pnpm run db:sqlite
```

**Dependency issues:**

```bash
# Clean and reinstall everything
pnpm run clean
pnpm run install
```

**Python environment issues:**

```bash
# Reset Python environment
cd backend
rm -rf .hatch
hatch env create
```

### **Still having issues?**

1. **Check the [FAQ](resources/faq.md)** - Common problems and solutions
2. **Search [GitHub Issues](https://github.com/filip-herceg/ReViewPoint/issues)** - See if others had the same problem
3. **Create a new issue** - We're here to help!

---

## 🎉 **You're Ready!**

**Congratulations!** You now have a fully functional ReViewPoint development environment.

**What's running:**

- ✅ **Backend**: FastAPI server with hot reload
- ✅ **Frontend**: React app with Vite hot reload
- ✅ **Database**: PostgreSQL or SQLite
- ✅ **Tests**: Full test suite ready to run

**Start developing**: Check out the [Developer Documentation](developer-overview.md) to learn the codebase!

```bash
# Clone the repository
git clone https://github.com/filip-herceg/ReViewPoint.git
cd ReViewPoint

# Install dependencies
pnpm run install

# Start with PostgreSQL (auto-setup)
pnpm run dev:postgres
```

This will:

- Check for Docker availability
- Start PostgreSQL container automatically
- Run database migrations
- Start both backend and frontend services

## Manual Setup

If you prefer manual control over each step:

### 1. Install Dependencies

```bash
# Root dependencies
pnpm install

# Backend dependencies (Python)
cd backend
hatch env create
cd ..

# Frontend dependencies (Node.js)
cd frontend
pnpm install
cd ..
```

### 2. Database Setup

#### Option A: SQLite (Simple)

```bash
# Switch to SQLite mode
pnpm run db:sqlite

# Run migrations
cd backend
hatch run alembic upgrade head
cd ..
```

#### Option B: PostgreSQL (Recommended)

```bash
# Start PostgreSQL container
pnpm run postgres:start

# Run migrations
cd backend
hatch run alembic upgrade head
cd ..
```

### 3. Start Services

```bash
# Terminal 1: Start backend
cd backend
hatch run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
pnpm run dev
```

## Environment Configuration

### Backend Configuration

The backend uses environment variables from `backend/config/.env`:

```env
# Database URL (automatically set by scripts)
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db

# OR for PostgreSQL:
# REVIEWPOINT_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint

# Other settings
SECRET_KEY=your-secret-key
DEBUG=true
```

### Frontend Configuration

The frontend automatically connects to the backend API. No configuration needed for development.

## Verification

Once everything is running, verify the installation:

1. **Backend API**: Visit `http://localhost:8000/docs` for the FastAPI Swagger UI
2. **Frontend App**: Visit `http://localhost:3000` for the React application
3. **Health Check**: The frontend should successfully connect to the backend

## Common Issues

### Docker Not Found

If you see "Docker not found" but want to use PostgreSQL:

1. Install Docker Desktop
2. Ensure Docker is running
3. Run `pnpm run postgres:check` to verify

### Port Conflicts

Default ports:

- Backend: `8000`
- Frontend: `3000`
- PostgreSQL: `5432`

If these ports are busy, modify the configuration or stop conflicting services.

### Permission Issues

On Linux/macOS, you might need to run Docker commands with `sudo` or add your user to the Docker group.

## Development Workflow

### Running Tests

```bash
# Backend tests
pnpm run test:backend

# Frontend tests
pnpm run test:frontend

# All tests
pnpm run test
```

### Code Quality

```bash
# Lint and format backend
pnpm run lint:backend
pnpm run format:backend

# Lint and format frontend
pnpm run lint:frontend
pnpm run format:frontend
```

### Database Migrations

```bash
# Create new migration
cd backend
hatch run alembic revision --autogenerate -m "Description"

# Apply migrations
hatch run alembic upgrade head
```

## Next Steps

- Read the [Developer Overview](developer-overview.md) for architecture details
- Explore the [Backend Documentation](backend/index.md) for API details
- Check out the [Frontend Documentation](frontend/index.md) for UI components
- Review [Contributing Guidelines](resources/contributing.md) to start contributing

## Getting Help

- **Documentation**: Browse this documentation for detailed guides
- **Issues**: Report problems on GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
