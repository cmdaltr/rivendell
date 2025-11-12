// Job Details Page Tests

const { test, expect } = require('@playwright/test');
const { setupMockAPI, setupProgressiveJobUpdates } = require('../fixtures/mock-api.js');

test.describe('Job Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
  });

  test('should display job details page', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    await expect(page.locator('h2', { hasText: 'Job Details' })).toBeVisible();
  });

  test('should display job ID', async ({ page }) => {
    await page.goto('/jobs/test-job-003');

    const jobId = page.locator('.job-id');
    await expect(jobId).toBeVisible();
    await expect(jobId).toContainText('test-job-003');
  });

  test('should display Back to Jobs button', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const backButton = page.locator('button', { hasText: 'Back to Jobs' });
    await expect(backButton).toBeVisible();
  });

  test('should navigate back to jobs list', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    await page.click('button:has-text("Back to Jobs")');

    await expect(page).toHaveURL('/jobs');
    await expect(page.locator('h2', { hasText: 'Analysis Jobs' })).toBeVisible();
  });

  test('should display job information grid', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const infoGrid = page.locator('.job-info-grid');
    await expect(infoGrid).toBeVisible();

    // Check for key information fields
    await expect(page.locator('strong', { hasText: 'Case Number:' })).toBeVisible();
    await expect(page.locator('strong', { hasText: 'Status:' })).toBeVisible();
    await expect(page.locator('strong', { hasText: 'Progress:' })).toBeVisible();
    await expect(page.locator('strong', { hasText: 'Created:' })).toBeVisible();
    await expect(page.locator('strong', { hasText: 'Started:' })).toBeVisible();
    await expect(page.locator('strong', { hasText: 'Completed:' })).toBeVisible();
    await expect(page.locator('strong', { hasText: 'Duration:' })).toBeVisible();
  });

  test('should display case number', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    await expect(page.locator('text=INC-2025-001')).toBeVisible();
  });

  test('should display status badge', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const statusBadge = page.locator('.status-badge');
    await expect(statusBadge).toBeVisible();
    await expect(statusBadge).toHaveText('completed');
    await expect(statusBadge).toHaveClass(/status-completed/);
  });

  test('should display progress bar', async ({ page }) => {
    await page.goto('/jobs/test-job-running');

    const progressBar = page.locator('.progress-bar');
    await expect(progressBar).toBeVisible();

    const progressFill = page.locator('.progress-fill');
    await expect(progressFill).toContainText(/\d+%/);
  });

  test('should display source images section', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const sourceSection = page.locator('.source-paths-section');
    await expect(sourceSection).toBeVisible();

    await expect(sourceSection.locator('h3')).toContainText('Source Images');
    await expect(sourceSection).toContainText('/mnt/case-001.e01');
  });

  test('should display enabled options section', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const optionsSection = page.locator('.options-section');
    await expect(optionsSection).toBeVisible();

    await expect(optionsSection.locator('h3')).toContainText('Enabled Options');

    // Should show option tags
    const optionTags = page.locator('.option-tag');
    await expect(optionTags.first()).toBeVisible();
  });

  test('should display job log section', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const logSection = page.locator('.log-section');
    await expect(logSection).toBeVisible();

    await expect(logSection.locator('h3')).toContainText('Job Log');

    const logViewer = page.locator('.log-viewer');
    await expect(logViewer).toBeVisible();
  });

  test('should display log entries', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const logViewer = page.locator('.log-viewer pre');
    await expect(logViewer).toBeVisible();
    await expect(logViewer).toContainText('Job created');
    await expect(logViewer).toContainText('Starting analysis');
  });

  test('should display results section for completed jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const resultSection = page.locator('.result-section');
    await expect(resultSection).toBeVisible();

    await expect(resultSection.locator('h3')).toContainText('Results');
    await expect(resultSection.locator('.success')).toContainText('Analysis completed successfully');

    await expect(page.locator('strong', { hasText: 'Output Directory:' })).toBeVisible();
  });

  test('should display error section for failed jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-failed');

    const errorSection = page.locator('.error-section');
    await expect(errorSection).toBeVisible();

    await expect(errorSection.locator('h3')).toContainText('Error');
    await expect(errorSection.locator('.error')).toBeVisible();
    await expect(errorSection).toContainText('Process exited with code 1');
  });

  test('should not show results section for incomplete jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-running');

    const resultSection = page.locator('.result-section');
    await expect(resultSection).not.toBeVisible();
  });

  test('should not show error section for successful jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const errorSection = page.locator('.error-section');
    await expect(errorSection).not.toBeVisible();
  });
});

