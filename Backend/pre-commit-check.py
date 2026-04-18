#!/usr/bin/env python3
"""
Pre-Commit Quality Gate Script
Runs tests, ruff lint, and ruff format checks with auto-fix capabilities
"""

import subprocess
import sys
import os
from pathlib import Path


def get_python_command() -> str:
    """Return the Python interpreter command used for subprocess checks.

    Prefer the project's virtualenv interpreter when available so the script
    works even if launched with a global Python executable.
    """
    backend_dir = Path(__file__).resolve().parent
    windows_venv = backend_dir / ".venv" / "Scripts" / "python.exe"
    unix_venv = backend_dir / ".venv" / "bin" / "python"

    if windows_venv.exists():
        return f'"{windows_venv.resolve()}"'
    if unix_venv.exists():
        return f'"{unix_venv.resolve()}"'

    return f'"{sys.executable}"'


class Colors:
    """Terminal color codes"""

    HEADER = "\033[95m"
    INFO = "\033[94m"
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(message):
    """Print a formatted header"""
    print()
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print()


def print_step(message):
    """Print a step message"""
    print(f"{Colors.INFO}[>] {message}{Colors.ENDC}")


def print_success(message):
    """Print a success message"""
    print(f"{Colors.SUCCESS}[OK] {message}{Colors.ENDC}")


def print_fail(message):
    """Print a failure message"""
    print(f"{Colors.FAIL}[X] {message}{Colors.ENDC}")


def print_warn(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}[!] {message}{Colors.ENDC}")


def run_command(cmd, capture=False):
    """Run a shell command and return exit code"""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=False
            )
            return result.returncode, result.stdout + result.stderr
        else:
            result = subprocess.run(cmd, shell=True, check=False)
            return result.returncode, ""
    except Exception as e:
        print_fail(f"Error running command: {e}")
        return 1, str(e)


def step_1_tests():
    """Step 1: Run tests with coverage check"""
    print_header("STEP 1: RUNNING TESTS & COVERAGE CHECK")

    print_step("Executing pytest with 95% coverage requirement...")
    print()

    python_cmd = get_python_command()
    exit_code, _ = run_command(
        f"{python_cmd} -m pytest tests --cov=app --cov-fail-under=95", capture=False
    )

    if exit_code == 0:
        print_success("All tests passed AND coverage exceeded 95%!")
        return True
    else:
        print_fail("Tests failed or coverage below 95%!")
        print()
        print_warn("Coverage details:")
        run_command(f"{python_cmd} -m pytest tests --cov=app --cov-report=term-missing")
        print()
        print_fail("[X] PRE-COMMIT CHECK ABORTED")
        print_fail("    Please fix test failures and/or increase coverage to 95%")
        return False


def step_2_ruff_lint():
    """Step 2: Run ruff lint with auto-fix"""
    print_header("STEP 2: RUNNING RUFF LINT CHECKS")

    max_attempts = 3
    python_cmd = get_python_command()
    
    # Move to repo root (like GitHub Actions does)
    repo_root = Path("..").resolve()
    backend_dir = Path(".").resolve()
    os.chdir(repo_root)

    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            print_step("Checking ruff lint violations from repo root...")
        else:
            print_step(f"Re-checking ruff lint from repo root (attempt {attempt}/{max_attempts})...")

        print()

        exit_code, output = run_command(
            f"{python_cmd} -m ruff check Backend/app Backend/tests --config Backend/pyproject.toml", capture=True
        )

        if exit_code == 0:
            print_success("No lint violations found! Clean code detected!")
            os.chdir(backend_dir)
            return True
        else:
            if attempt == 1:
                print_warn("Found lint violations. Auto-fixing...")
                print()
                print(output)
            else:
                print_warn(
                    f"Still finding violations. Running auto-fix again (attempt {attempt})..."
                )
                print()
                print(output)

            print_step(
                "Running: python -m ruff check Backend/app Backend/tests --config Backend/pyproject.toml --fix"
            )
            print()

            run_command(
                f"{python_cmd} -m ruff check Backend/app Backend/tests --config Backend/pyproject.toml --fix"
            )

            print()

    print_fail(f"Ruff lint still complaining after {max_attempts} fix attempts!")
    print()
    print_fail("[X] LINT CHECK FAILED")
    print_fail("   Please manually review and fix the lint violations:")
    print_fail("   ruff check Backend/app Backend/tests --config Backend/pyproject.toml")
    os.chdir(backend_dir)
    return False


