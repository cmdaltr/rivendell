import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getJob, cancelJob, deleteJob, restartJob, exportSiem } from '../api';

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
      logEndRef.current.scrollTop = logEndRef.current.scrollHeight;
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

  const handleRestart = async () => {
    setActionLoading(true);
    try {
      await restartJob(jobId);
      await loadJob();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to restart job');
    } finally {
      setActionLoading(false);
    }
  };

  const handleExportSiem = async () => {
    setActionLoading(true);
    try {
      await exportSiem(jobId);
      // Reload job to get updated logs
      await loadJob();
      alert('SIEM export started! Check the job log for progress.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to export SIEM data');
      alert('SIEM export failed: ' + (err.response?.data?.detail || 'Unknown error'));
    } finally {
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

  const downloadLog = () => {
    if (!job || !job.log || job.log.length === 0) return;

    const logText = job.log.join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `job-${job.id}-log.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
      'clamav': 'ClamAV',
      'splunk': 'Splunk',
      'elastic': 'Elastic',
      'navigator': 'Navigator'
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
              maxWidth: '900px',
              width: '100%',
              height: 'auto',
              marginBottom: '2rem',
              borderRadius: '8px'
            }}
          />
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
            {(job.status === 'failed' || job.status === 'cancelled' || job.status === 'completed') && (
              <>
                <button
                  onClick={handleRestart}
                  disabled={actionLoading}
                  style={{
                    background: 'rgba(107, 142, 63, 0.3)',
                    border: '1px solid rgba(107, 142, 63, 0.5)',
                    color: '#a7db6c'
                  }}
                >
                  Restart Job
                </button>
                <button
                  className="secondary"
                  onClick={handleDelete}
                  disabled={actionLoading}
                >
                  Delete Job
                </button>
              </>
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

        <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="source-paths-section" style={{ flex: '1', minWidth: '0' }}>
            <h3>Source Images ({job.source_paths.length})</h3>
            <ul>
              {job.source_paths.map((path, index) => (
                <li key={index}>{path}</li>
              ))}
            </ul>
          </div>

          <div className="options-section" style={{ flex: '1', minWidth: '0' }}>
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
        </div>

        {job.result && job.status === 'completed' && (
          <div className="result-section">
            <h3>Results</h3>
            <div className="success">
              Analysis completed successfully!
            </div>
            <div className="result-info">
              <strong>Output Directory:</strong> {job.result.output_directory}
            </div>

            {/* SIEM Quick Access Links */}
            {(job.options?.splunk || job.options?.elastic || job.options?.navigator) && (
              <div style={{ marginTop: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
                  {/* Splunk */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '1rem', background: job.options?.splunk ? 'rgba(255, 107, 157, 0.1)' : 'rgba(60, 60, 80, 0.3)', border: `1px solid ${job.options?.splunk ? 'rgba(255, 107, 157, 0.3)' : 'rgba(80, 80, 100, 0.3)'}`, borderRadius: '4px', opacity: job.options?.splunk ? 1 : 0.4, cursor: job.options?.splunk ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}
                       onClick={() => job.options?.splunk && window.open('http://localhost:7755', '_blank')}>
                    <svg width="32" height="32" viewBox="0 0 100 100" fill="none" style={{ marginBottom: '0.5rem' }}>
                      <defs>
                        <radialGradient id="splunkGradient" cx="30%" cy="30%">
                          <stop offset="0%" style={{ stopColor: '#FF6B9D', stopOpacity: 1 }} />
                          <stop offset="50%" style={{ stopColor: '#E91E8C', stopOpacity: 1 }} />
                          <stop offset="100%" style={{ stopColor: '#C4166C', stopOpacity: 1 }} />
                        </radialGradient>
                      </defs>
                      <circle cx="50" cy="50" r="48" fill="url(#splunkGradient)"/>
                      <path d="M45 35 L60 50 L45 65" stroke="white" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                    </svg>
                    <span style={{ color: job.options?.splunk ? '#f0dba5' : '#666', fontSize: '0.95rem', fontWeight: '500' }}>Splunk</span>
                  </div>

                  {/* Elastic/Kibana */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '1rem', background: job.options?.elastic ? 'rgba(0, 191, 179, 0.1)' : 'rgba(60, 60, 80, 0.3)', border: `1px solid ${job.options?.elastic ? 'rgba(0, 191, 179, 0.3)' : 'rgba(80, 80, 100, 0.3)'}`, borderRadius: '4px', opacity: job.options?.elastic ? 1 : 0.4, cursor: job.options?.elastic ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}
                       onClick={() => job.options?.elastic && window.open('http://localhost:5601/app/discover#/', '_blank')}>
                    <svg width="32" height="32" viewBox="0 0 100 100" fill="none" style={{ marginBottom: '0.5rem' }}>
                      <defs>
                        <linearGradient id="elasticYellow" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" style={{ stopColor: '#FED10A', stopOpacity: 1 }} />
                          <stop offset="100%" style={{ stopColor: '#FDB42F', stopOpacity: 1 }} />
                        </linearGradient>
                        <linearGradient id="elasticTeal" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" style={{ stopColor: '#00BFB3', stopOpacity: 1 }} />
                          <stop offset="100%" style={{ stopColor: '#00A9A5', stopOpacity: 1 }} />
                        </linearGradient>
                        <linearGradient id="elasticBlue" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" style={{ stopColor: '#24BBB1', stopOpacity: 1 }} />
                          <stop offset="100%" style={{ stopColor: '#0077CC', stopOpacity: 1 }} />
                        </linearGradient>
                      </defs>
                      <rect x="10" y="20" width="70" height="12" rx="6" fill="url(#elasticYellow)"/>
                      <rect x="15" y="44" width="70" height="12" rx="6" fill="url(#elasticTeal)"/>
                      <rect x="20" y="68" width="70" height="12" rx="6" fill="url(#elasticBlue)"/>
                    </svg>
                    <span style={{ color: job.options?.elastic ? '#f0dba5' : '#666', fontSize: '0.95rem', fontWeight: '500' }}>Elastic</span>
                  </div>

                  {/* Navigator */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '1rem', background: job.options?.navigator ? 'rgba(254, 209, 10, 0.1)' : 'rgba(60, 60, 80, 0.3)', border: `1px solid ${job.options?.navigator ? 'rgba(254, 209, 10, 0.3)' : 'rgba(80, 80, 100, 0.3)'}`, borderRadius: '4px', opacity: job.options?.navigator ? 1 : 0.4, cursor: job.options?.navigator ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}
                       onClick={async () => {
                         if (job.options?.navigator) {
                           // Open ATT&CK Navigator with the job's layer file
                           // Navigator uses URL fragment to load layers: /#layerURL=<encoded-url>
                           const layerUrl = `http://localhost:5602/assets/${job.case_number}.json`;
                           const encodedLayerUrl = encodeURIComponent(layerUrl);
                           window.open(`http://localhost:5602/#layerURL=${encodedLayerUrl}`, '_blank');
                         }
                       }}>
                    <svg width="32" height="32" viewBox="0 0 100 100" fill="none" style={{ marginBottom: '0.5rem' }}>
                      <defs>
                        <linearGradient id="mitreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" style={{ stopColor: '#FFD700', stopOpacity: 1 }} />
                          <stop offset="50%" style={{ stopColor: '#FFC107', stopOpacity: 1 }} />
                          <stop offset="100%" style={{ stopColor: '#FF9800', stopOpacity: 1 }} />
                        </linearGradient>
                      </defs>
                      <path d="M50 10 L85 25 L85 50 Q85 75 50 90 Q15 75 15 50 L15 25 Z" fill="url(#mitreGradient)"/>
                      <circle cx="50" cy="50" r="22" fill="none" stroke="white" strokeWidth="3"/>
                      <circle cx="50" cy="50" r="14" fill="none" stroke="white" strokeWidth="3"/>
                      <circle cx="50" cy="50" r="6" fill="white"/>
                      <line x1="50" y1="28" x2="50" y2="38" stroke="white" strokeWidth="2"/>
                      <line x1="50" y1="62" x2="50" y2="72" stroke="white" strokeWidth="2"/>
                      <line x1="28" y1="50" x2="38" y2="50" stroke="white" strokeWidth="2"/>
                      <line x1="62" y1="50" x2="72" y2="50" stroke="white" strokeWidth="2"/>
                    </svg>
                    <span style={{ color: job.options?.navigator ? '#f0dba5' : '#666', fontSize: '0.95rem', fontWeight: '500' }}>Navigator</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="log-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Job Log ({job.log.length} entries)</h3>
            {job.log.length > 0 && (
              <button
                onClick={downloadLog}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(107, 142, 63, 0.3)',
                  border: '1px solid rgba(107, 142, 63, 0.5)',
                  borderRadius: '4px',
                  color: '#a7db6c',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '0.9rem',
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
                Download Log
              </button>
            )}
          </div>
          <div className="log-viewer" ref={logEndRef}>
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
