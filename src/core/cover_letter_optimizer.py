#!/usr/bin/env python3
"""
Cover Letter Module

Generates dynamic, AI-powered cover letters that integrate seamlessly with 
the Resume to create compelling, personalized application materials.

Key Features:
- Resume data integration and alignment
- Company intelligence and culture analysis
- AI-powered content generation and optimization
- Multiple template and tone options
- Performance tracking and analytics
- AI Career Coach narrative integration
- Company culture insights
- Authentic storytelling approach
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import openai
import os
from datetime import datetime
import json
import re
from .ai_career_coach import AICareerCoach
from .company_enrichment_engine import CompanyEnrichmentEngines
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Install with: pip install openai")
    openai = None

@dataclass
class JobPosting:
    """Job posting data structure"""
    title: str
    company: str
    description: str
    requirements: List[str]
    preferred_qualifications: List[str]
    company_culture: str = ""
    industry: str = ""
    role_type: str = ""

@dataclass
class ResumeData:
    """Resume data from Resume module"""
    executive_summary: str
    selected_experience: List[Dict]
    selected_skills: List[str]
    selected_achievements: List[str]
    ai_suggestions: List[Dict]
    optimization_score: float

@dataclass
class CoverLetterContent:
    """Generated cover letter content"""
    opening_paragraph: str
    body_paragraphs: List[str]
    closing_paragraph: str
    word_count: int
    keyword_density: Dict[str, float]
    tone_score: float
    effectiveness_score: float

class CoverLetterTone(Enum):
    """Cover letter tone options"""
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"

class TemplateType(Enum):
    """Cover letter template types"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    CONSULTING = "consulting"
    SALES = "sales"
    MARKETING = "marketing"

