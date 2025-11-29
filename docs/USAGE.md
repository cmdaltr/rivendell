# Rivendell Usage Guide

**Version:** 2.1.0
**Quick Reference for Common Tasks**

---

## Quick Links

- **[API.md](API.md)** - Complete REST API reference
- **[CLI.md](CLI.md)** - Command-line interface guide
- **[CONFIG.md](CONFIG.md)** - Configuration and setup
- **[SECURITY.md](SECURITY.md)** - Security features and best practices

---

## Getting Started

### 1. Access the Web Interface

Open your browser to: **http://localhost:5687**

**Default Login:**
- **Email**: admin@rivendell.app
- **Password**: IWasThere3000YearsAgo!

⚠️ **Change this password immediately in production!**

### 2. Create a Forensic Analysis Job

**Via Web Interface:**
1. Click "New Analysis"
2. Enter case number (e.g., "CASE-2025-001")
3. Browse and select disk/memory images
4. Configure analysis options
5. Click "Start Analysis"

**Via API:**
```bash
curl -X POST http://localhost:5688/api/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "CASE-2025-001",
    "source_paths": ["/evidence/disk.E01"],
    "destination_path": "/output/CASE-2025-001",
    "options": {
      "collect": true,
      "analyze": true,
      "memory_analysis": false
    }
  }'
```

**Via CLI:**
```bash
elrond -C -P -A CASE-2025-001 /evidence/disk.E01 /output/CASE-2025-001
```

---

## Common Workflows

### Complete Investigation

**Step 1: Acquire Evidence** (if needed)
```bash
# Remote acquisition
python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u admin -M -o /evidence/CASE-001
```

**Step 2: Start Analysis**
- Use web interface or API to create job
- Select disk image and memory dump
- Enable desired analysis options

**Step 3: Monitor Progress**
- View real-time progress in web interface
- Check logs tab for detailed output
- Wait for completion (can take hours)

**Step 4: Review Results**
- View completed job details
- Download analysis reports
- Export to SIEM if needed

### Quick Triage

For rapid initial analysis:

**CLI:**
```bash
elrond -C -P -A -q TRIAGE-001 /evidence/disk.E01 /output/TRIAGE-001
```

**Web Interface:**
- Select "Quick" speed mode
- Disable optional analysis modules
- Focus on IOC extraction

### Memory-Only Analysis

For memory dump analysis only:

**CLI:**
```bash
elrond -M MEMORY-001 /evidence/memory.dmp /output/MEMORY-001
```

**Web Interface:**
- Create new analysis job
- Select only memory dump file
- Enable memory analysis option

---

## User Management

### Create New User

**Via Web Interface** (Admin only):
1. Navigate to Admin → Users
2. Click "Create User"
3. Fill in details
4. Assign role (Admin/User/Guest)
5. Click "Create"

**Via API:**
```bash
curl -X POST http://localhost:5688/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@company.com",
    "username": "analyst1",
    "password": "SecurePass123!",
    "full_name": "Security Analyst"
  }'
```

### Enable Multi-Factor Authentication (MFA)

**For Your Account:**
1. Click your profile → Security
2. Click "Enable MFA"
3. Scan QR code with authenticator app
4. Enter verification code
5. Save backup codes securely!

**For Other Users (Admin):**
1. Navigate to Admin → Users
2. Select user
3. Click "Reset MFA" to disable (emergency)

### Reset User Password (Admin)

**Via Web Interface:**
1. Navigate to Admin → Users
2. Select user
3. Click "Reset Password"
4. Enter new password
5. Click "Confirm"

**Via API:**
```bash
curl -X POST http://localhost:5688/api/auth/admin/reset-user-password \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid-here",
    "new_password": "NewSecurePass123!"
  }'
```

---

## Job Management

### List Jobs

**Web Interface:** Dashboard shows all your jobs

**API:**
```bash
# All jobs
curl http://localhost:5688/api/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by status
curl "http://localhost:5688/api/jobs?status=running" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cancel Running Job

**Web Interface:** Click "Cancel" button on job card

**API:**
```bash
curl -X POST http://localhost:5688/api/jobs/{job_id}/cancel \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**CLI:**
```bash
# Cancel via Celery
celery -A tasks control revoke {task_id}
```

### Restart Failed Job

**Web Interface:** Click "Restart" button on failed job

**API:**
```bash
curl -X POST http://localhost:5688/api/jobs/{job_id}/restart \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Archive Completed Jobs

**Web Interface:** Select jobs → Bulk Actions → Archive

**API:**
```bash
curl -X POST http://localhost:5688/api/jobs/bulk/archive \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_ids": ["uuid1", "uuid2"]}'
```

### Delete Jobs

**Web Interface:** Select jobs → Bulk Actions → Delete

**API:**
```bash
curl -X DELETE http://localhost:5688/api/jobs/{job_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

⚠️ **Cannot delete running jobs** - cancel first, then delete

---

## File System Browsing

### Browse Evidence Directory

**Web Interface:**
- File browser automatically shows allowed directories
- Navigate by clicking folders
- Select files by clicking checkboxes

