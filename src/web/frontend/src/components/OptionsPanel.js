import React, { useState, useEffect } from 'react';

function OptionsPanel({ options, onChange, disabled = false, hasImages = false, onSubmit, loading = false, error = null }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [operationMode, setOperationMode] = useState(''); // 'gandalf' or 'local'
  const [eta, setEta] = useState(0);
  const [gollumStep, setGollumStep] = useState(null); // Which step Gollum appears on

  // Step definitions in order
  const steps = [
    {
      key: 'mode',
      title: 'Mode',
      description: 'Choose your processing mode',
      type: 'single',
      options: [
        { key: 'brisk', label: 'Brisk', description: 'Optimized processing that balances speed and thoroughness', time: -30 },
        { key: 'exhaustive', label: 'Exhaustive', description: 'Enable all available options for maximum thoroughness' },
        { key: 'custom', label: 'Custom', description: 'Full control over all processing options' },
      ],
    },
    {
      key: 'collection',
      title: 'Collection',
      description: 'What to collect from the images',
      type: 'multi',
      options: [
        { key: 'collect_files', label: 'Collect Files', description: 'Collect files (binaries, documents, scripts)', time: 15 },
        { key: 'userprofiles', label: 'User Profiles', description: 'Collect user profiles\n(if available)', time: 10 },
        { key: 'vss', label: 'Volume Shadow Copies', description: 'Process VSS images\n(if available)', time: 30 },
        { key: 'symlinks', label: 'Follow Symlinks', description: 'Follow shortcuts/aliases/\nsymbolic links', time: 45, slow: true },
      ],
    },
    {
      key: 'verification',
      title: 'Metadata',
      description: 'File metadata and verification options',
      type: 'multi',
      options: [
        { key: 'last_access_times', label: 'Last Access Times', description: 'Obtain last access times of all files', time: 8 },
        { key: 'metacollected', label: 'Hash Only', description: 'Only hash collected artifacts', time: 5 },
        { key: 'nsrl', label: 'NSRL', description: 'Compare hashes against NSRL database', time: 20 },
        { key: 'imageinfo', label: 'Image Info', description: 'Extract E01 metadata information', time: 3, disabledForGandalf: true },
      ],
    },
    {
      key: 'analysis',
      title: 'Analysis',
      description: 'Analysis and processing features',
      type: 'multi',
      options: [
        { key: 'analysis', label: 'Automated Analysis', description: 'Conduct automated forensic analysis', time: 60 },
        { key: 'extract_iocs', label: 'Extract IOCs', description: 'Extract Indicators of Compromise', time: 25 },
        { key: 'timeline', label: 'Timeline', description: 'Create timeline using plaso', time: 120, slow: true, disabledForGandalf: true },
        { key: 'clamav', label: 'ClamAV', description: 'Run ClamAV against mounted image', time: 40 },
        { key: 'memory', label: 'Memory Analysis', description: 'Analyze memory using Volatility', time: 35 },
        { key: 'memory_timeline', label: 'Memory Timeline', description: 'Create memory timeline\nusing timeliner', time: 50 },
      ],
    },
    {
      key: 'output',
      title: 'Output',
      description: 'Where to send analysis results',
      type: 'multi',
      options: [
        { key: 'splunk', label: 'Splunk', description: 'Index into local Splunk instance', time: 5 },
        { key: 'elastic', label: 'Elastic', description: 'Index into local Elastic instance', time: 5 },
        { key: 'navigator', label: 'MITRE Navigator', description: 'Map to ATT&CK framework', time: 8 },
      ],
    },
    {
      key: 'postprocess',
      title: 'Post-Processing',
      description: 'Cleanup and archiving options',
      type: 'multi',
      options: [
        { key: 'archive', label: 'Archive', description: 'Create ZIP archive after processing', time: 15 },
        { key: 'delete', label: 'Delete Raw Data', description: 'Delete raw data after processing', time: 2 },
      ],
    },
    {
      key: 'confirm',
      title: 'Confirm',
      description: 'Review your selections and start processing',
      type: 'confirm',
    },
  ];

  // Get the current step data based on filtered steps
  const filteredSteps = getFilteredSteps();
  const currentStepData = filteredSteps[currentStep] || steps[0];

  // Get filtered steps based on operation mode (now returns all steps)
  function getFilteredSteps() {
    return steps;
  }

  // Check if a step is disabled based on operation mode
  function isStepDisabled(step, opMode = operationMode) {
    if (opMode === 'gandalf' && step.key === 'collection') {
      return true;
    }
    return false;
  }

  // Get filtered options for current step based on operation mode
  function getFilteredOptions() {
    if (!currentStepData.options) return [];

    // Return all options with disabled flag instead of filtering
    return currentStepData.options.map(opt => {
      let isDisabled = operationMode === 'gandalf' && opt.disabledForGandalf;

      // Disable collection options if no images are selected
      if (currentStepData.key === 'collection' && !hasImages) {
        isDisabled = true;
      }

      return {
        ...opt,
        disabled: isDisabled
      };
    });
  }

  // Calculate ETA whenever options change
  useEffect(() => {
    let totalTime = 30; // Base time in minutes
    steps.forEach(step => {
      if (step.options) {
        step.options.forEach(opt => {
          if (options[opt.key] && opt.time) {
            totalTime += opt.time;
          }
        });
      }
    });
    setEta(totalTime);
  }, [options]);

  // Auto-set collect and process
  useEffect(() => {
    onChange({
      ...options,
      collect: true,
      process: true,
    });
  }, []);

  const handleToggle = (key) => {
    if (disabled) return;

    const newOptions = {
      ...options,
      [key]: !options[key],
    };

    // For single select (Operation, Mode), auto-advance
    if (currentStepData.type === 'single') {
      // If already selected, allow deselection (don't auto-advance)
      if (options[key]) {
        newOptions[key] = false;
        onChange(newOptions);
        return;
      }

      // Clear other options in this group first
      currentStepData.options.forEach(opt => {
        if (opt.key !== key) {
          newOptions[opt.key] = false;
        }
      });
      newOptions[key] = true;

      // Special handling for Brisk mode
      if (key === 'brisk') {
        // Clear all non-mode options first
        steps.forEach(step => {
          if (step.options && step.key !== 'mode') {
            step.options.forEach(opt => {
              newOptions[opt.key] = false;
            });
          }
        });

        // Auto-enable specific options for Brisk mode
        newOptions.analysis = true;        // Automated Analysis
        newOptions.vss = true;              // Volume Shadow Copies
        newOptions.extract_iocs = true;     // Extract IOCs
        newOptions.navigator = true;        // ATT&CK Navigator
        newOptions.userprofiles = true;     // User Profiles

        onChange(newOptions);

        // Skip directly to Output step
        setTimeout(() => {
          const outputStepIndex = steps.findIndex(s => s.key === 'output');
          setCurrentStep(outputStepIndex !== -1 ? outputStepIndex : steps.length - 2);
        }, 300);
        return;
      }

      // Special handling for Exhaustive mode
      if (key === 'exhaustive') {
        // Clear all non-mode options first
        steps.forEach(step => {
          if (step.options && step.key !== 'mode') {
            step.options.forEach(opt => {
              newOptions[opt.key] = false;
            });
          }
        });

        // Enable ALL options from all steps except mode options
        steps.forEach(step => {
          if (step.options && step.key !== 'mode') {
            step.options.forEach(opt => {
              newOptions[opt.key] = true;
            });
          }
        });

        onChange(newOptions);

        // Skip directly to Confirm step (last step)
        setTimeout(() => {
          setCurrentStep(steps.length - 1);
        }, 300);
        return;
      }

      // Special handling for Custom mode
      if (key === 'custom') {
        // Clear all non-mode options first
        steps.forEach(step => {
          if (step.options && step.key !== 'mode') {
            step.options.forEach(opt => {
              newOptions[opt.key] = false;
            });
          }
        });

        onChange(newOptions);

        // Auto-advance to next step
        setTimeout(() => {
          handleNext();
        }, 300);
        return;
      }

      // Update operation mode if this is the operation step
      if (currentStepData.key === 'operation') {
        const newOpMode = key;
        setOperationMode(newOpMode);
        onChange(newOptions);

        // Auto-advance after a short delay for visual feedback
        setTimeout(() => {
          handleNextWithMode(newOpMode);
        }, 300);
      } else {
        // For other single-select steps (like Mode with custom/quick/super_quick)
        onChange(newOptions);
        setTimeout(() => {
          handleNext();
        }, 300);
      }
    } else {
      onChange(newOptions);
    }
  };

  const handleToggleAll = (value) => {
    const newOptions = { ...options };
    const filteredOptions = getFilteredOptions();
    filteredOptions.forEach(opt => {
      newOptions[opt.key] = value;
    });
    onChange(newOptions);
  };

  const handleNextWithMode = (opMode) => {
    const filteredSteps = getFilteredSteps();
    if (currentStep < filteredSteps.length - 1) {
      let nextStep = currentStep + 1;

      // Skip disabled steps based on the provided operation mode
      while (nextStep < filteredSteps.length && isStepDisabled(filteredSteps[nextStep], opMode)) {
        nextStep++;
      }

      if (nextStep < filteredSteps.length) {
        setCurrentStep(nextStep);

        // Randomly spawn Gollum on steps 3-6 (indices 2-5) when moving forward
        if (nextStep >= 2 && nextStep <= 5 && Math.random() < 0.5) {
          // 50% chance Gollum appears
          const gollumAppears = Math.floor(Math.random() * 4) + 2; // Random step between 2-5
          setGollumStep(gollumAppears);

          // Remove Gollum after 3 seconds
          setTimeout(() => {
            setGollumStep(null);
          }, 3000);
        }
      }
    }
  };

  const handleNext = () => {
    handleNextWithMode(operationMode);
  };

  const handleBack = () => {
    if (currentStep > 0) {
      let prevStep = currentStep - 1;

      // Skip disabled steps when going back
      while (prevStep >= 0 && isStepDisabled(steps[prevStep])) {
        prevStep--;
      }

      if (prevStep >= 0) {
        setCurrentStep(prevStep);
      }
    }
  };

  const formatEta = (minutes) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  const handleStepClick = (index) => {
    const filteredSteps = getFilteredSteps();
    const targetStep = filteredSteps[index];

    // Don't allow clicking on disabled steps
    if (isStepDisabled(targetStep)) {
      return;
    }

    // Allow clicking on completed steps or the current step
    if (index <= currentStep) {
      setCurrentStep(index);
    }
  };

  const renderStepIndicator = () => {
    const filteredSteps = getFilteredSteps();
    const progressPercent = (currentStep / (filteredSteps.length - 1)) * 100;

    return (
      <div className="wizard-steps" style={{ '--journey-progress': `${progressPercent}%` }}>
        {filteredSteps.map((step, index) => {
          const disabled = isStepDisabled(step);
          const isClickable = !disabled && index <= currentStep;
          const hasGollum = gollumStep === index;

          return (
            <div
              key={step.key}
              className={`wizard-step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''} ${disabled ? 'disabled' : ''} ${isClickable ? 'clickable' : ''} ${hasGollum ? 'has-gollum' : ''}`}
              onClick={() => handleStepClick(index)}
            >
              <div className="wizard-step-number">{index + 1}</div>
              <div className="wizard-step-title">{step.title}</div>
              {hasGollum && (
                <div className="gollum-emoji">
                  <span role="img" aria-label="Gollum">🧟</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const renderConfirmStep = () => {
    // Group selected options by step
    const groupedOptions = {};
    steps.forEach(step => {
      if (step.options) {
        const selectedInStep = [];
        step.options.forEach(opt => {
          if (options[opt.key]) {
            selectedInStep.push(opt.label);
          }
        });
        if (selectedInStep.length > 0) {
          groupedOptions[step.title] = selectedInStep;
        }
      }
    });

    return (
      <div className="confirm-step">
        {error && <div className="error" style={{ marginBottom: '1.5rem' }}>{error}</div>}
        <h3>Review Your Selections</h3>
        <div className="confirm-summary">
          {Object.entries(groupedOptions).map(([stepTitle, optionLabels], index) => (
            <div key={index} className="confirm-item">
              <span className="confirm-step-name">{stepTitle}:</span>
              <span className="confirm-option-name">{optionLabels.join(', ')}</span>
            </div>
          ))}
        </div>
        <div className="eta-large">
          <strong>Estimated Processing Time:</strong> {formatEta(eta)}
        </div>
      </div>
    );
  };

  return (
    <div className={`options-panel-wizard ${disabled ? 'disabled' : ''}`}>
      {renderStepIndicator()}

      <div className="wizard-content">
        <div className="wizard-header">
          <h3>{currentStepData.title}</h3>
          <p>{currentStepData.description}</p>
          {currentStepData.type !== 'confirm' && (
            <div className="slow-key">
              <span className="slow-indicator-key">!</span> = Slow operation
            </div>
          )}
        </div>

        <div className="wizard-navigation">
          <div className={`wizard-actions-left ${currentStepData.type === 'single' || currentStepData.type === 'confirm' ? 'hidden-buttons' : ''}`}>
            <button type="button" onClick={() => handleToggleAll(true)}>
              Enable All
            </button>
            <button type="button" onClick={() => handleToggleAll(false)}>
              Disable All
            </button>
          </div>
          <div className="wizard-actions-right">
            <div className="eta-display">
              <strong>ETA:</strong> {formatEta(eta)}
            </div>
            <button
              type="button"
              onClick={handleBack}
              disabled={currentStep === 0}
              className="button-back"
            >
              ← Back
            </button>
            {currentStepData.type === 'confirm' ? (
              onSubmit && (
                <button
                  type="button"
                  onClick={onSubmit}
                  disabled={loading || disabled}
                  className="button-start"
                >
                  {loading ? 'Starting...' : 'Start Analysis'}
                </button>
              )
            ) : (
              <button
                type="button"
                onClick={handleNext}
                disabled={currentStep >= steps.length - 1}
                className="button-next"
              >
                Next →
              </button>
            )}
          </div>
        </div>

        {currentStepData.type === 'confirm' ? (
          renderConfirmStep()
        ) : (
          <>
            <div
              className={`wizard-options ${currentStepData.type === 'single' ? 'radio-group' : 'checkbox-group'}`}
              data-option-count={getFilteredOptions().length}
            >
              {getFilteredOptions().map(option => (
                <div key={option.key} className={`wizard-option-item ${option.disabled ? 'option-disabled' : ''} ${option.slow ? 'option-slow' : ''}`}>
                  <input
                    type="checkbox"
                    id={option.key}
                    name={currentStepData.type === 'single' ? currentStepData.key : option.key}
                    checked={options[option.key] || false}
                    onChange={() => !option.disabled && handleToggle(option.key)}
                    disabled={option.disabled}
                    className={currentStepData.type === 'single' ? 'radio-style' : ''}
                  />
                  <label htmlFor={option.key} title={option.tooltip}>
                    <div className="option-label">
                      {option.label}
                      {option.slow && <span className="slow-indicator" title="This operation is slow">!</span>}
                      {option.tooltip && <span className="tooltip-icon" title={option.tooltip}>ⓘ</span>}
                    </div>
                    <div className="option-description">{option.description}</div>
                  </label>
                </div>
              ))}
            </div>
          </>
        )}

      </div>
    </div>
  );
}

export default OptionsPanel;
