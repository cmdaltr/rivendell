"""
Unit Tests for Platform Adapters

Tests platform-specific adapters for Linux, macOS, and Windows.
"""

import pytest
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from platform.linux import LinuxPlatformAdapter
from platform.macos import MacOSPlatformAdapter
from platform.windows import WindowsPlatformAdapter
from platform.factory import get_platform_adapter


@pytest.mark.unit
class TestLinuxPlatformAdapter:
    """Test Linux platform adapter."""

    def test_check_permissions_with_sudo(self):
        """Test permission check when running as root."""
        adapter = LinuxPlatformAdapter()

        with patch('os.geteuid', return_value=0):
            has_perms, message = adapter.check_permissions()

            assert has_perms is True
            assert "root" in message.lower() or "sudo" in message.lower()

    def test_check_permissions_without_sudo(self):
        """Test permission check when not running as root."""
        adapter = LinuxPlatformAdapter()

        with patch('os.geteuid', return_value=1000):
            has_perms, message = adapter.check_permissions()

            assert has_perms is False
            assert "sudo" in message.lower() or "root" in message.lower()

    def test_identify_image_type_e01(self):
        """Test identifying E01 disk images."""
        adapter = LinuxPlatformAdapter()

        assert adapter.identify_image_type(Path("/path/to/image.E01")) == "e01"
        assert adapter.identify_image_type(Path("/path/to/image.e01")) == "e01"
        assert adapter.identify_image_type(Path("/path/to/IMAGE.Ex01")) == "e01"

    def test_identify_image_type_raw(self):
        """Test identifying raw disk images."""
        adapter = LinuxPlatformAdapter()

        assert adapter.identify_image_type(Path("/path/to/image.dd")) == "raw"
        assert adapter.identify_image_type(Path("/path/to/image.raw")) == "raw"
        assert adapter.identify_image_type(Path("/path/to/image.img")) == "raw"

    def test_identify_image_type_vmdk(self):
        """Test identifying VMDK disk images."""
        adapter = LinuxPlatformAdapter()

        assert adapter.identify_image_type(Path("/path/to/image.vmdk")) == "vmdk"

    def test_identify_image_type_memory(self):
        """Test identifying memory images."""
        adapter = LinuxPlatformAdapter()

        assert adapter.identify_image_type(Path("/path/to/memory.mem")) == "memory"
        assert adapter.identify_image_type(Path("/path/to/memory.dmp")) == "memory"
        assert adapter.identify_image_type(Path("/path/to/memory.lime")) == "memory"

    def test_identify_image_type_unknown(self):
        """Test identifying unknown file types."""
        adapter = LinuxPlatformAdapter()

        assert adapter.identify_image_type(Path("/path/to/file.txt")) == "unknown"
        assert adapter.identify_image_type(Path("/path/to/file.pdf")) == "unknown"

    @patch('subprocess.run')
    def test_mount_image_e01_success(self, mock_run):
        """Test successfully mounting E01 image."""
        adapter = LinuxPlatformAdapter()
        mock_run.return_value.returncode = 0

        image_path = Path("/images/test.E01")
        mount_point = Path("/mnt/test")

        with patch.object(Path, 'mkdir'):
            result = adapter.mount_image(image_path, mount_point, image_type="e01")

            assert result is True
            mock_run.assert_called()

    @patch('subprocess.run')
    def test_mount_image_failure(self, mock_run):
        """Test failed image mounting."""
        adapter = LinuxPlatformAdapter()
        mock_run.return_value.returncode = 1

        image_path = Path("/images/test.E01")
        mount_point = Path("/mnt/test")

        with patch.object(Path, 'mkdir'):
            result = adapter.mount_image(image_path, mount_point, image_type="e01")

            assert result is False

    @patch('subprocess.run')
    def test_unmount_image_success(self, mock_run):
        """Test successfully unmounting image."""
        adapter = LinuxPlatformAdapter()
        mock_run.return_value.returncode = 0

        mount_point = Path("/mnt/test")
        result = adapter.unmount_image(mount_point)

        assert result is True
        mock_run.assert_called()

    @patch('subprocess.run')
    def test_is_mounted_true(self, mock_run):
        """Test checking if path is mounted (mounted)."""
        adapter = LinuxPlatformAdapter()
        mock_run.return_value.stdout = "/mnt/test\n"
        mock_run.return_value.returncode = 0

        result = adapter.is_mounted(Path("/mnt/test"))

        assert result is True

    @patch('subprocess.run')
    def test_is_mounted_false(self, mock_run):
        """Test checking if path is mounted (not mounted)."""
        adapter = LinuxPlatformAdapter()
        mock_run.return_value.stdout = ""
        mock_run.return_value.returncode = 0

        result = adapter.is_mounted(Path("/mnt/test"))

        assert result is False


