"""
Celery Tasks

Background tasks for running Elrond analysis.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from celery import Celery
from celery.utils.log import get_task_logger

from .config import settings
from .storage import JobStorage
from .models.job import JobStatus

# Initialize Celery
celery_app = Celery(
    "elrond",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

logger = get_task_logger(__name__)
job_storage = JobStorage()


@celery_app.task(bind=True)
def start_analysis(self, job_id: str):
    """
    Start Elrond analysis task.

    Args:
        job_id: Job ID
    """
    job = job_storage.get_job(job_id)

    if not job:
        logger.error(f"Job {job_id} not found")
        return

    try:
        # Update job status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        job.log.append(f"[{datetime.now().isoformat()}] Starting analysis")
        job_storage.save_job(job)

        # Build elrond command
        cmd = build_elrond_command(job)

        logger.info(f"Running command: {' '.join(cmd)}")
        job.log.append(f"[{datetime.now().isoformat()}] Command: {' '.join(cmd)}")
        job_storage.save_job(job)

        # Set destination directory
        dest_dir = job.destination_path or str(settings.output_dir / job.case_number)
        Path(dest_dir).mkdir(parents=True, exist_ok=True)

        # Run elrond
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=dest_dir,
        )

        # Monitor progress
        progress_count = 0
        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if line:
                # Update log
                job.log.append(f"[{datetime.now().isoformat()}] {line}")

                # Update progress (simple estimation)
                progress_count += 1
                job.progress = min(progress_count % 100, 99)

                # Save periodically (every 10 lines)
                if progress_count % 10 == 0:
                    job_storage.save_job(job)

                logger.info(line)

        # Wait for completion
        return_code = process.wait()

        if return_code == 0:
            # Success
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.log.append(f"[{datetime.now().isoformat()}] Analysis completed successfully")
            job.result = {
                "output_directory": dest_dir,
                "return_code": return_code,
            }
        else:
            # Failed
            job.status = JobStatus.FAILED
            job.error = f"Process exited with code {return_code}"
            job.log.append(f"[{datetime.now().isoformat()}] Analysis failed: {job.error}")

    except Exception as e:
        logger.exception(f"Error running analysis for job {job_id}")
        job.status = JobStatus.FAILED
        job.error = str(e)
        job.log.append(f"[{datetime.now().isoformat()}] Error: {str(e)}")

    finally:
        job.completed_at = datetime.now()
        job_storage.save_job(job)


def build_elrond_command(job):
    """
    Build elrond command from job options.

    Args:
        job: Job object

    Returns:
        Command list
    """
    cmd = [sys.executable, "-m", "elrond"]

    # Case number
    cmd.append(job.case_number)

    # Source paths
    cmd.extend(job.source_paths)

    # Destination path
    if job.destination_path:
        cmd.append(job.destination_path)

    opts = job.options

    # Main operation modes
    if opts.collect:
        cmd.extend(["-C", "--Collect"])
    if opts.gandalf:
        cmd.extend(["-G", "--Gandalf"])
    if opts.reorganise:
        cmd.extend(["-R", "--Reorganise"])
    if opts.process:
        cmd.extend(["-P", "--Process"])

    # Analysis options
    if opts.analysis:
        cmd.extend(["-A", "--Analysis"])
    if opts.extract_iocs:
        cmd.extend(["-I", "--extractIocs"])
    if opts.keywords_file:
        cmd.extend(["-K", "--Keywords", opts.keywords_file])
    if opts.yara_dir:
        cmd.extend(["-Y", "--Yara", opts.yara_dir])

    # Collection options
    if opts.collect_files:
        if opts.collect_files_filter:
            cmd.extend(["-F", "--collectFiles", opts.collect_files_filter])
        else:
            cmd.extend(["-F", "--collectFiles"])
    if opts.vss:
        cmd.extend(["-c", "--vss"])
    if opts.symlinks:
        cmd.extend(["-s", "--symlinks"])
    if opts.userprofiles:
        cmd.extend(["-U", "--Userprofiles"])

    # Processing options
    if opts.timeline:
        cmd.extend(["-T", "--Timeline"])
    if opts.memory:
        cmd.extend(["-M", "--Memory"])
    if opts.memory_timeline:
        cmd.extend(["-t", "--memorytimeline"])
    if opts.imageinfo:
        cmd.extend(["-i", "--imageinfo"])

    # Speed/Quality modes
    if opts.auto:
        cmd.extend(["-a", "--auto"])
    if opts.brisk:
        cmd.extend(["-B", "--Brisk"])
    if opts.exhaustive:
        cmd.extend(["-X", "--eXhaustive"])
    if opts.quick:
        cmd.extend(["-q", "--quick"])
    if opts.super_quick:
        cmd.extend(["-Q", "--superQuick"])

    # Output options
    if opts.splunk:
        cmd.extend(["-S", "--Splunk"])
    if opts.elastic:
        cmd.extend(["-E", "--Elastic"])
    if opts.navigator:
        cmd.extend(["-N", "--Navigator"])

    # Security scanning
    if opts.clamav:
        cmd.extend(["-V", "--clamaV"])

    # Hash comparison
    if opts.nsrl:
        cmd.extend(["-n", "--nsrl"])
    if opts.metacollected:
        cmd.extend(["-m", "--metacollected"])

    # Post-processing
    if opts.delete:
        cmd.extend(["-D", "--Delete"])
    if opts.archive:
        cmd.extend(["-Z", "--Ziparchive"])

    # Mount options
    if opts.unmount:
        cmd.extend(["-u", "--unmount"])

    # Display
    if opts.lotr:
        cmd.extend(["-l", "--lotr"])

    return cmd
