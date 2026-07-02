# Accessing Analysis Data from Docker Containers

This guide explains how to access analysis results and job data from Rivendell Docker containers on your local machine.

## Quick Access: Shared Directory (Recommended)

**All job outputs are now automatically accessible at:**
```
/tmp/rivendell/
```

This directory is mounted from the Docker containers and contains:
- Analysis results
- Extracted artifacts
- Job logs
- SIEM export files
- Navigator JSON files

### Example: Finding Your Job Output

```bash
# List all job outputs
ls -la /tmp/rivendell/

# Open output directory in Finder
open /tmp/rivendell/

# View a specific job's output
ls -la /tmp/rivendell/CASE-ID-HERE/

# Copy results to your desktop
cp -R /tmp/rivendell/CASE-ID-HERE ~/Desktop/
```

## Directory Structure

```
/tmp/rivendell/
├── CASE-ID-001_output/
│   ├── image.E01/
│   │   ├── artefacts/
│   │   │   ├── raw/          # Raw extracted artifacts
│   │   │   └── cooked/       # Processed artifacts
│   │   ├── analysis/         # Analysis results
│   │   └── navigator.json    # MITRE ATT&CK Navigator file (if enabled)
│   └── splunk/               # Splunk export files (if enabled)
└── CASE-ID-002_output/
    └── ...
```

## Method 1: Direct File Access (Easiest)

Since `/tmp/rivendell/` is mounted, you can:

### In Finder:
1. Press `Cmd + Shift + G`
2. Type `/tmp/rivendell`
3. Press Enter

### In Terminal:
```bash
# Navigate to output directory
cd /tmp/rivendell

# List all outputs
ls -la

# Open in Finder
open .

# Copy to your Documents folder
cp -R /tmp/rivendell ~/Documents/forensics-data/
```

## Method 2: Docker Copy Command

If you need to copy data from other container locations:

```bash
# Copy from backend container
docker cp rivendell-app:/path/in/container ~/Desktop/

# Copy from Celery worker
docker cp rivendell-celery:/path/in/container ~/Desktop/

# Examples:
docker cp rivendell-celery:/tmp/elrond/output/CASE-ID ~/Desktop/
docker cp rivendell-app:/app/backend/logs ~/Desktop/rivendell-logs/
```

## Method 3: Browse Container Filesystem

Explore what's available in containers:

```bash
# List files in backend container
docker exec rivendell-app ls -la /tmp/elrond/output/

# List files in Celery worker
docker exec rivendell-celery ls -la /tmp/elrond/output/

# Interactive shell (advanced)
docker exec -it rivendell-celery bash
# Now you can navigate and use commands like ls, cat, find, etc.
# Type 'exit' to leave
```

## Method 4: Export as Archive

Create a compressed archive for easy transfer:

```bash
# Create tar.gz of all outputs
docker exec rivendell-celery tar czf /tmp/rivendell-export.tar.gz /tmp/elrond/output/

# Copy to your machine
docker cp rivendell-celery:/tmp/rivendell-export.tar.gz ~/Desktop/

# Extract on your machine
cd ~/Desktop
tar xzf rivendell-export.tar.gz
```

## SIEM Data Export Locations

### Splunk Data
- **Container Path**: `/tmp/elrond/output/CASE-ID/splunk/`
- **Local Path**: `/tmp/rivendell/CASE-ID_output/splunk/`
- **Access via Web**: http://localhost:7755 (username: admin, password: rivendell)

### Elasticsearch/Kibana Data
- **Container Path**: Docker volume `elasticsearch_data`
- **Access via Web**: http://localhost:5601
- **Export via Kibana**: Use Kibana's export features in the web UI

### MITRE ATT&CK Navigator
- **Container Path**: `/tmp/elrond/output/CASE-ID/*navigator*.json`
- **Local Path**: `/tmp/rivendell/CASE-ID_output/*navigator*.json`
- **Download via Web**: Click Navigator icon in job details page

## Troubleshooting

### "Permission Denied" when accessing /tmp/rivendell

```bash
# Fix permissions
sudo chmod -R 755 /tmp/rivendell

# Or change ownership to your user
sudo chown -R $(whoami) /tmp/rivendell
```

### Directory doesn't exist

```bash
# Create the directory
sudo mkdir -p /tmp/rivendell

# Set permissions
sudo chmod 755 /tmp/rivendell
```

### Can't find output files

```bash
# Check what's in the container
docker exec rivendell-celery ls -la /tmp/elrond/output/

# Check running jobs
docker ps | grep rivendell

# Check job status in web UI
# Navigate to http://localhost:3000/jobs
```

### Files are not appearing in /tmp/rivendell

```bash
# Restart containers to apply volume mounts
docker restart rivendell-app rivendell-celery

# Or restart all services
cd /path/to/rivendell/src/web
docker-compose restart
```

## Best Practices

1. **Regular Backups**: Copy completed analysis results to a permanent location
   ```bash
   cp -R /tmp/rivendell/CASE-ID-* ~/Documents/cases/
   ```

2. **Disk Space**: Monitor `/tmp/rivendell/` size - forensic data can be large
   ```bash
   du -sh /tmp/rivendell/*
   ```

3. **Clean Up**: Remove old job outputs when done
   ```bash
   rm -rf /tmp/rivendell/OLD-CASE-ID_output
   ```

4. **Archive Important Cases**: Create compressed archives for long-term storage
   ```bash
   tar czf ~/Archives/CASE-ID.tar.gz /tmp/rivendell/CASE-ID_output/
   ```

## Integration with External Tools

### Open results in forensic tools:
```bash
# Open artifacts in Autopsy, X-Ways, etc.
open -a "Autopsy" /tmp/rivendell/CASE-ID_output/artifacts/

# Open timeline in Excel
open -a "Microsoft Excel" /tmp/rivendell/CASE-ID_output/timeline.csv
```

### Process with scripts:
```bash
# Run custom analysis script on results
python analyze.py /tmp/rivendell/CASE-ID_output/

# Batch process multiple cases
for case in /tmp/rivendell/*_output/; do
    echo "Processing $case"
    ./process.sh "$case"
done
```

## Additional Resources

- **Docker Volumes Documentation**: https://docs.docker.com/storage/volumes/
- **Docker CP Command**: https://docs.docker.com/engine/reference/commandline/cp/
- **Rivendell API**: http://localhost:5688/docs

## Quick Reference Card

```bash
# View outputs in Finder
open /tmp/rivendell

# List all job outputs
ls -la /tmp/rivendell/

# Copy specific job to Desktop
cp -R /tmp/rivendell/CASE-ID ~/Desktop/

# Browse container files
docker exec rivendell-celery ls -la /tmp/elrond/output/

# Copy from container
docker cp rivendell-celery:/tmp/elrond/output/CASE-ID ~/Desktop/

# Check disk usage
du -sh /tmp/rivendell/*

# Clean up old data
rm -rf /tmp/rivendell/OLD-CASE-ID_output
```
