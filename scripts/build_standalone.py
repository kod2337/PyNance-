#!/usr/bin/env python3
"""
Build Script for Finance Tracker Standalone Application
Creates executable files using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def build_cli_version():
    """Build CLI version of Finance Tracker"""
    print("\n🔨 Building CLI version...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onefile",
            "--console",
            "--name", "FinanceTracker",
            "main.py"
        ])
        print("✅ CLI version built successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to build CLI version")
        return False

def build_gui_version():
    """Build GUI version of Finance Tracker"""
    print("\n🔨 Building GUI version...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onefile",
            "--windowed",
            "--name", "FinanceTrackerGUI",
            "gui_finance_tracker.py"
        ])
        print("✅ GUI version built successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to build GUI version")
        return False

def copy_essential_files():
    """Copy essential files to dist directory"""
    essential_files = [
        "credentials.json",
        "user_settings.json",
        "env.example",
        "README.md"
    ]
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Dist directory not found")
        return False
    
    for file_name in essential_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"📋 Copied {file_name} to dist/")
    
    # Copy essential directories
    essential_dirs = ["config", "data"]
    for dir_name in essential_dirs:
        if os.path.exists(dir_name):
            dest_dir = dist_dir / dir_name
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(dir_name, dest_dir)
            print(f"📁 Copied {dir_name}/ to dist/")
    
    return True

def create_launcher_script():
    """Create a simple launcher script for easy execution"""
    launcher_content = '''@echo off
echo Starting Finance Tracker...
echo.
echo Choose your preferred interface:
echo 1. GUI Interface (Recommended)
echo 2. CLI Interface
echo.
set /p choice=Enter your choice (1 or 2): 

if "%choice%"=="1" (
    echo Starting GUI version...
    FinanceTrackerGUI.exe
) else if "%choice%"=="2" (
    echo Starting CLI version...
    FinanceTracker.exe
) else (
    echo Invalid choice. Starting GUI version...
    FinanceTrackerGUI.exe
)

pause
'''
    
    with open("dist/launch.bat", "w") as f:
        f.write(launcher_content)
    print("🚀 Created launch.bat script")

def main():
    """Main build process"""
    print("🏗️  Finance Tracker Standalone Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build both versions
    cli_success = build_cli_version()
    gui_success = build_gui_version()
    
    if not (cli_success or gui_success):
        print("\n❌ Build failed completely")
        return False
    
    # Copy essential files
    if not copy_essential_files():
        print("⚠️  Warning: Some essential files couldn't be copied")
    
    # Create launcher script
    create_launcher_script()
    
    print("\n🎉 Build completed!")
    print("\n📦 Your standalone applications are in the 'dist/' directory:")
    
    if cli_success:
        print("   • FinanceTracker.exe (CLI version)")
    if gui_success:
        print("   • FinanceTrackerGUI.exe (GUI version)")
    
    print("   • launch.bat (Easy launcher)")
    print("\n💡 To distribute your app, just copy the entire 'dist/' folder!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 