"""
Multi-Source Job Detector
Identifies duplicate jobs across platforms and analyzes content deltas
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import hashlib
from collections import defaultdict
from urllib.parse import urlparse

from .job_data_model import Job

logger = logging.getLogger(__name__)


@dataclass
class JobSource:
    """Represents a job posting source"""
    source_id: str
    job_id: str
    source_type: str  # 'primary' or 'secondary'
    source_platform: str  # 'company_careers', 'linkedin', 'indeed', etc.
    source_name: str
    source_url: str
    external_job_id: Optional[str] = None
    requisition_id: Optional[str] = None
    
    # Content
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_text: Optional[str] = None
    location_text: Optional[str] = None
    
    # Metadata
    discovered_at: datetime = None
    is_active: bool = True
    is_primary_source: bool = False
    source_reliability_score: float = 1.0
    content_fingerprint: Optional[str] = None
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now()
        if self.content_fingerprint is None:
            self.content_fingerprint = self.calculate_fingerprint()
    
    def calculate_fingerprint(self) -> str:
        """Calculate content fingerprint for duplicate detection"""
        content = '|'.join([
            self.title or '',
            self.description or '',
            self.requirements or ''
        ])
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class SourceDelta:
    """Represents differences between job sources"""
    job_id: str
    primary_source_id: str
    secondary_source_id: str
    delta_status: str  # 'identical', 'minor_differences', 'content_drift', etc.
    overall_similarity_score: float
    
    # Field-level similarities
    title_similarity: float = 0.0
    description_similarity: float = 0.0
    requirements_similarity: float = 0.0
    salary_similarity: float = 0.0
    location_similarity: float = 0.0
    
    # Specific differences
    title_differences: List[str] = field(default_factory=list)
    description_differences: List[str] = field(default_factory=list)
    requirements_differences: List[str] = field(default_factory=list)
    
    # Quality indicators
    indicates_outdated_secondary: bool = False
    indicates_poor_sync: bool = False
    quality_impact_score: float = 0.0


@dataclass
class CompanySourceAnalytics:
    """Company-level source management analytics"""
    company_id: str
    company_name: str
    total_jobs_tracked: int = 0
    jobs_with_primary_source: int = 0
    jobs_with_multiple_sources: int = 0
    avg_sources_per_job: float = 0.0
    
    # Platform usage
    platforms_used: List[str] = field(default_factory=list)
    primary_platforms: List[str] = field(default_factory=list)
    secondary_platforms: List[str] = field(default_factory=list)
    
    # Content consistency
    jobs_with_deltas: int = 0
    avg_similarity_score: float = 1.0
    content_consistency_score: float = 1.0
    
    # Quality indicators
    outdated_secondary_count: int = 0
    poor_sync_indicators: int = 0
    hr_quality_score: float = 1.0
    source_management_flags: List[str] = field(default_factory=list)


class MultiSourceJobDetector:
    """Service for detecting duplicate jobs across sources and analyzing deltas"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        
        # Platform reliability scores
        self.platform_reliability = {
            'company_careers': 1.0,
            'greenhouse': 0.95,
            'lever': 0.95,
            'smartrecruiters': 0.90,
            'workable': 0.90,
            'linkedin': 0.80,
            'indeed': 0.75,
            'glassdoor': 0.70,
            'ziprecruiter': 0.65,
            'monster': 0.60,
            'careerbuilder': 0.60
        }
        
        # Primary source indicators
        self.primary_source_indicators = [
            'careers.company.com',
            'company.com/careers',
            'jobs.company.com',
            'greenhouse.io',
            'lever.co',
            'smartrecruiters.com',
            'workable.com'
        ]
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase and strip
        normalized = text.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common formatting artifacts
        normalized = re.sub(r'[^\w\s\-\.,;:()]', '', normalized)
        
        return normalized
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def identify_text_differences(self, text1: str, text2: str) -> List[str]:
        """Identify specific differences between texts"""
        if not text1 or not text2:
            return ["One text is empty"]
        
        differences = []
        
        # Split into sentences for comparison
        sentences1 = re.split(r'[.!?]+', text1)
        sentences2 = re.split(r'[.!?]+', text2)
        
        # Find sentences that appear in one but not the other
        set1 = set(s.strip().lower() for s in sentences1 if s.strip())
        set2 = set(s.strip().lower() for s in sentences2 if s.strip())
        
        only_in_1 = set1 - set2
        only_in_2 = set2 - set1
        
        if only_in_1:
            differences.append(f"Primary source has {len(only_in_1)} unique sentences")
        if only_in_2:
            differences.append(f"Secondary source has {len(only_in_2)} unique sentences")
        
        # Check for length differences
        len_diff = abs(len(text1) - len(text2)) / max(len(text1), len(text2))
        if len_diff > 0.2:
            differences.append(f"Significant length difference: {len_diff:.1%}")
        
        return differences
    
    def determine_source_type(self, source_url: str) -> str:
        """Determine if source is primary or secondary based on URL"""
        if not source_url:
            return 'secondary'
        
        parsed_url = urlparse(source_url.lower())
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Check for primary source indicators
        for indicator in self.primary_source_indicators:
            if indicator in domain or indicator in path:
                return 'primary'
        
        # Known secondary sources
        secondary_domains = [
            'linkedin.com',
            'indeed.com',
            'glassdoor.com',
            'ziprecruiter.com',
            'monster.com',
            'careerbuilder.com',
            'dice.com',
            'stackoverflow.com'
        ]
        
        for secondary in secondary_domains:
            if secondary in domain:
                return 'secondary'
        
        # Default to secondary if uncertain
        return 'secondary'
    
    def get_platform_from_url(self, source_url: str) -> str:
        """Extract platform name from URL"""
        if not source_url:
            return 'other'
        
        parsed_url = urlparse(source_url.lower())
        domain = parsed_url.netloc
        
        platform_mapping = {
            'greenhouse.io': 'greenhouse',
            'lever.co': 'lever',
            'smartrecruiters.com': 'smartrecruiters',
            'workable.com': 'workable',
            'linkedin.com': 'linkedin',
            'indeed.com': 'indeed',
            'glassdoor.com': 'glassdoor',
            'ziprecruiter.com': 'ziprecruiter',
            'monster.com': 'monster',
            'careerbuilder.com': 'careerbuilder',
            'dice.com': 'dice',
            'stackoverflow.com': 'stackoverflow'
        }
        
        for domain_key, platform in platform_mapping.items():
            if domain_key in domain:
                return platform
        
        # Check if it's a company career page
        if any(indicator in domain for indicator in ['careers', 'jobs']):
            return 'company_careers'
        
        return 'other'
    
    def create_job_source(self, job: Job, source_url: str, **kwargs) -> JobSource:
        """Create a JobSource object from a Job and source URL"""
        source_type = self.determine_source_type(source_url)
        platform = self.get_platform_from_url(source_url)
        
        return JobSource(
            source_id=f"{job.job_id}_{platform}",
            job_id=job.job_id,
            source_type=source_type,
            source_platform=platform,
            source_name=kwargs.get('source_name', platform.title()),
            source_url=source_url,
            external_job_id=kwargs.get('external_job_id'),
            requisition_id=job.requisition_id,
            title=job.title,
            description=job.description,
            requirements=kwargs.get('requirements'),
            salary_text=str(job.salary) if job.salary else None,
            location_text=str(job.location) if job.location else None,
            is_primary_source=(source_type == 'primary'),
            source_reliability_score=self.platform_reliability.get(platform, 0.5)
        )
    
    def detect_duplicate_jobs(self, job_sources: List[JobSource]) -> List[Tuple[JobSource, JobSource, float]]:
        """Detect duplicate jobs across different sources"""
        duplicates = []
        
        # Group sources by company (assuming job_id contains company info)
        sources_by_company = defaultdict(list)
        for source in job_sources:
            # Extract company identifier from job_id or use a default grouping
            company_key = source.job_id.split('_')[0] if '_' in source.job_id else 'default'
            sources_by_company[company_key].append(source)
        
        # Check for duplicates within each company
        for company_sources in sources_by_company.values():
            for i, source1 in enumerate(company_sources):
                for source2 in company_sources[i+1:]:
                    similarity = self.calculate_job_similarity(source1, source2)
                    if similarity >= self.similarity_threshold:
                        duplicates.append((source1, source2, similarity))
        
        return duplicates
    
    def calculate_job_similarity(self, source1: JobSource, source2: JobSource) -> float:
        """Calculate overall similarity between two job sources"""
        # If fingerprints match exactly, they're identical
        if source1.content_fingerprint == source2.content_fingerprint:
            return 1.0
        
        # Calculate field-level similarities
        title_sim = self.calculate_text_similarity(source1.title, source2.title)
        desc_sim = self.calculate_text_similarity(source1.description, source2.description)
        req_sim = self.calculate_text_similarity(source1.requirements, source2.requirements)
        
        # Weighted average
        weights = {'title': 0.3, 'description': 0.5, 'requirements': 0.2}
        overall_sim = (
            title_sim * weights['title'] +
            desc_sim * weights['description'] +
            req_sim * weights['requirements']
        )
        
        return overall_sim
    
    def analyze_source_delta(self, primary_source: JobSource, secondary_source: JobSource) -> SourceDelta:
        """Analyze differences between primary and secondary sources"""
        # Calculate similarities
        title_sim = self.calculate_text_similarity(primary_source.title, secondary_source.title)
        desc_sim = self.calculate_text_similarity(primary_source.description, secondary_source.description)
        req_sim = self.calculate_text_similarity(primary_source.requirements, secondary_source.requirements)
        salary_sim = self.calculate_text_similarity(primary_source.salary_text, secondary_source.salary_text)
        location_sim = self.calculate_text_similarity(primary_source.location_text, secondary_source.location_text)
        
        # Calculate overall similarity
        overall_sim = (title_sim * 0.2 + desc_sim * 0.4 + req_sim * 0.3 + 
                      salary_sim * 0.05 + location_sim * 0.05)
        
        # Determine delta status
        if overall_sim >= 0.98:
            delta_status = 'identical'
        elif overall_sim >= 0.90:
            delta_status = 'minor_differences'
        elif overall_sim >= 0.75:
            delta_status = 'content_drift'
        elif overall_sim >= 0.50:
            delta_status = 'major_discrepancy'
        else:
            delta_status = 'outdated_secondary'
        
        # Identify specific differences
        title_diffs = self.identify_text_differences(primary_source.title, secondary_source.title)
        desc_diffs = self.identify_text_differences(primary_source.description, secondary_source.description)
        req_diffs = self.identify_text_differences(primary_source.requirements, secondary_source.requirements)
        
        # Quality indicators
        indicates_outdated = delta_status == 'outdated_secondary' or overall_sim < 0.60
        indicates_poor_sync = len(desc_diffs) > 3 or desc_sim < 0.70
        quality_impact = max(0.0, 1.0 - overall_sim)
        
        return SourceDelta(
            job_id=primary_source.job_id,
            primary_source_id=primary_source.source_id,
            secondary_source_id=secondary_source.source_id,
            delta_status=delta_status,
            overall_similarity_score=overall_sim,
            title_similarity=title_sim,
            description_similarity=desc_sim,
            requirements_similarity=req_sim,
            salary_similarity=salary_sim,
            location_similarity=location_sim,
            title_differences=title_diffs,
            description_differences=desc_diffs,
            requirements_differences=req_diffs,
            indicates_outdated_secondary=indicates_outdated,
            indicates_poor_sync=indicates_poor_sync,
            quality_impact_score=quality_impact
        )
    
    def analyze_company_sources(self, company_id: str, company_name: str, 
                               job_sources: List[JobSource]) -> CompanySourceAnalytics:
        """Analyze source management quality for a company"""
        if not job_sources:
            return CompanySourceAnalytics(company_id=company_id, company_name=company_name)
        
        # Group sources by job
        sources_by_job = defaultdict(list)
        for source in job_sources:
            sources_by_job[source.job_id].append(source)
        
        # Calculate metrics
        total_jobs = len(sources_by_job)
        jobs_with_primary = len([sources for sources in sources_by_job.values() 
                                if any(s.is_primary_source for s in sources)])
        jobs_with_multiple = len([sources for sources in sources_by_job.values() 
                                 if len(sources) > 1])
        
        total_sources = len(job_sources)
        avg_sources_per_job = total_sources / total_jobs if total_jobs > 0 else 0
        
        # Platform analysis
        all_platforms = list(set(s.source_platform for s in job_sources))
        primary_platforms = list(set(s.source_platform for s in job_sources if s.is_primary_source))
        secondary_platforms = list(set(s.source_platform for s in job_sources if not s.is_primary_source))
        
        # Analyze deltas
        deltas = []
        for sources in sources_by_job.values():
            primary_sources = [s for s in sources if s.is_primary_source]
            secondary_sources = [s for s in sources if not s.is_primary_source]
            
            if primary_sources and secondary_sources:
                primary = primary_sources[0]  # Use first primary source
                for secondary in secondary_sources:
                    delta = self.analyze_source_delta(primary, secondary)
                    deltas.append(delta)
        
        jobs_with_deltas = len(set(d.job_id for d in deltas))
        avg_similarity = sum(d.overall_similarity_score for d in deltas) / len(deltas) if deltas else 1.0
        content_consistency = avg_similarity  # Simplified calculation
        
        # Quality indicators
        outdated_count = len([d for d in deltas if d.indicates_outdated_secondary])
        poor_sync_count = len([d for d in deltas if d.indicates_poor_sync])
        
        # Calculate HR quality score
        hr_quality = 1.0
        if total_jobs > 0:
            # Penalize missing primary sources
            hr_quality -= (total_jobs - jobs_with_primary) / total_jobs * 0.3
            # Penalize poor content consistency
            hr_quality *= content_consistency
            # Penalize outdated secondary sources
            if deltas:
                hr_quality -= outdated_count / len(deltas) * 0.2
        
        hr_quality = max(0.0, min(1.0, hr_quality))
        
        # Generate flags
        flags = []
        if jobs_with_primary / total_jobs < 0.5:
            flags.append('missing_primary_sources')
        if content_consistency < 0.8:
            flags.append('poor_content_consistency')
        if outdated_count > total_jobs * 0.2:
            flags.append('frequent_outdated_secondaries')
        if poor_sync_count > total_jobs * 0.3:
            flags.append('poor_sync_quality')
        
        return CompanySourceAnalytics(
            company_id=company_id,
            company_name=company_name,
            total_jobs_tracked=total_jobs,
            jobs_with_primary_source=jobs_with_primary,
            jobs_with_multiple_sources=jobs_with_multiple,
            avg_sources_per_job=avg_sources_per_job,
            platforms_used=all_platforms,
            primary_platforms=primary_platforms,
            secondary_platforms=secondary_platforms,
            jobs_with_deltas=jobs_with_deltas,
            avg_similarity_score=avg_similarity,
            content_consistency_score=content_consistency,
            outdated_secondary_count=outdated_count,
            poor_sync_indicators=poor_sync_count,
            hr_quality_score=hr_quality,
            source_management_flags=flags
        )
    
    def generate_source_analysis_report(self, companies_analytics: List[CompanySourceAnalytics]) -> Dict[str, Any]:
        """Generate comprehensive source analysis report"""
        if not companies_analytics:
            return {}
        
        total_companies = len(companies_analytics)
        total_jobs = sum(c.total_jobs_tracked for c in companies_analytics)
        
        # Quality distribution
        excellent_companies = len([c for c in companies_analytics if c.hr_quality_score >= 0.9])
        good_companies = len([c for c in companies_analytics if 0.7 <= c.hr_quality_score < 0.9])
        fair_companies = len([c for c in companies_analytics if 0.5 <= c.hr_quality_score < 0.7])
        poor_companies = len([c for c in companies_analytics if c.hr_quality_score < 0.5])
        
        # Platform usage analysis
        all_platforms = set()
        for company in companies_analytics:
            all_platforms.update(company.platforms_used)
        
        platform_usage = {}
        for platform in all_platforms:
            usage_count = len([c for c in companies_analytics if platform in c.platforms_used])
            platform_usage[platform] = usage_count
        
        # Top problematic companies
        problematic_companies = sorted(companies_analytics, key=lambda c: c.hr_quality_score)[:10]
        
        return {
            'summary': {
                'total_companies_analyzed': total_companies,
                'total_jobs_tracked': total_jobs,
                'avg_sources_per_job': sum(c.avg_sources_per_job for c in companies_analytics) / total_companies,
                'companies_with_multi_source_jobs': len([c for c in companies_analytics if c.jobs_with_multiple_sources > 0])
            },
            'quality_distribution': {
                'excellent': excellent_companies,
                'good': good_companies,
                'fair': fair_companies,
                'poor': poor_companies
            },
            'platform_usage': platform_usage,
            'problematic_companies': [
                {
                    'company_name': c.company_name,
                    'hr_quality_score': c.hr_quality_score,
                    'content_consistency_score': c.content_consistency_score,
                    'flags': c.source_management_flags,
                    'jobs_tracked': c.total_jobs_tracked
                }
                for c in problematic_companies if c.hr_quality_score < 0.7
            ],
            'common_issues': {
                flag: len([c for c in companies_analytics if flag in c.source_management_flags])
                for flag in ['missing_primary_sources', 'poor_content_consistency', 
                           'frequent_outdated_secondaries', 'poor_sync_quality']
            }
        }