test.describe('Job Details - Action Buttons', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
  });

  test('should show Cancel button for running jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-running');

    const cancelButton = page.locator('button', { hasText: 'Cancel Job' });
    await expect(cancelButton).toBeVisible();
  });

  test('should show Delete button for completed jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const deleteButton = page.locator('button', { hasText: 'Delete Job' });
    await expect(deleteButton).toBeVisible();
  });

  test('should not show Cancel button for completed jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    const cancelButton = page.locator('button', { hasText: 'Cancel Job' });
    await expect(cancelButton).not.toBeVisible();
  });

  test('should cancel job when Cancel button is clicked', async ({ page }) => {
    await page.goto('/jobs/test-job-running');

    // Mock confirmation dialog
    page.on('dialog', dialog => dialog.accept());

    await page.click('button:has-text("Cancel Job")');

    // Status should update to cancelled
    await page.waitForTimeout(1000);
    const statusBadge = page.locator('.status-badge');
    await expect(statusBadge).toHaveText('cancelled');
  });

  test('should show confirmation before cancelling', async ({ page }) => {
    await page.goto('/jobs/test-job-running');

    let dialogShown = false;
    page.on('dialog', dialog => {
      dialogShown = true;
      expect(dialog.message()).toContain('Are you sure');
      dialog.dismiss();
    });

    await page.click('button:has-text("Cancel Job")');
    await page.waitForTimeout(500);

    expect(dialogShown).toBe(true);
  });

  test('should delete job and redirect to jobs list', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    // Mock confirmation dialog
    page.on('dialog', dialog => dialog.accept());

    await page.click('button:has-text("Delete Job")');

    // Should redirect to jobs list
    await expect(page).toHaveURL('/jobs');
  });

  test('should show confirmation before deleting', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    let dialogShown = false;
    page.on('dialog', dialog => {
      dialogShown = true;
      expect(dialog.message()).toContain('Are you sure');
      expect(dialog.message()).toContain('cannot be undone');
      dialog.dismiss();
    });

    await page.click('button:has-text("Delete Job")');
    await page.waitForTimeout(500);

    expect(dialogShown).toBe(true);
  });
});

test.describe('Job Details - Auto-refresh', () => {
  test('should auto-refresh job details periodically', async ({ page }) => {
    let apiCallCount = 0;
    await page.route('**/api/jobs/test-job-running', async (route) => {
      apiCallCount++;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-job-running',
          status: 'running',
          progress: apiCallCount * 10,
          log: [`Call ${apiCallCount}`],
        }),
      });
    });

    await page.goto('/jobs/test-job-running');

    // Wait for multiple refresh cycles (3 second intervals)
    await page.waitForTimeout(7000);

    // Should have made multiple API calls
    expect(apiCallCount).toBeGreaterThan(2);
  });

  test('should update progress in real-time', async ({ page }) => {
    await setupProgressiveJobUpdates(page, 'test-job-progressive');
    await page.goto('/jobs/test-job-progressive');

    // Initial progress
    let progressText = await page.locator('.progress-fill').textContent();
    let initialProgress = parseInt(progressText);

    // Wait for refresh
    await page.waitForTimeout(4000);

    // Progress should have updated
    progressText = await page.locator('.progress-fill').textContent();
    let newProgress = parseInt(progressText);

    expect(newProgress).toBeGreaterThan(initialProgress);
  });
});

test.describe('Job Details - Error Handling', () => {
  test('should display error for job not found', async ({ page }) => {
    await page.route('**/api/jobs/nonexistent', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Job not found' }),
      });
    });

    await page.goto('/jobs/nonexistent');

    const error = page.locator('.error');
    await expect(error).toBeVisible();
    await expect(error).toContainText('Job not found');

    // Should show back button
    const backButton = page.locator('button', { hasText: 'Back to Jobs' });
    await expect(backButton).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    await page.route('**/api/jobs/error-test', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto('/jobs/error-test');

    const error = page.locator('.error');
    await expect(error).toBeVisible();
  });
});

test.describe('Job Details - Responsive Design', () => {
  test('should be responsive on mobile viewport', async ({ page }) => {
    await setupMockAPI(page);
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/jobs/test-job-completed');

    const jobHeader = page.locator('.job-header');
    await expect(jobHeader).toBeVisible();

    // Buttons should stack
    const jobActions = page.locator('.job-actions');
    await expect(jobActions).toBeVisible();
  });
});

test.describe('Job Details - Duration Calculation', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
  });

  test('should show N/A for duration when not started', async ({ page }) => {
    await page.goto('/jobs/test-job-pending');

    await expect(page.locator('text=N/A')).toBeVisible();
  });

  test('should show running duration for active jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-running');

    // Should show some duration (seconds, minutes, or hours)
    const infoGrid = page.locator('.job-info-grid');
    await expect(infoGrid).toContainText(/\ds|\dm|\dh/);
  });

  test('should show total duration for completed jobs', async ({ page }) => {
    await page.goto('/jobs/test-job-completed');

    // Should show duration
    const infoGrid = page.locator('.job-info-grid');
    await expect(infoGrid).toContainText(/\dh \dm|\dm \ds|\ds/);
  });
});
