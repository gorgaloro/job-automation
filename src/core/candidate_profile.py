"""
Comprehensive Candidate Profile System

Structured format for candidate profiles that integrates resume data, AI career coaching results,
job targeting preferences, and other components to drive targeted job board API calls.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from enum import Enum
import json
import logging

from .personal_brand import PersonalBrandProfile
from .resume_optimizer import ResumeData

logger = logging.getLogger(__name__)

class ExperienceLevel(Enum):
    """Experience level categories"""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"

class SalaryRange(Enum):
    """Salary range categories"""
    UNDER_100K = "under_100k"
    RANGE_100_150K = "100k_150k"
    RANGE_150_200K = "150k_200k"
    RANGE_200_250K = "200k_250k"
    RANGE_250_300K = "250k_300k"
    OVER_300K = "over_300k"

@dataclass
class JobSearchCriteria:
    """Specific job search targeting criteria"""
    # Core targeting
    target_job_titles: List[str]  # Primary job titles to search for
    alternative_titles: List[str]  # Alternative/related titles
    excluded_titles: List[str]  # Titles to avoid
    
    # Experience and level
    experience_level: ExperienceLevel
    years_experience: int
    management_level: str  # "ic", "team_lead", "manager", "director", "vp"
    
    # Compensation
    salary_range: SalaryRange
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    equity_preference: str = "preferred"  # "required", "preferred", "not_important"
    
    # Location and work style
    preferred_locations: List[str]
    remote_preference: str  # "remote_only", "hybrid", "onsite", "flexible"
    willing_to_relocate: bool = False
    
    # Company preferences
    company_sizes: List[str]  # "startup", "small", "medium", "large", "enterprise"
    company_stages: List[str]  # "seed", "series_a", "series_b", "growth", "public"
    industries: List[str]
    excluded_industries: List[str] = field(default_factory=list)
    
    # Job characteristics
    role_types: List[str]  # "individual_contributor", "team_lead", "manager", "consultant"
    work_arrangements: List[str]  # "full_time", "contract", "part_time", "consulting"
    
    # Keywords for API searches
    required_keywords: List[str]  # Must have these keywords
    preferred_keywords: List[str]  # Nice to have keywords
    excluded_keywords: List[str]  # Exclude jobs with these keywords

@dataclass
class ResumeProfile:
    """Structured resume data for job matching"""
    # Basic info
    full_name: str
    location: str
    contact_info: Dict[str, str]  # email, phone, linkedin, etc.
    
    # Professional summary
    professional_summary: str
    years_total_experience: int
    
    # Skills and expertise
    core_skills: List[str]  # Top 10-15 core skills
    technical_skills: List[str]  # Technical/hard skills
    soft_skills: List[str]  # Leadership, communication, etc.
    certifications: List[str]
    
    # Experience
    current_role: Dict[str, Any]  # Current position details
    career_highlights: List[str]  # Key achievements
    industry_experience: List[str]  # Industries worked in
    
    # Education
    education: List[Dict[str, str]]
    
    # Keywords for matching
    resume_keywords: Set[str]  # All keywords extracted from resume
    
    # Metadata
    last_updated: datetime
    resume_versions: List[str] = field(default_factory=list)  # Different resume versions

@dataclass
class AICoachingResults:
    """Results from AI career coaching sessions"""
    # Session metadata
    session_id: str
    coaching_date: datetime
    session_duration_minutes: int
    
    # Career insights
    career_strengths: List[str]
    development_areas: List[str]
    career_goals: List[str]
    
    # Recommendations
    recommended_roles: List[str]
    recommended_industries: List[str]
    skill_development_plan: List[str]
    
    # Personality and work style
    work_style_assessment: Dict[str, Any]
    leadership_style: str
    communication_style: str
    
    # Job search strategy
    networking_recommendations: List[str]
    interview_preparation_areas: List[str]
    personal_brand_recommendations: List[str]
    
    # Confidence scores
    coaching_confidence: float  # AI confidence in recommendations
    profile_completeness: float  # How complete the assessment is

@dataclass
class JobBoardPreferences:
    """Preferences for job board searches"""
    # Preferred job boards
    primary_boards: List[str]  # ["greenhouse", "lever", "indeed", etc.]
    secondary_boards: List[str]
    excluded_boards: List[str] = field(default_factory=list)
    
    # Search frequency
    search_frequency: str = "daily"  # "hourly", "daily", "weekly"
    max_jobs_per_search: int = 50
    
    # Filtering preferences
    auto_apply_criteria: Dict[str, Any] = field(default_factory=dict)
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    # API rate limiting
    api_rate_limits: Dict[str, int] = field(default_factory=dict)

@dataclass
class CandidateProfile:
    """Comprehensive candidate profile for targeted job searching"""
    
    # Core identity
    profile_id: str
    candidate_name: str
    profile_version: str
    
    # Integrated components
    resume_profile: ResumeProfile
    personal_brand: PersonalBrandProfile
    job_search_criteria: JobSearchCriteria
    ai_coaching_results: Optional[AICoachingResults] = None
    job_board_preferences: JobBoardPreferences = field(default_factory=JobBoardPreferences)
    
    # Targeting data
    target_companies: List[str] = field(default_factory=list)  # Specific companies of interest
    company_blacklist: List[str] = field(default_factory=list)  # Companies to avoid
    
    # Job matching optimization
    keyword_weights: Dict[str, float] = field(default_factory=dict)  # Keyword importance weights
    matching_algorithm_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Activity tracking
    jobs_applied: List[str] = field(default_factory=list)  # Job IDs applied to
    jobs_saved: List[str] = field(default_factory=list)  # Saved job IDs
    jobs_rejected: List[str] = field(default_factory=list)  # Jobs marked as not interested
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_job_search: Optional[datetime] = None
    profile_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.last_job_search:
            data['last_job_search'] = self.last_job_search.isoformat()
        
        # Convert enums to values
        data['job_search_criteria']['experience_level'] = self.job_search_criteria.experience_level.value
        data['job_search_criteria']['salary_range'] = self.job_search_criteria.salary_range.value
        
        # Convert sets to lists for JSON serialization
        data['resume_profile']['resume_keywords'] = list(self.resume_profile.resume_keywords)
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandidateProfile':
        """Create from dictionary"""
        # Convert ISO strings back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('last_job_search'):
            data['last_job_search'] = datetime.fromisoformat(data['last_job_search'])
        
        # Convert enum values back to enums
        data['job_search_criteria']['experience_level'] = ExperienceLevel(data['job_search_criteria']['experience_level'])
        data['job_search_criteria']['salary_range'] = SalaryRange(data['job_search_criteria']['salary_range'])
        
        # Convert lists back to sets
        data['resume_profile']['resume_keywords'] = set(data['resume_profile']['resume_keywords'])
        
        # Reconstruct nested dataclasses
        data['resume_profile'] = ResumeProfile(**data['resume_profile'])
        data['job_search_criteria'] = JobSearchCriteria(**data['job_search_criteria'])
        data['job_board_preferences'] = JobBoardPreferences(**data['job_board_preferences'])
        
        if data.get('ai_coaching_results'):
            data['ai_coaching_results'] = AICoachingResults(**data['ai_coaching_results'])
        
        # Personal brand profile is handled separately
        data['personal_brand'] = PersonalBrandProfile.from_dict(data['personal_brand'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def get_job_search_query_params(self, job_board: str) -> Dict[str, Any]:
        """Generate job board API query parameters based on profile"""
        base_params = {
            "keywords": self.job_search_criteria.target_job_titles,
            "location": self.job_search_criteria.preferred_locations,
            "experience_level": self.job_search_criteria.experience_level.value,
            "salary_min": self.job_search_criteria.min_salary,
            "salary_max": self.job_search_criteria.max_salary,
            "remote": "remote" in self.job_search_criteria.remote_preference,
            "company_size": self.job_search_criteria.company_sizes,
            "industries": self.job_search_criteria.industries
        }
        
        # Job board specific customizations
        if job_board.lower() == "indeed":
            base_params.update({
                "q": " OR ".join(self.job_search_criteria.target_job_titles),
                "l": ", ".join(self.job_search_criteria.preferred_locations[:3]),
                "explvl": self._map_experience_to_indeed(),
                "salary": self._format_salary_for_indeed()
            })
        elif job_board.lower() == "greenhouse":
            base_params.update({
                "search": " ".join(self.job_search_criteria.target_job_titles),
                "location": self.job_search_criteria.preferred_locations[0] if self.job_search_criteria.preferred_locations else "",
                "department": self._map_role_to_department()
            })
        elif job_board.lower() in ["lever", "smartrecruiters", "workable"]:
            base_params.update({
                "query": " ".join(self.job_search_criteria.target_job_titles),
                "location": self.job_search_criteria.preferred_locations,
                "team": self._map_role_to_team()
            })
        
        return base_params
    
    def _map_experience_to_indeed(self) -> str:
        """Map experience level to Indeed's format"""
        mapping = {
            ExperienceLevel.ENTRY: "entry_level",
            ExperienceLevel.MID: "mid_level",
            ExperienceLevel.SENIOR: "senior_level",
            ExperienceLevel.STAFF: "senior_level",
            ExperienceLevel.PRINCIPAL: "senior_level",
            ExperienceLevel.DIRECTOR: "senior_level",
            ExperienceLevel.VP: "senior_level",
            ExperienceLevel.C_LEVEL: "senior_level"
        }
        return mapping.get(self.job_search_criteria.experience_level, "mid_level")
    
    def _format_salary_for_indeed(self) -> str:
        """Format salary range for Indeed"""
        if self.job_search_criteria.min_salary:
            return f"${self.job_search_criteria.min_salary}+"
        
        salary_mapping = {
            SalaryRange.UNDER_100K: "$80,000+",
            SalaryRange.RANGE_100_150K: "$100,000+",
            SalaryRange.RANGE_150_200K: "$150,000+",
            SalaryRange.RANGE_200_250K: "$200,000+",
            SalaryRange.RANGE_250_300K: "$250,000+",
            SalaryRange.OVER_300K: "$300,000+"
        }
        return salary_mapping.get(self.job_search_criteria.salary_range, "$100,000+")
    
    def _map_role_to_department(self) -> str:
        """Map role preferences to department categories"""
        role_dept_mapping = {
            "program manager": "Operations",
            "project manager": "Operations", 
            "revenue operations": "Sales",
            "customer experience": "Customer Success",
            "healthcare": "Operations",
            "technical": "Engineering"
        }
        
        for title in self.job_search_criteria.target_job_titles:
            for role_key, dept in role_dept_mapping.items():
                if role_key.lower() in title.lower():
                    return dept
        return "Operations"
    
    def _map_role_to_team(self) -> str:
        """Map role preferences to team categories"""
        for title in self.job_search_criteria.target_job_titles:
            if "engineering" in title.lower() or "technical" in title.lower():
                return "Engineering"
            elif "product" in title.lower():
                return "Product"
            elif "sales" in title.lower() or "revenue" in title.lower():
                return "Sales"
            elif "customer" in title.lower():
                return "Customer Success"
            elif "marketing" in title.lower():
                return "Marketing"
        return "Operations"
    
    def update_job_activity(self, job_id: str, action: str):
        """Update job activity tracking"""
        if action == "applied":
            if job_id not in self.jobs_applied:
                self.jobs_applied.append(job_id)
        elif action == "saved":
            if job_id not in self.jobs_saved:
                self.jobs_saved.append(job_id)
        elif action == "rejected":
            if job_id not in self.jobs_rejected:
                self.jobs_rejected.append(job_id)
        
        self.updated_at = datetime.now()
    
    def get_matching_score_weights(self) -> Dict[str, float]:
        """Get keyword weights for job matching algorithms"""
        if self.keyword_weights:
            return self.keyword_weights
        
        # Default weights based on profile
        weights = {}
        
        # Core skills get high weight
        for skill in self.resume_profile.core_skills:
            weights[skill.lower()] = 1.0
        
        # Target job titles get highest weight
        for title in self.job_search_criteria.target_job_titles:
            for word in title.split():
                weights[word.lower()] = 1.5
        
        # Industry experience gets medium weight
        for industry in self.resume_profile.industry_experience:
            weights[industry.lower()] = 0.8
        
        # Required keywords get high weight
        for keyword in self.job_search_criteria.required_keywords:
            weights[keyword.lower()] = 1.2
        
        return weights

