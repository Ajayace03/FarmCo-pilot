<p align="center">
  <img src=:"../../assets/Reco_banner.png" alt="FarmCo-Pilot Recommendation_Engine Banner" width="100%">
</p>


# Agricultural Recommendation Engine Pipeline
## Complete End-to-End AI-Powered Farming Solution

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/your-username/agricultural-recommendation-engine)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active%20Development-orange.svg)]()


### 🌾 Overview

A comprehensive agricultural recommendation system that processes farm location data, fetches multi-source agricultural data (weather, soil, satellite), generates intelligent crop and agroforestry recommendations using NABARD-compliant algorithms, and produces detailed AI-powered reports using Google Gemini.

**Key Capabilities:**
- ✅ Multi-source data integration (Weather, Soil, Satellite)
- ✅ NABARD-compliant crop recommendations (147 varieties, 15 zones)
- ✅ Realistic carbon credit calculations
- ✅ AI-powered detailed reports
- ✅ Local data processing (no cloud dependencies)

### 🏗️ System Architecture

```
Input Data (farms.csv)
          ↓
┌─────────────────────────────────────────────────┐
│               Data Fetchers                     │
│  ┌─────────────┬─────────────┬─────────────┐    │
│  │   Weather   │    Soil     │  Satellite  │    │
│  │   Fetcher   │   Fetcher   │   Fetcher   │    │
│  │             │             │             │    │
│  │ Visual      │ ISRIC       │ Google      │    │
│  │ Crossing    │ SoilGrids   │ Earth       │    │
│  │ API         │ API         │ Engine      │    │
│  └─────────────┴─────────────┴─────────────┘    │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│             Raw Data Storage                    │
│  farm_weather_history.csv | soil_test.csv |    │
│         satellite_data_ultimate.csv             │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│          NABARD Recommendation Engine           │
│  • 147 Crop Varieties • 15 Agro-Climatic Zones │
│  • Multi-factor Scoring • Carbon Calculations  │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│         JSON Recommendations per Farm           │
│  perfected_recommendations_F001.json, etc.     │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│            AI Report Generator                  │
│        (Google Gemini 1.5 Flash)               │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│            Final AI Reports                     │
│    fixed_agri_report_F001.json, etc.           │
└─────────────────────────────────────────────────┘
```

### 🚀 Quick Start

#### 1. **Prerequisites & Installation**

```bash
# Python 3.8+ required
python --version

# Clone or download the project files
# Ensure you have all Python files in the same directory

# Install dependencies
pip install -r requirements.txt

# Optional: Set up Google Earth Engine (for satellite data)
pip install earthengine-api
earthengine authenticate

# Optional: Set up API keys for enhanced functionality
export GOOGLE_API_KEY="your_gemini_api_key_here"          # For AI reports
export VISUAL_CROSSING_API_KEY="your_weather_key_here"    # Weather data (optional)
```

#### 2. **Prepare Input Data**

Create `farms.csv` with your farm data:
```csv
farm_id,farmer_id,farmer_name,lat,lon,area_ha,village,district,state,main_crop
F001,NBF_001,Arun Kumar,11.546179,76.41653,1.0,Kundrakudi,Karaikudi,Tamil Nadu,Rice
F002,NBF_002,Meena Devi,30.487916,75.456311,1.0,Bhiwani,Bhiwani,Haryana,Groundnut
F003,NBF_003,Ramesh Babu,21.092091,86.377062,1.0,Bhubaneswar,Khordha,Odisha,Maize
```

**Required Columns:**
- `farm_id`: Unique identifier for each farm
- `lat`, `lon`: GPS coordinates in decimal degrees
- Other columns are optional but recommended

#### 3. **Run Complete Pipeline**

```bash
# Single command to run entire pipeline
python main.py
```

**What happens when you run this:**
1. 🔄 **Validation**: Checks input data and dependencies
2. 🌤️ **Weather Data**: Fetches 365-day historical weather
3. 🌱 **Soil Data**: Collects soil properties from SoilGrids
4. 🛰️ **Satellite Data**: Processes vegetation indices from Earth Engine
5. 🧠 **Analysis**: Generates NABARD-compliant recommendations  
6. 🤖 **AI Reports**: Creates detailed reports using Gemini AI

### 📁 Actual Project Structure

```
agricultural-recommendation-engine/
├── main.py                           # 🎯 Main pipeline controller
├── farms.csv                         # 📊 Input farm data
├── requirements.txt                  # 📋 Python dependencies
├── setup.py                          # 🔧 Setup and validation script
├── README.md                         # 📖 This documentation
│
├── weather_fetcher.py                # 🌤️ Weather data collection
├── soil_fetcher.py                   # 🌱 Soil analysis fetching
├── satellite_fetcher.py              # 🛰️ Satellite data processing
├── recommendation_engine.py          # 🧠 NABARD recommendation system
├── report_generator.py               # 🤖 AI report generation
│
├── data/                             # 📁 Generated raw data
│   ├── farm_weather_history.csv      #     Weather records
│   ├── soil_test.csv                 #     Soil analysis
│   └── satellite_data_ultimate.csv   #     Satellite indices
│
├── output/                           # 📁 Recommendation files
│   ├── perfected_recommendations_F001.json
│   ├── perfected_recommendations_F002.json
│   └── perfected_recommendations_F003.json
│
└── reports/                          # 📁 AI-generated reports
    ├── fixed_agri_report_F001.json
    ├── fixed_agri_report_F002.json
    └── fixed_agri_report_F003.json
```

