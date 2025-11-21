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
        const confirmed = window.confirm(
          `A job with case ID "${caseNumber}" already exists.\n\nDo you want to overwrite the existing job and continue?`
        );

        if (confirmed) {
          // User confirmed - retry with force overwrite flag
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
            return;
          } catch (retryErr) {
            console.error('Error creating job with overwrite:', retryErr);
            setError(retryErr.response?.data?.detail || retryErr.message || 'Failed to create analysis job');
          }
        }
      }
      // Check if error is "File exists" (errno 17)
      else if (errorDetail.includes('[Errno 17]') || errorDetail.includes('File exists')) {
        // Extract the actual path from the error message
        const pathMatch = errorDetail.match(/'([^']+)'/);
        const existingPath = pathMatch ? pathMatch[1] : (destinationPath || selectedFiles[0]);

        const confirmed = window.confirm(
          `The output directory already exists:\n\n${existingPath}\n\nDo you want to delete the existing directory and continue?`
        );

        if (confirmed) {
          // User confirmed - retry with force overwrite flag
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
            return;
          } catch (retryErr) {
            console.error('Error creating job with overwrite:', retryErr);
            setError(retryErr.response?.data?.detail || retryErr.message || 'Failed to create analysis job');
          }
        }
      } else {
        setError(errorDetail);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="new-analysis">
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
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.0rem' }}>
                <label
                  style={{ display: 'flex', alignItems: 'center', cursor: isCaseNumberValid ? 'pointer' : 'not-allowed', opacity: isCaseNumberValid ? 1 : 0.5, flex: '0 0 40%', fontSize: '1.4rem' }}
                  title="Disk/Memory Images"
                >
                  <input
                    type="radio"
                    name="analysisMode"
                    value="local"
                    checked={analysisMode === 'local'}
                    onChange={(e) => setAnalysisMode(e.target.value)}
                    disabled={!isCaseNumberValid}
                    style={{ marginRight: '0.5rem', width: '16px', height: '16px' }}
                  />
                  Local Analysis
                </label>
                <label
                  style={{ display: 'flex', alignItems: 'center', cursor: isCaseNumberValid ? 'pointer' : 'not-allowed', opacity: isCaseNumberValid ? 1 : 0.5, flex: '0 0 40%', fontSize: '1.4rem' }}
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
                  Gandalf Jobs
                </label>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label>
              {analysisMode === 'local' ? 'Select Disk/Memory Images *' : 'Select Gandalf Jobs *'}
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
            <OptionsPanel
              options={options}
              onChange={handleOptionsChange}
              disabled={!isCaseNumberValid}
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
