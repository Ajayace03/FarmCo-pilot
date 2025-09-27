#!/usr/bin/env python3
"""
Secure Soil Data Fetcher - ENHANCED Version with Full Data Preservation
======================================================================

This version preserves ALL original detailed soil data while adding 
comprehensive security, performance, and reliability improvements.

Features:
- ✅ PRESERVES all ~150 original data columns 
- ✅ Depth-specific analysis (0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm)
- ✅ Statistical measures (median, p05, p95, uncertainty)
- ✅ All soil properties (bdod, cec, clay, sand, silt, phh2o, soc)
- ✅ Enhanced security (SSL verification, input validation)
- ✅ Structured logging and error handling
- ✅ Connection pooling and retry strategies

Author: Agricultural AI Team
Version: 3.1 - Enhanced Security + Full Data Preservation
"""

import os
import logging
import time
import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import validators
import json
from pathlib import Path

# Configure logger for this module
logger = logging.getLogger(__name__)

class SoilFetcherError(Exception):
    """Base exception for soil fetcher errors"""
    pass

class ConfigurationError(SoilFetcherError):
    """Configuration related errors"""
    pass

class ValidationError(SoilFetcherError):
    """Input validation errors"""
    pass

class APIError(SoilFetcherError):
    """SoilGrids API related errors"""
    pass

@dataclass
class SoilConfig:
    """Configuration for soil data fetcher"""
    api_url: str = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    properties: List[str] = None
    depths: List[str] = None
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    timeout: int = 30
    rate_limit_delay: float = 1.0
    max_connections: int = 10
    max_pool_size: int = 20
    cache_dir: str = "raw_soil"
    
    def __post_init__(self):
        """Set defaults and validate configuration"""
        if self.properties is None:
            # All properties from original version
            self.properties = ["phh2o", "clay", "sand", "silt", "soc", "cec", "bdod"]
        if self.depths is None:
            # All depth layers from original version  
            self.depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]
        
        # Validate configuration
        if not validators.url(self.api_url):
            raise ConfigurationError(f"Invalid API URL: {self.api_url}")
        if self.timeout <= 0:
            raise ConfigurationError("Timeout must be positive")
        if self.max_retries < 0:
            raise ConfigurationError("Max retries cannot be negative")
    
    @classmethod
    def from_env(cls) -> 'SoilConfig':
        """Create configuration from environment variables"""
        return cls(
            api_url=os.getenv('SOILGRIDS_API_URL', cls.__dataclass_fields__['api_url'].default),
            max_retries=int(os.getenv('SOIL_MAX_RETRIES', '3')),
            timeout=int(os.getenv('SOIL_TIMEOUT', '30')),
            rate_limit_delay=float(os.getenv('SOIL_RATE_LIMIT', '1.0')),
            cache_dir=os.getenv('SOIL_CACHE_DIR', 'raw_soil')
        )

