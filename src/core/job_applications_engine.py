#!/usr/bin/env python3
"""
Job Applications Engine

Core engine for automated job applications, manual application logging,
status tracking, and HubSpot CRM integration.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationStatus(Enum):
    """Application status enumeration"""
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_EXTENDED = "offer_extended"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    NO_RESPONSE = "no_response"
    GHOSTED = "ghosted"

class ApplicationMethod(Enum):
    """Application submission method"""
    AUTO_APPLY = "auto_apply"
    MANUAL_FORM = "manual_form"
    EMAIL = "email"
    COMPANY_WEBSITE = "company_website"
    JOB_BOARD = "job_board"
    REFERRAL = "referral"

@dataclass
class JobApplication:
    """Job application data structure"""
    application_id: str
    job_id: str
    company_id: str
    user_id: str
    job_title: str
    company_name: str
    resume_version_id: str
    cover_letter_id: Optional[str] = None
    application_method: ApplicationMethod = ApplicationMethod.MANUAL_FORM
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    submitted_at: str = None
    status_updated_at: str = None
    hubspot_deal_id: Optional[str] = None
    application_url: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.submitted_at is None:
            self.submitted_at = datetime.now().isoformat()
        if self.status_updated_at is None:
            self.status_updated_at = self.submitted_at
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ApplicationMetrics:
    """Application metrics and analytics"""
    total_applications: int
    applications_by_status: Dict[str, int]
    applications_by_method: Dict[str, int]
    applications_by_month: Dict[str, int]
    response_rate: float
    interview_rate: float
    offer_rate: float
    average_response_time_days: Optional[float]
    top_companies: List[Dict[str, Any]]
    top_job_titles: List[Dict[str, Any]]

class JobApplicationsEngine:
    """Core engine for job applications management"""
    
    def __init__(self):
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        # Initialize database service
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from integrations.supabase.job_applications_service import JobApplicationsService
            self.db_service = JobApplicationsService()
            logger.info("Database service initialized successfully")
        except ImportError as e:
            logger.warning(f"Database service not available: {e}")
            self.db_service = None
        
        # Initialize HubSpot integration
        try:
            from integrations.hubspot.job_applications_hubspot import JobApplicationsHubSpotService
            self.hubspot_service = JobApplicationsHubSpotService()
            logger.info("HubSpot service initialized successfully")
        except ImportError as e:
            logger.warning(f"HubSpot service not available: {e}")
            self.hubspot_service = None
        
        # Initialize other integrations (will be implemented)
        self.email_parser = None
        
        logger.info(f"Job Applications Engine initialized (demo_mode: {self.demo_mode})")
    
    def submit_application(self, job_data: Dict[str, Any], resume_version_id: str,
                          application_method: ApplicationMethod = ApplicationMethod.AUTO_APPLY,
                          cover_letter_id: Optional[str] = None,
                          notes: Optional[str] = None) -> JobApplication:
        """
        Submit a job application (auto or manual)
        
        Args:
            job_data: Job information dictionary
            resume_version_id: ID of resume version to use
            application_method: How the application was submitted
            cover_letter_id: Optional cover letter ID
            notes: Optional application notes
            
        Returns:
            JobApplication object with submission details
        """
        try:
            logger.info(f"Submitting application for {job_data.get('title', 'Unknown Job')}")
            
            # Generate application ID
            application_id = f"app_{int(datetime.now().timestamp())}"
            
            # Create application record
            application = JobApplication(
                application_id=application_id,
                job_id=job_data.get('job_id', f"job_{int(datetime.now().timestamp())}"),
                company_id=job_data.get('company_id', f"comp_{int(datetime.now().timestamp())}"),
                user_id="demo_user",  # Will be dynamic
                job_title=job_data.get('title', 'Unknown Job'),
                company_name=job_data.get('company_name', 'Unknown Company'),
                resume_version_id=resume_version_id,
                cover_letter_id=cover_letter_id,
                application_method=application_method,
                application_url=job_data.get('url'),
                source=job_data.get('source'),
                notes=notes,
                metadata={
                    'job_data': job_data,
                    'submission_timestamp': datetime.now().isoformat()
                }
            )
            
            # Submit application based on method
            if application_method == ApplicationMethod.AUTO_APPLY:
                success = self._auto_submit_application(application, job_data)
            else:
                success = self._log_manual_application(application)
            
            if success:
                # Create HubSpot deal
                deal_id = self._create_hubspot_deal(application)
                application.hubspot_deal_id = deal_id
                
                # Store application in database
                self._store_application(application)
                
                # Trigger downstream enrichment
                self._trigger_enrichment_flows(application)
                
                logger.info(f"Application submitted successfully: {application_id}")
                return application
            else:
                logger.error(f"Failed to submit application for {job_data.get('title')}")
                return None
                
        except Exception as e:
            logger.error(f"Application submission failed: {e}")
            return None
    
    def _auto_submit_application(self, application: JobApplication, job_data: Dict) -> bool:
        """Auto-submit application via job board API or email"""
        try:
            if self.demo_mode:
                logger.info(f"Demo mode: Would auto-submit to {application.company_name}")
                return True
            
            # Implementation for actual auto-submission
            # This would integrate with job board APIs (Greenhouse, Lever, etc.)
            # or send templated emails
            
            return True
            
        except Exception as e:
            logger.error(f"Auto-submission failed: {e}")
            return False
    
    def _log_manual_application(self, application: JobApplication) -> bool:
        """Log manually submitted application"""
        try:
            logger.info(f"Logging manual application to {application.company_name}")
            return True
            
        except Exception as e:
            logger.error(f"Manual application logging failed: {e}")
            return False
    
    def _create_hubspot_deal(self, application: JobApplication) -> Optional[str]:
        """Create HubSpot deal for application"""
        try:
            if self.hubspot_service:
                return self.hubspot_service.create_deal_for_application(application)
            else:
                deal_id = f"deal_{application.application_id}"
                logger.info(f"Demo mode: Would create HubSpot deal {deal_id}")
                return deal_id
            
        except Exception as e:
            logger.error(f"HubSpot deal creation failed: {e}")
            return None
    
    def _store_application(self, application: JobApplication) -> bool:
        """Store application in Supabase"""
        try:
            if self.db_service:
                return self.db_service.create_application(application)
            else:
                logger.info(f"Demo mode: Would store application {application.application_id}")
                return True
            
        except Exception as e:
            logger.error(f"Application storage failed: {e}")
            return False
    
    def _trigger_enrichment_flows(self, application: JobApplication) -> None:
        """Trigger downstream enrichment processes"""
        try:
            logger.info(f"Triggering enrichment flows for {application.application_id}")
            
            # Trigger company enrichment if needed
            # Trigger contact enrichment
            # Update tech classification
            
        except Exception as e:
            logger.error(f"Enrichment flow trigger failed: {e}")
    
    def update_application_status(self, application_id: str, new_status: ApplicationStatus,
                                 notes: Optional[str] = None) -> bool:
        """Update application status"""
        try:
            logger.info(f"Updating application {application_id} status to {new_status.value}")
            
            # Update in database
            db_success = True
            if self.db_service:
                db_success = self.db_service.update_application_status(application_id, new_status, notes)
            else:
                logger.info(f"Demo mode: Status updated to {new_status.value}")
            
            # Update HubSpot deal if database update succeeded
            if db_success:
                # Get application to find HubSpot deal ID
                if self.db_service:
                    application = self.db_service.get_application(application_id)
                    if application and application.hubspot_deal_id and self.hubspot_service:
                        self.hubspot_service.update_deal_stage(application.hubspot_deal_id, new_status, notes)
            
            return db_success
            
        except Exception as e:
            logger.error(f"Status update failed: {e}")
            return False
    
    def get_application_metrics(self, user_id: str = "demo_user") -> ApplicationMetrics:
        """Get application metrics and analytics"""
        try:
            if self.db_service:
                return self.db_service.get_application_metrics(user_id)
            else:
                return self._get_demo_metrics()
            
        except Exception as e:
            logger.error(f"Metrics retrieval failed: {e}")
            return None
    
    def _get_demo_metrics(self) -> ApplicationMetrics:
        """Generate demo metrics"""
        return ApplicationMetrics(
            total_applications=25,
            applications_by_status={
                "submitted": 10,
                "in_review": 5,
                "interview_scheduled": 3,
                "rejected": 6,
                "no_response": 1
            },
            applications_by_method={
                "auto_apply": 15,
                "manual_form": 8,
                "email": 2
            },
            applications_by_month={
                "2024-01": 8,
                "2024-02": 12,
                "2024-03": 5
            },
            response_rate=0.64,  # 64%
            interview_rate=0.12,  # 12%
            offer_rate=0.04,  # 4%
            average_response_time_days=7.5,
            top_companies=[
                {"name": "TechCorp", "applications": 3},
                {"name": "DataFlow", "applications": 2},
                {"name": "CloudScale", "applications": 2}
            ],
            top_job_titles=[
                {"title": "Software Engineer", "applications": 8},
                {"title": "Senior Developer", "applications": 5},
                {"title": "Tech Lead", "applications": 3}
            ]
        )
    
    def export_applications(self, user_id: str = "demo_user", 
                           filters: Optional[Dict] = None) -> List[Dict]:
        """Export application history"""
        try:
            logger.info(f"Exporting applications for user {user_id}")
            
            if self.db_service:
                # Get applications from database and convert to export format
                applications = self.db_service.get_user_applications(user_id)
                return [self._application_to_export_dict(app) for app in applications]
            else:
                return self._get_demo_export_data()
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return []
    
    def _application_to_export_dict(self, app: JobApplication) -> Dict:
        """Convert JobApplication to export dictionary format"""
        return {
            "application_id": app.application_id,
            "job_title": app.job_title,
            "company_name": app.company_name,
            "status": app.status.value,
            "submitted_at": app.submitted_at,
            "application_method": app.application_method.value,
            "resume_version": app.resume_version_id,
            "application_url": app.application_url,
            "source": app.source,
            "notes": app.notes,
            "hubspot_deal_id": app.hubspot_deal_id,
            "response_time_days": None  # Would calculate from status updates
        }
    
    def _get_demo_export_data(self) -> List[Dict]:
        """Generate demo export data"""
        return [
            {
                "application_id": "app_001",
                "job_title": "Senior Software Engineer",
                "company_name": "TechCorp",
                "status": "interview_scheduled",
                "submitted_at": "2024-01-15T10:30:00Z",
                "application_method": "auto_apply",
                "resume_version": "resume_v2_tech",
                "response_time_days": 5
            },
            {
                "application_id": "app_002", 
                "job_title": "Full Stack Developer",
                "company_name": "DataFlow",
                "status": "rejected",
                "submitted_at": "2024-01-20T14:15:00Z",
                "application_method": "manual_form",
                "resume_version": "resume_v1_general",
                "response_time_days": 12
            },
            {
                "application_id": "app_003",
                "job_title": "Tech Lead",
                "company_name": "CloudScale", 
                "status": "submitted",
                "submitted_at": "2024-02-01T09:00:00Z",
                "application_method": "auto_apply",
                "resume_version": "resume_v3_leadership",
                "response_time_days": None
            }
        ]

# Demo functions
def demo_job_applications():
    """Demo job applications functionality"""
    print("=== Job Applications Engine Demo ===")
    
    engine = JobApplicationsEngine()
    
    # Demo job data
    demo_jobs = [
        {
            "job_id": "job_001",
            "title": "Senior Software Engineer",
            "company_name": "TechCorp",
            "company_id": "comp_techcorp",
            "url": "https://techcorp.com/jobs/senior-engineer",
            "source": "company_website"
        },
        {
            "job_id": "job_002", 
            "title": "Full Stack Developer",
            "company_name": "DataFlow",
            "company_id": "comp_dataflow",
            "url": "https://dataflow.io/careers/fullstack",
            "source": "job_board"
        }
    ]
    
    print("\n1. Submitting Applications...")
    applications = []
    
    for job in demo_jobs:
        application = engine.submit_application(
            job_data=job,
            resume_version_id="resume_v2_optimized",
            application_method=ApplicationMethod.AUTO_APPLY,
            notes="Auto-submitted via job search automation"
        )
        
        if application:
            applications.append(application)
            print(f"  ✅ Applied to {job['title']} at {job['company_name']}")
            print(f"     Application ID: {application.application_id}")
            print(f"     HubSpot Deal: {application.hubspot_deal_id}")
    
    print(f"\n2. Application Status Updates...")
    if applications:
        # Update status of first application
        engine.update_application_status(
            applications[0].application_id,
            ApplicationStatus.INTERVIEW_SCHEDULED,
            "Interview scheduled for next week"
        )
        print(f"  ✅ Updated {applications[0].job_title} status to interview_scheduled")
    
    print(f"\n3. Application Metrics...")
    metrics = engine.get_application_metrics()
    if metrics:
        print(f"  Total Applications: {metrics.total_applications}")
        print(f"  Response Rate: {metrics.response_rate:.1%}")
        print(f"  Interview Rate: {metrics.interview_rate:.1%}")
        print(f"  Average Response Time: {metrics.average_response_time_days} days")
        print(f"  Top Companies: {[c['name'] for c in metrics.top_companies[:3]]}")
    
    print(f"\n4. Export Applications...")
    export_data = engine.export_applications()
    print(f"  Exported {len(export_data)} application records")
    if export_data:
        print(f"  Sample: {export_data[0]['job_title']} at {export_data[0]['company_name']}")
    
    print(f"\n✅ Job Applications Engine Demo Complete!")

if __name__ == "__main__":
    demo_job_applications()
