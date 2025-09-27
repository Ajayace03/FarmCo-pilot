#!/usr/bin/env python3

"""
Test Runner Script for Agricultural Pipeline
===========================================

Easy-to-use test runner with different test categories and options.

Usage:
    python run_tests.py --all          # Run all tests
    python run_tests.py --unit         # Run only unit tests
    python run_tests.py --integration  # Run only integration tests
    python run_tests.py --fast         # Run only fast tests
    python run_tests.py --component weather  # Run specific component tests
    python run_tests.py --coverage     # Run with detailed coverage
    python run_tests.py --report       # Generate HTML report
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

class TestRunner:
    """Test runner for agricultural pipeline"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = Path(__file__).parent
        
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
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package}")
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Install with:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def run_all_tests(self):
        """Run all tests with standard configuration"""
        cmd = [
            'pytest', 
            'tests/', 
            '-v',
            '--tb=short',
            '--durations=10'
        ]
        return self.run_command(cmd, "Running all tests")
    
    def run_unit_tests(self):
        """Run only unit tests (fast, isolated tests)"""
        cmd = [
            'pytest',
            'tests/',
            '-m', 'unit or not (integration or slow)',
            '-v'
        ]
        return self.run_command(cmd, "Running unit tests")
    
    def run_integration_tests(self):
        """Run only integration tests"""
        cmd = [
            'pytest',
            'tests/',
            '-m', 'integration',
            '-v',
            '--tb=long'
        ]
        return self.run_command(cmd, "Running integration tests")
    
    def run_fast_tests(self):
        """Run only fast tests (exclude slow tests)"""
        cmd = [
            'pytest',
            'tests/',
            '-m', 'not slow',
            '-v'
        ]
        return self.run_command(cmd, "Running fast tests")
    
    def run_component_tests(self, component):
        """Run tests for specific component"""
        component_file = f"test_{component}.py"
        test_path = self.tests_dir / component_file
        
        if not test_path.exists():
            available_tests = list(self.tests_dir.glob("test_*.py"))
            available_names = [f.stem.replace("test_", "") for f in available_tests]
            
            print(f"❌ Component test file not found: {component_file}")
            print(f"Available components: {', '.join(available_names)}")
            return False
        
        cmd = [
            'pytest',
            str(test_path),
            '-v',
            '--tb=short'
        ]
        return self.run_command(cmd, f"Running {component} tests")
    
    def run_with_coverage(self):
        """Run tests with detailed coverage reporting"""
        cmd = [
            'pytest',
            'tests/',
            '-v',
            '--cov=.',
            '--cov-report=html:tests/coverage_html',
            '--cov-report=term-missing',
            '--cov-fail-under=70'
        ]
        
        success = self.run_command(cmd, "Running tests with coverage")
        
        if success:
            coverage_file = self.project_root / 'tests' / 'coverage_html' / 'index.html'
            if coverage_file.exists():
                print(f"\n📊 Coverage report generated: {coverage_file}")
                print("Open in browser to view detailed coverage")
        
        return success
    
    def generate_test_report(self):
        """Generate comprehensive HTML test report"""
        cmd = [
            'pytest',
            'tests/',
            '--html=tests/test_report.html',
            '--self-contained-html',
            '-v'
        ]
        
        success = self.run_command(cmd, "Generating test report")
        
        if success:
            report_file = self.project_root / 'tests' / 'test_report.html'
            if report_file.exists():
                print(f"\n📋 Test report generated: {report_file}")
        
        return success
    
    def run_performance_tests(self):
        """Run performance and load tests"""
        cmd = [
            'pytest',
            'tests/',
            '-m', 'performance or slow',
            '-v',
            '--tb=short',
            '--durations=0'
        ]
        return self.run_command(cmd, "Running performance tests")
    
    def run_specific_test(self, test_name):
        """Run a specific test by name"""
        cmd = [
            'pytest',
            'tests/',
            '-k', test_name,
            '-v',
            '--tb=long'
        ]
        return self.run_command(cmd, f"Running specific test: {test_name}")
    
    def list_available_tests(self):
        """List all available test files and test functions"""
        print("📋 Available test files:")
        test_files = list(self.tests_dir.glob("test_*.py"))
        
        for test_file in sorted(test_files):
            component_name = test_file.stem.replace("test_", "")
            print(f"  📄 {component_name} ({test_file.name})")
            
            # Try to extract test function names
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    
                import re
                test_functions = re.findall(r'def (test_\w+)', content)
                if test_functions:
                    print(f"     Functions: {len(test_functions)} tests")
                    for func in test_functions[:3]:  # Show first 3
                        print(f"       - {func}")
                    if len(test_functions) > 3:
                        print(f"       - ... and {len(test_functions) - 3} more")
            except Exception:
                print("     Functions: Could not parse")
            
            print()
    
    def validate_project_structure(self):
        """Validate project structure before running tests"""
        print("🔍 Validating project structure...")
        
        required_dirs = [
            'data_fetchers',
            'engine', 
            'tests'
        ]
        
        required_files = [
            'main_complete.py',
            'government_schemes_matcher.py',
            'comprehensive_report_generator.py'
        ]
        
        missing_items = []
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_items.append(f"Directory: {dir_name}")
            else:
                print(f"  ✅ Directory: {dir_name}")
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_items.append(f"File: {file_name}")
            else:
                print(f"  ✅ File: {file_name}")
        
        if missing_items:
            print("\n⚠️  Missing project components:")
            for item in missing_items:
                print(f"  ❌ {item}")
            print("\nSome tests may fail due to missing components.")
            return False
        
        print("✅ Project structure valid")
        return True

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Test runner for Agricultural Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit                   # Run unit tests only
  python run_tests.py --fast                   # Run fast tests only
  python run_tests.py --component weather      # Run weather component tests
  python run_tests.py --coverage               # Run with coverage
  python run_tests.py --specific "test_name"   # Run specific test
  python run_tests.py --list                   # List available tests
        """
    )
    
    # Test type options
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='Run all tests')
    group.add_argument('--unit', action='store_true', help='Run unit tests only')
    group.add_argument('--integration', action='store_true', help='Run integration tests only')
    group.add_argument('--fast', action='store_true', help='Run fast tests only (exclude slow tests)')
    group.add_argument('--performance', action='store_true', help='Run performance tests only')
    
    # Specific test options
    parser.add_argument('--component', type=str, help='Run tests for specific component (weather, recommendation, etc.)')
    parser.add_argument('--specific', type=str, help='Run specific test by name or pattern')
    
    # Reporting options
    parser.add_argument('--coverage', action='store_true', help='Run with detailed coverage reporting')
    parser.add_argument('--report', action='store_true', help='Generate HTML test report')
    
    # Utility options
    parser.add_argument('--list', action='store_true', help='List available tests')
    parser.add_argument('--check', action='store_true', help='Check dependencies and project structure')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner()
    
    print("🧪 Agricultural Pipeline Test Runner")
    print("=" * 50)
    
    # Handle utility commands first
    if args.check:
        deps_ok = runner.check_dependencies()
        structure_ok = runner.validate_project_structure()
        return 0 if deps_ok and structure_ok else 1
    
    if args.list:
        runner.list_available_tests()
        return 0
    
    # Check dependencies before running tests
    if not runner.check_dependencies():
        print("\n❌ Dependency check failed. Install missing packages first.")
        return 1
    
    # Validate project structure
    if not runner.validate_project_structure():
        print("\n⚠️  Project structure issues detected. Some tests may fail.")
    
    print()
    
    # Run tests based on arguments
    success = True
    
    if args.coverage:
        success = runner.run_with_coverage()
    elif args.report:
        success = runner.generate_test_report()
    elif args.component:
        success = runner.run_component_tests(args.component)
    elif args.specific:
        success = runner.run_specific_test(args.specific)
    elif args.unit:
        success = runner.run_unit_tests()
    elif args.integration:
        success = runner.run_integration_tests()
    elif args.fast:
        success = runner.run_fast_tests()
    elif args.performance:
        success = runner.run_performance_tests()
    elif args.all:
        success = runner.run_all_tests()
    else:
        # Default: run fast tests
        print("No specific test type specified. Running fast tests by default.")
        print("Use --help to see all options.")
        print()
        success = runner.run_fast_tests()
    
    print()
    if success:
        print("🎉 All tests completed successfully!")
        return 0
    else:
        print("❌ Some tests failed. Check output above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())