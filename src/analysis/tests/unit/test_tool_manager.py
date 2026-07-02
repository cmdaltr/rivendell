"""
Unit Tests for Tool Manager

Tests the forensic tool management and verification system.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from tools.manager import ToolManager
from tools.definitions import TOOL_DEFINITIONS


@pytest.mark.unit
class TestToolManager:
    """Test ToolManager class."""

    def test_init(self):
        """Test tool manager initialization."""
        with patch("tools.manager.get_platform_adapter"):
            manager = ToolManager()

            assert manager is not None
            assert hasattr(manager, "platform_adapter")

    def test_verify_tool_available(self):
        """Test verifying tool that is available."""
        with patch("tools.manager.get_platform_adapter"), \
             patch("shutil.which", return_value="/usr/bin/volatility"):

            manager = ToolManager()
            is_available, path = manager.verify_tool("volatility")

            assert is_available is True
            assert path == "/usr/bin/volatility"

    def test_verify_tool_not_available(self):
        """Test verifying tool that is not available."""
        with patch("tools.manager.get_platform_adapter"), \
             patch("shutil.which", return_value=None):

            manager = ToolManager()
            is_available, path = manager.verify_tool("nonexistent-tool")

            assert is_available is False
            assert path is None

    def test_verify_tool_unknown(self):
        """Test verifying unknown tool."""
        with patch("tools.manager.get_platform_adapter"):
            manager = ToolManager()

            with pytest.raises(ValueError):
                manager.verify_tool("completely-unknown-tool")

    def test_check_all_dependencies_required_only(self):
        """Test checking only required dependencies."""
        with patch("tools.manager.get_platform_adapter") as mock_platform, \
             patch.object(ToolManager, "verify_tool") as mock_verify:

            mock_platform.return_value.system = "linux"
            mock_verify.return_value = (True, "/usr/bin/tool")

            manager = ToolManager()
            results = manager.check_all_dependencies(required_only=True)

            # Should only check required tools
            assert all(r["required"] for r in results.values())

    def test_check_all_dependencies_all_tools(self):
        """Test checking all dependencies."""
        with patch("tools.manager.get_platform_adapter") as mock_platform, \
             patch.object(ToolManager, "verify_tool") as mock_verify:

            mock_platform.return_value.system = "linux"
            mock_verify.return_value = (True, "/usr/bin/tool")

            manager = ToolManager()
            results = manager.check_all_dependencies(required_only=False)

            # Should include optional tools
            assert any(not r["required"] for r in results.values())

    def test_suggest_installation_linux(self):
        """Test installation suggestion for Linux."""
        with patch("tools.manager.get_platform_adapter") as mock_platform:
            mock_platform.return_value.system = "linux"

            manager = ToolManager()
            suggestion = manager.suggest_installation("volatility")

            assert "apt" in suggestion.lower() or "yum" in suggestion.lower()

    def test_suggest_installation_macos(self):
        """Test installation suggestion for macOS."""
        with patch("tools.manager.get_platform_adapter") as mock_platform:
            mock_platform.return_value.system = "darwin"

            manager = ToolManager()
            suggestion = manager.suggest_installation("volatility")

            assert "brew" in suggestion.lower()

    def test_suggest_installation_windows(self):
        """Test installation suggestion for Windows."""
        with patch("tools.manager.get_platform_adapter") as mock_platform:
            mock_platform.return_value.system = "windows"

            manager = ToolManager()
            suggestion = manager.suggest_installation("volatility")

            assert "download" in suggestion.lower() or "install" in suggestion.lower()

    def test_get_tool_category(self):
        """Test getting tool category."""
        with patch("tools.manager.get_platform_adapter"):
            manager = ToolManager()

            assert manager.get_tool_category("volatility") == "memory"
            assert manager.get_tool_category("plaso") == "timeline"
            assert manager.get_tool_category("ewfmount") == "imaging"

    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        with patch("tools.manager.get_platform_adapter"):
            manager = ToolManager()

            memory_tools = manager.get_tools_by_category("memory")

            assert "volatility" in memory_tools
            assert all(
                TOOL_DEFINITIONS[tool]["category"] == "memory"
                for tool in memory_tools
            )

    def test_is_tool_required(self):
        """Test checking if tool is required."""
        with patch("tools.manager.get_platform_adapter"):
            manager = ToolManager()

            # Check some known required tools
            assert manager.is_tool_required("python3") is True

    def test_get_missing_tools(self):
        """Test getting list of missing tools."""
        with patch("tools.manager.get_platform_adapter"), \
             patch.object(ToolManager, "verify_tool") as mock_verify:

            def verify_side_effect(tool_name):
                if tool_name in ["volatility", "plaso"]:
                    return (False, None)
                return (True, "/usr/bin/tool")

            mock_verify.side_effect = verify_side_effect

            manager = ToolManager()
            missing = manager.get_missing_tools(required_only=True)

            assert "volatility" in [t["name"] for t in missing] or \
                   "plaso" in [t["name"] for t in missing]

    def test_get_available_tools(self):
        """Test getting list of available tools."""
        with patch("tools.manager.get_platform_adapter"), \
             patch.object(ToolManager, "verify_tool") as mock_verify:

            mock_verify.return_value = (True, "/usr/bin/tool")

            manager = ToolManager()
            available = manager.get_available_tools()

            assert len(available) > 0
            assert all("path" in tool for tool in available)


@pytest.mark.unit
class TestToolDefinitions:
    """Test tool definitions structure."""

    def test_all_tools_have_required_fields(self):
        """Test that all tools have required fields."""
        required_fields = ["name", "category", "required", "platforms"]

        for tool_id, tool_def in TOOL_DEFINITIONS.items():
            for field in required_fields:
                assert field in tool_def, f"Tool {tool_id} missing field: {field}"

    def test_tool_categories_valid(self):
        """Test that all tools have valid categories."""
        valid_categories = {
            "imaging", "memory", "timeline", "registry", "logs",
            "filesystem", "network", "malware", "system", "analysis"
        }

        for tool_id, tool_def in TOOL_DEFINITIONS.items():
            assert tool_def["category"] in valid_categories, \
                f"Tool {tool_id} has invalid category: {tool_def['category']}"

    def test_platform_support_valid(self):
        """Test that all tools specify valid platforms."""
        valid_platforms = {"linux", "darwin", "windows"}

        for tool_id, tool_def in TOOL_DEFINITIONS.items():
            platforms = set(tool_def["platforms"])
            assert platforms.issubset(valid_platforms), \
                f"Tool {tool_id} has invalid platforms: {platforms - valid_platforms}"

    def test_required_tools_exist(self):
        """Test that required tools are properly defined."""
        required_tools = [
            tool_id for tool_id, tool_def in TOOL_DEFINITIONS.items()
            if tool_def.get("required", False)
        ]

        assert len(required_tools) > 0, "No required tools defined"

    def test_optional_tools_exist(self):
        """Test that optional tools are properly defined."""
        optional_tools = [
            tool_id for tool_id, tool_def in TOOL_DEFINITIONS.items()
            if not tool_def.get("required", False)
        ]

        assert len(optional_tools) > 0, "No optional tools defined"
