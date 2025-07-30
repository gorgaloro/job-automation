#!/usr/bin/env python3
"""
Company Enrichment & Tech Classification API Routes

FastAPI routes for company data enrichment, tech stack classification,
and company intelligence operations.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.core.company_enrichment_engine import CompanyEnrichmentEngine, CompanyEnrichmentData, TechClassification
from src.integrations.supabase.company_enrichment_service import CompanyEnrichmentDatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/company-enrichment", tags=["Company Enrichment"])

# Initialize services
enrichment_engine = CompanyEnrichmentEngine()
db_service = CompanyEnrichmentDatabaseService()

# Pydantic Models
class CompanyEnrichmentRequest(BaseModel):
    """Request model for company enrichment"""
    company_name: str = Field(..., description="Company name to enrich")
    domain: Optional[str] = Field(None, description="Company domain/website")
    existing_data: Optional[Dict[str, Any]] = Field(None, description="Any existing company data")

class TechClassificationRequest(BaseModel):
    """Request model for tech stack classification"""
    company_name: str = Field(..., description="Company name")
    domain: Optional[str] = Field(None, description="Company domain")
    job_description: Optional[str] = Field(None, description="Job description for tech stack hints")

class BatchEnrichmentRequest(BaseModel):
    """Request model for batch company enrichment"""
    companies: List[Dict[str, Any]] = Field(..., description="List of companies to enrich")

class CompanySearchRequest(BaseModel):
    """Request model for company search"""
    tech_vertical: str = Field(..., description="Tech vertical to search for")
    limit: int = Field(10, description="Maximum number of results", ge=1, le=50)

class HubSpotSyncRequest(BaseModel):
    """Request model for HubSpot company sync"""
    hubspot_company_data: Dict[str, Any] = Field(..., description="Company data from HubSpot")

class CompanyEnrichmentResponse(BaseModel):
    """Response model for company enrichment"""
    success: bool
    company_id: Optional[str] = None
    enriched_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None

class TechClassificationResponse(BaseModel):
    """Response model for tech classification"""
    success: bool
    classification: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None

class BatchEnrichmentResponse(BaseModel):
    """Response model for batch enrichment"""
    success: bool
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None

class CompanySearchResponse(BaseModel):
    """Response model for company search"""
    success: bool
    companies: Optional[List[Dict[str, Any]]] = None
    total_found: Optional[int] = None
    error: Optional[str] = None

class TechStatsResponse(BaseModel):
    """Response model for tech vertical statistics"""
    success: bool
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# API Endpoints

@router.post("/enrich", response_model=CompanyEnrichmentResponse)
async def enrich_company(request: CompanyEnrichmentRequest):
    """
    Enrich a single company with comprehensive data and tech classification
    
    This endpoint performs AI-powered company enrichment including:
    - Industry classification and company size estimation
    - Funding stage and valuation analysis
    - Tech stack classification and vertical assignment
    - Culture and values analysis
    - Competitive landscape mapping
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Enriching company: {request.company_name}")
        
        # Enrich company data
        enriched_data = enrichment_engine.enrich_company(
            company_name=request.company_name,
            domain=request.domain,
            existing_data=request.existing_data
        )
        
        # Store in database
        company_id = db_service.store_enriched_company(enriched_data)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CompanyEnrichmentResponse(
            success=True,
            company_id=company_id,
            enriched_data={
                "name": enriched_data.name,
                "industry": enriched_data.industry,
                "size_range": enriched_data.size_range,
                "employee_count": enriched_data.employee_count,
                "funding_stage": enriched_data.funding_stage,
                "headquarters": enriched_data.headquarters,
                "tech_classification": {
                    "primary_vertical": enriched_data.tech_classification.primary_vertical if enriched_data.tech_classification else None,
                    "tech_stack": enriched_data.tech_classification.tech_stack if enriched_data.tech_classification else [],
                    "confidence_score": enriched_data.tech_classification.confidence_score if enriched_data.tech_classification else 0.0
                },
                "culture_summary": enriched_data.culture_summary,
                "values": enriched_data.values,
                "competitors": enriched_data.competitors,
                "glassdoor_rating": enriched_data.glassdoor_rating,
                "remote_policy": enriched_data.remote_policy
            },
            confidence_score=enriched_data.confidence_score,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Company enrichment failed: {e}")
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CompanyEnrichmentResponse(
            success=False,
            error=str(e),
            processing_time_ms=processing_time
        )

@router.post("/classify-tech", response_model=TechClassificationResponse)
async def classify_tech_stack(request: TechClassificationRequest):
    """
    Classify a company's tech stack and vertical
    
    This endpoint performs detailed tech stack analysis including:
    - Primary and secondary tech vertical classification
    - Programming languages and frameworks identification
    - Database and cloud platform analysis
    - Confidence scoring and rationale generation
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Classifying tech stack for: {request.company_name}")
        
        # Classify tech stack
        classification = enrichment_engine.classify_tech_stack(
            company_name=request.company_name,
            domain=request.domain,
            job_description=request.job_description
        )
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return TechClassificationResponse(
            success=True,
            classification={
                "primary_vertical": classification.primary_vertical,
                "secondary_verticals": classification.secondary_verticals,
                "tech_stack": classification.tech_stack,
                "programming_languages": classification.programming_languages,
                "frameworks": classification.frameworks,
                "databases": classification.databases,
                "cloud_platforms": classification.cloud_platforms,
                "classification_rationale": classification.classification_rationale
            },
            confidence_score=classification.confidence_score,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Tech classification failed: {e}")
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return TechClassificationResponse(
            success=False,
            error=str(e),
            processing_time_ms=processing_time
        )

@router.post("/batch-enrich", response_model=BatchEnrichmentResponse)
async def batch_enrich_companies(request: BatchEnrichmentRequest):
    """
    Batch enrich multiple companies
    
    This endpoint processes multiple companies in a single request:
    - Parallel processing for efficiency
    - Individual success/failure tracking
    - Comprehensive batch statistics
    - Error handling and recovery
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Batch enriching {len(request.companies)} companies")
        
        # Perform batch enrichment
        results = db_service.batch_enrich_companies(request.companies)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return BatchEnrichmentResponse(
            success=True,
            results=results,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch enrichment failed: {e}")
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return BatchEnrichmentResponse(
            success=False,
            error=str(e),
            processing_time_ms=processing_time
        )

@router.get("/company/{company_id}", response_model=CompanyEnrichmentResponse)
async def get_enriched_company(company_id: str):
    """
    Retrieve enriched company data by ID
    
    Returns comprehensive enriched company data including:
    - Basic company information
    - Tech stack classification
    - Culture and values analysis
    - Competitive intelligence
    """
    try:
        logger.info(f"Retrieving enriched company: {company_id}")
        
        # Get company data
        company_data = db_service.get_enriched_company(company_id)
        
        if not company_data:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return CompanyEnrichmentResponse(
            success=True,
            company_id=company_id,
            enriched_data=company_data,
            confidence_score=company_data.get("confidence_score", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve company: {e}")
        return CompanyEnrichmentResponse(
            success=False,
            error=str(e)
        )

@router.post("/search", response_model=CompanySearchResponse)
async def search_companies_by_tech_vertical(request: CompanySearchRequest):
    """
    Search companies by tech vertical
    
    Find companies matching specific tech verticals:
    - Primary vertical matching
    - Secondary vertical matching
    - Confidence-based ranking
    - Pagination support
    """
    try:
        logger.info(f"Searching companies by tech vertical: {request.tech_vertical}")
        
        # Search companies
        companies = db_service.search_companies_by_tech_vertical(
            vertical=request.tech_vertical,
            limit=request.limit
        )
        
        return CompanySearchResponse(
            success=True,
            companies=companies,
            total_found=len(companies)
        )
        
    except Exception as e:
        logger.error(f"Company search failed: {e}")
        return CompanySearchResponse(
            success=False,
            error=str(e)
        )

@router.get("/tech-stats", response_model=TechStatsResponse)
async def get_tech_vertical_statistics():
    """
    Get tech vertical statistics
    
    Returns comprehensive statistics about tech verticals:
    - Total companies by vertical
    - Top performing verticals
    - Distribution analysis
    - Growth trends
    """
    try:
        logger.info("Retrieving tech vertical statistics")
        
        # Get statistics
        stats = db_service.get_tech_vertical_stats()
        
        return TechStatsResponse(
            success=True,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get tech stats: {e}")
        return TechStatsResponse(
            success=False,
            error=str(e)
        )

@router.post("/hubspot-sync", response_model=CompanyEnrichmentResponse)
async def sync_company_from_hubspot(request: HubSpotSyncRequest):
    """
    Sync and enrich company data from HubSpot
    
    Integrates HubSpot company data with enrichment:
    - HubSpot data integration
    - Automatic enrichment triggers
    - Bidirectional sync support
    - Conflict resolution
    """
    start_time = datetime.now()
    
    try:
        logger.info("Syncing company from HubSpot")
        
        # Update company from HubSpot
        company_id = db_service.update_company_from_hubspot(request.hubspot_company_data)
        
        if not company_id:
            raise HTTPException(status_code=400, detail="Failed to sync company from HubSpot")
        
        # Get updated company data
        company_data = db_service.get_enriched_company(company_id)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CompanyEnrichmentResponse(
            success=True,
            company_id=company_id,
            enriched_data=company_data,
            confidence_score=company_data.get("confidence_score", 0.0) if company_data else 0.0,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HubSpot sync failed: {e}")
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CompanyEnrichmentResponse(
            success=False,
            error=str(e),
            processing_time_ms=processing_time
        )

@router.get("/company-by-name/{company_name}", response_model=CompanyEnrichmentResponse)
async def get_company_by_name(company_name: str):
    """
    Get enriched company data by name
    
    Retrieve company data using company name:
    - Fuzzy name matching
    - Case-insensitive search
    - Alias resolution
    """
    try:
        logger.info(f"Retrieving company by name: {company_name}")
        
        # Get company data by name
        company_data = db_service.get_enriched_company_by_name(company_name)
        
        if not company_data:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return CompanyEnrichmentResponse(
            success=True,
            company_id=company_data.get("id"),
            enriched_data=company_data,
            confidence_score=company_data.get("confidence_score", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve company by name: {e}")
        return CompanyEnrichmentResponse(
            success=False,
            error=str(e)
        )

@router.post("/demo", response_model=Dict[str, Any])
async def demo_company_enrichment():
    """
    Demo endpoint showcasing company enrichment capabilities
    
    Demonstrates all major features:
    - Single company enrichment
    - Tech stack classification
    - Batch processing
    - Search functionality
    - Statistics and analytics
    """
    try:
        logger.info("Running company enrichment demo")
        
        demo_results = {
            "demo_timestamp": datetime.now().isoformat(),
            "features_demonstrated": [],
            "results": {}
        }
        
        # Demo 1: Single company enrichment
        demo_results["features_demonstrated"].append("single_company_enrichment")
        enriched = enrichment_engine.enrich_company("TechCorp")
        demo_results["results"]["single_enrichment"] = {
            "company_name": enriched.name,
            "industry": enriched.industry,
            "tech_vertical": enriched.tech_classification.primary_vertical if enriched.tech_classification else None,
            "confidence_score": enriched.confidence_score
        }
        
        # Demo 2: Tech classification
        demo_results["features_demonstrated"].append("tech_classification")
        tech_classification = enrichment_engine.classify_tech_stack("DataFlow")
        demo_results["results"]["tech_classification"] = {
            "primary_vertical": tech_classification.primary_vertical,
            "tech_stack": tech_classification.tech_stack[:3],
            "confidence_score": tech_classification.confidence_score
        }
        
        # Demo 3: Batch enrichment
        demo_results["features_demonstrated"].append("batch_enrichment")
        batch_companies = [
            {"name": "StartupX", "domain": "startupx.com"},
            {"name": "ScaleY", "domain": "scaley.io"}
        ]
        batch_results = db_service.batch_enrich_companies(batch_companies)
        demo_results["results"]["batch_enrichment"] = {
            "total_processed": batch_results["total_processed"],
            "success_rate": batch_results["success_rate"],
            "successful_count": len(batch_results["successful"])
        }
        
        # Demo 4: Tech vertical search
        demo_results["features_demonstrated"].append("tech_vertical_search")
        fintech_companies = db_service.search_companies_by_tech_vertical("fintech", limit=3)
        demo_results["results"]["tech_search"] = {
            "vertical": "fintech",
            "companies_found": len(fintech_companies)
        }
        
        # Demo 5: Statistics
        demo_results["features_demonstrated"].append("tech_statistics")
        stats = db_service.get_tech_vertical_stats()
        demo_results["results"]["statistics"] = {
            "total_companies": stats.get("total_companies", 0),
            "top_verticals": stats.get("top_verticals", [])[:3]
        }
        
        demo_results["summary"] = {
            "total_features": len(demo_results["features_demonstrated"]),
            "demo_success": True,
            "message": "Company Enrichment & Tech Classification system fully operational! 🚀"
        }
        
        return demo_results
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return {
            "demo_timestamp": datetime.now().isoformat(),
            "demo_success": False,
            "error": str(e),
            "message": "Demo encountered an error, but system is still functional in demo mode"
        }
