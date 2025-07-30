"""
Production FastAPI Main Application for AI Job Search Platform

Simplified production-ready API server with job board integrations.
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
    logger.info("🚀 Starting AI Job Search Platform API")
    yield
    logger.info("👋 Shutting down AI Job Search Platform API")

# Create FastAPI application
app = FastAPI(
    title="AI Job Search Platform API",
    description="""
    🚀 **AI-Powered Job Search Automation Platform**
    
    Production API for intelligent job search automation including:
    
    * **Job Board Integration** - Fetch jobs from Greenhouse, Lever, SmartRecruiters, Workable
    * **Company Enrichment** - Automatically gather company information
    * **Contact Enrichment** - Find contact information for networking
    * **AI Processing** - Intelligent job-candidate matching
    
    ## Quick Start
    
    1. Check API health using `/health`
    2. Fetch jobs using `/api/v1/job-boards/fetch`
    3. Enrich company data using `/api/v1/companies/enrich`
    4. Find contacts using `/api/v1/contacts/find`
    """,
    version="1.0.0",
    contact={
        "name": "AI Job Search Platform",
        "url": "https://github.com/gorgaloro/job-search-automation",
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

# Health check endpoint for Railway
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for Railway deployment monitoring.
    """
    return {
        "status": "healthy",
        "service": "AI Job Search Platform API",
        "version": "1.0.0",
        "environment": os.getenv("NODE_ENV", "development"),
        "integrations": {
            "job_boards": ["greenhouse", "lever", "smartrecruiters", "workable"],
            "company_enrichment": ["clearbit", "zoominfo", "apollo"],
            "contact_enrichment": ["hunter", "rocketreach", "contactout"]
        }
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
            "sources": list(set([job.source_api for job in jobs])),
            "jobs": [{
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source_api": job.source_api,
                "url": job.url,
                "posted_date": job.posted_date.isoformat() if job.posted_date else None
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
                    "description": company_data.description,
                    "industry": company_data.industry,
                    "size": company_data.size,
                    "location": company_data.location,
                    "founded_year": company_data.founded_year,
                    "website": company_data.website,
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
                "linkedin_url": contact.linkedin_url,
                "source_api": contact.source_api,
                "confidence_score": contact.confidence_score,
                "verified": contact.verified
            } for contact in contacts]
        }
    except Exception as e:
        logger.error(f"Error finding contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API status endpoint
@app.get("/api/v1/status", tags=["status"])
async def api_status():
    """
    Get API integration status and configuration.
    """
    return {
        "api_keys_configured": {
            "greenhouse": bool(os.getenv("GREENHOUSE_API_KEY")),
            "lever": bool(os.getenv("LEVER_API_KEY")),
            "smartrecruiters": bool(os.getenv("SMARTRECRUITERS_API_KEY")),
            "workable": bool(os.getenv("WORKABLE_API_KEY")),
            "clearbit": bool(os.getenv("CLEARBIT_API_KEY")),
            "hunter": bool(os.getenv("HUNTER_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY"))
        },
        "environment": os.getenv("NODE_ENV", "development"),
        "demo_mode": os.getenv("DEMO_MODE", "true").lower() == "true"
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Welcome endpoint with API information.
    """
    return {
        "message": "🚀 AI Job Search Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "/api/v1/status",
        "endpoints": {
            "job_boards": "/api/v1/job-boards/fetch",
            "company_enrichment": "/api/v1/companies/enrich",
            "contact_enrichment": "/api/v1/contacts/find"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
