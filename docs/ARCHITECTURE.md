# Rivendell DFIR Suite - System Architecture

## Table of Contents
- [1. Overview](#1-overview)
- [2. System Architecture](#2-system-architecture)
- [3. Component Diagrams](#3-component-diagrams)
- [4. Data Flow](#4-data-flow)
- [5. Authentication Flow](#5-authentication-flow)
- [6. Database Schema](#6-database-schema)
- [7. API Architecture](#7-api-architecture)
- [8. Deployment Architecture](#8-deployment-architecture)

---

## 1. Overview

The Rivendell DFIR (Digital Forensics and Incident Response) Acceleration Suite is a comprehensive platform for automating forensic analysis workflows. It consists of three main components:

- **Gandalf**: Evidence acquisition module
- **Elrond**: Forensic analysis and artifact processing engine
- **Mordor**: Security dataset exploration and threat simulation
- **Web Interface**: Unified control panel for all operations

### Technology Stack

```
Frontend:
├── React 18.x
├── React Router 6.x
├── Axios (HTTP client)
└── CSS3 (Custom styling)

Backend:
├── FastAPI (Python 3.11+)
├── SQLAlchemy 2.0 (ORM)
├── PostgreSQL 15 (Database)
├── Redis 7 (Caching & Message Broker)
├── Celery (Task Queue)
└── Alembic (Migrations)

Infrastructure:
├── Docker & Docker Compose
├── Nginx (Reverse Proxy)
└── uvicorn (ASGI Server)

Forensic Tools:
├── Sleuthkit
├── Volatility3
├── Plaso
├── YARA
└── Custom Python analyzers
```

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Browser    │  │  Mobile Web  │  │  API Client  │              │
│  │  (React UI)  │  │  (React UI)  │  │   (REST)     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│         └──────────────────┼──────────────────┘                       │
└─────────────────────────────┼─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Nginx Reverse Proxy                       │  │
│  │  • SSL/TLS Termination                                        │  │
│  │  • Load Balancing                                             │  │
│  │  • Static File Serving                                        │  │
│  │  • Request Routing                                            │  │
│  └────────────┬──────────────────────────┬──────────────────────┘  │
└───────────────┼──────────────────────────┼──────────────────────────┘
                │                          │
      ┌─────────▼─────────┐      ┌─────────▼─────────┐
      │  Frontend (React) │      │  Backend (FastAPI) │
      │  Port: 3000       │      │  Port: 8000        │
      └───────────────────┘      └─────────┬──────────┘
                                           │
┌──────────────────────────────────────────┼──────────────────────────┐
│                     APPLICATION LAYER    │                           │
│                                          ▼                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │  │
│  │  │    Auth    │  │    Jobs    │  │   Export   │             │  │
│  │  │   Routes   │  │   Routes   │  │   Routes   │             │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │  │
│  │        │               │               │                      │  │
│  │  ┌─────▼───────────────▼───────────────▼──────┐             │  │
│  │  │         Business Logic Layer               │             │  │
│  │  │  • Authentication & Authorization          │             │  │
│  │  │  • Job Management & Scheduling             │             │  │
│  │  │  • Data Export/Import                      │             │  │
│  │  │  • File System Operations                  │             │  │
│  │  └─────────────────┬──────────────────────────┘             │  │
│  └────────────────────┼───────────────────────────────────────┘  │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       TASK PROCESSING LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      Celery Workers                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │
│  │  │  Analysis  │  │ Acquisition│  │  Export    │             │   │
│  │  │   Worker   │  │   Worker   │  │   Worker   │             │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │   │
│  │        │               │               │                      │   │
│  │  ┌─────▼───────────────▼───────────────▼──────┐             │   │
│  │  │           Forensic Analysis Engine         │             │   │
│  │  │  • Elrond (Analysis & Artifact Processing) │             │   │
│  │  │  • Gandalf (Evidence Acquisition)          │             │   │
│  │  │  • Timeline Generation (Plaso)             │             │   │
│  │  │  • Memory Analysis (Volatility3)           │             │   │
│  │  └────────────────────────────────────────────┘             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostgreSQL  │  │    Redis     │  │  File System │              │
│  │   Database   │  │    Cache     │  │   Storage    │              │
│  │              │  │              │  │              │              │
│  │ • Users      │  │ • Sessions   │  │ • Evidence   │              │
│  │ • Jobs       │  │ • Task Queue │  │ • Artifacts  │              │
│  │ • Settings   │  │ • Results    │  │ • Reports    │              │
│  │ • Accounts   │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Diagrams

### 3.1 Authentication & Authorization

```
┌──────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION FLOW                         │
└──────────────────────────────────────────────────────────────┘

    User                Frontend            Backend              Database
     │                     │                   │                    │
     │   1. Login Request  │                   │                    │
     ├────────────────────>│                   │                    │
     │                     │  2. POST /api/auth/login              │
     │                     ├──────────────────>│                    │
     │                     │                   │ 3. Query User      │
     │                     │                   ├───────────────────>│
     │                     │                   │ 4. User Data       │
     │                     │                   │<───────────────────┤
     │                     │                   │                    │
     │                     │                   │ 5. Verify Password │
     │                     │                   │ (bcrypt)           │
     │                     │                   │                    │
     │                     │                   │ 6. Generate JWT    │
     │                     │                   │ Token              │
     │                     │                   │                    │
     │                     │                   │ 7. Create Session  │
     │                     │                   ├───────────────────>│
     │                     │                   │                    │
     │                     │ 8. Access Token   │                    │
     │                     │    + Set Cookie   │                    │
     │                     │<──────────────────┤                    │
     │  9. Redirect to     │                   │                    │
     │     Dashboard       │                   │                    │
     │<────────────────────┤                   │                    │
     │                     │                   │                    │
     │                     │                   │                    │
     │ 10. API Request     │                   │                    │
     │     with JWT        │                   │                    │
     ├────────────────────>│                   │                    │
     │                     │ 11. Include       │                    │
     │                     │     Bearer Token  │                    │
     │                     ├──────────────────>│                    │
     │                     │                   │ 12. Verify Token   │
     │                     │                   │                    │
     │                     │                   │ 13. Get User       │
     │                     │                   ├───────────────────>│
     │                     │                   │ 14. User Data      │
     │                     │                   │<───────────────────┤
     │                     │                   │                    │
     │                     │ 15. Protected     │                    │
     │                     │     Resource      │                    │
     │                     │<──────────────────┤                    │
     │ 16. Response        │                   │                    │
     │<────────────────────┤                   │                    │
```

### 3.2 Job Lifecycle Management

```
┌──────────────────────────────────────────────────────────────┐
│                      JOB STATE MACHINE                        │
└──────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   QUEUED    │◄──────┐
                    │             │       │
                    │ (Saved for  │       │ Save for Later
                    │   Later)    │       │
                    └──────┬──────┘       │
                           │              │
                      Start Job           │
                           │              │
                           ▼              │
                    ┌─────────────┐       │
             ┌─────>│   PENDING   │───────┘
             │      │             │
             │      │ (Ready to   │
             │      │   Start)    │
             │      └──────┬──────┘
             │             │
             │        Celery Task
             │        Dispatched
             │             │
     Restart │             ▼
             │      ┌─────────────┐
             │      │   RUNNING   │
             │      │             │
             │      │ (Executing) │◄────┐
             │      └──────┬──────┘     │
             │             │            │
             │        ┌────┴────┐       │
             │        │         │       │
             │   Success    Failure  Cancel
             │        │         │       │
             │        ▼         ▼       │
             │  ┌──────────┐ ┌────────┐│
             ├──┤COMPLETED│ │ FAILED ││
             │  │          │ │        ││
             │  └────┬─────┘ └───┬────┘│
             │       │           │     │
             │       │    Restart│     │
             │       │           └─────┘
             │       │Archive
             │       │
             │       ▼
             │  ┌──────────┐
             │  │ ARCHIVED │
             │  │          │
             │  └────┬─────┘
             │       │
             │   Restore
             │       │
             └───────┘


State Transitions:
─────────────────
QUEUED     → PENDING    (User starts job)
PENDING    → RUNNING    (Celery picks up task)
RUNNING    → COMPLETED  (Success)
RUNNING    → FAILED     (Error)
RUNNING    → CANCELLED  (User cancels)
COMPLETED  → ARCHIVED   (User archives)
FAILED     → ARCHIVED   (User archives)
FAILED     → PENDING    (User restarts)
CANCELLED  → PENDING    (User restarts)
ARCHIVED   → COMPLETED  (User restores)
ARCHIVED   → FAILED     (User restores)
```

### 3.3 Export/Import Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    EXPORT/IMPORT WORKFLOW                     │
└──────────────────────────────────────────────────────────────┘

EXPORT FLOW:
────────────
    User              Frontend           Backend          Database
     │                   │                  │                 │
     │ 1. Request Export │                  │                 │
     ├──────────────────>│                  │                 │
     │                   │ 2. POST /api/export/export        │
     │                   │  (Optional: job_ids)              │
     │                   ├─────────────────>│                 │
     │                   │                  │ 3. Query User   │
     │                   │                  │    Settings     │
     │                   │                  ├────────────────>│
     │                   │                  │ 4. Settings     │
     │                   │                  │<────────────────┤
     │                   │                  │ 5. Query        │
     │                   │                  │    Accounts     │
     │                   │                  ├────────────────>│
     │                   │                  │ 6. Accounts     │
     │                   │                  │<────────────────┤
     │                   │                  │ 7. Query Jobs   │
     │                   │                  ├────────────────>│
     │                   │                  │ 8. Jobs Data    │
     │                   │                  │<────────────────┤
     │                   │                  │                 │
     │                   │                  │ 9. Build Export │
     │                   │                  │    JSON Package │
     │                   │                  │                 │
     │                   │ 10. Export File  │                 │
     │                   │     (JSON)       │                 │
     │                   │<─────────────────┤                 │
     │ 11. Download File │                  │                 │
     │<──────────────────┤                  │                 │


IMPORT FLOW:
────────────
    User              Frontend           Backend          Database
     │                   │                  │                 │
     │ 1. Upload File    │                  │                 │
     ├──────────────────>│                  │                 │
     │                   │ 2. POST /api/export/import        │
     │                   │    + file upload                  │
     │                   │    + options                      │
     │                   ├─────────────────>│                 │
     │                   │                  │ 3. Parse JSON   │
     │                   │                  │    Validate     │
     │                   │                  │                 │
     │                   │                  │ 4. Import       │
     │                   │                  │    Settings     │
     │                   │                  ├────────────────>│
     │                   │                  │                 │
     │                   │                  │ 5. Import       │
     │                   │                  │    Accounts     │
     │                   │                  ├────────────────>│
     │                   │                  │                 │
     │                   │                  │ 6. Import Jobs  │
     │                   │                  │   (Merge/       │
     │                   │                  │    Overwrite)   │
     │                   │                  ├────────────────>│
     │                   │                  │                 │
     │                   │ 7. Import        │                 │
     │                   │    Summary       │                 │
     │                   │<─────────────────┤                 │
     │ 8. Success        │                  │                 │
     │    Notification   │                  │                 │
     │<──────────────────┤                  │                 │
```

---

## 4. Data Flow

### 4.1 Forensic Analysis Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│               FORENSIC ANALYSIS DATA FLOW                            │
└─────────────────────────────────────────────────────────────────────┘

 User Input                     Processing Pipeline              Output
┌──────────┐                                                  ┌──────────┐
│          │                                                  │          │
│  Disk    │                ┌──────────────┐                 │ Timeline │
│  Image   ├───────────────>│   Elrond     │────────────────>│  (CSV)   │
│  (.E01)  │                │   Engine     │                 │          │
│          │                └──────┬───────┘                 └──────────┘
└──────────┘                       │
                                   │                         ┌──────────┐
                                   │                         │          │
                                   ├────────────────────────>│ Registry │
                                   │                         │  Report  │
                                   │                         │          │
                                   │                         └──────────┘
                                   │
                                   │                         ┌──────────┐
                                   │                         │          │
                                   ├────────────────────────>│  Event   │
                                   │                         │   Logs   │
                                   │                         │          │
                                   │                         └──────────┘
                                   │
                                   │                         ┌──────────┐
                                   │                         │          │
                                   ├────────────────────────>│   IOCs   │
                                   │                         │ (JSON)   │
                                   │                         │          │
                                   │                         └──────────┘
                                   │
                                   │                         ┌──────────┐
                                   │                         │          │
                                   └────────────────────────>│ Splunk/  │
                                                             │ Elastic  │
                                                             │  Output  │
                                                             └──────────┘

PROCESSING STAGES:
──────────────────

1. IMAGE MOUNTING
   ├─ Detect image format (.E01, .DD, .IMG, etc.)
   ├─ Mount using appropriate tool (ewfmount, qemu-nbd)
   └─ Enumerate partitions

2. FILESYSTEM ANALYSIS
   ├─ Parse MFT/USN Journal (NTFS)
   ├─ Extract file metadata
   ├─ Recover deleted files
   └─ Identify file types

3. ARTIFACT COLLECTION
   ├─ Windows Registry
   ├─ Event Logs (EVTX)
   ├─ Prefetch files
   ├─ Browser history
   ├─ User profiles
   └─ System files

4. TIMELINE GENERATION
   ├─ Plaso (log2timeline)
   ├─ MFT timeline
   ├─ USN Journal
   └─ Merge all timestamps

5. ANALYSIS & CORRELATION
   ├─ YARA scanning
   ├─ IOC extraction
   ├─ Pattern matching
   └─ Threat hunting

6. REPORTING
   ├─ Generate HTML reports
   ├─ Export to CSV/JSON
   ├─ Send to SIEM
   └─ Create summary
```

---

## 5. Authentication Flow

### 5.1 User Roles & Permissions

```
┌────────────────────────────────────────────────────────────┐
│                    ROLE-BASED ACCESS CONTROL                │
└────────────────────────────────────────────────────────────┘

┌─────────────┐
│    ADMIN    │
│  (Highest)  │
└──────┬──────┘
       │
       │  ✓ All USER permissions
       │  ✓ Manage all users
       │  ✓ View all jobs
       │  ✓ System configuration
       │  ✓ Export all data
       │  ✓ Import data globally
       │
       ▼
┌─────────────┐
│    USER     │
│  (Standard) │
└──────┬──────┘
       │
       │  ✓ Create jobs
       │  ✓ View own jobs
       │  ✓ Start/Stop/Restart jobs
       │  ✓ Archive jobs
       │  ✓ Export own data
       │  ✓ Import data (own account)
       │  ✓ Manage accounts/settings
       │
       ▼
┌─────────────┐
│    GUEST    │
│  (Lowest)   │
└──────┬──────┘
       │
       │  ✓ Browse interface (read-only)
       │  ✓ View public documentation
       │  ✗ Cannot create jobs
       │  ✗ Cannot save data
       │  ✗ Cannot export/import
       │  ⏰ Auto-expire (1 hour)
       │
       ▼
┌─────────────┐
│ UNAUTHENTICATED│
└─────────────┘
```

### 5.2 JWT Token Structure

```
┌──────────────────────────────────────────────────────────┐
│                     JWT TOKEN ANATOMY                     │
└──────────────────────────────────────────────────────────┘

HEADER:
{
  "alg": "HS256",           // Algorithm: HMAC SHA-256
  "typ": "JWT"              // Type: JSON Web Token
}

PAYLOAD:
{
  "sub": "user-uuid-here",  // Subject: User ID
  "role": "user",           // User role
  "exp": 1735689600,        // Expiration timestamp
  "jti": "token-uuid-here"  // JWT ID (for revocation)
}

SIGNATURE:
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret_key
)

FINAL TOKEN:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJ1c2VyLXV1aWQiLCJyb2xlIjoidXNlciIsImV4cCI6MTczNTY4OTYwMCwianRpIjoidG9rZW4tdXVpZCJ9.
signature_hash_here
```

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                       DATABASE SCHEMA (ERD)                             │
└────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│      USERS       │
├──────────────────┤
│ PK id (UUID)     │
│    email         │◄──────────────────────┐
│    username      │                       │
│    hashed_pwd    │                       │
│    full_name     │                       │
│    role          │                       │
│    is_active     │                       │
│    created_at    │                       │
│    last_login    │                       │
└────────┬─────────┘                       │
         │                                 │
         │ 1                               │
         │                                 │
         │                                 │
         │ N                               │
         ▼                                 │
┌──────────────────┐                       │
│  USER_SETTINGS   │                       │
├──────────────────┤                       │
│ PK id (UUID)     │                       │
│ FK user_id       │───────────────────────┘
│    theme         │
│    notifications │
│    auto_refresh  │
│    default_opts  │ (JSON)
│    custom_set    │ (JSON)
└──────────────────┘

         │
         │ 1
         │
         │
         │ N
         ▼
┌──────────────────┐
│     ACCOUNTS     │
├──────────────────┤
│ PK id (UUID)     │
│ FK user_id       │───────────────────────┐
│    account_type  │                       │
│    name          │                       │
│    credentials   │ (JSON, encrypted)     │
│    endpoint_url  │                       │
│    is_active     │                       │
└──────────────────┘                       │
                                           │
         │                                 │
         │ 1                               │
         │                                 │
         │                                 │
         │ N                               │
         ▼                                 │
┌──────────────────┐                       │
│       JOBS       │                       │
├──────────────────┤                       │
│ PK id (UUID)     │                       │
│ FK user_id       │───────────────────────┘
│    case_number   │
│    source_paths  │ (JSON array)
│    dest_path     │
│    options       │ (JSON object)
│    status        │ (ENUM)
│    progress      │ (INT 0-100)
│    log           │ (JSON array)
│    result        │ (JSON)
│    error         │ (TEXT)
│    task_id       │ (Celery)
│    created_at    │
│    started_at    │
│    completed_at  │
│    archived_at   │
└──────────────────┘

         │
         │ 1
         │
         │
         │ N
         ▼
┌──────────────────┐
│     SESSIONS     │
├──────────────────┤
│ PK id (UUID)     │
│ FK user_id       │───────────────────────┐
│    token         │ (JWT)                 │
│    ip_address    │                       │
│    user_agent    │                       │
│    is_active     │                       │
│    created_at    │                       │
│    expires_at    │                       │
│    last_activity │                       │
└──────────────────┘                       │
                                           │
                                           │
         ▼                                 │
┌──────────────────┐                       │
│   AUDIT_LOGS     │                       │
├──────────────────┤                       │
│ PK id (UUID)     │                       │
│ FK user_id       │───────────────────────┘
│    action        │
│    resource_type │
│    resource_id   │
│    details       │ (JSON)
│    ip_address    │
│    timestamp     │
└──────────────────┘


INDEXES:
────────
users:          email, username, role
accounts:       user_id, account_type
jobs:           user_id, status, case_number, created_at
sessions:       token, user_id, expires_at
audit_logs:     user_id, timestamp, action
```

---

## 7. API Architecture

### 7.1 RESTful API Structure

```
┌────────────────────────────────────────────────────────────┐
│                    API ENDPOINT TREE                        │
└────────────────────────────────────────────────────────────┘

/api
│
├── /auth                              [Authentication]
│   ├── POST   /register              Register new user
│   ├── POST   /login                 Login with credentials
│   ├── POST   /logout                Logout current session
│   ├── POST   /guest                 Login as guest
│   ├── GET    /me                    Get current user info
│   ├── POST   /forgot-password       Request password reset
│   └── POST   /reset-password        Reset password with token
│
├── /jobs                              [Job Management]
│   ├── GET    /                      List all jobs
│   ├── POST   /                      Create new job
│   ├── GET    /{job_id}              Get job details
│   ├── PATCH  /{job_id}              Update job
│   ├── DELETE /{job_id}              Delete job
│   ├── POST   /{job_id}/start        Start job
│   ├── POST   /{job_id}/stop         Stop running job
│   ├── POST   /{job_id}/restart      Restart job
│   ├── POST   /{job_id}/cancel       Cancel job
│   ├── POST   /{job_id}/archive      Archive job
│   ├── POST   /{job_id}/unarchive    Restore archived job
│   ├── GET    /archived              List archived jobs
│   ├── POST   /bulk/archive          Archive multiple jobs
│   └── POST   /bulk/delete           Delete multiple jobs
│
├── /export                            [Export/Import]
│   ├── POST   /export                Export data to JSON
│   └── POST   /import                Import data from JSON
│
├── /fs                                [File System]
│   └── GET    /browse                Browse filesystem
│
├── /settings                          [User Settings]
│   ├── GET    /                      Get user settings
│   └── PATCH  /                      Update user settings
│
├── /accounts                          [External Accounts]
│   ├── GET    /                      List accounts
│   ├── POST   /                      Create account
│   ├── GET    /{account_id}          Get account details
│   ├── PATCH  /{account_id}          Update account
│   └── DELETE /{account_id}          Delete account
│
└── /health                            [Health Check]
    └── GET    /                      Service health status


AUTHENTICATION:
───────────────
• All endpoints except /auth/* require authentication
• Use Bearer token in Authorization header
• Or session cookie (httpOnly)

RESPONSE FORMATS:
─────────────────
SUCCESS:
{
  "data": { ... },          // Response data
  "message": "Success"      // Optional message
}

ERROR:
{
  "detail": "Error message",
  "error_code": "ERR_001"  // Optional error code
}

PAGINATION:
───────────
GET /api/jobs?limit=50&offset=0

{
  "jobs": [ ... ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

## 8. Deployment Architecture

### 8.1 Docker Compose Stack

```
┌────────────────────────────────────────────────────────────────┐
│                    DOCKER DEPLOYMENT STACK                      │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                           HOST SYSTEM                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Docker Network Bridge                   │ │
│  │                   (rivendell-network)                      │ │
│  │                                                             │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │ │
│  │  │   Nginx    │  │  Frontend  │  │  Backend   │          │ │
│  │  │            │  │            │  │            │          │ │
│  │  │ Port: 80   │  │ Port: 3000 │  │ Port: 8000 │          │ │
│  │  │ Port: 443  │  │  (React)   │  │  (FastAPI) │          │ │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘          │ │
│  │        │               │               │                  │ │
│  │        └───────────────┴───────────────┘                  │ │
│  │                        │                                   │ │
│  │  ┌─────────────────────┼────────────────────────┐         │ │
│  │  │                     │                        │         │ │
│  │  │  ┌─────────┐  ┌─────▼──────┐  ┌──────────┐  │         │ │
│  │  │  │ Celery  │  │   Redis    │  │PostgreSQL│  │         │ │
│  │  │  │ Worker  │  │            │  │          │  │         │ │
│  │  │  │         │  │ Port: 6379 │  │Port: 5432│  │         │ │
│  │  │  └────┬────┘  └────────────┘  └─────┬────┘  │         │ │
│  │  │       │                              │       │         │ │
│  │  └───────┼──────────────────────────────┼───────┘         │ │
│  │          │                              │                 │ │
│  │  ┌───────▼──────────────────────────────▼───────┐         │ │
│  │  │              Flower Monitor                   │         │ │
│  │  │           (Celery Dashboard)                  │         │ │
│  │  │              Port: 5689                       │         │ │
│  │  └───────────────────────────────────────────────┘         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     VOLUME MOUNTS                            │ │
│  │                                                              │ │
│  │  rivendell-evidence ──> /evidence                           │ │
│  │  rivendell-output   ──> /output                             │ │
│  │  rivendell-data     ──> /data                               │ │
│  │  rivendell-tmp      ──> /tmp/elrond                         │ │
│  │  rivendell-postgres ──> /var/lib/postgresql/data            │ │
│  │  rivendell-redis    ──> /data                               │ │
│  │                                                              │ │
│  │  Host Mounts:                                                │ │
│  │  /Volumes           ──> /Volumes (external drives)          │ │
│  │  /tmp               ──> /host/tmp (evidence staging)        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘


CONTAINER SPECIFICATIONS:
──────────────────────────

rivendell-app:
  Image: rivendell-web:dev
  Privileged: true
  Capabilities: SYS_ADMIN, SYS_RESOURCE
  Devices: /dev/fuse
  Ports: 5688:8000

rivendell-frontend:
  Image: rivendell-frontend:dev
  Ports: 5687:3000

rivendell-celery:
  Image: rivendell-web:dev
  Privileged: true
  Command: celery worker

rivendell-flower:
  Image: rivendell-web:dev
  Ports: 5689:5555

rivendell-postgres:
  Image: postgres:15-alpine
  Ports: 5432:5432
  Environment:
    POSTGRES_DB: rivendell
    POSTGRES_USER: rivendell
    POSTGRES_PASSWORD: rivendell

rivendell-redis:
  Image: redis:7-alpine
  Ports: 6379:6379
  Command: redis-server --appendonly yes

rivendell-nginx:
  Image: nginx:alpine
  Ports: 80:80, 443:443
  Profiles: production
```

### 8.2 Scaling Strategy

```
┌────────────────────────────────────────────────────────────┐
│                   HORIZONTAL SCALING                        │
└────────────────────────────────────────────────────────────┘

CURRENT (Single Node):
──────────────────────
┌──────────────────────────────┐
│       Single Host            │
│  ┌────────┐  ┌────────┐     │
│  │Backend │  │Worker  │     │
│  │   x1   │  │   x1   │     │
│  └────────┘  └────────┘     │
│  ┌────────┐  ┌────────┐     │
│  │  DB    │  │ Redis  │     │
│  └────────┘  └────────┘     │
└──────────────────────────────┘

SCALED (Multi-Node):
────────────────────
┌────────────────────────────────────────────────────────────┐
│                    Load Balancer                            │
│                     (Nginx/HAProxy)                         │
└─────────┬────────────────────┬────────────────────┬─────────┘
          │                    │                    │
    ┌─────▼──────┐      ┌─────▼──────┐      ┌─────▼──────┐
    │  Backend 1 │      │  Backend 2 │      │  Backend 3 │
    │  Worker 1  │      │  Worker 2  │      │  Worker 3  │
    └─────┬──────┘      └─────┬──────┘      └─────┬──────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Shared Services   │
                    │  ┌──────┐ ┌──────┐ │
                    │  │  DB  │ │Redis │ │
                    │  │(HA)  │ │(HA)  │ │
                    │  └──────┘ └──────┘ │
                    └─────────────────────┘


PERFORMANCE METRICS:
────────────────────
Target SLAs:
• API Response Time: < 200ms (95th percentile)
• Job Start Latency: < 5s
• Concurrent Jobs: 10+ simultaneous analyses
• User Sessions: 100+ concurrent users
• Database Queries: < 100ms average
```

---

## 9. Security Architecture

### 9.1 Security Layers

```
┌────────────────────────────────────────────────────────────┐
│                    SECURITY DEFENSE LAYERS                  │
└────────────────────────────────────────────────────────────┘

Layer 7: Application Security
┌──────────────────────────────────────────────────────────┐
│ • Input Validation & Sanitization                        │
│ • Output Encoding                                        │
│ • CSRF Protection                                        │
│ • XSS Prevention                                         │
│ • SQL Injection Prevention (ORM)                         │
│ • Rate Limiting                                          │
│ • Session Management                                     │
└──────────────────────────────────────────────────────────┘

Layer 6: Authentication & Authorization
┌──────────────────────────────────────────────────────────┐
│ • JWT Token Validation                                   │
│ • Role-Based Access Control (RBAC)                       │
│ • Password Hashing (bcrypt)                              │
│ • Session Timeout                                        │
│ • Multi-Factor Authentication (Future)                   │
└──────────────────────────────────────────────────────────┘

Layer 5: API Security
┌──────────────────────────────────────────────────────────┐
│ • HTTPS/TLS Encryption                                   │
│ • CORS Configuration                                     │
│ • API Key Management                                     │
│ • Request Throttling                                     │
└──────────────────────────────────────────────────────────┘

Layer 4: Network Security
┌──────────────────────────────────────────────────────────┐
│ • Docker Network Isolation                               │
│ • Firewall Rules                                         │
│ • Port Restrictions                                      │
│ • Reverse Proxy (Nginx)                                  │
└──────────────────────────────────────────────────────────┘

Layer 3: Data Security
┌──────────────────────────────────────────────────────────┐
│ • Database Encryption at Rest                            │
│ • Encrypted Credentials (Accounts)                       │
│ • Secure File Permissions                                │
│ • Audit Logging                                          │
└──────────────────────────────────────────────────────────┘

Layer 2: Infrastructure Security
┌──────────────────────────────────────────────────────────┐
│ • Container Security Scanning                            │
│ • Minimal Base Images                                    │
│ • Non-Root User Execution                                │
│ • Resource Limits                                        │
└──────────────────────────────────────────────────────────┘

Layer 1: Physical Security
┌──────────────────────────────────────────────────────────┐
│ • Host System Access Control                             │
│ • Evidence Chain of Custody                              │
│ • Secure Storage                                         │
└──────────────────────────────────────────────────────────┘
```

---

## 10. Monitoring & Observability

```
┌────────────────────────────────────────────────────────────┐
│                MONITORING & LOGGING STACK                   │
└────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Application Logs                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  FastAPI   │  │   Celery   │  │  Frontend  │           │
│  │   Logs     │  │   Logs     │  │   Errors   │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        └────────────────┼────────────────┘                  │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Log Aggregation                           │
│              (ELK Stack / Grafana Loki)                     │
│  • Centralized logging                                      │
│  • Full-text search                                         │
│  • Real-time alerting                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Metrics Collection                        │
│              (Prometheus / Grafana)                         │
│  • Request latency                                          │
│  • Error rates                                              │
│  • Job completion time                                      │
│  • Resource utilization                                     │
│  • Database performance                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Dashboards                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   System     │  │     Job      │  │    User      │     │
│  │   Health     │  │  Analytics   │  │  Activity    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘


KEY METRICS:
────────────
• Request Rate (requests/sec)
• Error Rate (errors/min)
• Response Time (P50, P95, P99)
• Job Queue Length
• Job Success/Failure Rate
• Database Connection Pool
• Memory Usage
• CPU Usage
• Disk I/O
```

---

This architecture documentation provides a comprehensive technical overview of the Rivendell DFIR Suite, including system architecture, component interactions, data flows, security layers, and deployment strategies.
