"""
Job Search Automation Platform API

Main FastAPI application with job parsing, management, and automation features.
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import API routes
from src.api.routes.jobs import router as jobs_router
from src.api.routes import (
    jobs, resumes, personal_brand, scoring, 
    company_enrichment, job_applications, application_tracking, mobile_networking, analytics_dashboard, workflow_orchestration
)
from src.api.canva_endpoints import router as canva_router

# Import new integrations
from src.integrations.job_board_apis import JobBoardIntegrator
from src.integrations.company_enrichment_apis import CompanyEnrichmentService
from src.integrations.contact_enrichment_apis import ContactEnrichmentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Job Search Automation Platform API")
    yield
    logger.info("👋 Shutting down Job Search Automation Platform API")

# Create FastAPI application
app = FastAPI(
    title="Job Search Automation Platform",
    description="""
    🚀 **Intelligent Job Search Automation Platform**
    
    An AI-powered platform for automating job search workflows including:
    
    * **Job Description Parsing** - Extract structured data from job postings
    * **Company Enrichment** - Automatically gather company information
    * **Resume Optimization** - Tailor resumes to specific job requirements
    * **Application Tracking** - Monitor application status and responses
    * **AI Scoring** - Intelligent job-candidate matching
    
    ## Features
    
    * 🤖 **AI-Powered Parsing** - Uses GPT-4 to extract structured job data
    * 📊 **Database Integration** - Supabase backend for data persistence
    * 🔍 **Advanced Search** - Filter jobs by skills, location, company, etc.
    * 📈 **Analytics** - Track application success rates and trends
    * 🔗 **CRM Integration** - Sync with HubSpot for contact management
    * 🚀 **Batch Processing** - Handle multiple job postings efficiently
    
    ## Getting Started
    
    1. Parse a job description using `/api/v1/jobs/parse`
    2. Search for jobs using `/api/v1/jobs/search`
    3. Get detailed job information using `/api/v1/jobs/{job_id}`
    4. Update application status using `/api/v1/jobs/{job_id}/status`
    
    ## Authentication
    
    Currently using API key authentication. Include your API key in the `Authorization` header:
    ```
    Authorization: Bearer your-api-key
    ```
    """,
    version="1.0.0",
    contact={
        "name": "Allen Walker",
        "url": "https://github.com/gorgaloro/job-search-automation",
        "email": "contact@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(personal_brand.router)
app.include_router(scoring.router)
app.include_router(company_enrichment.router)
app.include_router(job_applications.router)
app.include_router(application_tracking.router)
app.include_router(mobile_networking.router)
app.include_router(analytics_dashboard.router)
app.include_router(workflow_orchestration.router)
app.include_router(canva_router)

# Health check endpoint for Railway
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for Railway deployment monitoring.
    """
    return {
        "status": "healthy",
        "service": "Job Search Automation Platform API",
        "version": "1.0.0",
        "environment": os.getenv("NODE_ENV", "development")
    }

