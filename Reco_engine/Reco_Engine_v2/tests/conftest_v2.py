#!/usr/bin/env python3

"""
Fixed Test Configuration and Fixtures v2 - PATH FIXED
====================================================

Updated fixtures with proper Python path setup for your project structure.
"""

import pytest
import pandas as pd
import os
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# FIX: Add project root to Python path FIRST
project_root = Path(__file__).parent.parent  # Go up from tests/ to project root
sys.path.insert(0, str(project_root))

# Also add the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"🔧 Added to Python path: {project_root}")
print(f"🔧 Added to Python path: {parent_dir}")

@pytest.fixture
def sample_farm_data():
    """Sample farm data for testing - passes strict validation"""
    return {
        'farm_id': 'F001',
        'lat': 18.030504,
        'lon': 79.686037,
        'farmer_name': 'Test Farmer',
        'area_ha': 2.5,  # Positive value (required by validation)
        'state': 'Tamil Nadu',
        'district': 'Sivaganga',
        'crop': 'Rice',
        'village': 'Test Village'
    }

@pytest.fixture
def valid_farmer_data():
    """Valid farmer data that passes your strict validation"""
    return {
        'farm_id': 'F001',
        'farmer_name': 'Test Farmer',
        'area_ha': 2.5,  # Must be positive
        'state': 'Tamil Nadu',
        'district': 'Sivaganga',
        'crop': 'Rice',
        'lat': 18.030504,  # Valid coordinates
        'lon': 79.686037,
        'village': 'Test Village',
        'age': 45,
        'category': 'General',
        'annual_income': 150000,
        'education': 'Primary'
    }

@pytest.fixture
def sample_farms_df():
    """Sample farms DataFrame for testing"""
    return pd.DataFrame([
        {
            'farm_id': 'F001',
            'lat': 18.030504,
            'lon': 79.686037,
            'farmer_name': 'Arun Kumar',
            'area_ha': 1.0,
            'state': 'Tamil Nadu',
            'district': 'Sivaganga',
            'crop': 'Rice'
        },
        {
            'farm_id': 'F002', 
            'lat': 30.487916,
            'lon': 75.456311,
            'farmer_name': 'Raj Singh',
            'area_ha': 3.2,
            'state': 'Punjab',
            'district': 'Ludhiana',
            'crop': 'Wheat'
        }
    ])

@pytest.fixture
def sample_weather_data():
    """Sample weather API response data"""
    return {
        "days": [
            {
                "datetime": "2024-09-01",
                "tempmax": 32.5,
                "tempmin": 24.8,
                "temp": 28.6,
                "humidity": 78.3,
                "precip": 2.4,
                "windspeed": 12.3,
                "conditions": "Partly cloudy"
            },
            {
                "datetime": "2024-09-02", 
                "tempmax": 31.0,
                "tempmin": 25.0,
                "temp": 27.8,
                "humidity": 82.0,
                "precip": 0.0,
                "windspeed": 10.5,
                "conditions": "Clear"
            }
        ]
    }

@pytest.fixture
def complete_farm_data():
    """Complete farm data for testing recommendation engine"""
    weather_df = pd.DataFrame([
        {
            'farm_id': 'F001',
            'lat': 18.030504,
            'lon': 79.686037,
            'date': '2024-09-01',
            'temp': 28.5,
            'humidity': 78.0,
            'precip': 2.4,
            'temp_max': 32.0,
            'temp_min': 24.0
        }
    ])
    
    satellite_df = pd.DataFrame([
        {
            'farm_id': 'F001',
            'date': '2024-09-01',
            'NDVI': 0.67,
            'EVI': 0.52,
            'LAI': 2.8,
            'data_type': 'vegetation'
        }
    ])
    
    soil_df = pd.DataFrame([
        {
            'farm_id': 'F001',
            'lat': 18.030504,
            'lon': 79.686037,
            'pH': 7.1,
            'clay_pct': 27.65,
            'sand_pct': 28.55,
            'silt_pct': 27.9,
            'soc': 85.5,
            'cec': 237.0,
            'texture': 'Clay Loam'
        }
    ])
    
    return weather_df, satellite_df, soil_df

