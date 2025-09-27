#!/usr/bin/env python3
"""
Weather Data Fetcher for Agricultural Pipeline
============================================

Fetches historical weather data for farms using Visual Crossing Weather API.
Improved version with better error handling and retry logic.

Author: Agricultural AI Team
Version: 2.0
"""

import requests
import pandas as pd
import datetime
import time
import os
from typing import Optional, Dict, List

class WeatherDataFetcher:
    """Enhanced weather data fetcher with retry logic and better error handling"""

    def __init__(self, api_key: str = "NA4GPJH9SVCN5Z4FTMKQFXZ4D"):
        self.api_key = api_keys
        self.base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self.max_retries = 3
        self.retry_delay = 5  # seconds

        print("🌤️  Weather Data Fetcher v2.0 initialized")

    def fetch_farm_weather(self, farm_id: str, lat: float, lon: float, 
                          days_back: int = 365) -> List[Dict]:
        """Fetch weather data for a single farm"""

        # Calculate date range
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days_back)

        url = (
            f"{self.base_url}/{lat},{lon}/{start_date}/{end_date}"
            f"?unitGroup=metric&include=days&key={self.api_key}&contentType=json"
        )

        print(f"  🔄 Fetching weather for {farm_id} ({lat:.4f}, {lon:.4f})")

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    days = data.get("days", [])

                    weather_records = []
                    for day in days:
                        record = {
                            "farm_id": farm_id,
                            "lat": lat,
                            "lon": lon,
                            "date": day.get("datetime"),
                            "temp_max": day.get("tempmax", 0),
                            "temp_min": day.get("tempmin", 0),
                            "temp": day.get("temp", 0),
                            "humidity": day.get("humidity", 0),
                            "precip": day.get("precip", 0),
                            "windspeed": day.get("windspeed", 0),
                            "pressure": day.get("pressure", 1013.25),
                            "visibility": day.get("visibility", 10),
                            "cloudcover": day.get("cloudcover", 0),
                            "conditions": day.get("conditions", "Unknown"),
                            "description": day.get("description", ""),
                            "uvindex": day.get("uvindex", 0),
                            "sunrise": day.get("sunrise", "06:00:00"),
                            "sunset": day.get("sunset", "18:00:00")
                        }
                        weather_records.append(record)

                    print(f"    ✅ Successfully fetched {len(weather_records)} weather records")
                    return weather_records

                elif response.status_code == 429:  # Rate limit
                    print(f"    ⏳ Rate limit hit, waiting {self.retry_delay * (attempt + 1)} seconds...")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue

                else:
                    print(f"    ⚠️  API error {response.status_code}: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        break

            except requests.exceptions.Timeout:
                print(f"    ⏳ Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

            except requests.exceptions.RequestException as e:
                print(f"    ❌ Request error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

            except Exception as e:
                print(f"    ❌ Unexpected error: {e}")
                break

        print(f"    ❌ Failed to fetch weather data for {farm_id} after {self.max_retries} attempts")
        return []

    def fetch_all_farms_weather(self, farms_file: str, 
                              output_file: str = "farm_weather_history.csv") -> Optional[str]:
        """Fetch weather data for all farms and save to CSV"""

        try:
            # Load farms
            if not os.path.exists(farms_file):
                print(f"❌ Farms file not found: {farms_file}")
                return None

            farms_df = pd.read_csv(farms_file)
            print(f"📊 Loaded {len(farms_df)} farms from {farms_file}")

            # Validate required columns
            required_cols = ['farm_id', 'lat', 'lon']
            missing_cols = [col for col in required_cols if col not in farms_df.columns]
            if missing_cols:
                print(f"❌ Missing required columns: {missing_cols}")
                return None

            all_weather_records = []
            successful_farms = 0

            for idx, farm in farms_df.iterrows():
                farm_id = farm['farm_id']
                lat = farm['lat']
                lon = farm['lon']

                # Fetch weather data for this farm
                weather_records = self.fetch_farm_weather(farm_id, lat, lon)

                if weather_records:
                    all_weather_records.extend(weather_records)
                    successful_farms += 1

                # Add delay between requests to be respectful to the API
                if idx < len(farms_df) - 1:  # Don't delay after last farm
                    time.sleep(2)

            if all_weather_records:
                # Save to CSV
                weather_df = pd.DataFrame(all_weather_records)
                weather_df.to_csv(output_file, index=False)

                print(f"\n✅ Weather data fetch completed:")
                print(f"   • Successful farms: {successful_farms}/{len(farms_df)}")
                print(f"   • Total weather records: {len(all_weather_records)}")
                print(f"   • Output file: {output_file}")
                print(f"   • Date range: {weather_df['date'].min()} to {weather_df['date'].max()}")

                return output_file
            else:
                print("❌ No weather data was fetched successfully")
                return None

        except Exception as e:
            print(f"❌ Error in weather data fetching: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Test function"""
    fetcher = WeatherDataFetcher()
    result = fetcher.fetch_all_farms_weather("farms.csv")

    if result:
        print(f"✅ Weather data saved to: {result}")
    else:
        print("❌ Weather data fetch failed")

if __name__ == "__main__":
    main()
