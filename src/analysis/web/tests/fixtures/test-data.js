// Test Data and Fixtures for Elrond Tests

/**
 * Mock file system items for testing file browser
 */
export const mockFileSystemItems = [
  {
    name: '..',
    path: '/mnt',
    is_directory: true,
  },
  {
    name: 'evidence',
    path: '/mnt/evidence',
    is_directory: true,
  },
  {
    name: 'case-001.e01',
    path: '/mnt/case-001.e01',
    is_directory: false,
    size: 10737418240,
    modified: '2025-01-15T10:30:00',
    is_image: true,
  },
  {
    name: 'memory.raw',
    path: '/mnt/memory.raw',
    is_directory: false,
    size: 8589934592,
    modified: '2025-01-15T11:00:00',
    is_image: true,
  },
  {
    name: 'disk.dd',
    path: '/mnt/disk.dd',
    is_directory: false,
    size: 53687091200,
    modified: '2025-01-15T09:15:00',
    is_image: true,
  },
  {
    name: 'readme.txt',
    path: '/mnt/readme.txt',
    is_directory: false,
    size: 1024,
    modified: '2025-01-15T08:00:00',
    is_image: false,
  },
];

/**
 * Mock job data for testing
 */
export const mockJobPending = {
  id: 'test-job-001',
  case_number: 'INC-2025-001',
  source_paths: ['/mnt/case-001.e01'],
  destination_path: null,
  options: {
    collect: true,
    analysis: true,
    userprofiles: true,
    brisk: true,
  },
  status: 'pending',
  progress: 0,
  log: ['[2025-01-15T12:00:00] Job created'],
  result: null,
  error: null,
  created_at: '2025-01-15T12:00:00',
  started_at: null,
  completed_at: null,
};

export const mockJobRunning = {
  ...mockJobPending,
  id: 'test-job-002',
  status: 'running',
  progress: 45,
  log: [
    '[2025-01-15T12:00:00] Job created',
    '[2025-01-15T12:00:05] Starting analysis',
    '[2025-01-15T12:00:10] Mounting disk image',
    '[2025-01-15T12:01:00] Collecting artifacts...',
  ],
  started_at: '2025-01-15T12:00:05',
};

export const mockJobCompleted = {
  ...mockJobPending,
  id: 'test-job-003',
  status: 'completed',
  progress: 100,
  log: [
    '[2025-01-15T12:00:00] Job created',
    '[2025-01-15T12:00:05] Starting analysis',
    '[2025-01-15T12:00:10] Mounting disk image',
    '[2025-01-15T12:01:00] Collecting artifacts...',
    '[2025-01-15T12:30:00] Processing artifacts',
    '[2025-01-15T13:00:00] Analysis completed successfully',
  ],
  result: {
    output_directory: '/tmp/elrond/output/INC-2025-001',
    return_code: 0,
  },
  started_at: '2025-01-15T12:00:05',
  completed_at: '2025-01-15T13:00:00',
};

export const mockJobFailed = {
  ...mockJobPending,
  id: 'test-job-004',
  status: 'failed',
  progress: 25,
  log: [
    '[2025-01-15T12:00:00] Job created',
    '[2025-01-15T12:00:05] Starting analysis',
    '[2025-01-15T12:00:10] Error: Cannot mount disk image',
  ],
  error: 'Process exited with code 1',
  started_at: '2025-01-15T12:00:05',
  completed_at: '2025-01-15T12:00:10',
};

export const mockJobList = {
  jobs: [
    mockJobCompleted,
    mockJobRunning,
    mockJobPending,
    mockJobFailed,
  ],
  total: 4,
};

/**
 * Test case numbers for validation
 */
export const validCaseNumbers = [
  'INC-2025-001',
  'CASE-123',
  'INV-2025-XYZ',
  'TEST-001',
];

export const invalidCaseNumbers = [
  '',
  '   ',
];

/**
 * Analysis options presets for testing
 */
export const optionPresets = {
  minimal: {
    collect: true,
  },
  standard: {
    collect: true,
    analysis: true,
    userprofiles: true,
    brisk: true,
  },
  comprehensive: {
    collect: true,
    analysis: true,
    userprofiles: true,
    vss: true,
    timeline: true,
    memory: true,
    splunk: true,
    clamav: true,
    nsrl: true,
  },
  quick: {
    collect: true,
    process: true,
    super_quick: true,
  },
};

/**
 * Expected API response structures
 */
export const apiResponses = {
  health: {
    status: 'healthy',
    timestamp: expect.any(String),
  },
  root: {
    name: 'Elrond Web Interface',
    version: expect.any(String),
    status: 'running',
  },
};

/**
 * Test timeouts
 */
export const timeouts = {
  short: 5000,
  medium: 15000,
  long: 30000,
  veryLong: 60000,
};

/**
 * Error messages
 */
export const errorMessages = {
  noCaseNumber: 'Please enter a case number',
  noImages: 'Please select at least one disk or memory image',
  noOperationMode: 'Please select an operation mode (Collect, Gandalf, or Reorganise)',
  pathNotFound: 'Path not found',
  accessDenied: /Access denied/i,
  jobNotFound: 'Job not found',
};
