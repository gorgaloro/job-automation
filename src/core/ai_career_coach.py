"""
AI Career Coach System

Conducts intelligent voice interviews to extract personal brand profiles.
Uses GPT-4 to guide conversations and generate structured profiles.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import uuid
from openai import OpenAI
from dataclasses import asdict

from .personal_brand import (
    PersonalBrandProfile, WorkPreferences, CareerMotivators, 
    IndustryPreferences, RolePreferences, InterviewSession
)

logger = logging.getLogger(__name__)

class AICareerCoach:
    """AI-powered career coach for personal brand discovery"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI career coach"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.session_insights = []
        
    def start_interview_session(self, user_id: Optional[str] = None) -> InterviewSession:
        """Start a new interview session"""
        session_id = str(uuid.uuid4())
        
        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            transcript="",
            audio_file_path=None,
            session_duration=0,
            questions_asked=[],
            key_insights=[],
            generated_profile=None,
            session_quality_score=0.0,
            created_at=datetime.now()
        )
        
        # Reset conversation state
        self.conversation_history = []
        self.session_insights = []
        
        logger.info(f"Started interview session {session_id} for user {user_id}")
        return session
    
    def get_opening_question(self) -> str:
        """Get the opening question to start the interview"""
        opening_questions = [
            "Hi! I'm your AI career coach, and I'm here to help you discover your professional identity and career preferences. Let's start with something broad - tell me about yourself professionally. What kind of work energizes you?",
            
            "Welcome! I'm excited to help you uncover your personal brand and career alignment. To begin, I'd love to hear your story - what's your professional background, and what aspects of your work bring you the most satisfaction?",
            
            "Hello! I'm here to guide you through a conversation about your career identity and preferences. Let's dive in - when you think about your ideal work environment and role, what comes to mind first?"
        ]
        
        # For now, return the first one - could randomize later
        question = opening_questions[0]
        self.conversation_history.append({"role": "assistant", "content": question})
        return question
    
    def process_user_response(self, user_response: str, session: InterviewSession) -> Tuple[str, bool]:
        """
        Process user response and generate next question or conclude interview
        
        Returns:
            Tuple of (next_question_or_summary, is_complete)
        """
        # Add user response to conversation history
        self.conversation_history.append({"role": "user", "content": user_response})
        session.transcript += f"User: {user_response}\n\n"
        
        # Determine next action based on conversation progress
        if len(self.conversation_history) < 15:  # Continue interview
            next_question = self._generate_follow_up_question()
            self.conversation_history.append({"role": "assistant", "content": next_question})
            session.transcript += f"Coach: {next_question}\n\n"
            session.questions_asked.append(next_question)
            return next_question, False
        else:  # Conclude interview
            summary = self._conclude_interview()
            session.completed_at = datetime.now()
            return summary, True
    
    def _generate_follow_up_question(self) -> str:
        """Generate intelligent follow-up question based on conversation context"""
        
        # Analyze conversation to determine what to explore next
        conversation_text = "\n".join([msg["content"] for msg in self.conversation_history])
        
        prompt = f"""
You are an expert career coach conducting a personal brand discovery interview. Based on the conversation so far, generate the next most insightful question to ask.

CONVERSATION SO FAR:
{conversation_text}

AREAS TO EXPLORE (choose the most relevant based on what hasn't been covered well):
1. Work style preferences (collaborative vs independent, fast-paced vs methodical)
2. Leadership and management style
3. Career motivators (what drives them - impact, learning, autonomy, compensation)
4. Core values and deal-breakers
5. Industry preferences and aversions
6. Company stage/size preferences (startup vs enterprise)
7. Remote work preferences
8. Role responsibilities they enjoy most
9. Career growth trajectory and aspirations
10. Success metrics (how they measure achievement)
11. Past experiences that shaped their preferences
12. Skills they want to develop vs leverage

GUIDELINES:
- Ask ONE focused, open-ended question
- Build on what they've already shared
- Go deeper into areas that seem important to them
- Keep it conversational and engaging
- Avoid yes/no questions
- Make it feel like a natural conversation, not an interrogation

Generate the next question:
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            question = response.choices[0].message.content.strip()
            logger.info(f"Generated follow-up question: {question[:100]}...")
            return question
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            # Fallback questions
            fallback_questions = [
                "What type of work environment brings out your best performance?",
                "Tell me about a time when you felt most engaged and productive at work. What made that experience special?",
                "What are some non-negotiables for you in a role or company?",
                "How do you prefer to work with others - in teams, independently, or a mix?",
                "What industries or types of problems are you most passionate about solving?"
            ]
            return fallback_questions[len(self.conversation_history) % len(fallback_questions)]
    
    def _conclude_interview(self) -> str:
        """Conclude the interview and provide summary"""
        conclusion_message = """
