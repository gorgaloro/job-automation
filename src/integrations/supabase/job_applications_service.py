#!/usr/bin/env python3
"""
Job Applications Supabase Service

Database service for managing job applications, status tracking, metrics,
and analytics using Supabase as the backend.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from core.job_applications_engine import JobApplication, ApplicationStatus, ApplicationMethod, ApplicationMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobApplicationsService:
    """Supabase service for job applications management"""
    
    def __init__(self):
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        if not self.demo_mode:
            try:
                from supabase import create_client, Client
                
                supabase_url = os.getenv('SUPABASE_URL')
                supabase_key = os.getenv('SUPABASE_KEY')
                
                if not supabase_url or not supabase_key:
                    logger.warning("Supabase credentials not found, falling back to demo mode")
                    self.demo_mode = True
                else:
                    self.supabase: Client = create_client(supabase_url, supabase_key)
                    logger.info("Supabase client initialized successfully")
            except ImportError:
                logger.warning("Supabase client not available, using demo mode")
                self.demo_mode = True
        
        if self.demo_mode:
            logger.info("Job Applications Service initialized in demo mode")
            self._demo_applications = []
    
    def create_application(self, application: JobApplication) -> bool:
        """Create a new job application record"""
        try:
            if self.demo_mode:
                self._demo_applications.append(application)
                logger.info(f"Demo: Created application {application.application_id}")
                return True
            
            # Convert application to dict for Supabase
            app_data = asdict(application)
            
            # Convert enums to strings
            app_data['status'] = application.status.value
            app_data['application_method'] = application.application_method.value
            
            # Insert into Supabase
            result = self.supabase.table('job_applications').insert(app_data).execute()
            
            if result.data:
                logger.info(f"Created application {application.application_id}")
                return True
            else:
                logger.error(f"Failed to create application: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Application creation failed: {e}")
            return False
    
    def get_application(self, application_id: str) -> Optional[JobApplication]:
        """Get application by ID"""
        try:
            if self.demo_mode:
                for app in self._demo_applications:
                    if app.application_id == application_id:
                        return app
                return None
            
            result = self.supabase.table('job_applications').select('*').eq('application_id', application_id).execute()
            
            if result.data:
                app_data = result.data[0]
                return self._dict_to_application(app_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Application retrieval failed: {e}")
            return None
    
    def update_application_status(self, application_id: str, new_status: ApplicationStatus, 
                                 notes: Optional[str] = None) -> bool:
        """Update application status"""
        try:
            if self.demo_mode:
                for app in self._demo_applications:
                    if app.application_id == application_id:
                        app.status = new_status
                        app.status_updated_at = datetime.now().isoformat()
                        if notes:
                            app.notes = notes
                        logger.info(f"Demo: Updated application {application_id} status to {new_status.value}")
                        return True
                return False
            
            update_data = {
                'status': new_status.value,
                'status_updated_at': datetime.now().isoformat()
            }
            
            if notes:
                update_data['notes'] = notes
            
            result = self.supabase.table('job_applications').update(update_data).eq('application_id', application_id).execute()
            
            if result.data:
                logger.info(f"Updated application {application_id} status to {new_status.value}")
                return True
            else:
                logger.error(f"Failed to update application status: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Status update failed: {e}")
            return False
    
    def get_user_applications(self, user_id: str, limit: int = 100, 
                             status_filter: Optional[ApplicationStatus] = None) -> List[JobApplication]:
        """Get applications for a user"""
        try:
            if self.demo_mode:
                apps = [app for app in self._demo_applications if app.user_id == user_id]
                if status_filter:
                    apps = [app for app in apps if app.status == status_filter]
                return apps[:limit]
            
            query = self.supabase.table('job_applications').select('*').eq('user_id', user_id)
            
            if status_filter:
                query = query.eq('status', status_filter.value)
            
            result = query.limit(limit).execute()
            
            if result.data:
                return [self._dict_to_application(app_data) for app_data in result.data]
            
            return []
            
        except Exception as e:
            logger.error(f"User applications retrieval failed: {e}")
            return []
    
    def get_applications_by_company(self, company_id: str) -> List[JobApplication]:
        """Get all applications for a specific company"""
        try:
            if self.demo_mode:
                return [app for app in self._demo_applications if app.company_id == company_id]
            
            result = self.supabase.table('job_applications').select('*').eq('company_id', company_id).execute()
            
            if result.data:
                return [self._dict_to_application(app_data) for app_data in result.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Company applications retrieval failed: {e}")
            return []
    
    def get_application_metrics(self, user_id: str) -> ApplicationMetrics:
        """Get comprehensive application metrics"""
        try:
            if self.demo_mode:
                return self._get_demo_metrics(user_id)
            
            # Get all applications for user
            result = self.supabase.table('job_applications').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                return self._empty_metrics()
            
            applications = [self._dict_to_application(app_data) for app_data in result.data]
            
            return self._calculate_metrics(applications)
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return self._empty_metrics()
    
    def get_applications_by_date_range(self, user_id: str, start_date: datetime, 
                                      end_date: datetime) -> List[JobApplication]:
        """Get applications within date range"""
        try:
            if self.demo_mode:
                return [app for app in self._demo_applications 
                       if app.user_id == user_id and 
                       start_date.isoformat() <= app.submitted_at <= end_date.isoformat()]
            
            result = self.supabase.table('job_applications').select('*').eq('user_id', user_id).gte('submitted_at', start_date.isoformat()).lte('submitted_at', end_date.isoformat()).execute()
            
            if result.data:
                return [self._dict_to_application(app_data) for app_data in result.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Date range query failed: {e}")
            return []
    
    def search_applications(self, user_id: str, search_query: str) -> List[JobApplication]:
        """Search applications by job title or company name"""
        try:
            if self.demo_mode:
                query_lower = search_query.lower()
                return [app for app in self._demo_applications 
                       if app.user_id == user_id and 
                       (query_lower in app.job_title.lower() or 
                        query_lower in app.company_name.lower())]
            
            # Use Supabase full-text search or ilike for partial matching
            result = self.supabase.table('job_applications').select('*').eq('user_id', user_id).or_(f'job_title.ilike.%{search_query}%,company_name.ilike.%{search_query}%').execute()
            
            if result.data:
                return [self._dict_to_application(app_data) for app_data in result.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Application search failed: {e}")
            return []
    
    def bulk_create_applications(self, applications: List[JobApplication]) -> Tuple[int, int]:
        """Bulk create multiple applications"""
        try:
            if self.demo_mode:
                self._demo_applications.extend(applications)
                logger.info(f"Demo: Bulk created {len(applications)} applications")
                return len(applications), 0
            
            # Convert applications to dicts
            app_data_list = []
            for app in applications:
                app_data = asdict(app)
                app_data['status'] = app.status.value
                app_data['application_method'] = app.application_method.value
                app_data_list.append(app_data)
            
            result = self.supabase.table('job_applications').insert(app_data_list).execute()
            
            if result.data:
                success_count = len(result.data)
                failure_count = len(applications) - success_count
                logger.info(f"Bulk created {success_count} applications, {failure_count} failures")
                return success_count, failure_count
            else:
                logger.error(f"Bulk creation failed: {result}")
                return 0, len(applications)
                
        except Exception as e:
            logger.error(f"Bulk creation failed: {e}")
            return 0, len(applications)
    
    def delete_application(self, application_id: str) -> bool:
        """Delete an application"""
        try:
            if self.demo_mode:
                self._demo_applications = [app for app in self._demo_applications 
                                         if app.application_id != application_id]
                logger.info(f"Demo: Deleted application {application_id}")
                return True
            
            result = self.supabase.table('job_applications').delete().eq('application_id', application_id).execute()
            
            if result.data:
                logger.info(f"Deleted application {application_id}")
                return True
            else:
                logger.error(f"Failed to delete application: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Application deletion failed: {e}")
            return False
    
    def get_application_timeline(self, application_id: str) -> List[Dict[str, Any]]:
        """Get application status timeline/history"""
        try:
            if self.demo_mode:
                # Return demo timeline
                return [
                    {
                        'timestamp': '2024-01-15T10:30:00Z',
                        'status': 'submitted',
                        'notes': 'Application submitted via automation'
                    },
                    {
                        'timestamp': '2024-01-20T14:15:00Z',
                        'status': 'in_review',
                        'notes': 'Application under review'
                    },
                    {
                        'timestamp': '2024-01-25T09:00:00Z',
                        'status': 'interview_scheduled',
                        'notes': 'Phone screen scheduled'
                    }
                ]
            
            # In production, this would query an application_history table
            # For now, return basic info from main table
            app = self.get_application(application_id)
            if app:
                return [
                    {
                        'timestamp': app.submitted_at,
                        'status': app.status.value,
                        'notes': app.notes or 'Application submitted'
                    }
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Timeline retrieval failed: {e}")
            return []
    
    def _dict_to_application(self, app_data: Dict) -> JobApplication:
        """Convert dictionary to JobApplication object"""
        # Convert string enums back to enum objects
        app_data['status'] = ApplicationStatus(app_data['status'])
        app_data['application_method'] = ApplicationMethod(app_data['application_method'])
        
        return JobApplication(**app_data)
    
    def _calculate_metrics(self, applications: List[JobApplication]) -> ApplicationMetrics:
        """Calculate metrics from applications list"""
        if not applications:
            return self._empty_metrics()
        
        total_apps = len(applications)
        
        # Count by status
        status_counts = {}
        for app in applications:
            status = app.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by method
        method_counts = {}
        for app in applications:
            method = app.application_method.value
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Count by month
        month_counts = {}
        for app in applications:
            month = app.submitted_at[:7]  # YYYY-MM
            month_counts[month] = month_counts.get(month, 0) + 1
        
        # Calculate rates
        responded_statuses = ['in_review', 'interview_scheduled', 'interview_completed', 'offer_extended', 'rejected']
        responded_count = sum(status_counts.get(status, 0) for status in responded_statuses)
        response_rate = responded_count / total_apps if total_apps > 0 else 0
        
        interview_statuses = ['interview_scheduled', 'interview_completed', 'offer_extended']
        interview_count = sum(status_counts.get(status, 0) for status in interview_statuses)
        interview_rate = interview_count / total_apps if total_apps > 0 else 0
        
        offer_count = status_counts.get('offer_extended', 0)
        offer_rate = offer_count / total_apps if total_apps > 0 else 0
        
        # Top companies and job titles
        company_counts = {}
        title_counts = {}
        
        for app in applications:
            company_counts[app.company_name] = company_counts.get(app.company_name, 0) + 1
            title_counts[app.job_title] = title_counts.get(app.job_title, 0) + 1
        
        top_companies = [{'name': name, 'applications': count} 
                        for name, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)]
        
        top_job_titles = [{'title': title, 'applications': count}
                         for title, count in sorted(title_counts.items(), key=lambda x: x[1], reverse=True)]
        
        return ApplicationMetrics(
            total_applications=total_apps,
            applications_by_status=status_counts,
            applications_by_method=method_counts,
            applications_by_month=month_counts,
            response_rate=response_rate,
            interview_rate=interview_rate,
            offer_rate=offer_rate,
            average_response_time_days=7.5,  # Would calculate from actual data
            top_companies=top_companies,
            top_job_titles=top_job_titles
        )
    
    def _get_demo_metrics(self, user_id: str) -> ApplicationMetrics:
        """Get demo metrics"""
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
            response_rate=0.64,
            interview_rate=0.12,
            offer_rate=0.04,
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
    
    def _empty_metrics(self) -> ApplicationMetrics:
        """Return empty metrics"""
        return ApplicationMetrics(
            total_applications=0,
            applications_by_status={},
            applications_by_method={},
            applications_by_month={},
            response_rate=0.0,
            interview_rate=0.0,
            offer_rate=0.0,
            average_response_time_days=None,
            top_companies=[],
            top_job_titles=[]
        )

# Demo functions
def demo_job_applications_service():
    """Demo the job applications service"""
    print("=== Job Applications Service Demo ===")
    
    service = JobApplicationsService()
    
    # Create demo applications
    from core.job_applications_engine import JobApplication, ApplicationStatus, ApplicationMethod
    
    demo_apps = [
        JobApplication(
            application_id="app_demo_001",
            job_id="job_001",
            company_id="comp_001",
            user_id="demo_user",
            job_title="Senior Software Engineer",
            company_name="TechCorp",
            resume_version_id="resume_v1",
            application_method=ApplicationMethod.AUTO_APPLY,
            status=ApplicationStatus.SUBMITTED
        ),
        JobApplication(
            application_id="app_demo_002",
            job_id="job_002",
            company_id="comp_002",
            user_id="demo_user",
            job_title="Full Stack Developer",
            company_name="DataFlow",
            resume_version_id="resume_v2",
            application_method=ApplicationMethod.MANUAL_FORM,
            status=ApplicationStatus.IN_REVIEW
        )
    ]
    
    print("\n1. Creating Applications...")
    for app in demo_apps:
        success = service.create_application(app)
        print(f"  {'✓' if success else '✗'} {app.job_title} at {app.company_name}")
    
    print("\n2. Retrieving Applications...")
    user_apps = service.get_user_applications("demo_user")
    print(f"  Found {len(user_apps)} applications for demo_user")
    
    print("\n3. Updating Status...")
    if user_apps:
        success = service.update_application_status(
            user_apps[0].application_id,
            ApplicationStatus.INTERVIEW_SCHEDULED,
            "Phone screen scheduled"
        )
        print(f"  {'✓' if success else '✗'} Status updated")
    
    print("\n4. Getting Metrics...")
    metrics = service.get_application_metrics("demo_user")
    if metrics:
        print(f"  Total Applications: {metrics.total_applications}")
        print(f"  Response Rate: {metrics.response_rate:.1%}")
        print(f"  Interview Rate: {metrics.interview_rate:.1%}")
    
    print("\n5. Search Applications...")
    search_results = service.search_applications("demo_user", "Software")
    print(f"  Found {len(search_results)} applications matching 'Software'")
    
    print("\n✅ Job Applications Service Demo Complete!")

if __name__ == "__main__":
    demo_job_applications_service()
