"""
Daily Job Monitoring Script
Checks job posting status, detects closures, and runs repost analysis
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from dataclasses import dataclass
import json

from .job_data_model import Job, JobStatus
from .job_repost_detector import JobRepostDetector, analyze_all_companies

logger = logging.getLogger(__name__)


@dataclass
class JobVerificationResult:
    """Result of job posting verification"""
    job_id: str
    is_active: bool
    verification_method: str
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    verified_at: datetime = None
    
    def __post_init__(self):
        if self.verified_at is None:
            self.verified_at = datetime.now()


@dataclass
class MonitoringReport:
    """Daily monitoring report"""
    report_date: datetime
    total_jobs_checked: int
    active_jobs: int
    newly_closed_jobs: int
    verification_errors: int
    repost_clusters_detected: int
    companies_flagged: int
    processing_time_seconds: float
    alerts_generated: List[str]


class DailyJobMonitor:
    """Service for daily job posting monitoring and analysis"""
    
    def __init__(self, max_concurrent_checks: int = 10):
        self.max_concurrent_checks = max_concurrent_checks
        self.repost_detector = JobRepostDetector()
        
        # Verification methods by job board
        self.verification_methods = {
            'greenhouse': self._verify_greenhouse_job,
            'lever': self._verify_lever_job,
            'smartrecruiters': self._verify_smartrecruiters_job,
            'workable': self._verify_workable_job,
            'indeed': self._verify_indeed_job,
            'linkedin': self._verify_linkedin_job,
            'generic': self._verify_generic_job
        }
    
    async def _verify_greenhouse_job(self, job: Job) -> JobVerificationResult:
        """Verify Greenhouse job posting status"""
        if not job.external_url:
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method='greenhouse',
                error_message="No external URL available"
            )
        
        try:
            # Check if job page is accessible
            response = requests.get(job.external_url, timeout=10, allow_redirects=True)
            
            # Greenhouse typically returns 404 for closed jobs
            if response.status_code == 404:
                return JobVerificationResult(
                    job_id=job.job_id,
                    is_active=False,
                    verification_method='greenhouse',
                    response_code=404
                )
            
            # Check for "no longer accepting applications" text
            if response.status_code == 200:
                content = response.text.lower()
                closed_indicators = [
                    'no longer accepting applications',
                    'this job is no longer available',
                    'position has been filled',
                    'job posting has expired'
                ]
                
                for indicator in closed_indicators:
                    if indicator in content:
                        return JobVerificationResult(
                            job_id=job.job_id,
                            is_active=False,
                            verification_method='greenhouse',
                            response_code=200
                        )
                
                return JobVerificationResult(
                    job_id=job.job_id,
                    is_active=True,
                    verification_method='greenhouse',
                    response_code=200
                )
            
            # Other status codes indicate potential issues
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method='greenhouse',
                response_code=response.status_code,
                error_message=f"Unexpected status code: {response.status_code}"
            )
            
        except requests.RequestException as e:
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method='greenhouse',
                error_message=str(e)
            )
    
    async def _verify_lever_job(self, job: Job) -> JobVerificationResult:
        """Verify Lever job posting status"""
        if not job.external_url:
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method='lever',
                error_message="No external URL available"
            )
        
        try:
            response = requests.get(job.external_url, timeout=10)
            
            if response.status_code == 404:
                return JobVerificationResult(
                    job_id=job.job_id,
                    is_active=False,
                    verification_method='lever',
                    response_code=404
                )
            
            if response.status_code == 200:
                content = response.text.lower()
                if 'this job is no longer available' in content or 'position filled' in content:
                    return JobVerificationResult(
                        job_id=job.job_id,
                        is_active=False,
                        verification_method='lever',
                        response_code=200
                    )
                
                return JobVerificationResult(
                    job_id=job.job_id,
                    is_active=True,
                    verification_method='lever',
                    response_code=200
                )
            
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method='lever',
                response_code=response.status_code
            )
            
        except requests.RequestException as e:
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method='lever',
                error_message=str(e)
            )
    
    async def _verify_smartrecruiters_job(self, job: Job) -> JobVerificationResult:
        """Verify SmartRecruiters job posting status"""
        # Similar implementation to Greenhouse/Lever
        return await self._verify_generic_job(job, 'smartrecruiters')
    
    async def _verify_workable_job(self, job: Job) -> JobVerificationResult:
        """Verify Workable job posting status"""
        return await self._verify_generic_job(job, 'workable')
    
    async def _verify_indeed_job(self, job: Job) -> JobVerificationResult:
        """Verify Indeed job posting status"""
        return await self._verify_generic_job(job, 'indeed')
    
    async def _verify_linkedin_job(self, job: Job) -> JobVerificationResult:
        """Verify LinkedIn job posting status"""
        return await self._verify_generic_job(job, 'linkedin')
    
    async def _verify_generic_job(self, job: Job, platform: str = 'generic') -> JobVerificationResult:
        """Generic job verification for unknown platforms"""
        if not job.external_url:
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method=platform,
                error_message="No external URL available"
            )
        
        try:
            response = requests.get(job.external_url, timeout=10, allow_redirects=True)
            
            # Most platforms return 404 for removed jobs
            if response.status_code == 404:
                return JobVerificationResult(
                    job_id=job.job_id,
                    is_active=False,
                    verification_method=platform,
                    response_code=404
                )
            
            # Check for common closure indicators
            if response.status_code == 200:
                content = response.text.lower()
                closed_indicators = [
                    'no longer accepting',
                    'job is no longer',
                    'position has been filled',
                    'posting has expired',
                    'application deadline has passed',
                    'this opportunity is closed'
                ]
                
                for indicator in closed_indicators:
                    if indicator in content:
                        return JobVerificationResult(
                            job_id=job.job_id,
                            is_active=False,
                            verification_method=platform,
                            response_code=200
                        )
                
                return JobVerificationResult(
                    job_id=job.job_id,
                    is_active=True,
                    verification_method=platform,
                    response_code=200
                )
            
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method=platform,
                response_code=response.status_code
            )
            
        except requests.RequestException as e:
            return JobVerificationResult(
                job_id=job.job_id,
                is_active=False,
                verification_method=platform,
                error_message=str(e)
            )
    
    async def verify_job_status(self, job: Job) -> JobVerificationResult:
        """Verify the status of a single job posting"""
        # Determine verification method based on job source
        job_source = job.source.lower() if job.source else 'generic'
        
        verification_method = self.verification_methods.get(
            job_source, 
            self.verification_methods['generic']
        )
        
        return await verification_method(job)
    
    async def verify_jobs_batch(self, jobs: List[Job]) -> List[JobVerificationResult]:
        """Verify multiple jobs concurrently"""
        semaphore = asyncio.Semaphore(self.max_concurrent_checks)
        
        async def verify_with_semaphore(job):
            async with semaphore:
                return await self.verify_job_status(job)
        
        tasks = [verify_with_semaphore(job) for job in jobs]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def update_job_status(self, job: Job, verification_result: JobVerificationResult) -> Job:
        """Update job record based on verification result"""
        # Update verification tracking
        job.verification_attempts = (job.verification_attempts or 0) + 1
        job.last_verification_attempt = verification_result.verified_at
        
        if verification_result.error_message:
            job.verification_failures = (job.verification_failures or 0) + 1
            job.last_verification_error = verification_result.error_message
        
        # Update job status if changed
        if not verification_result.is_active and job.is_active:
            # Job was closed
            job.is_active = False
            job.closed_date = verification_result.verified_at
            job.status = JobStatus.CLOSED
            
            # Determine closure reason
            if verification_result.response_code == 404:
                job.closure_reason = 'expired'
            elif verification_result.error_message:
                job.closure_reason = 'verification_failed'
            else:
                job.closure_reason = 'filled'  # Assume filled if explicitly marked closed
            
            job.closure_detection_method = 'automated_check'
            
            # Calculate posting duration
            if job.posted_date:
                duration = (verification_result.verified_at - job.posted_date).days
                job.posting_duration_days = duration
        
        elif verification_result.is_active:
            # Job is still active
            job.last_verified_active = verification_result.verified_at
        
        return job
    
    def analyze_company_reposts(self, jobs_by_company: Dict[str, List[Job]]) -> Dict[str, Any]:
        """Analyze repost patterns for all companies"""
        return analyze_all_companies(jobs_by_company)
    
    def generate_monitoring_alerts(self, 
                                 verification_results: List[JobVerificationResult],
                                 repost_analytics: Dict[str, Any]) -> List[str]:
        """Generate alerts based on monitoring results"""
        alerts = []
        
        # Job verification alerts
        failed_verifications = [r for r in verification_results if r.error_message]
        if len(failed_verifications) > 10:
            alerts.append(f"High verification failure rate: {len(failed_verifications)} jobs failed verification")
        
        newly_closed = [r for r in verification_results if not r.is_active]
        if len(newly_closed) > 20:
            alerts.append(f"High job closure rate: {len(newly_closed)} jobs closed today")
        
        # Repost pattern alerts
        problematic_companies = []
        for company_id, analytics in repost_analytics.items():
            if analytics.quality_rating in ['avoid', 'poor']:
                problematic_companies.append(analytics.company_name)
        
        if problematic_companies:
            alerts.append(f"Companies with repost dysfunction detected: {', '.join(problematic_companies[:5])}")
        
        return alerts
    
    async def run_daily_monitoring(self, active_jobs: List[Job]) -> MonitoringReport:
        """Run complete daily monitoring workflow"""
        start_time = datetime.now()
        
        logger.info(f"Starting daily job monitoring for {len(active_jobs)} jobs")
        
        # Verify job statuses
        verification_results = await self.verify_jobs_batch(active_jobs)
        
        # Filter out exceptions
        valid_results = [r for r in verification_results if isinstance(r, JobVerificationResult)]
        
        # Update job records
        updated_jobs = []
        for job, result in zip(active_jobs, valid_results):
            updated_job = self.update_job_status(job, result)
            updated_jobs.append(updated_job)
        
        # Group jobs by company for repost analysis
        jobs_by_company = {}
        for job in updated_jobs:
            if job.company_id not in jobs_by_company:
                jobs_by_company[job.company_id] = []
            jobs_by_company[job.company_id].append(job)
        
        # Analyze repost patterns
        repost_analytics = self.analyze_company_reposts(jobs_by_company)
        
        # Generate alerts
        alerts = self.generate_monitoring_alerts(valid_results, repost_analytics)
        
        # Calculate metrics
        active_count = len([r for r in valid_results if r.is_active])
        closed_count = len([r for r in valid_results if not r.is_active])
        error_count = len([r for r in valid_results if r.error_message])
        
        repost_clusters = sum(len(analytics.repost_clusters) for analytics in repost_analytics.values())
        flagged_companies = len([a for a in repost_analytics.values() if a.quality_rating in ['avoid', 'poor']])
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        report = MonitoringReport(
            report_date=start_time,
            total_jobs_checked=len(valid_results),
            active_jobs=active_count,
            newly_closed_jobs=closed_count,
            verification_errors=error_count,
            repost_clusters_detected=repost_clusters,
            companies_flagged=flagged_companies,
            processing_time_seconds=processing_time,
            alerts_generated=alerts
        )
        
        logger.info(f"Daily monitoring completed: {report.total_jobs_checked} jobs checked, "
                   f"{report.newly_closed_jobs} newly closed, {report.companies_flagged} companies flagged")
        
        return report
    
    def save_monitoring_report(self, report: MonitoringReport, filepath: str = None):
        """Save monitoring report to file"""
        if not filepath:
            date_str = report.report_date.strftime("%Y%m%d")
            filepath = f"daily_monitoring_report_{date_str}.json"
        
        report_data = {
            'report_date': report.report_date.isoformat(),
            'total_jobs_checked': report.total_jobs_checked,
            'active_jobs': report.active_jobs,
            'newly_closed_jobs': report.newly_closed_jobs,
            'verification_errors': report.verification_errors,
            'repost_clusters_detected': report.repost_clusters_detected,
            'companies_flagged': report.companies_flagged,
            'processing_time_seconds': report.processing_time_seconds,
            'alerts_generated': report.alerts_generated
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Monitoring report saved to {filepath}")


# CLI interface for running monitoring
async def main():
    """Main function for running daily monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run daily job monitoring')
    parser.add_argument('--max-concurrent', type=int, default=10,
                       help='Maximum concurrent job checks')
    parser.add_argument('--output', type=str,
                       help='Output file for monitoring report')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = DailyJobMonitor(max_concurrent_checks=args.max_concurrent)
    
    # TODO: Load active jobs from database
    # For now, using empty list as placeholder
    active_jobs = []
    
    # Run monitoring
    report = await monitor.run_daily_monitoring(active_jobs)
    
    # Save report
    monitor.save_monitoring_report(report, args.output)
    
    # Print summary
    print(f"Daily Monitoring Report - {report.report_date.strftime('%Y-%m-%d')}")
    print(f"Jobs Checked: {report.total_jobs_checked}")
    print(f"Active Jobs: {report.active_jobs}")
    print(f"Newly Closed: {report.newly_closed_jobs}")
    print(f"Verification Errors: {report.verification_errors}")
    print(f"Repost Clusters: {report.repost_clusters_detected}")
    print(f"Companies Flagged: {report.companies_flagged}")
    print(f"Processing Time: {report.processing_time_seconds:.2f}s")
    
    if report.alerts_generated:
        print("\nAlerts:")
        for alert in report.alerts_generated:
            print(f"  - {alert}")


if __name__ == "__main__":
    asyncio.run(main())
