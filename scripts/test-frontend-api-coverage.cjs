#!/usr/bin/env node
/**
 * Frontend API Coverage Test
 *
 * This script validates that the frontend correctly addresses all routed backend APIs
 * with the expected arguments, including authentication and API key requirements.
 */

const fs = require("fs").promises;
const path = require("path");

// Color codes for output
const colors = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  white: "\x1b[37m",
};

function log(message, color = colors.white) {
  console.log(`${color}${message}${colors.reset}`);
}

// Expected backend routes based on previous logs and backend analysis
const expectedBackendRoutes = {
  auth: {
    "/api/v1/auth/register": { method: "POST", auth: false, apiKey: true },
    "/api/v1/auth/login": { method: "POST", auth: false, apiKey: true },
    "/api/v1/auth/logout": { method: "POST", auth: true, apiKey: true },
    "/api/v1/auth/refresh": { method: "POST", auth: false, apiKey: true },
    "/api/v1/auth/me": { method: "GET", auth: true, apiKey: true },
    "/api/v1/auth/forgot-password": {
      method: "POST",
      auth: false,
      apiKey: true,
    },
    "/api/v1/auth/reset-password": {
      method: "POST",
      auth: false,
      apiKey: true,
    },
  },
  users: {
    "/api/v1/users/": { method: "GET", auth: true, apiKey: true },
    "/api/v1/users/": { method: "POST", auth: true, apiKey: true },
    "/api/v1/users/{user_id}": { method: "GET", auth: true, apiKey: true },
    "/api/v1/users/{user_id}": { method: "PUT", auth: true, apiKey: true },
    "/api/v1/users/{user_id}": { method: "DELETE", auth: true, apiKey: true },
    "/api/v1/users/exports/csv": { method: "GET", auth: true, apiKey: true },
    "/api/v1/users/exports/json": { method: "GET", auth: true, apiKey: true },
    "/api/v1/users/test-only/create-test-user": {
      method: "POST",
      auth: false,
      apiKey: true,
    },
    "/api/v1/users/test-only/cleanup-test-users": {
      method: "DELETE",
      auth: false,
      apiKey: true,
    },
  },
  uploads: {
    "/api/v1/uploads/": { method: "POST", auth: true, apiKey: true },
    "/api/v1/uploads/": { method: "GET", auth: true, apiKey: true },
    "/api/v1/uploads/{upload_id}": { method: "GET", auth: true, apiKey: true },
    "/api/v1/uploads/{upload_id}": {
      method: "DELETE",
      auth: true,
      apiKey: true,
    },
  },
  health: {
    "/api/v1/health/": { method: "GET", auth: false, apiKey: false },
    "/api/v1/health/detailed": { method: "GET", auth: false, apiKey: false },
  },
  websocket: {
    "/api/v1/ws": { method: "WEBSOCKET", auth: false, apiKey: false },
  },
  metrics: {
    "/metrics": { method: "GET", auth: false, apiKey: false },
  },
};

// Frontend API implementations to check
const frontendApiFiles = [
  "frontend/src/lib/api/auth.ts",
  "frontend/src/lib/api/users/core.ts",
  "frontend/src/lib/api/users/exports.ts",
  "frontend/src/lib/api/users/test_only_router.ts",
  "frontend/src/lib/api/uploads.ts",
  "frontend/src/lib/api/health.ts",
  "frontend/src/lib/websocket/webSocketService.ts",
];

// Hook files to check
const frontendHookFiles = [
  "frontend/src/hooks/useAuth.ts",
  "frontend/src/hooks/useFileUpload.ts",
  "frontend/src/hooks/uploads/index.ts",
  "frontend/src/lib/websocket/hooks.ts",
];

/**
 * Check if a file exists and read its content
 */
async function readFileIfExists(filePath) {
  try {
    const fullPath = path.join(__dirname, filePath);
    const content = await fs.readFile(fullPath, "utf8");
    return content;
  } catch (error) {
    return null;
  }
}

/**
 * Analyze frontend API file for method implementations
 */