**Allowed Directories** (configured in `config.py`):
- `/tmp/rivendell` (macOS native)
- `/host/tmp/rivendell` (Docker on Mac)
- `/mnt`, `/media`, `/Volumes` (Linux/macOS)
- `C:\Temp\rivendell` (Windows)

### Supported Image Formats

**Disk Images:**
- E01, Ex01 (EnCase)
- DD, RAW, IMG, BIN (Raw)
- VMDK (VMware)
- VHD, VHDX (Hyper-V)

**Memory Dumps:**
- MEM, DMP (Raw memory)
- LIME (LiME format)
- VMEM (VMware snapshot)

---

## Viewing Results

### Access Output Files

**Docker (host machine):**
```bash
# Output is in Docker volume
docker volume inspect rivendell-output

# Copy from container
docker cp rivendell-app:/output/CASE-001 ./local-output/
```

**Native Installation:**
```bash
# Default output directory
ls -la /tmp/elrond/output/CASE-001/
```

### Output Structure

```
/output/CASE-001/
├── collected/           # Collected artifacts
├── processed/           # Parsed data (CSV/JSON)
├── analysis/            # Analysis results
├── memory/              # Memory analysis output
└── logs/                # Execution logs
```

### Common Result Files

```bash
# Timeline
cat /output/CASE-001/processed/timeline.csv

# Registry analysis
cat /output/CASE-001/processed/registry.csv

# Event logs
cat /output/CASE-001/processed/event_logs.csv

# IOCs
cat /output/CASE-001/analysis/iocs.csv

# Memory processes
cat /output/CASE-001/memory/processes.csv
```

---

## Integration Examples

### Export to Splunk

```bash
python3 -m rivendell.siem.splunk_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --hec-url https://splunk:8088 \
  --hec-token YOUR_HEC_TOKEN
```

### Export to Elasticsearch

```bash
python3 -m rivendell.siem.elastic_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --elastic-url https://elastic:9200 \
  --index rivendell-case-001
```

### Generate MITRE ATT&CK Mapping

```bash
# Map artifacts to techniques
python3 -m rivendell.mitre.mapper /output/CASE-001

# Generate Navigator layer
python3 -m rivendell.mitre.navigator /output/CASE-001 -o navigator.json
```

---

## API Authentication

### Login and Get Token

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:5688/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@rivendell.app", "password": "RivendellAdmin123!"}' \
  | jq -r '.access_token')

# Use token in requests
curl http://localhost:5688/api/jobs \
  -H "Authorization: Bearer $TOKEN"
```

### Login with MFA

```bash
# Step 1: Login (returns temp_token if MFA enabled)
TEMP_TOKEN=$(curl -s -X POST http://localhost:5688/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}' \
  | jq -r '.temp_token')

# Step 2: Verify MFA code
TOKEN=$(curl -s -X POST http://localhost:5688/api/auth/mfa/verify \
  -H "Content-Type: application/json" \
  -d '{"temp_token": "'$TEMP_TOKEN'", "code": "123456"}' \
  | jq -r '.access_token')
```

---

## Keyboard Shortcuts

**Web Interface (when available):**
- `n` - New Analysis
- `r` - Refresh job list
- `Escape` - Close modal/dialog
- `/` - Focus search

---

## Tips and Best Practices

### Performance

1. **Use SSD/NVMe** for evidence and output directories
2. **Limit concurrent jobs** (default: 3) based on available resources
3. **Close browser tabs** monitoring jobs to reduce load
4. **Archive old jobs** to keep database performant

### Security

1. **Change default password** immediately
2. **Enable MFA** for all admin accounts
3. **Use HTTPS** in production (configure reverse proxy)
4. **Limit allowed_paths** to necessary directories only
5. **Regular backups** of database and configuration

### Workflow

1. **Use meaningful case numbers** (e.g., CASE-2025-001)
2. **Document analysis options** used for each case
3. **Save backup codes** when enabling MFA
4. **Check logs** if job fails
5. **Export results** to SIEM for long-term storage

---

## Troubleshooting

### Job Stuck in "Pending"

**Check Celery worker:**
```bash
docker logs rivendell-celery
```

**Restart worker:**
```bash
docker restart rivendell-celery
```

### "Failed to load directory"

**Check permissions:**
```bash
chmod 755 /tmp/rivendell
ls -la /tmp/rivendell
```

**Verify allowed_paths** in `/src/web/backend/config.py`

### Can't Login

**Reset admin password:**
```bash
docker exec -it rivendell-postgres psql -U rivendell -d rivendell \
  -c "UPDATE users SET hashed_password='NEW_HASH' WHERE email='admin@rivendell.app';"
```

**Disable MFA (emergency):**
```bash
docker exec -it rivendell-postgres psql -U rivendell -d rivendell \
  -c "UPDATE users SET mfa_enabled=false WHERE email='user@example.com';"
```

---

## Further Reading

- **[API.md](API.md)** - Complete REST API documentation with examples
- **[CLI.md](CLI.md)** - Command-line tools (gandalf, elrond, MITRE, cloud, AI)
- **[CONFIG.md](CONFIG.md)** - Configuration options and tuning
- **[SECURITY.md](SECURITY.md)** - Security implementation details
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute getting started guide

---

**Version:** 2.1.0
**Last Updated:** 2025-01-15
