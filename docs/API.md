# Rivendell Web API Reference

**Version:** 2.1.0
**Base URL:** `http://localhost:8000/api`
**Protocol:** REST
**Authentication:** JWT Bearer Token or HTTP-only Cookie

---

## Table of Contents

1. [Authentication](#authentication)
2. [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
3. [Admin Endpoints](#admin-endpoints)
4. [Job Management](#job-management)
5. [File System](#file-system)
6. [Health Check](#health-check)
7. [Request/Response Formats](#requestresponse-formats)
8. [Error Handling](#error-handling)
9. [Code Examples](#code-examples)

---

## Authentication

All authenticated endpoints require either:
- **Bearer Token** in `Authorization` header: `Authorization: Bearer <token>`
- **HTTP-only cookie** set during login

### Register New User

**Endpoint:** `POST /auth/register`

**Description:** Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "full_name": "John Doe"  // Optional
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "last_login": null
  }
}
```

**Validation:**
- Email: Valid email format
- Username: Min 3 chars, alphanumeric + underscores only
- Password: Min 8 characters
- Full name: Optional, max 255 characters

**Errors:**
- `400 Bad Request`: Validation error or user already exists
- `500 Internal Server Error`: Server error

---

### Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive access token. Sets HTTP-only cookie.

**Request Body:**
```json
{
  "username": "user@example.com",  // Username or email
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "last_login": "2025-01-15T12:00:00Z"
  },
  "mfa_required": false  // True if MFA is enabled
}
```

**If MFA Required:** `200 OK`
```json
{
  "mfa_required": true,
  "temp_token": "temporary_token_for_mfa_verification"
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account disabled
- `500 Internal Server Error`: Server error

---

### Login as Guest

**Endpoint:** `POST /auth/guest`

**Description:** Create temporary guest session (expires in 1 hour).

**Request Body:** None

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": null,
    "username": "guest_abc123",
    "full_name": "Guest User",
    "role": "guest",
    "is_active": true,
    "created_at": "2025-01-15T12:00:00Z",
    "last_login": "2025-01-15T12:00:00Z"
  }
}
```

---

### Logout

**Endpoint:** `POST /auth/logout`

**Description:** End current session and invalidate token.

**Authentication:** Required

**Request Body:** None

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

### Get Current User

**Endpoint:** `GET /auth/me`

**Description:** Retrieve current authenticated user information.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-01-15T10:00:00Z",
    "last_login": "2025-01-15T12:00:00Z"
  }
}
```

---

### Forgot Password

**Endpoint:** `POST /auth/forgot-password`

**Description:** Request password reset email (development: token logged to console).

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset instructions sent to email",
  "reset_token": "abc123..."  // Only in development mode
}
```

**Note:** In production, token is sent via email only.

---

### Reset Password

**Endpoint:** `POST /auth/reset-password`

**Description:** Reset password using token from forgot-password endpoint.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "NewSecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset successful"
}
```

**Errors:**
- `400 Bad Request`: Invalid token, token expired, or password validation failed
- `500 Internal Server Error`: Server error

---

## Multi-Factor Authentication (MFA)

### Setup MFA

**Endpoint:** `POST /auth/mfa/setup`

**Description:** Initialize MFA setup and generate TOTP secret with QR code URI.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_uri": "otpauth://totp/Rivendell:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Rivendell",
  "backup_codes": [
    "1234-5678",
    "9012-3456",
    ...  // 10 codes total
  ]
}
```

**Note:** Save backup codes securely. They are shown only once.

---

### Enable MFA

**Endpoint:** `POST /auth/mfa/enable`

**Description:** Enable MFA after verifying TOTP code.

**Authentication:** Required

**Request Body:**
```json
{
  "code": "123456"  // 6-digit TOTP code from authenticator app
}
```

**Response:** `200 OK`
```json
{
  "message": "MFA enabled successfully"
}
```

**Errors:**
- `400 Bad Request`: Invalid TOTP code or MFA already enabled
- `401 Unauthorized`: Not authenticated

---

### Disable MFA

**Endpoint:** `POST /auth/mfa/disable`

**Description:** Disable MFA for current user.

**Authentication:** Required

**Request Body:**
```json
{
  "code": "123456"  // Current TOTP code or backup code
}
```

**Response:** `200 OK`
```json
{
  "message": "MFA disabled successfully"
}
```

---

### Verify MFA

**Endpoint:** `POST /auth/mfa/verify`

**Description:** Complete login with MFA code.

**Request Body:**
```json
{
  "temp_token": "temporary_token_from_login",
  "code": "123456"  // TOTP code or backup code
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "role": "user",
    "mfa_enabled": true
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid code or temp token
- `400 Bad Request`: Backup code already used

---

### Regenerate Backup Codes

**Endpoint:** `POST /auth/mfa/regenerate-backup-codes`

**Description:** Generate new set of backup codes (invalidates old ones).

**Authentication:** Required

**Request Body:**
```json
{
  "code": "123456"  // Current TOTP code for verification
}
```

**Response:** `200 OK`
```json
{
  "backup_codes": [
    "1234-5678",
    "9012-3456",
    ...  // 10 new codes
  ]
}
```

---

## Admin Endpoints

**Role Required:** `ADMIN`

### Reset User Password (Admin)

**Endpoint:** `POST /auth/admin/reset-user-password`

**Description:** Admin can reset any user's password (except other admins). Invalidates all user sessions.

**Authentication:** Admin role required

**Request Body:**
```json
{
  "user_id": "uuid",
  "new_password": "NewPassword123!"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset successful for user username"
}
```

**Errors:**
- `403 Forbidden`: Cannot reset admin passwords or insufficient permissions
- `404 Not Found`: User not found

---

### Disable User MFA (Admin)

**Endpoint:** `POST /auth/admin/disable-user-mfa`

**Description:** Emergency MFA disable for locked-out users.

**Authentication:** Admin role required

**Request Body:**
```json
{
  "user_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "message": "MFA disabled for user username"
}
```

**Errors:**
- `400 Bad Request`: MFA not enabled for user
- `404 Not Found`: User not found

---

### Toggle User Account Status (Admin)

**Endpoint:** `POST /auth/admin/toggle-user-status`

**Description:** Enable or disable user account.

**Authentication:** Admin role required

**Request Body:**
```json
{
  "user_id": "uuid",
  "is_active": false  // true to enable, false to disable
}
```

**Response:** `200 OK`
```json
{
  "message": "User account disabled successfully"
}
```

**Errors:**
- `403 Forbidden`: Cannot disable admin accounts or insufficient permissions
- `404 Not Found`: User not found

---

### List All Users (Admin)

**Endpoint:** `GET /auth/admin/users`

**Description:** Get list of all users with security status.

**Authentication:** Admin role required

**Query Parameters:**
- `role` (optional): Filter by role (user, admin, guest)
- `active_only` (optional): Boolean, show only active users

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-01-15T10:00:00Z",
    "last_login": "2025-01-15T12:00:00Z"
  },
  ...
]
```

---

## Job Management

### Create Job

**Endpoint:** `POST /api/jobs`

**Description:** Create and queue a new forensic analysis job.

**Authentication:** Required (User or Admin role)

**Request Body:**
```json
{
  "case_number": "CASE-2025-001",
  "source_paths": [
    "/evidence/disk.E01",
    "/evidence/memory.dmp"
  ],
  "destination_path": "/output/CASE-2025-001",
  "options": {
    "collect": true,
    "process": true,
    "analyze": true,
    "memory_analysis": true,
    "timeline": true,
    "extract_iocs": true,
    "speed_mode": "brisk"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "case_number": "CASE-2025-001",
  "source_paths": ["/evidence/disk.E01"],
  "destination_path": "/output/CASE-2025-001",
  "options": {},
  "status": "pending",
  "progress": 0,
  "log": [],
  "result": null,
  "error": null,
  "celery_task_id": "task-uuid",
  "created_at": "2025-01-15T12:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

**Validation:**
- `case_number`: Required, sanitized (alphanumeric, hyphens, underscores)
- `source_paths`: Required, non-empty array, validated against allowed paths
- `destination_path`: Required, validated path
- `options`: Optional JSON object

**Errors:**
- `400 Bad Request`: Validation error or invalid paths
- `403 Forbidden`: Guest users cannot create jobs or access denied to path
- `500 Internal Server Error`: Server error

---

### List Jobs

**Endpoint:** `GET /api/jobs`

**Description:** List all jobs for current user (admins see all jobs).

**Authentication:** Required

**Query Parameters:**
- `status` (optional): Filter by status (pending, running, completed, failed, cancelled, archived)
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `case_number` (optional): Filter by case number

**Response:** `200 OK`
```json
{
  "jobs": [
    {
      "id": "uuid",
      "case_number": "CASE-2025-001",
      "status": "completed",
      "progress": 100,
      "created_at": "2025-01-15T12:00:00Z",
      "completed_at": "2025-01-15T13:00:00Z"
    },
    ...
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### Get Job Details

**Endpoint:** `GET /api/jobs/{job_id}`

**Description:** Retrieve detailed information about a specific job.

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "case_number": "CASE-2025-001",
  "source_paths": ["/evidence/disk.E01"],
  "destination_path": "/output/CASE-2025-001",
  "options": {},
  "status": "running",
  "progress": 45,
  "log": [
    {"timestamp": "2025-01-15T12:00:00Z", "level": "INFO", "message": "Job started"},
    {"timestamp": "2025-01-15T12:15:00Z", "level": "INFO", "message": "Processing artifacts..."}
  ],
  "result": null,
  "error": null,
  "celery_task_id": "task-uuid",
  "created_at": "2025-01-15T12:00:00Z",
  "started_at": "2025-01-15T12:00:01Z",
  "completed_at": null
}
```

**Errors:**
- `404 Not Found`: Job not found or unauthorized access

---

### Update Job

**Endpoint:** `PATCH /api/jobs/{job_id}`

**Description:** Update job fields (limited to specific fields).

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Request Body:**
```json
{
  "status": "running",  // Optional
  "progress": 50,        // Optional, 0-100
  "log": ["New log entry"],  // Optional, appends to log
  "result": {},          // Optional
  "error": "Error message"  // Optional
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "running",
  "progress": 50,
  ...
}
```

**Errors:**
- `404 Not Found`: Job not found
- `400 Bad Request`: Invalid update data

---

### Delete Job

**Endpoint:** `DELETE /api/jobs/{job_id}`

**Description:** Permanently delete a job. Cannot delete running jobs (cancel first).

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `204 No Content`

**Errors:**
- `400 Bad Request`: Cannot delete running job
- `404 Not Found`: Job not found

---

### Cancel Job

**Endpoint:** `POST /api/jobs/{job_id}/cancel`

**Description:** Cancel a running or pending job. Terminates Celery task.

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

**Errors:**
- `400 Bad Request`: Job not in running/pending state
- `404 Not Found`: Job not found

---

### Restart Job

**Endpoint:** `POST /api/jobs/{job_id}/restart`

**Description:** Restart a failed or cancelled job. Creates new Celery task.

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "pending",
  "celery_task_id": "new-task-uuid",
  "message": "Job restarted successfully"
}
```

**Errors:**
- `400 Bad Request`: Job not in failed/cancelled state
- `404 Not Found`: Job not found

---

### Archive Job

**Endpoint:** `POST /api/jobs/{job_id}/archive`

**Description:** Archive a completed or failed job. Preserves original status for restoration.

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "archived",
  "archived_at": "2025-01-15T15:00:00Z",
  "message": "Job archived successfully"
}
```

**Errors:**
- `400 Bad Request`: Cannot archive running jobs
- `404 Not Found`: Job not found

---

### Unarchive Job

**Endpoint:** `POST /api/jobs/{job_id}/unarchive`

**Description:** Restore archived job to original status (completed/failed).

**Authentication:** Required

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "completed",  // Restored to original status
  "archived_at": null,
  "message": "Job restored successfully"
}
```

**Errors:**
- `400 Bad Request`: Job not archived
- `404 Not Found`: Job not found

---

### Bulk Cancel Jobs

**Endpoint:** `POST /api/jobs/bulk/cancel`

**Description:** Cancel multiple jobs at once.

**Authentication:** Required

**Request Body:**
```json
{
  "job_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:** `200 OK`
```json
{
  "cancelled": 3,
  "failed": 0,
  "errors": []
}
```

---

### Bulk Delete Jobs

**Endpoint:** `POST /api/jobs/bulk/delete`

**Description:** Delete multiple jobs at once.

**Authentication:** Required

**Request Body:**
```json
{
  "job_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:** `200 OK`
```json
{
  "deleted": 3,
  "failed": 0,
  "errors": []
}
```

---

### Bulk Archive Jobs

**Endpoint:** `POST /api/jobs/bulk/archive`

**Description:** Archive multiple jobs at once.

**Authentication:** Required

**Request Body:**
```json
{
  "job_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:** `200 OK`
```json
{
  "archived": 3,
  "failed": 0,
  "errors": []
}
```

---

## File System

### Browse File System

**Endpoint:** `GET /api/fs/browse`

**Description:** Browse server filesystem (limited to configured allowed paths).

**Authentication:** Required

**Query Parameters:**
- `path` (optional): Path to browse (default: "/")

**Response:** `200 OK`
```json
[
  {
    "name": "evidence",
    "path": "/evidence",
    "type": "directory",
    "size": null,
    "modified": "2025-01-15T10:00:00Z"
  },
  {
    "name": "disk.E01",
    "path": "/evidence/disk.E01",
    "type": "file",
    "size": 10737418240,
    "modified": "2025-01-15T09:00:00Z"
  }
]
```

**Errors:**
- `403 Forbidden`: Access denied to path
- `404 Not Found`: Path does not exist

---

## Health Check

### Health Status

**Endpoint:** `GET /api/health`

**Description:** Check API health status.

**Authentication:** None

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T12:00:00Z",
  "version": "2.1.0"
}
```

---

## Request/Response Formats

### Standard Success Response

```json
{
  "data": { ... },
  "message": "Operation successful"
}
```

### Standard Error Response

```json
{
  "detail": "Error description",
  "error_code": "ERR_001"  // Optional
}
```

### Validation Error Response (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid request or validation error
- `401 Unauthorized`: Authentication required or invalid credentials
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Common Error Codes

- `ERR_AUTH_001`: Invalid credentials
- `ERR_AUTH_002`: Account disabled
- `ERR_AUTH_003`: MFA verification failed
- `ERR_JOB_001`: Job not found
- `ERR_JOB_002`: Invalid job state transition
- `ERR_PATH_001`: Path access denied

---

## Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "user@example.com",
    "password": "password"
})
data = response.json()
token = data["access_token"]

# Create job with authentication
headers = {"Authorization": f"Bearer {token}"}
job_response = requests.post(
    f"{BASE_URL}/jobs",
    headers=headers,
    json={
        "case_number": "CASE-001",
        "source_paths": ["/evidence/disk.E01"],
        "destination_path": "/output/CASE-001",
        "options": {"collect": True, "analyze": True}
    }
)
job = job_response.json()
print(f"Job created: {job['id']}")

# Check job status
job_id = job["id"]
status_response = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
print(f"Job status: {status_response.json()['status']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api';

async function main() {
  // Login
  const loginResponse = await axios.post(`${BASE_URL}/auth/login`, {
    username: 'user@example.com',
    password: 'password'
  });

  const token = loginResponse.data.access_token;

  // Create job
  const jobResponse = await axios.post(
    `${BASE_URL}/jobs`,
    {
      case_number: 'CASE-001',
      source_paths: ['/evidence/disk.E01'],
      destination_path: '/output/CASE-001',
      options: { collect: true, analyze: true }
    },
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  console.log('Job created:', jobResponse.data.id);

  // Monitor job
  const jobId = jobResponse.data.id;
  const statusResponse = await axios.get(
    `${BASE_URL}/jobs/${jobId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  console.log('Job status:', statusResponse.data.status);
}

main();
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}' \
  | jq -r '.access_token' > token.txt

TOKEN=$(cat token.txt)

# Create job
curl -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "CASE-001",
    "source_paths": ["/evidence/disk.E01"],
    "destination_path": "/output/CASE-001",
    "options": {"collect": true, "analyze": true}
  }'

# List jobs
curl -X GET "http://localhost:8000/api/jobs?status=running" \
  -H "Authorization: Bearer $TOKEN"

# Cancel job
curl -X POST "http://localhost:8000/api/jobs/{job_id}/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Security Best Practices

1. **Always use HTTPS in production** - Encrypt all API communication
2. **Store tokens securely** - Never log or expose JWT tokens
3. **Implement rate limiting** - Prevent brute force attacks
4. **Validate all inputs** - API performs sanitization, but client validation helps UX
5. **Use MFA for sensitive accounts** - Especially admin accounts
6. **Rotate tokens regularly** - Implement token refresh mechanism
7. **Monitor API usage** - Track suspicious activity
8. **Keep secrets secret** - Use environment variables, never hardcode

---

## Rate Limiting

**Status:** Planned for v2.2

Future rate limits (per user):
- Authentication endpoints: 10 requests/minute
- Job creation: 100 requests/hour
- Other endpoints: 1000 requests/hour

---

## Pagination

For list endpoints (e.g., `/api/jobs`):

**Query Parameters:**
- `limit`: Number of results per page (default: 50, max: 100)
- `offset`: Number of results to skip (default: 0)

**Response includes:**
- `total`: Total number of results
- `limit`: Applied limit
- `offset`: Applied offset

**Example:**
```
GET /api/jobs?limit=20&offset=40
```

---

## WebSocket Support

**Status:** Planned for v2.2

Real-time job progress updates via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Progress: ${update.progress}%`);
  console.log(`Status: ${update.status}`);
};
```

---

**For additional support, see:**
- [SECURITY.md](/docs/SECURITY.md) - Security implementation details
- [QUICKSTART.md](/docs/QUICKSTART.md) - Getting started guide
- [USER_GUIDE.md](/docs/USER_GUIDE.md) - Complete user documentation

---

**Version:** 2.1.0
**Last Updated:** 2025-01-15
**License:** See LICENSE file
