"""
Celery Tasks - Dockerized Version

Background tasks for running Elrond analysis in Docker containers.
This version runs Elrond directly in the same container environment.
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path

from celery import Celery
from celery.utils.log import get_task_logger

from config import settings
from storage import JobStorage
from models.job import JobStatus

# Initialize Celery
celery_app = Celery(
    "elrond",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

logger = get_task_logger(__name__)
job_storage = JobStorage()


def translate_path_for_worker(path_str: str) -> str:
    """
    Translate paths from backend container perspective to celery-worker perspective.

    Both containers mount:
      - elrond_uploads volume -> /tmp/elrond/uploads (SAME in both containers)
      - /tmp/rivendell (host) -> /tmp/elrond/output (worker) or /host/tmp/rivendell (backend)

    Args:
        path_str: Path from backend perspective

    Returns:
        Path translated for celery worker
    """
    path_str = str(path_str)

    # Paths in /tmp/elrond/uploads are the SAME in both containers (shared volume)
    if path_str.startswith("/tmp/elrond/uploads/"):
        return path_str

    # Backend uses /host/tmp/rivendell for output, worker uses /tmp/elrond/output
    if path_str.startswith("/host/tmp/rivendell"):
        return path_str.replace("/host/tmp/rivendell", "/tmp/elrond/output")

    # Backend uses /tmp/elrond/output, worker uses same
    if path_str.startswith("/tmp/elrond/output"):
        return path_str

    # Default: return as-is
    return path_str


def _resolve_destination(job) -> Path:
    """
    Resolve the destination directory using the same logic as job creation.
    Uses case number as the output directory name instead of image name.
    """
    if job.destination_path:
        return Path(job.destination_path)

    if job.source_paths:
        first_source = Path(job.source_paths[0])
        if first_source.is_file():
            # Use case number instead of image name for output directory
            return first_source.parent / job.case_number
        return first_source / job.case_number

    return Path(settings.output_dir) / job.case_number


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
        job.log.append(f"[{datetime.now().isoformat()}] -> Starting rivendell...")
        job_storage.save_job(job)

        # Build elrond command
        cmd = build_elrond_command(job)

        logger.info(f"Running command: {' '.join(cmd)}")
        job.log.append(f"[{datetime.now().isoformat()}] -> Command: {' '.join(cmd)}")
        job_storage.save_job(job)

        # Set destination directory - must translate to worker perspective
        dest_dir_backend = _resolve_destination(job)
        dest_dir_str = translate_path_for_worker(str(dest_dir_backend))
        dest_dir = Path(dest_dir_str)

        # Check if force_overwrite is set and directory exists
        if getattr(job.options, "force_overwrite", False):
            if dest_dir.exists():
                import shutil

                logger.info(f"Force overwrite enabled, removing existing directory: {dest_dir_str}")

                job.log.append(
                    f"[{datetime.now().isoformat()}] -> Removing existing directory: {dest_dir_str} - stand by..."
                )
                job_storage.save_job(job)

                # Use rm -rf with progress monitoring for large directories
                start_time = datetime.now()
                try:
                    import time

                    # Start rm -rf in background
                    rm_process = subprocess.Popen(
                        ["rm", "-rf", dest_dir_str],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

                    # Monitor with periodic updates every 10 seconds
                    last_update = datetime.now()
                    while rm_process.poll() is None:
                        time.sleep(1)
                        elapsed = (datetime.now() - start_time).total_seconds()

                        # Update every 10 seconds
                        if (datetime.now() - last_update).total_seconds() >= 10:
                            job.log.append(
                                f"[{datetime.now().isoformat()}] -> Still removing directory... ({int(elapsed)}s elapsed)"
                            )
                            job_storage.save_job(job)
                            last_update = datetime.now()

                        # Timeout after 5 minutes
                        if elapsed > 300:
                            rm_process.kill()
                            raise subprocess.TimeoutExpired(
                                cmd=["rm", "-rf", dest_dir_str], timeout=300
                            )

                    # Check exit code
                    if rm_process.returncode != 0:
                        raise subprocess.CalledProcessError(
                            rm_process.returncode, ["rm", "-rf", dest_dir_str]
                        )

                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Successfully removed directory: {dest_dir_str} in {elapsed:.1f}s")
                    job.log.append(
                        f"[{datetime.now().isoformat()}] -> Successfully removed directory in {elapsed:.1f}s"
                    )
                except subprocess.TimeoutExpired:
                    logger.error(f"Timeout removing directory: {dest_dir_str}")
                    job.log.append(
                        f"[{datetime.now().isoformat()}] -> Timeout removing directory (took more than 5 minutes)"
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error removing directory (exit code {e.returncode})")
                    job.log.append(f"[{datetime.now().isoformat()}] -> Error removing directory")
                except Exception as e:
                    logger.error(f"Error removing directory: {e}")
                    job.log.append(
                        f"[{datetime.now().isoformat()}] -> Error removing directory: {e}"
                    )
                job_storage.save_job(job)

        # Create the output directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Run elrond directly in container
        # Since we're already in the forensics container, we can run it directly
        elrond_path = os.environ.get("ELROND_HOME", "/opt/elrond")
        elrond_script = Path(elrond_path) / "elrond.py"

        if not elrond_script.exists():
            # Elrond not installed - create placeholder error
            raise FileNotFoundError(
                f"Elrond script not found at {elrond_script}. "
                f"Please install Elrond or set ELROND_HOME environment variable to point to Elrond installation."
            )

        # Prepend python3 and elrond script path to command
        cmd.insert(0, str(elrond_script))
        cmd.insert(0, "python3")

        logger.info(f"Executing: {' '.join(cmd)}")

        # Run elrond with proper environment
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{elrond_path}:{env.get('PYTHONPATH', '')}"
        env["ELROND_HOME"] = elrond_path
        env["ELROND_OUTPUT"] = str(settings.output_dir)
        env["ELROND_NONINTERACTIVE"] = "1"  # Signal non-interactive mode

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffering to get output in real-time
            cwd=dest_dir_str,
            env=env,
        )

        # Monitor progress
        progress_count = 0
        last_log_message = None  # Track last message for deduplication
        seen_phases = set()  # Track seen phase transitions to prevent duplicates
        seen_filepaths = set()  # Track seen filepaths to prevent duplicates
        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if line:
                # Strip ANSI color codes
                line = re.sub(r"\x1b\[[0-9;]*m", "", line)

                # Filter: Only log lines containing ' -> ' or important keywords (audit log format)
                # This filters out verbose output and only shows important messages
                important_keywords = [
                    "skipping",
                    "warning",
                    "error",
                    "failed",
                    "completed",
                    "commencing",
                ]
                has_arrow = " -> " in line
                has_important_keyword = any(
                    keyword in line.lower() for keyword in important_keywords
                )

                if not has_arrow and not has_important_keyword:
                    continue

                # Clean up duplicate slashes in file paths (e.g., //$ -> /$)
                line = re.sub(r"/+", "/", line)

                # Fix timestamp format: convert "-> YYYY-MM-DD HH:MM:SS.ffffff -> message" to "[YYYY-MM-DD HH:MM:SS.ffffff] -> message"
                timestamp_pattern = (
                    r"^->\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+->\s+(.+)$"
                )
                timestamp_match = re.match(timestamp_pattern, line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                    message = timestamp_match.group(2)
                    line = f"[{timestamp}] -> {message}"

                # Format phase headers (Commencing/Completed) with visual separators BEFORE deduplication
                original_line = line
                is_phase_message = False
                phase_key = None  # Used for deduplicating phase messages
                if "commencing" in line.lower() and "phase" in line.lower():
                    # Extract the phase name (e.g., "Collection", "Processing", "Analysis")
                    phase_match = re.search(r"commencing\s+(.*?)\s*phase", line, re.IGNORECASE)
                    if phase_match:
                        phase_name = phase_match.group(1).strip().title()
                        # Simplify "Att&Ck® Navigator" to just "Navigator"
                        phase_name = re.sub(r"Att&Ck®\s*", "", phase_name, flags=re.IGNORECASE)
                        phase_key = f"commencing_{phase_name.lower()}"
                        line = f"========== Commencing {phase_name} Phase =========="
                        is_phase_message = True
                elif "completed" in line.lower() and "phase" in line.lower():
                    # Extract just the phase name, ignoring "for 'image'" suffixes
                    # Match: "Completed X Phase" or "Completed X Phase for 'image'"
                    phase_match = re.search(r"completed\s+(.*?)\s*phase", line, re.IGNORECASE)
                    if phase_match:
                        phase_name = phase_match.group(1).strip().title()
                        # Simplify "Att&Ck® Navigator" to just "Navigator"
                        phase_name = re.sub(r"Att&Ck®\s*", "", phase_name, flags=re.IGNORECASE)
                        phase_key = f"completed_{phase_name.lower()}"
                        line = f"========== Completed {phase_name} Phase =========="
                        is_phase_message = True

                # Deduplicate phase messages: only show each phase transition once
                if is_phase_message and phase_key:
                    if phase_key in seen_phases:
                        continue  # Skip duplicate phase message
                    seen_phases.add(phase_key)

                # Deduplicate: Skip if this exact filepath was already logged
                # Normalize message for comparison (remove extra quotes and whitespace)
                normalized_current = re.sub(r"'{2,}", "'", original_line).strip()

                # Extract filepath from the message for deduplication
                # Matches patterns like: '/path/to/file.ext' or "/path/to/file.ext"
                filepath_match = re.search(r"['\"]?(/[^'\"]+)['\"]?", normalized_current)
                if filepath_match:
                    filepath = filepath_match.group(1).lower()
                    if filepath in seen_filepaths:
                        continue  # Skip duplicate filepath message
                    seen_filepaths.add(filepath)

                last_log_message = original_line

                # Update log - only add timestamp if line doesn't already have one
                # Check if line starts with a timestamp (YYYY-MM-DD format or contains ' -> ')
                if re.match(r"^\d{4}-\d{2}-\d{2}", line) or " -> " in line:
                    # Line already has timestamp, don't add another
                    job.log.append(line)
                else:
                    # No timestamp, add one
                    log_entry = f"[{datetime.now().isoformat()}] {line}"
                    job.log.append(log_entry)

                # Update progress based on phase transitions (more accurate than counting)
                progress_count += 1
                line_lower = line.lower()

                # Phase-based progress: use phase transitions for accurate progress
                new_progress = job.progress  # Start with current progress

                if "commencing collection phase" in line_lower:
                    new_progress = 10
                elif "completed collection phase" in line_lower:
                    new_progress = 35
                elif "scanning for artefacts" in line_lower:
                    new_progress = 40
                elif "commencing processing phase" in line_lower:
                    new_progress = 45
                elif "completed processing phase" in line_lower:
                    new_progress = 70
                elif "commencing analysis phase" in line_lower:
                    new_progress = 75
                elif "completed analysis phase" in line_lower:
                    new_progress = 90
                elif any(
                    keyword in line_lower
                    for keyword in ["splunk phase", "elastic phase", "navigator phase"]
                ):
                    new_progress = 92
                elif "rivendell completed" in line_lower or "analysis finished" in line_lower:
                    new_progress = 95
                # Fallback: keyword-based progress for intermediate steps
                elif any(keyword in line_lower for keyword in ["collecting", "mounting"]):
                    new_progress = max(new_progress, min(10 + progress_count // 5, 30))
                elif any(keyword in line_lower for keyword in ["processing", "parsing"]):
                    new_progress = max(new_progress, min(45 + progress_count // 10, 65))
                elif any(keyword in line_lower for keyword in ["analyzing"]):
                    new_progress = max(new_progress, min(75 + progress_count // 10, 88))

                # Only update if progress increases (never go backwards)
                job.progress = max(job.progress, new_progress)

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
            job.log.append(
                f"[{datetime.now().isoformat().replace('T', ' ')}] -> rivendell completed successfully"
            )

            # Collect results information
            result_info = {
                "output_directory": dest_dir_str,
                "return_code": return_code,
                "analysis_duration": str(datetime.now() - job.started_at),
            }

            # Check for generated files
            output_path = dest_dir
            if output_path.exists():
                result_info["output_files"] = len(list(output_path.rglob("*")))
                result_info["output_size"] = sum(
                    f.stat().st_size for f in output_path.rglob("*") if f.is_file()
                )

            job.result = result_info

        else:
            # Failed
            job.status = JobStatus.FAILED
            job.error = f"Process exited with code {return_code}"
            job.log.append(f"[{datetime.now().isoformat()}] -> Analysis failed: {job.error}")

    except Exception as e:
        logger.exception(f"Error running analysis for job {job_id}")
        job.status = JobStatus.FAILED
        job.error = str(e)
        job.log.append(f"[{datetime.now().isoformat()}] -> Error: {str(e)}")

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

    # Source paths (translate from backend to worker perspective)
    translated_sources = [translate_path_for_worker(p) for p in job.source_paths]
    cmd.extend(translated_sources)

    # Destination path (mirror job creation logic and translate to worker perspective)
    dest_path = str(_resolve_destination(job))
    translated_dest = translate_path_for_worker(dest_path)
    cmd.append(translated_dest)

    opts = job.options

    # Primary mode flags
    # Process is ALWAYS invoked
    cmd.append("--Process")

    # Collection mode (mutually exclusive)
    if opts.gandalf:
        # Gandalf mode: process pre-collected artifacts (no collection)
        cmd.append("--Gandalf")
    else:
        # Default/Local mode: collect from disk image
        cmd.append("--Collect")

    # Analysis options
    analysis_requested = getattr(opts, "analysis", False)
    magic_bytes_requested = analysis_requested or getattr(opts, "magic_bytes", False)

    if analysis_requested:
        cmd.append("--Analysis")
    if magic_bytes_requested:
        cmd.append("--magicBytes")
    if opts.extract_iocs:
        cmd.append("--extractIocs")
    if opts.keywords_file:
        cmd.extend(["--Keywords", opts.keywords_file])
    if opts.yara_dir:
        cmd.extend(["--Yara", opts.yara_dir])

    # Collection options
    if opts.collectFiles:
        if opts.collectFiles_filter:
            cmd.extend(["--collectFiles", opts.collectFiles_filter])
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

    # Output options (MUST come before Brisk since Brisk invokes Navigator which requires Splunk/Elastic)
    if opts.splunk:
        cmd.append("--Splunk")
    if opts.elastic:
        cmd.append("--Elastic")
    # Navigator requires Splunk or Elastic
    if opts.navigator and (opts.splunk or opts.elastic):
        cmd.append("--Navigator")

    # Speed/Quality modes
    if opts.brisk:
        cmd.append("--Brisk")
    if opts.quick:
        cmd.append("--quick")
    if opts.super_quick:
        cmd.append("--superQuick")

    # Security scanning
    if opts.clamav:
        cmd.append("--clamaV")

    # Hash comparison
    if opts.nsrl:
        cmd.append("--nsrl")
    if opts.hash_collected:
        cmd.append("--hashCollected")

    # Post-processing
    if opts.delete:
        cmd.append("--Delete")
    if opts.archive:
        cmd.append("--Ziparchive")

    return cmd
