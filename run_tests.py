"""
Run Initiative Viewer tests
Python script to run tests with various options
"""

import sys
import subprocess
import argparse


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run Initiative Viewer tests')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--quick', action='store_true', help='Quick run without verbose output')
    parser.add_argument('--pdf', action='store_true', help='Run only PDF tests')
    parser.add_argument('--web', action='store_true', help='Run only web interface tests')
    parser.add_argument('--errors', action='store_true', help='Run only error handling tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest', 'tests/test_initiative_viewer.py']
    
    # Add options based on arguments
    if args.verbose or not args.quick:
        cmd.append('-v')
    
    if args.coverage:
        cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
        print("\n" + "="*60)
        print("Running tests with coverage report")
        print("="*60 + "\n")
    
    if args.pdf:
        cmd[2] = 'tests/test_initiative_viewer.py::TestPDFGeneration'
        print("\n" + "="*60)
        print("Running PDF Generation tests only")
        print("="*60 + "\n")
    elif args.web:
        cmd[2] = 'tests/test_initiative_viewer.py::TestWebInterface'
        print("\n" + "="*60)
        print("Running Web Interface tests only")
        print("="*60 + "\n")
    elif args.errors:
        cmd[2] = 'tests/test_initiative_viewer.py::TestErrorHandling'
        print("\n" + "="*60)
        print("Running Error Handling tests only")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("Running all Initiative Viewer tests")
        print("="*60 + "\n")
    
    # Run tests
    exit_code = run_command(cmd)
    
    # Print summary
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        print("\nTip: Run with -v for verbose output")
        print("     Run with --coverage for coverage report")
    print("="*60 + "\n")
    
    if args.coverage and exit_code == 0:
        print("📊 Coverage report: htmlcov/index.html\n")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
