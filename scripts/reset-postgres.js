#!/usr/bin/env node

import { spawn } from "child_process";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import logger from "./logger.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, "..");

async function runCommand(command, args, description) {
  return new Promise((resolve, reject) => {
    logger.postgres(description);

    const process = spawn(command, args, {
      cwd: rootDir,
      stdio: "pipe",
      shell: true,
    });

    let output = "";
    process.stdout.on("data", (data) => {
      output += data.toString();
    });

    process.stderr.on("data", (data) => {
      output += data.toString();
    });

    process.on("close", (code) => {
      if (code === 0) {
        logger.success(`${description} - Success`);
        resolve();
      } else {
        logger.error(`${description} - Failed (exit code: ${code})`);
        logger.error(output);
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
  });
}

async function resetPostgres() {
  try {
    logger.warn(
      "WARNING: This will completely reset the PostgreSQL database and remove all data!",
    );

    // Stop and remove containers with volumes
    await runCommand(
      "docker",
      ["compose", "-f", "backend/deployment/docker-compose.yml", "down", "-v"],
      "Stopping containers and removing volumes...",
    );

    // Start fresh PostgreSQL container
    await runCommand(
      "docker",
      [
        "compose",
        "-f",
        "backend/deployment/docker-compose.yml",
        "up",
        "-d",
        "postgres",
      ],
      "Starting fresh PostgreSQL container...",
    );

    logger.success("PostgreSQL database has been completely reset! 🐘");
    logger.info(
      "You can now run your development tasks with a clean database.",
    );
  } catch (error) {
    logger.error(`Failed to reset PostgreSQL: ${error.message}`);
    process.exit(1);
  }
}

resetPostgres();
