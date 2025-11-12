# SIEM Integration Setup Guide

This guide covers integration with Splunk and Elasticsearch, ensuring you're using the latest versions with proper authentication and dependencies.

## Table of Contents

- [Splunk Integration](#splunk-integration)
- [Elasticsearch Integration](#elasticsearch-integration)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

---

## Splunk Integration

### Latest Version Requirements

**Splunk Enterprise/Cloud: 9.x or higher**

- Download: [https://www.splunk.com/en_us/download.html](https://www.splunk.com/en_us/download.html)
- Documentation: [https://docs.splunk.com/](https://docs.splunk.com/)

### Prerequisites

1. **Splunk Enterprise** (9.0+) or **Splunk Cloud** instance
2. **HTTP Event Collector (HEC)** enabled
3. **Management API** access (port 8089)
4. **Admin credentials** or API token

### Installation Steps

#### 1. Install/Update Splunk

```bash
# Download latest Splunk Enterprise
wget -O splunk.tgz "https://download.splunk.com/products/splunk/releases/9.1.2/linux/splunk-9.1.2-b6436b649711-Linux-x86_64.tgz"

# Extract and install
tar xvzf splunk.tgz -C /opt

# Start Splunk
/opt/splunk/bin/splunk start --accept-license
```

#### 2. Enable HTTP Event Collector (HEC)

```bash
# Enable HEC via CLI
/opt/splunk/bin/splunk http-event-collector enable -uri https://localhost:8089 -auth admin:changeme

# Create HEC token
/opt/splunk/bin/splunk http-event-collector create rivendell-token \
    -uri https://localhost:8089 \
    -auth admin:changeme \
    -description "Rivendell DFIR Suite" \
    -disabled 0 \
    -index rivendell \
    -indexes rivendell
```

**Or via Web UI:**

1. Navigate to **Settings > Data Inputs > HTTP Event Collector**
2. Click **Global Settings**:
   - **All Tokens**: Enabled
   - **Default Source Type**: `_json`
   - **Default Index**: `rivendell`
   - **Enable SSL**: Yes (recommended)
3. Click **New Token**:
   - **Name**: `rivendell-token`
   - **Source type**: `rivendell:forensics`
   - **Allowed Indexes**: `rivendell, main`
   - **Index**: `rivendell`
4. Copy the generated token value

#### 3. Create Rivendell Index

```bash
# Create index via CLI
/opt/splunk/bin/splunk add index rivendell \
    -auth admin:changeme \
    -datatype event \
    -maxTotalDataSizeMB 500000 \
    -frozenTimePeriodInSecs 94608000
```

**Or via Web UI:**

1. Navigate to **Settings > Indexes**
2. Click **New Index**:
   - **Index Name**: `rivendell`
   - **Max Size**: 500000 MB (adjust as needed)
   - **Retention**: 3 years (adjust as needed)
3. Save

#### 4. Configure Rivendell

Create/edit `.env` file:

```bash
# Splunk Configuration (Latest: 9.x)
SPLUNK_ENABLED=true
SPLUNK_HOST=your-splunk-host.com
SPLUNK_PORT=8088
SPLUNK_HEC_TOKEN=your-hec-token-here
SPLUNK_INDEX=rivendell
SPLUNK_SOURCETYPE=rivendell:forensics
SPLUNK_SSL_VERIFY=true

# Management API (for app deployment)
SPLUNK_API_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-secure-password
SPLUNK_SCHEME=https
```

#### 5. Install Rivendell App for Splunk (Optional)

```bash
# Generate Splunk app during analysis
python3 analysis/elrond.py CASE-001 /evidence /output -CPAS

# The app will be generated in: /output/splunk/rivendell_app/

# Install the app
cp -r /output/splunk/rivendell_app/ /opt/splunk/etc/apps/
/opt/splunk/bin/splunk restart
```

### Authentication Options

#### Option 1: HEC Token (Recommended)

```bash
SPLUNK_HEC_TOKEN=your-hec-token-here
```

#### Option 2: Username/Password

```bash
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-password
```

#### Option 3: Bearer Token (API)

```bash
SPLUNK_BEARER_TOKEN=your-bearer-token
```

### Testing Connection

```bash
# Test HEC endpoint
curl -k https://your-splunk-host:8088/services/collector/event \
    -H "Authorization: Splunk your-hec-token" \
    -d '{"event": "test", "sourcetype": "rivendell:test"}'

# Expected response: {"text":"Success","code":0}
```

### MITRE ATT&CK Integration

The Rivendell Splunk app includes:

- **MITRE ATT&CK Framework** field extractions
- **Technique mappings** for all forensic artifacts
- **ATT&CK Navigator** JSON export
- **Dashboards** for technique visualization

Enable in `.env`:

```bash
MITRE_ATTACK_ENABLED=true
MITRE_NAVIGATOR_ENABLED=true
```

---

## Elasticsearch Integration

### Latest Version Requirements

**Elasticsearch: 8.x or higher** (Latest: 8.11+)

- Download: [https://www.elastic.co/downloads/elasticsearch](https://www.elastic.co/downloads/elasticsearch)
- Documentation: [https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

### Prerequisites

1. **Elasticsearch 8.x** cluster
2. **Kibana 8.x** (optional, for visualization)
3. **Security features enabled** (default in 8.x)
4. **TLS/SSL certificates** configured
5. **Authentication credentials** or API key

### Installation Steps

#### 1. Install/Update Elasticsearch

```bash
# Import Elasticsearch PGP key
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

# Add repository
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

# Install
sudo apt-get update && sudo apt-get install elasticsearch

# Start Elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

**Important:** On first start, Elasticsearch 8.x generates:
- Elastic superuser password
- Kibana enrollment token
- TLS certificates

**Save these credentials immediately!**

```bash
# Reset elastic password if needed
/usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

#### 2. Configure Security

Elasticsearch 8.x has security **enabled by default**. Configuration file: `/etc/elasticsearch/elasticsearch.yml`

```yaml
# Enable security features
xpack.security.enabled: true

# Enable TLS for HTTP
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: certs/http.p12

# Enable TLS for transport
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: certs/transport.p12
xpack.security.transport.ssl.truststore.path: certs/transport.p12

# Cluster name
cluster.name: rivendell-forensics

# Network
network.host: 0.0.0.0
http.port: 9200
```

Restart after changes:

```bash
sudo systemctl restart elasticsearch
```

#### 3. Create Rivendell Index Template

```bash
# Create index template with proper mappings
curl -k -u elastic:your-password -X PUT "https://localhost:9200/_index_template/rivendell-forensics" \
-H "Content-Type: application/json" \
-d '{
  "index_patterns": ["rivendell-forensics-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.mapping.total_fields.limit": 10000
    },
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "case_id": {"type": "keyword"},
        "hostname": {"type": "keyword"},
        "artifact_type": {"type": "keyword"},
        "artifact_path": {"type": "text"},
        "sha256": {"type": "keyword"},
        "mitre_attack": {
          "properties": {
            "technique_id": {"type": "keyword"},
            "technique_name": {"type": "text"},
            "tactic": {"type": "keyword"}
          }
        },
        "ioc": {
          "properties": {
            "type": {"type": "keyword"},
            "value": {"type": "keyword"},
            "severity": {"type": "keyword"}
          }
        }
      }
    }
  }
}'
```

#### 4. Create User and Role

```bash
# Create rivendell role
curl -k -u elastic:your-password -X POST "https://localhost:9200/_security/role/rivendell_writer" \
-H "Content-Type: application/json" \
-d '{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["rivendell-forensics-*"],
      "privileges": ["create_index", "write", "read", "view_index_metadata"]
    }
  ]
}'

# Create rivendell user
curl -k -u elastic:your-password -X POST "https://localhost:9200/_security/user/rivendell" \
-H "Content-Type: application/json" \
-d '{
  "password": "your-secure-password",
  "roles": ["rivendell_writer"],
  "full_name": "Rivendell DFIR",
  "email": "rivendell@example.com"
}'
```

#### 5. Generate API Key (Recommended)

```bash
# Create API key for Rivendell
curl -k -u elastic:your-password -X POST "https://localhost:9200/_security/api_key" \
-H "Content-Type: application/json" \
-d '{
  "name": "rivendell-api-key",
  "role_descriptors": {
    "rivendell_writer": {
      "cluster": ["monitor"],
      "index": [
        {
          "names": ["rivendell-forensics-*"],
          "privileges": ["create_index", "write", "read"]
        }
      ]
    }
  },
  "expiration": "365d"
}'

# Response will contain: {"id":"...","name":"...","api_key":"..."}
# Encode as: base64(id:api_key)
```

#### 6. Configure Rivendell

Create/edit `.env` file:

```bash
# Elasticsearch Configuration (Latest: 8.x)
ELASTIC_ENABLED=true
ELASTIC_HOST=your-elastic-host.com
ELASTIC_PORT=9200
ELASTIC_SCHEME=https
ELASTIC_INDEX=rivendell-forensics
ELASTIC_SSL_VERIFY=true

# Authentication Option 1: Username/Password
ELASTIC_USERNAME=rivendell
ELASTIC_PASSWORD=your-secure-password

# Authentication Option 2: API Key (Recommended)
ELASTIC_API_KEY=your-base64-encoded-api-key

# TLS Configuration
ELASTIC_CA_CERT=/etc/elasticsearch/certs/ca/ca.crt
ELASTIC_CLIENT_CERT=/etc/rivendell/certs/client.crt
ELASTIC_CLIENT_KEY=/etc/rivendell/certs/client.key

# Kibana (optional)
KIBANA_ENABLED=true
KIBANA_HOST=your-kibana-host.com
KIBANA_PORT=5601
KIBANA_USERNAME=elastic
KIBANA_PASSWORD=your-password
```

### Testing Connection

```bash
# Test with username/password
curl -k -u rivendell:your-password https://localhost:9200/_cluster/health

# Test with API key
curl -k -H "Authorization: ApiKey your-base64-api-key" https://localhost:9200/_cluster/health

# Expected response: {"cluster_name":"...","status":"green",...}
```

### Install Kibana (Optional)

```bash
# Install Kibana
sudo apt-get install kibana

# Configure Kibana (/etc/kibana/kibana.yml)
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["https://localhost:9200"]
elasticsearch.username: "kibana_system"
elasticsearch.password: "your-kibana-password"
elasticsearch.ssl.verificationMode: certificate
elasticsearch.ssl.certificateAuthorities: ["/etc/elasticsearch/certs/ca/ca.crt"]

# Start Kibana
sudo systemctl start kibana
sudo systemctl enable kibana
```

### Kibana Dashboard Import

After analysis, Rivendell generates Kibana dashboards:

```bash
# Export location
/output/elastic/kibana_dashboards.ndjson

# Import via UI:
# Kibana > Stack Management > Saved Objects > Import

# Or via API:
curl -k -u elastic:your-password -X POST "https://localhost:5601/api/saved_objects/_import" \
-H "kbn-xsrf: true" \
--form file=@kibana_dashboards.ndjson
```

---

## Security Best Practices

### 1. Use Strong Authentication

**DO:**
- ✅ Use API keys with limited permissions
- ✅ Rotate credentials regularly
- ✅ Use strong, unique passwords (20+ characters)
- ✅ Enable multi-factor authentication

**DON'T:**
- ❌ Use default passwords
- ❌ Share credentials between systems
- ❌ Store credentials in code

### 2. Enable TLS/SSL

**Splunk:**
```bash
# Force HTTPS for HEC
/opt/splunk/bin/splunk http-event-collector update -uri https://localhost:8089 -auth admin:changeme -enable-ssl 1
```

**Elasticsearch:**
```yaml
# Always use HTTPS in 8.x (enabled by default)
xpack.security.http.ssl.enabled: true
```

### 3. Network Security

- Use firewall rules to restrict access
- Enable IP whitelisting where possible
- Use VPN for remote access
- Isolate SIEM in secure network segment

**Splunk firewall rules:**
```bash
# Allow HEC (8088) and API (8089) only from Rivendell host
sudo ufw allow from 192.168.1.100 to any port 8088 proto tcp
sudo ufw allow from 192.168.1.100 to any port 8089 proto tcp
```

**Elasticsearch firewall rules:**
```bash
# Allow port 9200 only from Rivendell host
sudo ufw allow from 192.168.1.100 to any port 9200 proto tcp
```

### 4. Monitor and Audit

**Splunk:**
```spl
index=_audit action=* | stats count by action, user, info
```

**Elasticsearch:**
```json
GET /_security/_authenticate
GET /_security/user
GET /_security/role
```

### 5. Regular Updates

```bash
# Check versions
/opt/splunk/bin/splunk version  # Splunk
curl -k -u elastic:password https://localhost:9200  # Elasticsearch

# Update Splunk
/opt/splunk/bin/splunk stop
# Download and install new version
/opt/splunk/bin/splunk start

# Update Elasticsearch (Debian/Ubuntu)
sudo apt-get update && sudo apt-get upgrade elasticsearch kibana
```

---

## Troubleshooting

### Splunk Issues

#### HEC Token Not Working

```bash
# Verify HEC is enabled
/opt/splunk/bin/splunk http-event-collector list -uri https://localhost:8089 -auth admin:changeme

# Test HEC endpoint
curl -k https://localhost:8088/services/collector/event \
    -H "Authorization: Splunk YOUR-TOKEN" \
    -d '{"event":"test"}'
```

#### SSL Certificate Errors

```bash
# Disable SSL verification (NOT recommended for production)
SPLUNK_SSL_VERIFY=false

# Or add certificate to trust store
cp /opt/splunk/etc/auth/cacert.pem /etc/ssl/certs/splunk-ca.crt
update-ca-certificates
```

### Elasticsearch Issues

#### Authentication Failed

```bash
# Reset elastic password
/usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i

# Verify credentials
curl -k -u elastic:new-password https://localhost:9200/_cluster/health
```

#### Connection Refused

```bash
# Check Elasticsearch is running
sudo systemctl status elasticsearch

# Check logs
sudo journalctl -u elasticsearch -f

# Verify network binding
curl -k https://localhost:9200
```

#### Certificate Verification Failed

```bash
# Option 1: Disable verification (NOT recommended for production)
ELASTIC_SSL_VERIFY=false

# Option 2: Add CA certificate
ELASTIC_CA_CERT=/etc/elasticsearch/certs/ca/ca.crt

# Option 3: Use system trust store
cp /etc/elasticsearch/certs/ca/ca.crt /usr/local/share/ca-certificates/
update-ca-certificates
```

### Index/Ingest Issues

#### Index Creation Failed

```bash
# Check index template
curl -k -u elastic:password https://localhost:9200/_index_template/rivendell-forensics

# Delete and recreate if needed
curl -k -u elastic:password -X DELETE https://localhost:9200/_index_template/rivendell-forensics
# Then recreate with correct mappings
```

#### Bulk Ingest Errors

```bash
# Check cluster health
curl -k -u elastic:password https://localhost:9200/_cluster/health

# Check node stats
curl -k -u elastic:password https://localhost:9200/_nodes/stats

# Increase bulk size limits if needed (elasticsearch.yml)
http.max_content_length: 500mb
```

---

## Version Compatibility Matrix

| Rivendell | Splunk | Elasticsearch | Python | Docker |
|-----------|--------|---------------|--------|--------|
| 2.0.x     | 9.0+   | 8.0+          | 3.8+   | 20.10+ |

---

## Additional Resources

- **Splunk Documentation**: [https://docs.splunk.com/](https://docs.splunk.com/)
- **Elasticsearch Documentation**: [https://www.elastic.co/guide/](https://www.elastic.co/guide/)
- **MITRE ATT&CK**: [https://attack.mitre.org/](https://attack.mitre.org/)
- **Rivendell GitHub**: [https://github.com/yourusername/rivendell](https://github.com/yourusername/rivendell)

---

**Note:** Always refer to official vendor documentation for the most up-to-date installation and configuration instructions.
