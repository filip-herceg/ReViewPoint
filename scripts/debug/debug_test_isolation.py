"""
Test Isolation Debugging Tools

This script helps identify test isolation issues by analyzing test patterns,
database state, and creating detailed debugging reports.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TestIsolationIssue:
    """Represents a potential test isolation issue."""

    test_file: str
    test_method: str
    issue_type: str
    description: str
    hardcoded_values: List[str]
    line_numbers: List[int]
    severity: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class DatabaseUsagePattern:
    """Represents how a test uses the database."""

    test_file: str
    test_method: str
    creates_users: bool
    uses_hardcoded_emails: bool
    hardcoded_emails: List[str]
    has_cleanup: bool
    cleanup_methods: List[str]


class TestIsolationAnalyzer:
    """Analyzes test files for isolation issues."""

    def __init__(self, test_directory: str):
        self.test_directory = Path(test_directory)
        self.issues: List[TestIsolationIssue] = []
        self.patterns: List[DatabaseUsagePattern] = []

        # Common hardcoded test data patterns
        self.hardcoded_email_patterns = [
            r'"[^"]*@example\.com"',
            r"'[^']*@example\.com'",
            r'"[^"]*@test\.com"',
            r"'[^']*@test\.com'",
            r'"test.*@.*"',
            r"'test.*@.*'",
        ]

        # Patterns that indicate user creation
        self.user_creation_patterns = [
            r"register.*json.*email",
            r"create.*user",
            r"User\(",
            r"\.add\(.*user",
            r"/auth/register",
        ]

        # Patterns that indicate cleanup
        self.cleanup_patterns = [
            r"truncate",
            r"delete.*from",
            r"DROP.*TABLE",
            r"rollback",
            r"teardown",
            r"@pytest\.fixture.*teardown",
        ]

    def analyze_test_file(self, file_path: Path) -> List[TestIsolationIssue]:
        """Analyze a single test file for isolation issues."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Find hardcoded emails
            self._find_hardcoded_emails(content, lines)

            # Find test methods
            test_methods = self._find_test_methods(content, lines)

            # Check for user creation without cleanup
            self._check_user_creation(content)
            has_cleanup = self._check_cleanup_patterns(content)

            # Analyze each test method
            for method_name, method_lines in test_methods.items():
                method_content = "\n".join(lines[method_lines[0] : method_lines[1]])
                method_emails = self._find_hardcoded_emails(
                    method_content, lines[method_lines[0] : method_lines[1]]
                )

                if method_emails:
                    issues.append(
                        TestIsolationIssue(
                            test_file=str(file_path.relative_to(self.test_directory)),
                            test_method=method_name,
                            issue_type="HARDCODED_EMAIL",
                            description=f"Uses hardcoded emails: {', '.join(method_emails)}",
                            hardcoded_values=method_emails,
                            line_numbers=[
                                i
                                for i, line in enumerate(lines)
                                if any(email in line for email in method_emails)
                            ],
                            severity="HIGH",
                        )
                    )

                # Check if creates users without cleanup
                if (
                    self._check_user_creation(method_content)
                    and not self._check_cleanup_patterns(method_content)
                    and not has_cleanup
                ):
                    issues.append(
                        TestIsolationIssue(
                            test_file=str(file_path.relative_to(self.test_directory)),
                            test_method=method_name,
                            issue_type="NO_CLEANUP",
                            description="Creates users but has no cleanup mechanism",
                            hardcoded_values=[],
                            line_numbers=[method_lines[0]],
                            severity="HIGH",
                        )
                    )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _find_hardcoded_emails(self, content: str, lines: List[str]) -> List[str]:
        """Find hardcoded email addresses in content."""
        emails = set()

        for pattern in self.hardcoded_email_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the match (remove quotes)
                clean_email = match.strip("\"'")
                emails.add(clean_email)

        return list(emails)

    def _find_test_methods(
        self, content: str, lines: List[str]
    ) -> Dict[str, Tuple[int, int]]:
        """Find test methods and their line ranges."""
        methods = {}

        for i, line in enumerate(lines):
            if re.match(r"\s*(async\s+)?def\s+test_", line):
                method_name = re.search(r"def\s+(test_\w+)", line)
                if method_name:
                    # Find the end of the method (next def or class, or end of file)
                    end_line = len(lines)
                    for j in range(i + 1, len(lines)):
                        if re.match(r"\s*(def|class)", lines[j]) and not lines[
                            j
                        ].strip().startswith("#"):
                            end_line = j
                            break

                    methods[method_name.group(1)] = (i, end_line)

        return methods

    def _check_user_creation(self, content: str) -> bool:
        """Check if content contains user creation patterns."""
        for pattern in self.user_creation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _check_cleanup_patterns(self, content: str) -> bool:
        """Check if content contains cleanup patterns."""
        for pattern in self.cleanup_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def analyze_all_tests(self) -> List[TestIsolationIssue]:
        """Analyze all test files in the directory."""
        all_issues = []

        # Find all test files
        test_files = list(self.test_directory.rglob("test_*.py"))

        print(f"Analyzing {len(test_files)} test files...")

        for test_file in test_files:
            if "test_templates" in str(test_file):
                continue  # Skip template files

            print(f"Analyzing: {test_file.relative_to(self.test_directory)}")
            file_issues = self.analyze_test_file(test_file)
            all_issues.extend(file_issues)

        self.issues = all_issues
        return all_issues

    def generate_report(self) -> str:
        """Generate a detailed report of isolation issues."""
        report = []
        report.append("=" * 80)
        report.append("TEST ISOLATION ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Total issues found: {len(self.issues)}")
        report.append("")

        # Group by severity
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        for severity in ["HIGH", "MEDIUM", "LOW"]:
            if severity not in by_severity:
                continue

            report.append(
                f"\n{severity} PRIORITY ISSUES ({len(by_severity[severity])})"
            )
            report.append("-" * 50)

            # Group by issue type
            by_type = defaultdict(list)
            for issue in by_severity[severity]:
                by_type[issue.issue_type].append(issue)

            for issue_type, issues in by_type.items():
                report.append(f"\n{issue_type} ({len(issues)} issues):")

                for issue in issues:
                    report.append(f"  • {issue.test_file}::{issue.test_method}")
                    report.append(f"    {issue.description}")
                    if issue.hardcoded_values:
                        report.append(
                            f"    Values: {', '.join(issue.hardcoded_values)}"
                        )
                    if issue.line_numbers:
                        report.append(
                            f"    Lines: {', '.join(map(str, issue.line_numbers[:5]))}"
                        )
                    report.append("")

        # Summary and recommendations
        report.append("\nRECOMMENDations:")
        report.append("-" * 50)

        hardcoded_email_issues = [
            i for i in self.issues if i.issue_type == "HARDCODED_EMAIL"
        ]
        if hardcoded_email_issues:
            report.append("1. Replace hardcoded emails with UUID-based generation:")
            report.append("   email = f'test-{uuid.uuid4()}@example.com'")
            report.append("")

        no_cleanup_issues = [i for i in self.issues if i.issue_type == "NO_CLEANUP"]
        if no_cleanup_issues:
            report.append(
                "2. Add proper test cleanup using fixtures or teardown methods"
            )
            report.append("3. Use transactional tests that rollback automatically")
            report.append("")

        return "\n".join(report)

    def generate_fixes(self) -> Dict[str, List[str]]:
        """Generate suggested fixes for each file."""
        fixes_by_file = defaultdict(list)

        for issue in self.issues:
            if issue.issue_type == "HARDCODED_EMAIL":
                fixes_by_file[issue.test_file].append(
                    f"Replace hardcoded emails in {issue.test_method} with UUID-based generation"
                )
            elif issue.issue_type == "NO_CLEANUP":
                fixes_by_file[issue.test_file].append(
                    f"Add cleanup mechanism to {issue.test_method}"
                )

        return dict(fixes_by_file)


def main():
    """Main entry point for the analyzer."""
    if len(sys.argv) > 1:
        test_dir = sys.argv[1]
    else:
        # Default to backend/tests directory
        test_dir = Path(__file__).parent.parent / "backend" / "tests"

    analyzer = TestIsolationAnalyzer(str(test_dir))
    issues = analyzer.analyze_all_tests()

    # Generate and save report
    report = analyzer.generate_report()

    report_file = Path("test_isolation_report.txt")
    report_file.write_text(report, encoding="utf-8")

    print(f"\nReport saved to: {report_file.absolute()}")
    print(f"Found {len(issues)} isolation issues")

    # Print summary
    print("\nSUMMARY:")
    by_type = defaultdict(int)
    for issue in issues:
        by_type[issue.issue_type] += 1

    for issue_type, count in by_type.items():
        print(f"  {issue_type}: {count}")

    return issues


if __name__ == "__main__":
    main()
