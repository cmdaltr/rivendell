# Rivendell Documentation

**Rivendell DF Acceleration Suite - Complete Documentation Index**

---

## Core Documentation

### 📘 Essential Reading

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
- **[USAGE.md](USAGE.md)** - Common tasks and workflows quick reference
- **[CONFIG.md](CONFIG.md)** - Configuration, setup, and troubleshooting
- **[PERFORMANCE.md](PERFORMANCE.md)** - Processing time per option, image type and size

### 🔧 Technical References

- **[API.md](API.md)** ⭐ - Complete REST API documentation with examples
- **[CLI.md](CLI.md)** ⭐ - Command-line tools reference (gandalf, elrond, MITRE, cloud, AI, SIEM)
- **[SECURITY.md](SECURITY.md)** - Security features, MFA, authentication, best practices

### 📐 Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, components, data flow
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - System requirements and dependencies

---

## Quick Navigation

### For New Users
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Read [USAGE.md](USAGE.md) for common tasks
3. Configure following [CONFIG.md](CONFIG.md)

### For Developers
1. Review [ARCHITECTURE.md](ARCHITECTURE.md)
2. Study [API.md](API.md) for REST endpoints
3. Read [SECURITY.md](SECURITY.md) for implementation details

### For API Users
**[API.md](API.md)** - Everything you need:
- Authentication (JWT, MFA, sessions)
- Job management endpoints
- Admin operations
- Request/response examples in Python, JavaScript, cURL

### For CLI Users
**[CLI.md](CLI.md)** - Complete command reference:
- Gandalf acquisition (local & remote)
- Elrond analysis (all modes)
- MITRE ATT&CK tools
- Cloud forensics (AWS, Azure, GCP)
- AI agent commands
- SIEM integration

### For Administrators
1. [CONFIG.md](CONFIG.md) - Configuration and tuning
2. [SECURITY.md](SECURITY.md) - Security hardening
3. [REQUIREMENTS.md](REQUIREMENTS.md) - System setup

---

## Documentation Structure

```
docs/
├── README.md              # This file - documentation index
├── QUICKSTART.md          # 5-minute getting started guide
├── USAGE.md               # Common tasks quick reference
├── CONFIG.md              # Configuration and troubleshooting
│
├── API.md                 # ⭐ REST API complete reference
├── CLI.md                 # ⭐ Command-line tools reference
├── SECURITY.md            # Security features and implementation
│
├── ARCHITECTURE.md        # System architecture and design
├── REQUIREMENTS.md        # System requirements
│
└── diagrams/              # Architecture diagrams
```

---

## Common Tasks

### Getting Started
```bash
# Access web interface
http://localhost:5687

# Default login
Email: admin@rivendell.app
Password: IWasThere3000YearsAgo!
```

### Creating an Analysis Job
```bash
# Via API
curl -X POST http://localhost:5688/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"case_number": "CASE-001", "source_paths": ["/Volumes/Evidence/disk.E01"], "options": {"analysis": true}}'

# Via CLI
python3 src/analysis/elrond.py CASE-001 /evidence /output/CASE-001 --Collect --Process --Analysis
```

See [USAGE.md](USAGE.md) for more examples.

---

## Getting Help

**Documentation Issues:**
- Found an error? Open an issue at https://github.com/cmdaltr/rivendell/issues

**Technical Support:**
1. Check [CONFIG.md](CONFIG.md) troubleshooting section
2. Review relevant documentation
3. Search GitHub issues

---

**Documentation Version:** 2.1.0
**Last Updated:** 2026-10-22
