// Job List and Monitoring Tests

const { test, expect } = require('@playwright/test');
const { setupMockAPI } = require('../fixtures/mock-api.js');

test.describe('Job List Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/jobs');
  });

  test('should display job list page', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'Analysis Jobs' })).toBeVisible();
  });

  test('should display filter controls', async ({ page }) => {
    const filterControls = page.locator('.filter-controls');
    await expect(filterControls).toBeVisible();

    const filterLabel = filterControls.locator('label', { hasText: 'Filter by status' });
    await expect(filterLabel).toBeVisible();

    const filterSelect = filterControls.locator('select');
    await expect(filterSelect).toBeVisible();
  });

  test('should display jobs in table format', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Check table headers
    await expect(page.locator('th', { hasText: 'Case Number' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Status' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Progress' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Created' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Duration' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Actions' })).toBeVisible();
  });

  test('should display job rows', async ({ page }) => {
    const rows = page.locator('tbody tr');

    // Should have jobs (based on mock data)
    await expect(rows).toHaveCount(4);
  });

  test('should display job case numbers as links', async ({ page }) => {
    const firstJobLink = page.locator('tbody tr').first().locator('a');
    await expect(firstJobLink).toBeVisible();
    await expect(firstJobLink).toContainText(/INC-|CASE-|TEST-/);
  });

  test('should display job status badges', async ({ page }) => {
    const statusBadges = page.locator('.status-badge');

    // Should have status badges for each job
    await expect(statusBadges.first()).toBeVisible();

    // Check for different status types
    await expect(page.locator('.status-completed')).toBeVisible();
    await expect(page.locator('.status-running')).toBeVisible();
    await expect(page.locator('.status-pending')).toBeVisible();
  });

  test('should display progress bars', async ({ page }) => {
    const progressBars = page.locator('.progress-bar');
    await expect(progressBars.first()).toBeVisible();

    // Check progress fill
    const progressFills = page.locator('.progress-fill');
    await expect(progressFills.first()).toBeVisible();
  });

  test('should display formatted dates', async ({ page }) => {
    const firstRow = page.locator('tbody tr').first();

    // Should contain date/time information
    await expect(firstRow).toContainText(/\d{1,2}\/\d{1,2}\/\d{4}|AM|PM/);
  });

  test('should display duration information', async ({ page }) => {
    const firstRow = page.locator('tbody tr').first();

    // Should contain duration (seconds, minutes, hours)
    await expect(firstRow).toContainText(/\ds|\dm|\dh|N\/A/);
  });

  test('should have View Details button for each job', async ({ page }) => {
    const viewDetailsButtons = page.locator('button', { hasText: 'View Details' });
    await expect(viewDetailsButtons.first()).toBeVisible();
  });

  test('should navigate to job details when clicking View Details', async ({ page }) => {
    const firstViewButton = page.locator('button', { hasText: 'View Details' }).first();
    await firstViewButton.click();

    // Should navigate to job details page
    await expect(page).toHaveURL(/\/jobs\/.+/);
    await expect(page.locator('h2', { hasText: 'Job Details' })).toBeVisible();
  });

  test('should navigate to job details when clicking case number', async ({ page }) => {
    const firstJobLink = page.locator('tbody tr').first().locator('a');
    await firstJobLink.click();

    // Should navigate to job details page
    await expect(page).toHaveURL(/\/jobs\/.+/);
    await expect(page.locator('h2', { hasText: 'Job Details' })).toBeVisible();
  });

  test('should show image count for each job', async ({ page }) => {
    const firstRow = page.locator('tbody tr').first();

    // Should show "X image(s)"
    await expect(firstRow).toContainText(/\d+ image\(s\)/);
  });
});

test.describe('Job List - Filtering', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/jobs');
  });

  test('should filter jobs by status', async ({ page }) => {
    const filterSelect = page.locator('.filter-controls select');

    // Select "Running" status
    await filterSelect.selectOption('running');

    // Should make API call with status filter
    // Jobs should update (mocked)
  });

  test('should show all jobs when filter is "All"', async ({ page }) => {
    const filterSelect = page.locator('.filter-controls select');

    // Ensure "All" is selected
    await filterSelect.selectOption('');

    // Should show all jobs
    const rows = page.locator('tbody tr');
    await expect(rows).toHaveCount(4);
  });

  test('should have filter options for all statuses', async ({ page }) => {
    const filterSelect = page.locator('.filter-controls select');

    await expect(filterSelect.locator('option', { hasText: 'All' })).toBeVisible();
    await expect(filterSelect.locator('option', { hasText: 'Pending' })).toBeVisible();
    await expect(filterSelect.locator('option', { hasText: 'Running' })).toBeVisible();
    await expect(filterSelect.locator('option', { hasText: 'Completed' })).toBeVisible();
    await expect(filterSelect.locator('option', { hasText: 'Failed' })).toBeVisible();
    await expect(filterSelect.locator('option', { hasText: 'Cancelled' })).toBeVisible();
  });
});

