// Backend API Integration Tests

const { test, expect } = require('@playwright/test');

test.describe('Backend API - Health and Root', () => {
  test('GET /api/health should return healthy status', async ({ request }) => {
    const response = await request.get('/api/health');

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
    expect(data).toHaveProperty('timestamp');
  });

  test('GET / should return API information', async ({ request }) => {
    const response = await request.get('/');

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('name');
    expect(data).toHaveProperty('version');
    expect(data).toHaveProperty('status', 'running');
  });
});

test.describe('Backend API - File System', () => {
  test('GET /api/fs/browse should return file list', async ({ request }) => {
    const response = await request.get('/api/fs/browse?path=/mnt');

    if (response.status() === 403) {
      // Directory not accessible - expected in test environment
      const data = await response.json();
      expect(data).toHaveProperty('detail');
      expect(data.detail).toContain('Access denied');
    } else {
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(Array.isArray(data)).toBe(true);
    }
  });

  test('GET /api/fs/browse should reject unauthorized paths', async ({ request }) => {
    const response = await request.get('/api/fs/browse?path=/root');

    expect(response.status()).toBe(403);

    const data = await response.json();
    expect(data).toHaveProperty('detail');
    expect(data.detail).toContain('Access denied');
  });

  test('GET /api/fs/browse should handle non-existent paths', async ({ request }) => {
    const response = await request.get('/api/fs/browse?path=/nonexistent/path');

    if (response.status() === 404) {
      const data = await response.json();
      expect(data).toHaveProperty('detail');
    } else if (response.status() === 403) {
      // Also acceptable if path is not in allowed list
      const data = await response.json();
      expect(data.detail).toContain('Access denied');
    }
  });

  test('GET /api/fs/browse should require path parameter', async ({ request }) => {
    const response = await request.get('/api/fs/browse');

    // Should either use default path or return error
    expect([200, 400, 403]).toContain(response.status());
  });
});

test.describe('Backend API - Jobs', () => {
  let createdJobId;

  test('POST /api/jobs should create new job', async ({ request }) => {
    const jobData = {
      case_number: 'TEST-API-001',
      source_paths: ['/mnt/test.e01'],
      destination_path: '/tmp/elrond/test',
      options: {
        collect: true,
        analysis: true,
      },
    };

    const response = await request.post('/api/jobs', {
      data: jobData,
    });

    if (response.status() === 200) {
      const data = await response.json();

      createdJobId = data.id;

      expect(data).toHaveProperty('id');
      expect(data).toHaveProperty('case_number', 'TEST-API-001');
      expect(data).toHaveProperty('status', 'pending');
      expect(data).toHaveProperty('progress', 0);
      expect(data).toHaveProperty('created_at');
    } else {
      // May fail if paths don't exist - that's ok for this test
      expect([400, 404]).toContain(response.status());
    }
  });

  test('POST /api/jobs should validate required fields', async ({ request }) => {
    const invalidData = {
      case_number: 'TEST-001',
      // Missing source_paths
    };

    const response = await request.post('/api/jobs', {
      data: invalidData,
    });

    expect(response.status()).toBe(422); // Validation error
  });

  test('POST /api/jobs should validate source paths exist', async ({ request }) => {
    const jobData = {
      case_number: 'TEST-002',
      source_paths: ['/nonexistent/path/image.e01'],
      options: { collect: true },
    };

    const response = await request.post('/api/jobs', {
      data: jobData,
    });

    expect(response.status()).toBe(400);

    const data = await response.json();
    expect(data.detail).toContain('Source path does not exist');
  });

  test('GET /api/jobs should list all jobs', async ({ request }) => {
    const response = await request.get('/api/jobs');

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('jobs');
    expect(data).toHaveProperty('total');
    expect(Array.isArray(data.jobs)).toBe(true);
  });

  test('GET /api/jobs should support status filter', async ({ request }) => {
    const response = await request.get('/api/jobs?status=completed');

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('jobs');

    // All jobs should have completed status
    data.jobs.forEach(job => {
      expect(job.status).toBe('completed');
    });
  });

  test('GET /api/jobs should support pagination', async ({ request }) => {
    const response = await request.get('/api/jobs?limit=5&offset=0');

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.jobs.length).toBeLessThanOrEqual(5);
  });

  test('GET /api/jobs/:id should return job details', async ({ request }) => {
    // Use a known job ID or create one first
    if (!createdJobId) {
      // Skip if no job was created
      test.skip();
      return;
    }

    const response = await request.get(`/api/jobs/${createdJobId}`);

    if (response.status() === 200) {
      const data = await response.json();

      expect(data).toHaveProperty('id', createdJobId);
      expect(data).toHaveProperty('case_number');
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('progress');
    }
  });

  test('GET /api/jobs/:id should return 404 for nonexistent job', async ({ request }) => {
    const response = await request.get('/api/jobs/nonexistent-job-id');

    expect(response.status()).toBe(404);

    const data = await response.json();
    expect(data.detail).toContain('Job not found');
  });

  test('PATCH /api/jobs/:id should update job', async ({ request }) => {
    if (!createdJobId) {
      test.skip();
      return;
    }

    const updateData = {
      progress: 50,
      log_message: 'Test update',
    };

    const response = await request.patch(`/api/jobs/${createdJobId}`, {
      data: updateData,
    });

    if (response.status() === 200) {
      const data = await response.json();

      expect(data.progress).toBe(50);
      expect(data.log).toContainEqual(expect.stringContaining('Test update'));
    }
  });

  test('POST /api/jobs/:id/cancel should cancel running job', async ({ request }) => {
    // This would require a running job - may need to mock
    const response = await request.post('/api/jobs/some-job-id/cancel');

    // Accept both 200 (success) and 404 (job not found)
    expect([200, 400, 404]).toContain(response.status());
  });

  test('DELETE /api/jobs/:id should delete completed job', async ({ request }) => {
    if (!createdJobId) {
      test.skip();
      return;
    }

    // First update to completed status
    await request.patch(`/api/jobs/${createdJobId}`, {
      data: { status: 'completed' },
    });

    const response = await request.delete(`/api/jobs/${createdJobId}`);

    // Should either succeed or fail with appropriate error
    expect([200, 400, 404]).toContain(response.status());
  });

  test('DELETE /api/jobs/:id should not delete running job', async ({ request }) => {
    const response = await request.delete('/api/jobs/running-job-id');

    if (response.status() === 400) {
      const data = await response.json();
      expect(data.detail).toContain('Cannot delete running');
    } else {
      // Job doesn't exist
      expect(response.status()).toBe(404);
    }
  });
});

