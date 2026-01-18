#!/usr/bin/env python3
"""
Environment verification script for Weekly Deployment Update workflow.
Run this to verify your environment is set up correctly.
"""

import sys
import os

VENV_NAME = "flowbot"
REQUIRED_PYTHON_VERSION = (3, 8)

def print_status(check, passed, details=""):
    icon = "✓" if passed else "✗"
    status = "PASS" if passed else "FAIL"
    print(f"  [{icon}] {check}: {status}")
    if details:
        print(f"      {details}")
    return passed

def main():
    print()
    print("=" * 55)
    print("  🤖 FLOWBOT Environment Check")
    print("=" * 55)
    print()

    all_passed = True

    # Check 1: Python version
    print("1. Python Version")
    py_version = sys.version_info
    version_ok = py_version >= REQUIRED_PYTHON_VERSION
    all_passed &= print_status(
        f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+",
        version_ok,
        f"Found: {py_version.major}.{py_version.minor}.{py_version.micro}"
    )
    print()

    # Check 2: Virtual environment active
    print("2. Virtual Environment")
    venv_path = os.environ.get("VIRTUAL_ENV", "")
    venv_active = bool(venv_path)
    all_passed &= print_status(
        "venv is active",
        venv_active,
        f"Path: {venv_path}" if venv_active else "Run: source flowbot/bin/activate"
    )

    # Check if it's the right venv
    if venv_active:
        correct_venv = venv_path.endswith(VENV_NAME)
        all_passed &= print_status(
            f"Using '{VENV_NAME}' venv",
            correct_venv,
            "" if correct_venv else f"Expected '{VENV_NAME}', got '{os.path.basename(venv_path)}'"
        )
    print()

    # Check 3: Required files exist
    print("3. Project Files")
    script_dir = os.path.dirname(os.path.abspath(__file__))

    required_files = [
        ("test_workflow.py", "Main test script"),
        ("workflows/weekly_deployment_update.json", "n8n workflow"),
        ("docs/technical-documentation.md", "Technical docs"),
        ("docs/QA_Test_Plan.md", "QA test plan"),
        ("README.md", "Project readme"),
    ]

    for filepath, description in required_files:
        full_path = os.path.join(script_dir, filepath)
        exists = os.path.exists(full_path)
        all_passed &= print_status(description, exists, filepath)
    print()

    # Check 4: Output directories exist
    print("4. Output Directories")
    directories = ["outputs", "mockdata", "docs", "workflows"]

    for dirname in directories:
        dir_path = os.path.join(script_dir, dirname)
        exists = os.path.isdir(dir_path)
        all_passed &= print_status(f"{dirname}/", exists)
    print()

    # Check 5: Python imports
    print("5. Python Imports")
    imports_ok = True
    try:
        import json
        import datetime
        print_status("json", True)
        print_status("datetime", True)
        print_status("os", True)
    except ImportError as e:
        imports_ok = False
        print_status("Standard library", False, str(e))

    # Check for python-pptx (optional but recommended)
    try:
        from pptx import Presentation
        print_status("python-pptx", True, "PowerPoint generation enabled")
    except ImportError:
        print_status("python-pptx", False, "Run: pip install python-pptx")
        # Don't fail overall - it's optional
    all_passed &= imports_ok
    print()

    # Check 6: Validate generated outputs (if they exist)
    print("6. Output Validation (optional)")
    categorized_path = os.path.join(script_dir, "mockdata", "categorized_data.json")

    if os.path.exists(categorized_path):
        try:
            import json
            with open(categorized_path, 'r') as f:
                data = json.load(f)

            # Check for required bucket names
            required_buckets = [
                "fe_deployed", "be_deployed",
                "fe_upcoming", "be_upcoming",
                "focus_items", "risks_blocks", "uncategorized"
            ]
            buckets = data.get("buckets", {})

            missing_buckets = [b for b in required_buckets if b not in buckets]
            buckets_ok = len(missing_buckets) == 0
            all_passed &= print_status(
                "Bucket names in categorized_data.json",
                buckets_ok,
                "" if buckets_ok else f"Missing: {missing_buckets}"
            )

            # Check for required top-level keys
            required_keys = ["buckets", "windows", "week_id", "timestamp"]
            missing_keys = [k for k in required_keys if k not in data]
            keys_ok = len(missing_keys) == 0
            all_passed &= print_status(
                "Required keys in categorized_data.json",
                keys_ok,
                "" if keys_ok else f"Missing: {missing_keys}"
            )

            # Check windows has timezone
            windows = data.get("windows", {})
            tz_ok = windows.get("timezone") == "UTC"
            all_passed &= print_status(
                "Timezone is UTC",
                tz_ok,
                "" if tz_ok else f"Found: {windows.get('timezone', 'missing')}"
            )

        except json.JSONDecodeError as e:
            all_passed &= print_status("JSON parsing", False, str(e))
        except Exception as e:
            all_passed &= print_status("Output validation", False, str(e))
    else:
        print_status("categorized_data.json", False, "Run test_workflow.py first")
        print("      (This check is optional - outputs generated after first run)")
    print()

    # Summary
    print("=" * 55)
    if all_passed:
        print("  ✅ All checks passed! Environment is ready.")
        print()
        print("  Next steps:")
        print("    python3 test_workflow.py    # Run the workflow")
        print("    deactivate                  # Exit venv when done")
    else:
        print("  ❌ Some checks failed. Please fix issues above.")
        print()
        print("  Quick setup:")
        print(f"    cd {script_dir}")
        print(f"    python3 -m venv {VENV_NAME}")
        print(f"    source {VENV_NAME}/bin/activate")
        print("    python3 check_env.py")
    print("=" * 55)
    print()

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
