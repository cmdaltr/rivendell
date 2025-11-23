import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listJobs } from '../api';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

function JobList() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState(null);
  const [selectedJobs, setSelectedJobs] = useState([]);

  useEffect(() => {
    loadJobs();
    // Auto-refresh every 5 seconds
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  const loadJobs = async () => {
    try {
      const data = await listJobs(statusFilter);
      setJobs(data.jobs);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load jobs');
    } finally {
      setLoading(false);
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
    if (duration < 3600) return `${Math.floor(duration / 60)}m`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  const handleSelectJob = (jobId) => {
    setSelectedJobs(prev =>
      prev.includes(jobId)
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    );
  };

  const handleSelectAll = () => {
    if (selectedJobs.length === jobs.length) {
      setSelectedJobs([]);
    } else {
      setSelectedJobs(jobs.map(job => job.id));
    }
  };

  const handleBulkDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete ${selectedJobs.length} job(s)?`)) {
      return;
    }
    // TODO: Implement bulk delete API call
    alert('Bulk delete functionality will be implemented');
    setSelectedJobs([]);
  };

  const handleBulkExport = () => {
    // TODO: Implement bulk export functionality
    alert('Bulk export functionality will be implemented');
  };

  const handleBulkArchive = () => {
    // TODO: Implement bulk archive functionality
    alert('Bulk archive functionality will be implemented');
  };

  const handleBulkRestart = () => {
    // TODO: Implement bulk restart functionality
    alert('Bulk restart functionality will be implemented');
  };

  if (loading) {
    return <div className="loading">Loading jobs...</div>;
  }

  return (
    <div className="job-list journey-detail">
      <section className="hero-section">
        <img
          src={heroImage}
          alt="Rivendell - The Last Homely House"
          className="hero-image"
          style={{
            transform: 'scale(0.2)',
            transformOrigin: 'center top'
          }}
        />
      </section>

      <header>
        <h2>Analysis Jobs</h2>
        <p>Monitor and manage all forensic analysis and artifact processing jobs.</p>
      </header>

      <div className="card">
        <div className="list-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="filter-controls">
            <label>Filter by status:</label>
            <select
              value={statusFilter || ''}
              onChange={(e) => setStatusFilter(e.target.value || null)}
            >
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {selectedJobs.length > 0 && (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => handleBulkRestart()}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(102, 217, 239, 0.3)',
                  color: '#66d9ef',
                  border: '1px solid #5ac8d8',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  minWidth: '140px'
                }}
              >
                Restart ({selectedJobs.length})
              </button>
              <button
                onClick={() => handleBulkExport()}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(107, 142, 63, 0.3)',
                  color: '#a7db6c',
                  border: '1px solid #6b8e3f',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  minWidth: '140px'
                }}
              >
                Export ({selectedJobs.length})
              </button>
              <button
                onClick={() => handleBulkArchive()}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(240, 219, 165, 0.1)',
                  color: '#f0dba5',
                  border: '1px solid #8a7a5a',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  minWidth: '140px'
                }}
              >
                Archive ({selectedJobs.length})
              </button>
              <button
                onClick={() => handleBulkDelete()}
                style={{
                  padding: '0.5rem 1rem',
                  background: '#8b4513',
                  color: '#f0dba5',
                  border: '1px solid #654321',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  minWidth: '140px'
                }}
              >
                Delete ({selectedJobs.length})
              </button>
            </div>
          )}
            <Link to="/archive">
              <button
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(107, 142, 63, 0.3)',
                  color: '#a7db6c',
                  border: '1px solid #6b8e3f',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  minWidth: '140px',
                  boxSizing: 'border-box'
                }}
              >
                <span style={{ fontSize: '0.6rem' }}>📦</span> Archived Jobs
              </button>
            </Link>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {jobs.length === 0 ? (
          <div className="empty-state">
            <p>No jobs found.</p>
            <Link to="/">
              <button>Start New Analysis</button>
            </Link>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ width: '5%' }}>
                    <input
                      type="checkbox"
                      checked={selectedJobs.length === jobs.length && jobs.length > 0}
                      onChange={handleSelectAll}
                      style={{ cursor: 'pointer' }}
                    />
                  </th>
                  <th style={{ width: '22%' }}>Case ID</th>
                  <th style={{ width: '14%' }}>Status</th>
                  <th style={{ width: '16%' }}>Progress</th>
                  <th style={{ width: '16%', paddingLeft: '2rem' }}>Created</th>
                  <th style={{ width: '16%', paddingLeft: '2rem' }}>Duration</th>
                  <th style={{ width: '9%' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(job => (
                  <tr key={job.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedJobs.includes(job.id)}
                        onChange={() => handleSelectJob(job.id)}
                        style={{ cursor: 'pointer' }}
                      />
                    </td>
                    <td>
                      <Link to={`/jobs/${job.id}`}>
                        <strong>{job.case_number}</strong>
                      </Link>
                      <div style={{ fontSize: '0.875rem', color: '#888' }}>
                        {job.source_paths.length} image(s)
                      </div>
                    </td>
                    <td>
                      <span className={getStatusClass(job.status)}>
                        {job.status}
                      </span>
                    </td>
                    <td>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${job.progress}%` }}
                        >
                          {job.progress > 10 && `${job.progress}%`}
                        </div>
                      </div>
                    </td>
                    <td style={{ paddingLeft: '2rem' }}>{formatDate(job.created_at)}</td>
                    <td style={{ paddingLeft: '2rem' }}>{formatDuration(job.started_at, job.completed_at)}</td>
                    <td>
                      <Link to={`/jobs/${job.id}`}>
                        <button>Details</button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default JobList;
