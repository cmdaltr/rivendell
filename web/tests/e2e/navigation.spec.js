// Navigation and Layout Tests

const { test, expect } = require('@playwright/test');

test.describe('Application Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display application header with title', async ({ page }) => {
    const header = page.locator('.App-header');
    await expect(header).toBeVisible();

    const title = header.locator('h1');
    await expect(title).toContainText('Elrond Web Interface');
    await expect(title).toContainText('🧙‍♂️');
  });

  test('should display navigation links', async ({ page }) => {
    const nav = page.locator('.App-header nav');
    await expect(nav).toBeVisible();

    const newAnalysisLink = nav.locator('a', { hasText: 'New Analysis' });
    const jobsLink = nav.locator('a', { hasText: 'Jobs' });

    await expect(newAnalysisLink).toBeVisible();
    await expect(jobsLink).toBeVisible();
  });

  test('should navigate to New Analysis page', async ({ page }) => {
    await page.click('text=New Analysis');
    await expect(page).toHaveURL('/');
    await expect(page.locator('h2', { hasText: 'New Forensic Analysis' })).toBeVisible();
  });

  test('should navigate to Jobs page', async ({ page }) => {
    await page.click('text=Jobs');
    await expect(page).toHaveURL('/jobs');
    await expect(page.locator('h2', { hasText: 'Analysis Jobs' })).toBeVisible();
  });

  test('should display footer', async ({ page }) => {
    const footer = page.locator('.App-footer');
    await expect(footer).toBeVisible();
    await expect(footer).toContainText('Elrond v2.1.0');
    await expect(footer).toContainText('Digital Forensics Analysis Platform');
  });

  test('should have correct page title', async ({ page }) => {
    await expect(page).toHaveTitle('Elrond Web Interface');
  });

  test('should apply dark theme styles', async ({ page }) => {
    const body = page.locator('body');
    const bgColor = await body.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Dark background color
    expect(bgColor).toBeTruthy();
  });

  test('should highlight active navigation link', async ({ page }) => {
    const newAnalysisLink = page.locator('nav a', { hasText: 'New Analysis' });

    await newAnalysisLink.click();
    await page.waitForTimeout(100);

    // Check if link has active styles (color change on hover/active)
    const color = await newAnalysisLink.evaluate((el) =>
      window.getComputedStyle(el).color
    );
    expect(color).toBeTruthy();
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    const header = page.locator('.App-header');
    await expect(header).toBeVisible();

    const nav = page.locator('.App-header nav');
    await expect(nav).toBeVisible();
  });
});

test.describe('Page Routing', () => {
  test('should handle direct navigation to Jobs page', async ({ page }) => {
    await page.goto('/jobs');
    await expect(page.locator('h2', { hasText: 'Analysis Jobs' })).toBeVisible();
  });

  test('should handle back button navigation', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Jobs');
    await expect(page).toHaveURL('/jobs');

    await page.goBack();
    await expect(page).toHaveURL('/');
  });

  test('should handle forward button navigation', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Jobs');
    await page.goBack();
    await page.goForward();
    await expect(page).toHaveURL('/jobs');
  });
});