class CandidateProfileBuilder:
    """Builder class for creating candidate profiles"""
    
    def __init__(self):
        self.profile_data = {}
    
    def from_resume_file(self, resume_path: str) -> 'CandidateProfileBuilder':
        """Build profile from resume file"""
        # This would parse the resume file and extract structured data
        # For now, we'll create a method stub
        pass
    
    def from_personal_brand(self, brand_profile: PersonalBrandProfile) -> 'CandidateProfileBuilder':
        """Add personal brand profile"""
        self.profile_data['personal_brand'] = brand_profile
        return self
    
    def with_job_criteria(self, criteria: JobSearchCriteria) -> 'CandidateProfileBuilder':
        """Add job search criteria"""
        self.profile_data['job_search_criteria'] = criteria
        return self
    
    def with_ai_coaching(self, coaching_results: AICoachingResults) -> 'CandidateProfileBuilder':
        """Add AI coaching results"""
        self.profile_data['ai_coaching_results'] = coaching_results
        return self
    
    def build(self) -> CandidateProfile:
        """Build the complete candidate profile"""
        # Validate required fields and build profile
        # Implementation would ensure all required fields are present
        pass

def create_allen_walker_profile() -> CandidateProfile:
    """Create Allen Walker's candidate profile based on his resume"""
    
    # Resume profile from his resume data
    resume_profile = ResumeProfile(
        full_name="Allen Walker",
        location="San Francisco, CA",
        contact_info={
            "linkedin": "linkedin.com/in/allenwalker",
            "location": "San Francisco, CA"
        },
        professional_summary="Senior program leader and operations strategist with 15+ years transforming industries including healthcare, construction, property management, pharma, and community development. I drive change through systems thinking, infrastructure buildout, IT delivery, and hands-on execution across complex projects.",
        years_total_experience=15,
        core_skills=[
            "Program Management", "Revenue Operations", "GTM Strategy", 
            "Change Management", "Customer Success", "CX Ops",
            "Salesforce", "HubSpot", "Epic Systems", "Cross-functional Delivery"
        ],
        technical_skills=[
            "Salesforce", "HubSpot", "Epic (Resolute PB/HB)", "SAP", "Yardi",
            "SQL", "PostgreSQL", "Supabase", "VBA", "Python", "R",
            "MS Project", "Asana", "Jira", "Confluence"
        ],
        soft_skills=[
            "Leadership", "Cross-functional Collaboration", "Change Management",
            "Strategic Thinking", "Problem Solving", "Communication"
        ],
        certifications=[],
        current_role={
            "title": "Senior Program Manager",
            "company": "Healthcare/Tech",
            "duration": "Current"
        },
        career_highlights=[
            "Directed a $6B Epic program for 35,000+ users",
            "Managed an IT portfolio serving 100K+ users", 
            "Led RevOps and delivery for Fortune 100 clients"
        ],
        industry_experience=[
            "Healthcare", "SaaS", "AI", "EV Infrastructure", 
            "Pharma", "Real Estate", "Construction", "Property Management"
        ],
        education=[
            {"degree": "Bachelor's", "field": "Business/Technology", "school": "University"}
        ],
        resume_keywords={
            "program", "management", "revenue", "operations", "epic", "salesforce",
            "healthcare", "technology", "implementation", "delivery", "strategy",
            "change", "customer", "experience", "cross-functional", "leadership"
        },
        last_updated=datetime.now(),
        resume_versions=["general", "healthcare_focused", "tech_focused"]
    )
    
    # Job search criteria based on Allen's background
    job_search_criteria = JobSearchCriteria(
        target_job_titles=[
            "Senior Program Manager",
            "Revenue Operations Manager",
            "Customer Experience Manager", 
            "Technical Project Manager",
            "Healthcare IT Manager",
            "Business Operations Manager",
            "Implementation Manager",
            "Strategic Program Manager"
        ],
        alternative_titles=[
            "Program Director", "Operations Director", "Delivery Manager",
            "Customer Success Manager", "RevOps Manager"
        ],
        excluded_titles=[
            "Junior", "Associate", "Intern", "Entry Level"
        ],
        experience_level=ExperienceLevel.SENIOR,
        years_experience=15,
        management_level="manager",
        salary_range=SalaryRange.RANGE_150_200K,
        min_salary=150000,
        max_salary=250000,
        equity_preference="preferred",
        preferred_locations=[
            "San Francisco, CA", "Bay Area, CA", "Remote", "California"
        ],
        remote_preference="hybrid",
        willing_to_relocate=False,
        company_sizes=["medium", "large", "enterprise"],
        company_stages=["growth", "public"],
        industries=[
            "Healthcare", "Technology", "SaaS", "Fintech", 
            "Real Estate", "Automotive", "AI/ML"
        ],
        excluded_industries=["Gambling", "Tobacco", "Weapons"],
        role_types=["manager", "individual_contributor"],
        work_arrangements=["full_time"],
        required_keywords=[
            "program management", "revenue operations", "customer experience",
            "epic", "salesforce", "healthcare", "implementation"
        ],
        preferred_keywords=[
            "cross-functional", "strategy", "change management", 
            "delivery", "operations", "technology"
        ],
        excluded_keywords=["junior", "entry", "intern", "associate"]
    )
    
    # Job board preferences
    job_board_preferences = JobBoardPreferences(
        primary_boards=["greenhouse", "lever", "indeed", "smartrecruiters"],
        secondary_boards=["workable", "github", "angellist"],
        search_frequency="daily",
        max_jobs_per_search=25,
        auto_apply_criteria={
            "min_match_score": 85,
            "required_keywords_present": True,
            "salary_in_range": True
        },
        notification_preferences={
            "new_matches": True,
            "high_priority_matches": True,
            "daily_digest": True
        }
    )
    
    # Create the complete profile
    profile = CandidateProfile(
        profile_id="allen_walker_001",
        candidate_name="Allen Walker",
        profile_version="1.0",
        resume_profile=resume_profile,
        personal_brand=PersonalBrandProfile.from_dict({
            "brand_summary": "Senior program leader driving transformation in healthcare and technology",
            "professional_identity": "Strategic Program Manager with Healthcare Technology Expertise",
            "unique_value_proposition": "Combines deep healthcare domain knowledge with technology delivery expertise to drive large-scale transformational programs",
            "work_preferences": {
                "work_style": ["collaborative", "strategic", "hands-on"],
                "leadership_style": ["servant-leader", "cross-functional", "results-driven"],
                "team_size_preference": "medium-to-large",
                "remote_preference": "hybrid",
                "company_stage": ["growth", "enterprise"],
                "company_size": ["200-1000", ">1000"]
            },
            "career_motivators": {
                "primary_motivators": ["impact", "transformation", "leadership", "innovation"],
                "values": ["healthcare improvement", "technology advancement", "team development"],
                "deal_breakers": ["micromanagement", "lack of strategic focus", "poor work-life balance"],
                "success_metrics": ["program delivery", "team growth", "business impact", "user adoption"]
            },
            "industry_preferences": {
                "preferred_industries": ["healthcare", "technology", "saas", "fintech"],
                "avoided_industries": ["gambling", "tobacco"],
                "domain_expertise": ["healthcare IT", "revenue operations", "program management"],
                "emerging_interests": ["AI/ML", "digital health", "automation"]
            },
            "role_preferences": {
                "preferred_roles": ["Senior Program Manager", "Revenue Operations Manager", "Healthcare IT Manager"],
                "role_responsibilities": ["strategic planning", "cross-functional leadership", "system implementation"],
                "growth_trajectory": "senior-leadership",
                "management_interest": "people-and-program-management"
            },
            "career_highlights": [
                "Led $6B Epic implementation for 35,000+ users",
                "Managed IT portfolio serving 100K+ users",
                "Delivered Fortune 100 client programs"
            ],
            "skills_expertise": [
                "Program Management", "Revenue Operations", "Epic Systems",
                "Salesforce", "Healthcare Technology", "Change Management"
            ],
            "education_background": ["Bachelor's Degree", "Healthcare IT Certifications"],
            "profile_version": "1.0",
            "created_at": "2025-07-25T15:00:00",
            "updated_at": "2025-07-25T15:00:00",
            "confidence_score": 0.9
        }),
        job_search_criteria=job_search_criteria,
        job_board_preferences=job_board_preferences,
        target_companies=[
            "Epic Systems", "Salesforce", "HubSpot", "Kaiser Permanente",
            "UCSF Health", "Sutter Health", "Tesla", "Ford", "Stripe"
        ],
        company_blacklist=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        profile_active=True
    )
    
    return profile
