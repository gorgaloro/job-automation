"""
Personal Brand Profile System

Data models and core logic for personal brand profiling and career alignment.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class WorkPreferences:
    """Work style and environment preferences"""
    work_style: List[str]  # e.g., ["collaborative", "independent", "fast-paced"]
    leadership_style: List[str]  # e.g., ["servant-leader", "hands-on", "strategic"]
    team_size_preference: str  # e.g., "small", "medium", "large", "varies"
    remote_preference: str  # e.g., "remote", "hybrid", "in-person", "flexible"
    company_stage: List[str]  # e.g., ["startup", "growth", "enterprise"]
    company_size: List[str]  # e.g., ["<50", "50-200", "200-1000", ">1000"]

@dataclass
class CareerMotivators:
    """What drives and motivates the person professionally"""
    primary_motivators: List[str]  # e.g., ["impact", "learning", "autonomy", "compensation"]
    values: List[str]  # e.g., ["innovation", "work-life-balance", "diversity", "growth"]
    deal_breakers: List[str]  # e.g., ["micromanagement", "toxic culture", "no growth"]
    success_metrics: List[str]  # How they measure success

@dataclass
class IndustryPreferences:
    """Industry and domain preferences"""
    preferred_industries: List[str]  # e.g., ["fintech", "healthcare", "education"]
    avoided_industries: List[str]  # Industries to avoid
    domain_expertise: List[str]  # Areas of expertise
    emerging_interests: List[str]  # New areas of interest

@dataclass
class RolePreferences:
    """Preferred role types and responsibilities"""
    preferred_roles: List[str]  # e.g., ["Senior Engineer", "Tech Lead", "Product Manager"]
    role_responsibilities: List[str]  # Key responsibilities they enjoy
    growth_trajectory: str  # Career direction
    management_interest: str  # Interest in management roles

@dataclass
class PersonalBrandProfile:
    """Complete personal brand profile"""
    # Core identity
    brand_summary: str  # AI-generated summary of professional identity
    professional_identity: str  # How they see themselves professionally
    unique_value_proposition: str  # What makes them unique
    
    # Preferences and motivators
    work_preferences: WorkPreferences
    career_motivators: CareerMotivators
    industry_preferences: IndustryPreferences
    role_preferences: RolePreferences
    
    # Background context
    career_highlights: List[str]  # Key achievements and experiences
    skills_expertise: List[str]  # Core technical and soft skills
    education_background: List[str]  # Educational background
    
    # Metadata
    profile_version: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    confidence_score: Optional[float] = None  # AI confidence in profile accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalBrandProfile':
        """Create from dictionary"""
        # Convert ISO strings back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Reconstruct nested dataclasses
        data['work_preferences'] = WorkPreferences(**data['work_preferences'])
        data['career_motivators'] = CareerMotivators(**data['career_motivators'])
        data['industry_preferences'] = IndustryPreferences(**data['industry_preferences'])
        data['role_preferences'] = RolePreferences(**data['role_preferences'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def get_scoring_context(self) -> Dict[str, Any]:
        """Get context for job/company scoring"""
        return {
            "brand_summary": self.brand_summary,
            "professional_identity": self.professional_identity,
            "preferred_industries": self.industry_preferences.preferred_industries,
            "avoided_industries": self.industry_preferences.avoided_industries,
            "work_style": self.work_preferences.work_style,
            "company_stage": self.work_preferences.company_stage,
            "company_size": self.work_preferences.company_size,
            "primary_motivators": self.career_motivators.primary_motivators,
            "values": self.career_motivators.values,
            "deal_breakers": self.career_motivators.deal_breakers,
            "preferred_roles": self.role_preferences.preferred_roles,
            "remote_preference": self.work_preferences.remote_preference,
            "skills_expertise": self.skills_expertise
        }

@dataclass
class InterviewSession:
    """Represents a single AI interview session"""
    session_id: str
    user_id: Optional[str]
    transcript: str  # Full conversation transcript
    audio_file_path: Optional[str]  # Path to audio file if recorded
    session_duration: int  # Duration in seconds
    questions_asked: List[str]  # Questions that were asked
    key_insights: List[str]  # Key insights extracted
    generated_profile: Optional[PersonalBrandProfile]
    session_quality_score: float  # Quality of the session (0-1)
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        if self.generated_profile:
            data['generated_profile'] = self.generated_profile.to_dict()
        return data

@dataclass
class ProfileEvolution:
    """Tracks how a profile changes over time"""
    profile_id: str
    user_id: str
    version_history: List[Dict[str, Any]]  # Previous versions
    change_summary: List[str]  # What changed between versions
    evolution_triggers: List[str]  # What caused the changes
    created_at: datetime
    
    def add_version(self, profile: PersonalBrandProfile, trigger: str, changes: List[str]):
        """Add a new version to the history"""
        self.version_history.append(profile.to_dict())
        self.evolution_triggers.append(trigger)
        self.change_summary.extend(changes)

class PersonalBrandAnalyzer:
    """Analyzes and validates personal brand profiles"""
    
    @staticmethod
    def calculate_profile_completeness(profile: PersonalBrandProfile) -> float:
        """Calculate how complete a profile is (0-1)"""
        total_fields = 0
        filled_fields = 0
        
        # Check core identity fields
        core_fields = [
            profile.brand_summary,
            profile.professional_identity,
            profile.unique_value_proposition
        ]
        total_fields += len(core_fields)
        filled_fields += sum(1 for field in core_fields if field and field.strip())
        
        # Check preference lists
        preference_lists = [
            profile.work_preferences.work_style,
            profile.career_motivators.primary_motivators,
            profile.career_motivators.values,
            profile.industry_preferences.preferred_industries,
            profile.role_preferences.preferred_roles,
            profile.skills_expertise
        ]
        total_fields += len(preference_lists)
        filled_fields += sum(1 for lst in preference_lists if lst)
        
        # Check individual preference fields
        individual_fields = [
            profile.work_preferences.team_size_preference,
            profile.work_preferences.remote_preference,
            profile.role_preferences.growth_trajectory,
            profile.role_preferences.management_interest
        ]
        total_fields += len(individual_fields)
        filled_fields += sum(1 for field in individual_fields if field and field.strip())
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    @staticmethod
    def identify_profile_gaps(profile: PersonalBrandProfile) -> List[str]:
        """Identify missing or incomplete areas in the profile"""
        gaps = []
        
        if not profile.brand_summary or not profile.brand_summary.strip():
            gaps.append("Missing brand summary")
        
        if not profile.professional_identity or not profile.professional_identity.strip():
            gaps.append("Missing professional identity")
        
        if not profile.work_preferences.work_style:
            gaps.append("Missing work style preferences")
        
        if not profile.career_motivators.primary_motivators:
            gaps.append("Missing career motivators")
        
        if not profile.industry_preferences.preferred_industries:
            gaps.append("Missing industry preferences")
        
        if not profile.role_preferences.preferred_roles:
            gaps.append("Missing role preferences")
        
        if not profile.skills_expertise:
            gaps.append("Missing skills and expertise")
        
        if not profile.career_motivators.values:
            gaps.append("Missing core values")
        
        return gaps
    
    @staticmethod
    def suggest_profile_improvements(profile: PersonalBrandProfile) -> List[str]:
        """Suggest improvements to make the profile more effective"""
        suggestions = []
        
        # Check brand summary quality
        if profile.brand_summary and len(profile.brand_summary.split()) < 20:
            suggestions.append("Expand brand summary to be more descriptive")
        
        # Check for balance in preferences
        if len(profile.career_motivators.primary_motivators) > 5:
            suggestions.append("Consider narrowing down primary motivators to top 3-5")
        
        if len(profile.industry_preferences.preferred_industries) > 8:
            suggestions.append("Consider focusing on fewer industries for better targeting")
        
        # Check for deal breakers
        if not profile.career_motivators.deal_breakers:
            suggestions.append("Consider adding deal breakers to avoid mismatched opportunities")
        
        # Check for growth trajectory
        if not profile.role_preferences.growth_trajectory:
            suggestions.append("Define your career growth trajectory for better alignment")
        
        return suggestions
    
    @staticmethod
    def compare_profiles(profile1: PersonalBrandProfile, profile2: PersonalBrandProfile) -> Dict[str, Any]:
        """Compare two profiles and identify differences"""
        changes = {
            "brand_summary_changed": profile1.brand_summary != profile2.brand_summary,
            "motivators_changed": profile1.career_motivators.primary_motivators != profile2.career_motivators.primary_motivators,
            "industries_changed": profile1.industry_preferences.preferred_industries != profile2.industry_preferences.preferred_industries,
            "roles_changed": profile1.role_preferences.preferred_roles != profile2.role_preferences.preferred_roles,
            "work_style_changed": profile1.work_preferences.work_style != profile2.work_preferences.work_style,
            "values_changed": profile1.career_motivators.values != profile2.career_motivators.values
        }
        
        return {
            "changes": changes,
            "total_changes": sum(changes.values()),
            "change_percentage": sum(changes.values()) / len(changes) * 100
        }

def create_sample_profile() -> PersonalBrandProfile:
    """Create a sample profile for testing"""
    return PersonalBrandProfile(
        brand_summary="I'm a systems-builder who thrives in fast-moving startups, passionate about using technology to solve complex problems and build scalable solutions.",
        professional_identity="Senior Software Engineer with Product Mindset",
        unique_value_proposition="Combines deep technical expertise with business acumen to build products that users love and businesses need.",
        work_preferences=WorkPreferences(
            work_style=["collaborative", "fast-paced", "problem-solving"],
            leadership_style=["servant-leader", "hands-on", "mentoring"],
            team_size_preference="small-to-medium",
            remote_preference="hybrid",
            company_stage=["startup", "growth"],
            company_size=["50-200", "200-1000"]
        ),
        career_motivators=CareerMotivators(
            primary_motivators=["impact", "learning", "autonomy", "innovation"],
            values=["work-life-balance", "diversity", "transparency", "growth"],
            deal_breakers=["micromanagement", "toxic culture", "no learning opportunities"],
            success_metrics=["user impact", "team growth", "technical excellence", "business results"]
        ),
        industry_preferences=IndustryPreferences(
            preferred_industries=["fintech", "healthtech", "edtech", "developer-tools"],
            avoided_industries=["gambling", "tobacco", "weapons"],
            domain_expertise=["web development", "API design", "cloud architecture"],
            emerging_interests=["AI/ML", "blockchain", "sustainability-tech"]
        ),
        role_preferences=RolePreferences(
            preferred_roles=["Senior Software Engineer", "Tech Lead", "Staff Engineer"],
            role_responsibilities=["architecture", "mentoring", "product-development"],
            growth_trajectory="technical-leadership",
            management_interest="individual-contributor-with-mentoring"
        ),
        career_highlights=[
            "Led migration to microservices architecture serving 1M+ users",
            "Mentored 5 junior developers to senior level",
            "Built API platform used by 50+ internal teams"
        ],
        skills_expertise=[
            "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", 
            "System Design", "API Development", "Team Leadership"
        ],
        education_background=["BS Computer Science", "AWS Certified Solutions Architect"],
        profile_version="1.0",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        confidence_score=0.85
    )
