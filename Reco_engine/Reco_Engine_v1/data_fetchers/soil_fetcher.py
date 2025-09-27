#!/usr/bin/env python3
"""
Soil Data Fetcher for Agricultural Pipeline
==========================================

Fetches soil properties for farms using SoilGrids API from ISRIC.
Enhanced version with better error handling and data processing.

Author: Agricultural AI Team  
Version: 2.0
"""

import os
import time
import datetime
import json
import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple

class SoilDataFetcher:
    """Enhanced soil data fetcher with comprehensive soil analysis"""

    def __init__(self):
        self.api_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        self.properties = ["phh2o", "clay", "sand", "silt", "soc", "cec", "bdod"]
        self.depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        print("🌱 Soil Data Fetcher v2.0 initialized")
        print(f"   • Properties: {self.properties}")
        print(f"   • Depth layers: {self.depths}")

    def fetch_farm_soil(self, farm_id: str, lat: float, lon: float) -> Optional[Dict]:
        """Fetch soil data for a single farm"""

        # Prepare API parameters
        params = {
            "lat": lat,
            "lon": lon,
            "property": self.properties
        }

        print(f"  🔄 Fetching soil data for {farm_id} ({lat:.4f}, {lon:.4f})")

        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.api_url, params=params, timeout=30)

                if response.status_code == 200:
                    soil_data = response.json()
                    processed_data = self._process_soil_data(farm_id, lat, lon, soil_data)

                    if processed_data:
                        print(f"    ✅ Successfully fetched soil data")
                        return processed_data
                    else:
                        print(f"    ⚠️  No soil data available for this location")
                        return None

                elif response.status_code == 429:  # Rate limit
                    print(f"    ⏳ Rate limit hit, waiting {self.retry_delay * (attempt + 1)} seconds...")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue

                else:
                    print(f"    ⚠️  API error {response.status_code}: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue

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
                print(f"    ❌ Processing error: {e}")
                break

        print(f"    ❌ Failed to fetch soil data for {farm_id} after {self.max_retries} attempts")
        return None

    def _process_soil_data(self, farm_id: str, lat: float, lon: float, 
                          raw_data: Dict) -> Optional[Dict]:
        """Process raw SoilGrids data into structured format"""

        try:
            processed = {
                "farm_id": farm_id,
                "lat": lat,
                "lon": lon,
                "test_date": datetime.datetime.utcnow().isoformat() + "Z"
            }

            layers = raw_data.get("properties", {}).get("layers", [])

            for layer in layers:
                property_name = layer["name"]
                if property_name not in self.properties:
                    continue

                for depth_info in layer["depths"]:
                    depth_label = depth_info["label"]  # e.g., "0-5cm"

                    # Convert depth label to standardized format
                    depth_tag = depth_label.replace("cm", "").replace("-", "_")

                    values = depth_info["values"]

                    # Extract key statistics
                    median = values.get("Q0.5", values.get("mean", values.get("value")))
                    p05 = values.get("Q0.05")
                    p95 = values.get("Q0.95")

                    # Calculate uncertainty if possible
                    uncertainty = None
                    if median and median != 0 and p05 is not None and p95 is not None:
                        uncertainty = (p95 - p05) / median

                    # Store the processed values
                    prefix = f"{property_name}_{depth_tag}"
                    processed[f"{prefix}_median"] = median
                    processed[f"{prefix}_p05"] = p05
                    processed[f"{prefix}_p95"] = p95
                    processed[f"{prefix}_unc"] = uncertainty

            # Calculate derived soil characteristics
            self._calculate_soil_characteristics(processed)

            return processed

        except Exception as e:
            print(f"    ❌ Error processing soil data: {e}")
            return None

    def _calculate_soil_characteristics(self, soil_data: Dict) -> None:
        """Calculate additional soil characteristics from raw data"""

        try:
            # Calculate average values across depth layers
            for prop in ["phh2o", "clay", "sand", "silt", "soc", "cec"]:
                medians = []
                for depth in ["0_5", "5_15"]:  # Focus on top layers
                    key = f"{prop}_{depth}_median"
                    if key in soil_data and soil_data[key] is not None:
                        medians.append(soil_data[key])

                if medians:
                    soil_data[f"{prop}_avg"] = sum(medians) / len(medians)

            # Determine soil texture based on clay, sand, silt percentages
            clay_avg = soil_data.get("clay_avg", 0)
            sand_avg = soil_data.get("sand_avg", 0) 
            silt_avg = soil_data.get("silt_avg", 0)

            # Convert from g/kg to percentage if needed (SoilGrids uses g/kg)
            if clay_avg > 100:  # Likely in g/kg
                clay_avg = clay_avg / 10
                sand_avg = sand_avg / 10
                silt_avg = silt_avg / 10

                # Update the averages
                soil_data["clay_pct_avg"] = clay_avg
                soil_data["sand_pct_avg"] = sand_avg
                soil_data["silt_pct_avg"] = silt_avg
            else:
                soil_data["clay_pct_avg"] = clay_avg
                soil_data["sand_pct_avg"] = sand_avg
                soil_data["silt_pct_avg"] = silt_avg

            # Determine soil texture class
            soil_data["texture"] = self._get_soil_texture(clay_avg, sand_avg, silt_avg)

            # Classify pH status
            ph_avg = soil_data.get("phh2o_avg", 7.0)
            if ph_avg is not None:
                ph_avg = ph_avg / 10 if ph_avg > 14 else ph_avg  # Convert from pH*10 if needed
                soil_data["soil_ph_avg"] = ph_avg
                soil_data["ph_status"] = self._get_ph_status(ph_avg)

            # Classify nutrient status based on SOC and CEC
            soc_avg = soil_data.get("soc_avg", 0)
            cec_avg = soil_data.get("cec_avg", 0)

            # Convert SOC from dg/kg to percentage if needed
            if soc_avg > 100:
                soc_avg = soc_avg / 100
                soil_data["soc_avg"] = soc_avg

            soil_data["nutrient_status"] = self._get_nutrient_status(soc_avg, cec_avg)

        except Exception as e:
            print(f"    ⚠️  Warning: Could not calculate soil characteristics: {e}")

    def _get_soil_texture(self, clay: float, sand: float, silt: float) -> str:
        """Determine soil texture class using USDA soil triangle"""

        # Normalize to ensure they sum to 100%
        total = clay + sand + silt
        if total > 0:
            clay = (clay / total) * 100
            sand = (sand / total) * 100
            silt = (silt / total) * 100

        # USDA Soil Texture Classification
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
            return "Unknown"

    def _get_ph_status(self, ph: float) -> str:
        """Classify soil pH status"""
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

    def _get_nutrient_status(self, soc: float, cec: float) -> str:
        """Classify soil nutrient status based on SOC and CEC"""

        # SOC thresholds (%)
        soc_low = soc < 1.0
        soc_medium = 1.0 <= soc < 3.0
        soc_high = soc >= 3.0

        # CEC thresholds (cmol/kg)
        cec_low = cec < 10
        cec_medium = 10 <= cec < 25
        cec_high = cec >= 25

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

    def fetch_all_farms_soil(self, farms_file: str, 
                           output_file: str = "soil_test.csv") -> Optional[str]:
        """Fetch soil data for all farms and save to CSV"""

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

            # Create raw data directory for caching
            os.makedirs("raw_soil", exist_ok=True)

            all_soil_records = []
            successful_farms = 0

            for idx, farm in farms_df.iterrows():
                farm_id = farm['farm_id']
                lat = farm['lat']
                lon = farm['lon']

                # Check if cached data exists
                cache_file = f"raw_soil/{farm_id}.json"

                # Fetch soil data for this farm
                soil_data = self.fetch_farm_soil(farm_id, lat, lon)

                if soil_data:
                    # Cache the data
                    with open(cache_file, 'w') as f:
                        json.dump(soil_data, f, indent=2, default=str)

                    all_soil_records.append(soil_data)
                    successful_farms += 1

                # Add delay between requests
                if idx < len(farms_df) - 1:
                    time.sleep(1)

            if all_soil_records:
                # Save to CSV
                soil_df = pd.DataFrame(all_soil_records)
                soil_df.to_csv(output_file, index=False)

                print(f"\n✅ Soil data fetch completed:")
                print(f"   • Successful farms: {successful_farms}/{len(farms_df)}")
                print(f"   • Total soil records: {len(all_soil_records)}")
                print(f"   • Output file: {output_file}")
                print(f"   • Cached data: raw_soil/ directory")

                return output_file
            else:
                print("❌ No soil data was fetched successfully")
                return None

        except Exception as e:
            print(f"❌ Error in soil data fetching: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Test function"""
    fetcher = SoilDataFetcher()
    result = fetcher.fetch_all_farms_soil("farms.csv")

    if result:
        print(f"✅ Soil data saved to: {result}")
    else:
        print("❌ Soil data fetch failed")

if __name__ == "__main__":
    main()
