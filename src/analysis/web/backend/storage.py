"""
Job Storage

Simple file-based storage for jobs (can be replaced with database later).
"""

import json
from pathlib import Path
from typing import Optional, List

from .models.job import Job, JobStatus
from .config import settings


class JobStorage:
    """File-based job storage."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize job storage.

        Args:
            storage_dir: Directory to store job files
        """
        self.storage_dir = storage_dir or settings.output_dir / "jobs"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_job_path(self, job_id: str) -> Path:
        """Get path to job file."""
        return self.storage_dir / f"{job_id}.json"

    def save_job(self, job: Job) -> None:
        """
        Save job to storage.

        Args:
            job: Job to save
        """
        job_path = self._get_job_path(job.id)

        with open(job_path, "w") as f:
            json.dump(job.dict(), f, indent=2, default=str)

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job from storage.

        Args:
            job_id: Job ID

        Returns:
            Job if found, None otherwise
        """
        job_path = self._get_job_path(job_id)

        if not job_path.exists():
            return None

        with open(job_path, "r") as f:
            data = json.load(f)
            return Job(**data)

    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Job]:
        """
        List jobs from storage.

        Args:
            status: Filter by job status
            limit: Maximum number of jobs to return
            offset: Offset for pagination

        Returns:
            List of jobs
        """
        jobs = []

        # Get all job files
        job_files = sorted(
            self.storage_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        # Filter and paginate
        for job_file in job_files:
            try:
                with open(job_file, "r") as f:
                    data = json.load(f)
                    job = Job(**data)

                    # Filter by status if specified
                    if status and job.status != status:
                        continue

                    jobs.append(job)
            except Exception:
                # Skip invalid job files
                continue

        # Apply pagination
        return jobs[offset : offset + limit]

    def count_jobs(self, status: Optional[JobStatus] = None) -> int:
        """
        Count jobs in storage.

        Args:
            status: Filter by job status

        Returns:
            Number of jobs
        """
        count = 0

        for job_file in self.storage_dir.glob("*.json"):
            try:
                with open(job_file, "r") as f:
                    data = json.load(f)
                    job = Job(**data)

                    if status and job.status != status:
                        continue

                    count += 1
            except Exception:
                continue

        return count

    def delete_job(self, job_id: str) -> None:
        """
        Delete job from storage.

        Args:
            job_id: Job ID
        """
        job_path = self._get_job_path(job_id)

        if job_path.exists():
            job_path.unlink()
