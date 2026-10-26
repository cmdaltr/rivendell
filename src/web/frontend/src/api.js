import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5688';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for session management
});

// Add interceptor to include auth token from localStorage if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add interceptor to handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// File System API
export const browsePath = async (path = '/') => {
  const response = await api.get('/api/fs/browse', {
    params: { path },
  });
  return response.data;
};

// Jobs API
export const createJob = async (jobData) => {
  const response = await api.post('/api/jobs', jobData);
  return response.data;
};

export const listJobs = async (status = null, limit = 50, offset = 0) => {
  const response = await api.get('/api/jobs', {
    params: { status, limit, offset },
  });
  return response.data;
};

export const getJob = async (jobId) => {
  const response = await api.get(`/api/jobs/${jobId}`);
  return response.data;
};

export const updateJob = async (jobId, updateData) => {
  const response = await api.patch(`/api/jobs/${jobId}`, updateData);
  return response.data;
};

export const deleteJob = async (jobId) => {
  const response = await api.delete(`/api/jobs/${jobId}`);
  return response.data;
};

export const cancelJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/cancel`);
  return response.data;
};

export const pauseJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/pause`);
  return response.data;
};

export const resumeJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/resume`);
  return response.data;
};

export const restartJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/restart`);
  return response.data;
};

export const confirmSudo = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/confirm-sudo`);
  return response.data;
};

export const cancelSudo = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/cancel-sudo`);
  return response.data;
};

export const bulkCancelJobs = async (jobIds) => {
  const response = await api.post('/api/jobs/bulk/cancel', jobIds);
  return response.data;
};

export const bulkDeleteJobs = async (jobIds) => {
  const response = await api.post('/api/jobs/bulk/delete', jobIds);
  return response.data;
};

export const archiveJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/archive`);
  return response.data;
};

export const unarchiveJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/unarchive`);
  return response.data;
};

export const bulkArchiveJobs = async (jobIds) => {
  const response = await api.post('/api/jobs/bulk/archive', jobIds);
  return response.data;
};

export const bulkRestartJobs = async (jobIds) => {
  const response = await api.post('/api/jobs/bulk/restart', jobIds);
  return response.data;
};