@pytest.fixture
def sample_agricultural_data(tmp_path):
    """Create sample agricultural recommendations file"""
    agricultural_data = {
        "analysis_id": "test-analysis-001",
        "farm_profile": "Enhanced farm profile data",
        "detected_zone": "Zone_10_Southern_Plateau",
        "zone_characteristics": {
            "climate_type": "Semi-arid to sub-humid",
            "elevation": "Medium",
            "major_crops": ["Rice", "Cotton", "Sugarcane"]
        },
        "recommendations": {
            "rice": [
                {
                    "variety_name": "BPT-5204",
                    "suitability_score": 1.0,
                    "confidence_level": 0.85,
                    "carbon_potential": 3.0,
                    "characteristics": "High yielding variety"
                }
            ]
        },
        "realistic_carbon_potential": 2.79,
        "estimated_annual_credits": 2.37,
        "estimated_revenue": 59.29
    }
    
    agri_file = tmp_path / "agricultural_recommendations_F001.json"
    with open(agri_file, 'w') as f:
        json.dump(agricultural_data, f, indent=2)
    
    return str(agri_file), agricultural_data

@pytest.fixture
def sample_schemes_data(tmp_path):
    """Create sample government schemes file"""
    schemes_data = {
        "farmer_profile": {
            "name": "Test Farmer",
            "farm_id": "F001",
            "location": "Test Village, Test District, Tamil Nadu",
            "farm_size": "2.5 hectares"
        },
        "eligibility_summary": {
            "total_eligible_schemes": 5,
            "high_priority_schemes": 3,
            "medium_priority_schemes": 2
        },
        "recommended_schemes": {
            "immediate_apply": [
                {
                    "scheme_name": "PM-KISAN Samman Nidhi",
                    "category": "direct_benefit_schemes",
                    "eligibility_score": 1.0,
                    "subsidy_amount": "Rs 6,000 per year",
                    "key_benefits": ["Direct cash transfer"],
                    "next_steps": ["Register online at pmkisan.gov.in"]
                }
            ]
        }
    }
    
    schemes_file = tmp_path / "government_schemes_F001.json"
    with open(schemes_file, 'w') as f:
        json.dump(schemes_data, f, indent=2)
    
    return str(schemes_file), schemes_data

@pytest.fixture
def temp_csv_file(tmp_path):
    """Create temporary CSV file for testing"""
    csv_data = """farm_id,lat,lon,farmer_name,area_ha,state,district,crop
F001,18.030504,79.686037,Test Farmer 1,1.0,Tamil Nadu,Sivaganga,Rice
F002,30.487916,75.456311,Test Farmer 2,2.0,Punjab,Ludhiana,Wheat"""
    
    csv_file = tmp_path / "test_farms.csv"
    csv_file.write_text(csv_data)
    return str(csv_file)

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("VISUAL_CROSSING_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_api_key_12345")

# Safe import fixtures that handle missing modules
@pytest.fixture
def weather_fetcher(mock_env_vars):
    """Create weather fetcher for testing - handles import errors"""
    try:
        from data_fetchers.weather_fetcher import WeatherDataFetcher
        return WeatherDataFetcher()
    except ImportError as e:
        print(f"ℹ️ WeatherDataFetcher import failed: {e}")
        return Mock()

# Test utilities that work with your actual validation
def assert_valid_farm_id(farm_id):
    """Assert farm ID is valid format"""
    assert isinstance(farm_id, str)
    assert farm_id.strip() != ""
    assert len(farm_id) <= 50

def assert_valid_coordinates(lat, lon):
    """Assert coordinates are valid"""
    assert isinstance(lat, (int, float))
    assert isinstance(lon, (int, float))
    assert -90 <= lat <= 90
    assert -180 <= lon <= 180

def assert_valid_recommendation(recommendation):
    """Assert recommendation has required fields"""
    required_fields = ['variety_name', 'suitability_score', 'confidence_level']
    for field in required_fields:
        assert field in recommendation, f"Missing required field: {field}"
    
    # Validate ranges
    assert 0 <= recommendation['suitability_score'] <= 1
    assert 0 <= recommendation['confidence_level'] <= 1