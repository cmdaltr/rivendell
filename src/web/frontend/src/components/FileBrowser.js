import React, { useState, useEffect } from 'react';
import { browsePath } from '../api';

function FileBrowser({ onSelectFiles, selectedFiles = [], disabled = false }) {
  const [currentPath, setCurrentPath] = useState(null);
  const [allowedPaths, setAllowedPaths] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch allowed paths on mount
  useEffect(() => {
    fetchAllowedPaths();
  }, []);

  useEffect(() => {
    if (currentPath) {
      loadPath(currentPath);
    }
  }, [currentPath]);

  const fetchAllowedPaths = async () => {
    try {
      // Detect OS and set allowed paths
      const isWindows = navigator.platform.toLowerCase().includes('win');
      const isMac = navigator.platform.toLowerCase().includes('mac');

      let paths;
      if (isWindows) {
        paths = ['C:\\Temp\\rivendell', 'D:\\Temp\\rivendell', 'E:\\Temp\\rivendell', 'F:\\Temp\\rivendell'];
      } else if (isMac) {
        // Mac: /host/tmp/rivendell for host /tmp access, /Volumes for external drives
        paths = ['/host/tmp/rivendell', '/Volumes'];
      } else {
        // Linux: native uses /tmp/rivendell, Docker uses /host/tmp (for Docker on Mac)
        paths = ['/Volumes', '/mnt', '/media', '/tmp/rivendell'];
      }

      setAllowedPaths(paths);

      // Set first available path as default
      if (paths.length > 0) {
        setCurrentPath(paths[0]);
      }
    } catch (err) {
      setError('Failed to initialize file browser');
    }
  };

  const loadPath = async (path) => {
    setLoading(true);
    setError(null);

    try {
      const data = await browsePath(path);
      setItems(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load directory');
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item) => {
    if (disabled) return;

    if (item.is_directory) {
      setCurrentPath(item.path);
    } else {
      // Toggle file selection
      const isSelected = selectedFiles.includes(item.path);
      if (isSelected) {
        onSelectFiles(selectedFiles.filter(p => p !== item.path));
      } else {
        onSelectFiles([...selectedFiles, item.path]);
      }
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return '';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className={`file-browser-container ${disabled ? 'disabled' : ''}`}>
      {allowedPaths.length > 1 && (
        <div className="path-selector">
          <label htmlFor="pathSelect">Select Root Directory:</label>
          <select
            id="pathSelect"
            value={currentPath || ''}
            onChange={(e) => setCurrentPath(e.target.value)}
            disabled={disabled}
          >
            {allowedPaths.map((path) => (
              <option key={path} value={path}>
                {path}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="current-path" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong>Current Path:</strong> {currentPath || 'Loading...'}
        </div>
        <button
          onClick={() => currentPath && loadPath(currentPath)}
          disabled={disabled || loading}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            border: '1px solid #3f4b2a',
            background: 'rgba(240, 219, 165, 0.1)',
            color: '#f0dba5',
            cursor: disabled || loading ? 'not-allowed' : 'pointer',
            fontFamily: "'Cinzel', 'Times New Roman', serif",
            fontSize: '0.9rem',
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => !disabled && !loading && (e.target.style.background = 'rgba(240, 219, 165, 0.2)')}
          onMouseOut={(e) => (e.target.style.background = 'rgba(240, 219, 165, 0.1)')}
        >
          Refresh
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="file-browser">
          {items.map((item, index) => (
            <div
              key={index}
              className={`file-item ${
                selectedFiles.includes(item.path) ? 'selected' : ''
              } ${item.is_image ? 'image' : ''}`}
              onClick={() => handleItemClick(item)}
            >
              <span className="file-icon">
                {item.name === '..' ? '⬆️' : item.is_directory ? '📁' : item.is_image ? '💿' : '📄'}
              </span>
              <div className="file-info">
                <div className="file-name">{item.name}</div>
                {!item.is_directory && item.size && (
                  <div className="file-details">
                    {formatSize(item.size)} • {formatDate(item.modified)}
                  </div>
                )}
              </div>
              {item.is_image && (
                <span className="image-badge">IMAGE</span>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h4>Selected Files ({selectedFiles.length}):</h4>
          <ul>
            {selectedFiles.map((path, index) => (
              <li key={index}>{path}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default FileBrowser;
