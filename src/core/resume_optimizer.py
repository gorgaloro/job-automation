"""
Resume Optimization & Matching Engine

This module provides intelligent resume optimization and job matching capabilities.
It analyzes job requirements and tailors resumes to maximize compatibility scores.
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import openai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class ResumeSection:
    """Individual resume section structure"""
    title: str
    content: List[str]
    priority: int = 1  # 1-5, higher is more important
    keywords: List[str] = None

@dataclass
class ResumeProfile:
    """Complete resume profile structure"""
    personal_info: Dict[str, str]
    summary: str
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    certifications: List[str]
    projects: List[Dict[str, Any]]
    achievements: List[str]
    custom_sections: List[ResumeSection] = None

@dataclass
class OptimizationResult:
    """Resume optimization result"""
    optimized_resume: ResumeProfile
    compatibility_score: float
    optimization_rationale: str
    keyword_matches: Dict[str, int]
    missing_keywords: List[str]
    suggested_improvements: List[str]
    tailored_sections: List[str]

class ResumeOptimizer:
    """
    Intelligent resume optimizer that tailors resumes to specific job requirements
    using AI-powered analysis and keyword optimization.
    """
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def optimize_resume(self, 
                       resume_profile: ResumeProfile, 
                       job_details: Dict[str, Any],
                       optimization_level: str = "moderate") -> OptimizationResult:
        """
        Optimize resume for a specific job posting.
        
        Args:
            resume_profile: Original resume profile
            job_details: Job details from parser (database format)
            optimization_level: "conservative", "moderate", or "aggressive"
            
        Returns:
            OptimizationResult with optimized resume and analysis
        """
        try:
            logger.info(f"Optimizing resume for {job_details.get('job_title', 'Unknown')} at {job_details.get('company_name', 'Unknown')}")
            
            # Extract job requirements
            job_requirements = self._extract_job_requirements(job_details)
            
            # Analyze current resume compatibility
            compatibility_analysis = self._analyze_compatibility(resume_profile, job_requirements)
            
            # Generate optimized resume
            optimized_resume = self._generate_optimized_resume(
                resume_profile, 
                job_requirements, 
                compatibility_analysis,
                optimization_level
            )
            
            # Calculate final compatibility score
            final_score = self._calculate_compatibility_score(optimized_resume, job_requirements)
            
            # Generate optimization rationale
            rationale = self._generate_optimization_rationale(
                compatibility_analysis, 
                job_requirements, 
                optimization_level
            )
            
            # Identify keyword matches and gaps
            keyword_analysis = self._analyze_keywords(optimized_resume, job_requirements)
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(
                optimized_resume, 
                job_requirements, 
                keyword_analysis
            )
            
            result = OptimizationResult(
                optimized_resume=optimized_resume,
                compatibility_score=final_score,
                optimization_rationale=rationale,
                keyword_matches=keyword_analysis["matches"],
                missing_keywords=keyword_analysis["missing"],
                suggested_improvements=suggestions,
                tailored_sections=compatibility_analysis["tailored_sections"]
            )
            
            logger.info(f"Resume optimization completed. Compatibility score: {final_score:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Resume optimization failed: {e}")
            raise Exception(f"Optimization error: {e}")
    
    def _extract_job_requirements(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure job requirements for optimization."""
        
        # Parse JSON fields if they're strings
        def parse_json_field(field_value):
            if isinstance(field_value, str):
                try:
                    return json.loads(field_value)
                except (json.JSONDecodeError, TypeError):
                    return []
            return field_value or []
        
        requirements = {
            "job_title": job_details.get("job_title", ""),
            "company_name": job_details.get("company_name", ""),
            "required_skills": parse_json_field(job_details.get("required_skills")),
            "preferred_skills": parse_json_field(job_details.get("preferred_skills")),
            "technologies": parse_json_field(job_details.get("technologies")),
            "certifications": parse_json_field(job_details.get("certifications")),
            "experience_years": job_details.get("experience_years"),
            "education_level": job_details.get("education_level"),
            "job_type": job_details.get("job_type"),
            "remote_policy": job_details.get("remote_policy"),
            "description": job_details.get("description", ""),
            "benefits": parse_json_field(job_details.get("benefits")),
            "soft_skills": parse_json_field(job_details.get("soft_skills"))
        }
        
        # Combine all skills for comprehensive analysis
        all_skills = (
            requirements["required_skills"] + 
            requirements["preferred_skills"] + 
            requirements["technologies"] +
            requirements["soft_skills"]
        )
        requirements["all_skills"] = list(set(all_skills))
        
        return requirements
    
    def _analyze_compatibility(self, resume: ResumeProfile, job_req: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current resume compatibility with job requirements."""
        
        # Extract resume keywords
        resume_text = self._extract_resume_text(resume)
        resume_keywords = self._extract_keywords(resume_text)
        
        # Calculate skill matches
        skill_matches = self._calculate_skill_matches(resume.skills, job_req["all_skills"])
        
        # Analyze experience relevance
        experience_relevance = self._analyze_experience_relevance(resume.experience, job_req)
        
        # Check education compatibility
        education_match = self._check_education_compatibility(resume.education, job_req["education_level"])
        
        # Identify sections that need tailoring
        tailored_sections = []
        if skill_matches["score"] < 0.7:
            tailored_sections.append("skills")
        if experience_relevance["score"] < 0.7:
            tailored_sections.append("experience")
        if not resume.summary or len(resume.summary) < 100:
            tailored_sections.append("summary")
        
        return {
            "skill_matches": skill_matches,
            "experience_relevance": experience_relevance,
            "education_match": education_match,
            "resume_keywords": resume_keywords,
            "tailored_sections": tailored_sections,
            "overall_score": (skill_matches["score"] + experience_relevance["score"] + education_match) / 3
        }
    
    def _generate_optimized_resume(self, 
                                 resume: ResumeProfile, 
                                 job_req: Dict[str, Any],
                                 compatibility: Dict[str, Any],
                                 optimization_level: str) -> ResumeProfile:
        """Generate optimized resume using AI."""
        
        prompt = f"""
        Optimize this resume for the following job posting. Return a JSON object with the optimized resume structure.
        
        OPTIMIZATION LEVEL: {optimization_level}
        - conservative: Minor keyword additions, minimal changes
        - moderate: Rewrite sections for better alignment, add relevant keywords
        - aggressive: Significant restructuring, maximize keyword density
        
        JOB REQUIREMENTS:
        Title: {job_req['job_title']}
        Company: {job_req['company_name']}
        Required Skills: {', '.join(job_req['required_skills'])}
        Preferred Skills: {', '.join(job_req['preferred_skills'])}
        Technologies: {', '.join(job_req['technologies'])}
        Experience: {job_req['experience_years']} years
        Education: {job_req['education_level']}
        
        CURRENT RESUME:
        Summary: {resume.summary}
        Skills: {', '.join(resume.skills)}
        Experience: {json.dumps([exp for exp in resume.experience], indent=2)}
        Education: {json.dumps(resume.education, indent=2)}
        
        COMPATIBILITY ANALYSIS:
        Skill Match Score: {compatibility['skill_matches']['score']:.2f}
        Experience Relevance: {compatibility['experience_relevance']['score']:.2f}
        Sections to Tailor: {', '.join(compatibility['tailored_sections'])}
        
        OPTIMIZATION INSTRUCTIONS:
        1. Rewrite the summary to highlight relevant experience and skills
        2. Optimize experience descriptions to emphasize relevant achievements
        3. Reorganize skills to prioritize job-relevant technologies
        4. Add missing keywords naturally throughout the resume
        5. Quantify achievements where possible
        6. Maintain truthfulness - don't add false information
        
        Return JSON structure:
        {{
            "personal_info": {{"name": "", "email": "", "phone": "", "location": ""}},
            "summary": "Optimized professional summary",
            "experience": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "duration": "Start - End",
                    "description": "Optimized description with relevant keywords",
                    "achievements": ["Achievement 1", "Achievement 2"]
                }}
            ],
            "education": [
                {{
                    "degree": "Degree",
                    "institution": "School",
                    "year": "Year",
                    "relevant_coursework": ["Course 1", "Course 2"]
                }}
            ],
            "skills": ["Prioritized skill list"],
            "certifications": ["Cert 1", "Cert 2"],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Project description with relevant keywords",
                    "technologies": ["Tech 1", "Tech 2"]
                }}
            ],
            "achievements": ["Achievement 1", "Achievement 2"]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume optimizer. Create compelling, keyword-optimized resumes that maintain truthfulness while maximizing job compatibility."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            optimized_data = json.loads(response.choices[0].message.content)
            
            # Create optimized resume profile
            optimized_resume = ResumeProfile(
                personal_info=optimized_data.get("personal_info", resume.personal_info),
                summary=optimized_data.get("summary", resume.summary),
                experience=optimized_data.get("experience", resume.experience),
                education=optimized_data.get("education", resume.education),
                skills=optimized_data.get("skills", resume.skills),
                certifications=optimized_data.get("certifications", resume.certifications),
                projects=optimized_data.get("projects", resume.projects),
                achievements=optimized_data.get("achievements", resume.achievements)
            )
            
            return optimized_resume
            
        except Exception as e:
            logger.error(f"AI resume optimization failed: {e}")
            # Return original resume if AI fails
            return resume
    
    def _calculate_compatibility_score(self, resume: ResumeProfile, job_req: Dict[str, Any]) -> float:
        """Calculate compatibility score between resume and job requirements."""
        
        resume_text = self._extract_resume_text(resume).lower()
        
        # Score components
        scores = {
            "required_skills": 0,
            "preferred_skills": 0,
            "technologies": 0,
            "experience": 0,
            "education": 0
        }
        
        # Required skills (40% weight)
        if job_req["required_skills"]:
            matches = sum(1 for skill in job_req["required_skills"] if skill.lower() in resume_text)
            scores["required_skills"] = (matches / len(job_req["required_skills"])) * 40
        
        # Preferred skills (20% weight)
        if job_req["preferred_skills"]:
            matches = sum(1 for skill in job_req["preferred_skills"] if skill.lower() in resume_text)
            scores["preferred_skills"] = (matches / len(job_req["preferred_skills"])) * 20
        
        # Technologies (25% weight)
        if job_req["technologies"]:
            matches = sum(1 for tech in job_req["technologies"] if tech.lower() in resume_text)
            scores["technologies"] = (matches / len(job_req["technologies"])) * 25
        
        # Experience years (10% weight)
        if job_req["experience_years"]:
            resume_years = self._estimate_experience_years(resume.experience)
            if resume_years >= job_req["experience_years"]:
                scores["experience"] = 10
            else:
                scores["experience"] = (resume_years / job_req["experience_years"]) * 10
        
        # Education (5% weight)
        if job_req["education_level"]:
            if self._check_education_compatibility(resume.education, job_req["education_level"]) >= 0.8:
                scores["education"] = 5
        
        total_score = sum(scores.values())
        return min(total_score, 100.0)  # Cap at 100%
    
    def _generate_optimization_rationale(self, 
                                       compatibility: Dict[str, Any], 
                                       job_req: Dict[str, Any],
                                       optimization_level: str) -> str:
        """Generate explanation of optimization decisions."""
        
        rationale_parts = [
            f"Resume optimized at {optimization_level} level for {job_req['job_title']} position."
        ]
        
        if "skills" in compatibility["tailored_sections"]:
            rationale_parts.append(
                f"Skills section reorganized to prioritize {len(job_req['required_skills'])} required skills and {len(job_req['technologies'])} key technologies."
            )
        
        if "experience" in compatibility["tailored_sections"]:
            rationale_parts.append(
                "Experience descriptions enhanced to highlight relevant achievements and quantifiable results."
            )
        
        if "summary" in compatibility["tailored_sections"]:
            rationale_parts.append(
                "Professional summary rewritten to emphasize alignment with job requirements and company needs."
            )
        
        skill_score = compatibility["skill_matches"]["score"]
        if skill_score < 0.7:
            rationale_parts.append(
                f"Added {len(job_req['all_skills'])} relevant keywords to improve skill alignment from {skill_score:.1%} to target 85%+."
            )
        
        return " ".join(rationale_parts)
    
    def _analyze_keywords(self, resume: ResumeProfile, job_req: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze keyword matches and gaps."""
        
        resume_text = self._extract_resume_text(resume).lower()
        
        matches = {}
        missing = []
        
        # Check all job skills
        for skill in job_req["all_skills"]:
            skill_lower = skill.lower()
            if skill_lower in resume_text:
                # Count occurrences
                matches[skill] = resume_text.count(skill_lower)
            else:
                missing.append(skill)
        
        return {
            "matches": matches,
            "missing": missing,
            "match_rate": len(matches) / len(job_req["all_skills"]) if job_req["all_skills"] else 0
        }
    
    def _generate_improvement_suggestions(self, 
                                        resume: ResumeProfile, 
                                        job_req: Dict[str, Any],
                                        keyword_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific improvement suggestions."""
        
        suggestions = []
        
        # Missing critical skills
        critical_missing = [skill for skill in job_req["required_skills"] if skill in keyword_analysis["missing"]]
        if critical_missing:
            suggestions.append(f"Consider adding experience with: {', '.join(critical_missing[:3])}")
        
        # Low keyword density
        if keyword_analysis["match_rate"] < 0.6:
            suggestions.append("Increase keyword density by incorporating more job-relevant terms naturally")
        
        # Quantification opportunities
        if not any("%" in str(exp) or "$" in str(exp) for exp in resume.experience):
            suggestions.append("Add quantifiable achievements (percentages, dollar amounts, metrics)")
        
        # Certification gaps
        missing_certs = [cert for cert in job_req["certifications"] if cert not in resume.certifications]
        if missing_certs:
            suggestions.append(f"Consider pursuing certifications: {', '.join(missing_certs[:2])}")
        
        # Experience relevance
        if job_req["experience_years"] and self._estimate_experience_years(resume.experience) < job_req["experience_years"]:
            suggestions.append("Highlight transferable skills to compensate for experience gap")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    # Helper methods
    def _extract_resume_text(self, resume: ResumeProfile) -> str:
        """Extract all text from resume for analysis."""
        text_parts = [
            resume.summary,
            " ".join(resume.skills),
            " ".join(resume.certifications),
            " ".join(resume.achievements)
        ]
        
        # Add experience text
        for exp in resume.experience:
            text_parts.append(exp.get("title", ""))
            text_parts.append(exp.get("company", ""))
            text_parts.append(exp.get("description", ""))
            if exp.get("achievements"):
                text_parts.extend(exp["achievements"])
        
        # Add education text
        for edu in resume.education:
            text_parts.append(edu.get("degree", ""))
            text_parts.append(edu.get("institution", ""))
            if edu.get("relevant_coursework"):
                text_parts.extend(edu["relevant_coursework"])
        
        # Add projects text
        for project in resume.projects:
            text_parts.append(project.get("name", ""))
            text_parts.append(project.get("description", ""))
            if project.get("technologies"):
                text_parts.extend(project["technologies"])
        
        return " ".join(filter(None, text_parts))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return list(set(words))
    
    def _calculate_skill_matches(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Calculate skill matching score."""
        if not job_skills:
            return {"score": 1.0, "matches": [], "missing": []}
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matches = [skill for skill in job_skills if skill.lower() in resume_skills_lower]
        missing = [skill for skill in job_skills if skill.lower() not in resume_skills_lower]
        
        score = len(matches) / len(job_skills) if job_skills else 0
        
        return {
            "score": score,
            "matches": matches,
            "missing": missing
        }
    
    def _analyze_experience_relevance(self, experience: List[Dict[str, Any]], job_req: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how relevant experience is to job requirements."""
        if not experience:
            return {"score": 0.0, "relevant_roles": []}
        
        relevant_roles = []
        total_relevance = 0
        
        for exp in experience:
            relevance_score = 0
            exp_text = f"{exp.get('title', '')} {exp.get('description', '')}".lower()
            
            # Check for skill mentions
            for skill in job_req["all_skills"]:
                if skill.lower() in exp_text:
                    relevance_score += 1
            
            # Check for industry/domain relevance
            if job_req["company_name"].lower() in exp_text or job_req["job_title"].lower() in exp_text:
                relevance_score += 2
            
            if relevance_score > 0:
                relevant_roles.append({
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "relevance_score": relevance_score
                })
                total_relevance += relevance_score
        
        max_possible_score = len(experience) * len(job_req["all_skills"])
        score = min(total_relevance / max_possible_score, 1.0) if max_possible_score > 0 else 0
        
        return {
            "score": score,
            "relevant_roles": relevant_roles
        }
    
    def _check_education_compatibility(self, education: List[Dict[str, Any]], required_level: str) -> float:
        """Check education compatibility with job requirements."""
        if not required_level or not education:
            return 0.5  # Neutral score
        
        education_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        required_score = education_levels.get(required_level.lower(), 3)
        
        max_education_score = 0
        for edu in education:
            degree = edu.get("degree", "").lower()
            for level, score in education_levels.items():
                if level in degree:
                    max_education_score = max(max_education_score, score)
                    break
        
        if max_education_score >= required_score:
            return 1.0
        elif max_education_score > 0:
            return max_education_score / required_score
        else:
            return 0.3  # Some credit for unspecified education
    
    def _estimate_experience_years(self, experience: List[Dict[str, Any]]) -> int:
        """Estimate total years of experience from resume."""
        total_years = 0
        
        for exp in experience:
            duration = exp.get("duration", "")
            # Simple parsing - can be enhanced
            if "year" in duration.lower():
                years = re.findall(r'(\d+)', duration)
                if years:
                    total_years += int(years[0])
            elif "-" in duration:
                # Try to parse date ranges
                parts = duration.split("-")
                if len(parts) == 2:
                    try:
                        start_year = int(re.findall(r'(\d{4})', parts[0])[0])
                        end_part = parts[1].strip()
                        if "present" in end_part.lower() or "current" in end_part.lower():
                            end_year = datetime.now().year
                        else:
                            end_year = int(re.findall(r'(\d{4})', end_part)[0])
                        total_years += max(0, end_year - start_year)
                    except (IndexError, ValueError):
                        total_years += 2  # Default assumption
        
        return total_years

# Example usage and testing
if __name__ == "__main__":
    # Sample resume profile
    sample_resume = ResumeProfile(
        personal_info={
            "name": "John Developer",
            "email": "john@example.com",
            "phone": "555-0123",
            "location": "San Francisco, CA"
        },
        summary="Software developer with 3 years of experience in web development.",
        experience=[
            {
                "title": "Software Developer",
                "company": "Tech Startup",
                "duration": "2021 - Present",
                "description": "Developed web applications using Python and JavaScript",
                "achievements": ["Improved performance by 30%", "Led team of 3 developers"]
            }
        ],
        education=[
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of California",
                "year": "2021"
            }
        ],
        skills=["Python", "JavaScript", "HTML", "CSS"],
        certifications=["AWS Cloud Practitioner"],
        projects=[
            {
                "name": "E-commerce Platform",
                "description": "Built full-stack e-commerce application",
                "technologies": ["Python", "Django", "React"]
            }
        ],
        achievements=["Dean's List", "Hackathon Winner"]
    )
    
    # Sample job details (from our parser)
    sample_job = {
        "job_title": "Senior Full Stack Developer",
        "company_name": "TechCorp Solutions",
        "required_skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
        "preferred_skills": ["Docker", "Kubernetes", "AWS"],
        "technologies": ["Django", "FastAPI", "PostgreSQL", "Redis"],
        "experience_years": 5,
        "education_level": "Bachelor's"
    }
    
    try:
        optimizer = ResumeOptimizer()
        result = optimizer.optimize_resume(sample_resume, sample_job, "moderate")
        
        print("✅ Resume optimization completed!")
        print(f"Compatibility Score: {result.compatibility_score:.1f}%")
        print(f"Keyword Matches: {len(result.keyword_matches)}")
        print(f"Missing Keywords: {len(result.missing_keywords)}")
        print(f"Suggestions: {len(result.suggested_improvements)}")
        print(f"Rationale: {result.optimization_rationale}")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
