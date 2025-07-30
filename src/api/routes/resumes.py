"""
Resume Management API Endpoints

FastAPI routes for resume optimization, storage, and management.
"""

import os
import sys
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.integrations.supabase.resume_service import ResumeDatabaseService
from src.core.resume_optimizer import ResumeProfile, ResumeOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

# Pydantic models for API
class PersonalInfo(BaseModel):
    """Personal information model"""
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None

class Experience(BaseModel):
    """Experience entry model"""
    title: str
    company: str
    duration: str
    description: str
    achievements: Optional[List[str]] = []

class Education(BaseModel):
    """Education entry model"""
    degree: str
    institution: str
    year: str
    relevant_coursework: Optional[List[str]] = []

class Project(BaseModel):
    """Project entry model"""
    name: str
    description: str
    technologies: Optional[List[str]] = []

class ResumeCreateRequest(BaseModel):
    """Request model for creating a resume"""
    personal_info: PersonalInfo
    summary: str
    experience: List[Experience]
    education: List[Education]
    skills: List[str]
    certifications: Optional[List[str]] = []
    projects: Optional[List[Project]] = []
    achievements: Optional[List[str]] = []
    user_id: Optional[str] = None

class ResumeOptimizeRequest(BaseModel):
    """Request model for resume optimization"""
    base_resume_id: str
    job_id: str
    optimization_level: str = "moderate"
    
    @validator('optimization_level')
    def validate_optimization_level(cls, v):
        valid_levels = ['conservative', 'moderate', 'aggressive']
        if v not in valid_levels:
            raise ValueError(f'Optimization level must be one of: {", ".join(valid_levels)}')
        return v

class ResumeUpdateRequest(BaseModel):
    """Request model for resume updates"""
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
    certifications: Optional[List[str]] = None
    projects: Optional[List[Project]] = None
    achievements: Optional[List[str]] = None

class ResumeResponse(BaseModel):
    """Response model for resume data"""
    id: str
    name: str
    is_base_resume: bool
    compatibility_score: Optional[float]
    created_at: str
    updated_at: str

class OptimizationResponse(BaseModel):
    """Response model for optimization operations"""
    status: str
    base_resume_id: str
    optimized_resume_id: Optional[str]
    job_id: str
    compatibility_score: Optional[float]
    optimization_level: str
    keyword_matches: Optional[int]
    missing_keywords: Optional[int]
    suggestions_count: Optional[int]
    rationale: Optional[str]
    message: Optional[str]

# Dependency to get resume service
def get_resume_service() -> ResumeDatabaseService:
    """Dependency to get resume database service"""
    return ResumeDatabaseService()

