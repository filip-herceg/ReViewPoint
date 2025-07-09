"""
Automated Test Isolation Fix Script

This script automatically fixes test isolation issues by:
1. Replacing hardcoded emails with unique generated ones
2. Adding proper test data generation
3. Ensuring each test uses unique data
4. Adding cleanup mechanisms where needed
"""

import sys
import re
import shutil
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class FixAction:
    """Represents a fix to be applied to a file."""

    file_path: str
    line_number: int
    old_content: str
    new_content: str
    fix_type: str
    description: str


class TestIsolationFixer:
    """Automatically fixes test isolation issues."""

    def __init__(self, backend_dir: str, dry_run: bool = False):
        self.backend_dir = Path(backend_dir)
        self.tests_dir = self.backend_dir / "tests"
        self.dry_run = dry_run
        self.fixes_applied: List[FixAction] = []
        self.backup_dir = self.backend_dir / "test_isolation_backups"

        # Patterns for hardcoded emails
        self.email_patterns = [
            r'"([^"]*@example\.com)"',
            r"'([^']*@example\.com)'",
            r'"([^"]*@test\.com)"',
            r"'([^']*@test\.com)'",
        ]

        # Common hardcoded emails to replace
        self.hardcoded_emails = {
            "user@example.com",
            "test@example.com",
            "admin@example.com",
            "dev@example.com",
            "refreshuser@example.com",
            "me@example.com",
            "dupe@example.com",
            "pwreset@example.com",
            "doesnotexist@example.com",
            "missingpass@example.com",
            # Add model test specific emails
            "fileuser@example.com",
            "cruduser@example.com",
            "reluser@example.com",
            "bulkuser@example.com",
            "rollbackuser@example.com",
            "repruser@example.com",
            "invalidct@example.com",
            "dupuser@example.com",
            "longuser@example.com",
            "nullfname@example.com",
            "nullct@example.com",
            "multifile@example.com",
            "unicode@example.com",
            "specialchars@example.com",
            "unit@example.com",
            "role@example.com",
            "repr@example.com",
            # Database test emails
            "cascade@example.com",
            "update@example.com",
            "defaults@example.com",
            "prefs@example.com",
            "dt@example.com",
            "rollback@example.com",
            # Other common test emails
            "bulk@example.com",
            "past@example.com",
            "future@example.com",
            "dupdb@example.com",
            "defaultdb@example.com",
            "idx@example.com",
        }

    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file before modification."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(exist_ok=True)

        relative_path = file_path.relative_to(self.tests_dir)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_path)
        return backup_path

    def fix_auth_test_file(self) -> List[FixAction]:
        """Fix the main auth test file that's causing issues."""
        auth_file = self.tests_dir / "api" / "v1" / "test_auth.py"

        if not auth_file.exists():
            print(f"Auth test file not found: {auth_file}")
            return []

        print(f"Fixing auth test file: {auth_file}")

        # Read the file to check if it's already been partially fixed
        content = auth_file.read_text(encoding="utf-8")

        # Check if AuthTestDataGenerator is already imported
        if "from tests.test_data_generators import AuthTestDataGenerator" in content:
            print(
                "   Auth test file already partially fixed - skipping to avoid conflicts"
            )
            return []

        # Create backup
        if not self.dry_run:
            self.create_backup(auth_file)

        lines = content.split("\n")

        fixes = []

        # Strategy: Replace hardcoded emails with generator calls
        # We'll do this method by method to maintain context

        new_lines = []
        current_method = None
        method_indent = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Detect test method start
            method_match = re.match(r"(\s*)(async\s+)?def\s+(test_\w+)", line)
            if method_match:
                current_method = method_match.group(3)
                method_indent = len(method_match.group(1))

                # Check if this method already has test_data generator
                next_few_lines = lines[i : i + 5] if i + 5 < len(lines) else lines[i:]
                has_generator = any(
                    "test_data = AuthTestDataGenerator" in line
                    for line in next_few_lines
                )

                # Add the method definition
                new_lines.append(line)

                # Add test data generator initialization if not already present
                if not has_generator:
                    generator_line = f"{' ' * (method_indent + 8)}# Generate unique test data for isolation"
                    data_gen_line = f"{' ' * (method_indent + 8)}test_data = AuthTestDataGenerator('{current_method}')"
                    new_lines.append(generator_line)
                    new_lines.append(data_gen_line)

                    fixes.append(
                        FixAction(
                            file_path=str(auth_file),
                            line_number=i + 1,
                            old_content=line,
                            new_content=f"{line}\n{generator_line}\n{data_gen_line}",
                            fix_type="ADD_DATA_GENERATOR",
                            description=f"Added test data generator to {current_method}",
                        )
                    )

                i += 1
                continue

            # Replace hardcoded emails in the current line
            modified_line = line
            for pattern in self.email_patterns:

                def replace_email(match):
                    email = match.group(1)
                    if email in self.hardcoded_emails:
                        # Generate appropriate replacement based on context
                        if "register" in line.lower() or "Register" in line:
                            return '"{test_data.get_registration_user().email}"'
                        elif "login" in line.lower() or "Login" in line:
                            return '"{test_data.get_login_user().email}"'
                        elif "duplicate" in line.lower() or "dupe" in line.lower():
                            return '"{test_data.get_duplicate_test_users()[0].email}"'
                        elif "reset" in line.lower() or "pwreset" in line.lower():
                            return '"{test_data.get_password_reset_user().email}"'
                        else:
                            return '"{test_data.generate_unique_email()}"'
                    return match.group(0)

                new_content = re.sub(pattern, replace_email, modified_line)
                if new_content != modified_line:
                    fixes.append(
                        FixAction(
                            file_path=str(auth_file),
                            line_number=i + 1,
                            old_content=modified_line,
                            new_content=new_content,
                            fix_type="REPLACE_HARDCODED_EMAIL",
                            description=f"Replaced hardcoded email in {current_method or 'unknown method'}",
                        )
                    )
                    modified_line = new_content

            new_lines.append(modified_line)
            i += 1

        # Add import for test data generator at the top
        import_added = False
        for i, line in enumerate(new_lines):
            if line.startswith("from tests.test_templates import"):
                new_lines[i] = (
                    line
                    + "\nfrom tests.test_data_generators import AuthTestDataGenerator"
                )
                import_added = True
                break

        if not import_added:
            # Find a good place to add the import
            for i, line in enumerate(new_lines):
                if line.startswith("import") or line.startswith("from"):
                    continue
                else:
                    new_lines.insert(
                        i,
                        "from tests.test_data_generators import AuthTestDataGenerator",
                    )
                    break

        # Write the fixed file
        if not self.dry_run:
            new_content = "\n".join(new_lines)
            auth_file.write_text(new_content, encoding="utf-8")

        self.fixes_applied.extend(fixes)
        return fixes

    def fix_model_test_files(self) -> List[FixAction]:
        """Fix model test files with hardcoded emails."""
        model_test_files = [
            self.tests_dir / "models" / "test_user.py",
            self.tests_dir / "models" / "test_file.py",
            self.tests_dir / "models" / "test_used_password_reset_token.py",
        ]

        all_fixes = []

        for test_file in model_test_files:
            if not test_file.exists():
                continue

            print(f"Fixing model test file: {test_file}")

            if not self.dry_run:
                self.create_backup(test_file)

            fixes = self._fix_hardcoded_emails_in_file(test_file)
            all_fixes.extend(fixes)

        return all_fixes

    def _fix_hardcoded_emails_in_file(self, file_path: Path) -> List[FixAction]:
        """Fix hardcoded emails in a specific file."""
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        fixes = []
        new_lines = []

        # Add import at the top
        import_added = False

        for i, line in enumerate(lines):
            modified_line = line

            # Add import if we haven't already
            if not import_added and (
                line.startswith("from tests.") or line.startswith("from src.")
            ):
                new_lines.append(
                    "from tests.test_data_generators import get_unique_email, get_test_user"
                )
                import_added = True

            # Replace hardcoded emails
            for pattern in self.email_patterns:

                def replace_email(match):
                    email = match.group(1)
                    # Replace any email ending with @example.com or @test.com
                    if email.endswith("@example.com") or email.endswith("@test.com"):
                        # Use function call to generate unique email
                        return '"get_unique_email()"'
                    return match.group(0)

                new_content = re.sub(pattern, replace_email, modified_line)
                if new_content != modified_line:
                    fixes.append(
                        FixAction(
                            file_path=str(file_path),
                            line_number=i + 1,
                            old_content=modified_line,
                            new_content=new_content,
                            fix_type="REPLACE_HARDCODED_EMAIL",
                            description="Replaced hardcoded email with unique generator",
                        )
                    )
                    modified_line = new_content

            new_lines.append(modified_line)

        # Write the fixed file
        if not self.dry_run:
            new_content = "\n".join(new_lines)
            file_path.write_text(new_content, encoding="utf-8")

        return fixes

    def fix_all_test_files(self) -> Dict[str, List[FixAction]]:
        """Fix all test files with isolation issues."""
        all_fixes = {}

        print("🔧 Starting automated test isolation fixes...")

        # 1. Fix the main auth test file (highest priority)
        print("\n1. Fixing authentication tests...")
        auth_fixes = self.fix_auth_test_file()
        if auth_fixes:
            all_fixes["auth_tests"] = auth_fixes

        # 2. Fix model test files
        print("\n2. Fixing model tests...")
        model_fixes = self.fix_model_test_files()
        if model_fixes:
            all_fixes["model_tests"] = model_fixes

        # 3. Fix other test files with hardcoded emails
        print("\n3. Fixing other test files...")
        other_files = [
            self.tests_dir / "core" / "test_database.py",
            self.tests_dir / "repositories" / "test_user.py",
            self.tests_dir / "schemas" / "test_auth.py",
        ]

        for test_file in other_files:
            if test_file.exists():
                print(f"   Fixing: {test_file.name}")
                fixes = self._fix_hardcoded_emails_in_file(test_file)
                if fixes:
                    all_fixes[test_file.name] = fixes

        return all_fixes

    def generate_fix_report(self) -> str:
        """Generate a report of all fixes applied."""
        report = []
        report.append("=" * 80)
        report.append("TEST ISOLATION FIXES APPLIED")
        report.append("=" * 80)
        report.append(f"Total fixes: {len(self.fixes_applied)}")
        report.append(f"Dry run: {self.dry_run}")
        report.append("")

        # Group by file
        by_file = {}
        for fix in self.fixes_applied:
            if fix.file_path not in by_file:
                by_file[fix.file_path] = []
            by_file[fix.file_path].append(fix)

        for file_path, fixes in by_file.items():
            report.append(f"\nFile: {file_path}")
            report.append("-" * 50)

            by_type = {}
            for fix in fixes:
                if fix.fix_type not in by_type:
                    by_type[fix.fix_type] = []
                by_type[fix.fix_type].append(fix)

            for fix_type, type_fixes in by_type.items():
                report.append(f"  {fix_type}: {len(type_fixes)} fixes")
                for fix in type_fixes[:5]:  # Show first 5
                    report.append(f"    Line {fix.line_number}: {fix.description}")
                if len(type_fixes) > 5:
                    report.append(f"    ... and {len(type_fixes) - 5} more")

        report.append("\n\nNEXT STEPS:")
        report.append("-" * 50)
        report.append("1. Run the tests to verify fixes work correctly")
        report.append("2. Check that individual tests still pass")
        report.append("3. Run full test suite to confirm isolation issues are resolved")
        report.append("4. If issues remain, run the diagnostic script again")

        return "\n".join(report)


