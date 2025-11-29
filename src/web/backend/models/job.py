"""
Job Models

Database models for analysis jobs and results.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class AnalysisOptions(BaseModel):
    """Analysis options configuration."""
    # Main operation modes (mutually exclusive)
    # local: Collect artifacts from disk image and process (default)
    # gandalf: Process pre-collected Gandalf artifacts (no collection)
    local: bool = True  # Default mode - collect from disk image
    gandalf: bool = False  # Alternative mode - process pre-collected artifacts

    # Analysis options
    analysis: bool = False
    extract_iocs: bool = False
    timeline: bool = False
    clamav: bool = False
    memory: bool = False
    memory_timeline: bool = False

    # Advanced processing options
    keywords: bool = False
    keywords_file: Optional[str] = None
    yara: bool = False
    yara_dir: Optional[str] = None
    collectFiles: bool = False
    collectFiles_filter: Optional[str] = None

    # Speed/Quality modes (merged into analysis)
    brisk: bool = False
    quick: bool = False
    super_quick: bool = False

    # Collection options
    vss: bool = False
    symlinks: bool = False
    userprofiles: bool = False

    # Verification options
    nsrl: bool = False
    hash_collected: bool = False
    hash_all: bool = False
    imageinfo: bool = False

    # Output options
    splunk: bool = False
    elastic: bool = False
    navigator: bool = False

    # Post-processing
    delete: bool = False
    archive: bool = False

    # Internal options
    force_overwrite: bool = False


class JobCreate(BaseModel):
    """Job creation request."""
    case_number: str = Field(..., description="Investigation/Case/Incident Number")
    source_paths: list[str] = Field(..., description="List of source paths to disk/memory images")
    destination_path: Optional[str] = Field(None, description="Destination directory for output")
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


class Job(BaseModel):
    """Analysis job."""
    id: str = Field(..., description="Unique job ID")
    case_number: str
    source_paths: list[str]
    destination_path: Optional[str]
    options: AnalysisOptions
    status: JobStatus = JobStatus.PENDING
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    log: list[str] = Field(default_factory=list, description="Job log messages")
    result: Optional[Dict[str, Any]] = Field(None, description="Job results")
    error: Optional[str] = Field(None, description="Error message if failed")
    celery_task_id: Optional[str] = Field(None, description="Celery task ID for job control")
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobUpdate(BaseModel):
    """Job update request."""
    status: Optional[JobStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    log_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JobListResponse(BaseModel):
    """Job list response."""
    jobs: list[Job]
    total: int


class FileSystemItem(BaseModel):
    """File system item (file or directory)."""
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None
    modified: Optional[datetime] = None
    is_image: bool = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
