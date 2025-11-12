"""
Unit Tests for Utility Helpers

Tests helper functions in utils.helpers module.
"""

import pytest
from datetime import datetime
from pathlib import Path

from utils.helpers import (
    calculate_elapsed_time,
    format_elapsed_time,
    generate_mount_points,
    sanitize_case_id,
    yes_no_prompt,
    format_file_size,
    is_valid_path,
    create_directory_structure,
)


@pytest.mark.unit
class TestTimeHelpers:
    """Test time-related helper functions."""

    def test_calculate_elapsed_time(self):
        """Test elapsed time calculation."""
        start = "2025-01-15T10:00:00"
        end = "2025-01-15T10:05:30"

        seconds, formatted = calculate_elapsed_time(start, end)

        assert seconds == 330  # 5 minutes 30 seconds
        assert "5 minutes" in formatted

    def test_calculate_elapsed_time_hours(self):
        """Test elapsed time with hours."""
        start = "2025-01-15T10:00:00"
        end = "2025-01-15T13:30:45"

        seconds, formatted = calculate_elapsed_time(start, end)

        assert seconds == 12645  # 3h 30m 45s
        assert "3 hours" in formatted

    def test_format_elapsed_time_seconds(self):
        """Test formatting seconds."""
        formatted = format_elapsed_time(45)
        assert formatted == "45 seconds"

    def test_format_elapsed_time_minutes(self):
        """Test formatting minutes."""
        formatted = format_elapsed_time(150)
        assert formatted == "2 minutes 30 seconds"

    def test_format_elapsed_time_hours(self):
        """Test formatting hours."""
        formatted = format_elapsed_time(7265)
        assert formatted == "2 hours 1 minute 5 seconds"


@pytest.mark.unit
class TestFileHelpers:
    """Test file-related helper functions."""

    def test_format_file_size_bytes(self):
        """Test formatting bytes."""
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_file_size_kb(self):
        """Test formatting kilobytes."""
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(2048) == "2.00 KB"

    def test_format_file_size_mb(self):
        """Test formatting megabytes."""
        assert format_file_size(1048576) == "1.00 MB"
        assert format_file_size(5242880) == "5.00 MB"

    def test_format_file_size_gb(self):
        """Test formatting gigabytes."""
        assert format_file_size(1073741824) == "1.00 GB"
        assert format_file_size(10737418240) == "10.00 GB"

    def test_format_file_size_tb(self):
        """Test formatting terabytes."""
        assert format_file_size(1099511627776) == "1.00 TB"

    def test_is_valid_path_existing(self, temp_dir):
        """Test path validation for existing path."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        assert is_valid_path(test_file) is True

    def test_is_valid_path_nonexisting(self, temp_dir):
        """Test path validation for non-existing path."""
        test_file = temp_dir / "nonexistent.txt"

        assert is_valid_path(test_file) is False

    def test_is_valid_path_directory(self, temp_dir):
        """Test path validation for directory."""
        assert is_valid_path(temp_dir) is True

    def test_create_directory_structure(self, temp_dir):
        """Test creating nested directory structure."""
        structure = {
            "case_001": {
                "raw": {},
                "processed": {
                    "registry": {},
                    "logs": {},
                },
                "reports": {},
            }
        }

        base_path = temp_dir / "cases"
        create_directory_structure(base_path, structure)

        assert (base_path / "case_001").exists()
        assert (base_path / "case_001" / "raw").exists()
        assert (base_path / "case_001" / "processed" / "registry").exists()
        assert (base_path / "case_001" / "reports").exists()


@pytest.mark.unit
class TestCaseHelpers:
    """Test case-related helper functions."""

    def test_sanitize_case_id_alphanumeric(self):
        """Test sanitizing alphanumeric case ID."""
        assert sanitize_case_id("INC-2025-001") == "INC-2025-001"
        assert sanitize_case_id("CASE123") == "CASE123"

    def test_sanitize_case_id_special_chars(self):
        """Test sanitizing case ID with special characters."""
        assert sanitize_case_id("INC@2025#001") == "INC-2025-001"
        assert sanitize_case_id("CASE/123\\456") == "CASE-123-456"

    def test_sanitize_case_id_spaces(self):
        """Test sanitizing case ID with spaces."""
        assert sanitize_case_id("CASE 2025 001") == "CASE-2025-001"
        assert sanitize_case_id("  CASE  001  ") == "CASE-001"

    def test_sanitize_case_id_empty(self):
        """Test sanitizing empty case ID."""
        with pytest.raises(ValueError):
            sanitize_case_id("")

    def test_sanitize_case_id_unicode(self):
        """Test sanitizing case ID with unicode."""
        result = sanitize_case_id("CASE™2025①")
        assert result.isascii()


@pytest.mark.unit
class TestMountHelpers:
    """Test mount-related helper functions."""

    def test_generate_mount_points_default(self):
        """Test generating mount points with defaults."""
        mount_points = generate_mount_points("elrond")

        assert len(mount_points) == 20  # Default count
        assert all("elrond" in mp for mp in mount_points)
        assert mount_points[0].endswith("00")
        assert mount_points[19].endswith("19")

    def test_generate_mount_points_custom_count(self):
        """Test generating custom number of mount points."""
        mount_points = generate_mount_points("test", count=5)

        assert len(mount_points) == 5
        assert all("test" in mp for mp in mount_points)

    def test_generate_mount_points_base_path(self):
        """Test generating mount points with custom base path."""
        mount_points = generate_mount_points("elrond", base_path="/media", count=3)

        assert len(mount_points) == 3
        assert all(mp.startswith("/media") for mp in mount_points)

    def test_generate_mount_points_uniqueness(self):
        """Test that generated mount points are unique."""
        mount_points = generate_mount_points("elrond", count=10)

        assert len(mount_points) == len(set(mount_points))


@pytest.mark.unit
class TestUserInteraction:
    """Test user interaction helper functions."""

    def test_yes_no_prompt_yes(self, monkeypatch):
        """Test yes/no prompt with 'yes' input."""
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        result = yes_no_prompt("Continue?")
        assert result is True

    def test_yes_no_prompt_no(self, monkeypatch):
        """Test yes/no prompt with 'no' input."""
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        result = yes_no_prompt("Continue?")
        assert result is False

    def test_yes_no_prompt_variations(self, monkeypatch):
        """Test yes/no prompt with different variations."""
        # Test 'yes'
        monkeypatch.setattr('builtins.input', lambda _: 'yes')
        assert yes_no_prompt("Test?") is True

        # Test 'Y'
        monkeypatch.setattr('builtins.input', lambda _: 'Y')
        assert yes_no_prompt("Test?") is True

        # Test 'no'
        monkeypatch.setattr('builtins.input', lambda _: 'no')
        assert yes_no_prompt("Test?") is False

        # Test 'N'
        monkeypatch.setattr('builtins.input', lambda _: 'N')
        assert yes_no_prompt("Test?") is False

    def test_yes_no_prompt_invalid_then_valid(self, monkeypatch):
        """Test yes/no prompt with invalid input then valid."""
        inputs = iter(['maybe', 'invalid', 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        result = yes_no_prompt("Continue?")
        assert result is True

    def test_yes_no_prompt_default(self, monkeypatch):
        """Test yes/no prompt with empty input and default."""
        monkeypatch.setattr('builtins.input', lambda _: '')

        result = yes_no_prompt("Continue?", default=True)
        assert result is True

        result = yes_no_prompt("Continue?", default=False)
        assert result is False
