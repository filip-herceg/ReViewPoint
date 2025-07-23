#!/usr/bin/env node

import { spawn } from "child_process";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { readFileSync } from "fs";
import { ensurePostgresReady } from "./start-postgres.js";
import logger from "./logger.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, "..");

async function runBackendTestsWithAutoSetup(testArgs = []) {
  try {
    logger.info("Preparing to run backend tests...");

    // Check if we should use PostgreSQL by reading the .env file
    const envPath = join(rootDir, "backend/config/.env");
    let usePostgres = false;

    try {
      const envContent = readFileSync(envPath, "utf8");
      usePostgres = envContent.includes("postgresql+asyncpg://");

      if (usePostgres) {
        logger.info("PostgreSQL detected in configuration");
      } else {
        logger.info("SQLite detected in configuration (tests will use SQLite)");
      }
    } catch (error) {
      logger.warn("Could not read .env file, tests will use SQLite");
    }

    let testEnv = {
      ...process.env,
      // Force tests to use SQLite for consistency and speed
      REVIEWPOINT_DB_URL: "sqlite+aiosqlite:///./test_reviewpoint.db",
      REVIEWPOINT_ENVIRONMENT: "test",
      FAST_TESTS: "1",
    };

    // For integration tests, we might want PostgreSQL
    const isIntegrationTest = testArgs.some(
      (arg) =>
        arg.includes("integration") ||
        arg.includes("slow") ||
        arg.includes("e2e"),
    );

    if (usePostgres && isIntegrationTest) {
      logger.info(
        "Integration tests detected - ensuring PostgreSQL container is ready...",
      );

      try {
        await ensurePostgresReady();
        logger.success("PostgreSQL container is ready for integration tests!");

        // Use PostgreSQL for integration tests
        testEnv.REVIEWPOINT_DB_URL =
          "postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint_test";
        delete testEnv.FAST_TESTS;

        logger.backend("Running tests with PostgreSQL environment...");
      } catch (error) {
        logger.error(`PostgreSQL setup failed: ${error.message}`);
        logger.warn("Falling back to SQLite for tests...");
      }
    } else {
      logger.backend("Running tests with SQLite (fast mode)...");
    }

    // Run tests
    const testCommand = testArgs.length > 0 ? testArgs : ["-m", "pytest", "-v"];
    const tests = spawn("hatch", ["run", "python", ...testCommand], {
      cwd: join(rootDir, "backend"),
      env: testEnv,
      stdio: "inherit",
    });

    tests.on("close", (code) => {
      if (code === 0) {
        logger.success("Tests completed successfully!");
      } else {
        logger.error(`Tests failed with exit code ${code}`);
      }
      process.exit(code);
    });

    tests.on("error", (error) => {
      logger.error(`Test process error: ${error.message}`);
      process.exit(1);
    });

    // Handle Ctrl+C gracefully
    process.on("SIGINT", () => {
      logger.info("Stopping tests...");
      tests.kill("SIGINT");
      process.exit(0);
    });
  } catch (error) {
    logger.error(`Failed to run tests: ${error.message}`);
    process.exit(1);
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
runBackendTestsWithAutoSetup(args).catch((error) => {
  logger.error(error.message);
  process.exit(1);
});
