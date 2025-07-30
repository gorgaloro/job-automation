"""
Job Database Service

Handles all database operations for jobs and companies using Supabase.
Integrates with the job parser to store structured job data.
"""

import os
import json
import requests
import datetime
from typing import Dict, List, Optional, Union
from dataclasses import asdict
from dotenv import load_dotenv
import logging

from ...core.job_parser import JobDetails, JobDescriptionParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class JobDatabaseService:
    """
    Service for managing job and company data in Supabase database.
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
    
    def insert_or_get_company(self, job_details: JobDetails) -> str:
        """
        Insert company or retrieve existing company ID.
        
        Args:
            job_details: JobDetails object containing company information
            
        Returns:
            Company ID (string)
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Extract company domain
            parser = JobDescriptionParser()
            domain = parser.extract_company_domain(
                job_details.company, 
                job_details.job_board_url
            )
            
            # Check if company already exists
            if domain:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/companies",
                    headers=self.headers,
                    params={"domain": f"eq.{domain}", "select": "id"}
                )
                response.raise_for_status()
                results = response.json()
                
                if results:
                    logger.info(f"Found existing company: {job_details.company}")
                    return results[0]["id"]
            
            # Create new company record
            company_data = {
                "name": job_details.company,
                "domain": domain,
                "website": f"https://{domain}" if domain else None,
                "location": job_details.location,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Insert company
            response = requests.post(
                f"{self.supabase_url}/rest/v1/companies",
                headers=self.headers,
                json=company_data
            )
            response.raise_for_status()
            
            # Get the inserted company ID
            response = requests.get(
                f"{self.supabase_url}/rest/v1/companies",
                headers=self.headers,
                params={"select": "id", "order": "created_at.desc", "limit": 1}
            )
            response.raise_for_status()
            company_id = response.json()[0]["id"]
            
            logger.info(f"Created new company: {job_details.company} (ID: {company_id})")
            return company_id
            
        except requests.RequestException as e:
            logger.error(f"Database error inserting company: {e}")
            raise Exception(f"Failed to insert company: {e}")
        except Exception as e:
            logger.error(f"Unexpected error inserting company: {e}")
            raise
    
    def insert_job(self, job_details: JobDetails, company_id: str) -> Dict:
        """
        Insert job record into database.
        
        Args:
            job_details: JobDetails object with job information
            company_id: ID of the associated company
            
        Returns:
            Dictionary with insertion result
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Convert to database format
            parser = JobDescriptionParser()
            job_data = parser.to_database_format(job_details)
            
            # Add company ID and metadata
            job_data.update({
                "company_id": company_id,
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
                "status": "active",
                "source": "parsed",
                "parsing_version": "1.0"
            })
            
            # Convert lists to JSON strings for database storage
            list_fields = [
                "required_skills", "preferred_skills", "certifications",
                "technologies", "soft_skills", "benefits"
            ]
            for field in list_fields:
                if job_data.get(field):
                    job_data[field] = json.dumps(job_data[field])
            
            # Insert job
            response = requests.post(
                f"{self.supabase_url}/rest/v1/jobs",
                headers=self.headers,
                json=job_data
            )
            response.raise_for_status()
            
            # Get the inserted job ID
            response = requests.get(
                f"{self.supabase_url}/rest/v1/jobs",
                headers=self.headers,
                params={
                    "select": "id,job_title,company_id",
                    "order": "created_at.desc",
                    "limit": 1
                }
            )
            response.raise_for_status()
            job_record = response.json()[0]
            
            logger.info(f"Inserted job: {job_details.title} (ID: {job_record['id']})")
            
            return {
                "job_id": job_record["id"],
                "company_id": company_id,
                "status": "success",
                "message": f"Successfully inserted job: {job_details.title}"
            }
            
        except requests.RequestException as e:
            logger.error(f"Database error inserting job: {e}")
            raise Exception(f"Failed to insert job: {e}")
        except Exception as e:
            logger.error(f"Unexpected error inserting job: {e}")
            raise
    
    def process_job_from_url(self, url: str) -> Dict:
        """
        Complete workflow: parse job from URL and insert into database.
        
        Args:
            url: Job posting URL
            
        Returns:
            Dictionary with processing result
        """
        try:
            logger.info(f"Processing job from URL: {url}")
            
            # Parse job description
            parser = JobDescriptionParser()
            job_details = parser.parse_from_url(url)
            
            # Validate parsed data
            validation_results = parser.validate_job_data(job_details)
            if validation_results["missing_required"]:
                logger.warning(f"Missing required fields: {validation_results['missing_required']}")
            
            # Insert company
            company_id = self.insert_or_get_company(job_details)
            
            # Insert job
            result = self.insert_job(job_details, company_id)
            
            # Add validation info to result
            result["validation"] = validation_results
            result["parsed_data"] = {
                "title": job_details.title,
                "company": job_details.company,
                "location": job_details.location,
                "required_skills_count": len(job_details.requirements.required_skills),
                "technologies_count": len(job_details.requirements.technologies)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process job from URL {url}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "url": url
            }
    
    def process_job_from_text(self, text: str, source_url: Optional[str] = None) -> Dict:
        """
        Complete workflow: parse job from text and insert into database.
        
        Args:
            text: Raw job description text
            source_url: Optional source URL
            
        Returns:
            Dictionary with processing result
        """
        try:
            logger.info("Processing job from text input")
            
            # Parse job description
            parser = JobDescriptionParser()
            job_details = parser.parse_from_text(text, source_url)
            
            # Validate parsed data
            validation_results = parser.validate_job_data(job_details)
            if validation_results["missing_required"]:
                logger.warning(f"Missing required fields: {validation_results['missing_required']}")
            
            # Insert company
            company_id = self.insert_or_get_company(job_details)
            
            # Insert job
            result = self.insert_job(job_details, company_id)
            
            # Add validation info to result
            result["validation"] = validation_results
            result["parsed_data"] = {
                "title": job_details.title,
                "company": job_details.company,
                "location": job_details.location,
                "required_skills_count": len(job_details.requirements.required_skills),
                "technologies_count": len(job_details.requirements.technologies)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process job from text: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """
        Retrieve job by ID with company information.
        
        Args:
            job_id: Job ID to retrieve
            
        Returns:
            Job data with company info or None if not found
        """
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/jobs",
                headers=self.headers,
                params={
                    "id": f"eq.{job_id}",
                    "select": "*,companies(*)"
                }
            )
            response.raise_for_status()
            results = response.json()
            
            if results:
                job_data = results[0]
                
                # Parse JSON fields back to lists
                list_fields = [
                    "required_skills", "preferred_skills", "certifications",
                    "technologies", "soft_skills", "benefits"
                ]
                for field in list_fields:
                    if job_data.get(field):
                        try:
                            job_data[field] = json.loads(job_data[field])
                        except (json.JSONDecodeError, TypeError):
                            job_data[field] = []
                
                return job_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve job {job_id}: {e}")
            return None
    
    def search_jobs(self, 
                   company: Optional[str] = None,
                   skills: Optional[List[str]] = None,
                   location: Optional[str] = None,
                   job_type: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """
        Search jobs with various filters.
        
        Args:
            company: Company name filter
            skills: Required skills filter
            location: Location filter
            job_type: Job type filter
            limit: Maximum results to return
            
        Returns:
            List of matching job records
        """
        try:
            params = {
                "select": "*,companies(name,domain)",
                "limit": limit,
                "order": "created_at.desc"
            }
            
            # Add filters
            if company:
                params["companies.name"] = f"ilike.%{company}%"
            if location:
                params["location"] = f"ilike.%{location}%"
            if job_type:
                params["job_type"] = f"eq.{job_type}"
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/jobs",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            results = response.json()
            
            # Filter by skills if provided
            if skills:
                filtered_results = []
                for job in results:
                    job_skills = []
                    if job.get("required_skills"):
                        try:
                            job_skills.extend(json.loads(job["required_skills"]))
                        except (json.JSONDecodeError, TypeError):
                            pass
                    if job.get("preferred_skills"):
                        try:
                            job_skills.extend(json.loads(job["preferred_skills"]))
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    # Check if any of the search skills match job skills
                    job_skills_lower = [skill.lower() for skill in job_skills]
                    if any(skill.lower() in job_skills_lower for skill in skills):
                        filtered_results.append(job)
                
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search jobs: {e}")
            return []
    
    def update_job_status(self, job_id: str, status: str) -> bool:
        """
        Update job status (active, applied, rejected, etc.).
        
        Args:
            job_id: Job ID to update
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/jobs",
                headers=self.headers,
                params={"id": f"eq.{job_id}"},
                json={
                    "status": status,
                    "updated_at": datetime.datetime.now().isoformat()
                }
            )
            response.raise_for_status()
            
            logger.info(f"Updated job {job_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    service = JobDatabaseService()
    
    # Test with sample job text
    sample_text = """
    Senior Python Developer - TechCorp Inc.
    
    Location: San Francisco, CA (Remote friendly)
    Salary: $120,000 - $160,000 annually
    
    We are seeking a Senior Python Developer to join our growing team.
    
    Requirements:
    - 5+ years of Python development experience
    - Experience with Django, Flask, or FastAPI
    - Strong knowledge of SQL databases
    - Bachelor's degree in Computer Science or related field
    
    Benefits:
    - Health insurance
    - 401k matching
    - Flexible PTO
    """
    
    try:
        result = service.process_job_from_text(sample_text)
        if result["status"] == "success":
            print(f"✅ Successfully processed job: {result['parsed_data']['title']}")
            print(f"   Company: {result['parsed_data']['company']}")
            print(f"   Job ID: {result['job_id']}")
            print(f"   Required Skills: {result['parsed_data']['required_skills_count']}")
        else:
            print(f"❌ Failed to process job: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
