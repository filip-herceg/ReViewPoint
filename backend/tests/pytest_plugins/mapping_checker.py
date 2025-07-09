"""
Pytest plugin to enforce 1:1 mapping between backend source files and test files.
- For every file in backend/src/, there must be a corresponding test file in backend/tests/ (and vice versa).
- Mapping is strict: e.g., src/models/foo.py <-> tests/models/test_foo.py
- Reports missing, extra, or multiply-mapped files as pytest warnings/errors.
"""

import os
import pathlib
from typing import Final

import pytest
from pytest import StashKey

# Unique stash key for mapping check result
MAPPING_CHECK_RESULT_KEY: StashKey["MappingCheckResult"] = StashKey()

SRC_ROOT: Final[pathlib.Path] = pathlib.Path(__file__).parents[2] / "src"
TESTS_ROOT: Final[pathlib.Path] = pathlib.Path(__file__).parents[1]

IGNORED_FILES: Final[set[str]] = {"__init__.py", "__about__.py"}
IGNORED_TEST_FILES: Final[set[str]] = {"__init__.py"}

# List of (src_name, test_name) tuples to permanently exclude from mapping check
EXCLUDED_MAPPINGS: Final[list[tuple[str, str]]] = [
    ("config.py", "conftest.py"),
    ("mapping_checker.py", "mapping_checker.py"),  # Exclude plugin itself at any level
    # Add more (src, test) pairs here as needed
]


def src_to_test_path(src_path: pathlib.Path) -> pathlib.Path | None:
    """Given a src file path, return the expected test file path."""
    rel: pathlib.Path = src_path.relative_to(SRC_ROOT)
    if rel.name in IGNORED_FILES:
        return None
    test_name: str = (
        f"test_{rel.name}" if not rel.name.startswith("test_") else rel.name
    )
    return TESTS_ROOT / rel.parent / test_name


def test_to_src_path(test_path: pathlib.Path) -> pathlib.Path | None:
    """Given a test file path, return the expected src file path."""
    rel: pathlib.Path = test_path.relative_to(TESTS_ROOT)
    if rel.name in IGNORED_TEST_FILES:
        return None
    src_name: str = rel.name[5:] if rel.name.startswith("test_") else rel.name
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
    """Result container for mapping check between source and test files."""

    missing_tests: list[tuple[pathlib.Path, pathlib.Path]]
    missing_sources: list[tuple[pathlib.Path, pathlib.Path]]
    multiply_mapped: list[pathlib.Path]
    src_files: int
    test_files: int
    checked: bool

    def __init__(self: "MappingCheckResult") -> None:
        self.missing_tests = []
        self.missing_sources = []
        self.multiply_mapped = []
        self.src_files = 0
        self.test_files = 0
        self.checked = False


def pytest_sessionstart(session: pytest.Session) -> None:
    """Pytest hook: check 1:1 mapping between source and test files at session start."""
    result: MappingCheckResult = MappingCheckResult()
    src_files: set[pathlib.Path] = collect_py_files(SRC_ROOT, IGNORED_FILES)
    test_files: set[pathlib.Path] = collect_py_files(TESTS_ROOT, IGNORED_TEST_FILES)
    result.src_files = len(src_files)
    result.test_files = len(test_files)

    test_to_src: dict[pathlib.Path, pathlib.Path] = {}
    src_to_test: dict[pathlib.Path, pathlib.Path] = {}

    # Check src -> test
    for src in src_files:
        test: pathlib.Path | None = src_to_test_path(src)
        if test is not None:
            src_to_test[src] = test
            if not test.exists():
                result.missing_tests.append((src, test))

    # Check test -> src
    for test in test_files:
        src_path: pathlib.Path | None = test_to_src_path(test)
        if src_path is not None:
            test_to_src[test] = src_path
            if not src_path.exists():
                result.missing_sources.append((test, src_path))

    # Check for multiply-mapped (should not happen with strict naming)
    test_targets: list[pathlib.Path] = list(src_to_test.values())
    if len(test_targets) != len(set(test_targets)):
        from collections import Counter

        c: Counter[pathlib.Path] = Counter(test_targets)
        for t, count in c.items():
            if count > 1:
                result.multiply_mapped.append(t)

    result.checked = True
    # Use pytest's config.stash to store the result in a type-safe way
    # Requires pytest >=7.2
    if hasattr(session.config, "stash"):
        session.config.stash[MAPPING_CHECK_RESULT_KEY] = result
    else:
        # Fallback for older pytest: do nothing or raise
        pass
    # Do not print or exit here; summary will be shown at the end.


def pytest_terminal_summary(
    terminalreporter: "pytest.TerminalReporter", exitstatus: int, config: pytest.Config
) -> None:
    """Pytest hook: print summary of 1:1 mapping check between source and test files."""
    result: MappingCheckResult | None = None
    if hasattr(config, "stash") and MAPPING_CHECK_RESULT_KEY in config.stash:
        result = config.stash[MAPPING_CHECK_RESULT_KEY]
    if not result or not result.checked:
        return
    term = terminalreporter

    def color(text: str, color: str) -> str:
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

    def is_excluded(src: pathlib.Path, test: pathlib.Path) -> bool:
        return (src.name, test.name) in EXCLUDED_MAPPINGS

    missing_tests: list[tuple[pathlib.Path, pathlib.Path]] = [
        (src, test) for src, test in result.missing_tests if not is_excluded(src, test)
    ]
    missing_sources: list[tuple[pathlib.Path, pathlib.Path]] = [
        (test, src)
        for test, src in result.missing_sources
        if not is_excluded(src, test)
    ]
    # Remove test files from missing_sources if their name is in any test name in EXCLUDED_MAPPINGS
    excluded_test_names: set[str] = {test for _, test in EXCLUDED_MAPPINGS}
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

    def paint_path(path: pathlib.Path, root: pathlib.Path) -> str:
        rel: pathlib.Path = path.relative_to(root)
        parts: tuple[str, ...] = rel.parts
        if len(parts) > 1:
            return os.path.join(*parts[:-1]) + os.sep + color(parts[-1], "red")
        elif len(parts) == 1:
            return color(parts[-1], "red")
        else:
            return color(str(rel), "red")

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
            for _src, _test in missing_tests:
                term.write_line(f"  {paint_path(_src, SRC_ROOT)}")
        if missing_sources:
            term.write_line("")
            term.write_line(
                color(
                    f"Test files with no corresponding source file ({len(missing_sources)}):",
                    "yellow",
                )
            )
            for test, _src in missing_sources:
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
