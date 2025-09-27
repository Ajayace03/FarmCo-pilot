#!/usr/bin/env python3
"""
FIXED Enhanced Government Schemes Matcher - Production Ready Version
==================================================================

CRITICAL FIX: Resolves JSON parsing error with metadata handling

Fixed Issues:
- ✅ Handles mixed data types in JSON (integers, lists, dicts)
- ✅ Filters out metadata when counting schemes
- ✅ Robust error handling for malformed data
- ✅ All original functionality preserved

Author: Agricultural AI Team  
Version: 3.1 - HOTFIX for JSON Structure Issue
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
from functools import lru_cache
import re

# Configure module logger
logger = logging.getLogger(__name__)

class SchemeMatcherError(Exception):
    """Base exception for scheme matcher errors"""
    pass

class ConfigurationError(SchemeMatcherError):
    """Configuration related errors"""
    pass

class DataValidationError(SchemeMatcherError):
    """Data validation errors"""
    pass

class SchemeLoadingError(SchemeMatcherError):
    """Scheme database loading errors"""
    pass

@dataclass
class FarmerProfile:
    """Enhanced farmer profile with validation"""
    # Basic Information (Required)
    farm_id: str
    farmer_id: str
    farmer_name: str
    lat: float
    lon: float
    area_ha: float
    village: str
    district: str
    state: str
    crop: str
    
    # Enhanced Information (Optional but improves matching)
    age: Optional[int] = None
    category: Optional[str] = None  # SC/ST/OBC/General
    annual_income: Optional[float] = None
    education: Optional[str] = None
    aadhaar: Optional[str] = None
    land_ownership_type: Optional[str] = None  # owned/leased/tenant
    bank_account: Optional[str] = None
    livestock_count: Optional[int] = None
    interested_activities: Optional[List[str]] = field(default_factory=list)
    farming_experience: Optional[int] = None
    
    def __post_init__(self):
        """Validate farmer profile data"""
        # Validate required fields
        if not str(self.farm_id).strip():
            raise DataValidationError("Farm ID cannot be empty")
        if not str(self.farmer_name).strip():
            raise DataValidationError("Farmer name cannot be empty")
        
        # Validate coordinates
        if not -90 <= self.lat <= 90:
            raise DataValidationError(f"Invalid latitude: {self.lat}")
        if not -180 <= self.lon <= 180:
            raise DataValidationError(f"Invalid longitude: {self.lon}")
        
        # Validate area
        if self.area_ha <= 0:
            raise DataValidationError(f"Area must be positive: {self.area_ha}")
        
        # Validate optional fields
        if self.age is not None and not 18 <= self.age <= 100:
            logger.warning(f"Age {self.age} seems unusual for farmer {self.farmer_name}")
        
        if self.annual_income is not None and self.annual_income < 0:
            raise DataValidationError("Annual income cannot be negative")
        
        # Sanitize text fields
        self.farmer_name = str(self.farmer_name).strip()
        self.village = str(self.village).strip()
        self.district = str(self.district).strip()
        self.state = str(self.state).strip()

@dataclass
class SchemeMatch:
    """Represents a scheme match with eligibility details"""
    scheme_id: str
    scheme_name: str
    category: str
    eligibility_score: float  # 0.0 to 1.0
    eligible: bool
    subsidy_amount: str
    key_benefits: List[str]
    missing_requirements: List[str]
    next_steps: List[str]
    priority_level: str  # High/Medium/Low
    contact_details: Dict[str, Any]

@dataclass 
class MatchingConfig:
    """Configuration for scheme matching"""
    schemes_file: str = "./database/India_schemes_v1.json"
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    min_eligibility_score: float = 0.6
    priority_categories: List[str] = field(default_factory=lambda: ["nabard_schemes", "central_schemes"])
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'MatchingConfig':
        """Create configuration from environment variables"""
        return cls(
            schemes_file=os.getenv('SCHEMES_FILE', cls.__dataclass_fields__['schemes_file'].default),
            cache_enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            cache_ttl_hours=int(os.getenv('CACHE_TTL_HOURS', '24')),
            min_eligibility_score=float(os.getenv('MIN_ELIGIBILITY_SCORE', '0.6')),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )

class SchemeDataLoader:
    """Handles loading and caching of scheme database - FIXED VERSION"""
    
    def __init__(self, config: MatchingConfig):
        self.config = config
        self._schemes_cache: Optional[Dict] = None
        self._cache_timestamp: Optional[datetime.datetime] = None
        
    def load_schemes(self) -> Dict[str, Any]:
        """Load schemes database with caching - FIXED to handle mixed data types"""
        # Check cache validity
        if self._is_cache_valid():
            logger.debug("Using cached schemes database")
            return self._schemes_cache
        
        # Load from file
        try:
            schemes_path = Path(self.config.schemes_file)
            if not schemes_path.exists():
                raise SchemeLoadingError(f"Schemes file not found: {schemes_path}")
            
            logger.info(f"Loading schemes database from {schemes_path}")
            with open(schemes_path, 'r', encoding='utf-8') as f:
                schemes_data = json.load(f)
            
            # Validate structure
            if 'enhanced_schemes_database' not in schemes_data:
                raise SchemeLoadingError("Invalid schemes database structure")
            
            # Cache the data
            if self.config.cache_enabled:
                self._schemes_cache = schemes_data
                self._cache_timestamp = datetime.datetime.now()
                logger.debug(f"Cached schemes database")
            
            # FIXED: Log database stats safely
            db = schemes_data['enhanced_schemes_database']
            total_schemes = self._count_schemes_safely(db)
            logger.info(f"Loaded {total_schemes} schemes across {len(db)} categories")
            
            return schemes_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schemes file: {e}")
            raise SchemeLoadingError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error loading schemes database: {e}")
            raise SchemeLoadingError(f"Failed to load schemes: {e}")
    
    def _count_schemes_safely(self, db: Dict[str, Any]) -> int:
        """FIXED: Safely count schemes handling mixed data types"""
        total = 0
        scheme_categories = ['nabard_schemes', 'central_schemes', 'animal_husbandry_schemes', 
                            'fisheries_schemes', 'state_schemes', 'ut_schemes', 'special_programs']
        
        for category_name in scheme_categories:
            if category_name not in db:
                continue
                
            category_data = db[category_name]
            
            try:
                if isinstance(category_data, list):
                    # Direct list of schemes
                    total += len(category_data)
                elif isinstance(category_data, dict):
                    # Nested structure (like state_schemes)
                    for subcategory_data in category_data.values():
                        if isinstance(subcategory_data, list):
                            total += len(subcategory_data)
                        elif isinstance(subcategory_data, dict):
                            # Handle deeper nesting if needed
                            continue
                # Skip non-scheme data (integers, strings, etc.)
            except Exception as e:
                logger.warning(f"Error counting schemes in category {category_name}: {e}")
                continue
        
        return total
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.config.cache_enabled or self._schemes_cache is None:
            return False
        
        if self._cache_timestamp is None:
            return False
        
        age = datetime.datetime.now() - self._cache_timestamp
        max_age = datetime.timedelta(hours=self.config.cache_ttl_hours)
        
        return age < max_age

class EligibilityAnalyzer:
    """Analyzes farmer eligibility for schemes"""
    
    def __init__(self):
        self.state_mapping = self._create_state_mapping()
    
    def analyze_scheme_eligibility(self, farmer: FarmerProfile, scheme: Dict[str, Any]) -> SchemeMatch:
        """Analyze farmer eligibility for a specific scheme"""
        try:
            eligibility_score = 0.0
            missing_requirements = []
            eligible = False
            
            # Basic eligibility checks
            score_components = {
                'geographic': self._check_geographic_eligibility(farmer, scheme),
                'land_size': self._check_land_size_eligibility(farmer, scheme), 
                'age': self._check_age_eligibility(farmer, scheme),
                'income': self._check_income_eligibility(farmer, scheme),
                'category': self._check_category_eligibility(farmer, scheme),
                'activity': self._check_activity_eligibility(farmer, scheme)
            }
            
            # Calculate weighted score
            weights = {'geographic': 0.3, 'land_size': 0.2, 'age': 0.1, 'income': 0.1, 'category': 0.1, 'activity': 0.2}
            eligibility_score = sum(score * weights.get(component, 0.1) 
                                  for component, (score, _) in score_components.items())
            
            # Collect missing requirements
            for component, (score, missing) in score_components.items():
                if missing:
                    missing_requirements.extend(missing)
            
            eligible = eligibility_score >= 0.6  # 60% threshold
            
            # Determine priority level
            priority_level = self._determine_priority(farmer, scheme, eligibility_score)
            
            # Get subsidy information
            subsidy_amount = self._extract_subsidy_amount(farmer, scheme)
            
            return SchemeMatch(
                scheme_id=scheme.get('scheme_id', ''),
                scheme_name=scheme.get('scheme_name', ''),
                category=scheme.get('category', ''),
                eligibility_score=eligibility_score,
                eligible=eligible,
                subsidy_amount=subsidy_amount,
                key_benefits=scheme.get('key_benefits', []),
                missing_requirements=missing_requirements,
                next_steps=scheme.get('application_process', [])[:3],  # First 3 steps
                priority_level=priority_level,
                contact_details=scheme.get('contact_details', {})
            )
            
        except Exception as e:
            logger.error(f"Error analyzing eligibility for scheme {scheme.get('scheme_id', 'unknown')}: {e}")
            return self._create_error_match(scheme, str(e))
    
    def _check_geographic_eligibility(self, farmer: FarmerProfile, scheme: Dict) -> Tuple[float, List[str]]:
        """Check geographic eligibility"""
        scheme_coverage = scheme.get('state_ut', 'All India')
        
        if scheme_coverage == 'All India':
            return 1.0, []
        
        # Normalize state names for comparison
        farmer_state = self._normalize_state_name(farmer.state)
        scheme_state = self._normalize_state_name(scheme_coverage)
        
        if farmer_state == scheme_state:
            return 1.0, []
        
        return 0.0, [f"Scheme limited to {scheme_coverage}, farmer in {farmer.state}"]
    
    def _check_land_size_eligibility(self, farmer: FarmerProfile, scheme: Dict) -> Tuple[float, List[str]]:
        """Check land size requirements"""
        land_req = scheme.get('land_size_requirement', '')
        
        if not land_req or 'No minimum' in str(land_req) or 'All categories' in str(land_req):
            return 1.0, []
        
        # PM-KISAN specific check (up to 2 hectares)
        if 'PM-KISAN' in scheme.get('scheme_name', ''):
            if farmer.area_ha <= 2.0:
                return 1.0, []
            return 0.0, [f"PM-KISAN limited to ≤2 hectares, farmer has {farmer.area_ha} hectares"]
        
        # Default: assume eligible unless specific restrictions
        return 0.8, []
    
    def _check_age_eligibility(self, farmer: FarmerProfile, scheme: Dict) -> Tuple[float, List[str]]:
        """Check age requirements"""
        if farmer.age is None:
            return 0.5, ["Age information needed for complete eligibility check"]
        
        age_req = scheme.get('age_requirement', '')
        if not age_req or 'No age' in str(age_req):
            return 1.0, []
        
        # Extract age range (e.g., "18-60 years")
        age_match = re.findall(r'(\d+)-(\d+)', str(age_req))
        if age_match:
            min_age, max_age = map(int, age_match[0])
            if min_age <= farmer.age <= max_age:
                return 1.0, []
            return 0.0, [f"Age requirement: {min_age}-{max_age} years, farmer age: {farmer.age}"]
        
        return 0.8, []
    
    def _check_income_eligibility(self, farmer: FarmerProfile, scheme: Dict) -> Tuple[float, List[str]]:
        """Check income requirements"""
        if farmer.annual_income is None:
            return 0.5, ["Income information helpful for eligibility verification"]
        
        income_limit = scheme.get('income_limit', '')
        if not income_limit or 'No income' in str(income_limit) or 'No specific' in str(income_limit):
            return 1.0, []
        
        # PM-KISAN: Should not be income tax payer (assume > 5 lakhs)
        if 'PM-KISAN' in scheme.get('scheme_name', '') and farmer.annual_income > 500000:
            return 0.0, ["PM-KISAN: Should not be income tax payer"]
        
        return 0.8, []
    
    def _check_category_eligibility(self, farmer: FarmerProfile, scheme: Dict) -> Tuple[float, List[str]]:
        """Check caste category eligibility and benefits"""
        if farmer.category is None:
            return 0.7, ["Category information (SC/ST/OBC/General) needed for subsidy calculation"]
        
        # All schemes generally eligible for all categories, but subsidy rates vary
        return 1.0, []
    
    def _check_activity_eligibility(self, farmer: FarmerProfile, scheme: Dict) -> Tuple[float, List[str]]:
        """Check activity/interest-based eligibility"""
        scheme_name = scheme.get('scheme_name', '').lower()
        
        # Activity-specific schemes
        if 'livestock' in scheme_name or 'animal' in scheme_name:
            if farmer.livestock_count and farmer.livestock_count > 0:
                return 1.0, []
            return 0.3, ["Scheme for livestock farmers - livestock ownership needed"]
        
        if 'fisheries' in scheme_name or 'matsya' in scheme_name:
            if farmer.interested_activities and 'fisheries' in [a.lower() for a in farmer.interested_activities]:
                return 1.0, []
            return 0.3, ["Scheme for fisheries - interest in fish farming needed"]
        
        # Infrastructure schemes
        if 'infrastructure' in scheme_name or 'ami' in scheme_name.lower():
            if farmer.interested_activities and any('storage' in a.lower() or 'processing' in a.lower() 
                                                   for a in farmer.interested_activities):
                return 1.0, []
            return 0.5, ["Infrastructure scheme - interest in storage/processing needed"]
        
        # General agricultural schemes
        return 0.9, []
    
    def _determine_priority(self, farmer: FarmerProfile, scheme: Dict, score: float) -> str:
        """Determine scheme priority for farmer"""
        category = scheme.get('category', '')
        
        # High priority: NABARD and Central schemes with high eligibility
        if category in ['nabard_schemes', 'central_schemes'] and score >= 0.8:
            return 'High'
        
        # Medium priority: Good eligibility or important schemes
        if score >= 0.7 or 'PM-KISAN' in scheme.get('scheme_name', ''):
            return 'Medium'
        
        return 'Low'
    
    def _extract_subsidy_amount(self, farmer: FarmerProfile, scheme: Dict) -> str:
        """Extract subsidy amount information"""
        subsidy = scheme.get('subsidy_amount', 'Contact for details')
        
        # Enhance based on farmer category
        if farmer.category in ['SC', 'ST'] and 'SC/ST' in str(scheme.get('eligibility_criteria', '')):
            if 'higher' in str(subsidy).lower() or 'enhanced' in str(subsidy).lower():
                subsidy += " (Enhanced rate for SC/ST)"
        
        return str(subsidy)
    
    def _normalize_state_name(self, state: str) -> str:
        """Normalize state name for comparison"""
        return str(state).lower().replace(' ', '_').replace('-', '_')
    
    def _create_state_mapping(self) -> Dict[str, str]:
        """Create mapping for state name variations"""
        return {
            'tamil_nadu': 'tamil nadu',
            'uttar_pradesh': 'uttar pradesh',
            'madhya_pradesh': 'madhya pradesh',
            'andhra_pradesh': 'andhra pradesh',
            'himachal_pradesh': 'himachal pradesh',
            'west_bengal': 'west bengal',
            'jammu_kashmir': 'jammu kashmir'
        }
    
    def _create_error_match(self, scheme: Dict, error: str) -> SchemeMatch:
        """Create error match result"""
        return SchemeMatch(
            scheme_id=scheme.get('scheme_id', ''),
            scheme_name=scheme.get('scheme_name', 'Unknown'),
            category=scheme.get('category', ''),
            eligibility_score=0.0,
            eligible=False,
            subsidy_amount="Error in analysis",
            key_benefits=[],
            missing_requirements=[f"Analysis error: {error}"],
            next_steps=["Contact technical support"],
            priority_level='Low',
            contact_details={}
        )

class ReportGenerator:
    """Generates farmer eligibility reports"""
    
    def generate_farmer_report(self, farmer: FarmerProfile, matches: List[SchemeMatch]) -> Dict[str, Any]:
        """Generate comprehensive farmer eligibility report"""
        # Categorize matches
        eligible_schemes = [m for m in matches if m.eligible]
        high_priority = [m for m in eligible_schemes if m.priority_level == 'High']
        medium_priority = [m for m in eligible_schemes if m.priority_level == 'Medium']
        
        # Calculate total potential benefits
        total_schemes = len(eligible_schemes)
        direct_benefits = [m for m in eligible_schemes if 'Rs' in m.subsidy_amount]
        
        # Identify missing information impact
        missing_info_impact = self._analyze_missing_info_impact(farmer, matches)
        
        report = {
            'farmer_profile': {
                'name': farmer.farmer_name,
                'farm_id': farmer.farm_id,
                'location': f"{farmer.village}, {farmer.district}, {farmer.state}",
                'farm_size': f"{farmer.area_ha} hectares",
                'primary_crop': farmer.crop,
                'profile_completeness': self._calculate_profile_completeness(farmer)
            },
            'eligibility_summary': {
                'total_eligible_schemes': total_schemes,
                'high_priority_schemes': len(high_priority),
                'medium_priority_schemes': len(medium_priority),
                'direct_benefit_schemes': len(direct_benefits),
                'potential_additional_schemes': len([m for m in matches if not m.eligible and m.eligibility_score > 0.4])
            },
            'recommended_schemes': {
                'immediate_apply': [self._serialize_match(m) for m in high_priority[:5]],
                'consider_applying': [self._serialize_match(m) for m in medium_priority[:5]]
            },
            'missing_information': missing_info_impact,
            'next_steps': self._generate_next_steps(farmer, eligible_schemes),
            'report_metadata': {
                'generated_at': datetime.datetime.now().isoformat(),
                'total_schemes_analyzed': len(matches),
                'analysis_version': '3.1'
            }
        }
        
        return report
    
    def _calculate_profile_completeness(self, farmer: FarmerProfile) -> Dict[str, Any]:
        """Calculate farmer profile completeness"""
        total_fields = 20  # Total possible fields
        filled_fields = 10  # Basic required fields
        
        # Count optional fields
        optional_checks = [
            farmer.age is not None,
            farmer.category is not None,
            farmer.annual_income is not None,
            farmer.education is not None,
            farmer.aadhaar is not None,
            farmer.land_ownership_type is not None,
            farmer.bank_account is not None,
            farmer.livestock_count is not None,
            farmer.interested_activities is not None and len(farmer.interested_activities) > 0,
            farmer.farming_experience is not None
        ]
        
        filled_fields += sum(optional_checks)
        completeness_pct = (filled_fields / total_fields) * 100
        
        return {
            'percentage': round(completeness_pct, 1),
            'filled_fields': filled_fields,
            'total_fields': total_fields,
            'status': 'Excellent' if completeness_pct >= 90 else 'Good' if completeness_pct >= 70 else 'Needs Improvement'
        }
    
    def _analyze_missing_info_impact(self, farmer: FarmerProfile, matches: List[SchemeMatch]) -> Dict[str, Any]:
        """Analyze impact of missing farmer information"""
        missing_info = []
        potential_benefits = []
        
        if farmer.age is None:
            missing_info.append("Age")
            potential_benefits.append("Age-specific schemes and enhanced eligibility verification")
        
        if farmer.category is None:
            missing_info.append("Category (SC/ST/OBC/General)")
            potential_benefits.append("Enhanced subsidy rates for SC/ST/Women (up to 60% vs 40%)")
        
        if farmer.annual_income is None:
            missing_info.append("Annual Income")
            potential_benefits.append("Income-based scheme eligibility and accurate benefit calculation")
        
        if farmer.education is None:
            missing_info.append("Education Qualification")
            potential_benefits.append("Entrepreneurship schemes like NABARD ACABC")
        
        if not farmer.interested_activities:
            missing_info.append("Interested Activities")
            potential_benefits.append("Activity-specific schemes (storage, processing, livestock, fisheries)")
        
        return {
            'missing_fields': missing_info,
            'potential_benefits': potential_benefits,
            'improvement_impact': f"Adding missing information could unlock {len(potential_benefits)} additional benefit categories"
        }
    
    def _generate_next_steps(self, farmer: FarmerProfile, eligible_schemes: List[SchemeMatch]) -> List[str]:
        """Generate personalized next steps"""
        steps = []
        
        # Immediate actions
        if eligible_schemes:
            steps.append(f"Apply for PM-KISAN immediately (guaranteed Rs 6,000/year for {farmer.farmer_name})")
            steps.append("Visit nearest agriculture office for Interest Subvention Scheme enrollment")
        
        # Profile completion
        if farmer.category is None:
            steps.append("Obtain caste certificate if applicable (unlocks higher subsidy rates)")
        
        if farmer.aadhaar is None:
            steps.append("Ensure Aadhaar card is available (mandatory for most schemes)")
        
        # Specific recommendations
        if farmer.area_ha >= 0.5:
            steps.append("Consider applying for micro irrigation under PM-RKVY")
        
        steps.append(f"Contact {farmer.state} Agriculture Department for state-specific schemes")
        
        return steps[:6]  # Limit to top 6 actionable steps
    
    def _serialize_match(self, match: SchemeMatch) -> Dict[str, Any]:
        """Serialize scheme match for JSON output"""
        return {
            'scheme_name': match.scheme_name,
            'category': match.category,
            'eligibility_score': round(match.eligibility_score, 2),
            'subsidy_amount': match.subsidy_amount,
            'key_benefits': match.key_benefits[:3],  # Top 3 benefits
            'next_steps': match.next_steps[:3],  # Top 3 steps
            'missing_requirements': match.missing_requirements,
            'priority': match.priority_level,
            'contact': match.contact_details.get('helpline_number', 'Contact agriculture office')
        }

class EnhancedGovernmentSchemesMatcher:
    """
    Enhanced Government Schemes Matcher with modular architecture - FIXED VERSION
    
    Features:
    - Modular design with separated concerns
    - Professional logging
    - Configuration management  
    - Comprehensive error handling
    - Performance optimizations
    - Enhanced farmer profiling
    - FIXED: Handles mixed JSON data types properly
    """
    
    def __init__(self, config: Optional[MatchingConfig] = None):
        """Initialize enhanced schemes matcher"""
        self.config = config or MatchingConfig.from_env()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.data_loader = SchemeDataLoader(self.config)
        self.eligibility_analyzer = EligibilityAnalyzer()
        self.report_generator = ReportGenerator()
        
        logger.info(f"Enhanced Government Schemes Matcher v3.1 initialized (FIXED)")
        logger.info(f"Configuration: schemes_file={self.config.schemes_file}, cache_enabled={self.config.cache_enabled}")
    
    def _setup_logging(self):
        """Setup structured logging"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def analyze_farmer_eligibility(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze farmer eligibility for all schemes
        
        Args:
            farmer_data: Dictionary containing farmer information
            
        Returns:
            Comprehensive eligibility report
        """
        try:
            # Create farmer profile
            farmer = self._create_farmer_profile(farmer_data)
            
            logger.info(f"Analyzing eligibility for farmer {farmer.farmer_name} (ID: {farmer.farm_id})")
            logger.info(f"Location: {farmer.village}, {farmer.district}, {farmer.state}")
            logger.info(f"Farm: {farmer.area_ha} hectares, crop: {farmer.crop}")
            
            # Load schemes database
            schemes_data = self.data_loader.load_schemes()
            
            # Analyze eligibility for all schemes
            all_matches = []
            schemes_db = schemes_data['enhanced_schemes_database']
            
            # Process each scheme category
            for category_name, schemes in schemes_db.items():
                # FIXED: Skip metadata and non-scheme categories
                if category_name == 'metadata' or not isinstance(schemes, (list, dict)):
                    continue
                    
                category_matches = self._process_scheme_category(farmer, category_name, schemes)
                all_matches.extend(category_matches)
            
            logger.info(f"Analyzed {len(all_matches)} schemes for farmer {farmer.farm_id}")
            
            # Filter by minimum eligibility score
            filtered_matches = [m for m in all_matches if m.eligibility_score >= self.config.min_eligibility_score or m.eligible]
            
            logger.info(f"Found {len(filtered_matches)} eligible/potential schemes (score >= {self.config.min_eligibility_score})")
            
            # Generate comprehensive report
            report = self.report_generator.generate_farmer_report(farmer, all_matches)
            
            logger.info(f"Generated eligibility report for {farmer.farmer_name}")
            logger.info(f"Eligible schemes: {report['eligibility_summary']['total_eligible_schemes']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing farmer eligibility: {e}")
            raise SchemeMatcherError(f"Failed to analyze eligibility: {e}")
    
    def process_farms_csv(self, csv_file: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Process multiple farms from CSV file
        
        Args:
            csv_file: Path to farms CSV file
            output_file: Optional output file for results
            
        Returns:
            Processing results summary
        """
        try:
            logger.info(f"Processing farms from CSV: {csv_file}")
            
            # Load farms data
            farms_df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(farms_df)} farms from CSV")
            
            # Process each farm
            results = {}
            successful_farms = 0
            failed_farms = 0
            
            for idx, farm_row in farms_df.iterrows():
                try:
                    farm_data = farm_row.to_dict()
                    farm_id = farm_data.get('farm_id', f'farm_{idx}')
                    
                    # Analyze eligibility
                    result = self.analyze_farmer_eligibility(farm_data)
                    results[farm_id] = result
                    successful_farms += 1
                    
                    logger.debug(f"Successfully processed farm {farm_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process farm {farm_data.get('farm_id', idx)}: {e}")
                    failed_farms += 1
                    continue
            
            # Save results if output file specified
            if output_file:
                self._save_results(results, output_file)
                logger.info(f"Results saved to: {output_file}")
            
            summary = {
                'total_farms': len(farms_df),
                'successful_farms': successful_farms,
                'failed_farms': failed_farms,
                'results': results
            }
            
            logger.info(f"CSV processing completed: {successful_farms}/{len(farms_df)} farms successful")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error processing farms CSV: {e}")
            raise SchemeMatcherError(f"Failed to process CSV: {e}")
    
    def _create_farmer_profile(self, farmer_data: Dict[str, Any]) -> FarmerProfile:
        """Create validated farmer profile from data"""
        try:
            # Handle potential column name variations and missing data
            profile_data = {
                'farm_id': str(farmer_data.get('farm_id', '')),
                'farmer_id': str(farmer_data.get('farmer_id', farmer_data.get('farm_id', ''))),
                'farmer_name': str(farmer_data.get('farmer_name', 'Unknown')),
                'lat': float(farmer_data.get('lat', 0.0)),
                'lon': float(farmer_data.get('lon', 0.0)),
                'area_ha': float(farmer_data.get('area_ha', 0.0)),
                'village': str(farmer_data.get('village', '')),
                'district': str(farmer_data.get('district', '')),
                'state': str(farmer_data.get('state', '')),
                'crop': str(farmer_data.get('crop', 'Mixed')),
            }
            
            # Add optional fields if available
            optional_fields = {
                'age': 'age',
                'category': 'category', 
                'annual_income': 'annual_income',
                'education': 'education',
                'aadhaar': 'aadhaar',
                'land_ownership_type': 'land_ownership_type',
                'bank_account': 'bank_account',
                'livestock_count': 'livestock_count',
                'farming_experience': 'farming_experience'
            }
            
            for profile_key, data_key in optional_fields.items():
                value = farmer_data.get(data_key)
                if value is not None and str(value).strip():
                    if profile_key in ['age', 'livestock_count', 'farming_experience']:
                        try:
                            profile_data[profile_key] = int(float(value))
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid {profile_key} value: {value}")
                    elif profile_key == 'annual_income':
                        try:
                            profile_data[profile_key] = float(value)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid annual_income value: {value}")
                    else:
                        profile_data[profile_key] = str(value).strip()
            
            # Handle interested activities
            activities = farmer_data.get('interested_activities', '')
            if activities:
                if isinstance(activities, str):
                    profile_data['interested_activities'] = [a.strip() for a in activities.split(',') if a.strip()]
                elif isinstance(activities, list):
                    profile_data['interested_activities'] = activities
            
            return FarmerProfile(**profile_data)
            
        except Exception as e:
            logger.error(f"Error creating farmer profile: {e}")
            raise DataValidationError(f"Invalid farmer data: {e}")
    
    def _process_scheme_category(self, farmer: FarmerProfile, category_name: str, schemes: Any) -> List[SchemeMatch]:
        """Process schemes in a category"""
        matches = []
        
        try:
            if isinstance(schemes, list):
                # Direct list of schemes
                for scheme in schemes:
                    if isinstance(scheme, dict):  # Ensure it's a valid scheme object
                        match = self.eligibility_analyzer.analyze_scheme_eligibility(farmer, scheme)
                        matches.append(match)
            
            elif isinstance(schemes, dict):
                # State-wise schemes or nested structure
                if category_name == 'state_schemes':
                    # Process state-specific schemes
                    farmer_state_key = farmer.state.lower().replace(' ', '_')
                    
                    # Check if farmer's state exists in schemes
                    if farmer_state_key in schemes:
                        state_schemes = schemes[farmer_state_key]
                        if isinstance(state_schemes, list):
                            for scheme in state_schemes:
                                if isinstance(scheme, dict):
                                    match = self.eligibility_analyzer.analyze_scheme_eligibility(farmer, scheme)
                                    matches.append(match)
                    else:
                        logger.debug(f"No specific schemes found for state: {farmer.state}")
                
                elif category_name == 'ut_schemes':
                    # Process UT schemes if farmer is in UT
                    farmer_ut_key = farmer.state.lower().replace(' ', '_')
                    if farmer_ut_key in schemes:
                        ut_schemes = schemes[farmer_ut_key]
                        if isinstance(ut_schemes, list):
                            for scheme in ut_schemes:
                                if isinstance(scheme, dict):
                                    match = self.eligibility_analyzer.analyze_scheme_eligibility(farmer, scheme)
                                    matches.append(match)
                
                else:
                    # Other nested categories
                    for subcategory_schemes in schemes.values():
                        if isinstance(subcategory_schemes, list):
                            for scheme in subcategory_schemes:
                                if isinstance(scheme, dict):
                                    match = self.eligibility_analyzer.analyze_scheme_eligibility(farmer, scheme)
                                    matches.append(match)
            
            logger.debug(f"Processed {len(matches)} schemes in category: {category_name}")
            
        except Exception as e:
            logger.error(f"Error processing category {category_name}: {e}")
        
        return matches
    
    def _save_results(self, results: Dict[str, Any], output_file: str):
        """Save analysis results to file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise SchemeMatcherError(f"Failed to save results: {e}")

def create_enhanced_matcher() -> EnhancedGovernmentSchemesMatcher:
    """Create enhanced government schemes matcher with default configuration"""
    return EnhancedGovernmentSchemesMatcher()

def main():
    """Example usage and testing"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        logger.info("Testing Enhanced Government Schemes Matcher v3.1 (FIXED)")
        
        # Create matcher
        matcher = create_enhanced_matcher()
        
        # Test with sample farmer data
        sample_farmer = {
            'farm_id': 'F001',
            'farmer_id': 'NBF_001',
            'farmer_name': 'Arun Kumar',
            'lat': 18.030504,
            'lon': 79.686037,
            'area_ha': 1.0,
            'village': 'Kundrakudi',
            'district': 'Karaikudi', 
            'state': 'Tamil Nadu',
            'crop': 'Rice',
            'age': 35,
            'category': 'General'
        }
        
        # Analyze eligibility
        report = matcher.analyze_farmer_eligibility(sample_farmer)
        
        logger.info("Analysis completed successfully")
        logger.info(f"Farmer: {report['farmer_profile']['name']}")
        logger.info(f"Eligible schemes: {report['eligibility_summary']['total_eligible_schemes']}")
        logger.info(f"High priority: {report['eligibility_summary']['high_priority_schemes']}")
        
        # Test CSV processing if file exists
        if os.path.exists('farms.csv'):
            csv_results = matcher.process_farms_csv('farms.csv', 'scheme_analysis_results.json')
            logger.info(f"CSV processing: {csv_results['successful_farms']}/{csv_results['total_farms']} successful")
    
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        raise

if __name__ == "__main__":
    main()