// Mock API Handlers for Testing

import {
  mockFileSystemItems,
  mockJobPending,
  mockJobRunning,
  mockJobCompleted,
  mockJobFailed,
  mockJobList,
} from './test-data.js';

/**
 * Setup mock API routes for testing
 */
export async function setupMockAPI(page) {
  // Mock health check endpoint
  await page.route('**/api/health', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
      }),
    });
  });

  // Mock root endpoint
  await page.route('**/api', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          name: 'Elrond Web Interface',
          version: '2.1.0',
          status: 'running',
        }),
      });
    }
  });

  // Mock file browser endpoint
  await page.route('**/api/fs/browse**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.searchParams.get('path') || '/';

    // Simulate different paths
    let items = mockFileSystemItems;
    if (path === '/mnt/evidence') {
      items = [
        {
          name: '..',
          path: '/mnt',
          is_directory: true,
        },
        {
          name: 'disk1.e01',
          path: '/mnt/evidence/disk1.e01',
          is_directory: false,
          size: 10737418240,
          modified: '2025-01-15T10:30:00',
          is_image: true,
        },
      ];
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(items),
    });
  });

  // Mock create job endpoint
  await page.route('**/api/jobs', async (route) => {
    if (route.request().method() === 'POST') {
      const postData = JSON.parse(route.request().postData());
      const jobId = `test-job-${Date.now()}`;

      const job = {
        id: jobId,
        case_number: postData.case_number,
        source_paths: postData.source_paths,
        destination_path: postData.destination_path,
        options: postData.options,
        status: 'pending',
        progress: 0,
        log: [`[${new Date().toISOString()}] Job created`],
        result: null,
        error: null,
        created_at: new Date().toISOString(),
        started_at: null,
        completed_at: null,
      };

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(job),
      });
    } else if (route.request().method() === 'GET') {
      // Mock list jobs
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockJobList),
      });
    }
  });

  // Mock get job by ID endpoint
  await page.route('**/api/jobs/*', async (route) => {
    const jobId = route.request().url().split('/').pop();

    if (route.request().method() === 'GET') {
      // Return appropriate mock job based on ID
      let job;
      if (jobId.includes('pending')) {
        job = mockJobPending;
      } else if (jobId.includes('running')) {
        job = mockJobRunning;
      } else if (jobId.includes('completed')) {
        job = mockJobCompleted;
      } else if (jobId.includes('failed')) {
        job = mockJobFailed;
      } else {
        job = { ...mockJobPending, id: jobId };
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(job),
      });
    } else if (route.request().method() === 'PATCH') {
      // Mock update job
      const updateData = JSON.parse(route.request().postData());
      const job = {
        ...mockJobPending,
        id: jobId,
        ...updateData,
      };

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(job),
      });
    } else if (route.request().method() === 'DELETE') {
      // Mock delete job
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Job deleted successfully' }),
      });
    }
  });

  // Mock cancel job endpoint
  await page.route('**/api/jobs/*/cancel', async (route) => {
    const jobId = route.request().url().split('/')[5];
    const job = {
      ...mockJobRunning,
      id: jobId,
      status: 'cancelled',
      completed_at: new Date().toISOString(),
    };

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(job),
    });
  });
}

/**
 * Setup mock API with errors for testing error handling
 */
export async function setupMockAPIWithErrors(page) {
  // Mock 404 errors
  await page.route('**/api/jobs/nonexistent', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Job not found' }),
    });
  });

  // Mock 403 errors for file browser
  await page.route('**/api/fs/browse?path=/root', async (route) => {
    await route.fulfill({
      status: 403,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Access denied. Allowed paths: ["/mnt", "/media", "/tmp/elrond"]' }),
    });
  });

  // Mock 400 errors for invalid job creation
  await page.route('**/api/jobs', async (route) => {
    if (route.request().method() === 'POST') {
      const postData = JSON.parse(route.request().postData());

      if (!postData.source_paths || postData.source_paths.length === 0) {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Please select at least one disk or memory image' }),
        });
      } else {
        // Continue normally
        await route.continue();
      }
    }
  });

  // Mock 500 errors
  await page.route('**/api/error-test', async (route) => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Internal server error' }),
    });
  });
}

/**
 * Setup progressive job updates for testing progress monitoring
 */
export async function setupProgressiveJobUpdates(page, jobId) {
  let callCount = 0;

  await page.route(`**/api/jobs/${jobId}`, async (route) => {
    callCount++;

    let job;
    if (callCount === 1) {
      job = { ...mockJobPending, id: jobId };
    } else if (callCount <= 3) {
      job = { ...mockJobRunning, id: jobId, progress: 25 * callCount };
    } else {
      job = { ...mockJobCompleted, id: jobId };
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(job),
    });
  });
}
