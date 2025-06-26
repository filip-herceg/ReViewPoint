"""
Pytest plugin to enforce 1:1 mapping between backend source files and test files.
- For every file in backend/src/, there must be a corresponding test file in backend/tests/ (and vice versa).
- Mapping is strict: e.g., src/models/foo.py <-> tests/models/test_foo.py
- Reports missing, extra, or multiply-mapped files as pytest warnings/errors.
"""

import os
import pathlib

import pytest

SRC_ROOT = pathlib.Path(__file__).parents[2] / "src"
TESTS_ROOT = pathlib.Path(__file__).parents[1]

IGNORED_FILES = {"__init__.py", "__about__.py"}
IGNORED_TEST_FILES = {"__init__.py"}

# List of (src_name, test_name) tuples to permanently exclude from mapping check
EXCLUDED_MAPPINGS = [
    ("config.py", "conftest.py"),
    ("mapping_checker.py", "mapping_checker.py"),  # Exclude plugin itself at any level
    # Add more (src, test) pairs here as needed
]


def src_to_test_path(src_path: pathlib.Path) -> pathlib.Path | None:
    """Given a src file path, return the expected test file path."""
    rel = src_path.relative_to(SRC_ROOT)
    if rel.name in IGNORED_FILES:
        return None
    test_name = f"test_{rel.name}" if not rel.name.startswith("test_") else rel.name
    return TESTS_ROOT / rel.parent / test_name


def test_to_src_path(test_path: pathlib.Path) -> pathlib.Path | None:
    """Given a test file path, return the expected src file path."""
    rel = test_path.relative_to(TESTS_ROOT)
    if rel.name in IGNORED_TEST_FILES:
        return None
    src_name = rel.name[5:] if rel.name.startswith("test_") else rel.name
    return SRC_ROOT / rel.parent / src_name


def collect_py_files(root: pathlib.Path, ignored: set[str]) -> set[pathlib.Path]:
    def is_in_excluded_dir(p: pathlib.Path) -> bool:
        # Exclude any file under alembic_migrations/versions
        return any(
            str(p).replace("\\", "/").endswith(suffix)
            or "/alembic_migrations/versions/" in str(p).replace("\\", "/")
            for suffix in [
                "/alembic_migrations/versions",
                "/alembic_migrations/versions/",
            ]
        )

    return {
        p
        for p in root.rglob("*.py")
        if p.is_file()
        and p.name not in ignored
        and not any(part.startswith(".") or part == "__pycache__" for part in p.parts)
        and not is_in_excluded_dir(p)
    }


class MappingCheckResult:
    def __init__(self):
        self.missing_tests: list[tuple[pathlib.Path, pathlib.Path]] = []
        self.missing_sources: list[tuple[pathlib.Path, pathlib.Path]] = []
        self.multiply_mapped: list[pathlib.Path] = []
        self.src_files: int = 0
        self.test_files: int = 0
        self.checked: bool = False


