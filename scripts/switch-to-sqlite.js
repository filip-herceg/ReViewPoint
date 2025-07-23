#!/usr/bin/env node

import { readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import logger from "./logger.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, "..");

function updateEnvToSQLite() {
  const envPath = join(rootDir, "backend/config/.env");

  try {
    let envContent = readFileSync(envPath, "utf8");

    // Replace PostgreSQL URL with SQLite URL
    const sqliteUrl = "sqlite+aiosqlite:///./reviewpoint_dev.db";
    envContent = envContent.replace(
      /^REVIEWPOINT_DB_URL=.*$/m,
      `REVIEWPOINT_DB_URL=${sqliteUrl}`,
    );

    writeFileSync(envPath, envContent, "utf8");
    logger.info("Updated .env to use SQLite");

    return sqliteUrl;
  } catch (error) {
    logger.warn(`Failed to update .env file: ${error.message}`);
    throw error;
  }
}

export function switchToSQLite() {
  updateEnvToSQLite();
  logger.success("Switched to SQLite database configuration");
}

// If this script is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    switchToSQLite();
    process.exit(0);
  } catch (error) {
    logger.error(`Failed: ${error.message}`);
    process.exit(1);
  }
}
