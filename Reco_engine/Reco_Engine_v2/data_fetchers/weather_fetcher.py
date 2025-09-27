#!/usr/bin/env python3
"""
Secure Weather Data Fetcher for Agricultural Pipeline
===================================================

Production-ready weather data fetcher with comprehensive security,
error handling, logging, and performance optimizations.

Features:
- Secure API key management via environment variables
- Input validation and sanitization
- Structured logging with context
- Connection pooling and retry strategies
- Proper SSL verification
- Memory-efficient data processing
- Comprehensive error handling

Author: Agricultural AI Team
Version: 3.0 - Secure & Efficient
"""

import os
import logging
import time
import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import validators
from contextlib import contextmanager

# Configure logger for this module
logger = logging.getLogger(__name__)

class WeatherFetcherError(Exception):
    """Base exception for weather fetcher errors"""
    pass

class ConfigurationError(WeatherFetcherError):
    """Configuration related errors"""
    pass

class ValidationError(WeatherFetcherError):
    """Input validation errors"""
    pass

class APIError(WeatherFetcherError):
    """Weather API related errors"""
    pass

@dataclass
class WeatherConfig:
    """Configuration for weather data fetcher"""
    api_key: str
    base_url: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    max_retries: int = 3
    retry_backoff_factor: float = 1.0
    timeout: int = 30
    max_connections: int = 10
    max_pool_size: int = 20
    rate_limit_delay: float = 1.0
    max_days_back: int = 365
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key:
            raise ConfigurationError("API key cannot be empty")
        if not validators.url(self.base_url):
            raise ConfigurationError(f"Invalid base URL: {self.base_url}")
        if self.timeout <= 0:
            raise ConfigurationError("Timeout must be positive")
        if self.max_retries < 0:
            raise ConfigurationError("Max retries cannot be negative")
    
    @classmethod
    def from_env(cls) -> 'WeatherConfig':
        """Create configuration from environment variables"""
        api_key = os.getenv('VISUAL_CROSSING_API_KEY')
        if not api_key:
            raise ConfigurationError(
                "VISUAL_CROSSING_API_KEY environment variable not set. "
                "Please set your Visual Crossing API key in the environment."
            )
        
        return cls(
            api_key=api_key,
            base_url=os.getenv(
                'VISUAL_CROSSING_BASE_URL', 
                cls.__dataclass_fields__['base_url'].default
            ),
            max_retries=int(os.getenv('WEATHER_MAX_RETRIES', '3')),
            timeout=int(os.getenv('WEATHER_TIMEOUT', '30')),
            rate_limit_delay=float(os.getenv('WEATHER_RATE_LIMIT', '1.0'))
        )

@dataclass
class WeatherRecord:
    """Individual weather record with validation"""
    farm_id: str
    lat: float
    lon: float
    date: str
    temp_max: float
    temp_min: float
    temp: float
    humidity: float
    precip: float
    windspeed: float
    pressure: float = 1013.25
    visibility: float = 10.0
    cloudcover: float = 0.0
    conditions: str = "Unknown"
    description: str = ""
    uvindex: float = 0.0
    sunrise: str = "06:00:00"
    sunset: str = "18:00:00"
    
    def __post_init__(self):
        """Validate weather record data"""
        if not self.farm_id.strip():
            raise ValidationError("Farm ID cannot be empty")
        
        # Validate temperature ranges (reasonable values for Earth)
        if not -100 <= self.temp <= 70:
            logger.warning(f"Temperature {self.temp}°C seems unusual for {self.farm_id}")
        
        # Validate humidity percentage
        if not 0 <= self.humidity <= 100:
            logger.warning(f"Humidity {self.humidity}% out of range for {self.farm_id}")
        
        # Sanitize string fields
        self.conditions = str(self.conditions)[:50]
        self.description = str(self.description)[:200]
        self.sunrise = str(self.sunrise)[:8]
        self.sunset = str(self.sunset)[:8]

