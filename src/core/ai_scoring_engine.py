"""
AI Scoring & Decision Support Engine

This module provides intelligent scoring capabilities for jobs, companies, and resumes
based on personal brand profiles and AI-powered analysis.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScoringResult:
    """Result of an AI scoring operation"""
    score: float  # 0-100
    rationale: str
    confidence: float  # 0-1
    scoring_factors: Dict[str, Any]
    timestamp: datetime
    profile_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class JobScoringResult(ScoringResult):
    """Job-specific scoring result"""
    job_id: str
    job_title: str
    company_name: str
    alignment_areas: List[str]
    concern_areas: List[str]
    recommended_resume_version: Optional[str] = None

@dataclass
class CompanyScoringResult(ScoringResult):
    """Company-specific scoring result"""
    company_id: str
    company_name: str
    industry_alignment: float
    culture_alignment: float
    values_alignment: float
    size_stage_alignment: float

@dataclass
class ResumeScoringResult(ScoringResult):
    """Resume vs Job scoring result"""
    resume_id: str
    job_id: str
    resume_version: str
    keyword_match_score: float
    experience_relevance: float
    skills_alignment: float
    suggested_improvements: List[str]

class AIJobScorer:
    """AI-powered job scoring against personal brand profiles"""
    
    def __init__(self):
        """Initialize the job scorer"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            logger.warning("OpenAI API key not found - running in demo mode")
    
    def score_job_alignment(self, job_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> JobScoringResult:
        """
        Score how well a job aligns with a personal brand profile
        
        Args:
            job_data: Job information including title, description, company, etc.
            brand_profile: Personal brand profile data
            
        Returns:
            JobScoringResult with score and detailed analysis
        """
        try:
            if not self.client.api_key:
                return self._demo_job_scoring(job_data, brand_profile)
            
            # Prepare scoring prompt
            prompt = self._build_job_scoring_prompt(job_data, brand_profile)
            
            # Get AI scoring
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career advisor who analyzes job-candidate fit based on personal brand profiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response
            result_data = json.loads(response.choices[0].message.content)
            
            return JobScoringResult(
                job_id=job_data.get('id', 'unknown'),
                job_title=job_data.get('title', 'Unknown Position'),
                company_name=job_data.get('company_name', 'Unknown Company'),
                score=result_data['score'],
                rationale=result_data['rationale'],
                confidence=result_data['confidence'],
                scoring_factors=result_data['scoring_factors'],
                alignment_areas=result_data['alignment_areas'],
                concern_areas=result_data['concern_areas'],
                recommended_resume_version=result_data.get('recommended_resume_version'),
                timestamp=datetime.now(),
                profile_version=brand_profile.get('profile_version', '1.0')
            )
            
        except Exception as e:
            logger.error(f"Job scoring failed: {e}")
            return self._demo_job_scoring(job_data, brand_profile)
    
    def _build_job_scoring_prompt(self, job_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> str:
        """Build the AI prompt for job scoring"""
        return f"""
Analyze the alignment between this job opportunity and the candidate's personal brand profile.

JOB INFORMATION:
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company_name', 'N/A')}
Description: {job_data.get('description', 'N/A')[:1000]}...
Location: {job_data.get('location', 'N/A')}
Remote: {job_data.get('remote_friendly', 'N/A')}
Company Stage: {job_data.get('company_stage', 'N/A')}
Industry: {job_data.get('industry', 'N/A')}

PERSONAL BRAND PROFILE:
Professional Identity: {brand_profile.get('professional_identity', 'N/A')}
Brand Summary: {brand_profile.get('brand_summary', 'N/A')}
Work Preferences: {json.dumps(brand_profile.get('work_preferences', {}), indent=2)}
Career Motivators: {json.dumps(brand_profile.get('career_motivators', {}), indent=2)}
Industry Preferences: {json.dumps(brand_profile.get('industry_preferences', {}), indent=2)}
Role Preferences: {json.dumps(brand_profile.get('role_preferences', {}), indent=2)}

SCORING CRITERIA:
1. Role Alignment (25%): How well does the job title and responsibilities match preferred roles?
2. Industry Fit (20%): Does the company industry align with preferences?
3. Work Environment (20%): Company stage, size, remote policy vs preferences
4. Values Alignment (15%): Do company values match career motivators?
5. Growth Opportunity (10%): Does the role support desired growth trajectory?
6. Deal Breaker Check (10%): Are there any absolute deal breakers present?

Return a JSON response with:
{{
    "score": <0-100 numeric score>,
    "rationale": "<2-3 sentence explanation of the score>",
    "confidence": <0-1 confidence in the scoring>,
    "scoring_factors": {{
        "role_alignment": <0-100>,
        "industry_fit": <0-100>,
        "work_environment": <0-100>,
        "values_alignment": <0-100>,
        "growth_opportunity": <0-100>,
        "deal_breaker_penalty": <0-100>
    }},
    "alignment_areas": ["<area1>", "<area2>", ...],
    "concern_areas": ["<concern1>", "<concern2>", ...],
    "recommended_resume_version": "<version_name_if_applicable>"
}}
"""
    
    def _demo_job_scoring(self, job_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> JobScoringResult:
        """Demo mode job scoring with simulated results"""
        
        # Simulate scoring based on simple heuristics
        base_score = 75
        
        # Adjust based on industry preferences
        preferred_industries = brand_profile.get('industry_preferences', {}).get('preferred_industries', [])
        job_industry = job_data.get('industry', '').lower()
        
        industry_bonus = 0
        for pref_industry in preferred_industries:
            if pref_industry.lower() in job_industry:
                industry_bonus = 15
                break
        
        # Adjust based on remote preferences
        remote_pref = brand_profile.get('work_preferences', {}).get('remote_preference', 'hybrid')
        job_remote = job_data.get('remote_friendly', False)
        
        remote_bonus = 0
        if remote_pref == 'remote' and job_remote:
            remote_bonus = 10
        elif remote_pref == 'hybrid' and job_remote:
            remote_bonus = 5
        
        final_score = min(100, base_score + industry_bonus + remote_bonus)
        
        return JobScoringResult(
            job_id=job_data.get('id', 'demo_job'),
            job_title=job_data.get('title', 'Demo Position'),
            company_name=job_data.get('company_name', 'Demo Company'),
            score=final_score,
            rationale=f"Strong alignment with your {preferred_industries[0] if preferred_industries else 'preferred'} industry focus and {remote_pref} work preference. The role matches your technical leadership interests.",
            confidence=0.85,
            scoring_factors={
                "role_alignment": 80,
                "industry_fit": 85 if industry_bonus > 0 else 70,
                "work_environment": 75 + remote_bonus,
                "values_alignment": 80,
                "growth_opportunity": 85,
                "deal_breaker_penalty": 0
            },
            alignment_areas=["Technical leadership", "Industry focus", "Growth opportunity"],
            concern_areas=["Company size unclear", "Compensation not specified"],
            recommended_resume_version="technical_leadership_v2",
            timestamp=datetime.now(),
            profile_version=brand_profile.get('profile_version', '1.0')
        )

class AICompanyScorer:
    """AI-powered company scoring for culture and mission fit"""
    
    def __init__(self):
        """Initialize the company scorer"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            logger.warning("OpenAI API key not found - running in demo mode")
    
    def score_company_fit(self, company_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> CompanyScoringResult:
        """
        Score how well a company aligns with personal brand values and preferences
        
        Args:
            company_data: Company information including mission, values, stage, etc.
            brand_profile: Personal brand profile data
            
        Returns:
            CompanyScoringResult with detailed alignment analysis
        """
        try:
            if not self.client.api_key:
                return self._demo_company_scoring(company_data, brand_profile)
            
            # Prepare scoring prompt
            prompt = self._build_company_scoring_prompt(company_data, brand_profile)
            
            # Get AI scoring
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in company culture analysis and candidate-company fit assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response
            result_data = json.loads(response.choices[0].message.content)
            
            return CompanyScoringResult(
                company_id=company_data.get('id', 'unknown'),
                company_name=company_data.get('name', 'Unknown Company'),
                score=result_data['score'],
                rationale=result_data['rationale'],
                confidence=result_data['confidence'],
                scoring_factors=result_data['scoring_factors'],
                industry_alignment=result_data['industry_alignment'],
                culture_alignment=result_data['culture_alignment'],
                values_alignment=result_data['values_alignment'],
                size_stage_alignment=result_data['size_stage_alignment'],
                timestamp=datetime.now(),
                profile_version=brand_profile.get('profile_version', '1.0')
            )
            
        except Exception as e:
            logger.error(f"Company scoring failed: {e}")
            return self._demo_company_scoring(company_data, brand_profile)
    
    def _build_company_scoring_prompt(self, company_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> str:
        """Build the AI prompt for company scoring"""
        return f"""
Analyze the cultural and mission alignment between this company and the candidate's personal brand profile.

COMPANY INFORMATION:
Name: {company_data.get('name', 'N/A')}
Industry: {company_data.get('industry', 'N/A')}
Mission: {company_data.get('mission_statement', 'N/A')}
About: {company_data.get('about', 'N/A')[:500]}...
Size: {company_data.get('num_employees', 'N/A')} employees
Stage: {company_data.get('funding_stage', 'N/A')}
Values: {company_data.get('values_summary', 'N/A')}
Tech Focus: {company_data.get('tech_focus', 'N/A')}

PERSONAL BRAND PROFILE:
Values: {brand_profile.get('career_motivators', {}).get('values', [])}
Deal Breakers: {brand_profile.get('career_motivators', {}).get('deal_breakers', [])}
Preferred Industries: {brand_profile.get('industry_preferences', {}).get('preferred_industries', [])}
Avoided Industries: {brand_profile.get('industry_preferences', {}).get('avoided_industries', [])}
Company Stage Preference: {brand_profile.get('work_preferences', {}).get('company_stage', [])}
Company Size Preference: {brand_profile.get('work_preferences', {}).get('company_size', [])}

SCORING CRITERIA:
1. Industry Alignment (30%): Does the company industry match preferences and avoid deal breakers?
2. Values Alignment (25%): Do company values align with personal values?
3. Culture Fit (25%): Does the company culture match work style preferences?
4. Size/Stage Fit (20%): Does company size and stage match preferences?

Return a JSON response with:
{{
    "score": <0-100 numeric score>,
    "rationale": "<2-3 sentence explanation of the score>",
    "confidence": <0-1 confidence in the scoring>,
    "scoring_factors": {{
        "industry_match": <0-100>,
        "values_alignment": <0-100>,
        "culture_fit": <0-100>,
        "size_stage_fit": <0-100>
    }},
    "industry_alignment": <0-100>,
    "culture_alignment": <0-100>,
    "values_alignment": <0-100>,
    "size_stage_alignment": <0-100>
}}
"""
    
    def _demo_company_scoring(self, company_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> CompanyScoringResult:
        """Demo mode company scoring with simulated results"""
        
        base_score = 78
        
        # Check industry alignment
        preferred_industries = brand_profile.get('industry_preferences', {}).get('preferred_industries', [])
        avoided_industries = brand_profile.get('industry_preferences', {}).get('avoided_industries', [])
        company_industry = company_data.get('industry', '').lower()
        
        industry_score = 70
        for pref in preferred_industries:
            if pref.lower() in company_industry:
                industry_score = 90
                break
        
        for avoid in avoided_industries:
            if avoid.lower() in company_industry:
                industry_score = 20
                break
        
        # Check company stage alignment
        preferred_stages = brand_profile.get('work_preferences', {}).get('company_stage', [])
        company_stage = company_data.get('funding_stage', '').lower()
        
        stage_score = 75
        for pref_stage in preferred_stages:
            if pref_stage.lower() in company_stage:
                stage_score = 85
                break
        
        final_score = int((base_score + industry_score + stage_score) / 3)
        
        return CompanyScoringResult(
            company_id=company_data.get('id', 'demo_company'),
            company_name=company_data.get('name', 'Demo Company'),
            score=final_score,
            rationale=f"Good alignment with your industry preferences and company stage interests. The mission resonates with your values around {brand_profile.get('career_motivators', {}).get('values', ['growth'])[0]}.",
            confidence=0.82,
            scoring_factors={
                "industry_match": industry_score,
                "values_alignment": 85,
                "culture_fit": 80,
                "size_stage_fit": stage_score
            },
            industry_alignment=industry_score,
            culture_alignment=80,
            values_alignment=85,
            size_stage_alignment=stage_score,
            timestamp=datetime.now(),
            profile_version=brand_profile.get('profile_version', '1.0')
        )

class AIResumeScorer:
    """AI-powered resume vs job description scoring"""
    
    def __init__(self):
        """Initialize the resume scorer"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            logger.warning("OpenAI API key not found - running in demo mode")
    
    def score_resume_job_fit(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> ResumeScoringResult:
        """
        Score how well a resume matches a specific job description
        
        Args:
            resume_data: Resume content and metadata
            job_data: Job description and requirements
            brand_profile: Personal brand context for scoring
            
        Returns:
            ResumeScoringResult with detailed match analysis
        """
        try:
            if not self.client.api_key:
                return self._demo_resume_scoring(resume_data, job_data, brand_profile)
            
            # Prepare scoring prompt
            prompt = self._build_resume_scoring_prompt(resume_data, job_data, brand_profile)
            
            # Get AI scoring
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and ATS optimization specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response
            result_data = json.loads(response.choices[0].message.content)
            
            return ResumeScoringResult(
                resume_id=resume_data.get('id', 'unknown'),
                job_id=job_data.get('id', 'unknown'),
                resume_version=resume_data.get('version', '1.0'),
                score=result_data['score'],
                rationale=result_data['rationale'],
                confidence=result_data['confidence'],
                scoring_factors=result_data['scoring_factors'],
                keyword_match_score=result_data['keyword_match_score'],
                experience_relevance=result_data['experience_relevance'],
                skills_alignment=result_data['skills_alignment'],
                suggested_improvements=result_data['suggested_improvements'],
                timestamp=datetime.now(),
                profile_version=brand_profile.get('profile_version', '1.0')
            )
            
        except Exception as e:
            logger.error(f"Resume scoring failed: {e}")
            return self._demo_resume_scoring(resume_data, job_data, brand_profile)
    
    def _build_resume_scoring_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> str:
        """Build the AI prompt for resume scoring"""
        return f"""
Analyze how well this resume matches the job requirements and optimize for ATS compatibility.

RESUME CONTENT:
Version: {resume_data.get('version', 'N/A')}
Summary: {resume_data.get('summary', 'N/A')}
Experience: {resume_data.get('experience', 'N/A')[:1000]}...
Skills: {resume_data.get('skills', [])}
Education: {resume_data.get('education', 'N/A')}

JOB REQUIREMENTS:
Title: {job_data.get('title', 'N/A')}
Description: {job_data.get('description', 'N/A')[:1000]}...
Required Skills: {job_data.get('required_skills', [])}
Preferred Skills: {job_data.get('preferred_skills', [])}
Experience Level: {job_data.get('experience_level', 'N/A')}

PERSONAL BRAND CONTEXT:
Professional Identity: {brand_profile.get('professional_identity', 'N/A')}
Skills Expertise: {brand_profile.get('skills_expertise', [])}

SCORING CRITERIA:
1. Keyword Match (30%): How many job keywords appear in the resume?
2. Experience Relevance (25%): How relevant is the work experience?
3. Skills Alignment (25%): Do resume skills match job requirements?
4. ATS Optimization (20%): Is the resume ATS-friendly?

Return a JSON response with:
{{
    "score": <0-100 numeric score>,
    "rationale": "<2-3 sentence explanation of the score>",
    "confidence": <0-1 confidence in the scoring>,
    "scoring_factors": {{
        "keyword_match": <0-100>,
        "experience_relevance": <0-100>,
        "skills_alignment": <0-100>,
        "ats_optimization": <0-100>
    }},
    "keyword_match_score": <0-100>,
    "experience_relevance": <0-100>,
    "skills_alignment": <0-100>,
    "suggested_improvements": ["<improvement1>", "<improvement2>", ...]
}}
"""
    
    def _demo_resume_scoring(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], brand_profile: Dict[str, Any]) -> ResumeScoringResult:
        """Demo mode resume scoring with simulated results"""
        
        # Simulate keyword matching
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        job_skills = set(skill.lower() for skill in job_data.get('required_skills', []))
        
        keyword_match = len(resume_skills.intersection(job_skills)) / max(len(job_skills), 1) * 100
        
        # Simulate experience relevance
        experience_score = 82  # Base score
        
        # Simulate skills alignment
        skills_score = min(100, keyword_match + 20)
        
        final_score = int((keyword_match + experience_score + skills_score) / 3)
        
        return ResumeScoringResult(
            resume_id=resume_data.get('id', 'demo_resume'),
            job_id=job_data.get('id', 'demo_job'),
            resume_version=resume_data.get('version', '1.0'),
            score=final_score,
            rationale=f"Strong match with {len(resume_skills.intersection(job_skills))} overlapping skills and relevant experience. Consider emphasizing {list(job_skills - resume_skills)[:2]} skills if you have them.",
            confidence=0.88,
            scoring_factors={
                "keyword_match": keyword_match,
                "experience_relevance": experience_score,
                "skills_alignment": skills_score,
                "ats_optimization": 85
            },
            keyword_match_score=keyword_match,
            experience_relevance=experience_score,
            skills_alignment=skills_score,
            suggested_improvements=[
                "Add more quantified achievements",
                "Include missing keywords from job description",
                "Optimize for ATS scanning"
            ],
            timestamp=datetime.now(),
            profile_version=brand_profile.get('profile_version', '1.0')
        )

class ScoringOrchestrator:
    """Orchestrates all scoring operations and manages results"""
    
    def __init__(self):
        """Initialize the scoring orchestrator"""
        self.job_scorer = AIJobScorer()
        self.company_scorer = AICompanyScorer()
        self.resume_scorer = AIResumeScorer()
    
    def score_opportunity(self, job_data: Dict[str, Any], company_data: Dict[str, Any], 
                         resume_versions: List[Dict[str, Any]], brand_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive scoring of a job opportunity including job fit, company fit, and resume matching
        
        Args:
            job_data: Job information
            company_data: Company information
            resume_versions: List of available resume versions
            brand_profile: Personal brand profile
            
        Returns:
            Comprehensive scoring results
        """
        results = {
            'job_score': None,
            'company_score': None,
            'resume_scores': [],
            'recommended_resume': None,
            'overall_score': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Score job alignment
            job_result = self.job_scorer.score_job_alignment(job_data, brand_profile)
            results['job_score'] = job_result.to_dict()
            
            # Score company fit
            company_result = self.company_scorer.score_company_fit(company_data, brand_profile)
            results['company_score'] = company_result.to_dict()
            
            # Score each resume version
            best_resume_score = 0
            best_resume = None
            
            for resume in resume_versions:
                resume_result = self.resume_scorer.score_resume_job_fit(resume, job_data, brand_profile)
                results['resume_scores'].append(resume_result.to_dict())
                
                if resume_result.score > best_resume_score:
                    best_resume_score = resume_result.score
                    best_resume = resume_result
            
            results['recommended_resume'] = best_resume.to_dict() if best_resume else None
            
            # Calculate overall score (weighted average)
            job_weight = 0.4
            company_weight = 0.3
            resume_weight = 0.3
            
            overall_score = (
                job_result.score * job_weight +
                company_result.score * company_weight +
                best_resume_score * resume_weight
            )
            
            results['overall_score'] = round(overall_score, 1)
            
            logger.info(f"Scored opportunity: {job_data.get('title', 'Unknown')} at {company_data.get('name', 'Unknown')} - Overall: {overall_score:.1f}")
            
        except Exception as e:
            logger.error(f"Opportunity scoring failed: {e}")
            results['error'] = str(e)
        
        return results
    
    def batch_score_jobs(self, jobs_data: List[Dict[str, Any]], brand_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score multiple jobs in batch for efficiency
        
        Args:
            jobs_data: List of job data dictionaries
            brand_profile: Personal brand profile
            
        Returns:
            List of job scoring results
        """
        results = []
        
        for job_data in jobs_data:
            try:
                job_result = self.job_scorer.score_job_alignment(job_data, brand_profile)
                results.append(job_result.to_dict())
            except Exception as e:
                logger.error(f"Failed to score job {job_data.get('title', 'Unknown')}: {e}")
                continue
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

# Sample data for testing
def create_sample_job_data() -> Dict[str, Any]:
    """Create sample job data for testing"""
    return {
        'id': 'job_001',
        'title': 'Senior Software Engineer',
        'company_name': 'TechCorp',
        'description': 'We are looking for a senior software engineer to join our team building scalable web applications. You will work with React, Node.js, and AWS to deliver high-quality software solutions.',
        'location': 'San Francisco, CA',
        'remote_friendly': True,
        'company_stage': 'growth',
        'industry': 'fintech',
        'required_skills': ['JavaScript', 'React', 'Node.js', 'AWS', 'Python'],
        'preferred_skills': ['TypeScript', 'Docker', 'Kubernetes'],
        'experience_level': 'senior'
    }

def create_sample_company_data() -> Dict[str, Any]:
    """Create sample company data for testing"""
    return {
        'id': 'company_001',
        'name': 'TechCorp',
        'industry': 'fintech',
        'mission_statement': 'Democratizing financial services through innovative technology',
        'about': 'TechCorp is a fast-growing fintech company focused on building the next generation of financial tools for consumers and businesses.',
        'num_employees': 150,
        'funding_stage': 'series_b',
        'values_summary': 'Innovation, transparency, customer-first, work-life balance',
        'tech_focus': 'web applications, mobile apps, machine learning'
    }

def create_sample_resume_data() -> Dict[str, Any]:
    """Create sample resume data for testing"""
    return {
        'id': 'resume_001',
        'version': 'technical_leadership_v2',
        'summary': 'Senior Software Engineer with 5+ years of experience building scalable web applications using React, Node.js, and cloud technologies.',
        'experience': 'Led development of customer-facing web applications serving 100K+ users. Built microservices architecture using Node.js and AWS.',
        'skills': ['JavaScript', 'React', 'Node.js', 'AWS', 'Python', 'Docker', 'System Design'],
        'education': 'BS Computer Science, Stanford University'
    }
