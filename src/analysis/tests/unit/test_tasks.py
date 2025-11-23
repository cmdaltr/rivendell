"""
Unit Tests for Celery Tasks

Tests the background task execution system.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
from datetime import datetime

from web.backend.tasks import start_analysis, build_elrond_command
from web.backend.models.job import Job, JobStatus, AnalysisOptions


@pytest.mark.unit
class TestBuildElrondCommand:
    """Test elrond command building."""

    def test_basic_command(self, sample_job_data):
        """Test building basic command."""
        job = Job(**sample_job_data)

        cmd = build_elrond_command(job)

        assert cmd[0].endswith("python") or cmd[0].endswith("python3")
        assert "-m" in cmd
        assert "elrond" in cmd
        assert job.case_number in cmd

    def test_command_with_collect(self, sample_job_data):
        """Test command with collect flag."""
        job_data = {**sample_job_data}
        job_data["options"]["collect"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-C" in cmd or "--Collect" in cmd

    def test_command_with_process(self, sample_job_data):
        """Test command with process flag."""
        job_data = {**sample_job_data}
        job_data["options"]["process"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-P" in cmd or "--Process" in cmd

    def test_command_with_analysis(self, sample_job_data):
        """Test command with analysis flag."""
        job_data = {**sample_job_data}
        job_data["options"]["analysis"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-A" in cmd or "--Analysis" in cmd

    def test_command_with_quick_mode(self, sample_job_data):
        """Test command with quick mode."""
        job_data = {**sample_job_data}
        job_data["options"]["quick"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-q" in cmd or "--quick" in cmd

    def test_command_with_brisk_mode(self, sample_job_data):
        """Test command with brisk mode."""
        job_data = {**sample_job_data}
        job_data["options"]["brisk"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-B" in cmd or "--Brisk" in cmd

    def test_command_with_exhaustive_mode(self, sample_job_data):
        """Test command with exhaustive mode."""
        job_data = {**sample_job_data}
        job_data["options"]["exhaustive"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-X" in cmd or "--eXhaustive" in cmd

    def test_command_with_timeline(self, sample_job_data):
        """Test command with timeline."""
        job_data = {**sample_job_data}
        job_data["options"]["timeline"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-T" in cmd or "--Timeline" in cmd

    def test_command_with_memory(self, sample_job_data):
        """Test command with memory analysis."""
        job_data = {**sample_job_data}
        job_data["options"]["memory"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-M" in cmd or "--Memory" in cmd

    def test_command_with_splunk(self, sample_job_data):
        """Test command with Splunk output."""
        job_data = {**sample_job_data}
        job_data["options"]["splunk"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-S" in cmd or "--Splunk" in cmd

    def test_command_with_elastic(self, sample_job_data):
        """Test command with Elastic output."""
        job_data = {**sample_job_data}
        job_data["options"]["elastic"] = True
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-E" in cmd or "--Elastic" in cmd

    def test_command_with_keywords(self, sample_job_data):
        """Test command with keywords file."""
        job_data = {**sample_job_data}
        job_data["options"]["keywords_file"] = "/path/to/keywords.txt"
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-K" in cmd or "--Keywords" in cmd
        assert "/path/to/keywords.txt" in cmd

    def test_command_with_yara(self, sample_job_data):
        """Test command with YARA rules."""
        job_data = {**sample_job_data}
        job_data["options"]["yara_dir"] = "/path/to/yara"
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "-Y" in cmd or "--Yara" in cmd
        assert "/path/to/yara" in cmd

    def test_command_with_multiple_sources(self, sample_job_data):
        """Test command with multiple source paths."""
        job_data = {**sample_job_data}
        job_data["source_paths"] = ["/path/1.E01", "/path/2.E01"]
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "/path/1.E01" in cmd
        assert "/path/2.E01" in cmd

    def test_command_with_destination(self, sample_job_data):
        """Test command with destination path."""
        job_data = {**sample_job_data}
        job_data["destination_path"] = "/output/case-001"
        job = Job(**job_data)

        cmd = build_elrond_command(job)

        assert "/output/case-001" in cmd


@pytest.mark.unit
class TestStartAnalysisTask:
    """Test start_analysis Celery task."""

    @patch("web.backend.tasks.subprocess.Popen")
    @patch("web.backend.tasks.job_storage")
    def test_start_analysis_success(self, mock_storage, mock_popen, sample_job_data):
        """Test successful analysis execution."""
        job = Job(**sample_job_data)
        mock_storage.get_job.return_value = job

        # Mock process
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            "Starting collection...\n",
            "Processing files...\n",
            "Complete!\n",
            ""  # End of output
        ]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Run task
        start_analysis(None, job.id)

        # Verify job was updated
        assert mock_storage.save_job.called
        saved_job = mock_storage.save_job.call_args[0][0]
        assert saved_job.status == JobStatus.COMPLETED
        assert saved_job.progress == 100

    @patch("web.backend.tasks.subprocess.Popen")
    @patch("web.backend.tasks.job_storage")
    def test_start_analysis_failure(self, mock_storage, mock_popen, sample_job_data):
        """Test failed analysis execution."""
        job = Job(**sample_job_data)
        mock_storage.get_job.return_value = job

        # Mock failed process
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            "Starting...\n",
            "Error occurred!\n",
            ""
        ]
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        # Run task
        start_analysis(None, job.id)

        # Verify job marked as failed
        saved_job = mock_storage.save_job.call_args[0][0]
        assert saved_job.status == JobStatus.FAILED
        assert saved_job.error is not None

    @patch("web.backend.tasks.job_storage")
    def test_start_analysis_job_not_found(self, mock_storage):
        """Test analysis with non-existent job."""
        mock_storage.get_job.return_value = None

        # Should not crash
        start_analysis(None, "nonexistent-job")

    @patch("web.backend.tasks.subprocess.Popen")
    @patch("web.backend.tasks.job_storage")
    def test_start_analysis_exception(self, mock_storage, mock_popen, sample_job_data):
        """Test analysis with exception."""
        job = Job(**sample_job_data)
        mock_storage.get_job.return_value = job

        # Mock exception
        mock_popen.side_effect = Exception("Something went wrong")

        # Run task
        start_analysis(None, job.id)

        # Verify job marked as failed
        saved_job = mock_storage.save_job.call_args[0][0]
        assert saved_job.status == JobStatus.FAILED
        assert "Something went wrong" in saved_job.error

    @patch("web.backend.tasks.subprocess.Popen")
    @patch("web.backend.tasks.job_storage")
    def test_start_analysis_updates_log(self, mock_storage, mock_popen, sample_job_data):
        """Test that analysis updates job log."""
        job = Job(**sample_job_data)
        mock_storage.get_job.return_value = job

        # Mock process
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            "Line 1\n",
            "Line 2\n",
            "Line 3\n",
            ""
        ]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Run task
        start_analysis(None, job.id)

        # Verify log was updated
        saved_job = mock_storage.save_job.call_args[0][0]
        assert len(saved_job.log) > 0
        assert any("Line 1" in entry for entry in saved_job.log)

    @patch("web.backend.tasks.subprocess.Popen")
    @patch("web.backend.tasks.job_storage")
    @patch("web.backend.tasks.settings")
    def test_start_analysis_creates_output_dir(self, mock_settings, mock_storage, mock_popen, sample_job_data, temp_dir):
        """Test that analysis creates output directory."""
        job = Job(**{**sample_job_data, "destination_path": None})
        mock_storage.get_job.return_value = job
        mock_settings.output_dir = temp_dir

        # Mock process
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Run task
        start_analysis(None, job.id)

        # Verify output directory was created
        output_dir = temp_dir / job.case_number
        assert output_dir.exists()
