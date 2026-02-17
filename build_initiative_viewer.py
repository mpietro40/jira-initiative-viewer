"""
Build script for Initiative Viewer executable
Creates a standalone Windows executable using PyInstaller

Usage:
    python build_initiative_viewer.py
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} is installed")
        return True
    except ImportError:
        print("✗ PyInstaller is not installed")
        print("  Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Cleaned {dir_name}")
            except Exception as e:
                print(f"⚠ Could not clean {dir_name}: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n" + "="*60)
    print("Building Initiative Viewer Executable")
    print("="*60 + "\n")
    
    # Check for spec file
    spec_file = "initiative_viewer.spec"
    if not os.path.exists(spec_file):
        print(f"✗ Spec file '{spec_file}' not found!")
        return False
    
    print(f"✓ Found spec file: {spec_file}")
    
    # Run PyInstaller
    print("\nRunning PyInstaller...")
    try:
        subprocess.check_call([
            sys.executable,
            "-m", "PyInstaller",
            spec_file,
            "--noconfirm",
            "--clean"
        ])
        print("\n✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        return False

def show_results():
    """Show the location of the built executable"""
    exe_path = os.path.join("dist", "InitiativeViewer.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n" + "="*60)
        print("Build Results")
        print("="*60)
        print(f"✓ Executable created: {os.path.abspath(exe_path)}")
        print(f"  Size: {size_mb:.1f} MB")
        print("\nTo run the application:")
        print(f"  {exe_path} --jira-url <URL> --email <EMAIL> --token <TOKEN> --jql <JQL>")
        print("\nExample:")
        print('  InitiativeViewer.exe --jira-url https://jira.company.com \\')
        print('    --email user@company.com --token YOUR_API_TOKEN \\')
        print('    --jql "project = PROJ AND type = \'Business Initiative\'"')
        print("\n" + "="*60)
    else:
        print("\n✗ Executable not found in dist folder")

def main():
    """Main build process"""
    print("Initiative Viewer - Build Script")
    print("="*60)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("\n✗ Build aborted: PyInstaller not available")
        return 1
    
    # Clean old builds
    response = input("\nClean previous build directories? (y/n): ").lower()
    if response == 'y':
        clean_build_dirs()
    
    # Build
    if not build_executable():
        return 1
    
    # Show results
    show_results()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
