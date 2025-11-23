"""
Unit Tests for Elrond Engine

Tests the core ElrondEngine class functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import datetime

from core.engine import ElrondEngine, LegacyBridge


@pytest.mark.unit
class TestElrondEngine:
    """Test ElrondEngine class."""

    def test_init(self, mock_case_id, mock_source_dir, mock_output_dir):
        """Test engine initialization."""
        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter"), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(
                case_id=mock_case_id,
                source_directory=mock_source_dir,
                output_directory=mock_output_dir,
                verbosity="normal"
            )

            assert engine.case_id == mock_case_id
            assert engine.source_dir == mock_source_dir
            assert engine.output_dir == mock_output_dir
            assert isinstance(engine.images, dict)
            assert isinstance(engine.mounted_images, list)

    def test_init_without_output_dir(self, mock_case_id, mock_source_dir):
        """Test engine initialization without output directory."""
        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter"), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(
                case_id=mock_case_id,
                source_directory=mock_source_dir
            )

            assert engine.output_dir == Path.cwd()

    def test_check_permissions_success(self, mock_case_id, mock_source_dir):
        """Test permission check when running with proper permissions."""
        mock_platform = MagicMock()
        mock_platform.check_permissions.return_value = (True, "Running with sudo")

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            result = engine.check_permissions()

            assert result is True
            mock_platform.check_permissions.assert_called_once()

    def test_check_permissions_failure(self, mock_case_id, mock_source_dir):
        """Test permission check when not running with proper permissions."""
        mock_platform = MagicMock()
        mock_platform.check_permissions.return_value = (False, "Not running as root")

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            result = engine.check_permissions()

            assert result is False

    def test_check_dependencies_success(self, mock_case_id, mock_source_dir):
        """Test dependency check when all tools available."""
        mock_tool_mgr = MagicMock()
        mock_tool_mgr.check_all_dependencies.return_value = {
            "volatility": {"available": True, "required": True},
            "plaso": {"available": True, "required": True},
        }

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter"), \
             patch("core.engine.get_tool_manager", return_value=mock_tool_mgr), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            result = engine.check_dependencies()

            assert result is True
            mock_tool_mgr.check_all_dependencies.assert_called_once()

    def test_check_dependencies_missing_required(self, mock_case_id, mock_source_dir):
        """Test dependency check when required tools are missing."""
        mock_tool_mgr = MagicMock()
        mock_tool_mgr.check_all_dependencies.return_value = {
            "volatility": {"available": False, "required": True},
            "plaso": {"available": True, "required": True},
        }
        mock_tool_mgr.suggest_installation.return_value = "apt install volatility"

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter"), \
             patch("core.engine.get_tool_manager", return_value=mock_tool_mgr), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            result = engine.check_dependencies()

            assert result is False

    def test_identify_images(self, mock_case_id, mock_source_dir):
        """Test image identification in source directory."""
        mock_platform = MagicMock()
        mock_platform.identify_image_type.return_value = "e01"

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            images = engine.identify_images()

            assert len(images) >= 1
            # Should find the test.E01 file created in fixture

    def test_mount_image_success(self, mock_case_id, mock_source_dir, temp_dir):
        """Test successful image mounting."""
        image_path = mock_source_dir / "test.E01"
        mount_point = temp_dir / "mnt"
        mount_point.mkdir()

        mock_platform = MagicMock()
        mock_platform.is_mounted.return_value = False
        mock_platform.mount_image.return_value = True

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            result = engine.mount_image(image_path, mount_point)

            assert result == mount_point
            assert str(mount_point) in engine.mounted_images
            mock_platform.mount_image.assert_called_once()

    def test_mount_image_failure(self, mock_case_id, mock_source_dir, temp_dir):
        """Test failed image mounting."""
        image_path = mock_source_dir / "test.E01"
        mount_point = temp_dir / "mnt"
        mount_point.mkdir()

        mock_platform = MagicMock()
        mock_platform.is_mounted.return_value = False
        mock_platform.mount_image.return_value = False

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            result = engine.mount_image(image_path, mount_point)

            assert result is None
            assert str(mount_point) not in engine.mounted_images

    def test_unmount_all(self, mock_case_id, mock_source_dir):
        """Test unmounting all mounted images."""
        mock_platform = MagicMock()
        mock_platform.unmount_image.return_value = True

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            engine.mounted_images = ["/mnt/test1", "/mnt/test2"]

            result = engine.unmount_all()

            assert result is True
            assert len(engine.mounted_images) == 0
            assert mock_platform.unmount_image.call_count == 2

    def test_get_elapsed_time(self, mock_case_id, mock_source_dir):
        """Test elapsed time calculation."""
        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter"), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            engine = ElrondEngine(mock_case_id, mock_source_dir)
            elapsed = engine.get_elapsed_time()

            assert isinstance(elapsed, str)
            assert "second" in elapsed or "minute" in elapsed

    def test_context_manager(self, mock_case_id, mock_source_dir):
        """Test engine as context manager."""
        mock_platform = MagicMock()

        with patch("core.engine.get_logger"), \
             patch("core.engine.get_settings"), \
             patch("core.engine.get_platform_adapter", return_value=mock_platform), \
             patch("core.engine.get_tool_manager"), \
             patch("core.engine.get_executor"):

            with ElrondEngine(mock_case_id, mock_source_dir) as engine:
                engine.mounted_images = ["/mnt/test"]

            # Cleanup should have been called
            assert len(engine.mounted_images) == 0


@pytest.mark.unit
class TestLegacyBridge:
    """Test LegacyBridge class."""

    def test_create_engine_from_args(self, mock_source_dir, mock_output_dir):
        """Test creating engine from argparse arguments."""
        mock_args = MagicMock()
        mock_args.case = ["TEST-001"]
        mock_args.directory = [str(mock_source_dir), str(mock_output_dir)]

        with patch("core.engine.ElrondEngine.__init__", return_value=None):
            # Just test that the conversion works
            LegacyBridge.create_engine_from_args(mock_args)

    def test_convert_mount_points(self):
        """Test mount point conversion."""
        original_mounts = [f"/mnt/elrond_mount0{i}" for i in range(5)]
        converted = LegacyBridge.convert_mount_points(original_mounts)

        assert len(converted) == len(original_mounts)
        assert all("elrond" in mp for mp in converted)

    def test_check_tool_availability(self):
        """Test tool availability check."""
        mock_tool_mgr = MagicMock()
        mock_tool_mgr.verify_tool.return_value = (True, "/usr/bin/tool")

        with patch("core.engine.get_tool_manager", return_value=mock_tool_mgr):
            result = LegacyBridge.check_tool_availability("volatility")

            assert result is True
            mock_tool_mgr.verify_tool.assert_called_once_with("volatility")
