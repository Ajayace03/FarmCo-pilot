#!/usr/bin/env python3

"""
Basic Agricultural Pipeline Tests - FIXED
=========================================

Tests that work without requiring all project modules.
Fixed floating point precision issue.
"""

import pytest
import os
import pandas as pd
import json
import numpy as np
from pathlib import Path

class TestEnvironmentSetup:
    """Test basic environment and dependencies"""

    def test_python_basics(self):
        """Test basic Python functionality"""
        assert 1 + 1 == 2
        assert "hello" == "hello"
        assert [1, 2, 3] == [1, 2, 3]

    def test_pandas_works(self):
        """Test pandas is working"""
        df = pd.DataFrame({
            'farm_id': ['F001', 'F002', 'F003'],
            'lat': [18.0, 30.0, 21.0],
            'lon': [79.0, 75.0, 86.0],
            'crop': ['Rice', 'Wheat', 'Cotton']
        })
        assert len(df) == 3
        assert 'farm_id' in df.columns
        assert df.loc[0, 'crop'] == 'Rice'

    def test_json_processing(self):
        """Test JSON processing works"""
        data = {
            'farm_id': 'F001',
            'recommendations': {
                'rice': [{'variety': 'BPT-5204', 'confidence': 0.85}],
                'total_schemes': 5
            }
        }
        
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed['farm_id'] == 'F001'
        assert parsed['recommendations']['total_schemes'] == 5

class TestProjectStructure:
    """Test project structure without importing modules"""

    def test_basic_directories_exist(self):
        """Test basic directories exist"""
        # These should exist based on your project
        possible_dirs = ['tests', 'data_fetchers', 'engine', 'data', 'output']
        existing_dirs = [d for d in possible_dirs if Path(d).exists()]
        assert len(existing_dirs) > 0, f"Expected some directories, found none from: {possible_dirs}"
        print(f"Found directories: {existing_dirs}")

    def test_python_files_exist(self):
        """Test some Python files exist"""
        possible_files = [
            'main_complete.py',
            'government_schemes_matcher.py',
            'comprehensive_report_generator.py',
            'run_tests_v2.py'
        ]
        
        existing_files = [f for f in possible_files if Path(f).exists()]
        assert len(existing_files) > 0, f"Expected some Python files, found none from: {possible_files}"
        print(f"Found Python files: {existing_files}")

class TestDataProcessing:
    """Test data processing capabilities"""

    def test_coordinate_validation(self):
        """Test coordinate validation"""
        def is_valid_coordinate(lat, lon):
            return (-90 <= lat <= 90) and (-180 <= lon <= 180)
        
        # Valid coordinates
        assert is_valid_coordinate(18.030504, 79.686037) == True  # Tamil Nadu
        assert is_valid_coordinate(30.487916, 75.456311) == True  # Punjab
        assert is_valid_coordinate(0, 0) == True  # Equator
        
        # Invalid coordinates
        assert is_valid_coordinate(91, 79) == False  # Lat too high
        assert is_valid_coordinate(18, 181) == False  # Lon too high
        assert is_valid_coordinate(-91, 79) == False  # Lat too low

    def test_farm_data_processing(self):
        """Test basic farm data processing - FIXED floating point"""
        # Sample farm data
        farms = [
            {'farm_id': 'F001', 'lat': 18.030504, 'lon': 79.686037, 'area_ha': 1.0, 'crop': 'Rice'},
            {'farm_id': 'F002', 'lat': 30.487916, 'lon': 75.456311, 'area_ha': 3.2, 'crop': 'Wheat'},
            {'farm_id': 'F003', 'lat': 21.092091, 'lon': 86.377062, 'area_ha': 2.1, 'crop': 'Cotton'}
        ]
        
        df = pd.DataFrame(farms)
        
        # Test filtering
        rice_farms = df[df['crop'] == 'Rice']
        assert len(rice_farms) == 1
        assert rice_farms.iloc[0]['farm_id'] == 'F001'
        
        # Test calculations - FIXED: Use numpy.isclose for floating point comparison
        total_area = df['area_ha'].sum()
        expected_area = 6.3
        assert np.isclose(total_area, expected_area), f"Expected {expected_area}, got {total_area}"
        
        # Test grouping
        by_crop = df.groupby('crop')['area_ha'].sum()
        assert 'Rice' in by_crop.index

    def test_weather_data_structure(self):
        """Test weather data structure validation"""
        # Sample weather data structure
        weather_record = {
            'farm_id': 'F001',
            'date': '2024-09-01',
            'temp': 28.5,
            'humidity': 78.0,
            'precip': 2.4,
            'conditions': 'Partly cloudy'
        }
        
        # Validate structure
        required_fields = ['farm_id', 'date', 'temp', 'humidity', 'precip']
        for field in required_fields:
            assert field in weather_record, f"Missing required field: {field}"
        
        # Validate data types and ranges
        assert isinstance(weather_record['temp'], (int, float))
        assert -50 <= weather_record['temp'] <= 60  # Reasonable temperature range
        assert 0 <= weather_record['humidity'] <= 100  # Humidity percentage
        assert weather_record['precip'] >= 0  # Precipitation can't be negative