def step_3_ruff_format():
    """Step 3: Run ruff format with auto-fix"""
    print_header("STEP 3: RUNNING RUFF FORMAT CHECKS")

    max_attempts = 3
    python_cmd = get_python_command()
    
    # Move to repo root (like GitHub Actions does)
    repo_root = Path("..").resolve()
    backend_dir = Path(".").resolve()
    os.chdir(repo_root)

    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            print_step("Checking code formatting from repo root...")
        else:
            print_step(f"Re-checking formatting from repo root (attempt {attempt}/{max_attempts})...")

        print()

        exit_code, output = run_command(
            f"{python_cmd} -m ruff format Backend/app Backend/tests --config Backend/pyproject.toml --check",
            capture=True,
        )

        if exit_code == 0:
            print_success("All files are properly formatted!")
            os.chdir(backend_dir)
            return True
        else:
            if attempt == 1:
                print_warn("Found formatting violations. Auto-fixing...")
            else:
                print_warn(
                    f"Still finding format violations. Re-formatting (attempt {attempt})..."
                )

            print()
            print(output)

            print_step("Running: python -m ruff format Backend/app Backend/tests --config Backend/pyproject.toml")
            print()

            run_command(
                f"{python_cmd} -m ruff format Backend/app Backend/tests --config Backend/pyproject.toml"
            )

            print()

    print_fail(f"Ruff format still complaining after {max_attempts} fix attempts!")
    print()
    print_fail("[X] FORMAT CHECK FAILED")
    print_fail("   Please manually review and fix the format violations:")
    print_fail("   ruff format Backend/app Backend/tests --config Backend/pyproject.toml")
    os.chdir(backend_dir)
    return False


def main():
    """Main entry point"""
    # Check if we're in the Backend directory
    if not Path("pyproject.toml").exists():
        print_fail("Error: pyproject.toml not found!")
        print_fail("Please run this script from the Backend directory")
        sys.exit(1)

    # Check if venv is active or provide instructions
    venv_path = Path(".venv")
    if not venv_path.exists() and sys.prefix == sys.base_prefix:
        print_fail("Error: Virtual environment not found or not activated!")
        print_fail("Please activate your virtual environment first:")
        print_fail("  Windows: .venv\\Scripts\\activate")
        print_fail("Then run: python pre-commit-check.py")
        sys.exit(1)

    # Run all checks
    python_cmd = get_python_command()
    tests_pass = step_1_tests()
    if not tests_pass:
        sys.exit(1)

    lint_pass = step_2_ruff_lint()
    if not lint_pass:
        sys.exit(1)

    format_pass = step_3_ruff_format()
    if not format_pass:
        sys.exit(1)

    # BONUS: Validate from repo root matches Backend/ checks
    print_header("VALIDATING CONSISTENCY")
    print_step("Confirming Backend/ matches repo root checks...")
    print()
    
    # We're already at repo root from step_3, just confirm one more time
    repo_root = Path("..").resolve()
    os.chdir(repo_root)
    
    exit_code_lint, _ = run_command(
        f"{python_cmd} -m ruff check Backend/app Backend/tests --config Backend/pyproject.toml",
        capture=True
    )
    exit_code_format, _ = run_command(
        f"{python_cmd} -m ruff format Backend/app Backend/tests --config Backend/pyproject.toml --check",
        capture=True
    )
    
    if exit_code_lint == 0 and exit_code_format == 0:
        print_success("All checks consistent from repo root (GitHub Actions compatible)!")
    else:
        print_fail("Inconsistency detected between local and repo root!")
        os.chdir(str(Path(repo_root) / "Backend"))
        sys.exit(1)
    
    # Return to Backend directory
    backend_dir = Path(repo_root) / "Backend"
    os.chdir(backend_dir)

    # Success!
    print_header("ALL PRE-COMMIT CHECKS PASSED!")
    print_success("Your code is ready for commit and review!")
    print()
    print(f"{Colors.INFO}Summary:{Colors.ENDC}")
    print(f"{Colors.SUCCESS}  [OK] Tests passing with 95%+ coverage{Colors.ENDC}")
    print(f"{Colors.SUCCESS}  [OK] Ruff lint clean (both local and repo root){Colors.ENDC}")
    print(f"{Colors.SUCCESS}  [OK] Code properly formatted (both local and repo root){Colors.ENDC}")
    print()
    print(f"{Colors.INFO}Next step: git add . && git commit -m 'Your message'{Colors.ENDC}")
    print()


if __name__ == "__main__":
    main()
