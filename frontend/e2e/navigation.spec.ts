import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should have sidebar navigation', async ({ page }) => {
    await page.goto('/');

    // Check sidebar links
    await expect(page.getByRole('link', { name: /Dashboard/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Tests/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Connections/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Settings/i })).toBeVisible();
  });

  test('should navigate to Dashboard', async ({ page }) => {
    await page.goto('/tests');

    await page.getByRole('link', { name: /Dashboard/i }).click();

    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('should navigate to Tests', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: /Tests/i }).click();

    await expect(page).toHaveURL('/tests');
    await expect(page.getByRole('heading', { name: 'Tests' })).toBeVisible();
  });

  test('should navigate to Connections', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: /Connections/i }).click();

    await expect(page).toHaveURL('/connections');
    await expect(page.getByRole('heading', { name: 'Connections' })).toBeVisible();
  });

  test('should navigate to Settings', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: /Settings/i }).click();

    await expect(page).toHaveURL('/settings');
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  });

  test('should highlight active navigation item', async ({ page }) => {
    await page.goto('/');

    // Dashboard link should be active (have primary color)
    const dashboardLink = page.getByRole('link', { name: /Dashboard/i });
    await expect(dashboardLink).toHaveClass(/bg-primary/);

    // Navigate to Tests
    await page.goto('/tests');
    const testsLink = page.getByRole('link', { name: /Tests/i });
    await expect(testsLink).toHaveClass(/bg-primary/);
  });
});
