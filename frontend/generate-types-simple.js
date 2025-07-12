/**
 * Simple API Type Generation Script
 *
 * This script generates TypeScript types from the backend OpenAPI schema.
 * Simplified version that focuses on getting types generated quickly.
 */

import fs from "node:fs/promises";
import path from "node:path";
import openapiTS from "openapi-typescript";

const SCHEMA_PATH = path.resolve("openapi-schema.json");
const OUTPUT_DIR = path.resolve("src/lib/api/generated");
const SCHEMA_OUTPUT = path.join(OUTPUT_DIR, "schema.ts");

async function generateTypes() {
	console.log("🚀 Starting API type generation...");

	try {
		// Ensure output directory exists
		await fs.mkdir(OUTPUT_DIR, { recursive: true });

		// Generate types
		console.log("🔧 Generating TypeScript types...");
		const output = await openapiTS(SCHEMA_PATH);

		// Write schema types
		await fs.writeFile(SCHEMA_OUTPUT, output);

		console.log("✅ Types generated successfully at:", SCHEMA_OUTPUT);
	} catch (error) {
		console.error("❌ Generation failed:", error);
		process.exit(1);
	}
}

generateTypes();
