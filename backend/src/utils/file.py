"""
Strict static typing for file utility functions.
"""

import re
from typing import Final, Literal, TypeAlias, TypedDict

# Type aliases for stricter typing
Filename: TypeAlias = str
SanitizedFilename: TypeAlias = str


# TypedDict for future extensibility (if you want to return more info)
class SanitizedResult(TypedDict):
    sanitized: SanitizedFilename
    original: Filename


# Strict typing constants
_PATH_SEPARATORS: Final[tuple[Literal["/"], Literal["\\"]]] = ("/", "\\")
_DANGEROUS_COMPONENTS: Final[tuple[Literal[".."], Literal["."]]] = ("..", ".")
_INVALID_CHARS_PATTERN: Final[Literal[r'[\\/*?:"<>|]']] = r'[\\/*?:"<>|]'


def sanitize_filename(filename: Filename) -> SanitizedFilename:
    """
    Sanitizes a filename to prevent path traversal attacks.

    Args:
        filename: Filename (str) to sanitize

    Returns:
        SanitizedFilename (str) with no path components

    Examples:
        >>> sanitize_filename("../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("file.txt")
        'file.txt'

    Raises:
        None
    """
    if not filename:
        unnamed: Final[SanitizedFilename] = "unnamed_file"
        return unnamed

    parts: list[Filename] = [
        p for p in re.split(r"[\\/]+", filename) if p and p not in _DANGEROUS_COMPONENTS
    ]
    if not parts:
        empty: Final[SanitizedFilename] = "_"
        return empty
    safe_name: SanitizedFilename = "_".join(parts)
    safe_name = re.sub(_INVALID_CHARS_PATTERN, "_", safe_name)
    safe_name = safe_name.replace("..", "_")
    return safe_name


def is_safe_filename(filename: Filename) -> Literal[True, False]:
    """
    Checks if a filename is safe (no path traversal).

    Args:
        filename: Filename (str) to check

    Returns:
        Literal[True] if the filename is safe, Literal[False] otherwise
    """
    if not isinstance(filename, str) or not filename:
        return False
    # Path traversal detection
    if any(sep in filename for sep in _PATH_SEPARATORS) or ".." in filename:
        return False
    # Check for other potentially dangerous characters
    if re.search(_INVALID_CHARS_PATTERN, filename):
        return False
    return True
