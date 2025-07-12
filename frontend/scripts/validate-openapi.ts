#!/usr/bin/env tsx
/**
 * OpenAPI Schema Validation Script
 *
 * This script validates the exported OpenAPI schema for completeness
 * and ensures it has all the required components for type generation.
 *
 * Usage:
 *   pnpm run validate:api-schema
 *   or: tsx scripts/validate-openapi.ts
 */

import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import SwaggerParser from "@apidevtools/swagger-parser";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, "..");
const SCHEMA_PATH = path.join(PROJECT_ROOT, "frontend", "openapi-schema.json");

/**
 * Logger utility for validation script
 */
class ValidationLogger {
  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private log(level: string, message: string, ...args: unknown[]): void {
    const timestamp = this.formatTimestamp();
    console.log(`[${timestamp}] [${level}] ${message}`, ...args);
  }

  info(message: string, ...args: unknown[]): void {
    this.log("INFO", message, ...args);
  }

  warn(message: string, ...args: unknown[]): void {
    this.log("WARN", message, ...args);
  }

  error(message: string, ...args: unknown[]): void {
    this.log("ERROR", message, ...args);
  }

  success(message: string, ...args: unknown[]): void {
    this.log("SUCCESS", `✅ ${message}`, ...args);
  }
}

const logger = new ValidationLogger();

/**
 * Expected schemas that should be present in the OpenAPI spec
 */
const EXPECTED_SCHEMAS = [
  "UserProfile",
  "UserCreateRequest",
  "UserListResponse",
  "FileSchema",
  "ApiError",
  "ApiResponse",
  "MessageResponse",
] as const;

/**
 * Expected API endpoints that should be present
 */
const EXPECTED_ENDPOINTS = [
  "/api/v1/auth/login",
  "/api/v1/auth/register",
  "/api/v1/users/me",
  "/api/v1/uploads/",
  "/api/v1/health",
] as const;

/**
 * Validation result interface
 */
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  stats: {
    schemasCount: number;
    pathsCount: number;
    missingSchemas: string[];
    missingEndpoints: string[];
  };
}

/**
 * Validate OpenAPI schema structure and completeness
 */
async function validateOpenAPISchema(): Promise<ValidationResult> {
  const result: ValidationResult = {
    isValid: true,
    errors: [],
    warnings: [],
    stats: {
      schemasCount: 0,
      pathsCount: 0,
      missingSchemas: [],
      missingEndpoints: [],
    },
  };

  try {
    logger.info("🔍 Loading OpenAPI schema...");

    // Check if file exists
    try {
      await fs.access(SCHEMA_PATH);
    } catch (error) {
      result.errors.push(`Schema file not found: ${SCHEMA_PATH}`);
      result.isValid = false;
      return result;
    }

    // Parse and validate schema
    const schema = await SwaggerParser.validate(SCHEMA_PATH);
    const typedSchema = schema as any;

    logger.info("📊 Analyzing schema structure...");

    // Basic structure validation
    if (!typedSchema.openapi) {
      result.errors.push("Missing openapi version field");
      result.isValid = false;
    }

    if (!typedSchema.info) {
      result.errors.push("Missing info section");
      result.isValid = false;
    }

    if (!typedSchema.paths) {
      result.errors.push("Missing paths section");
      result.isValid = false;
    }

    if (!typedSchema.components?.schemas) {
      result.errors.push("Missing components.schemas section");
      result.isValid = false;
    }

    // Count schemas and paths
    const schemas = typedSchema.components?.schemas || {};
    const paths = typedSchema.paths || {};

    result.stats.schemasCount = Object.keys(schemas).length;
    result.stats.pathsCount = Object.keys(paths).length;

    // Check for expected schemas
    for (const expectedSchema of EXPECTED_SCHEMAS) {
      if (!schemas[expectedSchema]) {
        result.stats.missingSchemas.push(expectedSchema);
        result.warnings.push(`Missing expected schema: ${expectedSchema}`);
      }
    }

    // Check for expected endpoints
    for (const expectedEndpoint of EXPECTED_ENDPOINTS) {
      if (!paths[expectedEndpoint]) {
        result.stats.missingEndpoints.push(expectedEndpoint);
        result.warnings.push(`Missing expected endpoint: ${expectedEndpoint}`);
      }
    }

    // Additional validation checks
    if (result.stats.schemasCount === 0) {
      result.errors.push("No schemas found in OpenAPI specification");
      result.isValid = false;
    }

    if (result.stats.pathsCount === 0) {
      result.errors.push("No paths found in OpenAPI specification");
      result.isValid = false;
    }

    // Check schema quality
    for (const [schemaName, schemaSpec] of Object.entries(schemas)) {
      const typedSchemaSpec = schemaSpec as any;

      if (
        !typedSchemaSpec.type &&
        !typedSchemaSpec.properties &&
        !typedSchemaSpec.allOf
      ) {
        result.warnings.push(`Schema ${schemaName} appears to be incomplete`);
      }
    }

    logger.info("🎯 Schema validation completed");

    return result;
  } catch (error) {
    result.errors.push(`Schema validation failed: ${error}`);
    result.isValid = false;
    return result;
  }
}

/**
 * Print validation results
 */
function printValidationResults(result: ValidationResult): void {
  logger.info("📋 Validation Results Summary:");
  logger.info(`📊 Schemas found: ${result.stats.schemasCount}`);
  logger.info(`📊 Paths found: ${result.stats.pathsCount}`);

  if (result.errors.length > 0) {
    logger.error("❌ Errors found:");
    for (const error of result.errors) {
      logger.error(`  • ${error}`);
    }
  }

  if (result.warnings.length > 0) {
    logger.warn("⚠️  Warnings:");
    for (const warning of result.warnings) {
      logger.warn(`  • ${warning}`);
    }
  }

  if (result.stats.missingSchemas.length > 0) {
    logger.warn("Missing expected schemas:");
    for (const schema of result.stats.missingSchemas) {
      logger.warn(`  • ${schema}`);
    }
  }

  if (result.stats.missingEndpoints.length > 0) {
    logger.warn("Missing expected endpoints:");
    for (const endpoint of result.stats.missingEndpoints) {
      logger.warn(`  • ${endpoint}`);
    }
  }

  if (result.isValid && result.warnings.length === 0) {
    logger.success("OpenAPI schema validation passed with no issues!");
  } else if (result.isValid) {
    logger.success("OpenAPI schema validation passed with warnings");
  } else {
    logger.error("❌ OpenAPI schema validation failed");
  }
}

/**
 * Main validation function
 */
async function main(): Promise<void> {
  try {
    logger.info("🚀 Starting OpenAPI schema validation...");

    const result = await validateOpenAPISchema();
    printValidationResults(result);

    // Exit with appropriate code
    if (!result.isValid) {
      process.exit(1);
    }

    // Exit with warning code if there are warnings
    if (result.warnings.length > 0) {
      process.exit(2);
    }

    logger.success("🎉 Validation completed successfully");
  } catch (error) {
    logger.error("❌ Validation script failed:", error);
    process.exit(1);
  }
}

// Run if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { validateOpenAPISchema };
