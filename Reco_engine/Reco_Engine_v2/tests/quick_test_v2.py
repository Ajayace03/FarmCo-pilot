#!/usr/bin/env python3

"""
Quick Test Runner v2 - Import Fix Version
=========================================

Simple test runner to check imports first, then run other tests.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Quick test runner"""
    
    print("🧪 QUICK TEST RUNNER V2 - IMPORT FIX")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 Tests directory: {tests_dir}")
    
    # Check if test files exist
    test_files = {
        'imports': tests_dir / 'test_imports_v2.py',
        'conftest': tests_dir / 'conftest_v2.py',
        'government': tests_dir / 'test_government_schemes_v2.py',
        'engine': tests_dir / 'test_recommendation_engine_v2.py'
    }
    
    print(f"\n🔍 Checking for test files:")
    existing_tests = {}
    for name, filepath in test_files.items():
        exists = filepath.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {name}: {filepath.name}")
        if exists:
            existing_tests[name] = filepath
    
    if not existing_tests:
        print(f"\n❌ No test files found! Make sure you're in the right directory.")
        return 1
    
    # Run diagnosis first
    print(f"\n🔬 STEP 1: Running project diagnosis...")
    diagnosis_file = project_root / "diagnose_project_v2.py"
    if diagnosis_file.exists():
        try:
            subprocess.run([sys.executable, str(diagnosis_file)], cwd=project_root)
        except Exception as e:
            print(f"⚠️ Diagnosis failed: {e}")
    
    # Run import test first
    if 'imports' in existing_tests:
        print(f"\n🔬 STEP 2: Testing imports...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                str(existing_tests['imports']), 
                '-v', '--tb=short'
            ], cwd=project_root)
            
            if result.returncode == 0:
                print(f"✅ Import tests passed!")
            else:
                print(f"❌ Import tests failed with exit code: {result.returncode}")
                return result.returncode
                
        except Exception as e:
            print(f"❌ Import test execution failed: {e}")
            return 1
    
    # If imports work, try one component test
    if 'government' in existing_tests:
        print(f"\n🔬 STEP 3: Testing one component (government schemes)...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                str(existing_tests['government']), 
                '-v', '--tb=short', '-x'  # Stop on first failure
            ], cwd=project_root)
            
            if result.returncode == 0:
                print(f"✅ Government schemes tests passed!")
            else:
                print(f"⚠️ Government schemes tests had issues (exit code: {result.returncode})")
                print(f"This is expected - we're still debugging")
                
        except Exception as e:
            print(f"❌ Government schemes test execution failed: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Import testing completed")
    
    if 'imports' in existing_tests and len(existing_tests) > 1:
        print(f"✅ Found {len(existing_tests)} test files")
        print(f"\n🚀 Next steps:")
        print(f"   1. If imports work, run: python -m pytest tests/test_*_v2.py -v")
        print(f"   2. Or use the full runner: python run_tests_v2.py --all")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())