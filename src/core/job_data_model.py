"""
Comprehensive Job Data Model
Supports ATS API compatibility and AI-powered job analysis
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
import uuid


class EmploymentType(Enum):
    """Employment type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class LocationType(Enum):
    """Location type enumeration"""
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"


class JobLevel(Enum):
    """Job seniority level enumeration"""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    EXECUTIVE = "executive"


class JobStatus(Enum):
    """Job posting status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"
    ARCHIVED = "archived"
    PAUSED = "paused"


class VisaSponsorshipStatus(Enum):
    """Visa sponsorship availability"""
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    CASE_BY_CASE = "case_by_case"


class PayFrequency(Enum):
    """Pay frequency enumeration"""
    ANNUAL = "annual"
    HOURLY = "hourly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    PROJECT = "project"


@dataclass
class SalaryRange:
    """Salary range information"""
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "USD"
    pay_frequency: PayFrequency = PayFrequency.ANNUAL
    bonus_info: Optional[str] = None
    equity_info: Optional[str] = None
    commission_info: Optional[str] = None


@dataclass
class JobLocation:
    """Job location information"""
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    location_type: LocationType = LocationType.ON_SITE
    workplace_policy: Optional[str] = None
    remote_locations: List[str] = field(default_factory=list)
    is_remote_friendly: bool = False


@dataclass
class JobRequirements:
    """Job requirements and qualifications"""
    qualifications_required: List[str] = field(default_factory=list)
    qualifications_preferred: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    skills_preferred: List[str] = field(default_factory=list)
    education_required: Optional[str] = None
    experience_required: Optional[str] = None
    certifications_required: List[str] = field(default_factory=list)
    certifications_preferred: List[str] = field(default_factory=list)
    languages_required: List[str] = field(default_factory=list)
    travel_requirement: Optional[str] = None
    security_clearance: Optional[str] = None


@dataclass
class JobBenefits:
    """Job benefits and perks"""
    health_insurance: bool = False
    dental_insurance: bool = False
    vision_insurance: bool = False
    retirement_401k: bool = False
    paid_time_off: Optional[str] = None
    flexible_schedule: bool = False
    remote_work: bool = False
    professional_development: bool = False
    gym_membership: bool = False
    free_meals: bool = False
    stock_options: bool = False
    other_benefits: List[str] = field(default_factory=list)


@dataclass
class AIEnrichmentData:
    """AI-processed job analysis data"""
    keywords: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    industry_tags: List[str] = field(default_factory=list)
    role_category: Optional[str] = None
    seniority_score: Optional[float] = None
    complexity_score: Optional[float] = None
    growth_potential_score: Optional[float] = None
    culture_keywords: List[str] = field(default_factory=list)
    company_stage: Optional[str] = None  # startup, growth, enterprise
    team_size_estimate: Optional[str] = None
    management_scope: Optional[str] = None
    technical_depth: Optional[str] = None
    business_impact: Optional[str] = None


@dataclass
class JobStatusTracking:
    """Job posting status and lifecycle tracking"""
    # Current status
    is_active: bool = True
    last_verified_active: Optional[datetime] = None
    
    # Closure tracking
    closed_date: Optional[datetime] = None
    closure_reason: Optional[str] = None  # expired, filled, cancelled, company_decision
    closure_detection_method: Optional[str] = None  # automated_check, manual_update, ats_api
    
    # Verification tracking
    verification_attempts: int = 0
    last_verification_attempt: Optional[datetime] = None
    verification_failures: int = 0
    last_verification_error: Optional[str] = None
    
    # Posting duration metrics
    posting_duration_days: Optional[int] = None
    estimated_fill_time: Optional[int] = None
    
    # Status change history
    status_changes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ApplicationTracking:
    """Application tracking metadata"""
    application_url: Optional[str] = None
    application_instructions: Optional[str] = None
    contact_email: Optional[str] = None
    recruiter_name: Optional[str] = None
    hiring_manager: Optional[str] = None
    application_deadline: Optional[datetime] = None
    expected_response_time: Optional[str] = None
    interview_process: List[str] = field(default_factory=list)


@dataclass
class JobSource:
    """Job posting source information for multi-source tracking"""
    source_type: str  # primary, secondary
    source_name: str  # company_website, linkedin, indeed, glassdoor
    source_url: str
    discovered_date: datetime = field(default_factory=datetime.now)
    last_verified: Optional[datetime] = None
    is_active: bool = True
    
    # Content comparison for delta analysis
    content_hash: Optional[str] = None
    content_differences: List[str] = field(default_factory=list)
    last_content_check: Optional[datetime] = None


@dataclass
class RepostDetection:
    """Job repost detection and clustering data"""
    # Repost identification
    is_repost: bool = False
    original_job_id: Optional[str] = None
    repost_cluster_id: Optional[str] = None
    repost_sequence_number: int = 1
    
    # Similarity metrics
    title_similarity_score: Optional[float] = None
    description_similarity_score: Optional[float] = None
    requirements_similarity_score: Optional[float] = None
    overall_similarity_score: Optional[float] = None
    
    # Repost timing analysis
    days_since_original: Optional[int] = None
    days_since_last_repost: Optional[int] = None
    repost_frequency_score: Optional[float] = None
    
    # Company repost patterns
    company_repost_count: int = 0
    company_repost_frequency: Optional[float] = None
    company_quality_flag: Optional[str] = None  # green, yellow, red


@dataclass
class WhiteCollarClassification:
    """White collar job classification and categorization"""
    # Primary classification
    is_white_collar: bool = False
    confidence_score: float = 0.0
    classification_method: str = "keyword_based"  # keyword_based, ml_model, manual
    
    # Job categorization
    job_category: Optional[str] = None  # technology, healthcare, finance, etc.
    job_subcategory: Optional[str] = None  # software_engineering, data_science, etc.
    industry_sector: Optional[str] = None  # tech, healthcare, financial_services
    occupation_code: Optional[str] = None  # SOC code if available
    
    # Skills and requirements analysis
    key_skills: List[str] = field(default_factory=list)
    education_level: Optional[str] = None  # bachelors, masters, phd, none_required
    experience_level: Optional[str] = None  # entry, mid, senior, executive
    
    # Classification keywords that triggered white collar flag
    classification_keywords: List[str] = field(default_factory=list)
    exclusion_keywords: List[str] = field(default_factory=list)
    
    # Geographic and demographic context
    regional_demand_score: Optional[float] = None
    salary_percentile: Optional[float] = None


@dataclass
class GeographicData:
    """Geographic filtering and regional analysis data"""
    # Regional classification
    is_northern_california: bool = False
    region: Optional[str] = None  # bay_area, sacramento_valley, north_coast
    subregion: Optional[str] = None  # san_francisco, silicon_valley, east_bay
    
    # Location analysis
    metro_area: Optional[str] = None
    county: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Commute and accessibility
    transit_accessible: bool = False
    major_transit_lines: List[str] = field(default_factory=list)
    commute_score: Optional[float] = None
    
    # Regional market data
    regional_job_density: Optional[float] = None
    regional_salary_index: Optional[float] = None
    cost_of_living_index: Optional[float] = None


@dataclass
class JobAnalytics:
    """Job posting analytics and performance metrics"""
    # Posting performance
    view_count: int = 0
    application_count: int = 0
    click_through_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    
    # Time-based metrics
    time_to_fill: Optional[int] = None  # days
    posting_duration: Optional[int] = None  # days
    reposting_frequency: Optional[float] = None
    
    # Quality indicators
    description_quality_score: Optional[float] = None
    requirements_clarity_score: Optional[float] = None
    salary_competitiveness_score: Optional[float] = None
    
    # Market positioning
    similar_jobs_count: int = 0
    market_saturation_score: Optional[float] = None
    uniqueness_score: Optional[float] = None
    
    # Engagement metrics
    social_shares: int = 0
    bookmark_count: int = 0
    referral_count: int = 0


@dataclass
class Job:
    """Comprehensive job data structure with ATS compatibility"""
    
    # Core Identifiers
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_job_id: Optional[str] = None
    requisition_id: Optional[str] = None
    slug: Optional[str] = None
    
    # Basic Job Information
    title: str = ""
    description: str = ""
    summary: Optional[str] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    department: Optional[str] = None
    job_function: Optional[str] = None
    job_level: JobLevel = JobLevel.MID
    
    # Company Information
    company_id: Optional[str] = None
    company_name: str = ""
    office_id: Optional[str] = None
    
    # Location and Work Arrangement
    location: JobLocation = field(default_factory=JobLocation)
    
    # Compensation
    salary: SalaryRange = field(default_factory=SalaryRange)
    
    # Requirements and Qualifications
    requirements: JobRequirements = field(default_factory=JobRequirements)
    
    # Benefits and Perks
    benefits: JobBenefits = field(default_factory=JobBenefits)
    
    # Visa and Relocation
    visa_sponsorship: VisaSponsorshipStatus = VisaSponsorshipStatus.NOT_AVAILABLE
    relocation_assistance: bool = False
    
    # Posting Information
    status: JobStatus = JobStatus.OPEN
    posted_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    job_board_source: Optional[str] = None
    language: str = "en"
    is_internal: bool = False
    
    # Application Information
    application_tracking: ApplicationTracking = field(default_factory=ApplicationTracking)
    
    # Job Status Monitoring
    status_tracking: JobStatusTracking = field(default_factory=JobStatusTracking)
    
    # AI Enhancement Data
    ai_enrichment: AIEnrichmentData = field(default_factory=AIEnrichmentData)
    
    # Multi-Source Tracking
    sources: List[JobSource] = field(default_factory=list)
    primary_source: Optional[JobSource] = None
    
    # Repost Detection
    repost_detection: RepostDetection = field(default_factory=RepostDetection)
    
    # White Collar Classification
    white_collar_classification: WhiteCollarClassification = field(default_factory=WhiteCollarClassification)
    
    # Geographic Data
    geographic_data: GeographicData = field(default_factory=GeographicData)
    
    # Analytics and Performance
    analytics: JobAnalytics = field(default_factory=JobAnalytics)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.slug and self.title:
            self.slug = self._generate_slug(self.title)
        
        if not self.posted_date:
            self.posted_date = datetime.now()
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-safe slug from job title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for API responses"""
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company_name': self.company_name,
            'description': self.description,
            'summary': self.summary,
            'employment_type': self.employment_type.value,
            'location': {
                'city': self.location.city,
                'state': self.location.state,
                'country': self.location.country,
                'location_type': self.location.location_type.value,
                'is_remote_friendly': self.location.is_remote_friendly
            },
            'salary': {
                'min_salary': self.salary.min_salary,
                'max_salary': self.salary.max_salary,
                'currency': self.salary.currency,
                'pay_frequency': self.salary.pay_frequency.value
            },
            'requirements': {
                'skills_required': self.requirements.skills_required,
                'skills_preferred': self.requirements.skills_preferred,
                'experience_required': self.requirements.experience_required,
                'education_required': self.requirements.education_required
            },
            'ai_enrichment': {
                'keywords': self.ai_enrichment.keywords,
                'tech_stack': self.ai_enrichment.tech_stack,
                'industry_tags': self.ai_enrichment.industry_tags,
                'seniority_score': self.ai_enrichment.seniority_score
            },
            'application_url': self.application_tracking.application_url,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'status': self.status.value
        }
    
    def get_match_keywords(self) -> List[str]:
        """Get all keywords for matching algorithms"""
        keywords = []
        keywords.extend(self.requirements.skills_required)
        keywords.extend(self.requirements.skills_preferred)
        keywords.extend(self.ai_enrichment.keywords)
        keywords.extend(self.ai_enrichment.tech_stack)
        keywords.extend(self.tags)
        return list(set(keywords))  # Remove duplicates
    
    def is_remote_eligible(self) -> bool:
        """Check if job supports remote work"""
        return (
            self.location.location_type in [LocationType.REMOTE, LocationType.HYBRID] or
            self.location.is_remote_friendly
        )
    
    def get_salary_display(self) -> str:
        """Get formatted salary range for display"""
        if not self.salary.min_salary and not self.salary.max_salary:
            return "Salary not specified"
        
        currency_symbol = "$" if self.salary.currency == "USD" else self.salary.currency
        
        if self.salary.min_salary and self.salary.max_salary:
            return f"{currency_symbol}{self.salary.min_salary:,.0f} - {currency_symbol}{self.salary.max_salary:,.0f}"
        elif self.salary.min_salary:
            return f"{currency_symbol}{self.salary.min_salary:,.0f}+"
        elif self.salary.max_salary:
            return f"Up to {currency_symbol}{self.salary.max_salary:,.0f}"
        
        return "Competitive salary"
    
    def update_ai_enrichment(self, enrichment_data: Dict[str, Any]):
        """Update AI enrichment data"""
        for key, value in enrichment_data.items():
            if hasattr(self.ai_enrichment, key):
                setattr(self.ai_enrichment, key, value)
        self.updated_at = datetime.now()
    
    def mark_as_closed(self, closure_reason: str, detection_method: str = "manual_update"):
        """Mark job as closed and calculate posting duration"""
        self.status = JobStatus.CLOSED
        self.status_tracking.is_active = False
        self.status_tracking.closed_date = datetime.now()
        self.status_tracking.closure_reason = closure_reason
        self.status_tracking.closure_detection_method = detection_method
        
        # Calculate posting duration
        if self.posted_date:
            duration = (self.status_tracking.closed_date - self.posted_date).days
            self.status_tracking.posting_duration_days = duration
        
        # Add to status change history
        self.status_tracking.status_changes.append({
            'timestamp': datetime.now().isoformat(),
            'old_status': 'open',
            'new_status': 'closed',
            'reason': closure_reason,
            'method': detection_method
        })
        
        self.updated_at = datetime.now()
    
    def add_source(self, source_type: str, source_name: str, source_url: str, is_primary: bool = False):
        """Add a job posting source for multi-source tracking"""
        source = JobSource(
            source_type=source_type,
            source_name=source_name,
            source_url=source_url
        )
        
        self.sources.append(source)
        
        if is_primary or not self.primary_source:
            self.primary_source = source
        
        self.updated_at = datetime.now()
    
    def mark_as_repost(self, original_job_id: str, similarity_scores: Dict[str, float], cluster_id: str = None):
        """Mark job as a repost of another job"""
        self.repost_detection.is_repost = True
        self.repost_detection.original_job_id = original_job_id
        self.repost_detection.repost_cluster_id = cluster_id or f"cluster_{original_job_id}"
        
        # Set similarity scores
        self.repost_detection.title_similarity_score = similarity_scores.get('title', 0.0)
        self.repost_detection.description_similarity_score = similarity_scores.get('description', 0.0)
        self.repost_detection.requirements_similarity_score = similarity_scores.get('requirements', 0.0)
        
        # Calculate overall similarity
        scores = [s for s in similarity_scores.values() if s is not None]
        self.repost_detection.overall_similarity_score = sum(scores) / len(scores) if scores else 0.0
        
        self.updated_at = datetime.now()
    
    def classify_white_collar(self, is_white_collar: bool, confidence: float, 
                             category: str = None, keywords: List[str] = None):
        """Classify job as white collar with supporting data"""
        self.white_collar_classification.is_white_collar = is_white_collar
        self.white_collar_classification.confidence_score = confidence
        
        if category:
            self.white_collar_classification.job_category = category
        
        if keywords:
            self.white_collar_classification.classification_keywords = keywords
        
        self.updated_at = datetime.now()
    
    def set_geographic_data(self, is_northern_ca: bool, region: str = None, 
                           zip_code: str = None, transit_accessible: bool = False):
        """Set geographic classification and regional data"""
        self.geographic_data.is_northern_california = is_northern_ca
        self.geographic_data.region = region
        self.geographic_data.zip_code = zip_code
        self.geographic_data.transit_accessible = transit_accessible
        
        # Extract zip code from location if not provided
        if not zip_code and self.location.postal_code:
            self.geographic_data.zip_code = self.location.postal_code
        
        self.updated_at = datetime.now()
    
    def update_analytics(self, **metrics):
        """Update job analytics with new metrics"""
        for key, value in metrics.items():
            if hasattr(self.analytics, key):
                setattr(self.analytics, key, value)
        
        self.updated_at = datetime.now()
    
    def get_repost_risk_score(self) -> float:
        """Calculate repost risk score based on company patterns"""
        if not self.repost_detection.company_repost_frequency:
            return 0.0
        
        # Higher frequency = higher risk
        frequency_score = min(self.repost_detection.company_repost_frequency / 10.0, 1.0)
        
        # Factor in repost count
        count_score = min(self.repost_detection.company_repost_count / 20.0, 1.0)
        
        return (frequency_score + count_score) / 2.0
    
    def is_quality_company(self) -> bool:
        """Determine if company has good hiring practices based on repost patterns"""
        quality_flag = self.repost_detection.company_quality_flag
        return quality_flag == 'green' or (quality_flag is None and self.get_repost_risk_score() < 0.3)
    
    def get_market_competitiveness_score(self) -> float:
        """Calculate how competitive this job is in the market"""
        scores = []
        
        # Salary competitiveness
        if self.analytics.salary_competitiveness_score:
            scores.append(self.analytics.salary_competitiveness_score)
        
        # Market saturation (inverse)
        if self.analytics.market_saturation_score:
            scores.append(1.0 - self.analytics.market_saturation_score)
        
        # Uniqueness
        if self.analytics.uniqueness_score:
            scores.append(self.analytics.uniqueness_score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def to_dict_extended(self) -> Dict[str, Any]:
        """Extended dictionary representation with all new fields"""
        base_dict = self.to_dict()
        
        # Add new data structures
        base_dict.update({
            'sources': [{
                'source_type': s.source_type,
                'source_name': s.source_name,
                'source_url': s.source_url,
                'discovered_date': s.discovered_date.isoformat(),
                'is_active': s.is_active
            } for s in self.sources],
            'primary_source': {
                'source_type': self.primary_source.source_type,
                'source_name': self.primary_source.source_name,
                'source_url': self.primary_source.source_url
            } if self.primary_source else None,
            'repost_detection': {
                'is_repost': self.repost_detection.is_repost,
                'original_job_id': self.repost_detection.original_job_id,
                'overall_similarity_score': self.repost_detection.overall_similarity_score,
                'company_quality_flag': self.repost_detection.company_quality_flag
            },
            'white_collar_classification': {
                'is_white_collar': self.white_collar_classification.is_white_collar,
                'confidence_score': self.white_collar_classification.confidence_score,
                'job_category': self.white_collar_classification.job_category,
                'classification_keywords': self.white_collar_classification.classification_keywords
            },
            'geographic_data': {
                'is_northern_california': self.geographic_data.is_northern_california,
                'region': self.geographic_data.region,
                'zip_code': self.geographic_data.zip_code,
                'transit_accessible': self.geographic_data.transit_accessible
            },
            'analytics': {
                'view_count': self.analytics.view_count,
                'application_count': self.analytics.application_count,
                'time_to_fill': self.analytics.time_to_fill,
                'posting_duration': self.analytics.posting_duration,
                'market_competitiveness_score': self.get_market_competitiveness_score()
            },
            'quality_indicators': {
                'repost_risk_score': self.get_repost_risk_score(),
                'is_quality_company': self.is_quality_company()
            }
        })
        
        return base_dict
    
    def record_verification_attempt(self, success: bool, error_message: str = None):
        """Record job verification attempt"""
        self.status_tracking.verification_attempts += 1
        self.status_tracking.last_verification_attempt = datetime.now()
        
        if success:
            self.status_tracking.last_verified_active = datetime.now()
            self.status_tracking.verification_failures = 0  # Reset failure count
        else:
            self.status_tracking.verification_failures += 1
            if error_message:
                self.status_tracking.last_verification_error = error_message
        
        self.updated_at = datetime.now()
    
    def is_verification_needed(self, max_age_days: int = 7) -> bool:
        """Check if job needs verification based on last check date"""
        if not self.status_tracking.is_active:
            return False  # Don't verify closed jobs
        
        if not self.status_tracking.last_verified_active:
            return True  # Never verified
        
        days_since_verification = (datetime.now() - self.status_tracking.last_verified_active).days
        return days_since_verification >= max_age_days
    
    def get_posting_age_days(self) -> int:
        """Get number of days since job was posted"""
        if not self.posted_date:
            return 0
        return (datetime.now() - self.posted_date).days
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary for monitoring"""
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company_name': self.company_name,
            'is_active': self.status_tracking.is_active,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'posting_age_days': self.get_posting_age_days(),
            'last_verified': self.status_tracking.last_verified_active.isoformat() if self.status_tracking.last_verified_active else None,
            'verification_attempts': self.status_tracking.verification_attempts,
            'verification_failures': self.status_tracking.verification_failures,
            'needs_verification': self.is_verification_needed(),
            'closed_date': self.status_tracking.closed_date.isoformat() if self.status_tracking.closed_date else None,
            'posting_duration_days': self.status_tracking.posting_duration_days,
            'closure_reason': self.status_tracking.closure_reason
        }


# Utility functions for job processing

def create_job_from_ats_data(ats_data: Dict[str, Any], source: str) -> Job:
    """Create Job instance from ATS API data"""
    job = Job()
    
    # Map common ATS fields
    job.external_job_id = ats_data.get('id')
    job.title = ats_data.get('title', '')
    job.description = ats_data.get('description', '')
    job.company_name = ats_data.get('company', {}).get('name', '')
    job.job_board_source = source
    
    # Map location data
    location_data = ats_data.get('location', {})
    job.location.city = location_data.get('city')
    job.location.state = location_data.get('state')
    job.location.country = location_data.get('country')
    
    # Map salary data
    salary_data = ats_data.get('salary', {})
    job.salary.min_salary = salary_data.get('min')
    job.salary.max_salary = salary_data.get('max')
    job.salary.currency = salary_data.get('currency', 'USD')
    
    # Map application URL
    job.application_tracking.application_url = ats_data.get('application_url')
    
    return job


def enrich_job_with_ai(job: Job, ai_service) -> Job:
    """Enrich job with AI-generated insights"""
    # This would integrate with your AI service
    # For now, placeholder for the enrichment logic
    
    # Extract keywords from description
    # Analyze tech stack requirements
    # Determine seniority level
    # Assess company culture fit
    
    job.updated_at = datetime.now()
    return job
