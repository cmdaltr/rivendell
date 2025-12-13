"""
Elrond Web Backend

FastAPI backend for the Elrond web interface.
"""

import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from .config import settings
    from .auth.routes_simple import router as auth_router  # Simple file-based auth
    from .ai_routes import router as ai_router  # AI assistant routes
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
except ImportError:
    # Fallback for standalone execution
    from config import settings
    from auth.routes_simple import router as auth_router  # Simple file-based auth
    from ai_routes import router as ai_router  # AI assistant routes
    from models.job import (
        Job,
        JobCreate,
        JobListResponse,
        JobStatus,
        JobUpdate,
        FileSystemItem,
        FileSystemBrowseResponse,
    )
    from storage import JobStorage
    from tasks_docker import start_analysis

# Temporary replacements for security_utils
def sanitize_case_number(case_number: str) -> str:
    """Basic sanitization of case number."""
    return case_number.replace("/", "_").replace("\\", "_").replace("..", "")

def sanitize_path(path: str, allowed_prefixes: List[str]) -> Optional[str]:
    """
    Sanitize and validate file path.

    Args:
        path: Path to validate
        allowed_prefixes: List of allowed path prefixes

    Returns:
        Sanitized path if valid, None otherwise
    """
    if not path:
        return None

    # Resolve to absolute path to prevent traversal
    try:
        abs_path = os.path.abspath(path)
    except (ValueError, OSError):
        return None

    # Check if path starts with any allowed prefix
    for prefix in allowed_prefixes:
        abs_prefix = os.path.abspath(prefix)
        if abs_path.startswith(abs_prefix):
            return abs_path

    return None

# Initialize logger
logger = logging.getLogger(__name__)

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


# Startup event
@app.on_event("startup")
async def on_startup():
    """Run startup tasks."""
    # startup()  # Disabled - using file-based storage, not database
    pass


# Include authentication routes
app.include_router(auth_router)