class SoilDataFetcher:
    """
    Enhanced secure soil data fetcher that preserves ALL original data
    
    This version maintains the complete soil data structure from the original
    while adding comprehensive security and performance improvements.
    """
    
    def __init__(self, config: Optional[SoilConfig] = None):
        """
        Initialize soil fetcher with configuration
        
        Args:
            config: SoilConfig instance. If None, loads from environment
        """
        self.config = config or SoilConfig.from_env()
        self._session: Optional[requests.Session] = None
        self._last_request_time = 0.0
        
        # Create cache directory
        os.makedirs(self.config.cache_dir, exist_ok=True)
        
        logger.info(
            "Enhanced soil data fetcher initialized",
            extra={
                'api_url': self.config.api_url,
                'properties': len(self.config.properties),
                'depths': len(self.config.depths),
                'timeout': self.config.timeout,
                'cache_dir': self.config.cache_dir
            }
        )
    
    @property
    def session(self) -> requests.Session:
        """Lazy-initialized requests session with security enhancements"""
        if self._session is None:
            self._session = self._create_session()
        return self._session
    
    def _create_session(self) -> requests.Session:
        """Create properly configured requests session with security"""
        session = requests.Session()
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True,
            raise_on_status=False
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.config.max_connections,
            pool_maxsize=self.config.max_pool_size
        )
        
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        
        # Set security headers
        session.headers.update({
            'User-Agent': 'Agricultural-Pipeline-SoilFetcher/3.1-Enhanced',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        # CRITICAL: Enforce SSL verification (was missing in original)
        session.verify = True
        
        logger.info("Secure HTTP session created with SSL verification and connection pooling")
        return session
    
    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """Validate GPS coordinates with enhanced checks"""
        if not isinstance(lat, (int, float)):
            raise ValidationError(f"Latitude must be numeric, got {type(lat)}")
        if not isinstance(lon, (int, float)):
            raise ValidationError(f"Longitude must be numeric, got {type(lon)}")
        
        if not -90 <= lat <= 90:
            raise ValidationError(f"Latitude {lat} must be between -90 and 90")
        if not -180 <= lon <= 180:
            raise ValidationError(f"Longitude {lon} must be between -180 and 180")
    
    def _validate_farm_id(self, farm_id: str) -> str:
        """Validate and sanitize farm ID"""
        if not isinstance(farm_id, str):
            raise ValidationError(f"Farm ID must be string, got {type(farm_id)}")
        
        farm_id = farm_id.strip()
        if not farm_id:
            raise ValidationError("Farm ID cannot be empty")
        
        # Sanitize farm ID (security enhancement)
        sanitized = ''.join(c for c in farm_id if c.isalnum() or c in '-_')
        if sanitized != farm_id:
            logger.warning(f"Farm ID sanitized for security: '{farm_id}' -> '{sanitized}'")
        
        return sanitized[:50]
    
    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between API requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def fetch_farm_soil(self, farm_id: str, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch comprehensive soil data for a single farm
        
        This method preserves the COMPLETE original data structure while
        adding security and reliability enhancements.
        
        Returns: Dictionary with ALL original soil data columns
        """
        # Enhanced input validation
        farm_id = self._validate_farm_id(farm_id)
        self._validate_coordinates(lat, lon)
        
        logger.info(
            "Starting comprehensive soil data fetch",
            extra={
                'farm_id': farm_id,
                'lat': lat,
                'lon': lon
            }
        )
        
        try:
            # Enforce rate limiting
            self._enforce_rate_limit()
            
            # Prepare API request parameters
            params = {
                'lat': lat,
                'lon': lon,
                'property': self.config.properties,
                'depth': self.config.depths
            }
            
            logger.debug(
                "Making soil API request",
                extra={
                    'url': self.config.api_url,
                    'params_count': len(params),
                    'timeout': self.config.timeout
                }
            )
            
            # Make secure API request
            response = self.session.get(
                self.config.api_url,
                params=params,
                timeout=self.config.timeout,
                stream=False
            )
            
            logger.debug(
                "Soil API response received",
                extra={
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'content_length': len(response.content) if response.content else 0
                }
            )
            
            if response.status_code == 200:
                try:
                    raw_data = response.json()
                    
                    # Cache the response for efficiency
                    cache_file = Path(self.config.cache_dir) / f"{farm_id}.json"
                    try:
                        cache_file.write_text(json.dumps(raw_data, indent=2))
                        logger.debug(f"Cached soil data for {farm_id}")
                    except Exception as e:
                        logger.warning(f"Cache write failed for {farm_id}: {e}")
                    
                    # Process the comprehensive soil data (PRESERVES ALL ORIGINAL COLUMNS)
                    processed_soil_data = self._process_comprehensive_soil_data(farm_id, lat, lon, raw_data)
                    
                    logger.info(
                        "Comprehensive soil data fetch completed successfully",
                        extra={
                            'farm_id': farm_id,
                            'data_columns': len(processed_soil_data),
                            'texture': processed_soil_data.get('texture', 'Unknown'),
                            'soil_ph': processed_soil_data.get('soil_ph_avg', 0)
                        }
                    )
                    
                    return processed_soil_data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON response for {farm_id}: {e}")
                    raise APIError(f"Invalid JSON response: {e}")
                    
            elif response.status_code == 429:
                error_msg = "API rate limit exceeded"
                logger.error(error_msg, extra={'farm_id': farm_id})
                raise APIError(error_msg)
                
            elif response.status_code == 400:
                error_msg = f"Bad request: {response.text[:200]}"
                logger.error(error_msg, extra={'farm_id': farm_id})
                raise APIError(error_msg)
                
            else:
                error_msg = f"API error {response.status_code}: {response.text[:200]}"
                logger.error(error_msg, extra={'farm_id': farm_id})
                raise APIError(error_msg)
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL verification failed for {farm_id}: {e}")
            raise APIError(f"SSL verification failed: {e}")
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout for {farm_id} after {self.config.timeout}s")
            raise APIError(f"API request timeout: {e}")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {farm_id}: {e}")
            raise APIError(f"Connection failed: {e}")
        
        except (APIError, ValidationError):
            # Re-raise specific errors
            raise
            
        except Exception as e:
            logger.error(
                "Unexpected error during soil fetch",
                extra={
                    'farm_id': farm_id,
                    'error_type': type(e).__name__,
                    'error': str(e)
                }
            )
            raise APIError(f"Unexpected error: {e}")
    
    def _process_comprehensive_soil_data(self, farm_id: str, lat: float, lon: float, raw_data: Dict) -> Dict:
        """
        Process soil data to match the COMPLETE original format
        
        This preserves ALL ~150 columns from the original version:
        - Depth-specific data for all 6 layers
        - Statistical measures (median, p05, p95, unc) 
        - All soil properties (bdod, cec, clay, sand, silt, phh2o, soc)
        - Calculated averages and classifications
        """
        try:
            # Initialize comprehensive soil data structure
            processed = {
                "farm_id": farm_id,
                "lat": lat,
                "lon": lon,
                "test_date": datetime.datetime.now(datetime.UTC).isoformat() + "Z"
            }
            
            layers = raw_data.get("properties", {}).get("layers", [])
            if not layers:
                logger.warning(f"No soil layers found in response for {farm_id}")
                return None
            
            # Process each soil property layer (PRESERVES ALL DETAIL)
            for layer in layers:
                property_name = layer["name"]
                
                if property_name not in self.config.properties:
                    continue
                
                # Process each depth for this property
                for depth_info in layer["depths"]:
                    depth_label = depth_info["label"]  # e.g., "0-5cm"
                    depth_tag = depth_label.replace("cm", "").replace("-", "_")  # e.g., "0_5"
                    values = depth_info["values"]
                    
                    # Extract ALL statistical measures (SAME AS ORIGINAL)
                    median = values.get("Q0.5", values.get("mean"))
                    p05 = values.get("Q0.05")
                    p95 = values.get("Q0.95")
                    
                    # Calculate uncertainty (PRESERVES ORIGINAL CALCULATION)
                    uncertainty = None
                    if median and median != 0 and p05 is not None and p95 is not None:
                        uncertainty = (p95 - p05) / median
                    
                    # Store ALL detailed data (COMPLETE PRESERVATION)
                    prefix = f"{property_name}_{depth_tag}"
                    processed[f"{prefix}_median"] = median
                    processed[f"{prefix}_p05"] = p05
                    processed[f"{prefix}_p95"] = p95
                    processed[f"{prefix}_unc"] = uncertainty
            
            # Calculate derived characteristics (SAME AS ORIGINAL LOGIC)
            self._calculate_comprehensive_soil_characteristics(processed)
            
            logger.debug(
                "Comprehensive soil data processing completed",
                extra={
                    'farm_id': farm_id,
                    'processed_columns': len(processed),
                    'has_depth_data': any('_median' in key for key in processed.keys())
                }
            )
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing comprehensive soil data for {farm_id}: {e}")
            raise APIError(f"Failed to process soil data: {e}")
    
    def _calculate_comprehensive_soil_characteristics(self, soil_data: Dict) -> None:
        """
        Calculate additional soil characteristics using ORIGINAL logic
        
        This preserves all the calculations from the original version while
        adding better error handling and validation.
        """
        try:
            # Calculate averages across top soil layers (ORIGINAL LOGIC)
            properties_to_average = ["phh2o", "clay", "sand", "silt", "soc", "cec", "bdod"]
            
            for prop in properties_to_average:
                medians = []
                
                # Focus on top layers for averages (SAME AS ORIGINAL)
                for depth in ["0_5", "5_15"]:
                    key = f"{prop}_{depth}_median"
                    if key in soil_data and soil_data[key] is not None:
                        medians.append(float(soil_data[key]))
                
                if medians:
                    soil_data[f"{prop}_avg"] = sum(medians) / len(medians)
                else:
                    # Fallback values (enhanced error handling)
                    defaults = {
                        "phh2o": 70, "clay": 300, "sand": 400, "silt": 300,
                        "soc": 15, "cec": 150, "bdod": 1400
                    }
                    soil_data[f"{prop}_avg"] = defaults.get(prop, 0)
                    logger.warning(f"Using default value for {prop}_avg")
            
            # Process clay, sand, silt percentages (ORIGINAL LOGIC PRESERVED)
            clay_avg = soil_data.get("clay_avg", 300)
            sand_avg = soil_data.get("sand_avg", 400)  
            silt_avg = soil_data.get("silt_avg", 300)
            
            # Convert from g/kg to percentage (SAME AS ORIGINAL)
            if clay_avg > 100:  # SoilGrids uses g/kg
                clay_avg = clay_avg / 10
                sand_avg = sand_avg / 10
                silt_avg = silt_avg / 10
            
            soil_data["clay_pct_avg"] = clay_avg
            soil_data["sand_pct_avg"] = sand_avg
            soil_data["silt_pct_avg"] = silt_avg
            
            # Soil texture classification (ENHANCED VERSION OF ORIGINAL)
            soil_data["texture"] = self._classify_soil_texture(clay_avg, sand_avg, silt_avg)
            
            # Process pH (ORIGINAL LOGIC + PROPER UNIT CONVERSION)
            ph_avg = soil_data.get("phh2o_avg", 70)
            if ph_avg > 14:  # SoilGrids pH*10 format
                ph_avg = ph_avg / 10
            
            soil_data["soil_ph_avg"] = ph_avg  # PRESERVES ORIGINAL COLUMN NAME
            soil_data["ph_status"] = self._classify_ph_status(ph_avg)
            
            # Process SOC (ORIGINAL LOGIC)
            soc_avg = soil_data.get("soc_avg", 15)
            if soc_avg > 100:  # Convert from dg/kg to %
                soc_avg = soc_avg / 100
            soil_data["soc_avg"] = soc_avg
            
            # Nutrient status classification (ORIGINAL LOGIC)
            cec_avg = soil_data.get("cec_avg", 150)
            soil_data["nutrient_status"] = self._classify_nutrient_status(soc_avg, cec_avg)
            
        except Exception as e:
            logger.warning(f"Could not calculate all soil characteristics: {e}")
            # Set fallback values to prevent crashes
            soil_data.setdefault("texture", "Unknown")
            soil_data.setdefault("soil_ph_avg", 7.0)
            soil_data.setdefault("ph_status", "Neutral")
            soil_data.setdefault("nutrient_status", "Moderate")
    
    def _classify_soil_texture(self, clay: float, sand: float, silt: float) -> str:
        """Classify soil texture using USDA triangle (ENHANCED from original)"""
        try:
            # Normalize percentages
            total = clay + sand + silt
            if total > 0:
                clay = (clay / total) * 100
                sand = (sand / total) * 100  
                silt = (silt / total) * 100
            
            # USDA Soil Texture Classification (SAME LOGIC AS ORIGINAL)
            if sand >= 85:
                return "Sand"
            elif sand >= 70 and clay <= 15:
                return "Loamy Sand"
            elif (sand >= 43 and clay <= 7) or (sand >= 52 and clay <= 20 and clay >= 7):
                return "Sandy Loam"
            elif clay >= 7 and clay <= 27 and silt >= 28 and silt <= 50 and sand <= 52:
                return "Loam"
            elif silt >= 50 and clay >= 12 and clay <= 27:
                return "Silt Loam"
            elif silt >= 80 and clay <= 12:
                return "Silt"
            elif clay >= 20 and clay <= 35 and silt <= 28 and sand >= 45:
                return "Sandy Clay Loam"
            elif clay >= 27 and clay <= 40 and sand >= 20 and sand <= 45:
                return "Clay Loam"
            elif clay >= 27 and clay <= 40 and sand <= 20:
                return "Silty Clay Loam"
            elif clay >= 35 and sand >= 45:
                return "Sandy Clay"
            elif clay >= 40 and silt >= 40:
                return "Silty Clay"
            elif clay >= 40:
                return "Clay"
            else:
                return "Loam"  # Default fallback
        except Exception as e:
            logger.warning(f"Error classifying soil texture: {e}")
            return "Unknown"
    
    def _classify_ph_status(self, ph: float) -> str:
        """Classify pH status (SAME AS ORIGINAL)"""
        try:
            if ph < 5.5:
                return "Very Acidic"
            elif ph < 6.0:
                return "Acidic"
            elif ph < 6.8:
                return "Slightly Acidic"
            elif ph <= 7.2:
                return "Neutral"
            elif ph <= 7.8:
                return "Slightly Alkaline"
            elif ph <= 8.5:
                return "Alkaline"
            else:
                return "Very Alkaline"
        except Exception:
            return "Unknown"
    
    def _classify_nutrient_status(self, soc: float, cec: float) -> str:
        """Classify nutrient status (ENHANCED from original)"""
        try:
            # SOC thresholds (%)
            soc_low = soc < 1.0
            soc_medium = 1.0 <= soc < 3.0
            soc_high = soc >= 3.0
            
            # CEC thresholds (cmol/kg)
            cec_low = cec < 100
            cec_medium = 100 <= cec < 250
            cec_high = cec >= 250
            
            # Classification logic (SAME AS ORIGINAL)
            if soc_high and cec_high:
                return "Excellent"
            elif (soc_high and cec_medium) or (soc_medium and cec_high):
                return "Good"
            elif soc_medium and cec_medium:
                return "Moderate"
            elif soc_low or cec_low:
                return "Poor"
            else:
                return "Variable"
        except Exception:
            return "Moderate"
    
    def fetch_all_farms_soil(
        self, 
        farms_file: str,
        output_file: str = "soil_test.csv"
    ) -> Optional[str]:
        """
        Fetch comprehensive soil data for all farms
        
        Preserves the COMPLETE original data structure with ~150 columns
        """
        logger.info(
            "Starting bulk comprehensive soil data fetch",
            extra={
                'farms_file': farms_file,
                'output_file': output_file
            }
        )
        
        # Validate input file
        if not os.path.exists(farms_file):
            raise ConfigurationError(f"Farms file not found: {farms_file}")
        
        try:
            # Load farms data
            farms_df = pd.read_csv(farms_file)
            logger.info(f"Loaded {len(farms_df)} farms from {farms_file}")
            
            # Validate required columns
            required_cols = ['farm_id', 'lat', 'lon']
            missing_cols = [col for col in required_cols if col not in farms_df.columns]
            if missing_cols:
                raise ValidationError(f"Missing required columns: {missing_cols}")
            
            # Process farms and collect ALL comprehensive data
            all_soil_records = []
            successful_farms = 0
            failed_farms = 0
            
            for idx, farm_row in farms_df.iterrows():
                try:
                    farm_id = str(farm_row['farm_id'])
                    lat = float(farm_row['lat'])
                    lon = float(farm_row['lon'])
                    
                    # Fetch comprehensive soil data for this farm
                    soil_data = self.fetch_farm_soil(farm_id, lat, lon)
                    
                    if soil_data:
                        all_soil_records.append(soil_data)
                        successful_farms += 1
                        logger.debug(f"Successfully processed comprehensive data for farm {farm_id}")
                    else:
                        failed_farms += 1
                        logger.warning(f"No comprehensive soil data obtained for farm {farm_id}")
                
                except Exception as e:
                    failed_farms += 1
                    logger.error(
                        f"Failed to process farm {farm_row.get('farm_id', 'unknown')}",
                        extra={'error': str(e)}
                    )
                    continue
            
            # Save comprehensive results
            if all_soil_records:
                soil_df = pd.DataFrame(all_soil_records)
                
                # Create output directory if needed
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                # Save with ALL original columns preserved
                soil_df.to_csv(output_file, index=False)
                
                logger.info(
                    "Comprehensive soil data fetch completed",
                    extra={
                        'successful_farms': successful_farms,
                        'failed_farms': failed_farms,
                        'total_farms': len(farms_df),
                        'total_records': len(all_soil_records),
                        'data_columns': len(soil_df.columns),
                        'output_file': output_file
                    }
                )
                
                # Log sample of preserved data structure
                logger.info(f"✅ PRESERVED {len(soil_df.columns)} columns (vs ~150 original)")
                if len(soil_df.columns) < 100:
                    logger.warning("⚠️  Column count lower than expected - verify data preservation")
                
                return output_file
            else:
                logger.error("No comprehensive soil data was collected successfully")
                return None
                
        except pd.errors.EmptyDataError:
            raise ValidationError(f"Farms file {farms_file} is empty")
        except pd.errors.ParserError as e:
            raise ValidationError(f"Failed to parse farms file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during bulk fetch: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        if self._session:
            self._session.close()
            logger.info("Secure HTTP session closed")

def main():
    """Test the enhanced soil fetcher with full data preservation"""
    import logging
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("Testing enhanced soil fetcher with FULL data preservation")
        
        # Test with real farm coordinates
        with SoilDataFetcher() as fetcher:
            # Test single farm fetch
            test_data = fetcher.fetch_farm_soil("TEST_FARM", 13.030504, 79.686037)
            if test_data:
                logger.info(f"✅ Comprehensive fetch successful: {len(test_data)} data points")
                logger.info(f"Sample data: texture={test_data.get('texture')}, pH={test_data.get('soil_ph_avg'):.1f}")
            
            # Test bulk processing
            if os.path.exists("farms.csv"):
                result = fetcher.fetch_all_farms_soil("farms.csv", "enhanced_soil_test.csv")
                if result:
                    # Verify data preservation
                    df = pd.read_csv(result)
                    logger.info(f"✅ Bulk processing successful: {len(df.columns)} columns preserved")
                    if len(df.columns) >= 100:
                        logger.info("🎉 SUCCESS: Comprehensive soil data preservation achieved!")
                    else:
                        logger.warning("⚠️  Data preservation may be incomplete")
    
    except Exception as e:
        logger.error(f"Enhanced soil fetcher test failed: {e}")
        raise

if __name__ == "__main__":
    main()