import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileBrowser from './FileBrowser';
import GandalfJobBrowser from './GandalfJobBrowser';
import OptionsPanel from './OptionsPanel';
import { createJob } from '../api';

function NewAnalysis() {
  const navigate = useNavigate();
  const [caseNumber, setCaseNumber] = useState('');
  const [analysisMode, setAnalysisMode] = useState('local'); // 'local' or 'gandalf'
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [destinationPath, setDestinationPath] = useState('');
  const [options, setOptions] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAvWarning, setShowAvWarning] = useState(false);
  const [showOverwriteModal, setShowOverwriteModal] = useState(false);
  const [overwriteModalData, setOverwriteModalData] = useState({ type: '', message: '', path: '' });

  // Clear error when options change
  const handleOptionsChange = (newOptions) => {
    setOptions(newOptions);
    if (error) {
      setError(null);
    }
  };

  // Validate case number and get validation message
  const getCaseNumberValidation = (value) => {
    if (value.length === 0) {
      return { valid: false, message: '' };
    }

    if (value.length < 6) {
      return { valid: false, message: `Case number must be at least 6 characters (currently ${value.length})` };
    }

    if (value.length > 20) {
      return { valid: false, message: `Case number must be no longer than 20 characters (currently ${value.length})` };
    }

    const startsValid = /^[a-zA-Z0-9]/.test(value);
    if (!startsValid) {
      return { valid: false, message: 'Case number must start with a letter or number' };
    }

    const endsValid = /[a-zA-Z0-9]$/.test(value);
    if (!endsValid) {
      return { valid: false, message: 'Case number must end with a letter or number' };
    }

    const validChars = /^[a-zA-Z0-9\-._]+$/.test(value);
    if (!validChars) {
      const invalidChar = value.match(/[^a-zA-Z0-9\-._]/);
      return { valid: false, message: `Invalid character '${invalidChar ? invalidChar[0] : ''}' - only letters, numbers, hyphens, periods, and underscores allowed` };
    }

    return { valid: true, message: '' };
  };

  const caseNumberValidation = getCaseNumberValidation(caseNumber);
  const isCaseNumberValid = caseNumberValidation.valid;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!caseNumber.trim()) {
      setError('Please enter a case number');
      return;
    }

    if (!isCaseNumberValid) {
      setError('Case number must be at least 6 characters, start/end with a letter or number, and only contain letters, numbers, hyphens, periods, and underscores');
      return;
    }

    if (selectedFiles.length === 0) {
      setError('Please select at least one disk or memory image');
      return;
    }

    // Check operation mode is selected
    if (!options.collect && !options.gandalf && !options.reorganise) {
      setError('Please select an operation mode (Collect, Gandalf, or Reorganise)');
      return;
    }

    // Show AV warning modal before proceeding
    setShowAvWarning(true);
  };

  const handleAvWarningConfirm = async () => {
    setShowAvWarning(false);
    setLoading(true);
    setError(null);

    try {
      const jobData = {
        case_number: caseNumber,
        source_paths: selectedFiles,
        destination_path: destinationPath || null,
        options: {
          ...options,
          local: analysisMode === 'local',
          gandalf: analysisMode === 'gandalf',
        },
      };

      console.log('Creating job with data:', jobData);

      const job = await createJob(jobData);

      console.log('Job created successfully:', job);

      // Redirect to job details page
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      console.error('Error creating job:', err);
      console.error('Error response:', err.response);

      const errorDetail = err.response?.data?.detail || err.message || 'Failed to create analysis job';

      // Check if error is duplicate case ID
      if (errorDetail.includes('already exists')) {
        setOverwriteModalData({
          type: 'case_id',
          message: `A job with case ID "${caseNumber}" already exists.`,
          path: caseNumber
        });
        setShowOverwriteModal(true);
        return;
      }
      // Check if error is "File exists" (errno 17)
      else if (errorDetail.includes('[Errno 17]') || errorDetail.includes('File exists')) {
        // Extract the actual path from the error message
        const pathMatch = errorDetail.match(/'([^']+)'/);
        const existingPath = pathMatch ? pathMatch[1] : (destinationPath || selectedFiles[0]);

        setOverwriteModalData({
          type: 'directory',
          message: 'The output directory already exists:',
          path: existingPath
        });
        setShowOverwriteModal(true);
        return;
      } else {
        setError(errorDetail);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAvWarningCancel = () => {
    setShowAvWarning(false);
  };

  const handleOverwriteConfirm = async () => {
    setShowOverwriteModal(false);
    setLoading(true);
    setError(null);

    try {
      const job = await createJob({
        case_number: caseNumber,
        source_paths: selectedFiles,
        destination_path: destinationPath || null,
        options: {
          ...options,
          local: analysisMode === 'local',
          gandalf: analysisMode === 'gandalf',
          force_overwrite: true
        },
      });

      console.log('Job created successfully with overwrite:', job);
      navigate(`/jobs/${job.id}`);
    } catch (retryErr) {
      console.error('Error creating job with overwrite:', retryErr);
      setError(retryErr.response?.data?.detail || retryErr.message || 'Failed to create analysis job');
      setLoading(false);
    }
  };

  const handleOverwriteCancel = () => {
    setShowOverwriteModal(false);
    setLoading(false);
  };

  return (
    <div className="new-analysis">
      {/* AV Warning Modal */}
      {showAvWarning && (
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
            maxWidth: '680px',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7)'
          }}>
            <h3 style={{
              color: '#ffc107',
              marginBottom: '1rem',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1.5rem',
              textAlign: 'center'
            }}>
              ⚠️ Antivirus Warning
            </h3>
            <p style={{
              color: '#f0dba5',
              lineHeight: '1.8',
              marginBottom: '1.5rem',
              fontSize: '1rem'
            }}>
              During forensic analysis, malware or suspicious files may be identified and extracted.
              Your antivirus software may interfere with the analysis process by quarantining or deleting evidence.
            </p>
            <p style={{
              color: '#f0dba5',
              lineHeight: '1.8',
              marginBottom: '2rem',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}>
              Consider temporarily disabling antivirus protection or adding exclusions for the analysis output directory before proceeding.
            </p>
            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center'
            }}>
              <button
                onClick={handleAvWarningCancel}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(244, 67, 54, 0.2)',
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
                  e.target.style.background = 'rgba(244, 67, 54, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(244, 67, 54, 0.2)';
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleAvWarningConfirm}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(102, 217, 239, 0.3)',
                  border: '1px solid rgba(102, 217, 239, 0.5)',
                  borderRadius: '4px',
                  color: '#66d9ef',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  fontWeight: 600,
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(102, 217, 239, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(102, 217, 239, 0.3)';
                }}
              >
                Continue with Analysis
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overwrite Confirmation Modal */}
      {showOverwriteModal && (
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
            maxWidth: '680px',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7)'
          }}>
            <h3 style={{
              color: '#ffc107',
              marginBottom: '1rem',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1.5rem',
              textAlign: 'center'
            }}>
              ⚠️ Overwrite Confirmation
            </h3>
            <p style={{
              color: '#f0dba5',
              lineHeight: '1.8',
              marginBottom: '1rem',
              fontSize: '1rem'
            }}>
              {overwriteModalData.message}
            </p>
            <div style={{
              background: 'rgba(240, 219, 165, 0.1)',
              border: '1px solid rgba(240, 219, 165, 0.3)',
              borderRadius: '4px',
              padding: '0.75rem 1rem',
              marginBottom: '1.5rem',
              fontFamily: 'monospace',
              color: '#66d9ef',
              wordBreak: 'break-all'
            }}>
              {overwriteModalData.path}
            </div>
            <p style={{
              color: '#f0dba5',
              lineHeight: '1.8',
              marginBottom: '2rem',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}>
              {overwriteModalData.type === 'case_id'
                ? 'Do you want to overwrite the existing job and continue?'
                : 'Do you want to delete the existing directory and continue?'}
            </p>
            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center'
            }}>
              <button
                onClick={handleOverwriteCancel}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(244, 67, 54, 0.2)',
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
                  e.target.style.background = 'rgba(244, 67, 54, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(244, 67, 54, 0.2)';
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleOverwriteConfirm}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(255, 152, 0, 0.3)',
                  border: '1px solid rgba(255, 152, 0, 0.5)',
                  borderRadius: '4px',
                  color: '#ff9800',
                  cursor: 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif",
                  fontSize: '1rem',
                  fontWeight: 600,
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(255, 152, 0, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(255, 152, 0, 0.3)';
                }}
              >
                Overwrite and Continue
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h2>New Forensic Analysis</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="caseNumber">
                Case Number / Investigation ID *
              </label>
              <div className="input-with-icon">
                <input
                  type="text"
                  id="caseNumber"
                  value={caseNumber}
                  onChange={(e) => setCaseNumber(e.target.value)}
                  placeholder="e.g., INC-2025-001"
                  required
                  className={isCaseNumberValid ? 'valid-input' : ''}
                />
                {isCaseNumberValid && (
                  <span className="input-checkmark">✓</span>
                )}
              </div>
              {caseNumberValidation.message && (
                <div className="validation-message invalid">
                  {caseNumberValidation.message}
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Analysis Mode *</label>
              {!isCaseNumberValid && (
                <div className="info-message">
                  Please enter a valid case number to select analysis mode.
                </div>
              )}
              <div style={{ display: 'flex', gap: '3rem', marginTop: '1.0rem' }}>
                <label
                  style={{ display: 'flex', alignItems: 'center', cursor: isCaseNumberValid ? 'pointer' : 'not-allowed', opacity: isCaseNumberValid ? 1 : 0.5, fontSize: '1.2rem', whiteSpace: 'nowrap' }}
                  title="Disk/Memory Images"
                >
                  <input
                    type="radio"
                    name="analysisMode"
                    value="local"
                    checked={analysisMode === 'local'}
                    onChange={(e) => setAnalysisMode(e.target.value)}
                    disabled={!isCaseNumberValid}
                    style={{ marginLeft: '1rem', marginRight: '0.5rem', width: '16px', height: '16px' }}
                  />
                  Local Analysis
                </label>
                <label
                  style={{ display: 'flex', alignItems: 'center', cursor: isCaseNumberValid ? 'pointer' : 'not-allowed', opacity: isCaseNumberValid ? 1 : 0.5, fontSize: '1.2rem', whiteSpace: 'nowrap' }}
                  title="Gandalf Acquisition Jobs"
                >
                  <input
                    type="radio"
                    name="analysisMode"
                    value="gandalf"
                    checked={analysisMode === 'gandalf'}
                    onChange={(e) => setAnalysisMode(e.target.value)}
                    disabled={!isCaseNumberValid}
                    style={{ marginRight: '0.5rem', width: '16px', height: '16px' }}
                  />
                  Gandalf Acquisition
                </label>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label>
              {analysisMode === 'local' ? 'Select Disk/Memory Images *' : 'Select Gandalf Acquisitions *'}
            </label>
            {!isCaseNumberValid && (
              <div className="info-message">
                Please enter a valid case number to continue.
              </div>
            )}
            {analysisMode === 'local' ? (
              <FileBrowser
                onSelectFiles={setSelectedFiles}
                selectedFiles={selectedFiles}
                disabled={!isCaseNumberValid}
              />
            ) : (
              <GandalfJobBrowser
                onSelectJobs={setSelectedFiles}
                selectedJobs={selectedFiles}
                disabled={!isCaseNumberValid}
              />
            )}
          </div>

          <div className="form-group">
            <label>Processing Options</label>
            {!isCaseNumberValid && (
              <div className="info-message">
                Please enter a valid case number to configure processing options.
              </div>
            )}
            {isCaseNumberValid && selectedFiles.length === 0 && (
              <div className="info-message">
                Please select at least one disk or memory image to configure processing options.
              </div>
            )}
            <OptionsPanel
              options={options}
              onChange={handleOptionsChange}
              disabled={!isCaseNumberValid || selectedFiles.length === 0}
              hasImages={selectedFiles.length > 0}
              onSubmit={handleSubmit}
              loading={loading}
              error={error}
            />
          </div>
        </form>
      </div>
    </div>
  );
}

export default NewAnalysis;
