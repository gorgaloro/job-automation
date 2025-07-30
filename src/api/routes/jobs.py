"""
Job Management API Endpoints

FastAPI routes for job description parsing, storage, and retrieval.
"""

import os
import sys
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.integrations.supabase.job_service import JobDatabaseService
from src.core.job_parser import JobDescriptionParser, JobDetails

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

# Pydantic models for API
class JobParseRequest(BaseModel):
    """Request model for job parsing"""
    text: Optional[str] = None
    url: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None
    save_to_database: bool = True
    
    @validator('text', 'url')
    def validate_input(cls, v, values):
        if not v and not values.get('url') and not values.get('text'):
            raise ValueError('Either text or url must be provided')
        return v

class JobSearchRequest(BaseModel):
    """Request model for job search"""
    company: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    limit: int = 50
    offset: int = 0

class JobStatusUpdate(BaseModel):
    """Request model for job status updates"""
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'applied', 'rejected', 'interview', 'offer', 'closed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class JobResponse(BaseModel):
    """Response model for job data"""
    id: str
    job_title: str
    company_name: str
    location: Optional[str]
    job_type: Optional[str]
    remote_policy: Optional[str]
    status: str
    created_at: str
    required_skills: Optional[List[str]]
    technologies: Optional[List[str]]

class ParseResponse(BaseModel):
    """Response model for parsing operations"""
    status: str
    message: str
    job_id: Optional[str] = None
    company_id: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, List[str]]] = None

# Dependency to get database service
def get_job_service() -> JobDatabaseService:
    """Dependency to get job database service"""
    return JobDatabaseService()