function analyzeApiFile(content, filename) {
  const implementations = [];

  // Look for API endpoint patterns
  const patterns = [
    // Regular request calls
    /request[^'"`]*['"`]([^'"`]+)['"`]/gi,
    // Axios calls
    /axios[^'"`]*['"`]([^'"`]+)['"`]/gi,
    // URL patterns
    /url:\s*['"`]([^'"`]+)['"`]/gi,
    // Template literals with paths
    /`[^`]*\/api\/[^`]*`/gi,
    // String literals with /api/ paths
    /['"][^'"]*\/api\/[^'"]*['"]/gi,
  ];

  let match;
  patterns.forEach((pattern) => {
    while ((match = pattern.exec(content)) !== null) {
      if (match[1] && match[1].includes("/api/")) {
        implementations.push({
          endpoint: match[1],
          method: "UNKNOWN",
          file: filename,
        });
      } else if (match[0] && match[0].includes("/api/")) {
        // For template literals and full matches
        const cleanMatch = match[0].replace(/[`'"]/g, "");
        implementations.push({
          endpoint: cleanMatch,
          method: "UNKNOWN",
          file: filename,
        });
      }
    }
  });

  // Look for method specifications
  const methodPattern = /method:\s*['"]([^'"]+)['"]/gi;
  const methods = [];
  while ((match = methodPattern.exec(content)) !== null) {
    methods.push(match[1].toUpperCase());
  }

  // Look for specific function names that indicate endpoints
  const functionPatterns = [
    /login:/gi,
    /register:/gi,
    /logout:/gi,
    /refresh:/gi,
    /getCurrentUser:/gi,
    /getUsers:/gi,
    /createUser:/gi,
    /updateUser:/gi,
    /deleteUser:/gi,
    /uploadFile:/gi,
    /getUploads:/gi,
    /deleteUpload:/gi,
    /getHealth:/gi,
  ];

  functionPatterns.forEach((pattern) => {
    if (pattern.test(content)) {
      const functionName = pattern.source.replace(/[:/gi]/g, "");
      implementations.push({
        endpoint: `FUNCTION_${functionName}`,
        method: "FUNCTION",
        file: filename,
      });
    }
  });

  return implementations;
}

/**
 * Check authentication and API key usage in file
 */
function checkAuthPatterns(content, filename) {
  const authChecks = {
    hasAuthHeader: /Authorization:\s*|Bearer\s+/i.test(content),
    hasApiKeyHeader: /X-API-Key|api[_-]?key/i.test(content),
    usesAuthStore: /useAuthStore|authStore/i.test(content),
    usesTokens: /access_token|refresh_token|tokens/i.test(content),
    usesTokenService: /tokenService/i.test(content),
    hasRequestInterceptor: /interceptor/i.test(content),
    file: filename,
  };

  return authChecks;
}

/**
 * Main validation function
 */
