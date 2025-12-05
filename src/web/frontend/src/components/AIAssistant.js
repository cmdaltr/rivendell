import React, { useState, useRef, useEffect } from 'react';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

// API base URL - adjust based on environment
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5688';

function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState('');
  const [llmStatus, setLlmStatus] = useState({ available: false, model: null });
  const [loadingCases, setLoadingCases] = useState(true);
  const [showHelp, setShowHelp] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch available cases and LLM status on mount
  useEffect(() => {
    fetchCases();
    checkLlmStatus();
  }, []);

  // Auto-hide help section after 30 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowHelp(false);
    }, 30000);
    return () => clearTimeout(timer);
  }, []);

  const fetchCases = async () => {
    setLoadingCases(true);
    try {
      const response = await fetch(`${API_BASE}/api/ai/cases`);
      if (response.ok) {
        const data = await response.json();
        setCases(data.cases || []);
        // Auto-select first case if available
        if (data.cases && data.cases.length > 0) {
          setSelectedCase(data.cases[0].case_id);
        }
      }
    } catch (error) {
      console.error('Error fetching cases:', error);
    } finally {
      setLoadingCases(false);
    }
  };

  const checkLlmStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/ai/status`);
      if (response.ok) {
        const data = await response.json();
        setLlmStatus({
          available: data.llm_available || false,
          model: data.model_name || null
        });
      }
    } catch (error) {
      console.error('Error checking LLM status:', error);
      setLlmStatus({ available: false, model: null });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentQuestion = input;
    setInput('');
    setLoading(true);

    try {
      // If a case is selected, query case-specific data
      if (selectedCase) {
        const response = await fetch(`${API_BASE}/api/ai/cases/${selectedCase}/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: currentQuestion }),
        });

        if (response.ok) {
          const data = await response.json();
          const assistantMessage = {
            role: 'assistant',
            content: data.answer,
            sources: data.sources || [],
            confidence: data.confidence,
            processing_time: data.processing_time
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Query failed');
        }
      } else {
        // General query without case context - use general AI endpoint
        const response = await fetch(`${API_BASE}/api/ai/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: currentQuestion,
            context: 'forensic_assistant'
          }),
        });

        if (response.ok) {
          const data = await response.json();
          const assistantMessage = {
            role: 'assistant',
            content: data.response || data.answer || 'No response received.',
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          throw new Error('General query failed');
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please check that the AI backend is running and try again.`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleGetSuggestions = async () => {
    if (!selectedCase) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/ai/cases/${selectedCase}/suggestions`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        const suggestionsText = data.suggestions?.map((s, i) =>
          `${i + 1}. **${s.title}**\n   ${s.description}`
        ).join('\n\n') || 'No suggestions available.';

        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `**Investigation Path Suggestions for ${selectedCase}:**\n\n${suggestionsText}`
        }]);
      }
    } catch (error) {
      console.error('Error getting suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetSummary = async () => {
    if (!selectedCase) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/ai/cases/${selectedCase}/summary`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `**Case Summary for ${selectedCase}:**\n\n${data.executive_summary || 'No summary available.'}`
        }]);
      }
    } catch (error) {
      console.error('Error getting summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    'What PowerShell commands were executed?',
    'Show timeline of suspicious activities',
    'What MITRE ATT&CK techniques were detected?',
    'List all IOCs found',
    'What processes were running?',
    'Show network connections to external IPs',
    'What persistence mechanisms were found?',
    'Summarize the key findings'
  ];

  const handleQuickAction = (action) => {
    setInput(action);
  };

  // Format message content with markdown-like styling
  const formatContent = (content) => {
    if (!content) return '';

    // Basic markdown formatting
    let formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br/>');

    return <span dangerouslySetInnerHTML={{ __html: formatted }} />;
  };

  return (
    <div className="journey-detail ai-assistant">
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
        <h2>Eru (Rivendell AI Agent)</h2>
        <p>
          Intelligent guidance for forensic analysis workflows, feature explanations, and guidance through investigations and case management.
        </p>
      </header>

      <div className="card ai-chat-container">
        {/* Collapsible Help Section */}
        <div style={{ marginBottom: '1rem' }}>
          <button
            onClick={() => setShowHelp(!showHelp)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#f0dba5',
              cursor: 'pointer',
              fontSize: '0.85rem',
              padding: '0.25rem 0',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              opacity: 0.8
            }}
          >
            <span style={{
              transform: showHelp ? 'rotate(90deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease',
              display: 'inline-block'
            }}>
              &#9654;
            </span>
            What can Eru help you with?
          </button>

          {showHelp && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr 1fr',
              gap: '2rem',
              marginTop: '0.75rem',
              padding: '1rem 0'
            }}>
              <div>
                <h4 style={{ color: '#66d9ef', marginBottom: '0.5rem', fontSize: '1.2rem' }}>Case Analysis</h4>
                <ul style={{ fontSize: '1.05rem', lineHeight: '1.6', opacity: 0.9, paddingLeft: '1.2rem', margin: 0 }}>
                  <li>Natural language queries on case data</li>
                  <li>Timeline event analysis</li>
                  <li>IOC identification</li>
                  <li>MITRE ATT&CK mapping</li>
                </ul>
              </div>

              <div style={{ paddingLeft: '4rem' }}>
                <h4 style={{ color: '#a7db6c', marginBottom: '0.5rem', fontSize: '1.2rem' }}>Investigation Support</h4>
                <ul style={{ fontSize: '1.05rem', lineHeight: '1.6', opacity: 0.9, paddingLeft: '1.2rem', margin: 0 }}>
                  <li>Investigation path suggestions</li>
                  <li>Case summary generation</li>
                  <li>Artifact correlation</li>
                  <li>Evidence prioritization</li>
                </ul>
              </div>

              <div style={{ paddingLeft: '6rem' }}>
                <h4 style={{ color: '#f0dba5', marginBottom: '0.5rem', fontSize: '1.2rem' }}>Technical Guidance</h4>
                <ul style={{ fontSize: '1.05rem', lineHeight: '1.6', opacity: 0.9, paddingLeft: '1.2rem', margin: 0 }}>
                  <li>Tool recommendations</li>
                  <li>Workflow assistance</li>
                  <li>Best practices</li>
                  <li>Forensic methodology</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Case Selection and Status */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '1.5rem',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <div style={{ flex: 1, minWidth: '200px' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontSize: '0.85rem',
              color: '#f0dba5',
              opacity: 0.8
            }}>
              Select Case:
            </label>
            <select
              value={selectedCase}
              onChange={(e) => setSelectedCase(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                height: '48px',
                background: 'rgba(15, 15, 35, 0.6)',
                border: '1px solid rgba(240, 219, 165, 0.3)',
                borderRadius: '4px',
                color: '#f0dba5',
                fontFamily: "'Cinzel', 'Times New Roman', serif",
                fontSize: '1rem'
              }}
              disabled={loadingCases}
            >
              <option value="">-- General Assistant (No Case) --</option>
              {cases.map((c) => (
                <option key={c.case_id} value={c.case_id}>
                  {c.case_id} {c.indexed ? '(Indexed)' : ''}
                </option>
              ))}
            </select>
          </div>

          {selectedCase && (
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.5rem' }}>
              <button
                onClick={handleGetSuggestions}
                disabled={loading}
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: '0.85rem',
                  background: 'rgba(167, 219, 108, 0.2)',
                  border: '1px solid rgba(167, 219, 108, 0.4)',
                  borderRadius: '4px',
                  color: '#a7db6c',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif"
                }}
              >
                Get Suggestions
              </button>
              <button
                onClick={handleGetSummary}
                disabled={loading}
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: '0.85rem',
                  background: 'rgba(102, 217, 239, 0.2)',
                  border: '1px solid rgba(102, 217, 239, 0.4)',
                  borderRadius: '4px',
                  color: '#66d9ef',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontFamily: "'Cinzel', 'Times New Roman', serif"
                }}
              >
                Generate Summary
              </button>
            </div>
          )}
        </div>

        {/* Chat Messages */}
        <div className="chat-messages" style={{ minHeight: messages.length > 0 ? '200px' : '60px', maxHeight: '500px', overflowY: 'auto' }}>
          {messages.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '1rem',
              color: '#f0dba5',
              opacity: 0.6
            }}>
              {selectedCase
                ? `Ask questions about case "${selectedCase}" or use the quick actions below.`
                : 'Select a case to query case-specific data, or ask general forensics questions.'}
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
              style={{
                display: 'flex',
                marginBottom: '1rem',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              <div
                style={{
                  maxWidth: '80%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  background: message.role === 'user'
                    ? 'rgba(102, 217, 239, 0.2)'
                    : 'rgba(240, 219, 165, 0.1)',
                  border: message.role === 'user'
                    ? '1px solid rgba(102, 217, 239, 0.4)'
                    : '1px solid rgba(240, 219, 165, 0.2)',
                  color: message.role === 'user' ? '#66d9ef' : '#f0dba5'
                }}
              >
                <div style={{
                  fontSize: '0.75rem',
                  opacity: 0.7,
                  marginBottom: '0.25rem',
                  fontWeight: 600
                }}>
                  {message.role === 'user' ? 'You' : 'Eru'}
                  {message.processing_time && (
                    <span style={{ marginLeft: '0.5rem', fontWeight: 'normal' }}>
                      ({message.processing_time.toFixed(2)}s)
                    </span>
                  )}
                </div>
                <div style={{ lineHeight: '1.6' }}>
                  {formatContent(message.content)}
                </div>

                {/* Show sources if available */}
                {message.sources && message.sources.length > 0 && (
                  <div style={{
                    marginTop: '0.75rem',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid rgba(240, 219, 165, 0.2)',
                    fontSize: '0.8rem',
                    opacity: 0.7
                  }}>
                    <strong>Sources:</strong>
                    {message.sources.slice(0, 3).map((src, i) => (
                      <div key={i} style={{ marginTop: '0.25rem' }}>
                        [{src.metadata?.type || 'unknown'}] {src.metadata?.source || src.metadata?.name || 'N/A'}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div
                style={{
                  maxWidth: '70%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  background: 'rgba(240, 219, 165, 0.1)',
                  border: '1px solid rgba(240, 219, 165, 0.2)',
                  color: '#f0dba5'
                }}
              >
                <div style={{ fontSize: '0.75rem', opacity: 0.7, marginBottom: '0.25rem', fontWeight: 600 }}>
                  Eru
                </div>
                <div style={{ lineHeight: '1.5' }}>
                  Analyzing...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="quick-actions" style={{
          marginTop: '1rem',
          position: 'relative'
        }}>
          <h2 style={{
            marginBottom: '1rem'
          }}>
            Quick Actions
          </h2>
          <div style={{
            position: 'absolute',
            top: '0',
            right: '0',
            display: 'flex',
            gap: '0.5rem'
          }}>
            <span style={{
              display: 'inline-block',
              padding: '0.4rem 0.8rem',
              fontSize: '0.75rem',
              background: cases.length > 0 ? 'rgba(167, 219, 108, 0.2)' : 'rgba(255, 193, 7, 0.2)',
              border: `1px solid ${cases.length > 0 ? 'rgba(167, 219, 108, 0.4)' : 'rgba(255, 193, 7, 0.4)'}`,
              borderRadius: '4px',
              color: cases.length > 0 ? '#a7db6c' : '#ffc107',
              fontFamily: "'Cinzel', 'Times New Roman', serif"
            }}>
              Cases: {cases.length}
            </span>
            <span style={{
              display: 'inline-block',
              padding: '0.4rem 0.8rem',
              fontSize: '0.75rem',
              background: llmStatus.available ? 'rgba(167, 219, 108, 0.2)' : 'rgba(255, 193, 7, 0.2)',
              border: `1px solid ${llmStatus.available ? 'rgba(167, 219, 108, 0.4)' : 'rgba(255, 193, 7, 0.4)'}`,
              borderRadius: '4px',
              color: llmStatus.available ? '#a7db6c' : '#ffc107',
              fontFamily: "'Cinzel', 'Times New Roman', serif"
            }}>
              LLM: {llmStatus.available ? llmStatus.model || 'Connected' : 'Not Connected'}
            </span>
          </div>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem'
          }}>
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => handleQuickAction(action)}
                style={{
                  padding: '0.5rem 0.75rem',
                  fontSize: '0.85rem',
                  background: 'rgba(107, 142, 63, 0.2)',
                  border: '1px solid rgba(107, 142, 63, 0.4)',
                  borderRadius: '4px',
                  color: '#a7db6c',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: "'Cinzel', 'Times New Roman', serif"
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'rgba(107, 142, 63, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'rgba(107, 142, 63, 0.2)';
                }}
              >
                {action}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{
          marginTop: '1.5rem',
          display: 'flex',
          gap: '0.75rem'
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedCase
              ? `Ask about case "${selectedCase}"...`
              : "Ask me anything about forensic analysis..."}
            disabled={loading}
            style={{
              flex: 1,
              padding: '0.75rem 1rem',
              background: 'rgba(15, 15, 35, 0.6)',
              border: '1px solid rgba(240, 219, 165, 0.3)',
              borderRadius: '4px',
              color: '#f0dba5',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1rem'
            }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            style={{
              padding: '0.75rem 1.5rem',
              background: loading ? 'rgba(102, 217, 239, 0.2)' : 'rgba(102, 217, 239, 0.3)',
              border: '1px solid rgba(102, 217, 239, 0.5)',
              borderRadius: '4px',
              color: '#66d9ef',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              fontFamily: "'Cinzel', 'Times New Roman', serif",
              fontSize: '1rem',
              fontWeight: 600,
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              if (!loading && input.trim()) {
                e.target.style.background = 'rgba(102, 217, 239, 0.4)';
              }
            }}
            onMouseOut={(e) => {
              e.target.style.background = loading ? 'rgba(102, 217, 239, 0.2)' : 'rgba(102, 217, 239, 0.3)';
            }}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>

        <div style={{
          marginTop: '1.5rem',
          padding: '1rem',
          background: 'rgba(255, 193, 7, 0.1)',
          border: '1px solid rgba(255, 193, 7, 0.3)',
          borderRadius: '4px',
          fontSize: '0.875rem',
          color: '#ffc107'
        }}>
          <strong>Note:</strong> AI results are never 100% accurate - always validate findings!
          {!llmStatus.available && (
            <span style={{ display: 'block', marginTop: '0.5rem' }}>
              LLM backend not detected. Ensure Ollama is running with a model loaded.
            </span>
          )}
        </div>
      </div>

    </div>
  );
}

export default AIAssistant;