@router.post("/parse", response_model=ParseResponse)
async def parse_job(
    request: JobParseRequest,
    background_tasks: BackgroundTasks,
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Parse job description from URL or text.
    
    This endpoint accepts either a URL or raw text and extracts structured
    job information using AI-powered parsing.
    """
    try:
        logger.info(f"Parsing job - URL: {request.url}, Text length: {len(request.text or '')}")
        
        if request.url:
            # Parse from URL
            if request.save_to_database:
                result = service.process_job_from_url(str(request.url))
            else:
                parser = JobDescriptionParser()
                job_details = parser.parse_from_url(str(request.url))
                result = {
                    "status": "success",
                    "message": "Job parsed successfully",
                    "parsed_data": {
                        "title": job_details.title,
                        "company": job_details.company,
                        "location": job_details.location,
                        "required_skills_count": len(job_details.requirements.required_skills),
                        "technologies_count": len(job_details.requirements.technologies)
                    }
                }
        else:
            # Parse from text
            if request.save_to_database:
                result = service.process_job_from_text(
                    request.text, 
                    str(request.source_url) if request.source_url else None
                )
            else:
                parser = JobDescriptionParser()
                job_details = parser.parse_from_text(
                    request.text,
                    str(request.source_url) if request.source_url else None
                )
                result = {
                    "status": "success",
                    "message": "Job parsed successfully",
                    "parsed_data": {
                        "title": job_details.title,
                        "company": job_details.company,
                        "location": job_details.location,
                        "required_skills_count": len(job_details.requirements.required_skills),
                        "technologies_count": len(job_details.requirements.technologies)
                    }
                }
        
        if result["status"] == "success":
            return ParseResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Job parsing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

@router.get("/search", response_model=List[JobResponse])
async def search_jobs(
    company: Optional[str] = Query(None, description="Filter by company name"),
    skills: Optional[str] = Query(None, description="Filter by skills (comma-separated)"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Search for jobs with various filters.
    
    Returns a list of jobs matching the specified criteria.
    """
    try:
        # Parse skills if provided
        skills_list = [s.strip() for s in skills.split(',')] if skills else None
        
        results = service.search_jobs(
            company=company,
            skills=skills_list,
            location=location,
            job_type=job_type,
            limit=limit
        )
        
        # Apply offset
        results = results[offset:offset + limit]
        
        # Convert to response format
        job_responses = []
        for job in results:
            company_name = ""
            if job.get("companies"):
                if isinstance(job["companies"], dict):
                    company_name = job["companies"].get("name", "")
                elif isinstance(job["companies"], list) and job["companies"]:
                    company_name = job["companies"][0].get("name", "")
            
            job_response = JobResponse(
                id=str(job["id"]),
                job_title=job.get("job_title", ""),
                company_name=company_name,
                location=job.get("location"),
                job_type=job.get("job_type"),
                remote_policy=job.get("remote_policy"),
                status=job.get("status", "active"),
                created_at=job.get("created_at", ""),
                required_skills=job.get("required_skills", []),
                technologies=job.get("technologies", [])
            )
            job_responses.append(job_response)
        
        return job_responses
        
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/{job_id}")
async def get_job(
    job_id: str,
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Get detailed information about a specific job.
    
    Returns comprehensive job data including company information,
    requirements, and parsing metadata.
    """
    try:
        job_data = service.get_job_by_id(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")

@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: str,
    status_update: JobStatusUpdate,
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Update the status of a job.
    
    Valid statuses: active, applied, rejected, interview, offer, closed
    """
    try:
        success = service.update_job_status(job_id, status_update.status)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found or update failed")
        
        return {
            "status": "success",
            "message": f"Job status updated to {status_update.status}",
            "job_id": job_id,
            "new_status": status_update.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job status: {e}")
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")

@router.post("/batch-parse")
async def batch_parse_jobs(
    urls: List[HttpUrl],
    background_tasks: BackgroundTasks,
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Parse multiple job descriptions from URLs in batch.
    
    This endpoint processes multiple URLs and returns results for each.
    Processing happens in the background for better performance.
    """
    if len(urls) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 URLs allowed per batch")
    
    try:
        results = []
        
        for url in urls:
            try:
                result = service.process_job_from_url(str(url))
                results.append({
                    "url": str(url),
                    "status": result["status"],
                    "job_id": result.get("job_id"),
                    "message": result.get("message", "Success")
                })
            except Exception as e:
                results.append({
                    "url": str(url),
                    "status": "error",
                    "job_id": None,
                    "message": str(e)
                })
        
        return {
            "status": "completed",
            "total_processed": len(urls),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch parsing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch parsing failed: {str(e)}")

@router.get("/stats/summary")
async def get_job_stats(
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Get summary statistics about jobs in the database.
    
    Returns counts by status, company, location, and other metrics.
    """
    try:
        # Get all jobs for statistics
        all_jobs = service.search_jobs(limit=1000)
        
        # Calculate statistics
        stats = {
            "total_jobs": len(all_jobs),
            "by_status": {},
            "by_job_type": {},
            "by_remote_policy": {},
            "top_companies": {},
            "top_locations": {},
            "recent_jobs": len([j for j in all_jobs if j.get("created_at", "").startswith("2024")])
        }
        
        # Count by various fields
        for job in all_jobs:
            # Status counts
            status = job.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Job type counts
            job_type = job.get("job_type", "unknown")
            stats["by_job_type"][job_type] = stats["by_job_type"].get(job_type, 0) + 1
            
            # Remote policy counts
            remote_policy = job.get("remote_policy", "unknown")
            stats["by_remote_policy"][remote_policy] = stats["by_remote_policy"].get(remote_policy, 0) + 1
            
            # Company counts
            company_name = ""
            if job.get("companies"):
                if isinstance(job["companies"], dict):
                    company_name = job["companies"].get("name", "")
                elif isinstance(job["companies"], list) and job["companies"]:
                    company_name = job["companies"][0].get("name", "")
            
            if company_name:
                stats["top_companies"][company_name] = stats["top_companies"].get(company_name, 0) + 1
            
            # Location counts
            location = job.get("location", "")
            if location:
                stats["top_locations"][location] = stats["top_locations"].get(location, 0) + 1
        
        # Sort top companies and locations
        stats["top_companies"] = dict(sorted(stats["top_companies"].items(), key=lambda x: x[1], reverse=True)[:10])
        stats["top_locations"] = dict(sorted(stats["top_locations"].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get job stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    service: JobDatabaseService = Depends(get_job_service)
):
    """
    Delete a job from the database.
    
    This is a soft delete that updates the status to 'deleted'.
    """
    try:
        success = service.update_job_status(job_id, "deleted")
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "status": "success",
            "message": "Job deleted successfully",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "job-parser",
        "version": "1.0.0"
    }
