# Cloud Forensics Implementation Guide

## Overview

This guide provides detailed implementation steps for adding cloud forensics capabilities to the Rivendell DFIR Suite, enabling acquisition and analysis of forensic artifacts from AWS, Azure, and GCP cloud environments.

---

## Table of Contents

- [1. Architecture Overview](#1-architecture-overview)
- [2. Cloud Provider Support](#2-cloud-provider-support)
- [3. Database Schema Updates](#3-database-schema-updates)
- [4. Backend Implementation](#4-backend-implementation)
- [5. Frontend Implementation](#5-frontend-implementation)
- [6. Cloud Artifact Collection](#6-cloud-artifact-collection)
- [7. API Integration](#7-api-integration)
- [8. Security Considerations](#8-security-considerations)

---

## 1. Architecture Overview

### Cloud Forensics Workflow

```
┌────────────────────────────────────────────────────────────────┐
│                   CLOUD FORENSICS PIPELINE                      │
└────────────────────────────────────────────────────────────────┘

User Selection          Cloud API           Artifact Collection
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│              │     │              │     │                  │
│ Select Cloud │────>│ Authenticate │────>│ Collect Compute  │
│ Provider:    │     │ with Cloud   │     │ Collect Storage  │
│  • AWS       │     │ Credentials  │     │ Collect Network  │
│  • Azure     │     │              │     │ Collect Identity │
│  • GCP       │     │              │     │ Collect Logs     │
│              │     │              │     │                  │
└──────────────┘     └──────────────┘     └──────────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────┐
                                          │                  │
                                          │ Store & Analyze  │
                                          │ Forensic Data    │
                                          │                  │
                                          └──────────────────┘
```

---

## 2. Cloud Provider Support

### 2.1 Host Selection Enhancement

**Current State:**
- Host dropdown contains only "Local", "Remote", "Network"

**Enhanced State:**
```
Host Types:
├── Local (existing)
├── Remote (existing)
├── Network (existing)
├── AWS      ← NEW (with AWS logo)
├── Azure    ← NEW (with Azure logo)
└── GCP      ← NEW (with GCP logo)
```

### 2.2 Cloud Provider Metadata

**File:** `src/web/backend/models/cloud.py` (NEW)
```python
"""
Cloud Provider Models

Models for cloud forensics providers and artifact types.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    """Cloud provider enumeration."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CloudArtifactType(str, Enum):
    """Cloud-agnostic artifact types."""
    COMPUTE = "compute"           # EC2, VM, Compute Engine
    STORAGE = "storage"           # S3, Blob Storage, Cloud Storage
    NETWORK = "network"           # VPC, VNet, VPC
    IDENTITY = "identity"         # IAM, Azure AD, IAM
    LOGS = "logs"                 # CloudTrail, Monitor, Cloud Logging
    DATABASE = "database"         # RDS, SQL Database, Cloud SQL
    CONTAINER = "container"       # ECS, AKS, GKE
    SERVERLESS = "serverless"     # Lambda, Functions, Cloud Functions
    SECURITY = "security"         # GuardDuty, Defender, Security Command Center


class CloudCredentials(BaseModel):
    """Cloud provider credentials."""
    provider: CloudProvider
    credentials: Dict[str, str]  # Encrypted storage
    region: Optional[str] = None
    account_id: Optional[str] = None
    subscription_id: Optional[str] = None  # Azure
    project_id: Optional[str] = None       # GCP


class CloudArtifact(BaseModel):
    """Cloud artifact definition."""
    artifact_type: CloudArtifactType
    provider: CloudProvider
    resource_id: str
    resource_name: Optional[str] = None
    region: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CloudCollectionOptions(BaseModel):
    """Options for cloud artifact collection."""
    provider: CloudProvider
    artifacts: List[CloudArtifactType]
    regions: List[str] = Field(default_factory=list)  # All regions if empty
    include_deleted: bool = False
    snapshot_disks: bool = True  # For Compute instances
    export_logs: bool = True
    timeframe_hours: int = 24  # How far back to collect logs
```

---

## 3. Database Schema Updates

### 3.1 Add Cloud Provider Tables

**Migration:** `alembic/versions/add_cloud_support.py` (NEW)
```python
"""Add cloud forensics support

Revision ID: cloud_001
Revises: initial_schema
Create Date: 2025-01-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'cloud_001'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create cloud_credentials table
    op.create_table(
        'cloud_credentials',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('credentials', postgresql.JSON, nullable=False),  # Encrypted
        sa.Column('region', sa.String(50)),
        sa.Column('account_id', sa.String(255)),
        sa.Column('subscription_id', sa.String(255)),  # Azure
        sa.Column('project_id', sa.String(255)),       # GCP
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    # Create cloud_artifacts table
    op.create_table(
        'cloud_artifacts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('artifact_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('resource_id', sa.String(512), nullable=False),
        sa.Column('resource_name', sa.String(512)),
        sa.Column('region', sa.String(50)),
        sa.Column('metadata', postgresql.JSON),
        sa.Column('collected_at', sa.DateTime, nullable=False),
        sa.Column('file_path', sa.String(1024)),  # Path to stored artifact
        sa.Column('size_bytes', sa.BigInteger),
    )

    # Add indexes
    op.create_index('idx_cloud_creds_user', 'cloud_credentials', ['user_id'])
    op.create_index('idx_cloud_creds_provider', 'cloud_credentials', ['provider'])
    op.create_index('idx_cloud_artifacts_job', 'cloud_artifacts', ['job_id'])
    op.create_index('idx_cloud_artifacts_type', 'cloud_artifacts', ['artifact_type'])
    op.create_index('idx_cloud_artifacts_provider', 'cloud_artifacts', ['provider'])


def downgrade():
    op.drop_index('idx_cloud_artifacts_provider')
    op.drop_index('idx_cloud_artifacts_type')
    op.drop_index('idx_cloud_artifacts_job')
    op.drop_index('idx_cloud_creds_provider')
    op.drop_index('idx_cloud_creds_user')
    op.drop_table('cloud_artifacts')
    op.drop_table('cloud_credentials')
```

---

## 4. Backend Implementation

### 4.1 Cloud Collection Engines

**File:** `src/acquisition/cloud/aws_collector.py` (NEW)
```python
"""
AWS Artifact Collector

Collects forensic artifacts from AWS environments.
"""

import boto3
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base_collector import BaseCloudCollector, CloudArtifact


class AWSCollector(BaseCloudCollector):
    """AWS artifact collector."""

    def __init__(self, credentials: Dict[str, str], region: str = 'us-east-1'):
        """
        Initialize AWS collector.

        Args:
            credentials: AWS credentials (access_key_id, secret_access_key)
            region: AWS region
        """
        self.region = region
        self.session = boto3.Session(
            aws_access_key_id=credentials['access_key_id'],
            aws_secret_access_key=credentials['secret_access_key'],
            region_name=region
        )

    async def collect_compute(self) -> List[CloudArtifact]:
        """
        Collect EC2 compute artifacts.

        Returns:
            List of CloudArtifact objects for EC2 instances
        """
        ec2 = self.session.client('ec2')
        artifacts = []

        # Get all EC2 instances
        response = ec2.describe_instances()

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                artifact = CloudArtifact(
                    artifact_type='compute',
                    provider='aws',
                    resource_id=instance['InstanceId'],
                    resource_name=self._get_instance_name(instance),
                    region=self.region,
                    metadata={
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId'),
                        'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                    }
                )
                artifacts.append(artifact)

                # Create snapshot of attached volumes
                for bdm in instance.get('BlockDeviceMappings', []):
                    if 'Ebs' in bdm:
                        volume_id = bdm['Ebs']['VolumeId']
                        self._create_volume_snapshot(ec2, volume_id, instance['InstanceId'])

        return artifacts

    async def collect_storage(self) -> List[CloudArtifact]:
        """
        Collect S3 storage artifacts.

        Returns:
            List of CloudArtifact objects for S3 buckets
        """
        s3 = self.session.client('s3')
        artifacts = []

        # Get all S3 buckets
        response = s3.list_buckets()

        for bucket in response['Buckets']:
            bucket_name = bucket['Name']

            # Get bucket metadata
            try:
                location = s3.get_bucket_location(Bucket=bucket_name)
                versioning = s3.get_bucket_versioning(Bucket=bucket_name)
                encryption = s3.get_bucket_encryption(Bucket=bucket_name)
            except Exception as e:
                print(f"Error getting bucket metadata for {bucket_name}: {e}")
                continue

            artifact = CloudArtifact(
                artifact_type='storage',
                provider='aws',
                resource_id=bucket_name,
                resource_name=bucket_name,
                region=location.get('LocationConstraint', 'us-east-1'),
                metadata={
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'versioning': versioning.get('Status', 'Disabled'),
                    'encryption': encryption.get('ServerSideEncryptionConfiguration', {}),
                }
            )
            artifacts.append(artifact)

        return artifacts

    async def collect_network(self) -> List[CloudArtifact]:
        """
        Collect VPC network artifacts.

        Returns:
            List of CloudArtifact objects for VPCs, subnets, security groups
        """
        ec2 = self.session.client('ec2')
        artifacts = []

        # Get VPCs
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            artifact = CloudArtifact(
                artifact_type='network',
                provider='aws',
                resource_id=vpc['VpcId'],
                resource_name=self._get_tag_value(vpc.get('Tags', []), 'Name'),
                region=self.region,
                metadata={
                    'cidr_block': vpc['CidrBlock'],
                    'is_default': vpc['IsDefault'],
                    'state': vpc['State'],
                }
            )
            artifacts.append(artifact)

        # Get Security Groups
        sgs = ec2.describe_security_groups()
        for sg in sgs['SecurityGroups']:
            artifact = CloudArtifact(
                artifact_type='network',
                provider='aws',
                resource_id=sg['GroupId'],
                resource_name=sg['GroupName'],
                region=self.region,
                metadata={
                    'description': sg['Description'],
                    'vpc_id': sg.get('VpcId'),
                    'ingress_rules': sg['IpPermissions'],
                    'egress_rules': sg['IpPermissionsEgress'],
                }
            )
            artifacts.append(artifact)

        return artifacts

    async def collect_identity(self) -> List[CloudArtifact]:
        """
        Collect IAM identity artifacts.

        Returns:
            List of CloudArtifact objects for IAM users, roles, policies
        """
        iam = self.session.client('iam')
        artifacts = []

        # Get IAM users
        users = iam.list_users()
        for user in users['Users']:
            # Get user policies and groups
            policies = iam.list_attached_user_policies(UserName=user['UserName'])
            groups = iam.list_groups_for_user(UserName=user['UserName'])

            artifact = CloudArtifact(
                artifact_type='identity',
                provider='aws',
                resource_id=user['UserId'],
                resource_name=user['UserName'],
                region='global',  # IAM is global
                metadata={
                    'arn': user['Arn'],
                    'create_date': user['CreateDate'].isoformat(),
                    'password_last_used': user.get('PasswordLastUsed', datetime.now()).isoformat(),
                    'attached_policies': [p['PolicyArn'] for p in policies['AttachedPolicies']],
                    'groups': [g['GroupName'] for g in groups['Groups']],
                }
            )
            artifacts.append(artifact)

        return artifacts

    async def collect_logs(self, hours: int = 24) -> List[CloudArtifact]:
        """
        Collect CloudTrail logs.

        Args:
            hours: How far back to collect logs

        Returns:
            List of CloudArtifact objects for CloudTrail events
        """
        cloudtrail = self.session.client('cloudtrail')
        artifacts = []

        # Get CloudTrail events
        start_time = datetime.now() - timedelta(hours=hours)
        response = cloudtrail.lookup_events(
            StartTime=start_time,
            MaxResults=1000
        )

        for event in response['Events']:
            artifact = CloudArtifact(
                artifact_type='logs',
                provider='aws',
                resource_id=event['EventId'],
                resource_name=event['EventName'],
                region=self.region,
                metadata={
                    'event_time': event['EventTime'].isoformat(),
                    'event_source': event['EventSource'],
                    'username': event.get('Username'),
                    'resources': event.get('Resources', []),
                    'cloud_trail_event': event.get('CloudTrailEvent'),
                }
            )
            artifacts.append(artifact)

        return artifacts

    def _create_volume_snapshot(self, ec2_client, volume_id: str, instance_id: str):
        """Create snapshot of EBS volume for forensic analysis."""
        try:
            snapshot = ec2_client.create_snapshot(
                VolumeId=volume_id,
                Description=f"Forensic snapshot of {volume_id} from {instance_id}",
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {'Key': 'Purpose', 'Value': 'Forensic Analysis'},
                            {'Key': 'InstanceId', 'Value': instance_id'},
                            {'Key': 'CreatedBy', 'Value': 'Rivendell-Gandalf'},
                        ]
                    }
                ]
            )
            print(f"Created snapshot {snapshot['SnapshotId']} for volume {volume_id}")
        except Exception as e:
            print(f"Error creating snapshot for volume {volume_id}: {e}")

    def _get_instance_name(self, instance: Dict) -> str:
        """Extract instance name from tags."""
        return self._get_tag_value(instance.get('Tags', []), 'Name') or instance['InstanceId']

    def _get_tag_value(self, tags: List[Dict], key: str) -> str:
        """Get tag value by key."""
        for tag in tags:
            if tag['Key'] == key:
                return tag['Value']
        return ''
```

### 4.2 Azure Collector (Stub)

**File:** `src/acquisition/cloud/azure_collector.py` (NEW)
```python
"""
Azure Artifact Collector

Collects forensic artifacts from Azure environments.
"""

from typing import List, Dict
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient

from .base_collector import BaseCloudCollector, CloudArtifact


class AzureCollector(BaseCloudCollector):
    """Azure artifact collector."""

    def __init__(self, credentials: Dict[str, str], subscription_id: str):
        """
        Initialize Azure collector.

        Args:
            credentials: Azure credentials (tenant_id, client_id, client_secret)
            subscription_id: Azure subscription ID
        """
        self.subscription_id = subscription_id
        self.credential = ClientSecretCredential(
            tenant_id=credentials['tenant_id'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret']
        )

    async def collect_compute(self) -> List[CloudArtifact]:
        """Collect Azure VM artifacts."""
        # Implementation similar to AWS but using Azure SDK
        pass

    async def collect_storage(self) -> List[CloudArtifact]:
        """Collect Azure Blob Storage artifacts."""
        pass

    async def collect_network(self) -> List[CloudArtifact]:
        """Collect Azure VNet artifacts."""
        pass

    async def collect_identity(self) -> List[CloudArtifact]:
        """Collect Azure AD artifacts."""
        pass

    async def collect_logs(self, hours: int = 24) -> List[CloudArtifact]:
        """Collect Azure Monitor logs."""
        pass
```

### 4.3 GCP Collector (Stub)

**File:** `src/acquisition/cloud/gcp_collector.py` (NEW)
```python
"""
GCP Artifact Collector

Collects forensic artifacts from GCP environments.
"""

from typing import List, Dict
from google.cloud import compute_v1
from google.cloud import storage

from .base_collector import BaseCloudCollector, CloudArtifact


class GCPCollector(BaseCloudCollector):
    """GCP artifact collector."""

    def __init__(self, credentials: Dict[str, str], project_id: str):
        """
        Initialize GCP collector.

        Args:
            credentials: GCP service account credentials
            project_id: GCP project ID
        """
        self.project_id = project_id
        # Initialize GCP clients with service account credentials
        pass

    async def collect_compute(self) -> List[CloudArtifact]:
        """Collect Compute Engine artifacts."""
        pass

    async def collect_storage(self) -> List[CloudArtifact]:
        """Collect Cloud Storage artifacts."""
        pass

    async def collect_network(self) -> List[CloudArtifact]:
        """Collect VPC artifacts."""
        pass

    async def collect_identity(self) -> List[CloudArtifact]:
        """Collect IAM artifacts."""
        pass

    async def collect_logs(self, hours: int = 24) -> List[CloudArtifact]:
        """Collect Cloud Logging artifacts."""
        pass
```

---

## 5. Frontend Implementation

### 5.1 Host Selector Update

**File:** `src/web/frontend/src/components/NewAcquisition.js` (UPDATE)

Add cloud provider options to host selection:

```javascript
const hostTypes = [
  { value: 'local', label: 'Local', icon: '💻' },
  { value: 'remote', label: 'Remote', icon: '🌐' },
  { value: 'network', label: 'Network', icon: '📡' },
  {
    value: 'aws',
    label: 'AWS',
    icon: '☁️',
    logo: `${process.env.PUBLIC_URL}/images/logos/aws-logo.svg`
  },
  {
    value: 'azure',
    label: 'Azure',
    icon: '☁️',
    logo: `${process.env.PUBLIC_URL}/images/logos/azure-logo.svg`
  },
  {
    value: 'gcp',
    label: 'GCP',
    icon: '☁️',
    logo: `${process.env.PUBLIC_URL}/images/logos/gcp-logo.svg`
  },
];

// In the render:
<div className="form-group">
  <label>Host Type</label>
  <select
    value={hostType}
    onChange={(e) => setHostType(e.target.value)}
  >
    {hostTypes.map(type => (
      <option key={type.value} value={type.value}>
        {type.icon} {type.label}
      </option>
    ))}
  </select>
</div>

{/* Show cloud credentials form if cloud provider selected */}
{['aws', 'azure', 'gcp'].includes(hostType) && (
  <CloudCredentialsForm
    provider={hostType}
    onCredentialsChange={setCloudCredentials}
  />
)}
```

### 5.2 Cloud Artifact Selection Component

**File:** `src/web/frontend/src/components/CloudArtifactSelector.js` (NEW)

```javascript
import React, { useState } from 'react';

function CloudArtifactSelector({ provider, selectedArtifacts, onChange }) {
  const artifactTypes = [
    {
      type: 'compute',
      label: 'Compute',
      description: {
        aws: 'EC2 Instances & Snapshots',
        azure: 'Virtual Machines & Disks',
        gcp: 'Compute Engine Instances'
      }
    },
    {
      type: 'storage',
      label: 'Storage',
      description: {
        aws: 'S3 Buckets & Objects',
        azure: 'Blob Storage Containers',
        gcp: 'Cloud Storage Buckets'
      }
    },
    {
      type: 'network',
      label: 'Network',
      description: {
        aws: 'VPC, Security Groups, Flow Logs',
        azure: 'VNet, NSGs, Network Watcher',
        gcp: 'VPC, Firewall Rules, VPC Flow Logs'
      }
    },
    {
      type: 'identity',
      label: 'Identity & Access',
      description: {
        aws: 'IAM Users, Roles, Policies',
        azure: 'Azure AD, RBAC',
        gcp: 'IAM Members, Service Accounts'
      }
    },
    {
      type: 'logs',
      label: 'Logs',
      description: {
        aws: 'CloudTrail, CloudWatch Logs',
        azure: 'Activity Log, Monitor Logs',
        gcp: 'Cloud Logging, Audit Logs'
      }
    },
    {
      type: 'database',
      label: 'Database',
      description: {
        aws: 'RDS Instances & Snapshots',
        azure: 'SQL Database, Cosmos DB',
        gcp: 'Cloud SQL, Firestore'
      }
    },
    {
      type: 'container',
      label: 'Container',
      description: {
        aws: 'ECS, EKS Clusters',
        azure: 'AKS, Container Instances',
        gcp: 'GKE, Cloud Run'
      }
    },
    {
      type: 'serverless',
      label: 'Serverless',
      description: {
        aws: 'Lambda Functions',
        azure: 'Azure Functions',
        gcp: 'Cloud Functions'
      }
    },
    {
      type: 'security',
      label: 'Security',
      description: {
        aws: 'GuardDuty, Security Hub',
        azure: 'Defender, Sentinel',
        gcp: 'Security Command Center'
      }
    }
  ];

  const getProviderLogo = (provider) => {
    const logos = {
      aws: `${process.env.PUBLIC_URL}/images/logos/aws-logo.svg`,
      azure: `${process.env.PUBLIC_URL}/images/logos/azure-logo.svg`,
      gcp: `${process.env.PUBLIC_URL}/images/logos/gcp-logo.svg`
    };
    return logos[provider];
  };

  const handleToggle = (artifactType) => {
    const newSelection = selectedArtifacts.includes(artifactType)
      ? selectedArtifacts.filter(a => a !== artifactType)
      : [...selectedArtifacts, artifactType];
    onChange(newSelection);
  };

  return (
    <div className="cloud-artifact-selector">
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <img
          src={getProviderLogo(provider)}
          alt={provider}
          style={{ height: '24px' }}
        />
        Select {provider.toUpperCase()} Artifacts to Collect
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '1rem',
        marginTop: '1rem'
      }}>
        {artifactTypes.map(artifact => (
          <div
            key={artifact.type}
            onClick={() => handleToggle(artifact.type)}
            style={{
              padding: '1rem',
              border: selectedArtifacts.includes(artifact.type)
                ? '2px solid #51cf66'
                : '1px solid rgba(240, 219, 165, 0.3)',
              borderRadius: '8px',
              background: selectedArtifacts.includes(artifact.type)
                ? 'rgba(81, 207, 102, 0.1)'
                : 'rgba(15, 15, 35, 0.6)',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              if (!selectedArtifacts.includes(artifact.type)) {
                e.currentTarget.style.background = 'rgba(240, 219, 165, 0.1)';
              }
            }}
            onMouseOut={(e) => {
              if (!selectedArtifacts.includes(artifact.type)) {
                e.currentTarget.style.background = 'rgba(15, 15, 35, 0.6)';
              }
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <strong style={{ color: '#f0dba5' }}>{artifact.label}</strong>
              <input
                type="checkbox"
                checked={selectedArtifacts.includes(artifact.type)}
                onChange={() => {}}
                style={{ cursor: 'pointer' }}
              />
            </div>
            <p style={{
              fontSize: '0.85rem',
              color: '#a7db6c',
              margin: 0
            }}>
              {artifact.description[provider]}
            </p>

            {/* Provider logo badge */}
            <div style={{ marginTop: '0.5rem' }}>
              <img
                src={getProviderLogo(provider)}
                alt={provider}
                style={{ height: '16px', opacity: 0.6 }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CloudArtifactSelector;
```

---

## 6. Cloud Artifact Collection

### 6.1 Artifact Naming Convention

All artifacts use **cloud-agnostic** terminology:

| Artifact Type | AWS | Azure | GCP |
|--------------|-----|-------|-----|
| **Compute** | EC2 | Virtual Machines | Compute Engine |
| **Storage** | S3 | Blob Storage | Cloud Storage |
| **Network** | VPC | VNet | VPC |
| **Identity** | IAM | Azure AD | IAM |
| **Logs** | CloudTrail | Activity Log | Cloud Logging |
| **Database** | RDS | SQL Database | Cloud SQL |
| **Container** | ECS/EKS | AKS | GKE |
| **Serverless** | Lambda | Functions | Cloud Functions |
| **Security** | GuardDuty | Defender | Security Command Center |

### 6.2 Collection Workflow

```
┌──────────────────────────────────────────────────────────────┐
│              CLOUD ARTIFACT COLLECTION FLOW                   │
└──────────────────────────────────────────────────────────────┘

1. User Selects Cloud Provider
   ├─ AWS
   ├─ Azure
   └─ GCP

2. User Provides Credentials
   ├─ AWS: Access Key ID, Secret Access Key
   ├─ Azure: Tenant ID, Client ID, Client Secret, Subscription ID
   └─ GCP: Service Account JSON, Project ID

3. User Selects Artifact Types
   ├─ Compute (with disk snapshots)
   ├─ Storage (bucket inventory)
   ├─ Network (config export)
   ├─ Identity (user/role dump)
   ├─ Logs (time-based export)
   └─ ... (other types)

4. Backend Initiates Collection
   ├─ Authenticate with cloud provider API
   ├─ Enumerate resources in selected regions
   ├─ Create forensic snapshots (for Compute)
   ├─ Export configurations (Network, Identity)
   └─ Download logs (with timestamps)

5. Store Artifacts
   ├─ Save to /evidence/{provider}/{artifact_type}/
   ├─ Record metadata in database
   └─ Generate collection report

6. Analyze Artifacts
   └─ Process with Elrond analysis engine
```

---

## 7. API Integration

### 7.1 Cloud Credentials Management

**Endpoint:** `POST /api/cloud/credentials`

```python
@router.post("/api/cloud/credentials")
async def save_cloud_credentials(
    credentials: CloudCredentials,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Save cloud provider credentials (encrypted).
    """
    # Encrypt credentials before storage
    encrypted_creds = encrypt_credentials(credentials.credentials)

    cloud_cred = CloudCredential(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        provider=credentials.provider,
        credentials=encrypted_creds,
        region=credentials.region,
        account_id=credentials.account_id,
        subscription_id=credentials.subscription_id,
        project_id=credentials.project_id,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(cloud_cred)
    db.commit()

    return {"message": "Credentials saved successfully", "credential_id": cloud_cred.id}
```

### 7.2 Cloud Artifact Collection Job

**Endpoint:** `POST /api/jobs/cloud`

```python
@router.post("/api/jobs/cloud")
async def create_cloud_collection_job(
    request: CloudCollectionRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db_dependency),
):
    """
    Create cloud artifact collection job.
    """
    # Get cloud credentials
    cloud_creds = db.query(CloudCredential).filter(
        CloudCredential.id == request.credential_id,
        CloudCredential.user_id == current_user.id
    ).first()

    if not cloud_creds:
        raise HTTPException(status_code=404, detail="Cloud credentials not found")

    # Create job
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        user_id=current_user.id,
        case_number=request.case_number,
        source_paths=[],  # Cloud sources don't have paths
        options={
            'cloud_provider': cloud_creds.provider,
            'artifacts': request.artifacts,
            'regions': request.regions,
            'include_deleted': request.include_deleted,
            'snapshot_disks': request.snapshot_disks,
        },
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
    )

    db.add(job)
    db.commit()

    # Start cloud collection task
    cloud_collection_task.delay(job_id, cloud_creds.id)

    return job
```

---

## 8. Security Considerations

### 8.1 Credential Encryption

**All cloud credentials MUST be encrypted at rest:**

```python
from cryptography.fernet import Fernet
from ..config import settings

def encrypt_credentials(credentials: Dict[str, str]) -> str:
    """Encrypt cloud credentials."""
    key = settings.encryption_key.encode()
    f = Fernet(key)
    return f.encrypt(json.dumps(credentials).encode()).decode()

def decrypt_credentials(encrypted: str) -> Dict[str, str]:
    """Decrypt cloud credentials."""
    key = settings.encryption_key.encode()
    f = Fernet(key)
    return json.loads(f.decrypt(encrypted.encode()).decode())
```

### 8.2 Least Privilege Access

**Required IAM permissions:**

**AWS:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:CreateSnapshot",
        "ec2:DescribeVolumes",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "cloudtrail:LookupEvents",
        "iam:ListUsers",
        "iam:GetUser"
      ],
      "Resource": "*"
    }
  ]
}
```

**Azure:**
```
Reader role on subscription
```

**GCP:**
```
roles/viewer on project
```

### 8.3 Audit Logging

Log all cloud API calls:
```python
audit_log = AuditLog(
    id=str(uuid.uuid4()),
    user_id=current_user.id,
    action="cloud_artifact_collection",
    resource_type="cloud_credentials",
    resource_id=cloud_creds.id,
    details={
        'provider': cloud_creds.provider,
        'artifacts_collected': len(artifacts),
        'regions': regions,
    },
    timestamp=datetime.utcnow(),
)
db.add(audit_log)
```

---

## 9. Implementation Checklist

### Phase 1: Database & Models
- [ ] Create cloud provider models (`cloud.py`)
- [ ] Create database migration for cloud tables
- [ ] Add cloud credentials encryption utilities
- [ ] Test database schema

### Phase 2: Backend Collection Engines
- [ ] Implement AWS collector (`aws_collector.py`)
- [ ] Implement Azure collector (`azure_collector.py`)
- [ ] Implement GCP collector (`gcp_collector.py`)
- [ ] Create base collector interface
- [ ] Add unit tests for collectors

### Phase 3: API Endpoints
- [ ] Create cloud credentials management endpoints
- [ ] Create cloud collection job endpoints
- [ ] Add Celery task for cloud collection
- [ ] Test API integration

### Phase 4: Frontend Components
- [ ] Update host selector with cloud options
- [ ] Create cloud credentials form
- [ ] Create cloud artifact selector component
- [ ] Add cloud provider logos
- [ ] Test UI/UX flow

### Phase 5: Integration Testing
- [ ] Test AWS artifact collection end-to-end
- [ ] Test Azure artifact collection end-to-end
- [ ] Test GCP artifact collection end-to-end
- [ ] Verify artifact storage and metadata
- [ ] Security audit

### Phase 6: Documentation
- [ ] Update user guide with cloud forensics
- [ ] Create cloud setup tutorials
- [ ] Document IAM permissions required
- [ ] Add troubleshooting guide

---

This guide provides a complete implementation roadmap for cloud forensics capabilities in the Rivendell DFIR Suite, with support for AWS, Azure, and GCP using cloud-agnostic artifact terminology.
