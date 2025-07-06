from src.utils import file as file_utils
from tests.test_templates import UtilityUnitTestTemplate
from typing import Final


class TestFileUtils(UtilityUnitTestTemplate):
    def test_sanitize_filename_basic(self) -> None:
        """
        Test that sanitize_filename returns safe filenames for common cases.
        """
        self.assert_equal(file_utils.sanitize_filename("file.txt"), "file.txt")
        self.assert_equal(file_utils.sanitize_filename("../etc/passwd"), "etc_passwd")
        self.assert_equal(
            file_utils.sanitize_filename("..\\windows\\system32.dll"),
            "windows_system32.dll",
        )
        self.assert_equal(
            file_utils.sanitize_filename("folder/file.txt"), "folder_file.txt"
        )
        self.assert_equal(
            file_utils.sanitize_filename("folder\\file.txt"), "folder_file.txt"
        )
        self.assert_equal(
            file_utils.sanitize_filename("file:name.txt"), "file_name.txt"
        )
        self.assert_equal(file_utils.sanitize_filename(""), "unnamed_file")

    def test_sanitize_filename_edge_cases(self) -> None:
        """
        Test sanitize_filename with edge cases and dangerous input.
        """
        # Only dangerous chars
        self.assert_equal(file_utils.sanitize_filename(".."), "_")
        self.assert_equal(file_utils.sanitize_filename("..\\..\\.."), "_")
        self.assert_equal(
            file_utils.sanitize_filename("file*?<>|.txt"), "file_____.txt"
        )
        # Double dots in name
        self.assert_equal(file_utils.sanitize_filename("foo..bar.txt"), "foo_bar.txt")
        # Path traversal with mixed slashes
        self.assert_equal(
            file_utils.sanitize_filename("..\\folder/../evil.txt"), "folder_evil.txt"
        )
        # Unicode and spaces
        self.assert_equal(
            file_utils.sanitize_filename("fílè nâmé.txt"), "fílè nâmé.txt"
        )

    def test_is_safe_filename_basic(self) -> None:
        """
        Test is_safe_filename for common safe and unsafe filenames.
        """
        self.assert_is_true(file_utils.is_safe_filename("file.txt"))
        self.assert_is_true(file_utils.is_safe_filename("file_name.txt"))
        self.assert_is_true(file_utils.is_safe_filename("fílè.txt"))
        self.assert_is_false(file_utils.is_safe_filename("../etc/passwd"))
        self.assert_is_false(file_utils.is_safe_filename("..\\windows\\system32.dll"))
        self.assert_is_false(file_utils.is_safe_filename("folder/file.txt"))
        self.assert_is_false(file_utils.is_safe_filename("folder\\file.txt"))
        self.assert_is_false(file_utils.is_safe_filename("file:name.txt"))
        self.assert_is_false(file_utils.is_safe_filename("file*?<>|.txt"))
        self.assert_is_false(file_utils.is_safe_filename(".."))
        self.assert_is_false(file_utils.is_safe_filename(""))
        # Predicate helpers (demonstration)
        self.assert_predicate_true(file_utils.is_safe_filename, "file.txt")
        self.assert_predicate_false(file_utils.is_safe_filename, "../etc/passwd")

    def test_is_safe_filename_edge_cases(self) -> None:
        """
        Test is_safe_filename with edge cases and dangerous input.
        """
        # Only dangerous chars
        self.assert_is_false(file_utils.is_safe_filename(".."))
        self.assert_is_false(file_utils.is_safe_filename("..\\..\\.."))
        self.assert_is_false(file_utils.is_safe_filename("file*?<>|.txt"))
        # Unicode and spaces are allowed
        self.assert_is_true(file_utils.is_safe_filename("fílè nâmé.txt"))
        # Predicate helpers (demonstration)
        self.assert_predicate_true(file_utils.is_safe_filename, "fílè nâmé.txt")
        self.assert_predicate_false(file_utils.is_safe_filename, "..\\..\\..")
