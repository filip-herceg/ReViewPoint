"""
Test Isolation Diagnostic Script

This script helps demonstrate and debug test isolation issues by:
1. Running individual failing tests to confirm they pass in isolation
2. Running failing tests together to reproduce the issue
3. Capturing detailed database state between tests
4. Providing specific fix recommendations
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of running a test or test group."""

    name: str
    passed: bool
    output: str
    exit_code: int
    duration: float


class TestIsolationDiagnostic:
    """Diagnoses test isolation issues by running tests individually and together."""

    def __init__(self, backend_dir: str):
        self.backend_dir = Path(backend_dir)
        self.test_results: List[TestResult] = []

    from typing import Optional

    def run_single_test(
        self, test_path: str, test_name: Optional[str] = None
    ) -> TestResult:
        """Run a single test and capture results."""
        import time

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            test_path,
            "-v",
            "--tb=short",
            "--no-header",
        ]

        if test_name:
            cmd.extend(["-k", test_name])

        cmd.extend(["--tb=short", "-x"])  # Stop on first failure

        print(f"Running: {' '.join(cmd)}")

        start_time = time.time()
        result = subprocess.run(
            cmd,
            cwd=self.backend_dir,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
        )
        duration = time.time() - start_time

        test_result = TestResult(
            name=f"{test_path}::{test_name}" if test_name else test_path,
            passed=result.returncode == 0,
            output=result.stdout + result.stderr,
            exit_code=result.returncode,
            duration=duration,
        )

        self.test_results.append(test_result)
        return test_result

    def run_test_group(
        self, test_paths: List[str], group_name: str = "group"
    ) -> TestResult:
        """Run multiple tests together and capture results."""
        import time

        cmd = (
            [sys.executable, "-m", "pytest"]
            + test_paths
            + ["-v", "--tb=short", "--no-header", "-x"]
        )

        print(f"Running group '{group_name}': {' '.join(cmd)}")

        start_time = time.time()
        result = subprocess.run(
            cmd,
            cwd=self.backend_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        duration = time.time() - start_time

        test_result = TestResult(
            name=f"GROUP_{group_name}",
            passed=result.returncode == 0,
            output=result.stdout + result.stderr,
            exit_code=result.returncode,
            duration=duration,
        )

        self.test_results.append(test_result)
        return test_result

    def diagnose_auth_isolation_issue(self) -> Dict[str, TestResult]:
        """Specifically diagnose the auth test isolation issue."""
        results = {}

        auth_test_file = "tests/api/v1/test_auth.py"

        # Test individual auth tests that are known to fail in groups
        individual_tests = [
            "test_register_and_login",
            "test_me_and_logout",
            "test_register_duplicate_email",
            "test_password_reset_request_and_confirm",
        ]

        print("=" * 80)
        print("DIAGNOSING AUTH TEST ISOLATION ISSUES")
        print("=" * 80)

        # 1. Run each test individually
        print("\n1. Running individual tests (should all pass):")
        print("-" * 50)

        for test_name in individual_tests:
            try:
                result = self.run_single_test(auth_test_file, test_name)
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"  {test_name}: {status} ({result.duration:.2f}s)")
                results[f"individual_{test_name}"] = result
            except Exception as e:
                print(f"  {test_name}: ❌ ERROR - {e}")

        # 2. Run them all together
        print(
            "\n2. Running all auth tests together (may fail due to isolation issues):"
        )
        print("-" * 50)

        try:
            group_result = self.run_test_group([auth_test_file], "all_auth_tests")
            status = "✅ PASS" if group_result.passed else "❌ FAIL"
            print(f"  All auth tests: {status} ({group_result.duration:.2f}s)")
            results["group_all_auth"] = group_result
        except Exception as e:
            print(f"  All auth tests: ❌ ERROR - {e}")

        # 3. Run a specific problematic combination
        print("\n3. Running specific problematic combination:")
        print("-" * 50)

        # Run two tests that likely conflict (both use user@example.com)
        problematic_tests = [
            f"{auth_test_file}::test_register_and_login",
            f"{auth_test_file}::test_register_duplicate_email",
        ]

        try:
            combo_result = self.run_test_group(problematic_tests, "problematic_combo")
            status = "✅ PASS" if combo_result.passed else "❌ FAIL"
            print(f"  Problematic combo: {status} ({combo_result.duration:.2f}s)")
            results["problematic_combo"] = combo_result
        except Exception as e:
            print(f"  Problematic combo: ❌ ERROR - {e}")

        return results

    def run_full_suite_partial(self) -> TestResult:
        """Run a partial test suite to identify which tests cause conflicts."""
        # Run tests that are likely to conflict with auth tests
        conflicting_tests = [
            "tests/api/v1/test_auth.py",
            "tests/models/test_user.py",
            "tests/core/test_database.py",
            "tests/repositories/test_user.py",
        ]

        print("\n4. Running potentially conflicting tests together:")
        print("-" * 50)

        try:
            result = self.run_test_group(conflicting_tests, "potential_conflicts")
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  Potential conflicts: {status} ({result.duration:.2f}s)")
            return result
        except Exception as e:
            print(f"  Potential conflicts: ❌ ERROR - {e}")
            return TestResult("potential_conflicts", False, str(e), 1, 0.0)

    def generate_diagnostic_report(self) -> str:
        """Generate a detailed diagnostic report."""
        report = []
        report.append("=" * 80)
        report.append("TEST ISOLATION DIAGNOSTIC REPORT")
        report.append("=" * 80)

        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests

        report.append(f"Total test runs: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append("")

        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 50)

        for result in self.test_results:
            status = "PASS" if result.passed else "FAIL"
            report.append(f"\n{result.name}: {status} ({result.duration:.2f}s)")
            report.append(f"Exit code: {result.exit_code}")

            if not result.passed:
                # Include relevant parts of the output
                lines = result.output.split("\n")
                error_lines = []

                for i, line in enumerate(lines):
                    if any(
                        keyword in line.lower()
                        for keyword in [
                            "error",
                            "fail",
                            "exception",
                            "traceback",
                            "assert",
                        ]
                    ):
                        # Include some context around error lines
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        error_lines.extend(lines[start:end])
                        error_lines.append("...")

                if error_lines:
                    report.append("Error output:")
                    for line in error_lines[:20]:  # Limit output
                        report.append(f"  {line}")

        # Analysis and recommendations
        report.append("\n\nANALYSIS:")
        report.append("-" * 50)

        individual_results = [r for r in self.test_results if "individual_" in r.name]
        group_results = [r for r in self.test_results if "GROUP_" in r.name]

        individual_passed = all(r.passed for r in individual_results)
        group_failed = any(not r.passed for r in group_results)

        if individual_passed and group_failed:
            report.append("✅ ISOLATION ISSUE CONFIRMED:")
            report.append("  - Individual tests pass when run alone")
            report.append("  - Same tests fail when run together")
            report.append("  - This indicates test isolation problems")
            report.append("")
            report.append("LIKELY CAUSES:")
            report.append(
                "  1. Hardcoded test data (emails, usernames) causing conflicts"
            )
            report.append("  2. Incomplete database cleanup between tests")
            report.append("  3. Shared state in application or test fixtures")
            report.append("  4. Database constraints (unique email, etc.)")
        elif not individual_passed:
            report.append("⚠️  INDIVIDUAL TEST FAILURES:")
            report.append("  - Some tests fail even when run individually")
            report.append("  - Fix individual test issues first")
        else:
            report.append("✅ NO ISOLATION ISSUES DETECTED:")
            report.append("  - All tests pass individually and in groups")

        report.append("\n\nRECOMMENDATIONS:")
        report.append("-" * 50)
        report.append("1. Replace hardcoded emails with UUID-based generation:")
        report.append("   email = f'test-{uuid.uuid4()}@example.com'")
        report.append("")
        report.append("2. Ensure proper test cleanup:")
        report.append("   - Use transactional tests that rollback automatically")
        report.append("   - Add explicit cleanup in test teardown")
        report.append("")
        report.append("3. Use test-specific data:")
        report.append("   - Generate unique test data for each test")
        report.append("   - Avoid sharing data between tests")

        return "\n".join(report)


