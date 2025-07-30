"""
HubSpot Task Synchronization Module

This module provides bidirectional synchronization between the AI job search platform
and HubSpot tasks, enabling seamless task management across both systems.

Features:
- Sync job search action items to HubSpot tasks
- Import HubSpot tasks as action items
- Automatic task status updates
- Task categorization and prioritization
- Due date and reminder management
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HubSpot API Configuration
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TaskStatus(Enum):
    """Task status options"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    DEFERRED = "DEFERRED"

class TaskType(Enum):
    """Job search task categories"""
    APPLICATION = "APPLICATION"
    INTERVIEW = "INTERVIEW"
    FOLLOW_UP = "FOLLOW_UP"
    NETWORKING = "NETWORKING"
    RESEARCH = "RESEARCH"
    DOCUMENT_PREP = "DOCUMENT_PREP"
    SYSTEM_MAINTENANCE = "SYSTEM_MAINTENANCE"

@dataclass
class JobSearchTask:
    """Job search task data structure"""
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[datetime] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    contact_email: Optional[str] = None
    hubspot_task_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_hubspot_format(self) -> Dict[str, Any]:
        """Convert task to HubSpot API format"""
        properties = {
            "hs_task_subject": self.title,
            "hs_task_body": self.description,
            "hs_task_priority": self.priority.value,
            "hs_task_status": self.status.value,
            "hs_task_type": "TODO",  # HubSpot task type
        }
        
        if self.due_date:
            # Convert to HubSpot timestamp format (milliseconds since epoch)
            properties["hs_timestamp"] = int(self.due_date.timestamp() * 1000)
        
        # Add custom properties for job search context
        if self.company_name:
            properties["job_search_company"] = self.company_name
        if self.job_title:
            properties["job_search_position"] = self.job_title
        if self.task_type:
            properties["job_search_task_type"] = self.task_type.value
            
        return properties

class HubSpotTaskSync:
    """HubSpot task synchronization service"""
    
    def __init__(self):
        if not HUBSPOT_API_KEY:
            raise ValueError("HUBSPOT_API_KEY environment variable is required")
        
        self.base_url = HUBSPOT_BASE_URL
        self.headers = HEADERS
        
    def create_task(self, task: JobSearchTask) -> Optional[str]:
        """
        Create a new task in HubSpot
        
        Args:
            task: JobSearchTask object to create
            
        Returns:
            HubSpot task ID if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/tasks"
            payload = {
                "properties": task.to_hubspot_format()
            }
            
            logger.info(f"Creating HubSpot task: {task.title}")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            logger.info(f"✅ Created HubSpot task {task_id}: {task.title}")
            return task_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to create HubSpot task: {e}")
            return None
    
    def update_task(self, task_id: str, task: JobSearchTask) -> bool:
        """
        Update an existing HubSpot task
        
        Args:
            task_id: HubSpot task ID
            task: Updated task data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/tasks/{task_id}"
            payload = {
                "properties": task.to_hubspot_format()
            }
            
            logger.info(f"Updating HubSpot task {task_id}: {task.title}")
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"✅ Updated HubSpot task {task_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to update HubSpot task {task_id}: {e}")
            return False
    
    def get_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve tasks from HubSpot
        
        Args:
            limit: Maximum number of tasks to retrieve
            
        Returns:
            List of HubSpot task objects
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/tasks"
            params = {
                "limit": limit,
                "properties": [
                    "hs_task_subject",
                    "hs_task_body", 
                    "hs_task_priority",
                    "hs_task_status",
                    "hs_timestamp",
                    "job_search_company",
                    "job_search_position",
                    "job_search_task_type"
                ]
            }
            
            logger.info(f"Fetching {limit} tasks from HubSpot")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            tasks = data.get("results", [])
            
            logger.info(f"✅ Retrieved {len(tasks)} tasks from HubSpot")
            return tasks
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to fetch HubSpot tasks: {e}")
            return []
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from HubSpot
        
        Args:
            task_id: HubSpot task ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/tasks/{task_id}"
            
            logger.info(f"Deleting HubSpot task {task_id}")
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"✅ Deleted HubSpot task {task_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to delete HubSpot task {task_id}: {e}")
            return False

