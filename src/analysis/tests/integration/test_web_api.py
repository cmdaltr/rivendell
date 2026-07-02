"""
Integration Tests for Web Backend API

Tests the FastAPI web backend endpoints.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "web" / "backend"))

from main import app
from storage import JobStorage
from models.job import Job, JobStatus, AnalysisOptions


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_storage(temp_dir):
    """Create test storage."""
    storage_dir = temp_dir / "jobs"
    storage_dir.mkdir()
    return JobStorage(storage_dir=storage_dir)


@pytest.mark.web
@pytest.mark.integration
class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.web
@pytest.mark.integration
class TestFileSystemAPI:
    """Test file system browsing API."""

    def test_browse_filesystem_root(self, client, temp_dir):
        """Test browsing root directory."""
        with patch("main.settings.allowed_paths", [str(temp_dir)]):
            response = client.get(f"/api/fs/browse?path={temp_dir}")

            assert response.status_code == 200
            items = response.json()
            assert isinstance(items, list)

    def test_browse_filesystem_forbidden(self, client):
        """Test browsing forbidden directory."""
        response = client.get("/api/fs/browse?path=/etc")

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_browse_filesystem_not_found(self, client, temp_dir):
        """Test browsing non-existent directory."""
        nonexistent = temp_dir / "nonexistent"

        with patch("main.settings.allowed_paths", [str(temp_dir)]):
            response = client.get(f"/api/fs/browse?path={nonexistent}")

            assert response.status_code == 404

    def test_browse_filesystem_with_images(self, client, temp_dir):
        """Test browsing directory with disk images."""
        # Create test files
        (temp_dir / "test.E01").write_bytes(b"0" * 1024)
        (temp_dir / "test.txt").write_text("test")

        with patch("main.settings.allowed_paths", [str(temp_dir)]):
            response = client.get(f"/api/fs/browse?path={temp_dir}")

            assert response.status_code == 200
            items = response.json()

            # Find the E01 file
            e01_item = next((i for i in items if i["name"] == "test.E01"), None)
            assert e01_item is not None
            assert e01_item["is_image"] is True

    def test_browse_filesystem_parent_directory(self, client, temp_dir):
        """Test browsing with parent directory link."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        with patch("main.settings.allowed_paths", [str(temp_dir)]):
            response = client.get(f"/api/fs/browse?path={subdir}")

            assert response.status_code == 200
            items = response.json()

            # Should have parent directory link
            parent_item = next((i for i in items if i["name"] == ".."), None)
            assert parent_item is not None
            assert parent_item["is_directory"] is True


