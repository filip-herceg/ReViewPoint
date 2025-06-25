import os
import pytest
from src.utils import file as file_utils

def test_sanitize_filename_basic():
    assert file_utils.sanitize_filename("file.txt") == "file.txt"
    assert file_utils.sanitize_filename("../etc/passwd") == "etc_passwd"
    assert file_utils.sanitize_filename("..\\windows\\system32.dll") == "windows_system32.dll"
    assert file_utils.sanitize_filename("folder/file.txt") == "folder_file.txt"
    assert file_utils.sanitize_filename("folder\\file.txt") == "folder_file.txt"
    assert file_utils.sanitize_filename("file:name.txt") == "file_name.txt"
    assert file_utils.sanitize_filename("") == "unnamed_file"
    assert file_utils.sanitize_filename(None) == "unnamed_file"

def test_sanitize_filename_edge_cases():
    # Only dangerous chars
    assert file_utils.sanitize_filename("..") == "_"
    assert file_utils.sanitize_filename("..\\..\\..") == "_"
    assert file_utils.sanitize_filename("file*?<>|.txt") == "file_____.txt"
    # Double dots in name
    assert file_utils.sanitize_filename("foo..bar.txt") == "foo_bar.txt"
    # Path traversal with mixed slashes
    assert file_utils.sanitize_filename("..\\folder/../evil.txt") == "folder_evil.txt"
    # Unicode and spaces
    assert file_utils.sanitize_filename("fílè nâmé.txt") == "fílè nâmé.txt"

def test_is_safe_filename_basic():
    assert file_utils.is_safe_filename("file.txt")
    assert file_utils.is_safe_filename("file_name.txt")
    assert file_utils.is_safe_filename("fílè.txt")
    assert not file_utils.is_safe_filename("../etc/passwd")
    assert not file_utils.is_safe_filename("..\\windows\\system32.dll")
    assert not file_utils.is_safe_filename("folder/file.txt")
    assert not file_utils.is_safe_filename("folder\\file.txt")
    assert not file_utils.is_safe_filename("file:name.txt")
    assert not file_utils.is_safe_filename("file*?<>|.txt")
    assert not file_utils.is_safe_filename("..")
    assert not file_utils.is_safe_filename("")

def test_is_safe_filename_edge_cases():
    # Only dangerous chars
    assert not file_utils.is_safe_filename("..")
    assert not file_utils.is_safe_filename("..\\..\\..")
    assert not file_utils.is_safe_filename("file*?<>|.txt")
    # Unicode and spaces are allowed
    assert file_utils.is_safe_filename("fílè nâmé.txt")
    # None is not a valid filename
    assert not file_utils.is_safe_filename(None)