### 🔧 Component Details

#### **1. Weather Fetcher** (`weather_fetcher.py`)
- **API**: Visual Crossing Weather API (default key provided)
- **Data Period**: 365-day historical weather records
- **Parameters**: Temperature, rainfall, humidity, wind speed, conditions
- **Features**: Automatic retry logic, rate limiting, error handling
- **Fallback**: Mock weather data if API unavailable

#### **2. Soil Fetcher** (`soil_fetcher.py`)
- **API**: ISRIC SoilGrids v2.0 (free, no key required)
- **Depths**: 0-5cm and 5-15cm soil layers
- **Properties**: pH, texture (clay/sand/silt %), organic carbon, CEC
- **Analysis**: Automated nutrient status and pH classification
- **Features**: Local caching, derived characteristics calculation

#### **3. Satellite Fetcher** (`satellite_fetcher.py`)
- **Platform**: Google Earth Engine (optional authentication)
- **Satellites**: Sentinel-2, MODIS, Sentinel-1
- **Indices**: NDVI, EVI, SAVI, LAI, soil moisture (VV/VH)
- **Coverage**: Monthly data for entire year
- **Fallback**: Realistic mock satellite data with seasonal patterns

#### **4. Recommendation Engine** (`recommendation_engine.py`)
- **Database**: 147 crop varieties across 15 Indian agro-climatic zones
- **Categories**: 51 rice varieties, 53 agroforestry species, 43 crop varieties
- **Algorithm**: Multi-factor suitability scoring (climate, soil, zone compatibility)
- **Output**: JSON recommendations with carbon credit calculations
- **Features**: Zone auto-detection, realistic carbon potential (2-15 tCO₂/ha/yr)

#### **5. Report Generator** (`report_generator.py`)
- **AI Model**: Google Gemini 1.5 Flash
- **Input**: Recommendation JSON files
- **Output**: Structured business intelligence reports
- **Analysis**: Risk assessment, revenue projections, actionable insights
- **Features**: Retry logic, simplified schema, batch processing

### 🎛️ Configuration & Customization

#### **Environment Variables (Optional)**
```bash
# For AI-powered reports (highly recommended)
export GOOGLE_API_KEY="your_gemini_api_key"

# For enhanced weather data (optional - default key provided)  
export VISUAL_CROSSING_API_KEY="your_weather_key"

# For satellite data (optional - mock data used if not available)
export EARTH_ENGINE_PROJECT="your_ee_project"
```

#### **Main Controller Parameters**
Edit these variables in `main.py`:
```python
WEATHER_DAYS_BACK = 365                    # Historical weather period
SATELLITE_START_DATE = "2024-01-01"        # Satellite data start date
SOIL_DEPTH_LAYERS = ["0-5cm", "5-15cm"]    # Soil analysis depths  
RECOMMENDATION_TOP_N = 5                   # Top recommendations per category
CARBON_CREDIT_PRICE = 25.0                 # USD per tCO₂ credit
```

### 📈 Output Data Formats

#### **Recommendation JSON** (`perfected_recommendations_F001.json`)
```json
{
  "analysis_id": "uuid-12345",
  "farm_profile": "EnhancedFarmProfile(...)",
  "detected_zone": "Zone_10_Southern_Plateau",
  "zone_characteristics": {
    "climate_type": "Semi-arid to sub-humid",
    "elevation": "Medium",
    "major_crops": ["Rice", "Cotton", "Sugarcane", "Groundnut"]
  },
  "recommendations": {
    "rice": [
      {
        "variety_id": "RICE_019",
        "variety_name": "BPT-5204", 
        "suitability_score": 0.847,
        "carbon_potential": 3.0,
        "market_value": "High",
        "confidence_level": 0.720
      }
    ],
    "crops": [...],
    "agroforestry": [...]
  },
  "realistic_carbon_potential": 5.2,
  "estimated_annual_credits": 4.42,
  "estimated_revenue": 110.5,
  "farming_scenario": {
    "rice_coverage": "40%",
    "primary_crop_coverage": "30%", 
    "secondary_crop_coverage": "20%",
    "agroforestry_coverage": "10%"
  }
}
```

#### **AI Report JSON** (`fixed_agri_report_F001.json`)
```json
{
  "farm_id": "F001",
  "metadata": {
    "analysis_date": "2025-09-04T23:05:00",
    "model_version": "v2.1",
    "detected_zone": {
      "code": "Zone_10_Southern_Plateau",
      "name": "Southern Plateau and Hills Region"
    }
  },
  "report": {
    "farm_profile": {
      "location": {"latitude": 11.546179, "longitude": 76.41653},
      "climate": {"annual_rainfall_mm": 1247, "avg_temp_c": 28.5},
      "soil": {"ph": 6.8, "texture": "Sandy loam", "organic_carbon_pct": 1.2}
    },
    "recommendations": {...},
    "carbon_revenue": {
      "realistic_carbon_potential_t_ha": 5.2,
      "estimated_annual_credits": 4.42,
      "estimated_revenue_inr": 9200
    },
    "final_summary": "Based on comprehensive analysis..."
  }
}
```

