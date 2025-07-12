#!/usr/bin/env tsx

/**
 * API Type Generation Script
 *
 * This script generates TypeScript types from the backend OpenAPI schema.
 * It uses openapi-typescript to convert the OpenAPI specification into
 * type-safe TypeScript interfaces and types.
 *
 * Usage:
 *   pnpm run generate:api-types
 *   or: tsx scripts/generate-api-types.ts
 *
 * Dependencies:
 *   - openapi-typescript: Core type generation
 *   - @apidevtools/swagger-parser: Schema validation
 *   - Backend OpenAPI schema at ../openapi-schema.json
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import SwaggerParser from "@apidevtools/swagger-parser";
import openapiTS from "openapi-typescript";

// Import our logger (using dynamic import for compatibility)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const PROJECT_ROOT = path.resolve(__dirname, "..");
const FRONTEND_ROOT = path.join(PROJECT_ROOT, "frontend");
const SCHEMA_PATH = path.join(PROJECT_ROOT, "frontend", "openapi-schema.json");
const OUTPUT_DIR = path.join(FRONTEND_ROOT, "src", "lib", "api", "generated");
const SCHEMA_OUTPUT = path.join(OUTPUT_DIR, "schema.ts");
const CLIENT_OUTPUT = path.join(OUTPUT_DIR, "client.ts");
const VALIDATORS_OUTPUT = path.join(OUTPUT_DIR, "validators.ts");
const README_OUTPUT = path.join(OUTPUT_DIR, "README.md");

/**
 * Logger utility for the generation script
 */
class GenerationLogger {
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

	debug(message: string, ...args: unknown[]): void {
		if (process.env.NODE_ENV === "development" || process.env.DEBUG) {
			this.log("DEBUG", message, ...args);
		}
	}
}

const logger = new GenerationLogger();

/**
 * Validate that the OpenAPI schema exists and is valid
 */
async function validateSchema(): Promise<any> {
	logger.info("🔍 Validating OpenAPI schema...");

	try {
		// Check if schema file exists
		await fs.access(SCHEMA_PATH);

		// Parse and validate the schema
		const schema = await SwaggerParser.validate(SCHEMA_PATH);

		logger.info("✅ OpenAPI schema validation successful");
		logger.debug("Schema info:", {
			title: (schema as any).info?.title,
			version: (schema as any).info?.version,
			pathsCount: Object.keys((schema as any).paths || {}).length,
			schemasCount: Object.keys((schema as any).components?.schemas || {})
				.length,
		});

		return schema;
	} catch (error) {
		if ((error as any).code === "ENOENT") {
			logger.error("❌ OpenAPI schema file not found at:", SCHEMA_PATH);
			logger.error(
				'💡 Run "pnpm run generate:openapi-schema" first to export the schema from backend',
			);
		} else {
			logger.error("❌ Schema validation failed:", error);
		}
		throw error;
	}
}

/**
 * Generate TypeScript types from OpenAPI schema
 */
async function generateTypes(): Promise<string> {
	logger.info("🔧 Generating TypeScript types...");

	try {
		const output = await openapiTS(SCHEMA_PATH, {
			exportType: true,
			additionalProperties: false,
			defaultNonNullable: true,
		});

		logger.info("✅ TypeScript types generated successfully");
		return output as unknown as string;
	} catch (error) {
		logger.error("❌ Type generation failed:", error);
		throw error;
	}
}

/**
 * Create the generated API client wrapper
 */
function createClientCode(): string {
	return `/**
 * Generated API Client
 * 
 * Type-safe API client generated from OpenAPI schema.
 * This file is auto-generated - do not edit manually.
 * 
 * @generated ${new Date().toISOString()}
 */

import createClient from 'openapi-fetch';
import type { paths } from './schema';

// Import logger with proper typing
const logger = await import('@/logger').then(m => m.logger || m.default);

/**
 * Type-safe API client instance
 * Configured with base URL from environment variables
 */
export const generatedApiClient = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Add request/response logging interceptor
 */
generatedApiClient.use({
  onRequest(req) {
    logger.debug('🔄 API Request:', {
      method: req.method,
      url: req.url,
      headers: req.headers,
    });
    return req;
  },
  
  onResponse(res) {
    logger.debug('✅ API Response:', {
      status: res.status,
      statusText: res.statusText,
      url: res.url,
    });
    return res;
  },
});

/**
 * Type-safe error handling utility
 */
export function isApiError(error: unknown): error is { message: string; status?: number } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as any).message === 'string'
  );
}

/**
 * Extract error message from API response
 */
export function getApiErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unknown API error occurred';
}
`;
}

/**
 * Create runtime validators
 */
