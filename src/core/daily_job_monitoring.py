"""
Daily Job Monitoring System
Handles job status monitoring, repost detection, multi-source tracking, and analytics
"""

import asyncio
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests
from urllib.parse import urljoin, urlparse
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from job_data_model import Job, JobStatus, JobSource, RepostDetection
from white_collar_job_classifier import WhiteCollarJobClassifier
from northern_california_geo_filter import NorthernCaliforniaGeoFilter

logger = logging.getLogger(__name__)


@dataclass
class MonitoringResult:
    """Result of daily monitoring operations"""
    jobs_checked: int = 0
    jobs_closed: int = 0
    reposts_detected: int = 0
    sources_verified: int = 0
    companies_flagged: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class JobStatusMonitor:
    """Monitors job posting status across multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    async def check_job_status(self, job: Job) -> Tuple[bool, str]:
        """Check if a job posting is still active"""
        try:
            # Check primary source first
            if job.primary_source:
                is_active, reason = await self._check_source_status(job.primary_source)
                if not is_active:
                    return False, reason
            
            # Check secondary sources
            for source in job.sources:
                if source != job.primary_source and source.is_active:
                    is_active, reason = await self._check_source_status(source)
                    if not is_active:
                        source.is_active = False
                        source.last_verified = datetime.now()
            
            return True, "active"
            
        except Exception as e:
            logger.error(f"Error checking job status for {job.job_id}: {e}")
            return True, f"check_failed: {str(e)}"
    
    async def _check_source_status(self, source: JobSource) -> Tuple[bool, str]:
        """Check if a specific source is still active"""
        try:
            response = self.session.get(source.source_url, timeout=10)
            
            # Common indicators that job is no longer available
            inactive_indicators = [
                "job not found",
                "position no longer available",
                "this job has expired",
                "404",
                "page not found",
                "job has been filled",
                "no longer accepting applications"
            ]
            
            content_lower = response.text.lower()
            
            for indicator in inactive_indicators:
                if indicator in content_lower:
                    return False, f"inactive_indicator: {indicator}"
            
            # Check for redirect to general careers page
            if response.url != source.source_url:
                parsed_original = urlparse(source.source_url)
                parsed_final = urlparse(response.url)
                
                if (parsed_original.netloc == parsed_final.netloc and 
                    'careers' in parsed_final.path and 
                    'job' not in parsed_final.path):
                    return False, "redirected_to_careers"
            
            # Check HTTP status
            if response.status_code == 404:
                return False, "http_404"
            elif response.status_code >= 400:
                return False, f"http_error: {response.status_code}"
            
            return True, "active"
            
        except requests.RequestException as e:
            logger.warning(f"Request failed for {source.source_url}: {e}")
            return True, f"request_failed: {str(e)}"


class RepostDetector:
    """Detects job reposts and clusters similar jobs"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.similarity_thresholds = {
            'title': 0.8,
            'description': 0.7,
            'requirements': 0.75,
            'overall': 0.7
        }
    
    def detect_reposts(self, new_job: Job, existing_jobs: List[Job]) -> Optional[Dict[str, Any]]:
        """Detect if a new job is a repost of existing jobs"""
        
        # Filter to same company jobs that are closed
        company_jobs = [
            job for job in existing_jobs 
            if (job.company_name.lower() == new_job.company_name.lower() and 
                job.status == JobStatus.CLOSED and
                job.job_id != new_job.job_id)
        ]
        
        if not company_jobs:
            return None
        
        best_match = None
        highest_similarity = 0.0
        
        for existing_job in company_jobs:
            similarity_scores = self._calculate_similarity(new_job, existing_job)
            overall_similarity = similarity_scores['overall']
            
            if (overall_similarity > self.similarity_thresholds['overall'] and 
                overall_similarity > highest_similarity):
                
                highest_similarity = overall_similarity
                best_match = {
                    'original_job_id': existing_job.job_id,
                    'similarity_scores': similarity_scores,
                    'days_since_original': (new_job.created_at - existing_job.created_at).days,
                    'original_posting_duration': existing_job.status_tracking.posting_duration_days
                }
        
        return best_match
    
    def _calculate_similarity(self, job1: Job, job2: Job) -> Dict[str, float]:
        """Calculate similarity scores between two jobs"""
        
        # Title similarity
        title_similarity = self._text_similarity(job1.title, job2.title)
        
        # Description similarity
        desc_similarity = self._text_similarity(job1.description, job2.description)
        
        # Requirements similarity
        req1 = ' '.join(job1.requirements.skills_required + job1.requirements.skills_preferred)
        req2 = ' '.join(job2.requirements.skills_required + job2.requirements.skills_preferred)
        req_similarity = self._text_similarity(req1, req2)
        
        # Overall similarity (weighted average)
        overall_similarity = (
            title_similarity * 0.4 +
            desc_similarity * 0.4 +
            req_similarity * 0.2
        )
        
        return {
            'title': title_similarity,
            'description': desc_similarity,
            'requirements': req_similarity,
            'overall': overall_similarity
        }
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        if not text1 or not text2:
            return 0.0
        
        try:
            # Use TF-IDF vectorization
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            # Fallback to simple string similarity
            return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


