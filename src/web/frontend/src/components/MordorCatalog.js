import React, { useState, useEffect } from 'react';
import { getMordorCatalog, downloadMordorDataset } from '../api';

const MordorCatalog = ({ onDownloadComplete, search = '', showDownloadedOnly = false }) => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [platform, setPlatform] = useState('');
  const [tactic, setTactic] = useState('');

  // Statistics
  const [stats, setStats] = useState({ platforms: {}, tactics: {}, total: 0 });

  // Selected datasets
  const [selectedDatasets, setSelectedDatasets] = useState([]);
  const [downloading, setDownloading] = useState({});

  useEffect(() => {
    loadCatalog();
  }, [platform, tactic, search]);

  const loadCatalog = async () => {
    try {
      setLoading(true);
      const params = {};
      if (platform) params.platform = platform;
      if (tactic) params.tactic = tactic;
      if (search) params.search = search;

      params.limit = 200; // Request all datasets
      const result = await getMordorCatalog(params);
      setDatasets(result.datasets);
      setStats({
        platforms: result.platforms || {},
        tactics: result.tactics || {},
        total: result.total
      });
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load catalog');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (datasetId) => {
    try {
      setDownloading(prev => ({ ...prev, [datasetId]: true }));
      await downloadMordorDataset(datasetId);

      // Refresh to show updated status
      await loadCatalog();
      onDownloadComplete?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start download');
    } finally {
      setDownloading(prev => ({ ...prev, [datasetId]: false }));
    }
  };

  const handleBulkDownload = async () => {
    for (const datasetId of selectedDatasets) {
      await handleDownload(datasetId);
    }
    setSelectedDatasets([]);
  };

  const toggleSelect = (datasetId) => {
    setSelectedDatasets(prev =>
      prev.includes(datasetId)
        ? prev.filter(id => id !== datasetId)
        : [...prev, datasetId]
    );
  };

  const getPlatformIcon = (platformName) => {
    const platformImages = {
      'windows': `${process.env.PUBLIC_URL}/images/windows.png`,
      'linux': `${process.env.PUBLIC_URL}/images/linux.png`,
      'macos': `${process.env.PUBLIC_URL}/images/macos.png`,
      'aws': `${process.env.PUBLIC_URL}/images/aws.png`,
      'azure': `${process.env.PUBLIC_URL}/images/azure.png`,
    };

    const key = platformName?.toLowerCase();
    const imageSrc = platformImages[key];

    if (imageSrc) {
      return (
        <img
          src={imageSrc}
          alt={platformName}
          title={platformName}
          style={{ height: '36px', width: 'auto' }}
        />
      );
    }
    return platformName;
  };

  const getStatusBadge = (status) => {
    const styles = {
      available: { background: 'rgba(240, 219, 165, 0.2)', color: '#f0dba5' },
      downloading: { background: 'rgba(102, 217, 239, 0.2)', color: '#66d9ef' },
      downloaded: { background: 'rgba(167, 219, 108, 0.2)', color: '#a7db6c' },
      failed: { background: 'rgba(244, 67, 54, 0.2)', color: '#f44336' }
    };

    return (
      <span style={{
        ...styles[status] || styles.available,
        padding: '0.25rem 0.5rem',
        borderRadius: '4px',
        fontSize: '0.8rem',
        textTransform: 'uppercase'
      }}>
        {status}
      </span>
    );
  };

  if (loading && datasets.length === 0) {
    return <div className="loading">Loading catalog...</div>;
  }

  // Filter datasets based on showDownloadedOnly toggle
  const filteredDatasets = showDownloadedOnly
    ? datasets.filter(ds => ds.status === 'downloaded')
    : datasets;

  return (
    <div>
      {/* Filters */}
      <div className="dropdown-row" style={{ marginBottom: '1rem' }}>
        <select
          className="large-select"
          value={platform}
          onChange={(e) => setPlatform(e.target.value)}
        >
          <option value="">All Platforms</option>
          {Object.entries(stats.platforms).map(([p, count]) => (
            <option key={p} value={p}>{p} ({count})</option>
          ))}
        </select>

        <select
          className="large-select"
          value={tactic}
          onChange={(e) => setTactic(e.target.value)}
        >
          <option value="">All Tactics</option>
          {Object.entries(stats.tactics).sort().map(([t, count]) => (
            <option key={t} value={t}>{t} ({count})</option>
          ))}
        </select>
      </div>

      {selectedDatasets.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <button
            onClick={handleBulkDownload}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(102, 217, 239, 0.3)',
              color: '#66d9ef',
              border: '1px solid #5ac8d8',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Download Selected ({selectedDatasets.length})
          </button>
        </div>
      )}

      {error && <div className="error" style={{ marginBottom: '1rem' }}>{error}</div>}

      {/* Results */}
      <div style={{ marginBottom: '0.5rem', color: '#888' }}>
        Showing {filteredDatasets.length} of {stats.total} datasets
        {showDownloadedOnly && ' (downloaded only)'}
      </div>

      <div className="table-container" style={{ fontSize: '1.1rem' }}>
        <table>
          <thead>
            <tr>
              <th style={{ width: '5%' }}>
                <input
                  type="checkbox"
                  checked={selectedDatasets.length === filteredDatasets.length && filteredDatasets.length > 0}
                  onChange={() => {
                    if (selectedDatasets.length === filteredDatasets.length) {
                      setSelectedDatasets([]);
                    } else {
                      setSelectedDatasets(filteredDatasets.map(d => d.dataset_id));
                    }
                  }}
                />
              </th>
              <th style={{ width: '15%' }}>ID</th>
              <th style={{ width: '35%' }}>Title</th>
              <th style={{ width: '10%' }}>Platform</th>
              <th style={{ width: '15%' }}>Tactics</th>
              <th style={{ width: '15%' }}>Status</th>
              <th style={{ width: '15%' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredDatasets.map(ds => (
              <tr key={ds.dataset_id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedDatasets.includes(ds.dataset_id)}
                    onChange={() => toggleSelect(ds.dataset_id)}
                  />
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                  {ds.dataset_id}
                </td>
                <td>
                  <strong>{ds.title}</strong>
                  {ds.techniques && ds.techniques.length > 0 && (
                    <div style={{ fontSize: '1rem', color: '#888', marginTop: '0.25rem' }}>
                      {ds.techniques.slice(0, 3).join(', ')}
                      {ds.techniques.length > 3 && ` +${ds.techniques.length - 3} more`}
                    </div>
                  )}
                </td>
                <td style={{ textAlign: 'center' }}>{getPlatformIcon(ds.platform)}</td>
                <td style={{ fontSize: '1rem' }}>
                  {ds.tactics && ds.tactics.slice(0, 2).join(', ')}
                  {ds.tactics && ds.tactics.length > 2 && '...'}
                </td>
                <td>{getStatusBadge(ds.status)}</td>
                <td>
                  {ds.status === 'available' && (
                    <button
                      onClick={() => handleDownload(ds.dataset_id)}
                      disabled={downloading[ds.dataset_id]}
                      style={{
                        padding: '0.4rem 0.8rem',
                        fontSize: '0.85rem'
                      }}
                    >
                      {downloading[ds.dataset_id] ? 'Starting...' : 'Download'}
                    </button>
                  )}
                  {ds.status === 'downloading' && (
                    <span style={{ color: '#66d9ef' }}>
                      {ds.download_progress || 0}%
                    </span>
                  )}
                  {ds.status === 'downloaded' && (
                    <span style={{ color: '#a7db6c' }}>Ready</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredDatasets.length === 0 && !loading && (
        <div className="empty-state">
          <p>No datasets found matching your criteria.</p>
          <p style={{ color: '#888' }}>
            {showDownloadedOnly
              ? 'No downloaded datasets yet. Download some from the catalog.'
              : 'Try adjusting your filters or refresh the catalog.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default MordorCatalog;