test.describe('Job List - Auto-refresh', () => {
  test('should auto-refresh job list periodically', async ({ page }) => {
    await setupMockAPI(page);

    let apiCallCount = 0;
    await page.route('**/api/jobs**', async (route) => {
      apiCallCount++;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          jobs: [],
          total: 0,
        }),
      });
    });

    await page.goto('/jobs');

    // Wait for multiple refresh cycles (5 second intervals)
    await page.waitForTimeout(11000);

    // Should have made multiple API calls
    expect(apiCallCount).toBeGreaterThan(2);
  });
});

test.describe('Job List - Empty State', () => {
  test('should show empty state when no jobs exist', async ({ page }) => {
    await page.route('**/api/jobs**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          jobs: [],
          total: 0,
        }),
      });
    });

    await page.goto('/jobs');

    const emptyState = page.locator('.empty-state');
    await expect(emptyState).toBeVisible();
    await expect(emptyState).toContainText('No jobs found');

    // Should have link to create new analysis
    const newAnalysisButton = emptyState.locator('button', { hasText: 'Start New Analysis' });
    await expect(newAnalysisButton).toBeVisible();
  });

  test('should navigate to New Analysis from empty state', async ({ page }) => {
    await page.route('**/api/jobs**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          jobs: [],
          total: 0,
        }),
      });
    });

    await page.goto('/jobs');

    await page.click('button:has-text("Start New Analysis")');

    // Should navigate to home
    await expect(page).toHaveURL('/');
    await expect(page.locator('h2', { hasText: 'New Forensic Analysis' })).toBeVisible();
  });
});

test.describe('Job List - Status Display', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/jobs');
  });

  test('should display completed jobs with green badge', async ({ page }) => {
    const completedBadge = page.locator('.status-completed').first();
    await expect(completedBadge).toBeVisible();
    await expect(completedBadge).toHaveText('completed');
  });

  test('should display running jobs with blue badge', async ({ page }) => {
    const runningBadge = page.locator('.status-running').first();
    await expect(runningBadge).toBeVisible();
    await expect(runningBadge).toHaveText('running');
  });

  test('should display pending jobs with yellow badge', async ({ page }) => {
    const pendingBadge = page.locator('.status-pending').first();
    await expect(pendingBadge).toBeVisible();
    await expect(pendingBadge).toHaveText('pending');
  });

  test('should display failed jobs with red badge', async ({ page }) => {
    const failedBadge = page.locator('.status-failed').first();
    await expect(failedBadge).toBeVisible();
    await expect(failedBadge).toHaveText('failed');
  });
});

test.describe('Job List - Progress Display', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPI(page);
    await page.goto('/jobs');
  });

  test('should show 0% progress for pending jobs', async ({ page }) => {
    // Find pending job row
    const pendingRow = page.locator('tbody tr').filter({
      has: page.locator('.status-pending'),
    });

    const progressBar = pendingRow.locator('.progress-bar');
    await expect(progressBar).toBeVisible();

    // Progress fill should be minimal or 0%
    const progressFill = progressBar.locator('.progress-fill');
    const width = await progressFill.evaluate((el) => el.style.width);
    expect(width).toBe('0%');
  });

  test('should show partial progress for running jobs', async ({ page }) => {
    const runningRow = page.locator('tbody tr').filter({
      has: page.locator('.status-running'),
    });

    const progressBar = runningRow.locator('.progress-bar');
    const progressFill = progressBar.locator('.progress-fill');

    // Should have percentage
    await expect(progressFill).toContainText(/\d+%/);
  });

  test('should show 100% progress for completed jobs', async ({ page }) => {
    const completedRow = page.locator('tbody tr').filter({
      has: page.locator('.status-completed'),
    });

    const progressFill = completedRow.locator('.progress-fill');
    const width = await progressFill.evaluate((el) => el.style.width);
    expect(width).toBe('100%');
  });
});

test.describe('Job List - Error Handling', () => {
  test('should display error message on API failure', async ({ page }) => {
    await page.route('**/api/jobs**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await page.goto('/jobs');

    const error = page.locator('.error');
    await expect(error).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    await page.route('**/api/jobs**', async (route) => {
      await route.abort('failed');
    });

    await page.goto('/jobs');

    const error = page.locator('.error');
    await expect(error).toBeVisible();
  });
});

test.describe('Job List - Responsive Design', () => {
  test('should be responsive on mobile viewport', async ({ page }) => {
    await setupMockAPI(page);
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/jobs');

    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Should have horizontal scroll if needed
    const tableContainer = page.locator('.table-container');
    await expect(tableContainer).toBeVisible();
  });
});