class JobSearchTaskManager:
    """Manager for job search tasks with HubSpot synchronization"""
    
    def __init__(self):
        self.hubspot_sync = HubSpotTaskSync()
    
    def create_application_task(self, company_name: str, job_title: str, 
                              deadline: Optional[datetime] = None) -> JobSearchTask:
        """Create a job application task"""
        task = JobSearchTask(
            title=f"Apply to {job_title} at {company_name}",
            description=f"Submit application for {job_title} position at {company_name}",
            task_type=TaskType.APPLICATION,
            priority=TaskPriority.HIGH if deadline and deadline <= datetime.now() + timedelta(days=1) else TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            due_date=deadline,
            company_name=company_name,
            job_title=job_title
        )
        
        # Sync to HubSpot
        hubspot_id = self.hubspot_sync.create_task(task)
        if hubspot_id:
            task.hubspot_task_id = hubspot_id
        
        return task
    
    def create_interview_task(self, company_name: str, job_title: str, 
                            interview_date: datetime, interview_type: str = "Technical") -> JobSearchTask:
        """Create an interview preparation task"""
        task = JobSearchTask(
            title=f"Prepare for {interview_type} Interview - {company_name}",
            description=f"Prepare for {interview_type.lower()} interview for {job_title} at {company_name}",
            task_type=TaskType.INTERVIEW,
            priority=TaskPriority.HIGH,
            status=TaskStatus.NOT_STARTED,
            due_date=interview_date - timedelta(days=1),  # Prepare day before
            company_name=company_name,
            job_title=job_title
        )
        
        # Sync to HubSpot
        hubspot_id = self.hubspot_sync.create_task(task)
        if hubspot_id:
            task.hubspot_task_id = hubspot_id
        
        return task
    
    def create_follow_up_task(self, company_name: str, job_title: str, 
                            contact_email: str, follow_up_date: datetime) -> JobSearchTask:
        """Create a follow-up task"""
        task = JobSearchTask(
            title=f"Follow up on {job_title} application - {company_name}",
            description=f"Send follow-up email to {contact_email} regarding {job_title} application",
            task_type=TaskType.FOLLOW_UP,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            due_date=follow_up_date,
            company_name=company_name,
            job_title=job_title,
            contact_email=contact_email
        )
        
        # Sync to HubSpot
        hubspot_id = self.hubspot_sync.create_task(task)
        if hubspot_id:
            task.hubspot_task_id = hubspot_id
        
        return task
    
    def create_networking_task(self, contact_name: str, company_name: str, 
                             action: str, due_date: Optional[datetime] = None) -> JobSearchTask:
        """Create a networking task"""
        task = JobSearchTask(
            title=f"Network with {contact_name} at {company_name}",
            description=f"{action} with {contact_name} from {company_name}",
            task_type=TaskType.NETWORKING,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            due_date=due_date or datetime.now() + timedelta(days=7),
            company_name=company_name
        )
        
        # Sync to HubSpot
        hubspot_id = self.hubspot_sync.create_task(task)
        if hubspot_id:
            task.hubspot_task_id = hubspot_id
        
        return task
    
    def sync_from_dashboard_actions(self, action_items: List[Dict[str, Any]]) -> List[JobSearchTask]:
        """
        Convert dashboard action items to HubSpot tasks
        
        Args:
            action_items: List of action items from dashboard
            
        Returns:
            List of created JobSearchTask objects
        """
        created_tasks = []
        
        for item in action_items:
            # Parse action item and determine task type
            title = item.get("title", "")
            description = item.get("description", "")
            priority_level = item.get("priority", "medium").upper()
            
            # Determine task type from title/description
            task_type = TaskType.APPLICATION
            if "interview" in title.lower():
                task_type = TaskType.INTERVIEW
            elif "follow" in title.lower():
                task_type = TaskType.FOLLOW_UP
            elif "network" in title.lower():
                task_type = TaskType.NETWORKING
            elif "research" in title.lower():
                task_type = TaskType.RESEARCH
            
            # Create task
            task = JobSearchTask(
                title=title,
                description=description,
                task_type=task_type,
                priority=TaskPriority(priority_level) if priority_level in TaskPriority.__members__ else TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                company_name=item.get("company"),
                job_title=item.get("position")
            )
            
            # Sync to HubSpot
            hubspot_id = self.hubspot_sync.create_task(task)
            if hubspot_id:
                task.hubspot_task_id = hubspot_id
                created_tasks.append(task)
        
        return created_tasks
    
    def get_urgent_tasks(self) -> List[Dict[str, Any]]:
        """Get urgent tasks from HubSpot for dashboard display"""
        all_tasks = self.hubspot_sync.get_tasks()
        urgent_tasks = []
        
        for task in all_tasks:
            properties = task.get("properties", {})
            priority = properties.get("hs_task_priority")
            status = properties.get("hs_task_status")
            due_timestamp = properties.get("hs_timestamp")
            
            # Check if task is urgent (high priority or due soon)
            is_urgent = False
            if priority == "HIGH" or priority == "URGENT":
                is_urgent = True
            elif due_timestamp:
                due_date = datetime.fromtimestamp(int(due_timestamp) / 1000)
                if due_date <= datetime.now() + timedelta(hours=24):
                    is_urgent = True
            
            if is_urgent and status != "COMPLETED":
                urgent_tasks.append({
                    "id": task.get("id"),
                    "title": properties.get("hs_task_subject", ""),
                    "description": properties.get("hs_task_body", ""),
                    "priority": priority,
                    "status": status,
                    "company": properties.get("job_search_company", ""),
                    "position": properties.get("job_search_position", ""),
                    "task_type": properties.get("job_search_task_type", ""),
                    "due_date": due_date.isoformat() if due_timestamp else None
                })
        
        return urgent_tasks

# Example usage and testing
if __name__ == "__main__":
    # Initialize task manager
    task_manager = JobSearchTaskManager()
    
    # Create sample tasks
    print("Creating sample job search tasks...")
    
    # Application task
    app_task = task_manager.create_application_task(
        company_name="Google",
        job_title="Senior Product Manager",
        deadline=datetime.now() + timedelta(days=2)
    )
    
    # Interview task
    interview_task = task_manager.create_interview_task(
        company_name="Microsoft",
        job_title="Principal Program Manager",
        interview_date=datetime.now() + timedelta(days=5),
        interview_type="Behavioral"
    )
    
    # Follow-up task
    followup_task = task_manager.create_follow_up_task(
        company_name="Apple",
        job_title="Product Marketing Manager",
        contact_email="recruiter@apple.com",
        follow_up_date=datetime.now() + timedelta(days=3)
    )
    
    # Get urgent tasks
    print("\nFetching urgent tasks from HubSpot...")
    urgent_tasks = task_manager.get_urgent_tasks()
    
    print(f"Found {len(urgent_tasks)} urgent tasks:")
    for task in urgent_tasks:
        print(f"- {task['title']} ({task['priority']}) - Due: {task['due_date']}")
