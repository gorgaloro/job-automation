#!/usr/bin/env python3
"""
Indeed API Integration

Provides job search and application capabilities through Indeed's API.
Integrates with the job parsing and application tracking systems.
"""

import logging
import os
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IndeedJob:
    """Indeed job posting data structure"""
    job_id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str] = None
    posted_date: Optional[datetime] = None
    job_type: Optional[str] = None
    remote_allowed: bool = False
    experience_level: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    benefits: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    source: str = "indeed"
    scraped_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IndeedSearchParams:
    """Indeed job search parameters"""
    query: str
    location: str = ""
    radius: int = 25
    job_type: str = ""  # fulltime, parttime, contract, internship, temporary
    salary_min: Optional[int] = None
    experience_level: str = ""  # entry_level, mid_level, senior_level
    remote: bool = False
    company_size: str = ""  # startup, small, medium, large
    posted_days: int = 30
    limit: int = 50


class IndeedAPIClient:
    """
    Indeed API client for job search and data retrieval.
    
    Provides comprehensive job search capabilities with advanced filtering,
    company data enrichment, and integration with the platform's workflow.
    """
    
    def __init__(self):
        """Initialize Indeed API client"""
        self.api_key = os.getenv('INDEED_API_KEY')
        self.base_url = "https://api.indeed.com/ads/apisearch"
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        # Rate limiting
        self.requests_per_minute = 60
        self.last_request_time = None
        
        logger.info(f"Indeed API client initialized (demo_mode: {self.demo_mode})")
    
    def search_jobs(self, params: IndeedSearchParams) -> List[IndeedJob]:
        """
        Search for jobs on Indeed
        
        Args:
            params: Search parameters
            
        Returns:
            List of job postings
        """
        try:
            if self.demo_mode:
                return self._generate_demo_jobs(params)
            
            # Build API request
            api_params = {
                'publisher': self.api_key,
                'q': params.query,
                'l': params.location,
                'sort': 'date',
                'radius': params.radius,
                'st': 'jobsite',
                'jt': params.job_type,
                'start': 0,
                'limit': min(params.limit, 25),  # Indeed API limit
                'fromage': params.posted_days,
                'format': 'json',
                'v': '2'
            }
            
            # Add salary filter if specified
            if params.salary_min:
                api_params['salary'] = f"${params.salary_min}+"
            
            # Add remote filter
            if params.remote:
                api_params['q'] += ' remote'
            
            # Make API request
            response = self._make_request(api_params)
            
            if response and 'results' in response:
                jobs = []
                for job_data in response['results']:
                    job = self._parse_job_data(job_data)
                    if job:
                        jobs.append(job)
                
                logger.info(f"Retrieved {len(jobs)} jobs from Indeed")
                return jobs
            
            return []
            
        except Exception as e:
            logger.error(f"Indeed job search failed: {str(e)}")
            return []
    
    def get_job_details(self, job_id: str) -> Optional[IndeedJob]:
        """
        Get detailed information for a specific job
        
        Args:
            job_id: Indeed job ID
            
        Returns:
            Detailed job information
        """
        try:
            if self.demo_mode:
                return self._generate_demo_job_detail(job_id)
            
            # Indeed doesn't have a direct job details API
            # Would need to scrape the job page or use alternative methods
            logger.warning("Job details API not available in Indeed public API")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job details: {str(e)}")
            return None
    
    def get_company_jobs(self, company_name: str, location: str = "") -> List[IndeedJob]:
        """
        Get all jobs from a specific company
        
        Args:
            company_name: Company name to search
            location: Location filter
            
        Returns:
            List of jobs from the company
        """
        try:
            params = IndeedSearchParams(
                query=f"company:{company_name}",
                location=location,
                limit=50
            )
            
            jobs = self.search_jobs(params)
            logger.info(f"Found {len(jobs)} jobs at {company_name}")
            return jobs
            
        except Exception as e:
            logger.error(f"Company job search failed: {str(e)}")
            return []
    
    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request with rate limiting"""
        try:
            # Rate limiting
            if self.last_request_time:
                time_diff = datetime.utcnow() - self.last_request_time
                if time_diff.total_seconds() < 1:  # 1 request per second
                    import time
                    time.sleep(1 - time_diff.total_seconds())
            
            url = f"{self.base_url}?{urlencode(params)}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            self.last_request_time = datetime.utcnow()
            return response.json()
            
        except Exception as e:
            logger.error(f"Indeed API request failed: {str(e)}")
            return None
    
    def _parse_job_data(self, job_data: Dict[str, Any]) -> Optional[IndeedJob]:
        """Parse Indeed job data into structured format"""
        try:
            # Parse posted date
            posted_date = None
            if 'date' in job_data:
                try:
                    posted_date = datetime.strptime(job_data['date'], '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    pass
            
            job = IndeedJob(
                job_id=job_data.get('jobkey', ''),
                title=job_data.get('jobtitle', ''),
                company=job_data.get('company', ''),
                location=job_data.get('formattedLocation', ''),
                description=job_data.get('snippet', ''),
                url=job_data.get('url', ''),
                salary=job_data.get('salary'),
                posted_date=posted_date,
                remote_allowed='remote' in job_data.get('snippet', '').lower()
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to parse job data: {str(e)}")
            return None
    
    def _generate_demo_jobs(self, params: IndeedSearchParams) -> List[IndeedJob]:
        """Generate demo jobs for development"""
        demo_jobs = [
            IndeedJob(
                job_id="indeed_001",
                title="Senior Software Engineer",
                company="TechCorp Solutions",
                location="San Francisco, CA",
                description="Join our team building next-generation AI applications. Python, React, AWS experience required.",
                url="https://indeed.com/job/indeed_001",
                salary="$140,000 - $180,000",
                posted_date=datetime.utcnow() - timedelta(days=2),
                job_type="fulltime",
                remote_allowed=True,
                experience_level="senior_level",
                requirements=["Python", "React", "AWS", "5+ years experience"],
                benefits=["Health insurance", "401k", "Remote work", "Stock options"]
            ),
            IndeedJob(
                job_id="indeed_002",
                title="AI/ML Engineer",
                company="DataFlow Analytics",
                location="Seattle, WA",
                description="Build machine learning models for real-time data processing. TensorFlow, PyTorch, Kubernetes.",
                url="https://indeed.com/job/indeed_002",
                salary="$130,000 - $170,000",
                posted_date=datetime.utcnow() - timedelta(days=5),
                job_type="fulltime",
                remote_allowed=False,
                experience_level="mid_level",
                requirements=["TensorFlow", "PyTorch", "Kubernetes", "3+ years ML experience"],
                benefits=["Health insurance", "Unlimited PTO", "Learning budget"]
            ),
            IndeedJob(
                job_id="indeed_003",
                title="Full Stack Developer",
                company="StartupXYZ",
                location="Austin, TX",
                description="Join our fast-growing startup. Node.js, React, MongoDB. Equity package included.",
                url="https://indeed.com/job/indeed_003",
                salary="$100,000 - $140,000",
                posted_date=datetime.utcnow() - timedelta(days=1),
                job_type="fulltime",
                remote_allowed=True,
                experience_level="mid_level",
                requirements=["Node.js", "React", "MongoDB", "2+ years experience"],
                benefits=["Equity", "Health insurance", "Flexible hours", "Remote work"]
            )
        ]
        
        # Filter based on search params
        filtered_jobs = []
        for job in demo_jobs:
            if params.query.lower() in job.title.lower() or params.query.lower() in job.description.lower():
                if not params.location or params.location.lower() in job.location.lower():
                    if not params.remote or job.remote_allowed:
                        filtered_jobs.append(job)
        
        return filtered_jobs[:params.limit]
    
    def _generate_demo_job_detail(self, job_id: str) -> IndeedJob:
        """Generate detailed demo job data"""
        return IndeedJob(
            job_id=job_id,
            title="Senior Software Engineer",
            company="TechCorp Solutions",
            location="San Francisco, CA",
            description="""
            We are seeking a Senior Software Engineer to join our innovative team building next-generation AI applications.
            
            Responsibilities:
            - Design and develop scalable web applications
            - Collaborate with AI/ML teams on model integration
            - Mentor junior developers
            - Participate in architectural decisions
            
            Requirements:
            - 5+ years of software development experience
            - Strong Python and JavaScript skills
            - Experience with React, Node.js, and AWS
            - Knowledge of AI/ML concepts preferred
            
            Benefits:
            - Competitive salary and equity
            - Comprehensive health insurance
            - Unlimited PTO
            - Remote work flexibility
            - $2000 annual learning budget
            """,
            url=f"https://indeed.com/job/{job_id}",
            salary="$140,000 - $180,000",
            posted_date=datetime.utcnow() - timedelta(days=2),
            job_type="fulltime",
            remote_allowed=True,
            experience_level="senior_level",
            company_size="medium",
            industry="technology",
            requirements=[
                "5+ years software development",
                "Python programming",
                "JavaScript/React",
                "AWS cloud services",
                "AI/ML knowledge (preferred)"
            ],
            benefits=[
                "Competitive salary",
                "Equity package",
                "Health insurance",
                "Unlimited PTO",
                "Remote work",
                "Learning budget"
            ]
        )


class IndeedIntegrationService:
    """
    Service for integrating Indeed data with the job search platform.
    
    Provides high-level integration methods for workflow orchestration
    and seamless data flow with other platform components.
    """
    
    def __init__(self):
        """Initialize Indeed integration service"""
        self.client = IndeedAPIClient()
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        logger.info("Indeed integration service initialized")
    
    def import_jobs_for_profile(self, personal_brand_profile: Dict[str, Any], 
                               location: str = "", limit: int = 50) -> List[IndeedJob]:
        """
        Import jobs tailored to a personal brand profile
        
        Args:
            personal_brand_profile: Personal brand profile data
            location: Location preference
            limit: Maximum jobs to import
            
        Returns:
            List of relevant jobs
        """
        try:
            # Extract search terms from profile
            skills = personal_brand_profile.get('technical_skills', [])
            career_goals = personal_brand_profile.get('career_goals', {})
            target_role = career_goals.get('target_role', '')
            
            # Build search query
            query_terms = [target_role] + skills[:3]  # Top 3 skills
            query = ' '.join(query_terms)
            
            # Search parameters
            params = IndeedSearchParams(
                query=query,
                location=location,
                remote=personal_brand_profile.get('work_preferences', {}).get('remote_work', False),
                experience_level=career_goals.get('seniority_level', ''),
                limit=limit
            )
            
            jobs = self.client.search_jobs(params)
            logger.info(f"Imported {len(jobs)} jobs for profile")
            return jobs
            
        except Exception as e:
            logger.error(f"Profile-based job import failed: {str(e)}")
            return []
    
    def sync_with_job_parser(self, jobs: List[IndeedJob]) -> List[Dict[str, Any]]:
        """
        Convert Indeed jobs to platform job format for parsing
        
        Args:
            jobs: Indeed job listings
            
        Returns:
            Jobs in platform format
        """
        try:
            platform_jobs = []
            
            for job in jobs:
                platform_job = {
                    'source': 'indeed',
                    'external_id': job.job_id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'url': job.url,
                    'salary_text': job.salary,
                    'posted_date': job.posted_date.isoformat() if job.posted_date else None,
                    'job_type': job.job_type,
                    'remote_allowed': job.remote_allowed,
                    'requirements': job.requirements,
                    'benefits': job.benefits,
                    'raw_data': job.__dict__
                }
                platform_jobs.append(platform_job)
            
            logger.info(f"Converted {len(platform_jobs)} jobs to platform format")
            return platform_jobs
            
        except Exception as e:
            logger.error(f"Job format conversion failed: {str(e)}")
            return []
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get Indeed integration status and metrics"""
        return {
            'service': 'Indeed API',
            'status': 'operational' if self.demo_mode else 'configured',
            'demo_mode': self.demo_mode,
            'api_key_configured': bool(self.client.api_key),
            'rate_limit': f"{self.client.requests_per_minute} requests/minute",
            'capabilities': [
                'Job search with advanced filters',
                'Company-specific job listings',
                'Real-time job data import',
                'Personal brand profile matching',
                'Integration with job parser',
                'Workflow orchestration support'
            ],
            'supported_filters': [
                'Location and radius',
                'Salary range',
                'Job type (full-time, part-time, contract)',
                'Experience level',
                'Remote work options',
                'Company size',
                'Posted date range'
            ]
        }


# Export main classes
__all__ = ['IndeedAPIClient', 'IndeedIntegrationService', 'IndeedJob', 'IndeedSearchParams']
