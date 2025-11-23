import React, { useState, useRef, useEffect } from 'react';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // TODO: Replace with actual AI API endpoint
      // For now, simulate a response
      await new Promise(resolve => setTimeout(resolve, 1000));

      const assistantMessage = {
        role: 'assistant',
        content: 'This is a placeholder response. The AI assistant integration is currently under development. In production, this will connect to an AI service to provide intelligent assistance with forensic workflows, case management, and technical guidance.'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    'How do I start a new forensic analysis?',
    'Guide me through memory analysis',
    'What file formats are supported?',
    'Help me interpret YARA scan results',
    'Explain the timeline generation process',
    'How do I export my analysis results?',
    'What IOCs should I look for?',
    'How do I analyze suspicious files?',
    'How do I analyze browser history and artifacts?',
    'What are common malware persistence mechanisms?',
    'What tools does Rivendell integrate with?'
  ];

  const handleQuickAction = (action) => {
    setInput(action);
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
          Intelligent guidance for forensic analysis workflows, feature explainations, and guidance through investigations and case management.
        </p>
      </header>

      <div className="card ai-chat-container">
        <div className="chat-messages">
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
                  maxWidth: '70%',
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
                </div>
                <div style={{ lineHeight: '1.5' }}>
                  {message.content}
                </div>
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
                  Thinking...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="quick-actions" style={{
          marginTop: '0',
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
              background: 'rgba(255, 193, 7, 0.2)',
              border: '1px solid rgba(255, 193, 7, 0.4)',
              borderRadius: '4px',
              color: '#ffc107',
              fontFamily: "'Cinzel', 'Times New Roman', serif"
            }}>
              API Keys: 0
            </span>
            <span style={{
              display: 'inline-block',
              padding: '0.4rem 0.8rem',
              fontSize: '0.75rem',
              background: 'rgba(255, 193, 7, 0.2)',
              border: '1px solid rgba(255, 193, 7, 0.4)',
              borderRadius: '4px',
              color: '#ffc107',
              fontFamily: "'Cinzel', 'Times New Roman', serif"
            }}>
              Local LLM: Not Detected
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
            placeholder="Ask me anything about forensic analysis..."
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
          <strong>Note:</strong> AI Agent integration is currently under development.
          This interface will connect to advanced language models to provide intelligent
          assistance with forensic workflows, case analysis, and technical guidance.
        </div>
      </div>

      <div className="card" style={{ marginTop: '-1rem' }}>
        <h3>What can Eru help you with?</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginTop: '1.5rem'
        }}>
          <div>
            <h4 style={{ color: '#66d9ef', marginBottom: '0.5rem' }}>Forensic Analysis</h4>
            <ul style={{ fontSize: '0.9rem', lineHeight: '1.8', opacity: 0.9 }}>
              <li>Disk image analysis guidance</li>
              <li>Memory dump interpretation</li>
              <li>Timeline correlation</li>
              <li>Artifact analysis</li>
            </ul>
          </div>

          <div>
            <h4 style={{ color: '#a7db6c', marginBottom: '0.5rem' }}>Workflow Support</h4>
            <ul style={{ fontSize: '0.9rem', lineHeight: '1.8', opacity: 0.9 }}>
              <li>Job configuration help</li>
              <li>Feature explanations</li>
              <li>Best practices</li>
              <li>Troubleshooting</li>
            </ul>
          </div>

          <div>
            <h4 style={{ color: '#f0dba5', marginBottom: '0.5rem' }}>Technical Guidance</h4>
            <ul style={{ fontSize: '0.9rem', lineHeight: '1.8', opacity: 0.9 }}>
              <li>Tool recommendations</li>
              <li>Format compatibility</li>
              <li>Export options</li>
              <li>Integration setup</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AIAssistant;