Thank you for sharing so much about your professional identity and preferences! 

I've gathered valuable insights about your work style, motivators, and career aspirations. I'm now going to analyze everything you've shared to create your personalized brand profile.

This profile will help you:
- Identify jobs and companies that align with your values and preferences
- Optimize your resume for roles that truly fit
- Make more strategic career decisions
- Communicate your unique value proposition

Your profile is being generated now and will include your professional identity, work preferences, career motivators, and industry alignment. You'll be able to review and refine it once it's ready.
"""
        
        self.conversation_history.append({"role": "assistant", "content": conclusion_message})
        return conclusion_message
    
    def generate_personal_brand_profile(self, session: InterviewSession) -> PersonalBrandProfile:
        """Generate structured personal brand profile from interview transcript"""
        
        logger.info(f"Generating personal brand profile from session {session.session_id}")
        
        prompt = f"""
You are an expert career coach analyzing an interview transcript to create a comprehensive personal brand profile.

INTERVIEW TRANSCRIPT:
{session.transcript}

Based on this conversation, create a detailed personal brand profile with the following structure:

1. BRAND SUMMARY (2-3 sentences capturing their professional identity)
2. PROFESSIONAL IDENTITY (how they see themselves professionally)
3. UNIQUE VALUE PROPOSITION (what makes them unique and valuable)
4. WORK PREFERENCES:
   - Work style (collaborative, independent, fast-paced, methodical, etc.)
   - Leadership style (servant-leader, hands-on, strategic, etc.)
   - Team size preference (small, medium, large, varies)
   - Remote preference (remote, hybrid, in-person, flexible)
   - Company stage (startup, growth, enterprise)
   - Company size (<50, 50-200, 200-1000, >1000)
5. CAREER MOTIVATORS:
   - Primary motivators (impact, learning, autonomy, compensation, recognition, etc.)
   - Core values (work-life-balance, diversity, innovation, stability, etc.)
   - Deal breakers (micromanagement, toxic culture, no growth, etc.)
   - Success metrics (how they measure achievement)
6. INDUSTRY PREFERENCES:
   - Preferred industries
   - Industries to avoid
   - Domain expertise areas
   - Emerging interests
7. ROLE PREFERENCES:
   - Preferred role types
   - Responsibilities they enjoy
   - Growth trajectory
   - Management interest level
8. CAREER HIGHLIGHTS (key achievements and experiences mentioned)
9. SKILLS & EXPERTISE (technical and soft skills mentioned)
10. EDUCATION BACKGROUND (if mentioned)

IMPORTANT GUIDELINES:
- Base everything on what was actually discussed in the interview
- If something wasn't mentioned, use reasonable inferences but mark uncertainty
- Keep lists focused and actionable (3-8 items per list)
- Make the brand summary compelling and authentic to their voice
- Ensure consistency across all sections
- Use their own words and phrases where possible