@pytest.mark.web
@pytest.mark.integration
class TestJobManagementAPI:
    """Test job management API endpoints."""

    def test_create_job(self, client, temp_dir):
        """Test creating a new analysis job."""
        # Create test image
        test_image = temp_dir / "test.E01"
        test_image.write_bytes(b"0" * 1024)

        job_data = {
            "case_number": "INC-2025-001",
            "source_paths": [str(test_image)],
            "destination_path": str(temp_dir / "output"),
            "options": {
                "collect": True,
                "process": True,
                "quick": True,
            }
        }

        with patch("main.start_analysis.delay"):
            response = client.post("/api/jobs", json=job_data)

            assert response.status_code == 200
            data = response.json()
            assert data["case_number"] == "INC-2025-001"
            assert data["status"] == "pending"
            assert "id" in data

    def test_create_job_missing_source(self, client):
        """Test creating job with missing source path."""
        job_data = {
            "case_number": "INC-2025-001",
            "source_paths": ["/nonexistent/file.E01"],
            "options": {}
        }

        response = client.post("/api/jobs", json=job_data)

        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    def test_list_jobs_empty(self, client):
        """Test listing jobs when none exist."""
        with patch("main.job_storage.list_jobs", return_value=[]), \
             patch("main.job_storage.count_jobs", return_value=0):

            response = client.get("/api/jobs")

            assert response.status_code == 200
            data = response.json()
            assert data["jobs"] == []
            assert data["total"] == 0

    def test_list_jobs_with_pagination(self, client, sample_job_data):
        """Test listing jobs with pagination."""
        jobs = [Job(**{**sample_job_data, "id": f"job-{i}"}) for i in range(10)]

        with patch("main.job_storage.list_jobs", return_value=jobs[:5]), \
             patch("main.job_storage.count_jobs", return_value=10):

            response = client.get("/api/jobs?limit=5&offset=0")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 5
            assert data["total"] == 10

    def test_list_jobs_filter_by_status(self, client, sample_job_data):
        """Test filtering jobs by status."""
        running_jobs = [
            Job(**{**sample_job_data, "id": f"job-{i}", "status": JobStatus.RUNNING})
            for i in range(3)
        ]

        with patch("main.job_storage.list_jobs", return_value=running_jobs), \
             patch("main.job_storage.count_jobs", return_value=3):

            response = client.get("/api/jobs?status=running")

            assert response.status_code == 200
            data = response.json()
            assert all(j["status"] == "running" for j in data["jobs"])

    def test_get_job(self, client, sample_job_data):
        """Test getting specific job details."""
        job = Job(**sample_job_data)

        with patch("main.job_storage.get_job", return_value=job):
            response = client.get(f"/api/jobs/{job.id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == job.id
            assert data["case_number"] == job.case_number

    def test_get_job_not_found(self, client):
        """Test getting non-existent job."""
        with patch("main.job_storage.get_job", return_value=None):
            response = client.get("/api/jobs/nonexistent")

            assert response.status_code == 404

    def test_update_job(self, client, sample_job_data):
        """Test updating job status and progress."""
        job = Job(**sample_job_data)

        update_data = {
            "status": "running",
            "progress": 50,
            "log_message": "Processing registry hives"
        }

        with patch("main.job_storage.get_job", return_value=job), \
             patch("main.job_storage.save_job"):

            response = client.patch(f"/api/jobs/{job.id}", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "running"
            assert data["progress"] == 50

    def test_delete_job_completed(self, client, sample_job_data):
        """Test deleting completed job."""
        job = Job(**{**sample_job_data, "status": JobStatus.COMPLETED})

        with patch("main.job_storage.get_job", return_value=job), \
             patch("main.job_storage.delete_job"):

            response = client.delete(f"/api/jobs/{job.id}")

            assert response.status_code == 200
            assert "deleted successfully" in response.json()["message"]

    def test_delete_job_running(self, client, sample_job_data):
        """Test deleting running job (should fail)."""
        job = Job(**{**sample_job_data, "status": JobStatus.RUNNING})

        with patch("main.job_storage.get_job", return_value=job):
            response = client.delete(f"/api/jobs/{job.id}")

            assert response.status_code == 400
            assert "Cannot delete" in response.json()["detail"]

    def test_cancel_job(self, client, sample_job_data):
        """Test cancelling a running job."""
        job = Job(**{**sample_job_data, "status": JobStatus.RUNNING})

        with patch("main.job_storage.get_job", return_value=job), \
             patch("main.job_storage.save_job"):

            response = client.post(f"/api/jobs/{job.id}/cancel")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "cancelled"

    def test_cancel_job_already_completed(self, client, sample_job_data):
        """Test cancelling already completed job."""
        job = Job(**{**sample_job_data, "status": JobStatus.COMPLETED})

        with patch("main.job_storage.get_job", return_value=job):
            response = client.post(f"/api/jobs/{job.id}/cancel")

            assert response.status_code == 400
            assert "Can only cancel" in response.json()["detail"]


@pytest.mark.web
@pytest.mark.integration
class TestCORSHeaders:
    """Test CORS headers."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get("/")

        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options("/api/jobs")

        assert response.status_code == 200
        assert "access-control-allow-methods" in response.headers


@pytest.mark.web
@pytest.mark.integration
class TestAPIPerformance:
    """Test API performance benchmarks."""

    def test_health_check_performance(self, client):
        """Test health check responds quickly."""
        import time

        start = time.time()
        response = client.get("/api/health")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 1.0  # Should respond in < 1 second

    def test_job_list_performance(self, client):
        """Test job listing performs well."""
        import time

        with patch("main.job_storage.list_jobs", return_value=[]), \
             patch("main.job_storage.count_jobs", return_value=0):

            start = time.time()
            response = client.get("/api/jobs")
            duration = time.time() - start

            assert response.status_code == 200
            assert duration < 3.0  # Should respond in < 3 seconds
