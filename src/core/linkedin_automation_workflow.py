"""
LinkedIn Automation Workflow System
Handles automated content generation, scheduling, and posting workflows
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from enum import Enum
import schedule
import time as time_module
from pathlib import Path
import sqlite3
import requests
from abc import ABC, abstractmethod

from linkedin_content_generator import LinkedInContentGenerator, LinkedInPost, PostType

logger = logging.getLogger(__name__)


class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PostingMethod(Enum):
    MANUAL_REVIEW = "manual_review"
    AUTO_POST = "auto_post"
    BUFFER = "buffer"
    HOOTSUITE = "hootsuite"
    LINKEDIN_API = "linkedin_api"


@dataclass
class PostingSchedule:
    """Posting schedule configuration"""
    days_of_week: List[str] = field(default_factory=lambda: ['Tuesday', 'Wednesday', 'Thursday'])
    posting_times: List[time] = field(default_factory=lambda: [time(9, 0), time(14, 0)])  # 9 AM, 2 PM
    timezone: str = "America/Los_Angeles"
    posts_per_week: int = 3
    content_review_required: bool = True
    auto_post_enabled: bool = False


@dataclass
class ScheduledPost:
    """Scheduled LinkedIn post"""
    post_id: str
    post: LinkedInPost
    scheduled_time: datetime
    status: PostStatus = PostStatus.DRAFT
    posting_method: PostingMethod = PostingMethod.MANUAL_REVIEW
    review_notes: Optional[str] = None
    posted_time: Optional[datetime] = None
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    
    # Workflow tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class PostingPlatform(ABC):
    """Abstract base class for posting platforms"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        pass
    
    @abstractmethod
    def post_content(self, content: str, scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_post_metrics(self, post_id: str) -> Dict[str, int]:
        pass


class LinkedInDirectAPI(PostingPlatform):
    """LinkedIn API integration for direct posting"""
    
    def __init__(self):
        self.access_token = None
        self.person_id = None
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            # LinkedIn OAuth 2.0 flow would go here
            self.access_token = credentials.get('access_token')
            self.person_id = credentials.get('person_id')
            
            # Verify token validity
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get('https://api.linkedin.com/v2/people/~', headers=headers)
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            return False
    
    def post_content(self, content: str, scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        if not self.access_token:
            raise ValueError("Not authenticated with LinkedIn")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        post_data = {
            "author": f"urn:li:person:{self.person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'post_id': response.json().get('id'),
                    'posted_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_post_metrics(self, post_id: str) -> Dict[str, int]:
        """Get engagement metrics for a post"""
        if not self.access_token:
            return {}
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            # Get post statistics
            response = requests.get(
                f'https://api.linkedin.com/v2/socialActions/{post_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'likes': data.get('likesSummary', {}).get('totalLikes', 0),
                    'comments': data.get('commentsSummary', {}).get('totalComments', 0),
                    'shares': data.get('sharesSummary', {}).get('totalShares', 0),
                    'views': data.get('impressionCount', 0)
                }
        except Exception as e:
            logger.error(f"Failed to get post metrics: {e}")
        
        return {}


class BufferIntegration(PostingPlatform):
    """Buffer integration for scheduled posting"""
    
    def __init__(self):
        self.access_token = None
        self.profile_id = None
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Buffer API"""
        try:
            self.access_token = credentials.get('access_token')
            
            # Get LinkedIn profile ID from Buffer
            response = requests.get(
                f'https://api.bufferapp.com/1/profiles.json?access_token={self.access_token}'
            )
            
            if response.status_code == 200:
                profiles = response.json()
                linkedin_profile = next((p for p in profiles if p['service'] == 'linkedin'), None)
                if linkedin_profile:
                    self.profile_id = linkedin_profile['id']
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Buffer authentication failed: {e}")
            return False
    
    def post_content(self, content: str, scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Schedule content via Buffer"""
        if not self.access_token or not self.profile_id:
            raise ValueError("Not authenticated with Buffer")
        
        data = {
            'text': content,
            'profile_ids[]': [self.profile_id],
            'access_token': self.access_token
        }
        
        if scheduled_time:
            data['scheduled_at'] = scheduled_time.isoformat()
        else:
            data['now'] = True
        
        try:
            response = requests.post('https://api.bufferapp.com/1/updates/create.json', data=data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'post_id': result.get('updates', [{}])[0].get('id'),
                    'scheduled_at': scheduled_time.isoformat() if scheduled_time else None
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Failed to schedule via Buffer: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_post_metrics(self, post_id: str) -> Dict[str, int]:
        """Get post metrics from Buffer"""
        if not self.access_token:
            return {}
        
        try:
            response = requests.get(
                f'https://api.bufferapp.com/1/updates/{post_id}.json?access_token={self.access_token}'
            )
            
            if response.status_code == 200:
                data = response.json()
                statistics = data.get('statistics', {})
                return {
                    'likes': statistics.get('likes', 0),
                    'comments': statistics.get('comments', 0),
                    'shares': statistics.get('shares', 0),
                    'clicks': statistics.get('clicks', 0)
                }
        except Exception as e:
            logger.error(f"Failed to get Buffer metrics: {e}")
        
        return {}


class LinkedInAutomationWorkflow:
    """Main workflow orchestrator for LinkedIn automation"""
    
    def __init__(self, db_path: str = "linkedin_automation.db"):
        self.db_path = db_path
        self.content_generator = LinkedInContentGenerator()
        self.posting_platforms = {
            PostingMethod.LINKEDIN_API: LinkedInDirectAPI(),
            PostingMethod.BUFFER: BufferIntegration()
        }
        self.schedule_config = PostingSchedule()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for workflow tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                post_id TEXT PRIMARY KEY,
                post_data TEXT,
                scheduled_time TEXT,
                status TEXT,
                posting_method TEXT,
                created_at TEXT,
                posted_at TEXT,
                engagement_metrics TEXT,
                review_notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posting_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                action TEXT,
                timestamp TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def configure_schedule(self, schedule_config: PostingSchedule):
        """Configure posting schedule"""
        self.schedule_config = schedule_config
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO workflow_config (key, value) VALUES (?, ?)',
            ('schedule_config', json.dumps(schedule_config.__dict__, default=str))
        )
        conn.commit()
        conn.close()
    
    def generate_content_pipeline(self, job_data: List[Dict[str, Any]], 
                                 days_ahead: int = 7) -> List[ScheduledPost]:
        """Generate content pipeline for upcoming days"""
        
        # Generate posts for the specified period
        posts = self.content_generator.generate_content_calendar(job_data, days=days_ahead)
        
        # Create posting schedule
        scheduled_posts = []
        current_date = datetime.now()
        
        for i, post in enumerate(posts):
            # Calculate next posting slot
            posting_date = self._get_next_posting_slot(current_date, i)
            
            scheduled_post = ScheduledPost(
                post_id=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                post=post,
                scheduled_time=posting_date,
                posting_method=PostingMethod.MANUAL_REVIEW if self.schedule_config.content_review_required else PostingMethod.AUTO_POST
            )
            
            scheduled_posts.append(scheduled_post)
            self._save_scheduled_post(scheduled_post)
        
        return scheduled_posts
    
    def _get_next_posting_slot(self, start_date: datetime, offset: int) -> datetime:
        """Calculate next available posting slot"""
        target_days = self.schedule_config.days_of_week
        posting_times = self.schedule_config.posting_times
        
        current_date = start_date
        slots_found = 0
        
        while slots_found <= offset:
            day_name = current_date.strftime('%A')
            
            if day_name in target_days:
                for posting_time in posting_times:
                    posting_datetime = datetime.combine(current_date.date(), posting_time)
                    
                    if posting_datetime > datetime.now():
                        if slots_found == offset:
                            return posting_datetime
                        slots_found += 1
            
            current_date += timedelta(days=1)
        
        return current_date
    
    def _save_scheduled_post(self, scheduled_post: ScheduledPost):
        """Save scheduled post to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO scheduled_posts 
            (post_id, post_data, scheduled_time, status, posting_method, created_at, review_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            scheduled_post.post_id,
            json.dumps(scheduled_post.post.__dict__, default=str),
            scheduled_post.scheduled_time.isoformat(),
            scheduled_post.status.value,
            scheduled_post.posting_method.value,
            scheduled_post.created_at.isoformat(),
            scheduled_post.review_notes
        ))
        
        conn.commit()
        conn.close()
        
        # Log workflow action
        self._log_workflow_action(scheduled_post.post_id, "scheduled", f"Post scheduled for {scheduled_post.scheduled_time}")
    
    def review_pending_posts(self) -> List[ScheduledPost]:
        """Get posts pending review"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scheduled_posts 
            WHERE status = ? AND posting_method = ?
            ORDER BY scheduled_time
        ''', (PostStatus.DRAFT.value, PostingMethod.MANUAL_REVIEW.value))
        
        posts = []
        for row in cursor.fetchall():
            post_data = json.loads(row[1])
            post = LinkedInPost(**post_data)
            
            scheduled_post = ScheduledPost(
                post_id=row[0],
                post=post,
                scheduled_time=datetime.fromisoformat(row[2]),
                status=PostStatus(row[3]),
                posting_method=PostingMethod(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                review_notes=row[8]
            )
            posts.append(scheduled_post)
        
        conn.close()
        return posts
    
    def approve_post(self, post_id: str, approved_by: str, notes: Optional[str] = None) -> bool:
        """Approve a post for publishing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_posts 
            SET status = ?, review_notes = ?
            WHERE post_id = ?
        ''', (PostStatus.SCHEDULED.value, notes, post_id))
        
        conn.commit()
        conn.close()
        
        self._log_workflow_action(post_id, "approved", f"Approved by {approved_by}: {notes}")
        return True
    
    def execute_posting_workflow(self, platform: PostingMethod, credentials: Dict[str, str]):
        """Execute the posting workflow for scheduled posts"""
        
        # Authenticate with platform
        posting_platform = self.posting_platforms.get(platform)
        if not posting_platform or not posting_platform.authenticate(credentials):
            logger.error(f"Failed to authenticate with {platform.value}")
            return
        
        # Get posts ready for posting
        ready_posts = self._get_posts_ready_for_posting()
        
        for scheduled_post in ready_posts:
            try:
                # Format post content
                formatted_content = self.content_generator.format_linkedin_post(scheduled_post.post)
                
                # Post content
                result = posting_platform.post_content(
                    formatted_content,
                    scheduled_post.scheduled_time if platform != PostingMethod.LINKEDIN_API else None
                )
                
                if result.get('success'):
                    # Update post status
                    self._update_post_status(
                        scheduled_post.post_id,
                        PostStatus.POSTED,
                        result.get('post_id'),
                        datetime.now()
                    )
                    
                    self._log_workflow_action(
                        scheduled_post.post_id,
                        "posted",
                        f"Successfully posted via {platform.value}"
                    )
                    
                    logger.info(f"Successfully posted {scheduled_post.post_id}")
                else:
                    # Mark as failed
                    self._update_post_status(scheduled_post.post_id, PostStatus.FAILED)
                    self._log_workflow_action(
                        scheduled_post.post_id,
                        "failed",
                        f"Posting failed: {result.get('error')}"
                    )
                    
                    logger.error(f"Failed to post {scheduled_post.post_id}: {result.get('error')}")
                
            except Exception as e:
                logger.error(f"Error posting {scheduled_post.post_id}: {e}")
                self._update_post_status(scheduled_post.post_id, PostStatus.FAILED)
    
    def _get_posts_ready_for_posting(self) -> List[ScheduledPost]:
        """Get posts that are ready for posting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            SELECT * FROM scheduled_posts 
            WHERE status = ? AND scheduled_time <= ?
            ORDER BY scheduled_time
        ''', (PostStatus.SCHEDULED.value, now.isoformat()))
        
        posts = []
        for row in cursor.fetchall():
            post_data = json.loads(row[1])
            post = LinkedInPost(**post_data)
            
            scheduled_post = ScheduledPost(
                post_id=row[0],
                post=post,
                scheduled_time=datetime.fromisoformat(row[2]),
                status=PostStatus(row[3]),
                posting_method=PostingMethod(row[4])
            )
            posts.append(scheduled_post)
        
        conn.close()
        return posts
    
    def _update_post_status(self, post_id: str, status: PostStatus, 
                           platform_post_id: Optional[str] = None,
                           posted_time: Optional[datetime] = None):
        """Update post status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = ['status = ?']
        values = [status.value]
        
        if posted_time:
            update_fields.append('posted_at = ?')
            values.append(posted_time.isoformat())
        
        values.append(post_id)
        
        cursor.execute(f'''
            UPDATE scheduled_posts 
            SET {', '.join(update_fields)}
            WHERE post_id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def _log_workflow_action(self, post_id: str, action: str, details: str):
        """Log workflow action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO posting_history (post_id, action, timestamp, details)
            VALUES (?, ?, ?, ?)
        ''', (post_id, action, datetime.now().isoformat(), details))
        
        conn.commit()
        conn.close()
    
    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get workflow performance analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get post status distribution
        cursor.execute('SELECT status, COUNT(*) FROM scheduled_posts GROUP BY status')
        status_counts = dict(cursor.fetchall())
        
        # Get posting performance
        cursor.execute('''
            SELECT posting_method, COUNT(*) 
            FROM scheduled_posts 
            WHERE status = ?
            GROUP BY posting_method
        ''', (PostStatus.POSTED.value,))
        posting_performance = dict(cursor.fetchall())
        
        # Get recent activity
        cursor.execute('''
            SELECT action, COUNT(*) 
            FROM posting_history 
            WHERE timestamp >= ?
            GROUP BY action
        ''', ((datetime.now() - timedelta(days=30)).isoformat(),))
        recent_activity = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'status_distribution': status_counts,
            'posting_performance': posting_performance,
            'recent_activity': recent_activity,
            'total_posts_scheduled': sum(status_counts.values()),
            'success_rate': (status_counts.get(PostStatus.POSTED.value, 0) / 
                           max(sum(status_counts.values()), 1)) * 100
        }
    
    def setup_automated_scheduler(self):
        """Setup automated scheduler using the schedule library"""
        
        # Clear existing scheduled jobs
        schedule.clear()
        
        # Schedule content generation (weekly)
        schedule.every().monday.at("08:00").do(self._automated_content_generation)
        
        # Schedule posting checks (multiple times daily)
        for posting_time in self.schedule_config.posting_times:
            schedule.every().day.at(posting_time.strftime("%H:%M")).do(self._automated_posting_check)
        
        # Schedule metrics collection (daily)
        schedule.every().day.at("18:00").do(self._collect_engagement_metrics)
        
        logger.info("Automated scheduler configured")
    
    def _automated_content_generation(self):
        """Automated content generation job"""
        try:
            # This would integrate with your job data source
            job_data = []  # Load from your database
            self.generate_content_pipeline(job_data, days_ahead=7)
            logger.info("Automated content generation completed")
        except Exception as e:
            logger.error(f"Automated content generation failed: {e}")
    
    def _automated_posting_check(self):
        """Check for posts ready to be posted"""
        try:
            if not self.schedule_config.auto_post_enabled:
                return
            
            # This would use your configured credentials
            credentials = {}  # Load from secure storage
            self.execute_posting_workflow(PostingMethod.BUFFER, credentials)
            logger.info("Automated posting check completed")
        except Exception as e:
            logger.error(f"Automated posting check failed: {e}")
    
    def _collect_engagement_metrics(self):
        """Collect engagement metrics for posted content"""
        try:
            # Get recently posted content and collect metrics
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT post_id FROM scheduled_posts 
                WHERE status = ? AND posted_at >= ?
            ''', (PostStatus.POSTED.value, (datetime.now() - timedelta(days=7)).isoformat()))
            
            recent_posts = cursor.fetchall()
            conn.close()
            
            # Collect metrics for each post
            for (post_id,) in recent_posts:
                # This would use your platform integrations
                pass
            
            logger.info("Engagement metrics collection completed")
        except Exception as e:
            logger.error(f"Engagement metrics collection failed: {e}")
    
    def run_scheduler(self):
        """Run the automated scheduler"""
        logger.info("Starting LinkedIn automation scheduler...")
        
        while True:
            schedule.run_pending()
            time_module.sleep(60)  # Check every minute


# Utility functions for workflow management

def create_workflow_dashboard_data(workflow: LinkedInAutomationWorkflow) -> Dict[str, Any]:
    """Create dashboard data for workflow monitoring"""
    
    analytics = workflow.get_workflow_analytics()
    pending_posts = workflow.review_pending_posts()
    
    return {
        'workflow_status': {
            'total_scheduled': analytics['total_posts_scheduled'],
            'success_rate': f"{analytics['success_rate']:.1f}%",
            'pending_review': len(pending_posts),
            'auto_posting_enabled': workflow.schedule_config.auto_post_enabled
        },
        'upcoming_posts': [
            {
                'post_id': post.post_id,
                'title': post.post.title,
                'scheduled_time': post.scheduled_time.strftime('%Y-%m-%d %H:%M'),
                'status': post.status.value,
                'post_type': post.post.post_type.value
            }
            for post in pending_posts[:5]
        ],
        'performance_metrics': analytics,
        'schedule_config': {
            'posting_days': workflow.schedule_config.days_of_week,
            'posting_times': [t.strftime('%H:%M') for t in workflow.schedule_config.posting_times],
            'posts_per_week': workflow.schedule_config.posts_per_week,
            'review_required': workflow.schedule_config.content_review_required
        }
    }
