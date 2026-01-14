"""
Job Storage

PostgreSQL-based storage for jobs using SQLAlchemy.
"""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

try:
    from .models.job import Job, JobStatus
    from .config import settings
except ImportError:
    # Fallback for standalone module execution (Celery worker)
    from models.job import Job, JobStatus
    from config import settings


# SQLAlchemy Base
Base = declarative_base()


class JobModel(Base):
    """SQLAlchemy model for jobs table."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    case_number = Column(String, nullable=False, index=True)
    source_paths = Column(JSON, nullable=False)
    destination_path = Column(String, nullable=True)
    options = Column(JSON, nullable=False)
    status = Column(String, nullable=False, index=True)
    progress = Column(Integer, default=0)
    log = Column(JSON, default=list)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    celery_task_id = Column(String, nullable=True)
    pending_action = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class JobStorage:
    """PostgreSQL-based job storage using SQLAlchemy."""

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize job storage.

        Args:
            database_url: PostgreSQL connection URL (defaults to DATABASE_URL env var)
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://rivendell:rivendell@localhost:5432/rivendell"
        )

        # Create engine with connection pooling disabled for file-based compatibility
        # In production, you might want to enable pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=NullPool,
            echo=False  # Set to True for SQL debugging
        )

        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def _job_model_to_pydantic(self, job_model: JobModel) -> Job:
        """Convert SQLAlchemy model to Pydantic model."""
        return Job(
            id=job_model.id,
            case_number=job_model.case_number,
            source_paths=job_model.source_paths,
            destination_path=job_model.destination_path,
            options=job_model.options,
            status=JobStatus(job_model.status),
            progress=job_model.progress,
            log=job_model.log or [],
            result=job_model.result,
            error=job_model.error,
            celery_task_id=job_model.celery_task_id,
            pending_action=job_model.pending_action,
            created_at=job_model.created_at,
            started_at=job_model.started_at,
            completed_at=job_model.completed_at,
        )

    def save_job(self, job: Job) -> None:
        """
        Save job to storage.

        Args:
            job: Job to save
        """
        session = self.Session()
        try:
            # Check if job exists
            existing = session.query(JobModel).filter_by(id=job.id).first()

            if existing:
                # Update existing job
                existing.case_number = job.case_number
                existing.source_paths = job.source_paths
                existing.destination_path = job.destination_path
                existing.options = job.options.dict()
                existing.status = job.status.value
                existing.progress = job.progress
                existing.log = job.log
                existing.result = job.result
                existing.error = job.error
                existing.celery_task_id = job.celery_task_id
                existing.pending_action = job.pending_action.dict() if job.pending_action else None
                existing.created_at = job.created_at
                existing.started_at = job.started_at
                existing.completed_at = job.completed_at
            else:
                # Create new job
                job_model = JobModel(
                    id=job.id,
                    case_number=job.case_number,
                    source_paths=job.source_paths,
                    destination_path=job.destination_path,
                    options=job.options.dict(),
                    status=job.status.value,
                    progress=job.progress,
                    log=job.log,
                    result=job.result,
                    error=job.error,
                    celery_task_id=job.celery_task_id,
                    pending_action=job.pending_action.dict() if job.pending_action else None,
                    created_at=job.created_at,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                )
                session.add(job_model)

            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job from storage.

        Args:
            job_id: Job ID

        Returns:
            Job if found, None otherwise
        """
        session = self.Session()
        try:
            job_model = session.query(JobModel).filter_by(id=job_id).first()

            if not job_model:
                return None

            return self._job_model_to_pydantic(job_model)
        finally:
            session.close()

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
        session = self.Session()
        try:
            query = session.query(JobModel).order_by(JobModel.created_at.desc())

            if status:
                query = query.filter_by(status=status.value)

            job_models = query.offset(offset).limit(limit).all()

            return [self._job_model_to_pydantic(jm) for jm in job_models]
        finally:
            session.close()

    def count_jobs(self, status: Optional[JobStatus] = None) -> int:
        """
        Count jobs in storage.

        Args:
            status: Filter by job status

        Returns:
            Number of jobs
        """
        session = self.Session()
        try:
            query = session.query(JobModel)

            if status:
                query = query.filter_by(status=status.value)

            return query.count()
        finally:
            session.close()

    def delete_job(self, job_id: str) -> None:
        """
        Delete job from storage.

        Args:
            job_id: Job ID
        """
        session = self.Session()
        try:
            job_model = session.query(JobModel).filter_by(id=job_id).first()

            if job_model:
                session.delete(job_model)
                session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
