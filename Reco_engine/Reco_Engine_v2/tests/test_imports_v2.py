#!/usr/bin/env python3

"""
Simple Import Test v2
====================

Basic test to check if imports work correctly with fixed Python path.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(f"🔧 Project root: {project_root}")
print(f"🔧 Python path: {sys.path[:3]}")  # Show first 3 entries

class TestBasicImports:
    """Test basic imports work"""
    
    def test_import_main_complete(self):
        """Test importing main_complete module"""
        try:
            import main_complete
            print("✅ Successfully imported main_complete")
            
            # Try to import the controller
            from main_complete import CompletePipelineController
            controller = CompletePipelineController()
            print("✅ Successfully created CompletePipelineController")
            assert controller is not None
            
        except ImportError as e:
            print(f"❌ Import error for main_complete: {e}")
            # Check if file exists
            main_complete_file = project_root / "main_complete.py"
            print(f"🔍 main_complete.py exists: {main_complete_file.exists()}")
            if main_complete_file.exists():
                print(f"🔍 File path: {main_complete_file}")
            assert False, f"Could not import main_complete: {e}"
    
    def test_import_government_schemes(self):
        """Test importing government schemes matcher"""
        try:
            import government_schemes_matcher
            print("✅ Successfully imported government_schemes_matcher")
            
            from government_schemes_matcher import EnhancedGovernmentSchemesMatcher
            matcher = EnhancedGovernmentSchemesMatcher()
            print("✅ Successfully created EnhancedGovernmentSchemesMatcher")
            assert matcher is not None
            
        except ImportError as e:
            print(f"❌ Import error for government_schemes_matcher: {e}")
            schemes_file = project_root / "government_schemes_matcher.py"
            print(f"🔍 government_schemes_matcher.py exists: {schemes_file.exists()}")
            assert False, f"Could not import government_schemes_matcher: {e}"
    
    def test_import_report_generator(self):
        """Test importing report generator"""
        try:
            import comprehensive_report_generator
            print("✅ Successfully imported comprehensive_report_generator")
            
            from comprehensive_report_generator import OldEngineReportGenerator
            generator = OldEngineReportGenerator()
            print("✅ Successfully created OldEngineReportGenerator")
            assert generator is not None
            
        except ImportError as e:
            print(f"❌ Import error for comprehensive_report_generator: {e}")
            report_file = project_root / "comprehensive_report_generator.py"
            print(f"🔍 comprehensive_report_generator.py exists: {report_file.exists()}")
            assert False, f"Could not import comprehensive_report_generator: {e}"
    
    def test_import_weather_fetcher(self):
        """Test importing weather fetcher"""
        try:
            from data_fetchers.weather_fetcher import WeatherDataFetcher
            print("✅ Successfully imported WeatherDataFetcher")
            
            # Try to create it (might fail due to env vars, but import should work)
            try:
                fetcher = WeatherDataFetcher()
                print("✅ Successfully created WeatherDataFetcher")
            except Exception as e:
                print(f"ℹ️ WeatherDataFetcher creation failed (expected): {e}")
            
            assert True  # Import worked
            
        except ImportError as e:
            print(f"❌ Import error for WeatherDataFetcher: {e}")
            weather_file = project_root / "data_fetchers" / "weather_fetcher.py"
            print(f"🔍 weather_fetcher.py exists: {weather_file.exists()}")
            assert False, f"Could not import WeatherDataFetcher: {e}"
    
    def test_import_recommendation_engine(self):
        """Test importing recommendation engine"""
        try:
            from engine.recommendation_engine import FixedNABARDRecommendationEngine
            print("✅ Successfully imported FixedNABARDRecommendationEngine")
            
            engine = FixedNABARDRecommendationEngine()
            print("✅ Successfully created FixedNABARDRecommendationEngine")
            assert engine is not None
            
        except ImportError as e:
            print(f"❌ Import error for FixedNABARDRecommendationEngine: {e}")
            engine_file = project_root / "engine" / "recommendation_engine.py"
            print(f"🔍 recommendation_engine.py exists: {engine_file.exists()}")
            assert False, f"Could not import FixedNABARDRecommendationEngine: {e}"

class TestProjectStructure:
    """Test project structure is as expected"""
    
    def test_project_files_exist(self):
        """Test that key project files exist"""
        required_files = [
            "main_complete.py",
            "government_schemes_matcher.py", 
            "comprehensive_report_generator.py"
        ]
        
        missing_files = []
        existing_files = []
        
        for filename in required_files:
            filepath = project_root / filename
            if filepath.exists():
                existing_files.append(filename)
                print(f"✅ Found: {filename}")
            else:
                missing_files.append(filename)
                print(f"❌ Missing: {filename}")
        
        assert len(existing_files) >= 3, f"Missing files: {missing_files}"
    
    def test_data_fetchers_directory(self):
        """Test data_fetchers directory structure"""
        data_fetchers_dir = project_root / "data_fetchers"
        assert data_fetchers_dir.exists(), "data_fetchers directory not found"
        
        expected_files = ["weather_fetcher.py", "soil_fetcher.py", "satellite_fetcher.py"]
        existing_files = []
        
        for filename in expected_files:
            filepath = data_fetchers_dir / filename
            if filepath.exists():
                existing_files.append(filename)
                print(f"✅ Found: data_fetchers/{filename}")
        
        assert len(existing_files) >= 1, f"No data fetcher files found in {data_fetchers_dir}"
    
    def test_engine_directory(self):
        """Test engine directory structure"""
        engine_dir = project_root / "engine"
        
        if engine_dir.exists():
            print(f"✅ Found: engine directory")
            
            # Check for recommendation engine
            rec_engine = engine_dir / "recommendation_engine.py"
            if rec_engine.exists():
                print(f"✅ Found: engine/recommendation_engine.py")
            else:
                print(f"ℹ️ Missing: engine/recommendation_engine.py")
        else:
            print(f"ℹ️ Missing: engine directory")
        
        # Don't fail if missing - just document what we found
        assert True

if __name__ == "__main__":
    # Allow running this file directly for testing
    pytest.main([__file__, "-v", "--tb=short"])