@router.post("/", response_model=Dict[str, str])
async def create_resume(
    request: ResumeCreateRequest,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Create a new base resume.
    
    This endpoint creates a base resume that can be optimized for different jobs.
    """
    try:
        logger.info(f"Creating resume for {request.personal_info.name}")
        
        # Convert request to ResumeProfile
        resume_profile = ResumeProfile(
            personal_info=request.personal_info.dict(),
            summary=request.summary,
            experience=[exp.dict() for exp in request.experience],
            education=[edu.dict() for edu in request.education],
            skills=request.skills,
            certifications=request.certifications or [],
            projects=[proj.dict() for proj in request.projects] if request.projects else [],
            achievements=request.achievements or []
        )
        
        # Create resume in database
        resume_id = service.create_base_resume(resume_profile, request.user_id)
        
        return {
            "status": "success",
            "message": "Resume created successfully",
            "resume_id": resume_id
        }
        
    except Exception as e:
        logger.error(f"Resume creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create resume: {str(e)}")

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_resume(
    request: ResumeOptimizeRequest,
    background_tasks: BackgroundTasks,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Optimize a resume for a specific job.
    
    This endpoint takes a base resume and optimizes it for a specific job posting,
    returning an optimized version with compatibility scoring.
    """
    try:
        logger.info(f"Optimizing resume {request.base_resume_id} for job {request.job_id}")
        
        result = service.optimize_resume_for_job(
            request.base_resume_id,
            request.job_id,
            request.optimization_level
        )
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Resume optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    List all resumes for a user.
    
    Returns both base resumes and optimized versions.
    """
    try:
        resumes = service.get_resumes_for_user(user_id)
        
        resume_responses = []
        for resume in resumes:
            resume_response = ResumeResponse(
                id=str(resume["id"]),
                name=resume.get("name", ""),
                is_base_resume=resume.get("is_base_resume", False),
                compatibility_score=resume.get("compatibility_score"),
                created_at=resume.get("created_at", ""),
                updated_at=resume.get("updated_at", "")
            )
            resume_responses.append(resume_response)
        
        return resume_responses
        
    except Exception as e:
        logger.error(f"Failed to list resumes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list resumes: {str(e)}")

@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Get detailed information about a specific resume.
    
    Returns comprehensive resume data including optimization details if applicable.
    """
    try:
        resume_data = service.get_resume_by_id(resume_id)
        
        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return resume_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resume: {str(e)}")

@router.patch("/{resume_id}")
async def update_resume(
    resume_id: str,
    request: ResumeUpdateRequest,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Update resume information.
    
    Allows updating various sections of a resume.
    """
    try:
        # Convert request to update dictionary
        updates = {}
        
        if request.summary is not None:
            updates["summary"] = request.summary
        if request.skills is not None:
            updates["skills"] = request.skills
        if request.experience is not None:
            updates["experience"] = [exp.dict() for exp in request.experience]
        if request.education is not None:
            updates["education"] = [edu.dict() for edu in request.education]
        if request.certifications is not None:
            updates["certifications"] = request.certifications
        if request.projects is not None:
            updates["projects"] = [proj.dict() for proj in request.projects]
        if request.achievements is not None:
            updates["achievements"] = request.achievements
        
        success = service.update_resume(resume_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Resume not found or update failed")
        
        return {
            "status": "success",
            "message": "Resume updated successfully",
            "resume_id": resume_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Delete a resume.
    
    This is a soft delete that marks the resume as deleted.
    """
    try:
        success = service.delete_resume(resume_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {
            "status": "success",
            "message": "Resume deleted successfully",
            "resume_id": resume_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/{resume_id}/analytics")
async def get_resume_analytics(
    resume_id: str,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Get analytics for a base resume.
    
    Returns optimization statistics and performance metrics.
    """
    try:
        analytics = service.get_resume_analytics(resume_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Resume not found or no analytics available")
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@router.get("/job/{job_id}/optimized")
async def get_optimized_resumes_for_job(
    job_id: str,
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Get all optimized resume versions for a specific job.
    
    Returns resumes sorted by compatibility score.
    """
    try:
        resumes = service.get_optimized_resumes_for_job(job_id)
        
        return {
            "job_id": job_id,
            "total_resumes": len(resumes),
            "resumes": resumes
        }
        
    except Exception as e:
        logger.error(f"Failed to get optimized resumes for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimized resumes: {str(e)}")

@router.get("/{resume_id}/export")
async def export_resume(
    resume_id: str,
    format_type: str = Query("json", description="Export format: json, markdown, or text"),
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Export resume in various formats.
    
    Supports JSON, Markdown, and plain text formats.
    """
    try:
        if format_type not in ["json", "markdown", "text"]:
            raise HTTPException(status_code=400, detail="Invalid format. Use: json, markdown, or text")
        
        exported_data = service.export_resume_to_format(resume_id, format_type)
        
        if "error" in exported_data:
            raise HTTPException(status_code=404, detail=exported_data["error"])
        
        return exported_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/batch-optimize")
async def batch_optimize_resumes(
    resume_ids: List[str],
    job_id: str,
    background_tasks: BackgroundTasks,
    optimization_level: str = "moderate",
    service: ResumeDatabaseService = Depends(get_resume_service)
):
    """
    Optimize multiple resumes for a single job.
    
    Processes multiple base resumes and returns optimization results.
    """
    if len(resume_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 resumes allowed per batch")
    
    try:
        results = []
        
        for resume_id in resume_ids:
            try:
                result = service.optimize_resume_for_job(resume_id, job_id, optimization_level)
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "base_resume_id": resume_id,
                    "job_id": job_id,
                    "message": str(e)
                })
        
        successful = len([r for r in results if r["status"] == "success"])
        failed = len([r for r in results if r["status"] == "error"])
        
        return {
            "status": "completed",
            "total_processed": len(resume_ids),
            "successful": successful,
            "failed": failed,
            "job_id": job_id,
            "optimization_level": optimization_level,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch optimization failed: {str(e)}")

@router.get("/stats/summary")
async def get_resume_stats(
    service: ResumeDatabaseService = Depends(get_resume_service),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get summary statistics about resumes.
    
    Returns counts, averages, and trends for resume optimization.
    """
    try:
        resumes = service.get_resumes_for_user(user_id)
        
        base_resumes = [r for r in resumes if r.get("is_base_resume", False)]
        optimized_resumes = [r for r in resumes if not r.get("is_base_resume", False)]
        
        # Calculate statistics
        stats = {
            "total_resumes": len(resumes),
            "base_resumes": len(base_resumes),
            "optimized_resumes": len(optimized_resumes),
            "optimization_ratio": len(optimized_resumes) / len(base_resumes) if base_resumes else 0
        }
        
        # Score statistics for optimized resumes
        scores = [r["compatibility_score"] for r in optimized_resumes if r.get("compatibility_score")]
        if scores:
            stats.update({
                "average_compatibility_score": sum(scores) / len(scores),
                "best_compatibility_score": max(scores),
                "worst_compatibility_score": min(scores),
                "score_distribution": {
                    "90-100": len([s for s in scores if s >= 90]),
                    "80-89": len([s for s in scores if 80 <= s < 90]),
                    "70-79": len([s for s in scores if 70 <= s < 80]),
                    "60-69": len([s for s in scores if 60 <= s < 70]),
                    "below-60": len([s for s in scores if s < 60])
                }
            })
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get resume stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "resume-optimizer",
        "version": "1.0.0"
    }
