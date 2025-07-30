"""
Resume Database Service

Handles all database operations for resumes, resume versions, and optimization results.
Integrates with the resume optimizer to store tailored resumes for different jobs.
"""

import os
import json
import requests
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from dotenv import load_dotenv
import logging

from ...core.resume_optimizer import ResumeProfile, OptimizationResult, ResumeOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ResumeDatabaseService:
    """
    Service for managing resume data and optimization results in Supabase database.
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing required Supabase environment variables")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        self.service_headers = {
            "apikey": self.service_role_key or self.supabase_key,
            "Authorization": f"Bearer {self.service_role_key or self.supabase_key}",
            "Content-Type": "application/json"
        }
    
    def create_base_resume(self, resume_profile: ResumeProfile, user_id: Optional[str] = None) -> str:
        """
        Create a base resume profile in the database.
        
        Args:
            resume_profile: ResumeProfile object
            user_id: Optional user ID for multi-user support
            
        Returns:
            Resume ID (string)
        """
        try:
            resume_data = {
                "user_id": user_id,
                "name": resume_profile.personal_info.get("name", "Default Resume"),
                "personal_info": json.dumps(resume_profile.personal_info),
                "summary": resume_profile.summary,
                "experience": json.dumps(resume_profile.experience),
                "education": json.dumps(resume_profile.education),
                "skills": json.dumps(resume_profile.skills),
                "certifications": json.dumps(resume_profile.certifications),
                "projects": json.dumps(resume_profile.projects),
                "achievements": json.dumps(resume_profile.achievements),
                "is_base_resume": True,
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                json=resume_data
            )
            response.raise_for_status()
            
            # Get the inserted resume ID
            response = requests.get(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={
                    "select": "id",
                    "order": "created_at.desc",
                    "limit": 1
                }
            )
            response.raise_for_status()
            resume_id = response.json()[0]["id"]
            
            logger.info(f"Created base resume: {resume_profile.personal_info.get('name', 'Unknown')} (ID: {resume_id})")
            return resume_id
            
        except requests.RequestException as e:
            logger.error(f"Database error creating base resume: {e}")
            raise Exception(f"Failed to create base resume: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating base resume: {e}")
            raise
    
    def create_optimized_resume(self, 
                              base_resume_id: str,
                              job_id: str,
                              optimization_result: OptimizationResult) -> str:
        """
        Store an optimized resume version for a specific job.
        
        Args:
            base_resume_id: ID of the base resume
            job_id: ID of the target job
            optimization_result: OptimizationResult from optimizer
            
        Returns:
            Optimized resume ID (string)
        """
        try:
            optimized_resume = optimization_result.optimized_resume
            
            resume_data = {
                "base_resume_id": base_resume_id,
                "job_id": job_id,
                "name": f"Optimized for {job_id}",
                "personal_info": json.dumps(optimized_resume.personal_info),
                "summary": optimized_resume.summary,
                "experience": json.dumps(optimized_resume.experience),
                "education": json.dumps(optimized_resume.education),
                "skills": json.dumps(optimized_resume.skills),
                "certifications": json.dumps(optimized_resume.certifications),
                "projects": json.dumps(optimized_resume.projects),
                "achievements": json.dumps(optimized_resume.achievements),
                "is_base_resume": False,
                "compatibility_score": optimization_result.compatibility_score,
                "optimization_rationale": optimization_result.optimization_rationale,
                "keyword_matches": json.dumps(optimization_result.keyword_matches),
                "missing_keywords": json.dumps(optimization_result.missing_keywords),
                "suggested_improvements": json.dumps(optimization_result.suggested_improvements),
                "tailored_sections": json.dumps(optimization_result.tailored_sections),
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                json=resume_data
            )
            response.raise_for_status()
            
            # Get the inserted resume ID
            response = requests.get(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={
                    "select": "id",
                    "order": "created_at.desc",
                    "limit": 1
                }
            )
            response.raise_for_status()
            resume_id = response.json()[0]["id"]
            
            logger.info(f"Created optimized resume for job {job_id} (ID: {resume_id}, Score: {optimization_result.compatibility_score:.1f}%)")
            return resume_id
            
        except requests.RequestException as e:
            logger.error(f"Database error creating optimized resume: {e}")
            raise Exception(f"Failed to create optimized resume: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating optimized resume: {e}")
            raise
    
    def optimize_resume_for_job(self, 
                               base_resume_id: str, 
                               job_id: str,
                               optimization_level: str = "moderate") -> Dict[str, Any]:
        """
        Complete workflow: optimize base resume for specific job and store result.
        
        Args:
            base_resume_id: ID of base resume to optimize
            job_id: ID of target job
            optimization_level: "conservative", "moderate", or "aggressive"
            
        Returns:
            Dictionary with optimization result and database IDs
        """
        try:
            logger.info(f"Optimizing resume {base_resume_id} for job {job_id}")
            
            # Get base resume
            base_resume = self.get_resume_by_id(base_resume_id)
            if not base_resume:
                raise Exception(f"Base resume {base_resume_id} not found")
            
            # Get job details
            from .job_service import JobDatabaseService
            job_service = JobDatabaseService()
            job_details = job_service.get_job_by_id(job_id)
            if not job_details:
                raise Exception(f"Job {job_id} not found")
            
            # Convert database resume to ResumeProfile
            resume_profile = self._db_to_resume_profile(base_resume)
            
            # Optimize resume
            optimizer = ResumeOptimizer()
            optimization_result = optimizer.optimize_resume(
                resume_profile, 
                job_details, 
                optimization_level
            )
            
            # Store optimized resume
            optimized_resume_id = self.create_optimized_resume(
                base_resume_id, 
                job_id, 
                optimization_result
            )
            
            return {
                "status": "success",
                "base_resume_id": base_resume_id,
                "optimized_resume_id": optimized_resume_id,
                "job_id": job_id,
                "compatibility_score": optimization_result.compatibility_score,
                "optimization_level": optimization_level,
                "keyword_matches": len(optimization_result.keyword_matches),
                "missing_keywords": len(optimization_result.missing_keywords),
                "suggestions_count": len(optimization_result.suggested_improvements),
                "rationale": optimization_result.optimization_rationale
            }
            
        except Exception as e:
            logger.error(f"Resume optimization workflow failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "base_resume_id": base_resume_id,
                "job_id": job_id
            }
    
    def get_resume_by_id(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve resume by ID with related job information.
        
        Args:
            resume_id: Resume ID to retrieve
            
        Returns:
            Resume data or None if not found
        """
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={
                    "id": f"eq.{resume_id}",
                    "select": "*,jobs(*)"
                }
            )
            response.raise_for_status()
            results = response.json()
            
            if results:
                resume_data = results[0]
                
                # Parse JSON fields back to objects
                json_fields = [
                    "personal_info", "experience", "education", "skills",
                    "certifications", "projects", "achievements", "keyword_matches",
                    "missing_keywords", "suggested_improvements", "tailored_sections"
                ]
                
                for field in json_fields:
                    if resume_data.get(field):
                        try:
                            resume_data[field] = json.loads(resume_data[field])
                        except (json.JSONDecodeError, TypeError):
                            resume_data[field] = None
                
                return resume_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve resume {resume_id}: {e}")
            return None
    
    def get_resumes_for_user(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all resumes for a user.
        
        Args:
            user_id: User ID (optional for single-user systems)
            
        Returns:
            List of resume records
        """
        try:
            params = {
                "select": "id,name,is_base_resume,compatibility_score,created_at,updated_at",
                "order": "created_at.desc"
            }
            
            if user_id:
                params["user_id"] = f"eq.{user_id}"
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get resumes for user {user_id}: {e}")
            return []
    
    def get_optimized_resumes_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get all optimized resume versions for a specific job.
        
        Args:
            job_id: Job ID
            
        Returns:
            List of optimized resume records
        """
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={
                    "job_id": f"eq.{job_id}",
                    "is_base_resume": "eq.false",
                    "select": "id,name,compatibility_score,optimization_rationale,created_at",
                    "order": "compatibility_score.desc"
                }
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get optimized resumes for job {job_id}: {e}")
            return []
    
    def get_resume_analytics(self, base_resume_id: str) -> Dict[str, Any]:
        """
        Get analytics for a base resume across all optimizations.
        
        Args:
            base_resume_id: Base resume ID
            
        Returns:
            Analytics data
        """
        try:
            # Get all optimized versions
            response = requests.get(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={
                    "base_resume_id": f"eq.{base_resume_id}",
                    "is_base_resume": "eq.false",
                    "select": "compatibility_score,created_at,job_id"
                }
            )
            response.raise_for_status()
            optimized_resumes = response.json()
            
            if not optimized_resumes:
                return {
                    "total_optimizations": 0,
                    "average_score": 0,
                    "best_score": 0,
                    "optimization_trend": []
                }
            
            scores = [r["compatibility_score"] for r in optimized_resumes if r["compatibility_score"]]
            
            analytics = {
                "total_optimizations": len(optimized_resumes),
                "average_score": sum(scores) / len(scores) if scores else 0,
                "best_score": max(scores) if scores else 0,
                "worst_score": min(scores) if scores else 0,
                "score_distribution": self._calculate_score_distribution(scores),
                "optimization_trend": sorted(
                    [(r["created_at"], r["compatibility_score"]) for r in optimized_resumes],
                    key=lambda x: x[0]
                )
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get resume analytics: {e}")
            return {}
    
    def update_resume(self, resume_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update resume data.
        
        Args:
            resume_id: Resume ID to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add updated timestamp
            updates["updated_at"] = datetime.datetime.now().isoformat()
            
            # Convert objects to JSON strings for storage
            json_fields = [
                "personal_info", "experience", "education", "skills",
                "certifications", "projects", "achievements"
            ]
            
            for field in json_fields:
                if field in updates and updates[field] is not None:
                    updates[field] = json.dumps(updates[field])
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={"id": f"eq.{resume_id}"},
                json=updates
            )
            response.raise_for_status()
            
            logger.info(f"Updated resume {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update resume {resume_id}: {e}")
            return False
    
    def delete_resume(self, resume_id: str) -> bool:
        """
        Delete resume (soft delete by updating status).
        
        Args:
            resume_id: Resume ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/resumes",
                headers=self.headers,
                params={"id": f"eq.{resume_id}"},
                json={
                    "status": "deleted",
                    "updated_at": datetime.datetime.now().isoformat()
                }
            )
            response.raise_for_status()
            
            logger.info(f"Deleted resume {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete resume {resume_id}: {e}")
            return False
    
    def export_resume_to_format(self, resume_id: str, format_type: str = "json") -> Dict[str, Any]:
        """
        Export resume in various formats.
        
        Args:
            resume_id: Resume ID to export
            format_type: "json", "markdown", or "text"
            
        Returns:
            Exported resume data
        """
        try:
            resume_data = self.get_resume_by_id(resume_id)
            if not resume_data:
                raise Exception(f"Resume {resume_id} not found")
            
            if format_type == "json":
                return resume_data
            elif format_type == "markdown":
                return self._convert_to_markdown(resume_data)
            elif format_type == "text":
                return self._convert_to_text(resume_data)
            else:
                raise Exception(f"Unsupported format: {format_type}")
                
        except Exception as e:
            logger.error(f"Failed to export resume {resume_id}: {e}")
            return {"error": str(e)}
    
    # Helper methods
    def _db_to_resume_profile(self, db_resume: Dict[str, Any]) -> ResumeProfile:
        """Convert database resume to ResumeProfile object."""
        return ResumeProfile(
            personal_info=db_resume.get("personal_info", {}),
            summary=db_resume.get("summary", ""),
            experience=db_resume.get("experience", []),
            education=db_resume.get("education", []),
            skills=db_resume.get("skills", []),
            certifications=db_resume.get("certifications", []),
            projects=db_resume.get("projects", []),
            achievements=db_resume.get("achievements", [])
        )
    
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution for analytics."""
        if not scores:
            return {}
        
        distribution = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "below-60": 0
        }
        
        for score in scores:
            if score >= 90:
                distribution["90-100"] += 1
            elif score >= 80:
                distribution["80-89"] += 1
            elif score >= 70:
                distribution["70-79"] += 1
            elif score >= 60:
                distribution["60-69"] += 1
            else:
                distribution["below-60"] += 1
        
        return distribution
    
    def _convert_to_markdown(self, resume_data: Dict[str, Any]) -> Dict[str, str]:
        """Convert resume to markdown format."""
        personal_info = resume_data.get("personal_info", {})
        
        markdown = f"""# {personal_info.get('name', 'Resume')}

**Email:** {personal_info.get('email', '')}  
**Phone:** {personal_info.get('phone', '')}  
**Location:** {personal_info.get('location', '')}

## Summary
{resume_data.get('summary', '')}

## Experience
"""
        
        for exp in resume_data.get("experience", []):
            markdown += f"""
### {exp.get('title', '')} - {exp.get('company', '')}
*{exp.get('duration', '')}*

{exp.get('description', '')}

"""
            if exp.get('achievements'):
                markdown += "**Achievements:**\n"
                for achievement in exp['achievements']:
                    markdown += f"- {achievement}\n"
                markdown += "\n"
        
        markdown += "## Education\n"
        for edu in resume_data.get("education", []):
            markdown += f"- **{edu.get('degree', '')}** - {edu.get('institution', '')} ({edu.get('year', '')})\n"
        
        markdown += f"\n## Skills\n{', '.join(resume_data.get('skills', []))}\n"
        
        if resume_data.get('certifications'):
            markdown += f"\n## Certifications\n{', '.join(resume_data.get('certifications', []))}\n"
        
        return {"content": markdown, "format": "markdown"}
    
    def _convert_to_text(self, resume_data: Dict[str, Any]) -> Dict[str, str]:
        """Convert resume to plain text format."""
        personal_info = resume_data.get("personal_info", {})
        
        text = f"""{personal_info.get('name', 'Resume')}
Email: {personal_info.get('email', '')}
Phone: {personal_info.get('phone', '')}
Location: {personal_info.get('location', '')}

SUMMARY
{resume_data.get('summary', '')}

EXPERIENCE
"""
        
        for exp in resume_data.get("experience", []):
            text += f"""
{exp.get('title', '')} - {exp.get('company', '')}
{exp.get('duration', '')}

{exp.get('description', '')}
"""
            if exp.get('achievements'):
                text += "\nAchievements:\n"
                for achievement in exp['achievements']:
                    text += f"• {achievement}\n"
        
        text += "\nEDUCATION\n"
        for edu in resume_data.get("education", []):
            text += f"{edu.get('degree', '')} - {edu.get('institution', '')} ({edu.get('year', '')})\n"
        
        text += f"\nSKILLS\n{', '.join(resume_data.get('skills', []))}\n"
        
        if resume_data.get('certifications'):
            text += f"\nCERTIFICATIONS\n{', '.join(resume_data.get('certifications', []))}\n"
        
        return {"content": text, "format": "text"}

# Example usage and testing
if __name__ == "__main__":
    from ...core.resume_optimizer import ResumeProfile
    
    # Sample resume for testing
    sample_resume = ResumeProfile(
        personal_info={
            "name": "Jane Developer",
            "email": "jane@example.com",
            "phone": "555-0123",
            "location": "San Francisco, CA"
        },
        summary="Experienced software developer with expertise in full-stack development.",
        experience=[
            {
                "title": "Senior Developer",
                "company": "Tech Company",
                "duration": "2020 - Present",
                "description": "Lead development of web applications",
                "achievements": ["Increased performance by 40%", "Mentored 5 junior developers"]
            }
        ],
        education=[
            {
                "degree": "Master of Science in Computer Science",
                "institution": "Stanford University",
                "year": "2020"
            }
        ],
        skills=["Python", "JavaScript", "React", "Django", "PostgreSQL"],
        certifications=["AWS Solutions Architect"],
        projects=[
            {
                "name": "Task Management App",
                "description": "Full-stack application for team collaboration",
                "technologies": ["React", "Node.js", "MongoDB"]
            }
        ],
        achievements=["Employee of the Year 2023", "Published 3 technical articles"]
    )
    
    try:
        service = ResumeDatabaseService()
        
        # Create base resume
        resume_id = service.create_base_resume(sample_resume)
        print(f"✅ Created base resume: {resume_id}")
        
        # Get resume analytics
        analytics = service.get_resume_analytics(resume_id)
        print(f"📊 Analytics: {analytics}")
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
