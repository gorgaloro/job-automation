#!/usr/bin/env python3
"""
Mobile Networking API Routes - Epic 5

FastAPI routes for contact management, LinkedIn automation, networking opportunities,
and relationship analytics. Mobile-optimized networking assistant.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.mobile_networking_engine import (
    MobileNetworkingEngine, ContactType, RelationshipStrength, 
    LinkedInActionType, NetworkingOpportunityType, NetworkingAnalytics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/networking", tags=["Mobile Networking"])

# Initialize networking engine
networking_engine = MobileNetworkingEngine()

# Pydantic Models

class ContactCreate(BaseModel):
    """Request model for contact creation"""
    name: str = Field(..., description="Contact name")
    email: Optional[str] = Field(None, description="Email address")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Location")
    contact_type: str = Field("industry_peer", description="Type of contact")
    relationship_strength: str = Field("stranger", description="Relationship strength")
    tags: List[str] = Field(default_factory=list, description="Contact tags")
    notes: str = Field("", description="Notes about the contact")
    source: str = Field("manual", description="Source of contact")

class ContactResponse(BaseModel):
    """Response model for contacts"""
    contact_id: str
    name: str
    email: Optional[str]
    company: Optional[str]
    title: Optional[str]
    contact_type: str
    relationship_strength: str
    interaction_count: int
    response_rate: float
    influence_score: float

class NetworkingAnalyticsResponse(BaseModel):
    """Response model for networking analytics"""
    total_contacts: int
    new_contacts_this_month: int
    active_conversations: int
    response_rate: float
    network_growth_rate: float
    relationship_distribution: Dict[str, int]
    top_companies: List[Dict[str, Any]]
    networking_roi: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    optimization_recommendations: List[str]

# Contact Management Endpoints

@router.post("/contacts", response_model=Dict[str, Any])
async def create_contact(request: ContactCreate):
    """
    Create a new contact
    
    Creates a new professional contact with enrichment and influence scoring.
    Automatically calculates relationship metrics and networking potential.
    """
    try:
        logger.info(f"Creating contact {request.name}")
        
        from core.mobile_networking_engine import Contact, ContactType, RelationshipStrength
        
        # Validate enums
        try:
            contact_type = ContactType(request.contact_type)
            relationship_strength = RelationshipStrength(request.relationship_strength)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
        
        contact = Contact(
            contact_id=f"contact_{uuid4().hex[:8]}",
            name=request.name,
            email=request.email,
            linkedin_url=request.linkedin_url,
            company=request.company,
            title=request.title,
            location=request.location,
            contact_type=contact_type,
            relationship_strength=relationship_strength,
            tags=request.tags,
            notes=request.notes,
            source=request.source
        )
        
        success = networking_engine.add_contact(contact)
        
        if success:
            return {
                "success": True,
                "contact_id": contact.contact_id,
                "message": "Contact created successfully",
                "influence_score": contact.influence_score
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create contact")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contact creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contact creation failed: {str(e)}")

@router.get("/contacts/search", response_model=List[ContactResponse])
async def search_contacts(
    query: Optional[str] = Query(None, description="Search query"),
    company: Optional[str] = Query(None, description="Filter by company"),
    contact_type: Optional[str] = Query(None, description="Filter by contact type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    Search contacts with filters
    
    Searches professional contacts using text query and various filters.
    Returns contacts sorted by relevance and influence score.
    """
    try:
        logger.info(f"Searching contacts with query: {query}")
        
        filters = {}
        if company:
            filters['company'] = company
        if contact_type:
            filters['contact_type'] = contact_type
        
        contacts = networking_engine.db_service.search_contacts(query or "", filters) if networking_engine.db_service else []
        
        # Limit results
        contacts = contacts[:limit]
        
        response_contacts = []
        for contact in contacts:
            response_contacts.append(ContactResponse(
                contact_id=contact.contact_id,
                name=contact.name,
                email=contact.email,
                company=contact.company,
                title=contact.title,
                contact_type=contact.contact_type.value,
                relationship_strength=contact.relationship_strength.value,
                interaction_count=contact.interaction_count,
                response_rate=contact.response_rate,
                influence_score=contact.influence_score
            ))
        
        return response_contacts
        
    except Exception as e:
        logger.error(f"Contact search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contact search failed: {str(e)}")

@router.get("/contacts/top-influencers", response_model=List[ContactResponse])
async def get_top_influencers(
    limit: int = Query(10, ge=1, le=50, description="Number of top influencers to return")
):
    """
    Get top influential contacts
    
    Returns the most influential contacts in your network based on
    relationship strength, response rates, and networking potential.
    """
    try:
        logger.info(f"Getting top {limit} influential contacts")
        
        contacts = networking_engine.db_service.get_top_contacts_by_influence(limit) if networking_engine.db_service else []
        
        response_contacts = []
        for contact in contacts:
            response_contacts.append(ContactResponse(
                contact_id=contact.contact_id,
                name=contact.name,
                email=contact.email,
                company=contact.company,
                title=contact.title,
                contact_type=contact.contact_type.value,
                relationship_strength=contact.relationship_strength.value,
                interaction_count=contact.interaction_count,
                response_rate=contact.response_rate,
                influence_score=contact.influence_score
            ))
        
        return response_contacts
        
    except Exception as e:
        logger.error(f"Top influencers retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Top influencers retrieval failed: {str(e)}")

