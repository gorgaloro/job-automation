"""
Job Board API Integration Module

This module provides unified access to multiple job board and ATS APIs including:
- Greenhouse
- Lever  
- SmartRecruiters
- Workable

All APIs are normalized to a common job data format for consistent processing.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobData:
    """Normalized job data structure"""
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[datetime]
    source_api: str
    api_job_id: str
    department: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    company_size: Optional[str] = None
    raw_data: Optional[Dict] = None

class BaseJobBoardAPI:
    """Base class for job board API integrations"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_jobs(self, limit: int = 100) -> List[JobData]:
        """Override in subclasses"""
        raise NotImplementedError
        
    def normalize_job_data(self, raw_job: Dict, source_api: str) -> JobData:
        """Override in subclasses to normalize job data"""
        raise NotImplementedError

class GreenhouseAPI(BaseJobBoardAPI):
    """Greenhouse ATS API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('GREENHOUSE_API_KEY'),
            base_url='https://harvest-api.greenhouse.io/v1/'
        )
        
    async def get_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch jobs from Greenhouse API"""
        if not self.api_key:
            logger.warning("Greenhouse API key not provided, skipping")
            return []
            
        try:
            headers = {
                'Authorization': f'Basic {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = urljoin(self.base_url, f'jobs?per_page={min(limit, 500)}')
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    jobs_data = await response.json()
                    return [self.normalize_job_data(job, 'greenhouse') for job in jobs_data]
                else:
                    logger.error(f"Greenhouse API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Greenhouse jobs: {e}")
            return []
            
    def normalize_job_data(self, raw_job: Dict, source_api: str) -> JobData:
        """Normalize Greenhouse job data"""
        return JobData(
            id=f"gh_{raw_job.get('id')}",
            title=raw_job.get('name', ''),
            company=raw_job.get('departments', [{}])[0].get('name', '') if raw_job.get('departments') else '',
            location=', '.join([office.get('name', '') for office in raw_job.get('offices', [])]),
            description=raw_job.get('content', ''),
            url=raw_job.get('absolute_url', ''),
            posted_date=datetime.fromisoformat(raw_job.get('created_at', '').replace('Z', '+00:00')) if raw_job.get('created_at') else None,
            source_api=source_api,
            api_job_id=str(raw_job.get('id')),
            department=raw_job.get('departments', [{}])[0].get('name') if raw_job.get('departments') else None,
            employment_type=raw_job.get('job_type', {}).get('name') if raw_job.get('job_type') else None,
            raw_data=raw_job
        )

class LeverAPI(BaseJobBoardAPI):
    """Lever ATS API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('LEVER_API_KEY'),
            base_url='https://api.lever.co/v1/'
        )
        
    async def get_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch jobs from Lever API"""
        if not self.api_key:
            logger.warning("Lever API key not provided, skipping")
            return []
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = urljoin(self.base_url, f'postings?limit={min(limit, 100)}')
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    jobs_data = response_data.get('data', [])
                    return [self.normalize_job_data(job, 'lever') for job in jobs_data]
                else:
                    logger.error(f"Lever API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Lever jobs: {e}")
            return []
            
    def normalize_job_data(self, raw_job: Dict, source_api: str) -> JobData:
        """Normalize Lever job data"""
        return JobData(
            id=f"lv_{raw_job.get('id')}",
            title=raw_job.get('text', ''),
            company=raw_job.get('categories', {}).get('team', ''),
            location=raw_job.get('categories', {}).get('location', ''),
            description=raw_job.get('content', {}).get('description', ''),
            url=raw_job.get('hostedUrl', ''),
            posted_date=datetime.fromtimestamp(raw_job.get('createdAt', 0) / 1000) if raw_job.get('createdAt') else None,
            source_api=source_api,
            api_job_id=raw_job.get('id'),
            department=raw_job.get('categories', {}).get('department'),
            employment_type=raw_job.get('categories', {}).get('commitment'),
            raw_data=raw_job
        )

class SmartRecruitersAPI(BaseJobBoardAPI):
    """SmartRecruiters API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('SMARTRECRUITERS_API_KEY'),
            base_url='https://api.smartrecruiters.com/'
        )
        
    async def get_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch jobs from SmartRecruiters API"""
        if not self.api_key:
            logger.warning("SmartRecruiters API key not provided, skipping")
            return []
            
        try:
            headers = {
                'X-SmartToken': self.api_key,
                'Content-Type': 'application/json'
            }
            
            url = urljoin(self.base_url, f'postings?limit={min(limit, 100)}')
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    jobs_data = response_data.get('content', [])
                    return [self.normalize_job_data(job, 'smartrecruiters') for job in jobs_data]
                else:
                    logger.error(f"SmartRecruiters API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching SmartRecruiters jobs: {e}")
            return []
            
    def normalize_job_data(self, raw_job: Dict, source_api: str) -> JobData:
        """Normalize SmartRecruiters job data"""
        return JobData(
            id=f"sr_{raw_job.get('id')}",
            title=raw_job.get('name', ''),
            company=raw_job.get('company', {}).get('name', ''),
            location=raw_job.get('location', {}).get('city', ''),
            description=raw_job.get('jobAd', {}).get('sections', {}).get('jobDescription', {}).get('text', ''),
            url=raw_job.get('ref', ''),
            posted_date=datetime.fromisoformat(raw_job.get('releasedDate', '').replace('Z', '+00:00')) if raw_job.get('releasedDate') else None,
            source_api=source_api,
            api_job_id=raw_job.get('id'),
            department=raw_job.get('department', {}).get('label'),
            employment_type=raw_job.get('typeOfEmployment', {}).get('label'),
            raw_data=raw_job
        )

class WorkableAPI(BaseJobBoardAPI):
    """Workable API Integration"""
    
    def __init__(self, api_key: str = None, subdomain: str = None):
        self.subdomain = subdomain or os.getenv('WORKABLE_SUBDOMAIN')
        super().__init__(
            api_key=api_key or os.getenv('WORKABLE_API_KEY'),
            base_url=f'https://{self.subdomain}.workable.com/spi/v3/'
        )
        
    async def get_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch jobs from Workable API"""
        if not self.api_key or not self.subdomain:
            logger.warning("Workable API key or subdomain not provided, skipping")
            return []
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = urljoin(self.base_url, f'jobs?limit={min(limit, 100)}')
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    jobs_data = response_data.get('jobs', [])
                    return [self.normalize_job_data(job, 'workable') for job in jobs_data]
                else:
                    logger.error(f"Workable API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Workable jobs: {e}")
            return []
            
    def normalize_job_data(self, raw_job: Dict, source_api: str) -> JobData:
        """Normalize Workable job data"""
        return JobData(
            id=f"wk_{raw_job.get('shortcode')}",
            title=raw_job.get('title', ''),
            company=raw_job.get('department', ''),
            location=raw_job.get('location', {}).get('city', ''),
            description=raw_job.get('description', ''),
            url=raw_job.get('application_url', ''),
            posted_date=datetime.fromisoformat(raw_job.get('created_at', '').replace('Z', '+00:00')) if raw_job.get('created_at') else None,
            source_api=source_api,
            api_job_id=raw_job.get('shortcode'),
            department=raw_job.get('department'),
            employment_type=raw_job.get('employment_type'),
            raw_data=raw_job
        )

class JobBoardIntegrator:
    """Main class for managing all job board API integrations"""
    
    def __init__(self):
        self.apis = {
            'greenhouse': GreenhouseAPI(),
            'lever': LeverAPI(),
            'smartrecruiters': SmartRecruitersAPI(),
            'workable': WorkableAPI()
        }
        
    async def fetch_all_jobs(self, limit_per_api: int = 100) -> List[JobData]:
        """Fetch jobs from all configured APIs"""
        all_jobs = []
        
        for api_name, api_instance in self.apis.items():
            try:
                async with api_instance:
                    jobs = await api_instance.get_jobs(limit_per_api)
                    all_jobs.extend(jobs)
                    logger.info(f"Fetched {len(jobs)} jobs from {api_name}")
            except Exception as e:
                logger.error(f"Error with {api_name} API: {e}")
                continue
                
        logger.info(f"Total jobs fetched: {len(all_jobs)}")
        return all_jobs
        
    def deduplicate_jobs(self, jobs: List[JobData]) -> List[JobData]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            job_key = (job.title.lower().strip(), job.company.lower().strip())
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
                
        logger.info(f"Deduplicated {len(jobs)} jobs to {len(unique_jobs)} unique jobs")
        return unique_jobs

# Demo/Testing Functions
async def demo_job_board_integration():
    """Demo function to test job board API integration"""
    print("🚀 Testing Job Board API Integration...")
    
    integrator = JobBoardIntegrator()
    
    # Fetch jobs from all APIs
    jobs = await integrator.fetch_all_jobs(limit_per_api=10)
    
    # Deduplicate
    unique_jobs = integrator.deduplicate_jobs(jobs)
    
    # Display results
    print(f"\n📊 Results:")
    print(f"Total jobs fetched: {len(jobs)}")
    print(f"Unique jobs after deduplication: {len(unique_jobs)}")
    
    # Show sample jobs
    print(f"\n📋 Sample Jobs:")
    for i, job in enumerate(unique_jobs[:5]):
        print(f"\n{i+1}. {job.title} at {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Source: {job.source_api}")
        print(f"   URL: {job.url}")
        
    return unique_jobs

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_job_board_integration())
