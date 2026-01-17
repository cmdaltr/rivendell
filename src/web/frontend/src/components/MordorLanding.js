import React, { useState, useEffect } from 'react';
import MordorCatalog from './MordorCatalog';
import { getLocalMordorDatasets, refreshMordorCatalog } from '../api';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

const MordorLanding = () => {
  const [localCount, setLocalCount] = useState(0);
  const [search, setSearch] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [catalogKey, setCatalogKey] = useState(0);
  const [showDownloadedOnly, setShowDownloadedOnly] = useState(false);

  useEffect(() => {
    loadLocalCount();
    const interval = setInterval(loadLocalCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadLocalCount = async () => {
    try {
      const result = await getLocalMordorDatasets({ limit: 1 });
      setLocalCount(result.total);
    } catch (err) {
      console.error('Failed to load local dataset count:', err);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await refreshMordorCatalog(true);
      setCatalogKey(prev => prev + 1);
    } catch (err) {
      console.error('Failed to refresh catalog:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const toggleStyle = (isActive) => ({
    padding: '0.75rem 1.5rem',
    background: isActive
      ? 'rgba(102, 217, 239, 0.3)'
      : 'rgba(240, 219, 165, 0.1)',
    border: isActive
      ? '1px solid rgba(102, 217, 239, 0.5)'
      : '1px solid rgba(240, 219, 165, 0.2)',
    borderRadius: '4px',
    color: isActive ? '#66d9ef' : '#f0dba5',
    cursor: 'pointer',
    fontFamily: "'Cinzel', 'Times New Roman', serif",
    fontSize: '1rem',
    transition: 'all 0.3s ease'
  });

  return (
    <div className="journey-detail">
      <section className="hero-section">
        <img
          src={heroImage}
          alt="Mordor Recordings"
          className="hero-image"
          style={{
            transform: 'scale(0.2)',
            transformOrigin: 'center top'
          }}
        />
      </section>

      <header>
        <h2>Mordor Recordings</h2>
        <p>
          Access pre-recorded security event datasets from the OTRF Security Datasets
          project for threat research, detection development, and testing.
        </p>
      </header>

      <div className="card">
        {/* Tab Navigation */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '1.5rem',
          borderBottom: '1px solid rgba(240, 219, 165, 0.2)',
          paddingBottom: '1rem',
          alignItems: 'center'
        }}>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'rgba(107, 142, 63, 0.3)',
              border: '1px solid #6b8e3f',
              borderRadius: '4px',
              color: '#a7db6c',
              cursor: refreshing ? 'wait' : 'pointer',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1rem',
              transition: 'all 0.3s ease'
            }}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={() => setShowDownloadedOnly(!showDownloadedOnly)}
            style={toggleStyle(showDownloadedOnly)}
          >
            Downloaded ({localCount})
          </button>
          <input
            type="text"
            placeholder="Search datasets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ flex: 1 }}
          />
        </div>

        {/* Catalog Content */}
        <MordorCatalog
          key={catalogKey}
          onDownloadComplete={loadLocalCount}
          search={search}
          showDownloadedOnly={showDownloadedOnly}
        />
      </div>

      {/* Info Section */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h3>About OTRF Security Datasets</h3>
        <p style={{ color: '#888', marginBottom: '1rem' }}>
          The Open Threat Research Forge (OTRF) Security Datasets project provides
          pre-recorded security events from simulated adversarial techniques. These
          datasets are organized by MITRE ATT&CK tactics and can be used for:
        </p>
        <ul style={{ color: '#888', marginLeft: '1.5rem' }}>
          <li>Detection rule development and testing</li>
          <li>Threat hunting hypothesis validation</li>
          <li>Security analyst training</li>
          <li>SIEM integration testing</li>
        </ul>
        <p style={{ marginTop: '1rem' }}>
          <a
            href="https://github.com/OTRF/Security-Datasets"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#a7db6c' }}
          >
            View on GitHub
          </a>
        </p>

        <h4 style={{ marginTop: '1.5rem' }}>Using Mordor Datasets with Rivendell</h4>
        <p style={{ color: '#888', marginBottom: '0.5rem' }}>
          After downloading a dataset, you can process it with the Elrond analysis engine:
        </p>
        <pre style={{
          background: 'rgba(0, 0, 0, 0.3)',
          padding: '1rem',
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '0.9rem',
          overflow: 'auto'
        }}>
{`# Process a Mordor dataset
python elrond.py CASE001 /tmp/rivendell/mordor/SDWIN-xxx --Mordor --Process

# Or with full analysis
python elrond.py CASE001 /tmp/rivendell/mordor/SDWIN-xxx --Mordor --ThreatHunt`}
        </pre>
      </div>
    </div>
  );
};

export default MordorLanding;
