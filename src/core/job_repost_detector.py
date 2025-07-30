"""
Job Repost Detection Service
Identifies when companies repost similar jobs, indicating potential hiring dysfunction
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import hashlib
from collections import defaultdict

from .job_data_model import Job

logger = logging.getLogger(__name__)


@dataclass
class JobSimilarity:
    """Job similarity analysis result"""
    job1_id: str
    job2_id: str
    similarity_score: float
    title_similarity: float
    description_similarity: float
    requirements_similarity: float
    location_similarity: float
    salary_similarity: float
    is_likely_repost: bool
    confidence_level: str  # high, medium, low
    similarity_factors: List[str] = field(default_factory=list)


@dataclass
class RepostCluster:
    """Group of related job reposts"""
    cluster_id: str
    company_id: str
    company_name: str
    original_job_id: str
    reposted_job_ids: List[str] = field(default_factory=list)
    first_posted_date: datetime = None
    last_repost_date: datetime = None
    total_reposts: int = 0
    posting_frequency_days: float = 0.0
    cluster_score: float = 0.0  # Overall dysfunction indicator
    

@dataclass
class CompanyRepostAnalytics:
    """Company-level reposting analytics"""
    company_id: str
    company_name: str
    total_jobs_posted: int = 0
    total_reposts_detected: int = 0
    repost_rate: float = 0.0
    repost_clusters: List[RepostCluster] = field(default_factory=list)
    avg_days_between_reposts: float = 0.0
    dysfunction_score: float = 0.0  # 0.0-1.0, higher = more problematic
    red_flags: List[str] = field(default_factory=list)
    quality_rating: str = "unknown"  # excellent, good, fair, poor, avoid


class JobRepostDetector:
    """Service for detecting job reposts and analyzing company hiring patterns"""
    
    def __init__(self, similarity_threshold: float = 0.75, repost_window_days: int = 180):
        self.similarity_threshold = similarity_threshold
        self.repost_window_days = repost_window_days
        
        # Weights for similarity calculation
        self.similarity_weights = {
            'title': 0.30,
            'description': 0.35,
            'requirements': 0.20,
            'location': 0.10,
            'salary': 0.05
        }
        
        # Common variations that indicate same job
        self.title_normalizations = {
            r'\b(sr|senior)\b': 'senior',
            r'\b(jr|junior)\b': 'junior',
            r'\b(mgr|manager)\b': 'manager',
            r'\b(eng|engineer)\b': 'engineer',
            r'\b(dev|developer)\b': 'developer',
            r'\b(spec|specialist)\b': 'specialist',
            r'\b(coord|coordinator)\b': 'coordinator',
            r'\b(assoc|associate)\b': 'associate',
            r'\b(asst|assistant)\b': 'assistant',
            r'\b(dir|director)\b': 'director',
            r'\b(vp|vice president)\b': 'vice president',
            r'\b(i{1,3}|1-3)\b': '',  # Remove level indicators
            r'\s+': ' '  # Normalize whitespace
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower().strip()
        
        # Apply title normalizations
        for pattern, replacement in self.title_normalizations.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        # Use sequence matcher for similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def extract_key_requirements(self, description: str) -> Set[str]:
        """Extract key requirements from job description"""
        if not description:
            return set()
        
        # Common requirement patterns
        requirement_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'bachelor\'?s?\s+degree',
            r'master\'?s?\s+degree',
            r'phd|doctorate',
            r'certification\s+in\s+(\w+)',
            r'experience\s+with\s+([a-zA-Z0-9\s,]+)',
            r'proficient\s+in\s+([a-zA-Z0-9\s,]+)',
            r'knowledge\s+of\s+([a-zA-Z0-9\s,]+)',
            r'familiar\s+with\s+([a-zA-Z0-9\s,]+)'
        ]
        
        requirements = set()
        text = description.lower()
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    requirements.update(match)
                else:
                    requirements.add(match)
        
        # Clean and filter requirements
        cleaned_requirements = set()
        for req in requirements:
            if isinstance(req, str) and len(req.strip()) > 2:
                cleaned_requirements.add(req.strip())
        
        return cleaned_requirements
    
    def calculate_salary_similarity(self, job1: Job, job2: Job) -> float:
        """Calculate salary range similarity"""
        if not job1.salary or not job2.salary:
            return 0.5  # Neutral if salary info missing
        
        min1, max1 = job1.salary.min_salary, job1.salary.max_salary
        min2, max2 = job2.salary.min_salary, job2.salary.max_salary
        
        if not all([min1, max1, min2, max2]):
            return 0.5
        
        # Calculate overlap percentage
        overlap_start = max(min1, min2)
        overlap_end = min(max1, max2)
        
        if overlap_start >= overlap_end:
            return 0.0  # No overlap
        
        overlap = overlap_end - overlap_start
        total_range = max(max1, max2) - min(min1, min2)
        
        return overlap / total_range if total_range > 0 else 1.0
    
    def calculate_location_similarity(self, job1: Job, job2: Job) -> float:
        """Calculate location similarity"""
        if not job1.location or not job2.location:
            return 0.5
        
        # Exact match on city/state
        if (job1.location.city == job2.location.city and 
            job1.location.state == job2.location.state):
            return 1.0
        
        # Same state, different city
        if job1.location.state == job2.location.state:
            return 0.7
        
        # Both remote
        if (job1.location.location_type.value == 'remote' and 
            job2.location.location_type.value == 'remote'):
            return 1.0
        
        return 0.0
    
    def analyze_job_similarity(self, job1: Job, job2: Job) -> JobSimilarity:
        """Analyze similarity between two jobs"""
        # Calculate individual similarity scores
        title_sim = self.calculate_text_similarity(job1.title, job2.title)
        desc_sim = self.calculate_text_similarity(job1.description, job2.description)
        
        # Requirements similarity
        req1 = self.extract_key_requirements(job1.description)
        req2 = self.extract_key_requirements(job2.description)
        req_sim = len(req1.intersection(req2)) / len(req1.union(req2)) if req1.union(req2) else 0.0
        
        location_sim = self.calculate_location_similarity(job1, job2)
        salary_sim = self.calculate_salary_similarity(job1, job2)
        
        # Calculate weighted overall similarity
        overall_sim = (
            title_sim * self.similarity_weights['title'] +
            desc_sim * self.similarity_weights['description'] +
            req_sim * self.similarity_weights['requirements'] +
            location_sim * self.similarity_weights['location'] +
            salary_sim * self.similarity_weights['salary']
        )
        
        # Determine if likely repost
        is_repost = overall_sim >= self.similarity_threshold
        
        # Determine confidence level
        if overall_sim >= 0.9:
            confidence = "high"
        elif overall_sim >= 0.75:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Identify similarity factors
        factors = []
        if title_sim > 0.8:
            factors.append("identical_title")
        if desc_sim > 0.8:
            factors.append("identical_description")
        if req_sim > 0.8:
            factors.append("identical_requirements")
        if location_sim == 1.0:
            factors.append("same_location")
        if salary_sim > 0.8:
            factors.append("similar_salary")
        
        return JobSimilarity(
            job1_id=job1.job_id,
            job2_id=job2.job_id,
            similarity_score=overall_sim,
            title_similarity=title_sim,
            description_similarity=desc_sim,
            requirements_similarity=req_sim,
            location_similarity=location_sim,
            salary_similarity=salary_sim,
            is_likely_repost=is_repost,
            confidence_level=confidence,
            similarity_factors=factors
        )
    
    def detect_reposts_for_company(self, company_jobs: List[Job]) -> List[JobSimilarity]:
        """Detect reposts within a company's job listings"""
        reposts = []
        
        # Sort jobs by posting date
        sorted_jobs = sorted(company_jobs, key=lambda j: j.posted_date or datetime.min)
        
        for i, job1 in enumerate(sorted_jobs):
            for job2 in sorted_jobs[i+1:]:
                # Only compare jobs within repost window
                if job1.posted_date and job2.posted_date:
                    days_diff = (job2.posted_date - job1.posted_date).days
                    if days_diff > self.repost_window_days:
                        continue
                
                similarity = self.analyze_job_similarity(job1, job2)
                if similarity.is_likely_repost:
                    reposts.append(similarity)
        
        return reposts
    
    def create_repost_clusters(self, reposts: List[JobSimilarity], company_jobs: List[Job]) -> List[RepostCluster]:
        """Group related reposts into clusters"""
        # Create job lookup
        job_lookup = {job.job_id: job for job in company_jobs}
        
        # Build adjacency list of similar jobs
        adjacency = defaultdict(set)
        for repost in reposts:
            adjacency[repost.job1_id].add(repost.job2_id)
            adjacency[repost.job2_id].add(repost.job1_id)
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        for job_id in adjacency:
            if job_id in visited:
                continue
            
            # BFS to find all connected jobs
            cluster_jobs = set()
            queue = [job_id]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                cluster_jobs.add(current)
                
                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            if len(cluster_jobs) > 1:  # Only clusters with multiple jobs
                cluster_job_objects = [job_lookup[jid] for jid in cluster_jobs if jid in job_lookup]
                cluster_job_objects.sort(key=lambda j: j.posted_date or datetime.min)
                
                original_job = cluster_job_objects[0]
                reposted_jobs = cluster_job_objects[1:]
                
                # Calculate cluster metrics
                first_date = original_job.posted_date
                last_date = reposted_jobs[-1].posted_date if reposted_jobs else first_date
                
                frequency = 0.0
                if first_date and last_date and len(reposted_jobs) > 0:
                    total_days = (last_date - first_date).days
                    frequency = total_days / len(reposted_jobs) if total_days > 0 else 0.0
                
                # Calculate cluster dysfunction score
                cluster_score = min(1.0, len(reposted_jobs) / 5.0)  # More reposts = higher score
                if frequency > 0 and frequency < 30:  # Frequent reposts within 30 days
                    cluster_score += 0.3
                
                cluster = RepostCluster(
                    cluster_id=f"cluster_{original_job.job_id}",
                    company_id=original_job.company_id,
                    company_name=original_job.company_name,
                    original_job_id=original_job.job_id,
                    reposted_job_ids=[job.job_id for job in reposted_jobs],
                    first_posted_date=first_date,
                    last_repost_date=last_date,
                    total_reposts=len(reposted_jobs),
                    posting_frequency_days=frequency,
                    cluster_score=cluster_score
                )
                
                clusters.append(cluster)
        
        return clusters
    
    def analyze_company_repost_patterns(self, company_jobs: List[Job]) -> CompanyRepostAnalytics:
        """Analyze reposting patterns for a company"""
        if not company_jobs:
            return CompanyRepostAnalytics(company_id="", company_name="")
        
        company_id = company_jobs[0].company_id
        company_name = company_jobs[0].company_name
        
        # Detect reposts
        reposts = self.detect_reposts_for_company(company_jobs)
        
        # Create clusters
        clusters = self.create_repost_clusters(reposts, company_jobs)
        
        # Calculate analytics
        total_jobs = len(company_jobs)
        total_reposts = sum(cluster.total_reposts for cluster in clusters)
        repost_rate = total_reposts / total_jobs if total_jobs > 0 else 0.0
        
        # Calculate average days between reposts
        avg_frequency = 0.0
        if clusters:
            frequencies = [c.posting_frequency_days for c in clusters if c.posting_frequency_days > 0]
            avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0.0
        
        # Calculate dysfunction score
        dysfunction_score = 0.0
        red_flags = []
        
        if repost_rate > 0.3:  # More than 30% of jobs are reposts
            dysfunction_score += 0.4
            red_flags.append("high_repost_rate")
        
        if avg_frequency > 0 and avg_frequency < 30:  # Frequent reposts
            dysfunction_score += 0.3
            red_flags.append("frequent_reposts")
        
        if len(clusters) > 5:  # Many different positions being reposted
            dysfunction_score += 0.2
            red_flags.append("multiple_repost_clusters")
        
        # Check for rapid reposting (same job reposted within 2 weeks)
        rapid_reposts = [c for c in clusters if c.posting_frequency_days > 0 and c.posting_frequency_days < 14]
        if rapid_reposts:
            dysfunction_score += 0.1
            red_flags.append("rapid_reposts")
        
        # Determine quality rating
        if dysfunction_score >= 0.7:
            quality_rating = "avoid"
        elif dysfunction_score >= 0.5:
            quality_rating = "poor"
        elif dysfunction_score >= 0.3:
            quality_rating = "fair"
        elif dysfunction_score >= 0.1:
            quality_rating = "good"
        else:
            quality_rating = "excellent"
        
        return CompanyRepostAnalytics(
            company_id=company_id,
            company_name=company_name,
            total_jobs_posted=total_jobs,
            total_reposts_detected=total_reposts,
            repost_rate=repost_rate,
            repost_clusters=clusters,
            avg_days_between_reposts=avg_frequency,
            dysfunction_score=dysfunction_score,
            red_flags=red_flags,
            quality_rating=quality_rating
        )
    
    def generate_repost_report(self, company_analytics: List[CompanyRepostAnalytics]) -> Dict[str, Any]:
        """Generate comprehensive repost analysis report"""
        if not company_analytics:
            return {}
        
        # Sort by dysfunction score
        sorted_companies = sorted(company_analytics, key=lambda c: c.dysfunction_score, reverse=True)
        
        # Calculate overall statistics
        total_companies = len(company_analytics)
        companies_with_reposts = len([c for c in company_analytics if c.total_reposts_detected > 0])
        avg_repost_rate = sum(c.repost_rate for c in company_analytics) / total_companies
        
        # Quality distribution
        quality_dist = defaultdict(int)
        for company in company_analytics:
            quality_dist[company.quality_rating] += 1
        
        # Top problematic companies
        problematic_companies = [c for c in sorted_companies[:10] if c.dysfunction_score > 0.3]
        
        return {
            'summary': {
                'total_companies_analyzed': total_companies,
                'companies_with_reposts': companies_with_reposts,
                'average_repost_rate': avg_repost_rate,
                'companies_to_avoid': len([c for c in company_analytics if c.quality_rating == 'avoid'])
            },
            'quality_distribution': dict(quality_dist),
            'problematic_companies': [
                {
                    'company_name': c.company_name,
                    'dysfunction_score': c.dysfunction_score,
                    'repost_rate': c.repost_rate,
                    'total_reposts': c.total_reposts_detected,
                    'red_flags': c.red_flags,
                    'quality_rating': c.quality_rating
                }
                for c in problematic_companies
            ],
            'red_flag_frequency': {
                flag: len([c for c in company_analytics if flag in c.red_flags])
                for flag in ['high_repost_rate', 'frequent_reposts', 'multiple_repost_clusters', 'rapid_reposts']
            }
        }


# Utility functions for integration

def analyze_all_companies(jobs_by_company: Dict[str, List[Job]]) -> Dict[str, CompanyRepostAnalytics]:
    """Analyze repost patterns for all companies"""
    detector = JobRepostDetector()
    analytics = {}
    
    for company_id, jobs in jobs_by_company.items():
        analytics[company_id] = detector.analyze_company_repost_patterns(jobs)
    
    return analytics


def get_company_quality_flags(company_analytics: CompanyRepostAnalytics) -> List[str]:
    """Get quality flags for a company based on repost analysis"""
    flags = []
    
    if company_analytics.quality_rating == "avoid":
        flags.append("🚩 AVOID - High repost dysfunction")
    elif company_analytics.quality_rating == "poor":
        flags.append("⚠️ CAUTION - Frequent reposts detected")
    
    if "rapid_reposts" in company_analytics.red_flags:
        flags.append("⏰ Rapid reposting pattern")
    
    if "high_repost_rate" in company_analytics.red_flags:
        flags.append("🔄 High repost rate")
    
    return flags
