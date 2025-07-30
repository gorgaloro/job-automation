"""
Job Description Parsing & Intelligence Module

This module provides intelligent parsing and extraction of job descriptions
from multiple sources including URLs, raw text, and structured data.
"""

import os
import re
import json
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class JobRequirements:
    """Structured job requirements extracted from description"""
    required_skills: List[str]
    preferred_skills: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    certifications: List[str]
    technologies: List[str]
    soft_skills: List[str]

@dataclass
class JobDetails:
    """Comprehensive job details structure"""
    title: str
    company: str
    location: str
    job_type: str  # full-time, part-time, contract, etc.
    remote_policy: str  # remote, hybrid, onsite
    salary_range: Optional[Dict[str, Union[int, str]]]
    description: str
    requirements: JobRequirements
    benefits: List[str]
    application_deadline: Optional[str]
    job_board_url: Optional[str]
    company_url: Optional[str]
    posting_date: Optional[str]
    job_id: Optional[str]

class JobDescriptionParser:
    """
    Intelligent job description parser that extracts structured data
    from various input sources using AI-powered analysis.
    """
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def parse_from_url(self, url: str) -> JobDetails:
        """
        Parse job description from a URL.
        
        Args:
            url: Job posting URL
            
        Returns:
            JobDetails object with extracted information
            
        Raises:
            ValueError: If URL is invalid or inaccessible
            Exception: If parsing fails
        """
        try:
            logger.info(f"Parsing job from URL: {url}")
            
            # Fetch the webpage content
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract text content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Parse with AI
            job_details = self._parse_with_ai(clean_text, source_url=url)
            
            logger.info(f"Successfully parsed job: {job_details.title} at {job_details.company}")
            return job_details
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise ValueError(f"Unable to access URL: {e}")
        except Exception as e:
            logger.error(f"Failed to parse job from URL {url}: {e}")
            raise
    
    def parse_from_text(self, text: str, source_url: Optional[str] = None) -> JobDetails:
        """
        Parse job description from raw text.
        
        Args:
            text: Raw job description text
            source_url: Optional source URL for reference
            
        Returns:
            JobDetails object with extracted information
        """
        logger.info("Parsing job from raw text")
        return self._parse_with_ai(text, source_url=source_url)
    
    def _parse_with_ai(self, text: str, source_url: Optional[str] = None) -> JobDetails:
        """
        Use OpenAI to intelligently parse job description text.
        
        Args:
            text: Job description text to parse
            source_url: Optional source URL
            
        Returns:
            JobDetails object with structured data
        """
        
        prompt = f"""
        Analyze the following job description and extract structured information.
        Return a JSON object with the following structure:
        
        {{
            "title": "Job title",
            "company": "Company name",
            "location": "Location (city, state/country)",
            "job_type": "full-time|part-time|contract|internship",
            "remote_policy": "remote|hybrid|onsite",
            "salary_range": {{"min": 0, "max": 0, "currency": "USD", "period": "annual"}},
            "description": "Full job description",
            "requirements": {{
                "required_skills": ["skill1", "skill2"],
                "preferred_skills": ["skill1", "skill2"],
                "experience_years": 0,
                "education_level": "Bachelor's|Master's|PhD|High School|Associate's",
                "certifications": ["cert1", "cert2"],
                "technologies": ["tech1", "tech2"],
                "soft_skills": ["skill1", "skill2"]
            }},
            "benefits": ["benefit1", "benefit2"],
            "application_deadline": "YYYY-MM-DD or null",
            "posting_date": "YYYY-MM-DD or null",
            "job_id": "job_id or null"
        }}
        
        Guidelines:
        - Extract exact information from the text
        - Use null for missing information
        - Normalize skill names (e.g., "JavaScript" not "javascript")
        - Separate required vs preferred skills carefully
        - Include all mentioned technologies and frameworks
        - Extract soft skills like "communication", "leadership", etc.
        - Parse salary ranges carefully, convert to annual if needed
        - Identify remote work policies from keywords
        
        Job Description:
        {text}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert job description parser. Extract structured data accurately and comprehensively."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the JSON response
            parsed_data = json.loads(response.choices[0].message.content)
            
            # Create JobDetails object
            requirements = JobRequirements(**parsed_data["requirements"])
            
            job_details = JobDetails(
                title=parsed_data["title"],
                company=parsed_data["company"],
                location=parsed_data["location"],
                job_type=parsed_data["job_type"],
                remote_policy=parsed_data["remote_policy"],
                salary_range=parsed_data.get("salary_range"),
                description=parsed_data["description"],
                requirements=requirements,
                benefits=parsed_data.get("benefits", []),
                application_deadline=parsed_data.get("application_deadline"),
                job_board_url=source_url,
                company_url=None,  # Will be enriched later
                posting_date=parsed_data.get("posting_date"),
                job_id=parsed_data.get("job_id")
            )
            
            return job_details
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise Exception("AI parsing failed - invalid JSON response")
        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            raise Exception(f"AI parsing error: {e}")
    
    def validate_job_data(self, job_details: JobDetails) -> Dict[str, List[str]]:
        """
        Validate parsed job data and return any issues found.
        
        Args:
            job_details: JobDetails object to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = {
            "missing_required": [],
            "data_quality": [],
            "warnings": []
        }
        
        # Check required fields
        if not job_details.title:
            issues["missing_required"].append("job_title")
        if not job_details.company:
            issues["missing_required"].append("company")
        if not job_details.description:
            issues["missing_required"].append("description")
        
        # Check data quality
        if job_details.title and len(job_details.title) < 3:
            issues["data_quality"].append("job_title too short")
        if job_details.description and len(job_details.description) < 100:
            issues["data_quality"].append("description too short")
        
        # Check for warnings
        if not job_details.requirements.required_skills:
            issues["warnings"].append("no required skills identified")
        if not job_details.location:
            issues["warnings"].append("location not specified")
        if not job_details.salary_range:
            issues["warnings"].append("salary range not specified")
        
        return issues
    
    def extract_company_domain(self, company_name: str, job_url: Optional[str] = None) -> Optional[str]:
        """
        Extract company domain from company name or job URL.
        
        Args:
            company_name: Name of the company
            job_url: Optional job posting URL
            
        Returns:
            Company domain or None if not found
        """
        if job_url:
            parsed_url = urlparse(job_url)
            domain = parsed_url.netloc.lower()
            
            # Remove common job board domains
            job_boards = [
                'indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com',
                'ziprecruiter.com', 'careerbuilder.com', 'dice.com'
            ]
            
            if not any(jb in domain for jb in job_boards):
                return domain.replace('www.', '')
        
        # Try to guess domain from company name
        company_clean = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
        company_clean = company_clean.replace(' inc', '').replace(' llc', '').replace(' corp', '')
        company_clean = company_clean.replace(' company', '').replace(' corporation', '')
        company_clean = company_clean.strip().replace(' ', '')
        
        if company_clean:
            return f"{company_clean}.com"
        
        return None
    
    def to_database_format(self, job_details: JobDetails) -> Dict:
        """
        Convert JobDetails to database-compatible format.
        
        Args:
            job_details: JobDetails object
            
        Returns:
            Dictionary formatted for database insertion
        """
        return {
            "job_title": job_details.title,
            "company_name": job_details.company,
            "location": job_details.location,
            "job_type": job_details.job_type,
            "remote_policy": job_details.remote_policy,
            "salary_min": job_details.salary_range.get("min") if job_details.salary_range else None,
            "salary_max": job_details.salary_range.get("max") if job_details.salary_range else None,
            "salary_currency": job_details.salary_range.get("currency", "USD") if job_details.salary_range else "USD",
            "description": job_details.description,
            "required_skills": job_details.requirements.required_skills,
            "preferred_skills": job_details.requirements.preferred_skills,
            "experience_years": job_details.requirements.experience_years,
            "education_level": job_details.requirements.education_level,
            "certifications": job_details.requirements.certifications,
            "technologies": job_details.requirements.technologies,
            "soft_skills": job_details.requirements.soft_skills,
            "benefits": job_details.benefits,
            "application_deadline": job_details.application_deadline,
            "job_board_url": job_details.job_board_url,
            "company_url": job_details.company_url,
            "posting_date": job_details.posting_date,
            "job_id": job_details.job_id,
            "company_domain": self.extract_company_domain(job_details.company, job_details.job_board_url)
        }

