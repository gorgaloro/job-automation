#!/usr/bin/env python3
"""
Application Tracking Supabase Service - Epic 4

Database service for application tracking workflows, follow-ups, timeline events,
and analytics. Integrates with Epic 3 Job Applications database.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from core.application_tracking_engine import (
    WorkflowStage, FollowUpType, TimelineEventType,
    WorkflowRule, FollowUpSchedule, TimelineEvent, 
    ApplicationWorkflow, WorkflowAnalytics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationTrackingService:
    """
    Supabase database service for application tracking workflows and analytics.
    
    Handles workflow definitions, timeline events, follow-up schedules,
    and performance analytics with comprehensive error handling.
    """
    
    def __init__(self):
        """Initialize the Application Tracking Service"""
        self.demo_mode = True
        self.supabase = None
        
        # Try to initialize Supabase client
        if SUPABASE_AVAILABLE:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                try:
                    self.supabase = create_client(supabase_url, supabase_key)
                    self.demo_mode = False
                    logger.info("Application Tracking Service initialized with live Supabase")
                except Exception as e:
                    logger.warning(f"Failed to connect to Supabase: {str(e)}")
                    logger.info("Application Tracking Service initialized in demo mode")
            else:
                logger.warning("Supabase credentials not found, falling back to demo mode")
                logger.info("Application Tracking Service initialized in demo mode")
        else:
            logger.warning("Supabase client not available, running in demo mode")
            logger.info("Application Tracking Service initialized in demo mode")
    
    # Workflow Management
    
    def create_workflow(self, workflow: ApplicationWorkflow) -> bool:
        """
        Create a new workflow definition
        
        Args:
            workflow: Workflow to create
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Created workflow {workflow.workflow_id}")
                return True
            
            workflow_data = {
                'workflow_id': workflow.workflow_id,
                'name': workflow.name,
                'description': workflow.description,
                'stages': [stage.value for stage in workflow.stages],
                'rules': [asdict(rule) for rule in workflow.rules],
                'default_follow_ups': workflow.default_follow_ups,
                'is_template': workflow.is_template,
                'created_at': workflow.created_at.isoformat()
            }
            
            result = self.supabase.table('application_workflows').insert(workflow_data).execute()
            
            if result.data:
                logger.info(f"Created workflow {workflow.workflow_id}")
                return True
            else:
                logger.error("Workflow creation failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Workflow creation failed: {str(e)}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[ApplicationWorkflow]:
        """
        Get workflow by ID
        
        Args:
            workflow_id: Workflow ID to retrieve
            
        Returns:
            Workflow object or None
        """
        try:
            if self.demo_mode:
                # Return demo workflow
                return ApplicationWorkflow(
                    workflow_id=workflow_id,
                    name="Demo Tech Workflow",
                    description="Demo workflow for testing",
                    stages=[WorkflowStage.SUBMITTED, WorkflowStage.SCREENING, WorkflowStage.PHONE_SCREEN],
                    rules=[],
                    default_follow_ups={},
                    is_template=True
                )
            
            result = self.supabase.table('application_workflows').select('*').eq('workflow_id', workflow_id).execute()
            
            if result.data:
                data = result.data[0]
                # Convert back to ApplicationWorkflow object
                return ApplicationWorkflow(
                    workflow_id=data['workflow_id'],
                    name=data['name'],
                    description=data['description'],
                    stages=[WorkflowStage(stage) for stage in data['stages']],
                    rules=[],  # Would need to reconstruct WorkflowRule objects
                    default_follow_ups=data['default_follow_ups'],
                    is_template=data['is_template']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get workflow: {str(e)}")
            return None
    
    def list_workflow_templates(self) -> List[ApplicationWorkflow]:
        """
        Get all workflow templates
        
        Returns:
            List of workflow templates
        """
        try:
            if self.demo_mode:
                return [
                    ApplicationWorkflow(
                        workflow_id="wf_demo_tech",
                        name="Demo Tech Company",
                        description="Demo tech workflow",
                        stages=[WorkflowStage.SUBMITTED, WorkflowStage.SCREENING],
                        rules=[],
                        default_follow_ups={},
                        is_template=True
                    )
                ]
            
            result = self.supabase.table('application_workflows').select('*').eq('is_template', True).execute()
            
            workflows = []
            if result.data:
                for data in result.data:
                    workflows.append(ApplicationWorkflow(
                        workflow_id=data['workflow_id'],
                        name=data['name'],
                        description=data['description'],
                        stages=[WorkflowStage(stage) for stage in data['stages']],
                        rules=[],
                        default_follow_ups=data['default_follow_ups'],
                        is_template=data['is_template']
                    ))
            
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to list workflow templates: {str(e)}")
            return []
    
    # Timeline Management
    
    def add_timeline_event(self, event: TimelineEvent) -> bool:
        """
        Add a timeline event
        
        Args:
            event: Timeline event to add
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Added timeline event {event.event_id}")
                return True
            
            event_data = {
                'event_id': event.event_id,
                'application_id': event.application_id,
                'event_type': event.event_type.value,
                'event_date': event.event_date.isoformat(),
                'description': event.description,
                'metadata': event.metadata,
                'source': event.source,
                'created_at': event.created_at.isoformat()
            }
            
            result = self.supabase.table('application_timeline').insert(event_data).execute()
            
            if result.data:
                logger.info(f"Added timeline event {event.event_id}")
                return True
            else:
                logger.error("Timeline event creation failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Timeline event creation failed: {str(e)}")
            return False
    
    def get_application_timeline(self, application_id: str) -> List[TimelineEvent]:
        """
        Get timeline events for an application
        
        Args:
            application_id: Application ID
            
        Returns:
            List of timeline events
        """
        try:
            if self.demo_mode:
                return [
                    TimelineEvent(
                        event_id="evt_demo_001",
                        application_id=application_id,
                        event_type=TimelineEventType.APPLICATION_SUBMITTED,
                        event_date=datetime.utcnow() - timedelta(days=5),
                        description="Application submitted",
                        metadata={"demo": True}
                    ),
                    TimelineEvent(
                        event_id="evt_demo_002",
                        application_id=application_id,
                        event_type=TimelineEventType.FOLLOW_UP_SENT,
                        event_date=datetime.utcnow() - timedelta(days=2),
                        description="Follow-up email sent",
                        metadata={"type": "email", "demo": True}
                    )
                ]
            
            result = self.supabase.table('application_timeline').select('*').eq('application_id', application_id).order('event_date').execute()
            
            events = []
            if result.data:
                for data in result.data:
                    events.append(TimelineEvent(
                        event_id=data['event_id'],
                        application_id=data['application_id'],
                        event_type=TimelineEventType(data['event_type']),
                        event_date=datetime.fromisoformat(data['event_date']),
                        description=data['description'],
                        metadata=data['metadata'],
                        source=data['source']
                    ))
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get timeline events: {str(e)}")
            return []
    
    def get_timeline_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get timeline analytics for a user
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Timeline analytics
        """
        try:
            if self.demo_mode:
                return {
                    "total_events": 45,
                    "events_by_type": {
                        "application_submitted": 15,
                        "follow_up_sent": 12,
                        "response_received": 8,
                        "interview_scheduled": 5,
                        "status_change": 5
                    },
                    "average_response_time_hours": 72.5,
                    "most_active_days": ["Monday", "Tuesday", "Wednesday"]
                }
            
            # Complex analytics query would go here
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get timeline analytics: {str(e)}")
            return {}
    
    # Follow-up Management
    
    def schedule_follow_up(self, follow_up: FollowUpSchedule) -> bool:
        """
        Schedule a follow-up
        
        Args:
            follow_up: Follow-up schedule to create
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Scheduled follow-up {follow_up.schedule_id}")
                return True
            
            follow_up_data = {
                'schedule_id': follow_up.schedule_id,
                'application_id': follow_up.application_id,
                'follow_up_type': follow_up.follow_up_type.value,
                'scheduled_date': follow_up.scheduled_date.isoformat(),
                'template_id': follow_up.template_id,
                'is_automated': follow_up.is_automated,
                'is_completed': follow_up.is_completed,
                'completion_date': follow_up.completion_date.isoformat() if follow_up.completion_date else None,
                'effectiveness_score': follow_up.effectiveness_score,
                'created_at': follow_up.created_at.isoformat()
            }
            
            result = self.supabase.table('follow_up_schedules').insert(follow_up_data).execute()
            
            if result.data:
                logger.info(f"Scheduled follow-up {follow_up.schedule_id}")
                return True
            else:
                logger.error("Follow-up scheduling failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Follow-up scheduling failed: {str(e)}")
            return False
    
    def get_pending_follow_ups(self, user_id: str = None, days_ahead: int = 7) -> List[FollowUpSchedule]:
        """
        Get pending follow-ups
        
        Args:
            user_id: User ID (optional)
            days_ahead: Number of days ahead to look
            
        Returns:
            List of pending follow-ups
        """
        try:
            if self.demo_mode:
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
            
            end_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            result = self.supabase.table('follow_up_schedules').select('*').eq('is_completed', False).lte('scheduled_date', end_date.isoformat()).execute()
            
            follow_ups = []
            if result.data:
                for data in result.data:
                    follow_ups.append(FollowUpSchedule(
                        schedule_id=data['schedule_id'],
                        application_id=data['application_id'],
                        follow_up_type=FollowUpType(data['follow_up_type']),
                        scheduled_date=datetime.fromisoformat(data['scheduled_date']),
                        template_id=data['template_id'],
                        is_automated=data['is_automated'],
                        is_completed=data['is_completed'],
                        completion_date=datetime.fromisoformat(data['completion_date']) if data['completion_date'] else None,
                        effectiveness_score=data['effectiveness_score']
                    ))
            
            return follow_ups
            
        except Exception as e:
            logger.error(f"Failed to get pending follow-ups: {str(e)}")
            return []
    
    def complete_follow_up(self, schedule_id: str, effectiveness_score: float = None) -> bool:
        """
        Mark a follow-up as completed
        
        Args:
            schedule_id: Follow-up schedule ID
            effectiveness_score: Effectiveness score (0.0-1.0)
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Completed follow-up {schedule_id}")
                return True
            
            update_data = {
                'is_completed': True,
                'completion_date': datetime.utcnow().isoformat(),
                'effectiveness_score': effectiveness_score
            }
            
            result = self.supabase.table('follow_up_schedules').update(update_data).eq('schedule_id', schedule_id).execute()
            
            if result.data:
                logger.info(f"Completed follow-up {schedule_id}")
                return True
            else:
                logger.error("Follow-up completion failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Follow-up completion failed: {str(e)}")
            return False
    
    def get_follow_up_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get follow-up effectiveness analytics
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Follow-up analytics
        """
        try:
            if self.demo_mode:
                return {
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
            
            # Complex analytics query would go here
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get follow-up analytics: {str(e)}")
            return {}
    
    # Workflow Analytics
    
    def calculate_workflow_analytics(self, user_id: str, days: int = 30) -> Optional[WorkflowAnalytics]:
        """
        Calculate comprehensive workflow analytics
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Workflow analytics or None
        """
        try:
            if self.demo_mode:
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
            
            # Complex analytics calculation would go here
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate workflow analytics: {str(e)}")
            return None
    
    # Batch Operations
    
    def bulk_create_timeline_events(self, events: List[TimelineEvent]) -> int:
        """
        Bulk create timeline events
        
        Args:
            events: List of timeline events to create
            
        Returns:
            Number of events created
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Bulk created {len(events)} timeline events")
                return len(events)
            
            events_data = []
            for event in events:
                events_data.append({
                    'event_id': event.event_id,
                    'application_id': event.application_id,
                    'event_type': event.event_type.value,
                    'event_date': event.event_date.isoformat(),
                    'description': event.description,
                    'metadata': event.metadata,
                    'source': event.source,
                    'created_at': event.created_at.isoformat()
                })
            
            result = self.supabase.table('application_timeline').insert(events_data).execute()
            
            if result.data:
                created_count = len(result.data)
                logger.info(f"Bulk created {created_count} timeline events")
                return created_count
            else:
                logger.error("Bulk timeline event creation failed: No data returned")
                return 0
                
        except Exception as e:
            logger.error(f"Bulk timeline event creation failed: {str(e)}")
            return 0
    
    def export_tracking_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all tracking data for a user
        
        Args:
            user_id: User ID to export data for
            
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
                "analytics": {}
            }
            
            if self.demo_mode:
                export_data["demo_mode"] = True
                export_data["workflows"] = [{"workflow_id": "demo", "name": "Demo Workflow"}]
                export_data["timeline_events"] = [{"event_id": "demo", "type": "demo"}]
                export_data["follow_up_schedules"] = [{"schedule_id": "demo", "type": "demo"}]
                logger.info(f"Demo: Exported tracking data for user {user_id}")
            else:
                # Query all tables for user data
                pass
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export tracking data: {str(e)}")
            return {}
