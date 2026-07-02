# Rivendell — Project Context

## What this is

Rivendell is a unified DFIR platform — the merger of Elrond (analysis) and Gandalf (acquisition) into a single directed-graph execution model. It is Ben's primary professional tool, not a side project. Treat it accordingly.

## Architecture

```
Gandalf (acquisition) → Elrond (analysis) → Eru (AI analyst)
         ↓                      ↓                  ↓
  Remote collection      30+ forensic tools    MCP tool server
  SSH + PowerShell       Volatility3, Plaso     FastAPI backend
  SHA256 integrity       RegRipper, EvtxCmd     LLM integration
```

- **Execution model:** directed graph, not linear pipeline — conditional branching per OS, cloud provider, and evidence type
- **Scale:** 50,000+ lines, 30+ integrated tools, 600+ MITRE ATT&CK techniques
- **Platform support:** Windows, Linux, macOS, AWS, Azure, GCP
- **Output:** structured JSON throughout — consistent schema, parseable downstream

## Naming conventions — do not change these

- The platform: **Rivendell**
- Acquisition module: **Gandalf**
- Analysis module: **Elrond**
- AI analyst: **Eru**
- All Tolkien names are intentional and load-bearing for docs, CLI output, and logging

## Stack

- Python 3.12, FastAPI, Typer (CLI), Rich (terminal output)
- SQLite for case data; optional Postgres for production deployments
- openpyxl for XLSX output
- Volatility 3, Plaso, RegRipper, EvtxCmd, Bulk Extractor as subprocess calls
- MCP server for Eru tool integration (`mcp/tools/`)
- Ollama (local) or Anthropic API for Eru LLM backend

## Code conventions

- Type hints on all functions
- Docstrings on public functions and classes
- `pathlib` over `os.path`
- f-strings throughout
- Rich tables for CLI output — match existing patterns
- Logging via the existing project logger — do not add print statements
- Error handling: raise specific exceptions, catch at the CLI boundary
- New forensic tool integrations go in `rivendell/tools/` following existing module pattern

## What Eru touches

Eru is the AI layer. It receives structured case output from Elrond and provides:
- Automated MITRE ATT&CK mapping
- IOC pivoting and enrichment
- Natural language case summaries
- Threat intel correlation (including the Iran APT XLSX integration)

Eru's MCP tools live in `mcp/tools/`. When adding new Eru capabilities, register them via the existing FastMCP server setup — do not create a parallel registration system.

## Active work / known context

- Iran APT threat intel XLSX integration is in progress — `rivendell/threat_intel/iran_apt_loader.py`
- 10-column schema: Evidential Element, Threat Group, Procedure Example, Technique ID, Technique Name, Tactic, Contextual Evidence, Reference URL, Navigation Layer URL, Source Type
- `enrich_artefact()` is the primary Eru-facing function — given a process name, command, or file path, return all matching indicators
- SQLite table `threat_intel_indicators` — do not rename or restructure without asking

## What not to do

- Do not rename Gandalf, Elrond, or Eru
- Do not restructure the execution graph model without explicit instruction
- Do not add new Python dependencies without checking requirements.txt first
- Do not convert subprocess tool calls to library imports — the subprocess boundary is intentional (isolation)
- Do not add print statements — use the existing logger
