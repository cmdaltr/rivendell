"""
Elrond Web Backend

FastAPI backend for the Elrond web interface.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .models.job import (
    Job,
    JobCreate,
    JobListResponse,
    JobStatus,
    JobUpdate,
    FileSystemItem,
)
from .storage import JobStorage
from .tasks import start_analysis

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
job_storage = JobStorage()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# File System API
@app.get("/api/fs/browse", response_model=List[FileSystemItem])
async def browse_filesystem(path: str = Query("/", description="Path to browse")):
    """
    Browse filesystem to select disk/memory images.

    Args:
        path: Directory path to browse

    Returns:
        List of files and directories
    """
    try:
        # Security: Only allow browsing specific paths
        path_obj = Path(path).resolve()
        allowed = any(
            str(path_obj).startswith(allowed_path)
            for allowed_path in settings.allowed_paths
        )

        if not allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Allowed paths: {settings.allowed_paths}",
            )

        if not path_obj.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not path_obj.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        items = []

        # Add parent directory link if not at root
        if path != "/" and str(path_obj.parent) != str(path_obj):
            items.append(
                FileSystemItem(
                    name="..",
                    path=str(path_obj.parent),
                    is_directory=True,
                )
            )

        # List directory contents
        for item in sorted(path_obj.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
            try:
                stat = item.stat()

                # Check if file is a disk/memory image
                is_image = False
                if item.is_file():
                    ext = item.suffix.lower()
                    is_image = ext in [
                        ".e01", ".ex01", ".raw", ".dd", ".img", ".bin",
                        ".vmdk", ".vhd", ".vhdx", ".mem", ".dmp", ".lime"
                    ]

                items.append(
                    FileSystemItem(
                        name=item.name,
                        path=str(item),
                        is_directory=item.is_dir(),
                        size=stat.st_size if item.is_file() else None,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        is_image=is_image,
                    )
                )
            except (PermissionError, OSError):
                # Skip items we can't access
                continue

        return items

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Job Management API
@app.post("/api/jobs", response_model=Job)
async def create_job(job_request: JobCreate):
    """
    Create a new analysis job.

    Args:
        job_request: Job creation request

    Returns:
        Created job
    """
    try:
        # Validate source paths exist
        for path in job_request.source_paths:
            if not Path(path).exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Source path does not exist: {path}",
                )

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create job
        job = Job(
            id=job_id,
            case_number=job_request.case_number,
            source_paths=job_request.source_paths,
            destination_path=job_request.destination_path,
            options=job_request.options,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
        )

        # Save job
        job_storage.save_job(job)

        # Start analysis task
        start_analysis.delay(job_id)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[JobStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List all analysis jobs.

    Args:
        status: Filter by job status
        limit: Maximum number of jobs to return
        offset: Offset for pagination

    Returns:
        List of jobs
    """
    try:
        jobs = job_storage.list_jobs(status=status, limit=limit, offset=offset)
        total = job_storage.count_jobs(status=status)

        return JobListResponse(jobs=jobs, total=total)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """
    Get job details.

    Args:
        job_id: Job ID

    Returns:
        Job details
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/jobs/{job_id}", response_model=Job)
async def update_job(job_id: str, update: JobUpdate):
    """
    Update job status and progress.

    Args:
        job_id: Job ID
        update: Job update request

    Returns:
        Updated job
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Update job fields
        if update.status:
            job.status = update.status

            if update.status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now()
            elif update.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job.completed_at = datetime.now()

        if update.progress is not None:
            job.progress = update.progress

        if update.log_message:
            job.log.append(f"[{datetime.now().isoformat()}] {update.log_message}")

        if update.result:
            job.result = update.result

        if update.error:
            job.error = update.error

        # Save updated job
        job_storage.save_job(job)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job.

    Args:
        job_id: Job ID

    Returns:
        Success message
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Only allow deleting completed/failed/cancelled jobs
        if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete running or pending job",
            )

        job_storage.delete_job(job_id)

        return {"message": "Job deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a running job.

    Args:
        job_id: Job ID

    Returns:
        Updated job
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            raise HTTPException(
                status_code=400,
                detail="Can only cancel pending or running jobs",
            )

        # Update job status
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now()
        job.log.append(f"[{datetime.now().isoformat()}] Job cancelled by user")

        job_storage.save_job(job)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
