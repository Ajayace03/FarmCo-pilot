#!/usr/bin/env python3
"""
Agricultural Pipeline Setup Script
=================================

Quick setup and validation script for the agricultural recommendation pipeline.
Run this script first to verify all components are properly configured.

Author: Agricultural AI Team
Version: 1.0
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Tuple

def print_header():
    """Print setup script header"""
    print("🌾" + "=" * 70 + "🌾")
    print("    Agricultural Recommendation Engine - Setup & Validation")
    print("    Version 3.0 - Complete Pipeline Setup")
    print("🌾" + "=" * 70 + "🌾")
    print()

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_required_files() -> Dict[str, bool]:
    """Check if all required files exist"""
    print("\n📁 Checking required files...")

    required_files = {
        "main.py": "Main pipeline controller",
        "farms.csv": "Farm input data",
        "weather_fetcher.py": "Weather data fetcher",
        "soil_fetcher.py": "Soil data fetcher", 
        "satellite_fetcher.py": "Satellite data fetcher",
        "recommendation_engine.py": "NABARD recommendation engine",
        "report_generator.py": "AI report generator",
        "requirements.txt": "Python dependencies"
    }

    results = {}
    for file, description in required_files.items():
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"   {status} {file} - {description}")
        results[file] = exists

    return results

def install_dependencies() -> bool:
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")

    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("   ✅ Dependencies installed successfully")
            return True
        else:
            print("   ❌ Failed to install dependencies:")
            print(f"   {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("   ❌ Installation timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"   ❌ Installation error: {e}")
        return False

def check_api_keys() -> Dict[str, bool]:
    """Check if required API keys are available"""
    print("\n🔑 Checking API configuration...")

    api_checks = {
        "GOOGLE_API_KEY": {
            "required": False,
            "description": "Google Gemini API (for AI reports)",
            "url": "https://makersuite.google.com/app/apikey"
        },
        "VISUAL_CROSSING_API_KEY": {
            "required": False,
            "description": "Visual Crossing Weather API (default provided)",
            "url": "https://www.visualcrossing.com/sign-up"
        }
    }

    results = {}
    for key, info in api_checks.items():
        value = os.environ.get(key)
        has_key = bool(value)

        if has_key:
            print(f"   ✅ {key} - Found")
        elif info["required"]:
            print(f"   ❌ {key} - REQUIRED but not found")
            print(f"      Get key from: {info['url']}")
        else:
            print(f"   ⚠️  {key} - Optional (not set)")
            print(f"      For {info['description']}")
            print(f"      Get key from: {info['url']}")

        results[key] = has_key

    return results

def check_earth_engine() -> bool:
    """Check Google Earth Engine authentication"""
    print("\n🛰️  Checking Google Earth Engine...")

    try:
        import ee
        ee.Initialize()
        print("   ✅ Earth Engine authenticated and ready")
        return True
    except Exception as e:
        print("   ⚠️  Earth Engine not authenticated or unavailable")
        print("      Run: earthengine authenticate")
        print("      Note: Satellite data will use mock data if unavailable")
        return False

def validate_farms_data() -> bool:
    """Validate farms.csv data"""
    print("\n🚜 Validating farms data...")

    if not os.path.exists("farms.csv"):
        print("   ❌ farms.csv not found")
        return False

    try:
        import pandas as pd
        df = pd.read_csv("farms.csv")

        # Check required columns
        required_cols = ['farm_id', 'lat', 'lon']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"   ❌ Missing required columns: {missing_cols}")
            return False

        # Check data types and ranges
        if df['lat'].dtype not in ['float64', 'float32']:
            print("   ❌ Latitude column must be numeric")
            return False

        if df['lon'].dtype not in ['float64', 'float32']:
            print("   ❌ Longitude column must be numeric")
            return False

        # Check coordinate ranges
        if not df['lat'].between(-90, 90).all():
            print("   ❌ Invalid latitude values (must be -90 to 90)")
            return False

        if not df['lon'].between(-180, 180).all():
            print("   ❌ Invalid longitude values (must be -180 to 180)")
            return False

        print(f"   ✅ Farms data valid - {len(df)} farms loaded")
        print(f"      Farms: {list(df['farm_id'])}")
        return True

    except Exception as e:
        print(f"   ❌ Error validating farms data: {e}")
        return False

def create_directories():
    """Create necessary output directories"""
    print("\n📁 Creating output directories...")

    directories = ["data", "output", "reports", "raw_soil"]

    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"   ✅ Created/verified: {dir_name}/")

def run_quick_test() -> bool:
    """Run a quick test of the main components"""
    print("\n🧪 Running component tests...")

    try:
        # Test import of main modules
        print("   🔄 Testing module imports...")

        sys.path.append('.')  # Add current directory to path

        modules_to_test = [
            ("weather_fetcher", "WeatherDataFetcher"),
            ("soil_fetcher", "SoilDataFetcher"),
            ("satellite_fetcher", "SatelliteDataFetcher"),
            ("recommendation_engine", "PerfectedNABARDRecommendationEngine")
        ]

        for module_name, class_name in modules_to_test:
            try:
                module = __import__(module_name)
                cls = getattr(module, class_name)
                print(f"      ✅ {module_name}.{class_name}")
            except Exception as e:
                print(f"      ❌ {module_name}.{class_name} - {e}")
                return False

        print("   ✅ All core modules import successfully")
        return True

    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return False

def print_next_steps(results: Dict[str, bool]):
    """Print next steps based on setup results"""
    print("\n" + "=" * 70)
    print("🎯 SETUP SUMMARY & NEXT STEPS")
    print("=" * 70)

    all_good = all(results.values())

    if all_good:
        print("✅ Setup completed successfully! You're ready to run the pipeline.")
        print("\n🚀 To run the complete pipeline:")
        print("   python main.py")
        print("\n📊 Expected outputs:")
        print("   • data/ - Raw data files (weather, soil, satellite)")
        print("   • output/ - JSON recommendation files")
        print("   • reports/ - AI-generated detailed reports")

    else:
        print("⚠️  Setup completed with warnings. The pipeline may have limited functionality.")

        print("\n🔧 Optional improvements:")

        if not results.get("google_api_key", True):
            print("   • Set GOOGLE_API_KEY environment variable for AI reports")
            print("     export GOOGLE_API_KEY='your_key_here'")

        if not results.get("earth_engine", True):
            print("   • Run 'earthengine authenticate' for satellite data")
            print("     (Mock data will be used otherwise)")

        print("\n🚀 You can still run the pipeline:")
        print("   python main.py")

    print("\n📖 For more information, see README.md")
    print("💬 For support, check the GitHub issues page")

def main():
    """Main setup function"""
    print_header()

    results = {}

    # Step 1: Check Python version
    results["python_version"] = check_python_version()

    if not results["python_version"]:
        print("\n❌ Setup cannot continue with incompatible Python version.")
        return False

    # Step 2: Check required files
    file_results = check_required_files()
    results["required_files"] = all(file_results.values())

    if not results["required_files"]:
        print("\n❌ Setup cannot continue with missing files.")
        return False

    # Step 3: Install dependencies
    print("\n❓ Install Python dependencies? (y/n): ", end="")
    if input().lower().strip() in ['y', 'yes', '']:
        results["dependencies"] = install_dependencies()
    else:
        results["dependencies"] = True
        print("   ⏭️  Skipping dependency installation")

    # Step 4: Check API keys
    api_results = check_api_keys()
    results["google_api_key"] = api_results.get("GOOGLE_API_KEY", False)

    # Step 5: Check Earth Engine
    results["earth_engine"] = check_earth_engine()

    # Step 6: Validate farms data
    results["farms_data"] = validate_farms_data()

    # Step 7: Create directories
    create_directories()
    results["directories"] = True

    # Step 8: Run component tests
    results["component_tests"] = run_quick_test()

    # Step 9: Print next steps
    print_next_steps(results)

    return results["required_files"] and results["dependencies"] and results["farms_data"]

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)
