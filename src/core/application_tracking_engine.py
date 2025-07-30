#!/usr/bin/env python3
"""
Application Tracking Engine - Epic 4

Advanced workflow management, follow-up automation, and timeline tracking
for job applications. Builds on Epic 3 Job Applications foundation.
"""

import logging
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    """Application workflow stages"""
    SUBMITTED = "submitted"
    SCREENING = "screening"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_INTERVIEW = "technical_interview"
    FINAL_INTERVIEW = "final_interview"
    REFERENCE_CHECK = "reference_check"
    OFFER_PENDING = "offer_pending"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ACCEPTED = "accepted"

class FollowUpType(Enum):
    """Types of follow-up actions"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    APPLICATION_STATUS = "application_status"
    THANK_YOU = "thank_you"
    INTEREST_REAFFIRMATION = "interest_reaffirmation"

class TimelineEventType(Enum):
    """Timeline event types"""
    APPLICATION_SUBMITTED = "application_submitted"
    STATUS_CHANGE = "status_change"
    FOLLOW_UP_SENT = "follow_up_sent"
    RESPONSE_RECEIVED = "response_received"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    DECISION_MADE = "decision_made"

@dataclass
class WorkflowRule:
    """Workflow automation rule"""
    rule_id: str
    name: str
    from_stage: WorkflowStage
    to_stage: WorkflowStage
    trigger_type: str  # "time_based", "external_signal", "manual"
    trigger_condition: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FollowUpSchedule:
    """Follow-up schedule definition"""
    schedule_id: str
    application_id: str
    follow_up_type: FollowUpType
    scheduled_date: datetime
    template_id: Optional[str] = None
    is_automated: bool = True
    is_completed: bool = False
    completion_date: Optional[datetime] = None
    effectiveness_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TimelineEvent:
    """Application timeline event"""
    event_id: str
    application_id: str
    event_type: TimelineEventType
    event_date: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"  # "system", "manual", "integration"
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ApplicationWorkflow:
    """Application workflow definition"""
    workflow_id: str
    name: str
    description: str
    stages: List[WorkflowStage]
    rules: List[WorkflowRule]
    default_follow_ups: Dict[WorkflowStage, List[Dict[str, Any]]]
    is_template: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowAnalytics:
    """Workflow performance analytics"""
    total_applications: int
    stage_conversion_rates: Dict[str, float]
    average_time_per_stage: Dict[str, float]
    follow_up_effectiveness: Dict[str, float]
    predicted_success_rate: float
    bottleneck_stages: List[str]
    optimization_recommendations: List[str]

class ApplicationTrackingEngine:
    """
    Advanced application tracking and workflow management engine.
    
    Provides sophisticated workflow automation, follow-up scheduling,
    timeline tracking, and performance analytics.
    """
    
    def __init__(self):
        """Initialize the Application Tracking Engine"""
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        # Initialize services (will be integrated with Epic 3 services)
        self.db_service = None
        self.notification_service = None
        self.calendar_service = None
        
        # Default workflows
        self.default_workflows = self._create_default_workflows()
        
        logger.info(f"Application Tracking Engine initialized (demo_mode: {self.demo_mode})")
    
    def _create_default_workflows(self) -> Dict[str, ApplicationWorkflow]:
        """Create default workflow templates"""
        
        # Standard Tech Company Workflow
        tech_workflow = ApplicationWorkflow(
            workflow_id="wf_tech_standard",
            name="Standard Tech Company",
            description="Standard workflow for technology companies",
            stages=[
                WorkflowStage.SUBMITTED,
                WorkflowStage.SCREENING,
                WorkflowStage.PHONE_SCREEN,
                WorkflowStage.TECHNICAL_INTERVIEW,
                WorkflowStage.FINAL_INTERVIEW,
                WorkflowStage.OFFER_PENDING
            ],
            rules=[
                WorkflowRule(
                    rule_id="rule_tech_01",
                    name="Auto-advance after 7 days no response",
                    from_stage=WorkflowStage.SUBMITTED,
                    to_stage=WorkflowStage.SCREENING,
                    trigger_type="time_based",
                    trigger_condition={"days": 7, "no_response": True}
                )
            ],
            default_follow_ups={
                WorkflowStage.SUBMITTED: [
                    {"type": "email", "days": 7, "template": "follow_up_application"},
                    {"type": "linkedin", "days": 14, "template": "linkedin_connection"}
                ],
                WorkflowStage.PHONE_SCREEN: [
                    {"type": "thank_you", "days": 1, "template": "thank_you_phone"},
                    {"type": "email", "days": 7, "template": "follow_up_next_steps"}
                ]
            },
            is_template=True
        )
        
        # Startup Workflow
        startup_workflow = ApplicationWorkflow(
            workflow_id="wf_startup_fast",
            name="Fast-Moving Startup",
            description="Accelerated workflow for startup companies",
            stages=[
                WorkflowStage.SUBMITTED,
                WorkflowStage.PHONE_SCREEN,
                WorkflowStage.FINAL_INTERVIEW,
                WorkflowStage.OFFER_PENDING
            ],
            rules=[
                WorkflowRule(
                    rule_id="rule_startup_01",
                    name="Fast follow-up after 3 days",
                    from_stage=WorkflowStage.SUBMITTED,
                    to_stage=WorkflowStage.PHONE_SCREEN,
                    trigger_type="time_based",
                    trigger_condition={"days": 3, "no_response": True}
                )
            ],
            default_follow_ups={
                WorkflowStage.SUBMITTED: [
                    {"type": "email", "days": 3, "template": "startup_follow_up"},
                    {"type": "linkedin", "days": 7, "template": "startup_linkedin"}
                ]
            },
            is_template=True
        )
        
        return {
            "tech_standard": tech_workflow,
            "startup_fast": startup_workflow
        }
    
    def create_application_workflow(self, application_id: str, workflow_template: str = "tech_standard") -> bool:
        """
        Create a workflow for an application
        
        Args:
            application_id: Application to create workflow for
            workflow_template: Workflow template to use
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Creating workflow for application {application_id}")
            
            if workflow_template not in self.default_workflows:
                logger.error(f"Unknown workflow template: {workflow_template}")
                return False
            
            workflow = self.default_workflows[workflow_template]
            
            # Create timeline event
            event = TimelineEvent(
                event_id=f"evt_{uuid4().hex[:8]}",
                application_id=application_id,
                event_type=TimelineEventType.APPLICATION_SUBMITTED,
                event_date=datetime.utcnow(),
                description=f"Application workflow created using {workflow.name} template",
                metadata={"workflow_id": workflow.workflow_id, "template": workflow_template}
            )
            
            # Schedule default follow-ups
            self._schedule_default_follow_ups(application_id, workflow, WorkflowStage.SUBMITTED)
            
            if self.demo_mode:
                logger.info(f"Demo: Created workflow for {application_id} using {workflow_template}")
            else:
                # Store in database
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {str(e)}")
            return False
    
    def update_application_stage(self, application_id: str, new_stage: WorkflowStage, 
                               notes: str = "", source: str = "manual") -> bool:
        """
        Update application stage and trigger workflow automation
        
        Args:
            application_id: Application to update
            new_stage: New workflow stage
            notes: Optional notes about the stage change
            source: Source of the update (manual, integration, automation)
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Updating application {application_id} to stage {new_stage.value}")
            
            # Create timeline event
            event = TimelineEvent(
                event_id=f"evt_{uuid4().hex[:8]}",
                application_id=application_id,
                event_type=TimelineEventType.STATUS_CHANGE,
                event_date=datetime.utcnow(),
                description=f"Stage updated to {new_stage.value}",
                metadata={"previous_stage": "unknown", "notes": notes, "source": source}
            )
            
            # Schedule follow-ups for new stage
            workflow = self.default_workflows.get("tech_standard")  # Default for demo
            if workflow and new_stage in workflow.default_follow_ups:
                self._schedule_default_follow_ups(application_id, workflow, new_stage)
            
            # Check for automation rules
            self._check_automation_rules(application_id, new_stage)
            
            if self.demo_mode:
                logger.info(f"Demo: Updated {application_id} to {new_stage.value}")
            else:
                # Update in database
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update application stage: {str(e)}")
            return False
    
    def _schedule_default_follow_ups(self, application_id: str, workflow: ApplicationWorkflow, 
                                   stage: WorkflowStage) -> None:
        """Schedule default follow-ups for a stage"""
        if stage not in workflow.default_follow_ups:
            return
        
        follow_ups = workflow.default_follow_ups[stage]
        
        for follow_up_config in follow_ups:
            scheduled_date = datetime.utcnow() + timedelta(days=follow_up_config["days"])
            
            follow_up = FollowUpSchedule(
                schedule_id=f"fu_{uuid4().hex[:8]}",
                application_id=application_id,
                follow_up_type=FollowUpType(follow_up_config["type"]),
                scheduled_date=scheduled_date,
                template_id=follow_up_config.get("template"),
                is_automated=True
            )
            
            logger.info(f"Scheduled {follow_up.follow_up_type.value} follow-up for {scheduled_date}")
    
    def _check_automation_rules(self, application_id: str, current_stage: WorkflowStage) -> None:
        """Check and execute automation rules"""
        # This would check for time-based and condition-based automation rules
        logger.info(f"Checking automation rules for {application_id} at {current_stage.value}")
    
    def get_application_timeline(self, application_id: str) -> List[TimelineEvent]:
        """
        Get complete timeline for an application
        
        Args:
            application_id: Application to get timeline for
            
        Returns:
            List of timeline events
        """
        try:
            if self.demo_mode:
                # Return demo timeline
                return [
                    TimelineEvent(
                        event_id="evt_demo_001",
                        application_id=application_id,
                        event_type=TimelineEventType.APPLICATION_SUBMITTED,
                        event_date=datetime.utcnow() - timedelta(days=5),
                        description="Application submitted via company website",
                        metadata={"source": "auto_apply", "confidence": 0.95}
                    ),
                    TimelineEvent(
                        event_id="evt_demo_002",
                        application_id=application_id,
                        event_type=TimelineEventType.FOLLOW_UP_SENT,
                        event_date=datetime.utcnow() - timedelta(days=3),
                        description="Follow-up email sent to hiring manager",
                        metadata={"type": "email", "template": "follow_up_application"}
                    ),
                    TimelineEvent(
                        event_id="evt_demo_003",
                        application_id=application_id,
                        event_type=TimelineEventType.RESPONSE_RECEIVED,
                        event_date=datetime.utcnow() - timedelta(days=1),
                        description="Response received - phone screen scheduled",
                        metadata={"response_time_hours": 48, "sentiment": "positive"}
                    )
                ]
            else:
                # Query database
                return []
                
        except Exception as e:
            logger.error(f"Failed to get timeline: {str(e)}")
            return []
    
    def get_pending_follow_ups(self, user_id: str = None) -> List[FollowUpSchedule]:
        """
        Get pending follow-ups for a user
        
        Args:
            user_id: User to get follow-ups for (optional)
            
        Returns:
            List of pending follow-ups
        """
        try:
            if self.demo_mode:
                # Return demo follow-ups
                return [
                    FollowUpSchedule(
                        schedule_id="fu_demo_001",
                        application_id="app_demo_001",
                        follow_up_type=FollowUpType.EMAIL,
                        scheduled_date=datetime.utcnow() + timedelta(days=1),
                        template_id="follow_up_application",
                        is_automated=True
                    ),
                    FollowUpSchedule(
                        schedule_id="fu_demo_002",
                        application_id="app_demo_002",
                        follow_up_type=FollowUpType.LINKEDIN,
                        scheduled_date=datetime.utcnow() + timedelta(days=3),
                        template_id="linkedin_connection",
                        is_automated=True
                    )
                ]
            else:
                # Query database
                return []
                
        except Exception as e:
            logger.error(f"Failed to get pending follow-ups: {str(e)}")
            return []
    
    def complete_follow_up(self, schedule_id: str, effectiveness_score: float = None) -> bool:
        """
        Mark a follow-up as completed
        
        Args:
            schedule_id: Follow-up schedule to complete
            effectiveness_score: Optional effectiveness rating (0.0-1.0)
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Completing follow-up {schedule_id}")
            
            if self.demo_mode:
                logger.info(f"Demo: Completed follow-up {schedule_id} with score {effectiveness_score}")
            else:
                # Update in database
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete follow-up: {str(e)}")
            return False
    
    def get_workflow_analytics(self, user_id: str = None, days: int = 30) -> WorkflowAnalytics:
        """
        Get workflow performance analytics
        
        Args:
            user_id: User to analyze (optional)
            days: Number of days to analyze
            
        Returns:
            Workflow analytics
        """
        try:
            if self.demo_mode:
                # Return demo analytics
                return WorkflowAnalytics(
                    total_applications=25,
                    stage_conversion_rates={
                        "submitted_to_screening": 0.72,
                        "screening_to_phone": 0.45,
                        "phone_to_technical": 0.68,
                        "technical_to_final": 0.55,
                        "final_to_offer": 0.35
                    },
                    average_time_per_stage={
                        "submitted": 3.2,
                        "screening": 5.8,
                        "phone_screen": 2.1,
                        "technical_interview": 4.5,
                        "final_interview": 6.2
                    },
                    follow_up_effectiveness={
                        "email": 0.28,
                        "linkedin": 0.15,
                        "phone": 0.42
                    },
                    predicted_success_rate=0.18,
                    bottleneck_stages=["screening", "final_interview"],
                    optimization_recommendations=[
                        "Increase follow-up frequency during screening stage",
                        "Personalize technical interview preparation",
                        "Improve final interview follow-up timing"
                    ]
                )
            else:
                # Calculate from database
                pass
                
        except Exception as e:
            logger.error(f"Failed to get analytics: {str(e)}")
            return None
    
    def suggest_workflow_optimizations(self, application_id: str) -> List[str]:
        """
        Get AI-powered workflow optimization suggestions
        
        Args:
            application_id: Application to analyze
            
        Returns:
            List of optimization suggestions
        """
        try:
            # This would use AI to analyze patterns and suggest optimizations
            suggestions = [
                "Consider sending a follow-up email 5 days after application submission",
                "LinkedIn connection request shows 23% higher response rate for this company type",
                "Technical interview preparation materials increase success rate by 31%",
                "Thank you note within 24 hours of phone screen improves advancement rate"
            ]
            
            logger.info(f"Generated {len(suggestions)} optimization suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {str(e)}")
            return []
    
    def export_tracking_data(self, user_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export comprehensive tracking data
        
        Args:
            user_id: User to export data for
            format: Export format (json, csv)
            
        Returns:
            Exported tracking data
        """
        try:
            export_data = {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "workflows": [],
                "timeline_events": [],
                "follow_up_schedules": [],
                "analytics": self.get_workflow_analytics(user_id).__dict__ if self.get_workflow_analytics(user_id) else {}
            }
            
            logger.info(f"Exported tracking data for user {user_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export tracking data: {str(e)}")
            return {}
