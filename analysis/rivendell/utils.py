#!/usr/bin/env python3 -tt
"""
Utility functions for Elrond
"""
import os
import sys


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
    if os.environ.get('ELROND_NONINTERACTIVE') == '1':
        # In non-interactive mode, return default without prompting
        # Print the prompt and default to log for debugging
        print(f"{prompt}[auto: {default}]")
        return default
    else:
        # In interactive mode, use regular input
        return input(prompt)