def pytest_sessionstart(session: pytest.Session) -> None:
    result = MappingCheckResult()
    src_files: set[pathlib.Path] = collect_py_files(SRC_ROOT, IGNORED_FILES)
    test_files: set[pathlib.Path] = collect_py_files(TESTS_ROOT, IGNORED_TEST_FILES)
    result.src_files = len(src_files)
    result.test_files = len(test_files)

    test_to_src: dict[pathlib.Path, pathlib.Path] = {}
    src_to_test: dict[pathlib.Path, pathlib.Path] = {}

    # Check src -> test
    for src in src_files:
        test = src_to_test_path(src)
        if test is None:
            continue
        src_to_test[src] = test
        if not test.exists():
            result.missing_tests.append((src, test))

    # Check test -> src
    for test in test_files:
        src = test_to_src_path(test)
        if src is None:
            continue
        test_to_src[test] = src
        if not src.exists():
            result.missing_sources.append((test, src))

    # Check for multiply-mapped (should not happen with strict naming)
    test_targets = list(src_to_test.values())
    if len(test_targets) != len(set(test_targets)):
        from collections import Counter

        c = Counter(test_targets)
        for t, count in c.items():
            if count > 1:
                result.multiply_mapped.append(t)

    result.checked = True
    session.config._mapping_check_result = result
    # Do not print or exit here; summary will be shown at the end.


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    result = getattr(config, "_mapping_check_result", None)
    if not result or not result.checked:
        return
    term = terminalreporter

    def color(text, color):
        return (
            "\x1b["
            + {
                "red": "31",
                "green": "32",
                "yellow": "33",
                "blue": "34",
                "magenta": "35",
                "cyan": "36",
            }.get(color, "0")
            + "m"
            + text
            + "\x1b[0m"
        )

    def is_excluded(src, test):
        return (src.name, test.name) in EXCLUDED_MAPPINGS

    missing_tests = [
        (src, test) for src, test in result.missing_tests if not is_excluded(src, test)
    ]
    missing_sources = [
        (test, src)
        for test, src in result.missing_sources
        if not is_excluded(src, test)
    ]
    # Remove test files from missing_sources if their name is in any test name in EXCLUDED_MAPPINGS
    excluded_test_names = {test for _, test in EXCLUDED_MAPPINGS}
    missing_sources = [
        (test, src)
        for test, src in missing_sources
        if test.name not in excluded_test_names
    ]

    # Sort missing_tests and missing_sources alphabetically by relative path
    missing_tests = sorted(
        missing_tests, key=lambda pair: str(pair[0].relative_to(SRC_ROOT))
    )
    missing_sources = sorted(
        missing_sources, key=lambda pair: str(pair[0].relative_to(TESTS_ROOT))
    )

    def paint_path(path, root):
        rel = path.relative_to(root)
        parts = rel.parts
        if len(parts) > 1:
            return os.path.join(*parts[:-1]) + os.sep + color(parts[-1], "red")
        else:
            return color(parts[-1], "red")

    if missing_tests or missing_sources or result.multiply_mapped:
        # Use default pytest section separator (let pytest handle width and color)
        term.section(color("1:1 Source-Test Mapping Errors Detected", "yellow"))
        if missing_tests:
            term.write_line("")
            term.write_line(
                color(
                    f"Missing test files for ({len(missing_tests)}) source file(s):",
                    "yellow",
                )
            )
            for src, test in missing_tests:
                term.write_line(f"  {paint_path(src, SRC_ROOT)}")
        if missing_sources:
            term.write_line("")
            term.write_line(
                color(
                    f"Test files with no corresponding source file ({len(missing_sources)}):",
                    "yellow",
                )
            )
            for test, src in missing_sources:
                term.write_line(f"  {paint_path(test, TESTS_ROOT)}")
        if result.multiply_mapped:
            term.write_line("")
            term.write_line(
                color(
                    f"Multiply-mapped test files ({len(result.multiply_mapped)}):",
                    "yellow",
                )
            )
            for t in sorted(
                result.multiply_mapped, key=lambda p: str(p.relative_to(TESTS_ROOT))
            ):
                term.write_line(f"  {paint_path(t, TESTS_ROOT)}")
        term.write_line("")
        term.write_line(color("Please fix the mapping errors above.", "red"))
    else:
        if term.verbosity > 0:
            term.section(
                color(
                    "[pytest-mapping-checker] 1:1 source-test mapping check PASSED",
                    "green",
                ),
                sep="-",
            )
            term.write_line(
                color(f"  Total source files checked: {result.src_files}", "green")
            )
            term.write_line(
                color(f"  Total test files checked:   {result.test_files}", "green")
            )
            term.write_line(
                color(
                    "  All source files have matching test files and vice versa.",
                    "green",
                )
            )
        else:
            term.write_line(
                color(
                    "[pytest-mapping-checker] 1:1 source-test mapping check PASSED: every source file has a matching test file and vice versa.",
                    "green",
                )
            )
