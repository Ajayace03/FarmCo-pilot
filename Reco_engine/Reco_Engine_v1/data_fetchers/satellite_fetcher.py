#!/usr/bin/env python3
"""
Satellite Data Fetcher for Agricultural Pipeline v2.0
===================================================

Enhanced satellite data collection using Google Earth Engine
with local CSV export and comprehensive error handling.

Author: Agricultural AI Team
Version: 2.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import time
import warnings

warnings.filterwarnings('ignore')

# Try to import Earth Engine
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    ee = None
    EE_AVAILABLE = False
    print("⚠️  Google Earth Engine not available. Mock data will be used.")

class SatelliteDataFetcher:
    """
    Enhanced satellite data fetcher with Earth Engine integration
    and local CSV export functionality.
    """

    def __init__(self, ee_project: str = "ceres-470308"):
        """Initialize the satellite data fetcher"""
        self.ee_project = ee_project
        self.ee_available = False
        self.buffer_size = 1000  # meters
        self.start_date = "2024-01-01"
        self.end_date = "2025-08-30"

        print("🛰️  Satellite Data Fetcher v2.0 initialized")

        # Initialize Earth Engine if available
        if EE_AVAILABLE and ee is not None:
            try:
                ee.Initialize(project=self.ee_project)
                self.ee_available = True
                print(f"   ✅ Earth Engine initialized with project: {self.ee_project}")
            except Exception as e:
                self.ee_available = False
                print(f"   ⚠️  Earth Engine initialization failed: {e}")
                print("   📝 Mock data will be used instead")
        else:
            self.ee_available = False
            print("   ⚠️  Earth Engine not available - using mock data")

    def _process_s2_image(self, image):
        """Process Sentinel-2 image to calculate vegetation indices"""
        if not self.ee_available:
            return None

        try:
            # Scale the image
            scaled = image.divide(10000)

            # Calculate NDVI
            ndvi = scaled.normalizedDifference(["B8", "B4"]).rename("NDVI")

            # Calculate EVI
            evi = scaled.expression(
                "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
                {
                    "NIR": scaled.select("B8"),
                    "RED": scaled.select("B4"), 
                    "BLUE": scaled.select("B2")
                }
            ).rename("EVI")

            # Calculate SAVI
            savi = scaled.expression(
                "((NIR - RED) / (NIR + RED + 0.5)) * 1.5",
                {
                    "NIR": scaled.select("B8"),
                    "RED": scaled.select("B4")
                }
            ).rename("SAVI")

            # Calculate LAI (approximation)
            lai = ndvi.multiply(3).clamp(0, 8).rename("LAI")

            return image.addBands([ndvi, evi, savi, lai])

        except Exception as e:
            print(f"   ⚠️  Error processing Sentinel-2: {e}")
            return None

    def _process_modis_image(self, image):
        """Process MODIS image to calculate vegetation indices"""
        if not self.ee_available:
            return None

        try:
            # Scale MODIS data
            ndvi = image.select("NDVI").multiply(0.0001).rename("NDVI")
            evi = image.select("EVI").multiply(0.0001).rename("EVI")

            # Calculate SAVI from NDVI
            savi = ndvi.expression("((NDVI * 1.5) + 0.1)", {"NDVI": ndvi}).rename("SAVI")

            # Calculate LAI approximation
            lai = ndvi.multiply(3).clamp(0, 8).rename("LAI")

            return image.addBands([ndvi, evi, savi, lai])

        except Exception as e:
            print(f"   ⚠️  Error processing MODIS: {e}")
            return None

    def fetch_farm_satellite_data(self, farm_id: str, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Fetch satellite data for a single farm"""

        print(f"🛰️  Fetching satellite data for {farm_id} at ({lat:.6f}, {lon:.6f})")

        # Use mock data if Earth Engine is not available
        if not self.ee_available or ee is None:
            print("   📝 Using mock satellite data")
            return self._generate_mock_satellite_data(farm_id, lat, lon)

        try:
            # Create geometry
            point = ee.Geometry.Point([lon, lat])
            buffer = point.buffer(self.buffer_size)

            # Load datasets
            s2_collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                           .filterDate(self.start_date, self.end_date)
                           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 90))
                           .filterBounds(buffer)
                           .map(self._process_s2_image))

            modis_collection = (ee.ImageCollection("MODIS/061/MOD13Q1")
                              .filterDate(self.start_date, self.end_date) 
                              .filterBounds(buffer)
                              .map(self._process_modis_image))

            s1_collection = (ee.ImageCollection("COPERNICUS/S1_GRD")
                           .filterDate("2024-06-01", "2024-11-30")
                           .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
                           .filter(ee.Filter.eq("instrumentMode", "IW"))
                           .filterBounds(buffer)
                           .select(["VV", "VH"]))

            all_records = []

            # Process monthly data for 2024
            for month in range(1, 13):
                try:
                    start_month = ee.Date.fromYMD(2024, month, 1)
                    end_month = start_month.advance(1, "month")

                    # Filter collections for this month
                    s2_month = s2_collection.filterDate(start_month, end_month)
                    modis_month = modis_collection.filterDate(start_month, end_month)

                    # Count available images
                    s2_count = s2_month.size()
                    modis_count = modis_month.size()

                    # Choose data source (prefer Sentinel-2)
                    composite = ee.Algorithms.If(
                        s2_count.gt(0),
                        s2_month.median(),
                        ee.Algorithms.If(
                            modis_count.gt(0),
                            modis_month.median(),
                            ee.Image.constant([0.45, 0.35, 0.40, 1.5]).rename(["NDVI", "EVI", "SAVI", "LAI"])
                        )
                    )

                    composite = ee.Image(composite)

                    # Extract values at point
                    values = composite.select(["NDVI", "EVI", "SAVI", "LAI"]).reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=point,
                        scale=10,
                        maxPixels=1e9,
                        bestEffort=True
                    )

                    # Get values with error handling
                    try:
                        values_dict = values.getInfo()

                        # Source determination  
                        source = ee.Algorithms.If(
                            s2_count.gt(0), "Sentinel-2",
                            ee.Algorithms.If(modis_count.gt(0), "MODIS", "Default")
                        )
                        source_str = source.getInfo() if hasattr(source, 'getInfo') else "Unknown"
                        s2_count_val = s2_count.getInfo() if hasattr(s2_count, 'getInfo') else 0
                        modis_count_val = modis_count.getInfo() if hasattr(modis_count, 'getInfo') else 0

                    except Exception as e:
                        print(f"   ⚠️  Error getting values for month {month}: {e}")
                        values_dict = {"NDVI": 0.45, "EVI": 0.35, "SAVI": 0.40, "LAI": 1.5}
                        source_str = "Default"
                        s2_count_val = 0
                        modis_count_val = 0

                    # Create vegetation record
                    veg_record = {
                        "farm_id": farm_id,
                        "date": f"2024-{month:02d}-15",  # Mid-month date
                        "month": month,
                        "year": 2024,
                        "data_type": "vegetation",
                        "data_source": source_str,
                        "s2_count": s2_count_val,
                        "modis_count": modis_count_val,
                        "s1_count": 0,
                        "NDVI": values_dict.get("NDVI", 0.45),
                        "EVI": values_dict.get("EVI", 0.35),
                        "SAVI": values_dict.get("SAVI", 0.40), 
                        "LAI": values_dict.get("LAI", 1.5),
                        "VV": None,
                        "VH": None
                    }

                    all_records.append(veg_record)

                    # Add soil moisture data for monsoon months (June-November)
                    if 6 <= month <= 11:
                        try:
                            s1_month = s1_collection.filterDate(start_month, end_month)
                            s1_count = s1_month.size()

                            soil_composite = ee.Algorithms.If(
                                s1_count.gt(0),
                                s1_month.median(),
                                ee.Image.constant([-15, -20]).rename(["VV", "VH"])
                            )

                            soil_composite = ee.Image(soil_composite)

                            soil_values = soil_composite.select(["VV", "VH"]).reduceRegion(
                                reducer=ee.Reducer.mean(),
                                geometry=point,
                                scale=10,
                                maxPixels=1e9,
                                bestEffort=True
                            )

                            try:
                                soil_values_dict = soil_values.getInfo()
                                s1_count_val = s1_count.getInfo()
                            except Exception as e:
                                print(f"   ⚠️  Error getting soil values for month {month}: {e}")
                                soil_values_dict = {"VV": -15, "VH": -20}
                                s1_count_val = 0

                            # Create soil moisture record
                            soil_record = {
                                "farm_id": farm_id,
                                "date": f"2024-{month:02d}-15",
                                "month": month,
                                "year": 2024,
                                "data_type": "soil_moisture",
                                "data_source": "Sentinel-1" if s1_count_val > 0 else "Default",
                                "s2_count": 0,
                                "modis_count": 0,
                                "s1_count": s1_count_val,
                                "NDVI": None,
                                "EVI": None,
                                "SAVI": None,
                                "LAI": None,
                                "VV": soil_values_dict.get("VV", -15),
                                "VH": soil_values_dict.get("VH", -20)
                            }

                            all_records.append(soil_record)

                        except Exception as e:
                            print(f"   ⚠️  Error processing soil moisture for month {month}: {e}")

                    # Add small delay to avoid rate limiting
                    time.sleep(0.1)

                except Exception as e:
                    print(f"   ⚠️  Error processing month {month}: {e}")
                    continue

            print(f"   ✅ Fetched {len(all_records)} satellite records for {farm_id}")
            return all_records

        except Exception as e:
            print(f"   ❌ Error fetching satellite data: {e}")
            print("   📝 Falling back to mock data")
            return self._generate_mock_satellite_data(farm_id, lat, lon)

    def _generate_mock_satellite_data(self, farm_id: str, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Generate realistic mock satellite data when Earth Engine is unavailable"""

        print(f"   📝 Generating mock satellite data for {farm_id}")

        import random
        random.seed(hash(farm_id) % (10**8))  # Consistent random data per farm

        all_records = []

        # Generate vegetation data for all months
        for month in range(1, 13):
            # Seasonal patterns for vegetation indices
            seasonal_factor = 0.8 if month in [6, 7, 8, 9, 10] else 0.5  # Higher in monsoon

            # Generate realistic vegetation data
            base_ndvi = 0.3 + (seasonal_factor * 0.4) + random.uniform(-0.1, 0.1)
            base_ndvi = max(0.1, min(0.9, base_ndvi))  # Clamp between 0.1-0.9

            veg_record = {
                "farm_id": farm_id,
                "date": f"2024-{month:02d}-01",
                "month": month,
                "year": 2024,
                "data_type": "vegetation",
                "data_source": "Mock Data",
                "s2_count": random.randint(0, 5),
                "modis_count": random.randint(1, 8),
                "s1_count": 0,
                "NDVI": round(base_ndvi, 3),
                "EVI": round(base_ndvi * 0.8, 3),
                "SAVI": round(base_ndvi * 0.9, 3),
                "LAI": round(base_ndvi * 4, 2),
                "VV": None,
                "VH": None
            }

            all_records.append(veg_record)

            # Add soil moisture for monsoon months
            if 6 <= month <= 11:
                soil_record = {
                    "farm_id": farm_id,
                    "date": f"2024-{month:02d}-01",
                    "month": month,
                    "year": 2024,
                    "data_type": "soil_moisture",
                    "data_source": "Mock Data",
                    "s2_count": 0,
                    "modis_count": 0,
                    "s1_count": random.randint(1, 6),
                    "NDVI": None,
                    "EVI": None,
                    "SAVI": None,
                    "LAI": None,
                    "VV": round(random.uniform(-18, -12), 2),
                    "VH": round(random.uniform(-22, -16), 2)
                }

                all_records.append(soil_record)

        print(f"   ✅ Generated {len(all_records)} mock satellite records for {farm_id}")
        return all_records

    def fetch_all_farms_satellite(self, farms_file: str, 
                                 output_file: str = "satellite_data_ultimate.csv") -> Optional[str]:
        """
        Fetch satellite data for all farms and save to CSV

        Args:
            farms_file: Path to farms CSV file
            output_file: Path to output CSV file

        Returns:
            Path to output file if successful, None otherwise
        """

        try:
            # Load farms data
            import os
            if not os.path.exists(farms_file):
                print(f"❌ Farms file not found: {farms_file}")
                return None

            farms_df = pd.read_csv(farms_file)
            print(f"📊 Loaded {len(farms_df)} farms from {farms_file}")

            # Validate required columns
            required_cols = ['farm_id', 'lat', 'lon']
            missing_cols = [col for col in required_cols if col not in farms_df.columns]

            if missing_cols:
                print(f"❌ Missing required columns in {farms_file}: {missing_cols}")
                return None

            all_satellite_records = []
            successful_farms = 0

            # Process each farm
            for idx, farm in farms_df.iterrows():
                try:
                    farm_id = farm['farm_id']
                    lat = float(farm['lat'])
                    lon = float(farm['lon'])

                    # Fetch satellite data for this farm
                    satellite_records = self.fetch_farm_satellite_data(farm_id, lat, lon)

                    if satellite_records:
                        all_satellite_records.extend(satellite_records)
                        successful_farms += 1

                    # Add delay between farms to avoid rate limiting
                    if self.ee_available and idx < len(farms_df) - 1:
                        time.sleep(2)

                except Exception as e:
                    print(f"   ❌ Error processing farm {farm.get('farm_id', 'unknown')}: {e}")
                    continue

            if not all_satellite_records:
                print("❌ No satellite data collected")
                return None

            # Convert to DataFrame and save
            satellite_df = pd.DataFrame(all_satellite_records)

            # Ensure proper column order (matching your original format)
            columns_order = [
                "farm_id", "date", "month", "year", "data_type", "data_source",
                "s2_count", "modis_count", "s1_count",
                "NDVI", "EVI", "SAVI", "LAI", "VV", "VH"
            ]

            # Filter to existing columns
            available_columns = [col for col in columns_order if col in satellite_df.columns]
            satellite_df = satellite_df[available_columns]

            # Save to CSV
            satellite_df.to_csv(output_file, index=False)

            print(f"\n✅ Satellite data fetch completed:")
            print(f"   • Successful farms: {successful_farms}/{len(farms_df)}")
            print(f"   • Total satellite records: {len(all_satellite_records)}")
            print(f"   • Vegetation records: {len(satellite_df[satellite_df['data_type'] == 'vegetation'])}")
            print(f"   • Soil moisture records: {len(satellite_df[satellite_df['data_type'] == 'soil_moisture'])}")
            print(f"   • Output file: {output_file}")
            print(f"   • Date range: 2024-01-01 to 2024-12-01")

            # Show data sources breakdown
            if 'data_source' in satellite_df.columns:
                source_breakdown = satellite_df['data_source'].value_counts()
                print(f"   📡 Data sources:")
                for source, count in source_breakdown.items():
                    print(f"      - {source}: {count} records")

            return output_file

        except Exception as e:
            print(f"❌ Error in satellite data fetching: {e}")
            import traceback
            traceback.print_exc()
            return None

    def validate_satellite_data(self, csv_file: str = "satellite_data_ultimate.csv") -> Dict[str, Any]:
        """Validate the collected satellite data"""

        try:
            df = pd.read_csv(csv_file)

            validation_results = {
                "total_records": len(df),
                "farms_processed": df['farm_id'].nunique(),
                "date_range": {
                    "start": df['date'].min(),
                    "end": df['date'].max()
                },
                "data_types": df['data_type'].value_counts().to_dict(),
                "data_sources": df['data_source'].value_counts().to_dict(),
                "quality_checks": {}
            }

            # Quality checks
            vegetation_data = df[df['data_type'] == 'vegetation']

            if len(vegetation_data) > 0:
                validation_results["quality_checks"] = {
                    "ndvi_range": {
                        "min": vegetation_data['NDVI'].min(),
                        "max": vegetation_data['NDVI'].max(),
                        "mean": vegetation_data['NDVI'].mean()
                    },
                    "missing_values": {
                        "ndvi": vegetation_data['NDVI'].isna().sum(),
                        "evi": vegetation_data['EVI'].isna().sum(),
                        "lai": vegetation_data['LAI'].isna().sum()
                    }
                }

            print("✅ Satellite data validation completed")
            return validation_results

        except Exception as e:
            print(f"❌ Error validating satellite data: {e}")
            return {"error": str(e)}

def main():
    """Main function to fetch satellite data for all farms"""
    print("🚀 Starting Satellite Data Collection")
    print("=" * 50)

    # Initialize fetcher
    fetcher = SatelliteDataFetcher()

    # Fetch satellite data for all farms
    result = fetcher.fetch_all_farms_satellite("farms.csv")

    if result:
        print(f"\n🎉 Satellite data collection completed successfully!")
        print(f"✅ Satellite data saved to: {result}")

        # Validate the collected data
        validation_results = fetcher.validate_satellite_data(result)

        print(f"\n📊 Data Summary:")
        print(f"   Total records: {validation_results.get('total_records', 'N/A')}")
        print(f"   Farms processed: {validation_results.get('farms_processed', 'N/A')}")
        print(f"   Date range: {validation_results.get('date_range', {}).get('start', 'N/A')} to {validation_results.get('date_range', {}).get('end', 'N/A')}")

    else:
        print("\n❌ Satellite data collection failed!")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main()
