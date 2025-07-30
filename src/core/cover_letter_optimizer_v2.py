#!/usr/bin/env python3
"""
Cover Letter Optimizer V2 - Holistic Narrative Integration

Revolutionary AI-powered narrative engine that creates authentic, deeply personalized 
cover letters by integrating the candidate's holistic personal story with comprehensive 
company intelligence and culture analysis.

Key Features:
- AI Career Coach narrative integration (dreams, passions, authentic self)
- Deep company culture analysis (Glassdoor, employee sentiment, culture assessments)
- Authentic storytelling that connects personal narrative to company mission
- Holistic positioning beyond skills matching to cultural fit
- Dynamic tone adaptation based on company culture insights
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import openai
import os
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Install with: pip install openai")
    openai = None

@dataclass
class PersonalNarrative:
    """AI Career Coach narrative data structure"""
    dreams_and_aspirations: List[str]
    core_passions: List[str]
    personal_values: List[str]
    projects_proud_of: List[str]
    authentic_self_description: str
    career_motivations: List[str]
    work_style_preferences: List[str]
    ideal_company_culture: str
    personal_mission_statement: str

@dataclass
class CompanyCultureInsights:
    """Comprehensive company culture analysis"""
    glassdoor_rating: float
    glassdoor_pros: List[str]
    glassdoor_cons: List[str]
    employee_sentiment: str  # positive, neutral, negative
    culture_keywords: List[str]
    work_life_balance_score: float
    leadership_rating: float
    career_opportunities_rating: float
    company_values: List[str]
    culture_assessment: str  # collaborative, competitive, innovative, traditional, etc.
    employee_reviews_summary: str
    diversity_inclusion_score: float

@dataclass
class CompanyMissionAlignment:
    """Analysis of company mission and candidate alignment"""
    company_mission: str
    company_values: List[str]
    social_impact_focus: List[str]
    innovation_areas: List[str]
    alignment_score: float
    connection_points: List[str]
    why_candidate_drawn: str

@dataclass
class JobPosting:
    """Enhanced job posting with culture context"""
    title: str
    company: str
    description: str
    requirements: List[str]
    preferred_qualifications: List[str]
    company_culture: str = ""
    industry: str = ""
    role_type: str = ""
    team_culture: str = ""
    growth_opportunities: List[str] = None

@dataclass
class ResumeData:
    """Resume data from Resume Optimizer"""
    optimized_bullets: List[str]
    key_skills: List[str]
    achievements: List[str]
    experience_summary: str
    industry_experience: List[str]
    technical_skills: List[str]
    leadership_experience: List[str]

class NarrativeTone(Enum):
    """Narrative-driven tone options"""
    PASSIONATE_MISSION_DRIVEN = "passionate_mission_driven"
    AUTHENTIC_COLLABORATIVE = "authentic_collaborative"
    INNOVATIVE_FORWARD_THINKING = "innovative_forward_thinking"
    RESULTS_ORIENTED_CULTURAL_FIT = "results_oriented_cultural_fit"
    GROWTH_MINDED_ADAPTIVE = "growth_minded_adaptive"

class CoverLetterTemplate(Enum):
    """Template options based on company culture"""
    MISSION_DRIVEN_NONPROFIT = "mission_driven_nonprofit"
    INNOVATIVE_TECH_STARTUP = "innovative_tech_startup"
    COLLABORATIVE_HEALTHCARE = "collaborative_healthcare"
    RESULTS_FOCUSED_ENTERPRISE = "results_focused_enterprise"
    CREATIVE_AGENCY = "creative_agency"
    TRADITIONAL_CORPORATE = "traditional_corporate"

@dataclass
class NarrativeCoverLetter:
    """Generated cover letter with narrative insights"""
    content: str
    opening_hook: str
    personal_connection: str
    experience_narrative: str
    company_alignment: str
    closing_call_to_action: str
    authenticity_score: float
    cultural_fit_score: float
    narrative_strength: float
    word_count: int
    tone: NarrativeTone
    template: CoverLetterTemplate

class HolisticCoverLetterOptimizer:
    """
    Advanced Cover Letter Optimizer with AI Career Coach integration
    and deep company culture analysis
    """
    
    def __init__(self):
        """Initialize the optimizer with AI integrations"""
        self.client = None
        if openai:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        # Mock integrations for demo - replace with actual implementations
        self.ai_career_coach = None  # AICareerCoach()
        self.company_enrichment = None  # CompanyEnrichmentEngine()
    
    def generate_narrative_cover_letter(
        self,
        job_posting: JobPosting,
        resume_data: ResumeData,
        personal_narrative: PersonalNarrative,
        company_culture: CompanyCultureInsights,
        company_mission: CompanyMissionAlignment,
        template: CoverLetterTemplate = None,
        tone: NarrativeTone = None
    ) -> NarrativeCoverLetter:
        """
        Generate a holistic, narrative-driven cover letter
        """
        
        # Auto-select template and tone based on company culture
        if not template:
            template = self._select_optimal_template(company_culture, job_posting)
        if not tone:
            tone = self._select_optimal_tone(company_culture, personal_narrative)
        
        # Generate narrative components
        opening_hook = self._generate_opening_hook(
            job_posting, personal_narrative, company_mission
        )
        
        personal_connection = self._generate_personal_connection(
            personal_narrative, company_culture, company_mission
        )
        
        experience_narrative = self._generate_experience_narrative(
            resume_data, job_posting, personal_narrative
        )
        
        company_alignment = self._generate_company_alignment(
            personal_narrative, company_culture, company_mission, job_posting
        )
        
        closing_call_to_action = self._generate_closing(
            job_posting, personal_narrative, company_culture, tone
        )
        
        # Combine into full cover letter
        full_content = self._combine_narrative_sections(
            opening_hook, personal_connection, experience_narrative,
            company_alignment, closing_call_to_action, template
        )
        
        # Calculate narrative scores
        authenticity_score = self._calculate_authenticity_score(
            full_content, personal_narrative
        )
        cultural_fit_score = self._calculate_cultural_fit_score(
            full_content, company_culture
        )
        narrative_strength = self._calculate_narrative_strength(
            full_content, personal_narrative, company_mission
        )
        
        return NarrativeCoverLetter(
            content=full_content,
            opening_hook=opening_hook,
            personal_connection=personal_connection,
            experience_narrative=experience_narrative,
            company_alignment=company_alignment,
            closing_call_to_action=closing_call_to_action,
            authenticity_score=authenticity_score,
            cultural_fit_score=cultural_fit_score,
            narrative_strength=narrative_strength,
            word_count=len(full_content.split()),
            tone=tone,
            template=template
        )
    
    def _select_optimal_template(
        self, 
        company_culture: CompanyCultureInsights, 
        job_posting: JobPosting
    ) -> CoverLetterTemplate:
        """Select template based on company culture analysis"""
        
        culture_keywords = [kw.lower() for kw in company_culture.culture_keywords]
        
        if any(kw in culture_keywords for kw in ['mission', 'impact', 'social', 'nonprofit']):
            return CoverLetterTemplate.MISSION_DRIVEN_NONPROFIT
        elif any(kw in culture_keywords for kw in ['startup', 'innovation', 'disrupt', 'agile']):
            return CoverLetterTemplate.INNOVATIVE_TECH_STARTUP
        elif any(kw in culture_keywords for kw in ['healthcare', 'patient', 'care', 'medical']):
            return CoverLetterTemplate.COLLABORATIVE_HEALTHCARE
        elif any(kw in culture_keywords for kw in ['creative', 'design', 'agency', 'brand']):
            return CoverLetterTemplate.CREATIVE_AGENCY
        elif company_culture.glassdoor_rating > 4.0 and 'collaborative' in culture_keywords:
            return CoverLetterTemplate.COLLABORATIVE_HEALTHCARE
        else:
            return CoverLetterTemplate.RESULTS_FOCUSED_ENTERPRISE
    
    def _select_optimal_tone(
        self, 
        company_culture: CompanyCultureInsights, 
        personal_narrative: PersonalNarrative
    ) -> NarrativeTone:
        """Select tone based on company culture and personal narrative"""
        
        # Match personal values with company culture
        if any('mission' in value.lower() for value in personal_narrative.personal_values):
            return NarrativeTone.PASSIONATE_MISSION_DRIVEN
        elif company_culture.culture_assessment == 'innovative':
            return NarrativeTone.INNOVATIVE_FORWARD_THINKING
        elif company_culture.culture_assessment == 'collaborative':
            return NarrativeTone.AUTHENTIC_COLLABORATIVE
        elif 'growth' in personal_narrative.ideal_company_culture.lower():
            return NarrativeTone.GROWTH_MINDED_ADAPTIVE
        else:
            return NarrativeTone.RESULTS_ORIENTED_CULTURAL_FIT
    
    def _generate_opening_hook(
        self,
        job_posting: JobPosting,
        personal_narrative: PersonalNarrative,
        company_mission: CompanyMissionAlignment
    ) -> str:
        """Generate compelling opening that connects personal passion to company mission"""
        
        if not self.client:
            return f"I am excited to apply for the {job_posting.title} position at {job_posting.company}, as it perfectly aligns with my passion for {personal_narrative.core_passions[0] if personal_narrative.core_passions else 'innovation'} and {job_posting.company}'s mission to {company_mission.company_mission[:100]}..."
        
        prompt = f"""
        Create a compelling opening paragraph for a cover letter that authentically connects:
        
        Personal Passion: {personal_narrative.core_passions[:3]}
        Personal Values: {personal_narrative.personal_values[:3]}
        Company Mission: {company_mission.company_mission}
        Job Title: {job_posting.title}
        Company: {job_posting.company}
        Why Drawn to Company: {company_mission.why_candidate_drawn}
        
        Make it authentic, passionate, and demonstrate genuine interest beyond just the role.
        Keep it to 2-3 sentences maximum.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"I am thrilled to apply for the {job_posting.title} position at {job_posting.company}, as it represents the perfect intersection of my passion for {personal_narrative.core_passions[0] if personal_narrative.core_passions else 'innovation'} and {job_posting.company}'s commitment to {company_mission.company_mission[:50]}..."
    
    def _generate_personal_connection(
        self,
        personal_narrative: PersonalNarrative,
        company_culture: CompanyCultureInsights,
        company_mission: CompanyMissionAlignment
    ) -> str:
        """Generate paragraph connecting personal story to company culture"""
        
        if not self.client:
            return f"What draws me to {company_mission.company_mission[:50]}... is how it aligns with my personal values of {', '.join(personal_narrative.personal_values[:2])}. {personal_narrative.authentic_self_description[:100]}..."
        
        prompt = f"""
        Write a personal connection paragraph that authentically weaves together:
        
        Personal Values: {personal_narrative.personal_values}
        Personal Mission: {personal_narrative.personal_mission_statement}
        Authentic Self: {personal_narrative.authentic_self_description}
        Projects Proud Of: {personal_narrative.projects_proud_of[:2]}
        
        Company Values: {company_mission.company_values}
        Company Culture: {company_culture.culture_keywords[:5]}
        Employee Sentiment: {company_culture.employee_reviews_summary[:200]}
        
        Show genuine alignment and authentic interest. Be specific about why this company resonates.
        Keep to 3-4 sentences.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"What particularly resonates with me about {company_mission.company_mission[:50]}... is how it mirrors my own values of {', '.join(personal_narrative.personal_values[:2])}. {personal_narrative.authentic_self_description[:100]}..."
    
    def _generate_experience_narrative(
        self,
        resume_data: ResumeData,
        job_posting: JobPosting,
        personal_narrative: PersonalNarrative
    ) -> str:
        """Generate experience section that tells a story, not just lists achievements"""
        
        if not self.client:
            return f"In my experience as {resume_data.experience_summary[:50]}..., I have consistently {resume_data.achievements[0] if resume_data.achievements else 'delivered results'} while staying true to my passion for {personal_narrative.core_passions[0] if personal_narrative.core_passions else 'innovation'}."
        
        prompt = f"""
        Create a compelling experience narrative that weaves together:
        
        Key Achievements: {resume_data.achievements[:3]}
        Optimized Bullets: {resume_data.optimized_bullets[:3]}
        Leadership Experience: {resume_data.leadership_experience[:2]}
        
        Personal Motivations: {personal_narrative.career_motivations[:2]}
        Core Passions: {personal_narrative.core_passions[:2]}
        
        Job Requirements: {job_posting.requirements[:3]}
        
        Tell a story of growth and passion, not just accomplishments. Show how personal motivations 
        drive professional excellence. Keep to 4-5 sentences.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Throughout my career, my passion for {personal_narrative.core_passions[0] if personal_narrative.core_passions else 'innovation'} has driven me to {resume_data.achievements[0] if resume_data.achievements else 'achieve exceptional results'}. {resume_data.experience_summary[:100]}..."
    
    def _generate_company_alignment(
        self,
        personal_narrative: PersonalNarrative,
        company_culture: CompanyCultureInsights,
        company_mission: CompanyMissionAlignment,
        job_posting: JobPosting
    ) -> str:
        """Generate section showing deep understanding of company and authentic fit"""
        
        if not self.client:
            return f"I am particularly drawn to {job_posting.company}'s {company_culture.culture_keywords[0] if company_culture.culture_keywords else 'innovative'} culture and commitment to {company_mission.company_values[0] if company_mission.company_values else 'excellence'}."
        
        prompt = f"""
        Write a company alignment paragraph that demonstrates deep understanding:
        
        Company Culture Insights:
        - Glassdoor Pros: {company_culture.glassdoor_pros[:3]}
        - Culture Keywords: {company_culture.culture_keywords[:5]}
        - Employee Sentiment: {company_culture.employee_reviews_summary[:150]}
        
        Company Mission: {company_mission.company_mission}
        Connection Points: {company_mission.connection_points[:3]}
        
        Personal Alignment:
        - Ideal Culture: {personal_narrative.ideal_company_culture}
        - Work Style: {personal_narrative.work_style_preferences[:2]}
        
        Show you've done deep research and understand what makes this company special.
        Demonstrate authentic cultural fit. Keep to 3-4 sentences.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"What excites me most about {job_posting.company} is {company_culture.glassdoor_pros[0] if company_culture.glassdoor_pros else 'the innovative culture'} and the company's commitment to {company_mission.company_values[0] if company_mission.company_values else 'excellence'}, which aligns perfectly with my {personal_narrative.ideal_company_culture[:50]}..."
    
    def _generate_closing(
        self,
        job_posting: JobPosting,
        personal_narrative: PersonalNarrative,
        company_culture: CompanyCultureInsights,
        tone: NarrativeTone
    ) -> str:
        """Generate closing that reinforces authentic interest and cultural fit"""
        
        if tone == NarrativeTone.PASSIONATE_MISSION_DRIVEN:
            return f"I am genuinely excited about the opportunity to contribute to {job_posting.company}'s mission and would welcome the chance to discuss how my passion for {personal_narrative.core_passions[0] if personal_narrative.core_passions else 'innovation'} and proven experience can drive meaningful impact in the {job_posting.title} role."
        elif tone == NarrativeTone.AUTHENTIC_COLLABORATIVE:
            return f"I would love the opportunity to bring my collaborative approach and authentic passion for {personal_narrative.core_passions[0] if personal_narrative.core_passions else 'teamwork'} to {job_posting.company}'s {company_culture.culture_keywords[0] if company_culture.culture_keywords else 'innovative'} team."
        else:
            return f"I am excited about the possibility of contributing to {job_posting.company}'s continued success and would appreciate the opportunity to discuss how my background and genuine enthusiasm for {company_culture.culture_keywords[0] if company_culture.culture_keywords else 'innovation'} align with your team's goals."
    
    def _combine_narrative_sections(
        self,
        opening: str,
        connection: str,
        experience: str,
        alignment: str,
        closing: str,
        template: CoverLetterTemplate
    ) -> str:
        """Combine sections into cohesive narrative cover letter"""
        
        sections = [opening, connection, experience, alignment, closing]
        return "\n\n".join(section for section in sections if section.strip())
    
    def _calculate_authenticity_score(
        self, 
        content: str, 
        personal_narrative: PersonalNarrative
    ) -> float:
        """Calculate how authentic the cover letter feels"""
        
        score = 0.0
        content_lower = content.lower()
        
        # Check for personal passion mentions
        for passion in personal_narrative.core_passions:
            if passion.lower() in content_lower:
                score += 0.2
        
        # Check for personal values
        for value in personal_narrative.personal_values:
            if value.lower() in content_lower:
                score += 0.15
        
        # Check for authentic language patterns
        authentic_phrases = ['passionate about', 'excited about', 'drawn to', 'resonates with', 'aligns with']
        for phrase in authentic_phrases:
            if phrase in content_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_cultural_fit_score(
        self, 
        content: str, 
        company_culture: CompanyCultureInsights
    ) -> float:
        """Calculate cultural fit demonstration"""
        
        score = 0.0
        content_lower = content.lower()
        
        # Check for culture keyword mentions
        for keyword in company_culture.culture_keywords:
            if keyword.lower() in content_lower:
                score += 0.15
        
        # Check for values alignment
        for value in company_culture.company_values:
            if value.lower() in content_lower:
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_narrative_strength(
        self, 
        content: str, 
        personal_narrative: PersonalNarrative,
        company_mission: CompanyMissionAlignment
    ) -> float:
        """Calculate overall narrative strength and storytelling quality"""
        
        score = 0.0
        
        # Story elements present
        story_elements = ['experience', 'passion', 'mission', 'values', 'impact']
        content_lower = content.lower()
        
        for element in story_elements:
            if element in content_lower:
                score += 0.15
        
        # Connection strength
        if company_mission.alignment_score > 0.8:
            score += 0.25
        
        return min(score, 1.0)

# Example usage and demo functions
def create_sample_personal_narrative() -> PersonalNarrative:
    """Create sample personal narrative for Allen Walker"""
    return PersonalNarrative(
        dreams_and_aspirations=[
            "Transform healthcare through technology innovation",
            "Build systems that improve patient outcomes at scale",
            "Lead cross-functional teams in meaningful mission-driven work"
        ],
        core_passions=[
            "Healthcare technology innovation",
            "Cross-functional team leadership",
            "Process optimization and efficiency",
            "AI/ML applications in healthcare"
        ],
        personal_values=[
            "Patient-centered care",
            "Continuous learning and growth",
            "Collaborative teamwork",
            "Data-driven decision making",
            "Authentic leadership"
        ],
        projects_proud_of=[
            "Led Epic EHR implementation across 15+ healthcare organizations",
            "Built cross-functional teams of 50+ clinical and technical professionals",
            "Developed AI-powered job search automation platform",
            "Managed $2M+ healthcare technology initiatives"
        ],
        authentic_self_description="I am a healthcare technology leader who thrives at the intersection of innovation and patient care. My approach combines analytical rigor with genuine empathy, always asking 'how does this improve patient outcomes?' I believe the best solutions emerge from diverse, collaborative teams working toward a shared mission.",
        career_motivations=[
            "Making meaningful impact on patient care through technology",
            "Building and leading high-performing, diverse teams",
            "Solving complex problems at the intersection of healthcare and technology",
            "Continuous learning and professional growth"
        ],
        work_style_preferences=[
            "Collaborative, cross-functional team environments",
            "Data-driven decision making with room for innovation",
            "Clear mission alignment and purpose-driven work",
            "Continuous learning and professional development opportunities"
        ],
        ideal_company_culture="A mission-driven organization that values innovation, collaboration, and continuous learning. Where diverse perspectives are celebrated, patient outcomes drive decisions, and team members are empowered to make meaningful impact.",
        personal_mission_statement="To leverage technology and collaborative leadership to transform healthcare delivery, improving patient outcomes while building inclusive, high-performing teams that drive sustainable innovation."
    )

def create_sample_company_culture() -> CompanyCultureInsights:
    """Create sample company culture insights"""
    return CompanyCultureInsights(
        glassdoor_rating=4.2,
        glassdoor_pros=[
            "Mission-driven work with real patient impact",
            "Collaborative, supportive team environment",
            "Strong leadership and clear communication",
            "Excellent benefits and work-life balance",
            "Opportunities for professional growth"
        ],
        glassdoor_cons=[
            "Fast-paced environment can be demanding",
            "Rapid growth sometimes creates process gaps",
            "Limited remote work flexibility in some roles"
        ],
        employee_sentiment="positive",
        culture_keywords=[
            "mission-driven", "collaborative", "innovative", "patient-focused",
            "growth-oriented", "inclusive", "data-driven", "agile"
        ],
        work_life_balance_score=4.1,
        leadership_rating=4.3,
        career_opportunities_rating=4.0,
        company_values=[
            "Patient-centered care",
            "Innovation and continuous improvement",
            "Collaboration and teamwork",
            "Integrity and transparency",
            "Diversity and inclusion"
        ],
        culture_assessment="collaborative",
        employee_reviews_summary="Employees consistently praise the mission-driven culture and collaborative environment. Leadership is viewed as supportive and transparent. The company is seen as genuinely committed to improving patient outcomes through technology innovation.",
        diversity_inclusion_score=4.0
    )

def create_sample_company_mission() -> CompanyMissionAlignment:
    """Create sample company mission alignment"""
    return CompanyMissionAlignment(
        company_mission="To transform healthcare delivery through innovative AI and data analytics solutions that improve patient outcomes, reduce costs, and empower healthcare providers with actionable insights.",
        company_values=[
            "Patient-centered innovation",
            "Data-driven healthcare solutions",
            "Collaborative partnerships",
            "Continuous learning and improvement",
            "Ethical AI development"
        ],
        social_impact_focus=[
            "Improving patient outcomes through technology",
            "Reducing healthcare disparities",
            "Supporting healthcare provider efficiency",
            "Advancing medical research through data"
        ],
        innovation_areas=[
            "AI/ML for clinical decision support",
            "Predictive analytics for population health",
            "Healthcare data interoperability",
            "Patient engagement platforms"
        ],
        alignment_score=0.92,
        connection_points=[
            "Healthcare technology innovation passion",
            "Patient-centered care values alignment",
            "AI/ML expertise and interest",
            "Cross-functional team leadership experience",
            "Data-driven approach to problem solving"
        ],
        why_candidate_drawn="The intersection of AI innovation and patient care represents the perfect convergence of my technical background, healthcare experience, and personal mission to improve patient outcomes through technology. The company's commitment to ethical AI development and collaborative approach aligns perfectly with my values and leadership style."
    )

if __name__ == "__main__":
    # Demo the enhanced Cover Letter Optimizer
    optimizer = HolisticCoverLetterOptimizer()
    
    # Sample data
    job_posting = JobPosting(
        title="AI Platform Manager",
        company="HealthTech Innovations",
        description="Lead AI/ML platform development for healthcare applications...",
        requirements=["5+ years AI/ML experience", "Healthcare domain knowledge", "Team leadership"],
        preferred_qualifications=["Epic experience", "Python/ML frameworks", "Agile methodology"],
        industry="Healthcare Technology",
        role_type="Management"
    )
    
    resume_data = ResumeData(
        optimized_bullets=[
            "Led Epic EHR implementation for 15+ healthcare organizations",
            "Built cross-functional teams of 50+ clinical and technical professionals",
            "Managed AI/ML initiatives with $2M+ budget and measurable patient impact"
        ],
        key_skills=["AI/ML Platform Management", "Healthcare Technology", "Cross-functional Leadership"],
        achievements=[
            "Delivered 99.9% uptime for critical healthcare systems",
            "Reduced patient wait times by 30% through process optimization",
            "Led teams that improved clinical workflow efficiency by 40%"
        ],
        experience_summary="Healthcare Technology Program Manager with 15+ years experience",
        industry_experience=["Healthcare", "Technology", "AI/ML"],
        technical_skills=["Python", "Machine Learning", "Epic Systems", "Data Analytics"],
        leadership_experience=["Cross-functional team leadership", "Program management", "Stakeholder management"]
    )
    
    personal_narrative = create_sample_personal_narrative()
    company_culture = create_sample_company_culture()
    company_mission = create_sample_company_mission()
    
    # Generate narrative cover letter
    cover_letter = optimizer.generate_narrative_cover_letter(
        job_posting=job_posting,
        resume_data=resume_data,
        personal_narrative=personal_narrative,
        company_culture=company_culture,
        company_mission=company_mission
    )
    
    print("🎯 Holistic Cover Letter Optimizer - Narrative Integration Demo")
    print("=" * 70)
    print(f"📄 Generated Cover Letter (Template: {cover_letter.template.value})")
    print(f"🎭 Tone: {cover_letter.tone.value}")
    print(f"📊 Authenticity Score: {cover_letter.authenticity_score:.1%}")
    print(f"🤝 Cultural Fit Score: {cover_letter.cultural_fit_score:.1%}")
    print(f"📖 Narrative Strength: {cover_letter.narrative_strength:.1%}")
    print(f"📝 Word Count: {cover_letter.word_count}")
    print("-" * 70)
    print(cover_letter.content)
    print("=" * 70)
    print("✨ Holistic Cover Letter Optimizer Demo Complete!")