Return the response as a JSON object with this exact structure:
{{
  "brand_summary": "string",
  "professional_identity": "string", 
  "unique_value_proposition": "string",
  "work_preferences": {{
    "work_style": ["string"],
    "leadership_style": ["string"],
    "team_size_preference": "string",
    "remote_preference": "string",
    "company_stage": ["string"],
    "company_size": ["string"]
  }},
  "career_motivators": {{
    "primary_motivators": ["string"],
    "values": ["string"],
    "deal_breakers": ["string"],
    "success_metrics": ["string"]
  }},
  "industry_preferences": {{
    "preferred_industries": ["string"],
    "avoided_industries": ["string"],
    "domain_expertise": ["string"],
    "emerging_interests": ["string"]
  }},
  "role_preferences": {{
    "preferred_roles": ["string"],
    "role_responsibilities": ["string"],
    "growth_trajectory": "string",
    "management_interest": "string"
  }},
  "career_highlights": ["string"],
  "skills_expertise": ["string"],
  "education_background": ["string"],
  "confidence_score": 0.85
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            profile_json = response.choices[0].message.content.strip()
            
            # Parse JSON response
            profile_data = json.loads(profile_json)
            
            # Create PersonalBrandProfile object
            profile = PersonalBrandProfile(
                brand_summary=profile_data["brand_summary"],
                professional_identity=profile_data["professional_identity"],
                unique_value_proposition=profile_data["unique_value_proposition"],
                work_preferences=WorkPreferences(**profile_data["work_preferences"]),
                career_motivators=CareerMotivators(**profile_data["career_motivators"]),
                industry_preferences=IndustryPreferences(**profile_data["industry_preferences"]),
                role_preferences=RolePreferences(**profile_data["role_preferences"]),
                career_highlights=profile_data["career_highlights"],
                skills_expertise=profile_data["skills_expertise"],
                education_background=profile_data["education_background"],
                profile_version="1.0",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                user_id=session.user_id,
                confidence_score=profile_data.get("confidence_score", 0.8)
            )
            
            # Update session with generated profile
            session.generated_profile = profile
            session.session_quality_score = self._calculate_session_quality(session)
            
            logger.info(f"Successfully generated personal brand profile for session {session.session_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error generating personal brand profile: {e}")
            raise Exception(f"Failed to generate personal brand profile: {str(e)}")
    
    def _calculate_session_quality(self, session: InterviewSession) -> float:
        """Calculate the quality score of the interview session"""
        quality_factors = []
        
        # Length of conversation (more is generally better up to a point)
        conversation_length = len(self.conversation_history)
        length_score = min(conversation_length / 20, 1.0)  # Optimal around 20 exchanges
        quality_factors.append(length_score)
        
        # Transcript length (more detailed responses are better)
        transcript_words = len(session.transcript.split())
        word_score = min(transcript_words / 1000, 1.0)  # Optimal around 1000 words
        quality_factors.append(word_score)
        
        # Number of questions asked
        questions_score = min(len(session.questions_asked) / 10, 1.0)  # Optimal around 10 questions
        quality_factors.append(questions_score)
        
        # Profile completeness (if generated)
        if session.generated_profile:
            from .personal_brand import PersonalBrandAnalyzer
            completeness = PersonalBrandAnalyzer.calculate_profile_completeness(session.generated_profile)
            quality_factors.append(completeness)
        
        return sum(quality_factors) / len(quality_factors)
    
    def refine_profile_with_feedback(self, profile: PersonalBrandProfile, feedback: str) -> PersonalBrandProfile:
        """Refine the profile based on user feedback"""
        
        prompt = f"""
You are refining a personal brand profile based on user feedback.

CURRENT PROFILE:
{profile.to_json()}

USER FEEDBACK:
{feedback}

Please update the profile based on the feedback. Return the updated profile as JSON with the same structure, incorporating the user's corrections and suggestions.

Guidelines:
- Make specific changes requested by the user
- Maintain consistency across all sections
- Update the updated_at timestamp
- Increment the profile version
- Keep the same overall structure
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            updated_json = response.choices[0].message.content.strip()
            updated_data = json.loads(updated_json)
            
            # Create updated profile
            updated_profile = PersonalBrandProfile.from_dict(updated_data)
            updated_profile.updated_at = datetime.now()
            updated_profile.profile_version = f"{float(profile.profile_version) + 0.1:.1f}"
            
            logger.info(f"Refined profile based on user feedback")
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error refining profile: {e}")
            raise Exception(f"Failed to refine profile: {str(e)}")
    
    def generate_profile_insights(self, profile: PersonalBrandProfile) -> Dict[str, Any]:
        """Generate insights and recommendations based on the profile"""
        
        prompt = f"""
Analyze this personal brand profile and provide actionable insights and recommendations.

PROFILE:
{profile.to_json()}

Provide insights in the following areas:

1. STRENGTHS: What are their key professional strengths based on this profile?
2. OPPORTUNITIES: What career opportunities align best with their profile?
3. POTENTIAL CHALLENGES: What challenges might they face given their preferences?
4. RECOMMENDATIONS: Specific actions they should take for career success
5. PROFILE GAPS: What additional information would strengthen their profile?
6. MARKET POSITIONING: How should they position themselves in the job market?

Return as JSON:
{{
  "strengths": ["string"],
  "opportunities": ["string"], 
  "challenges": ["string"],
  "recommendations": ["string"],
  "profile_gaps": ["string"],
  "market_positioning": "string"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.4
            )
            
            insights_json = response.choices[0].message.content.strip()
            insights = json.loads(insights_json)
            
            logger.info("Generated profile insights successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating profile insights: {e}")
            return {
                "strengths": ["Profile analysis unavailable"],
                "opportunities": ["Please try again later"],
                "challenges": ["Analysis service temporarily unavailable"],
                "recommendations": ["Contact support if issue persists"],
                "profile_gaps": ["Unable to analyze at this time"],
                "market_positioning": "Analysis unavailable"
            }

def create_sample_interview_session() -> InterviewSession:
    """Create a sample interview session for testing"""
    return InterviewSession(
        session_id=str(uuid.uuid4()),
        user_id="test_user",
        transcript="""
Coach: Hi! I'm your AI career coach, and I'm here to help you discover your professional identity and career preferences. Let's start with something broad - tell me about yourself professionally. What kind of work energizes you?

User: I'm a software engineer with about 5 years of experience. I really love building things from scratch and solving complex technical problems. What energizes me most is when I can see the direct impact of my work on users and the business.

Coach: That's great! It sounds like you're driven by both technical challenges and meaningful impact. Tell me more about the types of environments where you've felt most productive and engaged.

User: I definitely thrive in smaller, fast-moving teams where I can wear multiple hats. I've worked at both large corporations and startups, and I much prefer the startup environment where decisions are made quickly and I can have more influence on the product direction.

Coach: Interesting! It sounds like autonomy and influence are important to you. What about leadership - do you enjoy mentoring others or leading projects?

User: Yes, I really enjoy mentoring junior developers. I find it rewarding to help others grow and see them succeed. I'm not sure if I want to be a full-time manager, but I like the technical leadership aspect.

Coach: That's a valuable insight. When you think about your ideal role, what specific responsibilities would you want to focus on?

User: I'd love to be involved in system architecture decisions, mentor other engineers, and work closely with product teams to shape what we build. I want to stay technical but also have strategic input.
""",
        audio_file_path=None,
        session_duration=900,  # 15 minutes
        questions_asked=[
            "Tell me about yourself professionally. What kind of work energizes you?",
            "Tell me more about the types of environments where you've felt most productive and engaged.",
            "What about leadership - do you enjoy mentoring others or leading projects?",
            "When you think about your ideal role, what specific responsibilities would you want to focus on?"
        ],
        key_insights=[
            "Driven by technical challenges and meaningful impact",
            "Prefers startup environments with fast decision-making",
            "Values autonomy and influence on product direction",
            "Enjoys mentoring but prefers technical leadership over management"
        ],
        generated_profile=None,
        session_quality_score=0.85,
        created_at=datetime.now(),
        completed_at=datetime.now()
    )
