#!/usr/bin/env python3
"""
File Descriptor Limit Management
Handles "Too many open files" errors gracefully with retry logic
"""

import os
import gc
import time
import errno
import logging as stdlib_logging
from functools import wraps
from typing import Callable, Any, Optional

logger = stdlib_logging.getLogger(__name__)


class FileDescriptorLimitError(Exception):
    """Raised when file descriptor limit is reached after all retries"""
    pass


def retry_on_fd_limit(
    max_retries: int = 5,
    initial_wait: float = 0.5,
    backoff_multiplier: float = 2.0,
    max_wait: float = 10.0,
    trigger_gc: bool = True
):
    """
    Decorator to retry file operations when hitting file descriptor limits.

    This decorator catches OSError with errno EMFILE (24) or ENFILE (23) and:
    1. Triggers garbage collection to close unreferenced file handles
    2. Waits with exponential backoff
    3. Retries the operation
    4. Fails after max_retries attempts

    Args:
        max_retries: Maximum number of retry attempts (default: 5)
        initial_wait: Initial wait time in seconds (default: 0.5)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        max_wait: Maximum wait time between retries (default: 10.0)
        trigger_gc: Whether to trigger garbage collection on retry (default: True)

    Usage:
        @retry_on_fd_limit(max_retries=3)
        def process_files():
            with open('/path/to/file', 'r') as f:
                return f.read()

    Example:
        >>> @retry_on_fd_limit()
        ... def read_many_files(paths):
        ...     results = []
        ...     for path in paths:
        ...         with open(path, 'r') as f:
        ...             results.append(f.read())
        ...     return results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            wait_time = initial_wait
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except OSError as e:
                    # Check if this is a file descriptor limit error
                    if e.errno not in (errno.EMFILE, errno.ENFILE):
                        # Not a file descriptor error, re-raise immediately
                        raise

                    last_exception = e

                    # If this was the last attempt, raise custom exception
                    if attempt >= max_retries:
                        logger.error(
                            f"File descriptor limit reached after {max_retries} retries "
                            f"in {func.__name__}: {e}"
                        )
                        raise FileDescriptorLimitError(
                            f"Too many open files after {max_retries} retries. "
                            f"Consider increasing ulimit or reducing concurrent file operations."
                        ) from e

                    # Log the retry attempt
                    logger.warning(
                        f"File descriptor limit reached in {func.__name__} "
                        f"(attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Waiting {wait_time:.1f}s and retrying..."
                    )

                    # Trigger garbage collection to close unreferenced files
                    if trigger_gc:
                        closed_count = gc.collect()
                        logger.debug(
                            f"Garbage collection freed {closed_count} objects, "
                            f"attempting to close file handles"
                        )

                    # Wait before retrying
                    time.sleep(wait_time)

                    # Exponential backoff with max limit
                    wait_time = min(wait_time * backoff_multiplier, max_wait)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def safe_open(
    filepath: str,
    mode: str = 'r',
    encoding: Optional[str] = None,
    max_retries: int = 5,
    **kwargs
):
    """
    Open a file with automatic retry on file descriptor limit errors.

    This is a drop-in replacement for open() that handles "Too many open files" errors.

    Args:
        filepath: Path to file
        mode: File mode ('r', 'w', 'rb', etc.)
        encoding: Text encoding (for text mode)
        max_retries: Maximum retry attempts
        **kwargs: Additional arguments passed to open()

    Returns:
        File handle

    Raises:
        FileDescriptorLimitError: If limit reached after all retries

    Usage:
        # Instead of:
        with open('/path/to/file', 'r') as f:
            data = f.read()

        # Use:
        with safe_open('/path/to/file', 'r') as f:
            data = f.read()
    """
    @retry_on_fd_limit(max_retries=max_retries)
    def _open():
        if encoding:
            return open(filepath, mode, encoding=encoding, **kwargs)
        else:
            return open(filepath, mode, **kwargs)

    return _open()


def get_open_fd_count() -> int:
    """
    Get the current number of open file descriptors for this process.

    Returns:
        Number of open file descriptors

    Note:
        On Linux/macOS, reads from /proc/self/fd or /dev/fd
        On other systems, returns -1
    """
    try:
        if os.path.exists('/proc/self/fd'):
            return len(os.listdir('/proc/self/fd'))
        elif os.path.exists('/dev/fd'):
            return len(os.listdir('/dev/fd'))
        else:
            return -1
    except Exception:
        return -1


def get_fd_limit() -> tuple[int, int]:
    """
    Get the current file descriptor soft and hard limits.

    Returns:
        Tuple of (soft_limit, hard_limit)

    Example:
        >>> soft, hard = get_fd_limit()
        >>> print(f"Current FD limit: {soft} (soft), {hard} (hard)")
    """
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        return (soft, hard)
    except Exception:
        return (-1, -1)


def check_fd_usage(warn_threshold: float = 0.8) -> dict:
    """
    Check current file descriptor usage and warn if approaching limit.

    Args:
        warn_threshold: Warn if usage exceeds this fraction of limit (0.0-1.0)

    Returns:
        Dictionary with usage statistics

    Example:
        >>> stats = check_fd_usage(warn_threshold=0.8)
        >>> print(f"FD usage: {stats['used']}/{stats['limit']} ({stats['percent']}%)")
    """
    used = get_open_fd_count()
    soft_limit, hard_limit = get_fd_limit()

    stats = {
        'used': used,
        'soft_limit': soft_limit,
        'hard_limit': hard_limit,
        'percent': round((used / soft_limit * 100) if soft_limit > 0 else 0, 1),
        'available': soft_limit - used if soft_limit > 0 else -1
    }

    # Warn if approaching limit
    if soft_limit > 0 and used / soft_limit >= warn_threshold:
        logger.warning(
            f"File descriptor usage high: {used}/{soft_limit} ({stats['percent']}%). "
            f"Consider closing files or increasing ulimit."
        )

    return stats


# Example usage and testing
if __name__ == '__main__':
    stdlib_logging.basicConfig(level=stdlib_logging.DEBUG)

    print("File Descriptor Limit Management Utility")
    print("=" * 50)

    # Show current limits
    soft, hard = get_fd_limit()
    print(f"Current FD limits: {soft} (soft), {hard} (hard)")

    used = get_open_fd_count()
    print(f"Currently open FDs: {used}")

    # Test retry decorator
    @retry_on_fd_limit(max_retries=3, initial_wait=0.1)
    def test_function():
        print("Function executed successfully")
        return "success"

    result = test_function()
    print(f"Test result: {result}")

    # Check usage
    stats = check_fd_usage()
    print(f"\nFD Usage Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
