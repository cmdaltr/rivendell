"""
Celery Tasks - Dockerized Version

Background tasks for running Elrond analysis in Docker containers.
This version runs Elrond directly in the same container environment.
"""

import subprocess
import sys
import os
import traceback
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
    Start Elrond analysis task in dockerized environment.

    Runs the full forensics engine directly in the container.

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
        job.log.append(f"[{datetime.now().isoformat()}] Starting forensic analysis")
        job_storage.save_job(job)

        # Build elrond command
        cmd = build_elrond_command(job)

        logger.info(f"Running command: {' '.join(cmd)}")
        job.log.append(f"[{datetime.now().isoformat()}] Command: {' '.join(cmd)}")
        job_storage.save_job(job)

        # Set destination directory - must match what's passed to elrond command
        dest_dir = job.destination_path if job.destination_path else str(Path(settings.output_dir) / job.case_number)

        # Check if force_overwrite is set and directory exists
        if getattr(job.options, 'force_overwrite', False):
            if Path(dest_dir).exists():
                import shutil
                logger.info(f"Force overwrite enabled, removing existing directory: {dest_dir}")
                job.log.append(f"[{datetime.now().isoformat()}] Removing existing directory: {dest_dir}")
                try:
                    shutil.rmtree(dest_dir)
                    logger.info(f"Successfully removed directory: {dest_dir}")
                    job.log.append(f"[{datetime.now().isoformat()}] Successfully removed directory")
                except Exception as e:
                    logger.error(f"Error removing directory: {e}")
                    job.log.append(f"[{datetime.now().isoformat()}] Error removing directory: {e}")
                job_storage.save_job(job)

        # Create the output directory if it doesn't exist
        Path(dest_dir).mkdir(parents=True, exist_ok=True)

        # Run elrond directly in container
        # Since we're already in the forensics container, we can run it directly
        elrond_path = os.environ.get('ELROND_HOME', '/opt/elrond')
        elrond_script = Path(elrond_path) / 'elrond.py'

        if not elrond_script.exists():
            # Elrond not installed - create placeholder error
            raise FileNotFoundError(
                f"Elrond script not found at {elrond_script}. "
                f"Please install Elrond or set ELROND_HOME environment variable to point to Elrond installation."
            )

        # Prepend python3 and elrond script path to command
        cmd.insert(0, str(elrond_script))
        cmd.insert(0, 'python3')

        logger.info(f"Executing: {' '.join(cmd)}")

        # Run elrond with proper environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{elrond_path}:{env.get('PYTHONPATH', '')}"
        env['ELROND_HOME'] = elrond_path
        env['ELROND_OUTPUT'] = str(settings.output_dir)
        env['ELROND_NONINTERACTIVE'] = '1'  # Signal non-interactive mode

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=dest_dir,
            env=env,
        )

        # Monitor progress
        progress_count = 0
        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if line:
                # Update log
                log_entry = f"[{datetime.now().isoformat()}] {line}"
                job.log.append(log_entry)

                # Update progress (simple estimation based on output)
                progress_count += 1

                # Estimate progress based on keywords
                if any(keyword in line.lower() for keyword in ['collecting', 'mounting']):
                    job.progress = min(progress_count, 20)
                elif any(keyword in line.lower() for keyword in ['processing', 'parsing']):
                    job.progress = min(20 + progress_count, 60)
                elif any(keyword in line.lower() for keyword in ['analyzing', 'extracting']):
                    job.progress = min(60 + progress_count, 90)
                elif 'complete' in line.lower() or 'finished' in line.lower():
                    job.progress = 95

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

            # Collect results information
            result_info = {
                "output_directory": dest_dir,
                "return_code": return_code,
                "analysis_duration": str(datetime.now() - job.started_at),
            }

            # Check for generated files
            output_path = Path(dest_dir)
            if output_path.exists():
                result_info["output_files"] = len(list(output_path.rglob("*")))
                result_info["output_size"] = sum(f.stat().st_size for f in output_path.rglob("*") if f.is_file())

            job.result = result_info

        else:
            # Failed
            job.status = JobStatus.FAILED
            job.error = f"Process exited with code {return_code}"
            job.log.append(f"[{datetime.now().isoformat()}] Analysis failed: {job.error}")

    except Exception as e:
        logger.exception(f"Error running analysis for job {job_id}")
        job.status = JobStatus.FAILED
        job.error = str(e)

        # Capture full traceback in the log
        tb_str = traceback.format_exc()
        job.log.append(f"[{datetime.now().isoformat()}] ========== ERROR ==========")
        job.log.append(f"[{datetime.now().isoformat()}] {str(e)}")
        job.log.append(f"[{datetime.now().isoformat()}] Traceback:")
        for line in tb_str.split('\n'):
            if line.strip():
                job.log.append(f"[{datetime.now().isoformat()}] {line}")

    finally:
        job.completed_at = datetime.now()
        job_storage.save_job(job)


def build_elrond_command(job):
    """
    Build elrond command from job options.

    Args:
        job: Job object

    Returns:
        Command list for subprocess
    """
    cmd = []

    # Case number
    cmd.append(job.case_number)

    # Source paths
    cmd.extend(job.source_paths)

    # Destination path
    if job.destination_path:
        cmd.append(job.destination_path)
    else:
        # Use default output directory
        cmd.append(str(Path(settings.output_dir) / job.case_number))

    opts = job.options

    # Main operation modes
    if opts.collect:
        cmd.append("--Collect")
    if opts.gandalf:
        cmd.append("--Gandalf")
    if opts.process:
        cmd.append("--Process")

    # Analysis options
    if opts.analysis:
        cmd.append("--Analysis")
    if opts.extract_iocs:
        cmd.append("--extractIocs")
    if opts.keywords_file:
        cmd.extend(["--Keywords", opts.keywords_file])
    if opts.yara_dir:
        cmd.extend(["--Yara", opts.yara_dir])

    # Collection options
    if opts.collect_files:
        if opts.collect_files_filter:
            cmd.extend(["--collectFiles", opts.collect_files_filter])
        else:
            cmd.append("--collectFiles")
    if opts.vss:
        cmd.append("--vss")
    if opts.symlinks:
        cmd.append("--symlinks")
    if opts.userprofiles:
        cmd.append("--Userprofiles")

    # Processing options
    if opts.timeline:
        cmd.append("--Timeline")
    if opts.memory:
        cmd.append("--Memory")
    if opts.memory_timeline:
        cmd.append("--memorytimeline")
    if opts.imageinfo:
        cmd.append("--imageinfo")

    # Speed/Quality modes
    if opts.brisk:
        cmd.append("--Brisk")
    if opts.quick:
        cmd.append("--quick")
    if opts.super_quick:
        cmd.append("--superQuick")

    # Output options
    if opts.splunk:
        cmd.append("--Splunk")
    if opts.elastic:
        cmd.append("--Elastic")
    # Navigator requires Splunk or Elastic
    if opts.navigator and (opts.splunk or opts.elastic):
        cmd.append("--Navigator")

    # Security scanning
    if opts.clamav:
        cmd.append("--clamaV")

    # Hash comparison
    if opts.nsrl:
        cmd.append("--nsrl")
    if opts.metacollected:
        cmd.append("--metacollected")

    # Post-processing
    if opts.delete:
        cmd.append("--Delete")
    if opts.archive:
        cmd.append("--Ziparchive")

    return cmd