# Job Board API endpoints
@app.get("/api/v1/job-boards/fetch", tags=["job-boards"])
async def fetch_jobs_from_all_boards(limit: int = 100):
    """
    Fetch jobs from all configured job board APIs.
    """
    try:
        integrator = JobBoardIntegrator()
        jobs = await integrator.fetch_all_jobs(limit_per_api=limit)
        unique_jobs = integrator.deduplicate_jobs(jobs)
        
        return {
            "success": True,
            "total_jobs_fetched": len(jobs),
            "unique_jobs": len(unique_jobs),
            "jobs": [{
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source_api": job.source_api,
                "url": job.url
            } for job in unique_jobs[:50]]  # Return first 50 for API response
        }
    except Exception as e:
        logger.error(f"Error fetching jobs from job boards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Company enrichment endpoint
@app.post("/api/v1/companies/enrich", tags=["company-enrichment"])
async def enrich_company(domain: str = None, company_name: str = None):
    """
    Enrich company data using multiple APIs.
    """
    if not domain and not company_name:
        raise HTTPException(status_code=400, detail="Either domain or company_name is required")
    
    try:
        service = CompanyEnrichmentService()
        company_data = await service.enrich_company(domain=domain, company_name=company_name)
        
        if company_data:
            return {
                "success": True,
                "company": {
                    "name": company_data.name,
                    "domain": company_data.domain,
                    "industry": company_data.industry,
                    "size": company_data.size,
                    "location": company_data.location,
                    "source_api": company_data.source_api,
                    "confidence_score": company_data.confidence_score
                }
            }
        else:
            return {
                "success": False,
                "message": "Company data not found"
            }
    except Exception as e:
        logger.error(f"Error enriching company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Contact enrichment endpoint
@app.post("/api/v1/contacts/find", tags=["contact-enrichment"])
async def find_contact_email(domain: str, first_name: str = None, last_name: str = None):
    """
    Find contact email using multiple APIs.
    """
    try:
        service = ContactEnrichmentService()
        contacts = await service.find_contact_email(
            domain=domain, 
            first_name=first_name, 
            last_name=last_name
        )
        
        return {
            "success": True,
            "contacts_found": len(contacts),
            "contacts": [{
                "email": contact.email,
                "full_name": contact.full_name,
                "title": contact.title,
                "company": contact.company,
                "source_api": contact.source_api,
                "confidence_score": contact.confidence_score
            } for contact in contacts]
        }
    except Exception as e:
        logger.error(f"Error finding contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Welcome endpoint with API information.
    """
    return {
        "message": "🚀 Welcome to Job Search Automation Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/v1/jobs/health",
        "features": [
            "AI-powered job description parsing",
            "Intelligent company enrichment",
            "Resume optimization engine",
            "Application tracking system",
            "Advanced job search and filtering",
            "CRM integration with HubSpot",
            "Batch processing capabilities"
        ],
        "endpoints": {
            "parse_job": "/api/v1/jobs/parse",
            "search_jobs": "/api/v1/jobs/search",
            "get_job": "/api/v1/jobs/{job_id}",
            "update_status": "/api/v1/jobs/{job_id}/status",
            "batch_parse": "/api/v1/jobs/batch-parse",
            "job_statistics": "/api/v1/jobs/stats/summary",
            "create_resume": "/api/v1/resumes/",
            "optimize_resume": "/api/v1/resumes/optimize",
            "list_resumes": "/api/v1/resumes/",
            "get_resume": "/api/v1/resumes/{resume_id}",
            "resume_analytics": "/api/v1/resumes/{resume_id}/analytics",
            "export_resume": "/api/v1/resumes/{resume_id}/export",
            "resume_statistics": "/api/v1/resumes/stats/summary",
            "start_interview": "/api/v1/personal-brand/interview/start",
            "respond_interview": "/api/v1/personal-brand/interview/respond",
            "list_profiles": "/api/v1/personal-brand/profiles",
            "get_profile": "/api/v1/personal-brand/profiles/{profile_id}",
            "profile_insights": "/api/v1/personal-brand/profiles/{profile_id}/insights",
            "refine_profile": "/api/v1/personal-brand/profiles/{profile_id}/refine",
            "brand_analytics": "/api/v1/personal-brand/analytics",
            "score_job": "/api/v1/scoring/jobs/score",
            "score_company": "/api/v1/scoring/companies/score",
            "score_resume": "/api/v1/scoring/resumes/score",
            "score_opportunity": "/api/v1/scoring/opportunities/score",
            "batch_score_jobs": "/api/v1/scoring/jobs/batch-score",
            "top_jobs": "/api/v1/scoring/top-jobs",
            "top_companies": "/api/v1/scoring/top-companies",
            "scoring_analytics": "/api/v1/scoring/analytics"
        }
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "service": "job-search-automation-api",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": "server_error"
        }
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 handler.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "type": "not_found"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