export const exportSiem = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/export-siem`);
  return response.data;
};

// Authentication API
export const register = async (userData) => {
  const response = await api.post('/api/auth/register', userData);
  return response.data;
};

export const login = async (username, password) => {
  // OAuth2 form data
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await api.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // Store token and user data
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }

  return response.data;
};

export const loginAsGuest = async () => {
  const response = await api.post('/api/auth/guest');

  // Store token and user data
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }

  return response.data;
};

export const logout = async () => {
  try {
    await api.post('/api/auth/logout');
  } finally {
    // Clear local storage regardless of API response
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const forgotPassword = async (email) => {
  const response = await api.post('/api/auth/forgot-password', { email });
  return response.data;
};

export const resetPassword = async (token, newPassword) => {
  const response = await api.post('/api/auth/reset-password', {
    token,
    new_password: newPassword,
  });
  return response.data;
};

// Helper to check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

// Helper to get stored user
export const getStoredUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// ============================================
// Mordor Datasets API
// ============================================

export const getMordorCatalog = async (params = {}) => {
  const response = await api.get('/api/mordor/catalog', { params });
  return response.data;
};

export const refreshMordorCatalog = async (force = false) => {
  const response = await api.post('/api/mordor/catalog/refresh', null, {
    params: { force }
  });
  return response.data;
};

export const getLocalMordorDatasets = async (params = {}) => {
  const response = await api.get('/api/mordor/datasets', { params });
  return response.data;
};

export const getMordorDataset = async (datasetId) => {
  const response = await api.get(`/api/mordor/datasets/${datasetId}`);
  return response.data;
};

export const downloadMordorDataset = async (datasetId, outputDir = null) => {
  const response = await api.post(`/api/mordor/datasets/${datasetId}/download`, {
    output_dir: outputDir
  });
  return response.data;
};

export const deleteMordorDataset = async (datasetId) => {
  const response = await api.delete(`/api/mordor/datasets/${datasetId}`);
  return response.data;
};

export const verifyMordorDataset = async (datasetId) => {
  const response = await api.get(`/api/mordor/datasets/${datasetId}/verify`);
  return response.data;
};

export const getMordorStats = async () => {
  const response = await api.get('/api/mordor/stats');
  return response.data;
};

// ============================================
// Aragorn (Docker administration) API
// ============================================

export const getAragornStatus = async () => (await api.get('/api/aragorn/status')).data;

export const listAragornContainers = async () => (await api.get('/api/aragorn/containers')).data;

export const listAragornImages = async () => (await api.get('/api/aragorn/images')).data;

export const getAragornLogs = async (name, tail = 200) =>
  (await api.get(`/api/aragorn/containers/${encodeURIComponent(name)}/logs`, { params: { tail } })).data;

export const getAragornStats = async (name) =>
  (await api.get(`/api/aragorn/containers/${encodeURIComponent(name)}/stats`)).data;

export const aragornContainerAction = async (name, action, force = false) =>
  (await api.post(`/api/aragorn/containers/${encodeURIComponent(name)}/${action}`, { force })).data;

export const aragornPullImage = async (ref) => (await api.post('/api/aragorn/images/pull', { ref })).data;

export const aragornRemoveImage = async (id) => (await api.post('/api/aragorn/images/remove', { id })).data;

export const aragornPruneImages = async () => (await api.post('/api/aragorn/images/prune')).data;

export const getAragornOp = async (opId) => (await api.get(`/api/aragorn/ops/${opId}`)).data;

export const listAragornOps = async () => (await api.get('/api/aragorn/ops')).data;

export default api;

// Test lab API (proxied to the lab agent on the host)
export const getLabStatus = async () => (await api.get('/api/lab/status')).data;
export const getLabState = async () => (await api.get('/api/lab/state')).data;
export const saveLabConfig = async (settings) => (await api.put('/api/lab/config', { settings })).data;
export const setLabPassword = async (password) => (await api.put('/api/lab/password', { password })).data;
export const runLabCommand = async (command, args = []) => (await api.post('/api/lab/run', { command, args })).data;
export const listLabRuns = async () => (await api.get('/api/lab/runs')).data;
export const getLabRun = async (runId, offset = 0) =>
  (await api.get(`/api/lab/runs/${runId}`, { params: { offset } })).data;
export const cancelLabRun = async (runId) => (await api.post(`/api/lab/runs/${runId}/cancel`)).data;

// Mordor: recorded attack telemetry (src/mordor/telemetry) and the lab that records it
// (src/mordor/lab, through the host's lab agent; admin-only)
export const getTelemetryStatus = async () => (await api.get('/api/mordor/telemetry/status')).data;
export const getTelemetryTechniques = async (params = {}) =>
  (await api.get('/api/mordor/telemetry/techniques', { params })).data;
export const getTelemetryTechnique = async (tid, params = {}) =>
  (await api.get(`/api/mordor/telemetry/technique/${encodeURIComponent(tid)}`, { params })).data;
export const searchTelemetry = async (q) => (await api.get('/api/mordor/telemetry/search', { params: { q } })).data;
export const updateTelemetry = async () => (await api.post('/api/mordor/telemetry/build')).data;
export const getMordorLab = async () => (await api.get('/api/mordor/lab/overview')).data;
export const getMordorLabLogs = async (engine, name) =>
  (await api.get('/api/mordor/lab/logs', { params: { engine, name } })).data;
export const getMordorLabSteps = async (os) => (await api.get('/api/mordor/lab/provision-steps', { params: { os } })).data;
export const postMordorLab = async (verb, body) => (await api.post(`/api/mordor/lab/${verb}`, body)).data;