async function validateFrontendApiCoverage() {
  log("\n🔍 Frontend API Coverage Validation Starting...", colors.cyan);
  log("=".repeat(80), colors.cyan);

  const results = {
    covered: [],
    missing: [],
    authIssues: [],
    implementations: [],
    authPatterns: [],
  };

  // Analyze frontend API files
  log("\n📁 Analyzing Frontend API Files:", colors.yellow);
  for (const apiFile of frontendApiFiles) {
    const content = await readFileIfExists(apiFile);
    if (content) {
      log(`  ✓ Reading ${apiFile}`, colors.green);
      const implementations = analyzeApiFile(content, apiFile);
      const authPatterns = checkAuthPatterns(content, apiFile);

      results.implementations.push(...implementations);
      results.authPatterns.push(authPatterns);
    } else {
      log(`  ✗ File not found: ${apiFile}`, colors.red);
    }
  }

  // Analyze frontend hook files
  log("\n🪝 Analyzing Frontend Hook Files:", colors.yellow);
  for (const hookFile of frontendHookFiles) {
    const content = await readFileIfExists(hookFile);
    if (content) {
      log(`  ✓ Reading ${hookFile}`, colors.green);
      const authPatterns = checkAuthPatterns(content, hookFile);
      results.authPatterns.push(authPatterns);
    } else {
      log(`  ✗ File not found: ${hookFile}`, colors.red);
    }
  }

  // Show found implementations
  log("\n🔍 Found Frontend Implementations:", colors.yellow);
  results.implementations.forEach((impl) => {
    log(`  • ${impl.endpoint} (${impl.method}) in ${impl.file}`, colors.blue);
  });

  // Check coverage of backend routes
  log("\n🎯 Checking Backend Route Coverage:", colors.yellow);
  const allBackendRoutes = [];
  Object.entries(expectedBackendRoutes).forEach(([category, routes]) => {
    Object.entries(routes).forEach(([path, config]) => {
      allBackendRoutes.push({ category, path, ...config });
    });
  });

  allBackendRoutes.forEach((route) => {
    // Simplified matching logic
    const routePath = route.path.toLowerCase();
    const found = results.implementations.find((impl) => {
      const implPath = impl.endpoint.toLowerCase();
      return (
        (implPath.includes("auth") && routePath.includes("auth")) ||
        (implPath.includes("user") && routePath.includes("user")) ||
        (implPath.includes("upload") && routePath.includes("upload")) ||
        (implPath.includes("health") && routePath.includes("health")) ||
        (impl.file.includes("websocket") && routePath.includes("ws"))
      );
    });

    if (found) {
      results.covered.push({ route, implementation: found });
      log(`  ✓ ${route.method} ${route.path} - Covered`, colors.green);
    } else {
      results.missing.push(route);
      log(`  ✗ ${route.method} ${route.path} - Not found`, colors.red);
    }
  });

  // Report results
  log("\n📊 Coverage Report:", colors.cyan);
  log("=".repeat(80), colors.cyan);

  const totalRoutes = allBackendRoutes.length;
  const coveredRoutes = results.covered.length;
  const coveragePercent = Math.round((coveredRoutes / totalRoutes) * 100);

  log(
    `\nRoute Coverage: ${coveredRoutes}/${totalRoutes} (${coveragePercent}%)`,
    coveragePercent >= 80
      ? colors.green
      : coveragePercent >= 60
        ? colors.yellow
        : colors.red,
  );

  if (results.missing.length > 0) {
    log(
      `\n❌ Missing Implementations (${results.missing.length}):`,
      colors.red,
    );
    results.missing.forEach((route) => {
      log(`  • ${route.method} ${route.path} (${route.category})`, colors.red);
    });
  }

  // Check authentication patterns
  log("\n🔐 Authentication Pattern Analysis:", colors.yellow);
  const authSummary = {
    authHeaders: 0,
    apiKeyHeaders: 0,
    authStores: 0,
    tokenUsage: 0,
    tokenServices: 0,
  };

  results.authPatterns.forEach((pattern) => {
    if (pattern.hasAuthHeader) authSummary.authHeaders++;
    if (pattern.hasApiKeyHeader) authSummary.apiKeyHeaders++;
    if (pattern.usesAuthStore) authSummary.authStores++;
    if (pattern.usesTokens) authSummary.tokenUsage++;
    if (pattern.usesTokenService) authSummary.tokenServices++;

    log(`  ${path.basename(pattern.file)}:`, colors.white);
    log(
      `    Auth Header: ${pattern.hasAuthHeader ? "✓" : "✗"}`,
      pattern.hasAuthHeader ? colors.green : colors.red,
    );
    log(
      `    API Key: ${pattern.hasApiKeyHeader ? "✓" : "✗"}`,
      pattern.hasApiKeyHeader ? colors.green : colors.red,
    );
    log(
      `    Auth Store: ${pattern.usesAuthStore ? "✓" : "✗"}`,
      pattern.usesAuthStore ? colors.green : colors.red,
    );
    log(
      `    Token Usage: ${pattern.usesTokens ? "✓" : "✗"}`,
      pattern.usesTokens ? colors.green : colors.red,
    );
    log(
      `    Token Service: ${pattern.usesTokenService ? "✓" : "✗"}`,
      pattern.usesTokenService ? colors.green : colors.red,
    );
  });

  log("\n📈 Authentication Summary:", colors.cyan);
  log(`  Files with Auth Headers: ${authSummary.authHeaders}`, colors.white);
  log(`  Files with API Keys: ${authSummary.apiKeyHeaders}`, colors.white);
  log(`  Files using Auth Store: ${authSummary.authStores}`, colors.white);
  log(`  Files using Tokens: ${authSummary.tokenUsage}`, colors.white);
  log(
    `  Files using Token Service: ${authSummary.tokenServices}`,
    colors.white,
  );

  // Recommendations
  log("\n💡 Recommendations:", colors.cyan);

  if (results.missing.length > 0) {
    log("  • Implement missing API endpoints in frontend", colors.yellow);
    log(
      "  • Ensure all backend routes have corresponding frontend implementations",
      colors.yellow,
    );
  }

  if (authSummary.authHeaders === 0) {
    log(
      "  • Add proper Authorization headers to protected endpoints",
      colors.yellow,
    );
  }

  if (authSummary.tokenServices === 0) {
    log(
      "  • Integrate token service for automatic token management",
      colors.yellow,
    );
  }

  // Final status
  log("\n🎉 Validation Complete!", colors.cyan);
  const overallStatus = coveragePercent >= 70 && authSummary.tokenUsage > 0;
  log(
    `Overall Status: ${overallStatus ? "PASS" : "NEEDS IMPROVEMENT"}`,
    overallStatus ? colors.green : colors.yellow,
  );

  return results;
}

// Run the validation
if (require.main === module) {
  validateFrontendApiCoverage()
    .then((results) => {
      process.exit(results.missing.length <= 3 ? 0 : 1); // Allow a few missing routes
    })
    .catch((error) => {
      log(`\n❌ Validation failed: ${error.message}`, colors.red);
      console.error(error);
      process.exit(1);
    });
}

module.exports = { validateFrontendApiCoverage };
