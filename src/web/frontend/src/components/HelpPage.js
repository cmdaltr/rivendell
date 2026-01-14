import React, { useState } from 'react';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

const HelpPage = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = {
    overview: {
      title: 'Overview',
      content: (
        <>
          <h3>Rivendell DF Acceleration Suite v2.1.0</h3>
          <p>
            Rivendell is a comprehensive Digital Forensics and Incident Response (DFIR) suite designed to accelerate
            forensic investigations through automation, AI-powered analysis, and integrated threat intelligence.
          </p><br />

          <h4>Architecture</h4>
          <pre className="code-block">
{`        ┌──────────────────────────────────────────────────────────────┐
        │                       Rivendell Suite                        │
        ├──────────────────────────────────────────────────────────────┤
        │                                                              │
        │    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
        │    │   Gandalf    │   │    Elrond    │   │     Eru      │    │
        │    │ Acquisition  │ → │   Analysis   │ → │   AI Agent   |    │
        │    └──────────────┘   └──────────────┘   └──────────────┘    │
        │           ↓                  ↓                  ↓            │
        │     ┌─────────────────────────────────────────────────┐      │
        │     │      MITRE ATT&CK • Cloud • SIEM • Reports      │      │
        │     └─────────────────────────────────────────────────┘      │
        │                                                              │
        └──────────────────────────────────────────────────────────────┘`}
          </pre>
          <br />
          <h4>Key Capabilities</h4>
          <ul>
            <li><strong>Remote Acquisition (Gandalf):</strong> Collect forensic artifacts from Windows, Linux, and macOS systems</li>
            <li><strong>Automated Analysis (Elrond):</strong> Process evidence with 30+ integrated forensic tools</li>
            <li><strong>MITRE ATT&CK Integration:</strong> Automatic technique mapping and coverage analysis</li>
            <li><strong>Cloud Forensics:</strong> AWS, Azure, and GCP investigation support</li>
            <li><strong>AI-Powered Analysis (Eru):</strong> Natural language queries using local LLM</li>
            <li><strong>Memory Forensics:</strong> Volatility 3 integration</li>
            <li><strong>Timeline Generation:</strong> Plaso/log2timeline support</li>
            <li><strong>SIEM Integration:</strong> Direct export to Splunk and Elasticsearch</li>
          </ul>
        </>
      )
    },
    installation: {
      title: 'Installation',
      content: (
        <>
          <h3>Quick Installation</h3>

          <br />
          <h4>Linux</h4>
          <pre className="code-block">
{`git clone https://github.com/cmdaltr/rivendell.git
cd rivendell
chmod +x scripts/install_linux.sh
sudo ./scripts/install_linux.sh`}
          </pre>

          <br />
          <h4>macOS</h4>
          <pre className="code-block">
{`git clone https://github.com/cmdaltr/rivendell.git
cd rivendell
chmod +x scripts/install_macos.sh
./scripts/install_macos.sh`}
          </pre>

          <br />
          <h4>Windows (WSL2)</h4>
          <pre className="code-block">
{`git clone https://github.com/cmdaltr/rivendell.git
cd rivendell
.\\scripts\\install_windows_wsl.ps1`}
          </pre>

          <br />
          <h4>Docker Deployment</h4>
          <pre className="code-block">
{`docker-compose up -d
# Access web interface at http://localhost:5687`}
          </pre>

          <br />
          <br />
          <h4>Dependencies</h4>
          <br />
          <p><strong>Core Requirements:</strong></p>
          <ul>
            <li>Python 3.8+</li>
            <li>Volatility 3 (memory analysis)</li>
            <li>Plaso/log2timeline (timeline generation)</li>
            <li>30+ forensic tools (automatically installed)</li>
          </ul>

          <br />
          <p><strong>Optional:</strong></p>
          <ul>
            <li>Docker (for containerized deployment)</li>
            <li>Ollama (for AI agent)</li>
            <li>Splunk/Elasticsearch (for SIEM integration)</li>
          </ul>

          <br />
          <h4>Verification</h4>
          <pre className="code-block">
{`elrond --check-dependencies`}
          </pre>
        </>
      )
    },
    gandalf: {
      title: 'Gandalf',
      content: (
        <>
          <h3>Remote Forensic Acquisition</h3>
          <p>
            Gandalf enables secure collection of forensic artifacts from local and remote systems across
            Windows, Linux, and macOS platforms.
          </p>

          <h4>Features</h4>
          <ul>
            <li>Multi-platform support (Windows, Linux, macOS)</li>
            <li>Remote acquisition via SSH/PowerShell</li>
            <li>Encrypted evidence packaging</li>
            <li>Memory dump acquisition</li>
            <li>Audit logging with SHA256 hashing</li>
            <li>Network-based collection</li>
          </ul>

          <h4>Basic Usage</h4>

          <h5>Local Acquisition</h5>
          <pre className="code-block">
{`# Windows (PowerShell)
.\\acquisition\\powershell\\gandalf.ps1 Password Local -M -o C:\\evidence

# Linux/macOS (Python)
sudo python3 acquisition/python/gandalf.py Password Local -M -o /evidence`}
          </pre>

          <h5>Remote Acquisition (SSH)</h5>
          <pre className="code-block">
{`python3 acquisition/python/gandalf.py Password 192.168.1.100 \\
  -u admin \\
  -M \\
  -o /evidence/CASE-001`}
          </pre>

          <h5>Windows Remote (PowerShell)</h5>
          <pre className="code-block">
{`.\\acquisition\\powershell\\gandalf.ps1 \\
  -Target 192.168.1.100 \\
  -User administrator \\
  -Memory \\
  -Output C:\\evidence`}
          </pre>

          <h4>Collection Options</h4>
          <ul>
            <li><code>-M</code> Memory dump</li>
            <li><code>-R</code> Registry hives (Windows)</li>
            <li><code>-E</code> Event logs (Windows)</li>
            <li><code>-B</code> Browser artifacts</li>
            <li><code>-F</code> File collection</li>
            <li><code>-U</code> User profiles</li>
            <li><code>-L</code> Last access times</li>
            <li><code>-H</code> Hash artifacts</li>
          </ul>

          <h4>Encryption Modes</h4>
          <ul>
            <li><strong>Password:</strong> Symmetric encryption with password</li>
            <li><strong>Certificate:</strong> PKI-based encryption</li>
            <li><strong>Key:</strong> Pre-shared key encryption</li>
            <li><strong>None:</strong> No encryption (not recommended)</li>
          </ul>
        </>
      )
    },
    elrond: {
      title: 'Elrond',
      content: (
        <>
          <h3>Automated Forensic Analysis</h3>
          <p>
            Elrond processes and analyzes forensic evidence using automated tooling, timeline generation,
            and MITRE ATT&CK mapping.
          </p>

          <h4>Features</h4>
          <ul>
            <li>Automated artifact parsing</li>
            <li>Timeline generation with Plaso</li>
            <li>Memory forensics with Volatility 3</li>
            <li>Registry analysis</li>
            <li>Event log parsing</li>
            <li>Browser artifact extraction</li>
            <li>IOC detection and extraction</li>
            <li>MITRE ATT&CK technique mapping</li>
          </ul>

          <h4>Basic Usage</h4>

          <h5>Process Evidence (Collect Mode)</h5>
          <pre className="code-block">
{`elrond -C -c CASE-001 -s /evidence -o /output`}
          </pre>

          <h5>Analyze Gandalf Extraction</h5>
          <pre className="code-block">
{`elrond -G -c CASE-001 -s /extracted_data -o /output`}
          </pre>

          <h5>With Memory Analysis</h5>
          <pre className="code-block">
{`elrond -C -c CASE-001 \\
  -s /evidence \\
  -m /memory.dmp \\
  -o /output`}
          </pre>

          <h5>Timeline Generation</h5>
          <pre className="code-block">
{`elrond -C -c CASE-001 \\
  -s /evidence \\
  -t \\
  --start-date 2024-01-01 \\
  --end-date 2024-12-31 \\
  -o /output`}
          </pre>

          <h4>Processing Modes</h4>
          <ul>
            <li><strong>Brisk:</strong> Optimized processing that balances speed and thoroughness</li>
            <li><strong>Exhaustive:</strong> Enable all available options for maximum thoroughness</li>
            <li><strong>Custom:</strong> Full control over all processing options</li>
            <li><strong>Template:</strong> Load a saved template of custom options for quick reuse</li>
          </ul>

          <h4>Templates</h4>
          <p>
            Templates allow you to save your custom processing configurations for reuse across multiple jobs.
            This is useful when you regularly process similar evidence with the same options.
          </p>
          <ul>
            <li><strong>Save:</strong> On the Confirm step, click "Save as Template" to save your current configuration</li>
            <li><strong>Load:</strong> Select "Template" mode and choose from your saved templates</li>
            <li><strong>Delete:</strong> Click the × button next to a template to remove it</li>
          </ul>
          <p>
            Templates are stored locally in your browser and persist across sessions.
          </p>

          <h4>Analysis Features</h4>
          <ul>
            <li>Automated forensic analysis</li>
            <li>IOC extraction</li>
            <li>Timeline creation with Plaso</li>
            <li>ClamAV malware scanning</li>
            <li>Memory analysis with Volatility</li>
            <li>Memory timeline generation</li>
          </ul>

          <h4>Output Destinations</h4>
          <ul>
            <li><strong>Splunk:</strong> Index into local Splunk instance</li>
            <li><strong>Elastic:</strong> Index into Elasticsearch</li>
            <li><strong>MITRE Navigator:</strong> ATT&CK framework mapping</li>
          </ul>
        </>
      )
    },
    mordor: {
      title: 'Mordor',
      content: (
        <>
          <h3>Security Event Datasets</h3>
          <p>
            Access pre-recorded security event datasets from the OTRF Mordor project for threat research,
            detection development, and testing.
          </p>

          <h4>About Mordor</h4>
          <p>
            The Mordor project provides realistic adversary simulation datasets that can be used to:
          </p>
          <ul>
            <li>Test and validate detection rules</li>
            <li>Research attacker techniques</li>
            <li>Develop analytics and hunting queries</li>
            <li>Train security teams</li>
            <li>Benchmark detection capabilities</li>
          </ul>

          <h4>Dataset Categories</h4>
          <ul>
            <li><strong>Windows:</strong> Event logs from adversary simulations</li>
            <li><strong>Linux:</strong> System logs and audit data</li>
            <li><strong>Network:</strong> Packet captures and flow data</li>
            <li><strong>Cloud:</strong> Cloud platform logs (AWS, Azure, GCP)</li>
          </ul>

          <h4>Integration with Rivendell</h4>
          <p>Mordor datasets are automatically cloned during Docker deployment:</p>
          <pre className="code-block">
{`# Location: /data/mordor
# Access via: python3 -m rivendell.mordor.loader`}
          </pre>

          <h4>External Access</h4>
          <p>
            Visit the official repository:{' '}
            <a
              href="https://github.com/OTRF/Security-Datasets"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#a7db6c' }}
            >
              https://github.com/OTRF/Security-Datasets
            </a>
          </p>
        </>
      )
    },
    eru: {
      title: 'Eru',
      content: (
        <>
          <h3>Eru - AI-Powered Analysis</h3>
          <p>
            Query investigation data using natural language with a privacy-focused local LLM powered by Ollama.
            Named after Eru Iluvatar, the supreme deity in Tolkien's legendarium.
          </p>

          <h4>Features</h4>
          <ul>
            <li>Natural language queries of case data</li>
            <li>Investigation suggestions and insights</li>
            <li>Automated case summaries</li>
            <li>Web chat interface</li>
            <li>Privacy-focused local processing (no cloud)</li>
            <li>Vector database indexing for fast queries</li>
          </ul>

          <h4>Setup</h4>
          <pre className="code-block">
{`# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama3

# Verify
ollama list`}
          </pre>

          <h4>Usage</h4>

          <h5>Index Case Data</h5>
          <pre className="code-block">
{`rivendell-ai index CASE-001 /output/CASE-001`}
          </pre>

          <h5>Query Cases</h5>
          <pre className="code-block">
{`# Ask questions
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# Timeline queries
rivendell-ai query CASE-001 "Show events between 14:00 and 15:00"

# IOC queries
rivendell-ai query CASE-001 "List all suspicious IP addresses"`}
          </pre>

          <h5>Generate Summaries</h5>
          <pre className="code-block">
{`rivendell-ai summary CASE-001 --format markdown --output report.md`}
          </pre>

          <h5>Web Interface</h5>
          <pre className="code-block">
{`python3 -m rivendell.ai.web_interface
# Visit http://localhost:5687/ai/chat/CASE-001`}
          </pre>

          <h4>Example Queries</h4>
          <ul>
            <li>"What were the initial access vectors?"</li>
            <li>"Show all credential access attempts"</li>
            <li>"What persistence mechanisms were used?"</li>
            <li>"List files created in the last hour of the incident"</li>
            <li>"What lateral movement techniques were observed?"</li>
          </ul>
        </>
      )
    },
    features: {
      title: 'Features',
      content: (
        <>
          <h3>Advanced Features</h3>
          <p>
            Rivendell includes powerful features for threat intelligence mapping, cloud forensics, and SIEM integration.
          </p>

          <h4>MITRE ATT&CK Integration</h4>
          <p>
            Automatic mapping of forensic findings to MITRE ATT&CK techniques provides tactical context
            and helps understand attacker methodologies.
          </p>
          <ul>
            <li>Auto-updates from MITRE ATT&CK framework</li>
            <li>Technique mapping for forensic artifacts</li>
            <li>ATT&CK matrix dashboard generation</li>
            <li>Coverage analysis and reporting</li>
            <li>Navigator layer export</li>
          </ul>

          <h5>MITRE Usage</h5>
          <pre className="code-block">
{`# Update MITRE Data
python3 -m rivendell.mitre.updater

# Map Artifacts to Techniques
python3 -m rivendell.mitre.mapper /path/to/artifacts

# Generate Dashboard
python3 -m rivendell.mitre.dashboard -o /output`}
          </pre>

          <h4>Cloud Forensics</h4>
          <p>
            Acquire and analyze cloud infrastructure across AWS, Azure, and GCP.
          </p>

          <h5>Supported Providers</h5>
          <ul>
            <li><strong>AWS:</strong> EC2 snapshots, CloudTrail, S3, IAM</li>
            <li><strong>Azure:</strong> VM disks, Activity Logs, Storage, AAD</li>
            <li><strong>GCP:</strong> Compute Engine, Cloud Logging, Storage, IAM</li>
          </ul>

          <h5>Cloud Usage Examples</h5>
          <pre className="code-block">
{`# AWS - Acquire logs
python3 -m rivendell.cloud.cli aws acquire-logs --days 7 --output ./logs

# Azure - Acquire disk snapshot
python3 -m rivendell.cloud.cli azure acquire-disk --instance-id vm-name

# GCP - Create snapshot
python3 -m rivendell.cloud.cli gcp snapshot --instance server-name`}
          </pre>

          <h4>SIEM Integration</h4>
          <p>Export forensic findings directly to your SIEM platform.</p>
          <ul>
            <li><strong>Splunk:</strong> HTTP Event Collector (HEC) integration</li>
            <li><strong>Elasticsearch:</strong> Direct indexing with Kibana dashboards</li>
            <li><strong>Custom:</strong> JSON/CSV export for other platforms</li>
          </ul>

          <h4>Memory Forensics</h4>
          <p>Integrated Volatility 3 support for memory analysis.</p>
          <ul>
            <li>Process and DLL analysis</li>
            <li>Network connection enumeration</li>
            <li>Registry hive extraction</li>
            <li>Malware detection</li>
            <li>Memory timeline generation</li>
          </ul>

          <h4>Timeline Generation</h4>
          <p>Plaso/log2timeline integration for comprehensive timelines.</p>
          <ul>
            <li>Multi-source timeline correlation</li>
            <li>Customizable date range filtering</li>
            <li>CSV and JSON export formats</li>
          </ul>
        </>
      )
    },
    workflow: {
      title: 'Workflow',
      content: (
        <>
          <h3>End-to-End Investigation</h3>
          <p>
            Follow this comprehensive workflow for a complete forensic investigation from acquisition to reporting.
          </p>

          <h4>Step 1: Acquire Evidence</h4>
          <pre className="code-block">
{`# Remote Windows system
python3 acquisition/python/gandalf.py Password 192.168.1.100 \\
  -u administrator \\
  -M \\
  -o /evidence/CASE-001`}
          </pre>

          <h4>Step 2: Process Evidence</h4>
          <pre className="code-block">
{`# Analyze with Elrond
elrond -C \\
  -c CASE-001 \\
  -s /evidence/CASE-001 \\
  -m /evidence/CASE-001/memory.dmp \\
  -o /cases/CASE-001 \\
  --veryverbose`}
          </pre>

          <h4>Step 3: MITRE Mapping</h4>
          <pre className="code-block">
{`# Map findings to ATT&CK
python3 -m rivendell.mitre.mapper /cases/CASE-001`}
          </pre>

          <h4>Step 4: Index for AI</h4>
          <pre className="code-block">
{`# Index artifacts for queries
rivendell-ai index CASE-001 /cases/CASE-001`}
          </pre>

          <h4>Step 5: Investigate</h4>
          <pre className="code-block">
{`# Query with AI
rivendell-ai query CASE-001 "What were the initial access vectors?"
rivendell-ai query CASE-001 "Show persistence mechanisms"
rivendell-ai query CASE-001 "List lateral movement activity"`}
          </pre>

          <h4>Step 6: Generate Report</h4>
          <pre className="code-block">
{`# Create summary report
rivendell-ai summary CASE-001 --format markdown --output report.md`}
          </pre>

          <h4>Step 7: Export to SIEM</h4>
          <pre className="code-block">
{`# Export to Splunk
python3 -m rivendell.siem.splunk_exporter \\
  --case-id CASE-001 \\
  --data-dir /cases/CASE-001 \\
  --hec-url https://splunk:8088 \\
  --hec-token YOUR_TOKEN`}
          </pre>

          <h4>Best Practices</h4>
          <ul>
            <li><strong>Always verify hashes</strong> - Check SHA256 of acquired evidence</li>
            <li><strong>Use encryption</strong> - Enable encryption for sensitive data</li>
            <li><strong>Document everything</strong> - Keep detailed investigation notes</li>
            <li><strong>Start with triage</strong> - Quick analysis to identify key artifacts</li>
            <li><strong>Use timelines</strong> - Timeline analysis reveals attack patterns</li>
            <li><strong>Map to MITRE</strong> - Understand attacker techniques</li>
            <li><strong>Leverage AI</strong> - Use natural language for insights</li>
          </ul>
        </>
      )
    },
    troubleshooting: {
      title: 'Troubleshooting',
      content: (
        <>
          <h3>Common Issues & Solutions</h3>

          <h4>"Tool not found" Errors</h4>
          <pre className="code-block">
{`# Check dependencies
elrond --check-dependencies

# Install missing tools
elrond --install

# Manual installation (Ubuntu/Debian)
sudo apt-get install volatility3 plaso-tools`}
          </pre>

          <h4>Memory Analysis Failures</h4>
          <pre className="code-block">
{`# Check memory dump
file /path/to/memory.dmp

# Try different profile
elrond -C -c CASE-001 -m /memory.dmp -p Win10x64_19041

# Use Volatility directly
vol3 -f /memory.dmp windows.info`}
          </pre>

          <h4>AI Agent Issues</h4>
          <pre className="code-block">
{`# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check vector database
rivendell-ai info CASE-001

# Re-index if needed
rivendell-ai reindex CASE-001`}
          </pre>

          <h4>SIEM Export Failures</h4>
          <pre className="code-block">
{`# Test Splunk connection
curl -k https://splunk:8088/services/collector/health

# Verify HEC token
python3 -m rivendell.siem.splunk_test --hec-token YOUR_TOKEN

# Check firewall rules
telnet splunk 8088`}
          </pre>

          <h4>Docker Issues</h4>
          <pre className="code-block">
{`# Check container status
docker-compose ps

# View logs
docker-compose logs rivendell

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d`}
          </pre>

          <h4>Debug Mode</h4>
          <pre className="code-block">
{`# Maximum verbosity
elrond -C -c CASE-001 -s /evidence --veryverbose

# Enable debug logs
export RIVENDELL_DEBUG=1
python3 -m rivendell.analysis.engine`}
          </pre>

          <h4>Getting Help</h4>
          <ul>
            <li>
              <strong>GitHub Issues:</strong>{' '}
              <a
                href="https://github.com/cmdaltr/rivendell/issues"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#a7db6c' }}
              >
                Report bugs and request features
              </a>
            </li>
            <li>
              <strong>GitHub:</strong>{' '}
              <a
                href="https://github.com/cmdaltr"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#a7db6c' }}
              >
                @cmdaltr
              </a>
            </li>
            <li><strong>Documentation:</strong> Check /docs directory for detailed guides</li>
          </ul>
        </>
      )
    }
  };

  return (
    <div className="journey-detail">
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
        <h2>Help & Documentation</h2>
        <p>
          Comprehensive guide to using the Rivendell DF Acceleration Suite.
        </p>
      </header>

      <div className="card">
        {/* Tab Navigation */}
        <div style={{
          display: 'flex',
          borderBottom: '2px solid #3f4b2a',
          marginBottom: '1.5rem',
          overflow: 'hidden',
          width: '100%'
        }}>
          {Object.keys(sections).map((key, index) => (
            <button
              key={key}
              onClick={() => setActiveSection(key)}
              style={{
                flex: '1 1 auto',
                padding: '0.75rem 0.5rem',
                background: activeSection === key ? 'rgba(167, 219, 108, 0.15)' : 'transparent',
                color: activeSection === key ? '#a7db6c' : '#888',
                border: 'none',
                borderBottom: activeSection === key ? '2px solid #a7db6c' : '2px solid transparent',
                marginBottom: '-2px',
                cursor: 'pointer',
                fontFamily: 'Cinzel, Times New Roman, serif',
                fontSize: '0.85rem',
                fontWeight: activeSection === key ? '600' : '400',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
                textAlign: 'center'
              }}
              onMouseOver={(e) => {
                if (activeSection !== key) {
                  e.target.style.color = '#a7db6c';
                  e.target.style.background = 'rgba(167, 219, 108, 0.05)';
                }
              }}
              onMouseOut={(e) => {
                if (activeSection !== key) {
                  e.target.style.color = '#888';
                  e.target.style.background = 'transparent';
                }
              }}
            >
              {sections[key].title}
            </button>
          ))}
        </div>

        <div className="help-content">
          {sections[activeSection].content}
        </div>

        <div style={{ marginTop: '3rem', padding: '1.5rem', background: 'rgba(167, 219, 108, 0.1)', borderRadius: '8px' }}>
          <h4>Additional Resources</h4>
          <ul>
            <li>
              <strong>Project Repository:</strong>{' '}
              <a
                href="https://github.com/cmdaltr/rivendell"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#a7db6c' }}
              >
                https://github.com/cmdaltr/rivendell
              </a>
            </li>
            <li>
              <strong>Author:</strong>{' '}
              <a
                href="https://github.com/cmdaltr"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#a7db6c' }}
              >
                @cmdaltr
              </a>
            </li>
            <li><strong>Version:</strong> 2.1.0</li>
            <li><strong>License:</strong> MIT</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;
