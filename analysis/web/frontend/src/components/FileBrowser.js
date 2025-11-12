import React, { useState, useEffect } from 'react';
import { browsePath } from '../api';

function FileBrowser({ onSelectFiles, selectedFiles = [] }) {
  const [currentPath, setCurrentPath] = useState('/');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPath(currentPath);
  }, [currentPath]);

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
    <div className="file-browser-container">
      <div className="current-path">
        <strong>Current Path:</strong> {currentPath}
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
