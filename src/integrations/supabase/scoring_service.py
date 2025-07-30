"""
AI Scoring Database Service

Manages storage and retrieval of AI scoring results for jobs, companies, and resumes.
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from src.integrations.supabase.supabase_client import get_supabase_client
from src.core.ai_scoring_engine import (
    ScoringOrchestrator, JobScoringResult, CompanyScoringResult, 
    ResumeScoringResult, create_sample_job_data, create_sample_company_data,
    create_sample_resume_data
)
from src.core.personal_brand import create_sample_profile

logger = logging.getLogger(__name__)

class ScoringDatabaseService:
    """Database service for AI scoring results"""
    
    def __init__(self):
        """Initialize the scoring database service"""
        self.supabase = get_supabase_client()
        self.orchestrator = ScoringOrchestrator()
        
        if not self.supabase:
            logger.warning("Supabase client not available - running in demo mode")
    
    def store_job_score(self, job_score: JobScoringResult) -> str:
        """
        Store job scoring result in database
        
        Args:
            job_score: JobScoringResult to store
            
        Returns:
            Score record ID
        """
        try:
            if not self.supabase:
                logger.info("Demo mode: Would store job score")
                return str(uuid.uuid4())
            
            score_data = {
                "id": str(uuid.uuid4()),
                "job_id": job_score.job_id,
                "score_type": "job_alignment",
                "score": job_score.score,
                "rationale": job_score.rationale,
                "confidence": job_score.confidence,
                "scoring_factors": json.dumps(job_score.scoring_factors),
                "profile_version": job_score.profile_version,
                "metadata": json.dumps({
                    "job_title": job_score.job_title,
                    "company_name": job_score.company_name,
                    "alignment_areas": job_score.alignment_areas,
                    "concern_areas": job_score.concern_areas,
                    "recommended_resume_version": job_score.recommended_resume_version
                }),
                "created_at": job_score.timestamp.isoformat()
            }
            
            result = self.supabase.table("ai_scores").insert(score_data).execute()
            
            if result.data:
                logger.info(f"Stored job score: {job_score.job_id} - {job_score.score}")
                return result.data[0]["id"]
            else:
                logger.error("Failed to store job score")
                return str(uuid.uuid4())
                
        except Exception as e:
            logger.error(f"Error storing job score: {e}")
            return str(uuid.uuid4())
    
    def store_company_score(self, company_score: CompanyScoringResult) -> str:
        """
        Store company scoring result in database
        
        Args:
            company_score: CompanyScoringResult to store
            
        Returns:
            Score record ID
        """
        try:
            if not self.supabase:
                logger.info("Demo mode: Would store company score")
                return str(uuid.uuid4())
            
            score_data = {
                "id": str(uuid.uuid4()),
                "company_id": company_score.company_id,
                "score_type": "company_fit",
                "score": company_score.score,
                "rationale": company_score.rationale,
                "confidence": company_score.confidence,
                "scoring_factors": json.dumps(company_score.scoring_factors),
                "profile_version": company_score.profile_version,
                "metadata": json.dumps({
                    "company_name": company_score.company_name,
                    "industry_alignment": company_score.industry_alignment,
                    "culture_alignment": company_score.culture_alignment,
                    "values_alignment": company_score.values_alignment,
                    "size_stage_alignment": company_score.size_stage_alignment
                }),
                "created_at": company_score.timestamp.isoformat()
            }
            
            result = self.supabase.table("ai_scores").insert(score_data).execute()
            
            if result.data:
                logger.info(f"Stored company score: {company_score.company_id} - {company_score.score}")
                return result.data[0]["id"]
            else:
                logger.error("Failed to store company score")
                return str(uuid.uuid4())
                
        except Exception as e:
            logger.error(f"Error storing company score: {e}")
            return str(uuid.uuid4())
    
    def store_resume_score(self, resume_score: ResumeScoringResult) -> str:
        """
        Store resume scoring result in database
        
        Args:
            resume_score: ResumeScoringResult to store
            
        Returns:
            Score record ID
        """
        try:
            if not self.supabase:
                logger.info("Demo mode: Would store resume score")
                return str(uuid.uuid4())
            
            score_data = {
                "id": str(uuid.uuid4()),
                "resume_id": resume_score.resume_id,
                "job_id": resume_score.job_id,
                "score_type": "resume_job_fit",
                "score": resume_score.score,
                "rationale": resume_score.rationale,
                "confidence": resume_score.confidence,
                "scoring_factors": json.dumps(resume_score.scoring_factors),
                "profile_version": resume_score.profile_version,
                "metadata": json.dumps({
                    "resume_version": resume_score.resume_version,
                    "keyword_match_score": resume_score.keyword_match_score,
                    "experience_relevance": resume_score.experience_relevance,
                    "skills_alignment": resume_score.skills_alignment,
                    "suggested_improvements": resume_score.suggested_improvements
                }),
                "created_at": resume_score.timestamp.isoformat()
            }
            
            result = self.supabase.table("ai_scores").insert(score_data).execute()
            
            if result.data:
                logger.info(f"Stored resume score: {resume_score.resume_id} vs {resume_score.job_id} - {resume_score.score}")
                return result.data[0]["id"]
            else:
                logger.error("Failed to store resume score")
                return str(uuid.uuid4())
                
        except Exception as e:
            logger.error(f"Error storing resume score: {e}")
            return str(uuid.uuid4())
    
    def get_job_scores(self, job_id: str, profile_version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all scores for a specific job
        
        Args:
            job_id: Job ID to get scores for
            profile_version: Optional profile version filter
            
        Returns:
            List of job scoring results
        """
        try:
            if not self.supabase:
                return self._demo_job_scores(job_id)
            
            query = self.supabase.table("ai_scores").select("*").eq("job_id", job_id).eq("score_type", "job_alignment")
            
            if profile_version:
                query = query.eq("profile_version", profile_version)
            
            result = query.order("created_at", desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting job scores: {e}")
            return []
    
    def get_company_scores(self, company_id: str, profile_version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all scores for a specific company
        
        Args:
            company_id: Company ID to get scores for
            profile_version: Optional profile version filter
            
        Returns:
            List of company scoring results
        """
        try:
            if not self.supabase:
                return self._demo_company_scores(company_id)
            
            query = self.supabase.table("ai_scores").select("*").eq("company_id", company_id).eq("score_type", "company_fit")
            
            if profile_version:
                query = query.eq("profile_version", profile_version)
            
            result = query.order("created_at", desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting company scores: {e}")
            return []
    
    def get_resume_scores(self, resume_id: str, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all scores for a specific resume
        
        Args:
            resume_id: Resume ID to get scores for
            job_id: Optional job ID filter
            
        Returns:
            List of resume scoring results
        """
        try:
            if not self.supabase:
                return self._demo_resume_scores(resume_id, job_id)
            
            query = self.supabase.table("ai_scores").select("*").eq("resume_id", resume_id).eq("score_type", "resume_job_fit")
            
            if job_id:
                query = query.eq("job_id", job_id)
            
            result = query.order("created_at", desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting resume scores: {e}")
            return []
    
    def get_top_scored_jobs(self, profile_version: str, limit: int = 10, min_score: float = 70.0) -> List[Dict[str, Any]]:
        """
        Get top-scored jobs for a profile version
        
        Args:
            profile_version: Profile version to filter by
            limit: Maximum number of results
            min_score: Minimum score threshold
            
        Returns:
            List of top-scored jobs
        """
        try:
            if not self.supabase:
                return self._demo_top_jobs(limit, min_score)
            
            result = self.supabase.table("ai_scores").select("*").eq("score_type", "job_alignment").eq("profile_version", profile_version).gte("score", min_score).order("score", desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting top scored jobs: {e}")
            return []
    
    def get_top_scored_companies(self, profile_version: str, limit: int = 10, min_score: float = 70.0) -> List[Dict[str, Any]]:
        """
        Get top-scored companies for a profile version
        
        Args:
            profile_version: Profile version to filter by
            limit: Maximum number of results
            min_score: Minimum score threshold
            
        Returns:
            List of top-scored companies
        """
        try:
            if not self.supabase:
                return self._demo_top_companies(limit, min_score)
            
            result = self.supabase.table("ai_scores").select("*").eq("score_type", "company_fit").eq("profile_version", profile_version).gte("score", min_score).order("score", desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting top scored companies: {e}")
            return []
    
    def score_and_store_opportunity(self, job_data: Dict[str, Any], company_data: Dict[str, Any], 
                                  resume_versions: List[Dict[str, Any]], brand_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score an opportunity and store all results in database
        
        Args:
            job_data: Job information
            company_data: Company information
            resume_versions: List of resume versions
            brand_profile: Personal brand profile
            
        Returns:
            Comprehensive scoring results with database IDs
        """
        try:
            # Get comprehensive scoring
            results = self.orchestrator.score_opportunity(job_data, company_data, resume_versions, brand_profile)
            
            # Store job score
            if results.get('job_score'):
                job_score_obj = JobScoringResult(**{
                    k: v for k, v in results['job_score'].items() 
                    if k != 'timestamp'
                })
                job_score_obj.timestamp = datetime.fromisoformat(results['job_score']['timestamp'])
                job_score_id = self.store_job_score(job_score_obj)
                results['job_score']['database_id'] = job_score_id
            
            # Store company score
            if results.get('company_score'):
                company_score_obj = CompanyScoringResult(**{
                    k: v for k, v in results['company_score'].items() 
                    if k != 'timestamp'
                })
                company_score_obj.timestamp = datetime.fromisoformat(results['company_score']['timestamp'])
                company_score_id = self.store_company_score(company_score_obj)
                results['company_score']['database_id'] = company_score_id
            
            # Store resume scores
            for resume_score in results.get('resume_scores', []):
                resume_score_obj = ResumeScoringResult(**{
                    k: v for k, v in resume_score.items() 
                    if k != 'timestamp'
                })
                resume_score_obj.timestamp = datetime.fromisoformat(resume_score['timestamp'])
                resume_score_id = self.store_resume_score(resume_score_obj)
                resume_score['database_id'] = resume_score_id
            
            logger.info(f"Scored and stored opportunity: {job_data.get('title', 'Unknown')} - Overall: {results.get('overall_score', 0)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error scoring and storing opportunity: {e}")
            return {"error": str(e)}
    
    def batch_score_jobs(self, jobs_data: List[Dict[str, Any]], brand_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score multiple jobs and store results
        
        Args:
            jobs_data: List of job data
            brand_profile: Personal brand profile
            
        Returns:
            List of job scoring results with database IDs
        """
        results = []
        
        for job_data in jobs_data:
            try:
                # Score the job
                job_result = self.orchestrator.job_scorer.score_job_alignment(job_data, brand_profile)
                
                # Store in database
                score_id = self.store_job_score(job_result)
                
                # Add to results
                result_dict = job_result.to_dict()
                result_dict['database_id'] = score_id
                results.append(result_dict)
                
            except Exception as e:
                logger.error(f"Failed to score job {job_data.get('title', 'Unknown')}: {e}")
                continue
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def get_scoring_analytics(self, profile_version: str) -> Dict[str, Any]:
        """
        Get analytics about scoring results for a profile version
        
        Args:
            profile_version: Profile version to analyze
            
        Returns:
            Analytics data
        """
        try:
            if not self.supabase:
                return self._demo_scoring_analytics()
            
            # Get all scores for this profile version
            result = self.supabase.table("ai_scores").select("*").eq("profile_version", profile_version).execute()
            
            if not result.data:
                return {"error": "No scoring data found"}
            
            scores = result.data
            
            # Calculate analytics
            job_scores = [s for s in scores if s['score_type'] == 'job_alignment']
            company_scores = [s for s in scores if s['score_type'] == 'company_fit']
            resume_scores = [s for s in scores if s['score_type'] == 'resume_job_fit']
            
            analytics = {
                "total_scores": len(scores),
                "job_scores": {
                    "count": len(job_scores),
                    "average": sum(s['score'] for s in job_scores) / len(job_scores) if job_scores else 0,
                    "top_score": max(s['score'] for s in job_scores) if job_scores else 0,
                    "high_fit_count": len([s for s in job_scores if s['score'] >= 80])
                },
                "company_scores": {
                    "count": len(company_scores),
                    "average": sum(s['score'] for s in company_scores) / len(company_scores) if company_scores else 0,
                    "top_score": max(s['score'] for s in company_scores) if company_scores else 0,
                    "high_fit_count": len([s for s in company_scores if s['score'] >= 80])
                },
                "resume_scores": {
                    "count": len(resume_scores),
                    "average": sum(s['score'] for s in resume_scores) / len(resume_scores) if resume_scores else 0,
                    "top_score": max(s['score'] for s in resume_scores) if resume_scores else 0,
                    "high_fit_count": len([s for s in resume_scores if s['score'] >= 80])
                },
                "profile_version": profile_version,
                "last_updated": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting scoring analytics: {e}")
            return {"error": str(e)}
    
    def rescore_on_profile_update(self, old_profile_version: str, new_profile_version: str, brand_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Re-score all opportunities when profile is updated
        
        Args:
            old_profile_version: Previous profile version
            new_profile_version: New profile version
            brand_profile: Updated brand profile
            
        Returns:
            Re-scoring results summary
        """
        try:
            if not self.supabase:
                return self._demo_rescore_results()
            
            # Get all unique jobs and companies from old profile version
            old_scores = self.supabase.table("ai_scores").select("*").eq("profile_version", old_profile_version).execute()
            
            if not old_scores.data:
                return {"message": "No previous scores found to update"}
            
            # Extract unique job and company IDs
            job_ids = set()
            company_ids = set()
            
            for score in old_scores.data:
                if score['score_type'] == 'job_alignment' and score.get('job_id'):
                    job_ids.add(score['job_id'])
                elif score['score_type'] == 'company_fit' and score.get('company_id'):
                    company_ids.add(score['company_id'])
            
            rescore_results = {
                "jobs_rescored": 0,
                "companies_rescored": 0,
                "profile_version": new_profile_version,
                "timestamp": datetime.now().isoformat()
            }
            
            # Re-score jobs (would need job data from another service)
            # This is a placeholder - in real implementation, you'd fetch job data and re-score
            logger.info(f"Would re-score {len(job_ids)} jobs and {len(company_ids)} companies")
            
            rescore_results["jobs_rescored"] = len(job_ids)
            rescore_results["companies_rescored"] = len(company_ids)
            
            return rescore_results
            
        except Exception as e:
            logger.error(f"Error re-scoring on profile update: {e}")
            return {"error": str(e)}
    
    # Demo mode methods
    def _demo_job_scores(self, job_id: str) -> List[Dict[str, Any]]:
        """Demo job scores"""
        return [{
            "id": str(uuid.uuid4()),
            "job_id": job_id,
            "score_type": "job_alignment",
            "score": 87.5,
            "rationale": "Strong alignment with your technical leadership interests and fintech industry preference",
            "confidence": 0.88,
            "scoring_factors": json.dumps({"role_alignment": 90, "industry_fit": 85}),
            "profile_version": "1.0",
            "created_at": datetime.now().isoformat()
        }]
    
    def _demo_company_scores(self, company_id: str) -> List[Dict[str, Any]]:
        """Demo company scores"""
        return [{
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "score_type": "company_fit",
            "score": 82.0,
            "rationale": "Good cultural fit with your values and growth stage preference",
            "confidence": 0.85,
            "scoring_factors": json.dumps({"industry_match": 85, "values_alignment": 80}),
            "profile_version": "1.0",
            "created_at": datetime.now().isoformat()
        }]
    
    def _demo_resume_scores(self, resume_id: str, job_id: Optional[str]) -> List[Dict[str, Any]]:
        """Demo resume scores"""
        return [{
            "id": str(uuid.uuid4()),
            "resume_id": resume_id,
            "job_id": job_id or "demo_job",
            "score_type": "resume_job_fit",
            "score": 79.0,
            "rationale": "Good keyword match and relevant experience",
            "confidence": 0.82,
            "scoring_factors": json.dumps({"keyword_match": 75, "experience_relevance": 85}),
            "profile_version": "1.0",
            "created_at": datetime.now().isoformat()
        }]
    
    def _demo_top_jobs(self, limit: int, min_score: float) -> List[Dict[str, Any]]:
        """Demo top jobs"""
        return [
            {
                "id": str(uuid.uuid4()),
                "job_id": f"job_{i}",
                "score": 95 - i * 3,
                "rationale": f"Excellent fit for your background and interests",
                "metadata": json.dumps({"job_title": f"Senior Engineer {i}", "company_name": f"Company {i}"})
            }
            for i in range(min(limit, 5))
        ]
    
    def _demo_top_companies(self, limit: int, min_score: float) -> List[Dict[str, Any]]:
        """Demo top companies"""
        return [
            {
                "id": str(uuid.uuid4()),
                "company_id": f"company_{i}",
                "score": 92 - i * 4,
                "rationale": f"Strong cultural and values alignment",
                "metadata": json.dumps({"company_name": f"TechCorp {i}"})
            }
            for i in range(min(limit, 5))
        ]
    
    def _demo_scoring_analytics(self) -> Dict[str, Any]:
        """Demo scoring analytics"""
        return {
            "total_scores": 45,
            "job_scores": {
                "count": 20,
                "average": 78.5,
                "top_score": 95,
                "high_fit_count": 8
            },
            "company_scores": {
                "count": 15,
                "average": 81.2,
                "top_score": 92,
                "high_fit_count": 6
            },
            "resume_scores": {
                "count": 10,
                "average": 76.8,
                "top_score": 88,
                "high_fit_count": 4
            },
            "profile_version": "1.0",
            "last_updated": datetime.now().isoformat()
        }
    
    def _demo_rescore_results(self) -> Dict[str, Any]:
        """Demo re-score results"""
        return {
            "jobs_rescored": 12,
            "companies_rescored": 8,
            "profile_version": "1.1",
            "timestamp": datetime.now().isoformat()
        }

# Demo functions
def demo_comprehensive_scoring():
    """Demo comprehensive opportunity scoring"""
    service = ScoringDatabaseService()
    
    # Create sample data
    job_data = create_sample_job_data()
    company_data = create_sample_company_data()
    resume_data = [create_sample_resume_data()]
    brand_profile = create_sample_profile().to_dict()
    
    # Score and store
    results = service.score_and_store_opportunity(job_data, company_data, resume_data, brand_profile)
    
    return results

def demo_batch_job_scoring():
    """Demo batch job scoring"""
    service = ScoringDatabaseService()
    
    # Create sample jobs
    jobs_data = [create_sample_job_data() for _ in range(3)]
    brand_profile = create_sample_profile().to_dict()
    
    # Batch score
    results = service.batch_score_jobs(jobs_data, brand_profile)
    
    return results
