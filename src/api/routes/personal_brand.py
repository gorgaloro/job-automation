"""
Personal Brand API Endpoints

FastAPI routes for AI-powered personal brand discovery and management.
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

from src.integrations.supabase.personal_brand_service import PersonalBrandDatabaseService
from src.core.ai_career_coach import AICareerCoach
from src.core.personal_brand import PersonalBrandProfile, PersonalBrandAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/personal-brand", tags=["personal-brand"])

# Pydantic models for API
class InterviewStartRequest(BaseModel):
    """Request model for starting an interview"""
    user_id: Optional[str] = None

class InterviewResponseRequest(BaseModel):
    """Request model for interview responses"""
    session_id: str
    user_response: str

class ProfileFeedbackRequest(BaseModel):
    """Request model for profile feedback"""
    profile_id: str
    feedback: str

class ProfileUpdateRequest(BaseModel):
    """Request model for profile updates"""
    brand_summary: Optional[str] = None
    professional_identity: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    work_style: Optional[List[str]] = None
    leadership_style: Optional[List[str]] = None
    team_size_preference: Optional[str] = None
    remote_preference: Optional[str] = None
    company_stage: Optional[List[str]] = None
    company_size: Optional[List[str]] = None
    primary_motivators: Optional[List[str]] = None
    values: Optional[List[str]] = None
    deal_breakers: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None
    avoided_industries: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    skills_expertise: Optional[List[str]] = None

class InterviewResponse(BaseModel):
    """Response model for interview operations"""
    status: str
    session_id: Optional[str] = None
    profile_id: Optional[str] = None
    opening_question: Optional[str] = None
    next_question: Optional[str] = None
    summary: Optional[str] = None
    message: str

class ProfileResponse(BaseModel):
    """Response model for profile data"""
    id: str
    brand_summary: str
    professional_identity: str
    confidence_score: float
    completeness_score: float
    version: str
    created_at: str
    updated_at: str

class AnalyticsResponse(BaseModel):
    """Response model for analytics data"""
    total_profiles: int
    total_sessions: int
    profile_completeness: float
    profile_gaps: List[str]
    improvement_suggestions: List[str]

# Dependency to get personal brand service
def get_personal_brand_service() -> PersonalBrandDatabaseService:
    """Dependency to get personal brand database service"""
    return PersonalBrandDatabaseService()

@router.post("/interview/start", response_model=InterviewResponse)
async def start_interview(
    request: InterviewStartRequest,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Start a new AI-powered personal brand discovery interview.
    
    This endpoint initiates an intelligent conversation to help users discover
    their professional identity, preferences, and career alignment.
    """
    try:
        logger.info(f"Starting interview for user {request.user_id}")
        
        result = service.conduct_ai_interview(request.user_id)
        
        return InterviewResponse(**result)
        
    except Exception as e:
        logger.error(f"Interview start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@router.post("/interview/respond", response_model=InterviewResponse)
async def respond_to_interview(
    request: InterviewResponseRequest,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Respond to an ongoing AI interview session.
    
    This endpoint processes user responses and either continues the conversation
    or completes the interview and generates a personal brand profile.
    """
    try:
        logger.info(f"Processing response for session {request.session_id}")
        
        result = service.process_interview_response(request.session_id, request.user_response)
        
        return InterviewResponse(**result)
        
    except Exception as e:
        logger.error(f"Interview response processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

@router.get("/profiles", response_model=List[ProfileResponse])
async def list_profiles(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    List all personal brand profiles for a user.
    
    Returns profile summaries with key metadata and completeness scores.
    """
    try:
        profiles = service.get_profiles_for_user(user_id) if user_id else []
        
        profile_responses = []
        for profile in profiles:
            completeness = PersonalBrandAnalyzer.calculate_profile_completeness(profile)
            
            profile_response = ProfileResponse(
                id="profile_" + profile.profile_version,  # Would be actual ID in real implementation
                brand_summary=profile.brand_summary,
                professional_identity=profile.professional_identity,
                confidence_score=profile.confidence_score or 0.8,
                completeness_score=completeness,
                version=profile.profile_version,
                created_at=profile.created_at.isoformat(),
                updated_at=profile.updated_at.isoformat()
            )
            profile_responses.append(profile_response)
        
        return profile_responses
        
    except Exception as e:
        logger.error(f"Failed to list profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list profiles: {str(e)}")

@router.get("/profiles/{profile_id}")
async def get_profile(
    profile_id: str,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Get detailed information about a specific personal brand profile.
    
    Returns comprehensive profile data including all preferences and insights.
    """
    try:
        profile = service.get_personal_brand_profile(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Calculate additional metrics
        completeness = PersonalBrandAnalyzer.calculate_profile_completeness(profile)
        gaps = PersonalBrandAnalyzer.identify_profile_gaps(profile)
        suggestions = PersonalBrandAnalyzer.suggest_profile_improvements(profile)
        
        # Return comprehensive profile data
        profile_data = profile.to_dict()
        profile_data.update({
            "completeness_score": completeness,
            "profile_gaps": gaps,
            "improvement_suggestions": suggestions,
            "scoring_context": profile.get_scoring_context()
        })
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")

@router.get("/profiles/{profile_id}/insights")
async def get_profile_insights(
    profile_id: str,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Get AI-generated insights and recommendations for a profile.
    
    Returns strengths, opportunities, challenges, and actionable recommendations.
    """
    try:
        profile = service.get_personal_brand_profile(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Generate insights using AI coach
        coach = AICareerCoach()
        insights = coach.generate_profile_insights(profile)
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get insights for profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@router.patch("/profiles/{profile_id}")
async def update_profile(
    profile_id: str,
    request: ProfileUpdateRequest,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Update personal brand profile information.
    
    Allows updating various sections of a profile with validation.
    """
    try:
        # Convert request to update dictionary
        updates = {}
        
        # Core identity updates
        if request.brand_summary is not None:
            updates["brand_summary"] = request.brand_summary
        if request.professional_identity is not None:
            updates["professional_identity"] = request.professional_identity
        if request.unique_value_proposition is not None:
            updates["unique_value_proposition"] = request.unique_value_proposition
        
        # Work preferences updates
        work_prefs_updates = {}
        if request.work_style is not None:
            work_prefs_updates["work_style"] = request.work_style
        if request.leadership_style is not None:
            work_prefs_updates["leadership_style"] = request.leadership_style
        if request.team_size_preference is not None:
            work_prefs_updates["team_size_preference"] = request.team_size_preference
        if request.remote_preference is not None:
            work_prefs_updates["remote_preference"] = request.remote_preference
        if request.company_stage is not None:
            work_prefs_updates["company_stage"] = request.company_stage
        if request.company_size is not None:
            work_prefs_updates["company_size"] = request.company_size
        
        if work_prefs_updates:
            updates["work_preferences"] = work_prefs_updates
        
        # Career motivators updates
        motivators_updates = {}
        if request.primary_motivators is not None:
            motivators_updates["primary_motivators"] = request.primary_motivators
        if request.values is not None:
            motivators_updates["values"] = request.values
        if request.deal_breakers is not None:
            motivators_updates["deal_breakers"] = request.deal_breakers
        
        if motivators_updates:
            updates["career_motivators"] = motivators_updates
        
        # Industry preferences updates
        industry_updates = {}
        if request.preferred_industries is not None:
            industry_updates["preferred_industries"] = request.preferred_industries
        if request.avoided_industries is not None:
            industry_updates["avoided_industries"] = request.avoided_industries
        
        if industry_updates:
            updates["industry_preferences"] = industry_updates
        
        # Role preferences updates
        role_updates = {}
        if request.preferred_roles is not None:
            role_updates["preferred_roles"] = request.preferred_roles
        
        if role_updates:
            updates["role_preferences"] = role_updates
        
        # Skills updates
        if request.skills_expertise is not None:
            updates["skills_expertise"] = request.skills_expertise
        
        success = service.update_personal_brand_profile(profile_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found or update failed")
        
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "profile_id": profile_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.post("/profiles/{profile_id}/refine")
async def refine_profile_with_feedback(
    profile_id: str,
    request: ProfileFeedbackRequest,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Refine a profile using AI based on user feedback.
    
    Uses GPT-4 to intelligently update the profile based on user corrections.
    """
    try:
        profile = service.get_personal_brand_profile(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Use AI coach to refine profile
        coach = AICareerCoach()
        refined_profile = coach.refine_profile_with_feedback(profile, request.feedback)
        
        # Create new profile version
        new_profile_id = service.create_personal_brand_profile(refined_profile)
        
        return {
            "status": "success",
            "message": "Profile refined successfully",
            "original_profile_id": profile_id,
            "refined_profile_id": new_profile_id,
            "changes_made": "Profile updated based on your feedback"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refine profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: str,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Delete a personal brand profile.
    
    This is a soft delete that marks the profile as deleted.
    """
    try:
        success = service.delete_personal_brand_profile(profile_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "status": "success",
            "message": "Profile deleted successfully",
            "profile_id": profile_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Get analytics and insights about personal brand profiles.
    
    Returns profile completeness, gaps, and improvement suggestions.
    """
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        analytics = service.get_profile_analytics(user_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=500, detail=analytics["error"])
        
        return AnalyticsResponse(
            total_profiles=analytics["total_profiles"],
            total_sessions=analytics["total_sessions"],
            profile_completeness=analytics["profile_completeness"],
            profile_gaps=analytics["profile_gaps"],
            improvement_suggestions=analytics["improvement_suggestions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/sessions")
async def list_interview_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    List all interview sessions for a user.
    
    Returns session metadata and quality scores.
    """
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        sessions = service.get_sessions_for_user(user_id)
        
        session_data = []
        for session in sessions:
            session_info = {
                "session_id": session.session_id,
                "duration": session.session_duration,
                "quality_score": session.session_quality_score,
                "questions_count": len(session.questions_asked),
                "insights_count": len(session.key_insights),
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "has_generated_profile": session.generated_profile is not None
            }
            session_data.append(session_info)
        
        return {
            "total_sessions": len(sessions),
            "sessions": session_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_interview_session(
    session_id: str,
    service: PersonalBrandDatabaseService = Depends(get_personal_brand_service)
):
    """
    Get detailed information about a specific interview session.
    
    Returns transcript, questions, insights, and generated profile if available.
    """
    try:
        session = service.get_interview_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "transcript": session.transcript,
            "duration": session.session_duration,
            "questions_asked": session.questions_asked,
            "key_insights": session.key_insights,
            "quality_score": session.session_quality_score,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "generated_profile": session.generated_profile.to_dict() if session.generated_profile else None
        }
        
        return session_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "personal-brand-ai",
        "version": "1.0.0"
    }