@router.get("/opportunities", response_model=List[Dict[str, Any]])
async def get_networking_opportunities(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of opportunities")
):
    """
    Get networking opportunities
    
    Identifies and returns strategic networking opportunities including
    warm introductions, mutual connections, and referral possibilities.
    """
    try:
        logger.info("Getting networking opportunities")
        
        opportunities = networking_engine.identify_networking_opportunities()
        
        # Filter by status if provided
        if status:
            opportunities = [opp for opp in opportunities if opp.status == status]
        
        # Limit results
        opportunities = opportunities[:limit]
        
        response_opportunities = []
        for opportunity in opportunities:
            response_opportunities.append({
                "opportunity_id": opportunity.opportunity_id,
                "opportunity_type": opportunity.opportunity_type.value,
                "target_company": opportunity.target_company,
                "priority_score": opportunity.priority_score,
                "context": opportunity.context,
                "suggested_approach": opportunity.suggested_approach,
                "status": opportunity.status
            })
        
        return response_opportunities
        
    except Exception as e:
        logger.error(f"Networking opportunities retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Networking opportunities retrieval failed: {str(e)}")

@router.get("/analytics", response_model=NetworkingAnalyticsResponse)
async def get_networking_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get networking analytics
    
    Provides comprehensive networking performance analytics including
    network growth, engagement metrics, ROI tracking, and optimization insights.
    """
    try:
        logger.info("Getting networking analytics")
        
        analytics = networking_engine.get_networking_analytics(days)
        
        if analytics:
            return NetworkingAnalyticsResponse(
                total_contacts=analytics.total_contacts,
                new_contacts_this_month=analytics.new_contacts_this_month,
                active_conversations=analytics.active_conversations,
                response_rate=analytics.response_rate,
                network_growth_rate=analytics.network_growth_rate,
                relationship_distribution=analytics.relationship_distribution,
                top_companies=analytics.top_companies,
                networking_roi=analytics.networking_roi,
                engagement_metrics=analytics.engagement_metrics,
                optimization_recommendations=analytics.optimization_recommendations
            )
        else:
            raise HTTPException(status_code=404, detail="Analytics data not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Networking analytics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Networking analytics retrieval failed: {str(e)}")

@router.get("/mobile/dashboard", response_model=Dict[str, Any])
async def get_mobile_dashboard():
    """
    Get mobile networking dashboard
    
    Returns mobile-optimized dashboard with quick stats, urgent actions,
    recent activity, and networking goals for on-the-go management.
    """
    try:
        logger.info("Getting mobile networking dashboard")
        
        dashboard = networking_engine.get_mobile_dashboard()
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Mobile dashboard failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mobile dashboard failed: {str(e)}")

@router.get("/export", response_model=Dict[str, Any])
async def export_networking_data(
    user_id: str = Query(..., description="User ID to export data for"),
    format: str = Query("json", description="Export format (json, csv)")
):
    """
    Export networking data
    
    Exports comprehensive networking data including contacts, interactions,
    campaigns, opportunities, and analytics for backup and analysis.
    """
    try:
        logger.info(f"Exporting networking data for user {user_id}")
        
        export_data = networking_engine.export_networking_data(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "export_format": format,
            "data": export_data,
            "exported_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Networking data export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Networking data export failed: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check for mobile networking service
    
    Returns service status, database connectivity, and system metrics
    for monitoring and diagnostics.
    """
    try:
        return {
            "status": "healthy",
            "service": "Mobile Networking API",
            "version": "1.0.0",
            "demo_mode": networking_engine.db_service.demo_mode if networking_engine.db_service else True,
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "contact_management": True,
                "linkedin_automation": True,
                "networking_opportunities": True,
                "relationship_analytics": True,
                "mobile_optimization": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/demo", response_model=Dict[str, Any])
async def demo_showcase():
    """
    Mobile networking demo showcase
    
    Demonstrates all mobile networking capabilities with sample data
    including contact management, LinkedIn automation, and analytics.
    """
    try:
        logger.info("Running mobile networking demo showcase")
        
        demo_results = {
            "demo_name": "Mobile Networking & Contact Management",
            "epic": "Epic 5",
            "timestamp": datetime.utcnow().isoformat(),
            "features_demonstrated": [],
            "sample_data": {},
            "performance_metrics": {},
            "integration_status": {}
        }
        
        # Demo contact management
        contacts = networking_engine.db_service.search_contacts() if networking_engine.db_service else []
        demo_results["features_demonstrated"].append("Contact Management")
        demo_results["sample_data"]["contacts_count"] = len(contacts)
        
        # Demo networking opportunities
        opportunities = networking_engine.identify_networking_opportunities()
        demo_results["features_demonstrated"].append("Networking Opportunities")
        demo_results["sample_data"]["opportunities_count"] = len(opportunities)
        
        # Demo analytics
        analytics = networking_engine.get_networking_analytics()
        if analytics:
            demo_results["features_demonstrated"].append("Relationship Analytics")
            demo_results["performance_metrics"]["total_contacts"] = analytics.total_contacts
            demo_results["performance_metrics"]["response_rate"] = analytics.response_rate
            demo_results["performance_metrics"]["network_growth_rate"] = analytics.network_growth_rate
        
        # Demo mobile dashboard
        dashboard = networking_engine.get_mobile_dashboard()
        demo_results["features_demonstrated"].append("Mobile Dashboard")
        demo_results["sample_data"]["dashboard_widgets"] = len(dashboard.get("widgets", []))
        
        # Integration status
        demo_results["integration_status"] = {
            "database_service": "operational",
            "ai_engine": "operational",
            "linkedin_automation": "demo_mode",
            "mobile_optimization": "enabled"
        }
        
        return demo_results
        
    except Exception as e:
        logger.error(f"Demo showcase failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo showcase failed: {str(e)}")
