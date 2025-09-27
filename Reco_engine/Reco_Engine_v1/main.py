#!/usr/bin/env python3
"""
Agricultural Recommendation Engine - Main Controller
==================================================

This is the main orchestrator that controls the entire pipeline:
1. Load farms from CSV
2. Fetch weather, soil, and satellite data
3. Generate crop recommendations
4. Create AI-powered detailed reports

Author: Agricultural AI Team
Version: 3.0
Date: September 2025
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import traceback

class AgriculturalPipelineController:
    """Main controller for the agricultural recommendation pipeline"""

    def __init__(self):
        self.farms_file = "farms.csv"
        self.output_dir = "output"
        self.data_dir = "data"
        self.reports_dir = "reports"

        # Create necessary directories
        for dir_name in [self.output_dir, self.data_dir, self.reports_dir]:
            os.makedirs(dir_name, exist_ok=True)

        print("🚀 Agricultural Pipeline Controller v3.0 Initialized")
        print("=" * 60)

    def load_farms(self) -> pd.DataFrame:
        """Load farms data from CSV"""
        try:
            if not os.path.exists(self.farms_file):
                raise FileNotFoundError(f"Farms file {self.farms_file} not found!")

            farms_df = pd.read_csv(self.farms_file)
            print(f"📊 Loaded {len(farms_df)} farms from {self.farms_file}")

            # Validate required columns
            required_cols = ['farm_id', 'lat', 'lon']
            missing_cols = [col for col in required_cols if col not in farms_df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            return farms_df

        except Exception as e:
            print(f"❌ Error loading farms: {e}")
            raise

    def fetch_weather_data(self) -> bool:
        """Fetch weather data for all farms"""
        print("\n🌤️  STEP 1: Fetching Weather Data")
        print("-" * 40)

        try:
            from data_fetchers.weather_fetcher import WeatherDataFetcher
            fetcher = WeatherDataFetcher()

            weather_file = fetcher.fetch_all_farms_weather(
                self.farms_file, 
                output_file=os.path.join(self.data_dir, "farm_weather_history.csv")
            )

            if weather_file and os.path.exists(weather_file):
                print(f"✅ Weather data saved to: {weather_file}")
                return True
            else:
                print("❌ Weather data fetch failed")
                return False

        except Exception as e:
            print(f"❌ Weather data error: {e}")
            traceback.print_exc()
            return False

    def fetch_soil_data(self) -> bool:
        """Fetch soil data for all farms"""
        print("\n🌱 STEP 2: Fetching Soil Data")
        print("-" * 40)

        try:
            from data_fetchers.soil_fetcher import SoilDataFetcher
            fetcher = SoilDataFetcher()

            soil_file = fetcher.fetch_all_farms_soil(
                self.farms_file,
                output_file=os.path.join(self.data_dir, "soil_test.csv")
            )

            if soil_file and os.path.exists(soil_file):
                print(f"✅ Soil data saved to: {soil_file}")
                return True
            else:
                print("❌ Soil data fetch failed")
                return False

        except Exception as e:
            print(f"❌ Soil data error: {e}")
            traceback.print_exc()
            return False

    def fetch_satellite_data(self) -> bool:
        """Fetch satellite data for all farms"""
        print("\n🛰️  STEP 3: Fetching Satellite Data")
        print("-" * 40)

        try:
            from data_fetchers.satellite_fetcher import SatelliteDataFetcher
            fetcher = SatelliteDataFetcher()

            satellite_file = fetcher.fetch_all_farms_satellite(
                self.farms_file,
                output_file=os.path.join(self.data_dir, "satellite_data_ultimate.csv")
            )

            if satellite_file and os.path.exists(satellite_file):
                print(f"✅ Satellite data saved to: {satellite_file}")
                return True
            else:
                print("❌ Satellite data fetch failed")
                return False

        except Exception as e:
            print(f"❌ Satellite data error: {e}")
            traceback.print_exc()
            return False

    def generate_recommendations(self) -> bool:
        """Generate crop recommendations using the recommendation engine"""
        print("\n🌾 STEP 4: Generating Crop Recommendations")  
        print("-" * 40)

        try:
            # Import the recommendation engine
            from engine.recommendation_engine import PerfectedNABARDRecommendationEngine

            engine = PerfectedNABARDRecommendationEngine()

            # Load the data files
            weather_file = os.path.join(self.data_dir, "farm_weather_history.csv")
            soil_file = os.path.join(self.data_dir, "soil_test.csv")
            satellite_file = os.path.join(self.data_dir, "satellite_data_ultimate.csv")

            # Check if all data files exist
            missing_files = []
            for file_path in [weather_file, soil_file, satellite_file]:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)

            if missing_files:
                print(f"❌ Missing data files: {missing_files}")
                return False

            # Load data
            weather_df = pd.read_csv(weather_file)
            soil_df = pd.read_csv(soil_file)
            satellite_df = pd.read_csv(satellite_file)

            print(f"📊 Loaded weather data: {len(weather_df)} records")
            print(f"📊 Loaded soil data: {len(soil_df)} records")
            print(f"📊 Loaded satellite data: {len(satellite_df)} records")

            # Generate recommendations for all farms
            results = engine.analyze_all_farms(weather_df, satellite_df, soil_df)

            # Move recommendation files to output directory
            for farm_id, result in results.items():
                if 'filename' in result:
                    old_path = result['filename']
                    new_path = os.path.join(self.output_dir, os.path.basename(old_path))
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        result['filename'] = new_path

            print(f"✅ Generated recommendations for {len(results)} farms")
            return True

        except Exception as e:
            print(f"❌ Recommendation generation error: {e}")
            traceback.print_exc()
            return False

    def generate_detailed_reports(self) -> bool:
        """Generate detailed AI reports using Gemini"""
        print("\n📄 STEP 5: Generating Detailed AI Reports")
        print("-" * 40)

        try:
            from report_generator import FixedAgriculturalReportGenerator

            # Check for API key
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                print("⚠️  GOOGLE_API_KEY not found in environment variables")
                print("Report generation skipped. Set the API key to enable this feature.")
                return True  # Not a failure, just skipped

            generator = FixedAgriculturalReportGenerator()

            # Find all recommendation JSON files
            recommendation_files = []
            for file in os.listdir(self.output_dir):
                if file.startswith("perfected_recommendations_") and file.endswith(".json"):
                    recommendation_files.append(os.path.join(self.output_dir, file))

            if not recommendation_files:
                print("❌ No recommendation files found")
                return False

            print(f"📁 Found {len(recommendation_files)} recommendation files")

            # Generate reports
            results = generator.process_multiple_farms(
                recommendation_files, 
                output_dir=self.reports_dir
            )

            successful = sum(1 for success in results.values() if success)
            print(f"✅ Generated {successful}/{len(results)} detailed reports")

            return successful > 0

        except Exception as e:
            print(f"❌ Report generation error: {e}")
            traceback.print_exc()
            return False

    def run_complete_pipeline(self) -> Dict[str, bool]:
        """Run the complete agricultural recommendation pipeline"""
        print("🌾 STARTING COMPLETE AGRICULTURAL PIPELINE")
        print("=" * 60)

        start_time = time.time()
        results = {
            'farms_loaded': False,
            'weather_data': False,
            'soil_data': False,
            'satellite_data': False,
            'recommendations': False,
            'reports': False
        }

        try:
            # Load farms
            farms_df = self.load_farms()
            results['farms_loaded'] = True
            print(f"📍 Farms to process: {list(farms_df['farm_id'])}")

            # Step 1: Fetch weather data
            results['weather_data'] = self.fetch_weather_data()

            # Step 2: Fetch soil data
            results['soil_data'] = self.fetch_soil_data()

            # Step 3: Fetch satellite data
            results['satellite_data'] = self.fetch_satellite_data()

            # Check if we have all required data
            data_steps = ['weather_data', 'soil_data', 'satellite_data']
            if not all(results[step] for step in data_steps):
                print("\n⚠️  Some data fetching steps failed. Attempting to continue with available data...")

            # Step 4: Generate recommendations
            results['recommendations'] = self.generate_recommendations()

            # Step 5: Generate detailed reports (optional)
            results['reports'] = self.generate_detailed_reports()

        except Exception as e:
            print(f"\n❌ Pipeline error: {e}")
            traceback.print_exc()

        # Summary
        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "=" * 60)
        print("🎯 PIPELINE EXECUTION SUMMARY")
        print("=" * 60)

        for step, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{step.replace('_', ' ').title()}: {status}")

        successful_steps = sum(results.values())
        total_steps = len(results)

        print(f"\n📊 Overall Success: {successful_steps}/{total_steps} steps completed")
        print(f"⏱️  Total Duration: {duration:.1f} seconds")

        print(f"\n📁 Output Files:")
        print(f"  • Data files: {self.data_dir}/")
        print(f"  • Recommendations: {self.output_dir}/")
        print(f"  • Reports: {self.reports_dir}/")

        return results

def main():
    """Main execution function"""
    print("🌾 Agricultural Recommendation Engine - Main Controller")
    print("🚀 Starting pipeline execution...")
    print()

    try:
        controller = AgriculturalPipelineController()
        results = controller.run_complete_pipeline()

        # Exit with appropriate code
        if results['recommendations']:
            print("\n🎉 Pipeline completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Pipeline completed with errors.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Pipeline interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()