class MultiSourceTracker:
    """Tracks jobs across multiple sources and detects content changes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    async def verify_sources(self, job: Job) -> List[Dict[str, Any]]:
        """Verify all sources for a job and detect content changes"""
        results = []
        
        for source in job.sources:
            try:
                result = await self._verify_single_source(job, source)
                results.append(result)
            except Exception as e:
                logger.error(f"Error verifying source {source.source_url}: {e}")
                results.append({
                    'source_id': source.source_url,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    async def _verify_single_source(self, job: Job, source: JobSource) -> Dict[str, Any]:
        """Verify a single source and detect content changes"""
        try:
            response = self.session.get(source.source_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'source_id': source.source_url,
                    'status': 'inactive',
                    'reason': f'http_status_{response.status_code}'
                }
            
            # Calculate content hash
            content_hash = hashlib.sha256(response.text.encode()).hexdigest()
            
            # Check for content changes
            content_changed = (source.content_hash and 
                             source.content_hash != content_hash)
            
            result = {
                'source_id': source.source_url,
                'status': 'active',
                'content_changed': content_changed,
                'content_hash': content_hash,
                'last_verified': datetime.now().isoformat()
            }
            
            if content_changed:
                # Detect specific changes
                changes = self._detect_content_changes(job, response.text)
                result['changes'] = changes
            
            # Update source
            source.content_hash = content_hash
            source.last_verified = datetime.now()
            source.last_content_check = datetime.now()
            
            return result
            
        except Exception as e:
            return {
                'source_id': source.source_url,
                'status': 'error',
                'error': str(e)
            }
    
    def _detect_content_changes(self, job: Job, new_content: str) -> List[Dict[str, str]]:
        """Detect specific content changes in job posting"""
        changes = []
        
        # This would involve more sophisticated content parsing
        # For now, we'll detect major changes
        
        # Check if salary information changed
        salary_keywords = ['salary', '$', 'compensation', 'pay']
        if any(keyword in new_content.lower() for keyword in salary_keywords):
            changes.append({
                'field': 'compensation',
                'change_type': 'modified',
                'description': 'Salary information may have changed'
            })
        
        # Check if requirements changed
        req_keywords = ['required', 'must have', 'qualifications', 'experience']
        if any(keyword in new_content.lower() for keyword in req_keywords):
            changes.append({
                'field': 'requirements',
                'change_type': 'modified',
                'description': 'Job requirements may have changed'
            })
        
        return changes


class CompanyQualityAnalyzer:
    """Analyzes company hiring quality based on repost patterns"""
    
    def __init__(self):
        self.quality_thresholds = {
            'green': {'repost_rate': 0.1, 'avg_duration': 30},
            'yellow': {'repost_rate': 0.25, 'avg_duration': 14},
            'red': {'repost_rate': 0.4, 'avg_duration': 7}
        }
    
    def analyze_company_quality(self, company_jobs: List[Job]) -> Dict[str, Any]:
        """Analyze company hiring quality based on job patterns"""
        
        if not company_jobs:
            return {'quality_flag': 'unknown', 'reason': 'no_data'}
        
        total_jobs = len(company_jobs)
        reposts = sum(1 for job in company_jobs if job.repost_detection.is_repost)
        repost_rate = reposts / total_jobs if total_jobs > 0 else 0
        
        # Calculate average posting duration
        durations = [
            job.status_tracking.posting_duration_days 
            for job in company_jobs 
            if job.status_tracking.posting_duration_days
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Determine quality flag
        quality_flag = 'green'
        reasons = []
        
        if repost_rate > self.quality_thresholds['red']['repost_rate']:
            quality_flag = 'red'
            reasons.append(f'high_repost_rate: {repost_rate:.2%}')
        elif repost_rate > self.quality_thresholds['yellow']['repost_rate']:
            quality_flag = 'yellow'
            reasons.append(f'moderate_repost_rate: {repost_rate:.2%}')
        
        if avg_duration < self.quality_thresholds['red']['avg_duration']:
            quality_flag = 'red'
            reasons.append(f'very_short_duration: {avg_duration:.1f} days')
        elif avg_duration < self.quality_thresholds['yellow']['avg_duration']:
            if quality_flag == 'green':
                quality_flag = 'yellow'
            reasons.append(f'short_duration: {avg_duration:.1f} days')
        
        return {
            'quality_flag': quality_flag,
            'repost_rate': repost_rate,
            'avg_posting_duration': avg_duration,
            'total_jobs': total_jobs,
            'total_reposts': reposts,
            'reasons': reasons
        }


class DailyJobMonitor:
    """Main daily monitoring orchestrator"""
    
    def __init__(self):
        self.status_monitor = JobStatusMonitor()
        self.repost_detector = RepostDetector()
        self.source_tracker = MultiSourceTracker()
        self.quality_analyzer = CompanyQualityAnalyzer()
        self.white_collar_classifier = WhiteCollarJobClassifier()
        self.geo_filter = NorthernCaliforniaGeoFilter()
    
    async def run_daily_monitoring(self, jobs: List[Job]) -> MonitoringResult:
        """Run complete daily monitoring workflow"""
        result = MonitoringResult()
        
        logger.info(f"Starting daily monitoring for {len(jobs)} jobs")
        
        try:
            # Step 1: Check job status
            await self._monitor_job_status(jobs, result)
            
            # Step 2: Detect reposts
            await self._detect_reposts(jobs, result)
            
            # Step 3: Verify multi-source tracking
            await self._verify_sources(jobs, result)
            
            # Step 4: Classify white collar jobs
            await self._classify_jobs(jobs, result)
            
            # Step 5: Analyze company quality
            await self._analyze_company_quality(jobs, result)
            
            logger.info(f"Daily monitoring completed: {result}")
            
        except Exception as e:
            logger.error(f"Daily monitoring failed: {e}")
            result.errors.append(f"monitoring_failed: {str(e)}")
        
        return result
    
    async def _monitor_job_status(self, jobs: List[Job], result: MonitoringResult):
        """Monitor job posting status"""
        active_jobs = [job for job in jobs if job.status == JobStatus.OPEN]
        
        for job in active_jobs:
            try:
                is_active, reason = await self.status_monitor.check_job_status(job)
                result.jobs_checked += 1
                
                if not is_active:
                    job.mark_as_closed(reason, "automated_check")
                    result.jobs_closed += 1
                    logger.info(f"Job {job.job_id} marked as closed: {reason}")
                
                # Record verification attempt
                job.record_verification_attempt(is_active, None if is_active else reason)
                
            except Exception as e:
                logger.error(f"Error monitoring job {job.job_id}: {e}")
                result.errors.append(f"status_check_failed: {job.job_id}")
    
    async def _detect_reposts(self, jobs: List[Job], result: MonitoringResult):
        """Detect job reposts"""
        new_jobs = [job for job in jobs if not job.repost_detection.is_repost]
        existing_jobs = [job for job in jobs if job.job_id not in [j.job_id for j in new_jobs]]
        
        for new_job in new_jobs:
            try:
                repost_match = self.repost_detector.detect_reposts(new_job, existing_jobs)
                
                if repost_match:
                    new_job.mark_as_repost(
                        repost_match['original_job_id'],
                        repost_match['similarity_scores']
                    )
                    result.reposts_detected += 1
                    logger.info(f"Repost detected: {new_job.job_id} -> {repost_match['original_job_id']}")
                
            except Exception as e:
                logger.error(f"Error detecting reposts for {new_job.job_id}: {e}")
                result.errors.append(f"repost_detection_failed: {new_job.job_id}")
    
    async def _verify_sources(self, jobs: List[Job], result: MonitoringResult):
        """Verify multi-source tracking"""
        for job in jobs:
            if job.sources:
                try:
                    source_results = await self.source_tracker.verify_sources(job)
                    result.sources_verified += len(source_results)
                    
                    # Log any content changes
                    for source_result in source_results:
                        if source_result.get('content_changed'):
                            logger.info(f"Content changed for job {job.job_id} at {source_result['source_id']}")
                
                except Exception as e:
                    logger.error(f"Error verifying sources for {job.job_id}: {e}")
                    result.errors.append(f"source_verification_failed: {job.job_id}")
    
    async def _classify_jobs(self, jobs: List[Job], result: MonitoringResult):
        """Classify white collar jobs and set geographic data"""
        unclassified_jobs = [
            job for job in jobs 
            if not job.white_collar_classification.is_white_collar and 
               job.white_collar_classification.confidence_score == 0.0
        ]
        
        for job in unclassified_jobs:
            try:
                # White collar classification
                classification_result = self.white_collar_classifier.classify_job(job)
                job.classify_white_collar(
                    classification_result['is_white_collar'],
                    classification_result['confidence'],
                    classification_result.get('category'),
                    classification_result.get('keywords')
                )
                
                # Geographic classification
                geo_result = self.geo_filter.classify_location(job.location)
                job.set_geographic_data(
                    geo_result['is_northern_california'],
                    geo_result.get('region'),
                    job.location.postal_code,
                    geo_result.get('transit_accessible', False)
                )
                
            except Exception as e:
                logger.error(f"Error classifying job {job.job_id}: {e}")
                result.errors.append(f"classification_failed: {job.job_id}")
    
    async def _analyze_company_quality(self, jobs: List[Job], result: MonitoringResult):
        """Analyze company quality based on hiring patterns"""
        companies = {}
        
        # Group jobs by company
        for job in jobs:
            company_name = job.company_name.lower()
            if company_name not in companies:
                companies[company_name] = []
            companies[company_name].append(job)
        
        # Analyze each company
        for company_name, company_jobs in companies.items():
            try:
                quality_analysis = self.quality_analyzer.analyze_company_quality(company_jobs)
                
                # Update quality flags for all jobs from this company
                for job in company_jobs:
                    job.repost_detection.company_quality_flag = quality_analysis['quality_flag']
                    job.repost_detection.company_repost_count = quality_analysis['total_reposts']
                    job.repost_detection.company_repost_frequency = quality_analysis['repost_rate']
                
                if quality_analysis['quality_flag'] in ['yellow', 'red']:
                    result.companies_flagged += 1
                    logger.warning(f"Company flagged: {company_name} - {quality_analysis['quality_flag']}")
                
            except Exception as e:
                logger.error(f"Error analyzing company quality for {company_name}: {e}")
                result.errors.append(f"company_analysis_failed: {company_name}")


# Utility functions for integration

async def run_daily_monitoring_for_jobs(jobs: List[Job]) -> MonitoringResult:
    """Run daily monitoring for a list of jobs"""
    monitor = DailyJobMonitor()
    return await monitor.run_daily_monitoring(jobs)


def generate_monitoring_report(result: MonitoringResult) -> str:
    """Generate a human-readable monitoring report"""
    report = f"""
Daily Job Monitoring Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
- Jobs Checked: {result.jobs_checked}
- Jobs Closed: {result.jobs_closed}
- Reposts Detected: {result.reposts_detected}
- Sources Verified: {result.sources_verified}
- Companies Flagged: {result.companies_flagged}

"""
    
    if result.errors:
        report += f"ERRORS ({len(result.errors)}):\n"
        for error in result.errors:
            report += f"- {error}\n"
    else:
        report += "No errors encountered.\n"
    
    return report


if __name__ == "__main__":
    # Example usage
    async def main():
        # This would load jobs from your database
        jobs = []  # Load from database
        
        monitor = DailyJobMonitor()
        result = await monitor.run_daily_monitoring(jobs)
        
        print(generate_monitoring_report(result))
    
    asyncio.run(main())