class CoverLetter:
    """
    Main Cover Letter class that generates personalized cover letters
    by integrating resume data, company insights, and AI-powered content generation.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the Cover Letter module"""
        self.openai_client = None
        if openai_api_key and openai:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Load templates and configurations
        self.templates = self._load_templates()
        self.tone_configurations = self._load_tone_configurations()
        
    def generate_cover_letter(
        self,
        job_posting: JobPosting,
        resume_data: ResumeData,
        template_type: TemplateType = TemplateType.TECHNOLOGY,
        tone: CoverLetterTone = CoverLetterTone.PROFESSIONAL,
        custom_instructions: str = ""
    ) -> CoverLetterContent:
        """
        Generate a complete cover letter optimized for the specific job and company.
        
        Args:
            job_posting: Job posting information
            resume_data: Resume data from Resume module
            template_type: Template style to use
            tone: Desired tone for the cover letter
            custom_instructions: Additional customization instructions
            
        Returns:
            CoverLetterContent: Generated cover letter with metadata
        """
        
        # Analyze job posting for key requirements and keywords
        job_analysis = self._analyze_job_posting(job_posting)
        
        # Select most relevant resume content
        relevant_content = self._select_relevant_content(resume_data, job_analysis)
        
        # Generate cover letter sections
        opening = self._generate_opening_paragraph(job_posting, relevant_content, tone)
        body = self._generate_body_paragraphs(job_posting, relevant_content, tone)
        closing = self._generate_closing_paragraph(job_posting, tone)
        
        # Calculate metrics
        full_text = f"{opening} {' '.join(body)} {closing}"
        word_count = len(full_text.split())
        keyword_density = self._calculate_keyword_density(full_text, job_analysis['keywords'])
        tone_score = self._calculate_tone_score(full_text, tone)
        effectiveness_score = self._calculate_effectiveness_score(
            full_text, job_analysis, relevant_content
        )
        
        return CoverLetterContent(
            opening_paragraph=opening,
            body_paragraphs=body,
            closing_paragraph=closing,
            word_count=word_count,
            keyword_density=keyword_density,
            tone_score=tone_score,
            effectiveness_score=effectiveness_score
        )
    
    def _analyze_job_posting(self, job_posting: JobPosting) -> Dict:
        """Analyze job posting to extract key requirements and keywords"""
        
        # Extract keywords from job description
        keywords = self._extract_keywords(job_posting.description)
        
        # Identify key requirements
        requirements = job_posting.requirements + job_posting.preferred_qualifications
        
        # Determine company culture indicators
        culture_indicators = self._analyze_company_culture(job_posting.description)
        
        # Identify role focus areas
        focus_areas = self._identify_focus_areas(job_posting.description)
        
        return {
            'keywords': keywords,
            'requirements': requirements,
            'culture_indicators': culture_indicators,
            'focus_areas': focus_areas,
            'industry': job_posting.industry,
            'role_type': job_posting.role_type
        }
    
    def _select_relevant_content(self, resume_data: ResumeData, job_analysis: Dict) -> Dict:
        """Select most relevant resume content for the cover letter"""
        
        # Score experience items by relevance
        scored_experience = []
        for exp in resume_data.selected_experience:
            relevance_score = self._calculate_relevance_score(exp, job_analysis)
            scored_experience.append((exp, relevance_score))
        
        # Sort by relevance and select top items
        scored_experience.sort(key=lambda x: x[1], reverse=True)
        top_experience = [exp for exp, score in scored_experience[:3]]
        
        # Select relevant skills
        relevant_skills = self._select_relevant_skills(
            resume_data.selected_skills, job_analysis['keywords']
        )
        
        # Select relevant achievements
        relevant_achievements = self._select_relevant_achievements(
            resume_data.selected_achievements, job_analysis
        )
        
        # Include relevant AI suggestions
        relevant_ai_suggestions = self._select_relevant_ai_suggestions(
            resume_data.ai_suggestions, job_analysis
        )
        
        return {
            'experience': top_experience,
            'skills': relevant_skills,
            'achievements': relevant_achievements,
            'ai_suggestions': relevant_ai_suggestions,
            'executive_summary': resume_data.executive_summary
        }
    
    def _generate_opening_paragraph(
        self, 
        job_posting: JobPosting, 
        relevant_content: Dict, 
        tone: CoverLetterTone
    ) -> str:
        """Generate compelling opening paragraph"""
        
        if self.openai_client:
            return self._generate_ai_opening(job_posting, relevant_content, tone)
        else:
            return self._generate_template_opening(job_posting, relevant_content, tone)
    
    def _generate_ai_opening(
        self, 
        job_posting: JobPosting, 
        relevant_content: Dict, 
        tone: CoverLetterTone
    ) -> str:
        """Generate AI-powered opening paragraph"""
        
        prompt = f"""
        Generate a compelling opening paragraph for a cover letter with the following details:
        
        Job Title: {job_posting.title}
        Company: {job_posting.company}
        Industry: {job_posting.industry}
        
        Candidate Background:
        - Executive Summary: {relevant_content['executive_summary']}
        - Key Skills: {', '.join(relevant_content['skills'][:5])}
        - Top Achievement: {relevant_content['achievements'][0] if relevant_content['achievements'] else 'N/A'}
        
        Tone: {tone.value}
        
        Requirements:
        - 2-3 sentences maximum
        - Reference specific job title and company
        - Highlight most relevant qualification
        - Create immediate interest
        - Match the {tone.value} tone
        
        Generate only the opening paragraph, no additional text.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_opening(job_posting, relevant_content, tone)
    
    def _generate_template_opening(
        self, 
        job_posting: JobPosting, 
        relevant_content: Dict, 
        tone: CoverLetterTone
    ) -> str:
        """Generate template-based opening paragraph"""
        
        if tone == CoverLetterTone.PROFESSIONAL:
            return f"I am writing to express my strong interest in the {job_posting.title} position at {job_posting.company}. With my background in {relevant_content['skills'][0] if relevant_content['skills'] else 'relevant experience'} and proven track record of {relevant_content['achievements'][0][:50] if relevant_content['achievements'] else 'delivering results'}, I am confident I would be a valuable addition to your team."
        
        elif tone == CoverLetterTone.ENTHUSIASTIC:
            return f"I am excited to apply for the {job_posting.title} role at {job_posting.company}! Your company's innovative approach to {job_posting.industry} aligns perfectly with my passion for {relevant_content['skills'][0] if relevant_content['skills'] else 'technology'} and my experience in {relevant_content['achievements'][0][:50] if relevant_content['achievements'] else 'driving growth'}."
        
        else:  # Default professional tone
            return f"I am pleased to submit my application for the {job_posting.title} position at {job_posting.company}. My expertise in {relevant_content['skills'][0] if relevant_content['skills'] else 'relevant areas'} and demonstrated success in {relevant_content['achievements'][0][:50] if relevant_content['achievements'] else 'project delivery'} make me an ideal candidate for this role."
    
    def _generate_body_paragraphs(
        self, 
        job_posting: JobPosting, 
        relevant_content: Dict, 
        tone: CoverLetterTone
    ) -> List[str]:
        """Generate 2-3 body paragraphs highlighting relevant experience"""
        
        paragraphs = []
        
        # Paragraph 1: Most relevant experience
        if relevant_content['experience']:
            exp = relevant_content['experience'][0]
            para1 = f"In my role as {exp.get('title', 'Professional')} at {exp.get('company', 'Previous Company')}, I {exp.get('description', 'delivered significant results')}. This experience directly aligns with your requirements for {job_posting.title}, particularly in {relevant_content['skills'][0] if relevant_content['skills'] else 'key areas'}."
            paragraphs.append(para1)
        
        # Paragraph 2: Skills and achievements
        if relevant_content['skills'] and relevant_content['achievements']:
            para2 = f"My technical expertise includes {', '.join(relevant_content['skills'][:3])}, which I have applied to achieve {relevant_content['achievements'][0]}. I am particularly drawn to {job_posting.company}'s focus on {job_posting.industry} and believe my background in {relevant_content['skills'][0]} would contribute significantly to your team's success."
            paragraphs.append(para2)
        
        # Paragraph 3: Company connection and value proposition
        para3 = f"I am impressed by {job_posting.company}'s commitment to {job_posting.industry} innovation and would welcome the opportunity to contribute to your continued growth. My proven ability to {relevant_content['achievements'][0][:50] if relevant_content['achievements'] else 'deliver results'} and collaborative approach would enable me to make an immediate impact in the {job_posting.title} role."
        paragraphs.append(para3)
        
        return paragraphs
    
    def _generate_closing_paragraph(
        self, 
        job_posting: JobPosting, 
        tone: CoverLetterTone
    ) -> str:
        """Generate professional closing paragraph"""
        
        if tone == CoverLetterTone.ENTHUSIASTIC:
            return f"I would love the opportunity to discuss how my experience and enthusiasm can contribute to {job_posting.company}'s success. Thank you for considering my application, and I look forward to hearing from you soon!"
        
        elif tone == CoverLetterTone.FORMAL:
            return f"I would welcome the opportunity to discuss my qualifications further and learn more about how I can contribute to {job_posting.company}'s objectives. Thank you for your time and consideration."
        
        else:  # Professional default
            return f"I would appreciate the opportunity to discuss how my background and skills align with {job_posting.company}'s needs. Thank you for considering my application, and I look forward to the possibility of contributing to your team."
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from job description"""
        
        # Common technical and professional keywords
        keyword_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms (API, SQL, etc.)
            r'\b\w+(?:\.js|\.py|\.java)\b',  # Programming languages/frameworks
            r'\b(?:management|leadership|strategy|analysis|development|design|implementation)\b',  # Professional skills
        ]
        
        keywords = set()
        for pattern in keyword_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update([match.lower() for match in matches])
        
        # Add common job-specific terms
        common_terms = ['experience', 'skills', 'team', 'project', 'customer', 'business', 'technical']
        for term in common_terms:
            if term.lower() in text.lower():
                keywords.add(term.lower())
        
        return list(keywords)
    
    def _analyze_company_culture(self, description: str) -> List[str]:
        """Analyze company culture from job description"""
        
        culture_indicators = {
            'innovative': ['innovation', 'cutting-edge', 'pioneering', 'breakthrough'],
            'collaborative': ['team', 'collaboration', 'partnership', 'together'],
            'fast-paced': ['fast-paced', 'dynamic', 'agile', 'rapid'],
            'customer-focused': ['customer', 'client', 'user', 'service'],
            'data-driven': ['data', 'analytics', 'metrics', 'insights'],
            'growth-oriented': ['growth', 'scale', 'expansion', 'development']
        }
        
        detected_culture = []
        description_lower = description.lower()
        
        for culture_type, indicators in culture_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                detected_culture.append(culture_type)
        
        return detected_culture
    
    def _identify_focus_areas(self, description: str) -> List[str]:
        """Identify key focus areas from job description"""
        
        focus_areas = {
            'technical': ['development', 'programming', 'coding', 'technical', 'software', 'engineering'],
            'management': ['manage', 'lead', 'oversight', 'coordinate', 'supervise'],
            'strategy': ['strategy', 'planning', 'roadmap', 'vision', 'direction'],
            'customer': ['customer', 'client', 'user', 'stakeholder', 'relationship'],
            'product': ['product', 'feature', 'solution', 'platform', 'system'],
            'operations': ['operations', 'process', 'workflow', 'efficiency', 'optimization']
        }
        
        detected_areas = []
        description_lower = description.lower()
        
        for area, keywords in focus_areas.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_areas.append(area)
        
        return detected_areas
    
    def _calculate_relevance_score(self, experience: Dict, job_analysis: Dict) -> float:
        """Calculate relevance score for experience item"""
        
        score = 0.0
        exp_text = f"{experience.get('title', '')} {experience.get('description', '')}".lower()
        
        # Keyword matching
        for keyword in job_analysis['keywords']:
            if keyword in exp_text:
                score += 1.0
        
        # Focus area matching
        for focus_area in job_analysis['focus_areas']:
            if focus_area in exp_text:
                score += 0.5
        
        return score
    
    def _select_relevant_skills(self, skills: List[str], keywords: List[str]) -> List[str]:
        """Select skills most relevant to job keywords"""
        
        relevant_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in keywords):
                relevant_skills.append(skill)
        
        # If no direct matches, return top skills
        if not relevant_skills:
            relevant_skills = skills[:5]
        
        return relevant_skills[:5]  # Limit to top 5
    
    def _select_relevant_achievements(self, achievements: List[str], job_analysis: Dict) -> List[str]:
        """Select achievements most relevant to job requirements"""
        
        scored_achievements = []
        for achievement in achievements:
            score = 0
            achievement_lower = achievement.lower()
            
            # Score based on keyword presence
            for keyword in job_analysis['keywords']:
                if keyword in achievement_lower:
                    score += 1
            
            # Score based on focus areas
            for focus_area in job_analysis['focus_areas']:
                if focus_area in achievement_lower:
                    score += 0.5
            
            scored_achievements.append((achievement, score))
        
        # Sort by score and return top achievements
        scored_achievements.sort(key=lambda x: x[1], reverse=True)
        return [achievement for achievement, score in scored_achievements[:3]]
    
    def _select_relevant_ai_suggestions(self, ai_suggestions: List[Dict], job_analysis: Dict) -> List[Dict]:
        """Select AI suggestions most relevant to job requirements"""
        
        if not ai_suggestions:
            return []
        
        relevant_suggestions = []
        for suggestion in ai_suggestions:
            suggestion_text = suggestion.get('text', '').lower()
            
            # Check for keyword relevance
            relevance_score = 0
            for keyword in job_analysis['keywords']:
                if keyword in suggestion_text:
                    relevance_score += 1
            
            if relevance_score > 0:
                suggestion['relevance_score'] = relevance_score
                relevant_suggestions.append(suggestion)
        
        # Sort by relevance and return top suggestions
        relevant_suggestions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return relevant_suggestions[:3]
    
    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density in the cover letter"""
        
        text_lower = text.lower()
        total_words = len(text.split())
        
        keyword_density = {}
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            density = (count / total_words) * 100 if total_words > 0 else 0
            keyword_density[keyword] = round(density, 2)
        
        return keyword_density
    
    def _calculate_tone_score(self, text: str, target_tone: CoverLetterTone) -> float:
        """Calculate how well the text matches the target tone"""
        
        tone_indicators = {
            CoverLetterTone.PROFESSIONAL: ['experience', 'expertise', 'qualifications', 'professional'],
            CoverLetterTone.ENTHUSIASTIC: ['excited', 'passionate', 'love', 'thrilled', 'eager'],
            CoverLetterTone.ANALYTICAL: ['analysis', 'data', 'metrics', 'results', 'performance'],
            CoverLetterTone.CONVERSATIONAL: ['I believe', 'I think', 'personally', 'feel'],
            CoverLetterTone.FORMAL: ['pleased', 'respectfully', 'formally', 'consideration']
        }
        
        text_lower = text.lower()
        indicators = tone_indicators.get(target_tone, [])
        
        matches = sum(1 for indicator in indicators if indicator in text_lower)
        total_indicators = len(indicators)
        
        return (matches / total_indicators) if total_indicators > 0 else 0.5
    
    def _calculate_effectiveness_score(
        self, 
        text: str, 
        job_analysis: Dict, 
        relevant_content: Dict
    ) -> float:
        """Calculate overall effectiveness score of the cover letter"""
        
        score = 0.0
        
        # Keyword coverage (30%)
        keyword_matches = sum(1 for keyword in job_analysis['keywords'] if keyword in text.lower())
        keyword_score = min(keyword_matches / len(job_analysis['keywords']), 1.0) if job_analysis['keywords'] else 0
        score += keyword_score * 0.3
        
        # Content relevance (25%)
        content_score = min(len(relevant_content['experience']) / 3, 1.0)
        score += content_score * 0.25
        
        # Length appropriateness (20%)
        word_count = len(text.split())
        if 250 <= word_count <= 400:
            length_score = 1.0
        elif 200 <= word_count < 250 or 400 < word_count <= 500:
            length_score = 0.8
        else:
            length_score = 0.5
        score += length_score * 0.2
        
        # Skills integration (15%)
        skills_mentioned = sum(1 for skill in relevant_content['skills'] if skill.lower() in text.lower())
        skills_score = min(skills_mentioned / len(relevant_content['skills']), 1.0) if relevant_content['skills'] else 0
        score += skills_score * 0.15
        
        # Achievement inclusion (10%)
        achievements_mentioned = sum(1 for achievement in relevant_content['achievements'] if achievement[:20].lower() in text.lower())
        achievement_score = min(achievements_mentioned / len(relevant_content['achievements']), 1.0) if relevant_content['achievements'] else 0
        score += achievement_score * 0.1
        
        return round(score, 2)
    
    def _load_templates(self) -> Dict:
        """Load cover letter templates"""
        
        # Basic template structure - in production, these would be loaded from database
        templates = {
            TemplateType.TECHNOLOGY: {
                'structure': ['opening', 'technical_experience', 'innovation_focus', 'closing'],
                'tone_preference': CoverLetterTone.PROFESSIONAL,
                'max_length': 350
            },
            TemplateType.HEALTHCARE: {
                'structure': ['opening', 'clinical_experience', 'patient_focus', 'closing'],
                'tone_preference': CoverLetterTone.PROFESSIONAL,
                'max_length': 400
            },
            TemplateType.STARTUP: {
                'structure': ['opening', 'entrepreneurial_experience', 'growth_mindset', 'closing'],
                'tone_preference': CoverLetterTone.ENTHUSIASTIC,
                'max_length': 300
            }
        }
        
        return templates
    
    def _load_tone_configurations(self) -> Dict:
        """Load tone configuration settings"""
        
        configurations = {
            CoverLetterTone.PROFESSIONAL: {
                'vocabulary': 'formal',
                'sentence_structure': 'complex',
                'enthusiasm_level': 'moderate'
            },
            CoverLetterTone.ENTHUSIASTIC: {
                'vocabulary': 'energetic',
                'sentence_structure': 'varied',
                'enthusiasm_level': 'high'
            },
            CoverLetterTone.ANALYTICAL: {
                'vocabulary': 'data-focused',
                'sentence_structure': 'precise',
                'enthusiasm_level': 'measured'
            }
        }
        
        return configurations

# Utility functions for integration
def create_job_posting_from_description(
    title: str, 
    company: str, 
    description: str,
    industry: str = "",
    role_type: str = ""
) -> JobPosting:
    """Create JobPosting object from basic job information"""
    
    # Extract requirements from description (basic parsing)
    requirements = []
    preferred = []
    
    # Look for requirement sections
    if "requirements:" in description.lower():
        req_section = description.lower().split("requirements:")[1]
        if "preferred" in req_section:
            req_section = req_section.split("preferred")[0]
        requirements = [req.strip() for req in req_section.split('\n') if req.strip()]
    
    return JobPosting(
        title=title,
        company=company,
        description=description,
        requirements=requirements,
        preferred_qualifications=preferred,
        industry=industry,
        role_type=role_type
    )

def create_resume_data_from_resume(resume_output: Dict) -> ResumeData:
    """Create ResumeData object from Resume module output"""
    
    return ResumeData(
        executive_summary=resume_output.get('executive_summary', ''),
        selected_experience=resume_output.get('selected_experience', []),
        selected_skills=resume_output.get('selected_skills', []),
        selected_achievements=resume_output.get('selected_achievements', []),
        ai_suggestions=resume_output.get('ai_suggestions', []),
        optimization_score=resume_output.get('optimization_score', 0.0)
    )

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    cover_letter = CoverLetter()
    
    # Sample job posting
    job = JobPosting(
        title="Senior Software Engineer",
        company="TechCorp",
        description="We are seeking a Senior Software Engineer with experience in Python, React, and cloud technologies. The ideal candidate will have 5+ years of experience building scalable web applications.",
        requirements=["5+ years Python experience", "React expertise", "Cloud platforms"],
        preferred_qualifications=["AWS certification", "Team leadership"],
        industry="Technology",
        role_type="Engineering"
    )
    
    # Sample resume data
    resume = ResumeData(
        executive_summary="Experienced software engineer with 7 years of Python and React development",
        selected_experience=[
            {"title": "Senior Developer", "company": "StartupCo", "description": "Led development of React applications using Python backend"}
        ],
        selected_skills=["Python", "React", "AWS", "Docker"],
        selected_achievements=["Increased application performance by 40%", "Led team of 5 developers"],
        ai_suggestions=[{"text": "Implemented microservices architecture", "relevance_score": 0.9}],
        optimization_score=0.85
    )
    
    # Generate cover letter
    result = cover_letter.generate_cover_letter(
        job_posting=job,
        resume_data=resume,
        template_type=TemplateType.TECHNOLOGY,
        tone=CoverLetterTone.PROFESSIONAL
    )
    
    print("Generated Cover Letter:")
    print("=" * 50)
    print(f"Opening: {result.opening_paragraph}")
    print()
    for i, paragraph in enumerate(result.body_paragraphs, 1):
        print(f"Body {i}: {paragraph}")
        print()
    print(f"Closing: {result.closing_paragraph}")
    print()
    print(f"Word Count: {result.word_count}")
    print(f"Effectiveness Score: {result.effectiveness_score}")
