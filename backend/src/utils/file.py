import os
import re


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent path traversal attacks.

    Args:
        filename: The original filename

    Returns:
        A sanitized filename with no path components

    Examples:
        >>> sanitize_filename("../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("file.txt")
        'file.txt'
    """
    if not filename:
        return "unnamed_file"

    # Split into path components, remove empty and dangerous ones
    parts = [p for p in re.split(r"[\\/]+", filename) if p and p not in ("..", ".")]
    if not parts:
        return "_"
    # Join with underscores to preserve all info, but prevent traversal
    safe_name = "_".join(parts)
    # Replace any problematic characters
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", safe_name)
    # Remove any remaining '..' just in case
    safe_name = safe_name.replace("..", "_")
    return safe_name


def is_safe_filename(filename: str) -> bool:
    """
    Checks if a filename is safe (no path traversal).

    Args:
        filename: The filename to check

    Returns:
        True if the filename is safe, False otherwise
    """
    if not filename or not isinstance(filename, str):
        return False
    # Path traversal detection
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    # Check for other potentially dangerous characters
    if re.search(r'[*?:"<>|]', filename):
        return False
    return True
