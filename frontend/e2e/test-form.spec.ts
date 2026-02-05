import { test, expect } from '@playwright/test';

test.describe('Test Form', () => {
  test('should load create test form', async ({ page }) => {
    await page.goto('/tests/new');

    await expect(page.getByRole('heading', { name: 'Create Test' })).toBeVisible();

    // Check tabs are visible
    await expect(page.getByRole('tab', { name: 'Basic Info' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Query' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Configuration' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Alerts' })).toBeVisible();
  });

  test('should have form fields in Basic Info tab', async ({ page }) => {
    await page.goto('/tests/new');

    // Check form fields
    await expect(page.getByLabel('Test Name')).toBeVisible();
    await expect(page.getByLabel('Description')).toBeVisible();
  });

  test('should switch between form tabs', async ({ page }) => {
    await page.goto('/tests/new');

    // Click Query tab
    await page.getByRole('tab', { name: 'Query' }).click();
    await expect(page.getByRole('tabpanel', { name: 'Query' })).toBeVisible();

    // Click Configuration tab
    await page.getByRole('tab', { name: 'Configuration' }).click();
    await expect(page.getByText('Test Configuration')).toBeVisible();

    // Click Alerts tab
    await page.getByRole('tab', { name: 'Alerts' }).click();
    await expect(page.getByText('Alert Configuration')).toBeVisible();
  });

  test('should have cancel and submit buttons', async ({ page }) => {
    await page.goto('/tests/new');

    await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Create Test' })).toBeVisible();
  });

  test('should navigate back to tests list on cancel', async ({ page }) => {
    await page.goto('/tests/new');

    await page.getByRole('button', { name: 'Cancel' }).click();

    await expect(page).toHaveURL('/tests');
  });
});