# Example usage and testing
if __name__ == "__main__":
    parser = JobDescriptionParser()
    
    # Test with sample text
    sample_job_text = """
    Senior Python Developer - TechCorp Inc.
    
    Location: San Francisco, CA (Remote friendly)
    Salary: $120,000 - $160,000 annually
    
    We are seeking a Senior Python Developer to join our growing team.
    
    Requirements:
    - 5+ years of Python development experience
    - Experience with Django, Flask, or FastAPI
    - Strong knowledge of SQL databases
    - Bachelor's degree in Computer Science or related field
    - Experience with AWS or similar cloud platforms
    
    Preferred:
    - Experience with React or Vue.js
    - Knowledge of Docker and Kubernetes
    - Previous startup experience
    
    Benefits:
    - Health insurance
    - 401k matching
    - Flexible PTO
    - Remote work options
    
    Apply by: March 15, 2024
    """
    
    try:
        job_details = parser.parse_from_text(sample_job_text)
        print("✅ Parsed job successfully!")
        print(f"Title: {job_details.title}")
        print(f"Company: {job_details.company}")
        print(f"Required Skills: {job_details.requirements.required_skills}")
        print(f"Technologies: {job_details.requirements.technologies}")
        
        # Validate the data
        validation_results = parser.validate_job_data(job_details)
        if validation_results["missing_required"]:
            print(f"⚠️ Missing required fields: {validation_results['missing_required']}")
        
        # Convert to database format
        db_format = parser.to_database_format(job_details)
        print(f"✅ Database format ready with {len(db_format)} fields")
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