function createValidatorsCode(): string {
	return `/**
 * Runtime Validators
 * 
 * Runtime validation helpers for API responses.
 * This file is auto-generated - do not edit manually.
 * 
 * @generated ${new Date().toISOString()}
 */

import type { components } from './schema';

// Import logger with proper typing
const logger = await import('@/logger').then(m => m.logger || m.default);

/**
 * Validate upload response structure
 */
export function validateUploadResponse(
  data: unknown
): data is components['schemas']['FileUploadResponse'] {
  try {
    if (!data || typeof data !== 'object') {
      logger.warn('Invalid upload response: not an object', data);
      return false;
    }
    
    const response = data as Record<string, unknown>;
    const isValid = 
      typeof response.filename === 'string' &&
      typeof response.url === 'string';
    
    if (!isValid) {
      logger.warn('Invalid upload response structure:', data);
    }
    
    return isValid;
  } catch (error) {
    logger.error('Upload response validation error:', error);
    return false;
  }
}

/**
 * Validate API error response structure
 */
export function validateApiError(
  data: unknown
): data is components['schemas']['ApiError'] {
  try {
    if (!data || typeof data !== 'object') {
      return false;
    }
    
    const error = data as Record<string, unknown>;
    return (
      typeof error.message === 'string' &&
      (error.status === undefined || typeof error.status === 'number') &&
      (error.type === undefined || typeof error.type === 'string')
    );
  } catch (error) {
    logger.error('API error validation error:', error);
    return false;
  }
}

/**
 * Generic response validator
 */
export function validateApiResponse<T>(
  data: unknown,
  validator: (data: unknown) => data is T
): data is T {
  return validator(data);
}

/**
 * Development-only runtime validation
 * Only runs validation in development mode for performance
 */
export function devValidate<T>(
  data: unknown,
  validator: (data: unknown) => data is T,
  errorMessage = 'Runtime validation failed'
): data is T {
  if (import.meta.env.DEV) {
    const isValid = validator(data);
    if (!isValid) {
      logger.warn(errorMessage, data);
    }
    return isValid;
  }
  return true; // Skip validation in production
}
`;
}

/**
 * Create README documentation
 */
function createReadmeContent(): string {
	return `# Generated API Types

This directory contains auto-generated TypeScript types and utilities from the backend OpenAPI schema.

**⚠️ DO NOT EDIT FILES IN THIS DIRECTORY MANUALLY**

All files are regenerated automatically when the backend schema changes.

## Files

- \`schema.ts\` - Generated TypeScript types from OpenAPI schema
- \`client.ts\` - Type-safe API client wrapper
- \`validators.ts\` - Runtime validation helpers
- \`README.md\` - This documentation file

## Usage

### Import Types

\`\`\`typescript
import type { components, paths } from '@/lib/api/generated/schema';

type User = components['schemas']['UserProfile'];
type UploadResponse = components['schemas']['FileUploadResponse'];
\`\`\`

### Use API Client

\`\`\`typescript
import { generatedApiClient } from '@/lib/api/generated/client';

// Type-safe API calls
const { data, error } = await generatedApiClient.GET('/api/v1/users/me');
if (error) {
  console.error('API error:', error);
} else {
  console.log('User data:', data); // Fully typed
}
\`\`\`

### Runtime Validation

\`\`\`typescript
import { validateUploadResponse, devValidate } from '@/lib/api/generated/validators';

// Development-only validation
if (devValidate(response, validateUploadResponse)) {
  // response is typed as FileUploadResponse
}
\`\`\`

## Regeneration

To regenerate these files after backend changes:

\`\`\`bash
# Export schema from backend
pnpm run generate:openapi-schema

# Generate TypeScript types
pnpm run generate:api-types

# Or run both at once
pnpm run generate:all
\`\`\`

## Generated: ${new Date().toISOString()}
`;
}

/**
 * Ensure output directory exists
 */
async function ensureOutputDir(): Promise<void> {
	logger.info("📁 Creating output directory...");

	try {
		await fs.mkdir(OUTPUT_DIR, { recursive: true });
		logger.info("✅ Output directory ready:", OUTPUT_DIR);
	} catch (error) {
		logger.error("❌ Failed to create output directory:", error);
		throw error;
	}
}

/**
 * Write generated files to disk
 */
async function writeFiles(typesOutput: string): Promise<void> {
	logger.info("💾 Writing generated files...");

	try {
		// Write all files in parallel
		await Promise.all([
			fs.writeFile(SCHEMA_OUTPUT, typesOutput, "utf-8"),
			fs.writeFile(CLIENT_OUTPUT, createClientCode(), "utf-8"),
			fs.writeFile(VALIDATORS_OUTPUT, createValidatorsCode(), "utf-8"),
			fs.writeFile(README_OUTPUT, createReadmeContent(), "utf-8"),
		]);

		logger.info("✅ Generated files written successfully:");
		logger.info(
			"  📄 Schema types:",
			path.relative(FRONTEND_ROOT, SCHEMA_OUTPUT),
		);
		logger.info(
			"  📄 API client:",
			path.relative(FRONTEND_ROOT, CLIENT_OUTPUT),
		);
		logger.info(
			"  📄 Validators:",
			path.relative(FRONTEND_ROOT, VALIDATORS_OUTPUT),
		);
		logger.info("  📄 README:", path.relative(FRONTEND_ROOT, README_OUTPUT));
	} catch (error) {
		logger.error("❌ Failed to write files:", error);
		throw error;
	}
}

/**
 * Main generation function
 */
async function generateApiTypes(): Promise<void> {
	const startTime = Date.now();

	try {
		logger.info("🚀 Starting API type generation...");

		// Validate input schema
		await validateSchema();

		// Generate TypeScript types
		const typesOutput = await generateTypes();

		// Ensure output directory exists
		await ensureOutputDir();

		// Write all generated files
		await writeFiles(typesOutput);

		const duration = Date.now() - startTime;
		logger.info(
			`🎉 API type generation completed successfully in ${duration}ms`,
		);
	} catch (error) {
		logger.error("❌ API type generation failed:", error);
		process.exit(1);
	}
}

/**
 * Main entry point
 */
async function main(): Promise<void> {
	try {
		await generateApiTypes();
	} catch (error) {
		if (error instanceof Error && error.message.includes("ENOENT")) {
			logger.error(
				'💡 Make sure to run "pnpm run generate:openapi-schema" first',
			);
		}
		process.exit(1);
	}
}

// Run if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
	main();
}

export { generateApiTypes };
