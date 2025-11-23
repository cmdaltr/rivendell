"""
Pytest Configuration and Fixtures

This module provides shared fixtures and configuration for all tests.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

# Add elrond to path
ELROND_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ELROND_ROOT))


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_case_id():
    """Return a mock case ID."""
    return "TEST-2025-001"


@pytest.fixture
def mock_source_dir(temp_dir):
    """Create a mock source directory with test files."""
    source = temp_dir / "source"
    source.mkdir()

    # Create a mock disk image (large file)
    disk_image = source / "test.E01"
    disk_image.write_bytes(b"0" * (1024 * 1024 * 1024 + 1))  # > 1GB

    # Create a small file that should be ignored
    small_file = source / "readme.txt"
    small_file.write_text("Test file")

    return source


@pytest.fixture
def mock_output_dir(temp_dir):
    """Create a mock output directory."""
    output = temp_dir / "output"
    output.mkdir()
    return output


@pytest.fixture
def mock_settings():
    """Mock settings object."""
    from unittest.mock import MagicMock

    settings = MagicMock()
    settings.platform_name = "Linux"
    settings.architecture = "x86_64"
    settings.output_dir = Path("/tmp/elrond/output")
    settings.upload_dir = Path("/tmp/elrond/uploads")
    settings.allowed_paths = ["/mnt", "/media", "/tmp/elrond"]
    settings.max_upload_size = 100 * 1024 * 1024 * 1024
    settings.debug = True

    return settings


@pytest.fixture
def mock_platform_adapter():
    """Mock platform adapter."""
    adapter = MagicMock()
    adapter.check_permissions.return_value = (True, "Running with sudo")
    adapter.is_mounted.return_value = False
    adapter.mount_image.return_value = True
    adapter.unmount_image.return_value = True
    adapter.identify_image_type.return_value = "e01"

    return adapter


@pytest.fixture
def mock_tool_manager():
    """Mock tool manager."""
    manager = MagicMock()
    manager.verify_tool.return_value = (True, "/usr/bin/tool")
    manager.check_all_dependencies.return_value = {
        "volatility": {"available": True, "required": True, "category": "memory"},
        "plaso": {"available": True, "required": True, "category": "timeline"},
    }
    manager.suggest_installation.return_value = "apt install tool"

    return manager


@pytest.fixture
def mock_logger():
    """Mock logger."""
    logger = MagicMock()
    return logger


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "id": "test-job-123",
        "case_number": "INC-2025-001",
        "source_paths": ["/mnt/test.E01"],
        "destination_path": "/tmp/elrond/output/INC-2025-001",
        "options": {
            "collect": True,
            "process": True,
            "analysis": False,
            "extract_iocs": False,
            "keywords_file": None,
            "yara_dir": None,
            "collect_files": False,
            "collect_files_filter": None,
            "vss": False,
            "symlinks": False,
            "userprofiles": True,
            "timeline": False,
            "memory": False,
            "memory_timeline": False,
            "imageinfo": True,
            "auto": True,
            "brisk": False,
            "exhaustive": False,
            "quick": True,
            "super_quick": False,
            "splunk": False,
            "elastic": False,
            "navigator": False,
            "clamav": False,
            "nsrl": False,
            "metacollected": False,
            "delete": False,
            "archive": False,
            "unmount": False,
            "lotr": False,
        },
        "status": "pending",
        "progress": 0,
        "log": [],
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
    }


@pytest.fixture
def sample_job_create_request():
    """Sample job creation request."""
    return {
        "case_number": "INC-2025-001",
        "source_paths": ["/mnt/test.E01"],
        "destination_path": "/tmp/elrond/output/INC-2025-001",
        "options": {
            "collect": True,
            "process": True,
            "userprofiles": True,
            "quick": True,
        }
    }


@pytest.fixture
def mock_job_storage(temp_dir):
    """Mock job storage with temporary directory."""
    from web.backend.storage import JobStorage

    storage_dir = temp_dir / "jobs"
    storage_dir.mkdir()

    return JobStorage(storage_dir=storage_dir)


@pytest.fixture
def mock_celery_app():
    """Mock Celery app."""
    app = MagicMock()
    app.task.return_value = lambda f: f
    return app


# Auto-use fixtures
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    yield
    # Clear any cached singletons here if needed


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring external services"
    )
    config.addinivalue_line(
        "markers", "web: Web backend API tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "platform_specific: Tests that only run on specific platforms"
    )


# Environment setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ["ELROND_TEST_MODE"] = "true"
    os.environ["ELROND_DEBUG"] = "true"

    yield

    # Cleanup
    os.environ.pop("ELROND_TEST_MODE", None)
    os.environ.pop("ELROND_DEBUG", None)
