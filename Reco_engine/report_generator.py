#!/usr/bin/env python3
"""
Agricultural Report Generator for Pipeline
=========================================

Enhanced AI report generator using Gemini API to create detailed 
agricultural analysis reports from recommendation data.

Author: Agricultural AI Team
Version: 2.1
"""

import json
import os
import re
import time
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime

class FixedAgriculturalReportGenerator:
    """
    Fixed Agricultural Report Generator - Simplified schema approach
    Avoids the "too many states" API error by using basic JSON output
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the report generator with simplified configuration"""
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Please set GOOGLE_API_KEY environment variable or provide api_key parameter")

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize the model with SIMPLIFIED configuration
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",  # Basic JSON output only
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192
            }
        )

        print("✅ Fixed Agricultural Report Generator v2.1 initialized successfully")

    def _parse_farm_profile(self, farm_profile_str: str) -> Dict:
        """Extract farm data from the farm profile string"""
        try:
            # Extract key-value pairs using regex
            patterns = {
                'farm_id': r"farm_id='([^']*)'",
                'lat': r"lat=np\.float64\(([^)]*)\)",
                'lon': r"lon=np\.float64\(([^)]*)\)",
                'total_rainfall': r"total_rainfall=np\.float64\(([^)]*)\)",
                'rainy_days': r"rainy_days=np\.int64\(([^)]*)\)",
                'avg_temp': r"avg_temp=np\.float64\(([^)]*)\)",
                'avg_humidity': r"avg_humidity=np\.float64\(([^)]*)\)",
                'kharif_rainfall': r"kharif_rainfall=np\.float64\(([^)]*)\)",
                'rabi_rainfall': r"rabi_rainfall=np\.float64\(([^)]*)\)",
                'vegetation_health': r"vegetation_health='([^']*)'",
                'soil_ph_avg': r"soil_ph_avg=np\.float64\(([^)]*)\)",
                'clay_pct_avg': r"clay_pct_avg=np\.float64\(([^)]*)\)",
                'sand_pct_avg': r"sand_pct_avg=np\.float64\(([^)]*)\)",
                'silt_pct_avg': r"silt_pct_avg=np\.float64\(([^)]*)\)",
                'soc_avg': r"soc_avg=np\.float64\(([^)]*)\)",
                'cec_avg': r"cec_avg=np\.float64\(([^)]*)\)",
                'texture': r"texture='([^']*)'",
                'nutrient_status': r"nutrient_status='([^']*)'",
                'ph_status': r"ph_status='([^']*)'",
                'heat_stress_days': r"heat_stress_days=np\.int64\(([^)]*)\)",
                'drought_stress_days': r"drought_stress_days=np\.int64\(([^)]*)\)",
                'temp_variability': r"temp_variability=np\.float64\(([^)]*)\)",
                'recent_rainfall': r"recent_rainfall=np\.float64\(([^)]*)\)",
                'recent_avg_temp': r"recent_avg_temp=np\.float64\(([^)]*)\)",
                'recent_avg_humidity': r"recent_avg_humidity=np\.float64\(([^)]*)\)",
                'detected_zone': r"detected_zone='([^']*)'"
            }

            parsed_data = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, farm_profile_str)
                if match:
                    value = match.group(1)

                    # Convert to appropriate type
                    if key in ['lat', 'lon', 'total_rainfall', 'avg_temp', 'avg_humidity',
                              'kharif_rainfall', 'rabi_rainfall', 'soil_ph_avg', 'clay_pct_avg',
                              'sand_pct_avg', 'silt_pct_avg', 'soc_avg', 'cec_avg',
                              'temp_variability', 'recent_rainfall', 'recent_avg_temp', 'recent_avg_humidity']:
                        parsed_data[key] = float(value)
                    elif key in ['rainy_days', 'heat_stress_days', 'drought_stress_days']:
                        parsed_data[key] = int(value)
                    else:
                        parsed_data[key] = value

            return parsed_data

        except Exception as e:
            print(f"⚠️ Error parsing farm profile: {e}")
            return {}

    def _create_simplified_prompt(self, farm_data: Dict) -> str:
        """Create a simplified prompt that generates JSON without complex schema"""
        return f"""
You are an expert agricultural advisor and carbon farming specialist for Indian agriculture.
Analyze this farm recommendation data and create a comprehensive agricultural report in clean JSON format.

## INPUT DATA:
{json.dumps(farm_data, indent=2)}

## TASK:
Generate a detailed agricultural report as a well-structured JSON object with these main sections:

### Required JSON Structure:

```json
{{
  "farm_id": "extracted_from_input",
  "metadata": {{
    "analysis_id": "unique_id",
    "analysis_date": "current_timestamp",
    "detected_zone": {{
      "code": "zone_code_from_input",
      "name": "zone_display_name",
      "climate_type": "climate_description",
      "elevation": "elevation_level",
      "major_crops": ["crop1", "crop2", "crop3", "crop4"]
    }},
    "data_sources": ["Remote sensing data", "Soil analysis reports", "Historical climate data", "Crop yield databases"],
    "model_version": "v2.1"
  }},
  "report": {{
    "farm_profile": {{
      "location": {{"latitude": number, "longitude": number}},
      "climate": {{
        "annual_rainfall_mm": number,
        "rainy_days": number,
        "avg_temp_c": number,
        "avg_humidity_pct": number,
        "vegetation_health": "status"
      }},
      "soil": {{
        "type": "soil_type",
        "texture": "texture_type",
        "ph": number,
        "ph_status": "status",
        "organic_carbon_pct": number,
        "nutrient_status": "status",
        "clay_pct": number,
        "sand_pct": number,
        "silt_pct": number,
        "cec": number
      }}
    }},
    "key_observations": {{
      "rainfall": {{"kharif_mm": number, "rabi_mm": number, "recent_rainfall_mm": number}},
      "temperature": {{"avg_temp_c": number, "recent_avg_temp_c": number, "temp_variability": number}},
      "humidity": {{"avg_humidity_pct": number, "recent_avg_humidity_pct": number}},
      "stress_indicators": {{"heat_stress_days": number, "drought_stress_days": number}}
    }},
    "recommendations": {{
      "rice_varieties": [/* array of recommended rice varieties with full details */],
      "crops": [/* array of recommended crops with full details */],
      "agroforestry": [/* array of recommended trees with full details */]
    }},
    "farming_scenario": {{
      "rice_coverage": "40%",
      "primary_crop_coverage": "30%",
      "secondary_crop_coverage": "20%",
      "agroforestry_coverage": "10%"
    }},
    "carbon_revenue": {{
      "realistic_carbon_potential_t_ha": number,
      "estimated_annual_credits": number,
      "estimated_revenue_inr": number,
      "income_analysis": {{
        "short_term_crops": "detailed_analysis_text",
        "long_term_agroforestry": "detailed_analysis_text",
        "investment_horizon_years": "timeframe_description",
        "stability_over_10_years": "stability_analysis",
        "recommendation_on_scaling": "scaling_advice"
      }}
    }},
    "zone_context": {{
      "description": "detailed_zone_description_200_plus_characters",
      "best_suited_crops": ["crop1", "crop2", "crop3", "crop4"],
      "challenges": ["challenge1", "challenge2", "challenge3", "challenge4"],
      "opportunities": ["opportunity1", "opportunity2", "opportunity3", "opportunity4"]
    }},
    "risks": {{
      "climate": "climate_risk_description",
      "soil": "soil_risk_description", 
      "market": "market_risk_description",
      "pest_disease": "pest_disease_risk_description"
    }},
    "actions": ["action1", "action2", "action3", "action4"],
    "future_outlook": {{
      "climate_resilience": "resilience_strategy",
      "income_stability": "stability_strategy",
      "sustainability": "sustainability_approach",
      "carbon_farming_scalability": "scaling_potential"
    }},
    "final_summary": "comprehensive_summary_paragraph_150_plus_words"
  }},
  "visualization": {{
    "highlight": ["highlight1", "highlight2", "highlight3", "highlight4"],
    "chart_recommendations": {{
      "rainfall_distribution": ["chart1", "chart2", "chart3"],
      "stress_indicators": ["chart1", "chart2", "chart3"],
      "soil_composition": ["chart1", "chart2", "chart3"],
      "carbon_trends": ["chart1", "chart2", "chart3"]
    }}
  }}
}}
```

## INSTRUCTIONS:

1. **Extract ALL data accurately** from the input farm profile and recommendations

2. **Fill every field** with meaningful, relevant information

3. **Use actual values** from the input data - don't make up numbers

4. **Provide detailed analysis** - each text field should be substantial and informative

5. **Focus on practical advice** that farmers and agricultural officers can implement

6. **Include zone-specific insights** based on the detected agro-climatic zone

7. **Ensure carbon analysis is realistic** and based on the input carbon potential data

8. **Make recommendations actionable** with specific steps and timeframes

## CRITICAL REQUIREMENTS:

- Use EXACT coordinates, rainfall, temperature, and soil data from input
- Base zone analysis on the detected_zone from input
- Include ALL recommended varieties from the input recommendations
- Calculate carbon revenue from the realistic_carbon_potential in input
- Provide farmer-friendly explanations while maintaining scientific accuracy
- Include visualization suggestions that would help farmers understand the data

Generate a complete, professional agricultural report that covers all aspects of farming, carbon sequestration, and business planning for this specific farm.
"""

    def load_recommendation_file(self, filepath: str) -> Optional[Dict]:
        """Load and validate a recommendation JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Basic validation
            required_fields = ['farm_profile', 'detected_zone', 'recommendations']
            for field in required_fields:
                if field not in data:
                    print(f"⚠️ Warning: Missing required field '{field}' in {filepath}")

            print(f"✅ Successfully loaded {filepath}")
            return data

        except FileNotFoundError:
            print(f"❌ Error: File {filepath} not found")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in {filepath}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return None

    def generate_report(self, recommendation_data: Dict, max_retries: int = 3) -> Optional[Dict]:
        """Generate agricultural report with simplified approach"""
        farm_id = recommendation_data.get('farm_profile', '').split("'")[1] if "farm_id=" in str(recommendation_data.get('farm_profile', '')) else 'Unknown'
        print(f"🔄 Generating report for {farm_id}...")

        # Parse farm profile if it's a string
        if isinstance(recommendation_data.get('farm_profile'), str):
            parsed_profile = self._parse_farm_profile(recommendation_data['farm_profile'])
            recommendation_data['parsed_farm_profile'] = parsed_profile

        prompt = self._create_simplified_prompt(recommendation_data)

        for attempt in range(max_retries):
            try:
                print(f"  Attempt {attempt + 1}/{max_retries}...")
                response = self.model.generate_content(prompt)

                if not response.text:
                    print(f"  ⚠️ Empty response on attempt {attempt + 1}")
                    continue

                # Parse and validate JSON
                report_json = json.loads(response.text)

                # Basic validation and cleanup
                if 'farm_id' not in report_json:
                    report_json['farm_id'] = farm_id

                # Ensure farm_id is correct
                if 'farm_id' in report_json:
                    report_json['farm_id'] = farm_id

                print(f"  ✅ Successfully generated report for {farm_id}")
                return report_json

            except json.JSONDecodeError as e:
                print(f"  ⚠️ JSON decode error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue

            except Exception as e:
                print(f"  ⚠️ Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue

        print(f"❌ Failed to generate report for {farm_id} after {max_retries} attempts")
        return None

    def save_report(self, report_data: Dict, output_filename: str) -> bool:
        """Save the generated report to a JSON file"""
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Report saved to {output_filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving report to {output_filename}: {e}")
            return False

    def process_multiple_farms(self, input_files: List[str], output_dir: str = ".") -> Dict[str, bool]:
        """Process multiple farm recommendation files"""
        results = {}
        print(f"🚀 Processing {len(input_files)} farm recommendation files...")

        # Create output directory if it doesn't exist
        if output_dir != "." and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")

        for input_file in input_files:
            try:
                # Load recommendation data
                recommendation_data = self.load_recommendation_file(input_file)
                if not recommendation_data:
                    results[input_file] = False
                    continue

                # Generate report
                report = self.generate_report(recommendation_data)
                if not report:
                    results[input_file] = False
                    continue

                # Create output filename
                farm_id = report.get('farm_id', 'unknown')
                output_filename = os.path.join(output_dir, f"fixed_agri_report_{farm_id}.json")

                # Save report
                success = self.save_report(report, output_filename)
                results[input_file] = success

                # Add delay to avoid rate limiting
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error processing {input_file}: {e}")
                results[input_file] = False

        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"\n📊 Processing Summary: {successful}/{total} files processed successfully")

        return results

def main():
    """Main function with error handling"""
    try:
        # Initialize the fixed report generator
        generator = FixedAgriculturalReportGenerator()

        # List of recommendation files to process
        input_files = [
            "perfected_recommendations_F001.json",
            "perfected_recommendations_F002.json",
            "perfected_recommendations_F003.json"
        ]

        # Check which files exist
        existing_files = [f for f in input_files if os.path.exists(f)]
        if not existing_files:
            print("❌ No recommendation files found!")
            print("Expected files:")
            for f in input_files:
                print(f"  - {f}")
            return

        print(f"📁 Found {len(existing_files)} recommendation files")

        # Process all files
        results = generator.process_multiple_farms(existing_files, output_dir="fixed_reports")

        print("\n🎉 Fixed agricultural report generation completed!")
        print("Check the 'fixed_reports' directory for output files.")

        # Show results
        for file, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {file}: {status}")

    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
