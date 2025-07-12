import { test, expect } from "@playwright/test";

test("homepage has expected text", async ({ page }) => {
  try {
    await page.goto("/");
    await expect(page.locator("h1")).toHaveText(/ReViewPoint/i);
  } catch (err) {
    // Defensive: log error and rethrow for Playwright reporting
    // You could also use a custom error utility here if desired
    // eslint-disable-next-line no-console
    console.error("E2E test error:", err);
    throw err;
  }
});

test("error handling logs and rethrows errors", async ({ page }) => {
  let errorLogged = false;
  const originalConsoleError = console.error;
  console.error = (...args) => {
    errorLogged = true;
    originalConsoleError(...args);
  };
  let thrown = false;
  try {
    // This will fail because the selector does not exist
    await expect(page.locator("non-existent-selector")).toHaveText(
      "ShouldFail",
    );
  } catch (err) {
    thrown = true;
    // Error should be logged
    expect(errorLogged).toBe(true);
  } finally {
    console.error = originalConsoleError;
  }
  expect(thrown).toBe(true);
});