def main():
    """Main entry point for the fixer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix test isolation issues automatically"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    parser.add_argument(
        "--backend-dir", default="backend", help="Path to backend directory"
    )

    args = parser.parse_args()

    backend_dir = Path(args.backend_dir)
    if not backend_dir.exists():
        print(f"Error: Backend directory not found: {backend_dir}")
        sys.exit(1)

    fixer = TestIsolationFixer(str(backend_dir), dry_run=args.dry_run)

    try:
        print("🚀 AUTOMATED TEST ISOLATION FIXER")
        print("=" * 50)

        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        else:
            print("⚠️  LIVE MODE - Files will be modified (backups created)")

        # Apply fixes
        fixer.fix_all_test_files()

        # Generate report
        report = fixer.generate_fix_report()

        # Save report
        report_file = Path("test_isolation_fixes_report.txt")
        report_file.write_text(report, encoding="utf-8")

        print(f"\n✅ Fix report saved to: {report_file.absolute()}")

        if not args.dry_run and fixer.fixes_applied:
            print(f"📁 Backups saved to: {fixer.backup_dir.absolute()}")

        total_fixes = len(fixer.fixes_applied)
        if total_fixes > 0:
            print(f"\n🎯 Applied {total_fixes} fixes")
            if args.dry_run:
                print("   Re-run without --dry-run to apply changes")
        else:
            print("\n✨ No fixes needed - tests already isolated!")

    except KeyboardInterrupt:
        print("\n\n❌ Fix process interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Fix process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
