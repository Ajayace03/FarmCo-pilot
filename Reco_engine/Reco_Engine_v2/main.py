#!/usr/bin/env python3

"""
COMPLETE Main Pipeline - OLD ENGINE + REPORT GENERATION
=======================================================

UPDATED VERSION - Complete pipeline with report generation
- Uses OLD engine with 15 rich recommendations
- Generates government schemes analysis  
- Creates comprehensive reports from the JSON outputs
- Enhanced logging and error handling

Author: Agricultural AI Team
Version: 6.6 - COMPLETE WITH REPORTS
Date: September 2025
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import traceback
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("[INFO] Environment variables loaded successfully")

# Configure Windows-compatible logging (no Unicode)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agricultural_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompletePipelineController:
    """Complete pipeline controller with OLD ENGINE + REPORT GENERATION"""
    
    def __init__(self):
        self.farms_file = "farms.csv"
        self.output_dir = "output"
        self.data_dir = "data"
        self.reports_dir = "modular_reports"
        self.final_reports_dir = "comprehensive_reports"
        
        # Ensure directories exist with proper creation
        self._create_directories()
            
        logger.info("[INIT] Complete Pipeline Controller v6.6 Initialized")
        logger.info("[ENGINE] Using OLD engine with rich recommendations")
        logger.info("[REPORTS] Including comprehensive report generation")
        logger.info("[CONFIG] 15 recommendations + numerical confidence + carbon potential + reports")
        print("=" * 70)
    
    def _create_directories(self):
        """Create necessary directories with proper error handling"""
        for dir_name in [self.output_dir, self.data_dir, self.reports_dir, self.final_reports_dir]:
            try:
                Path(dir_name).mkdir(parents=True, exist_ok=True)
                logger.info(f"[DIRECTORY] Created/verified directory: {dir_name}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to create directory {dir_name}: {e}")
                raise
    
    def load_farms(self) -> pd.DataFrame:
        """Load farms data from CSV with validation"""
        try:
            if not os.path.exists(self.farms_file):
                raise FileNotFoundError(f"Farms file {self.farms_file} not found!")
            
            farms_df = pd.read_csv(self.farms_file)
            logger.info(f"[DATA] Loaded {len(farms_df)} farms from {self.farms_file}")
            
            # Validate required columns
            required_cols = ['farm_id', 'lat', 'lon']
            missing_cols = [col for col in required_cols if col not in farms_df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Show farm locations
            if 'state' in farms_df.columns:
                state_counts = farms_df['state'].value_counts()
                print("[LOCATIONS] Farm locations:")
                for state, count in state_counts.items():
                    print(f" * {state}: {count} farms")
                    
            return farms_df
            
        except Exception as e:
            logger.error(f"[ERROR] Error loading farms: {e}")
            raise
    
    def fetch_weather_data(self) -> bool:
        """Fetch weather data for all farms"""
        print("\n[STEP 1] Fetching Weather Data")
        print("-" * 40)
        
        try:
            from data_fetchers.weather_fetcher import WeatherDataFetcher
            
            fetcher = WeatherDataFetcher()
            weather_file = fetcher.fetch_all_farms_weather(
                self.farms_file,
                output_file=os.path.join(self.data_dir, "farm_weather_history.csv")
            )
            
            if weather_file and os.path.exists(weather_file):
                logger.info(f"[SUCCESS] Weather data saved to: {weather_file}")
                return True
            else:
                logger.error("[FAILED] Weather data fetch failed")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Weather data error: {e}")
            traceback.print_exc()
            return False
    
    def fetch_soil_data(self) -> bool:
        """Fetch soil data for all farms"""
        print("\n[STEP 2] Fetching Soil Data")
        print("-" * 40)
        
        try:
            from data_fetchers.soil_fetcher import SoilDataFetcher
            
            fetcher = SoilDataFetcher()
            soil_file = fetcher.fetch_all_farms_soil(
                self.farms_file,
                output_file=os.path.join(self.data_dir, "soil_test.csv")
            )
            
            if soil_file and os.path.exists(soil_file):
                logger.info(f"[SUCCESS] Soil data saved to: {soil_file}")
                return True
            else:
                logger.error("[FAILED] Soil data fetch failed")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Soil data error: {e}")
            traceback.print_exc()
            return False
    
    def fetch_satellite_data(self) -> bool:
        """Fetch satellite data for all farms"""
        print("\n[STEP 3] Fetching Satellite Data")
        print("-" * 40)
        
        try:
            from data_fetchers.satellite_fetcher import SatelliteDataFetcher
            
            fetcher = SatelliteDataFetcher()
            satellite_file = fetcher.fetch_all_farms_satellite(
                self.farms_file,
                output_file=os.path.join(self.data_dir, "satellite_data_ultimate.csv")
            )
            
            if satellite_file and os.path.exists(satellite_file):
                logger.info(f"[SUCCESS] Satellite data saved to: {satellite_file}")
                return True
            else:
                logger.error("[FAILED] Satellite data fetch failed")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Satellite data error: {e}")
            traceback.print_exc()
            return False
    
    def generate_agricultural_recommendations_old_format(self) -> bool:
        """Generate agricultural recommendations using OLD ENGINE - SEPARATE output"""
        print("\n[STEP 4A] Generating Agricultural Recommendations (OLD ENGINE FORMAT)")
        print("-" * 40)
        
        try:
            # Import OLD engine with logging  
            from engine.recommendation_engine import FixedNABARDRecommendationEngine
            
            recommendation_engine = FixedNABARDRecommendationEngine()
            logger.info("[INIT] OLD NABARD Engine initialized successfully")
            
            # Load required data files
            weather_file = os.path.join(self.data_dir, "farm_weather_history.csv")
            soil_file = os.path.join(self.data_dir, "soil_test.csv")
            satellite_file = os.path.join(self.data_dir, "satellite_data_ultimate.csv")
            
            # Check data files existence
            missing_files = []
            for file_path in [weather_file, soil_file, satellite_file]:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                logger.error(f"[ERROR] Missing required data files: {missing_files}")
                return False
            
            # Load data
            weather_df = pd.read_csv(weather_file)
            soil_df = pd.read_csv(soil_file)
            satellite_df = pd.read_csv(satellite_file)
            farms_df = pd.read_csv(self.farms_file)
            
            logger.info(f"[DATA] Loaded data - Weather: {len(weather_df)}, Soil: {len(soil_df)}, Satellite: {len(satellite_df)}")
            
            # Use OLD ENGINE method - analyze_all_farms
            logger.info("[PROCESSING] Using OLD engine analyze_all_farms method")
            all_farm_results = recommendation_engine.analyze_all_farms(weather_df, satellite_df, soil_df)
            
            # Save results in our modular format
            successful_farms = 0
            total_farms = len(farms_df)
            
            for farm_id in farms_df['farm_id']:
                try:
                    if farm_id in all_farm_results:
                        logger.info(f"[PROCESSING] OLD format recommendations for farm {farm_id}")
                        
                        # Extract OLD format recommendations
                        farm_result = all_farm_results[farm_id]
                        old_format_recommendations = farm_result["recommendations"]
                        
                        # Ensure output directory exists
                        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
                        
                        # Save agricultural recommendations in OLD FORMAT
                        recommendations_output_file = os.path.join(self.output_dir, f"agricultural_recommendations_{farm_id}.json")
                        
                        with open(recommendations_output_file, 'w', encoding='utf-8') as f:
                            json.dump(old_format_recommendations, f, indent=2, ensure_ascii=False, default=str)
                        
                        logger.info(f"[SUCCESS] OLD format recommendations saved: {recommendations_output_file}")
                        successful_farms += 1
                        
                        # Log key results from OLD format
                        try:
                            if 'recommendations' in old_format_recommendations:
                                total_recs = 0
                                categories = []
                                for category, recs in old_format_recommendations['recommendations'].items():
                                    if recs:
                                        categories.append(category)
                                        total_recs += len(recs)
                                        # Log top variety from each category
                                        if recs:
                                            top_variety = recs[0]
                                            logger.info(f"[RESULT] Top {category} for {farm_id}: {top_variety.get('variety_name', 'Unknown')}")
                                
                                logger.info(f"[RESULT] Generated {total_recs} OLD format recommendations for {farm_id}")
                                logger.info(f"[RESULT] Categories: {', '.join(categories)}")
                            
                            if 'realistic_carbon_potential' in old_format_recommendations:
                                carbon = old_format_recommendations['realistic_carbon_potential']
                                logger.info(f"[RESULT] Carbon potential for {farm_id}: {carbon} tCO2/ha/yr")
                            
                            if 'estimated_revenue' in old_format_recommendations:
                                revenue = old_format_recommendations['estimated_revenue']
                                logger.info(f"[RESULT] Estimated revenue for {farm_id}: ${revenue:.0f}")
                                
                        except Exception as result_error:
                            logger.warning(f"[WARNING] Could not extract OLD format results: {result_error}")
                    
                    else:
                        logger.warning(f"[WARNING] No results found for farm {farm_id} in OLD engine output")
                        continue
                    
                except Exception as e:
                    logger.error(f"[ERROR] Error processing OLD format recommendations for farm {farm_id}: {e}")
                    continue
            
            logger.info(f"[SUCCESS] Generated OLD format agricultural recommendations for {successful_farms}/{total_farms} farms")
            print(f"[SUCCESS] OLD format agricultural recommendations generated for {successful_farms} farms")
            print(f"[FILES] Files saved in: {self.output_dir}/agricultural_recommendations_*.json")
            
            if successful_farms > 0:
                print(f"\n[BENEFITS] OLD ENGINE FORMAT Benefits Delivered:")
                print(" [SUCCESS] Up to 15 recommendations per farm (5 rice + 5 crops + 5 agroforestry)")
                print(" [SUCCESS] Real variety names (BPT-5204, IR-64, Alphonso, etc.)")
                print(" [SUCCESS] Numerical confidence levels (0.782, 0.748, etc.)")
                print(" [SUCCESS] Carbon potential calculations included")
                print(" [SUCCESS] Multiple categories with detailed variety information")
            
            return successful_farms > 0
            
        except Exception as e:
            logger.error(f"[ERROR] OLD format agricultural recommendation generation error: {e}")
            traceback.print_exc()
            return False
    
    def generate_government_schemes_analysis(self) -> bool:
        """Generate government schemes analysis - SEPARATE output"""
        print("\n[STEP 4B] Analyzing Government Schemes Eligibility (SEPARATE OUTPUT)")
        print("-" * 40)
        
        try:
            # Import government schemes matcher
            from government_schemes_matcher import EnhancedGovernmentSchemesMatcher
            
            schemes_matcher = EnhancedGovernmentSchemesMatcher()
            logger.info("[INIT] Government Schemes Matcher initialized")
            
            # Load farms data
            farms_df = pd.read_csv(self.farms_file)
            
            # Process each farm for government schemes
            successful_farms = 0
            total_farms = len(farms_df)
            
            for idx, farm_row in farms_df.iterrows():
                try:
                    farm_id = farm_row['farm_id']
                    logger.info(f"[PROCESSING] Government schemes for farm {farm_id} ({idx + 1}/{total_farms})")
                    
                    # Prepare farmer data
                    farmer_data = {
                        'farm_id': farm_id,
                        'farmer_name': farm_row.get('farmer_name', 'Unknown'),
                        'area_ha': farm_row.get('area_ha', 1.0),
                        'state': farm_row.get('state', 'Unknown'),
                        'district': farm_row.get('district', 'Unknown'),
                        'crop': farm_row.get('crop', 'Mixed'),
                        'lat': farm_row['lat'],
                        'lon': farm_row['lon'],
                        'village': farm_row.get('village', 'Unknown'),
                        'age': farm_row.get('age'),
                        'category': farm_row.get('category'),
                        'annual_income': farm_row.get('annual_income'),
                        'education': farm_row.get('education'),
                        'livestock_count': farm_row.get('livestock_count'),
                        'interested_activities': farm_row.get('interested_activities')
                    }
                    
                    # Generate schemes analysis
                    schemes_analysis = schemes_matcher.analyze_farmer_eligibility(farmer_data)
                    
                    # Ensure output directory exists
                    Path(self.output_dir).mkdir(parents=True, exist_ok=True)
                    
                    # Save government schemes file
                    schemes_output_file = os.path.join(self.output_dir, f"government_schemes_{farm_id}.json")
                    
                    with open(schemes_output_file, 'w', encoding='utf-8') as f:
                        json.dump(schemes_analysis, f, indent=2, ensure_ascii=False, default=str)
                    
                    logger.info(f"[SUCCESS] Government schemes analysis saved: {schemes_output_file}")
                    successful_farms += 1
                    
                    # Log results
                    try:
                        if 'eligibility_summary' in schemes_analysis:
                            summary = schemes_analysis['eligibility_summary']
                            total_schemes = summary.get('total_eligible_schemes', 0)
                            high_priority = summary.get('high_priority_schemes', 0)
                            logger.info(f"[RESULT] Schemes for {farm_id}: {total_schemes} total, {high_priority} high priority")
                            
                            if ('recommended_schemes' in schemes_analysis and
                                'immediate_apply' in schemes_analysis['recommended_schemes'] and
                                schemes_analysis['recommended_schemes']['immediate_apply']):
                                top_scheme = schemes_analysis['recommended_schemes']['immediate_apply'][0]
                                logger.info(f"[RESULT] Top scheme for {farm_id}: {top_scheme.get('scheme_name', 'Unknown')}")
                    except Exception as result_error:
                        logger.warning(f"[WARNING] Could not extract schemes results: {result_error}")
                    
                except Exception as e:
                    logger.error(f"[ERROR] Error processing government schemes for farm {farm_id}: {e}")
                    continue
            
            logger.info(f"[SUCCESS] Generated government schemes analysis for {successful_farms}/{total_farms} farms")
            print(f"[SUCCESS] Government schemes analysis generated for {successful_farms} farms")
            print(f"[FILES] Files saved in: {self.output_dir}/government_schemes_*.json")
            
            return successful_farms > 0
            
        except Exception as e:
            logger.error(f"[ERROR] Government schemes analysis error: {e}")
            traceback.print_exc()
            return False
    
    def generate_comprehensive_reports(self) -> bool:
        """Generate comprehensive reports from OLD engine + government schemes JSON files"""
        print("\n[STEP 5] Generating Comprehensive Reports (NEW)")
        print("-" * 40)
        
        try:
            # Import the comprehensive report generator
            try:
                from comprehensive_report_generator import OldEngineReportGenerator
                logger.info("[INIT] Comprehensive Report Generator imported successfully")
            except ImportError:
                logger.error("[ERROR] Could not import comprehensive_report_generator.py")
                logger.error("[ERROR] Make sure comprehensive_report_generator.py is in the same directory")
                return False
            
            # Initialize the report generator
            try:
                report_generator = OldEngineReportGenerator()
                logger.info("[INIT] Report generator initialized successfully")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize report generator: {e}")
                return False
            
            # Find all agricultural recommendations and government schemes files
            recommendation_files = []
            schemes_files = []
            
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    if file.startswith("agricultural_recommendations_") and file.endswith(".json"):
                        recommendation_files.append(file)
                    elif file.startswith("government_schemes_") and file.endswith(".json"):
                        schemes_files.append(file)
            
            logger.info(f"[FILES] Found {len(recommendation_files)} recommendation files and {len(schemes_files)} schemes files")
            
            if not recommendation_files:
                logger.error("[ERROR] No agricultural recommendation files found")
                return False
            
            if not schemes_files:
                logger.error("[ERROR] No government schemes files found")
                return False
            
            # Generate comprehensive reports for each farm
            successful_reports = 0
            total_farms = 0
            
            # Match recommendation and schemes files by farm_id
            farm_files = {}
            for rec_file in recommendation_files:
                farm_id = rec_file.replace("agricultural_recommendations_", "").replace(".json", "")
                if farm_id not in farm_files:
                    farm_files[farm_id] = {}
                farm_files[farm_id]['recommendation'] = os.path.join(self.output_dir, rec_file)
            
            for schemes_file in schemes_files:
                farm_id = schemes_file.replace("government_schemes_", "").replace(".json", "")
                if farm_id in farm_files:
                    farm_files[farm_id]['schemes'] = os.path.join(self.output_dir, schemes_file)
            
            total_farms = len(farm_files)
            
            for farm_id, files in farm_files.items():
                if 'recommendation' in files and 'schemes' in files:
                    try:
                        logger.info(f"[PROCESSING] Comprehensive report for farm {farm_id}")
                        
                        # Generate comprehensive report
                        report = report_generator.generate_comprehensive_report(
                            files['recommendation'], 
                            files['schemes']
                        )
                        
                        if report:
                            # Save comprehensive report
                            output_filename = os.path.join(self.final_reports_dir, f"comprehensive_agricultural_report_{farm_id}.json")
                            success = report_generator.save_comprehensive_report(report, output_filename)
                            
                            if success:
                                successful_reports += 1
                                logger.info(f"[SUCCESS] Comprehensive report generated for {farm_id}")
                                
                                # Log report highlights
                                try:
                                    if 'report' in report:
                                        report_data = report['report']
                                        
                                        # Log varieties count
                                        if 'recommendations' in report_data:
                                            recs = report_data['recommendations']
                                            rice_count = len(recs.get('rice_varieties', []))
                                            crop_count = len(recs.get('crops', []))
                                            agro_count = len(recs.get('agroforestry', []))
                                            total_varieties = rice_count + crop_count + agro_count
                                            logger.info(f"[RESULT] {farm_id}: {total_varieties} varieties ({rice_count} rice + {crop_count} crops + {agro_count} agroforestry)")
                                        
                                        # Log schemes count
                                        if 'government_schemes' in report_data:
                                            schemes_count = report_data['government_schemes'].get('total_eligible_schemes', 0)
                                            logger.info(f"[RESULT] {farm_id}: {schemes_count} eligible government schemes")
                                        
                                        # Log carbon revenue
                                        if 'carbon_revenue' in report_data:
                                            carbon_revenue = report_data['carbon_revenue'].get('estimated_revenue_inr', 0)
                                            logger.info(f"[RESULT] {farm_id}: Rs {carbon_revenue} carbon credit revenue")
                                            
                                except Exception as result_error:
                                    logger.warning(f"[WARNING] Could not extract report highlights: {result_error}")
                            else:
                                logger.error(f"[ERROR] Failed to save comprehensive report for {farm_id}")
                        else:
                            logger.error(f"[ERROR] Failed to generate comprehensive report for {farm_id}")
                            
                    except Exception as e:
                        logger.error(f"[ERROR] Error generating comprehensive report for {farm_id}: {e}")
                        continue
                else:
                    logger.warning(f"[WARNING] Missing files for {farm_id} - skipping comprehensive report")
            
            logger.info(f"[SUCCESS] Generated {successful_reports}/{total_farms} comprehensive reports")
            print(f"[SUCCESS] Generated {successful_reports}/{total_farms} comprehensive reports")
            print(f"[FILES] Comprehensive reports saved in: {self.final_reports_dir}/comprehensive_agricultural_report_*.json")
            
            if successful_reports > 0:
                print(f"\n[BENEFITS] COMPREHENSIVE REPORTS Benefits:")
                print(" [SUCCESS] Complete integration of OLD engine + government schemes")
                print(" [SUCCESS] Professional report format with enhanced location detection")
                print(" [SUCCESS] Financial projections combining crops + carbon + schemes")
                print(" [SUCCESS] Actionable recommendations with implementation timeline")
                print(" [SUCCESS] Scientific accuracy with web-based location verification")
            
            return successful_reports > 0
            
        except Exception as e:
            logger.error(f"[ERROR] Comprehensive report generation error: {e}")
            traceback.print_exc()
            return False
    
    def generate_modular_summary_reports(self) -> bool:
        """Generate modular summary reports with OLD FORMAT highlights"""
        print("\n[STEP 6] Generating Modular Summary Reports (OLD FORMAT HIGHLIGHTS)")
        print("-" * 40)
        
        try:
            # Find component files
            recommendation_files = []
            schemes_files = []
            comprehensive_files = []
            
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    if file.startswith("agricultural_recommendations_") and file.endswith(".json"):
                        recommendation_files.append(file)
                    elif file.startswith("government_schemes_") and file.endswith(".json"):
                        schemes_files.append(file)
            
            if os.path.exists(self.final_reports_dir):
                for file in os.listdir(self.final_reports_dir):
                    if file.startswith("comprehensive_agricultural_report_") and file.endswith(".json"):
                        comprehensive_files.append(file)
            
            logger.info(f"[FILES] Found {len(recommendation_files)} recommendation files, {len(schemes_files)} schemes files, {len(comprehensive_files)} comprehensive reports")
            
            if not recommendation_files and not schemes_files:
                logger.warning("[WARNING] No component files found")
                return False
            
            # Generate summaries
            successful_summaries = 0
            all_farm_ids = set()
            
            # Get farm IDs from all files
            for f in recommendation_files:
                farm_id = f.replace("agricultural_recommendations_", "").replace(".json", "")
                all_farm_ids.add(farm_id)
            for f in schemes_files:
                farm_id = f.replace("government_schemes_", "").replace(".json", "")
                all_farm_ids.add(farm_id)
            
            for farm_id in all_farm_ids:
                try:
                    rec_file = os.path.join(self.output_dir, f"agricultural_recommendations_{farm_id}.json")
                    schemes_file = os.path.join(self.output_dir, f"government_schemes_{farm_id}.json")
                    comprehensive_file = os.path.join(self.final_reports_dir, f"comprehensive_agricultural_report_{farm_id}.json")
                    
                    recommendations = None
                    schemes = None
                    comprehensive = None
                    
                    # Load available data
                    if os.path.exists(rec_file):
                        with open(rec_file, 'r', encoding='utf-8') as f:
                            recommendations = json.load(f)
                    
                    if os.path.exists(schemes_file):
                        with open(schemes_file, 'r', encoding='utf-8') as f:
                            schemes = json.load(f)
                    
                    if os.path.exists(comprehensive_file):
                        try:
                            with open(comprehensive_file, 'r', encoding='utf-8') as f:
                                comprehensive = json.load(f)
                        except Exception as e:
                            logger.warning(f"[WARNING] Could not load comprehensive report for {farm_id}: {e}")
                    
                    if not recommendations and not schemes:
                        continue
                    
                    # Create COMPLETE summary
                    summary_report = {
                        "farm_id": farm_id,
                        "format_type": "COMPLETE_PIPELINE_OUTPUT",
                        "modular_components": {
                            "agricultural_recommendations_available": os.path.exists(rec_file),
                            "government_schemes_available": os.path.exists(schemes_file),
                            "comprehensive_report_available": os.path.exists(comprehensive_file),
                            "agricultural_recommendations_file": f"agricultural_recommendations_{farm_id}.json" if os.path.exists(rec_file) else None,
                            "government_schemes_file": f"government_schemes_{farm_id}.json" if os.path.exists(schemes_file) else None,
                            "comprehensive_report_file": f"comprehensive_agricultural_report_{farm_id}.json" if os.path.exists(comprehensive_file) else None
                        },
                        "pipeline_highlights": {
                            "total_recommendations": 0,
                            "categories_covered": [],
                            "carbon_potential": 0.0,
                            "estimated_revenue": 0.0,
                            "total_eligible_schemes": 0,
                            "high_priority_schemes": 0,
                            "comprehensive_report_generated": os.path.exists(comprehensive_file)
                        },
                        "next_steps": [],
                        "metadata": {
                            "summary_generated_at": datetime.now().isoformat(),
                            "pipeline_version": "complete_6.6",
                            "components": ["OLD_engine", "government_schemes", "comprehensive_reports"]
                        }
                    }
                    
                    # Extract highlights
                    if recommendations:
                        try:
                            if 'recommendations' in recommendations:
                                total_recs = 0
                                categories = []
                                for category, recs in recommendations['recommendations'].items():
                                    if recs:
                                        categories.append(category)
                                        total_recs += len(recs)
                                
                                summary_report["pipeline_highlights"]["total_recommendations"] = total_recs
                                summary_report["pipeline_highlights"]["categories_covered"] = categories
                            
                            if 'realistic_carbon_potential' in recommendations:
                                summary_report["pipeline_highlights"]["carbon_potential"] = recommendations['realistic_carbon_potential']
                            
                            if 'estimated_revenue' in recommendations:
                                summary_report["pipeline_highlights"]["estimated_revenue"] = recommendations['estimated_revenue']
                                
                        except Exception as e:
                            logger.warning(f"[WARNING] Could not extract recommendation highlights: {e}")
                    
                    if schemes:
                        try:
                            if 'eligibility_summary' in schemes:
                                summary = schemes['eligibility_summary']
                                summary_report["pipeline_highlights"]["total_eligible_schemes"] = summary.get('total_eligible_schemes', 0)
                                summary_report["pipeline_highlights"]["high_priority_schemes"] = summary.get('high_priority_schemes', 0)
                        except Exception as e:
                            logger.warning(f"[WARNING] Could not extract schemes highlights: {e}")
                    
                    # Add next steps
                    if recommendations:
                        total_recs = summary_report["pipeline_highlights"]["total_recommendations"]
                        summary_report["next_steps"].append(f"Review {total_recs} OLD engine recommendations with real variety names")
                    
                    if schemes:
                        schemes_count = summary_report["pipeline_highlights"]["total_eligible_schemes"]
                        summary_report["next_steps"].append(f"Apply for {schemes_count} eligible government schemes")
                    
                    if comprehensive:
                        summary_report["next_steps"].append("Review comprehensive report for complete implementation strategy")
                    else:
                        summary_report["next_steps"].append("Consider generating comprehensive report for integrated analysis")
                    
                    # Save summary
                    summary_file = os.path.join(self.reports_dir, f"complete_pipeline_summary_{farm_id}.json")
                    
                    with open(summary_file, 'w', encoding='utf-8') as f:
                        json.dump(summary_report, f, indent=2, ensure_ascii=False, default=str)
                    
                    logger.info(f"[SUCCESS] Complete pipeline summary generated: {summary_file}")
                    successful_summaries += 1
                    
                except Exception as e:
                    logger.error(f"[ERROR] Error generating summary for farm {farm_id}: {e}")
                    continue
            
            logger.info(f"[SUCCESS] Generated {successful_summaries} complete pipeline summaries")
            print(f"[SUCCESS] Generated {successful_summaries} complete pipeline summaries")
            print(f"[FILES] Summary files saved in: {self.reports_dir}/complete_pipeline_summary_*.json")
            
            return successful_summaries > 0
            
        except Exception as e:
            logger.error(f"[ERROR] Complete pipeline summary generation error: {e}")
            traceback.print_exc()
            return False
    
    def validate_complete_pipeline_components(self) -> bool:
        """Validate all pipeline components"""
        print("\n[VALIDATION] Validating Complete Pipeline Components...")
        
        try:
            # Test OLD engine
            from engine.recommendation_engine import FixedNABARDRecommendationEngine
            old_engine = FixedNABARDRecommendationEngine()
            logger.info("[SUCCESS] OLD NABARD Engine loaded")
            
            # Test government schemes matcher
            from government_schemes_matcher import EnhancedGovernmentSchemesMatcher
            schemes_matcher = EnhancedGovernmentSchemesMatcher()
            logger.info("[SUCCESS] Government Schemes Matcher loaded")
            
            # Test comprehensive report generator
            try:
                from comprehensive_report_generator import OldEngineReportGenerator
                report_generator = OldEngineReportGenerator()
                logger.info("[SUCCESS] Comprehensive Report Generator loaded")
            except ImportError:
                logger.warning("[WARNING] Comprehensive Report Generator not available")
                logger.warning("[WARNING] Make sure comprehensive_report_generator.py is in the directory")
                return False
            
            logger.info("[SUCCESS] All pipeline components validation passed")
            return True
            
        except Exception as e:
            logger.warning(f"[WARNING] Pipeline components validation failed: {e}")
            return False
    
    def run_complete_pipeline(self) -> Dict[str, bool]:
        """Run complete pipeline with OLD ENGINE + COMPREHENSIVE REPORTS"""
        print("[PIPELINE] STARTING COMPLETE PIPELINE WITH OLD ENGINE + REPORTS")
        print("=" * 70)
        
        start_time = time.time()
        results = {
            'farms_loaded': False,
            'complete_pipeline_validation': False,
            'weather_data': False,
            'soil_data': False,
            'satellite_data': False,
            'agricultural_recommendations_old_format': False,
            'government_schemes_analysis': False,
            'comprehensive_reports': False,
            'modular_summary_reports': False
        }
        
        try:
            # Validate complete pipeline components
            results['complete_pipeline_validation'] = self.validate_complete_pipeline_components()
            
            # Load farms
            farms_df = self.load_farms()
            results['farms_loaded'] = True
            logger.info(f"[FARMS] Farms to process: {list(farms_df['farm_id'])}")
            
            # Fetch data
            results['weather_data'] = self.fetch_weather_data()
            results['soil_data'] = self.fetch_soil_data()
            results['satellite_data'] = self.fetch_satellite_data()
            
            # Generate recommendations in OLD FORMAT
            results['agricultural_recommendations_old_format'] = self.generate_agricultural_recommendations_old_format()
            
            # Generate government schemes
            results['government_schemes_analysis'] = self.generate_government_schemes_analysis()
            
            # Generate comprehensive reports (NEW STEP!)
            results['comprehensive_reports'] = self.generate_comprehensive_reports()
            
            # Generate summaries
            results['modular_summary_reports'] = self.generate_modular_summary_reports()
            
        except Exception as e:
            logger.error(f"[ERROR] Pipeline error: {e}")
            traceback.print_exc()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("[SUMMARY] COMPLETE PIPELINE EXECUTION SUMMARY")
        print("=" * 70)
        
        for step, success in results.items():
            status = "[SUCCESS]" if success else "[FAILED]"
            step_name = step.replace('_', ' ').title()
            print(f"{step_name}: {status}")
        
        successful_steps = sum(results.values())
        total_steps = len(results)
        
        logger.info(f"[SUMMARY] Overall Success: {successful_steps}/{total_steps} steps completed")
        logger.info(f"[SUMMARY] Total Duration: {duration:.1f} seconds")
        
        print(f"\n[SUMMARY] Overall Success: {successful_steps}/{total_steps} steps completed")
        print(f"[SUMMARY] Total Duration: {duration:.1f} seconds")
        
        print(f"\n[FILES] COMPLETE PIPELINE Output Structure:")
        print(f" * Raw data files: {self.data_dir}/")
        print(f" * Agricultural recommendations (OLD FORMAT): {self.output_dir}/agricultural_recommendations_*.json")
        print(f" * Government schemes analysis: {self.output_dir}/government_schemes_*.json")
        print(f" * Comprehensive reports (NEW): {self.final_reports_dir}/comprehensive_agricultural_report_*.json")
        print(f" * Modular summary reports: {self.reports_dir}/complete_pipeline_summary_*.json")
        
        if results['comprehensive_reports']:
            print(f"\n[BENEFITS] COMPLETE PIPELINE Benefits:")
            print(" [SUCCESS] OLD Engine: 15 recommendations with real variety names")
            print(" [SUCCESS] Government Schemes: Eligible schemes with detailed benefits")
            print(" [SUCCESS] Comprehensive Reports: Professional format with financial integration")
            print(" [SUCCESS] Enhanced Location: Web-based geocoding for accuracy")
            print(" [SUCCESS] Complete Integration: Crops + Carbon + Schemes + Reports")
            print(" [SUCCESS] Modular Architecture: Separate files for flexibility")
        
        return results

def main():
    """Main execution with COMPLETE PIPELINE"""
    print("[PIPELINE] COMPLETE Agricultural Pipeline with OLD Engine + Reports")
    print("[ENGINE] Rich recommendations with real variety names")
    print("[REPORTS] Comprehensive reports with government schemes integration")
    print("[BENEFITS] 15 recommendations + numerical confidence + carbon potential + comprehensive reports")
    print("[PIPELINE] Starting complete pipeline execution...")
    print()
    
    try:
        controller = CompletePipelineController()
        results = controller.run_complete_pipeline()
        
        # Exit with appropriate code
        if results['comprehensive_reports']:
            print("\n[SUCCESS] Complete pipeline executed successfully!")
            print("[SUCCESS] OLD engine recommendations + Government schemes + Comprehensive reports generated!")
            print("[FILES] Check comprehensive_reports/ folder for final reports!")
            logger.info("[SUCCESS] Complete pipeline completed successfully")
            sys.exit(0)
        elif results['agricultural_recommendations_old_format']:
            print("\n[PARTIAL SUCCESS] OLD engine recommendations generated successfully!")
            print("[INFO] Comprehensive reports may have failed - check logs")
            print("[FILES] Check output/ folder for OLD format files!")
            logger.info("[PARTIAL SUCCESS] Pipeline completed with some components")
            sys.exit(0)
        else:
            print("\n[FAILED] Pipeline failed to generate outputs.")
            logger.error("[FAILED] Complete pipeline failed")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Complete pipeline interrupted by user")
        logger.info("[INTERRUPTED] Pipeline interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n[FATAL] Fatal error in complete pipeline: {e}")
        logger.error(f"[FATAL] Fatal pipeline error: {e}")
        traceback.print_exc()
        sys.exit(4)

if __name__ == "__main__":
    main()