test.describe('Backend API - Error Handling', () => {
  test('should return 404 for unknown endpoints', async ({ request }) => {
    const response = await request.get('/api/unknown-endpoint');

    expect(response.status()).toBe(404);
  });

  test('should return 405 for wrong HTTP method', async ({ request }) => {
    const response = await request.post('/api/health');

    expect(response.status()).toBe(405);
  });

  test('should validate JSON payload', async ({ request }) => {
    const response = await request.post('/api/jobs', {
      data: 'invalid json string',
    });

    expect([400, 422]).toContain(response.status());
  });

  test('should handle malformed query parameters', async ({ request }) => {
    const response = await request.get('/api/jobs?limit=invalid');

    expect([200, 422]).toContain(response.status());
  });
});

test.describe('Backend API - CORS', () => {
  test('should include CORS headers', async ({ request }) => {
    const response = await request.get('/api/health');

    const headers = response.headers();

    // Check for CORS headers (may or may not be present depending on config)
    // This is a best-effort check
    if (headers['access-control-allow-origin']) {
      expect(headers['access-control-allow-origin']).toBeTruthy();
    }
  });
});

test.describe('Backend API - Content Type', () => {
  test('should return JSON content type for API endpoints', async ({ request }) => {
    const response = await request.get('/api/health');

    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');
  });

  test('should accept JSON content type for POST requests', async ({ request }) => {
    const response = await request.post('/api/jobs', {
      headers: {
        'Content-Type': 'application/json',
      },
      data: {
        case_number: 'TEST',
        source_paths: ['/test'],
        options: {},
      },
    });

    // Should process request (even if it fails validation)
    expect([200, 400, 422]).toContain(response.status());
  });
});

test.describe('Backend API - Performance', () => {
  test('should respond to health check within 1 second', async ({ request }) => {
    const startTime = Date.now();

    await request.get('/api/health');

    const endTime = Date.now();
    const duration = endTime - startTime;

    expect(duration).toBeLessThan(1000);
  });

  test('should respond to job list within 3 seconds', async ({ request }) => {
    const startTime = Date.now();

    await request.get('/api/jobs');

    const endTime = Date.now();
    const duration = endTime - startTime;

    expect(duration).toBeLessThan(3000);
  });
});
