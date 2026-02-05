import { test, expect } from '@playwright/test';

test.describe('Tests List', () => {
  test('should load tests list page', async ({ page }) => {
    await page.goto('/tests');

    // Check header is visible
    await expect(page.getByRole('heading', { name: 'Tests' })).toBeVisible();

    // Check "New Test" button is visible
    await expect(page.getByRole('link', { name: /New Test/i })).toBeVisible();
  });

  test('should display test filters', async ({ page }) => {
    await page.goto('/tests');

    // Check search input
    await expect(page.getByPlaceholder('Search tests...')).toBeVisible();

    // Check filter dropdowns
    await expect(page.getByRole('combobox')).toHaveCount(3); // Type, Status, Severity
  });

  test('should filter tests by search', async ({ page }) => {
    await page.goto('/tests');

    const searchInput = page.getByPlaceholder('Search tests...');
    await searchInput.fill('Orders');

    // Should show filtered results (mock data has "Daily Orders Volume")
    await expect(page.getByText('Daily Orders Volume')).toBeVisible();
  });

  test('should navigate to new test form', async ({ page }) => {
    await page.goto('/tests');

    await page.getByRole('link', { name: /New Test/i }).click();

    await expect(page).toHaveURL('/tests/new');
    await expect(page.getByRole('heading', { name: 'Create Test' })).toBeVisible();
  });

  test('should display test cards with run buttons', async ({ page }) => {
    await page.goto('/tests');

    // Wait for tests to load and check for Run button
    await expect(page.getByRole('button', { name: /Run/i }).first()).toBeVisible();

    // Check test names are visible (from mock data)
    await expect(page.getByText('Daily Orders Volume')).toBeVisible();
  });
});
