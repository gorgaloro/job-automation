"""
AI Scoring & Decision Support API Endpoints

FastAPI routes for intelligent job, company, and resume scoring.
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

from src.integrations.supabase.scoring_service import ScoringDatabaseService
from src.core.ai_scoring_engine import ScoringOrchestrator
from src.core.personal_brand import create_sample_profile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scoring", tags=["ai-scoring"])

# Pydantic models for API
class JobScoringRequest(BaseModel):
    """Request model for job scoring"""
    job_data: Dict[str, Any]
    brand_profile: Dict[str, Any]

class CompanyScoringRequest(BaseModel):
    """Request model for company scoring"""
    company_data: Dict[str, Any]
    brand_profile: Dict[str, Any]

class ResumeScoringRequest(BaseModel):
    """Request model for resume scoring"""
    resume_data: Dict[str, Any]
    job_data: Dict[str, Any]
    brand_profile: Dict[str, Any]

class OpportunityScoringRequest(BaseModel):
    """Request model for comprehensive opportunity scoring"""
    job_data: Dict[str, Any]
    company_data: Dict[str, Any]
    resume_versions: List[Dict[str, Any]]
    brand_profile: Dict[str, Any]

class BatchJobScoringRequest(BaseModel):
    """Request model for batch job scoring"""
    jobs_data: List[Dict[str, Any]]
    brand_profile: Dict[str, Any]

class ScoringResponse(BaseModel):
    """Response model for scoring operations"""
    status: str
    score: Optional[float] = None
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    scoring_factors: Optional[Dict[str, Any]] = None
    database_id: Optional[str] = None
    message: str

class OpportunityScoringResponse(BaseModel):
    """Response model for comprehensive opportunity scoring"""
    status: str
    overall_score: float
    job_score: Optional[Dict[str, Any]] = None
    company_score: Optional[Dict[str, Any]] = None
    resume_scores: List[Dict[str, Any]] = []
    recommended_resume: Optional[Dict[str, Any]] = None
    message: str

class AnalyticsResponse(BaseModel):
    """Response model for scoring analytics"""
    total_scores: int
    job_scores: Dict[str, Any]
    company_scores: Dict[str, Any]
    resume_scores: Dict[str, Any]
    profile_version: str
    last_updated: str

# Dependency to get scoring service
def get_scoring_service() -> ScoringDatabaseService:
    """Dependency to get scoring database service"""
    return ScoringDatabaseService()

@router.post("/jobs/score", response_model=ScoringResponse)
async def score_job(
    request: JobScoringRequest,
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Score a job opportunity against a personal brand profile.
    
    This endpoint analyzes job alignment based on role fit, industry preferences,
    work environment, values alignment, and growth opportunities.
    """
    try:
        logger.info(f"Scoring job: {request.job_data.get('title', 'Unknown')}")
        
        # Score the job
        job_result = service.orchestrator.job_scorer.score_job_alignment(
            request.job_data, 
            request.brand_profile
        )
        
        # Store in database
        score_id = service.store_job_score(job_result)
        
        return ScoringResponse(
            status="success",
            score=job_result.score,
            rationale=job_result.rationale,
            confidence=job_result.confidence,
            scoring_factors=job_result.scoring_factors,
            database_id=score_id,
            message=f"Job scored successfully: {job_result.score:.1f}/100"
        )
        
    except Exception as e:
        logger.error(f"Job scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Job scoring failed: {str(e)}")

