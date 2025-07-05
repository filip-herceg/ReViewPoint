import { test, expect } from '@playwright/test';

test('homepage has expected text', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toHaveText(/ReViewPoint/i);
});