@pytest.mark.unit
class TestMacOSPlatformAdapter:
    """Test macOS platform adapter."""

    def test_check_permissions_with_sudo(self):
        """Test permission check when running as root."""
        adapter = MacOSPlatformAdapter()

        with patch('os.geteuid', return_value=0):
            has_perms, message = adapter.check_permissions()

            assert has_perms is True

    def test_check_permissions_without_sudo(self):
        """Test permission check when not running as root."""
        adapter = MacOSPlatformAdapter()

        with patch('os.geteuid', return_value=501):
            has_perms, message = adapter.check_permissions()

            assert has_perms is False

    def test_identify_image_type(self):
        """Test image type identification on macOS."""
        adapter = MacOSPlatformAdapter()

        # Should work same as Linux
        assert adapter.identify_image_type(Path("/path/to/image.E01")) == "e01"
        assert adapter.identify_image_type(Path("/path/to/image.dmg")) == "dmg"

    @patch('subprocess.run')
    def test_mount_image_dmg(self, mock_run):
        """Test mounting DMG image on macOS."""
        adapter = MacOSPlatformAdapter()
        mock_run.return_value.returncode = 0

        image_path = Path("/images/test.dmg")
        mount_point = Path("/Volumes/test")

        with patch.object(Path, 'mkdir'):
            result = adapter.mount_image(image_path, mount_point, image_type="dmg")

            assert result is True


@pytest.mark.unit
@pytest.mark.platform_specific
class TestWindowsPlatformAdapter:
    """Test Windows platform adapter."""

    def test_check_permissions_with_admin(self):
        """Test permission check when running as administrator."""
        adapter = WindowsPlatformAdapter()

        with patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=1):
            has_perms, message = adapter.check_permissions()

            assert has_perms is True

    def test_check_permissions_without_admin(self):
        """Test permission check when not running as administrator."""
        adapter = WindowsPlatformAdapter()

        with patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=0):
            has_perms, message = adapter.check_permissions()

            assert has_perms is False

    def test_identify_image_type_vhd(self):
        """Test identifying VHD images on Windows."""
        adapter = WindowsPlatformAdapter()

        assert adapter.identify_image_type(Path("C:\\images\\test.vhd")) == "vhd"
        assert adapter.identify_image_type(Path("C:\\images\\test.vhdx")) == "vhdx"

    @patch('subprocess.run')
    def test_mount_image_vhd(self, mock_run):
        """Test mounting VHD image on Windows."""
        adapter = WindowsPlatformAdapter()
        mock_run.return_value.returncode = 0

        image_path = Path("C:\\images\\test.vhd")
        mount_point = Path("D:\\")

        result = adapter.mount_image(image_path, mount_point, image_type="vhd")

        assert result is True


@pytest.mark.unit
class TestPlatformFactory:
    """Test platform adapter factory."""

    @patch('platform.system', return_value='Linux')
    def test_get_platform_adapter_linux(self, mock_system):
        """Test getting Linux platform adapter."""
        adapter = get_platform_adapter()

        assert isinstance(adapter, LinuxPlatformAdapter)

    @patch('platform.system', return_value='Darwin')
    def test_get_platform_adapter_macos(self, mock_system):
        """Test getting macOS platform adapter."""
        adapter = get_platform_adapter()

        assert isinstance(adapter, MacOSPlatformAdapter)

    @patch('platform.system', return_value='Windows')
    def test_get_platform_adapter_windows(self, mock_system):
        """Test getting Windows platform adapter."""
        adapter = get_platform_adapter()

        assert isinstance(adapter, WindowsPlatformAdapter)

    @patch('platform.system', return_value='FreeBSD')
    def test_get_platform_adapter_unsupported(self, mock_system):
        """Test getting adapter for unsupported platform."""
        with pytest.raises(NotImplementedError):
            get_platform_adapter()
