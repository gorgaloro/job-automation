"""
Job Status Monitoring Service
Automated job posting lifecycle tracking and closure detection
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
from urllib.parse import urlparse
import time

from .job_data_model import Job, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of job verification attempt"""
    job_id: str
    is_active: bool
    error_message: Optional[str] = None
    response_code: Optional[int] = None
    detection_method: str = "automated_check"
    verification_timestamp: datetime = None
    
    def __post_init__(self):
        if self.verification_timestamp is None:
            self.verification_timestamp = datetime.now()


@dataclass
class MonitoringStats:
    """Job monitoring statistics"""
    total_jobs_checked: int = 0
    active_jobs_found: int = 0
    closed_jobs_detected: int = 0
    verification_errors: int = 0
    average_posting_duration: float = 0.0
    jobs_by_closure_reason: Dict[str, int] = None
    
    def __post_init__(self):
        if self.jobs_by_closure_reason is None:
            self.jobs_by_closure_reason = {}


class JobStatusMonitor:
    """Service for monitoring job posting status and detecting closures"""
    
    def __init__(self, max_concurrent_requests: int = 10, request_delay: float = 1.0):
        self.max_concurrent_requests = max_concurrent_requests
        self.request_delay = request_delay
        self.session = None
        
        # Job board specific detection patterns
        self.closure_patterns = {
            'indeed': [
                r'job.*no longer.*available',
                r'position.*filled',
                r'posting.*expired',
                r'job.*removed'
            ],
            'greenhouse': [
                r'position.*no longer.*accepting',
                r'job.*closed',
                r'application.*deadline.*passed'
            ],
            'lever': [
                r'position.*filled',
                r'no longer.*hiring',
                r'job.*closed'
            ],
            'linkedin': [
                r'job.*no longer.*available',
                r'position.*filled',
                r'applications.*closed'
            ],
            'generic': [
                r'404.*not found',
                r'page.*not.*found',
                r'job.*not.*found',
                r'position.*unavailable',
                r'expired.*posting'
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_job_board_from_url(self, url: str) -> str:
        """Determine job board from URL"""
        if not url:
            return 'generic'
        
        domain = urlparse(url).netloc.lower()
        
        if 'indeed' in domain:
            return 'indeed'
        elif 'greenhouse' in domain:
            return 'greenhouse'
        elif 'lever' in domain:
            return 'lever'
        elif 'linkedin' in domain:
            return 'linkedin'
        else:
            return 'generic'
    
    async def verify_single_job(self, job: Job) -> VerificationResult:
        """Verify if a single job is still active"""
        if not job.application_tracking.application_url:
            return VerificationResult(
                job_id=job.job_id,
                is_active=False,
                error_message="No application URL available",
                detection_method="no_url"
            )
        
        try:
            # Add delay to avoid rate limiting
            await asyncio.sleep(self.request_delay)
            
            async with self.session.get(job.application_tracking.application_url) as response:
                response_text = await response.text()
                job_board = self.get_job_board_from_url(job.application_tracking.application_url)
                
                # Check HTTP status
                if response.status == 404:
                    return VerificationResult(
                        job_id=job.job_id,
                        is_active=False,
                        response_code=404,
                        detection_method="http_404"
                    )
                
                # Check for closure patterns in response text
                patterns = self.closure_patterns.get(job_board, self.closure_patterns['generic'])
                for pattern in patterns:
                    if re.search(pattern, response_text, re.IGNORECASE):
                        return VerificationResult(
                            job_id=job.job_id,
                            is_active=False,
                            response_code=response.status,
                            detection_method=f"pattern_match_{job_board}"
                        )
                
                # If we get here, job appears to still be active
                return VerificationResult(
                    job_id=job.job_id,
                    is_active=True,
                    response_code=response.status,
                    detection_method="content_check"
                )
                
        except asyncio.TimeoutError:
            return VerificationResult(
                job_id=job.job_id,
                is_active=False,
                error_message="Request timeout",
                detection_method="timeout_error"
            )
        except Exception as e:
            return VerificationResult(
                job_id=job.job_id,
                is_active=False,
                error_message=str(e),
                detection_method="request_error"
            )
    
    async def verify_jobs_batch(self, jobs: List[Job]) -> List[VerificationResult]:
        """Verify multiple jobs concurrently with rate limiting"""
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def verify_with_semaphore(job: Job) -> VerificationResult:
            async with semaphore:
                return await self.verify_single_job(job)
        
        tasks = [verify_with_semaphore(job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        verification_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                verification_results.append(VerificationResult(
                    job_id=jobs[i].job_id,
                    is_active=False,
                    error_message=str(result),
                    detection_method="exception"
                ))
            else:
                verification_results.append(result)
        
        return verification_results
    
    def update_job_status(self, job: Job, verification_result: VerificationResult) -> bool:
        """Update job status based on verification result"""
        job.record_verification_attempt(
            success=verification_result.is_active,
            error_message=verification_result.error_message
        )
        
        if not verification_result.is_active and job.status_tracking.is_active:
            # Job was active but is now closed
            closure_reason = self._determine_closure_reason(verification_result)
            job.mark_as_closed(
                closure_reason=closure_reason,
                detection_method=verification_result.detection_method
            )
            return True  # Status changed
        
        return False  # No status change
    
    def _determine_closure_reason(self, verification_result: VerificationResult) -> str:
        """Determine closure reason from verification result"""
        if verification_result.response_code == 404:
            return "expired"
        elif "pattern_match" in verification_result.detection_method:
            return "filled"
        elif "timeout" in verification_result.detection_method:
            return "unreachable"
        elif verification_result.error_message:
            return "error"
        else:
            return "unknown"
    
    async def monitor_jobs(self, jobs: List[Job]) -> Tuple[List[Job], MonitoringStats]:
        """Monitor a list of jobs and return updated jobs with statistics"""
        # Filter jobs that need verification
        jobs_to_verify = [job for job in jobs if job.is_verification_needed()]
        
        if not jobs_to_verify:
            logger.info("No jobs need verification")
            return jobs, MonitoringStats()
        
        logger.info(f"Verifying {len(jobs_to_verify)} jobs")
        
        # Verify jobs in batches
        verification_results = await self.verify_jobs_batch(jobs_to_verify)
        
        # Update job statuses and collect statistics
        stats = MonitoringStats()
        stats.total_jobs_checked = len(jobs_to_verify)
        
        updated_jobs = jobs.copy()
        for job, result in zip(jobs_to_verify, verification_results):
            # Find the job in the updated list and update it
            job_index = next(i for i, j in enumerate(updated_jobs) if j.job_id == job.job_id)
            status_changed = self.update_job_status(updated_jobs[job_index], result)
            
            # Update statistics
            if result.is_active:
                stats.active_jobs_found += 1
            else:
                stats.closed_jobs_detected += 1
                if status_changed:
                    closure_reason = updated_jobs[job_index].status_tracking.closure_reason
                    stats.jobs_by_closure_reason[closure_reason] = stats.jobs_by_closure_reason.get(closure_reason, 0) + 1
            
            if result.error_message:
                stats.verification_errors += 1
        
        # Calculate average posting duration for closed jobs
        closed_jobs_with_duration = [
            job for job in updated_jobs 
            if not job.status_tracking.is_active and job.status_tracking.posting_duration_days
        ]
        
        if closed_jobs_with_duration:
            total_duration = sum(job.status_tracking.posting_duration_days for job in closed_jobs_with_duration)
            stats.average_posting_duration = total_duration / len(closed_jobs_with_duration)
        
        return updated_jobs, stats
    
    def get_jobs_needing_verification(self, jobs: List[Job], max_age_days: int = 7) -> List[Job]:
        """Get list of jobs that need verification"""
        return [job for job in jobs if job.is_verification_needed(max_age_days)]
    
    def get_monitoring_report(self, jobs: List[Job]) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        active_jobs = [job for job in jobs if job.status_tracking.is_active]
        closed_jobs = [job for job in jobs if not job.status_tracking.is_active]
        
        # Calculate posting duration statistics
        durations = [job.status_tracking.posting_duration_days for job in closed_jobs if job.status_tracking.posting_duration_days]
        
        return {
            'summary': {
                'total_jobs': len(jobs),
                'active_jobs': len(active_jobs),
                'closed_jobs': len(closed_jobs),
                'jobs_needing_verification': len(self.get_jobs_needing_verification(jobs))
            },
            'posting_duration_stats': {
                'average_days': sum(durations) / len(durations) if durations else 0,
                'min_days': min(durations) if durations else 0,
                'max_days': max(durations) if durations else 0,
                'total_jobs_with_duration': len(durations)
            },
            'closure_reasons': {
                reason: len([job for job in closed_jobs if job.status_tracking.closure_reason == reason])
                for reason in set(job.status_tracking.closure_reason for job in closed_jobs if job.status_tracking.closure_reason)
            },
            'verification_stats': {
                'total_attempts': sum(job.status_tracking.verification_attempts for job in jobs),
                'total_failures': sum(job.status_tracking.verification_failures for job in jobs),
                'jobs_with_failures': len([job for job in jobs if job.status_tracking.verification_failures > 0])
            },
            'age_distribution': {
                '0-7_days': len([job for job in active_jobs if job.get_posting_age_days() <= 7]),
                '8-14_days': len([job for job in active_jobs if 8 <= job.get_posting_age_days() <= 14]),
                '15-30_days': len([job for job in active_jobs if 15 <= job.get_posting_age_days() <= 30]),
                '30+_days': len([job for job in active_jobs if job.get_posting_age_days() > 30])
            }
        }


# Utility functions for scheduled monitoring

async def run_daily_job_monitoring(jobs: List[Job]) -> Tuple[List[Job], Dict[str, Any]]:
    """Run daily job monitoring routine"""
    async with JobStatusMonitor() as monitor:
        updated_jobs, stats = await monitor.monitor_jobs(jobs)
        report = monitor.get_monitoring_report(updated_jobs)
        
        logger.info(f"Daily monitoring complete: {stats.total_jobs_checked} jobs checked, "
                   f"{stats.closed_jobs_detected} closures detected")
        
        return updated_jobs, report


def create_monitoring_schedule(jobs: List[Job], max_age_days: int = 7) -> List[Job]:
    """Create optimized monitoring schedule based on job age and verification history"""
    # Prioritize jobs that haven't been verified recently
    jobs_by_priority = sorted(jobs, key=lambda job: (
        job.status_tracking.verification_failures,  # Failed verifications first
        -job.get_posting_age_days(),  # Older jobs first
        job.status_tracking.last_verified_active or datetime.min  # Never verified first
    ))
    
    return [job for job in jobs_by_priority if job.is_verification_needed(max_age_days)]