class WeatherDataFetcher:
    """
    Secure and efficient weather data fetcher
    
    Features:
    - Secure API key management
    - Input validation and sanitization  
    - Comprehensive error handling and logging
    - Connection pooling and retry strategies
    - Rate limiting and quota management
    - Memory-efficient data processing
    """
    
    def __init__(self, config: Optional[WeatherConfig] = None):
        """
        Initialize weather fetcher with configuration
        
        Args:
            config: WeatherConfig instance. If None, loads from environment
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config or WeatherConfig.from_env()
        self._session: Optional[requests.Session] = None
        self._last_request_time = 0.0
        
        logger.info(
            "Weather data fetcher initialized",
            extra={
                'base_url': self.config.base_url,
                'timeout': self.config.timeout,
                'max_retries': self.config.max_retries,
                'rate_limit_delay': self.config.rate_limit_delay
            }
        )
    
    @property
    def session(self) -> requests.Session:
        """Lazy-initialized requests session with proper configuration"""
        if self._session is None:
            self._session = self._create_session()
        return self._session
    
    def _create_session(self) -> requests.Session:
        """Create properly configured requests session"""
        session = requests.Session()
        
        # Configure retry strategy
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
            'User-Agent': 'Agricultural-Pipeline-WeatherFetcher/3.0',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        # Verify SSL certificates
        session.verify = True
        
        logger.debug("HTTP session created with connection pooling")
        return session
    
    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """
        Validate GPS coordinates
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Raises:
            ValidationError: If coordinates are invalid
        """
        if not isinstance(lat, (int, float)):
            raise ValidationError(f"Latitude must be numeric, got {type(lat)}")
        if not isinstance(lon, (int, float)):
            raise ValidationError(f"Longitude must be numeric, got {type(lon)}")
        
        if not -90 <= lat <= 90:
            raise ValidationError(f"Latitude {lat} must be between -90 and 90")
        if not -180 <= lon <= 180:
            raise ValidationError(f"Longitude {lon} must be between -180 and 180")
    
    def _validate_farm_id(self, farm_id: str) -> str:
        """
        Validate and sanitize farm ID
        
        Args:
            farm_id: Farm identifier
            
        Returns:
            Sanitized farm ID
            
        Raises:
            ValidationError: If farm ID is invalid
        """
        if not isinstance(farm_id, str):
            raise ValidationError(f"Farm ID must be string, got {type(farm_id)}")
        
        farm_id = farm_id.strip()
        if not farm_id:
            raise ValidationError("Farm ID cannot be empty")
        
        # Sanitize farm ID (remove potentially dangerous characters)
        sanitized = ''.join(c for c in farm_id if c.isalnum() or c in '-_')
        if sanitized != farm_id:
            logger.warning(f"Farm ID sanitized: '{farm_id}' -> '{sanitized}'")
        
        return sanitized[:50]  # Limit length
    
    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between API requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _make_api_request(self, url: str, params: Dict[str, Any]) -> requests.Response:
        """
        Make secure API request with validation
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            API response
            
        Raises:
            APIError: If API request fails
        """
        # Validate URL
        if not validators.url(url):
            raise APIError(f"Invalid API URL: {url}")
        
        # Create safe params for logging (exclude API key)
        safe_params = {k: v for k, v in params.items() if k != 'key'}
        
        logger.debug(
            "Making weather API request",
            extra={
                'url': url,
                'params': safe_params,
                'timeout': self.config.timeout
            }
        )
        
        try:
            # Enforce rate limiting
            self._enforce_rate_limit()
            
            # Make request
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.timeout,
                stream=False  # Don't stream for small responses
            )
            
            logger.debug(
                "Weather API response received",
                extra={
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'content_length': len(response.content) if response.content else 0
                }
            )
            
            return response
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL verification failed: {e}")
            raise APIError(f"SSL verification failed: {e}")
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {self.config.timeout}s")
            raise APIError(f"API request timeout: {e}")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIError(f"Connection failed: {e}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"API request failed: {e}")
    
    def _process_weather_response(
        self, 
        farm_id: str, 
        lat: float, 
        lon: float, 
        response_data: Dict[str, Any]
    ) -> List[WeatherRecord]:
        """
        Process and validate weather API response
        
        Args:
            farm_id: Farm identifier
            lat: Farm latitude
            lon: Farm longitude
            response_data: Raw API response data
            
        Returns:
            List of validated weather records
        """
        days = response_data.get("days", [])
        if not days:
            logger.warning(f"No weather data in API response for {farm_id}")
            return []
        
        weather_records = []
        processed_count = 0
        error_count = 0
        
        for day_data in days:
            try:
                record = WeatherRecord(
                    farm_id=farm_id,
                    lat=lat,
                    lon=lon,
                    date=str(day_data.get("datetime", "")),
                    temp_max=self._safe_float(day_data.get("tempmax"), 0.0),
                    temp_min=self._safe_float(day_data.get("tempmin"), 0.0),
                    temp=self._safe_float(day_data.get("temp"), 0.0),
                    humidity=self._safe_float(day_data.get("humidity"), 0.0),
                    precip=self._safe_float(day_data.get("precip"), 0.0),
                    windspeed=self._safe_float(day_data.get("windspeed"), 0.0),
                    pressure=self._safe_float(day_data.get("pressure"), 1013.25),
                    visibility=self._safe_float(day_data.get("visibility"), 10.0),
                    cloudcover=self._safe_float(day_data.get("cloudcover"), 0.0),
                    conditions=str(day_data.get("conditions", "Unknown")),
                    description=str(day_data.get("description", "")),
                    uvindex=self._safe_float(day_data.get("uvindex"), 0.0),
                    sunrise=str(day_data.get("sunrise", "06:00:00")),
                    sunset=str(day_data.get("sunset", "18:00:00"))
                )
                weather_records.append(record)
                processed_count += 1
                
            except (ValidationError, ValueError, TypeError) as e:
                error_count += 1
                logger.warning(
                    f"Failed to process weather record for {farm_id}",
                    extra={
                        'date': day_data.get("datetime"),
                        'error': str(e)
                    }
                )
                continue
        
        logger.info(
            "Weather response processing completed",
            extra={
                'farm_id': farm_id,
                'processed_records': processed_count,
                'error_records': error_count,
                'total_records': len(days)
            }
        )
        
        return weather_records
    
    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        """Safely convert value to float with validation"""
        if value is None:
            return default
        
        try:
            result = float(value)
            # Check for reasonable weather values
            if abs(result) > 1e6:  # Prevent extreme values
                logger.warning(f"Extreme weather value {result}, using default {default}")
                return default
            return result
        except (ValueError, TypeError, OverflowError):
            return default
    
    def fetch_farm_weather(
        self, 
        farm_id: str, 
        lat: float, 
        lon: float,
        days_back: int = 35
    ) -> List[WeatherRecord]:
        """
        Fetch weather data for a single farm with comprehensive validation
        
        Args:
            farm_id: Unique farm identifier
            lat: Farm latitude in decimal degrees
            lon: Farm longitude in decimal degrees
            days_back: Number of days of historical data (1-365)
            
        Returns:
            List of weather records
            
        Raises:
            ValidationError: If input parameters are invalid
            APIError: If API request fails
            ConfigurationError: If configuration is invalid
        """
        # Input validation
        farm_id = self._validate_farm_id(farm_id)
        self._validate_coordinates(lat, lon)
        
        if not isinstance(days_back, int) or not 1 <= days_back <= self.config.max_days_back:
            raise ValidationError(
                f"days_back must be integer between 1 and {self.config.max_days_back}"
            )
        
        logger.info(
            "Starting weather data fetch",
            extra={
                'farm_id': farm_id,
                'lat': lat,
                'lon': lon,
                'days_back': days_back
            }
        )
        
        # Calculate date range
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days_back)
        
        # Build API URL and parameters
        url = f"{self.config.base_url}/{lat},{lon}/{start_date}/{end_date}"
        params = {
            'unitGroup': 'metric',
            'include': 'days',
            'key': self.config.api_key,
            'contentType': 'json'
        }
        
        try:
            # Make API request
            response = self._make_api_request(url, params)
            
            # Handle different response codes
            if response.status_code == 200:
                data = response.json()
                weather_records = self._process_weather_response(farm_id, lat, lon, data)
                
                logger.info(
                    "Weather data fetch completed successfully",
                    extra={
                        'farm_id': farm_id,
                        'records_fetched': len(weather_records)
                    }
                )
                
                return weather_records
                
            elif response.status_code == 429:
                error_msg = "API rate limit exceeded"
                logger.error(error_msg, extra={'farm_id': farm_id})
                raise APIError(error_msg)
                
            elif response.status_code == 401:
                error_msg = "Invalid API key"
                logger.error(error_msg)
                raise APIError(error_msg)
                
            elif response.status_code == 400:
                error_msg = f"Bad request: {response.text[:200]}"
                logger.error(error_msg, extra={'farm_id': farm_id})
                raise APIError(error_msg)
                
            else:
                error_msg = f"API error {response.status_code}: {response.text[:200]}"
                logger.error(error_msg, extra={'farm_id': farm_id})
                raise APIError(error_msg)
                
        except APIError:
            # Re-raise API errors as-is
            raise
        except Exception as e:
            logger.error(
                "Unexpected error during weather fetch",
                extra={
                    'farm_id': farm_id,
                    'error_type': type(e).__name__,
                    'error': str(e)
                }
            )
            raise APIError(f"Unexpected error: {e}")
    
    def fetch_all_farms_weather(
        self, 
        farms_file: str,
        output_file: str = "farm_weather_history.csv",
        days_back: int = 35
    ) -> Optional[str]:
        """
        Fetch weather data for all farms and save to CSV
        
        Args:
            farms_file: Path to CSV file containing farm data
            output_file: Path to output CSV file
            days_back: Number of days of historical data
            
        Returns:
            Path to output file if successful, None otherwise
            
        Raises:
            ConfigurationError: If input file is invalid
            ValidationError: If farms data is malformed
        """
        logger.info(
            "Starting bulk weather data fetch",
            extra={
                'farms_file': farms_file,
                'output_file': output_file,
                'days_back': days_back
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
            
            # Process farms
            all_weather_records = []
            successful_farms = 0
            failed_farms = 0
            
            for idx, farm_row in farms_df.iterrows():
                try:
                    farm_id = str(farm_row['farm_id'])
                    lat = float(farm_row['lat'])
                    lon = float(farm_row['lon'])
                    
                    # Fetch weather data for this farm
                    weather_records = self.fetch_farm_weather(farm_id, lat, lon, days_back)
                    
                    if weather_records:
                        # Convert to dictionaries for DataFrame
                        record_dicts = [
                            {
                                'farm_id': record.farm_id,
                                'lat': record.lat,
                                'lon': record.lon,
                                'date': record.date,
                                'temp_max': record.temp_max,
                                'temp_min': record.temp_min,
                                'temp': record.temp,
                                'humidity': record.humidity,
                                'precip': record.precip,
                                'windspeed': record.windspeed,
                                'pressure': record.pressure,
                                'visibility': record.visibility,
                                'cloudcover': record.cloudcover,
                                'conditions': record.conditions,
                                'description': record.description,
                                'uvindex': record.uvindex,
                                'sunrise': record.sunrise,
                                'sunset': record.sunset
                            }
                            for record in weather_records
                        ]
                        all_weather_records.extend(record_dicts)
                        successful_farms += 1
                        
                        logger.debug(
                            f"Successfully processed farm {farm_id}",
                            extra={'records_count': len(weather_records)}
                        )
                    else:
                        failed_farms += 1
                        logger.warning(f"No weather data obtained for farm {farm_id}")
                
                except Exception as e:
                    failed_farms += 1
                    logger.error(
                        f"Failed to process farm {farm_row.get('farm_id', 'unknown')}",
                        extra={'error': str(e)}
                    )
                    continue
            
            # Save results
            if all_weather_records:
                weather_df = pd.DataFrame(all_weather_records)
                
                # Create output directory if needed
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                weather_df.to_csv(output_file, index=False)
                
                logger.info(
                    "Weather data fetch completed",
                    extra={
                        'successful_farms': successful_farms,
                        'failed_farms': failed_farms,
                        'total_farms': len(farms_df),
                        'total_records': len(all_weather_records),
                        'output_file': output_file,
                        'date_range': f"{weather_df['date'].min()} to {weather_df['date'].max()}"
                    }
                )
                
                return output_file
            else:
                logger.error("No weather data was collected successfully")
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
            logger.debug("HTTP session closed")

# Convenience function for quick usage
def create_weather_fetcher() -> WeatherDataFetcher:
    """Create weather fetcher with environment configuration"""
    return WeatherDataFetcher()

def main():
    """Example usage and testing"""
    import logging
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("Testing secure weather fetcher")
        
        # Test with environment configuration
        with create_weather_fetcher() as fetcher:
            # Test single farm fetch
            test_records = fetcher.fetch_farm_weather("TEST_FARM", 13.0305, 79.6860, 7)
            logger.info(f"Fetched {len(test_records)} weather records for test farm")
            
            # Test bulk fetch if farms.csv exists
            if os.path.exists("farms.csv"):
                result = fetcher.fetch_all_farms_weather("farms.csv", "test_weather_output.csv")
                if result:
                    logger.info(f"Bulk weather data saved to {result}")
                else:
                    logger.warning("Bulk fetch failed")
    
    except Exception as e:
        logger.error(f"Weather fetcher test failed: {e}")
        raise

if __name__ == "__main__":
    main()