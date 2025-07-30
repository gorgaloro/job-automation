"""
White Collar Job Classifier
Identifies and categorizes white collar jobs for workforce analytics
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SeniorityLevel(Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"
    C_SUITE = "c_suite"


class EducationLevel(Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATES = "associates"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    PROFESSIONAL = "professional"  # JD, MD, etc.


class RemoteWorkOption(Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"


class MarketDemand(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class JobClassification:
    """Result of job classification analysis"""
    is_white_collar: bool
    confidence_score: float  # 0.0-1.0
    job_category: Optional[str] = None
    job_sector: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = None
    education_level: Optional[EducationLevel] = None
    
    # Keywords that led to classification
    classification_keywords: List[str] = field(default_factory=list)
    sector_keywords: List[str] = field(default_factory=list)
    skill_keywords: List[str] = field(default_factory=list)
    
    # Analytics fields
    experience_years_min: Optional[int] = None
    experience_years_max: Optional[int] = None
    remote_work_option: Optional[RemoteWorkOption] = None
    
    # Market indicators
    market_demand_indicator: Optional[MarketDemand] = None
    posting_frequency_score: Optional[float] = None


class WhiteCollarJobClassifier:
    """Service for classifying white collar jobs and extracting analytics data"""
    
    def __init__(self):
        # White collar job indicators
        self.white_collar_keywords = {
            # Job titles
            'manager', 'director', 'analyst', 'consultant', 'coordinator', 'specialist',
            'engineer', 'developer', 'architect', 'designer', 'researcher', 'scientist',
            'executive', 'officer', 'president', 'vice president', 'vp', 'ceo', 'cto', 'cfo',
            'administrator', 'supervisor', 'lead', 'principal', 'senior', 'staff',
            'product manager', 'project manager', 'program manager', 'account manager',
            'business analyst', 'data analyst', 'financial analyst', 'marketing analyst',
            
            # Professional roles
            'attorney', 'lawyer', 'counsel', 'paralegal', 'accountant', 'auditor',
            'consultant', 'advisor', 'strategist', 'planner', 'recruiter', 'hr',
            'sales', 'marketing', 'communications', 'public relations', 'pr',
            'operations', 'finance', 'accounting', 'legal', 'compliance',
            
            # Technical roles
            'software', 'hardware', 'systems', 'network', 'security', 'cloud',
            'data', 'analytics', 'machine learning', 'ai', 'artificial intelligence',
            'devops', 'sre', 'platform', 'infrastructure', 'database', 'web',
            'mobile', 'frontend', 'backend', 'fullstack', 'full stack',
            
            # Healthcare professional
            'physician', 'doctor', 'nurse practitioner', 'physician assistant',
            'pharmacist', 'therapist', 'psychologist', 'psychiatrist',
            
            # Education requirements indicators
            'bachelor', 'master', 'mba', 'phd', 'degree', 'university', 'college'
        }
        
        # Blue collar exclusion keywords
        self.blue_collar_keywords = {
            'driver', 'delivery', 'warehouse', 'factory', 'manufacturing', 'assembly',
            'construction', 'maintenance', 'repair', 'technician', 'mechanic',
            'janitor', 'cleaner', 'security guard', 'cashier', 'retail', 'server',
            'bartender', 'cook', 'chef', 'dishwasher', 'housekeeper', 'landscaper',
            'laborer', 'operator', 'forklift', 'crane', 'welder', 'electrician',
            'plumber', 'carpenter', 'painter', 'roofer', 'installer'
        }
        
        # Job categories and their keywords
        self.job_categories = {
            'Technology': {
                'software engineer', 'developer', 'programmer', 'architect', 'devops',
                'data scientist', 'machine learning', 'ai', 'cloud', 'security',
                'product manager', 'technical', 'platform', 'infrastructure',
                'frontend', 'backend', 'fullstack', 'mobile', 'web', 'database'
            },
            'Finance': {
                'financial', 'accounting', 'finance', 'investment', 'banking',
                'analyst', 'controller', 'treasurer', 'auditor', 'risk',
                'portfolio', 'trading', 'wealth', 'credit', 'loans'
            },
            'Healthcare': {
                'healthcare', 'medical', 'clinical', 'hospital', 'physician',
                'nurse', 'doctor', 'patient', 'health', 'pharmaceutical',
                'biotech', 'life sciences', 'medical device'
            },
            'Marketing': {
                'marketing', 'brand', 'advertising', 'digital marketing', 'seo',
                'content', 'social media', 'campaign', 'growth', 'acquisition',
                'communications', 'public relations', 'pr'
            },
            'Sales': {
                'sales', 'business development', 'account management', 'revenue',
                'customer success', 'relationship', 'partnership', 'enterprise'
            },
            'Operations': {
                'operations', 'supply chain', 'logistics', 'procurement',
                'vendor', 'process', 'efficiency', 'optimization'
            },
            'Human Resources': {
                'human resources', 'hr', 'recruiting', 'talent', 'people',
                'compensation', 'benefits', 'training', 'development'
            },
            'Legal': {
                'legal', 'attorney', 'lawyer', 'counsel', 'compliance',
                'regulatory', 'contracts', 'intellectual property', 'litigation'
            },
            'Consulting': {
                'consulting', 'consultant', 'advisory', 'strategy', 'transformation',
                'implementation', 'change management'
            },
            'Design': {
                'design', 'designer', 'ux', 'ui', 'user experience', 'user interface',
                'graphic', 'visual', 'creative', 'art director'
            }
        }
        
        # Job sectors
        self.job_sectors = {
            'Technology': {
                'software', 'saas', 'tech', 'startup', 'cloud', 'ai', 'fintech',
                'edtech', 'healthtech', 'cybersecurity', 'blockchain', 'crypto'
            },
            'Financial Services': {
                'bank', 'investment', 'insurance', 'financial services', 'asset management',
                'private equity', 'venture capital', 'hedge fund', 'credit union'
            },
            'Healthcare': {
                'healthcare', 'hospital', 'medical', 'pharmaceutical', 'biotech',
                'life sciences', 'medical device', 'health insurance'
            },
            'Consulting': {
                'consulting', 'professional services', 'advisory', 'management consulting',
                'strategy consulting', 'technology consulting'
            },
            'Media & Entertainment': {
                'media', 'entertainment', 'publishing', 'broadcasting', 'gaming',
                'streaming', 'content', 'digital media'
            },
            'Education': {
                'education', 'university', 'college', 'school', 'learning',
                'training', 'edtech', 'online education'
            },
            'Government': {
                'government', 'federal', 'state', 'local', 'public sector',
                'agency', 'department', 'municipal'
            },
            'Non-Profit': {
                'non-profit', 'nonprofit', 'foundation', 'charity', 'ngo',
                'social impact', 'community'
            }
        }
        
        # Northern California regions
        self.northern_california_regions = {
            'Bay Area': {
                'counties': ['San Francisco', 'San Mateo', 'Santa Clara', 'Alameda', 'Contra Costa', 'Marin', 'Napa', 'Solano', 'Sonoma'],
                'metro_areas': ['San Francisco-Oakland-Berkeley', 'San Jose-Sunnyvale-Santa Clara', 'Santa Rosa-Petaluma'],
                'cities': ['San Francisco', 'San Jose', 'Oakland', 'Fremont', 'Santa Clara', 'Sunnyvale', 'Hayward', 'Palo Alto', 'Mountain View', 'Redwood City']
            },
            'Sacramento Valley': {
                'counties': ['Sacramento', 'Yolo', 'Placer', 'El Dorado'],
                'metro_areas': ['Sacramento-Roseville-Folsom'],
                'cities': ['Sacramento', 'Roseville', 'Folsom', 'Davis', 'Woodland']
            },
            'Central Valley': {
                'counties': ['San Joaquin', 'Stanislaus', 'Merced', 'Fresno', 'Kings', 'Tulare', 'Kern'],
                'metro_areas': ['Stockton', 'Modesto', 'Fresno', 'Bakersfield'],
                'cities': ['Stockton', 'Modesto', 'Fresno', 'Bakersfield', 'Visalia']
            }
        }
        
        # Seniority indicators
        self.seniority_indicators = {
            SeniorityLevel.ENTRY: {'entry', 'junior', 'associate', 'coordinator', 'assistant', 'intern', 'new grad', 'recent graduate'},
            SeniorityLevel.MID: {'mid', 'intermediate', 'specialist', 'analyst', 'consultant'},
            SeniorityLevel.SENIOR: {'senior', 'sr', 'lead', 'principal', 'staff', 'expert'},
            SeniorityLevel.EXECUTIVE: {'director', 'vp', 'vice president', 'head of', 'chief'},
            SeniorityLevel.C_SUITE: {'ceo', 'cto', 'cfo', 'coo', 'cmo', 'chief executive', 'chief technology', 'chief financial', 'chief operating', 'chief marketing'}
        }
        
        # Education indicators
        self.education_indicators = {
            EducationLevel.HIGH_SCHOOL: {'high school', 'hs diploma', 'ged'},
            EducationLevel.ASSOCIATES: {'associates', 'aa', 'as', '2 year'},
            EducationLevel.BACHELORS: {'bachelor', 'ba', 'bs', 'undergraduate', '4 year'},
            EducationLevel.MASTERS: {'master', 'ma', 'ms', 'mba', 'graduate'},
            EducationLevel.PHD: {'phd', 'doctorate', 'doctoral', 'ph.d'},
            EducationLevel.PROFESSIONAL: {'jd', 'md', 'law degree', 'medical degree'}
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for keyword matching"""
        if not text:
            return ""
        return re.sub(r'[^\w\s]', ' ', text.lower()).strip()
    
    def extract_keywords(self, text: str, keyword_set: Set[str]) -> List[str]:
        """Extract matching keywords from text"""
        if not text:
            return []
        
        normalized_text = self.normalize_text(text)
        found_keywords = []
        
        for keyword in keyword_set:
            if keyword in normalized_text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def classify_white_collar(self, job_title: str, job_description: str) -> Tuple[bool, float, List[str]]:
        """Determine if job is white collar"""
        combined_text = f"{job_title} {job_description}"
        normalized_text = self.normalize_text(combined_text)
        
        # Find white collar indicators
        white_collar_matches = self.extract_keywords(combined_text, self.white_collar_keywords)
        
        # Find blue collar exclusions
        blue_collar_matches = self.extract_keywords(combined_text, self.blue_collar_keywords)
        
        # Calculate confidence score
        white_collar_score = len(white_collar_matches) * 0.1
        blue_collar_penalty = len(blue_collar_matches) * 0.2
        
        # Education requirement boost
        education_boost = 0.0
        if any(edu in normalized_text for edu in ['bachelor', 'master', 'mba', 'phd', 'degree']):
            education_boost = 0.3
        
        # Professional certification boost
        cert_boost = 0.0
        if any(cert in normalized_text for cert in ['certified', 'certification', 'license', 'cpa', 'pmp']):
            cert_boost = 0.2
        
        confidence = min(1.0, white_collar_score + education_boost + cert_boost - blue_collar_penalty)
        is_white_collar = confidence >= 0.5 and len(blue_collar_matches) == 0
        
        return is_white_collar, confidence, white_collar_matches
    
    def classify_job_category(self, job_title: str, job_description: str) -> Tuple[Optional[str], List[str]]:
        """Classify job into category"""
        combined_text = f"{job_title} {job_description}"
        
        category_scores = {}
        category_keywords = {}
        
        for category, keywords in self.job_categories.items():
            matches = self.extract_keywords(combined_text, keywords)
            category_keywords[category] = matches
            category_scores[category] = len(matches)
        
        if not category_scores or max(category_scores.values()) == 0:
            return None, []
        
        best_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        return best_category, category_keywords[best_category]
    
    def classify_job_sector(self, job_title: str, job_description: str, company_name: str = "") -> Tuple[Optional[str], List[str]]:
        """Classify job into sector"""
        combined_text = f"{job_title} {job_description} {company_name}"
        
        sector_scores = {}
        sector_keywords = {}
        
        for sector, keywords in self.job_sectors.items():
            matches = self.extract_keywords(combined_text, keywords)
            sector_keywords[sector] = matches
            sector_scores[sector] = len(matches)
        
        if not sector_scores or max(sector_scores.values()) == 0:
            return None, []
        
        best_sector = max(sector_scores.keys(), key=lambda k: sector_scores[k])
        return best_sector, sector_keywords[best_sector]
    
    def determine_seniority_level(self, job_title: str, job_description: str) -> Optional[SeniorityLevel]:
        """Determine seniority level from job content"""
        combined_text = f"{job_title} {job_description}"
        normalized_text = self.normalize_text(combined_text)
        
        # Check for seniority indicators in order of precedence
        for level, indicators in self.seniority_indicators.items():
            if any(indicator in normalized_text for indicator in indicators):
                return level
        
        # Default based on experience requirements
        if 'years' in normalized_text:
            years_match = re.search(r'(\d+)\+?\s*years?', normalized_text)
            if years_match:
                years = int(years_match.group(1))
                if years >= 10:
                    return SeniorityLevel.SENIOR
                elif years >= 5:
                    return SeniorityLevel.MID
                elif years >= 0:
                    return SeniorityLevel.ENTRY
        
        return None
    
    def determine_education_level(self, job_description: str) -> Optional[EducationLevel]:
        """Determine required education level"""
        normalized_text = self.normalize_text(job_description)
        
        # Check for education indicators in order of precedence (highest first)
        education_order = [
            EducationLevel.PHD,
            EducationLevel.PROFESSIONAL,
            EducationLevel.MASTERS,
            EducationLevel.BACHELORS,
            EducationLevel.ASSOCIATES,
            EducationLevel.HIGH_SCHOOL
        ]
        
        for level in education_order:
            indicators = self.education_indicators[level]
            if any(indicator in normalized_text for indicator in indicators):
                return level
        
        return None
    
    def extract_experience_years(self, job_description: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract minimum and maximum experience years"""
        if not job_description:
            return None, None
        
        normalized_text = self.normalize_text(job_description)
        
        # Pattern for "X-Y years" or "X to Y years"
        range_pattern = r'(\d+)\s*[-to]\s*(\d+)\s*years?'
        range_match = re.search(range_pattern, normalized_text)
        if range_match:
            return int(range_match.group(1)), int(range_match.group(2))
        
        # Pattern for "X+ years" or "minimum X years"
        min_pattern = r'(?:minimum|min|at least|(\d+)\+)\s*(\d+)?\s*years?'
        min_match = re.search(min_pattern, normalized_text)
        if min_match:
            years = int(min_match.group(1) or min_match.group(2))
            return years, None
        
        # Pattern for just "X years"
        single_pattern = r'(\d+)\s*years?'
        single_match = re.search(single_pattern, normalized_text)
        if single_match:
            years = int(single_match.group(1))
            return years, years
        
        return None, None
    
    def determine_remote_work_option(self, job_description: str, location: str = "") -> Optional[RemoteWorkOption]:
        """Determine remote work options"""
        combined_text = f"{job_description} {location}"
        normalized_text = self.normalize_text(combined_text)
        
        if any(term in normalized_text for term in ['remote', 'work from home', 'distributed', 'anywhere']):
            if any(term in normalized_text for term in ['hybrid', 'flexible', 'some onsite']):
                return RemoteWorkOption.HYBRID
            else:
                return RemoteWorkOption.REMOTE
        elif any(term in normalized_text for term in ['hybrid', 'flexible']):
            return RemoteWorkOption.HYBRID
        elif any(term in normalized_text for term in ['onsite', 'on-site', 'office', 'in person']):
            return RemoteWorkOption.ONSITE
        
        return None
    
    def classify_northern_california_region(self, location: str) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """Classify location within Northern California"""
        if not location:
            return None, None, None, False
        
        normalized_location = self.normalize_text(location)
        
        for region_name, region_data in self.northern_california_regions.items():
            # Check counties
            for county in region_data['counties']:
                if county.lower() in normalized_location:
                    return region_name, None, county, True
            
            # Check metro areas
            for metro in region_data['metro_areas']:
                if metro.lower() in normalized_location:
                    return region_name, metro, None, True
            
            # Check cities
            for city in region_data['cities']:
                if city.lower() in normalized_location:
                    return region_name, None, None, True
        
        # Check for general Northern California indicators
        if any(term in normalized_location for term in ['northern california', 'norcal', 'bay area', 'silicon valley']):
            return 'Northern California', None, None, True
        
        return None, None, None, False
    
    def extract_skill_keywords(self, job_description: str) -> List[str]:
        """Extract skill keywords from job description"""
        if not job_description:
            return []
        
        # Common skill patterns
        skill_patterns = [
            r'(?:experience with|proficient in|knowledge of|skilled in|familiar with)\s+([^.]+)',
            r'(?:required skills|must have|should have):\s*([^.]+)',
            r'(?:technologies|tools|platforms):\s*([^.]+)'
        ]
        
        skills = []
        normalized_text = self.normalize_text(job_description)
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, normalized_text, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters and clean
                skill_items = re.split(r'[,;/&]', match)
                for skill in skill_items:
                    clean_skill = skill.strip()
                    if len(clean_skill) > 2 and len(clean_skill) < 50:
                        skills.append(clean_skill)
        
        return skills[:20]  # Limit to top 20 skills
    
    def classify_job(self, job_title: str, job_description: str, location: str = "", 
                    company_name: str = "") -> JobClassification:
        """Perform comprehensive job classification"""
        
        # White collar classification
        is_white_collar, confidence, classification_keywords = self.classify_white_collar(job_title, job_description)
        
        # Category and sector
        job_category, category_keywords = self.classify_job_category(job_title, job_description)
        job_sector, sector_keywords = self.classify_job_sector(job_title, job_description, company_name)
        
        # Seniority and education
        seniority_level = self.determine_seniority_level(job_title, job_description)
        education_level = self.determine_education_level(job_description)
        
        # Experience and remote work
        exp_min, exp_max = self.extract_experience_years(job_description)
        remote_option = self.determine_remote_work_option(job_description, location)
        
        # Skills
        skill_keywords = self.extract_skill_keywords(job_description)
        
        return JobClassification(
            is_white_collar=is_white_collar,
            confidence_score=confidence,
            job_category=job_category,
            job_sector=job_sector,
            seniority_level=seniority_level,
            education_level=education_level,
            classification_keywords=classification_keywords,
            sector_keywords=sector_keywords,
            skill_keywords=skill_keywords,
            experience_years_min=exp_min,
            experience_years_max=exp_max,
            remote_work_option=remote_option
        )


# Utility functions for batch processing

def classify_jobs_batch(jobs: List[Dict[str, Any]]) -> List[JobClassification]:
    """Classify multiple jobs in batch"""
    classifier = WhiteCollarJobClassifier()
    results = []
    
    for job in jobs:
        classification = classifier.classify_job(
            job_title=job.get('title', ''),
            job_description=job.get('description', ''),
            location=job.get('location', ''),
            company_name=job.get('company_name', '')
        )
        results.append(classification)
    
    return results


def generate_white_collar_analytics_report(classifications: List[JobClassification]) -> Dict[str, Any]:
    """Generate analytics report from job classifications"""
    total_jobs = len(classifications)
    white_collar_jobs = [c for c in classifications if c.is_white_collar]
    
    # Category distribution
    category_dist = {}
    for classification in white_collar_jobs:
        if classification.job_category:
            category_dist[classification.job_category] = category_dist.get(classification.job_category, 0) + 1
    
    # Sector distribution
    sector_dist = {}
    for classification in white_collar_jobs:
        if classification.job_sector:
            sector_dist[classification.job_sector] = sector_dist.get(classification.job_sector, 0) + 1
    
    # Seniority distribution
    seniority_dist = {}
    for classification in white_collar_jobs:
        if classification.seniority_level:
            level = classification.seniority_level.value
            seniority_dist[level] = seniority_dist.get(level, 0) + 1
    
    return {
        'summary': {
            'total_jobs_analyzed': total_jobs,
            'white_collar_jobs': len(white_collar_jobs),
            'white_collar_percentage': len(white_collar_jobs) / total_jobs * 100 if total_jobs > 0 else 0,
            'avg_confidence_score': sum(c.confidence_score for c in white_collar_jobs) / len(white_collar_jobs) if white_collar_jobs else 0
        },
        'category_distribution': category_dist,
        'sector_distribution': sector_dist,
        'seniority_distribution': seniority_dist,
        'top_skills': [skill for c in white_collar_jobs for skill in c.skill_keywords][:50]
    }
