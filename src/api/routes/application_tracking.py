#!/usr/bin/env python3
"""
Application Tracking API Routes - Epic 4

FastAPI routes for application tracking workflows, follow-ups, timeline events,
and analytics. Integrates with Epic 3 Job Applications system.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.application_tracking_engine import (
    ApplicationTrackingEngine, WorkflowStage, FollowUpType, 
    TimelineEventType, WorkflowAnalytics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/tracking", tags=["Application Tracking"])

# Initialize tracking engine
tracking_engine = ApplicationTrackingEngine()

# Pydantic Models

class WorkflowStageUpdate(BaseModel):
    """Request model for workflow stage updates"""
    application_id: str = Field(..., description="Application ID to update")
    new_stage: str = Field(..., description="New workflow stage")
    notes: Optional[str] = Field(None, description="Optional notes about the stage change")
    source: str = Field("manual", description="Source of the update")

class FollowUpRequest(BaseModel):
    """Request model for follow-up scheduling"""
    application_id: str = Field(..., description="Application ID")
    follow_up_type: str = Field(..., description="Type of follow-up (email, linkedin, phone)")
    scheduled_date: datetime = Field(..., description="When to schedule the follow-up")
    template_id: Optional[str] = Field(None, description="Template ID to use")
    is_automated: bool = Field(True, description="Whether this is an automated follow-up")

class FollowUpCompletion(BaseModel):
    """Request model for follow-up completion"""
    schedule_id: str = Field(..., description="Follow-up schedule ID")
    effectiveness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Effectiveness score (0.0-1.0)")

class TimelineEventCreate(BaseModel):
    """Request model for timeline event creation"""
    application_id: str = Field(..., description="Application ID")
    event_type: str = Field(..., description="Type of timeline event")
    description: str = Field(..., description="Event description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")
    source: str = Field("manual", description="Source of the event")

class WorkflowCreateRequest(BaseModel):
    """Request model for workflow creation"""
    application_id: str = Field(..., description="Application ID")
    workflow_template: str = Field("tech_standard", description="Workflow template to use")

class AnalyticsRequest(BaseModel):
    """Request model for analytics"""
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    days: int = Field(30, ge=1, le=365, description="Number of days to analyze")

# Response Models

class WorkflowStageResponse(BaseModel):
    """Response model for workflow stage updates"""
    success: bool
    application_id: str
    new_stage: str
    message: str

class FollowUpResponse(BaseModel):
    """Response model for follow-up operations"""
    success: bool
    schedule_id: str
    message: str

class TimelineEventResponse(BaseModel):
    """Response model for timeline events"""
    event_id: str
    application_id: str
    event_type: str
    event_date: datetime
    description: str
    metadata: Dict[str, Any]
    source: str

class WorkflowAnalyticsResponse(BaseModel):
    """Response model for workflow analytics"""
    total_applications: int
    stage_conversion_rates: Dict[str, float]
    average_time_per_stage: Dict[str, float]
    follow_up_effectiveness: Dict[str, float]
    predicted_success_rate: float
    bottleneck_stages: List[str]
    optimization_recommendations: List[str]

class FollowUpScheduleResponse(BaseModel):
    """Response model for follow-up schedules"""
    schedule_id: str
    application_id: str
    follow_up_type: str
    scheduled_date: datetime
    template_id: Optional[str]
    is_automated: bool
    is_completed: bool

# API Endpoints

@router.post("/workflows/create", response_model=Dict[str, Any])
async def create_application_workflow(request: WorkflowCreateRequest):
    """
    Create a workflow for an application
    
    Creates a new workflow instance for an application using a predefined template.
    Automatically schedules default follow-ups and creates initial timeline events.
    """
    try:
        logger.info(f"Creating workflow for application {request.application_id}")
        
        success = tracking_engine.create_application_workflow(
            application_id=request.application_id,
            workflow_template=request.workflow_template
        )
        
        if success:
            return {
                "success": True,
                "application_id": request.application_id,
                "workflow_template": request.workflow_template,
                "message": "Workflow created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create workflow")
            
    except Exception as e:
        logger.error(f"Workflow creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@router.put("/workflows/stage", response_model=WorkflowStageResponse)
async def update_workflow_stage(request: WorkflowStageUpdate):
    """
    Update application workflow stage
    
    Updates the workflow stage for an application, triggers automation rules,
    and schedules appropriate follow-ups based on the new stage.
    """
    try:
        logger.info(f"Updating stage for application {request.application_id}")
        
        # Validate stage
        try:
            stage = WorkflowStage(request.new_stage)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid workflow stage: {request.new_stage}")
        
        success = tracking_engine.update_application_stage(
            application_id=request.application_id,
            new_stage=stage,
            notes=request.notes or "",
            source=request.source
        )
        
        if success:
            return WorkflowStageResponse(
                success=True,
                application_id=request.application_id,
                new_stage=request.new_stage,
                message="Workflow stage updated successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to update workflow stage")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stage update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stage update failed: {str(e)}")

@router.get("/timeline/{application_id}", response_model=List[TimelineEventResponse])
async def get_application_timeline(
    application_id: str = Path(..., description="Application ID")
):
    """
    Get application timeline
    
    Retrieves the complete timeline of events for an application,
    including status changes, follow-ups, and external interactions.
    """
    try:
        logger.info(f"Getting timeline for application {application_id}")
        
        timeline_events = tracking_engine.get_application_timeline(application_id)
        
        response_events = []
        for event in timeline_events:
            response_events.append(TimelineEventResponse(
                event_id=event.event_id,
                application_id=event.application_id,
                event_type=event.event_type.value,
                event_date=event.event_date,
                description=event.description,
                metadata=event.metadata,
                source=event.source
            ))
        
        return response_events
        
    except Exception as e:
        logger.error(f"Timeline retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Timeline retrieval failed: {str(e)}")

@router.post("/timeline/events", response_model=Dict[str, Any])
async def create_timeline_event(request: TimelineEventCreate):
    """
    Create a timeline event
    
    Manually creates a timeline event for an application.
    Useful for logging external interactions or manual updates.
    """
    try:
        logger.info(f"Creating timeline event for application {request.application_id}")
        
        # Validate event type
        try:
            event_type = TimelineEventType(request.event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {request.event_type}")
        
        from core.application_tracking_engine import TimelineEvent
        
        event = TimelineEvent(
            event_id=f"evt_{uuid4().hex[:8]}",
            application_id=request.application_id,
            event_type=event_type,
            event_date=datetime.utcnow(),
            description=request.description,
            metadata=request.metadata,
            source=request.source
        )
        
        # Add to database via tracking engine
        success = tracking_engine.db_service.add_timeline_event(event) if tracking_engine.db_service else True
        
        if success:
            return {
                "success": True,
                "event_id": event.event_id,
                "message": "Timeline event created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create timeline event")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Timeline event creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Timeline event creation failed: {str(e)}")

@router.get("/follow-ups/pending", response_model=List[FollowUpScheduleResponse])
async def get_pending_follow_ups(
    user_id: Optional[str] = Query(None, description="User ID (optional)"),
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days ahead to look")
):
    """
    Get pending follow-ups
    
    Retrieves all pending follow-ups for a user within the specified timeframe.
    Useful for daily/weekly follow-up planning and execution.
    """
    try:
        logger.info(f"Getting pending follow-ups for user {user_id}")
        
        follow_ups = tracking_engine.get_pending_follow_ups(user_id)
        
        response_follow_ups = []
        for follow_up in follow_ups:
            # Filter by days_ahead
            days_until = (follow_up.scheduled_date - datetime.utcnow()).days
            if days_until <= days_ahead:
                response_follow_ups.append(FollowUpScheduleResponse(
                    schedule_id=follow_up.schedule_id,
                    application_id=follow_up.application_id,
                    follow_up_type=follow_up.follow_up_type.value,
                    scheduled_date=follow_up.scheduled_date,
                    template_id=follow_up.template_id,
                    is_automated=follow_up.is_automated,
                    is_completed=follow_up.is_completed
                ))
        
        return response_follow_ups
        
    except Exception as e:
        logger.error(f"Follow-up retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Follow-up retrieval failed: {str(e)}")

@router.post("/follow-ups/schedule", response_model=FollowUpResponse)
async def schedule_follow_up(request: FollowUpRequest):
    """
    Schedule a follow-up
    
    Manually schedules a follow-up for an application.
    Can be used to override automatic scheduling or add custom follow-ups.
    """
    try:
        logger.info(f"Scheduling follow-up for application {request.application_id}")
        
        # Validate follow-up type
        try:
            follow_up_type = FollowUpType(request.follow_up_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid follow-up type: {request.follow_up_type}")
        
        from core.application_tracking_engine import FollowUpSchedule
        
        follow_up = FollowUpSchedule(
            schedule_id=f"fu_{uuid4().hex[:8]}",
            application_id=request.application_id,
            follow_up_type=follow_up_type,
            scheduled_date=request.scheduled_date,
            template_id=request.template_id,
            is_automated=request.is_automated
        )
        
        # Schedule via tracking engine
        success = tracking_engine.db_service.schedule_follow_up(follow_up) if tracking_engine.db_service else True
        
        if success:
            return FollowUpResponse(
                success=True,
                schedule_id=follow_up.schedule_id,
                message="Follow-up scheduled successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to schedule follow-up")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Follow-up scheduling failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Follow-up scheduling failed: {str(e)}")

@router.put("/follow-ups/complete", response_model=FollowUpResponse)
async def complete_follow_up(request: FollowUpCompletion):
    """
    Mark follow-up as completed
    
    Marks a scheduled follow-up as completed and optionally records
    an effectiveness score for analytics and optimization.
    """
    try:
        logger.info(f"Completing follow-up {request.schedule_id}")
        
        success = tracking_engine.complete_follow_up(
            schedule_id=request.schedule_id,
            effectiveness_score=request.effectiveness_score
        )
        
        if success:
            return FollowUpResponse(
                success=True,
                schedule_id=request.schedule_id,
                message="Follow-up completed successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to complete follow-up")
            
    except Exception as e:
        logger.error(f"Follow-up completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Follow-up completion failed: {str(e)}")

@router.get("/analytics/workflow", response_model=WorkflowAnalyticsResponse)
async def get_workflow_analytics(
    user_id: Optional[str] = Query(None, description="User ID (optional)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get workflow analytics
    
    Provides comprehensive analytics on workflow performance including
    conversion rates, timing, bottlenecks, and optimization recommendations.
    """
    try:
        logger.info(f"Getting workflow analytics for user {user_id}")
        
        analytics = tracking_engine.get_workflow_analytics(user_id, days)
        
        if analytics:
            return WorkflowAnalyticsResponse(
                total_applications=analytics.total_applications,
                stage_conversion_rates=analytics.stage_conversion_rates,
                average_time_per_stage=analytics.average_time_per_stage,
                follow_up_effectiveness=analytics.follow_up_effectiveness,
                predicted_success_rate=analytics.predicted_success_rate,
                bottleneck_stages=analytics.bottleneck_stages,
                optimization_recommendations=analytics.optimization_recommendations
            )
        else:
            raise HTTPException(status_code=404, detail="Analytics data not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.get("/analytics/follow-ups", response_model=Dict[str, Any])
async def get_follow_up_analytics(
    user_id: Optional[str] = Query(None, description="User ID (optional)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get follow-up analytics
    
    Provides detailed analytics on follow-up effectiveness including
    completion rates, response rates, and optimal timing insights.
    """
    try:
        logger.info(f"Getting follow-up analytics for user {user_id}")
        
        analytics = tracking_engine.db_service.get_follow_up_analytics(user_id, days) if tracking_engine.db_service else {
            "total_follow_ups": 28,
            "completed_follow_ups": 22,
            "completion_rate": 0.786,
            "effectiveness_by_type": {
                "email": 0.32,
                "linkedin": 0.18,
                "phone": 0.45
            },
            "average_effectiveness": 0.317,
            "best_timing": {
                "day_of_week": "Tuesday",
                "hour_of_day": 10
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Follow-up analytics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Follow-up analytics retrieval failed: {str(e)}")

@router.get("/optimization/{application_id}", response_model=List[str])
async def get_optimization_suggestions(
    application_id: str = Path(..., description="Application ID")
):
    """
    Get optimization suggestions
    
    Provides AI-powered optimization suggestions for a specific application
    based on historical patterns and performance data.
    """
    try:
        logger.info(f"Getting optimization suggestions for application {application_id}")
        
        suggestions = tracking_engine.suggest_workflow_optimizations(application_id)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Optimization suggestions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization suggestions failed: {str(e)}")

@router.get("/export", response_model=Dict[str, Any])
async def export_tracking_data(
    user_id: str = Query(..., description="User ID to export data for"),
    format: str = Query("json", description="Export format (json, csv)")
):
    """
    Export tracking data
    
    Exports comprehensive tracking data for a user including workflows,
    timeline events, follow-ups, and analytics for backup or analysis.
    """
    try:
        logger.info(f"Exporting tracking data for user {user_id}")
        
        export_data = tracking_engine.export_tracking_data(user_id, format)
        
        return export_data
        
    except Exception as e:
        logger.error(f"Data export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def tracking_health_check():
    """
    Health check for tracking system
    
    Provides status information about the tracking system components
    and their operational status.
    """
    try:
        return {
            "status": "healthy",
            "tracking_engine": "operational",
            "database_service": "available" if tracking_engine.db_service else "unavailable",
            "demo_mode": tracking_engine.demo_mode,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/demo", response_model=Dict[str, Any])
async def tracking_demo():
    """
    Comprehensive tracking system demo
    
    Demonstrates all tracking system capabilities with sample data
    for testing and validation purposes.
    """
    try:
        demo_results = {
            "demo_type": "Application Tracking System",
            "timestamp": datetime.utcnow().isoformat(),
            "results": {}
        }
        
        # Demo workflow creation
        workflow_success = tracking_engine.create_application_workflow("demo_app_001", "tech_standard")
        demo_results["results"]["workflow_creation"] = {
            "success": workflow_success,
            "application_id": "demo_app_001",
            "template": "tech_standard"
        }
        
        # Demo stage update
        from core.application_tracking_engine import WorkflowStage
        stage_success = tracking_engine.update_application_stage(
            "demo_app_001", 
            WorkflowStage.PHONE_SCREEN, 
            "Demo stage update"
        )
        demo_results["results"]["stage_update"] = {
            "success": stage_success,
            "new_stage": "phone_screen"
        }
        
        # Demo timeline
        timeline = tracking_engine.get_application_timeline("demo_app_001")
        demo_results["results"]["timeline"] = {
            "event_count": len(timeline),
            "events": [{"type": event.event_type.value, "description": event.description} for event in timeline[:3]]
        }
        
        # Demo follow-ups
        follow_ups = tracking_engine.get_pending_follow_ups()
        demo_results["results"]["follow_ups"] = {
            "pending_count": len(follow_ups),
            "follow_ups": [{"type": fu.follow_up_type.value, "scheduled": fu.scheduled_date.isoformat()} for fu in follow_ups[:3]]
        }
        
        # Demo analytics
        analytics = tracking_engine.get_workflow_analytics()
        demo_results["results"]["analytics"] = {
            "total_applications": analytics.total_applications if analytics else 0,
            "predicted_success_rate": analytics.predicted_success_rate if analytics else 0.0,
            "bottleneck_stages": analytics.bottleneck_stages if analytics else []
        }
        
        return demo_results
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")