def main():
    """Main diagnostic entry point."""
    backend_dir = Path(__file__).parent / "backend"

    if not backend_dir.exists():
        print(f"Error: Backend directory not found at {backend_dir}")
        sys.exit(1)

    diagnostic = TestIsolationDiagnostic(str(backend_dir))

    try:
        # Run the auth isolation diagnosis
        diagnostic.diagnose_auth_isolation_issue()

        # Run additional tests to confirm the scope of the problem
        diagnostic.run_full_suite_partial()

        # Generate and save report
        report = diagnostic.generate_diagnostic_report()

        report_file = Path("test_isolation_diagnostic.txt")
        report_file.write_text(report, encoding="utf-8")

        print(f"\n\nDiagnostic report saved to: {report_file.absolute()}")

        # Print summary
        total_tests = len(diagnostic.test_results)
        failed_tests = sum(1 for r in diagnostic.test_results if not r.passed)

        if failed_tests > 0:
            print(
                f"\n🔍 ISOLATION ISSUES DETECTED: {failed_tests}/{total_tests} test runs failed"
            )
            print(
                "Check the diagnostic report for detailed analysis and recommendations."
            )
        else:
            print(f"\n✅ NO ISOLATION ISSUES: All {total_tests} test runs passed")

    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
    except Exception as e:
        print(f"\n\nDiagnostic failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
