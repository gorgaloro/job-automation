#!/usr/bin/env python3
"""
Job Applications API Routes

FastAPI routes for job application management including:
- Application submission (auto and manual)
- Status tracking and updates
- Metrics and analytics
- Search and filtering
- Export functionality
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from core.job_applications_engine import (
    JobApplicationsEngine, 
    JobApplication, 
    ApplicationStatus, 
    ApplicationMethod,
    ApplicationMetrics
)

# Initialize router
router = APIRouter(prefix="/api/v1/applications", tags=["Job Applications"])

# Initialize engine
applications_engine = JobApplicationsEngine()

# Pydantic models for API
class JobApplicationRequest(BaseModel):
    """Request model for job application submission"""
    job_data: Dict[str, Any] = Field(..., description="Job information dictionary")
    resume_version_id: str = Field(..., description="ID of resume version to use")
    application_method: ApplicationMethod = Field(default=ApplicationMethod.AUTO_APPLY, description="Application submission method")
    cover_letter_id: Optional[str] = Field(None, description="Optional cover letter ID")
    notes: Optional[str] = Field(None, description="Optional application notes")

class JobApplicationResponse(BaseModel):
    """Response model for job application"""
    application_id: str
    job_id: str
    company_id: str
    user_id: str
    job_title: str
    company_name: str
    resume_version_id: str
    cover_letter_id: Optional[str]
    application_method: str
    status: str
    submitted_at: str
    status_updated_at: str
    hubspot_deal_id: Optional[str]
    application_url: Optional[str]
    source: Optional[str]
    notes: Optional[str]
    metadata: Dict[str, Any]

class StatusUpdateRequest(BaseModel):
    """Request model for status updates"""
    new_status: ApplicationStatus = Field(..., description="New application status")
    notes: Optional[str] = Field(None, description="Optional update notes")

class ApplicationSearchRequest(BaseModel):
    """Request model for application search"""
    query: Optional[str] = Field(None, description="Search query")
    status_filter: Optional[ApplicationStatus] = Field(None, description="Filter by status")
    company_filter: Optional[str] = Field(None, description="Filter by company")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    limit: int = Field(default=100, description="Maximum results")

class ApplicationMetricsResponse(BaseModel):
    """Response model for application metrics"""
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

class BulkApplicationRequest(BaseModel):
    """Request model for bulk application submission"""
    applications: List[JobApplicationRequest] = Field(..., description="List of applications to submit")

class BulkApplicationResponse(BaseModel):
    """Response model for bulk application submission"""
    success_count: int
    failure_count: int
    successful_applications: List[str]
    failed_applications: List[Dict[str, Any]]

# API Routes

@router.post("/submit", response_model=JobApplicationResponse)
async def submit_application(request: JobApplicationRequest):
    """
    Submit a job application (auto or manual)
    
    This endpoint handles both automated and manual job application submissions,
    creating HubSpot deals and storing application data in Supabase.
    """
    try:
        # Submit application using engine
        application = applications_engine.submit_application(
            job_data=request.job_data,
            resume_version_id=request.resume_version_id,
            application_method=request.application_method,
            cover_letter_id=request.cover_letter_id,
            notes=request.notes
        )
        
        if not application:
            raise HTTPException(status_code=400, detail="Failed to submit application")
        
        # Convert to response model
        return JobApplicationResponse(
            application_id=application.application_id,
            job_id=application.job_id,
            company_id=application.company_id,
            user_id=application.user_id,
            job_title=application.job_title,
            company_name=application.company_name,
            resume_version_id=application.resume_version_id,
            cover_letter_id=application.cover_letter_id,
            application_method=application.application_method.value,
            status=application.status.value,
            submitted_at=application.submitted_at,
            status_updated_at=application.status_updated_at,
            hubspot_deal_id=application.hubspot_deal_id,
            application_url=application.application_url,
            source=application.source,
            notes=application.notes,
            metadata=application.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application submission failed: {str(e)}")

@router.put("/{application_id}/status", response_model=Dict[str, str])
async def update_application_status(application_id: str, request: StatusUpdateRequest):
    """
    Update application status
    
    Updates both database and HubSpot CRM deal stage automatically.
    """
    try:
        success = applications_engine.update_application_status(
            application_id=application_id,
            new_status=request.new_status,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update application status")
        
        return {
            "message": "Status updated successfully",
            "application_id": application_id,
            "new_status": request.new_status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")

@router.get("/metrics", response_model=ApplicationMetricsResponse)
async def get_application_metrics(user_id: str = Query(default="demo_user", description="User ID")):
    """
    Get comprehensive application metrics and analytics
    
    Returns detailed statistics including response rates, interview rates,
    top companies, and application trends.
    """
    try:
        metrics = applications_engine.get_application_metrics(user_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Metrics not found")
        
        return ApplicationMetricsResponse(
            total_applications=metrics.total_applications,
            applications_by_status=metrics.applications_by_status,
            applications_by_method=metrics.applications_by_method,
            applications_by_month=metrics.applications_by_month,
            response_rate=metrics.response_rate,
            interview_rate=metrics.interview_rate,
            offer_rate=metrics.offer_rate,
            average_response_time_days=metrics.average_response_time_days,
            top_companies=metrics.top_companies,
            top_job_titles=metrics.top_job_titles
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@router.get("/export", response_model=List[Dict[str, Any]])
async def export_applications(
    user_id: str = Query(default="demo_user", description="User ID"),
    format: str = Query(default="json", description="Export format (json, csv)")
):
    """
    Export application history and data
    
    Supports multiple export formats for reporting and analysis.
    """
    try:
        export_data = applications_engine.export_applications(user_id)
        
        if format.lower() == "csv":
            # Convert to CSV format (simplified for demo)
            return {"message": "CSV export would be implemented here", "data": export_data}
        
        return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/search", response_model=List[JobApplicationResponse])
async def search_applications(request: ApplicationSearchRequest):
    """
    Search and filter applications
    
    Advanced search with multiple filter options including status,
    company, date range, and text search.
    """
    try:
        # Use database service for search if available
        if applications_engine.db_service:
            results = []
            
            # Text search
            if request.query:
                results = applications_engine.db_service.search_applications("demo_user", request.query)
            else:
                # Get all applications with filters
                results = applications_engine.db_service.get_user_applications(
                    "demo_user", 
                    limit=request.limit,
                    status_filter=request.status_filter
                )
            
            # Convert to response models
            return [
                JobApplicationResponse(
                    application_id=app.application_id,
                    job_id=app.job_id,
                    company_id=app.company_id,
                    user_id=app.user_id,
                    job_title=app.job_title,
                    company_name=app.company_name,
                    resume_version_id=app.resume_version_id,
                    cover_letter_id=app.cover_letter_id,
                    application_method=app.application_method.value,
                    status=app.status.value,
                    submitted_at=app.submitted_at,
                    status_updated_at=app.status_updated_at,
                    hubspot_deal_id=app.hubspot_deal_id,
                    application_url=app.application_url,
                    source=app.source,
                    notes=app.notes,
                    metadata=app.metadata
                ) for app in results
            ]
        else:
            return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/bulk-submit", response_model=BulkApplicationResponse)
async def bulk_submit_applications(request: BulkApplicationRequest):
    """
    Submit multiple applications in batch
    
    Efficient bulk processing for automated application campaigns.
    """
    try:
        successful_applications = []
        failed_applications = []
        
        for app_request in request.applications:
            try:
                application = applications_engine.submit_application(
                    job_data=app_request.job_data,
                    resume_version_id=app_request.resume_version_id,
                    application_method=app_request.application_method,
                    cover_letter_id=app_request.cover_letter_id,
                    notes=app_request.notes
                )
                
                if application:
                    successful_applications.append(application.application_id)
                else:
                    failed_applications.append({
                        "job_title": app_request.job_data.get("title", "Unknown"),
                        "error": "Application submission failed"
                    })
                    
            except Exception as e:
                failed_applications.append({
                    "job_title": app_request.job_data.get("title", "Unknown"),
                    "error": str(e)
                })
        
        return BulkApplicationResponse(
            success_count=len(successful_applications),
            failure_count=len(failed_applications),
            successful_applications=successful_applications,
            failed_applications=failed_applications
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk submission failed: {str(e)}")

@router.get("/{application_id}", response_model=JobApplicationResponse)
async def get_application(application_id: str):
    """
    Get single application by ID
    
    Retrieve detailed information about a specific application.
    """
    try:
        if applications_engine.db_service:
            application = applications_engine.db_service.get_application(application_id)
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            return JobApplicationResponse(
                application_id=application.application_id,
                job_id=application.job_id,
                company_id=application.company_id,
                user_id=application.user_id,
                job_title=application.job_title,
                company_name=application.company_name,
                resume_version_id=application.resume_version_id,
                cover_letter_id=application.cover_letter_id,
                application_method=application.application_method.value,
                status=application.status.value,
                submitted_at=application.submitted_at,
                status_updated_at=application.status_updated_at,
                hubspot_deal_id=application.hubspot_deal_id,
                application_url=application.application_url,
                source=application.source,
                notes=application.notes,
                metadata=application.metadata
            )
        else:
            raise HTTPException(status_code=503, detail="Database service not available")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application retrieval failed: {str(e)}")

@router.get("/{application_id}/timeline", response_model=List[Dict[str, Any]])
async def get_application_timeline(application_id: str):
    """
    Get application status timeline/history
    
    Returns chronological history of status changes and updates.
    """
    try:
        if applications_engine.db_service:
            timeline = applications_engine.db_service.get_application_timeline(application_id)
            return timeline
        else:
            raise HTTPException(status_code=503, detail="Database service not available")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline retrieval failed: {str(e)}")

@router.delete("/{application_id}", response_model=Dict[str, str])
async def delete_application(application_id: str):
    """
    Delete an application
    
    Removes application from database (use with caution).
    """
    try:
        if applications_engine.db_service:
            success = applications_engine.db_service.delete_application(application_id)
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to delete application")
            
            return {
                "message": "Application deleted successfully",
                "application_id": application_id
            }
        else:
            raise HTTPException(status_code=503, detail="Database service not available")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application deletion failed: {str(e)}")

@router.get("/demo/showcase", response_model=Dict[str, Any])
async def demo_showcase():
    """
    Demo endpoint showcasing all job applications features
    
    Demonstrates the complete job applications automation pipeline
    for portfolio and testing purposes.
    """
    try:
        # Demo data
        demo_jobs = [
            {
                "job_id": "demo_001",
                "title": "Senior Software Engineer",
                "company_name": "TechCorp",
                "company_id": "comp_techcorp",
                "url": "https://techcorp.com/jobs/senior-engineer",
                "source": "company_website"
            },
            {
                "job_id": "demo_002",
                "title": "AI Engineer", 
                "company_name": "IntelliCorp",
                "company_id": "comp_intellicorp",
                "url": "https://intellicorp.ai/jobs/ai-engineer",
                "source": "linkedin"
            }
        ]
        
        # Submit demo applications
        submitted_apps = []
        for job in demo_jobs:
            application = applications_engine.submit_application(
                job_data=job,
                resume_version_id="resume_demo_optimized",
                application_method=ApplicationMethod.AUTO_APPLY,
                notes="Demo application via API"
            )
            if application:
                submitted_apps.append(application.application_id)
        
        # Get metrics
        metrics = applications_engine.get_application_metrics()
        
        # Export data
        export_data = applications_engine.export_applications()
        
        return {
            "message": "Job Applications API Demo Complete!",
            "submitted_applications": len(submitted_apps),
            "application_ids": submitted_apps,
            "metrics_summary": {
                "total_applications": metrics.total_applications if metrics else 0,
                "response_rate": f"{metrics.response_rate:.1%}" if metrics else "0%",
                "interview_rate": f"{metrics.interview_rate:.1%}" if metrics else "0%"
            },
            "export_count": len(export_data),
            "integration_status": {
                "database_service": applications_engine.db_service is not None,
                "hubspot_service": applications_engine.hubspot_service is not None,
                "demo_mode": applications_engine.demo_mode
            },
            "api_endpoints": [
                "POST /api/v1/applications/submit",
                "PUT /api/v1/applications/{id}/status", 
                "GET /api/v1/applications/metrics",
                "GET /api/v1/applications/export",
                "POST /api/v1/applications/search",
                "POST /api/v1/applications/bulk-submit",
                "GET /api/v1/applications/{id}",
                "GET /api/v1/applications/{id}/timeline",
                "DELETE /api/v1/applications/{id}"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

# Health check endpoint
@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check for job applications service
    
    Returns status of all integrated services and components.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "job_applications_engine": "operational",
            "database_service": "operational" if applications_engine.db_service else "unavailable",
            "hubspot_service": "operational" if applications_engine.hubspot_service else "unavailable"
        },
        "demo_mode": applications_engine.demo_mode,
        "version": "1.0.0"
    }
