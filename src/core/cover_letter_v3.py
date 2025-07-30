#!/usr/bin/env python3
"""
Cover Letter Module v3 - Constraint-Optimized AI Generation

Generates AI-powered cover letters with strict formatting constraints:
- Maximum 29 lines
- Under 1,300 characters
- Inline editable sections
- Real-time alignment scoring

Key Features:
- Company data integration
- Resume data analysis
- Career coaching insights
- Constraint optimization
- Alignment scoring system
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
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
class CoverLetterConstraints:
    """Cover letter formatting constraints"""
    max_lines: int = 29
    max_characters: int = 1300
    min_characters: int = 800
    sections: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.sections is None:
            self.sections = {
                'opening_hook': {'max_lines': 3, 'max_chars': 200},
                'value_proposition': {'max_lines': 10, 'max_chars': 500},
                'company_connection': {'max_lines': 8, 'max_chars': 400},
                'future_impact': {'max_lines': 6, 'max_chars': 250},
                'professional_close': {'max_lines': 4, 'max_chars': 150}
            }

@dataclass
class AlignmentScore:
    """Cover letter alignment scoring"""
    overall: float
    job_alignment: float
    culture_alignment: float
    breakdown: Dict[str, float]
    recommendations: List[str]

@dataclass
class CoverLetterSection:
    """Individual cover letter section"""
    name: str
    content: str
    line_count: int
    char_count: int
    score: float
    editable: bool = True

@dataclass
class CoverLetterOutput:
    """Complete cover letter with metadata"""
    sections: List[CoverLetterSection]
    total_lines: int
    total_characters: int
    alignment_score: AlignmentScore
    meets_constraints: bool
    generation_timestamp: str

class CoverLetterAI:
    """AI engine for cover letter generation and optimization"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the Cover Letter AI engine"""
        self.openai_client = None
        if openai_api_key and openai:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        self.constraints = CoverLetterConstraints()
        
    def generate_cover_letter(
        self,
        job_data: Dict,
        company_data: Dict,
        resume_data: Dict,
        career_coaching_data: Dict
    ) -> CoverLetterOutput:
        """
        Generate a complete cover letter with constraints and scoring
        
        Args:
            job_data: Job posting and requirements
            company_data: Company insights and culture data
            resume_data: Resume highlights and achievements
            career_coaching_data: Personal narrative and coaching insights
            
        Returns:
            CoverLetterOutput: Complete cover letter with metadata
        """
        
        # Phase 1: Analyze all input data
        analysis = self._analyze_inputs(job_data, company_data, resume_data, career_coaching_data)
        
        # Phase 2: Generate content sections
        sections = self._generate_sections(analysis)
        
        # Phase 3: Optimize for constraints
        optimized_sections = self._optimize_for_constraints(sections)
        
        # Phase 4: Calculate alignment scores
        alignment_score = self._calculate_alignment_score(optimized_sections, job_data, company_data)
        
        # Phase 5: Create final output
        return self._create_output(optimized_sections, alignment_score)
    
    def _analyze_inputs(self, job_data: Dict, company_data: Dict, resume_data: Dict, career_coaching_data: Dict) -> Dict:
        """Analyze all input data for content generation"""
        
        analysis = {
            'job_insights': self._analyze_job_data(job_data),
            'company_insights': self._analyze_company_data(company_data),
            'resume_highlights': self._extract_resume_highlights(resume_data),
            'personal_narrative': self._extract_personal_narrative(career_coaching_data)
        }
        
        return analysis
    
    def _analyze_job_data(self, job_data: Dict) -> Dict:
        """Extract key insights from job posting"""
        
        description = job_data.get('description', '')
        requirements = job_data.get('requirements', [])
        
        # Extract keywords and key requirements
        keywords = self._extract_keywords(description)
        key_skills = self._identify_key_skills(requirements)
        role_focus = self._identify_role_focus(description)
        
        return {
            'keywords': keywords,
            'key_skills': key_skills,
            'role_focus': role_focus,
            'seniority_level': job_data.get('seniority_level', 'mid'),
            'industry': job_data.get('industry', '')
        }
    
    def _analyze_company_data(self, company_data: Dict) -> Dict:
        """Extract company culture and mission insights"""
        
        return {
            'mission': company_data.get('mission', ''),
            'values': company_data.get('values', []),
            'culture_keywords': company_data.get('culture_keywords', []),
            'industry_position': company_data.get('industry_position', ''),
            'recent_news': company_data.get('recent_news', []),
            'employee_sentiment': company_data.get('employee_sentiment', {})
        }
    
    def _extract_resume_highlights(self, resume_data: Dict) -> Dict:
        """Extract most relevant resume content"""
        
        return {
            'top_achievements': resume_data.get('selected_achievements', [])[:3],
            'relevant_experience': resume_data.get('selected_experience', [])[:2],
            'key_skills': resume_data.get('selected_skills', [])[:5],
            'executive_summary': resume_data.get('executive_summary', ''),
            'quantified_results': self._extract_quantified_results(resume_data)
        }
    
    def _extract_personal_narrative(self, career_coaching_data: Dict) -> Dict:
        """Extract personal story and motivations"""
        
        return {
            'career_aspirations': career_coaching_data.get('aspirations', ''),
            'core_values': career_coaching_data.get('values', []),
            'passion_areas': career_coaching_data.get('passions', []),
            'authentic_story': career_coaching_data.get('personal_story', ''),
            'growth_mindset': career_coaching_data.get('growth_areas', [])
        }
    
    def _generate_sections(self, analysis: Dict) -> Dict[str, str]:
        """Generate content for each cover letter section"""
        
        sections = {}
        
        # Generate each section using AI
        sections['opening_hook'] = self._generate_opening_hook(analysis)
        sections['value_proposition'] = self._generate_value_proposition(analysis)
        sections['company_connection'] = self._generate_company_connection(analysis)
        sections['future_impact'] = self._generate_future_impact(analysis)
        sections['professional_close'] = self._generate_professional_close(analysis)
        
        return sections
    
    def _generate_opening_hook(self, analysis: Dict) -> str:
        """Generate compelling opening hook (2-3 lines, ~150-200 chars)"""
        
        if not self.openai_client:
            return self._generate_template_opening(analysis)
        
        prompt = f"""
        Create a compelling 2-3 line opening hook for a cover letter (150-200 characters max).
        
        Job Focus: {analysis['job_insights']['role_focus']}
        Company Mission: {analysis['company_insights']['mission']}
        Personal Passion: {analysis['personal_narrative']['passion_areas']}
        
        Requirements:
        - Hook the reader immediately
        - Show genuine interest in the company
        - Connect personal passion to role
        - 2-3 lines maximum
        - 150-200 characters total
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_opening(analysis)
    
    def _generate_value_proposition(self, analysis: Dict) -> str:
        """Generate value proposition section (8-10 lines, ~400-500 chars)"""
        
        if not self.openai_client:
            return self._generate_template_value_prop(analysis)
        
        achievements = analysis['resume_highlights']['top_achievements']
        skills = analysis['resume_highlights']['key_skills']
        job_skills = analysis['job_insights']['key_skills']
        
        prompt = f"""
        Create a value proposition section for a cover letter (8-10 lines, 400-500 characters max).
        
        Top Achievements: {achievements}
        Relevant Skills: {skills}
        Job Requirements: {job_skills}
        
        Requirements:
        - Highlight 2-3 key achievements with quantified results
        - Show direct skill alignment with job requirements
        - Use active voice and strong action verbs
        - 8-10 lines maximum
        - 400-500 characters total
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_value_prop(analysis)
    
    def _generate_company_connection(self, analysis: Dict) -> str:
        """Generate company connection section (6-8 lines, ~300-400 chars)"""
        
        if not self.openai_client:
            return self._generate_template_company_connection(analysis)
        
        mission = analysis['company_insights']['mission']
        values = analysis['company_insights']['values']
        personal_values = analysis['personal_narrative']['core_values']
        
        prompt = f"""
        Create a company connection section for a cover letter (6-8 lines, 300-400 characters max).
        
        Company Mission: {mission}
        Company Values: {values}
        Personal Values: {personal_values}
        
        Requirements:
        - Show genuine interest in this specific company
        - Connect personal values to company values
        - Demonstrate company knowledge
        - 6-8 lines maximum
        - 300-400 characters total
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_company_connection(analysis)
    
    def _generate_future_impact(self, analysis: Dict) -> str:
        """Generate future impact section (4-6 lines, ~200-250 chars)"""
        
        if not self.openai_client:
            return self._generate_template_future_impact(analysis)
        
        role_focus = analysis['job_insights']['role_focus']
        growth_areas = analysis['personal_narrative']['growth_mindset']
        
        prompt = f"""
        Create a future impact section for a cover letter (4-6 lines, 200-250 characters max).
        
        Role Focus: {role_focus}
        Growth Areas: {growth_areas}
        
        Requirements:
        - Show what you'll bring to the role
        - Demonstrate growth potential
        - Focus on team/company impact
        - 4-6 lines maximum
        - 200-250 characters total
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_future_impact(analysis)
    
    def _generate_professional_close(self, analysis: Dict) -> str:
        """Generate professional closing (3-4 lines, ~100-150 chars)"""
        
        return """I would welcome the opportunity to discuss how my experience can contribute to your team's success. Thank you for your consideration.

Best regards,
[Your Name]"""
    
    def _optimize_for_constraints(self, sections: Dict[str, str]) -> List[CoverLetterSection]:
        """Optimize sections to meet character and line constraints"""
        
        optimized_sections = []
        
        for section_name, content in sections.items():
            constraints = self.constraints.sections[section_name]
            
            # Count lines and characters
            lines = content.count('\n') + 1
            chars = len(content)
            
            # Optimize if needed
            if chars > constraints['max_chars'] or lines > constraints['max_lines']:
                content = self._compress_section(content, constraints)
                lines = content.count('\n') + 1
                chars = len(content)
            
            section = CoverLetterSection(
                name=section_name,
                content=content,
                line_count=lines,
                char_count=chars,
                score=0.0  # Will be calculated later
            )
            
            optimized_sections.append(section)
        
        return optimized_sections
    
    def _compress_section(self, content: str, constraints: Dict) -> str:
        """Compress section content to meet constraints"""
        
        max_chars = constraints['max_chars']
        max_lines = constraints['max_lines']
        
        # If content is too long, truncate intelligently
        if len(content) > max_chars:
            # Find good breaking points (sentences, phrases)
            sentences = content.split('. ')
            compressed = ""
            
            for sentence in sentences:
                if len(compressed + sentence + '. ') <= max_chars:
                    compressed += sentence + '. '
                else:
                    break
            
            content = compressed.rstrip('. ') + '.'
        
        # If too many lines, compress line breaks
        lines = content.split('\n')
        if len(lines) > max_lines:
            content = '\n'.join(lines[:max_lines])
        
        return content
    
    def _calculate_alignment_score(self, sections: List[CoverLetterSection], job_data: Dict, company_data: Dict) -> AlignmentScore:
        """Calculate alignment score for the cover letter"""
        
        # Combine all section content
        full_content = '\n'.join([section.content for section in sections])
        
        # Calculate job alignment (60% weight)
        job_score = self._calculate_job_alignment(full_content, job_data)
        
        # Calculate culture alignment (40% weight)
        culture_score = self._calculate_culture_alignment(full_content, company_data)
        
        # Overall weighted score
        overall_score = (job_score * 0.6) + (culture_score * 0.4)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(job_score, culture_score, sections)
        
        return AlignmentScore(
            overall=round(overall_score, 1),
            job_alignment=round(job_score, 1),
            culture_alignment=round(culture_score, 1),
            breakdown={
                'skills_match': job_score * 0.3,
                'experience_relevance': job_score * 0.25,
                'requirements_coverage': job_score * 0.25,
                'keywords_integration': job_score * 0.2,
                'values_alignment': culture_score * 0.4,
                'tone_match': culture_score * 0.25,
                'culture_fit': culture_score * 0.2,
                'mission_connection': culture_score * 0.15
            },
            recommendations=recommendations
        )
    
    def _calculate_job_alignment(self, content: str, job_data: Dict) -> float:
        """Calculate how well the cover letter aligns with job requirements"""
        
        job_keywords = job_data.get('keywords', [])
        requirements = job_data.get('requirements', [])
        
        content_lower = content.lower()
        
        # Skills match (30%)
        skills_mentioned = sum(1 for keyword in job_keywords if keyword.lower() in content_lower)
        skills_score = min(skills_mentioned / max(len(job_keywords), 1) * 100, 100)
        
        # Requirements coverage (70%)
        requirements_covered = sum(1 for req in requirements if any(word in content_lower for word in req.lower().split()))
        requirements_score = min(requirements_covered / max(len(requirements), 1) * 100, 100)
        
        return (skills_score * 0.3) + (requirements_score * 0.7)
    
    def _calculate_culture_alignment(self, content: str, company_data: Dict) -> float:
        """Calculate how well the cover letter aligns with company culture"""
        
        culture_keywords = company_data.get('culture_keywords', [])
        values = company_data.get('values', [])
        
        content_lower = content.lower()
        
        # Culture keywords match (60%)
        culture_mentions = sum(1 for keyword in culture_keywords if keyword.lower() in content_lower)
        culture_score = min(culture_mentions / max(len(culture_keywords), 1) * 100, 100)
        
        # Values alignment (40%)
        values_mentioned = sum(1 for value in values if value.lower() in content_lower)
        values_score = min(values_mentioned / max(len(values), 1) * 100, 100)
        
        return (culture_score * 0.6) + (values_score * 0.4)
    
    def _generate_recommendations(self, job_score: float, culture_score: float, sections: List[CoverLetterSection]) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        if job_score < 70:
            recommendations.append("Include more specific job-related keywords and skills")
        
        if culture_score < 70:
            recommendations.append("Better connect your values to the company's mission and culture")
        
        # Check section-specific issues
        for section in sections:
            if section.char_count < 50:
                recommendations.append(f"Expand the {section.name.replace('_', ' ')} section with more detail")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _create_output(self, sections: List[CoverLetterSection], alignment_score: AlignmentScore) -> CoverLetterOutput:
        """Create final cover letter output with metadata"""
        
        total_lines = sum(section.line_count for section in sections)
        total_chars = sum(section.char_count for section in sections)
        
        meets_constraints = (
            total_lines <= self.constraints.max_lines and
            total_chars <= self.constraints.max_characters and
            total_chars >= self.constraints.min_characters
        )
        
        return CoverLetterOutput(
            sections=sections,
            total_lines=total_lines,
            total_characters=total_chars,
            alignment_score=alignment_score,
            meets_constraints=meets_constraints,
            generation_timestamp=datetime.now().isoformat()
        )
    
    # Template fallback methods
    def _generate_template_opening(self, analysis: Dict) -> str:
        """Template-based opening when AI is unavailable"""
        company = analysis['company_insights'].get('mission', 'your company')
        return f"I am excited to apply for this position at {company}. My background aligns perfectly with your needs."
    
    def _generate_template_value_prop(self, analysis: Dict) -> str:
        """Template-based value proposition when AI is unavailable"""
        achievements = analysis['resume_highlights']['top_achievements'][:2]
        return f"In my previous roles, I have {achievements[0] if achievements else 'delivered strong results'}. My experience includes {achievements[1] if len(achievements) > 1 else 'relevant expertise'} that directly applies to this position."
    
    def _generate_template_company_connection(self, analysis: Dict) -> str:
        """Template-based company connection when AI is unavailable"""
        return "I am particularly drawn to your company's mission and values. Your commitment to innovation aligns with my professional goals and personal values."
    
    def _generate_template_future_impact(self, analysis: Dict) -> str:
        """Template-based future impact when AI is unavailable"""
        return "I am eager to bring my skills and experience to contribute to your team's continued success and growth."
    
    # Utility methods
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from job description"""
        # Simple keyword extraction - could be enhanced with NLP
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        return list(set(keywords))[:10]  # Top 10 unique keywords
    
    def _identify_key_skills(self, requirements: List[str]) -> List[str]:
        """Identify key skills from job requirements"""
        skills = []
        for req in requirements:
            # Extract skills using simple patterns
            words = req.split()
            skills.extend([word.strip('.,()') for word in words if len(word) > 3])
        return list(set(skills))[:8]  # Top 8 unique skills
    
    def _identify_role_focus(self, description: str) -> str:
        """Identify the main focus of the role"""
        focus_keywords = {
            'leadership': ['lead', 'manage', 'director', 'senior'],
            'technical': ['develop', 'engineer', 'code', 'technical'],
            'creative': ['design', 'creative', 'brand', 'marketing'],
            'analytical': ['analyze', 'data', 'research', 'insights']
        }
        
        description_lower = description.lower()
        for focus, keywords in focus_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return focus
        
        return 'general'
    
    def _extract_quantified_results(self, resume_data: Dict) -> List[str]:
        """Extract quantified achievements from resume"""
        achievements = resume_data.get('selected_achievements', [])
        quantified = []
        
        for achievement in achievements:
            if any(char.isdigit() for char in achievement):
                quantified.append(achievement)
        
        return quantified[:3]  # Top 3 quantified results

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    cover_letter_ai = CoverLetterAI()
    
    # Sample data
    job_data = {
        'title': 'Senior Product Manager',
        'description': 'We are seeking a Senior Product Manager with experience in AI/ML products...',
        'requirements': ['5+ years product management', 'AI/ML experience', 'Data-driven decision making'],
        'keywords': ['product', 'AI', 'ML', 'data', 'strategy', 'roadmap']
    }
    
    company_data = {
        'mission': 'Democratizing AI for everyone',
        'values': ['Innovation', 'Collaboration', 'Impact'],
        'culture_keywords': ['fast-paced', 'innovative', 'collaborative', 'data-driven']
    }
    
    resume_data = {
        'selected_achievements': [
            'Increased user engagement by 40% through AI-powered features',
            'Led cross-functional team of 12 engineers and designers',
            'Launched 3 successful ML products generating $2M ARR'
        ],
        'selected_skills': ['Product Management', 'AI/ML', 'Data Analysis', 'Leadership'],
        'executive_summary': 'Senior Product Manager with 7 years of AI/ML product experience'
    }
    
    career_coaching_data = {
        'aspirations': 'Build AI products that solve real-world problems',
        'values': ['Innovation', 'Impact', 'Learning'],
        'passions': ['AI/ML', 'Product Strategy', 'Team Leadership'],
        'personal_story': 'Passionate about democratizing AI technology'
    }
    
    # Generate cover letter
    result = cover_letter_ai.generate_cover_letter(
        job_data=job_data,
        company_data=company_data,
        resume_data=resume_data,
        career_coaching_data=career_coaching_data
    )
    
    print("Generated Cover Letter:")
    print("=" * 50)
    print(f"Total Lines: {result.total_lines}/{cover_letter_ai.constraints.max_lines}")
    print(f"Total Characters: {result.total_characters}/{cover_letter_ai.constraints.max_characters}")
    print(f"Meets Constraints: {result.meets_constraints}")
    print(f"Alignment Score: {result.alignment_score.overall}/100")
    print()
    
    for section in result.sections:
        print(f"=== {section.name.replace('_', ' ').title()} ===")
        print(f"Lines: {section.line_count}, Chars: {section.char_count}")
        print(section.content)
        print()
    
    print("Recommendations:")
    for rec in result.alignment_score.recommendations:
        print(f"- {rec}")
