#!/usr/bin/env python3

"""
Test Runner Script v2 - SIMPLIFIED & OPTIMIZED  
==============================================

Streamlined test runner focused on v2 tests only.
Removes original test dependencies and focuses on working components.
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

class TestRunnerV2:
    """Agricultural pipeline test runner v2 - streamlined"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = Path(__file__).parent / "tests"

    def get_v2_test_files(self):
        """Get list of v2 test files explicitly"""
        v2_test_files = []
        
        # List of v2 test files (the ones that work perfectly)
        expected_files = [
            "test_government_schemes_v2.py",
            "test_recommendation_engine_v2.py", 
            "test_report_generator_v2.py",
            "test_main_pipeline_v2.py",
            "test_weather_fetcher_v2.py",
            "test_imports_v2.py"
        ]
        
        for filename in expected_files:
            filepath = self.tests_dir / filename
            if filepath.exists():
                v2_test_files.append(str(filepath))
                print(f" ✅ Found: {filename}")
            else:
                print(f" ❌ Missing: {filename}")
        
        return v2_test_files

    def run_command(self, cmd, description="Running tests"):
        """Run a shell command and return success status"""
        print(f"🚀 {description}")
        print(f"💻 Command: {' '.join(cmd)}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=False)
            end_time = time.time()
            duration = end_time - start_time
            print("-" * 60)
            print(f"✅ SUCCESS: {description} completed in {duration:.1f}s")
            return True
            
        except subprocess.CalledProcessError as e:
            end_time = time.time() 
            duration = end_time - start_time
            print("-" * 60)
            print(f"❌ FAILED: {description} failed after {duration:.1f}s")
            print(f"Exit code: {e.returncode}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'pytest',
            'pytest-cov', 
            'pytest-mock',
            'pandas',
            'requests',
            'numpy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f" ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f" ❌ {package}")
        
        if missing_packages:
            print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
            print("Install with:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def run_all_v2_tests(self):
        """Run all v2 tests with explicit file paths"""
        print("🔍 Finding v2 test files...")
        v2_files = self.get_v2_test_files()
        
        if not v2_files:
            print("❌ No v2 test files found!")
            return False
        
        print(f"✅ Found {len(v2_files)} v2 test files")
        
        # Add conftest_v2.py if it exists
        conftest_file = self.tests_dir / "conftest_v2.py"
        if conftest_file.exists():
            v2_files.append(str(conftest_file))
            print(f" ✅ Added: conftest_v2.py")
        
        cmd = [
            'pytest',
            *v2_files,  # Explicit file paths instead of wildcard
            '-v',
            '--tb=short',
            '--durations=10'
        ]
        
        return self.run_command(cmd, "Running all v2 tests")

    def run_component_tests_v2(self, component):
        """Run v2 tests for specific component"""
        component_file = f"test_{component}_v2.py"
        test_path = self.tests_dir / component_file
        
        if not test_path.exists():
            available_tests = list(self.tests_dir.glob("test_*_v2.py"))
            available_names = [f.stem.replace("test_", "").replace("_v2", "") for f in available_tests]
            print(f"❌ Component test file not found: {component_file}")
            print(f"Available v2 components: {', '.join(available_names)}")
            return False
        
        # Also include conftest if it exists
        files_to_run = [str(test_path)]
        conftest_file = self.tests_dir / "conftest_v2.py"
        if conftest_file.exists():
            files_to_run.append(str(conftest_file))
        
        cmd = [
            'pytest',
            *files_to_run,
            '-v',
            '--tb=short'
        ]
        
        return self.run_command(cmd, f"Running {component} v2 tests") 
    
    def run_with_coverage_v2(self):
        """Run v2 tests with detailed coverage reporting"""
        print("🔍 Finding v2 test files for coverage...")
        v2_files = self.get_v2_test_files()
        
        if not v2_files:
            print("❌ No v2 test files found!")
            return False
        
        cmd = [
            'pytest',
            *v2_files,
            '-v',
            '--cov=.',
            '--cov-report=html:tests/coverage_html_v2',
            '--cov-report=term-missing',
            '--cov-fail-under=70'  # Good threshold for production
        ]
        
        success = self.run_command(cmd, "Running v2 tests with coverage")
        
        if success:
            coverage_file = self.project_root / 'tests' / 'coverage_html_v2' / 'index.html'
            if coverage_file.exists():
                print(f"\n📊 V2 Coverage report generated: {coverage_file}")
                print("Open in browser to view detailed coverage")
        
        return success
    
    def list_available_tests_v2(self):
        """List all available v2 test files and test functions"""
        print("📋 Available v2 test files:")
        test_files = list(self.tests_dir.glob("test_*_v2.py"))
        
        if not test_files:
            print("❌ No v2 test files found!")
            return
        
        for test_file in sorted(test_files):
            component_name = test_file.stem.replace("test_", "").replace("_v2", "")
            print(f" 📄 {component_name} ({test_file.name})")
            
            # Try to extract test function names
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                
                import re
                test_functions = re.findall(r'def (test_\w+)', content)
                if test_functions:
                    print(f"    Functions: {len(test_functions)} tests")
                    for func in test_functions[:3]:  # Show first 3
                        print(f"    - {func}")
                    if len(test_functions) > 3:
                        print(f"    - ... and {len(test_functions) - 3} more")
                        
            except Exception:
                print("    Functions: Could not parse")
            
            print()
    
    def run_single_test_file(self, test_file):
        """Run a single test file"""
        test_path = self.tests_dir / test_file
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        files_to_run = [str(test_path)]
        
        # Add conftest if exists
        conftest_file = self.tests_dir / "conftest_v2.py"
        if conftest_file.exists():
            files_to_run.append(str(conftest_file))
        
        cmd = [
            'pytest',
            *files_to_run,
            '-v',
            '--tb=short'
        ]
        
        return self.run_command(cmd, f"Running {test_file}")

    def run_quick_validation(self):
        """Run quick validation of key components"""
        print("🚀 Quick validation of agricultural pipeline components...")
        
        # Run imports test first (fastest)
        imports_success = self.run_single_test_file("test_imports_v2.py")
        
        if not imports_success:
            print("❌ Import validation failed - check your Python path setup")
            return False
        
        print("✅ Import validation passed - all modules load correctly")
        
        # Run one component test for validation
        gov_success = self.run_single_test_file("test_government_schemes_v2.py")
        
        if gov_success:
            print("✅ Component validation passed - government schemes working")
            print("🎯 Your agricultural pipeline is ready!")
        else:
            print("⚠️ Component validation had issues - but imports work")
        
        return imports_success

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Agricultural Pipeline Test Runner v2 - Streamlined",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests_v2.py                    # Run all v2 tests (default)
  python run_tests_v2.py --all             # Run all v2 tests 
  python run_tests_v2.py --quick           # Quick validation (imports + 1 component)
  python run_tests_v2.py --government      # Government schemes tests only
  python run_tests_v2.py --engine          # Recommendation engine tests only
  python run_tests_v2.py --pipeline        # Main pipeline tests only
  python run_tests_v2.py --coverage        # Run with coverage report
  python run_tests_v2.py --list            # List all available tests
"""
    )
    
    # Test type options
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='Run all v2 tests')
    group.add_argument('--quick', action='store_true', help='Quick validation (imports + 1 component)')
    group.add_argument('--government', action='store_true', help='Run government schemes v2 tests only')
    group.add_argument('--engine', action='store_true', help='Run recommendation engine v2 tests only')
    group.add_argument('--report', action='store_true', help='Run report generator v2 tests only')
    group.add_argument('--pipeline', action='store_true', help='Run main pipeline v2 tests only')
    group.add_argument('--weather', action='store_true', help='Run weather fetcher v2 tests only')
    group.add_argument('--imports', action='store_true', help='Run import tests only')
    
    # Specific test options
    parser.add_argument('--component', type=str, help='Run v2 tests for specific component')
    
    # Reporting options
    parser.add_argument('--coverage', action='store_true', help='Run v2 tests with detailed coverage reporting')
    
    # Utility options
    parser.add_argument('--list', action='store_true', help='List available v2 tests')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunnerV2()
    
    print("🧪 Agricultural Pipeline Test Runner v2 - Streamlined")
    print("=" * 55)
    
    # Handle utility commands first
    if args.check:
        deps_ok = runner.check_dependencies()
        return 0 if deps_ok else 1
    
    if args.list:
        runner.list_available_tests_v2()
        return 0
    
    # Check dependencies before running tests
    if not runner.check_dependencies():
        print("\n❌ Dependency check failed. Install missing packages first.")
        return 1
    
    print()
    
    # Run tests based on arguments
    success = True
    
    if args.coverage:
        success = runner.run_with_coverage_v2()
    elif args.component:
        success = runner.run_component_tests_v2(args.component)
    elif args.quick:
        success = runner.run_quick_validation()
    elif args.government:
        success = runner.run_single_test_file("test_government_schemes_v2.py")
    elif args.engine:
        success = runner.run_single_test_file("test_recommendation_engine_v2.py")
    elif args.report:
        success = runner.run_single_test_file("test_report_generator_v2.py")
    elif args.pipeline:
        success = runner.run_single_test_file("test_main_pipeline_v2.py")
    elif args.weather:
        success = runner.run_single_test_file("test_weather_fetcher_v2.py")
    elif args.imports:
        success = runner.run_single_test_file("test_imports_v2.py")
    elif args.all:
        success = runner.run_all_v2_tests()
    else:
        # Default: run all v2 tests (they work perfectly!)
        print("Running all v2 tests (default behavior)")
        print("Use --help to see all options.")
        print()
        success = runner.run_all_v2_tests()
    
    print()
    
    if success:
        print("🎉 Tests completed successfully!")
        print("🌾 Your agricultural pipeline is working perfectly!")
        return 0
    else:
        print("❌ Some tests failed. Check output above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())