### 🔍 Troubleshooting

#### **Common Issues & Quick Fixes**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Missing Dependencies** | `ModuleNotFoundError` | `pip install -r requirements.txt` |
| **Earth Engine Auth** | Satellite data fails | `earthengine authenticate` or use mock data |
| **API Key Issues** | AI reports fail | Set `GOOGLE_API_KEY` environment variable |
| **Invalid Coordinates** | Zone detection fails | Check lat/lon are in decimal degrees |
| **File Not Found** | `farms.csv` missing | Ensure farms.csv exists with correct columns |

#### **Validation Script**
```bash
# Run setup validation before main pipeline
python setup.py
```

### 📊 Performance Metrics

#### **Processing Capacity**
- **Tested Range**: 3-100 farms successfully processed
- **Data Volume**: ~1-2MB generated data per farm
- **Processing Time**: 
  - With APIs: ~2-3 minutes per farm
  - Mock data only: ~30 seconds per farm
- **Memory Usage**: ~500MB peak for 10 farms

#### **API Rate Limits & Quotas**
- **Visual Crossing**: 1,000 calls/day (free tier) - 1 call per farm
- **ISRIC SoilGrids**: No official limits - 1 call per farm  
- **Google Earth Engine**: 25,000 requests/day (free tier) - ~12 calls per farm
- **Google Gemini**: Varies by plan - 1 call per farm for reports

### 🛡️ Data Privacy & Security

- ✅ **Local Processing**: All data stored locally, no cloud uploads
- ✅ **Minimal Data**: Only coordinates and agricultural parameters collected
- ✅ **API Security**: Keys stored in environment variables only
- ✅ **Open Source**: Full code transparency
- ✅ **GDPR Friendly**: No personal data collection or storage

### 📋 System Requirements

#### **Minimum Requirements**
- Python 3.8+
- 4GB RAM
- 1GB free disk space
- Internet connection (for data fetching)

#### **Recommended Setup**
- Python 3.9+
- 8GB RAM  
- 5GB free disk space
- Stable internet connection
- Google Earth Engine account (free)
- Google Cloud API key (for AI reports)

### 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Follow Code Style**: Use Python PEP 8 standards
4. **Add Tests**: Ensure new features work correctly
5. **Update Documentation**: Keep README and docstrings current
6. **Submit Pull Request**: Describe your changes clearly

#### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/your-username/agricultural-recommendation-engine.git
cd agricultural-recommendation-engine

# Create virtual environment
python -m venv agri_env
source agri_env/bin/activate  # On Windows: agri_env\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Development tools

# Run tests (when available)
pytest tests/

# Check code style
black *.py
flake8 *.py
```

### 📄 License & Legal

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Third-Party Services:**
- Visual Crossing Weather API - Commercial use allowed
- ISRIC SoilGrids - Open data, attribution required
- Google Earth Engine - Subject to Google's terms
- Google Gemini API - Subject to Google's terms

### 👨‍💻 Authors & Acknowledgments  

**Core Development Team:**
- **Agricultural AI Team** - *Architecture and implementation*
- **Data Science Contributors** - *Algorithm development*

**Data Sources & Standards:**
- **NABARD** - Agricultural zone and variety classification standards
- **Google Earth Engine Team** - Satellite data platform and processing
- **ISRIC World Soil Information** - Global soil property database
- **Visual Crossing** - Historical weather data services

**Special Thanks:**
- Indian agricultural research institutions
- Open source Python community
- Earth Engine developer community

### 🙏 Support

If you find this project helpful, please ⭐ **star the repository**!

**Commercial Support:**
For enterprise deployments, custom integrations, or commercial licensing, please contact our team.

---

### 🌟 Project Roadmap

#### **Current Version (v3.0)**
- ✅ Multi-source data integration
- ✅ NABARD-compliant recommendations  
- ✅ AI-powered reporting
- ✅ Local processing pipeline

#### **Upcoming Features (v3.1)**
- 🔄 Database integration (PostgreSQL)
- 🔄 Web dashboard interface
- 🔄 Batch processing optimization
- 🔄 Mobile app compatibility

#### **Future Vision (v4.0)**
- 🚀 Real-time monitoring integration
- 🚀 Machine learning model training
- 🚀 Multi-language support
- 🚀 IoT sensor data integration

---

**🌾 Happy Farming! 🚜**

*Building the future of agriculture, one farm at a time.*

**Last Updated**: September 4, 2025 | **Version**: 3.0 | **Status**: Active Development

---

## 🚧 **Project Status: Active Development**
> **⚠️ Important Notice**: This project is currently in **active development**. All data, files, and documentation are subject to change. Features may be incomplete, experimental, or unstable. Do **not** rely on the current version for production use without thorough testing.

---