# Utility functions for script execution

def run_duplicate_detection_script(job_sources: List[JobSource]) -> Dict[str, Any]:
    """Script to identify duplicate jobs across sources"""
    detector = MultiSourceJobDetector()
    
    duplicates = detector.detect_duplicate_jobs(job_sources)
    
    return {
        'total_sources_analyzed': len(job_sources),
        'duplicates_found': len(duplicates),
        'duplicate_pairs': [
            {
                'source1': {'platform': dup[0].source_platform, 'url': dup[0].source_url},
                'source2': {'platform': dup[1].source_platform, 'url': dup[1].source_url},
                'similarity_score': dup[2]
            }
            for dup in duplicates
        ]
    }


def run_delta_analysis_script(job_sources: List[JobSource]) -> Dict[str, Any]:
    """Script to analyze content deltas between primary and secondary sources"""
    detector = MultiSourceJobDetector()
    
    # Group sources by job
    sources_by_job = defaultdict(list)
    for source in job_sources:
        sources_by_job[source.job_id].append(source)
    
    deltas = []
    for sources in sources_by_job.values():
        primary_sources = [s for s in sources if s.is_primary_source]
        secondary_sources = [s for s in sources if not s.is_primary_source]
        
        if primary_sources and secondary_sources:
            primary = primary_sources[0]
            for secondary in secondary_sources:
                delta = detector.analyze_source_delta(primary, secondary)
                deltas.append(delta)
    
    return {
        'total_jobs_analyzed': len(sources_by_job),
        'deltas_found': len(deltas),
        'avg_similarity_score': sum(d.overall_similarity_score for d in deltas) / len(deltas) if deltas else 1.0,
        'outdated_secondaries': len([d for d in deltas if d.indicates_outdated_secondary]),
        'poor_sync_indicators': len([d for d in deltas if d.indicates_poor_sync]),
        'delta_breakdown': {
            'identical': len([d for d in deltas if d.delta_status == 'identical']),
            'minor_differences': len([d for d in deltas if d.delta_status == 'minor_differences']),
            'content_drift': len([d for d in deltas if d.delta_status == 'content_drift']),
            'major_discrepancy': len([d for d in deltas if d.delta_status == 'major_discrepancy']),
            'outdated_secondary': len([d for d in deltas if d.delta_status == 'outdated_secondary'])
        }
    }
