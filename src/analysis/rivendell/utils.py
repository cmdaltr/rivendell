#!/usr/bin/env python3 -tt
"""
Utility functions for Elrond
"""
import os
import re
import sys


def is_noninteractive():
    """
    Check if running in non-interactive mode (e.g., web interface, automation)

    Non-interactive mode is ALWAYS enabled by default unless explicitly disabled.
    This ensures clean output for web interfaces and automation.

    Returns:
        bool: True if running in non-interactive mode (default), False only if explicitly disabled
    """
    # Check if explicitly set to '0' to disable non-interactive mode
    # Otherwise, default to non-interactive (True)
    env_value = os.environ.get('ELROND_NONINTERACTIVE', '1')
    return env_value != '0'


def strip_ansi_codes(text):
    """
    Remove ANSI color codes and escape sequences from text

    Args:
        text: String that may contain ANSI codes

    Returns:
        String with ANSI codes removed
    """
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', text)


def safe_print(text, use_colors=True):
    """
    Print text with optional ANSI color code stripping for non-interactive mode

    Args:
        text: Text to print
        use_colors: If False or in non-interactive mode, strip ANSI codes
    """
    if is_noninteractive() or not use_colors:
        text = strip_ansi_codes(text)
    # Filter out visual noise in non-interactive mode
    if is_noninteractive():
        # Skip empty lines, separator lines, and ASCII art
        if text.strip() in ['', '----------------------------------------', '-' * 40]:
            return
        # Skip lines that are just visual formatting
        if all(c in ' -=_.|/\\' for c in text.strip()):
            return
    print(text)


def safe_input(prompt, default="y"):
    """
    Wrapper for input() that handles non-interactive mode.

    When ELROND_NONINTERACTIVE environment variable is set,
    returns the default value without prompting.

    Args:
        prompt: The prompt to display to the user
        default: The default value to return in non-interactive mode (default: "y")

    Returns:
        User input string or default value
    """
    if is_noninteractive():
        # In non-interactive mode, return default without prompting
        # Print the prompt and default to log for debugging
        prompt_clean = strip_ansi_codes(prompt)
        print(f"{prompt_clean}[auto: {default}]")
        return default
    else:
        # In interactive mode, use regular input
        return input(prompt)
