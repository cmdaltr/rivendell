import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5688';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default api;
