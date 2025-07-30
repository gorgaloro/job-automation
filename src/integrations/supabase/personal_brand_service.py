"""
Personal Brand Database Service

Manages personal brand profiles, interview sessions, and profile evolution in Supabase.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from supabase import create_client, Client
from src.integrations.supabase.supabase_client import get_supabase_client
from ...core.personal_brand import PersonalBrandProfile, InterviewSession, ProfileEvolution
from ...core.ai_career_coach import AICareerCoach

logger = logging.getLogger(__name__)

class PersonalBrandDatabaseService:
    """Database service for personal brand management"""
    
    def __init__(self):
        """Initialize the database service"""
        self.supabase = get_supabase_client()
        if not self.supabase:
            logger.warning("Supabase client not available - running in demo mode")
    
    def create_personal_brand_profile(self, profile: PersonalBrandProfile) -> str:
        """Create a new personal brand profile in the database"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would create personal brand profile")
                return str(uuid.uuid4())
            
            # Convert profile to database format
            profile_data = {
                "user_id": profile.user_id,
                "brand_summary": profile.brand_summary,
                "professional_identity": profile.professional_identity,
                "unique_value_proposition": profile.unique_value_proposition,
                "work_preferences": json.dumps(profile.work_preferences.__dict__),
                "career_motivators": json.dumps(profile.career_motivators.__dict__),
                "industry_preferences": json.dumps(profile.industry_preferences.__dict__),
                "role_preferences": json.dumps(profile.role_preferences.__dict__),
                "career_highlights": json.dumps(profile.career_highlights),
                "skills_expertise": json.dumps(profile.skills_expertise),
                "education_background": json.dumps(profile.education_background),
                "profile_version": profile.profile_version,
                "confidence_score": profile.confidence_score,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
            
            result = self.supabase.table("personal_brand_profiles").insert(profile_data).execute()
            
            if result.data:
                profile_id = result.data[0]["id"]
                logger.info(f"Created personal brand profile with ID: {profile_id}")
                return str(profile_id)
            else:
                raise Exception("Failed to create personal brand profile")
                
        except Exception as e:
            logger.error(f"Error creating personal brand profile: {e}")
            raise Exception(f"Database error: {str(e)}")
    
    def get_personal_brand_profile(self, profile_id: str) -> Optional[PersonalBrandProfile]:
        """Get a personal brand profile by ID"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would retrieve personal brand profile")
                from ...core.personal_brand import create_sample_profile
                return create_sample_profile()
            
            result = self.supabase.table("personal_brand_profiles").select("*").eq("id", profile_id).execute()
            
            if result.data:
                return self._convert_db_to_profile(result.data[0])
            else:
                logger.warning(f"Personal brand profile not found: {profile_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving personal brand profile: {e}")
            return None
    
    def get_profiles_for_user(self, user_id: str) -> List[PersonalBrandProfile]:
        """Get all personal brand profiles for a user"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would retrieve user profiles")
                from ...core.personal_brand import create_sample_profile
                return [create_sample_profile()]
            
            result = self.supabase.table("personal_brand_profiles").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            profiles = []
            for row in result.data:
                profile = self._convert_db_to_profile(row)
                if profile:
                    profiles.append(profile)
            
            logger.info(f"Retrieved {len(profiles)} profiles for user {user_id}")
            return profiles
            
        except Exception as e:
            logger.error(f"Error retrieving user profiles: {e}")
            return []
    
    def get_latest_profile_for_user(self, user_id: str) -> Optional[PersonalBrandProfile]:
        """Get the most recent personal brand profile for a user"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would retrieve latest profile")
                from ...core.personal_brand import create_sample_profile
                return create_sample_profile()
            
            result = self.supabase.table("personal_brand_profiles").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
            
            if result.data:
                return self._convert_db_to_profile(result.data[0])
            else:
                logger.info(f"No profiles found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving latest profile: {e}")
            return None
    
    def update_personal_brand_profile(self, profile_id: str, updates: Dict[str, Any]) -> bool:
        """Update a personal brand profile"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would update personal brand profile")
                return True
            
            # Add updated timestamp
            updates["updated_at"] = datetime.now().isoformat()
            
            # Convert complex objects to JSON if needed
            for key, value in updates.items():
                if key in ["work_preferences", "career_motivators", "industry_preferences", "role_preferences"]:
                    if isinstance(value, dict):
                        updates[key] = json.dumps(value)
                elif key in ["career_highlights", "skills_expertise", "education_background"]:
                    if isinstance(value, list):
                        updates[key] = json.dumps(value)
            
            result = self.supabase.table("personal_brand_profiles").update(updates).eq("id", profile_id).execute()
            
            if result.data:
                logger.info(f"Updated personal brand profile: {profile_id}")
                return True
            else:
                logger.warning(f"Failed to update personal brand profile: {profile_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating personal brand profile: {e}")
            return False
    
    def delete_personal_brand_profile(self, profile_id: str) -> bool:
        """Delete a personal brand profile (soft delete)"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would delete personal brand profile")
                return True
            
            updates = {
                "deleted_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("personal_brand_profiles").update(updates).eq("id", profile_id).execute()
            
            if result.data:
                logger.info(f"Deleted personal brand profile: {profile_id}")
                return True
            else:
                logger.warning(f"Failed to delete personal brand profile: {profile_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting personal brand profile: {e}")
            return False
    
    def create_interview_session(self, session: InterviewSession) -> str:
        """Create a new interview session in the database"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would create interview session")
                return session.session_id
            
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "transcript": session.transcript,
                "audio_file_path": session.audio_file_path,
                "session_duration": session.session_duration,
                "questions_asked": json.dumps(session.questions_asked),
                "key_insights": json.dumps(session.key_insights),
                "generated_profile_id": None,  # Will be updated when profile is generated
                "session_quality_score": session.session_quality_score,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
            
            result = self.supabase.table("interview_sessions").insert(session_data).execute()
            
            if result.data:
                logger.info(f"Created interview session: {session.session_id}")
                return session.session_id
            else:
                raise Exception("Failed to create interview session")
                
        except Exception as e:
            logger.error(f"Error creating interview session: {e}")
            raise Exception(f"Database error: {str(e)}")
    
    def update_interview_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update an interview session"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would update interview session")
                return True
            
            # Convert lists to JSON if needed
            for key, value in updates.items():
                if key in ["questions_asked", "key_insights"] and isinstance(value, list):
                    updates[key] = json.dumps(value)
                elif key in ["completed_at"] and isinstance(value, datetime):
                    updates[key] = value.isoformat()
            
            result = self.supabase.table("interview_sessions").update(updates).eq("session_id", session_id).execute()
            
            if result.data:
                logger.info(f"Updated interview session: {session_id}")
                return True
            else:
                logger.warning(f"Failed to update interview session: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating interview session: {e}")
            return False
    
    def get_interview_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get an interview session by ID"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would retrieve interview session")
                from ...core.ai_career_coach import create_sample_interview_session
                return create_sample_interview_session()
            
            result = self.supabase.table("interview_sessions").select("*").eq("session_id", session_id).execute()
            
            if result.data:
                return self._convert_db_to_session(result.data[0])
            else:
                logger.warning(f"Interview session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving interview session: {e}")
            return None
    
    def get_sessions_for_user(self, user_id: str) -> List[InterviewSession]:
        """Get all interview sessions for a user"""
        try:
            if not self.supabase:
                logger.info("Demo mode: Would retrieve user sessions")
                from ...core.ai_career_coach import create_sample_interview_session
                return [create_sample_interview_session()]
            
            result = self.supabase.table("interview_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            sessions = []
            for row in result.data:
                session = self._convert_db_to_session(row)
                if session:
                    sessions.append(session)
            
            logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving user sessions: {e}")
            return []
    
    def conduct_ai_interview(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Conduct a complete AI interview session and generate profile"""
        try:
            # Initialize AI coach
            coach = AICareerCoach()
            
            # Start interview session
            session = coach.start_interview_session(user_id)
            
            # Create session in database
            self.create_interview_session(session)
            
            # Get opening question
            opening_question = coach.get_opening_question()
            
            return {
                "status": "started",
                "session_id": session.session_id,
                "opening_question": opening_question,
                "message": "Interview session started. Please respond to begin the conversation."
            }
            
        except Exception as e:
            logger.error(f"Error starting AI interview: {e}")
            return {
                "status": "error",
                "message": f"Failed to start interview: {str(e)}"
            }
    
    def process_interview_response(self, session_id: str, user_response: str) -> Dict[str, Any]:
        """Process user response in an ongoing interview"""
        try:
            # Get session from database
            session = self.get_interview_session(session_id)
            if not session:
                return {
                    "status": "error",
                    "message": "Interview session not found"
                }
            
            # Initialize coach and restore conversation state
            coach = AICareerCoach()
            # Note: In a full implementation, you'd restore the conversation history from the session
            
            # Process response
            next_question, is_complete = coach.process_user_response(user_response, session)
            
            # Update session in database
            updates = {
                "transcript": session.transcript,
                "questions_asked": session.questions_asked,
                "session_duration": session.session_duration
            }
            
            if is_complete:
                updates["completed_at"] = datetime.now()
                
                # Generate profile
                profile = coach.generate_personal_brand_profile(session)
                profile_id = self.create_personal_brand_profile(profile)
                
                updates["generated_profile_id"] = profile_id
                updates["session_quality_score"] = session.session_quality_score
                
                self.update_interview_session(session_id, updates)
                
                return {
                    "status": "completed",
                    "session_id": session_id,
                    "profile_id": profile_id,
                    "summary": next_question,
                    "message": "Interview completed! Your personal brand profile has been generated."
                }
            else:
                self.update_interview_session(session_id, updates)
                
                return {
                    "status": "continuing",
                    "session_id": session_id,
                    "next_question": next_question,
                    "message": "Please continue the conversation."
                }
                
        except Exception as e:
            logger.error(f"Error processing interview response: {e}")
            return {
                "status": "error",
                "message": f"Failed to process response: {str(e)}"
            }
    
    def get_profile_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for user's personal brand profiles"""
        try:
            profiles = self.get_profiles_for_user(user_id)
            sessions = self.get_sessions_for_user(user_id)
            
            if not profiles:
                return {
                    "total_profiles": 0,
                    "total_sessions": len(sessions),
                    "message": "No profiles found for user"
                }
            
            latest_profile = profiles[0]  # Most recent
            
            from ...core.personal_brand import PersonalBrandAnalyzer
            completeness = PersonalBrandAnalyzer.calculate_profile_completeness(latest_profile)
            gaps = PersonalBrandAnalyzer.identify_profile_gaps(latest_profile)
            suggestions = PersonalBrandAnalyzer.suggest_profile_improvements(latest_profile)
            
            analytics = {
                "total_profiles": len(profiles),
                "total_sessions": len(sessions),
                "latest_profile": {
                    "id": "latest",  # Would be actual ID in real implementation
                    "version": latest_profile.profile_version,
                    "created_at": latest_profile.created_at.isoformat(),
                    "completeness_score": completeness,
                    "confidence_score": latest_profile.confidence_score
                },
                "profile_completeness": completeness,
                "profile_gaps": gaps,
                "improvement_suggestions": suggestions,
                "session_quality": {
                    "average_quality": sum(s.session_quality_score for s in sessions) / len(sessions) if sessions else 0,
                    "best_session_quality": max(s.session_quality_score for s in sessions) if sessions else 0,
                    "total_interview_time": sum(s.session_duration for s in sessions)
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting profile analytics: {e}")
            return {
                "error": f"Failed to get analytics: {str(e)}"
            }
    
    def _convert_db_to_profile(self, row: Dict[str, Any]) -> Optional[PersonalBrandProfile]:
        """Convert database row to PersonalBrandProfile object"""
        try:
            from ...core.personal_brand import WorkPreferences, CareerMotivators, IndustryPreferences, RolePreferences
            
            profile = PersonalBrandProfile(
                brand_summary=row["brand_summary"],
                professional_identity=row["professional_identity"],
                unique_value_proposition=row["unique_value_proposition"],
                work_preferences=WorkPreferences(**json.loads(row["work_preferences"])),
                career_motivators=CareerMotivators(**json.loads(row["career_motivators"])),
                industry_preferences=IndustryPreferences(**json.loads(row["industry_preferences"])),
                role_preferences=RolePreferences(**json.loads(row["role_preferences"])),
                career_highlights=json.loads(row["career_highlights"]),
                skills_expertise=json.loads(row["skills_expertise"]),
                education_background=json.loads(row["education_background"]),
                profile_version=row["profile_version"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                user_id=row["user_id"],
                confidence_score=row.get("confidence_score", 0.8)
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error converting database row to profile: {e}")
            return None
    
    def _convert_db_to_session(self, row: Dict[str, Any]) -> Optional[InterviewSession]:
        """Convert database row to InterviewSession object"""
        try:
            session = InterviewSession(
                session_id=row["session_id"],
                user_id=row["user_id"],
                transcript=row["transcript"],
                audio_file_path=row["audio_file_path"],
                session_duration=row["session_duration"],
                questions_asked=json.loads(row["questions_asked"]) if row["questions_asked"] else [],
                key_insights=json.loads(row["key_insights"]) if row["key_insights"] else [],
                generated_profile=None,  # Would load separately if needed
                session_quality_score=row["session_quality_score"],
                created_at=datetime.fromisoformat(row["created_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Error converting database row to session: {e}")
            return None
