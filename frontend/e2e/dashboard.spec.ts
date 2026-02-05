import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/');

    // Check header is visible
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    // Check health score ring is visible
    await expect(page.getByText('Health Score')).toBeVisible();

    // Check status cards are visible - use more specific selectors
    await expect(page.locator('p').filter({ hasText: 'Passed' })).toBeVisible();
    await expect(page.locator('p').filter({ hasText: 'Failed' })).toBeVisible();
    await expect(page.locator('p').filter({ hasText: 'Running' })).toBeVisible();
    await expect(page.locator('p').filter({ hasText: 'Pending' })).toBeVisible();
  });

  test('should display trends chart', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Test Results Trend')).toBeVisible();
  });

  test('should display recent executions table', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Recent Executions')).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Test' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible();
  });

  test('should display critical alerts panel', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Critical Alerts')).toBeVisible();
  });
});