@router.post("/companies/score", response_model=ScoringResponse)
async def score_company(
    request: CompanyScoringRequest,
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Score a company for culture and mission fit against a personal brand profile.
    
    This endpoint analyzes company alignment based on industry fit, values alignment,
    culture match, and company size/stage preferences.
    """
    try:
        logger.info(f"Scoring company: {request.company_data.get('name', 'Unknown')}")
        
        # Score the company
        company_result = service.orchestrator.company_scorer.score_company_fit(
            request.company_data,
            request.brand_profile
        )
        
        # Store in database
        score_id = service.store_company_score(company_result)
        
        return ScoringResponse(
            status="success",
            score=company_result.score,
            rationale=company_result.rationale,
            confidence=company_result.confidence,
            scoring_factors=company_result.scoring_factors,
            database_id=score_id,
            message=f"Company scored successfully: {company_result.score:.1f}/100"
        )
        
    except Exception as e:
        logger.error(f"Company scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Company scoring failed: {str(e)}")

@router.post("/resumes/score", response_model=ScoringResponse)
async def score_resume(
    request: ResumeScoringRequest,
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Score a resume against a specific job description.
    
    This endpoint analyzes resume-job fit based on keyword matching,
    experience relevance, skills alignment, and ATS optimization.
    """
    try:
        logger.info(f"Scoring resume {request.resume_data.get('version', 'Unknown')} against job {request.job_data.get('title', 'Unknown')}")
        
        # Score the resume
        resume_result = service.orchestrator.resume_scorer.score_resume_job_fit(
            request.resume_data,
            request.job_data,
            request.brand_profile
        )
        
        # Store in database
        score_id = service.store_resume_score(resume_result)
        
        return ScoringResponse(
            status="success",
            score=resume_result.score,
            rationale=resume_result.rationale,
            confidence=resume_result.confidence,
            scoring_factors=resume_result.scoring_factors,
            database_id=score_id,
            message=f"Resume scored successfully: {resume_result.score:.1f}/100"
        )
        
    except Exception as e:
        logger.error(f"Resume scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Resume scoring failed: {str(e)}")

@router.post("/opportunities/score", response_model=OpportunityScoringResponse)
async def score_opportunity(
    request: OpportunityScoringRequest,
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Comprehensive scoring of a job opportunity including job fit, company fit, and resume matching.
    
    This endpoint provides a complete analysis of an opportunity with recommendations
    for the best resume version to use.
    """
    try:
        logger.info(f"Comprehensive scoring: {request.job_data.get('title', 'Unknown')} at {request.company_data.get('name', 'Unknown')}")
        
        # Score and store the opportunity
        results = service.score_and_store_opportunity(
            request.job_data,
            request.company_data,
            request.resume_versions,
            request.brand_profile
        )
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        return OpportunityScoringResponse(
            status="success",
            overall_score=results["overall_score"],
            job_score=results.get("job_score"),
            company_score=results.get("company_score"),
            resume_scores=results.get("resume_scores", []),
            recommended_resume=results.get("recommended_resume"),
            message=f"Opportunity scored successfully: {results['overall_score']:.1f}/100"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Opportunity scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Opportunity scoring failed: {str(e)}")

@router.post("/jobs/batch-score")
async def batch_score_jobs(
    request: BatchJobScoringRequest,
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Score multiple jobs in batch for efficiency.
    
    This endpoint processes multiple job opportunities and returns them
    sorted by score for prioritization.
    """
    try:
        logger.info(f"Batch scoring {len(request.jobs_data)} jobs")
        
        # Batch score jobs
        results = service.batch_score_jobs(request.jobs_data, request.brand_profile)
        
        return {
            "status": "success",
            "jobs_scored": len(results),
            "results": results,
            "message": f"Successfully scored {len(results)} jobs"
        }
        
    except Exception as e:
        logger.error(f"Batch job scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")

@router.get("/jobs/{job_id}/scores")
async def get_job_scores(
    job_id: str,
    profile_version: Optional[str] = Query(None, description="Filter by profile version"),
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Get all scoring results for a specific job.
    
    Returns historical scores and version comparisons for a job.
    """
    try:
        scores = service.get_job_scores(job_id, profile_version)
        
        return {
            "status": "success",
            "job_id": job_id,
            "scores_found": len(scores),
            "scores": scores
        }
        
    except Exception as e:
        logger.error(f"Failed to get job scores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scores: {str(e)}")

@router.get("/companies/{company_id}/scores")
async def get_company_scores(
    company_id: str,
    profile_version: Optional[str] = Query(None, description="Filter by profile version"),
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Get all scoring results for a specific company.
    
    Returns historical scores and version comparisons for a company.
    """
    try:
        scores = service.get_company_scores(company_id, profile_version)
        
        return {
            "status": "success",
            "company_id": company_id,
            "scores_found": len(scores),
            "scores": scores
        }
        
    except Exception as e:
        logger.error(f"Failed to get company scores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scores: {str(e)}")

@router.get("/resumes/{resume_id}/scores")
async def get_resume_scores(
    resume_id: str,
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Get all scoring results for a specific resume.
    
    Returns how the resume performed against different jobs.
    """
    try:
        scores = service.get_resume_scores(resume_id, job_id)
        
        return {
            "status": "success",
            "resume_id": resume_id,
            "scores_found": len(scores),
            "scores": scores
        }
        
    except Exception as e:
        logger.error(f"Failed to get resume scores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scores: {str(e)}")

@router.get("/top-jobs")
async def get_top_jobs(
    profile_version: str = Query(..., description="Profile version to filter by"),
    limit: int = Query(10, description="Maximum number of results"),
    min_score: float = Query(70.0, description="Minimum score threshold"),
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Get top-scored jobs for a profile version.
    
    Returns the highest-scoring job opportunities for prioritization.
    """
    try:
        top_jobs = service.get_top_scored_jobs(profile_version, limit, min_score)
        
        return {
            "status": "success",
            "profile_version": profile_version,
            "jobs_found": len(top_jobs),
            "min_score": min_score,
            "top_jobs": top_jobs
        }
        
    except Exception as e:
        logger.error(f"Failed to get top jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get top jobs: {str(e)}")

@router.get("/top-companies")
async def get_top_companies(
    profile_version: str = Query(..., description="Profile version to filter by"),
    limit: int = Query(10, description="Maximum number of results"),
    min_score: float = Query(70.0, description="Minimum score threshold"),
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Get top-scored companies for a profile version.
    
    Returns the highest-scoring companies for prioritization.
    """
    try:
        top_companies = service.get_top_scored_companies(profile_version, limit, min_score)
        
        return {
            "status": "success",
            "profile_version": profile_version,
            "companies_found": len(top_companies),
            "min_score": min_score,
            "top_companies": top_companies
        }
        
    except Exception as e:
        logger.error(f"Failed to get top companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get top companies: {str(e)}")

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_scoring_analytics(
    profile_version: str = Query(..., description="Profile version to analyze"),
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Get analytics about scoring results for a profile version.
    
    Returns comprehensive analytics including averages, top scores, and distribution.
    """
    try:
        analytics = service.get_scoring_analytics(profile_version)
        
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        
        return AnalyticsResponse(**analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/rescore-profile")
async def rescore_on_profile_update(
    old_profile_version: str,
    new_profile_version: str,
    brand_profile: Dict[str, Any],
    background_tasks: BackgroundTasks,
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Trigger re-scoring when personal brand profile is updated.
    
    This endpoint re-scores all previous opportunities with the updated profile.
    """
    try:
        logger.info(f"Re-scoring profile update: {old_profile_version} -> {new_profile_version}")
        
        # Add re-scoring to background tasks
        background_tasks.add_task(
            service.rescore_on_profile_update,
            old_profile_version,
            new_profile_version,
            brand_profile
        )
        
        return {
            "status": "success",
            "message": "Re-scoring initiated in background",
            "old_version": old_profile_version,
            "new_version": new_profile_version
        }
        
    except Exception as e:
        logger.error(f"Failed to initiate re-scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Re-scoring failed: {str(e)}")

@router.get("/demo/sample-scoring")
async def demo_sample_scoring(
    service: ScoringDatabaseService = Depends(get_scoring_service)
):
    """
    Demo endpoint showing sample scoring results.
    
    This endpoint demonstrates the scoring system with sample data.
    """
    try:
        from src.integrations.supabase.scoring_service import demo_comprehensive_scoring
        
        results = demo_comprehensive_scoring()
        
        return {
            "status": "success",
            "message": "Sample scoring completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Demo scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "ai-scoring-engine",
        "version": "1.0.0"
    }
