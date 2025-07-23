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

async function startBackendWithAutoSetup() {
  try {
    logger.info("Starting backend with auto-setup...");

    // Check if we should use PostgreSQL by reading the .env file
    const envPath = join(rootDir, "backend/config/.env");
    let usePostgres = false;

    try {
      const envContent = readFileSync(envPath, "utf8");
      usePostgres = envContent.includes("postgresql+asyncpg://");

      if (usePostgres) {
        logger.info("PostgreSQL detected in configuration");
      } else {
        logger.info("SQLite detected in configuration");
      }
    } catch (error) {
      logger.warn("Could not read .env file, assuming SQLite mode");
    }

    let backendEnv = { ...process.env };

    if (usePostgres) {
      logger.info("Ensuring PostgreSQL container is ready...");

      try {
        await ensurePostgresReady();
        logger.success("PostgreSQL container is ready!");

        // Set PostgreSQL environment variables for this session
        backendEnv = {
          ...process.env,
          REVIEWPOINT_DB_URL:
            "postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint",
          REVIEWPOINT_ENVIRONMENT: "dev",
          ENV_FILE: "config/.env",
        };

        logger.backend("Starting backend with PostgreSQL environment...");
      } catch (error) {
        logger.error(`PostgreSQL setup failed: ${error.message}`);
        logger.warn("Falling back to current configuration...");
      }
    } else {
      logger.backend("Starting backend with current configuration...");
    }

    // Start backend
    const host = process.env.HOST || "localhost";
    const backend = spawn(
      "hatch",
      [
        "run",
        "python",
        "-m",
        "uvicorn",
        "src.main:app",
        "--reload",
        "--host",
        host,
        "--port",
        "8000",
      ],
      {
        cwd: join(rootDir, "backend"),
        env: backendEnv,
        stdio: "inherit",
      },
    );

    logger.success(
      `Backend started successfully! ${usePostgres ? "(with PostgreSQL auto-setup)" : "(with current config)"}`,
    );

    backend.on("close", (code) => {
      logger.backend(`Backend process exited with code ${code}`);
      process.exit(code);
    });

    backend.on("error", (error) => {
      logger.error(`Backend process error: ${error.message}`);
      process.exit(1);
    });

    // Handle Ctrl+C gracefully
    process.on("SIGINT", () => {
      logger.info("Shutting down backend...");
      backend.kill("SIGINT");
      process.exit(0);
    });

    process.on("SIGTERM", () => {
      logger.info("Shutting down backend...");
      backend.kill("SIGTERM");
      process.exit(0);
    });
  } catch (error) {
    logger.error(`Failed to start backend: ${error.message}`);
    process.exit(1);
  }
}

startBackendWithAutoSetup().catch((error) => {
  logger.error(error.message);
  process.exit(1);
});
