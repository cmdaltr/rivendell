import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getJob, cancelJob, deleteJob } from '../api';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

function JobDetails() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const logEndRef = useRef(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    loadJob();
    // Auto-refresh every 3 seconds
    const interval = setInterval(loadJob, 3000);
    return () => clearInterval(interval);
  }, [jobId]);

  // Auto-scroll to bottom of log when it updates
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [job?.log]);

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

  const handleCancel = () => {
    setShowCancelModal(true);
  };

  const handleCancelConfirm = async () => {
    setShowCancelModal(false);
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

  const handleDelete = () => {
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    setShowDeleteModal(false);
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
    // Internal options to exclude from display
    const internalOptions = ['collect', 'process', 'local', 'gandalf', 'brisk', 'force_overwrite'];

    // Special formatting for specific options
    const specialFormatting = {
      'vss': 'VSS',
      'userprofiles': 'User Profiles',
      'nsrl': 'NSRL',
      'extract_iocs': 'Extract IOCs',
      'clamav': 'ClamAV'
    };

    Object.entries(job.options).forEach(([key, value]) => {
      // Use case-insensitive comparison for internal options
      const keyLower = key.toLowerCase();
      if (value === true && !internalOptions.includes(keyLower)) {
        // Check if there's special formatting for this key (case-insensitive)
        const displayName = specialFormatting[keyLower] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        enabled.push(displayName);
      }
    });
    return enabled;
  };

  if (loading) {
    return <div className="loading">Loading job details...</div>;
  }

  if (error && !job) {
    // Select a random 404 image
    const notFoundImages = [
      'boromir404.png',
      'frodo1404.png',
      'frodo2404.png',
      'gandalf404.png',
      'gollum404.png'
    ];
    const randomImage = notFoundImages[Math.floor(Math.random() * notFoundImages.length)];
    const notFoundImageUrl = `${process.env.PUBLIC_URL}/images/404/${randomImage}`;

    return (
      <div className="job-details journey-detail">
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
          <h2>Job Not Found</h2>
          <p>The requested job could not be found. It may have been deleted or the ID is incorrect.</p>
        </header>

        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <img
            src={notFoundImageUrl}
            alt="Job Not Found"
            style={{
              maxWidth: '400px',
              width: '100%',
              height: 'auto',
              marginBottom: '2rem',
              borderRadius: '8px'
            }}
          />
          <h3 style={{ marginBottom: '1rem', color: '#f0dba5' }}>404 - Job Not Found</h3>
          <p style={{ marginBottom: '2rem', color: '#a7db6c' }}>{error}</p>
          <Link to="/jobs">
            <button>Back to Jobs</button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="job-details journey-detail">
      {/* Cancel Job Modal */}
      {showCancelModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(15, 15, 35, 0.98) 0%, rgba(25, 25, 45, 0.98) 100%)',
            border: '2px solid rgba(240, 219, 165, 0.5)',
            borderRadius: '8px',
            padding: '2rem',
            maxWidth: '500px',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7)'
          }}>
            <h3 style={{
              color: '#ffc107',
              marginBottom: '1rem',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1.5rem',
              textAlign: 'center'
            }}>
              ⚠️ Cancel Job
            </h3>
            <p style={{
              color: '#f0dba5',
              lineHeight: '1.8',
              marginBottom: '2rem',
              fontSize: '1rem',
              textAlign: 'center'
            }}>
              Are you sure you want to cancel this job?
            </p>
            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center'
            }}>
              <button
                onClick={() => setShowCancelModal(false)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(107, 142, 63, 0.3)',
                  border: '1px solid rgba(107, 142, 63, 0.5)',
                  borderRadius: '4px',
                  color: '#a7db6c',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  fontWeight: 600,
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(107, 142, 63, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(107, 142, 63, 0.3)';
                }}
              >
                No, Keep Job
              </button>
              <button
                onClick={handleCancelConfirm}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(244, 67, 54, 0.3)',
                  border: '1px solid rgba(244, 67, 54, 0.5)',
                  borderRadius: '4px',
                  color: '#f44336',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  fontWeight: 600,
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(244, 67, 54, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(244, 67, 54, 0.3)';
                }}
              >
                Yes, Cancel Job
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Job Modal */}
      {showDeleteModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(15, 15, 35, 0.98) 0%, rgba(25, 25, 45, 0.98) 100%)',
            border: '2px solid rgba(240, 219, 165, 0.5)',
            borderRadius: '8px',
            padding: '2rem',
            maxWidth: '500px',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7)'
          }}>
            <h3 style={{
              color: '#ffc107',
              marginBottom: '1rem',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1.5rem',
              textAlign: 'center'
            }}>
              ⚠️ Delete Job
            </h3>
            <p style={{
              color: '#f0dba5',
              lineHeight: '1.8',
              marginBottom: '1rem',
              fontSize: '1rem',
              textAlign: 'center'
            }}>
              Are you sure you want to delete this job?
            </p>
            <p style={{
              color: '#f44336',
              lineHeight: '1.8',
              marginBottom: '2rem',
              fontSize: '0.9rem',
              textAlign: 'center',
              fontWeight: 'bold'
            }}>
              This action cannot be undone.
            </p>
            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center'
            }}>
              <button
                onClick={() => setShowDeleteModal(false)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(107, 142, 63, 0.3)',
                  border: '1px solid rgba(107, 142, 63, 0.5)',
                  borderRadius: '4px',
                  color: '#a7db6c',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  fontWeight: 600,
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(107, 142, 63, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(107, 142, 63, 0.3)';
                }}
              >
                No, Keep Job
              </button>
              <button
                onClick={handleDeleteConfirm}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(244, 67, 54, 0.3)',
                  border: '1px solid rgba(244, 67, 54, 0.5)',
                  borderRadius: '4px',
                  color: '#f44336',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  fontWeight: 600,
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(244, 67, 54, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(244, 67, 54, 0.3)';
                }}
              >
                Yes, Delete Job
              </button>
            </div>
          </div>
        </div>
      )}

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
        <h2>Job Monitoring</h2>
        <p>Real-time monitoring of forensic analysis and artifact processing jobs.</p>
      </header>

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

        <div className="job-info-grid" style={{ display: 'grid', gridTemplateColumns: '0.8fr 0.8fr 0.8fr 1.6fr', gap: '1rem', marginBottom: '2rem' }}>
          <div className="info-item">
            <strong>Case #:</strong>
            <span>{job.case_number}</span>
          </div>
          <div className="info-item">
            <strong>Status:</strong>
            <span className={getStatusClass(job.status)} style={{ display: 'inline-block', width: '50%', textAlign: 'center' }}>{job.status}</span>
          </div>
          <div className="info-item">
            <strong>Progress:</strong>
            <div className="progress-bar" style={{ marginRight: 'auto', width: '80%' }}>
              <div
                className="progress-fill"
                style={{ width: `${job.progress}%` }}
              >
                {job.progress}%
              </div>
            </div>
          </div>
          <div className="info-item">
            <strong>Destination:</strong>
            <span style={{ fontSize: '0.85rem' }}>{job.destination_path || 'Default location'}</span>
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
              <div ref={logEndRef} />
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

export default JobDetails;
