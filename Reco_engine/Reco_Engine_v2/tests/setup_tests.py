#!/usr/bin/env python3

"""
Test Setup Script for Agricultural Pipeline
===========================================

Installs all required testing dependencies and sets up the testing environment.

Usage:
    python setup_tests.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main setup function"""
    print("🧪 Setting up Agricultural Pipeline Testing Environment")
    print("=" * 60)
    
    # Required testing packages
    test_packages = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0", 
        "pytest-mock>=3.10.0",
        "pytest-html>=3.1.0",
        "coverage>=7.0.0"
    ]
    
    # Required project packages (if not already installed)
    project_packages = [
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "requests>=2.28.0",
        "validators>=0.20.0"
    ]
    
    all_packages = test_packages + project_packages
    
    print("📦 Installing required packages...")
    print(f"Packages to install: {len(all_packages)}")
    print()
    
    failed_packages = []
    
    for i, package in enumerate(all_packages, 1):
        print(f"[{i}/{len(all_packages)}] Installing {package}...")
        
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
            failed_packages.append(package)
        print()
    
    # Summary
    print("-" * 60)
    if failed_packages:
        print(f"❌ Failed to install {len(failed_packages)} packages:")
        for package in failed_packages:
            print(f"  - {package}")
        print()
        print("Please install these manually:")
        print(f"pip install {' '.join(failed_packages)}")
        return 1
    else:
        print("✅ All packages installed successfully!")
    
    # Create necessary directories
    print("\n📁 Setting up test directories...")
    
    test_dirs = [
        "tests/coverage_html",
        "tests/reports", 
        "tests/__pycache__"
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")
    
    # Verify setup
    print("\n🔍 Verifying setup...")
    
    try:
        import pytest
        print(f"  ✅ pytest {pytest.__version__}")
    except ImportError:
        print("  ❌ pytest not available")
        return 1
    
    try:
        import pytest_cov
        print("  ✅ pytest-cov available")
    except ImportError:
        print("  ❌ pytest-cov not available")
    
    try:
        import pandas as pd
        print(f"  ✅ pandas {pd.__version__}")
    except ImportError:
        print("  ❌ pandas not available")
        return 1
    
    # Create simple test verification
    print("\n🧪 Running test verification...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--version"
        ], capture_output=True, text=True, check=True)
        print(f"  ✅ pytest working: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ pytest verification failed: {e}")
        return 1
    
    print("\n🎉 Test setup completed successfully!")
    print("\nNext steps:")
    print("1. Run basic tests:     python run_tests.py --fast")
    print("2. Run all tests:       python run_tests.py --all") 
    print("3. Run with coverage:   python run_tests.py --coverage")
    print("4. List available tests: python run_tests.py --list")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())