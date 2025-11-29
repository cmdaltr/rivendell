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

export const restartJob = async (jobId) => {
  const response = await api.post(`/api/jobs/${jobId}/restart`);
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

export default api;