# Include AI assistant routes
app.include_router(ai_router)


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
@app.get("/api/fs/browse", response_model=FileSystemBrowseResponse)
async def browse_filesystem(path: str = Query("/", description="Path to browse")):
    """
    Browse filesystem to select disk/memory images.

    Args:
        path: Directory path to browse

    Returns:
        FileSystemBrowseResponse with items, current path, and any permission warnings
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
        skipped_count = 0
        permission_warning = None

        # Add parent directory link if not at root
        if path != "/" and str(path_obj.parent) != str(path_obj):
            items.append(
                FileSystemItem(
                    name="..",
                    path=str(path_obj.parent),
                    is_directory=True,
                )
            )

        # List directory contents - collect readable items first
        readable_items = []
        for item in path_obj.iterdir():
            try:
                # Skip macOS metadata files (._* files) and hidden files
                if item.name.startswith("._") or item.name == ".DS_Store":
                    continue
                # Test if we can access this item
                is_dir = item.is_dir()
                readable_items.append((item, is_dir))
            except (PermissionError, OSError) as e:
                # Track permission errors for external volumes
                skipped_count += 1
                if "Operation not permitted" in str(e) and not permission_warning:
                    permission_warning = (
                        "Some files could not be accessed. On macOS, Docker may need "
                        "Full Disk Access permission. Go to System Settings > Privacy & Security > "
                        "Full Disk Access and add Docker Desktop."
                    )
                continue

        # Sort: directories first, then by name
        readable_items.sort(key=lambda x: (not x[1], x[0].name))

        for item, is_dir in readable_items:
            try:
                stat = item.stat()

                # Check if file is a disk/memory image
                is_image = False
                if not is_dir:
                    ext = item.suffix.lower()
                    is_image = ext in [
                        ".e01", ".ex01", ".raw", ".dd", ".img", ".bin",
                        ".vmdk", ".vhd", ".vhdx", ".mem", ".dmp", ".lime"
                    ]

                items.append(
                    FileSystemItem(
                        name=item.name,
                        path=str(item),
                        is_directory=is_dir,
                        size=stat.st_size if not is_dir else None,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        is_image=is_image,
                    )
                )
            except (PermissionError, OSError) as e:
                skipped_count += 1
                if "Operation not permitted" in str(e) and not permission_warning:
                    permission_warning = (
                        "Some files could not be accessed. On macOS, Docker may need "
                        "Full Disk Access permission. Go to System Settings > Privacy & Security > "
                        "Full Disk Access and add Docker Desktop."
                    )
                continue

        return FileSystemBrowseResponse(
            items=items,
            current_path=str(path_obj),
            permission_warning=permission_warning,
            skipped_count=skipped_count,
        )

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
        # Sanitize case number
        case_number = sanitize_case_number(job_request.case_number)

        # Validate and sanitize source paths
        sanitized_source_paths = []
        for path in job_request.source_paths:
            # Sanitize path to prevent directory traversal
            sanitized = sanitize_path(path, settings.allowed_paths)
            if not sanitized:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied to path: {path}",
                )
            if not Path(sanitized).exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Source path does not exist: {path}",
                )
            sanitized_source_paths.append(sanitized)

        # Sanitize destination path if provided
        destination_path = job_request.destination_path
        if destination_path:
            sanitized_dest = sanitize_path(destination_path, settings.allowed_paths)
            if not sanitized_dest:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied to destination path: {destination_path}",
                )
            destination_path = sanitized_dest

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Set destination path - if not specified, use case number as directory name
        if not destination_path and sanitized_source_paths:
            first_source = Path(sanitized_source_paths[0])
            # Create output directory using case number (e.g., /tmp/rivendell/mfttesting/)
            if first_source.is_file():
                destination_path = str(first_source.parent / case_number)
            else:
                destination_path = str(first_source / case_number)

        # Check if destination directory already exists (unless force_overwrite is set)
        if not job_request.options.force_overwrite and destination_path:
            dest_path = Path(destination_path)
            # Only check if it exists as a directory, not as a file
            if dest_path.exists() and dest_path.is_dir():
                raise HTTPException(
                    status_code=400,
                    detail=f"[Errno 17] File exists: '{destination_path}'",
                )

        # Create job
        job = Job(
            id=job_id,
            case_number=case_number,
            source_paths=sanitized_source_paths,
            destination_path=destination_path,
            options=job_request.options,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
        )

        # Save job
        job_storage.save_job(job)

        # Start analysis task and store Celery task ID
        task = start_analysis.delay(job_id)
        job.celery_task_id = task.id
        job_storage.save_job(job)

        return job

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error creating job: {str(e)}")
        logger.error(traceback.format_exc())
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


@app.get("/api/validate/case-id/{case_id}")
async def validate_case_id(case_id: str):
    """
    Check if a case ID already exists.

    Args:
        case_id: Case ID to check

    Returns:
        {"exists": bool, "jobs": [list of matching job IDs]}
    """
    try:
        all_jobs = job_storage.list_jobs()
        matching_jobs = [
            {"id": job.id, "status": job.status, "created_at": job.created_at}
            for job in all_jobs
            if job.case_number == case_id
        ]

        return {
            "exists": len(matching_jobs) > 0,
            "case_id": case_id,
            "jobs": matching_jobs
        }
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
                detail=f"Job already {job.status.value} - can only cancel pending or running jobs",
            )

        # Revoke Celery task if it exists
        if job.celery_task_id:
            from celery import current_app
            current_app.control.revoke(job.celery_task_id, terminate=True, signal='SIGKILL')

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


@app.post("/api/jobs/{job_id}/restart")
async def restart_job(job_id: str):
    """
    Restart a failed or cancelled job.

    Args:
        job_id: Job ID

    Returns:
        Updated job
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status not in [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.COMPLETED]:
            raise HTTPException(
                status_code=400,
                detail="Can only restart failed, cancelled, or completed jobs",
            )

        # Reset job state
        job.status = JobStatus.PENDING
        job.progress = 0
        job.error = None
        job.started_at = None
        job.completed_at = None
        job.log.append(f"[{datetime.now().isoformat()}] Job restarted by user")

        job_storage.save_job(job)

        # Start new analysis task
        task = start_analysis.delay(job_id)
        job.celery_task_id = task.id
        job_storage.save_job(job)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/bulk/cancel")