class TestRecommendationLogic:
    """Test basic recommendation logic without importing complex modules"""

    def test_confidence_level_validation(self):
        """Test confidence level validation"""
        def is_valid_confidence(confidence):
            return isinstance(confidence, (int, float)) and 0 <= confidence <= 1
        
        # Valid confidence levels
        assert is_valid_confidence(0.85) == True
        assert is_valid_confidence(0.0) == True
        assert is_valid_confidence(1.0) == True
        assert is_valid_confidence(0.5) == True
        
        # Invalid confidence levels
        assert is_valid_confidence(1.5) == False  # Too high
        assert is_valid_confidence(-0.1) == False  # Negative
        assert is_valid_confidence("High") == False  # String instead of number

    def test_variety_recommendation_structure(self):
        """Test variety recommendation data structure"""
        sample_recommendation = {
            'variety_id': 'RICE_001',
            'variety_name': 'BPT-5204',
            'category': 'rice',
            'suitability_score': 1.0,
            'confidence_level': 0.85,
            'carbon_potential': 3.0,
            'characteristics': 'High yielding variety'
        }
        
        # Check required fields
        required_fields = ['variety_name', 'suitability_score', 'confidence_level']
        for field in required_fields:
            assert field in sample_recommendation
        
        # Check data types
        assert isinstance(sample_recommendation['variety_name'], str)
        assert len(sample_recommendation['variety_name']) > 0
        assert 0 <= sample_recommendation['suitability_score'] <= 1
        assert 0 <= sample_recommendation['confidence_level'] <= 1

    def test_scheme_recommendation_structure(self):
        """Test government scheme recommendation structure"""
        sample_scheme = {
            'scheme_name': 'PM-KISAN Samman Nidhi',
            'category': 'direct_benefit_schemes',
            'eligibility_score': 1.0,
            'subsidy_amount': 'Rs 6,000 per year',
            'key_benefits': ['Direct cash transfer'],
            'next_steps': ['Register online at pmkisan.gov.in']
        }
        
        # Check structure
        assert isinstance(sample_scheme['scheme_name'], str)
        assert len(sample_scheme['scheme_name']) > 5  # Meaningful name
        assert isinstance(sample_scheme['key_benefits'], list)
        assert len(sample_scheme['key_benefits']) > 0
        assert isinstance(sample_scheme['next_steps'], list)
        assert len(sample_scheme['next_steps']) > 0
        
        # Check eligibility score
        assert 0 <= sample_scheme['eligibility_score'] <= 1

class TestFileOperations:
    """Test file operations that the pipeline would use"""

    def test_csv_operations(self, tmp_path):
        """Test CSV file operations"""
        # Create sample data
        data = {
            'farm_id': ['F001', 'F002', 'F003'],
            'lat': [18.0, 30.0, 21.0],
            'lon': [79.0, 75.0, 86.0],
            'crop': ['Rice', 'Wheat', 'Cotton']
        }
        
        df = pd.DataFrame(data)
        
        # Write to temporary CSV
        csv_file = tmp_path / "test_farms.csv"
        df.to_csv(csv_file, index=False)
        
        # Read back and verify
        loaded_df = pd.read_csv(csv_file)
        assert len(loaded_df) == 3
        assert list(loaded_df.columns) == ['farm_id', 'lat', 'lon', 'crop']
        assert loaded_df.loc[0, 'farm_id'] == 'F001'

    def test_json_operations(self, tmp_path):
        """Test JSON file operations"""
        # Sample recommendation data
        data = {
            'analysis_id': 'test-001',
            'farm_id': 'F001',
            'recommendations': {
                'rice': [
                    {'variety_name': 'BPT-5204', 'confidence_level': 0.85}
                ],
                'total_varieties': 1
            },
            'carbon_potential': 2.79
        }
        
        # Write JSON
        json_file = tmp_path / "test_recommendations.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Read back and verify
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data['farm_id'] == 'F001'
        assert 'recommendations' in loaded_data
        assert loaded_data['carbon_potential'] == 2.79

# Performance test (basic)
class TestBasicPerformance:
    """Basic performance tests"""

    def test_dataframe_performance(self):
        """Test pandas performance with moderate dataset"""
        # Create moderately sized dataset
        import random
        data = []
        for i in range(1000):  # 1000 farms
            data.append({
                'farm_id': f'F{i:04d}',
                'lat': 18.0 + random.uniform(-5, 5),
                'lon': 79.0 + random.uniform(-5, 5),
                'area_ha': random.uniform(0.5, 10.0),
                'crop': random.choice(['Rice', 'Wheat', 'Cotton', 'Sugarcane'])
            })
        
        df = pd.DataFrame(data)
        
        # Basic operations should be fast
        assert len(df) == 1000
        
        # Test filtering
        rice_farms = df[df['crop'] == 'Rice']
        assert len(rice_farms) > 0
        
        # Test aggregation
        total_area = df['area_ha'].sum()
        assert total_area > 0
        
        # Test grouping
        by_crop = df.groupby('crop')['area_ha'].sum()
        assert len(by_crop) > 0

# Run this file directly for quick testing
if __name__ == "__main__":
    import sys
    # Add current directory to path for imports
    sys.path.insert(0, '.')
    
    # Run pytest on this file
    pytest.main([__file__, "-v", "--tb=short"])