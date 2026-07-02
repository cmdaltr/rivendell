"""
Unit Tests for Job Storage

Tests the job storage and persistence system.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path

from web.backend.storage import JobStorage
from web.backend.models.job import Job, JobStatus, AnalysisOptions


@pytest.mark.unit
class TestJobStorage:
    """Test JobStorage class."""

    def test_init(self, temp_dir):
        """Test storage initialization."""
        storage_dir = temp_dir / "jobs"
        storage = JobStorage(storage_dir=storage_dir)

        assert storage.storage_dir == storage_dir
        assert storage_dir.exists()

    def test_init_creates_directory(self, temp_dir):
        """Test that init creates storage directory."""
        storage_dir = temp_dir / "nonexistent" / "jobs"

        storage = JobStorage(storage_dir=storage_dir)

        assert storage_dir.exists()

    def test_save_job(self, temp_dir, sample_job_data):
        """Test saving a job."""
        storage = JobStorage(storage_dir=temp_dir)
        job = Job(**sample_job_data)

        storage.save_job(job)

        job_file = temp_dir / f"{job.id}.json"
        assert job_file.exists()

        # Verify content
        with open(job_file) as f:
            data = json.load(f)
            assert data["id"] == job.id
            assert data["case_number"] == job.case_number

    def test_get_job_exists(self, temp_dir, sample_job_data):
        """Test getting an existing job."""
        storage = JobStorage(storage_dir=temp_dir)
        job = Job(**sample_job_data)

        storage.save_job(job)
        retrieved = storage.get_job(job.id)

        assert retrieved is not None
        assert retrieved.id == job.id
        assert retrieved.case_number == job.case_number
        assert retrieved.status == job.status

    def test_get_job_not_exists(self, temp_dir):
        """Test getting a non-existent job."""
        storage = JobStorage(storage_dir=temp_dir)

        retrieved = storage.get_job("nonexistent-id")

        assert retrieved is None

    def test_list_jobs_empty(self, temp_dir):
        """Test listing jobs when none exist."""
        storage = JobStorage(storage_dir=temp_dir)

        jobs = storage.list_jobs()

        assert jobs == []

    def test_list_jobs_with_data(self, temp_dir, sample_job_data):
        """Test listing jobs with data."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create multiple jobs
        for i in range(5):
            job = Job(**{**sample_job_data, "id": f"job-{i}"})
            storage.save_job(job)

        jobs = storage.list_jobs()

        assert len(jobs) == 5

    def test_list_jobs_pagination(self, temp_dir, sample_job_data):
        """Test listing jobs with pagination."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create 10 jobs
        for i in range(10):
            job = Job(**{**sample_job_data, "id": f"job-{i}"})
            storage.save_job(job)

        # Get first 5
        jobs_page1 = storage.list_jobs(limit=5, offset=0)
        assert len(jobs_page1) == 5

        # Get next 5
        jobs_page2 = storage.list_jobs(limit=5, offset=5)
        assert len(jobs_page2) == 5

        # Ensure they're different
        page1_ids = {j.id for j in jobs_page1}
        page2_ids = {j.id for j in jobs_page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_list_jobs_filter_by_status(self, temp_dir, sample_job_data):
        """Test filtering jobs by status."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create jobs with different statuses
        for i, status in enumerate([JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED]):
            job = Job(**{**sample_job_data, "id": f"job-{i}", "status": status})
            storage.save_job(job)

        # Filter by running
        running_jobs = storage.list_jobs(status=JobStatus.RUNNING)

        assert len(running_jobs) == 1
        assert running_jobs[0].status == JobStatus.RUNNING

    def test_count_jobs(self, temp_dir, sample_job_data):
        """Test counting jobs."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create jobs
        for i in range(7):
            job = Job(**{**sample_job_data, "id": f"job-{i}"})
            storage.save_job(job)

        count = storage.count_jobs()

        assert count == 7

    def test_count_jobs_with_filter(self, temp_dir, sample_job_data):
        """Test counting jobs with status filter."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create jobs with different statuses
        for i in range(3):
            job = Job(**{**sample_job_data, "id": f"pending-{i}", "status": JobStatus.PENDING})
            storage.save_job(job)

        for i in range(2):
            job = Job(**{**sample_job_data, "id": f"running-{i}", "status": JobStatus.RUNNING})
            storage.save_job(job)

        count_pending = storage.count_jobs(status=JobStatus.PENDING)
        count_running = storage.count_jobs(status=JobStatus.RUNNING)

        assert count_pending == 3
        assert count_running == 2

    def test_delete_job(self, temp_dir, sample_job_data):
        """Test deleting a job."""
        storage = JobStorage(storage_dir=temp_dir)
        job = Job(**sample_job_data)

        storage.save_job(job)
        assert storage.get_job(job.id) is not None

        storage.delete_job(job.id)
        assert storage.get_job(job.id) is None

    def test_delete_nonexistent_job(self, temp_dir):
        """Test deleting a non-existent job (should not error)."""
        storage = JobStorage(storage_dir=temp_dir)

        # Should not raise exception
        storage.delete_job("nonexistent-id")

    def test_job_ordering_by_modified_time(self, temp_dir, sample_job_data):
        """Test that jobs are ordered by modification time (newest first)."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create jobs with delay
        import time

        job1 = Job(**{**sample_job_data, "id": "job-1"})
        storage.save_job(job1)
        time.sleep(0.1)

        job2 = Job(**{**sample_job_data, "id": "job-2"})
        storage.save_job(job2)
        time.sleep(0.1)

        job3 = Job(**{**sample_job_data, "id": "job-3"})
        storage.save_job(job3)

        jobs = storage.list_jobs()

        # Should be in reverse chronological order (newest first)
        assert jobs[0].id == "job-3"
        assert jobs[1].id == "job-2"
        assert jobs[2].id == "job-1"

    def test_save_job_updates_existing(self, temp_dir, sample_job_data):
        """Test that saving updates existing job."""
        storage = JobStorage(storage_dir=temp_dir)
        job = Job(**sample_job_data)

        storage.save_job(job)

        # Update job
        job.status = JobStatus.COMPLETED
        job.progress = 100
        storage.save_job(job)

        # Retrieve and verify
        retrieved = storage.get_job(job.id)
        assert retrieved.status == JobStatus.COMPLETED
        assert retrieved.progress == 100

    def test_invalid_job_file_skipped(self, temp_dir):
        """Test that invalid job files are skipped."""
        storage = JobStorage(storage_dir=temp_dir)

        # Create invalid job file
        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        # Should not crash
        jobs = storage.list_jobs()
        assert jobs == []

    def test_get_job_path(self, temp_dir):
        """Test internal get_job_path method."""
        storage = JobStorage(storage_dir=temp_dir)

        path = storage._get_job_path("test-job-123")

        assert path == temp_dir / "test-job-123.json"
        assert "test-job-123.json" in str(path)
