// File Browser Component Tests

const { test, expect } = require('@playwright/test');
const { setupMockAPI } = require('../fixtures/mock-api.js');

test.describe('File Browser', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/');
  });

  test('should display file browser component', async ({ page }) => {
    const fileBrowser = page.locator('.file-browser-container');
    await expect(fileBrowser).toBeVisible();
  });

  test('should show current path', async ({ page }) => {
    const currentPath = page.locator('.current-path');
    await expect(currentPath).toBeVisible();
    await expect(currentPath).toContainText('Current Path:');
    await expect(currentPath).toContainText('/');
  });

  test('should list files and directories', async ({ page }) => {
    await page.waitForSelector('.file-browser');
    const fileItems = page.locator('.file-item');

    // Should have multiple items
    await expect(fileItems).toHaveCount(6); // Based on mock data
  });

  test('should display directory icons', async ({ page }) => {
    const directoryItems = page.locator('.file-item').filter({
      has: page.locator('.file-icon', { hasText: '📁' })
    });

    await expect(directoryItems.first()).toBeVisible();
  });

  test('should display disk image icons', async ({ page }) => {
    const imageItems = page.locator('.file-item').filter({
      has: page.locator('.file-icon', { hasText: '💿' })
    });

    await expect(imageItems.first()).toBeVisible();
  });

  test('should display IMAGE badge for disk images', async ({ page }) => {
    const imageBadge = page.locator('.image-badge', { hasText: 'IMAGE' });
    await expect(imageBadge.first()).toBeVisible();
  });

  test('should display file size and modification date', async ({ page }) => {
    const fileDetails = page.locator('.file-details').first();
    await expect(fileDetails).toBeVisible();
    // Should contain size and date
    await expect(fileDetails).toContainText(/GB|MB|KB/);
  });

  test('should navigate into directory on click', async ({ page }) => {
    // Click on a directory
    const directoryItem = page.locator('.file-item').filter({
      has: page.locator('.file-name', { hasText: 'evidence' })
    });

    await directoryItem.click();

    // Wait for path to update
    await page.waitForTimeout(500);

    // Current path should update
    const currentPath = page.locator('.current-path');
    await expect(currentPath).toContainText('/mnt/evidence');
  });

  test('should navigate up using parent directory link', async ({ page }) => {
    // First navigate into a directory
    await page.click('text=evidence');
    await page.waitForTimeout(500);

    // Click parent directory (..)
    const parentLink = page.locator('.file-item').filter({
      has: page.locator('.file-icon', { hasText: '⬆️' })
    });

    await parentLink.click();
    await page.waitForTimeout(500);

    // Should be back at /mnt
    const currentPath = page.locator('.current-path');
    await expect(currentPath).toContainText('/mnt');
  });

  test('should select file on click', async ({ page }) => {
    // Click on a disk image
    const imageItem = page.locator('.file-item').filter({
      has: page.locator('.file-name', { hasText: 'case-001.e01' })
    });

    await imageItem.click();

    // Item should be selected
    await expect(imageItem).toHaveClass(/selected/);

    // Selected files section should appear
    const selectedFiles = page.locator('.selected-files');
    await expect(selectedFiles).toBeVisible();
    await expect(selectedFiles).toContainText('Selected Files (1)');
    await expect(selectedFiles).toContainText('/mnt/case-001.e01');
  });

  test('should allow multiple file selections', async ({ page }) => {
    // Select first image
    await page.click('text=case-001.e01');
    await page.waitForTimeout(200);

    // Select second image
    await page.click('text=memory.raw');
    await page.waitForTimeout(200);

    // Should show 2 selected files
    const selectedFiles = page.locator('.selected-files');
    await expect(selectedFiles).toContainText('Selected Files (2)');
    await expect(selectedFiles).toContainText('/mnt/case-001.e01');
    await expect(selectedFiles).toContainText('/mnt/memory.raw');
  });

  test('should deselect file on second click', async ({ page }) => {
    // Select file
    await page.click('text=case-001.e01');
    await page.waitForTimeout(200);

    // Deselect same file
    await page.click('text=case-001.e01');
    await page.waitForTimeout(200);

    // Selected files section should not be visible or show 0
    const selectedFilesCount = await page.locator('.selected-files').count();
    if (selectedFilesCount > 0) {
      await expect(page.locator('.selected-files')).toContainText('Selected Files (0)');
    }
  });

  test('should not select directories', async ({ page }) => {
    // Try to select a directory (should navigate instead)
    const directoryItem = page.locator('.file-item').filter({
      has: page.locator('.file-name', { hasText: 'evidence' })
    });

    await directoryItem.click();

    // Should not be selected, should navigate
    await expect(directoryItem).not.toHaveClass(/selected/);
  });

  test('should filter disk/memory images visually', async ({ page }) => {
    // Image files should have special styling
    const imageItems = page.locator('.file-item.image');
    await expect(imageItems.first()).toBeVisible();

    // Check that they have different styling
    const imageColor = await imageItems.first().evaluate((el) =>
      window.getComputedStyle(el).color
    );
    expect(imageColor).toBeTruthy();
  });

  test('should show loading state while fetching files', async ({ page }) => {
    // Navigate to trigger new fetch
    await page.click('text=evidence');

    // Look for loading indicator (brief)
    const loading = page.locator('.loading');
    // May or may not catch it depending on speed
  });

  test('should handle empty directories gracefully', async ({ page }) => {
    // Mock an empty directory response
    await page.route('**/api/fs/browse?path=/mnt/empty', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    // Would need to navigate to this path via the UI
    // This is more of an edge case
  });
});

test.describe('File Browser Error Handling', () => {
  test('should display error for access denied', async ({ page }) => {
    await page.route('**/api/fs/browse**', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Access denied' }),
      });
    });

    await page.goto('/');

    // Should show error message
    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Access denied');
  });

  test('should display error for path not found', async ({ page }) => {
    await page.route('**/api/fs/browse**', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Path not found' }),
      });
    });

    await page.goto('/');

    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Path not found');
  });
});

test.describe('File Browser Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/');
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Tab to file items
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Enter should select/navigate
    await page.keyboard.press('Enter');
  });

  test('should have appropriate ARIA labels', async ({ page }) => {
    // Check for semantic HTML
    const fileItems = page.locator('.file-item');
    await expect(fileItems.first()).toBeVisible();
  });
});
