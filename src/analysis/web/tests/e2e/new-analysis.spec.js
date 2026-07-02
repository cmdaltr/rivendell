// New Analysis Workflow End-to-End Tests

const { test, expect } = require('@playwright/test');
const { setupMockAPI } = require('../fixtures/mock-api.js');

test.describe('New Analysis Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/');
  });

  test('should display new analysis form', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'New Forensic Analysis' })).toBeVisible();

    // Form fields should be visible
    await expect(page.locator('label', { hasText: 'Case Number' })).toBeVisible();
    await expect(page.locator('label', { hasText: 'Destination Directory' })).toBeVisible();
    await expect(page.locator('label', { hasText: 'Select Disk/Memory Images' })).toBeVisible();
    await expect(page.locator('label', { hasText: 'Analysis Options' })).toBeVisible();
  });

  test('should have submit button', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"]', { hasText: 'Start Analysis' });
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toBeEnabled();
  });

  test('should require case number', async ({ page }) => {
    // Try to submit without case number
    await page.click('button[type="submit"]');

    // Should show error
    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Please enter a case number');
  });

  test('should require at least one image selection', async ({ page }) => {
    // Fill case number
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');

    // Try to submit without selecting images
    await page.click('button[type="submit"]');

    // Should show error
    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Please select at least one disk or memory image');
  });

  test('should require operation mode selection', async ({ page }) => {
    // Fill case number
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');

    // Select an image
    await page.click('text=case-001.e01');
    await page.waitForTimeout(200);

    // Try to submit without operation mode
    await page.click('button[type="submit"]');

    // Should show error
    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Please select an operation mode');
  });

  test('should complete full analysis creation workflow', async ({ page }) => {
    // Step 1: Enter case number
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');

    // Step 2: Select destination (optional)
    await page.fill('input[id="destinationPath"]', '/tmp/elrond/test-output');

    // Step 3: Select images
    await page.click('text=case-001.e01');
    await page.waitForTimeout(200);

    // Verify selection
    await expect(page.locator('.selected-files')).toContainText('/mnt/case-001.e01');

    // Step 4: Configure options
    await page.check('input[id="collect"]');
    await page.check('input[id="analysis"]');

    // Switch to collection options
    await page.click('button:has-text("Collection Options")');
    await page.check('input[id="userprofiles"]');

    // Switch to speed mode
    await page.click('button:has-text("Speed/Quality Mode")');
    await page.check('input[id="brisk"]');

    // Step 5: Submit
    await page.click('button[type="submit"]');

    // Should navigate to job details page
    await page.waitForURL(/\/jobs\/.+/, { timeout: 5000 });

    // Should show job details
    await expect(page.locator('h2', { hasText: 'Job Details' })).toBeVisible();
  });

  test('should allow multiple image selections', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');

    // Select multiple images
    await page.click('text=case-001.e01');
    await page.waitForTimeout(200);
    await page.click('text=memory.raw');
    await page.waitForTimeout(200);
    await page.click('text=disk.dd');
    await page.waitForTimeout(200);

    // Verify selections
    const selectedFiles = page.locator('.selected-files');
    await expect(selectedFiles).toContainText('Selected Files (3)');
    await expect(selectedFiles).toContainText('/mnt/case-001.e01');
    await expect(selectedFiles).toContainText('/mnt/memory.raw');
    await expect(selectedFiles).toContainText('/mnt/disk.dd');

    // Complete submission
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/jobs\/.+/);
  });

  test('should preserve form data when navigating between sections', async ({ page }) => {
    // Fill form
    await page.fill('input[id="caseNumber"]', 'TEST-CASE-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');

    // Navigate away and back
    await page.click('text=Jobs');
    await page.click('text=New Analysis');

    // Form should be reset (new form)
    await expect(page.locator('input[id="caseNumber"]')).toHaveValue('');
  });

  test('should handle long case numbers', async ({ page }) => {
    const longCaseNumber = 'A'.repeat(100);
    await page.fill('input[id="caseNumber"]', longCaseNumber);

    const input = page.locator('input[id="caseNumber"]');
    await expect(input).toHaveValue(longCaseNumber);
  });

  test('should handle special characters in case number', async ({ page }) => {
    const specialCaseNumber = 'INC-2025-001_TEST#123';
    await page.fill('input[id="caseNumber"]', specialCaseNumber);
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/jobs\/.+/);
  });

  test('should show loading state during submission', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');

    // Click submit
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Button should show loading state (briefly)
    await expect(submitButton).toContainText(/Starting Analysis/);
  });

  test('should disable submit button while loading', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Button should be disabled during submission
    await expect(submitButton).toBeDisabled();
  });
});

test.describe('New Analysis - Validation', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/');
  });

  test('should trim whitespace from case number', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', '  INC-2025-001  ');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    // Should still work (trimmed)
    await page.waitForURL(/\/jobs\/.+/);
  });

  test('should reject empty case number after trimming', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', '     ');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    // Should show error
    const error = page.locator('.error');
    await expect(error).toBeVisible();
  });

  test('should allow optional destination path', async ({ page }) => {
    // Leave destination empty
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    // Should work without destination
    await page.waitForURL(/\/jobs\/.+/);
  });
});

test.describe('New Analysis - Presets', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/');
  });

  test('should create analysis with minimal options', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', 'MIN-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/jobs\/.+/);
  });

  test('should create analysis with brisk mode preset', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', 'BRISK-001');
    await page.click('text=case-001.e01');

    // Enable brisk mode (enables multiple options)
    await page.click('button:has-text("Speed/Quality Mode")');
    await page.check('input[id="brisk"]');

    // Also need operation mode
    await page.click('button:has-text("Operation Mode")');
    await page.check('input[id="collect"]');

    await page.click('button[type="submit"]');
    await page.waitForURL(/\/jobs\/.+/);
  });

  test('should create analysis with exhaustive options', async ({ page }) => {
    await page.fill('input[id="caseNumber"]', 'EXHAUST-001');
    await page.click('text=case-001.e01');

    // Enable multiple options across sections
    await page.check('input[id="collect"]');

    await page.click('button:has-text("Analysis Options")');
    await page.click('button:has-text("Enable All")');

    await page.click('button:has-text("Collection Options")');
    await page.click('button:has-text("Enable All")');

    await page.click('button:has-text("Operation Mode")');
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/jobs\/.+/);
  });
});

test.describe('New Analysis - Error Handling', () => {
  test('should display API error messages', async ({ page }) => {
    await page.route('**/api/jobs', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Source path does not exist' }),
        });
      }
    });

    await page.goto('/');
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Source path does not exist');
  });

  test('should handle network errors gracefully', async ({ page }) => {
    await page.route('**/api/jobs', async (route) => {
      await route.abort('failed');
    });

    await page.goto('/');
    await page.fill('input[id="caseNumber"]', 'INC-2025-001');
    await page.click('text=case-001.e01');
    await page.check('input[id="collect"]');
    await page.click('button[type="submit"]');

    // Should show some error
    const error = page.locator('.error');
    await expect(error).toBeVisible();
  });
});
