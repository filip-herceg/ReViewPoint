#!/usr/bin/env python3
"""
Validation script for the new testing setup.

This script checks that all components are properly configured.
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and report status."""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False

def check_hatch_env():
    """Check if hatch environments are configured."""
    try:
        import subprocess
        result = subprocess.run(
            ["hatch", "env", "show"], 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            # Check if 'fast' appears as an environment name in the output
            lines = result.stdout.split('\n')
            fast_found = any('fast' in line and ('virtual' in line or 'Scripts' in line) for line in lines)
            
            if fast_found:
                print("✅ Hatch fast environment configured")
                return True
            else:
                print(f"❌ Hatch fast environment not found in output")
                return False
        else:
            print(f"❌ Hatch command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Hatch not found - install with: pip install hatch")
        return False
    except Exception as e:
        print(f"❌ Error checking hatch: {e}")
        return False

def main():
    """Validate the testing setup."""
    print("🔍 Validating ReViewPoint Backend Testing Setup")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    all_good = True
    
    # Check file structure
    print("\n📁 File Structure:")
    files_to_check = [
        ("testing/fast/conftest.py", "Fast test configuration"),
        ("testing/fast/pytest.ini", "Fast pytest settings"),
        ("testing/fast/templates.py", "Fast test templates"),
        ("testing/fast/README.md", "Fast test documentation"),
        ("test.py", "Cross-platform test runner"),
        ("test.ps1", "PowerShell test runner"),
        ("TESTING.md", "Testing documentation"),
        ("pyproject.toml", "Project configuration"),
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check old files are removed
    print("\n🧹 Old Files Cleanup:")
    old_files = [
        "pytest_fast.ini", 
        "fast_test_templates.py"
    ]
    
    for old_file in old_files:
        if Path(old_file).exists():
            print(f"⚠️  Old file still exists: {old_file}")
            all_good = False
        else:
            print(f"✅ Old file removed: {old_file}")
    
    # Check hatch environment
    print("\n🔧 Hatch Configuration:")
    if not check_hatch_env():
        all_good = False
    
    # Check pyproject.toml content
    print("\n📋 Configuration Validation:")
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            if "[tool.hatch.envs.fast]" in content:
                print("✅ Fast environment configured in pyproject.toml")
            else:
                print("❌ Fast environment missing in pyproject.toml")
                all_good = False
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        all_good = False
    
    # Final status
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 Setup validation completed successfully!")
        print("\n🚀 Ready to use:")
        print("   python test.py fast     # Run fast tests")
        print("   python test.py full     # Run full tests") 
        print("   python test.py watch    # Fast tests in watch mode")
        return 0
    else:
        print("❌ Setup validation failed - please check the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