async def bulk_cancel_jobs(job_ids: list[str]):
    """
    Cancel multiple jobs at once.

    Args:
        job_ids: List of job IDs to cancel

    Returns:
        Results for each job
    """
    try:
        results = []
        from celery import current_app

        for job_id in job_ids:
            job = job_storage.get_job(job_id)

            if not job:
                results.append({"job_id": job_id, "success": False, "error": "Job not found"})
                continue

            if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
                results.append({"job_id": job_id, "success": False, "error": f"Job already {job.status.value}"})
                continue

            # Revoke Celery task if it exists
            if job.celery_task_id:
                current_app.control.revoke(job.celery_task_id, terminate=True, signal='SIGKILL')

            # Update job status
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            job.log.append(f"[{datetime.now().isoformat()}] Job cancelled by user (bulk operation)")

            job_storage.save_job(job)
            results.append({"job_id": job_id, "success": True})

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/bulk/delete")
async def bulk_delete_jobs(job_ids: list[str]):
    """
    Delete multiple completed/failed/cancelled jobs at once.

    Args:
        job_ids: List of job IDs to delete

    Returns:
        Results for each job
    """
    try:
        results = []

        for job_id in job_ids:
            job = job_storage.get_job(job_id)

            if not job:
                results.append({"job_id": job_id, "success": False, "error": "Job not found"})
                continue

            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
                results.append({"job_id": job_id, "success": False, "error": "Cannot delete running job"})
                continue

            job_storage.delete_job(job_id)
            results.append({"job_id": job_id, "success": True})

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/{job_id}/archive")
async def archive_job(job_id: str):
    """
    Archive a completed, failed, or cancelled job.

    Args:
        job_id: Job ID

    Returns:
        Updated job
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            raise HTTPException(
                status_code=400,
                detail="Cannot archive pending or running jobs",
            )

        if job.status == JobStatus.ARCHIVED:
            raise HTTPException(
                status_code=400,
                detail="Job is already archived",
            )

        # Update job status to archived
        job.status = JobStatus.ARCHIVED
        job.log.append(f"[{datetime.now().isoformat()}] Job archived by user")

        job_storage.save_job(job)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/{job_id}/unarchive")
async def unarchive_job(job_id: str):
    """
    Unarchive a job, restoring it to its previous status.

    Args:
        job_id: Job ID

    Returns:
        Updated job
    """
    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status != JobStatus.ARCHIVED:
            raise HTTPException(
                status_code=400,
                detail="Job is not archived",
            )

        # Determine status to restore to based on job state
        if job.error:
            job.status = JobStatus.FAILED
        elif job.completed_at:
            job.status = JobStatus.COMPLETED
        else:
            job.status = JobStatus.CANCELLED

        job.log.append(f"[{datetime.now().isoformat()}] Job unarchived by user")

        job_storage.save_job(job)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/bulk/archive")
async def bulk_archive_jobs(job_ids: list[str]):
    """
    Archive multiple jobs at once.

    Args:
        job_ids: List of job IDs to archive

    Returns:
        Results for each job
    """
    try:
        results = []

        for job_id in job_ids:
            job = job_storage.get_job(job_id)

            if not job:
                results.append({"job_id": job_id, "success": False, "error": "Job not found"})
                continue

            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
                results.append({"job_id": job_id, "success": False, "error": "Cannot archive running job"})
                continue

            if job.status == JobStatus.ARCHIVED:
                results.append({"job_id": job_id, "success": False, "error": "Already archived"})
                continue

            job.status = JobStatus.ARCHIVED
            job.log.append(f"[{datetime.now().isoformat()}] Job archived by user (bulk operation)")
            job_storage.save_job(job)
            results.append({"job_id": job_id, "success": True})

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/bulk/restart")
async def bulk_restart_jobs(job_ids: list[str]):
    """
    Restart multiple failed, cancelled, or completed jobs at once.

    Args:
        job_ids: List of job IDs to restart

    Returns:
        Results for each job
    """
    try:
        results = []

        for job_id in job_ids:
            job = job_storage.get_job(job_id)

            if not job:
                results.append({"job_id": job_id, "success": False, "error": "Job not found"})
                continue

            if job.status not in [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.COMPLETED]:
                results.append({"job_id": job_id, "success": False, "error": "Can only restart failed, cancelled, or completed jobs"})
                continue

            # Reset job state
            job.status = JobStatus.PENDING
            job.progress = 0
            job.error = None
            job.started_at = None
            job.completed_at = None
            job.log.append(f"[{datetime.now().isoformat()}] Job restarted by user (bulk operation)")
            job_storage.save_job(job)

            # Start new analysis task
            task = start_analysis.delay(job_id)
            job.celery_task_id = task.id
            job_storage.save_job(job)

            results.append({"job_id": job_id, "success": True})

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/{job_id}/export-siem")
async def trigger_siem_export(job_id: str):
    """
    Manually trigger SIEM export for a completed job.

    This is useful for jobs that completed before automatic SIEM export was implemented,
    or to re-run SIEM export if it failed.

    Args:
        job_id: Job ID to export

    Returns:
        Export status
    """
    from .tasks import run_siem_export
    from pathlib import Path
    import logging

    try:
        job = job_storage.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Can only export SIEM data for completed jobs")

        # Check if SIEM options are enabled
        opts = job.options
        if not (opts.splunk or opts.elastic or opts.navigator):
            raise HTTPException(status_code=400, detail="Job does not have SIEM export enabled")

        # Get output directory
        if job.destination_path:
            dest_dir = Path(job.destination_path)
        elif job.result and job.result.get("output_directory"):
            dest_dir = Path(job.result["output_directory"])
        else:
            raise HTTPException(status_code=400, detail="Cannot determine output directory for job")

        if not dest_dir.exists():
            raise HTTPException(status_code=400, detail=f"Output directory does not exist: {dest_dir}")

        # Log the manual export trigger
        job.log.append(f"[{datetime.now().isoformat()}] -> Manual SIEM export triggered by user")
        job.log.append(f"[{datetime.now().isoformat()}] -> ")
        job.log.append(f"[{datetime.now().isoformat()}] -> ======== COMMENCING SIEM EXPORT ========")
        job.log.append(f"[{datetime.now().isoformat()}] -> ")
        job_storage.save_job(job)

        # Run SIEM export
        logger = logging.getLogger(__name__)
        run_siem_export(job, dest_dir, logger)

        job.log.append(f"[{datetime.now().isoformat()}] -> ")
        job.log.append(f"[{datetime.now().isoformat()}] -> ======== SIEM EXPORT COMPLETED ========")
        job.log.append(f"[{datetime.now().isoformat()}] -> ")
        job_storage.save_job(job)

        return {"success": True, "message": "SIEM export completed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        if job:
            job.log.append(f"[{datetime.now().isoformat()}] -> ❌ Manual SIEM export failed: {e}")
            job_storage.save_job(job)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/navigator")
async def get_navigator_json(job_id: str):
    """
    Get the MITRE ATT&CK Navigator JSON file for a job.
    """
    from pathlib import Path
    from fastapi.responses import FileResponse

    try:
        job = job_storage.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get output directory
        if job.result and "output_directory" in job.result:
            output_dir = Path(job.result["output_directory"])
        elif job.destination_path:
            output_dir = Path(job.destination_path)
        else:
            raise HTTPException(status_code=404, detail="Job output directory not found")

        # Search for navigator JSON file
        navigator_files = list(output_dir.rglob("*navigator*.json"))

        if not navigator_files:
            raise HTTPException(status_code=404, detail="Navigator JSON file not found")

        # Return the first navigator file found
        nav_file = navigator_files[0]
        return FileResponse(
            path=str(nav_file),
            media_type="application/json",
            filename=nav_file.name
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# File requirements for advanced processing options
FILE_REQUIREMENTS = {
    'keywords': 'keywords.txt',
    'yara': 'yara.yar',
    'collectFiles': 'files.txt',
}

# Default directory for required files (OS-aware)
import platform
if platform.system() == 'Darwin' or platform.system() == 'Linux':
    REQUIRED_FILES_DIR = '/tmp/rivendell'
else:
    REQUIRED_FILES_DIR = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'rivendell')


@app.post("/api/check-required-files")
async def check_required_files(request: dict):
    """
    Check if required files exist in the default location.

    Args:
        request: {"options": ["keywords", "yara", "collectFiles"]}

    Returns:
        {"missing": ["keywords", "yara"], "found": ["collectFiles"]}
    """
    try:
        options = request.get('options', [])
        missing = []
        found = []

        # Ensure directory exists
        os.makedirs(REQUIRED_FILES_DIR, exist_ok=True)

        for opt in options:
            if opt in FILE_REQUIREMENTS:
                filename = FILE_REQUIREMENTS[opt]
                filepath = os.path.join(REQUIRED_FILES_DIR, filename)

                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    found.append(opt)
                else:
                    missing.append(opt)

        return {"missing": missing, "found": found, "directory": REQUIRED_FILES_DIR}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import File, UploadFile

@app.post("/api/upload-required-files")
async def upload_required_files_impl(
    keywords: Optional[UploadFile] = File(None),
    yara: Optional[UploadFile] = File(None),
    collectFiles: Optional[UploadFile] = File(None),
):
    """
    Upload required files for advanced processing options.
    """
    try:
        # Ensure directory exists
        os.makedirs(REQUIRED_FILES_DIR, exist_ok=True)

        uploaded = []

        file_mapping = {
            'keywords': (keywords, 'keywords.txt'),
            'yara': (yara, 'yara.yar'),
            'collectFiles': (collectFiles, 'files.txt'),
        }

        for key, (upload_file, target_filename) in file_mapping.items():
            if upload_file and upload_file.filename:
                content = await upload_file.read()
                target_path = os.path.join(REQUIRED_FILES_DIR, target_filename)

                with open(target_path, 'wb') as f:
                    f.write(content)

                uploaded.append({
                    'option': key,
                    'filename': target_filename,
                    'path': target_path,
                    'size': len(content)
                })

        return {"success": True, "uploaded": uploaded, "directory": REQUIRED_FILES_DIR}

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
