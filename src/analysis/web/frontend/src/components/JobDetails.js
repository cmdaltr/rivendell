import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getJob, cancelJob, deleteJob } from '../api';

function JobDetails() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadJob();
    // Auto-refresh every 3 seconds
    const interval = setInterval(loadJob, 3000);
    return () => clearInterval(interval);
  }, [jobId]);

  const loadJob = async () => {
    try {
      const data = await getJob(jobId);
      setJob(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load job');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this job?')) {
      return;
    }

    setActionLoading(true);
    try {
      await cancelJob(jobId);
      await loadJob();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to cancel job');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this job? This cannot be undone.')) {
      return;
    }

    setActionLoading(true);
    try {
      await deleteJob(jobId);
      navigate('/jobs');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete job');
      setActionLoading(false);
    }
  };

  const getStatusClass = (status) => {
    return `status-badge status-${status.toLowerCase()}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (start, end) => {
    if (!start) return 'N/A';
    const startDate = new Date(start);
    const endDate = end ? new Date(end) : new Date();
    const duration = Math.floor((endDate - startDate) / 1000);

    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getEnabledOptions = () => {
    if (!job) return [];
    const enabled = [];
    Object.entries(job.options).forEach(([key, value]) => {
      if (value === true) {
        enabled.push(key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
      }
    });
    return enabled;
  };

  if (loading) {
    return <div className="loading">Loading job details...</div>;
  }

  if (error && !job) {
    return (
      <div className="card">
        <div className="error">{error}</div>
        <Link to="/jobs">
          <button>Back to Jobs</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="job-details">
      <div className="card">
        <div className="job-header">
          <div>
            <h2>Job Details</h2>
            <div className="job-id">ID: {job.id}</div>
          </div>
          <div className="job-actions">
            {(job.status === 'pending' || job.status === 'running') && (
              <button
                className="secondary"
                onClick={handleCancel}
                disabled={actionLoading}
              >
                Cancel Job
              </button>
            )}
            {(job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') && (
              <button
                className="secondary"
                onClick={handleDelete}
                disabled={actionLoading}
              >
                Delete Job
              </button>
            )}
            <Link to="/jobs">
              <button>Back to Jobs</button>
            </Link>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="job-info-grid">
          <div className="info-item">
            <strong>Case Number:</strong>
            <span>{job.case_number}</span>
          </div>
          <div className="info-item">
            <strong>Status:</strong>
            <span className={getStatusClass(job.status)}>{job.status}</span>
          </div>
          <div className="info-item">
            <strong>Progress:</strong>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${job.progress}%` }}
              >
                {job.progress}%
              </div>
            </div>
          </div>
          <div className="info-item">
            <strong>Created:</strong>
            <span>{formatDate(job.created_at)}</span>
          </div>
          <div className="info-item">
            <strong>Started:</strong>
            <span>{formatDate(job.started_at)}</span>
          </div>
          <div className="info-item">
            <strong>Completed:</strong>
            <span>{formatDate(job.completed_at)}</span>
          </div>
          <div className="info-item">
            <strong>Duration:</strong>
            <span>{formatDuration(job.started_at, job.completed_at)}</span>
          </div>
          <div className="info-item">
            <strong>Destination:</strong>
            <span>{job.destination_path || 'Default location'}</span>
          </div>
        </div>

        {job.error && (
          <div className="error-section">
            <h3>Error</h3>
            <div className="error">{job.error}</div>
          </div>
        )}

        <div className="source-paths-section">
          <h3>Source Images ({job.source_paths.length})</h3>
          <ul>
            {job.source_paths.map((path, index) => (
              <li key={index}>{path}</li>
            ))}
          </ul>
        </div>

        <div className="options-section">
          <h3>Enabled Options</h3>
          {getEnabledOptions().length > 0 ? (
            <div className="options-tags">
              {getEnabledOptions().map((option, index) => (
                <span key={index} className="option-tag">{option}</span>
              ))}
            </div>
          ) : (
            <p>No options enabled (default configuration)</p>
          )}
        </div>

        {job.result && (
          <div className="result-section">
            <h3>Results</h3>
            <div className="success">
              Analysis completed successfully!
            </div>
            <div className="result-info">
              <strong>Output Directory:</strong> {job.result.output_directory}
            </div>
          </div>
        )}

        <div className="log-section">
          <h3>Job Log ({job.log.length} entries)</h3>
          <div className="log-viewer">
            <pre>
              {job.log.length > 0
                ? job.log.join('\n')
                : 'No log entries yet...'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

export default JobDetails;
