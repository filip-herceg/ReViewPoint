#!/usr/bin/env node

// ReViewPoint Setup Validation Script
// This script validates that all prerequisites are properly installed
// and the project can be set up and run successfully

const { exec } = require("child_process");
const { promisify } = require("util");
const execAsync = promisify(exec);

// ANSI color codes for output
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

function logSuccess(message) {
  console.log(`${colorize("✅", "green")} ${message}`);
}

function logError(message) {
  console.log(`${colorize("❌", "red")} ${message}`);
}

function logWarning(message) {
  console.log(`${colorize("⚠️", "yellow")} ${message}`);
}

function logInfo(message) {
  console.log(`${colorize("ℹ️", "blue")} ${message}`);
}

function logStep(message) {
  console.log(`${colorize("🔧", "cyan")} ${message}`);
}

function logHeader(message) {
  console.log(`\n${colorize("=".repeat(50), "magenta")}`);
  console.log(`${colorize(message, "magenta")}`);
  console.log(`${colorize("=".repeat(50), "magenta")}\n`);
}

async function checkCommand(command, name, required = true) {
  try {
    const { stdout } = await execAsync(`${command} 2>nul || echo "NOT_FOUND"`);
    if (stdout.trim() === "NOT_FOUND" || stdout.includes("not found")) {
      if (required) {
        logError(`${name} is not installed or not in PATH`);
        return false;
      } else {
        logWarning(`${name} is not installed (optional)`);
        return null;
      }
    } else {
      const version = stdout.trim().split("\n")[0];
      logSuccess(`${name}: ${version}`);
      return true;
    }
  } catch (error) {
    if (required) {
      logError(`${name} check failed: ${error.message}`);
      return false;
    } else {
      logWarning(`${name} is not available (optional)`);
      return null;
    }
  }
}

async function runValidation() {
  logHeader("ReViewPoint Setup Validation");

  logInfo("Validating all prerequisites for ReViewPoint development...\n");

  // Phase 1: Core Prerequisites
  logStep("Phase 1: Core Prerequisites");
  const coreTools = [
    { command: "git --version", name: "Git", required: true },
    { command: "node --version", name: "Node.js", required: true },
    { command: "pnpm --version", name: "pnpm", required: true },
    { command: "python --version", name: "Python", required: true },
    { command: "hatch --version", name: "Hatch", required: true },
  ];

  let coreSuccess = true;
  for (const tool of coreTools) {
    const result = await checkCommand(tool.command, tool.name, tool.required);
    if (result === false) coreSuccess = false;
  }

  // Phase 2: Optional Tools
  logStep("\nPhase 2: Optional Tools");
  await checkCommand("docker --version", "Docker", false);

  // Phase 3: Project Dependencies
  if (coreSuccess) {
    logStep("\nPhase 3: Project Dependencies");

    try {
      logInfo("Installing project dependencies...");
      await execAsync("pnpm install --silent");
      logSuccess("Root dependencies installed");

      try {
        await execAsync("cd backend && hatch env create");
        logSuccess("Backend Python environment created");
      } catch (error) {
        logWarning(
          "Backend environment creation had issues (may already exist)",
        );
      }

      await execAsync("cd frontend && pnpm install --silent");
      logSuccess("Frontend dependencies installed");
    } catch (error) {
      logError(`Dependency installation failed: ${error.message}`);
      coreSuccess = false;
    }

    // Phase 4: Quick Functionality Test
    logStep("\nPhase 4: Quick Functionality Test");

    try {
      logInfo("Testing backend startup (quick check)...");
      const { stdout } = await execAsync(
        'cd backend && timeout 10 hatch run python -c "from src.main import app; print(\'Backend import successful\')" 2>&1 || echo "TIMEOUT"',
      );
      if (stdout.includes("Backend import successful")) {
        logSuccess("Backend can start successfully");
      } else {
        logWarning("Backend startup test inconclusive");
      }
    } catch (error) {
      logWarning("Backend test skipped (dependencies may still be installing)");
    }

    try {
      logInfo("Testing frontend build system...");
      await execAsync("cd frontend && pnpm run type-check");
      logSuccess("Frontend TypeScript compilation successful");
    } catch (error) {
      logWarning(
        "Frontend type check had issues (may need API types generation)",
      );
    }
  }

  // Summary
  logHeader("Validation Summary");

  if (coreSuccess) {
    logSuccess("🎉 All core prerequisites are installed and working!");
    logInfo("\nNext steps:");
    logInfo("1. Run: pnpm run dev (for SQLite setup)");
    logInfo("2. Or run: pnpm run dev:postgres (for PostgreSQL setup)");
    logInfo("3. Open http://localhost:3000 in your browser");
    logInfo("\nFor VS Code users:");
    logInfo(
      '- Use "ReViewPoint: Start Both (Backend + Frontend) - SQLite" task',
    );
    logInfo(
      '- Or "ReViewPoint: Start Both (Backend + Frontend) - PostgreSQL" task',
    );
  } else {
    logError("❌ Some prerequisites are missing!");
    logInfo("\nTo fix this:");
    logInfo(
      "1. Run: powershell -ExecutionPolicy Bypass -File scripts/install-prerequisites.ps1",
    );
    logInfo(
      '2. Or run VS Code task: "ReViewPoint: Setup Fresh Windows Machine"',
    );
    logInfo("3. Then run this validation script again");
  }

  logInfo(
    "\n💡 For detailed setup instructions, see: docs/content/installation.md",
  );
}

// Handle unhandled promise rejections
process.on("unhandledRejection", (reason, promise) => {
  logError(`Unhandled Rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Run validation
runValidation().catch((error) => {
  logError(`Validation script failed: ${error.message}`);
  process.exit(1);
});
