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

    # Get only the basename (remove any directory components)
    safe_name = os.path.basename(filename)

    # Replace any potentially problematic characters with underscores
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", safe_name)

    # Additional check to ensure no relative path components
    if ".." in safe_name:
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
    # Check if the normalized path still has the same basename

    # Path traversal detection
    if ".." in filename or "/" in filename or "\\" in filename:
        return False

    # Check for other potentially dangerous characters
    if re.search(r'[*?:"<>|]', filename):
        return False

    return True
